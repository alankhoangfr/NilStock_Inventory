$('#formAreaSubmit').click( function(e) { 
 $.ajax({
     data: JSON.stringify({
        'csrf-token':$('#csrf_token').val(),
        "submit": 'Add Area',
        "area_name": $('#area_name').val(),
        "stateArea": $('#stateArea option:selected').val()
     }),
     type: "post",
     url: "/area/new",
     contentType: "application/json"
 })
 .done(function(data){
  if(data.status ==='fail'){
    $('#errorAlertArea').show();
    $('#successAlertArea').hide();
    $('#errorAlertArea').html(data.reason)
    window.setTimeout(function(){ $('#errorAlertArea').hide(); }, 3000); 
  }else{
    $('#errorAlertArea').hide();
    $('#successAlertArea').show();
    window.setTimeout(function(){ $('#successAlertArea').hide(); }, 3000); 
  }
   
 })
 
  e.preventDefault();

  
});