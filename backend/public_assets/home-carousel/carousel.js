// Presentation enhancement: move the original buttons, never duplicate their IDs/actions.
var homeWheel = null;
var navigationWheel = null;

function carouselOffset(index, center, count) {
  var offset = (index - center + count) % count;
  return offset > count / 2 ? offset - count : offset;
}

function makeCarousel(host, buttons, vertical) {
  var state = {host:host, buttons:buttons, center:0, lastActive:null};
  var viewport = document.createElement('div');
  viewport.className = 'wheel-viewport';
  host.appendChild(viewport);
  buttons.forEach(function(button) {
    button.classList.add('wheel-card');
    viewport.appendChild(button);
  });
  function render() {
    var focused = buttons.indexOf(document.activeElement);
    buttons.forEach(function(button, index) {
      var offset = carouselOffset(index, state.center, buttons.length);
      var visible = Math.abs(offset) <= (vertical ? 2 : 1);
      button.dataset.wheelOffset = String(offset);
      button.classList.toggle('wheel-center', offset === 0);
      button.style.setProperty('--wheel-offset', offset);
      button.style.zIndex = String(5 - Math.abs(offset));
      button.hidden = !visible;
      button.tabIndex = Math.abs(offset) <= 1 ? 0 : -1;
      button.setAttribute('aria-hidden', String(!visible || Math.abs(offset) > 1));
    });
    // Tab order follows the visible position, including at the wrap boundary.
    buttons.slice().sort(function(a,b) {
      return Number(a.dataset.wheelOffset) - Number(b.dataset.wheelOffset);
    }).forEach(function(button) { viewport.appendChild(button); });
    if (focused !== -1) {
      var focusIndex = Math.abs(carouselOffset(focused,state.center,buttons.length)) > 1 ? state.center : focused;
      buttons[focusIndex].focus({preventScroll:true});
    }
    host.dataset.centerIndex = String(state.center);
  }
  state.select = function(index) {
    state.center = (index + buttons.length) % buttons.length;
    render();
  };
  state.move = function(step) { state.select(state.center + step); };
  [-1,1].forEach(function(step) {
    var arrow = document.createElement('button');
    arrow.type = 'button';
    arrow.className = 'wheel-arrow wheel-arrow-' + (step < 0 ? 'prev' : 'next');
    arrow.dataset.labelKey = step < 0 ? 'fc_previous' : 'fc_next';
    var d = vertical ? (step < 0 ? 'M6 15l6-6 6 6' : 'M6 9l6 6 6-6') : (step < 0 ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7');
    arrow.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + d + '"/></svg>';
    arrow.addEventListener('click', function() { state.move(step); });
    host.appendChild(arrow);
  });
  var suppressClickUntil = 0;
  host.addEventListener('click', function(event) {
    if (Date.now() < suppressClickUntil) {
      event.preventDefault(); event.stopImmediatePropagation(); return;
    }
    var button = event.target.closest('.wheel-card');
    var index = buttons.indexOf(button);
    if (index !== -1 && index !== state.center) {
      event.preventDefault(); event.stopImmediatePropagation(); state.select(index);
    }
  }, true);
  host.addEventListener('keydown', function(event) {
    var previous = vertical ? 'ArrowUp' : 'ArrowLeft';
    var next = vertical ? 'ArrowDown' : 'ArrowRight';
    if (event.key === previous || event.key === next) {
      event.preventDefault(); state.move(event.key === previous ? -1 : 1);
      buttons[state.center].focus({preventScroll:true});
    }
  });
  var gesture = null;
  // Mouse wheels and trackpads rotate the same cards as arrows and swipes.
  // Keep pinch-to-zoom native, and damp momentum to one card per deliberate step.
  var wheelTotal = 0, wheelLast = 0, wheelLockUntil = 0;
  viewport.addEventListener('wheel', function(event) {
    if (event.ctrlKey) return;
    var delta = vertical ? event.deltaY :
      (Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY);
    if (!delta || (vertical && Math.abs(event.deltaX) > Math.abs(delta))) return;
    event.preventDefault();
    var now = Date.now();
    if (now < wheelLockUntil) return;
    if (now - wheelLast > 180 || Math.sign(delta) !== Math.sign(wheelTotal)) wheelTotal = 0;
    wheelLast = now;
    wheelTotal += delta * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 200 : 1);
    if (Math.abs(wheelTotal) < 32) return;
    state.move(wheelTotal > 0 ? 1 : -1);
    wheelTotal = 0;
    wheelLockUntil = now + 360;
  }, {passive:false});
  viewport.addEventListener('pointerdown', function(event) {
    if (!event.isPrimary || event.button !== 0) return;
    gesture = {id:event.pointerId,x:event.clientX,y:event.clientY};
  });
  viewport.addEventListener('pointerup', function(event) {
    if (!gesture || gesture.id !== event.pointerId) return;
    var dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
    gesture = null;
    var distance = vertical ? dy : dx;
    var cross = vertical ? dx : dy;
    if (Math.abs(distance) < 28 || Math.abs(distance) <= Math.abs(cross)) return;
    suppressClickUntil = Date.now() + 400;
    state.move(distance < 0 ? 1 : -1);
  });
  viewport.addEventListener('pointercancel', function() { gesture = null; });
  viewport.addEventListener('pointerleave', function(event) {
    if (event.pointerType === 'mouse') gesture = null;
  });
  render();
  return state;
}

function carouselImage(button, filename, selector) {
  var old = button.querySelector(selector);
  var image = document.createElement('img');
  image.src = '/api/assets/home-carousel/' + filename;
  image.alt = '';
  image.width = 128; image.height = 128;
  image.className = 'wheel-image';
  image.draggable = false;
  if (old) old.replaceWith(image);
  else button.prepend(image);
}

function initHomeCarousels() {
  if (homeWheel) return;
  var home = document.getElementById('screenHome');
  var main = home.querySelector('.home-main-actions');
  var choices = Array.from(main.querySelectorAll(':scope > .home-main-choice'));
  var quiz = home.querySelector('.home-cta:not(.home-cta-exam)');
  var exam = document.getElementById('startExamBtn');
  var stopping = document.getElementById('stoppingHomeBtn');
  var lab = document.getElementById('trafikklabHomeBtn');
  var buttons = [choices[0],lab,quiz,exam,stopping,choices[1],choices[2],choices[3],choices[4],choices[5]];
  // Leave the original usable layout intact if a future shell changes its contract.
  if (buttons.some(function(button){return !button;}) || choices.length !== 6) return;
  quiz.querySelector('[data-key="home_primary_action"]').dataset.key = 'hc_daily';
  exam.querySelector('[data-key="home_exam_action"]').dataset.key = 'hc_exam';
  var files = [null,'trafikklab.webp','daglig-test.webp','ovingsprove.webp','stopplengde.webp',
    'videokurs.webp','mine-feil-skilt.webp','trafikkbegreper.webp','flipp-flopp.webp','sikkerhetskontroll.webp'];
  buttons.forEach(function(button,index) {
    button.type = 'button';
    if (files[index]) carouselImage(button,files[index],'.home-main-choice-icon,.tl-home-ico,.tesla-red');
    else button.querySelector('img').classList.add('wheel-image');
  });
  var host = document.createElement('div');
  host.id = 'homeFeatureWheel'; host.className = 'feature-wheel';
  host.setAttribute('role','group'); host.dataset.labelKey = 'home_choose_action';
  home.querySelector('.home-main-label').after(host);
  homeWheel = makeCarousel(host,buttons,true);
  // Keep the existing targeted-practice submenu outside the clipped wheel.
  main.classList.add('wheel-submenu');
  var nav = document.getElementById('bottomNav');
  var ids = ['bnHome','bnCats','bnHistory','bnTeacher','bnLibrary','bnSigns','bnStudybook','bnBookmarks','bnSettings'];
  var navFiles = ['nav-hjem','nav-kategorier','nav-historikk',null,'nav-videoer','nav-trafikkskilt','nav-studiebok','nav-bokmerker','nav-innstillinger'];
  var navKeys = ['home','cats','history',null,'library','signs','studybook','bookmarks','settings'];
  var navButtons = ids.map(function(id) { return document.getElementById(id); });
  navButtons.forEach(function(button,index) {
    button.type = 'button';
    if (!navFiles[index]) return;
    var icon = button.querySelector('.bn-icon');
    icon.replaceChildren();
    var image = document.createElement('img');
    image.src = '/api/assets/home-carousel/' + navFiles[index] + '.png';
    image.alt = ''; image.width = 28; image.height = 28; image.draggable = false;
    icon.appendChild(image);
    // applyUILang rebuilds the nav contents from this existing shared icon map.
    NAV_SVG[navKeys[index]] = image.outerHTML;
  });
  nav.classList.add('navigation-wheel');
  navigationWheel = makeCarousel(nav,navButtons,false);
  document.getElementById('bottomNavMoreBtn').hidden = true;
  document.getElementById('bottomNavMorePanel').hidden = true;
}

function syncCarouselNavigation(screenId) {
  if (!navigationWheel) return false;
  var screenButtons = {
    screenHome:'bnHome', screenCats:'bnCats', screenHistory:'bnHistory',
    screenTeacher:'bnTeacher', screenLibrary:'bnLibrary', screenSigns:'bnSigns',
    screenStudybook:'bnStudybook', screenBookmarks:'bnBookmarks', screenSettings:'bnSettings'
  };
  var openedButton = screenButtons[screenId];
  if (openedButton) {
    navigationWheel.buttons.forEach(function(button) {
      button.classList.toggle('active', button.id === openedButton);
    });
  }
  var selected = navigationWheel.buttons.findIndex(function(button) { return button.classList.contains('active'); });
  if (selected >= 0 && (openedButton || selected !== navigationWheel.lastActive)) navigationWheel.select(selected);
  navigationWheel.lastActive = selected;
  navigationWheel.buttons.forEach(function(button,index) {
    button.setAttribute('aria-current',index === selected ? 'page' : 'false');
  });
  return true;
}
