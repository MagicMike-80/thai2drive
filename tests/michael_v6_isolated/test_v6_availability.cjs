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
const context = {document:{getElementById:() => button}, token:null, _guestKey:null, appLang:'no',
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
  const entry = source.slice(source.indexOf('function ensureGuestDeviceId()'), source.indexOf('function openGuestRegistration()'));
  const storage = new Map();
  const crypto = require('node:crypto').webcrypto;
  let opened = 0, failed = 0;
  const guest = {window:{isSecureContext:true,crypto}, crypto, navigator:{}, deviceId:null,
    token:null, user:null, _guestKey:null, _ls:{get:k=>storage.get(k), set:(k,v)=>storage.set(k,v), remove:k=>storage.delete(k)},
    fetch:async()=>{throw new Error('offline');}, enterApp:()=>opened++, t:k=>k, toast:()=>failed++};
  vm.runInNewContext(entry, guest);
  await guest.enterGuest();
  assert.match(guest.deviceId, /^web_guest_(?!v6-)/, 'first visit retains ordinary guest access offline');
  assert.equal(guest._guestKey, null);
  assert.equal(opened, 1);
  storage.delete('t2d_guest_device_id');
  await guest.enterGuest();
  assert.equal(failed, 1, 'existing proof cannot be exchanged for fresh quota while offline');
  assert.equal(opened, 1);
  guest.fetch = async () => {
    guest.token = 'synthetic-account'; guest.deviceId = 'account-id';
    return {ok:true, json:async()=>({ready:true, device_id:'web_guest_v6-'+'a'.repeat(64)})};
  };
  await guest.enterGuest();
  assert.equal(guest.deviceId, 'account-id');
  assert.equal(guest._guestKey, null);
  assert.equal(opened, 1, 'a late guest handshake must not reopen the app as a guest');
  console.log('PASS V6 availability: closed by default, auth/language race and network failure');
})().catch(error => { console.error(error); process.exitCode = 1; });
