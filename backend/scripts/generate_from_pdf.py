"""
generate_from_pdf.py
====================
Leser sider fra PDF-filer, analyserer med Claude AI,
genererer trafikkspørsmål på norsk/thai/engelsk, lagrer i MongoDB.

Kjør: python scripts/generate_from_pdf.py
"""

import asyncio
import base64
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO

import anthropic
import fitz  # PyMuPDF
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from PIL import Image

# ── Setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / '.env')

PDF_FILES = [
    (r"C:\Users\Stein Hoang\CrossDevice\Michael sin Z Flip5\storage\Oslo team\Trafikalt Grunnkurs 2015.pdf", "Safety"),
    (r"C:\Users\Stein Hoang\CrossDevice\Michael sin Z Flip5\storage\Download\Sikkerhetskurs på vei 2024.pdf", "Road Rules"),
]

MONGO_URL     = os.environ['MONGO_URL']
DB_NAME       = os.environ['DB_NAME']
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not ANTHROPIC_KEY:
    print("FEIL: Mangler ANTHROPIC_API_KEY i .env")
    sys.exit(1)

client_ai = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
mongo     = AsyncIOMotorClient(MONGO_URL)
db        = mongo[DB_NAME]

# ── PDF-behandling ─────────────────────────────────────────────────────
def get_page_text(page) -> str:
    return page.get_text().strip()


def get_page_image(page, max_px=900, quality=82) -> tuple[str, str] | None:
    """Render PDF-side som bilde. Returnerer (base64, media_type) eller None."""
    try:
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for bedre kvalitet
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        w, h = img.size
        if max(w, h) > max_px:
            scale = max_px / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return b64, "image/jpeg"
    except Exception:
        return None


# ── AI prompt ──────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """Du er ekspert på norsk trafikkopplæring og norsk trafikk­lov (lovdata.no).

Denne siden er fra et norsk trafikkopplærings­dokument. Her er innholdet:
--- SIDE-TEKST ---
{text}
---

Lag {count} FORSKJELLIGE teoriprøvespørsmål basert på denne siden.
Spørsmålene skal teste forståelse, ikke bare hukommelse.

Returner KUN gyldig JSON-array:
[
  {{
    "category": "<Traffic Signs | Road Rules | Right of Way | Speed Limits | Safety | Driving Conditions | Situations | Pedestrians and Cyclists | Vehicle Knowledge | Environment and Economy>",
    "difficulty": "<easy | medium | hard>",
    "question": {{"no": "...", "th": "คำถามภาษาไทย", "en": "..."}},
    "options": [
      {{"id": "A", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "B", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "C", "text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"id": "D", "text": {{"no": "...", "th": "...", "en": "..."}}}}
    ],
    "correctOptionId": "A",
    "explanation": {{"no": "Forklaring med lovhenvisning", "th": "คำอธิบายภาษาไทย", "en": "Explanation with law reference"}},
    "law_reference": "Eks: Vegtrafikkloven § 3"
  }}
]

Regler:
- Kun basert på innholdet på siden
- Riktig svar iht. norsk lov / Statens vegvesen / lovdata.no
- Hvert spørsmål skal ha ULIK vinkel
- Hvis side-teksten er for kort eller ikke egner seg → returner tom array []"""


def clean_json(text: str):
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


async def generate_from_page(page_text: str, page_img: tuple | None,
                              default_category: str, source: str,
                              page_num: int, count: int = 2) -> list[dict]:
    if len(page_text.strip()) < 20:
        return []

    prompt = PROMPT_TEMPLATE.format(text=page_text, count=count)

    content = []
    if page_img:
        b64, media_type = page_img
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
    content.append({"type": "text", "text": prompt})

    try:
        resp = client_ai.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            messages=[{"role": "user", "content": content}]
        )
        text = clean_json(resp.content[0].text)
        items = json.loads(text)
        if not isinstance(items, list):
            return []

        results = []
        for data in items[:count]:
            if not data.get("question", {}).get("no"):
                continue
            if page_img:
                b64, media_type = page_img
                data["bildeUrl"] = f"data:{media_type};base64,{b64}"
            data["id"] = str(uuid.uuid4())
            data["schema_version"] = 2
            data["active"] = True
            data["created_at"] = datetime.now(timezone.utc).isoformat()
            data["source"] = "pdf_agent"
            data["source_file"] = source
            data["source_page"] = page_num
            results.append(data)
        return results

    except (json.JSONDecodeError, KeyError) as e:
        print(f"    Parse-feil: {e}")
        return []
    except Exception as e:
        print(f"    AI-feil: {e}")
        return []


async def is_duplicate(q: dict) -> bool:
    existing = await db.questions.find_one({"question.no": q["question"]["no"]})
    return existing is not None


# ── Hovedlogikk ────────────────────────────────────────────────────────
async def main():
    total_saved = 0
    total_skipped = 0
    total_errors = 0

    for pdf_path, default_cat in PDF_FILES:
        path = Path(pdf_path)
        if not path.exists():
            print(f"IKKE FUNNET: {pdf_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Fil: {path.name}")

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            print(f"  Kunne ikke lese: {e}")
            continue

        print(f"Sider: {doc.page_count}")

        # Sjekk hvilke sider allerede er behandlet
        done = set()
        async for q in db.questions.find(
            {"source": "pdf_agent", "source_file": path.name},
            {"source_page": 1}
        ):
            done.add(q.get("source_page"))

        todo_pages = [(i+1, doc[i]) for i in range(doc.page_count) if (i+1) not in done]
        print(f"Allerede behandlet: {len(done)} | Gjenstaar: {len(todo_pages)}")

        for page_num, page in todo_pages:
            text = get_page_text(page)
            img  = get_page_image(page)

            preview = text[:50].replace('\n', ' ') if text else "(ingen tekst)"
            print(f"  [{page_num}/{doc.page_count}] {preview} ...", flush=True)

            if len(text.strip()) < 20:
                print(f"    HOPPET OVER (for kort tekst)")
                continue

            questions = await generate_from_page(
                text, img, default_cat, path.name, page_num, count=2
            )

            if not questions:
                print(f"    INGEN spørsmål generert")
                total_errors += 1
                continue

            for q in questions:
                if await is_duplicate(q):
                    print(f"    DUPLIKAT: {q['question']['no'][:50]}")
                    total_skipped += 1
                    continue
                await db.questions.insert_one(q)
                print(f"    OK [{q.get('difficulty','?')}] {q['question']['no'][:55]}")
                total_saved += 1

            await asyncio.sleep(1.5)

        doc.close()

    total_db = await db.questions.count_documents({})
    print(f"\n{'='*60}")
    print(f"FERDIG!")
    print(f"Lagret:   {total_saved}")
    print(f"Duplikat: {total_skipped}")
    print(f"Feil:     {total_errors}")
    print(f"Totalt i DB: {total_db} sporsmal")


if __name__ == "__main__":
    asyncio.run(main())
