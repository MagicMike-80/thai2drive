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

async function run(browser, lang) {
  const item = await readMessage();
  assert.equal(item.language, lang);
  const context = await browser.newContext({serviceWorkers:'block', viewport:{width:1280, height:960}});
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(10000);
    page.on('pageerror', error => console.error('Web page error:', error.message));
    await page.addInitScript(() => localStorage.setItem('t2d_token', 'synthetic-bearer'));
    const pagePath = '/' + lang + '/app';
    const appPaths = new Set([pagePath, '/api/teacher/v6/status', '/api/teacher/v6/text/start', '/api/teacher/chat']);
    let pending = Promise.resolve();
    await page.route('**/*', async route => {
      const req = route.request();
      const url = new URL(req.url());
      if (url.origin !== 'http://127.0.0.1') return route.abort();
      if (appPaths.has(url.pathname)) {
        pending = pending.then(async () => {
          send({method:req.method(), path:url.pathname + url.search, authorization:req.headers().authorization,
                body:req.method() === 'POST' ? req.postDataJSON() : null});
          const reply = await readMessage();
          assert.equal(reply.status, 200);
          await route.fulfill({status:reply.status, contentType:reply.type, body:reply.body});
        });
        return pending;
      }
      if (url.pathname === '/api/auth/me') {
        return route.fulfill({json:{id:'synthetic-user', name:'Test', is_premium:true}});
      }
      if (url.pathname.includes('maintenance')) return route.fulfill({json:{active:false, owner:false}});
      if (url.pathname === '/api/teacher/welcome') return route.fulfill({json:{welcome:''}});
      return route.abort();
    });
    await page.goto('http://127.0.0.1' + pagePath);
    await page.locator('#bnTeacher').click();
    await page.locator('#v6TextPilotBtn:not([hidden])').click();
    const chat = page.locator('#teacherMessages');
    await chat.getByText(item.question, {exact:true}).waitFor();
    for (const [choice, expected] of [[item.wrong, item.hint], [item.wrong, item.alternative],
                                      [item.right, item.confirmation]]) {
      await chat.getByRole('button', {name:choice, exact:true}).click();
      await chat.locator('.tm-bubble.assistant').filter({hasText:expected}).waitFor();
      await page.waitForFunction(() => !_teacherTyping);
    }
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
    for (const lang of ['no', 'th', 'en']) await run(browser, lang);
  } finally {
    await browser.close();
    process.stdin.destroy();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
