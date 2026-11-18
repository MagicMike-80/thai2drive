// Synthetic DOM test of the existing V6 sender. No application server or real users.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.V6_PLAYWRIGHT_PATH || '../../tools/gstack/node_modules/playwright-core');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'backend', 'webapp.py'), 'utf8');
const start = source.indexOf('function _v6ClassifyIntent(');
const end = source.indexOf('\nfunction toggleSound(', start);
assert(start >= 0 && end > start);
const handler = source.slice(start, end);

(async () => {
  const browser = await chromium.launch({headless: true,
    executablePath: process.env.V6_CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    args: ['--disable-background-networking', '--disable-quic', '--host-resolver-rules=MAP * ~NOTFOUND']});
  const page = await browser.newPage();
  const requests = [];
  let failOnce = false;
  await page.route('**/*', async route => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.hostname !== '127.0.0.1') return route.abort();
    if (request.method() === 'GET') return route.fulfill({status: 200, contentType: 'text/html', body:
      '<!doctype html><html><body><div id="messages"></div><input id="teacherInput"><button id="teacherSendBtn">Send</button></body></html>'});
    if (url.pathname !== '/api/teacher/chat') return route.abort();
    const payload = request.postDataJSON();
    requests.push(payload);
    if (failOnce) { failOnce = false; return route.fulfill({status: 503, body: 'synthetic failure'}); }
    const feedback = payload.v6_intent === 'answer' ? 'incorrect' : 'guidance';
    return route.fulfill({json: {session_id: 'synthetic-session', mode: 'v6_quiz_pilot',
      reply: 'synthetic reply', suggestions: [{v6_feedback: feedback, question: 'Synthetic question'}, 'Red', 'Blue']}});
  });
  try {
    async function loadTestPage() {
      await page.goto('http://127.0.0.1/');
      await page.evaluate(() => {
      Object.assign(window, {
        _teacherUploadedImage: null, _teacherUploadedDoc: null, _teacherTyping: false,
        _teacherActiveSessionType: 'quiz', _teacherQuizSessionId: 'synthetic-session',
        _teacherQuizConversationId: 'synthetic-session', _teacherExplainLevel: 1,
        _teacherV6Context: {questionId:'synthetic', deliveryToken:'synthetic-token',
          actorBinding:'synthetic-binding', sessionId:'synthetic-session', language:'no'},
        appLang:'no', user:null, token:'synthetic-token', lastToast:'',
        _teacherDeviceId: () => 'synthetic-device', t: key => key,
        toast: text => { window.lastToast = text; }, _teacherClearMediaCards: () => {},
        stopAllSpeech: () => {}, showTab: () => {}, _teacherHideSuggestions: () => {},
        _teacherRemoveChips: () => {}, _teacherShowTyping: () => {}, _teacherHideTyping: () => {},
        _teacherAppendBubble: (role, text) => { const el = document.createElement('div');
          el.dataset.role = role; el.textContent = text; document.querySelector('#messages').append(el); return el; },
        _teacherScrollToAnswerStart: () => {}, _teacherLinkSignReferences: async () => {},
        _teacherAppendMediaCards: () => [], _teacherResponseMedia: () => [],
        _teacherAppendSignCards: async () => {}, _teacherClearDoc: () => {},
      });
      });
      await page.addScriptTag({content: handler});
    }
    await loadTestPage();
    for (const lang of ['no', 'th', 'en']) {
      await page.evaluate(lang => { window.appLang = lang; window._teacherV6Context.language = lang; }, lang);
      await page.evaluate(() => teacherSend('hint'));
      const button = page.locator('.teacher-chip').last();
      await button.click();
      await page.waitForFunction(() => !window._teacherTyping);
      assert.equal(requests.at(-1).language, lang);
      assert.equal(requests.at(-1).v6_intent, 'answer');
      assert.equal(requests.at(-1).v6_answer_text, 'Blue');
      assert.match(requests.at(-1).v6_event_id, /^v6_[a-f0-9]{32}$/);
    }
    failOnce = true;
    await page.evaluate(() => teacherSend('retry synthetic answer'));
    const failedId = requests.at(-1).v6_event_id;
    const stored = await page.evaluate(() => JSON.stringify(sessionStorage));
    assert(!stored.includes('retry synthetic answer'), 'storage must not contain the learner answer');
    await loadTestPage(); // A real page navigation clears in-memory state, not sessionStorage.
    await page.evaluate(() => { window.appLang = 'en'; window._teacherV6Context.language = 'en'; });
    await page.evaluate(() => teacherSend('retry synthetic answer'));
    assert.equal(requests.at(-1).v6_event_id, failedId, 'network retry must retain the event id');
    const before = requests.length;
    await page.evaluate(() => { window._teacherV6Context.sessionId = 'different-session'; });
    await page.locator('.teacher-chip').last().click();
    assert.equal(requests.length, before, 'a stale chip must not send into a different session');
    assert.equal(await page.evaluate(() => window.lastToast), 'coach_unavailable');
    // A request can finish after someone has already opened another conversation.
    for (const change of ['account', 'language', 'conversation']) {
      await loadTestPage();
      await page.evaluate(() => {
        window.fetch = () => new Promise(resolve => {
          window.finishOldRequest = () => resolve(new Response(JSON.stringify({
            session_id:'obsolete-session', conversation_id:'obsolete-session',
            mode:'v6_quiz_pilot', reply:'obsolete reply', suggestions:[]
          })));
        });
        window.pendingReply = teacherSend('hint');
      });
      await page.waitForFunction(() => typeof window.finishOldRequest === 'function');
      await page.evaluate(async change => {
        if (change === 'account') window.token = 'next-synthetic-account';
        if (change === 'language') window.appLang = 'th';
        if (change === 'conversation') window._teacherActiveSessionType = 'normal';
        window.finishOldRequest();
        await window.pendingReply;
      }, change);
      assert.equal(await page.locator('[data-role=assistant]').count(), 0, change);
      assert.equal(await page.evaluate(() => window._teacherQuizSessionId), 'synthetic-session', change);
      assert.equal(await page.evaluate(() => window._teacherTyping), false, change);
    }
    console.log('PASS synthetic Chromium DOM: NO/TH/EN chips, retry ID, stale-session guard');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
