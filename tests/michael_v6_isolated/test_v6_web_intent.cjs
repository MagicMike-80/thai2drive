// Synthetic browser-flow control. Extracts only the two web functions; no
// app import, network, database, credentials, or live traffic content.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const { TextEncoder } = require('node:util');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'backend', 'webapp.py'), 'utf8');
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'v6_synthetic_scenarios.json'), 'utf8'));
const start = source.indexOf('function _v6ClassifyIntent(');
const end = source.indexOf('\nfunction toggleSound(', start);
assert.ok(start >= 0 && end > start, 'V6 web functions must exist');

const calls = { payloads: [], headers: [], tabs: [], feedback: null, fail: false, random: 0 };
const sessionValues = new Map();
const context = {
  crypto: {getRandomValues: bytes => { bytes.fill(++calls.random); return bytes; }, subtle:webcrypto.subtle},
  TextEncoder,
  sessionStorage: {getItem:key => sessionValues.get(key) || null,
    setItem:(key,value) => sessionValues.set(key,value), removeItem:key => sessionValues.delete(key)},
  document: { getElementById: () => null, querySelectorAll: () => [] },
  _teacherUploadedImage: null, _teacherUploadedDoc: null, _teacherTyping: false,
  _teacherActiveSessionType: 'quiz', _teacherQuizSessionId: 'test-session',
  _teacherQuizConversationId: 'test-session', _teacherSessionId: 'normal',
  _teacherConversationId: 'normal', _teacherExplainLevel: 1,
  _teacherV6Context: { questionId: 'synthetic', deliveryToken: 'synthetic-token', sessionId: 'test-session', language: 'no' },
  appLang: 'no', user: null, token: 'synthetic-login', _guestKey:null,
  _teacherDeviceId: () => 'synthetic-device', t: (key) => key,
  toast: () => {}, _teacherClearMediaCards: () => {}, stopAllSpeech: () => {},
  showTab: (tab) => calls.tabs.push(tab), _teacherHideSuggestions: () => {},
  _teacherRemoveChips: () => {}, _teacherShowTyping: () => {}, _teacherHideTyping: () => {},
  _teacherAppendBubble: () => null, _teacherScrollToAnswerStart: () => {},
  _teacherLinkSignReferences: async () => {}, _teacherAppendMediaCards: () => [],
  _teacherResponseMedia: () => [], _teacherAppendSignCards: async () => {},
  _teacherClearDoc: () => {},
  fetch: async (_url, request) => {
    calls.payloads.push(JSON.parse(request.body));
    calls.headers.push(request.headers);
    if (calls.fail) throw new Error('synthetic network failure');
    return { ok: true, json: async () => ({ session_id: 'test-session', mode: 'v6_quiz_pilot', reply: 'synthetic', suggestions: calls.feedback ? [{v6_feedback: calls.feedback}] : [] }) };
  }
};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context, { timeout: 1000 });

(async () => {
  for (const [language, values] of Object.entries(fixture.languages)) {
    context.appLang = language;
    context._teacherV6Context.language = language;
    for (const [field, expected] of [['stuck', 'hint'], ['different_method', 'alternative'], ['answer_request', 'explain'], ['ambiguous', 'answer']]) {
      await context.teacherSend(values[field]);
      assert.equal(calls.payloads.at(-1).v6_intent, expected, `${language}: ${field}`);
      assert.equal(calls.headers.at(-1).Authorization, 'Bearer synthetic-login');
    }
  }
  context.appLang = 'en';
  context._teacherV6Context.language = 'en';
  for (const choice of ['open study book', 'min statistikk', 'fasit', 'what is the answer?']) {
    const before = calls.tabs.length;
    await context.teacherSend(choice, choice, 'v6_quiz_pilot', 'answer');
    assert.equal(calls.tabs.length, before, `choice must not navigate: ${choice}`);
    assert.equal(calls.payloads.at(-1).v6_intent, 'answer');
    assert.equal(calls.payloads.at(-1).v6_answer_text, choice);
  }
  calls.feedback = 'incorrect';
  calls.fail = true;
  await context.teacherSend('retry this answer');
  const retryId = calls.payloads.at(-1).v6_event_id;
  assert.equal([...sessionValues.values()].some(value => value.includes('retry this answer')), false,
    'pending session storage must not contain learner text');
  context._teacherV6Context.pendingAnswer = null; // simulate page state rebuilt after reload
  calls.fail = false;
  await context.teacherSend('retry this answer');
  assert.equal(calls.payloads.at(-1).v6_event_id, retryId, 'network retry must retain its event id');
  await context.teacherSend('retry this answer');
  assert.notEqual(calls.payloads.at(-1).v6_event_id, retryId, 'a later accepted attempt must have a new id');
  calls.feedback = 'unavailable';
  await context.teacherSend('uncertain storage response');
  const unavailableId = calls.payloads.at(-1).v6_event_id;
  calls.feedback = 'incorrect';
  await context.teacherSend('uncertain storage response');
  assert.equal(calls.payloads.at(-1).v6_event_id, unavailableId,
    'an unavailable reply must not be mistaken for a recorded event');
  await context.teacherSend('uncertain storage response');
  assert.notEqual(calls.payloads.at(-1).v6_event_id, unavailableId,
    'a confirmed answer clears the pending event');
  const beforeStorageFailure = calls.payloads.length;
  const originalSetItem = context.sessionStorage.setItem;
  context.sessionStorage.setItem = () => { throw new Error('synthetic storage unavailable'); };
  await context.teacherSend('storage failure answer');
  assert.equal(calls.payloads.length, beforeStorageFailure,
    'an answer must not be sent if its retry id cannot be stored');
  context.sessionStorage.setItem = originalSetItem;
  for (let count = 0; count < 4; count++) {
    await context.teacherSend('synthetic wrong option', 'synthetic wrong option', 'v6_quiz_pilot', 'answer');
    assert.equal('v6_hint_level' in calls.payloads.at(-1), false, 'client must not declare a verified history');
  }
  calls.feedback = 'unknown';
  await context.teacherSend('unclear');
  calls.feedback = 'correct';
  await context.teacherSend('synthetic correct option', 'synthetic correct option', 'v6_quiz_pilot', 'answer');
  context.token = null;
  await context.teacherSend('synthetic answer', 'synthetic answer', 'v6_quiz_pilot', 'answer');
  assert.equal('Authorization' in calls.headers.at(-1), false, 'guest must not invent an identity');
  context._teacherV6Context = null;
  await context.teacherSend('open study book');
  assert.equal(calls.tabs.at(-1), 'studybook', 'ordinary navigation must still work');
  console.log('PASS synthetic NO/TH/EN requests and explicit answer navigation safety');
})().catch((error) => { console.error(error); process.exitCode = 1; });
