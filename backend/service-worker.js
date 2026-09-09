/**
 * Thai2Drive Offline Service Worker (v1.1.0)
 * -------------------------------------------
 * Cacher kjerne-UI og skilt for offline øving.
 *
 * KRITISK REGEL (iOS Safari Range-støtte):
 * Alle forespørsler til /api/, Range requests og lyd/video (MP3/M4A/MP4)
 * skal ALDRI avskjæres av Service Workeren. De slippes direkte igjennom
 * til nettverket slik at audio/video streaming fungerer 100% på iPhone/Safari.
 *
 * ENESTE UNNTAK (v1.1.0): en smal allowlist av offentlige, JSON-baserte
 * GET-endepunkt for quiz og skilt caches «network-first» i en egen cache,
 * slik at appen kan øves offline. Range-forespørsler, mediefiler, POST og
 * alt annet under /api/ går fortsatt rett til nettverket.
 */

const CACHE_NAME = 'thai2drive-offline-v1.1.0';
const API_CACHE_NAME = 'thai2drive-api-v1.1.0';
const OFFLINE_URLS = [
  '/',
  '/api/assets/favicon.ico'
];

// Kun offentlig innhold uten personopplysninger. Eksakt path-match.
const OFFLINE_API_ALLOWLIST = [
  '/api/questions/random',
  '/api/traffic-signs',
  '/api/categories',
  '/api/glossary',
  '/api/lessons/culture'
];

const MEDIA_RE = /\.(mp3|m4a|mp4|wav|ogg|aac|webm)$/i;

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Tvinger den nye SW-en ut av ventemodus umiddelbart
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        OFFLINE_URLS.map((url) => cache.add(url).catch((err) => console.log('SW cache skip:', url, err)))
      );
    })
  );
});

self.addEventListener('activate', (event) => {
  const keep = new Set([CACHE_NAME, API_CACHE_NAME]);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => (keep.has(name) ? undefined : caches.delete(name)))
      );
    }).then(() => self.clients.claim()) // Tar kontroll over alle faner umiddelbart
  );
});

function isAllowlistedApi(url) {
  return OFFLINE_API_ALLOWLIST.indexOf(url.pathname) !== -1;
}

// Network-first: hent friskt når nettet er der, fall tilbake til cache offline.
// Query-strengen ignoreres ved fallback, så ?count=10 vs ?count=45 spiller
// ingen rolle når man er offline.
function networkFirst(event) {
  return fetch(event.request).then((networkResponse) => {
    if (networkResponse && networkResponse.status === 200) {
      const copy = networkResponse.clone();
      caches.open(API_CACHE_NAME).then((cache) => cache.put(event.request, copy));
    }
    return networkResponse;
  }).catch(() => caches.match(event.request, { ignoreSearch: true }));
}

self.addEventListener('fetch', (event) => {
  // Avskjær kun GET-forespørsler (POST/PUT/DELETE går alltid direkte til nettverket)
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const hasRange = event.request.headers && event.request.headers.has('range');
  const isMedia = MEDIA_RE.test(url.pathname);

  // 0. UNNTAK: smal allowlist for offline quiz/skilt — men aldri for Range
  //    eller mediefiler (iOS Safari-regelen står).
  if (isAllowlistedApi(url) && !hasRange && !isMedia) {
    event.respondWith(networkFirst(event));
    return;
  }

  // 1. KRITISK FORBUD: Avbryt umiddelbart for alle /api/ endepunkter
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/api/')) {
    return;
  }

  // 2. KRITISK FORBUD: Avbryt for alle Range-forespørsler (viktig for iOS Safari 206 Partial Content)
  if (hasRange) {
    return;
  }

  // 3. KRITISK FORBUD: Avbryt for alle podcast/audio/video mediefiler
  if (isMedia) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
          return caches.match('/');
        }
      });
    })
  );
});
