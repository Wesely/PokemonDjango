from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404


def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        # 'latest_question_list': latest_question_list,
    }
    return render(request, 'ivrename/index.html', context)

def test(request):
    return render(request, 'ivrename/index.html')
