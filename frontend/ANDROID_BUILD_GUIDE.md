# Thai2Drive — Android Build Guide
# ──────────────────────────────────

## Filer som ble endret/opprettet:

| Fil | Hva |
|-----|-----|
| `app.json` | App-navn, package name, Android-konfig, splash, ikon |
| `eas.json` | EAS Build-profiler (development, preview, production) |
| `assets/images/icon.png` | App-ikon 1024x1024 (Thai2Drive branded) |
| `assets/images/adaptive-icon.png` | Android adaptive ikon |
| `assets/images/splash-icon.png` | Splash screen |
| `assets/images/favicon.png` | Web favicon |
| `.env.production` | Referanse for produksjonsmiljøvariabler |

---

## STEG-FOR-STEG: Fra "Last ned kode" til "Test på Android"

### Steg 1: Last ned koden
- I Emergent → klikk **Download** knappen
- Pakk ut ZIP-filen på din PC

### Steg 2: Installer verktøy (én gang)
```bash
# Installer Node.js (v18+) fra nodejs.org
# Installer EAS CLI globalt
npm install -g eas-cli

# Logg inn på Expo
eas login
```

### Steg 3: Konfigurer prosjektet
```bash
cd frontend

# Installer avhengigheter
yarn install

# Initialiser EAS (kobler prosjektet til din Expo-konto)
eas init
# → Dette gir deg en "projectId" — den settes automatisk i app.json
```

### Steg 4: Bygg Android APK (for testing)
```bash
# Bygg en testbar APK
eas build --profile preview --platform android

# Vent 10-15 min → du får en nedlastingslenke for .apk-filen
# Installer APK-en på din Android-telefon
```

### Steg 5: Google Play Developer-konto
1. Gå til https://play.google.com/console
2. Registrer deg ($25 engangsbetaling)
3. Opprett en ny app: **Thai2Drive**
4. Package name: `com.thai2drive.app` (matcher app.json)

### Steg 6: Opprett in-app produkter i Google Play
1. Google Play Console → Din app → Monetization → Products → Subscriptions
2. Opprett/oppdater:
   - Product ID: `monthly_99` → Pris: 99 NOK/måned
   - Product ID: `threemonth_249` → Pris: 249 NOK/3 måneder
   - Product ID: `lifetime_699` → Pris: 699 NOK engangsbetaling

### Steg 7: Koble RevenueCat til Google Play
1. RevenueCat Dashboard → Project Settings → Apps → Add Android
2. Package name: `com.thai2drive.app`
3. Last opp Google Play Service Account Key (JSON)
   - Google Play Console → Settings → API access → Service accounts → Create key
4. RevenueCat → Products → Koble `monthly_99`, `threemonth_249` og `lifetime_699` til Google Play-produktene

### Steg 8: Bygg for produksjon
```bash
# Oppdater eas.json med din produksjons RC-nøkkel (erstatt YOUR_PRODUCTION_RC_KEY)

# Bygg .aab for Google Play
eas build --profile production --platform android

# Last opp til Google Play
eas submit --platform android
```

### Steg 9: Test betalinger
1. Google Play Console → Testing → Internal testing
2. Legg til testere (din e-post)
3. Installer appen via intern test-link
4. Test kjøp med Google sandbox

---

## ENV-VARIABLER DU MÅ SETTE:

| Variabel | Hvor | Verdi |
|----------|------|-------|
| `EXPO_PUBLIC_BACKEND_URL` | eas.json (allerede satt) | `https://norge-quiz-app.preview.emergentagent.com` |
| `EXPO_PUBLIC_RC_API_KEY` | eas.json | Din RevenueCat public key |

## HVA DU MÅ GJØRE MANUELT:

1. ✋ Opprett **Google Play Developer-konto** ($25)
2. ✋ Opprett **Expo/EAS-konto** (gratis)
3. ✋ Kjør `eas init` (genererer projectId)
4. ✋ Opprett **Google Play subscriptions/products** (monthly_99, threemonth_249, lifetime_699)
5. ✋ Koble **RevenueCat → Google Play** (Service Account Key)
6. ✋ Kjør `eas build` og `eas submit`

## BACKEND:
Backend kjører allerede på Emergent — ingen endringer nødvendig.
Mobilappen kobler seg til: `https://norge-quiz-app.preview.emergentagent.com/api`

---

## QUICK TEST (uten Google Play):
```bash
# Bygg en development APK for rask testing
eas build --profile development --platform android

# Installer på telefon → alt fungerer untatt ekte betalinger
# Betalinger testes via Google Play intern testing
```
