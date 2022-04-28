
let addAreaButton = document.getElementById('addAreaButton');
let addLocButton = document.getElementById('addLocButton');
let addMainButton = document.getElementById('addMainButton');
let addArea = document.getElementById('addAreaId');
let addLocation = document.getElementById('addLocationId');
let addMain = document.getElementById('addMainId');

addMain.style.display = 'block';
addMainButton.style.display = 'none';
addAreaButton.style.display = 'none';

addMainButton.onclick = function(){
  addMain.style.display = 'block';
  addLocation.style.display = 'none'
  addArea.style.display = 'none';

  addMainButton.style.display = 'none'
  addLocButton.style.display='block'
  addAreaButton.style.display = 'none'; 
}

addLocButton.onclick = function(){
  addMain.style.display = 'none';
  addLocation.style.display='block'
  addArea.style.display = 'none';

  addMainButton.style.display = 'block';
  addLocButton.style.display='none'
  addAreaButton.style.display = 'block'
  
}

addAreaButton.onclick = function(){
  addMain.style.display = 'none';
  addLocation.style.display = 'none'
  addArea.style.display = 'block';
  
  addMainButton.style.display = 'block'
  addLocButton.style.display='none'
  addAreaButton.style.display = 'none';
}



$(document).on('click', '[data-dismiss="modal"]', function(){
  history.go(0)
})
