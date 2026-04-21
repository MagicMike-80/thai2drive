"""Propose questions for 4 new images (yield sign, end of 60, police, 3-car RoW)."""
import asyncio, json, os, sys
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(Path(__file__).parent))
from _img_utils import image_to_base64  # noqa
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent  # noqa

KEY = os.getenv("EMERGENT_LLM_KEY") or "sk-emergent-b48A3D57008C8350c6"

SYSTEM = """You are a Norwegian driving theory (førerkort klasse B) expert.

Create ONE quiz question that matches STRICTLY what is visible in the image.
- Exactly 4 options (A, B, C, D), ONE clearly correct.
- NO/EN/TH translations for everything.
- Category from: Traffic Signs, Traffic Rules, Right of Way, Safety, Parking, Road Conditions.
- Difficulty: easy, medium, hard.

Return ONLY strict JSON (no markdown):
{
  "image_identification": "kort norsk beskrivelse",
  "question": {"no": "...", "en": "...", "th": "..."},
  "options": [
    {"id": "A", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "B", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "C", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "D", "text": {"no": "...", "en": "...", "th": "..."}}
  ],
  "correctOptionId": "A|B|C|D",
  "explanation": {"no": "...", "en": "...", "th": "..."},
  "category": "...",
  "difficulty": "..."
}
"""

IMAGES = [
    {"slot": "#1", "path": "/tmp/batch3/img1_yield.jpg",
     "hint": "Vikepliktsskilt 202 (rødkantet trekant som peker nedover, hvit midt). Question about what the sign means and what you must do."},
    {"slot": "#2", "path": "/tmp/batch3/img2_end60.jpg",
     "hint": "Landevei med gul midtlinje og skilt 364 'Slutt på fartsgrense 60' (hvit skilt med 60 og diagonale streker). Question about what this sign means and what speed limit applies AFTER it (landevei utenfor tettbygd strøk = 80 km/t som hovedregel)."},
    {"slot": "#3", "path": "/tmp/batch3/img3_police.jpg",
     "hint": "Kryss med grønt trafikklys, men en trafikkbetjent (i gul vest) står midt i krysset og styrer trafikken med utstrakte armer. En rød bil nærmer seg. Question about who/what to follow when a police officer directs traffic while lights are green (svar: politi/trafikkbetjent overstyrer trafikklys)."},
    {"slot": "#4", "path": "/tmp/batch3/img4_abc.jpg",
     "hint": "Et T-kryss med 3 kjøretøy markert A (rød bil nederst, vil svinge høyre), B (blå bil til høyre, vil svinge venstre), og C (motorsykkel ovenfra, kjører rett fram). Alle veier ser like ut (uskiltet T-kryss). Question about right-of-way order. In Norwegian unsigned T-crossroad: A has C on right (vikeplikt for C), B has A on right (vikeplikt for A). So order: C goes first, then A, then B."},
]

async def propose(path, hint):
    b64 = image_to_base64(path, max_dim=600, quality=82).split(",", 1)[1]
    chat = LlmChat(api_key=KEY, session_id=f"p3-{Path(path).stem}", system_message=SYSTEM).with_model("gemini", "gemini-2.5-pro")
    msg = UserMessage(text=f"Create a quiz question.\nHint: {hint}", file_contents=[ImageContent(image_base64=b64)])
    raw = str(await chat.send_message(msg)).strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"): raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]
    s, e = raw.find("{"), raw.rfind("}")
    return json.loads(raw[s:e+1])

async def main():
    out = []
    for spec in IMAGES:
        print(f"{spec['slot']} ...", flush=True)
        try:
            q = await propose(spec["path"], spec["hint"])
            print(f"  -> {q.get('category')} / {q.get('difficulty')} / correct={q.get('correctOptionId')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            q = {"error": str(e)}
        out.append({"slot": spec["slot"], "path": spec["path"], "proposal": q})
    Path(__file__).parent.joinpath("proposed_batch3.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print("Saved")

asyncio.run(main())
