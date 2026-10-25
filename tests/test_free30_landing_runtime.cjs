const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync('backend/landing.py','utf8');
const fn=source.slice(source.indexOf('  function renderPaywall(){'),source.indexOf('  function escapeHtml(s){'));
let cases=0;
for(const lang of ['no','th','en']) for(const search of ['?campaign=free30','?campaign=other','']) {
 const context={currentLang:()=>lang,barEl:{style:{}},nowEl:{},TOTAL:10,body:{},nextBtn:{},score:4,URLSearchParams,window:{location:{search}}};
 vm.runInNewContext(fn+';renderPaywall();',context);
 const href=context.body.innerHTML.match(/href="([^"]+)"/)[1];
 assert.equal(href,`/${lang}/app${search==='?campaign=free30'?search:''}`);
 assert.equal(context.nextBtn.disabled,true); cases++;
}
console.log(`${cases} real mini-quiz rendering cases passed`);
