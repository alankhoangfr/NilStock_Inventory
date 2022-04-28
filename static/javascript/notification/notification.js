$('#submit').click( function(e){
  title=$('#title').val()
  content =$('#content').val()

   $.ajax({
       data: JSON.stringify({
          "submit": 'post',
          "title": title,
          "content":content
       }),
       type: "post",
       url: "/post/new",
       contentType: "application/json"
   })
   .done(function(data){
    if(data.status =='fail'){

    }else{
           
    }
    window.location.href = "/notification"
    $('#title').val('')
    $('#content').val('')
     
   })

})
/*
$(document).on('click', '[data-dismiss="modal"]', function(){
  history.go(0)
})
*/