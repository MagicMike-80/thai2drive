/**
 * Behavioural tests for service-worker.js — run with:  node backend/tests/sw_behavior.test.mjs
 *
 * Loads the SW source in a mock worker context and drives synthetic fetch
 * events. No npm dependencies (node:vm / node:assert / node:fs only).
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = readFileSync(join(HERE, '..', 'service-worker.js'), 'utf-8');

function makeContext() {
  const stores = new Map(); // name -> Map(urlNoHashMaybeNoSearch -> response)
  const cacheApi = {
    open: async (name) => {
      if (!stores.has(name)) stores.set(name, new Map());
      const m = stores.get(name);
      return {
        put: async (req, res) => { m.set(req.url, res); },
        match: async (req) => m.get(req.url),
      };
    },
    match: async (req, opts) => {
      for (const m of stores.values()) {
        if (m.has(req.url)) return m.get(req.url);
        if (opts && opts.ignoreSearch) {
          const bare = req.url.split('?')[0];
          for (const [k, v] of m) if (k.split('?')[0] === bare) return v;
        }
      }
      return undefined;
    },
    keys: async () => [...stores.keys()],
    delete: async (name) => stores.delete(name),
  };

  const handlers = {};
  const self = {
    addEventListener: (type, fn) => { handlers[type] = fn; },
    skipWaiting: () => {},
    clients: { claim: async () => {} },
    caches: cacheApi,
  };
  const ctx = { self, caches: cacheApi, URL, console, Promise, Set, fetch: null };
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  return { handlers, ctx, stores };
}

function headers(obj = {}) {
  const map = new Map(Object.entries(obj).map(([k, v]) => [k.toLowerCase(), v]));
  return { has: (k) => map.has(k.toLowerCase()), get: (k) => map.get(k.toLowerCase()) ?? null };
}
function resp(body, status = 200) {
  return { status, type: 'basic', _body: body, clone() { return this; }, async text() { return body; } };
}
function fireFetch(handlers, request) {
  let responded, respondedWith;
  const event = { request, respondWith: (p) => { responded = true; respondedWith = p; } };
  handlers.fetch(event);
  return { responded: !!responded, value: respondedWith };
}

let pass = 0;
async function test(name, fn) {
  try { await fn(); console.log('  ok  ' + name); pass++; }
  catch (e) { console.error('FAIL  ' + name + '\n      ' + (e && e.message)); process.exitCode = 1; }
}

const req = (url, { method = 'GET', range = false } = {}) => ({
  url: 'https://app.example' + url,
  method,
  headers: headers(range ? { range: 'bytes=0-1' } : { accept: 'application/json' }),
});

// ---------------------------------------------------------------------------

await test('allowlisted GET is served from network and cached', async () => {
  const { handlers, ctx, stores } = makeContext();
  ctx.fetch = async () => resp('FRESH');
  const r = fireFetch(handlers, req('/api/questions/random?count=10'));
  assert.equal(r.responded, true, 'respondWith should be called');
  assert.equal((await r.value).status, 200);
  await new Promise((res) => setTimeout(res, 0)); // let the cache.put microtask run
  const apiCache = [...stores.entries()].find(([k]) => k.includes('api'))[1];
  assert.ok([...apiCache.keys()].some((k) => k.includes('/api/questions/random')), 'response cached');
});

await test('allowlisted GET falls back to cache when offline', async () => {
  const { handlers, ctx } = makeContext();
  ctx.fetch = async () => resp('FRESH');
  fireFetch(handlers, req('/api/questions/random?count=10')); // seed cache
  await new Promise((res) => setTimeout(res, 0));
  ctx.fetch = async () => { throw new Error('offline'); };
  const r = fireFetch(handlers, req('/api/questions/random?count=45')); // different query
  assert.equal(r.responded, true);
  const got = await r.value;
  assert.equal(await got.text(), 'FRESH', 'ignoreSearch fallback should return the cached set');
});

await test('non-allowlisted /api/ GET is passed through untouched', async () => {
  const { handlers } = makeContext();
  const r = fireFetch(handlers, req('/api/user/readiness'));
  assert.equal(r.responded, false, 'SW must not intercept other /api/ paths');
});

await test('Range request on an allowlisted path is passed through', async () => {
  const { handlers } = makeContext();
  const r = fireFetch(handlers, req('/api/traffic-signs', { range: true }));
  assert.equal(r.responded, false, 'Range must always reach the network (iOS Safari)');
});

await test('POST to an allowlisted path is passed through', async () => {
  const { handlers } = makeContext();
  const r = fireFetch(handlers, req('/api/questions/random', { method: 'POST' }));
  assert.equal(r.responded, false);
});

await test('same-origin page asset still uses cache-first', async () => {
  const { handlers, ctx } = makeContext();
  ctx.fetch = async () => resp('<html>');
  const r = fireFetch(handlers, req('/quiz'));
  assert.equal(r.responded, true);
  assert.equal((await r.value).status, 200);
});

console.log('\n' + pass + ' passed' + (process.exitCode ? ', with failures' : ''));
