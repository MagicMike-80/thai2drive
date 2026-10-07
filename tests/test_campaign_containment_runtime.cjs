const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('backend/webapp.py', 'utf8');
const start = source.indexOf('function checkCampaignStatus()');
const end = source.indexOf('function _getMediaLangBadge', start);
for (const language of ['no', 'th', 'en']) {
  const banner = {style:{display:'flex'}};
  const modal = {style:{display:'flex'}};
  let prevented = false;
  const user = {is_premium:false, has_premium:false};
  const ctx = vm.createContext({user, appLang:language,
    document:{getElementById:id=>({homeCampaignBanner:banner,campaignModal:modal}[id])},
    fetch(){throw Error('Retired campaign must not send a request');},
    api(){throw Error('Retired campaign must not send a request');}
  });
  vm.runInContext(source.slice(start,end),ctx);
  ctx.checkCampaignStatus();
  ctx.openCampaignModal();
  assert.equal(ctx.submitCampaignRegistration({preventDefault(){prevented=true;}}),false);
  assert.equal(banner.style.display,'none');
  assert.equal(modal.style.display,'none');
  assert.equal(prevented,true);
  assert.deepEqual(user,{is_premium:false,has_premium:false});
  ctx.document.getElementById=()=>null;
  ctx.checkCampaignStatus();
  ctx.openCampaignModal();
  ctx.submitCampaignRegistration();
}
console.log('A1 inert campaign handlers passed (NO/TH/EN, stale and absent UI).');
