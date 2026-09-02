/**
 * Thai2Drive Offline Service Worker (v1.0.1)
 * -------------------------------------------
 * Cacher kjerne-UI og skilt for offline øving.
 *
 * KRITISK REGEL (iOS Safari Range-støtte):
 * Alle forespørsler til /api/, Range requests og lyd/video (MP3/M4A/MP4)
 * skal ALDRI avskjæres av Service Workeren. De slippes direkte igjennom
 * til nettverket slik at audio/video streaming fungerer 100% på iPhone/Safari.
 */

const CACHE_NAME = 'thai2drive-offline-v1.0.1';
const OFFLINE_URLS = [
  '/',
  '/api/assets/favicon.ico'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        OFFLINE_URLS.map((url) => cache.add(url).catch((err) => console.log('SW cache skip:', url, err)))
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Avskjær kun GET-forespørsler (POST/PUT/DELETE går alltid direkte til nettverket)
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // 1. KRITISK FORBUD: Avbryt umiddelbart for alle /api/ endepunkter
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/api/')) {
    return;
  }

  // 2. KRITISK FORBUD: Avbryt for alle Range-forespørsler (viktig for iOS Safari 206 Partial Content)
  if (event.request.headers && event.request.headers.has('range')) {
    return;
  }

  // 3. KRITISK FORBUD: Avbryt for alle podcast/audio/video mediefiler
  if (url.pathname.match(/\.(mp3|m4a|mp4|wav|ogg|aac|webm)$/i)) {
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
