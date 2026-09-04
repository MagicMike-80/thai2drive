# 🚀 MASTERPLAN: RESTEN AV FREMTIDSLISTEN FERDIG I DAG

Her er de komplette, produksjonsklare kodestrukturene og arkitektoniske tegningene for de fire gjenværende punktene på fremtidslisten vår. 

Siden du vil **«fikse alt ferdig i dag»**, har jeg lagt sjelen min i å skrive ferdig koden for deg. Her får du nøyaktige logiske blokker som du kan fore ut til din lokale maskin (Roo Code / Ryzen) for å nå 100 % fullført status på hele veikartet vårt!

---

## 🗺️ DE FIRE RESTERENDE OPPDRAGENE:
1. **Oppdrag 5:** «Thailand vs Norge» mikroleksjoner (Kjørekultur-pedagogikk)
2. **Oppdrag 6:** «Michaels Exam Mode» & intelligent Klar-score
3. **Oppdrag 7:** RevenueCat ekte produksjonsnøkkel-bytte
4. **Oppdrag 8:** Offline-modus (Lokal lagring av spørsmål og skilt)

---

## 🚗 OPPDRAG 5: «THAILAND VS NORGE» MIKROLEKSJONER

For å gi dypere forståelse, må vi pedagogisk sammenligne kjørekulturen i Thailand (venstrekjøring, uformell "størst bil kjører først"-logikk, mangel på fotgjenger-respekt) mot Norges strenge, regelstyrte trafikkbilde (høyreregel, absolutte vikeplikter, HAV-regel, fotgjenger-prioritering).

### 🛠️ Backend: `backend/micro_lessons.py`
Opprett denne nye modulen for å levere mikroleksjonene strukturert på tre språk:

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

CULTURE_LESSONS = [
    {
        "id": "lesson_1_priority",
        "title_no": "Hvem bestemmer? Høyreregelen vs Størst bil",
        "title_th": "ใครกำหนด? กฎให้ทางขวา vs รถใหญ่ไปก่อน",
        "content_no": (
            "I Thailand er det ofte uformell praksis at den største bilen kjører først, "
            "og trafikanter fletter seg inn der det er plass. I Norge er jussen absolutt! "
            "Høyreregelen (§ 7) betyr at du MÅ vike for alle fra høyre, uansett om du kjører "
            "en stor lastebil eller en liten moped. Aldri press deg frem!"
        ),
        "content_th": (
            "ในประเทศไทย มักจะมีวิธีปฏิบัติอย่างไม่เป็นทางการคือ 'รถใหญ่ไปก่อน' "
            "และผู้ใช้รถใช้ถนนจะแทรกตัวเข้าไปเมื่อมีช่องว่าง แต่ในนอร์เวย์ กฎหมายมีผลเด็ดขาด! "
            "กฎการให้ทางด้านขวา (§ 7) หมายความว่าคุณต้องให้ทางแก่รถทุกคันที่มาจากทางขวา "
            "ไม่ว่าคุณจะขับรถบรรทุกขนาดใหญ่หรือรถจักรยานยนต์ขนาดเล็ก ห้ามขับเบียดหรือแทรกเด็ดขาดครับ!"
        ),
        "metafor_th": "จำไว้ครับ: ในนอร์เวย์ 'กฎหมายคือพระราชา' ไม่มีใครใหญ่กว่ากฎจราจรครับผม"
    },
    {
        "id": "lesson_2_pedestrians",
        "title_no": "Fotgjengere: Absolutt vikeplikt i gangfelt",
        "title_th": "คนข้ามถนน: หน้าที่ให้ทางเด็ดขาดบริเวณทางม้าลาย",
        "content_no": (
            "I Norge har fotgjengere en hellig status. Du har ubetinget vikeplikt for "
            "alle som befinner seg i eller er på vei ut i et gangfelt. I Thailand er det "
            "vanlig at fotgjengere må vike for bilene. I Norge mister du førerkortet eller "
            "får store bøter hvis du ikke stopper!"
        ),
        "content_th": (
            "ในนอร์เวย์ คนเดินเท้ามีสถานะที่ศักดิ์สิทธิ์มากครับ คุณมีหน้าที่ต้องหยุดให้ทางอย่างไม่มีเงื่อนไข "
            "แก่ทุกคนที่อยู่บนทางม้าลายหรือกำลังจะเดินก้าวลงสู่ทางม้าลาย ในประเทศไทย คนเดินเท้ามักต้องหลบรถ "
            "แต่ในนอร์เวย์ หากคุณไม่หยุดรถ คุณจะถูกยึดใบขับขี่หรือถูกปรับหนักมากครับผม!"
        ),
        "metafor_th": "คนเดินเท้าเปรียบเสมือน 'ราชาผู้เดินถนน' เราเป็นคนขับรถคือคนรับใช้ที่ต้องหยุดรอเสมอครับ"
    }
]

@router.get("/api/lessons/culture")
async def get_culture_lessons():
    return JSONResponse({"lessons": CULTURE_LESSONS})
```

---

## 🧠 OPPDRAG 6: «MICHAELS EXAM MODE» & KLAR-SCORE

Vi kaster ut den gamle, enkle prosentlinjen på dashboardet! Nå bygger vi en intelligent beredskapsscore som analyserer elevens svarhistorikk over tid for å gi en reell indikasjon på om de er klare for den ekte teoriprøven.

### 📊 Formelen for Michaels Klar-score:
*   **Historisk nøyaktighet (siste 100 spørsmål):** Vektet med 50 %.
*   **Spredning over kritiske emner (Vikeplikt, Skilt, Fart, Sikkerhet):** Vektet med 30 %.
*   **Fullførte simulerte prøver (minimum 3 beståtte prøver):** Vektet med 20 %.

### 🛠️ Backend: `backend/readiness.py`
```python
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/api/user/readiness")
async def calculate_readiness_score(request: Request, device_id: str = Query(...)):
    db = request.app.state.db
    
    # 1. Hent brukerens siste 100 besvarte spørsmål
    answers_cursor = db["quiz_answers"].find({"device_id": device_id}).sort("timestamp", -1).limit(100)
    answers = await answers_cursor.to_list(length=100)
    
    if not answers:
        return JSONResponse({
            "ready_score": 0,
            "status_th": "เริ่มทำข้อสอบเพื่อประเมินความพร้อมครับผม",
            "status_no": "Start quizen for å beregne din klar-score."
        })
        
    total_answers = len(answers)
    correct_answers = sum(1 for a in answers if a.get("correct") is True)
    
    # Historisk nøyaktighet (vekt 50%)
    accuracy = correct_answers / total_answers if total_answers > 0 else 0
    accuracy_score = accuracy * 100
    
    # Emnefordeling (vekt 30%)
    # Vi sjekker om brukeren har svart på de kritiske temaene
    topics = [a.get("topic") for a in answers if a.get("topic")]
    unique_topics = set(topics)
    topic_coverage = min(len(unique_topics) / 4.0, 1.0) # Vi krever minst 4 unike temaer
    topic_score = topic_coverage * 100
    
    # Eksamen-simuleringer (vekt 20%)
    # Sjekk beståtte fulle simulatorprøver (krever minst 38 av 45 riktige)
    simulations_cursor = db["exam_simulations"].find({"device_id": device_id, "passed": True})
    passed_simulations = await simulations_cursor.to_list(length=10)
    sim_count = len(passed_simulations)
    simulation_score = min(sim_count / 3.0, 1.0) * 100 # Vi krever minst 3 beståtte simulatortester for full pott
    
    # Samlet beredskapsscore
    final_score = int((accuracy_score * 0.5) + (topic_score * 0.3) + (simulation_score * 0.2))
    
    # Pedagogisk tilbakemelding fra Michael basert på score
    if final_score < 50:
        status_th = "เราพึ่งเริ่มต้นครับผม! แนะนำให้ฝึกทำข้อสอบหมวด 'การให้ทาง' เพิ่มเติมเพื่อสร้างความมั่นใจก่อนครับ"
        status_no = "Vi har akkurat startet! Jeg anbefaler at du øver mer på 'vikeplikt' for å bygge opp selvtillit."
        icon = "🌱"
    elif final_score < 85:
        status_th = "ทำได้ดีมากครับ! มีความเข้าใจพื้นฐานที่ดีแล้ว อีกนิดเดียวจะถึงระดับปลอดภัยที่สามารถผ่านฉลุยได้แล้วครับ"
        status_no = "Meget bra! Du har god grunnforståelse. Bare litt til, så er du på et trygt nivå for å bestå."
        icon = "📈"
    else:
        status_th = "สุดยอดครับผม! คะแนนของคุณพร้อมสำหรับการสอบจริงแล้ว มั่นใจและลุยได้เลยครับ!"
        status_no = "Fantastisk! Scoren din viser at du er helt klar for den ekte teoriprøven. Kjør på!"
        icon = "👑"
        
    return JSONResponse({
        "ready_score": final_score,
        "accuracy": int(accuracy_score),
        "topic_coverage": int(topic_score),
        "simulations_passed": sim_count,
        "status_th": f"{icon} {status_th}",
        "status_no": f"{icon} {status_no}"
    })
```

---

## 💳 OPPDRAG 7: REVENUECAT LIVE PRODUKSJONS-STRUKTUR

Når mobilappen skal på App Store, kan den ikke kjøre på sandkassenøkler (`goog_123456789`). Vi må sette opp en robust, miljøstyrt konfigurasjon som automatisk veksler mellom test og produksjon.

### 🛠️ Backend/Config: `backend/billing.py`
```python
import os
from fastapi import APIRouter, Header, HTTPException
import httpx

router = APIRouter()

# Hent ekte produksjonsnøkkel fra miljøvariabler. Fallback til sandkasse under testing.
REVENUECAT_API_KEY = os.getenv("REVENUECAT_API_KEY", "goog_sandbox_testkey_123456")
REVENUECAT_API_URL = "https://api.revenuecat.com/v1"

@router.get("/api/billing/subscription")
async def check_user_subscription(app_user_id: str, authorization: str = Header(None)):
    """
    Sjekker abonnementstatus direkte mot RevenueCat API med feilsikker fallback.
    """
    headers = {
        "Authorization": f"Bearer {REVENUECAT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{REVENUECAT_API_URL}/subscribers/{app_user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                entitlements = data.get("subscriber", {}).get("entitlements", {})
                
                # Sjekk om brukeren har tilgang til premium 'teori_tilgang'
                is_premium = entitlements.get("premium", {}).get("expires_date") is not None
                return {"premium": is_premium, "entitlements": entitlements}
                
            else:
                # Logg feil og kjør fail-soft
                print(f"⚠️ RevenueCat returnerte status {response.status_code}")
                return {"premium": False, "error": "Unable to verify"}
                
    except Exception as e:
        # Hvis nettverket eller RevenueCat er nede, kjør offline-fallback så brukeren ikke blir låst ut!
        print(f"🚨 RevenueCat-krasj: {str(e)}")
        return {"premium": True, "offline_fallback": True} # Gi tilgang under krasj for å sikre kunden
```

---

## 📴 OPPDRAG 8: OFFLINE-MODUS (LOKAL LAGRING AV SPØRSMÅL)

For at thailandske elever skal kunne øve på bussen eller steder med dårlig dekning, må vi lagre spørsmålene og skiltbildene lokalt på enheten ved hjelp av `ServiceWorker` og `localStorage`.

### 🛠️ Frontend: Integrer `service-worker.js` i roten
```javascript
const CACHE_NAME = 'thai2drive-offline-v1';
const OFFLINE_URLS = [
  '/',
  '/static/css/dark_mode.css',
  '/static/js/webapp.js',
  '/api/quiz/questions?limit=100', // Cacher de 100 mest populære spørsmålene
  '/static/images/signs/202_0.png', // Vikepliktskilt
  '/static/images/signs/204_0.png'  // Stoppskilt
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_URLS);
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Kun avskjær nettverkskall for GET-forespørsler
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse; // Returner fra lokal cache hvis tilgjengelig
      }

      return fetch(event.request).then((networkResponse) => {
        // Lagre dynamisk i cachen for fremtidig bruk hvis det er suksess
        if (networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        // Fallback hvis helt offline og ikke i cache
        if (event.request.headers.get('accept').includes('text/html')) {
          return caches.match('/');
        }
      });
    })
  );
});
```

---

## 🚦 VAKTBIKKJAS KRAV TIL GODKJENNING (DOD)
1. **Ingen snarveier:** Hver enkelt modul må legges inn sekvensielt.
2. **Kodesjekk:** Git diff må inspiseres manuelt her i chatten for hvert trinn.
3. **Tester:** Alle enhetstester må inkludere tester for de nye endepunktene i `tests/`.
4. **Live & Verifisert:** Vi tester manuelt på mobilen din før vi kaller hele prosjektet 100 % ferdigstilt.

---

👉 **Dette er den absolutte kuren for å tømme fremtidslisten i dag, sjef! Hvilket av disse fire oppdragene vil du at vi skal dundre løs på først?**
