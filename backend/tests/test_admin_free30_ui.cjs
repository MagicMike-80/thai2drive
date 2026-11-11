const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('backend/admin.html', 'utf8');
// Parse the complete script as well as exercising the customer controls.
for (const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
const start = html.indexOf('let free30Customer = null;');
const end = html.indexOf('\n}', html.indexOf('async function activateFreePeriod()', start)) + 2;
function setup() {
  const nodes = Object.fromEntries(['email','days','result','count','activate','manual','search'].map(key=>[
    'free30-'+key, {value:key==='days'?'60':'learner@example.test',disabled:false,textContent:''}
  ]));
  const calls=[];
  const customer={email:'learner@example.test',user_id:'synthetic',name:'<img onerror=alert(1)>',
    eligible:true,manual_eligible:true,premium_active:false,free30_used:false,remaining_seats:50};
  const c={document:{getElementById:id=>nodes[id]},Intl,Date,Number,JSON,
    crypto:{randomUUID:()=> '00000000-0000-4000-8000-000000000001'},
    api:async(path,args)=>{calls.push([path,args]);return path.endsWith('/status')?{remaining:50,total_seats:50}:customer;}};
  vm.createContext(c);vm.runInContext(html.slice(start,end),c);
  return {c,nodes,calls,customer};
}
(async()=>{
  {
    const {c,nodes,customer}=setup();
    await c.refreshFree30Count();
    assert.equal(nodes['free30-count'].textContent,'FREE30 igjen: 50 av 50');
    await c.lookupFree30();
    assert.ok(nodes['free30-result'].textContent.includes(customer.name));
    assert.equal(nodes['free30-result'].innerHTML,undefined,'customer name stays plain text');
    let complete;c.api=()=>new Promise(resolve=>complete=resolve);
    const pending=c.lookupFree30();c.clearFree30();complete(customer);await pending;
    assert.equal(nodes['free30-manual'].disabled,true,'stale search cannot activate another account');
  }
  {
    const {c,nodes}=setup();await c.lookupFree30();
    let count=0,complete;c.api=()=>{count++;return new Promise(resolve=>complete=resolve);};
    const pending=c.activateFreePeriod();await c.activateFreePeriod();
    assert.equal(count,1,'double click submits only once');
    assert.equal(nodes['free30-email'].disabled,true);
    complete({premium_until:'2027-01-20T23:00:00+00:00'});await pending;
    assert.ok(nodes['free30-result'].textContent.includes('learner@example.test'));
    assert.equal(nodes['free30-manual'].disabled,true);
  }
  {
    const {c,nodes}=setup();await c.lookupFree30();const sent=[];
    c.api=async(_path,args)=>{sent.push(args.body);throw Error('network');};
    await c.activateFreePeriod();await c.activateFreePeriod();
    assert.equal(sent[0],sent[1],'retry preserves request id and days');
    assert.equal(nodes['free30-days'].disabled,true);
    c.clearFree30();assert.equal(nodes['free30-days'].disabled,false);
  }
  {
    const {c,nodes,calls}=setup();await c.lookupFree30();
    for(const days of ['0','366','1.5']) {nodes['free30-days'].value=days;await c.activateFreePeriod();}
    assert.equal(calls.length,1,'invalid periods never sent');
  }
  {
    const {c,nodes,customer}=setup();customer.eligible=false;customer.free30_used=true;
    customer.reason='FREE30 er allerede brukt';customer.remaining_seats=0;
    await c.lookupFree30();assert.equal(nodes['free30-activate'].disabled,true);
    assert.equal(nodes['free30-manual'].disabled,false);
    assert.equal(nodes['free30-count'].textContent,'FREE30 igjen: 0 av 50');
  }
  console.log('PASS: full script syntax; counter; plain-text customer; stale search; duplicate click; idempotent retry; day validation; sold-out campaign.');
})().catch(error=>{console.error(error);process.exitCode=1;});
