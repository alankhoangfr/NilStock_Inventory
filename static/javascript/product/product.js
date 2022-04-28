
let category =  document.getElementById('ap_category');
let subcategory =  document.getElementById('ap_subcategory');

category.onchange = function(){
  category_id = $('#ap_category option:selected').val() 
  fetch('/subcategory/' + category_id).then(function(response) {
    response.json().then(function(data) {
      let optionSubHtml = '';
      for (let sub of data.subcategoryData){
        optionSubHtml+= '<option value ='+sub.id+'>'+sub.name+'</option>';   
      }
      subcategory.innerHTML=  optionSubHtml;

    });
  });
}

