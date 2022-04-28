	
function getStocktakeTableInfo(){
	tableinfo=[]
	$('.table tr').each(function (i, row) {
		if($(this).attr('id') != undefined){
			info={}
			product_id =$(this).attr('id').split('_').pop()
			quantity=$(this).find('input[name ="quantity"]').val()
			info['product_id']=product_id
			info['quantity']=quantity
			listingInfo=[]
			$(row).find('input[name ="per_booking"]').each(function (){
				if($(this).attr('id') != undefined){
					perListing ={}
					listings = $(this).attr('id').split('listing_').pop()
					perListing['listing_id']=listings
					perListing['per_booking']=$(this).val()
					listingInfo.push(perListing)
				}
			})
			
			$(row).find('select[name ="supplier_select"]  option:selected').each(function (index){
				listingInfo[index]['supplier_id']=$(this).val() 
				
			})
			$(row).find('select[name ="buyer"]  option:selected').each(function (index){
				listingInfo[index]['buyer']=$(this).val() 				
			})
			info['listingInfo']=listingInfo
			tableinfo.push(info)
		}    
    });
    return tableinfo
}

function getShoppingTableInfo(){
	tableinfo=[]
	$('.table tr').each(function (i, row) {
		if($(this).attr('id') != undefined){
			info={}
			product_id =$(this).attr('id').split('_').pop()
			quantity=$(this).find('input[name ="shoppingQuantity"]').val()
			let status
			$(row).find('select[name ="status_selected"]  option:selected').each(function (index){
				info['status']=$(this).val()
			})
			info['product_id']=product_id
			info['quantity']=quantity	

			tableinfo.push(info)
		}    
    });
    return tableinfo
}

$(document).on("click",'button[name="buttonStocktake"]',function(elem){

	let submit=$(this).attr('id')
	let storage_id =$('#storageId').text()
	let comment =$('#comment').val()
	let tableinfo=[]
	let url=""
	let submitName=""
	$('button[name="buttonStocktake"]').attr('disabled','disabled');
  $('#spinnerSend').show()
	if(submit=="updateStocktakeVerify" || submit=="sendStocktake"||submit=="updateStocktake"){
		tableinfo=getStocktakeTableInfo()
		url="/update/stocktake/"
		submitName='stocktake'
	}
	else if(submit=="sendShopping"){
		tableinfo=getShoppingTableInfo()
		url="/update/shopping/"
		submitName='sendShopping'
	}else if(submit=="updateShoppingVerify"){
		tableinfo=getShoppingTableInfo()
		url="/update/shopping/"
		submitName='verifyShopping'
	}
    let verifyId=""
    if(submit=="updateStocktakeVerify" || submit=="updateShoppingVerify"){
     verifyId=$('h4[name="verifyInfo"]').attr('id')
    }

    $.ajax({
    data: JSON.stringify({
      "verifyId":verifyId,
      "submit": submitName,
      "storage_id": storage_id,
      "info":tableinfo,
      "comment":comment
    }),
    type: "post",
    url: url,
    contentType: "application/json"
	}) .done(function(data){
	if(data.status ==='fail'){
	  alert("danger",data.reason)
	  $('button[name="buttonStocktake"]').removeAttr('disabled');
    $('#spinnerSend').hide()
	}else{
	  window.location.href = "/storageCage/"+storage_id
	  $('button[name="buttonStocktake"]').removeAttr('disabled');
    $('#spinnerSend').hide()
	}
  }); 
    

})

$('#autoFill').click( function(e){

	let multipleInput = $('#inputNBoookings').val()
	if(multipleInput==""){
		multiple=0
	}else{
		multiple=parseInt(multipleInput)
	}
	$('.table tr').each(function (i, row) {
		if($(this).attr('id') != undefined){
			product_id =$(this).attr('id').split('_').pop()
			let total=0
			$(row).find('.per_booking').each(function (){
				if($(this).attr('id') != undefined){
					total+=parseInt($(this).text())*multiple
				}
			})
			$(row).find('input[name ="shoppingQuantity"]').each(function (index){
				$(this).val(total) 				
			})

		}    
    });
    $('#inputNBoookings').val("")
})

$('#autoFillStatus').click( function(e){

	let status = $('#autoFill_status_selected option:selected').val()
	
	$('.table tr').each(function (i, row) {
		if($(this).attr('id') != undefined){
			$(row).find('select[name ="status_selected"]').each(function (index){
				$(this).val(status) 				
			})

		}    
    });
})

$('#removeStocktake').click( function(e) { 
  verifyId=$('h4[name="verifyInfo"]').attr('id')
  storage_id1 =$('#storageId').text()
  fetch('/verification/stocktake/remove/'+verifyId).then(function(response) {
    response.json().then(function(data) {
      if(data["status"]=="success"){
        window.location.href = "/storageCage/"+storage_id1
      }
    });
  });
})


$('#removeShopping').click( function(e) { 
  verifyId=$('h4[name="verifyInfo"]').attr('id')
  storage_id1 =$('#storageId').text()
  fetch('/verification/shopping/remove/'+verifyId).then(function(response) {
    response.json().then(function(data) {
      if(data["status"]=="success"){
        window.location.href = "/storageCage/"+storage_id1
      }
    });
  });
})

