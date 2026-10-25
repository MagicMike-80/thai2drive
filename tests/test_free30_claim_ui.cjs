const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const src = fs.readFileSync('backend/webapp.py', 'utf8');
const start = src.indexOf('async function checkCampaignStatus()');
const end = src.indexOf('function _getMediaLangBadge', start);
(async () => {
 for (const lang of ['no','th','en']) {
  const nodes = {homeCampaignBanner:{style:{display:'flex'}}, cbRemainingText:{textContent:'50'},campFeedback:{style:{}},campSubmitBtn:{},campaignModal:{style:{}}};
  let statusCalls=0, refreshes=0;
  const c={appLang:lang,user:{is_premium:false},token:'synthetic',campaignClaimPending:false,
   document:{getElementById:id=>nodes[id]},isPremium:()=>c.user.is_premium,
   api:async()=>{statusCalls++;return {success:true,remaining:49,is_active:true}},
   tf:(_k,args)=>String(args.remaining),t:k=>k,applyUILang:()=>{},
   fetch:async()=>({ok:true,json:async()=>({success:true,message:'ok'})}),
   refreshCurrentUser:async()=>{refreshes++;c.user={is_premium:true,trial_used:true}},
   renderPremiumBanner:()=>{},setTimeout:()=>{},console};
  vm.runInNewContext(src.slice(start,end),c);
  assert.equal(await c.submitCampaignRegistration(),true);
  assert.equal(refreshes,1);
  assert.equal(nodes.homeCampaignBanner.style.display,'none');
  assert.equal(statusCalls,0,'premium account must not show a new claim offer');
  assert.equal(nodes.campSubmitBtn.disabled,false);
  c.user=null;
  await c.checkCampaignStatus();
  assert.equal(nodes.cbRemainingText.textContent,'49');
  assert.equal(nodes.homeCampaignBanner.style.display,'flex');
 }
 console.log('3 language cases: successful claim hides stale banner; guest sees fresh count');
})().catch(e=>{console.error(e);process.exitCode=1});
