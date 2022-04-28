var supplier_selected_id
var supplier_selected_info

$(document).on("click",'[name="removeSupplier"]',function(elem){
  supplier_selected_id=$(this).attr('id')
  fetch('getSupplierInfo/' + supplier_selected_id).then(response=>{
  	response.json().then(data=>{
  		supplier_selected_info=data
  		if(data["product_storage_listing"]==0 && data["verify_product_storage_listing"]==0){
	  		$('#confirmationModalTitle').text('Remove supplier')
	  		$('#confirmationText').text('Are you sure you want to delete '+data["fullAddress"])
  		}else{
  			$('#confirmationModalTitle').text('Error')
	  		$('#confirmationText').text('A Listing and Product has already been assigned to this Supplier. Please contact IT to delete')
	  		$('#proceed').hide()
  		}
  		$('#confirmation').modal()
  	})
  }) 
})

$(document).on("click",'#closeModal',function(elem){
  $('#proceed').show()
})


$(document).on("click",'#proceed',function(elem){
  supplier_id =supplier_selected_id
   $.ajax({
    data: JSON.stringify({
      "supplier_id":supplier_id,
      "submit": 'removeSupplier',
    }),
    type: "post",
    url: '/supplier/remove',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/supplier"
  }
    }); 
})

$(document).on("click",'[name="editSupplier"]',function(elem){
  supplier_selected_id=$(this).attr('id')
  fetch('getSupplierInfo/' + supplier_selected_id).then(response=>{
    response.json().then(data=>{
      supplier_selected_info=data
      $('#addMainModal').modal()
      $('#addMainId').show()
      $('#all_buttons').hide()
      $('#main_form_state').hide()
      $('#main_form_suburb').hide()
      $('#main_form_address').hide()
      document.getElementById('infoForNewMain').style.display = 'none';

      $('#addMainLabel').text('Edit '+data.name)

      $('#formMainSubmit').hide()

      var newInput = document.createElement('INPUT')
      newInput.setAttribute("type","submit")
      newInput.id="editSupplierButton"
      newInput.classList.add("btn")
      newInput.classList.add("btn-outline-info")
      newInput.setAttribute("value","Save Edit")
      $('#main_form_submit').append(newInput)

      $('#name').val(data.name)
      $('#contact').val(data.contact)
      $('#website').val(data.website)
    })
  }) 
})

$(document).on("click",'#closeMainModal',function(elem){
   returnModalNoraml()
})

$(document).on("click",'#editSupplierButton',function(elem){
  
  type= 'supplier edit'
  dataSend = JSON.stringify({
      "submit": type,
      "newName": $('#name').val(),
      "newContact": $('#contact').val(),
      "newWebsite": $('#website').val(),
      "supplier_id":supplier_selected_id
   })
   $.ajax({
     data: dataSend,
     type: "post",
     url: "/supplier/edit",
     contentType: "application/json"
 }).done(function(data){
  if(data.status ==='fail'){

  }else{
    returnModalNoraml()
    window.location.href = "/supplier"
    
  }
    }); 
   
})

function returnModalNoraml(){
  setTimeout(function(){ 
    $('#addMainModal').modal('hide')
      $('#all_buttons').show()
      $('#main_form_state').show()
      $('#main_form_suburb').show()
      $('#main_form_address').show()
       document.getElementById('infoForNewMain').style.display = 'block';
      $('#formMainSubmit').show()
      $('#editSupplierButton').remove()
      $('#formMainSubmit').val('Add Suppliers')
      $('#name').val('')
      $('#contact').val('')
      $('#website').val('')
  }, 500);
      
}