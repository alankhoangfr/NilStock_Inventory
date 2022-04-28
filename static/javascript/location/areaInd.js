
//Remove Area

$(document).on("click",'#proceed',function(elem){
  area_id =$('#area').text()
   $.ajax({
    data: JSON.stringify({
      "area_id":area_id,
      "submit": 'removeArea',
    }),
    type: "post",
    url: '/area/remove',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/area"
  }
    }); 
})

$(document).on("click",'#edit',function(elem){
  area_id =$('#area').text()
  newName =$('#areaNewName').val()
   $.ajax({
    data: JSON.stringify({
      "area_id":area_id,
      "newName":newName,
      "submit": 'editArea',
    }),
    type: "post",
    url: '/area/edit',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/areaInd/"+area_id
  }
    }); 
})

$(document).on("click","#areaModalClose",function(elem){
  history.go(0)
})