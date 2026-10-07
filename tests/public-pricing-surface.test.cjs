const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('backend/landing.py', 'utf8');
const script = source.match(/PUBLIC_PRICING_JS = r"""([\s\S]*?)"""/)[1];

function element() {
  return {children: [], textContent: '', appendChild(child) { this.children.push(child); },
    replaceChildren() { this.children = []; }};
}
async function render(lang, result, rejects = false) {
  const container = element();
  const calls = [];
  vm.runInNewContext(script, {
    document: {getElementById: () => container, createElement: element,
      documentElement: {getAttribute: () => lang}},
    fetch: async (url, options) => {
      calls.push({url, options});
      if (rejects) throw new Error('offline');
      return {ok: true, json: async () => result};
    },
  });
  await new Promise(resolve => setImmediate(resolve));
  return {container, calls};
}

test('public pricing reads live prices and uses only selected language', async () => {
  for (const lang of ['no', 'th', 'en']) {
    const plan = {id: 'monthly', label: {no: 'Månedlig', th: 'รายเดือน', en: 'Monthly'},
      period: {no: 'per måned', th: 'ต่อเดือน', en: 'per month'}, display: '123 kr'};
    const {container, calls} = await render(lang, {plans: [plan]});
    assert.equal(calls[0].url, '/api/pricing');
    assert.equal(calls[0].options.cache, 'no-store');
    assert.equal(container.children.length, 1);
    assert.equal(container.children[0].children[0].textContent, plan.label[lang]);
    assert.equal(container.children[0].children[1].textContent, '123 kr');
    assert.equal(container.children[0].children[1].children[0].textContent, ' / ' + plan.period[lang]);
  }
});

test('missing translations and offline prices never produce Norwegian fallback or invented amounts', async () => {
  const plan = {id: 'monthly', label: {no: 'Månedlig'}, period: {no: 'per måned'}, display: '123 kr'};
  assert.equal((await render('th', {plans: [plan]})).container.children.length, 0);
  assert.equal((await render('en', null, true)).container.children.length, 0);
  assert.equal((await render('en', {plans: 'invalid'})).container.children.length, 0);
});

test('quiz loading failures render the approved label in the selected language', () => {
  const errorFunction = source.match(/  function showLoadError\(\)\{[\s\S]*?\n  \}/)[0];
  for (const [lang, expected] of Object.entries({th:'โหลดไม่สำเร็จ', no:'Feil ved lasting', en:'Loading failed', unknown:''})) {
    const body = {replaceChildren(child) { this.child = child; }};
    vm.runInNewContext(errorFunction + ';showLoadError();', {
      currentLang: () => lang, body,
      document: {createElement: () => ({style: {}, setAttribute() {}})},
    });
    assert.equal(body.child.textContent, expected);
  }
  assert.doesNotMatch(source, /Could not load questions\.|No image questions available right now\./);
});
