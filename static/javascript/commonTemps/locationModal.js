let stateLoc_select =  document.getElementById('stateLoc');
let area_select =  document.getElementById('area');

stateLoc_select.onchange = function(){
  state_id = $('#stateLoc option:selected').val() 
  fetch('/locations/' + state_id+'/area').then(function(responseSuburb) {
    responseSuburb.json().then(function(dataSuburb) {
      let optionAreaHtml = '';
      for (let locSuburb of dataSuburb.locations){
        optionAreaHtml+= '<option value ='+locSuburb.name+'>'+locSuburb.name+'</option>';   
      }
      area_select.innerHTML=  optionAreaHtml;

    });
  });
}








$('#formLocationSubmit').click( function(e) { 
 //do things on submit

 $.ajax({
     data: JSON.stringify({
        "submit": 'location',
        "addressLoc": $('#addressLoc').val(),
        "suburbLoc": $('#suburbLoc').val(),
        "postcode": $('#postcode').val(),
        "area": $('#area option:selected').text(),
        "stateLoc": $('#stateLoc option:selected').val(),
     }),
     type: "post",
     url: "/location/new",
     contentType: "application/json"
 })
 .done(function(data){
  if(data.status ==='fail'){
    $('#errorAlertLocation').show();
    $('#successAlertLocation').hide();
    $('#errorAlertLocation').html(data.reason)
    window.setTimeout(function(){ $('#errorAlertLocation').hide(); }, 3000); 
  }else{
    $('#errorAlertLocation').hide();
    $('#successAlertLocation').show();
    window.setTimeout(function(){ $('#successAlertLocation').hide(); }, 3000); 
  }
   
 })
 
  e.preventDefault();

  
});