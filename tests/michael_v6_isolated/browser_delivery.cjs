// Runs in the runner's network namespace with no external interface. Only the
// named app routes below are forwarded to the inspected container, over stdio.
const assert = require('node:assert/strict');
const readline = require('node:readline');
const { chromium } = require(process.env.V6_PLAYWRIGHT_PATH);
const lines = readline.createInterface({input: process.stdin, crlfDelay: Infinity})[Symbol.asyncIterator]();

async function readMessage() {
  for (;;) {
    const {value, done} = await lines.next();
    if (done) throw new Error('The isolated app closed the test channel');
    if (value.startsWith('V6 ')) return JSON.parse(value.slice(3));
  }
}

function send(message) {
  process.stdout.write(JSON.stringify(message) + '\n');
}

async function run(browser, lang, tier) {
  const item = await readMessage();
  assert.equal(item.language, lang);
  assert.equal(item.tier, tier);
  const context = await browser.newContext({serviceWorkers:'block', viewport:{width:1280, height:960}});
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(10000);
    page.on('pageerror', error => console.error('Web page error:', error.message));
    await page.addInitScript(bearer => localStorage.setItem('t2d_token', bearer), item.bearer);
    const pagePath = '/' + lang + '/app';
    const appPaths = new Set([pagePath, '/api/auth/me', '/api/teacher/v6/status', '/api/teacher/v6/text/start', '/api/teacher/chat']);
    let pending = Promise.resolve();
    let releaseStatus;
    const initialVisibilityChecked = new Promise(resolve => { releaseStatus = resolve; });
    await page.route('**/*', async route => {
      const req = route.request();
      const url = new URL(req.url());
      if (url.origin !== 'http://127.0.0.1') return route.abort();
      if (appPaths.has(url.pathname)) {
        pending = pending.then(async () => {
          if (url.pathname === '/api/teacher/v6/status') await initialVisibilityChecked;
          send({method:req.method(), path:url.pathname + url.search, authorization:req.headers().authorization,
                body:req.method() === 'POST' ? req.postDataJSON() : null});
          const reply = await readMessage();
          assert.equal(reply.status, 200);
          await route.fulfill({status:reply.status, contentType:reply.type, body:reply.body});
        });
        return pending;
      }
      if (url.pathname.includes('maintenance')) return route.fulfill({json:{active:false, owner:false}});
      if (url.pathname === '/api/teacher/welcome') return route.fulfill({json:{welcome:''}});
      return route.abort();
    });
    await page.goto('http://127.0.0.1' + pagePath);
    await page.locator('#bnTeacher').click();
    const entry = page.locator('#v6TextPilotBtn');
    try {
      assert.equal(await entry.evaluate(button => getComputedStyle(button).display), 'none');
    } finally {
      releaseStatus();
    }
    await page.locator('#v6TextPilotBtn:not([hidden])').click();
    const chat = page.locator('#teacherMessages');
    await chat.getByText(item.question, {exact:true}).waitFor();
    async function typeAnswer(text) {
      await page.locator('#teacherInput').fill(text);
      const replied = page.waitForResponse(response => new URL(response.url()).pathname === '/api/teacher/chat');
      await page.locator('#teacherSendBtn').click();
      const response = await (await replied).json();
      await page.waitForFunction(() => !_teacherTyping);
      return response.suggestions[0].v6_feedback;
    }
    const examples = {no:['Gi meg et hint', 'Blå eller rød'], en:['Give me a hint', 'Blue or red'],
                      th:['ขอคำใบ้', 'สีน้ำเงินหรือสีแดง']};
    assert.equal(await typeAnswer(examples[lang][0]), 'guidance');
    await chat.getByText(item.firstPrompt, {exact:true}).waitFor();
    assert.equal(await typeAnswer(examples[lang][1]), 'unknown');
    assert.equal(await typeAnswer(item.wrongPhrase), 'incorrect');
    await chat.locator('.tm-bubble.assistant').filter({hasText:item.hint}).waitFor();
    await chat.getByRole('button', {name:item.wrong, exact:true}).click();
    await chat.locator('.tm-bubble.assistant').filter({hasText:item.alternative}).waitFor();
    await page.waitForFunction(() => !_teacherTyping);
    assert.equal(await typeAnswer(item.rightPhrase), 'correct');
    await chat.locator('.tm-bubble.assistant').filter({hasText:item.confirmation}).waitFor();
    assert.equal(await chat.locator('.teacher-chip').count(), 0);
    await pending;
  } finally {
    await context.close();
  }
  send({finished:lang});
}

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.V6_CHROME_PATH,
    args:['--disable-background-networking', '--disable-quic', '--host-resolver-rules=MAP * ~NOTFOUND']});
  try {
    for (const lang of ['no', 'th', 'en']) {
      for (const tier of ['premium', 'registered']) await run(browser, lang, tier);
    }
  } finally {
    await browser.close();
    process.stdin.destroy();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
