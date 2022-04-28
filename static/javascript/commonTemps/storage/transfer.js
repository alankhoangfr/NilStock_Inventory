$(document).on("change",'input[name="transfer"]',function(elem){
  let quantityChage = parseInt($(this).val())
  let idTransfer = $(this).attr('id')
  let productId = idTransfer.split('_')[0]
  let q1 = parseInt(idTransfer.split('_')[1])
  let q2 = parseInt(idTransfer.split('_')[2])
  let id1 = "#s1_"+productId
  let id2 = "#s2_"+productId
  $(id1).text(q1-quantityChage)
  $(id2).text(q2+quantityChage)
})


$(document).on("click",'button[name="buttonTransfer"]',function(elem){
	submit=$(this).attr('id')
	storage_id1 =$('#storageId').text()
	storage_id2 =$('#storageId2').text()
	comment =$('#comment').val()
	tableinfo=[]
  $('button[name="buttonTransfer"]').attr('disabled','disabled');
  $('#spinnerSend').show()
	$('.table tr').each(function (i, row) {
		if($(this).attr('id') != undefined){
			info={}
			product_id =$(this).attr('id').split('_').pop()
			let id1 = "#s1_"+product_id
  			let id2 = "#s2_"+product_id
			quantity=$(this).find('input[name ="quantity"]').val()
			info['product_id']=product_id
			info['quantity1']=$(id1).text()
			info['quantity2']=$(id2).text()
			tableinfo.push(info)
		}    
    });
    verifyId=""
    if(submit=="updateTransferVerify"){
     verifyId=$('h2[name="verifyInfo"]').attr('id')
    }
    $.ajax({
    data: JSON.stringify({
      "verifyId":verifyId,
      "submit": 'transfer',
      "storage_id1": storage_id1,
      "storage_id2": storage_id2,
      "info":tableinfo,
      "comment":comment
    }),
    type: "post",
    url: "/update/transfer/",
    contentType: "application/json"
	}) .done(function(data){
	if(data.status ==='fail'){
    $('#spinnerSend').hide()
    $('button[name="buttonTransfer"]').removeAttr('disabled');
	  alert("danger",data.status.reason)
	}else{
	  window.location.href = "/storageCage/"+storage_id1
    $('button[name="buttonTransfer"]').removeAttr('disabled');
    $('#spinnerSend').hide()
	}
  }); 
    

})

$('#removeTransfer').click( function(e) { 
  verifyId=$('h4[name="verifyInfo"]').attr('id')
  storage_id1 =$('#storageId').text()
  fetch('/verification/transfer/remove/'+verifyId).then(function(response) {
    response.json().then(function(data) {
      if(data["status"]=="success"){
        window.location.href = "/storageCage/"+storage_id1
      }
    });
  });
})