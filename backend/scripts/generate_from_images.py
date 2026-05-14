"""
generate_from_images.py
=======================
Leser bilder fra Trafikkbildet-mappen, analyserer med Claude AI,
genererer trafikkspørsmål på norsk/thai/engelsk, lagrer i MongoDB.

Kjør: python scripts/generate_from_images.py
"""

import asyncio
import base64
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

import anthropic
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv, dotenv_values
from PIL import Image
import io

# ── Setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / '.env')
_env = dotenv_values(ROOT / '.env')
os.environ.update({k: v for k, v in _env.items() if v})

IMAGES_DIR = Path(r"C:\Users\Stein Hoang\CrossDevice\Michael sin Z Flip5\storage\DCIM\Trafikkbildet")
SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp'}

MONGO_URL = os.environ['MONGO_URL']
DB_NAME   = os.environ['DB_NAME']
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')

if not ANTHROPIC_KEY:
    print("FEIL: Mangler ANTHROPIC_API_KEY i .env")
    sys.exit(1)

client_ai = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
mongo     = AsyncIOMotorClient(MONGO_URL)
db        = mongo[DB_NAME]

CATEGORIES = [
    "Traffic Signs", "Road Rules", "Right of Way", "Speed Limits",
    "Safety", "Driving Conditions", "Situations",
    "Pedestrians and Cyclists", "Vehicle Knowledge", "Environment and Economy"
]

# ── Bildebehandling ────────────────────────────────────────────────────
def prepare_image(path: Path, max_px=900, quality=82, max_kb=400) -> tuple[str, str]:
    """Resize og konverter bilde til base64 JPEG. Returnerer (base64_str, media_type)."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if max(w, h) > max_px:
        scale = max_px / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    while buf.tell() > max_kb * 1024 and quality > 40:
        quality -= 8
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)

    b64 = base64.b64encode(buf.getvalue()).decode()
    return b64, "image/jpeg"


# ── AI-generering ──────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Du er ekspert på norsk trafikkopplæring og norsk trafikk­lov (lovdata.no).

Analyser dette trafikkbildet og lag {count} FORSKJELLIGE teoriprøvespørsmål basert på samme bilde.
Spørsmålene skal handle om ULIKE aspekter ved bildet (f.eks. spørsmål 1 om skiltet, spørsmål 2 om handlingen).

Returner KUN gyldig JSON-array (ingen annen tekst):
[
  {{
    "category": "<Traffic Signs | Road Rules | Right of Way | Speed Limits | Safety | Driving Conditions | Situations | Pedestrians and Cyclists | Vehicle Knowledge | Environment and Economy>",
    "difficulty": "<easy | medium | hard>",
    "question": {{"no": "...", "th": "...", "en": "..."}},
    "options": [
      {{"id": "A", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "B", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "C", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "D", "text": {{"no": "...", "th": "...", "en": "..."}}}}
    ],
    "correctOptionId": "A",
    "explanation": {{"no": "...", "th": "...", "en": "..."}},
    "law_reference": "Eks: Trafikkreglene § 7"
  }},
  {{ ... spørsmål 2 med annen vinkel ... }}
]

Regler:
- Hvert spørsmål skal ha ULIK problemstilling (ikke bare bytt om ordene)
- Riktig svar skal stemme med norsk lovdata.no / Statens vegvesen
- 4 svaralternativer, kun 1 riktig per spørsmål
- Thai-tekst skal være korrekt trafikkfaglig thai"""


def clean_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


async def generate_questions(img_path: Path, count: int = 2) -> list[dict]:
    b64, media_type = prepare_image(img_path)
    prompt = PROMPT_TEMPLATE.format(count=count)

    try:
        resp = client_ai.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        text = clean_json(resp.content[0].text)
        items = json.loads(text)
        if not isinstance(items, list):
            items = [items]

        results = []
        for data in items[:count]:
            data["bildeUrl"] = f"data:{media_type};base64,{b64}"
            data["id"] = str(uuid.uuid4())
            data["schema_version"] = 2
            data["active"] = True
            data["created_at"] = datetime.now(timezone.utc).isoformat()
            data["source"] = "image_agent"
            data["source_file"] = img_path.name
            results.append(data)
        return results

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"  Parse-feil ({img_path.name}): {e}")
        return []
    except Exception as e:
        print(f"  AI-feil ({img_path.name}): {e}")
        return []


async def is_duplicate(q: dict) -> bool:
    """Sjekk om spørsmål med samme tekst allerede finnes."""
    existing = await db.questions.find_one({"question.no": q["question"]["no"]})
    return existing is not None


# ── Hovedlogikk ────────────────────────────────────────────────────────
async def main():
    images = [p for p in sorted(IMAGES_DIR.iterdir()) if p.suffix.lower() in SUPPORTED]
    print(f"Fant {len(images)} bilder i {IMAGES_DIR.name}")

    already_done = set()
    # Finn bilder som allerede er lastet opp (etter source_file)
    async for q in db.questions.find({"source": "image_agent"}, {"source_file": 1}):
        already_done.add(q.get("source_file", ""))

    todo = [p for p in images if p.name not in already_done]
    print(f"Allerede behandlet: {len(already_done)} | Gjenstaar: {len(todo)}")

    if not todo:
        print("Alle bilder er allerede behandlet!")
        return

    saved = 0
    skipped = 0
    errors = 0

    for i, img_path in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {img_path.name} ...", flush=True)

        questions = await generate_questions(img_path, count=2)
        if not questions:
            print(f"  FEIL — ingen spørsmål generert")
            errors += 1
            continue

        for q in questions:
            if await is_duplicate(q):
                print(f"  DUPLIKAT hoppet over: {q['question']['no'][:50]}")
                skipped += 1
                continue
            await db.questions.insert_one(q)
            print(f"  OK [{q['difficulty']}] {q['question']['no'][:60]}")
            saved += 1

        # Pause mellom bilder
        await asyncio.sleep(1.5)

    print(f"\n=== FERDIG ===")
    print(f"Lagret:   {saved}")
    print(f"Duplikat: {skipped}")
    print(f"Feil:     {errors}")
    total = await db.questions.count_documents({})
    print(f"Totalt i DB: {total} spørsmål")


if __name__ == "__main__":
    asyncio.run(main())
