onload = function() {
	initForm();
};

var initForm = function(){
	$("#ivlookup-form").submit(function(e)
	{
	    var postData = $(this).serializeArray();
	    var formURL = IV_LOOKUP_URL;
	    $.ajax(
	    {
	        url : formURL,
	        type: "POST",
	        data : postData,
	        success:function(data, textStatus, jqXHR) 
	        {
	            showPokemons(data);
	        },
	        error: function(jqXHR, textStatus, errorThrown) 
	        {
	            alert("error: please check your account and password.");      
	        }
	    });
	    e.preventDefault(); //STOP default action
	    //e.unbind(); //unbind. to stop multiple form submit.
	});
	
	$("#ivlookup-form-btn").click(function(){
		$("#ivlookup-form").submit(); //Submit  the FORM
	});
}


var showPokemons = function(ele){
	var data = eval(ele);
	var pokemons = data.table_data;
	var pageContent = document.getElementById('page-content');
	var table = document.createElement("table");
	table.id = "pokemon-table";
	table.setAttribute("class", "table table-striped table-bordered");
	var thead = document.createElement("thead");
	var tr = document.createElement("tr");
	// table head
	var pokemon_table_head = pokemons[0];
	for(var i=0;i<pokemon_table_head.length;i++){
		var th = document.createElement("th");
		th.textContent = pokemon_table_head[i];
		th.setAttribute("class", "sorting_asc");
		tr.appendChild(th);
	}
	thead.appendChild(tr);
	table.appendChild(thead);
	// table body
	var tbody = document.createElement("tbody");
	var a, span;
	for(var i=1;i<pokemons.length;i++){
		tr = document.createElement("tr");
		for(var j=0;j<pokemon_table_head.length;j++){
			var td = document.createElement("td");
			td.textContent = pokemons[i][j];
			tr.appendChild(td);
		}
		tbody.appendChild(tr);
	}
	table.appendChild(tbody);
	clearContent();
	pageContent.appendChild(table);
}

var clearContent = function(){
	var pageContent = document.getElementById('page-content');
	pageContent.innerHTML = "";
}