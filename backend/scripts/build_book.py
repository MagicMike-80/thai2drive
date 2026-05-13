"""
Thai2Drive - Bygg læringsbok fra PDF
Skriver om tekst med egne ord, oversetter til thai+engelsk, lagrer i DB.
Bruk: python build_book.py [start_side] [slutt_side]
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

PDF_PATH = r"C:\Users\Stein Hoang\Desktop\My Agents\PDF.4t.pdf"
NAV_WORDS = {'meny', 'tilbake', 'bytt bilde', 'neste', 'oppgaver', 'skjul', 'vis'}

# Kapittelstruktur basert på PDF-innhold
CHAPTERS = [
    {"num": 1, "title": "Grunnleggende trafikklære",     "pages": (1, 115)},
    {"num": 2, "title": "Mennesket i trafikken",          "pages": (116, 220)},
    {"num": 3, "title": "Trafikksystemet og regler",      "pages": (221, 340)},
    {"num": 4, "title": "Kjøretøy og teknisk kunnskap",  "pages": (341, 437)},
]


def extract_pages(pdf_path: str, start: int, end: int) -> list[tuple[int, str]]:
    try:
        import fitz
    except ImportError:
        os.system(f"{sys.executable} -m pip install pymupdf -q")
        import fitz

    doc = fitz.open(pdf_path)
    result = []
    for i in range(start - 1, min(end, len(doc))):
        text = doc[i].get_text().strip()
        lines = [l.strip() for l in text.splitlines()
                 if l.strip() and l.strip().lower() not in NAV_WORDS
                 and not l.strip().isdigit()]
        clean = ' '.join(lines)
        if len(clean.split()) >= 20:
            result.append((i + 1, clean))
    doc.close()
    return result


def make_sections(pages: list[tuple[int, str]], max_chars: int = 2500) -> list[tuple[list[int], str]]:
    """Grupper sider i seksjoner av passelig størrelse"""
    sections = []
    cur_pages = []
    cur_text = ""

    for page_num, text in pages:
        if len(cur_text) + len(text) > max_chars and cur_text:
            sections.append((cur_pages, cur_text.strip()))
            cur_pages = [page_num]
            cur_text = text
        else:
            cur_pages.append(page_num)
            cur_text += "\n" + text

    if cur_text.strip():
        sections.append((cur_pages, cur_text.strip()))

    return sections


def rewrite_and_translate(raw_text: str, chapter_title: str) -> dict | None:
    """Skriv om tekst med egne ord og oversett"""

    prompt = f"""Du jobber med en læringsbok om norsk trafikklære for kapitlet: "{chapter_title}".

Her er råtekst fra pensumet:
---
{raw_text[:2500]}
---

Gjør følgende:
1. Skriv innholdet om med dine EGNE ORD på naturlig, enkel norsk. Behold alle fakta korrekte, men lag nye setninger. IKKE kopier setninger fra originalen.
2. Lag en kort tittel for dette avsnittet (maks 6 ord, norsk)
3. Oversett tittelen og innholdet til thai og engelsk

Svar KUN med JSON:
{{
  "tittel": {{
    "no": "Kort tittel på norsk",
    "th": "หัวข้อภาษาไทย",
    "en": "Short English title"
  }},
  "innhold": {{
    "no": "Omskrevet tekst på norsk. Skriv i avsnitt, 3-6 setninger. Enkelt og klart språk.",
    "th": "เนื้อหาภาษาไทย",
    "en": "English content"
  }}
}}"""

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())
    except Exception as e:
        print(f"    Feil: {e}")
        return None


async def save_section(db, chapter_num: int, chapter_title: str,
                       section_num: int, pages: list[int], data: dict) -> bool:
    doc = {
        "id": str(uuid.uuid4()),
        "chapter_num": chapter_num,
        "chapter_title": {
            "no": chapter_title,
            "th": chapter_title,
            "en": chapter_title
        },
        "section_num": section_num,
        "section_title": data["tittel"],
        "content": data["innhold"],
        "pages": pages,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.chapters.insert_one(doc)
    return True


async def main():
    # Args: optional start/stop chapter
    start_ch = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_ch = int(sys.argv[2]) if len(sys.argv) > 2 else 4

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

    # Create index for fast lookup
    await db.chapters.create_index([("chapter_num", 1), ("section_num", 1)])

    print(f"\n{'='*60}")
    print(f"  Thai2Drive - Bygger laeringsbok")
    print(f"{'='*60}")

    total_sections = 0

    for ch in CHAPTERS:
        if not (start_ch <= ch["num"] <= end_ch):
            continue

        print(f"\n  Kapittel {ch['num']}: {ch['title']}")
        print(f"  Side {ch['pages'][0]}-{ch['pages'][1]}")

        # Check if already done
        existing = await db.chapters.count_documents({"chapter_num": ch["num"]})
        if existing > 0:
            print(f"  Allerede ferdig ({existing} seksjoner) - hopper over")
            continue

        pages = extract_pages(PDF_PATH, ch["pages"][0], ch["pages"][1])
        sections = make_sections(pages)
        print(f"  {len(sections)} seksjoner funnet")

        for s_num, (page_nums, raw_text) in enumerate(sections, 1):
            print(f"  [{s_num}/{len(sections)}] side {page_nums[0]}...", end=" ", flush=True)
            result = rewrite_and_translate(raw_text, ch["title"])
            if result:
                await save_section(db, ch["num"], ch["title"], s_num, page_nums, result)
                print(f"OK: {result['tittel']['no'][:45]}")
                total_sections += 1
            else:
                print("Hoppet over")

    total = await db.chapters.count_documents({})
    mongo_client.close()

    print(f"\n{'='*60}")
    print(f"  FERDIG! {total_sections} nye seksjoner lagret")
    print(f"  Totalt i DB: {total} seksjoner")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
