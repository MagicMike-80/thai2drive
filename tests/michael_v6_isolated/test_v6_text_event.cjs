// Read-only synthetic test of actual web functions. No app, network or DB.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'backend', 'webapp.py'), 'utf8');
function section(startMarker, endMarker) {
  const start = source.indexOf(startMarker);
  const end = source.indexOf(endMarker, start);
  assert.ok(start >= 0 && end > start, `missing ${startMarker}`);
  return source.slice(start, end);
}
const delivery = section('function _v6DeliverySession(', '\n// The entry button');
const consume = section('async function consumeQuestionAccess(', '\nfunction checkPaywall(');
const calls = [];
const ctx = {
  appLang: 'en', deviceId: 'synthetic-device', qIdx: 2, quizStartedAt: 'synthetic-run',
  isExamMode: false, currentCat: null, accessState: null, premium: false,
  isPremium: () => ctx.premium,
  atob: (value) => Buffer.from(value, 'base64').toString('binary'),
  api: async (method, endpoint, body) => { calls.push({ method, endpoint, body }); return { can_answer: true }; },
  t: (key) => key, toast: () => {}, loadAccessStatus: async () => {}, showPaywall: () => {},
  console: { warn: () => {} }
};
vm.createContext(ctx);
vm.runInContext(delivery + '\n' + consume, ctx, { timeout: 1000 });
const nonce = 'synthetic_nonce_123456789';
const payload = Buffer.from(JSON.stringify({ v: 1, nonce })).toString('base64url');
const token = payload + '.synthetic-signature'; // format test only, no server verification claimed

(async () => {
  assert.equal(await ctx.consumeQuestionAccess({id: 'ordinary'}), true);
  assert.equal(calls.at(-1).body.event_id, 'synthetic-device:ordinary:2:synthetic-run');
  assert.equal(await ctx.consumeQuestionAccess({id: 'synthetic', _v6_text_delivery: token}), true);
  assert.equal(calls.at(-1).body.event_id, 'v6:' + nonce);
  const firstEvent = calls.at(-1).body.event_id;
  assert.equal(await ctx.consumeQuestionAccess({id: 'synthetic', _v6_text_delivery: token}), true);
  assert.equal(calls.at(-1).body.event_id, firstEvent, 'a retry must keep the same idempotency key');
  const before = calls.length;
  assert.equal(await ctx.consumeQuestionAccess({id: 'synthetic', _v6_text_delivery: 'bad'}), false);
  assert.equal(calls.length, before, 'bad V6 binding must not call consume');
  ctx.premium = true;
  assert.equal(await ctx.consumeQuestionAccess({id: 'synthetic', _v6_text_delivery: token}), true);
  assert.equal(calls.length, before, 'existing premium short circuit must remain unchanged');
  console.log('PASS synthetic V6 event binding, retry and existing quiz/premium paths');
})().catch((error) => { console.error(error); process.exitCode = 1; });
