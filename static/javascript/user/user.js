let storageSelect = document.getElementById('possibleStorage');

function populateStorage(responseStorage) {
    responseStorage.json().then(function(storages) {
      let optionStorages = '';
      for (let stor of storages.storageCages){
        optionStorages+= '<option value ='+stor[0]+'>'+stor[1]+'</option>';   
      }
      storageSelect.innerHTML=  optionStorages;

    });
  }

$(document).on("click",'[name="addManager"]',function(elem){
  user_id=$(this).attr('id')
  fetch('users_storage/' + user_id+'/nothing').then(responseStorage=> populateStorage(responseStorage));
  $('#searchingStorage').val("")
})


$(document).on("change",'#searchingStorage',function(event){

    value = "nothing"
    if($('#searchingStorage').val()!=""){
    	value=$('#searchingStorage').val()
    }
    fetch('users_storage/' + user_id+'/'+value).then(responseStorage=>populateStorage(responseStorage));
  
})

$('#searchingStorage').keydown(function(event){
  if (event.which == '13') {
    event.preventDefault();
    event.stopPropagation();
    value = "nothing"
    if($('#searchingStorage').val()!=""){
    	value=$('#searchingStorage').val()
    }
    fetch('users_storage/' + user_id+'/'+value).then(responseStorage=>populateStorage(responseStorage));
  }
});

$(document).on("click",'#addResponsibility',function(elem){
	storage_id = $('#possibleStorage option:selected').val()
	 $.ajax({
    data: JSON.stringify({
      "storage_id":storage_id,
      "submit": 'add_user_storage',
      "user_id": user_id,
    }),
    type: "post",
    url: '/add_storage_user',
    contentType: "application/json"
	}) .done(function(data){
	if(data.status ==='fail'){

	}else{
	}
  	}); 
})


function populateRemoveStorage(responseStorage) {
    responseStorage.json().then(function(storages) {
      let optionStorages = '';
      for (let stor of storages.removeStorage){
        optionStorages+= '<option value ='+stor[0]+'>'+stor[1]+'</option>';   
      }
      document.getElementById('possibleStorageRemove').innerHTML=  optionStorages;

    });
  }

$(document).on("click",'[name="removeManager"]',function(elem){
  user_id=$(this).attr('id')
  fetch('users_storage/' + user_id+'/nothing').then(responseStorage=> populateRemoveStorage(responseStorage));

})

$(document).on("click",'#removeResponsibility',function(elem){
	storage_id = $('#possibleStorageRemove option:selected').val()
	 $.ajax({
    data: JSON.stringify({
      "storage_id":storage_id,
      "submit": 'remove_user_storage',
      "user_id": user_id,
    }),
    type: "post",
    url: '/remove_storage_user',
    contentType: "application/json"
	}) .done(function(data){
	if(data.status ==='fail'){

	}else{
	}
  	}); 
})
