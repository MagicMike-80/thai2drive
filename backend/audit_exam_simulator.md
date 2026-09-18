# Fase 5 Audit – Eksamenssimulator & Teoritest-logikk for Klasse B (TASK-011)

**Dato:** 18. september 2026  
**Repository:** MagicMike-80/thai2drive  
**Branch:** `audit/exam-simulator`  
**Status:** Audit fullført – ingen produktkode endret.

---

## 1. Spørrebank for Klasse B

### 1.1 Lagringssted & Kilde til sannhet
- **Database:** MongoDB Atlas (databasenavn `thai2drive`), collection `questions` (`db.questions`).
- **Skript og seed-filer:** Katalogen `backend/scripts/` inneholder historiske import- og migreringsskripter (f.eks. `seed_vikeplikt_questions.py`, `insert_batch_5_questions.py`, `generated_with_images_*.json`). I aktiv drift og produksjon hentes alle spørsmål direkte fra `db.questions`.
- **Krav om illustrasjonsbilde:** Spørsmålene filtreres med `IMAGE_ONLY_FILTER = {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}` i `server.py:955`.

### 1.2 Datamodell & Normalisering (`normalize_question`)
Spørsmålene normaliseres gjennom `normalize_question(q)` i `backend/server.py:85-148`. Funksjonen sikrer kompatibilitet mellom eldre v1-flatt format og gjeldende v2-struktur:
- `id`: Unik ID (streng).
- `question`: Flerspråklig tekstobjekt `{"no": "...", "th": "...", "en": "..."}`.
- `options`: Liste med alternativer `[{"id": "A", "text": {"no": "...", "th": "...", "en": "..."}}, ...]`.
- `correctOptionId`: Fasitbokstav (`"A"`, `"B"`, `"C"`, `"D"`). Normaliseringsfunksjonen stokker svaralternativene dynamisk ved hver uthenting for å forhindre posisjonsbias.
- `explanation`: Forklaringsobjekt `{"no": "...", "th": "...", "en": "..."}`.
- `bildeUrl`: Bildebane (f.eks. `skilt_202.png` eller full URL).
- `category`: Emnekategori (f.eks. `vikeplikt`, `skilt`, `fart`, `sikkerhet`).
- `difficulty`: Vanskelighetsgrad (`hard`, `medium`, `easy`).
- `active`: Boolean (`true`).

---

## 2. Eksamensrutiner i Backend

### 2.1 Eksisterende API-ruter
Det finnes **ikke** egne dedikerte ruter som `/api/exam/start` eller `/api/exam/submit`. Eksamenslogikken er i dag integrert i eksisterende ruter via parametere:
1. **Spørsmålsuthenting:** `GET /api/questions/random?count=45&has_image=true&mode=exam` (`server.py:1046-1067`).
   - Kaller funksjonen `_get_exam_questions(approved, x_device_id, user)` (`server.py:943-1043`).
   - Vekting:
     - Inntil 30 % (opptil 13 spørsmål) hentes fra brukerens nylig feilbesvarte spørsmål i `db.quiz_attempts` (siste 10 forsøk).
     - 90 % av gjenværende plasser fylles med vanskelige spørsmål (`difficulty: "hard"`).
     - 10 % fylles med middels spørsmål (`difficulty: "medium"`).
     - Fyller opp med øvrige spørsmål ved behov og stokker listen til slutt.
2. **Innsending og evaluering:** `POST /api/quiz-attempts` (`server.py:2217-2255`).
   - Når `doc.get("mode") == "exam"`:
     - Beregner `duration = completed_at - started_at`.
     - Kaller `evaluate_exam_attempt()` fra `exam_logic.py`.
     - Setter `passed`, `score_percentage`, `duration_seconds` og `timed_out`.
     - Lagrer forsøket i `db.quiz_attempts`.

---

## 3. Karakterlogikk & Bestått-kriterier for Klasse B

### 3.1 Statens vegvesen Standard
- **Antall spørsmål:** 45 spørsmål.
- **Tidsfrist:** 90 minutter (5400 sekunder).
- **Krav for å bestå:** Maksimum 7 feil (dvs. minst 38 riktige besvarelser / 84.4 % nøyaktighet).

### 3.2 Implementasjon i Kildekoden
- **Backend-domene:** `backend/exam_logic.py:15-58`
  - Konstanter:
    - `EXAM_TOTAL_QUESTIONS = 45`
    - `EXAM_TIME_LIMIT_SECONDS = 5400`
    - `EXAM_MAX_ERRORS = 7`
    - `EXAM_PASS_THRESHOLD = 38`
  - Funksjon `evaluate_exam_attempt(total_questions, correct_answers, duration_seconds)`:
    - `errors = total_questions - correct_answers`
    - `passed = (errors <= 7) and (correct_answers >= 38)`
    - `timed_out = duration_seconds > 5430` (30 sekunders grace period for nettverksforsinkelse).
- **Frontend-evaluering:** `backend/webapp.py:9350-9351` og `9425`
  - `var examErrors = Math.max(0, total - qScore);`
  - `var examPassed = examErrors <= 7;`
  - `passed: isExamMode ? ((total - qScore) <= 7) : null`

---

## 4. Michael-integrasjon & `mode: "quiz_coach"`

### 4.1 Nåværende overordnet Michael-slusing
- På resultatskjermen (`#screenEnd`) vises knappen `#endCoachMichaelPriBtn` ("💬 Gå gjennom med Michael AI") når `isExamMode === true`.
- Klikk kaller `consultMichaelFromExam()` (`webapp.py:9464-9539`):
  - Finner elevens svakeste tema basert på `_topicErrors`.
  - Genererer en skreddersydd prompt via `generate_michael_exam_prompt()`-mønsteret på thai, norsk eller engelsk.
  - Skifter fane til Michael og sender meldingen.

### 4.2 Spørsmålsspesifikk veiledning med `mode: "quiz_coach"`
- I `backend/teacher_chat.py:1185-1200` og `2874-2886`:
  - Støtter `mode: "quiz_coach"`.
  - Mottar strukturert `<quiz_context>`:
    ```
    <quiz_context>
    Question: ...
    Student answer (A): ...
    Correct answer (B): ...
    Existing explanation: ...
    </quiz_context>
    ```
  - Michael åpner uten skryt/ros, forklarer hvorfor elevens valgte svar er feil og hvorfor fasiten er riktig, med én konkret trafikksituasjon.
- I `backend/webapp.py:9897-9950`:
  - `_quizCoachRequest(message)` kaller `/api/teacher/chat` med `mode: 'quiz_coach'`.
  - `openMichaelQuizCoach()` håndterer dette i øvingsmodus.
- **Identifisert forbedringspunkt for Fase 5:** På resultatskjermen (`screenEnd`) etter fullført eksamen mangler det i dag en inline-liste over alle de 45 spørsmålene (eller kun de feilbesvarte) med en direkte `[💬 Spør Michael AI]`-knapp på hvert enkelt feilkort.

---

## 5. Frontend UI i `webapp.py`

| Funksjon / Element | Lokasjon i `webapp.py` | Ansvar og Oppførsel |
| :--- | :--- | :--- |
| `startExam()` | `webapp.py:7402-7408` | Sjekker premium-status, setter `isExamMode = true`, henter 45 spørsmål via `/api/questions/random?count=45&has_image=true&mode=exam`. |
| `startExamTimer()` | `webapp.py:7417-7439` | Viser `#examTimerBadge` og `#examSubmitBtn`, teller ned 5400 sekunder (90 min), farger timeren rød ved <= 60s, kaller `showEnd()` ved 0s. |
| `stopExamTimer()` | `webapp.py:7441-7447` | Stopper intervall og skjuler badge og innleveringsknapp. |
| `confirmSubmitExam()` | `webapp.py:7410-7415` | Bekreftelsesdialog (`confirm(t('exam_submit_confirm'))`) før tidlig innlevering og overgang til `showEnd()`. |
| `renderQuestion()` | `webapp.py:7515-7620` | Rendrer spørsmålskort `#qCard`, bilde `#qImgWrap`, tekst `#qText`, alternativer `.ans-btn`, og fremdriftslinje `#qProgLbl`. |
| `selectAns()` | `webapp.py:7810-7880` | Registrerer svar, oppdaterer `qScore`, lagrer besvarelse i `_sessionAnswers`, og aktiverer neste-knapp. |
| `_buildDebrief()` | `webapp.py:9340-9382` | Beregner bestått/stryk basert på `errors <= 7`, genererer overskrift og finner svakeste tema. |
| `showEnd()` | `webapp.py:9384-9462` | Stopper timer, viser `#screenEnd`, aktiverer `#endCoachMichaelPriBtn`, lagrer forsøket i `db.quiz_attempts`. |
| `consultMichaelFromExam()` | `webapp.py:9464-9539` | Sluser eleven direkte til Michael AI med resultat- og svakhetsprompt. |

---

## 6. Arkitektur-plan for Fase 5 (Minste trygge inngrep)

For å levere en komplett og profesjonell Eksamenssimulator uten å forstyrre den ordinære øvings-quizen anbefales følgende arkitektur:

1. **Beholde backend-kjernen i `exam_logic.py`:**
   - Dagens `evaluate_exam_attempt` og `_get_exam_questions` fungerer allerede optimalt.
   - Valgfritt: Etablere dedikerte alias-ruter `GET /api/exam/questions` og `POST /api/exam/submit` i en ny `backend/exam_routes.py` for å isolere eksamen helt fra generell quiz.
2. **Ekte eksamensflyt i frontend (uten umiddelbar fasit):**
   - I en offisiell teoriprøve får man ikke se fasit underveis.
   - Når `isExamMode === true`:
     - Skjul umiddelbar grønn/rød fargelegging, forklaring og quiz-coach panel i `selectAns()`.
     - Gi eleven mulighet til å navigere fritt (Forrige / Neste) og markere spørsmål de er usikre på.
     - Spørsmålene forblir ubesvarte eller valgte inntil eleven trykker "Lever prøve" (`confirmSubmitExam()`).
3. **Detaljert Resultatside med feilgjennomgang & Michael AI:**
   - Utvide `showEnd()` slik at når `isExamMode === true`, vises en oversikt over alle feilbesvarte spørsmål rett under bestått/stryk-banneret.
   - Hvert feilspørsmål viser spørsmålsteksten, elevens svar, riktig svar, og en dedikert knapp:
     `[💬 Spør Michael AI om dette spørsmålet]`
   - Klikk kaller Michael AI med `mode: "quiz_coach"` og spørsmålets `<quiz_context>`, slik at eleven får personlig veiledning på nøyaktig det spørsmålet de feilet på.
4. **100 % Språkisolasjon (Protokoll Null):**
   - Alle nye tekster (markere usikker, lever prøve, feilliste, Michael-knapper) legges inn i `TR` for `th`, `no` og `en` uten fallbacks til andre språk.
