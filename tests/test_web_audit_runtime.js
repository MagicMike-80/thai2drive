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
  isPremium:()=>false, accessState:{can_answer:false}, FREE_LIMIT:5,
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
vm.runInContext(fn('showEnd'), results);
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
