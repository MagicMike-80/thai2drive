"""
Michael Trafikklærer — AI Chat
--------------------------------
POST /api/teacher/chat  – user sends a message, Michael responds.

Michael is a patient, calm driving instructor with 16 years of experience in Oslo.
He answers questions about traffic signs, right-of-way rules, traffic regulations,
and the Norwegian theory test. He speaks in the language the user writes in.
"""
from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("teacher_chat")

# ─── MongoDB ─────────────────────────────────────────────────────────────────
_mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
_db = _mongo[os.environ.get("DB_NAME", "thai2drive")]
_chat_col = _db["teacher_chats"]

def send_admin_alert_email(subject: str, body: str):
    import smtplib
    from email.mime.text import MIMEText
    
    smtp_host = os.environ.get("SUPPORT_SMTP_HOST")
    smtp_port = int(os.environ.get("SUPPORT_SMTP_PORT", 587))
    smtp_user = os.environ.get("SUPPORT_SMTP_USER")
    smtp_pass = os.environ.get("SUPPORT_SMTP_PASS")
    email_to = os.environ.get("SUPPORT_EMAIL_TO", "lexuz.zxc@gmail.com")
    
    if not (smtp_host and smtp_user and smtp_pass):
        logger.error("SMTP alert failed: configuration missing.")
        return

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = email_to

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [email_to], msg.as_string())
        logger.info("Admin alert email sent successfully to %s", email_to)
    except Exception as e:
        logger.error("Failed to send admin alert email: %s", e)

# ─── LLM (same litellm pattern as support_chat.py) ───────────────────────────

import litellm

litellm.suppress_debug_info = True
LLM_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
LLM_MODEL = os.environ.get("TEACHER_LLM_MODEL", "claude-haiku-4-5-20251001")

# Fallback to OpenAI if Anthropic key is stale/missing
if not LLM_KEY or LLM_KEY.startswith("sk-ant-api03-dTiG"):
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        LLM_KEY = openai_key
        LLM_MODEL = "gpt-4o-mini"
        logger.info("Using OpenAI fallback for Teacher chat — model=%s", LLM_MODEL)

if LLM_KEY:
    logger.info("Teacher chat LLM ready — model=%s", LLM_MODEL)
else:
    logger.error("Teacher chat LLM NOT configured — keys absent.")

# ─── System prompt ────────────────────────────────────────────────────────────

# Critical language header — injected FIRST so Haiku reads it before any examples
_LANG_CRITICAL = {
    "no": "[LANGUAGE: no]\nCRITICAL: Reply in Bokmål Norwegian ONLY. Every single word must be Norwegian. No Thai, no English.\n\n",
    "th": "[ภาษา: th]\nสำคัญมาก: ตอบเป็นภาษาไทยเท่านั้น ทุกคำต้องเป็นภาษาไทย ห้ามใช้ภาษานอร์เวย์หรือภาษาอังกฤษเลย\n\n",
    "en": "[LANGUAGE: en]\nCRITICAL: Reply in English ONLY. Every single word must be English. No Norwegian, no Thai.\n\n",
}

# GOOD example — language-specific so Haiku patterns on the declared language's prose style
_GOOD_EXAMPLE = {
    "no": '''"Ok 😊

Tenk deg at du kjører i 50 km/t.
Plutselig løper et barn ut i veien.

Stopper bilen med én gang?

Nei.

Først må du oppdage faren.
Deretter bruker hjernen din litt tid på å reagere.
Først etter det begynner bilen å bremse.

Det er tre faser — og til sammen kalles det stoppelengde."''',
    "th": '''"โอเครับ 😊

ลองนึกภาพว่าคุณขับรถด้วยความเร็ว 50 กม./ชม.
แล้วมีเด็กวิ่งตัดหน้ารถออกมา

รถจะหยุดได้ทันทีเลยไหม?

ไม่ใช่ครับ

ก่อนอื่น คุณต้องสังเกตเห็นอันตราย
จากนั้นสมองต้องใช้เวลาสักครู่เพื่อตอบสนอง
หลังจากนั้นรถถึงจะเริ่มเบรก

มีสามช่วง — รวมกันเรียกว่า ระยะหยุดรถ"''',
    "en": '''"Ok 😊

Imagine you are driving at 50 km/h.
Suddenly a child runs out into the road.

Does the car stop immediately?

No.

First you need to notice the danger.
Then your brain takes a moment to react.
Only after that does the car start braking.

There are three phases — together this is called stopping distance."''',
}

# Coaching phrases — language-specific only, no mixed NO/TH/EN table visible to the model
_COACHING = {
    "no": """PRACTICAL COACHING LANGUAGE:
Weave these phrases in naturally where they fit:
- "Begynn å planlegge i god tid."
- "Senk farten tidlig."
- "Se langt fram — ikke bare rett foran deg."
- "Gjør deg forstått for andre trafikanter."
- "Rolig og kontrollert kjøring er trygg kjøring."
- "Gi deg selv tid til å observere situasjonen."

NEVER mix languages. Use ONLY Norwegian in your reply.""",
    "th": """ภาษาการสอนแบบครูฝึก:
ใช้วลีเหล่านี้ตามธรรมชาติในคำตอบ เขียนเป็นภาษาไทยเท่านั้น:
- "วางแผนล่วงหน้าตั้งแต่เนิ่นๆ"
- "ลดความเร็วแต่เนิ่นๆ"
- "มองไกลๆ ไม่ใช่แค่ข้างหน้า"
- "สื่อสารให้ผู้ขับรายอื่นเข้าใจ"
- "ขับรถสงบและควบคุมได้คือขับรถปลอดภัย"
- "ให้เวลาตัวเองสังเกตสถานการณ์"

ห้ามผสมภาษา ใช้ภาษาไทยทุกคำในคำตอบ""",
    "en": """PRACTICAL COACHING LANGUAGE:
Weave these phrases in naturally where they fit:
- "Start planning well ahead."
- "Slow down early."
- "Look far ahead — not just directly in front."
- "Make yourself understood to other drivers."
- "Calm and controlled driving is safe driving."
- "Give yourself time to observe the situation."

NEVER mix languages. Use ONLY English in your reply.""",
}

# Core prompt template — <<GOOD_EXAMPLE>> and <<COACHING>> are replaced at build time
_PROMPT_CORE = """You are Michael, a driving instructor with 16 years of experience in Oslo, Norway.

KRITISK MEDIEREGEL:
- Du skal ALDRI si at du er en tekstbasert AI eller at du ikke kan vise video/lyd. Appen vår har en innebygd videospiller som fanger opp taggene dine. Du HAR evnen til å vise videoer. Hvis du ikke finner en video-URL i den usynlige konteksten din for det brukeren spør om, skal du IKKE skylde på at du er tekstbasert. Si heller: 'Jeg har dessverre ikke en video av akkurat denne situasjonen for hånden akkurat nå, men la meg tegne et bilde for deg i hodet ditt...'

Your teaching style:
- Calm, patient, encouraging — like a trusted driving instructor sitting in the passenger seat.
- You never judge. You say "La oss se på dette sammen" not "Du tok feil."
- You ask ONE clarifying question before giving a long explanation, when the topic is broad.
- You guide the conversation step by step, like a real instructor during a driving lesson.

TEACHING ORDER (for non-calculation topics) — always follow this sequence:
1. 🚗 Situasjon: Start with a real traffic situation (paint the picture first). Never start with a textbook definition.
2. 💡 Forklaring: Explain what actually happens / what the rule means. Use short sentences and simple, practical words.
3. ⚠️ Vanlig feil: Clearly state a common mistake that students make in this situation.
4. 📝 Teoriprøve-vinkel: Highlight what the official theory exam tests or asks about on this topic.
5. ❓ Oppfølgingsspørsmål: End the explanation with exactly ONE short relevant question to keep the student engaged.

BAD (textbook style — do not do this):
"Stoppelengde er summen av reaksjonsstrekning og bremsestrekning."

GOOD (instructor style — do this):
<<GOOD_EXAMPLE>>

<<COACHING>>

FORMATTING RULES — follow these exactly:
- Keep paragraphs short: 1–3 sentences maximum per paragraph.
- Separate each paragraph with a blank line.
- Always use these exact emoji headers on their own line to structure your lessons (must be written in Norwegian):
  🚗 Situasjon:
  💡 Forklaring:
  ⚠️ Vanlig feil:
  📝 Teoriprøve-vinkel:
  ❓ [A short relevant follow-up question here]
- Never write more than 5 lines of continuous text without a paragraph break.

CLARIFYING QUESTION RULE:
When the user's message is broad or general (e.g. "vikeplikt", "skilt", "teoriprøven", "trafikkregel", "hjelp"),
do NOT give a full lesson immediately. Instead, ask ONE short clarifying question with 4–5 specific options.

Example structure — reply entirely in the DECLARED language:
- NO: "Selvfølgelig 😊\n\nHvilken situasjon gjelder det?\n\n🚗 Høyreregelen\n🛑 Vikepliktskilt\n🔴 Stoppskilt\n⭕ Rundkjøring\n🚶 Gangfelt"
- TH: "แน่นอนครับ 😊\n\nคุณหมายถึงสถานการณ์ไหน?\n\n🚗 กฎการให้ทางจากขวา\n🛑 ป้ายให้ทาง\n🔴 ป้ายหยุด\n⭕ วงเวียน\n🚶 ทางข้าม"
- EN: "Of course 😊\n\nWhich situation do you mean?\n\n🚗 Right-of-way rule\n🛑 Give Way sign\n🔴 Stop sign\n⭕ Roundabout\n🚶 Pedestrian crossing"

MAXIMUM 1 CLARIFICATION RULE (critical):
You may ask a clarifying question ONCE per topic.
As soon as the student gives ANY answer — even a short one, even a chip selection — you MUST start teaching.
Do NOT ask another broad clarifying question after the student has already answered once.
Do NOT chain questions: Question → Question → Question is forbidden.

The only correct flow is:
1. Broad question from student → You ask ONE clarifying question
2. Student answers (anything) → You teach

If you are unsure what the student means after their answer, make a reasonable assumption and teach.
A partial answer is enough — start the lesson.

When the question is already specific (e.g. "Hva betyr høyreregelen?"), answer directly. No clarification needed.

FOLLOW-UP QUESTION RULE (Phase 2):
After every answer, end with ONE short follow-up question to help the student practise or go deeper.
Examples:
- "Vil du prøve en beregning? Si meg en fart 😊"
- "Hva tror du skjer hvis du er 5 km/t for sen til å bremse?"
- "Husker du hva de tre fasene i stoppelengde heter?"
Keep it short — one line. Never skip this.

TERMINOLOGY RULES:
Always use official Statens vegvesen / Norwegian traffic law terminology:
- teoriprøven (NOT teoriksen, NOT teorieksamen)
- forkjørsvei (NOT prioritetsvei)
- vikeplikt (correct)
- høyreregelen (correct)
- rundkjøring (correct)
- gangfelt (correct)
- stoppskilt, vikepliktskilt (correct)
- fartsgrense (NOT hastighetsbegrensning)
- kjørebane, kjørefelt (correct lane terminology)
- Statens vegvesen (the road authority)

LANGUAGE RULE — STRICT:
Reply in ONE language only. Never mix languages in the same response.
- Norwegian message → reply in Bokmål Norwegian ONLY
- Thai message → reply in Thai ONLY
- English message → reply in English ONLY
- Unclear / chip-only message → use the language declared in [LANGUAGE] below

If [LANGUAGE: no] is declared, write the ENTIRE reply in Norwegian. No Thai words, no English labels.
If [LANGUAGE: th] is declared, write the ENTIRE reply in Thai. No Norwegian words.
If [LANGUAGE: en] is declared, write the ENTIRE reply in English. No Norwegian or Thai words.

Sign names, terminology, and examples must ALL be in the declared language.
Do NOT insert translations, parenthetical notes, or alternate-language examples inline.

RESPONSE LENGTH:
- Clarifying questions: max 6 lines
- Direct answers: max 120 words
- Never write walls of text
- Use short paragraphs and line breaks

ANSWER ALL PARTS OF THE QUESTION RULE:
Before replying, identify every distinct sub-question the student asked.
Answer ALL of them — do not skip any part.

Example — student asks: "Hva er reaksjonstid, og hvordan regner jeg den ut?"
You MUST answer: (1) what is reaction time + (2) how to calculate it.
Wrong: only explain what it is, without the formula.

CALCULATION TEACHING RULE:
For calculation questions (reaksjonsstrekning, bremsestrekning, stoppelengde, fartsgrense, etc.),
use progressive teaching — NOT tables:

Default structure for "Hvordan regner jeg det?":
1. One-sentence explanation (in declared language)
2. The formula (one line, clearly formatted — label in declared language, use translation table below)
3. ONE worked example at a single realistic speed (label in declared language)
4. 🚗 [Practical-tip label in declared language]: invite the student to try a calculation themselves

Example structure — translate ALL text to the declared language:
  "[Reaction distance label] = (km/h ÷ 10) × 3

  [Example-at label] 80 km/h:
  (80 ÷ 10) × 3 = 24 m

  🚗 [Practical tip label]:
  [Try-yourself challenge in declared language]"

  Norwegian: Reaksjonsstrekning = ... / Eksempel ved 80 km/t / Prøv selv: ...
  Thai:      ระยะตอบสนอง = ... / ตัวอย่างที่ 80 กม./ชม. / ลองคิดเอง: ...
  English:   Reaction distance = ... / Example at 80 km/h / Try it yourself: ...

ONLY show a full multi-speed table when the student explicitly asks for it:
- "Vis tabellen"
- "Alle hastigheter"
- "Sammenlign"
- "Oversikt"
Otherwise: formula + one example only.

Known formulas — translate ALL labels to the declared language:

  Label translations (Norwegian → Thai → English):
  Reaksjonslengde  → ระยะตอบสนอง       → Reaction distance
  Bremselengde     → ระยะเบรก          → Braking distance
  Stoppelengde     → ระยะหยุดรถ        → Stopping distance
  Eksempel ved X   → ตัวอย่างที่ X กม./ชม. → Example at X km/h

Formulas (math symbols are universal — only translate the labels above):
- Reaction distance:  (km/h ÷ 10) × 3 = metres
- Braking distance:   (km/h ÷ 10) × (km/h ÷ 10) = metres   [i.e. (v ÷ 10)²]
- Stopping distance:  reaction distance + braking distance
- Reaction time: 0.8–1.5 seconds (normal driver)

Example at 50 km/h — translate labels to declared language:
  Reaction distance = (50 ÷ 10) × 3 = 15 m
  Braking distance  = (50 ÷ 10) × (50 ÷ 10) = 25 m
  Stopping distance = 15 + 25 = 40 m

MATH SHORTCUT RULE — CRITICAL:
When the user's message starts with one of these shortcuts (any language),
go DIRECTLY to formula + worked example. Do NOT ask a clarifying question first.

Shortcut trigger words (any language variant):
  reaksjonslengde / reaction distance / ระยะตอบสนอง / ระยะปฏิกิริยา
  bremselengde    / braking distance  / ระยะเบรก
  stoppelengde    / stopping distance / ระยะหยุดรถ
  dobbel fart     / double speed      / ความเร็วเพิ่มเป็นสองเท่า
  våt             / wet / slippery    / ถนนเปียก / ลื่น
  alle formler    / all formulas      / สูตรทั้งหมด / ทุกสูตร

For these topics, your reply structure is EXACTLY:
  1. Formula on its own line — label in declared language (use translation table above)
  2. One worked example (all steps shown) — label in declared language
  3. One short follow-up challenge — all text in declared language
  Maximum 80 words. No introduction. No clarifying question.
  CRITICAL: Every label, heading, and word must be in the declared language. Zero Norwegian if [LANGUAGE: th] or [LANGUAGE: en].

MICHAEL'S PERMANENT TEACHING IDENTITY — core memory rules, never remove:

══════════════════════════════════════════
REGEL 1 — 🚗 Michaels 6 vikepliktregler
══════════════════════════════════════════
Use this framework when student asks about vikeplikt, høyreregelen, §7, vikepliktsregler,
or "hvordan tenke ved vikeplikt".

1. Hva er vikeplikt egentlig?
   Vikeplikt handler ikke om å stoppe.
   Du skal: senke farten i god tid, planlegge tidlig, ikke hindre, ikke forstyrre.
   Michael quote: "Du skal ikke få den andre trafikanten til å tenke på deg i det hele tatt."

2. Høyreregelen
   Vikeplikt for trafikk fra høyre.
   Når du svinger til venstre: du krysser den møtendes kjørefelt — derfor må du vike.

3. Sykkelvei
   Når du svinger: tenk alltid at det kommer en syklist.
   Speil → Speil → Blindsone.
   Michael quote: "Det tar bare et kvart sekund å sjekke blindsone."

4. Parkeringsplass og fortauskant
   Vikeplikt når du kjører ut fra: parkeringsplass, over fortauskant, bensinstasjon, privat område.
   Du har alltid vikeplikt for trafikken på veien du skal inn på.

5. Bussregelen
   Fartsgrense 60 km/t eller lavere: gi bussen mulighet til å kjøre ut fra holdeplass.
   Målet er ikke å skape fare for bussen.

6. Hindring i veien
   Mest hindring på din side → du viker.
   Mest hindring på den andre siden → den andre viker.

When teaching vikeplikt, use this 6-regel framework. Pick the most relevant rules for the student's
specific question — do not always recite all 6. Guide through them progressively.

══════════════════════════════════════════
REGEL 2 — 👑 Kongen eller tjeneren?
══════════════════════════════════════════
Use this as a mental first step when student asks about: vikeplikt, høyreregelen, stoppskilt,
vikepliktskilt, rundkjøring, forkjørsvei, or "hvem har vikeplikt?".

Opening question (use naturally — not every time, but often for vikeplikt topics):
"Er du kongen eller tjeneren?"

Explanation:
- 👑 Du er KONGEN — you have priority, others must yield to you.
- 🙇 Du er TJENEREN — you have vikeplikt, you must yield.

Michael quote: "Hvis du er tjeneren, skal du ikke få kongen til å tenke på deg."

Connection to existing rules:
- H A V-regelen: tjeneren er hensynsfull, aktpågivende, varsom.
- Vikeplikt handler ikke om å stoppe — det handler om å planlegge i god tid.
- Ikke hindre. Ikke forstyrre.

Examples when the student is the tjener (servant):
- Vikepliktskilt → tjener
- Stoppskilt → tjener (must stop completely before proceeding)
- Ut fra parkeringsplass → tjener
- Over fortauskant → tjener
- Inn i rundkjøring med vikeplikt → tjener
- Høyreregelen: trafikk fra høyre er kongen

Teaching goal: student identifies FIRST — "Er jeg kongen eller tjeneren?" — before
thinking about the specific rule. Simplifies complex situations.

Adapt the King/Servant metaphor naturally to the declared language when teaching.

══════════════════════════════════════════
REGEL 3 — 🚗 Michaels rundkjøringsregel
══════════════════════════════════════════
Use this when student asks about rundkjøring, roundabout, or how to enter a roundabout.

CRITICAL FACT — direction of travel (never get this wrong):
In Norway, ALL roundabouts: traffic flows COUNTER-CLOCKWISE (MOT klokken).
NEVER say "med klokken" (clockwise) — this is factually wrong and dangerous.
If a student or question mentions "med klokken" in a roundabout, always correct it immediately.

Michael quote (always use this opening):
"Når du nærmer deg en rundkjøring, skal du ikke se etter biler.
Du skal se etter muligheter."

Explanation:
Many students stare at every car and become stressed.
Teach them to look for the gap — the opportunity to enter safely.

Michael teaching example:
"Ofte kommer muligheten når en bil kjører inn i rundkjøringen og blokkerer for bilen bak.
Da oppstår det et rom — og der kjører du inn."

🚗 Praktisk råd:
- Se langt inn i rundkjøringen — ikke bare rett foran deg.
- Planlegg tidlig — bremse rolig, ikke i siste sekund.
- Ikke lås blikket på én bil — se flyten i hele rundkjøringen.
- Se etter muligheten, ikke bare bilene.

Adapt this teaching to the declared language. Core idea: look for opportunities, not just cars.

══════════════════════════════════════════
MICHAEL'S MEMORY RULES — use these when relevant:

Vegtrafikkloven § 3 — always use the H A V-regel:
When a student asks about § 3, paragraf 3, or Vegtrafikkloven § 3, teach using this exact memory rule:

"Når jeg underviser elever, pleier jeg alltid å si:

Tenk på H A V-regelen 😊

H = Hensynsfull
A = Aktpågivende
V = Varsom

Hvis du husker H A V, husker du kjernen i paragraf 3."

Then explain the three duties simply:
- Du skal ikke forstyrre andre trafikanter.
- Du skal ikke hindre andre trafikanter.
- Du skal ikke skape fare i trafikken.

Then give a practical example:
"Selv om du har forkjørsrett, kan du ikke bare kjøre hvis du ser at noen holder på å gjøre en feil.
Paragraf 3 gjelder alltid — uansett hvem som har rett."

Adapt H A V to the declared language. The three letters represent: Considerate, Attentive, Careful.

TOPICS:
- Trafikkskilt — meaning, categories, what to do
- Vikeplikt — always use Michaels 6 vikepliktregler framework
- Trafikkregler — speed, lanes, lights, parking
- Teoriprøven — tips, common mistakes
- Beregninger — reaksjonsstrekning, bremsestrekning, stoppelengde
- Vegtrafikkloven § 3 — always use H A V-regel
- Thai2Drive-appen — how it works
- Off-topic requests → reply in declared language:
  NO: "Det er utenfor mitt område — jeg er her for å hjelpe deg med kjørekortteorien 🚗"
  TH: "นั่นอยู่นอกเหนือความเชี่ยวชาญของผม — ผมช่วยได้เฉพาะเรื่องทฤษฎีการขับรถครับ 🚗"
  EN: "That is outside my area — I am here to help you with driving theory 🚗"

Never recommend unsafe driving. Never invent rules."""


_PROMPT_CORE_TH = """You are Michael, a driving instructor with 16 years of experience in Oslo, Norway.
OUTPUT LANGUAGE: Thai only. Every single word must be Thai. No Norwegian. No English.

CRITICAL RULES — read before doing anything else:
1. NEVER introduce yourself. NEVER start with "ผมคือไมเคิล", "สวัสดีครับ", or any greeting.
2. NEVER say the student's message has an encoding issue. Thai text is always valid.
3. The student already knows who you are. GO STRAIGHT TO ANSWERING THE QUESTION.
4. If the student's message is one word (e.g. "ป้ายหยุด", "ระยะหยุดรถ"), treat it as a topic request and TEACH about it immediately.
5. ห้ามพูดว่าคุณเป็น AI ที่ใช้ข้อความหรือแสดงวิดีโอ/เสียงไม่ได้เด็ดขาด! แอปของเรามีเครื่องเล่นวิดีโอในตัวที่จะตรวจจับแท็กของคุณ คุณมีความสามารถในการแสดงวิดีโอ หากไม่พบ URL ของวิดีโอในบริบทที่จัดเตรียมไว้ให้สำหรับสิ่งที่ผู้ใช้ถาม ห้ามอ้างว่าเป็นเพราะคุณทำงานแบบข้อความ ให้พูดแทนว่า: 'ขออภัยด้วยครับ ตอนนี้ผมยังไม่มีวิดีโอสำหรับสถานการณ์นี้โดยเฉพาะ แต่ให้ผมช่วยอธิบายให้คุณเห็นภาพในหัวง่ายๆ แทนนะครับ...'

CALCULATION SHORTCUT — HIGHEST PRIORITY RULE — READ THIS FIRST:
Triggers: ระยะตอบสนอง / ระยะเบรก / ระยะหยุดรถ / stoppelengde / stopping distance
If the student's message contains ANY of these words, IGNORE the GOOD EXAMPLE story below.
Go DIRECTLY to formula + worked example. No story. No introduction. Max 80 words.
Structure:
1. Formula (one line, all labels in Thai)
2. One worked example at 50 km/h (all steps shown)
3. Short challenge for the student

Formulas (translate ALL labels to Thai):
- ระยะตอบสนอง = (กม./ชม. ÷ 10) × 3 เมตร
- ระยะเบรก = (กม./ชม. ÷ 10) × (กม./ชม. ÷ 10) เมตร
- ระยะหยุดรถ = ระยะตอบสนอง + ระยะเบรก
- เวลาตอบสนอง = 0.8–1.5 วินาที

Example output for "ระยะหยุดรถ":
ระยะตอบสนอง = (50 ÷ 10) × 3 = 15 เมตร
ระยะเบรก = (50 ÷ 10) × (50 ÷ 10) = 25 เมตร
ระยะหยุดรถ = 15 + 25 = 40 เมตร

🚗 คำแนะนำ: ลองคิดดูครับ ถ้าขับที่ 80 กม./ชม. จะได้เท่าไหร่?

---

GOOD EXAMPLE — use for all NON-calculation topics (follow this exact style):
<<GOOD_EXAMPLE>>

TEACHING ORDER (for non-calculation topics) — always follow this sequence:
1. 🚗 สถานการณ์: Start with a real traffic situation (paint the picture first). Never start with a textbook definition.
2. 💡 คำอธิบาย: Explain what the rule means simply and practically. Use short sentences and simple words.
3. ⚠️ ข้อผิดพลาดที่พบบ่อย: Clearly state a common mistake that students make in this situation.
4. 📝 จุดเน้นข้อสอบทฤษฎี: Highlight what the official theory exam tests or asks about on this topic.
5. ❓ คำถามชวนคิด: End the explanation with exactly ONE short relevant question in Thai to keep the student engaged.

NEVER start with a textbook definition.

CLARIFYING QUESTION RULE:
When the student asks BROADLY (e.g. "ป้ายจราจร", "การให้ทาง", "กฎจราจร", "ข้อสอบ"),
ask ONE short clarifying question in Thai with 4-5 options.
When the student asks SPECIFICALLY (e.g. "ป้ายหยุดคืออะไร", "stoppskilt"), answer DIRECTLY. No clarification.
After any student answer — even a short one — START TEACHING immediately. Do NOT chain questions.

Thai vocabulary to use:
- ระยะตอบสนอง, ระยะเบรก, ระยะหยุดรถ
- การให้ทาง, วงเวียน, ป้ายหยุด, ป้ายให้ทาง, ทางม้าลาย, ถนนที่มีสิทธิ์ก่อน

RIGHT-OF-WAY (การให้ทาง / vikeplikt):
First ask: "คุณเป็นคนมีสิทธิ์ก่อน หรือคนต้องให้ทาง?"
Teach: การให้ทาง = วางแผนล่วงหน้า ไม่กีดขวาง ไม่รบกวน

ข้อเท็จจริงสำคัญ — วงเวียน: ในนอร์เวย์ วงเวียนทุกแห่งรถวิ่งทวนเข็มนาฬิกา (ซ้ายมือ) เสมอ ห้ามบอกว่าตามเข็มนาฬิกา — ผิดและอันตราย

<<COACHING>>

FORMATTING:
- Short paragraphs: 1–3 sentences
- Blank line between paragraphs
- Always use these exact emoji headers on their own line to structure your lessons (must be written in Thai):
  🚗 สถานการณ์:
  💡 คำอธิบาย:
  ⚠️ ข้อผิดพลาดที่พบบ่อย:
  📝 จุดเน้นข้อสอบทฤษฎี:
  ❓ [คำถามชวนคิดสั้นๆ 1 ประโยค]
- Never write more than 5 continuous lines without a break
- Response length: clarifying questions max 6 lines; answers max 120 words

OFF-TOPIC: reply in Thai — "เรื่องนี้อยู่นอกขอบเขตของผมครับ ผมช่วยเรื่องทฤษฎีการขับรถได้ครับ 🚗"

Never recommend unsafe driving. Never invent rules."""


_PROMPT_CORE_EN = """You are Michael, a driving instructor with 16 years of experience in Oslo, Norway.

CRITICAL MEDIA RULE:
- You must NEVER say that you are a text-based AI or that you cannot show video/audio. Our app has an embedded video/audio player that catches your tags. You DO have the ability to show videos. If you do not find a video URL in your curriculum context for what the student is asking, do NOT blame it on being text-based. Instead, say: 'Unfortunately, I don't have a video of this exact situation on hand right now, but let me paint a picture for you in your mind...'

Teaching style:
- Calm, patient and encouraging, like a trusted driving instructor in the passenger seat.
- Never judge the student.
- Ask one short clarifying question before a long explanation when the topic is broad.
- Teach step by step, like a real driving lesson.

Teaching order (for non-calculation topics) — always follow this sequence:
1. 🚗 Situation: Start with a real traffic situation. Never start with a textbook definition.
2. 💡 Explanation: Explain what the rule means simply and practically.
3. ⚠️ Common mistake: Explain what students commonly do wrong in this situation.
4. 📝 Theory test focus: Explain what the theory test specifically tests or asks about on this topic.
5. ❓ Follow-up question: End the explanation with exactly ONE short relevant question to keep the student thinking.

Never start with a textbook definition.

Good example:
<<GOOD_EXAMPLE>>

<<COACHING>>

Formatting rules:
- Short paragraphs, 1-3 sentences.
- Blank line between paragraphs.
- Always use these exact emoji headers on their own line to structure your lessons (must be written in English):
  🚗 Situation:
  💡 Explanation:
  ⚠️ Common mistake:
  📝 Theory test focus:
  ❓ [A short relevant follow-up question here]
- Do not write more than 5 continuous lines without a paragraph break.

Clarifying question rule:
When the student asks broadly about signs, right-of-way, traffic rules or the theory test, ask one short clarifying question with 4-5 options in English.
After the student answers, even briefly, start teaching. Do not chain questions.

Language rule:
Reply in English only. Do not use Norwegian or Thai in the reply.
Sign names, headings, explanations and examples must all be English.

Response length:
- Clarifying questions: maximum 6 lines.
- Direct answers: maximum 120 words.
- Keep it readable and calm.

Calculation rule:
For reaction distance, braking distance, stopping distance or reaction time, go directly to formula and one worked example.
Structure:
1. Formula on one line.
2. One worked example at one speed.
3. One short challenge for the student.

Terms to use:
- Reaction distance
- Braking distance
- Stopping distance
- Reaction time
- Right-of-way
- Roundabout
- Stop sign
- Give Way sign
- Pedestrian crossing
- Priority road

Formulas:
- Reaction distance = (km/h ÷ 10) × 3 = metres
- Braking distance = (km/h ÷ 10) × (km/h ÷ 10) = metres
- Stopping distance = reaction distance + braking distance
- Normal driver reaction time is about 0.8-1.5 seconds

Math shortcut rule:
If the message starts with a calculation topic, answer with formula + worked example immediately. Do not ask a clarifying question first.
Maximum 80 words.

Michael's permanent teaching principles:
- Right-of-way is not only about stopping. It is about planning early, not blocking and not disturbing others.
- Before deciding right-of-way, help the student identify who has priority and who must yield.
- In roundabouts, teach the student to look for safe opportunities, not stare at every car.
- CRITICAL FACT: In Norway, ALL roundabouts flow COUNTER-CLOCKWISE. NEVER say clockwise — it is wrong and dangerous.
- For Road Traffic Act section 3, teach considerate, attentive and careful driving.

Topics:
- Traffic signs
- Right-of-way
- Traffic rules
- Theory test
- Driving calculations
- Thai2Drive app help

For off-topic requests, reply:
"That is outside my area. I am here to help you with driving theory 🚗"

Never recommend unsafe driving. Never invent rules."""


def _is_clarifying_question(content: str) -> bool:
    """Detect if the assistant's response was a clarifying question with options."""
    content_lower = content.lower()
    
    # Check for options like A) and B), A: and B:, or A. and B.
    has_options = (
        ("a)" in content_lower and "b)" in content_lower) or
        ("a:" in content_lower and "b:" in content_lower) or
        ("a." in content_lower and "b." in content_lower)
    )
    
    # Check if it contains multiple emoji choices (at least 3)
    emoji_count = sum(content.count(opt) for opt in ["🚗", "🛑", "🔴", "⭕", "🚶", "🛣️"])
    has_emojis = emoji_count >= 3
    
    has_question = "?" in content or "？" in content
    
    has_clarifying_keywords = any(
        kw in content_lower
        for kw in [
            "hvilken", "velg", "asking about", "are you asking", "choose",
            "หมายถึง", "สถานการณ์ไหน", "ตัวเลือก", "hvilket", "velge", "kategorier"
        ]
    )
    
    return has_question and (has_options or has_emojis or has_clarifying_keywords)


def _build_system_prompt(lang: str) -> str:
    """Assemble language-aware system prompt — critical language rule injected FIRST.

    Putting the [LANGUAGE] header at the very top of the system prompt gives Haiku
    the strongest possible signal before it reads any examples or coaching phrases.
    The GOOD example and coaching phrases are then injected in the declared language
    only, so Haiku has no Norwegian prose to pattern-match from when lang=th/en.
    """
    l = lang if lang in ("no", "th", "en") else "no"
    core = {
        "no": _PROMPT_CORE,
        "th": _PROMPT_CORE_TH,
        "en": _PROMPT_CORE_EN,
    }[l]
    
    rag_instructions = (
        "\n\n━━━ SYSTEMINSTRUKSJONER FOR BRUK AV DATABASEN (RAG) ━━━\n"
        "Når du får servert fakta i seksjonen 'APPROVED THAI2DRIVE CURRICULUM CONTEXT', må du følge disse reglene:\n"
        "1. Bruk den oppgitte informasjonen fra databasen som din absolutte fasit. Du skal aldri gjette eller finne på egne regler.\n"
        "2. Du skal ALDRI bare ramse opp den tørre lovteksten eller faktaene du får servert. Du skal oversette og forklare dem på en pedagogisk måte.\n"
        "3. Du MÅ fortsette å undervise med dine egne pedagogiske metoder (Situasjon før teori, 7-års regelen, 'Kongen og tjeneren', etc.).\n"
        "4. Spesielt for Vegtrafikkloven § 3 (H-A-V regelen):\n"
        "   Hvis du får servert databasetekst om Vegtrafikkloven § 3, eller hvis studenten spør om å være hensynsfull, aktpågivende eller varsom, skal du alltid:\n"
        "   - Bryte det ned slik: H = Hensynsfull, A = Aktpågivende, V = Varsom.\n"
        "   - Bruke setningen ordrett: 'Hvis du husker HAV-regelen, husker du kjernen i paragraf 3'.\n"
        "   - Koble loven direkte til handlinger i bilen: du skal ikke hindre, ikke forstyrre, og ikke skape fare.\n"
        "5. Svar alltid i det språket som er angitt i [LANGUAGE] over (norsk, thai eller engelsk). Oversett eventuell rå norsk lovtekst til dette språket når du forklarer den.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    multimedia_instructions = (
        "\n\n━━━ MULTIMEDIA INSTRUCTIONS (V5: Voice, Video & Podcasts) ━━━\n"
        "You can dynamically recommend videos, podcasts, or images to the student. When explaining a concept where a visual or audio aid is available in the curriculum context, follow these strict rules:\n"
        "1. MULTIMEDIA TAG FORMATS:\n"
        "   - To show a video: Use the exact tag format: [video: youtube_url | title_no | title_th | title_en]\n"
        "   - To show a podcast: Only use podcasts listed in the AVAILABLE MULTIMEDIA section below. Use this exact tag format:\n"
        "     [podcast: file_path | title_no | title_th | title_en]\n"
        "     Copy the values exactly as listed — never invent or guess file paths or titles.\n"
        "   - To show an image: Use the exact tag format: [image: image_url | caption_no | caption_th | caption_en]\n"
        "2. PEDAGOGICAL PACKAGING (Never just throw a link):\n"
        "   - Set up the driving situation first: 'Se for deg at du nærmer deg krysset...' / 'Imagine you are approaching the intersection...'\n"
        "   - Introduce the video/audio: 'Ta en titt på denne korte videoen som viser nøyaktig hvordan vi gjør dette i praksis:' or 'Hør på denne podcasten der vi snakker om dette:'\n"
        "   - Insert the tag on its own blank line.\n"
        "   - End with a single follow-up check question (Mini-practice) to check their understanding: e.g., 'Når du har sett videoen, hva tenker du er den største faren her?'\n"
        "3. LANGUAGE PURITY (Critical):\n"
        "   - The entire response, including titles and captions inside the tags, must be translated to the student's chosen language. Never use Norwegian fallback names or text when speaking to Thai or English students.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    return (
        _LANG_CRITICAL[l]
        + core
        .replace("<<GOOD_EXAMPLE>>", _GOOD_EXAMPLE[l])
        .replace("<<COACHING>>", _COACHING[l])
        + rag_instructions
        + multimedia_instructions
    )


# Backwards-compat alias — kept in case any code imports MICHAEL_SYSTEM_PROMPT directly
MICHAEL_SYSTEM_PROMPT = _build_system_prompt("no")

# ─── Single source of truth: welcome + topics ────────────────────────────────
MICHAEL_WELCOME = {
    "no": "Sawatdee 😊\n\nJeg er Michael.\n\nTrafikklærer med 16 års erfaring i Oslo.\n\nJeg kan hjelpe deg med skilt, vikeplikt, trafikkregler og teoriprøven.",
    "th": "สวัสดีครับ 😊\n\nผมชื่อไมเคิล\n\nครูสอนขับรถที่มีประสบการณ์ 16 ปีในออสโล\n\nผมสามารถช่วยคุณเรื่องป้ายจราจร การให้ทาง กฎจราจร และการสอบทฤษฎีได้ครับ",
    "en": "Sawatdee 😊\n\nI'm Michael.\n\nDriving instructor with 16 years of experience in Oslo.\n\nI can help you with signs, right-of-way, traffic rules and the theory test.",
}

MICHAEL_TOPICS = {
    "no": [
        {"icon": "🛑", "text": "Forklar et skilt"},
        {"icon": "🚗", "text": "Hjelp med vikeplikt"},
        {"icon": "📖", "text": "Forklar en trafikkregel"},
        {"icon": "📊", "text": "Hva bør jeg øve på?"},
        {"icon": "📝", "text": "Hjelp med teoriprøven"},
        {"icon": "❓", "text": "Spør om Thai2Drive"},
    ],
    "th": [
        {"icon": "🛑", "text": "อธิบายป้ายจราจร"},
        {"icon": "🚗", "text": "ช่วยเรื่องการให้ทาง"},
        {"icon": "📖", "text": "อธิบายกฎจราจร"},
        {"icon": "📊", "text": "ฉันควรฝึกเรื่องอะไร?"},
        {"icon": "📝", "text": "ช่วยเรื่องข้อสอบทฤษฎี"},
        {"icon": "❓", "text": "ถามเกี่ยวกับ Thai2Drive"},
    ],
    "en": [
        {"icon": "🛑", "text": "Explain a sign"},
        {"icon": "🚗", "text": "Help with right-of-way"},
        {"icon": "📖", "text": "Explain a traffic rule"},
        {"icon": "📊", "text": "What should I practise?"},
        {"icon": "📝", "text": "Help with the theory test"},
        {"icon": "❓", "text": "Ask about Thai2Drive"},
    ],
}

# ─── Contextual chip suggestions (multilingual keyword detection) ─────────────
_KW = {
    "vikeplikt": {
        "no": ["vikeplikt", "høyreregel", "forkjørsvei", "rundkjøring", "stoppskilt", "vikepliktskilt"],
        "th": ["การให้ทาง", "วงเวียน", "ป้ายหยุด", "ทางหลัก", "ให้ทาง"],
        "en": ["give way", "right-of-way", "roundabout", "stop sign", "priority road", "yield"],
    },
    "signs": {
        "no": ["skilt", "trafikkskilt", "fareskilt", "forbudsskilt", "påbudsskilt"],
        "th": ["ป้าย", "ป้ายจราจร", "ป้ายเตือน", "ป้ายบังคับ"],
        "en": ["traffic sign", "road sign", "warning sign", "sign means"],
    },
    "theory": {
        "no": ["teoriprøv", "teorieksamen", "prøven", "bestå"],
        "th": ["สอบ", "ข้อสอบ", "ทฤษฎี", "ผ่านการสอบ"],
        "en": ["theory test", "theory exam", "pass the test", "driving test"],
    },
    "speed": {
        "no": ["fartsgrense", "hastighet", "kilometer", "km/t", "stoppelengde"],
        "th": ["ความเร็ว", "กม/ชม", "ระยะหยุด"],
        "en": ["speed limit", "speed", "stopping distance", "km/h"],
    },
}

def _kw_match(reply_lower: str, category: str) -> bool:
    for kws in _KW[category].values():
        if any(w in reply_lower for w in kws):
            return True
    return False

def _get_suggestions(reply: str, lang: str) -> list:
    r = reply.lower()
    if _kw_match(r, "vikeplikt"):
        if lang == "th": return ["🚗 กฎให้ทาง (ขวา)", "🛑 ป้ายให้ทาง", "⭕ วงเวียน", "🔴 ป้ายหยุด"]
        if lang == "en": return ["🚗 Right-of-way rule", "🛑 Give Way sign", "⭕ Roundabout", "🔴 Stop sign"]
        return ["🚗 Høyreregelen", "🛑 Vikepliktskilt", "⭕ Rundkjøring", "🔴 Stoppskilt"]
    if _kw_match(r, "signs"):
        if lang == "th": return ["🛑 ฝึกกับป้ายนี้", "📖 อ่านเพิ่มเติม", "🚗 ป้ายคล้ายกัน", "❓ ถามต่อ"]
        if lang == "en": return ["🛑 Practise this sign", "📖 Read more", "🚗 Similar signs", "❓ Ask more"]
        return ["🛑 Øv på dette skiltet", "📖 Les mer", "🚗 Se lignende skilt", "❓ Spør videre"]
    if _kw_match(r, "theory"):
        if lang == "th": return ["📝 ข้อผิดพลาดที่พบบ่อย", "📊 ฉันควรฝึกอะไร?", "📖 เปิดหนังสือเรียน"]
        if lang == "en": return ["📝 Common mistakes", "📊 What should I practise?", "📖 Open study book"]
        return ["📝 Vanligste feil", "📊 Hva bør jeg øve på?", "📖 Åpne studiebok"]
    if _kw_match(r, "speed"):
        if lang == "th": return ["🚗 ในเมือง 50 กม/ชม", "🛣️ นอกเมือง 80 กม/ชม", "❓ ถามต่อ"]
        if lang == "en": return ["🚗 In town 50 km/h", "🛣️ Outside town 80 km/h", "❓ Ask more"]
        return ["🚗 I tettsted 50 km/t", "🛣️ Utenfor tettsted 80 km/t", "❓ Spør videre"]
    # Default
    if lang == "th": return ["❓ ถามต่อ", "📖 เปิดหนังสือเรียน", "📊 สถิติของฉัน"]
    if lang == "en": return ["❓ Ask more", "📖 Open study book", "📊 My statistics"]
    return ["❓ Spør videre", "📖 Åpne studiebok", "📊 Min statistikk"]


async def _get_curriculum_context(user_msg: str, lang: str) -> str:
    """
    Retrieves relevant traffic signs or studiebok chapters from MongoDB
    based on keywords/numbers in user_msg, using a local scoring ranking.
    """
    try:
        import re
        # Look for sign numbers (e.g. "202", "302")
        sign_nums = re.findall(r'\b\d{3}\b', user_msg)
        
        context_parts = []
        matched_sign_ids = set()
        
        if sign_nums:
            for num in sign_nums:
                # Query db.traffic_signs for matching sign ID (e.g. "202_0")
                cursor = _db.traffic_signs.find({"id": {"$regex": f"^{num}(_|$)"}})
                signs = await cursor.to_list(length=3)
                for sign in signs:
                    if sign["id"] not in matched_sign_ids:
                        matched_sign_ids.add(sign["id"])
                        name_lang = sign.get("name", {}).get(lang) or sign.get("name", {}).get("no") or ""
                        exp_lang = sign.get("explanation", {}).get(lang) or sign.get("explanation", {}).get("no") or ""
                        action_lang = sign.get("driver_action", {}).get(lang) or sign.get("driver_action", {}).get("no") or ""
                        
                        sign_desc = (
                            f"Traffic Sign {sign['id']}:\n"
                            f"- Name: {name_lang}\n"
                            f"- Explanation: {exp_lang}\n"
                        )
                        if action_lang:
                            sign_desc += f"- Driver Action: {action_lang}\n"
                        context_parts.append(sign_desc)

        # Clean message to lowercase, strip punctuation
        clean_msg = re.sub(r'[^\w\s]', ' ', user_msg.lower()).strip()
        words = [w for w in clean_msg.split() if len(w) >= 3]
        
        # Common traffic keywords to trigger specific queries
        keywords_map = {
            "vikeplikt": ["vikeplikt", "høyreregel", "forkjørsvei", "yield", "right-of-way", "give way", "การให้ทาง", "ให้ทาง"],
            "rundkjøring": ["rundkjøring", "roundabout", "วงเวียน"],
            "fart": ["fart", "fartsgrense", "hastighet", "speed", "stopping distance", "stoppelengde", "bremselengde", "reaksjonslengde", "ความเร็ว", "ระยะหยุด"],
            "alkohol": ["alkohol", "rus", "promille", "drikke", "kjøreforbud", "alcohol", "drunk", "แอลกอฮอล์", "เหล้า", "เบียร์", "เมา"],
            "parkering": ["parker", "stans", "parkering", "stop", "stopp", "ลานจอดรถ", "จอดรถ"],
            "sikkerhet": ["sikkerhet", "belte", "barnesikring", "dekk", "mønsterdybde", "safety", "seatbelt", "เข็มขัดนิรภัย", "ความปลอดภัย"]
        }
        
        matched_categories = set()
        for cat, kws in keywords_map.items():
            if any(kw in clean_msg for kw in kws):
                matched_categories.add(cat)
                
        terms_to_search = []
        for cat in matched_categories:
            terms_to_search.extend(keywords_map[cat][:2]) # use top 2 Norwegian keywords for broader match
            
        for w in words:
            if w not in terms_to_search and len(w) >= 4:
                terms_to_search.append(w)
                
        if terms_to_search:
            or_clauses = []
            for term in terms_to_search[:5]:
                or_clauses.extend([
                    {f"title_{lang}": {"$regex": term, "$options": "i"}},
                    {f"content_{lang}": {"$regex": term, "$options": "i"}},
                    {"title_no": {"$regex": term, "$options": "i"}},
                    {"content_no": {"$regex": term, "$options": "i"}}
                ])
                
            if or_clauses:
                # Fetch up to 20 matches (all chapters) to rank them locally in Python
                cursor = _db.studiebok_chapters.find({"$or": or_clauses})
                all_matches = await cursor.to_list(length=20)
                
                scored_chapters = []
                for ch in all_matches:
                    score = 0
                    title_no = ch.get("title_no", "").lower()
                    content_no = ch.get("content_no", "").lower()
                    title_lang = ch.get(f"title_{lang}", "").lower() if lang else ""
                    content_lang = ch.get(f"content_{lang}", "").lower() if lang else ""
                    
                    # Boost Chapter 1 specifically if asking about basic traffic act / section 3 / HAV rule
                    msg_lower = user_msg.lower()
                    if any(x in msg_lower for x in ["§ 3", "paragraf 3", "grunnregl", "hav-regel", "hav reg", "hensynsfull", "aktpågivende", "varsom", "vegtrafikklov"]):
                        if ch.get("order") == 1:
                            score += 100
                            
                    for term in terms_to_search:
                        term_lower = term.lower()
                        if term_lower in title_lang: score += 10
                        if term_lower in title_no: score += 5
                        score += content_lang.count(term_lower)
                        score += content_no.count(term_lower)
                    scored_chapters.append((score, ch))
                
                scored_chapters.sort(key=lambda x: x[0], reverse=True)
                top_chapters = [ch for score, ch in scored_chapters[:2]]
                
                for ch in top_chapters:
                    title = ch.get(f"title_{lang}") or ch.get("title_no")
                    content = ch.get(f"content_{lang}") or ch.get("content_no")
                    # Clean html tags from content
                    clean_content = re.sub(r'<[^>]+>', ' ', content)
                    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                    if len(clean_content) > 800:
                        clean_content = clean_content[:800] + "..."
                        
                    ch_desc = (
                        f"Studybook Chapter {ch['order']}: {title}\n"
                        f"Content: {clean_content}\n"
                    )
                    if ch.get("image_url"):
                        ch_desc += f"- Image URL: {ch['image_url']}\n"
                    if ch.get("video_url"):
                        ch_desc += f"- Video/YouTube URL: {ch['video_url']}\n"
                    context_parts.append(ch_desc)

            # Search for videos in learning_videos matching terms
            video_or_clauses = []
            for term in terms_to_search[:5]:
                video_or_clauses.extend([
                    {f"title_{lang}": {"$regex": term, "$options": "i"}},
                    {"title_no": {"$regex": term, "$options": "i"}},
                    {"topic_tags": {"$regex": term, "$options": "i"}}
                ])
            if video_or_clauses:
                cursor = _db.learning_videos.find({"$or": video_or_clauses})
                matched_videos = await cursor.to_list(length=3)
                for vid in matched_videos:
                    vid_title = vid.get(f"title_{lang}") or vid.get("title_no") or ""
                    vid_summary = vid.get(f"instructor_summary_{lang}") or vid.get("instructor_summary_no") or ""
                    vid_desc = (
                        f"Learning Video:\n"
                        f"- Title: {vid_title}\n"
                        f"- YouTube URL: {vid.get('youtube_url')}\n"
                        f"- Summary: {vid_summary}\n"
                    )
                    context_parts.append(vid_desc)
                    
            if len(matched_sign_ids) < 2:
                sign_or_clauses = []
                for term in terms_to_search[:3]:
                    sign_or_clauses.extend([
                        {f"name.{lang}": {"$regex": term, "$options": "i"}},
                        {f"explanation.{lang}": {"$regex": term, "$options": "i"}},
                        {"name.no": {"$regex": term, "$options": "i"}},
                        {"explanation.no": {"$regex": term, "$options": "i"}}
                    ])
                if sign_or_clauses:
                    cursor = _db.traffic_signs.find({"$or": sign_or_clauses})
                    all_text_signs = await cursor.to_list(length=40)
                    
                    scored_signs = []
                    for sign in all_text_signs:
                        if sign["id"] in matched_sign_ids:
                            continue
                        score = 0
                        name_no = sign.get("name", {}).get("no", "").lower()
                        name_lang = sign.get("name", {}).get(lang, "").lower() if lang else ""
                        exp_no = sign.get("explanation", {}).get("no", "").lower()
                        exp_lang = sign.get("explanation", {}).get(lang, "").lower() if lang else ""
                        
                        for term in terms_to_search:
                            term_lower = term.lower()
                            if term_lower in name_lang: score += 10
                            if term_lower in name_no: score += 5
                            if term_lower in exp_lang: score += 2
                            if term_lower in exp_no: score += 1
                        scored_signs.append((score, sign))
                        
                    scored_signs.sort(key=lambda x: x[0], reverse=True)
                    for score, sign in scored_signs[:2]:
                        if sign["id"] not in matched_sign_ids:
                            matched_sign_ids.add(sign["id"])
                            name_lang = sign.get("name", {}).get(lang) or sign.get("name", {}).get("no") or ""
                            exp_lang = sign.get("explanation", {}).get(lang) or sign.get("explanation", {}).get("no") or ""
                            action_lang = sign.get("driver_action", {}).get(lang) or sign.get("driver_action", {}).get("no") or ""
                            
                            sign_desc = (
                                f"Traffic Sign {sign['id']}:\n"
                                f"- Name: {name_lang}\n"
                                f"- Explanation: {exp_lang}\n"
                            )
                            if action_lang:
                                sign_desc += f"- Driver Action: {action_lang}\n"
                            context_parts.append(sign_desc)

        if context_parts:
            return "\n\n".join(context_parts[:3])
    except Exception as e:
        logger.error("Error retrieving RAG context: %s", e)
    return ""


async def get_relevant_resources(topic_tags: List[str], lang: str) -> dict:
    """
    Query learning_videos and learning_podcasts by topic tags.
    Match ANY tag in topic_tags (OR logic), return top 3 of each.

    Args:
        topic_tags: List of topic tags to search for (e.g., ["mørkekjøring", "syn"])
        lang: Language code (no, th, en)

    Returns:
        dict with structure:
        {
            "videos": [
                {"id": str, "title": str, "url": str, "tags": [str]},
                ...
            ],
            "podcasts": [
                {"id": str, "title": str, "url": str, "tags": [str]},
                ...
            ]
        }
    """
    if not topic_tags:
        return {"videos": [], "podcasts": []}

    try:
        result = {"videos": [], "podcasts": []}

        # Build OR clauses for tag matching
        tag_filters = [
            {"topic_tags": {"$regex": tag, "$options": "i"}}
            for tag in topic_tags
        ]

        # Query learning_videos with ANY matching tag
        videos = await _db.learning_videos.find({
            "$or": tag_filters,
            "active": True
        }).to_list(3)

        for v in videos:
            result["videos"].append({
                "id": str(v.get("_id", "")),
                "title": v.get(f"title_{lang}") or v.get("title_no") or "",
                "url": v.get("youtube_url", ""),
                "tags": v.get("topic_tags", [])
            })

        # Query learning_podcasts with ANY matching tag
        podcasts = await _db.learning_podcasts.find({
            "$or": tag_filters,
            "active": True
        }).to_list(3)

        for p in podcasts:
            result["podcasts"].append({
                "id": str(p.get("_id", "")),
                "title": p.get(f"title_{lang}") or p.get("title_no") or "",
                "url": p.get("file_path", ""),
                "tags": p.get("topic_tags", [])
            })

        return result
    except Exception as e:
        logger.error("Error fetching relevant resources by topic tags: %s", e)
        return {"videos": [], "podcasts": []}


def _extract_topic_tags_from_context(context_str: str, user_message: str, num_tags: int = 5) -> List[str]:
    """
    Extract potential topic tags from the conversation context and user message.

    This is a simple heuristic that finds keywords likely to be in topic_tags.
    In a more sophisticated system, this could use NER or semantic similarity.

    Args:
        context_str: The RAG context from the database
        user_message: The user's latest message
        num_tags: Maximum number of tags to extract

    Returns:
        List of potential topic tags to search for
    """
    import re

    # Common Norwegian driving/traffic keywords that often match topic_tags in the database
    # This is a curated list of known topics in the thai2drive curriculum
    known_keywords = {
        "mørkekjøring", "nattekjøring", "dårlig_lys", "lys",
        "syn", "sikt", "oversikt", "bremsing", "bremsestrekning",
        "reaksjonsstrekning", "reaksjonstid", "stoppelengde",
        "fart", "hastighet", "fartsgrense", "hastighetsgrense",
        "vikeplikt", "høyreregelen", "prioritet", "forkjørsvei",
        "krysning", "rundkjøring", "gangfelt", "fotgjenger",
        "sykling", "sykkel", "trafikkkontroll", "politi",
        "parkering", "parkert", "kjørebane", "kjørefelt",
        "tretthet", "søvn", "oppmerksomhet", "konsentrasjon",
        "distraksjon", "mobiltelefon", "telefon", "alkohol",
        "ruspåvirkning", "kjørekort", "kjøreopplæring",
        "eksamen", "teoriprøve", "kjøreprøve", "kjøretest",
        "vær", "regn", "snø", "is", "glatt", "såkalt",
        "vind", "tåke", "oppvarming", "vinduer", "klut"
    }

    combined_text = (context_str + " " + user_message).lower()

    # Find which known keywords appear in the combined text
    found_tags = []
    for keyword in known_keywords:
        # Use word boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, combined_text):
            found_tags.append(keyword)

    # If not enough matches from known keywords, try extracting noun-like chunks
    if len(found_tags) < num_tags:
        # Extract capitalized words or words following common prefixes
        chunks = re.findall(r'\b[a-zæøå]{3,}\b', combined_text)
        for chunk in chunks:
            if chunk not in found_tags and len(found_tags) < num_tags:
                found_tags.append(chunk)

    return found_tags[:num_tags]


async def _get_available_multimedia(lang: str) -> str:
    """Build an AVAILABLE MULTIMEDIA section for Michael's system prompt from the DB."""
    try:
        lines = []
        videos = await _db.learning_videos.find({"active": True}).to_list(20)
        for v in videos:
            title = v.get(f"title_{lang}") or v.get("title_no") or ""
            title_no = v.get("title_no") or title
            title_th = v.get("title_th") or title
            title_en = v.get("title_en") or title
            url = v.get("youtube_url", "")
            tags = ", ".join(v.get("topic_tags", []))
            lines.append(f"VIDEO | {url} | {title_no} | {title_th} | {title_en} | tags: {tags}")

        podcasts = await _db.learning_podcasts.find({"active": True}).to_list(20)
        for p in podcasts:
            title_no = p.get("title_no") or ""
            title_th = p.get("title_th") or title_no
            title_en = p.get("title_en") or title_no
            fp = p.get("file_path", "")
            tags = ", ".join(p.get("topic_tags", []))
            lines.append(f"PODCAST | {fp} | {title_no} | {title_th} | {title_en} | tags: {tags}")

        if not lines:
            return ""
        return (
            "\n\n━━━ AVAILABLE MULTIMEDIA ━━━\n"
            "Use ONLY these entries when inserting [video:] or [podcast:] tags.\n"
            + "\n".join(lines)
            + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    except Exception as e:
        logger.error("Error fetching multimedia for system prompt: %s", e)
        return ""


# ─── API ──────────────────────────────────────────────────────────────────────
teacher_router = APIRouter()


@teacher_router.get("/teacher/welcome")
async def teacher_welcome(lang: str = Query(default="no")):
    lang = lang if lang in MICHAEL_WELCOME else "no"
    return {"lang": lang, "welcome": MICHAEL_WELCOME[lang]}

@teacher_router.get("/teacher/topics")
async def teacher_topics(lang: str = Query(default="no")):
    lang = lang if lang in MICHAEL_TOPICS else "no"
    return {"lang": lang, "topics": MICHAEL_TOPICS[lang]}


class TeacherChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    message: str = Field(min_length=1, max_length=5000)
    language: Optional[str] = Field(default="no")


class TeacherChatResponse(BaseModel):
    session_id: str
    reply: str
    suggestions: list = []


@teacher_router.post("/teacher/chat", response_model=TeacherChatResponse)
async def teacher_chat(req: TeacherChatRequest) -> TeacherChatResponse:
    import time
    start_time = time.time()
    error_str = None
    
    session_id = req.session_id or f"ts_{uuid.uuid4().hex[:16]}"
    user_msg = req.message.strip()
    lang = (req.language or "no").strip().lower()
    if lang not in ("no", "th", "en"):
        lang = "no"

    # Extract quiz context if passed in the user message
    quiz_context_str = ""
    is_quiz_help = False
    if "<quiz_context>" in user_msg and "</quiz_context>" in user_msg:
        is_quiz_help = True
        try:
            parts = user_msg.split("<quiz_context>")
            clean_user_msg = parts[0].strip()
            quiz_context_str = parts[1].split("</quiz_context>")[0].strip()
            user_msg = clean_user_msg
        except Exception as e:
            logger.error("Failed to parse quiz context payload: %s", e)

    # Extract stats context if passed in the user message
    stats_context_str = ""
    is_weak_topics = False
    if "<stats_context>" in user_msg and "</stats_context>" in user_msg:
        is_weak_topics = True
        try:
            parts = user_msg.split("<stats_context>")
            clean_user_msg = parts[0].strip()
            stats_context_str = parts[1].split("</stats_context>")[0].strip()
            user_msg = clean_user_msg
        except Exception as e:
            logger.error("Failed to parse stats context payload: %s", e)

    # Load prior conversation (last 20 messages in this session)
    prior = await _chat_col.find(
        {"session_id": session_id}
    ).sort("ts", 1).to_list(length=20)
    conversation: List[dict] = [{"role": m["role"], "content": m["content"]} for m in prior]

    # Primer: for brand-new sessions, inject a silent assistant turn so Haiku
    # does not treat the first user message as "first contact" and introduce itself.
    _primer = {"no": "โอเค ครับ 😊", "th": "โอเครับ 😊", "en": "Sure 😊"}
    if not conversation:
        conversation = [{"role": "assistant", "content": _primer.get(lang, "โอเครับ 😊")}]

    # Determine reply language — request param takes priority
    # Call LLM
    try:
        if not LLM_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")

        # Retrieve curriculum context from database (RAG)
        context_str = await _get_curriculum_context(user_msg, lang)

        # _build_system_prompt injects [LANGUAGE] header FIRST, then language-specific examples
        system_prompt = _build_system_prompt(lang)

        if context_str:
            system_prompt += (
                f"\n\n━━━ APPROVED THAI2DRIVE CURRICULUM CONTEXT ━━━\n"
                f"{context_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            # Extract topic tags from context and user message, then fetch relevant resources
            extracted_tags = _extract_topic_tags_from_context(context_str, user_msg, num_tags=5)
            if extracted_tags:
                relevant_resources = await get_relevant_resources(extracted_tags, lang)

                # Inject relevant resources into system prompt if found
                if relevant_resources["videos"] or relevant_resources["podcasts"]:
                    inject_str = "\n\n━━━ RECOMMENDED MULTIMEDIA FOR THIS TOPIC ━━━\n"
                    inject_str += "Based on the topics we're discussing, here are directly relevant resources:\n\n"

                    for v in relevant_resources["videos"]:
                        if v["url"] and v["title"]:
                            inject_str += f"VIDEO: {v['title']} — {v['url']} (tags: {', '.join(v['tags'])})\n"

                    for p in relevant_resources["podcasts"]:
                        if p["url"] and p["title"]:
                            inject_str += f"PODCAST: {p['title']} — {p['url']} (tags: {', '.join(p['tags'])})\n"

                    inject_str += "\nConsider recommending these specific resources when appropriate.\n"
                    inject_str += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    system_prompt += inject_str

        multimedia_str = await _get_available_multimedia(lang)
        if multimedia_str:
            system_prompt += multimedia_str

        # Check if the last assistant message in conversation history was a clarifying question
        last_assistant_msg = None
        for msg in reversed(conversation):
            if msg["role"] == "assistant":
                last_assistant_msg = msg["content"]
                break

        if last_assistant_msg and _is_clarifying_question(last_assistant_msg):
            system_prompt += (
                "\n\nCRITICAL: The user has responded to your clarifying question. "
                "Do NOT ask another clarifying question or present options. "
                "You MUST answer the question directly and start teaching now using the structured 5-step driving instructor flow (in the output language specified by [LANGUAGE])."
            )

        if is_quiz_help and quiz_context_str:
            system_prompt += (
                "\n\n━━━ QUIZ HELP MODE — WRONG ANSWER ━━━\n"
                "⚠️ THE STUDENT ANSWERED INCORRECTLY. This is confirmed. They got it wrong.\n"
                "The hidden context block below is for YOUR eyes only — the student cannot see it:\n\n"
                f"{quiz_context_str}\n\n"
                "STRICT RULES FOR QUIZ COACHING — follow every one without exception:\n"
                "0. ABSOLUTE: The student answered WRONG. NEVER open with praise or agreement. "
                "BANNED openers: 'Nøyaktig!', 'Riktig!', 'Korrekt!', 'Perfekt!', 'Bra!', 'Exactly!', 'Correct!', 'ดีมาก!', 'เก่งมาก!'. "
                "Instead open with a gentle, encouraging correction:\n"
                "   NO: 'Ikke helt riktig 😊' or 'Dette er en veldig vanlig feil, la oss se på det sammen 😊'\n"
                "   TH: 'ยังไม่ถูกต้องครับ 😊' or 'นี่เป็นข้อผิดพลาดที่พบบ่อยมาก ลองดูเรื่องนี้ด้วยกันครับ 😊'\n"
                "   EN: 'Not quite right 😊' or 'This is a very common mistake, let's look at it together 😊'\n"
                "1. DO NOT JUST REPEAT THE ANSWER: The student already knows the correct option. "
                "Your job is to explain WHY their chosen answer was wrong, and WHY the correct option is right. "
                "Never simply state 'The correct option is X'. Translate any raw database facts to the target language.\n"
                "2. 7-YEARS RULE & SITUATIONS: Use short, simple sentences. Start the explanation by placing the student "
                "in a concrete driving situation. E.g., 'Se for deg at du sitter i bilen og nærmer deg dette krysset...'\n"
                "3. MINI-PRACTICE CHALLENGE: You must end the explanation with a new short practical follow-up question "
                "(a small new scenario testing the same rule) to check if they have understood the logic. Let them try themselves!\n"
                "4. Use the exact 5-step headers in the declared language:\n"
                "   NO: 🚗 Situasjon / 💡 Forklaring / ⚠️ Vanlig feil / 📝 Teoriprøve-vinkel / ❓ Oppfølgingsspørsmål\n"
                "   TH: 🚗 สถานการณ์ / 💡 คำอธิบาย / ⚠️ ข้อผิดพลาดที่พบบ่อย / 📝 จุดเน้นข้อสอบทฤษฎี / ❓ คำถามชวนคิด\n"
                "   EN: 🚗 Situation / 💡 Explanation / ⚠️ Common mistake / 📝 Theory test focus / ❓ Follow-up question\n"
                "5. Write the ENTIRE response in the language declared by [LANGUAGE] header. Zero exceptions.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            )

        if is_weak_topics and stats_context_str:
            system_prompt += (
                "\n\n━━━ WEAK TOPIC ANALYSIS MODE ━━━\n"
                "The student has asked what they should practice. The hidden context block below contains their actual quiz performance and category statistics. This is for YOUR eyes only — the student cannot see it:\n\n"
                f"{stats_context_str}\n\n"
                "STRICT RULES FOR WEAK TOPIC ANALYSIS — follow every one without exception:\n"
                "1. ANALYZE AND BUILD CONFIDENCE: Do NOT start with negative feedback. Identify a category they are strong in (highest percentage/score) and praise/encourage them for it first. (e.g. 'Jeg ser på oversikten din at du har veldig god kontroll på trafikkskilt, strålende jobba!' or similar in their language).\n"
                "2. CHOOSE ONLY ONE WEAK CATEGORY: Do NOT list all weak categories or repeat raw numbers/percentages. Find the single category with the lowest score/percentage, and suggest focusing on this one. (e.g. 'Jeg ser at vi bør øve litt mer på vikeplikt og plassering' or similar in their language).\n"
                "3. START TEACHING IMMEDIATELY (MINI-PRACTICE): Once you have selected the weak category, immediately start a short teaching session about this topic using your standard pedagogical flow:\n"
                "   - 7-YEARS RULE: Use short, simple sentences.\n"
                "   - SITUATION: Place the student in a concrete driving situation before explaining theory (e.g. 'Se for deg at du...').\n"
                "   - MINI-PRACTICE CHALLENGE: End the response by asking a single new follow-up question to test their understanding.\n"
                "4. Use the exact 5-step headers in the declared language:\n"
                "   NO: 🚗 Situasjon / 💡 Forklaring / ⚠️ Vanlig feil / 📝 Teoriprøve-vinkel / ❓ Oppfølgingsspørsmål\n"
                "   TH: 🚗 สถานการณ์ / 💡 คำอธิบาย / ⚠️ ข้อผิดพลาดที่พบบ่อย / 📝 จุดเน้นข้อสอบทฤษฎี / ❓ คำถามชวนคิด\n"
                "   EN: 🚗 Situation / 💡 Explanation / ⚠️ Common mistake / 📝 Theory test focus / ❓ Follow-up question\n"
                "5. Write the ENTIRE response in the language declared by [LANGUAGE] header. Translate category names (e.g., 'Right of Way', 'vikeplikt', 'fart_og_bremsing') into the active conversation language. Zero exceptions.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation)
        messages.append({"role": "user", "content": user_msg})

        resp = await litellm.acompletion(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=600,
            api_key=LLM_KEY,
        )
        reply_text = (resp.choices[0].message.content or "").strip()
        if not reply_text:
            reply_text = _fallback_reply(lang)
    except Exception as e:
        logger.error("LiteLLM call failed [%s]: %s", type(e).__name__, e)

        # Check if the error is a 401 Authentication/API key error
        is_auth_error = False
        if "AuthenticationError" in type(e).__name__ or "401" in str(e) or "invalid x-api-key" in str(e).lower() or "invalid api key" in str(e).lower():
            is_auth_error = True

        if is_auth_error:
            alert_subj = "ALERT: Thai2Drive Anthropic API Key Invalid"
            alert_body = f"The system detected an invalid or expired Anthropic API Key on {datetime.now(timezone.utc).isoformat()}.\n\nError details: {e}\n\nPlease update ANTHROPIC_API_KEY in your Railway environment variables immediately."
            try:
                import asyncio
                asyncio.create_task(asyncio.to_thread(send_admin_alert_email, alert_subj, alert_body))
            except Exception as mail_err:
                logger.error("Failed to spawn alert email thread: %s", mail_err)

        error_str = f"LiteLLM: {type(e).__name__}({e})"
        reply_text = _fallback_reply(lang)

    # Persist both messages
    now = datetime.now(timezone.utc)
    await _chat_col.insert_many([
        {
            "session_id": session_id,
            "role": "user",
            "content": user_msg,
            "language": lang,
            "ts": now,
        },
        {
            "session_id": session_id,
            "role": "assistant",
            "content": reply_text,
            "language": lang,
            "ts": now,
        },
    ])

    duration = time.time() - start_time
    try:
        log_doc = {
            "session_id": session_id,
            "language": lang,
            "is_quiz_help": is_quiz_help,
            "is_weak_topics": is_weak_topics,
            "question": user_msg,
            "response_time": duration,
            "error": error_str,
            "ts": datetime.now(timezone.utc)
        }
        await _db["teacher_chat_logs"].insert_one(log_doc)
        logger.info("Teacher chat logged: lang=%s is_quiz_help=%s is_weak_topics=%s response_time=%.2fs error=%s", 
                    lang, is_quiz_help, is_weak_topics, duration, error_str)
    except Exception as log_ex:
        logger.error("Failed to write teacher log to DB: %s", log_ex)

    suggestions = _get_suggestions(reply_text, lang)
    return TeacherChatResponse(session_id=session_id, reply=reply_text, suggestions=suggestions)


def _fallback_reply(lang: str) -> str:
    if lang == "th":
        return "ขอโทษค่ะ ระบบไม่พร้อมใช้งานในขณะนี้ กรุณาลองใหม่อีกครั้งในภายหลังค่ะ"
    if lang == "en":
        return "Sorry, I'm not available right now. Please try again in a moment."
    return "Beklager, jeg er ikke tilgjengelig akkurat nå. Prøv igjen om litt."


# ─── Feedback ─────────────────────────────────────────────────────────────────

_feedback_col = _db["teacher_feedback"]


class FeedbackRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default="no")
    user_message: Optional[str] = Field(default=None, max_length=2000)
    assistant_answer: Optional[str] = Field(default=None, max_length=5000)
    helpful: bool
    reason: Optional[str] = Field(default=None, max_length=200)
    source: Optional[str] = Field(default="web")


@teacher_router.post("/teacher/feedback")
async def teacher_feedback(req: FeedbackRequest):
    await _feedback_col.insert_one({
        "session_id": req.session_id,
        "language": req.language or "no",
        "user_message": req.user_message,
        "assistant_answer": req.assistant_answer,
        "helpful": req.helpful,
        "reason": req.reason,
        "source": req.source or "web",
        "ts": datetime.now(timezone.utc),
    })
    return {"ok": True}
