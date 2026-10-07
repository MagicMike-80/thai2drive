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
