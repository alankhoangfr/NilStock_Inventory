$("#apsl_submit").val("Add New Listing");

function allInput(){
  var isValid=true;
  $('input[name="booking"]').each(function() {
     var element = $(this);
     if (element.val() == "") {
         isValid = false;
         $('#apsl_submit').prop('disabled', true);        
     }
  });
  if(isValid){
    alert("success","")
    $('#apsl_submit').prop('disabled', false);
  }else{
    alert("danger","Please complete all the per booking")
  }
}

function alert(type,text){
  if(type=="danger"){
    $('#errorAlert').hide()
    $('#errorAlert').text(text)
    $('#errorAlert').show()
  }else{
    $('#errorAlert').hide()
  }
}

function isvalid(){
  if($('#listingName').text().trim()==''){

    $('#apsl_submit').prop('disabled', true);
    alert("danger","Please select a listing")
  }else{
    if(!$('input[name="booking"]').length){
      $('#apsl_submit').prop('disabled', true);
      alert("danger","Please register at least one product")
    }
    else{
      allInput()
    }
  }
}

isvalid()

$(document).on("change",'input[name="booking"]',function(elem){
  isvalid()
})

let stateLoc_select =  document.getElementById('sla_state');
let area_select =  document.getElementById('sla_area');
let listing_select =  document.getElementById('sla_listing');


function populateListing(responseListing){
  responseListing.json().then(function(dataListing) {
    if(dataListing.listings.length==0){
      $('#selectListing').prop('disabled', true);
    }else if(dataListing.listings.length>0){
      $('#selectListing').prop('disabled', false);
    }
    let optionListingHtml = '';
    for (let listing of dataListing.listings){
      optionListingHtml+= '<option value ='+listing.id+'>'+listing.name+'</option>';   
    }
    optionListingHtml+= '<option value ='+'>'+'</option>';   
    listing_select.innerHTML=  optionListingHtml;

  });
}


function populateArea(responseArea){
    responseArea.json().then(function(dataArea) {
      let optionAreaHtml = '';
      for (let locArea of dataArea.locations){
        optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
      }
      area_select.innerHTML=  optionAreaHtml;

    });
  }

stateLoc_select.onchange = function(){
  state = $('#sla_state option:selected').val()
  storage_id =$('#storageId').text()
  fetch('/locations/' + state+'/area').then(responseArea=>populateArea(responseArea));
  fetch('/notlisting/state/' + state+'/storage/'+storage_id).then(responseListing=>populateListing(responseListing) );
}

area_select.onchange = function(){
  area = $('#sla_area option:selected').val()
  storage_id =$('#storageId').text()
  fetch('/notlisting/area/' + area+'/storage/'+storage_id).then(responseListing=>populateListing(responseListing) );
}

$('#selectListing').click( function(e) { 
  listing_id=$('#sla_listing option:selected').val()
  storage_id =$('#storageId').text()
  let listingNameText = 'Products that are in '+$('#sla_listing option:selected').text()
  $('#listingName').text(listingNameText)
  $('#findListing').collapse("hide")
  e.preventDefault();
  alert("success","")
  isvalid()
 })
 





$(document).on("click",' .btn_supplier',function(elem){
    let listing = $(this).attr('id')
   let fs_area =  document.getElementById('fs_area');
   let fs_state =  document.getElementById('fs_state');
   let fs_supplier =  document.getElementById('fs_supplier');

  fs_state.onchange = function(){
    state = $('#fs_state option:selected').val()
    fetch('/locations/' + state+'/area').then(function(responseArea) {
      responseArea.json().then(function(dataArea) {
        let optionAreaHtml = '';
        for (let locArea of dataArea.locations){
          optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
        }
        fs_area.innerHTML=  optionAreaHtml;

      });
    });
    fetch('/supplier/state/' + state).then(function(responseListing) {
      responseListing.json().then(function(dataListing) {
        if(dataListing.suppliers.length==0){
          $('#fs_Submit').prop('disabled', true);
        }else if(dataListing.suppliers.length>0){
          $('#fs_Submit').prop('disabled', false);
        }
        let optionSupplierHtml = '';
        for (let supplier of dataListing.suppliers){
          optionSupplierHtml+= '<option value ='+supplier.id+'>'+supplier.name+'</option>';   
        }
        fs_supplier.innerHTML=  optionSupplierHtml;

      });
    });
  }

  fs_area.onchange = function(){
    area = $('#fs_area option:selected').val()
    fetch('/supplier/area/' + area).then(function(responseListing) {
      responseListing.json().then(function(dataListing) {
        if(dataListing.suppliers.length==0){
          $('#fs_Submit').prop('disabled', true);
        }else if(dataListing.suppliers.length>0){
          $('#fs_Submit').prop('disabled', false);
        }
        let optionSupplierHtml = '';
        for (let supplier of dataListing.suppliers){
          optionSupplierHtml+= '<option value ='+supplier.id+'>'+supplier.name+'</option>';   
        }
        fs_supplier.innerHTML=  optionSupplierHtml;

      });
    });
  }
    $('#fs_submit').click( function(e) { 
      supplier_id = $('#fs_supplier option:selected').val()
      supplier_name = $('#fs_supplier option:selected').text()
      document.getElementById('fs_supplier_'+listing).innerHTML='<option value ='+supplier_id+'>'+supplier_name+'</option>';   
    $('#findSupplier').collapse("hide")
    e.preventDefault();
  })
})








$('#apsl_submit').click( function(e) { 
  storage_id =$('#storageId').text()
  listing_id=$('#sla_listing option:selected').val()
  var status = new Array();
  var tbl= $('#idTableAddListingInfo').find('table');
  var productInfo = {}
  var count=0
  tbl.find('tr').each(function(i, row){

    var $row = $(row)
    if($row.attr('id') !== undefined){
      count+=1
      infoEach={}
      infoEach['booking']=$row.find('input[name="booking"]').val()
      buyer = '#buyer_'+$row.attr('id')+ ' option:selected'
      infoEach['buyer']=$row.find(buyer).val()
      supplier_id='#fs_supplier_'+$row.attr('id')+' option:selected'

      infoEach['supplier_id']=$row.find(supplier_id).val()
      productInfo[$row.attr('id')]=infoEach
    }
  })

  $.ajax({
    data: JSON.stringify({
      "submit": 'addProductListing',
      "storage_id": storage_id,
      "listing_id":listing_id,
      "info":productInfo,
      "infoCount":count
    }),
    type: "post",
    url: "/storageAddListing/"+storage_id,
    contentType: "application/json"
  }) .done(function(data){
    if(data.status ==='fail'){
      alert("danger",data.status.reason)
    }else{
      window.location.href = "/storageCage/"+storage_id
    }
  }); 
  history.go(0)

});

$('#backStorage').click( function(e){
  storage_id =$('#storageId').text()
  window.location.href = "/storageCage/"+storage_id
})

/*

*/