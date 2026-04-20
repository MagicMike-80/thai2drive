"""
Use Gemini 2.5 Pro Vision to propose quiz questions for uploaded images.
Does NOT write to DB. Outputs JSON to scripts/proposed_questions.json for review.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(Path(__file__).parent))
from _img_utils import image_to_base64  # noqa: E402

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent  # noqa: E402

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY") or "sk-emergent-b48A3D57008C8350c6"

SYSTEM = """You are a Norwegian driving theory (førerkort klasse B) expert.

You will be given an image from the Norwegian road. Look carefully at what is ACTUALLY visible
in the image, then create ONE quiz question that:
- Matches STRICTLY what is visible in the image (no invented elements).
- Is relevant to the Norwegian driving theory test.
- Has exactly 4 answer options (A, B, C, D) where only ONE is unambiguously correct.
- The wrong options should be plausible distractors, not obviously wrong.
- The question and options must be short and clear.
- Provide translations in Norwegian (no), English (en), and Thai (th).

Return ONLY a strict JSON object (no markdown) with this schema:
{
  "image_identification": "short Norwegian description of what the image shows (e.g. 'Fareskilt 114 Glatt kjørebane')",
  "question": {"no": "...", "en": "...", "th": "..."},
  "options": [
    {"id": "A", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "B", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "C", "text": {"no": "...", "en": "...", "th": "..."}},
    {"id": "D", "text": {"no": "...", "en": "...", "th": "..."}}
  ],
  "correctOptionId": "A|B|C|D",
  "explanation": {"no": "...", "en": "...", "th": "..."},
  "category": "Traffic Signs|Traffic Rules|Right of Way|Safety|Parking|Road Conditions",
  "difficulty": "easy|medium|hard"
}
"""


async def propose(path: str, hint: str = "") -> dict:
    b64 = image_to_base64(path, max_dim=600, quality=82).split(",", 1)[1]
    chat = (
        LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"propose-{Path(path).stem}",
            system_message=SYSTEM,
        )
        .with_model("gemini", "gemini-2.5-pro")
    )
    user_text = "Please propose a Norwegian driving theory quiz question for this image."
    if hint:
        user_text += f"\n\nHint about the scene: {hint}"
    msg = UserMessage(text=user_text, file_contents=[ImageContent(image_base64=b64)])
    raw = await chat.send_message(msg)
    text = raw if isinstance(raw, str) else str(raw)
    # strip ```json ... ```
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    start = text.find("{")
    end = text.rfind("}")
    return json.loads(text[start : end + 1])


IMAGES = [
    {
        "slot": "#2",
        "label": "Tunnel SOS nødstasjon",
        "path": "/tmp/signs/tunnel_sos.jpg",
        "hint": "Inne i en norsk biltunnel med et blått informasjonsskilt som viser SOS-telefon og brannslukker (nødstasjon i tunnel).",
    },
    {
        "slot": "#3",
        "label": "Rødt+gult trafikklys (ALTERNATIV)",
        "path": "/tmp/signs/light_redyellow.jpg",
        "hint": (
            "Bygate med trafikklys som viser rødt og gult samtidig. Propose a DIFFERENT question "
            "than 'what do you do if you go straight' — focus instead on the MEANING of the red+yellow "
            "light signal itself."
        ),
    },
    {
        "slot": "#4",
        "label": "Fareskilt Glatt kjørebane (114)",
        "path": "/tmp/signs/slippery.jpg",
        "hint": "Rødkantet trekantet fareskilt med bil og sklimerker (skilt 114 Glatt kjørebane).",
    },
    {
        "slot": "#5",
        "label": "Smal landevei med trær",
        "path": "/tmp/signs/country_road.jpg",
        "hint": "En smal norsk landevei med trær på begge sider, stiplet midtlinje, solrik dag. Ingen skilt synlige. Propose a question about driving behaviour on such a rural road (e.g. speed limit outside built-up area, overtaking, visibility).",
    },
]


async def main():
    proposals = []
    for spec in IMAGES:
        print(f"Generating for {spec['slot']} — {spec['label']} ...", flush=True)
        try:
            q = await propose(spec["path"], spec["hint"])
        except Exception as e:
            print(f"  ERROR: {e}")
            q = {"error": str(e)}
        proposals.append({"slot": spec["slot"], "label": spec["label"], "proposal": q})
        print(f"  -> OK ({q.get('category', '?')} / {q.get('difficulty', '?')})")

    out = Path(__file__).parent / "proposed_questions.json"
    out.write_text(json.dumps(proposals, ensure_ascii=False, indent=2))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    asyncio.run(main())
