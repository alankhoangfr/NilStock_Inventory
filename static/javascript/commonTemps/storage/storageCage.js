


$('#backStorage').click( function(e){
  storage_id =$('#storageId').text()
  window.location.href = "/storageCage/"+storage_id
})


//REMOVE LISTING

$('#rl_submit').click( function(e) { 
  listing_id=$('#rl_listing option:selected').val()
  storage_id =$('#storageId').text()

   $.ajax({
       data: JSON.stringify({
          "submit": 'listingAdd',
          "storage_id": storage_id,
          "listing_id":listing_id
       }),
       type: "post",
       url: "/storageListingRemove",
       contentType: "application/json"
   })
   .done(function(data){
    if(data.status ==='fail'){
      $('#errorAlertArea').show();
      $('#successAlertArea').hide();
      window.setTimeout(function(){ $('#errorAlertArea').hide(); }, 3000); 
    }else{
      window.location.href = "/storageCage/"+storage_id
    }
    history.go(0)

     
   })
  
});


//REMOVE AND ADD PRODUCTS

//ADD PRODUCTS
function populateProduct(product_select,response){
  response.json().then(function(dataProducts) {
    if(dataProducts.productData.length==0){
      $('#apsl_submit').prop('disabled', true);
    }else if(dataProducts.productData.length>0){
      $('#apsl_submit').prop('disabled', false);
    }
    let optionNameHtml = '';
    for (let prod of dataProducts.productData){
      optionNameHtml+= '<option value ='+prod.id+'>'+prod.name+'</option>';   
    }
    product_select.innerHTML=  optionNameHtml;

  });
}



$('#searchSubmitProductAdd').click( function(e) { 
  storage_id =$('#storageId').text()
  let apsl_product =  document.getElementById('apsl_product');
  search=$('#searchingProductIdAdd').val()
  searchValue='all'
  if(search!=''){
    searchValue=search
  }
  fetch('/product/addToStorage/search/' + searchValue+'/'+storage_id).then(response => populateProduct(apsl_product,response) );
  e.preventDefault(); 
});

$('#clearSubmitProductAdd').click( function(e) { 
  storage_id =$('#storageId').text()
  let apsl_product =  document.getElementById('apsl_product');
  searchValue='all'
  fetch('/product/addToStorage/search/' + searchValue+'/'+storage_id).then(response => populateProduct(apsl_product, response) );
  $('#searching').val('')
  e.preventDefault(); 
  $('#searchingProductIdAdd').val('')
});



$('#apsl_submit').click( function(e) { 
  storage_id =$('#storageId').text()
  product_id = $('#apsl_product option:selected').val()
  quantity = $('#apsl_quantity').val()
  var status = new Array();
  var tbl= $('#idTableAdd').find('table');
  var listingInfo = {}
  tbl.find('tr').each(function(i, row){
    var $row = $(row)
    if($row.attr('id') !== undefined){
      infoEach={}
      infoEach['booking']=$row.find('input[name="booking"]').val()
      buyer = '#buyer_'+$row.attr('id')+ ' option:selected'
      infoEach['buyer']=$row.find(buyer).val()
      supplier_id='#fs_supplier_'+$row.attr('id')+' option:selected'

      infoEach['supplier_id']=$row.find(supplier_id).val()
      listingInfo[$row.attr('id')]=infoEach
    }
  })
  $.ajax({
    data: JSON.stringify({
      "submit": 'addProductListingStorage',
      "storage_id": storage_id,
      "info":listingInfo,
      "quantity":quantity,
      "product_id":product_id,
    }),
    type: "post",
    url: "/product/storage/listing/add",
    contentType: "application/json"
  }) .done(function(data){
    if(data.status ==='fail'){
    }else{
    }
  });
  history.go(0)

});

//REMOVE PRODUCTS

$('#searchSubmitProductRemove').click( function(e) { 
  storage_id =$('#storageId').text()
  let apsl_product =  document.getElementById('apsl_product');
  search=$('#searchingProductIdRemove').val()
  searchValue='all'
  if(search!=''){
    searchValue=search
  }
  fetch('/product/removeFromStorage/search/' + searchValue+'/'+storage_id).then(response => populateProduct(removeProductSelect,response) );
  e.preventDefault(); 
});

$('#clearSubmitProductRemove').click( function(e) { 
  storage_id =$('#storageId').text()
  let apsl_product =  document.getElementById('apsl_product');
  searchValue='all'
  fetch('/product/removeFromStorage/search/' + searchValue+'/'+storage_id).then(response => populateProduct(removeProductSelect, response) );
  $('#searching').val('')
  e.preventDefault(); 
  $('#searchingProductIdRemove').val('')
});

$('#removeProductButton').click( function(e) {
    storage_id =$('#storageId').text()
    product_id = $('#removeProductSelect option:selected').val()
    $.ajax({
    data: JSON.stringify({
      "submit": 'productStorageListingRemove',
      "storage_id": storage_id,
      "product_id":product_id,
    }),
    type: "post",
    url: "/product/storage/listing/remove",
    contentType: "application/json"
  }) .done(function(data){
    if(data.status ==='fail'){
    }else{
    }
  });
  history.go(0)
})



//Find Supplier
function populateArea(responseArea){
  responseArea.json().then(function(dataArea) {
    let optionAreaHtml = '';
    for (let locArea of dataArea.locations){
      optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
    }
    fs_area.innerHTML=  optionAreaHtml;

  });``
}



function populateListing(responseListing){
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
}

  $(document).on("click",' .btn_supplier',function(elem){
    let listing = $(this).attr('id')
    let product_id = ''
    let fs_area =  document.getElementById('fs_area');
    let fs_state =  document.getElementById('fs_state');
    let fs_supplier =  document.getElementById('fs_supplier');

    fs_state.onchange = function(){
      state = $('#fs_state option:selected').val()
      fetch('/locations/' + state+'/area').then(responseArea=> populateArea(responseArea) );
      fetch('/supplier/state/' + state).then(responseListing=> populateListing(responseListing)) 
    }

    fs_area.onchange = function(){
      area = $('#fs_area option:selected').val()
      fetch('/supplier/area/' + area).then(responseListing=> populateListing(responseListing) );
    }
    $('#fs_submit').unbind('click').click( function(e) { 
      supplier_id = $('#fs_supplier option:selected').val()
      supplier_name = $('#fs_supplier option:selected').text()
      
      if ($('#apsl_product option:selected').val() ==undefined){
        ending = listing.split('#').pop()
        document.getElementById(ending).innerHTML='<option value ='+supplier_id+'>'+supplier_name+'</option>';   
      }else{
        document.getElementById('fs_supplier_'+listing+product_id).innerHTML='<option value ='+supplier_id+'>'+supplier_name+'</option>';   
      }

      
    $('#findSupplier').collapse("hide")
    e.preventDefault();
  })
  })



//Remove Users 

$(document).on("click",'#removeUserSubmit',function(elem){
  user_id = $('#userRemovePossible option:selected').val()
  storage_id =$('#storageId').text()
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

//Add USERS

function populateUsers(responseUsers){
  responseUsers.json().then(function(data) {
    if(data.usersArray.length==0){
      $('#searchSubmitUser').prop('disabled', true);
    }else if(data.usersArray.length>0){
      $('#searchSubmitUser').prop('disabled', false);
    }
    let optionUserHtml = '';
    for (let user of data.usersArray){
      optionUserHtml+= '<option value ='+user.id+'>'+user.name+'</option>';   
    }
    document.getElementById('possibleStorage').innerHTML=  optionUserHtml;

  });
}


$('#searchSubmitUser').click( function(e) { 
  search=$('#searchingUserId').val()
  searchValue='all'
  if(search!=''){
    searchValue=search
  }
  storage_id =$('#storageId').text()
  fetch('/user/search/' + searchValue+'/'+storage_id).then(response => populateUsers(response) );
  e.preventDefault(); 
});

$('#clearSubmitUser').click( function(e) { 

  searchValue='all'
  storage_id =$('#storageId').text()
  fetch('/user/search/' + searchValue+'/'+storage_id).then(response => populateUsers(response) );
  $('#searching').val('')
  e.preventDefault(); 
});


$(document).on("click",'#addResponsibility',function(elem){
  user_id = $('#possibleUserAdd option:selected').val()
  storage_id =$('#storageId').text()
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

//Remove Storage

$(document).on("click",'#proceed',function(elem){
  storage_id =$('#storageId').text()
   $.ajax({
    data: JSON.stringify({
      "storage_id":storage_id,
      "submit": 'removeStorage',
    }),
    type: "post",
    url: '/storage/remove',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/storage"
  }
    }); 
})


//Edit Storage
$(document).on("click",'#edit',function(elem){
  storage_id =$('#storageId').text()
  newName =$('#areaNewName').val()
   $.ajax({
    data: JSON.stringify({
      "storage_id":storage_id,
      "newName":newName,
      "submit": 'editStorage',
    }),
    type: "post",
    url: '/storage/edit',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/storageCage/"+storage_id
  }
    }); 
})