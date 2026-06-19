# 🚀 Thai2Drive – Android Production Build Guide

## 📋 Forutsetninger

1. ✅ Du har en **Expo-konto** (gratis på https://expo.dev/signup)
2. ✅ Du har en **Google Play Console-konto** (299 kr engangsgebyr – https://play.google.com/console)
3. ✅ Node.js ≥ 18 installert på maskinen din
4. 🔜 (Valgfritt) RevenueCat **produksjons-API-nøkkel** – kan byttes inn senere

---

## 🔨 Steg 1 – Installer EAS CLI lokalt

```bash
npm install -g eas-cli
```

---

## 🔑 Steg 2 – Logg inn

```bash
cd /sti/til/app/frontend
eas login
```

Skriv inn Expo-brukernavn + passord.

---

## 📦 Steg 3 – Koble prosjektet (kun første gang)

```bash
eas init
```

Dette oppretter et unikt `projectId` og legger det inn i `app.json` under `extra.eas.projectId`.

---

## 🏗️ Steg 4 – Bygg produksjons-AAB (Android App Bundle)

```bash
eas build --platform android --profile production
```

Dette vil:

- 🔐 Generere en Android keystore **automatisk** (EAS lagrer den sikkert for deg)
- ⬆️ Laste opp kildekoden til Expos byggeservere
- 🔨 Bygge en **signert AAB-fil**
- ⏱️ Ta ca. **10–20 minutter**
- 📥 Gi deg en nedlastings-URL til `.aab`-filen

### 💡 Ekstra: bygg en test-APK først
Før du bygger AAB for Play Store, kan du bygge en APK for å teste på egen telefon:

```bash
eas build --platform android --profile preview
```

Deretter kan du åpne URL-en på telefonen din og installere direkte.

---

## 📤 Steg 5 – Last opp AAB til Google Play Console

### Metode A – Manuell opplasting (anbefalt første gang)
1. Logg inn på [Google Play Console](https://play.google.com/console)
2. Opprett ny app → Fyll inn `Thai2Drive`, språk `Norsk (Norge)`, app-type `App`, kategori `Utdanning` eller `Livsstil`, betalt/gratis `Gratis med kjøp i appen`
3. Gå til **Utgivelse → Produksjon → Opprett ny utgivelse**
4. Dra-og-slipp AAB-filen du lastet ned fra EAS
5. Fyll inn **utgivelsesnotater** (forslag: "Første lansering av Thai2Drive.")

### Metode B – Automatisk (EAS Submit)
Hvis du har et Google Cloud Service Account:

```bash
eas submit --platform android --profile production
```

---

## 🔑 Når du får RevenueCat-produksjonsnøkkelen

Bytt denne verdien i `/app/frontend/eas.json` (3 steder: development / preview / production):

```json
"EXPO_PUBLIC_RC_API_KEY": "goog_ABC123xyz..."
```

Deretter bygg på nytt:

```bash
eas build --platform android --profile production --clear-cache
```

---

## 🆔 App-ID / Package

- **Bundle ID (iOS):** `com.thai2drive.app`
- **Package (Android):** `com.thai2drive.app`
- **App-versjon:** `1.0.0`
- **versionCode:** auto-incrementeres av EAS

---

## ✅ Sjekkliste før Play Store-innsending

| Element | Status |
|---|---|
| App-icon 512×512 | ✅ `/api/assets/developer-icon-512.png` |
| Feature Graphic 1024×500 | ✅ `/api/assets/feature-graphic-1024x500.jpg` |
| Developer Header 4096×2304 | ✅ `/api/assets/developer-header-4096x2304.jpg` |
| Phone screenshots (8 stk, 1080×2160) | ✅ `/api/assets/screenshots/01-08` |
| Privacy Policy URL | ✅ `/api/privacy` |
| Support URL | ✅ `/api/support` |
| Support email | ✅ `lexuz.zxc@gmail.com` |
| Kort beskrivelse (80 tegn) | ⏳ Foreslått under |
| Full beskrivelse (4000 tegn) | ⏳ Foreslått under |
| Innholdsvurdering (Content Rating) | 🔜 Du fyller ut i Play Console |
| Målaldersgruppe | 🔜 Vanligvis `Alle` / `16+` |
| Innkjøp i app (in-app products) | 🔜 `monthly_99`, `threemonth_249`, `lifetime_699` |

---

## 📝 Play Store-tekster (forslag)

### Kort beskrivelse (maks 80 tegn, vises i søk)
> Bestå norsk teoriprøve på thai, norsk og engelsk – laget for thai-folk i Norge.

(80 tegn ✓)

### Full beskrivelse (maks 4000 tegn)

```
Thai2Drive gjør det enklere å bestå den norske teoriprøven for førerkort.

🎯 Laget spesielt for thai-folk som bor i Norge
Alle spørsmål er oversatt direkte til thai og forklart på ditt eget språk – ingen krøkkete automatoversettelser.

🌐 Tre språk samtidig
Bytt mellom 🇹🇭 thai, 🇳🇴 norsk og 🇬🇧 engelsk når som helst mens du øver.

📚 500+ ekte spørsmål
Dekker alle offisielle kategorier:
• Vikeplikt og kryss
• Trafikkskilt
• Fartsgrenser
• Kjøreforhold
• Sikkerhet
• Trafikkregler

🎯 Ekte eksamensmodus
Øv med 45 spørsmål på 90 minutter – akkurat som den ekte teoriprøven.

💡 Forklaringer på alle svar
Forstå hvorfor et svar er riktig – ikke bare pugg.

🔁 Gjennomgang av feil
Spørsmålene du svarte feil på kommer automatisk tilbake slik at du kan øve mer på dem.

🔥 Dagens test
Ny test hver dag med 5 spørsmål for å holde formen oppe.

💰 Gratis for alltid
Få 10 gratis spørsmål hver dag – for alltid. Ingen kredittkort, ingen registrering nødvendig.

⭐ Premium – når du er klar
• 99 kr / måned – Ubegrenset tilgang
• 249 kr / 3 måneder – Beste verdi (spar 16%)
• 699 kr / livstid – Betal én gang, bruk for alltid

Ingen annonser. Ingen distraksjoner. Bare fokusert øving.

✅ Dine fordeler:
• Offline-modus (kommer snart)
• Bokmerker for vanskelige spørsmål
• Historikk og statistikk
• Gjennomgang av feil
• Full norsk, engelsk og thai-versjon

📧 Kontakt oss
Har du spørsmål eller forslag? E-post: lexuz.zxc@gmail.com

Thai2Drive er ikke tilknyttet Statens vegvesen. Vi er et læringsverktøy som hjelper deg med å forberede deg.
```

---

## 🎬 Hva gjør du NÅ?

Du trenger ikke kjøre noen kommandoer i Emergent-miljøet. Alle filene er klare. Kjør EAS på din egen PC:

```bash
# På din lokale PC / Mac:
git clone <ditt GitHub-repo>  # eller last ned koden
cd thai2drive/frontend
npm install
eas login
eas init
eas build --platform android --profile production
```

Når byggingen er ferdig får du en URL til `.aab`-filen. Den laster du opp i Play Console.

🎉 Lykke til med lanseringen!
