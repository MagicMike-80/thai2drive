const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const src = fs.readFileSync(process.env.T2D_TEST_WEBAPP || path.join(__dirname, '..', 'webapp.py'), 'utf8');
const start = src.indexOf('var maintenanceState =');
const end = src.indexOf('var PREMIUM_PRICING =', start);
assert(start > 0 && end > start);
const keys = ['maintenance_title','maintenance_message','maintenance_wait','maintenance_pause','maintenance_open','maintenance_confirm','maintenance_error'];
const translations = {};
for (const key of keys) {
  const match = src.match(new RegExp('^\\s*' + key + ':\\s*(\\{[^\\n]+\\}),', 'm'));
  assert(match, key);
  translations[key] = vm.runInNewContext('(' + match[1] + ')');
  for (const lang of ['no','th','en']) assert(translations[key][lang], `${key}/${lang}`);
}

const elements = Object.fromEntries(['maintenanceOverlay','maintenanceHeading','maintenanceMessage','ownerMaintenanceButton'].map(id => [id, {style:{}, textContent:'', disabled:false}]));
let server = {active:false, owner:false};
let changed = [];
let allowed = false;
const context = {
  document:{getElementById:id => elements[id]},
  appLang:'no', token:'test-token', _ls:{get:() => null},
  t:key => translations[key][context.appLang],
  confirm:() => allowed, toast:() => {},
  fetch:async (url, options) => {
    if (url.endsWith('/status')) return {ok:true, json:async () => ({...server})};
    changed.push(JSON.parse(options.body));
    server.active = changed.at(-1).active;
    return {ok:true};
  }
};
vm.createContext(context);
vm.runInContext(src.slice(start,end), context);
(async () => {
  for (const lang of ['no','th','en']) {
    context.appLang = lang;
    server = {active:true, owner:false};
    await context.refreshMaintenance();
    assert.equal(elements.maintenanceOverlay.style.display, 'flex');
    assert.equal(elements.maintenanceMessage.textContent, translations.maintenance_message[lang]);
    assert.equal(elements.ownerMaintenanceButton.style.display, 'none');
    server = {active:true, owner:true};
    await context.refreshMaintenance();
    assert.equal(elements.maintenanceOverlay.style.display, 'none');
    assert.equal(elements.ownerMaintenanceButton.textContent, translations.maintenance_open[lang]);
  }
  server = {active:false, owner:true};
  await context.refreshMaintenance();
  await context.toggleOwnerMaintenance();
  assert.equal(changed.length, 0, 'cancel must not activate');
  allowed = true;
  await context.toggleOwnerMaintenance();
  assert.deepEqual(changed[0], {active:true, confirmed:true});
  assert.equal(elements.ownerMaintenanceButton.textContent, translations.maintenance_open.en);
  await context.toggleOwnerMaintenance();
  assert.deepEqual(changed[1], {active:false, confirmed:false});
  server = {active:false, owner:false};
  await context.refreshMaintenance();
  assert.equal(elements.maintenanceOverlay.style.display, 'none');
  assert.equal(elements.ownerMaintenanceButton.style.display, 'none');
  console.log('Maintenance web UI: NO/TH/EN, owner, confirmation and reopening passed');
})().catch(err => { console.error(err); process.exitCode = 1; });
