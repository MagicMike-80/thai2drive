// Chromium test using synthetic HTTP responses only; no real service is contacted.
const {chromium} = require('../../tools/gstack/node_modules/playwright-core');
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const assert = require('node:assert/strict');
const python = path.resolve('.venv/Scripts/python.exe');
const html = execFileSync(python, ['-X', 'utf8', '-c', "import os,runpy,sys; sys.path.insert(0,'backend'); m=runpy.run_path(os.environ.get('T2D_TEST_WEBAPP', 'backend/webapp.py')); print(m['_webapp_html']('no'))"], {encoding:'utf8',maxBuffer:12*1024*1024});
const game = execFileSync(python, ['-X', 'utf8', '-c', "import asyncio,sys; sys.path.insert(0,'backend'); import webapp; sys.stdout.buffer.write(asyncio.run(webapp.flipp_flopp_page('no')).body)"], {encoding:'utf8',maxBuffer:12*1024*1024});
const book = execFileSync(python, ['-X', 'utf8', '-c', "import sys; sys.path.insert(0,'backend'); import website; sys.stdout.buffer.write(website.laeringsbok().body)"], {encoding:'utf8',maxBuffer:12*1024*1024});

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try {
    for (const lang of ['no','th','en']) {
      const page = await browser.newPage();
      await page.route('**/*', async route => {
        const url = new URL(route.request().url());
        if (url.pathname === '/app') return route.fulfill({status:200,contentType:'text/html',body:html});
        if (url.pathname === '/api/maintenance/status') return route.fulfill({json:{active:true,owner:false}});
        return route.fulfill({json:{}});
      });
      await page.goto('http://localhost/app', {waitUntil:'domcontentloaded'});
      await page.locator('#maintenanceOverlay').waitFor({state:'visible'});
      await page.locator(`#maintenanceOverlay button[onclick="setLang('${lang}')"]`).click();
      const heading = await page.locator('#maintenanceHeading').textContent();
      const expected = {no:'Vi tar en liten vedlikeholdspause',th:'พักปรับปรุงชั่วคราว',en:'We are taking a short maintenance break'};
      assert.equal(heading, expected[lang]);
      assert.equal(await page.locator('#ownerMaintenanceButton').isVisible(), false);
      await page.close();
    }
    let state = false;
    const page = await browser.newPage();
    await page.addInitScript(() => localStorage.setItem('t2d_token', 'synthetic-owner'));
    page.on('dialog', d => d.accept());
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/app') return route.fulfill({status:200,contentType:'text/html',body:html});
      if (url.pathname === '/api/maintenance/status') return route.fulfill({json:{active:state,owner:true}});
      if (url.pathname === '/api/admin/maintenance') {
        const change = route.request().postDataJSON();
        if (change.active) assert.equal(change.confirmed, true);
        state = change.active;
        return route.fulfill({json:{active:state}});
      }
      if (url.pathname === '/api/auth/me') return route.fulfill({json:{id:'test-owner',email:'owner@example.test',name:'Owner',is_admin:true,is_premium:true}});
      return route.fulfill({json:{}});
    });
    await page.goto('http://localhost/app', {waitUntil:'domcontentloaded'});
    await page.waitForFunction(() => window.user && window.user.id === 'test-owner');
    await page.evaluate(() => showTab('settings'));
    const button = page.locator('#ownerMaintenanceButton');
    await button.waitFor({state:'visible'});
    await button.click();
    await page.waitForFunction(() => document.querySelector('#ownerMaintenanceButton').textContent === 'Åpne kundetilgang');
    assert.equal(state, true);
    assert.equal(await page.locator('#maintenanceOverlay').isVisible(), false);
    await button.click();
    await page.waitForFunction(() => document.querySelector('#ownerMaintenanceButton').textContent === 'Sett kundetilgang på pause');
    assert.equal(state, false);
    await page.close();
    const recovery = await browser.newPage();
    await recovery.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/app') return route.fulfill({status:200,contentType:'text/html',body:html});
      if (url.pathname === '/api/auth/login') {
        const isOwner = route.request().postDataJSON().email === 'owner@example.test';
        return route.fulfill({json:{token:isOwner?'owner-token':'customer-token',user:{id:isOwner?'test-owner':'test-customer',email:isOwner?'owner@example.test':'customer@example.test',is_admin:isOwner}}});
      }
      if (url.pathname === '/api/maintenance/status') return route.fulfill({json:{active:true,owner:route.request().headers().authorization === 'Bearer owner-token'}});
      return route.fulfill({json:{}});
    });
    await recovery.goto('http://localhost/app', {waitUntil:'domcontentloaded'});
    await recovery.locator('#maintenanceOverlay').waitFor({state:'visible'});
    assert.equal(await recovery.locator('#maintenanceLogin').isVisible(), false);
    await recovery.locator('[data-key="maintenance_login_open"]').click();
    await recovery.locator('#maintenanceEmail').fill('customer@example.test');
    await recovery.locator('#maintenancePassword').fill('synthetic');
    await recovery.locator('#maintenanceLogin button[type="submit"]').click();
    await recovery.waitForFunction(() => document.querySelector('#maintenanceLoginError').textContent.length > 0);
    assert.equal(await recovery.locator('#maintenanceOverlay').isVisible(), true);
    assert.equal(await recovery.evaluate(() => localStorage.getItem('t2d_token')), null);
    await recovery.locator('#maintenanceEmail').fill('owner@example.test');
    await recovery.locator('#maintenancePassword').fill('synthetic');
    await recovery.locator('#maintenanceLogin button[type="submit"]').click();
    await recovery.locator('#maintenanceOverlay').waitFor({state:'hidden'});
    assert.equal(await recovery.evaluate(() => localStorage.getItem('t2d_token')), 'owner-token');
    await recovery.close();
    const gamePage = await browser.newPage();
    await gamePage.addInitScript(() => {localStorage.setItem('t2d_token','stale-token'); localStorage.setItem('admin_token','owner-token');});
    const gameRequests = [];
    await gamePage.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/no/flipp-flopp') return route.fulfill({contentType:'text/html',body:game});
      if (url.pathname === '/api/maintenance/status') return route.fulfill({json:{active:true,owner:route.request().headers().authorization === 'Bearer owner-token'}});
      if (url.pathname.endsWith('.json')) gameRequests.push(route.request().headers().authorization);
      return route.fulfill({json:[]});
    });
    await gamePage.goto('http://localhost/no/flipp-flopp', {waitUntil:'domcontentloaded'});
    await gamePage.waitForTimeout(300);
    assert.ok(gameRequests.length >= 2, 'game requests its card data');
    assert.ok(gameRequests.every(value => value === 'Bearer owner-token'), 'game data requests authenticate the owner');
    await gamePage.close();
    const bookPage = await browser.newPage();
    await bookPage.addInitScript(() => {localStorage.setItem('authToken','stale-token'); localStorage.setItem('t2d_token','owner-token');});
    const bookRequests = [];
    await bookPage.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/bok') return route.fulfill({contentType:'text/html',body:book});
      if (url.pathname === '/api/maintenance/status') return route.fulfill({json:{active:true,owner:route.request().headers().authorization === 'Bearer owner-token'}});
      if (url.pathname === '/api/auth/me') {bookRequests.push(route.request().headers().authorization); return route.fulfill({json:{is_admin:true}});}
      if (url.pathname === '/api/chapters') {bookRequests.push(route.request().headers().authorization); return route.fulfill({json:[]});}
      return route.fulfill({json:{}});
    });
    await bookPage.goto('http://localhost/bok', {waitUntil:'domcontentloaded'});
    await bookPage.waitForFunction(() => document.getElementById('bok-chapters').style.display === 'block');
    assert.equal(bookRequests.length, 2);
    assert.ok(bookRequests.every(value => value === 'Bearer owner-token'), 'book requests use the verified owner during pause');
    await bookPage.close();
    console.log('Chromium: customer NO/TH/EN, owner pause and reopening passed');
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
