# Findings & Systemkartlegging: Michael AI (Thai2Drive)

Dette dokumentet inneholder faktiske observasjoner og kartlegging av eksisterende kodebaser, databaser, integrasjonspunkter, juridisk mapping og 4-agent strukturen i Thai2Drive.

---

## 🏛️ 0. Reusable Intelligence & 4-Agent Squad Status

| Mappe / Område | Ansvarlig Agent | Primærfunksjon | Status |
|---|---|---|---|
| `/app-brief/` | **Agent 1: Pain Hunter** | Smerteprofiler (`PAIN_PROFILE.md`), gap-analyse og krav | Operativ (§ 7 nr. 2 profil ferdig) |
| `/agents/` | **Agent 2: Solution Architect** | Grunnloven (`AGENTS.md`), systemarkitektur og `SOLUTION_BLUEPRINT.md` | Operativ |
| `/runbook/` | **Agent 2 & DevOps** | Kjøreplan (`task_plan.md`), testprosedyrer og deploy-instrukser | Operativ |
| `/outputs/` | **Agent 3 & 4 (Code & QA)** | Leveranser, testrapporter (`QA_REPORT.md`) og artefakter | Operativ (60/60 tester PASS) |

---

## 1. Kartlegging av Databaser & Kilder (MongoDB Atlas)

| Samling / Kilde | Innhold / Nøkkelfelt | Bruk i Michael AI |
|---|---|---|
| `traffic_signs` | `id`, `group`, `name{no,th,en}`, `explanation{no,th,en}`, `driver_action{no,th,en}`, `image_url` | Skiltgjenkjenning, skiltkort i chat, approved image tags |
| `studiebok_chapters` | `order`, `icon`, `title_no/th/en`, `content_no/th/en`, `image_url`, `video_url` | Pensum-RAG (15 kapitler) for dybdeforklaringer og § 3 |
| `chapters` | `chapter_num`, `section_num`, `section_title{no,th,en}`, `content{no,th,en}` | 61 pensumseksjoner |
| `questions` | `id`, `category`, `difficulty`, `question{no,th,en}`, `options[{no,th,en}]`, `correct_answer`, `explanation{no,th,en}` | 700+ teorispørsmål |
| `quiz_attempts` | `device_id`, `user_id`, `question_id`, `selected_answer`, `correct`, `quiz_mode` | Elevens svarhistorikk for feilanalyse |
| `user_progress` | `device_id`, `user_id`, `category`, `total_attempts`, `correct_attempts`, `accuracy` | Kategori-statistikk for svak-tema veiledning |
| `learning_videos` | `title_no/th/en`, `youtube_url`, `topic_tags`, `sign_ids`, `instructor_summary`, `active` | Kontekstuelle videoforklaringer |
| `learning_podcasts` | `title_no/th/en`, `file_path`, `duration_seconds`, `topic_tags`, `active` | Lydpodkaster |
| `michael_materials` | `id`, `type`, `source_id`, `source_url`, `title{no,th,en}`, `caption{no,th,en}`, `sign_ids`, `situation_tags`, `topic_tags`, `priority`, `active` | Godkjent multimediamateriell for Michael |
| `teacher_chats` | `session_id`, `role`, `content`, `language`, `ts` | Samtalehistorikk (opptil 20 siste meldinger per økt) |
| `teacher_chat_logs` | `session_id`, `language`, `is_quiz_help`, `is_weak_topics`, `response_time`, `error`, `ts` | Telemetri og feilsporing |
| `teacher_feedback` | `session_id`, `language`, `helpful`, `reason`, `source`, `ts` | Elevens tommel opp/ned tilbakemelding |

---

## 2. API-Endepunkter & Rutemapping

| Metode | Endepunkt | Kilde | Funksjon |
|---|---|---|---|
| `POST` | `/api/teacher/chat` | `backend/teacher_chat.py` | Hovedmotor for Michael AI (støtter `<quiz_context>` og `<stats_context>`) |
| `GET` | `/api/teacher/welcome` | `backend/teacher_chat.py` | Språktilpasset velkomsthilsen (NO, TH, EN) |
| `GET` | `/api/teacher/topics` | `backend/teacher_chat.py` | Hurtigvalg / emneforslag (chips) |
| `POST` | `/api/teacher/feedback` | `backend/teacher_chat.py` | Lagre elevtilbakemeldinger |
| `GET` | `/api/signs` | `backend/signs_data.py` | Statisk skiltliste |
| `GET` | `/api/signs/{id}` | `backend/server.py` | Hente enkeltskilt med lokalisert navn og bilde-URL |
| `GET` | `/api/traffic-signs` | `backend/server.py` | Hente alle skilt fra MongoDB gruppert |
| `GET` | `/api/stats/me` | `backend/server.py` | Samlet statistikk og kategoripresisjon |
| `GET` | `/api/questions/random` | `backend/server.py` | Hente tilfeldige spørsmål (normal, eksamen, feilmodus) |
| `GET` | `/api/tts` | `backend/server.py` | TTS-tale (Google Cloud Chirp3 for Thai, ElevenLabs for NO/EN) |
| `GET` | `/api/admin/analytics/weaknesses` | `backend/admin_analytics.py` | Anonymisert aggregering av svakheter/feil per tag |
| `GET` | `/api/admin/analytics/conversions`| `backend/admin_analytics.py` | Anonymisert konverteringsstatistikk |
| `GET` | `/api/web` | `backend/webapp.py` | Web-app SPA grensesnitt (Single Page Application) |

---

## 3. Juridisk Mapping & Bildekatalog-Hashtags (LAW_MAPPING)

| Lovhjemmel | Tags | Søkeord (NO / TH / EN) | Bilde/Skilt-tilknytning |
|---|---|---|---|
| **Vegtrafikkloven § 3** (HAV-regelen) | `["#3", "#hav", "#grunnregel", "#hensynsfull", "#aktpaagivende", "#varsom"]` | "paragraf 3", "§ 3", "hav-regelen", "hensynsfull", "aktpågivende", "varsom", "grunnregel", "considerate", "attentive", "careful", "ข้อ 3" | `grunnregel_hav.png`, `situasjon_varsomhet.png` |
| **Trafikkreglene § 7 nr. 2** (Høyreregel & Venstresving) | `["#7", "#7_2", "#vikeplikt", "#hoyreregel", "#venstresving", "#motende"]` | "paragraf 7", "§ 7", "§ 7-2", "§ 7 nr. 2", "høyreregelen", "vikeplikt venstresving", "møtende trafikk", "right of way", "left turn", "oncoming", "กฎให้ทาง", "เลี้ยวซ้าย" | `kryss_venstresving.png`, `kryss_hoyreregel.png`, `#202` |
| **Trafikkreglene § 7 nr. 4** (Bussregelen) | `["#7", "#7_4", "#bussregelen", "#vikeplikt_buss"]` | "bussregel", "buss", "holdeplass", "vikeplikt buss", "bus rule", "bus stop", "กฎรถเมล์" | `buss_holdeplass.png` |
| **Vikepliktskilt** | `["#202", "#vikeplikt", "#vikepliktskilt"]` | "202", "vikepliktskilt", "give way sign", "yield sign", "ป้ายให้ทาง" | `kryss_vikeplikt.png`, Skilt `202_0` |
| **Stoppskilt** | `["#204", "#stopp", "#stoppskilt"]` | "204", "stoppskilt", "stop sign", "ป้ายหยุด" | `kryss_stopp.png`, Skilt `204_0` |

---

## 4. Eksisterende LLM-Konfigurasjon & Fallback-Kjede

1. **Primær motor:** `DeepSeek` (`DEEPSEEK_API_KEY` -> model `deepseek/deepseek-chat`).
2. **Sekundær motor:** `OpenRouter` (`OPENROUTER_API_KEY` -> fallback-modeller `openrouter/deepseek/deepseek-chat`, `openrouter/google/gemini-2.5-flash`, `openrouter/openai/gpt-4o-mini`).
3. **Tertiær motor:** `OpenAI` (`OPENAI_API_KEY` -> model `gpt-4o-mini`).
4. **Timeout:** 10 sekunder med automatisk prøving av neste modell i kjeden.
5. **Fail-Soft:** Ved API-feil returneres lokalisert høflig melding, og admin varsles via e-post ved ugyldige nøkler.

---

## 5. gstack & Test-Isolasjon

- **Klonet lokasjon:** `tools/gstack`
- **Test-isolasjon:** Alle enhetstester i `tests/test_michael_unified.py` kjører med lokale mocks/fixtures for databaser og eksterne API-kall (ElevenLabs, Stripe, LiteLLM) for å garantere null belastning eller risiko for produksjonsmiljøet (`www.thai2drive.no`).
