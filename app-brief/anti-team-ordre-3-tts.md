# 🚀 IMPLEMENTERINGS-ORDRE 3: FEILSØK OG SIKRE BACKEND-TTS (LYD PÅ MOBIL)

Dette dokumentet fungerer som den offisielle produksjonsordren for **Oppdrag 3**. Siden Claude er på ferie, er det vår vaktbikkje (Anti) som spesifiserer kravene. Oppdraget skal løses umiddelbart av ditt utviklingsmiljø.

---

## 🔇 Problemet: Lyden er helt død på iOS / mobil
Selv om de automatiske testene melder grønt, er lydavspillingen (`/api/tts/stream`) helt tyst på fysiske mobiltelefoner (særlig på iPhone/Safari). 

### 🔍 Rotårsaker som må løses:
1.  **iOS Safari Lydblokkering (User Interaction Constraint):**
    iOS tillater aldri avspilling av programmatisk lyd (som TTS) med mindre avspillingen startes direkte fra en ekte brukerhandling (f.eks. et klikk på en knapp). Hvis appen prøver å laste og spille av lyd automatisk i bakgrunnen uten eksplisitt bruker-klikk, blokkeres det tvert.
2.  **Manglende streaming-headere for Safari (Chunked / Ranges):**
    iOS Safari er ekstremt sær på streaming-responser. Den krever ofte `Accept-Ranges: bytes` og korrekt `Content-Type` (f.eks. `audio/mpeg` eller `audio/wav`), samt stabil chunking. Hvis backend bare spytter ut en rå strøm uten riktige HTTP-headere, nekter Safari å dekode den.
3.  **Lydspiller-koding i frontenden (`webapp.py`):**
    Audio-objektet i Javascript må instansieres og startes på en måte som iOS godkjenner, med en eksplisitt fallback-metode hvis strømmen blir stående fast (timeout).

---

## 🛠️ Trinnvis teknisk spesifikasjon (Kuren)

### 1. Oppdater backend-endepunktet for TTS (f.eks. `/api/tts/stream`)
*   **Headere:** Sørg for at FastAPI-responsen sender med korrekte streaming-headere som Safari krever:
    ```python
    headers = {
        "Content-Type": "audio/mpeg",
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-cache"
    }
    ```
*   **Sikkerhet:** Sørg for at feil i ElevenLabs (f.eks. utgått API-nøkkel eller kvotegrense) fanges opp grasiøst, slik at API-et returnerer en forståelig feilkode (f.eks. HTTP 500 med JSON-feil) i stedet for å bare henge og fryse frontenden.

### 2. Robust frontend-avspilling i `backend/webapp.py`
*   **User Gesture Unlock:** Sørg for at audio-avspillingen i Javascript kalles *direkte* i klikkhåndtereren til "Spill av lyd"-knappen.
*   **iOS Safari Fallback:** Bruk følgende robuste mønster for å instansiere og spille av strømmen:
    ```javascript
    let audio = new Audio();
    audio.src = `/api/tts/stream?text=${encodeURIComponent(text)}`;
    
    // iOS krever at load() kalles etter src er satt, og play() må trigges i samme callstack som klikket
    audio.load();
    let playPromise = audio.play();
    
    if (playPromise !== undefined) {
        playPromise.catch(error => {
            console.error("Audio playback failed on iOS:", error);
            // Vis en diskret feilmelding eller fallback-knapp til brukeren
        });
    }
    ```
*   **Timeout-kontroll:** Hvis strømmen bruker mer enn 5 sekunder på å starte, skal spilleren resette seg selv og gi beskjed til brukeren, i stedet for å etterlate appen i en evig "laster lyd..."-tilstand.

---

## 🚦 Godkjenningskrav (Definition of Done)
1.  **Sikker feilhåndtering:** Hvis backend feiler mot ElevenLabs, skal appen vise en tydelig feilmelding i stedet for å henge.
2.  **Lokal test grønn:** Koden skal kompilere og kjøre uten syntaksfeil.
3.  **Fysisk lydverifisering:** Lyden MÅ testes manuelt på en fysisk mobiltelefon og høres klart og tydelig før oppgaven godkjennes.
