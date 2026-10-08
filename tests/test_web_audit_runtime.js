const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../backend/webapp.py'), 'utf8');
function fn(name) {
  let start = source.indexOf('function ' + name + '(');
  assert(start >= 0, name);
  if (source.slice(start - 6, start) === 'async ') start -= 6;
  const tail = source.slice(start);
  const end = tail.slice(1).search(/\n(?:async )?function /);
  return end < 0 ? tail : tail.slice(0, end + 1);
}
for (const language of ['no', 'th', 'en']) {
  const ctx = vm.createContext({appLang: language});
  vm.runInContext(fn('historyAnswerForLanguage'), ctx);
  vm.runInContext(fn('accessEndMessage'), ctx);
  ctx.accessState = {can_answer:false,message:{no:'Norsk',th:'ไทย',en:'English'}};
  const translated = {no:'Norsk', th:'ไทย', en:'English'};
  assert.equal(ctx.accessEndMessage(), translated[language]);
  ctx.accessState.message = {other:'Wrong'};
  assert.equal(ctx.accessEndMessage(), '');
  const result = ctx.historyAnswerForLanguage({question_text:'Norsk snapshot', explanation:'Norsk', question_obj:{question:translated, explanation:translated}});
  assert.equal(result.question_text, translated[language]);
  assert.equal(result.explanation, translated[language]);
  assert.equal(ctx.historyAnswerForLanguage({question_text:'Unlabelled legacy'}).question_text, '');
  assert.equal(ctx.historyAnswerForLanguage({question_text:'Known', language}).question_text, 'Known');
  assert.equal(ctx.historyAnswerForLanguage({question_text:'Wrong', language:'other'}).question_text, '');
  assert.equal(ctx.historyAnswerForLanguage({question_obj:{question:{other:'Wrong'}}}).question_text, '');
}
let ended = 0, paywallChecked = 0, rendered = 0;
const quiz = vm.createContext({
  stopAllSpeech(){}, closeMichaelQuizCoach(){}, _aiPanelTimer:null, _reviewMode:false, _answerPending:false,
  isExamMode:false, qAnswered:true, qIdx:4, questions:Array(10), _sessionAnswers:Array(5),
  quizTransitionBlocked:()=>false, isPremium:()=>false, accessState:{can_answer:false}, FREE_LIMIT:5,
  showEnd(){ended++;}, checkPaywall(){paywallChecked++;return true;}, renderQuestion(){rendered++;},
  document:{querySelector:()=>null}
});
vm.runInContext(fn('nextQ'), quiz);
quiz._answerPending = true;
quiz.nextQ();
assert.equal(quiz.qIdx, 4, 'cannot advance while quota response is pending');
quiz._answerPending = false;
quiz.nextQ();
assert.equal(ended, 1, 'five answered questions finish before paywall');
assert.equal(paywallChecked, 0);
quiz.accessState = {can_answer:true}; quiz.qIdx = 1;
quiz.nextQ();
assert.equal(rendered, 1, 'remaining allowance continues quiz');
quiz.isExamMode = true; quiz.qIdx = 1; quiz.accessState = {can_answer:false};
quiz.nextQ();
assert.equal(ended, 1, 'exam is not ended by practice quota');

const endNodes = {};
const results = vm.createContext({
  stopAllSpeech(){},stopExamTimer(){},showScreen(){},isExamMode:false,questions:Array(10),
  _sessionAnswers:Array(5),qScore:3,token:null,deviceId:null,accessState:{can_answer:false},
  _buildDebrief:()=>({heading:'Done',body:'Practice'}),tf:(_key,args)=>args.correct+'/'+args.total,
  accessEndMessage:()=> 'Create an account',
  document:{getElementById:id=>endNodes[id] || (endNodes[id]={style:{},classList:{remove(){}}})},
  console
});
vm.runInContext(fn('renderEndResult') + '\n' + fn('showEnd'), results);
results.showEnd();
assert.equal(endNodes.endScoreQuiet.textContent,'3/5', 'summary counts answers, not fetched questions');
assert.equal(endNodes.endRegisterBtn.style.display,'block');
assert.equal(endNodes.endRetryBtn.style.display,'none');

let handler, advanced = 0;
const keyboard = source.slice(source.indexOf('//  KEYBOARD')).split("window.matchMedia")[0];
const keys = vm.createContext({
  document:{addEventListener:(_event, callback)=>handler=callback, querySelector:()=>({id:'screenQuiz'}), querySelectorAll:()=>[]},
  qAnswered:true, nextQ:()=>advanced++
});
vm.runInContext(keyboard, keys);
for (const key of ['Enter', ' ', 'ArrowRight']) {
  handler({key, target:{closest:()=>({tagName:'BUTTON'})}, preventDefault(){throw Error('native button intercepted');}});
}
assert.equal(advanced, 0);
handler({key:'Enter',target:{closest:()=>null},preventDefault(){}});
assert.equal(advanced, 1, 'background shortcut still works');

let screen, authTab;
const elements = {topBar:{style:{}},bottomNav:{style:{}}};
const auth = vm.createContext({stopAllSpeech(){},stopExamTimer(){},showScreen:s=>screen=s,switchTab:t=>authTab=t,document:{getElementById:id=>elements[id]}});
vm.runInContext(fn('openGuestRegistration'), auth);
auth.openGuestRegistration();
assert.equal(screen,'screenAuth'); assert.equal(authTab,'register');
assert.equal(elements.bottomNav.style.display,'none');
assert(!source.includes('data-key="pw_best_value"'), 'unsubstantiated discount is not rendered');
(async function authMigrationChecks() {
  for (const action of ['doRegister', 'doLogin']) {
    let payload;
    const guestId = 'web_guest_12345678-1234-1234-1234-123456789012';
    const button = {};
    const ctx = vm.createContext({
      token:null, user:null, deviceId:guestId,clearAuthMessages(){},t:key=>key,
      showAuthError:message=>{throw Error(message);}, enterApp(){},
      _ls:{get:()=>guestId,set(){}},
      document:{getElementById:()=>({value:'test-value'}),querySelector:()=>button},
      api:async (_method,_route,body)=>{payload=body;return {token:'test-token',user:{id:'account-id'}};}
    });
    vm.runInContext(fn('guestDeviceForAuth') + '\n' + fn(action),ctx);
    await ctx[action]();
    assert.equal(payload.device_id,guestId,action+' migrates original guest before replacing identity');
    assert.equal(ctx.deviceId,'account-id');
    assert.equal(ctx.guestDeviceForAuth(),null,'authenticated identity cannot be sent as guest');
    ctx.token=null;ctx.deviceId='other-account';
    assert.equal(ctx.guestDeviceForAuth(),null,'unrelated id cannot be sent as guest');
  }
  console.log('Web audit runtime: history NO/TH/EN, quota finish, keyboard, signup migration and discount checks passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

// Exercise the COMPLETE language updater against the actual result-button markup.
// This catches late positional overwrites after the generic data-key pass.
const resultMarkup = source.slice(source.indexOf('<div class="end-btns">'), source.indexOf('<!-- ═══ PAYWALL SCREEN'));
const resultButtons = [...resultMarkup.matchAll(/<button\s+([^>]+)>(.*?)<\/button>/gs)].map(match => {
  const attrs = Object.fromEntries([...match[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(a => [a[1],a[2]]));
  return {attrs, textContent:match[2], style:{}, getAttribute:key=>attrs[key],
    set innerHTML(value){this.textContent=value;}};
});
const resultState = {screen:null, tab:null};
const bars = {topBar:{style:{}}, bottomNav:{style:{}}};
const resultLang = vm.createContext({
  appLang:'no', window:{console}, console,
  renderPremiumBanner(){}, renderPaywallSub(){}, renderPremiumPricing(){},
  stopAllSpeech(){}, stopExamTimer(){},
  showScreen(id){resultState.screen=id;}, switchTab(id){resultState.tab=id;},
  showTab(id){resultState.tab=id;}, consultMichaelFromExam(){resultState.tab='coach';},
  retryQuiz(){resultState.tab='retry';},
  document:{documentElement:{},
    getElementById:id=>resultButtons.find(b=>b.attrs.id===id)||bars[id]||null,
    querySelector(selector){return this.querySelectorAll(selector)[0]||null;},
    querySelectorAll(selector){
      if(selector==='[data-key]')return resultButtons;
      if(selector==='.end-btn-pri'||selector==='.end-btn-sec')
        return resultButtons.filter(b=>b.attrs.class.split(' ').includes(selector.slice(1)));
      return [];
    }
  }
});
vm.runInContext(source.slice(source.indexOf('var UI = {'),source.indexOf('\nfunction t(key)')),resultLang);
vm.runInContext(fn('t'),resultLang);
const updaterStart=source.indexOf('function applyUILang()');
vm.runInContext(source.slice(updaterStart,source.indexOf('\nvar catsLoaded',updaterStart)),resultLang);
vm.runInContext(fn('openGuestRegistration'),resultLang);
const actionContracts = [
  ['openGuestRegistration()', 'create_account', 'register'],
  ['consultMichaelFromExam()', 'result_michael_coach', 'coach'],
  ['retryQuiz()', 'result_retry', 'retry'],
  ["showTab('teacher')", 'result_michael', 'teacher'],
  ["showTab('home')", 'home', 'home'],
  ["showTab('cats')", 'pickcat', 'cats'],
];
for(const language of ['no','th','en','no']) {
  resultLang.appLang=language;
  resultLang.applyUILang();
  for(const [handler,key,destination] of actionContracts) {
    const button=resultButtons.find(b=>b.attrs.onclick===handler);
    assert(button,handler);
    assert.equal(button.textContent,resultLang.UI[key][language],`${language}: ${handler}`);
    resultState.tab=null; resultState.screen=null;
    vm.runInContext(button.attrs.onclick,resultLang);
    assert.equal(resultState.tab,destination,`${language}: actual inline handler`);
    if(destination==='register') assert.equal(resultState.screen,'screenAuth');
  }
}
console.log('Result actions: full applyUILang, NO→TH→EN→NO labels and all six handlers passed.');

// Switch a visible result repeatedly without saving, changing score or replacing
// the original answer snapshot. Exercise real translation and rendering code.
const dynamicNodes = {};
for (const id of ['screenEnd','endScoreQuiet','endHeading','endBody','endFocus',
  'endFocusTopic','endAccessHint','endExamErrorsContainer','endExamErrorsTitle','endExamErrorsList']) {
  dynamicNodes[id] = {textContent:'', innerHTML:'', style:{},
    classList:{contains:()=>true,add(){},remove(){}}};
}
const originalGet = resultLang.document.getElementById;
resultLang.document.getElementById = id=>dynamicNodes[id]||originalGet(id);
Object.assign(resultLang, {
  isExamMode:false, questions:Array(10), _sessionAnswers:Array(5), qScore:3,
  _topicErrors:{Vikeplikt:2}, _examErrors:[],
  accessState:{can_answer:false,message:{no:'NORSK KVOTE',th:'ไทยโควตา',en:'ENGLISH QUOTA'}},
  api(){throw Error('Language refresh must not write');},
  showEnd(){throw Error('Language refresh must not complete the attempt again');},
  escH:s=>String(s), pickStrict:value=>value[resultLang.appLang]||'',
});
for (const name of ['tf','accessEndMessage','topicLabel','_buildDebrief',
  'historyAnswerForLanguage','resultAnswerForLanguage','renderEndResult']) {
  vm.runInContext(fn(name),resultLang);
}
const translations = {no:'NORSK', th:'ภาษาไทย', en:'ENGLISH'};
const savedError = {language:'no',question_index:1,user_answer:'A',correct_answer:'B',
  question_text:'NORSK',explanation:'NORSK',user_answer_text:'NORSK',correct_answer_text:'NORSK',
  question_obj:{question:translations,explanation:translations,
    options:[{id:'A',text:translations},{id:'B',text:translations}]}};
const snapshot = JSON.stringify(savedError);
for (const exam of [false,true]) {
  resultLang.isExamMode=exam;
  resultLang._examErrors=[savedError];
  for (const language of ['no','th','en','no']) {
    resultLang.appLang=language;
    resultLang.applyUILang();
    const total=exam?10:5;
    assert.equal(dynamicNodes.endScoreQuiet.textContent,resultLang.tf('result_score',{correct:3,total}));
    assert.equal(dynamicNodes.endHeading.textContent,resultLang._buildDebrief(Math.round(300/total),total).heading);
    assert.equal(dynamicNodes.endBody.textContent,resultLang._buildDebrief(Math.round(300/total),total).body);
    assert.equal(dynamicNodes.endFocusTopic.textContent,resultLang.topicLabel('Vikeplikt'));
    assert.equal(dynamicNodes.endAccessHint.textContent,resultLang.accessState.message[language]);
    if(exam) {
      assert(dynamicNodes.endExamErrorsList.innerHTML.includes(translations[language]));
      for(const other of ['no','th','en'].filter(l=>l!==language))
        assert(!dynamicNodes.endExamErrorsList.innerHTML.includes(translations[other]));
    }
    assert.equal(resultLang.qScore,3);
    assert.equal(resultLang._sessionAnswers.length,5);
    assert.equal(JSON.stringify(savedError),snapshot,'render leaves saved history untouched');
  }
}
resultLang.appLang='th';
resultLang._examErrors=[{...savedError,question_obj:{}}];
resultLang.accessState.message={no:'NORSK'};
resultLang.applyUILang();
assert(!dynamicNodes.endExamErrorsList.innerHTML.includes('NORSK'),'missing translation never falls back to saved Norwegian');
assert.equal(dynamicNodes.endAccessHint.textContent,'');
assert.equal(dynamicNodes.endAccessHint.style.display,'none');
resultLang._examErrors=[];
resultLang.applyUILang();
assert.equal(dynamicNodes.endExamErrorsList.innerHTML,'');
assert.equal(dynamicNodes.endExamErrorsTitle.textContent,resultLang.t('exam_all_correct'));
console.log('Result language refresh: practice/exam NO→TH→EN→NO, missing translations, immutable score/history and no resave passed.');
const remapped = {...savedError,question_obj:{...savedError.question_obj,
  options:[{id:'A',text:{th:'ตัวเลือกหนึ่ง'}},{id:'B',text:{th:'ตัวเลือกสอง'}}],
  _shuffledOpts:{opts:[{id:'A',sourceId:'B'},{id:'B',sourceId:'A'}]}}};
assert.equal(resultLang.resultAnswerForLanguage(remapped).user_answer_text,'ตัวเลือกสอง');
assert.equal(resultLang.resultAnswerForLanguage(remapped).correct_answer_text,'ตัวเลือกหนึ่ง');
const oldShuffle = {...savedError,question_obj:{...savedError.question_obj,
  _shuffledOpts:{opts:[{id:'A'},{id:'B'}]}}};
for(const language of ['no','th','en']) {
  resultLang.appLang=language;
  assert.equal(resultLang.resultAnswerForLanguage(oldShuffle).user_answer_text,'');
  assert.equal(resultLang.resultAnswerForLanguage(oldShuffle).correct_answer_text,'');
}
resultLang.appLang='th';
vm.runInContext(fn('shuffleOpts'),resultLang);
const shuffled = resultLang.shuffleOpts([{id:'A',text:'first'},{id:'B',text:'second'}],'A');
for(const option of shuffled.opts) assert.equal(option.sourceId,option.text==='first'?'A':'B');
let coachDisplay;
Object.assign(resultLang,{setTimeout:callback=>callback(),switchTeacherSession(){},
  teacherSend:(_prompt,display)=>{coachDisplay=display;}});
vm.runInContext(fn('consultMichaelFromExamQuestion'),resultLang);
resultLang._examErrors=[savedError];
resultLang.consultMichaelFromExamQuestion(0);
assert(coachDisplay.includes(translations.th));
assert(!coachDisplay.includes(translations.no));
coachDisplay=null;
resultLang._examErrors=[{...savedError,question_obj:{}}];
resultLang.consultMichaelFromExamQuestion(0);
assert.equal(coachDisplay,null,'missing translated question cannot launch misleading coaching');

// Regression: real language-selector entry point must not complete/save again.
Object.assign(resultLang, {
  _ls:{set(){}}, syncAppLanguagePath(){}, _msOnLangChange(){},
  signsLoaded:false, catsLoaded:false, _videosCached:null, _podcastsCached:null,
  _signPanelData:null, resetTeacherForLanguage(){}, toast(){},
});
vm.runInContext(fn('setLang'), resultLang);
for (const exam of [false,true]) {
  resultLang.isExamMode=exam;
  resultLang._examErrors=[savedError];
  resultLang.accessState.message={no:'NORSK KVOTE',th:'ไทยโควตา',en:'ENGLISH QUOTA'};
  for (const language of ['no','th','en','no','no']) {
    resultLang.setLang(language);
    assert.equal(resultLang.appLang,language);
    assert.equal(dynamicNodes.endScoreQuiet.textContent,resultLang.tf('result_score',{correct:3,total:exam?10:5}));
    assert.equal(dynamicNodes.endAccessHint.textContent,resultLang.accessState.message[language]);
    assert.equal(resultLang.qScore,3);
    assert.equal(resultLang._sessionAnswers.length,5);
    assert.equal(JSON.stringify(savedError),snapshot);
  }
}
console.log('Actual setLang entry point: repeated NO/TH/EN switches preserve results without completion or writes.');
(async function transitionChecks() {
  let now=1000, consumes=0, focused=0;
  const answer={}; const body={};
  const next={disabled:false,getClientRects:()=>[{}],focus(){focused++;}};
  const ctx=vm.createContext({
    Date:{now:()=>now},_quizTransitionUntil:0,_answerPending:false,
    _reviewMode:false,_aiPanelTimer:null,isExamMode:false,qAnswered:true,qIdx:0,
    questions:[{}, {}, {}],_sessionAnswers:[],FREE_LIMIT:5,
    stopAllSpeech(){},closeMichaelQuizCoach(){},isPremium:()=>false,
    accessState:{can_answer:true},checkPaywall:()=>true,
    renderQuestion(){ctx.qAnswered=false;},
    consumeQuestionAccess:async()=>{consumes++;return false;},
    document:{activeElement:answer,body,querySelector:()=>null,getElementById:()=>next},
  });
  for(const name of ['quizTransitionBlocked','focusQuizNext','nextQ','selectAns'])
    vm.runInContext(fn(name),ctx);
  ctx.nextQ(); assert.equal(ctx.qIdx,1);
  for(const tick of [1100,1250,1500,1800]) {
    now=tick; ctx.nextQ(); await ctx.selectAns(answer,'A');
    assert.equal(ctx.qIdx,1); assert.equal(consumes,0); assert.equal(ctx.qAnswered,false);
  }
  now=2251; await ctx.selectAns(answer,'A');
  assert.equal(consumes,1,'intentional answer after quiet interval reaches access policy');
  assert.equal(ctx._answerPending,false);
  for(const language of ['no','th','en']) {
    ctx.appLang=language;ctx.document.activeElement=answer;
    ctx.focusQuizNext(answer,true);
  }
  assert.equal(focused,3,'visible Next reachable after focused answer in every language');
  ctx.document.activeElement={};ctx.focusQuizNext(answer,true);
  ctx.document.activeElement=answer;ctx.focusQuizNext(answer,false);
  next.disabled=true;ctx.focusQuizNext(answer,true);
  next.disabled=false;next.getClientRects=()=>[];ctx.focusQuizNext(answer,true);
  assert.equal(focused,3,'do not steal moved focus or focus a disabled/hidden Next');
  console.log('Next burst: no answer consumption during trailing taps; quiet-interval recovery and focus handoff passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
let preventedRepeats=0;
for (const key of ['Enter',' ']) handler({key,repeat:true,target:{closest:()=>({tagName:'BUTTON'})},preventDefault(){preventedRepeats++;}});
assert.equal(preventedRepeats,2,'held activation must prevent native clicks after focus transfers to Next');
assert.equal(advanced,1,'held activation must not advance');