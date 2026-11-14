const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.env.T2D_TEST_ADMIN || 'backend/admin.html', 'utf8');
const start = html.indexOf('let maintenanceActive = false;');
const end = html.indexOf('\nfunction toast(', start);
assert(start > 0 && end > start);
const nodes = Object.fromEntries(['maintenance-owner','maintenance-owner-button','maintenance-owner-status'].map(id => [id, {style:{}, disabled:false, textContent:''}]));
let server = {owner:false, active:false}, allowed = false;
const calls = [];
const ctx = {document:{getElementById:id => nodes[id]}, token:'synthetic', confirm:() => allowed, toast:() => {},
  fetch:async () => ({ok:true, json:async () => ({...server})}),
  api:async (url, opts) => {calls.push(JSON.parse(opts.body)); server.active = calls.at(-1).active;}};
vm.createContext(ctx);
vm.runInContext(html.slice(start, end), ctx);
(async () => {
  await ctx.refreshMaintenance();
  assert.equal(nodes['maintenance-owner'].style.display, 'none');
  server.owner = true;
  await ctx.refreshMaintenance();
  assert.equal(nodes['maintenance-owner'].style.display, 'block');
  await ctx.toggleMaintenance();
  assert.equal(calls.length, 0);
  allowed = true;
  await ctx.toggleMaintenance();
  assert.deepEqual(calls[0], {active:true, confirmed:true});
  assert.equal(nodes['maintenance-owner-button'].textContent, 'Åpne kundetilgang');
  await ctx.toggleMaintenance();
  assert.deepEqual(calls[1], {active:false, confirmed:false});
  console.log('Maintenance admin UI: owner visibility, confirmation and reopening passed');
})().catch(err => {console.error(err); process.exitCode = 1;});
