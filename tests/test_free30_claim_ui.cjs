const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const src = fs.readFileSync('backend/webapp.py', 'utf8');
const start = src.indexOf('async function checkCampaignStatus()');
const end = src.indexOf('function _getMediaLangBadge', start);
const dictionaries = {};
for (const line of src.split('\n')) {
 const m = line.match(/^\s*(campaign_\w+):\s*(\{.*\}),?\s*$/);
 if (m) dictionaries[m[1]] = vm.runInNewContext('(' + m[2] + ')');
}
function setup(lang) {
 const nodes = Object.fromEntries(['homeCampaignBanner','cbRemainingText','campFeedback','campSubmitBtn','campaignModal','campRemainingText'].map(id=>[id,{style:{},textContent:''}]));
 let requests=0;
 const c={appLang:lang,user:{id:'synthetic-1',is_premium:false},token:'synthetic',campaignClaimPending:false,
  document:{getElementById:id=>nodes[id]},isPremium:()=>!!(c.user && c.user.is_premium),
  api:async()=>({success:true,remaining:2,is_active:true}),
  t:k=>dictionaries[k]?.[c.appLang] || '',tf:(k,a)=>c.t(k).replace('{remaining}',a.remaining),
  localeForLang:()=>({no:'nb-NO',th:'th-TH',en:'en-US'})[c.appLang],
  applyUILang:()=>c.renderCampaignFeedback(),openGuestRegistration:()=>{c.registerOpened=true},
  fetch:async()=>{requests++;return {ok:true,json:async()=>({success:true,premium_until:'2026-12-11T12:00:00Z',message:'DO NOT DISPLAY SERVER LANGUAGE'})}},
  renderPremiumBanner:()=>{},console};
 vm.runInNewContext(src.slice(start,end),c);
 return {c,nodes,requests:()=>requests};
}
(async()=>{
 for(const lang of ['no','th','en']) {
  let {c,nodes,requests}=setup(lang);
  await c.openCampaignModal();
  assert.equal(nodes.campSubmitBtn.disabled,false);
  assert.equal(nodes.campRemainingText.textContent,c.tf('campaign_desc',{remaining:2}));
  const first=c.submitCampaignRegistration();
  assert.equal(await c.submitCampaignRegistration(),false);
  assert.equal(await first,true); assert.equal(requests(),1);
  assert.equal(nodes.campSubmitBtn.disabled,true);
  assert.equal(c.user.is_premium,true);
  assert.equal(nodes.homeCampaignBanner.style.display,'none');
  assert.ok(nodes.campFeedback.textContent.startsWith(dictionaries.campaign_success_fallback[lang]));
  assert.ok(nodes.campFeedback.textContent.includes('→'));
  assert.ok(nodes.campFeedback.textContent.includes('12') || nodes.campFeedback.textContent.includes('Dec') || nodes.campFeedback.textContent.includes('des') || lang==='th');
  assert.ok(!nodes.campFeedback.textContent.includes('SERVER'));
  assert.equal(nodes.campaignModal.style.display,'flex','confirmation remains visible');
  c.appLang=lang==='th'?'en':'th';c.renderCampaignFeedback();
  assert.ok(nodes.campFeedback.textContent.startsWith(dictionaries.campaign_success_fallback[c.appLang]));
  await c.openCampaignModal();assert.equal(nodes.campFeedback.textContent,c.t('campaign_used'));
  assert.equal(await c.submitCampaignRegistration(),false);assert.equal(requests(),1);
  ({c,nodes}=setup(lang));c.api=async()=>({success:true,remaining:0,is_active:false});
  await c.openCampaignModal();assert.equal(nodes.campSubmitBtn.disabled,true);assert.equal(nodes.campFeedback.textContent,c.t('campaign_sold_out'));
  ({c,nodes}=setup(lang));c.api=async()=>{throw Error('offline')};await c.openCampaignModal();assert.equal(nodes.campSubmitBtn.disabled,true);
  ({c,nodes}=setup(lang));await c.openCampaignModal();c.fetch=async()=>{throw Error('offline')};await c.submitCampaignRegistration();assert.equal(c.user.is_premium,false);assert.equal(nodes.campSubmitBtn.disabled,false);
  ({c,nodes}=setup(lang));await c.openCampaignModal();let resolve;
  c.fetch=()=>new Promise(r=>resolve=r);let pending=c.submitCampaignRegistration();c.user={id:'other',is_premium:false};c.token='other-token';
  resolve({ok:true,json:async()=>({success:true,premium_until:'2026-12-11T12:00:00Z'})});
  assert.equal(await pending,false);assert.equal(c.user.is_premium,false);
  ({c,nodes}=setup(lang));c.user=null;await c.openCampaignModal();assert.equal(c.registerOpened,true);
  await c.checkCampaignStatus();assert.equal(nodes.homeCampaignBanner.style.display,'flex');
 }
 assert.ok(!src.includes('mailto:admin@thai2drive.no?subject=FREE30'));
 console.log('PASS NO/TH/EN: direct entry, count, durable dated confirmation, duplicate click, used trial, sold out, offline, language change, account isolation, guest registration.');
})().catch(e=>{console.error(e);process.exitCode=1});
