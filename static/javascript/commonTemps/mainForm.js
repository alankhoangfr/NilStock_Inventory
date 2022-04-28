

let state_select =  document.getElementById('state');
let suburb_select = document.getElementById('suburb');
let address_select = document.getElementById('address');

function populateAddress(responseAddress){
  responseAddress.json().then(function(dataAddress) {
    let optionAddressHtml = '';
    for (let locAddress of dataAddress.locations){
      optionAddressHtml+= '<option value ='+locAddress.address+'>'+locAddress.address+'</option>';  
    }
    address_select.innerHTML=  optionAddressHtml;
  })
}

function populateSuburb(responseSuburb){
  responseSuburb.json().then(function(dataSuburb) {
    let optionSuburbHtml = '';
    for (let locSuburb of dataSuburb.locations){
      optionSuburbHtml+= '<option value ='+locSuburb.suburb+'>'+locSuburb.suburb+'</option>';   
    }
    suburb_select.innerHTML=  optionSuburbHtml;
    if(dataSuburb.locations.length==1){
      fetch('/locations/' +state_id+'/'+ dataSuburb.locations[0].suburb+'/address').then(response=>populateAddress(response))
    }
  });
}

state_select.onchange = function(){
  state_id = $('#state option:selected').val() 
  fetch('/locations/' + state_id+'/suburb').then(response=>populateSuburb(response));
}

suburb_select.onchange = function(){
  suburb =$('#suburb option:selected').text() 
  state_id = $('#state option:selected').val() 
  fetch('/locations/' +state_id+'/'+ suburb+'/address').then(response=>populateAddress(response))
}




$('#formMainSubmit').click( function(e) { 
  var type;
  var status;
  var url;
 if($('#formMainSubmit').val()=='Add Listing'){
  type = 'listing'
  dataSend = JSON.stringify({
        "submit": type,
        "name": $('#name').val(),
        "suburb": $('#suburb option:selected').text(),
        "address": $('#address option:selected').text(),
        "state": $('#state option:selected').val()
     })
  url="/"+type+"/new"
 }else if ($('#formMainSubmit').val()=='Add Storage'){
  type = 'storage'
  dataSend = JSON.stringify({
      "submit": type,
      "name": $('#name').val(),
      "suburb": $('#suburb option:selected').text(),
      "address": $('#address option:selected').text(),
      "state": $('#state option:selected').val()
   })
  url="/"+type+"/new"
 }else{
  type= 'supplier'
  dataSend = JSON.stringify({
      "submit": type,
      "name": $('#name').val(),
      "contact": $('#contact').val(),
      "website": $('#website').val(),
      "suburb": $('#suburb option:selected').text(),
      "address": $('#address option:selected').text(),
      "state": $('#state option:selected').val()
   })
  url="/"+type+"/new"
 }

 $.ajax({
     data: dataSend,
     type: "post",
     url: url,
     contentType: "application/json"
 })
 .done(function(data){
  if(data.status ==='fail'){
    status='fail'
    $('#errorAlertMain').show();
    $('#successAlertMain').hide();
    $('#errorAlertMain').html(data.reason)
    window.setTimeout(function(){ $('#errorAlertMain').hide(); }, 3000);    
  }else{
    status='success'
    $('#errorAlertMain').hide();
    $('#successAlertMain').show();
    window.setTimeout(function(){ $('#successAlertMain').hide(); }, 3000); 
  }
 })
e.preventDefault();

  
});


/*


 */