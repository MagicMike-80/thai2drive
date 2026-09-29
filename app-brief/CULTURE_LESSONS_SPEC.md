# Spesifikasjon: «Thailand vs Norge»-mikroleksjoner (`culture_lessons`)

Status: godkjent for implementering. Innhold = Deep. Backend/DB/deploy = Anti.
Web-first (`backend/webapp.py`). Språkrenhet: thai-modus = kun thai; `title_no`
og `norway_term_no` er bevisste norske fagbegreper og **skal** vises.

Avklaringer (besluttet):

- **HAV-akronymet:** Beholdes som Michaels pedagogiske anker for **vegtrafikkloven
  § 3** — *Hensynsfull, Aktpågivende, Varsom*. Dette er ordrett grunnregelen i § 3.
  Den konkrete vikeplikten ved gangfelt er fortsatt trafikkreglene § 9; HAV er
  tankesettet som leder dit.
- **UI-plassering:** Egen dedikert kortstokk «Thailand vs Norge», plassert i
  web-appen **under de eksisterende mikroleksjonene** (library-fane `micro`).
- **Quiz-kobling:** Utenfor scope i denne PR-en. `category`-feltet klargjøres for
  fremtidig kobling mot feilsvar.

---

## 1. JSON-schema: `culture_lessons`

### Innholdsfelt

| Felt | Type | Språk | Beskrivelse |
|---|---|---|---|
| `id` | string | — | Stabil slug, f.eks. `cl_hoyreregelen`. Idempotent seeding. |
| `title_th` | string | 🇹🇭 | Tittel på thai |
| `title_no` | string | 🇳🇴 | Norsk tittel/fagterm (vises alltid) |
| `category` | string | — | `Vikeplikt` · `Gangfelt` · `Rundkjøring` · `Sikkerhet` · `Lov og regler` |
| `thailand_practice_th` | string | 🇹🇭 | «Slik er du vant til det i Thailand» |
| `norway_rule_th` | string | 🇹🇭 | Den norske regelen forklart på thai |
| `norway_term_no` | string | 🇳🇴 | Nøkkel-fagbegrep(er) på norsk |
| `michaels_tip_th` | string | 🇹🇭 | Michael-tips (rolig, trygg) |

### Lagringsfelt (speiler `learning_glossary`)

| Felt | Type | Default | Beskrivelse |
|---|---|---|---|
| `active` | bool | `true` | Skjul uten å slette |
| `order` | int | — | Visningsrekkefølge (1–5) |
| `created_at` | string (ISO) | — | Settes av seed-script |

### Språkrenhet

- `lang=th`-respons: alle `*_th`-felt **pluss** `title_no` og `norway_term_no`.
- Ingen `*_en`. Ingen andre `*_no`-prosafelt. Ingen fallback for manglende `*_th`.
- `lang != "th"` → tom liste (thai-først).

### Påkrevde thai-felt (fail-stop)

`title_th`, `thailand_practice_th`, `norway_rule_th`, `michaels_tip_th`.
En leksjon som mangler ett av disse utelates helt fra responsen.

---

## 2. De 5 kjerne-leksjonene

```json
[
  {
    "id": "cl_hoyreregelen",
    "order": 1,
    "category": "Vikeplikt",
    "title_th": "ใครไปก่อน? กฎ «รถทางขวา» ของนอร์เวย์",
    "title_no": "Høyreregelen",
    "thailand_practice_th": "ที่ไทยเราขับชิดซ้าย และมักถือว่า «ถนนใหญ่ไปก่อน» ที่สี่แยกเล็ก ๆ ที่ไม่มีป้าย เรามักกะกันเองว่าใครจะไปก่อน",
    "norway_rule_th": "ที่นอร์เวย์ขับชิดขวา ถ้าสี่แยกไม่มีป้าย ไม่มีไฟจราจร และไม่ใช่ถนนหลัก คุณต้อง «ให้ทางรถที่มาจากทางขวาของคุณ» เสมอ นี่คือกฎพื้นฐานที่เรียกว่า Høyreregelen ป้าย ไฟจราจร ตำรวจ และป้ายถนนหลัก (skilt 202/204/220) จะยกเลิกกฎนี้",
    "norway_term_no": "Høyreregelen – vikeplikt for trafikk fra høyre",
    "michaels_tip_th": "เมื่อเข้าสี่แยกที่ไม่มีป้าย ให้ชะลอความเร็ว แล้วมองไปทางขวาก่อนเสมอ ถ้ามีรถมาจากขวา ให้รอ ใจเย็น ๆ การรอสองวินาทีปลอดภัยกว่าการเดา"
  },
  {
    "id": "cl_gangfelt_hav",
    "order": 2,
    "category": "Gangfelt",
    "title_th": "ทางม้าลาย: ให้ทางคนเดินเท้า + หลัก «HAV»",
    "title_no": "Vikeplikt ved gangfelt · HAV-regelen (§ 3)",
    "thailand_practice_th": "ที่ไทย รถมักไม่หยุดให้คนข้ามทางม้าลาย คนเดินเท้าต้องคอยจังหวะและระวังเอง",
    "norway_rule_th": "ที่นอร์เวย์ ตรงทางม้าลายที่ไม่มีไฟหรือตำรวจ คนขับ «ต้องให้ทาง» คนที่อยู่บนทางม้าลายหรือกำลังจะก้าวลงมา (trafikkreglene § 9) ไมเคิลใช้หลัก «HAV» จากกฎพื้นฐาน vegtrafikkloven § 3 เป็นตัวช่วยจำ: H – Hensynsfull (คำนึงถึงผู้อื่น), A – Aktpågivende (ตั้งใจสังเกตรอบตัว), V – Varsom (ระมัดระวัง) ถ้าขับแบบ HAV คุณจะชะลอและพร้อมหยุดให้คนข้ามเองโดยธรรมชาติ ห้ามแซงรถที่จอดอยู่หน้าทางม้าลาย และห้ามจอดบนทางม้าลายหรือใกล้กว่า 5 เมตร",
    "norway_term_no": "Gangfelt · vikeplikt for gående (trafikkreglene § 9) · grunnregelen HAV: Hensynsfull, Aktpågivende, Varsom (vegtrafikkloven § 3)",
    "michaels_tip_th": "จำสามคำนี้ไว้ทุกครั้งที่ขับ: Hensynsfull, Aktpågivende, Varsom เห็นคนยืนใกล้ทางม้าลายให้คิดไว้ก่อนว่าเขาจะข้าม ชะลอ พร้อมหยุด และสบตากับเขาเพื่อให้เขารู้ว่าคุณเห็นแล้ว"
  },
  {
    "id": "cl_rundkjoring",
    "order": 3,
    "category": "Rundkjøring",
    "title_th": "วงเวียนแบบนอร์เวย์: ให้ทางตอนเข้า + อยู่เลนให้ถูก",
    "title_no": "Rundkjøring",
    "thailand_practice_th": "ที่ไทย กฎวงเวียนไม่ชัดเจน บางวงเวียนรถที่อยู่ในวงเวียนต้องให้ทางรถที่เข้ามา และหลายคนไม่ค่อยเปิดไฟเลี้ยว",
    "norway_rule_th": "ที่นอร์เวย์ รถที่จะ «เข้า» วงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้วเสมอ (vikeplikt) การจัดเลน: ออกทางแรก/เลี้ยวขวา – ใช้เลนขวา เปิดไฟขวาตลอด; ตรงไป – ปกติใช้เลนขวา ไม่ต้องเปิดไฟตอนเข้า; ไปครึ่งวงหรือมากกว่า – ใช้เลนซ้าย เปิดไฟซ้ายตอนเข้า แล้วเปลี่ยนเป็นไฟขวาเมื่อผ่านทางออกก่อนหน้าทางที่จะออก ต้องเปิดไฟขวาก่อนออกจากวงเวียนทุกครั้ง ระวังจักรยานและรถใหญ่ที่ต้องใช้สองเลน",
    "norway_term_no": "Rundkjøring · vikeplikt ved innkjøring · plassering og tegn",
    "michaels_tip_th": "ก่อนถึงวงเวียน มองซ้ายเพื่อดูรถในวงเวียน ชะลอ ถ้ามีรถมาให้รอ เลือกเลนตั้งแต่เนิ่น ๆ ตามทางออกที่จะไป และอย่าลืมเปิดไฟขวาก่อนออกทุกครั้ง"
  },
  {
    "id": "cl_vinter_bremselengde",
    "order": 4,
    "category": "Sikkerhet",
    "title_th": "หน้าหนาวและถนนลื่น: ระยะเบรกยาวขึ้นมาก",
    "title_no": "Bremselengde på vinterføre",
    "thailand_practice_th": "ที่ไทยไม่มีหิมะหรือน้ำแข็ง สิ่งที่ต้องระวังคือฝนและน้ำท่วม แต่หลายคนก็ยังขับเร็วเท่าเดิมตอนฝนตก",
    "norway_rule_th": "ที่นอร์เวย์ ถนนที่มีน้ำแข็งหรือหิมะทำให้ «ระยะเบรก» (bremselengde) ยาวขึ้น 3–10 เท่า กฎหมาย (vegtrafikkloven § 6) บอกว่าต้องปรับความเร็วตามสภาพถนน แสง ทัศนวิสัย และการจราจร เพิ่มระยะห่างจากรถคันหน้า (จาก 3 วินาที เป็นมากกว่านั้นมาก) และต้องใช้ยางฤดูหนาว (vinterdekk) เมื่อถนนเป็นน้ำแข็ง/หิมะ จำไว้ว่าระยะเบรกเพิ่มตามกำลังสองของความเร็ว ความเร็วสองเท่า = ระยะเบรกสี่เท่า",
    "norway_term_no": "Bremselengde · stoppelengde · sikkerhetsavstand · vinterdekk",
    "michaels_tip_th": "ถ้าถนนดูมันวาวหรือมีหิมะ ให้ลดความเร็วและทิ้งระยะห่างเยอะ ๆ เบรกเบา ๆ แต่เนิ่น ๆ ถ้าไม่แน่ใจ ให้ขับช้าลงอีก"
  },
  {
    "id": "cl_promille",
    "order": 5,
    "category": "Lov og regler",
    "title_th": "เมาแล้วขับ: นอร์เวย์จำกัดที่ 0,2 (เข้มกว่าไทยมาก)",
    "title_no": "Promillegrense 0,2",
    "thailand_practice_th": "ที่ไทย ระดับแอลกอฮอล์ในเลือดที่กฎหมายยอมให้คือ 0,5 (50 มก.%) และการตรวจจับก็ไม่สม่ำเสมอ",
    "norway_rule_th": "ที่นอร์เวย์ ระดับที่ยอมให้คือ «0,2» เท่านั้น ต่ำกว่าไทยมาก แค่ดื่มนิดเดียวก็ทำให้ «เวลาตอบสนอง» (reaksjonstid ปกติราว 1 วินาที) ช้าลงและการตัดสินใจแย่ลง โทษหนักมาก: เสียใบขับขี่ ปรับเงินตามรายได้ และอาจติดคุก ข้อจำกัดนี้ใช้กับยาบางชนิดและสารเสพติดด้วย ทางที่ปลอดภัยคือ «ดื่ม = ไม่ขับ»",
    "norway_term_no": "Promillegrense (0,2 ‰) · reaksjonstid · reaksjonsstrekning",
    "michaels_tip_th": "ถ้าคืนนี้จะดื่ม วางแผนกลับบ้านด้วยวิธีอื่นไว้เลย และจำไว้ว่าแอลกอฮอล์จากเมื่อคืนอาจยังอยู่ในเลือดตอนเช้า ถ้าไม่แน่ใจ อย่าขับ"
  }
]
```

Faglige merknader:

- **HAV** = *Hensynsfull, Aktpågivende, Varsom* — ordlyden i vegtrafikkloven § 3.
  Den konkrete vikeplikten ved gangfelt er trafikkreglene § 9.
- Promille: Norge **0,2 ‰** vs. Thailand **0,5 ‰** (0,2 for yrkes-/nye/unge sjåfører).
- Rundkjøring: blinke **høyre før avkjøring, hver gang**.

---

## 3. Implementeringsplan (Anti)

### 3.1 Datalag — `culture_lessons`

- Ny MongoDB-collection, samme mønster som `learning_glossary`.
- Dokument = innholdsfelt + `active` (default `true`), `order` (int), `created_at` (ISO).
- Seed-script `backend/scripts/seed_culture_lessons.py` — kopi av `seed_glossary.py`:
  leser `MONGO_URL` fra env/`.env`, `DB_NAME="thai2drive"`, idempotent på `id`,
  ryddig `RuntimeError`-guard, dry-run som standard (`--apply` for skriving).
- Indeks i `backend/create_indexes.py`: unik `id`, sammensatt `active + order`.

### 3.2 Ren modul — `backend/culture_lessons.py`

`server.py` leser `os.environ[...]` på importtid og krasjer i offline-test (samme
grunn som `glossary_match.py`). Logikken ligger utenfor `server.py`:

- `REQUIRED_TH = ("title_th", "thailand_practice_th", "norway_rule_th", "michaels_tip_th")`
- `serialize_lesson(doc, lang="th")` → `id`, `category`, `order`, alle `*_th`, `title_no`, `norway_term_no`. Ingen `_id`, ingen `*_en`, ingen andre `*_no`.
- `lessons_for_lang(docs, lang="th", category=None)` → filtrer `active`; fail-stop på manglende `REQUIRED_TH`; valgfri `category`-filter (case-insensitivt); sorter `(order, id)`. `lang != "th"` → `[]`.

### 3.3 API — `GET /api/lessons/culture`

- `server.py`, `api_router` (prefix `/api`), nær glossary-rutene.
- Query: `lang="th"`, `category: Optional[str]`, `id: Optional[str]`, `X-Device-ID`-header.
- In-memory cache `_CULTURE_CACHE`, varmet i egen `@app.on_event("startup")` + lazy-last.
- `id` satt → én leksjon (404 hvis mangler/inaktiv). Ellers `lessons_for_lang(...)`.
- Respons `{"lessons": [...]}`; ingen treff → `{"lessons": []}`.
- Best-effort anonym logg i `culture_lesson_views` (`device_id`, `lesson_ids`, `category`, `lang`, `created_at`) i try/except.

### 3.4 Frontend — `backend/webapp.py` (`WEBAPP_HTML`)

- Utvid `renderMicroLessons(container)`: behold de eksisterende akkordeon-leksjonene,
  legg `<div id="cultureLessonsMount"></div>` under, kall ny `renderCultureLessons()`.
- `renderCultureLessons()` — `api('GET', '/api/lessons/culture?lang=th')`, samme
  mønster som `renderFagordkort`. Render kun når `appLang === 'th'`; ellers kort
  notis, ingen innholds-fallback.
- Kort-layout per leksjon: tittel (`title_th` stor, `title_no` liten/dempet) + 4 rader:
  🇹🇭 «ที่ไทย» → `thailand_practice_th` · 🇳🇴 «ที่นอร์เวย์» → `norway_rule_th` ·
  📘 fagord → `norway_term_no` · 💡 «เคล็ดลับจากไมเคิล» → `michaels_tip_th`.
- CSS: nytt sett (`.culture-deck`, `.culture-card`, `.cc-row`, `.cc-label`, `.cc-term`)
  i samme stil som `.micro-lesson` / `.fagordkort`. All tekst gjennom `escH()`.

### 3.5 Offline-test — `backend/tests/test_culture_lessons.py`

`unittest`, importerer kun `culture_lessons`. Dekker: (a) `lang="th"` gir `title_no`
+ `norway_term_no` men ingen `*_en` / andre `*_no`; (b) manglende `norway_rule_th`
→ leksjon droppes; (c) `category`-filter; (d) `lang="no"` → `[]`; (e) sortering på `order`.

Kjør: `python -m unittest tests.test_culture_lessons` fra `backend/`.

### 3.6 Kjøre-/verifiseringsrekkefølge

1. `python -m unittest tests.test_culture_lessons` → grønt.
2. `python scripts/seed_culture_lessons.py` (dry-run).
3. `python scripts/seed_culture_lessons.py --apply` mot riktig `MONGO_URL`.
4. `python create_indexes.py`.
5. Start backend → `GET /api/lessons/culture?lang=th` gir 5 leksjoner; `?category=Rundkjøring` gir 1.
6. `/api/web` i thai-modus → library-fane «Thailand vs. Norge» viser kortstokken under mikroleksjonene; bytt språk → notis, ingen fallback.
7. Bump `/api/web/version`, deploy, canary.

### 3.7 Berørte filer

- Nye: `backend/culture_lessons.py`, `backend/scripts/seed_culture_lessons.py`, `backend/tests/test_culture_lessons.py`
- Endres: `backend/server.py`, `backend/webapp.py` (`WEBAPP_HTML` + CSS), `backend/create_indexes.py`
