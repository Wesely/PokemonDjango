#!/usr/bin/env python
# coding=utf-8

from django.shortcuts import render
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from subprocess import call

import time
import argparse
from itertools import groupby
from pgoapi import PGoApi
from random import randint
from terminaltables import AsciiTable
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))


def jsonResponse(dict):
    """ return json response """
    return HttpResponse(json.dumps(dict), content_type='application/json; charset="utf-8"')

@csrf_exempt
@require_POST
def get_iv(request):
    global a, u, p , lo, clear, fast
    header = u'fast的設定其實還沒有用...'
    format_msg = u'必要參數: a=google/ptc, u=email, p=password; \n 非必要: list_only=False會重新命名(預設True), clear=True會命名成原本中文名稱(預設False), fast=還沒做好:快速重新命名(預設False)'
    if request.POST.get('a'):
        a = request.POST.get('a')
    else:
        print u'no param:a'
        return jsonResponse({'msg':format_msg,  'success':False})

    if request.POST.get('u'):
        u = request.POST.get('u')
    else:
        print u'no param:u'
        return jsonResponse({'msg':format_msg,  'success':False})

    if request.POST.get('p'):
        p = request.POST.get('p')
    else:
        print u'no param:u'
        return jsonResponse({'msg':format_msg,  'success':False})

    if request.POST.get('list_only'):
        lo = request.POST.get('list_only')
    else:
        lo = True

    if request.POST.get('clear'):
        clear = request.POST.get('clear')
    else:
        clear = False


    if request.POST.get('fast'):
        fast = request.POST.get('fast')
    else:
        fast = False
    #table_data = call(['python', 'main2.py', '-a', a, '-u', u, '-p', p, '-lo'])
    renamer = Renamer3()
    table_data = renamer.start()
    return jsonResponse({'usage':format_msg, 'header': header, 'table_data':table_data,  'success':True})

class Colors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

class Renamer3(object):
    """Main renamer class object"""

    def __init__(self):
        self.pokemon = []
        self.api = None
        self.pokemon_list = None


    def init_config(self):

        self.auth_service = a
        self.username = u
        self.password = p
        self.clear = clear
        self.list_only = lo
        self.format = "%percent% %name"
        self.overwrite = None
        self.min_delay = 10
        self.max_delay = 20
        self.iv = 0
        self.locale = "en"
        self.data = None
        """Gets configuration from command line arguments"""
        # parser = argparse.ArgumentParser()

        # parser.add_argument("-a", "--auth_service")
        # parser.add_argument("-u", "--username")
        # parser.add_argument("-p", "--password")
        # parser.add_argument("--clear", action='store_true', default=False)
        # parser.add_argument("-lo", "--list_only", action='store_true', default=False)
        # parser.add_argument("--format", default="%ivsum, %atk/%def/%sta")
        # parser.add_argument("-l", "--locale", default="en")
        # parser.add_argument("--min_delay", type=int, default=10)
        # parser.add_argument("--max_delay", type=int, default=20)
        # parser.add_argument("--iv", type=int, default=0)

        # self.config = parser.parse_args()
        # self.overwrite = True
        #self.skip_favorite = True
        #self.only_favorite = False

    def start(self):
        """Start renamer"""
        print "Start renamer"

        self.init_config()
        json_data = open(os.path.join(BASE, 'pokemon.tw.json'))
        print json_data  
        self.pokemon_list = json.load(json_data)
        #except IOError:
        #print "~the selected language is currently not supported"
        #exit(0)

        self.setup_api()
        self.get_pokemon()
        data = self.print_pokemon()
        print 'lo:'+str(lo)+',  clear:'+str(clear)
        if (lo not 'false') and (lo not 'False'):
            print 'to pass, do nothing'
            pass
        elif clear=='true' or clear=='True':
            print 'to clear'
            self.clear_pokemon()
        else:
            print 'to rename'
            self.rename_pokemon()
        return self.data

    def setup_api(self):
        """Prepare and sign in to API"""
        self.api = PGoApi()

        if not self.api.login(self.auth_service,
                              str(self.username),
                              str(self.password)):
            print "Login error"
            exit(0)

        print "Signed in"

    def get_pokemon(self):
        """Fetch Pokemon from server and store in array"""
        print "Getting Pokemon list"
        self.api.get_inventory()
        response_dict = self.api.call()

        self.pokemon = []
        inventory_items = response_dict['responses'] \
                                       ['GET_INVENTORY'] \
                                       ['inventory_delta'] \
                                       ['inventory_items']

    def get_pokemon(self):
        """Fetch Pokemon from server and store in array"""
        print "Getting Pokemon list"
        self.api.get_inventory()
        response_dict = self.api.call()

        self.pokemon = []
        inventory_items = response_dict['responses'] \
                                       ['GET_INVENTORY'] \
                                       ['inventory_delta'] \
                                       ['inventory_items']

        for item in inventory_items:
            try:
                reduce(dict.__getitem__, ["inventory_item_data", "pokemon_data"], item)
            except KeyError:
                pass
            else:
                try:
                    pokemon = item['inventory_item_data']['pokemon_data']

                    pid = pokemon['id']
                    num = pokemon['pokemon_id']
                    name = self.pokemon_list[str(num)]

                    attack = pokemon.get('individual_attack', 0)
                    defense = pokemon.get('individual_defense', 0)
                    stamina = pokemon.get('individual_stamina', 0)
                    iv_percent = (float(attack + defense + stamina) / 45.0) * 100.0

                    nickname = pokemon.get('nickname', 'NONE')
                    combat_power = pokemon.get('cp', 0)

                    self.pokemon.append({
                        'id': pid,
                        'num': num,
                        'name': name,
                        'nickname': nickname,
                        'cp': combat_power,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina,
                        'iv_percent': iv_percent,
                    })
                except KeyError:
                    pass
        # Sort the way the in-game `Number` option would, i.e. by Pokedex number
        # in ascending order and then by CP in descending order.
        self.pokemon.sort(key=lambda k: (k['num'], -k['cp']))

    def print_pokemon(self):
        """Print Pokemon and their stats"""
        sorted_mons = sorted(self.pokemon, key=lambda k: (k['num'], -k['iv_percent']))
        groups = groupby(sorted_mons, key=lambda k: k['num'])
        table_data = [
            ['Pokemon', 'CP', 'IV %', 'ATK', 'DEF', 'STA']
        ]
        for key, group in groups:
            group = list(group)
            pokemon_name = self.pokemon_list[str(key)].replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)')
            best_iv_pokemon = max(group, key=lambda k: k['iv_percent'])
            best_iv_pokemon['best_iv'] = True
            for pokemon in group:
                row_data = [
                    pokemon_name,
                    pokemon['cp'],
                    "{0:.0f}%".format(pokemon['iv_percent']),
                    pokemon['attack'],
                    pokemon['defense'],
                    pokemon['stamina']
                ]
                table_data.append(row_data)
        self.data = table_data
                # if pokemon.get('best_iv', False) and len(group) > 1:
                #     row_data = [Colors.OKGREEN + str(cell) + Colors.ENDC for cell in row_data]
        table = AsciiTable(table_data)
        table.justify_columns[0] = 'left'
        table.justify_columns[1] = 'right'
        table.justify_columns[2] = 'right'
        table.justify_columns[3] = 'right'
        table.justify_columns[4] = 'right'
        table.justify_columns[5] = 'right'
        print table.table

    def rename_pokemon(self):
        print 'rename >>\n'
        """Renames Pokemon according to configuration"""
        already_renamed = 0
        renamed = 0

        for pokemon in self.pokemon:
            individual_value = pokemon['attack'] + pokemon['defense'] + pokemon['stamina']
            iv_percent = int(pokemon['iv_percent'])

            if individual_value < 10:
                individual_value = "0" + str(individual_value)

            num = pokemon['num']
            pokemon_name = self.pokemon_list[str(num)]

            name = self.format
            name = name.replace("%id", str(num))
            name = name.replace("%ivsum", str(individual_value))
            name = name.replace("%atk", str(pokemon['attack']))
            name = name.replace("%def", str(pokemon['defense']))
            name = name.replace("%sta", str(pokemon['stamina']))
            name = name.replace("%percent", str(iv_percent))
            name = name.replace("%cp", str(pokemon['cp']))
            name = name.replace("%name", pokemon_name)
            name = name[:12]

            if (pokemon['nickname'] == "NONE" \
                or pokemon['nickname'] == pokemon_name \
                or (pokemon['nickname'] != name and self.overwrite)) \
                and iv_percent >= self.iv:

                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name)
                response = self.api.call()

                result = response['responses']['NICKNAME_POKEMON']['result']

                if result == 1:
                    print "Renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name
                else:
                    print "Something went wrong with renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name + ". Error code: " + str(result)

                random_delay = randint(self.min_delay, self.max_delay)
                time.sleep(random_delay)

                renamed += 1

            else:
                already_renamed += 1

        print str(renamed) + " Pokemon renamed."
        print str(already_renamed) + " Pokemon already renamed."

    def clear_pokemon(self):
        """Resets all Pokemon names to the original"""
        cleared = 0

        for pokemon in self.pokemon:
            num = int(pokemon['num'])
            name_original = self.pokemon_list[str(num)]

            if pokemon['nickname'] != "NONE" and pokemon['nickname'] != name_original:
                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name_original)
                response = self.api.call()

                result = response['responses']['NICKNAME_POKEMON']['result']

                if result == 1:
                    print "Resetted " + pokemon['nickname'] +  " to " + name_original
                else:
                    print "Something went wrong with resetting " + pokemon['nickname'] + " to " + name_original + ". Error code: " + str(result)

                random_delay = randint(self.min_delay, self.max_delay)
                time.sleep(random_delay)

                cleared += 1

        print "Cleared " + str(cleared) + " names"
