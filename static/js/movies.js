var level = document.getElementById('level');
var levelCap = parseInt(level.getAttribute('data-level-cap'));
var curLevel = parseInt(level.getAttribute('data-level-current'));
var card = document.getElementById("card");

for(var i = 1; i <= levelCap; i++) {
  if(curLevel >= i) {
    level.innerHTML += '<div class="star current-level"></div>';
  }
  else {
    level.innerHTML += '<div class="star"></div>';
  }
}

card.addEventListener('click', function(e){
  e.stopPropagation();
  if(card.classList.contains('card--flipped')) {
    card.classList.add('card--unflip');
    setTimeout(function(){
      card.classList.remove('card--flipped', 'card--unflip');
    }, 500);
  }
  else {
    card.classList.add("card--flipped");
  }
});

