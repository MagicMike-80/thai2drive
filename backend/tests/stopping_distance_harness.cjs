// Execute the actual shipped JavaScript offline; API fixtures come from traffic_math.
const assert = require('node:assert/strict');
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const elements = new Map();
let animated = 0, cancelled = 0, reduced = false;
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: '', textContent: '', hidden: true, disabled: false, style: {}, dataset: {},
    attrs: {}, children: [], clientWidth: id === 'stopRoad' ? 700 : 130,
    classList: {contains(){return false;}},
    setAttribute(k,v) {this.attrs[k]=v;},
    replaceChildren() {this.children=[];}, appendChild(e) {this.children.push(e);},
    animate(frames, options) {animated++;assert.equal(options.duration,2200);assert.equal(frames[2].transform,'translateX(493px)');return {cancel(){cancelled++;}};}
  });
  return elements.get(id);
}
const presets = [30,50,80,100,120].map(n=>Object.assign(element('speed'+n),{dataset:{speed:String(n)}}));
const conditions = ['dry','wet','snow','ice'].map(n=>Object.assign(element('condition'+n),{dataset:{condition:n}}));
const gaps = [2,3].map(n=>Object.assign(element('gap'+n),{dataset:{seconds:String(n)}}));
global.UI={};global.appLang='no';
global.document={getElementById:element,createElement:()=>({textContent:'',children:[],appendChild(e){this.children.push(e);}}),querySelectorAll:s=>s==='[data-speed]'?presets:s==='[data-condition]'?conditions:gaps};
global.window={location:{href:'http://localhost/api/web',search:''},matchMedia:()=>({matches:reduced}),addEventListener(name,fn){this[name]=fn;}};
global.history={pushState(a,b,u){window.location.href=String(u);},replaceState(a,b,u){window.location.href=String(u);}};
global.showTab=tab=>{global.lastTab=tab;};global.t=key=>UI[key]?.[appLang] || '';
let requests=[];
global.fetch=url=>new Promise((resolve,reject)=>requests.push({url,resolve,reject}));
vm.runInThisContext(input.script);
function respond(pair, payloads=input.payloads) {pair.forEach((r,i)=>r.resolve({ok:true,json:async()=>payloads[i]}));}
async function settle(){await new Promise(r=>setImmediate(r));}
async function main(){
  openStopping();assert.equal(lastTab,'stopping');assert.match(window.location.href,/tool=stopping-distance/);
  let task=loadStopping(false), pair=requests.splice(0);
  assert.equal(element('stopRun').disabled,true);
  assert.match(pair[0].url,/speed=80&condition=dry&reaction=1/);
  assert.match(pair[1].url,/seconds=2/);
  appLang='th';renderStopping();assert.equal(element('stopStatus').textContent,UI.stop_loading.th);
  appLang='no';respond(pair);await task;
  assert.equal(element('stopTotalValue').textContent,'86,2 m');
  assert.equal(element('stopFollowingValue').textContent,'44,4 m');
  assert.equal(element('stopResults').hidden,false);
  assert.equal(element('stopStepList').children.length,4);
  assert.match(element('stopStepList').children[0].children[0].textContent,/80 ÷ 3,6 = 22,22 m\/s/);
  for(const lang of ['no','th','en']){appLang=lang;renderStopping();assert.equal(element('stopConditionNote').textContent,input.payloads[0].condition_info.note[lang]);}
  element('stopSteps').hidden=true;toggleStoppingSteps();assert.equal(element('stopSteps').hidden,false);assert.equal(element('stopStepsToggle').attrs['aria-expanded'],'true');toggleStoppingSteps();assert.equal(element('stopSteps').hidden,true);
  appLang='no';setStoppingSpeed(120);pair=requests.splice(0);assert.equal(stoppingState.speed,120);assert.equal(presets[4].attrs['aria-pressed'],'true');respond(pair);await settle();
  setStoppingCondition('ice');pair=requests.splice(0);assert.equal(stoppingState.condition,'ice');respond(pair);await settle();
  setStoppingGap(3);pair=requests.splice(0);assert.match(pair[1].url,/seconds=3/);respond(pair);await settle();
  // Newer request wins even when the older one finishes last.
  const old=loadStopping(false), oldPair=requests.splice(0);
  const latest=loadStopping(false), latestPair=requests.splice(0);
  const newer=structuredClone(input.payloads);newer[0].results.stopping_distance_m=999;
  respond(latestPair,newer);await latest;respond(oldPair);await old;
  assert.equal(stoppingState.data.results.stopping_distance_m,999);
  // HTTP and malformed JSON failures hide stale results, allow retry and translate status.
  task=loadStopping(false);pair=requests.splice(0);pair[0].resolve({ok:false});pair[1].resolve({ok:true});await task;
  assert.equal(element('stopResults').hidden,true);assert.equal(element('stopRun').disabled,false);
  appLang='th';renderStopping();assert.equal(element('stopStatus').textContent,UI.stop_error.th);
  task=loadStopping(false);pair=requests.splice(0);respond(pair,[{},{}]);await task;assert.equal(stoppingState.data,null);
  task=loadStopping(false);pair=requests.splice(0);pair[0].reject(new Error('offline'));pair[1].resolve({ok:true,json:async()=>input.payloads[1]});await task;assert.equal(stoppingState.statusKey,'stop_error');assert.equal(element('stopRun').disabled,false);
  task=loadStopping(false);pair=requests.splice(0);pair[0].resolve({ok:true,json:async()=>{throw new Error('invalid json');}});pair[1].resolve({ok:true,json:async()=>input.payloads[1]});await task;assert.equal(stoppingState.statusKey,'stop_error');assert.equal(element('stopResults').hidden,true);
  // Animation is suppressed for reduced motion and cancelled on exit.
  reduced=true;task=loadStopping(true);respond(requests.splice(0));await task;assert.equal(animated,0);
  reduced=false;task=loadStopping(true);respond(requests.splice(0));await task;assert.equal(animated,1);
  closeStopping();assert.equal(cancelled,1);assert.equal(lastTab,'home');assert.doesNotMatch(window.location.href,/tool=/);
  window.location.search='?tool=stopping-distance';window.popstate();assert.equal(lastTab,'stopping');window.location.search='';window.popstate();assert.equal(lastTab,'home');
  window.location.href='http://localhost/api/web?tool=stopping-distance';clearStoppingUrl();assert.doesNotMatch(window.location.href,/tool=/);
  task=loadStopping(true);pair=requests.splice(0);deactivateStopping();respond(pair);await task;assert.equal(animated,1);
  console.log('JavaScript stopping-distance behaviors: PASS');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
