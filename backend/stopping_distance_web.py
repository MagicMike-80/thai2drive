"""Web-only stopping-distance screen. Uses the existing math API and language system."""

CSS = r"""
.stop-home {width:100%;display:flex;align-items:center;justify-content:center;gap:14px;margin:0 0 16px;padding:16px;background:#102039;border:2px solid #00F5FF;border-radius:16px;color:#fff;cursor:pointer;font:inherit;text-align:left}
.stop-home strong,.stop-home small {display:block}.stop-home small{color:#bacce2;margin-top:4px}
.tesla-red {width:72px;height:38px;flex-shrink:0;background:url('/api/assets/stopping-distance-teslas-v1.png') center top/100% 200% no-repeat}
#screenStopping {padding:24px;overflow-y:auto;background:#081426;gap:18px}
.stop-header {display:flex;justify-content:space-between;align-items:center;gap:12px}.stop-header h1{font-size:26px;margin:0}
.stop-layout {display:grid;grid-template-columns:280px minmax(0,1fr);gap:20px}
.stop-controls,.stop-results,.stop-steps {background:#102039;border:1px solid #304e6e;border-radius:16px;padding:20px}
.stop-controls label,.stop-controls legend {display:block;margin-bottom:12px;font-weight:700}.stop-controls fieldset{border:0;padding:0;margin:22px 0}
.stop-speed-value{font-size:32px;display:block;margin-bottom:12px}.stop-controls input{width:100%;accent-color:#00b9e8}
.stop-buttons{display:flex;gap:6px;flex-wrap:wrap}.stop-button{border:1px solid #426080;border-radius:10px;background:#11273f;color:#fff;padding:12px;min-height:44px;font:inherit;cursor:pointer}
.stop-button[aria-pressed=true]{background:#006eaa;border-color:#00F5FF}.stop-button:focus-visible,.stop-home:focus-visible{outline:3px solid #00F5FF;outline-offset:3px}
.stop-run{width:100%;background:#ff861c;color:#111;font-weight:700;border:0;margin-top:12px}.stop-run:disabled{opacity:.6;cursor:wait}
.stop-road{position:relative;min-height:300px;border-radius:16px;overflow:hidden;background:linear-gradient(0deg,rgba(4,12,24,.55),transparent),url('/api/assets/stopping-distance-road-v1.png') center/cover}
.tesla-road{position:absolute;left:3%;bottom:80px;width:130px;height:65px;background:url('/api/assets/stopping-distance-teslas-v1.png') center bottom/100% 200% no-repeat;z-index:2}
.stop-track{position:absolute;left:8%;right:8%;bottom:54px;display:flex;height:12px;border-left:2px solid white;border-right:3px solid white}
.stop-reaction{background:#ff951e;width:26%;border-right:2px solid white}.stop-braking{background:#fa3358;flex:1}.stop-marker{position:absolute;right:5%;bottom:74px;background:#9f1830;border:2px solid white;border-radius:8px;padding:6px 10px;color:white;font-weight:700}
.stop-caption{position:absolute;bottom:12px;left:0;right:0;text-align:center;color:white;font-size:16px;background:#081426cc;padding:4px}
.stop-results{margin-top:16px}.stop-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.stop-metrics strong{display:block;font-size:26px;margin-top:6px}.stop-orange{color:#ffab4b}.stop-red{color:#ff6b86}.stop-total{color:#fff}
.stop-equation{font-size:22px;text-align:center;margin:18px 0}.stop-muted{color:#b8c9df;font-size:16px;line-height:1.5}.stop-follow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:18px 0}.stop-follow strong{font-size:22px}
.stop-button:hover:not(:disabled),.stop-home:hover{box-shadow:0 0 0 1px #00F5FF;filter:brightness(1.08)}
.stop-steps{margin-top:16px}.stop-steps ol{padding-left:24px;margin:0}.stop-steps li{padding:12px 0;border-bottom:1px solid #304e6e}.stop-steps li:last-child{border-bottom:0}.stop-steps code{display:block;margin-top:8px;font-size:18px;white-space:normal;color:#fff}.stop-status{min-height:22px;margin-top:12px}
@media(min-width:700px){#app.stopping-mode{width:min(1100px,96vw);max-width:none;margin:auto;border-radius:16px}#app.stopping-mode .flag-bg{display:none}}
@media(max-width:699px){#screenStopping{padding:16px}.stop-layout{grid-template-columns:1fr}.stop-header h1{font-size:22px}.stop-road{min-height:260px}.stop-metrics strong{font-size:22px}.tesla-road{width:100px;height:50px}.stop-controls fieldset{margin:16px 0}}
@media(prefers-reduced-motion:reduce){#app.stopping-mode{transition:none}}
"""

HOME = r"""<button class="stop-home" id="stoppingHomeBtn" onclick="openStopping()"><span class="tesla-red" aria-hidden="true"></span><span><strong data-key="stop_title"></strong><small data-key="stop_home_sub"></small></span></button>"""

SCREEN = r"""
<div class="screen" id="screenStopping">
  <div class="stop-header"><h1 data-key="stop_title"></h1><button class="stop-button" onclick="closeStopping()" data-key="backhome"></button></div>
  <div class="stop-layout">
    <section class="stop-controls">
      <label for="stopSpeed" data-key="stop_speed"></label><output class="stop-speed-value" id="stopSpeedValue" for="stopSpeed">80 km/h</output>
      <input id="stopSpeed" type="range" min="30" max="120" step="1" value="80" oninput="setStoppingSpeed(this.value)">
      <div class="stop-buttons" id="stopPresets">
        <button class="stop-button" onclick="setStoppingSpeed(30)" data-speed="30">30</button><button class="stop-button" onclick="setStoppingSpeed(50)" data-speed="50">50</button><button class="stop-button" onclick="setStoppingSpeed(80)" data-speed="80">80</button><button class="stop-button" onclick="setStoppingSpeed(100)" data-speed="100">100</button><button class="stop-button" onclick="setStoppingSpeed(120)" data-speed="120">120</button>
      </div>
      <fieldset><legend data-key="stop_surface"></legend><div class="stop-buttons" id="stopConditions">
        <button class="stop-button" onclick="setStoppingCondition('dry')" data-condition="dry" data-key="stop_dry"></button><button class="stop-button" onclick="setStoppingCondition('wet')" data-condition="wet" data-key="stop_wet"></button><button class="stop-button" onclick="setStoppingCondition('snow')" data-condition="snow" data-key="stop_snow"></button><button class="stop-button" onclick="setStoppingCondition('ice')" data-condition="ice" data-key="stop_ice"></button>
      </div></fieldset>
      <p class="stop-muted" data-key="stop_reaction_time"></p>
      <button class="stop-button stop-run" id="stopRun" onclick="loadStopping(true)" data-key="stop_show"></button>
      <div class="stop-status stop-muted" id="stopStatus" role="status" aria-live="polite"></div>
    </section>
    <section>
      <div class="stop-road" role="img" id="stopRoad"><div class="tesla-road" id="stopTesla" aria-hidden="true"></div><div class="stop-track"><div class="stop-reaction" id="stopReactionTrack"></div><div class="stop-braking"></div></div><span class="stop-marker" data-key="stop_point"></span><div class="stop-caption" data-key="stop_scale"></div></div>
      <div class="stop-results" id="stopResults" hidden>
        <div class="stop-metrics"><div class="stop-orange"><span data-key="stop_reaction"></span><strong id="stopReactionValue"></strong></div><div class="stop-red"><span data-key="stop_braking"></span><strong id="stopBrakingValue"></strong></div><div class="stop-total"><span data-key="stop_total"></span><strong id="stopTotalValue"></strong></div></div>
        <p class="stop-equation" id="stopEquation"></p><p class="stop-muted" id="stopConditionNote"></p>
        <div class="stop-follow"><span data-key="stop_follow"></span><button class="stop-button" data-seconds="2" onclick="setStoppingGap(2)">2 s</button><button class="stop-button" data-seconds="3" onclick="setStoppingGap(3)">3 s</button><strong id="stopFollowingValue"></strong></div>
        <button class="stop-button" id="stopStepsToggle" aria-expanded="false" aria-controls="stopSteps" onclick="toggleStoppingSteps()" data-key="stop_steps"></button>
        <div class="stop-steps" id="stopSteps" hidden><ol id="stopStepList"></ol></div>
        <p class="stop-muted" data-key="stop_estimate"></p>
      </div>
    </section>
  </div>
</div>
"""

SCRIPT = r"""
Object.assign(UI, {
  stop_title:{no:'Stopplengde',th:'ระยะหยุดรถ',en:'Stopping distance'},
  stop_home_sub:{no:'Se hvor bilen stopper',th:'ดูว่ารถหยุดตรงไหน',en:'See where the car stops'},
  stop_speed:{no:'Hastighet (km/t)',th:'ความเร็ว (กม./ชม.)',en:'Speed (km/h)'},
  stop_speed_unit:{no:'km/t',th:'กม./ชม.',en:'km/h'},
  stop_surface:{no:'Veiføre',th:'สภาพถนน',en:'Road conditions'},
  stop_dry:{no:'Tørr',th:'แห้ง',en:'Dry'},stop_wet:{no:'Våt',th:'เปียก',en:'Wet'},stop_snow:{no:'Snø',th:'หิมะ',en:'Snow'},stop_ice:{no:'Is',th:'น้ำแข็ง',en:'Ice'},
  stop_reaction_time:{no:'Reaksjonstid: 1 sekund',th:'เวลาปฏิกิริยา: 1 วินาที',en:'Reaction time: 1 second'},
  stop_show:{no:'Vis stopplengde',th:'แสดงระยะหยุดรถ',en:'Show stopping distance'},
  stop_point:{no:'Stopp',th:'หยุด',en:'Stop'},
  stop_reaction:{no:'Reaksjon',th:'ปฏิกิริยา',en:'Reaction'},stop_braking:{no:'Brems',th:'เบรก',en:'Braking'},stop_total:{no:'Totalt',th:'รวม',en:'Total'},
  stop_follow:{no:'Følgeavstand',th:'ระยะห่างจากรถคันหน้า',en:'Following distance'},
  stop_steps:{no:'Slik regner vi',th:'วิธีคำนวณ',en:'How we calculate'},
  stop_scale:{no:'Illustrasjon – skalaen tilpasses avstanden',th:'ภาพประกอบ – มาตราส่วนปรับตามระยะทาง',en:'Illustration – scale adapts to the distance'},
  stop_estimate:{no:'Veiledende beregning. Virkelig stopplengde varierer med dekk, føre og fører.',th:'การคำนวณโดยประมาณ ระยะหยุดจริงขึ้นอยู่กับยาง สภาพถนน และผู้ขับขี่',en:'Approximate calculation. Actual stopping distance varies with tyres, road conditions and driver.'},
  stop_loading:{no:'Beregner …',th:'กำลังคำนวณ …',en:'Calculating …'},
  stop_error:{no:'Kunne ikke beregne. Prøv igjen.',th:'คำนวณไม่ได้ กรุณาลองอีกครั้ง',en:'Could not calculate. Please try again.'}
});
var stoppingState = {speed:80,condition:'dry',seconds:2,data:null,following:null,request:0,animation:null,statusKey:''};
function stopEl(id){return document.getElementById(id);}
function stoppingNumber(value,precision){return new Intl.NumberFormat(appLang === 'no' ? 'nb-NO' : appLang === 'th' ? 'th-TH' : 'en-GB',{maximumFractionDigits:precision || 1}).format(value);}
function deactivateStopping(){++stoppingState.request;if(stoppingState.animation){stoppingState.animation.cancel();stoppingState.animation=null;}stoppingState.statusKey='';stopEl('stopRun').disabled=false;}
function openStopping(){var url=new URL(window.location.href);url.searchParams.set('tool','stopping-distance');history.pushState({},'',url);showTab('stopping');}
function clearStoppingUrl(){var url=new URL(window.location.href);if(url.searchParams.has('tool')){url.searchParams.delete('tool');history.replaceState({},'',url);}}
window.addEventListener('popstate',function(){if(document.getElementById('screenAuth').classList.contains('active'))return;showTab(new URLSearchParams(window.location.search).get('tool')==='stopping-distance'?'stopping':'home');});
function closeStopping(){deactivateStopping();var url=new URL(window.location.href);url.searchParams.delete('tool');history.replaceState({},'',url);showTab('home');}
function updateStoppingControls(){
  stopEl('stopSpeed').value=stoppingState.speed;
  stopEl('stopSpeedValue').textContent=stoppingState.speed+' '+t('stop_speed_unit');
  document.querySelectorAll('[data-speed]').forEach(function(b){b.setAttribute('aria-pressed',String(Number(b.dataset.speed)===stoppingState.speed));});
  document.querySelectorAll('[data-condition]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.condition===stoppingState.condition));});
  document.querySelectorAll('[data-seconds]').forEach(function(b){b.setAttribute('aria-pressed',String(Number(b.dataset.seconds)===stoppingState.seconds));});
}
function setStoppingSpeed(speed){stoppingState.speed=Math.min(120,Math.max(30,Number(speed)));updateStoppingControls();loadStopping(false);}
function setStoppingCondition(condition){if(['dry','wet','snow','ice'].indexOf(condition)<0)return;stoppingState.condition=condition;updateStoppingControls();loadStopping(false);}
function setStoppingGap(seconds){stoppingState.seconds=seconds===3?3:2;updateStoppingControls();loadStopping(false);}
function toggleStoppingSteps(){var panel=stopEl('stopSteps');panel.hidden=!panel.hidden;stopEl('stopStepsToggle').setAttribute('aria-expanded',String(!panel.hidden));}
function renderStopping(){
  updateStoppingControls();stopEl('stopStatus').textContent=stoppingState.statusKey?t(stoppingState.statusKey):'';var data=stoppingState.data;if(!data)return;
  var r=data.results;['Reaction','Braking','Total'].forEach(function(name,i){stopEl('stop'+name+'Value').textContent=stoppingNumber([r.reaction_distance_m,r.braking_distance_m,r.stopping_distance_m][i])+' m';});
  stopEl('stopEquation').textContent=stoppingNumber(r.reaction_distance_m)+' + '+stoppingNumber(r.braking_distance_m)+' = '+stoppingNumber(r.stopping_distance_m)+' m';
  stopEl('stopReactionTrack').style.width=(100*r.reaction_distance_m/r.stopping_distance_m)+'%';
  stopEl('stopConditionNote').textContent=data.condition_info.note[appLang] || '';
  stopEl('stopRoad').setAttribute('aria-label',t('stop_reaction')+' '+stoppingNumber(r.reaction_distance_m)+' m, '+t('stop_braking')+' '+stoppingNumber(r.braking_distance_m)+' m, '+t('stop_total')+' '+stoppingNumber(r.stopping_distance_m)+' m');
  stopEl('stopFollowingValue').textContent=stoppingState.following?stoppingNumber(stoppingState.following.results.following_distance_m)+' m':'';
  var list=stopEl('stopStepList');list.replaceChildren();data.steps.forEach(function(step){var li=document.createElement('li');li.textContent=step.label[appLang] || '';var formula=document.createElement('code');formula.textContent=step.formula.replace(/\d+(?:\.\d+)?/g,function(n){return stoppingNumber(Number(n),2);})+' = '+stoppingNumber(step.result,step.unit==='m/s'?2:1)+' '+step.unit;li.appendChild(formula);list.appendChild(li);});
}
async function loadStopping(animate){
  updateStoppingControls();var request=++stoppingState.request;
  if(stoppingState.animation){stoppingState.animation.cancel();stoppingState.animation=null;}
  stoppingState.statusKey='stop_loading';stopEl('stopResults').hidden=true;stopEl('stopRun').disabled=true;stopEl('stopStatus').textContent=t(stoppingState.statusKey);
  var speed=stoppingState.speed,condition=stoppingState.condition,seconds=stoppingState.seconds;
  try{
    var responses=await Promise.all([fetch('/api/math/stopping-distance?speed='+speed+'&condition='+condition+'&reaction=1'),fetch('/api/math/following-distance?speed='+speed+'&seconds='+seconds)]);
    if(responses.some(function(r){return !r.ok;}))throw new Error('math response');
    var payloads=await Promise.all(responses.map(function(r){return r.json();}));
    if(request!==stoppingState.request)return;
    if(!payloads[0].results || !Array.isArray(payloads[0].steps) || !payloads[1].results)throw new Error('math payload');
    stoppingState.statusKey='';stoppingState.data=payloads[0];stoppingState.following=payloads[1];renderStopping();stopEl('stopResults').hidden=false;
    if(animate && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      var road=stopEl('stopRoad'),car=stopEl('stopTesla');var travel=Math.max(0,road.clientWidth*.92-car.clientWidth-road.clientWidth*.03);
      var ratio=payloads[0].results.reaction_distance_m/payloads[0].results.stopping_distance_m;
      stoppingState.animation=car.animate([{transform:'translateX(0)',offset:0},{transform:'translateX('+travel*ratio+'px)',offset:.35},{transform:'translateX('+travel+'px)',offset:1}],{duration:2200,fill:'forwards',easing:'ease-out'});
    }
  }catch(error){if(request===stoppingState.request){stoppingState.statusKey='stop_error';stoppingState.data=null;stoppingState.following=null;stopEl('stopStatus').textContent=t(stoppingState.statusKey);}}
  finally{if(request===stoppingState.request)stopEl('stopRun').disabled=false;}
}
"""


def install(html: str) -> str:
    """Install isolated screen into the existing web shell; no mobile/payment changes."""
    return (html.replace('</style>', CSS + '\n</style>', 1)
            .replace('<div class="home-main-actions">', HOME + '\n<div class="home-main-actions">', 1)
            .replace('<div class="screen" id="screenCats">', SCREEN + '\n<div class="screen" id="screenCats">', 1)
            .replace('function t(key) {', SCRIPT + '\nfunction t(key) {', 1))
