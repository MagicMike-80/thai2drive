# 📐 SOLUTION BLUEPRINT: Tvunget Service Worker-aktivering & Auto-reload

**Status:** READY FOR AGENT 3  
**Dato:** 2026-09-02  
**Eier:** Agent 2: Solution Architect (Fase: Løsningsdesign)  

---

## 1. Mål & Ikke-mål

### Mål:
- Tvinge ny Service Worker til å overta kontrollen umiddelbart på Android/Chrome (Samsung) og andre enheter.
- Tvinge frontend til å laste inn nyeste versjon automatisk via `window.location.reload()` når en ny Service Worker er aktivert.
- Sørge for at endringen er 100 % trygg mot reload-loops.
- Bevare alle eksisterende unntak for `/api/`, Range requests og lydfiler (`.mp3`, `.m4a`, etc.).

### Ikke-mål:
- Ikke endre backend API-kontrakter eller databaser.
- Ikke berøre Expo/mobilapp-kode.

---

## 2. Berørte filer

1. `backend/service-worker.js`:
   - Oppdatere cache-versjon til `thai2drive-offline-v1.0.2`.
   - Kalle `self.skipWaiting()` direkte ved mottak av `install`-event.
   - Sikre at `activate`-event tømmer gamle cacher og kjører `clients.claim()`.
2. `backend/webapp.py`:
   - Legge til `refreshing`-guard (`var refreshing = false;`) for å forhindre reload-loops.
   - Lytte på `controllerchange` på `navigator.serviceWorker`.
   - Lytte på `updatefound` og `newWorker.onstatechange` ved registrering av både `/service-worker.js` og fallback `/api/service-worker.js`.

---

## 3. Trinnvis patchplan

### Trinn 1: Oppdater `backend/service-worker.js`
```javascript
const CACHE_NAME = 'thai2drive-offline-v1.0.2';
const OFFLINE_URLS = [
  '/',
  '/api/assets/favicon.ico'
];

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
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim()) // Tar kontroll over alle faner umiddelbart
  );
});
```

### Trinn 2: Oppdater registrering i `backend/webapp.py`
```javascript
// ════════════════════════════════════════════
//  SERVICE WORKER REGISTRATION (Offline mode + Auto-update)
// ════════════════════════════════════════════
if ('serviceWorker' in navigator) {
  var refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function() {
    if (!refreshing) {
      refreshing = true;
      console.log('Ny Service Worker overtok kontrollen, reloader...');
      window.location.reload();
    }
  });

  function setupSwUpdate(reg) {
    if (!reg) return;
    reg.addEventListener('updatefound', function() {
      var newWorker = reg.installing;
      if (!newWorker) return;
      newWorker.addEventListener('statechange', function() {
        if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
          console.log('Ny versjon aktivert, reloader...');
          if (!refreshing) {
            refreshing = true;
            window.location.reload();
          }
        }
      });
    });
  }

  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js')
      .then(function(reg) {
        setupSwUpdate(reg);
      })
      .catch(function() {
        navigator.serviceWorker.register('/api/service-worker.js')
          .then(function(reg) {
            setupSwUpdate(reg);
          })
          .catch(function(err) {
            console.log('SW registration skipped:', err);
          });
      });
  });
}
```

---

## 4. Status
**READY FOR AGENT 3**
