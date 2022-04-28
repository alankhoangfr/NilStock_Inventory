$('#backListing').click( function(e){
  storage_id =$('#listing_id').text()
  window.location.href = "/listingind/"+storage_id
})

//Update BOokngs
$('.submitBookingUpdate').click(function(e){
  listing_id=$('#up_listing option:selected').val()
  booking=$('#up_bookings').val()
  comment=$('#up_comment').val()
  submit=$(this).attr('id')
  verifyId=""
  if(submit=="updateBookingSubmit"){
     verifyId=$('h2[name="verifyInfo"]').attr('id')
    }
    console.log(submit)
   $('.submitBookingUpdate').attr('disabled','disabled');
   $.ajax({
       data: JSON.stringify({
          "submit": 'updateBooking',
          "booking": booking,
          "listing_id":listing_id,
          "comment":comment,
          "verifyId":verifyId
       }),
       type: "post",
       url: "/update/updateBooking",
       contentType: "application/json"
   })
   .done(function(data){
    if(data.status ==='fail'){
      $('#errorAlertArea').show();
      $('#successAlertArea').hide();

      window.setTimeout(function(){ $('#errorAlertArea').hide(); }, 3000); 
    }else{

    }
    $('.submitBookingUpdate').removeAttr('disabled');
      history.go(0)
    //window.location.href = "/listingind/"+listing_id

     
   })
})

$('#removeUpdateBooking').click( function(e) { 
  verifyId=$('h4[name="verifyInfo"]').attr('id')
  listing_id =$('#listing_id').text()
  fetch('/verification/updateBooking/remove/'+verifyId).then(function(response) {
    response.json().then(function(data) {
      if(data["status"]=="success"){
        history.go(0)
        //window.location.href = "/listingind/"+listing_id
      }
    });
  });
})
