
//Remove Listing

$(document).on("click",'#proceed',function(elem){
  listing_id =$('#listing').text()
   $.ajax({
    data: JSON.stringify({
      "listing_id":listing_id,
      "submit": 'removeListing',
    }),
    type: "post",
    url: '/listing/remove',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/listing"
  }
    }); 
})


//Edit Listing
$(document).on("click",'#edit',function(elem){
  listing_id =$('#listing').text()
  newName =$('#areaNewName').val()
   $.ajax({
    data: JSON.stringify({
      "listing_id":listing_id,
      "newName":newName,
      "submit": 'editListing',
    }),
    type: "post",
    url: '/listing/edit',
    contentType: "application/json"
  }) .done(function(data){
  if(data.status ==='fail'){

  }else{
    window.location.href = "/listingind/"+listing_id
  }
    }); 
})