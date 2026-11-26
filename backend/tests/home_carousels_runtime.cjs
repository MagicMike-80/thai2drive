// Run the actual assembled web shell in a DOM, offline. jsdom is a test-only dependency.
const assert = require('node:assert/strict');
const {JSDOM} = require('jsdom');
const html = require('node:fs').readFileSync(0, 'utf8');
const dom = new JSDOM(html, {url:'http://localhost/app/no',runScripts:'outside-only',pretendToBeVisual:true});
const w = dom.window;
w.matchMedia = () => ({matches:false,addEventListener(){},removeEventListener(){}});
w.fetch = async () => ({ok:true,status:200,json:async()=>({}),text:async()=>''});
w.setInterval = () => 0;
w.setTimeout = () => 0;
w.HTMLElement.prototype.scrollIntoView = function(){};
w.alert = () => {};
for (const script of w.document.querySelectorAll('script:not([src])')) {
  // Suppress only startup networking/auth restoration. Test shipped functions below.
  let code = script.textContent;
  const start = code.indexOf('(async function init() {');
  if (start !== -1) {
    const end = code.indexOf('\n})();', start) + '\n})();'.length;
    code = code.slice(0,start) + code.slice(end);
  }
  w.eval(code);
}
w.initHomeCarousels();
const home = w.homeWheel, nav = w.navigationWheel;
assert.equal(home.buttons.length,10);
assert.equal(nav.buttons.length,9);
assert.equal(w.document.querySelectorAll('#homeFeatureWheel').length,1);
w.initHomeCarousels();
assert.equal(w.document.querySelectorAll('#homeFeatureWheel').length,1,'init is idempotent');
let opened = [];
home.buttons.forEach((b,i)=>{ b.onclick=()=>opened.push(i); });
nav.buttons.forEach((b,i)=>{ b.onclick=()=>opened.push('nav'+i); });
function visible(state){return state.buttons.filter(b=>!b.hidden);}
assert.equal(visible(home).length,5,'three full cards and two edge peeks');
assert.equal(home.buttons.filter(b=>b.tabIndex===0).length,3);
assert.equal(visible(nav).length,3);
home.buttons[1].click();
assert.equal(home.center,1); assert.deepEqual(opened,[],'side click must not open');
home.buttons[1].click(); assert.deepEqual(opened,[1],'center click opens once');
home.select(0); home.move(-1); assert.equal(home.center,9);
home.move(1); assert.equal(home.center,0);
for(let i=0;i<30;i++) home.move(1);
assert.equal(home.center,0);
nav.move(-1); assert.equal(nav.center,8);
nav.buttons[0].click(); assert.equal(nav.center,0);
nav.buttons[0].click(); assert.equal(opened.at(-1),'nav0');
home.buttons[0].focus();
home.buttons[0].dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true,cancelable:true}));
assert.equal(home.center,9); assert.equal(w.document.activeElement,home.buttons[9]);
function swipe(dx,dy,cancel=false){
  const viewport=home.host.querySelector('.wheel-viewport');
  const down=new w.Event('pointerdown',{bubbles:true});
  Object.assign(down,{pointerId:1,isPrimary:true,button:0,clientX:100,clientY:200,pointerType:'touch'});
  viewport.dispatchEvent(down);
  const up=new w.Event(cancel?'pointercancel':'pointerup',{bubbles:true});
  Object.assign(up,{pointerId:1,clientX:100+dx,clientY:200+dy}); viewport.dispatchEvent(up);
}
home.select(0); swipe(0,-80); assert.equal(home.center,1);
const count=opened.length; home.buttons[1].click(); assert.equal(opened.length,count,'swipe synthesized click suppressed');
swipe(90,2); assert.equal(home.center,1,'cross-axis gestures ignored');
swipe(0,80,true); assert.equal(home.center,1,'cancelled gestures ignored');
for(const lang of ['no','th','en']) {
  w.appLang=lang; w.applyUILang();
  for(const el of home.host.querySelectorAll('[data-key]')) {
    assert.equal(el.textContent,w.UI[el.dataset.key][lang]);
  }
  for(const arrow of w.document.querySelectorAll('.wheel-arrow')) {
    assert.equal(arrow.getAttribute('aria-label'),w.UI[arrow.dataset.labelKey][lang]);
  }
  for(const button of nav.buttons) {
    assert.ok(button.querySelector('.bn-icon img'),'nav asset survives language update');
  }
  assert.ok(home.buttons[0].querySelector('img').src.endsWith('/home-carousel/michael-ai-256.png'));
  for (const button of home.buttons) {
    assert.ok(button.querySelector('img.wheel-image'),'home image survives language update');
  }
}
nav.buttons.forEach(b=>b.classList.remove('active'));
nav.buttons[4].classList.add('active'); w.syncCarouselNavigation();
assert.equal(nav.center,4); assert.equal(nav.buttons[4].getAttribute('aria-current'),'page');
nav.move(1); w.syncCarouselNavigation(); assert.equal(nav.center,5,'refresh does not undo browsing');
const ids=Array.from(w.document.querySelectorAll('[id]'),el=>el.id);
for(const id of ['startExamBtn','targetPracticeToggle','mistakesHomeCount','targetPracticeMenu','stoppingHomeBtn','trafikklabHomeBtn']) {
  assert.equal(ids.filter(x=>x===id).length,1,'preserve unique original ID '+id);
}
assert.ok(!home.host.contains(w.document.getElementById('targetPracticeMenu')),'submenu is not clipped');
console.log('PASS: wheel wrap, select/open, swipe, cancellation, keyboard/focus, NO/TH/EN, persistent icons, original IDs, navigation sync');
dom.window.close();
