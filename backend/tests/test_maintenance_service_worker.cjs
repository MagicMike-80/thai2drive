const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('backend/service-worker.js','utf8');
const handlers = {};
const context = {self:{addEventListener:(name,fn) => handlers[name]=fn}, URL, console};
vm.createContext(context);
vm.runInContext(source, context);
for (const pathname of ['/bok','/bok/','/app','/app/no','/no/flipp-flopp','/api/maintenance/status']) {
  let intercepted = false;
  handlers.fetch({request:{method:'GET',url:'https://test.invalid'+pathname},respondWith:()=>{intercepted=true}});
  assert.equal(intercepted,false, `${pathname} must use network even if cached`);
}
console.log('Service worker: book, app, game and maintenance status bypass cache');
