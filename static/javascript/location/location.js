var location_selected_id
var location_selected_info

$(document).on("click",'[name="removeLocation"]',function(elem){
  location_selected_id=$(this).attr('id')
  fetch('getLocationInfo/' + location_selected_id).then(response=>{
  	response.json().then(data=>{
  		location_selected_info=data
  		if(data["status"]=="Empty"){
	  		$('#confirmationModalTitle').text('Remove Location')
	  		$('#confirmationText').text('Are you sure you want to delete '+data["fullAddress"])
  		}else{
  			$('#confirmationModalTitle').text('Error')
	  		$('#confirmationText').text('A Listing, Supplier or Storage Cage has already been assigned to this location. Please contact IT to delete')
	  		$('#proceed').hide()
  		}
  		$('#confirmation').modal()
  	})
  }) 
})

$(document).on("click",'#closeModal',function(elem){
	setTimeout(function(){ $('#proceed').show(); }, 500);

})


$(document).on("click",'#proceed',function(elem){
  location_id =location_selected_id
   $.ajax({
    data: JSON.stringify({
      "location_id":location_id,
      "submit": 'removeLocation',
    }),
    type: "post",
    url: '/location/remove',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/location"
  }
    }); 
})

$(document).on("click","#locationModalClose",function(elem){
  history.go(0)
})