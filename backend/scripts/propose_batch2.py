"""Propose Norwegian driving theory questions for 5 new images."""
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

Given an image, create ONE quiz question that matches STRICTLY what is visible.
- Exactly 4 options (A, B, C, D), one unambiguously correct.
- Provide Norwegian (no), English (en), Thai (th) translations for everything.
- Choose an appropriate category from: Traffic Signs, Traffic Rules, Right of Way, Safety, Parking, Road Conditions.
- Choose difficulty: easy, medium, or hard.

Return ONLY strict JSON (no markdown):
{
  "image_identification": "short Norwegian description",
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
    {"slot": "#4", "path": "/tmp/batch2/img4_engine.jpg",
     "hint": "Motorrom med VW/Skoda-motor og et ikon over ekspansjonstanken som viser termometer+vann = kjølevæskenivå/kjølevæsketemperatur. Question should be about engine coolant/temperature."},
    {"slot": "#5", "path": "/tmp/batch2/img5_bus.jpg",
     "hint": "Grønn norsk buss ved busstopp i bygate, bussen har vikepliktsskilt (trekant rødhvit) synlig. Question about passing/yielding to buses leaving bus stops in urban areas (norsk regel: §40 gi forrang til buss som starter fra holdeplass i tettbygd strøk)."},
    {"slot": "#6", "path": "/tmp/batch2/img6_priority.jpg",
     "hint": "Gult rombeskilt 206 Forkjørsvei med underskilt som viser sidevei fra høyre. Question should ask what the combination means — you are on a priority road but a side road joins from the right."},
    {"slot": "#7", "path": "/tmp/batch2/img7_intersection.jpg",
     "hint": "En tegnet kryssituasjon med en rød bil som svinger mot høyre, flere felt, fotgjengerovergang, vikepliktsskilt og 'svinge høyre påbudt' blått skilt. Question about positioning / what to check when turning right at a complex intersection."},
    {"slot": "#8", "path": "/tmp/batch2/img8_exhaust.jpg",
     "hint": "Eksosrør som slipper ut eksosrøyk fra bil. Question about environmental impact — CO2, drivstoffbruk, miljø, eco-driving (miljøvennlig kjøring)."},
]

async def propose(path, hint):
    b64 = image_to_base64(path, max_dim=600, quality=82).split(",", 1)[1]
    chat = LlmChat(api_key=KEY, session_id=f"p-{Path(path).stem}", system_message=SYSTEM).with_model("gemini", "gemini-2.5-pro")
    msg = UserMessage(text=f"Create a quiz question for this image.\nHint: {hint}", file_contents=[ImageContent(image_base64=b64)])
    raw = str(await chat.send_message(msg)).strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]
    s, e = raw.find("{"), raw.rfind("}")
    return json.loads(raw[s:e+1])

async def main():
    proposals = []
    for spec in IMAGES:
        print(f"Processing {spec['slot']} ...", flush=True)
        try:
            q = await propose(spec["path"], spec["hint"])
            print(f"  -> {q.get('category')}, correct={q.get('correctOptionId')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            q = {"error": str(e)}
        proposals.append({"slot": spec["slot"], "path": spec["path"], "proposal": q})
    Path(__file__).parent.joinpath("proposed_batch2.json").write_text(json.dumps(proposals, ensure_ascii=False, indent=2))
    print("Saved proposed_batch2.json")

asyncio.run(main())
