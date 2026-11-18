// Synthetic UI readiness test; no network, accounts, or production data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../../backend/webapp.py'), 'utf8');
const start = source.indexOf('async function _refreshV6Availability()');
const end = source.indexOf('\nasync function loadTeacher()', start);
assert(start >= 0 && end > start);
const button = {hidden:false};
let available = false, called = 0, mutate = () => {};
const context = {document:{getElementById:() => button}, token:null, appLang:'no',
  fetch:async () => { called++; mutate(); return {ok:true, json:async () => ({available})}; }};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context);
(async () => {
  await context._refreshV6Availability();
  assert.equal(button.hidden, true);
  assert.equal(called, 0, 'no token means no status call');
  context.token = 'synthetic-token';
  await context._refreshV6Availability();
  assert.equal(button.hidden, true, 'unavailable is hidden');
  available = true;
  await context._refreshV6Availability();
  assert.equal(button.hidden, false, 'verified availability shows the button');
  mutate = () => { context.token = 'other-token'; };
  await context._refreshV6Availability();
  assert.equal(button.hidden, true, 'a stale response must not cross accounts');
  mutate = () => { context.appLang = 'th'; };
  await context._refreshV6Availability();
  assert.equal(button.hidden, true, 'a stale response must not cross languages');
  context.fetch = async () => { throw new Error('offline'); };
  await context._refreshV6Availability();
  assert.equal(button.hidden, true, 'network errors fail closed');
  console.log('PASS V6 availability: closed by default, auth/language race and network failure');
})().catch(error => { console.error(error); process.exitCode = 1; });
