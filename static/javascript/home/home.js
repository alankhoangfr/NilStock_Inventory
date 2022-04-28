let state_select =  document.getElementById('state');
let area_select =  document.getElementById('area');
let suburb_select =  document.getElementById('suburb');
let storage_select =  document.getElementById('storageCage');
let listing_select =  document.getElementById('listing');

state_select.onchange = function(){
  state_id = $('#state option:selected').val() 
  fetch('/locations/' + state_id+'/area').then(function(responseSuburb) {
    responseSuburb.json().then(function(dataSuburb) {
      let optionAreaHtml = '<option value =0>All</option>'
      for (let locArea of dataSuburb.locations){
        optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
      }
      area_select.innerHTML=  optionAreaHtml;

    });
  });
  fetch('/storage/state/' + state_id).then(function(responseStorage) {
    responseStorage.json().then(function(dataStorage) {
      let optionStorageHtml = '<option value =0>All</option>'
      for (let stor of dataStorage.storages){
        optionStorageHtml+= '<option value ='+stor.id+'>'+stor.name+'</option>';   
      }
      storage_select.innerHTML=  optionStorageHtml;

    });
  });
  fetch('/listing/state/' + state_id).then(function(responseListing) {
    responseListing.json().then(function(dataListing) {
      let optionListing = '<option value =0>All</option>'
      for (let lists of dataListing.listings){
        optionListing+= '<option value ='+lists.id+'>'+lists.name+'</option>';   
      }
      listing_select.innerHTML=  optionListing;

    });
  });
}



area_select.onchange = function(){
  area_id = $('#area option:selected').val() 
  fetch('/locations/area/' + area_id+'/suburb').then(function(responseSuburb) {
    responseSuburb.json().then(function(dataSuburb) {
      let optionSuburbHtml = '<option value =0>All</option>'
      for (let locSuburb of dataSuburb.locations){
        optionSuburbHtml+= '<option value ='+locSuburb.id+'>'+locSuburb.suburb+'</option>';   
      }
      suburb_select.innerHTML=  optionSuburbHtml;

    });
  });
  fetch('/storage/area/' + area_id).then(function(responseStorage) {
    responseStorage.json().then(function(dataStorage) {
      let optionStorageHtml = '<option value =0>All</option>'
      for (let stor of dataStorage.storages){
        optionStorageHtml+= '<option value ='+stor.id+'>'+stor.name+'</option>';   
      }
      storage_select.innerHTML=  optionStorageHtml;

    });
  });
  fetch('/listing/area/' + area_id).then(function(responseListing) {
    responseListing.json().then(function(dataListing) {
      let optionListing = '<option value =0>All</option>'
      for (let lists of dataListing.listings){
        optionListing+= '<option value ='+lists.id+'>'+lists.name+'</option>';   
      }
      listing_select.innerHTML=  optionListing;

    });
  });
}

suburb_select.onchange = function(){
  suburb = $('#suburb option:selected').text() 

  fetch('/storage/suburb/' + suburb).then(function(responseStorage) {
    responseStorage.json().then(function(dataStorage) {
      let optionStorageHtml = '<option value =0>All</option>'
      for (let stor of dataStorage.storages){
        optionStorageHtml+= '<option value ='+stor.id+'>'+stor.name+'</option>';   
      }
      storage_select.innerHTML=  optionStorageHtml;

    });
  });
  fetch('/listing/suburb/' + suburb).then(function(responseListing) {
    responseListing.json().then(function(dataListing) {
      let optionListing = '<option value =0>All</option>'
      for (let lists of dataListing.listings){
        optionListing+= '<option value ='+lists.id+'>'+lists.name+'</option>';   
      }
      listing_select.innerHTML=  optionListing;

    });
  });
}




storage_select.onchange = function(){
  storage_id = $('#storageCage option:selected').val() 
  fetch('/storageInfo/' + storage_id).then(function(response) {
    response.json().then(function(data) {
      let optionStateHtml = '';
      for (let locState of data.state){
        optionStateHtml+= '<option value ='+locState.id+'>'+locState.name+'</option>';   
      }
      area_select.innerHTML=  optionStateHtml;

      let optionAreaHtml = '';
      for (let locArea of data.area){
        optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
      }
      area_select.innerHTML=  optionAreaHtml;

      let optionSuburbHtml = '';
      for (let locSuburb of data.suburb){
        optionSuburbHtml+= '<option value ='+locSuburb.id+'>'+locSuburb.name+'</option>';   
      }
      suburb_select.innerHTML=  optionSuburbHtml;

      let optionListingHtml = '';
      for (let locListing of data.listing){
        optionListingHtml+= '<option value ='+locListing[0]+'>'+locListing[1]+'</option>';   
      }
      listing_select.innerHTML=  optionListingHtml;
    });
  });
}

listing_select.onchange = function(){
  listing_id = $('#listing option:selected').val() 
  fetch('/listingInfo/' + listing_id).then(function(response) {
    response.json().then(function(data) {
      let optionStateHtml = '';
      for (let locState of data.state){
        optionStateHtml+= '<option value ='+locState.id+'>'+locState.name+'</option>';   
      }
      area_select.innerHTML=  optionStateHtml;

      let optionAreaHtml = '';
      for (let locArea of data.area){
        optionAreaHtml+= '<option value ='+locArea.id+'>'+locArea.name+'</option>';   
      }
      area_select.innerHTML=  optionAreaHtml;

      let optionSuburbHtml = '';
      for (let locSuburb of data.suburb){
        optionSuburbHtml+= '<option value ='+locSuburb.id+'>'+locSuburb.name+'</option>';   
      }
      suburb_select.innerHTML=  optionSuburbHtml;

      let optionListingHtml = '';
      for (let locStorages of data.storages){
        optionListingHtml+= '<option value ='+locStorages[0]+'>'+locStorages[1]+'</option>';   
      }
      storage_select.innerHTML=  optionListingHtml;
    });
  });
}

$('#search').click( function(e) { 
})