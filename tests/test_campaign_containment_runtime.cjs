const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('backend/webapp.py', 'utf8');
const start = source.indexOf('async function checkCampaignStatus()');
const end = source.indexOf('function _getMediaLangBadge', start);
assert(start >= 0 && end > start, 'campaign handlers must exist');

(async () => {
  for (const language of ['no', 'th', 'en']) {
    const banner = {style:{display:'none'}};
    const modal = {style:{display:'none'}};
    const remaining = {textContent:''};
    const user = {is_premium:false, has_premium:false, trial_used:false};
    let statusCalls = 0;
    let registrationOpens = 0;
    let prevented = false;
    const ctx = vm.createContext({
      user, token:null, appLang:language, campaignClaimPending:false,
      isPremium:()=>false,
      api:async () => {statusCalls++; return {success:true, is_active:true, remaining:3};},
      tf:(_key, args)=>String(args.remaining),
      openGuestRegistration:()=>registrationOpens++,
      document:{getElementById:id=>({homeCampaignBanner:banner,campaignModal:modal,cbRemainingText:remaining}[id] || null)}
    });
    vm.runInContext(source.slice(start,end),ctx);
    await ctx.checkCampaignStatus();
    assert.equal(banner.style.display,'flex');
    assert.equal(remaining.textContent,'3');
    assert.equal(statusCalls,1);
    ctx.openCampaignModal();
    assert.equal(registrationOpens,1,'guest must register before campaign claim');
    assert.equal(modal.style.display,'none');
    assert.equal(ctx.campaignClaimPending,true);
    assert.equal(await ctx.submitCampaignRegistration({preventDefault(){prevented=true;}}),false);
    assert.equal(prevented,true);
    assert.equal(user.is_premium,false);
    user.trial_used = true;
    await ctx.checkCampaignStatus();
    assert.equal(banner.style.display,'none','used trial must not show campaign banner');
    assert.equal(statusCalls,1,'used trial must not query campaign status');
  }
  console.log('Campaign guest gate and trial containment passed (NO/TH/EN).');
})().catch(error=>{console.error(error);process.exitCode=1;});
