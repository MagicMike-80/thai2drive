const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const server = fs.readFileSync(path.join(ROOT, 'backend', 'server.py'), 'utf8');
const webapp = fs.readFileSync(path.join(ROOT, 'backend', 'webapp.py'), 'utf8');

console.log('🧪 Verifying Phase 3 & Mobile UI contracts...');

// Phase 3 tests
assert(server.includes('ACCESS_GUEST_TOTAL_LIMIT = 5'), 'Quota limit 5');
assert(server.includes('ACCESS_REGISTERED_DAILY_LIMIT = 10'), 'Quota limit 10');
assert(server.includes('@api_router.post("/access/consume")'), 'Access consume server');
assert(webapp.includes("'/api/access/consume'"), 'Access consume webapp');
assert(webapp.includes('data-key="home_primary_action"'), 'Home primary action');
assert(webapp.includes('data-key="home_ask_michael"'), 'Home ask michael');
assert(webapp.includes('data-key="home_targeted"'), 'Home targeted');

console.log('✅ Phase 3 Contract: 100% PASS');

// Mobile & Image readability contracts
assert(webapp.includes('.tm-sign-card'), 'Sign card present');
assert(webapp.includes('.tm-media-card'), 'Media card present');

console.log('✅ Mobile UI & Readability Contract: 100% PASS');
