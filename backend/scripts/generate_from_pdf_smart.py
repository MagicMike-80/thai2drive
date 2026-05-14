"""
Thai2Drive - Smart PDF-generator
Leser PDF, hopper over tomme sider, genererer spørsmål fra meningsfullt innhold.
Bruk: python generate_from_pdf_smart.py <pdf-fil> [sporsmal_per_bolk]
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv(override=True)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break

client = anthropic.Anthropic(api_key=api_key)
LETTERS = ["A", "B", "C", "D"]

# Ord som indikerer navigasjonsside uten innhold
NAV_WORDS = {"meny", "trinn", "tilbake", "bytt bilde", "oppgaver", "neste"}


def extract_pdf_text(pdf_path: str) -> list[tuple[int, str]]:
    """Ekstraher tekst fra PDF, returner liste av (sidenr, tekst)"""
    try:
        import fitz
    except ImportError:
        os.system(f"{sys.executable} -m pip install pymupdf -q")
        import fitz

    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        pages.append((i + 1, text))
    doc.close()
    return pages


def is_useful_page(text: str, min_words: int = 30) -> bool:
    """Sjekk om siden har nok innhold"""
    words = text.lower().split()
    if len(words) < min_words:
        return False
    # Sjekk at det ikke er bare navigasjonsord
    real_words = [w for w in words if w not in NAV_WORDS and len(w) > 2]
    return len(real_words) >= min_words // 2


def make_batches(pages: list[tuple[int, str]], batch_size: int = 2000) -> list[tuple[str, list[int]]]:
    """Grupper sider i bolker basert på tegn-grense"""
    batches = []
    current_text = ""
    current_pages = []

    for page_num, text in pages:
        if not is_useful_page(text):
            continue
        if len(current_text) + len(text) > batch_size and current_text:
            batches.append((current_text, current_pages))
            current_text = text
            current_pages = [page_num]
        else:
            current_text += "\n\n" + text
            current_pages.append(page_num)

    if current_text:
        batches.append((current_text, current_pages))

    return batches


def generate_questions_from_text(text: str, pages: list[int], count: int) -> list:
    """Send tekst til Claude og få spørsmål"""

    prompt = f"""Du er ekspert på norsk trafikklære og vegtrafikkloven.

Her er innhold fra den offisielle norske trafikklæreplanen (side {pages[0]}-{pages[-1]}):

---
{text[:3000]}
---

Lag nøyaktig {count} gode teoriprøve-spørsmål basert på dette innholdet.

Krav:
- Spørsmålene MÅ baseres på innholdet ovenfor
- Hvert spørsmål har 4 alternativer (A, B, C, D), kun ETT riktig svar
- riktigSvar MÅ variere — bruk en blanding av A, B, C og D
- Alle tekster på tre språk: norsk (no), thai (th), engelsk (en)
- Varier vanskelighetsgrad (easy/medium/hard)
- IKKE lag spørsmål om navigasjonsmenyer eller skjermbilder

Svar KUN med gyldig JSON-array:

[
  {{
    "sporsmal": {{"no": "...", "th": "...", "en": "..."}},
    "alternativer": [
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}}
    ],
    "riktigSvar": "B",
    "vanskelighetsgrad": "medium",
    "kategori": "Traffic Rules",
    "forklaring": {{"no": "...", "th": "...", "en": "..."}}
  }}
]"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )

    text_out = response.content[0].text.strip()
    if "```" in text_out:
        text_out = text_out.split("```")[1]
        if text_out.startswith("json"):
            text_out = text_out[4:]
        text_out = text_out.rsplit("```", 1)[0]

    result = json.loads(text_out.strip())
    # Filter out any questions without proper structure
    return [q for q in result if "sporsmal" in q and "alternativer" in q and len(q["alternativer"]) == 4]


async def save_to_database(questions: list, source: str) -> tuple[int, int]:
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")

    if not mongo_url:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        with open(env_path) as f:
            for line in f:
                if line.startswith("MONGO_URL="):
                    mongo_url = line.strip().split("=", 1)[1].strip('"')
                if line.startswith("DB_NAME="):
                    db_name = line.strip().split("=", 1)[1].strip('"')

    mongo_client = AsyncIOMotorClient(mongo_url)
    db = mongo_client[db_name]

    inserted = 0
    skipped = 0

    for q in questions:
        existing = await db.questions.find_one({"question.no": q["sporsmal"]["no"]})
        if existing:
            skipped += 1
            continue

        doc = {
            "id": str(uuid.uuid4()),
            "question": q["sporsmal"],
            "options": [
                {"id": LETTERS[i], "text": q["alternativer"][i]["text"]}
                for i in range(4)
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": q["forklaring"],
            "bildeUrl": None,
            "category": q.get("kategori", "Traffic Rules"),
            "difficulty": q.get("vanskelighetsgrad", "medium"),
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": f"pdf_smart:{Path(source).name}"
        }

        await db.questions.insert_one(doc)
        inserted += 1

    total = await db.questions.count_documents({})
    mongo_client.close()
    return inserted, skipped


async def main():
    if len(sys.argv) < 2:
        print("\nBruk: python generate_from_pdf_smart.py <pdf-fil> [sporsmal_per_bolk]")
        print("Eks:  python generate_from_pdf_smart.py trafikkloven.pdf 5")
        return

    pdf_path = sys.argv[1]
    q_per_batch = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    if not os.path.exists(pdf_path):
        print(f"Finner ikke filen: {pdf_path}")
        return

    print(f"\n{'='*60}")
    print(f"  Thai2Drive - Smart PDF-generator")
    print(f"{'='*60}")
    print(f"  Fil: {Path(pdf_path).name}")
    print(f"  Sporsmal per bolk: {q_per_batch}")

    # Extract text
    print(f"\n  Leser PDF...")
    pages = extract_pdf_text(pdf_path)
    print(f"  Totalt sider: {len(pages)}")

    # Make batches
    batches = make_batches(pages)
    useful = sum(1 for _, t in pages if is_useful_page(t))
    print(f"  Nyttige sider: {useful}")
    print(f"  Bolker med innhold: {len(batches)}")
    print(f"  Estimert antall sporsmal: {len(batches) * q_per_batch}")
    print(f"{'='*60}\n")

    all_questions = []
    total_inserted = 0
    total_skipped = 0

    for i, (text, page_nums) in enumerate(batches):
        print(f"  Bolk {i+1}/{len(batches)} (side {page_nums[0]}-{page_nums[-1]})...")
        try:
            questions = generate_questions_from_text(text, page_nums, q_per_batch)
            all_questions.extend(questions)

            # Save each batch to DB immediately
            ins, skip = await save_to_database(questions, pdf_path)
            total_inserted += ins
            total_skipped += skip
            print(f"    {len(questions)} generert | {ins} lagret | {skip} duplikater")

        except Exception as e:
            print(f"    Feil: {e}")
            continue

    # Save full JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(os.path.dirname(__file__), f"from_pdf_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  FERDIG!")
    print(f"  Totalt generert: {len(all_questions)}")
    print(f"  Lagret i DB:     {total_inserted}")
    print(f"  Duplikater:      {total_skipped}")
    print(f"  JSON-fil:        {Path(json_file).name}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
