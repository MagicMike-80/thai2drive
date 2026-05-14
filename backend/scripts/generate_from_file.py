"""
Thai2Drive - Generer spørsmål fra bilde eller PDF
Dra og slipp en fil på .bat-snarveien, eller kjør direkte:
  python generate_from_file.py bilde.jpg
  python generate_from_file.py skilt.png --antall 5
  python generate_from_file.py trafikkloven.pdf --antall 10
"""

import asyncio
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient

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

SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MIME_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"
}


def image_to_base64(path: str) -> tuple[str, str]:
    """Return (base64_data, media_type)"""
    ext = Path(path).suffix.lower()
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, MIME_TYPES.get(ext, "image/jpeg")


def pdf_to_images(pdf_path: str) -> list[tuple[str, str]]:
    """Convert PDF pages to base64 images. Returns list of (base64, media_type)"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Installerer PyMuPDF...")
        os.system(f"{sys.executable} -m pip install pymupdf -q")
        import fitz

    doc = fitz.open(pdf_path)
    images = []
    print(f"  PDF: {len(doc)} sider funnet")

    for i, page in enumerate(doc):
        mat = fitz.Matrix(2, 2)  # 2x zoom for bedre kvalitet
        pix = page.get_pixmap(matrix=mat)
        img_data = base64.standard_b64encode(pix.tobytes("png")).decode("utf-8")
        images.append((img_data, "image/png"))
        print(f"  Side {i+1}/{len(doc)} konvertert")

    doc.close()
    return images


def generate_questions_from_image(
    img_data: str,
    media_type: str,
    antall: int,
    source_label: str
) -> list:
    """Send image to Claude and get questions back"""

    prompt = f"""Du er ekspert på norsk trafikklære og vegtrafikkloven.

VIKTIG: Se nøye på bildet og vurder hva det viser:
- Hvis bildet er et SKJERMBILDE av en app, nettside eller quiz → AVVIS og returner []
- Hvis bildet viser en TRAFIKKSITUASJON, trafikkskilt, vei eller kjøresituasjon → lag spørsmål
- Hvis bildet er fra en bok/PDF med trafikkregler → lag spørsmål basert på tekst/innhold

Lag nøyaktig {antall} spørsmål til norsk teoriprøve (klasse B) basert på hva du ser.

Regler:
- Spørsmål MÅ være basert på gjeldende norsk vegtrafikkloven og trafikkregler
- Hvis bildet viser et trafikkskilt: lag spørsmål om hva skiltet betyr og reglene
- Hvis bildet viser en trafikksituasjon: lag spørsmål om riktig oppførsel
- IKKE lag spørsmål om appen eller skjermbildet selv
- Hvert spørsmål: 4 alternativer (A, B, C, D), kun ETT riktig svar
- Det riktige svaret MÅ stemme med norsk vegtrafikkloven
- VIKTIG: riktigSvar MÅ variere — bruk en blanding av A, B, C og D. IKKE samme bokstav på alle spørsmål!
- Bland rekkefølgen på alternativene slik at riktig svar ikke alltid er på samme plass
- Alle tekster på tre språk: norsk (no), thai (th), engelsk (en)
- Varier vanskelighetsgrad (easy/medium/hard)

Svar KUN med gyldig JSON-array (eller [] hvis bildet ikke er egnet):

[
  {{
    "sporsmal": {{"no": "...", "th": "...", "en": "..."}},
    "alternativer": [
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}},
      {{"text": {{"no": "...", "th": "...", "en": "..."}}}}
    ],
    "riktigSvar": "A",
    "vanskelighetsgrad": "medium",
    "kategori": "Traffic Signs",
    "forklaring": {{"no": "...", "th": "...", "en": "..."}}
  }}
]"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data,
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    )

    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())


async def save_to_database(questions: list, source_file: str) -> int:
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")

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
            "generated_by": f"ai_from_file:{Path(source_file).name}"
        }

        await db.questions.insert_one(doc)
        inserted += 1

    total = await db.questions.count_documents({})
    mongo_client.close()

    print(f"  Lagret: {inserted} nye | Hoppet over: {skipped} duplikater | Totalt: {total}")
    return inserted


async def process_file(filepath: str, antall_per_bilde: int):
    ext = Path(filepath).suffix.lower()
    filename = Path(filepath).name
    all_questions = []

    print(f"\n  Fil: {filename}")

    if ext in SUPPORTED_IMAGES:
        print(f"  Analyserer bilde med Claude...")
        img_data, media_type = image_to_base64(filepath)
        questions = generate_questions_from_image(img_data, media_type, antall_per_bilde, filename)
        print(f"  Genererte {len(questions)} spørsmål")
        all_questions.extend(questions)

    elif ext == ".pdf":
        print(f"  Konverterer PDF til bilder...")
        images = pdf_to_images(filepath)
        print(f"  Analyserer {len(images)} sider...")
        for i, (img_data, media_type) in enumerate(images):
            print(f"\n  Side {i+1}/{len(images)}: sender til Claude...")
            try:
                questions = generate_questions_from_image(
                    img_data, media_type, antall_per_bilde, f"{filename} s.{i+1}"
                )
                print(f"  Side {i+1}: {len(questions)} spørsmål")
                all_questions.extend(questions)
            except Exception as e:
                print(f"  Side {i+1}: feilet ({e})")
    else:
        print(f"  Ukjent filtype: {ext}")
        print(f"  Støttede formater: jpg, jpeg, png, gif, webp, pdf")
        return 0

    if not all_questions:
        print("  Ingen spørsmål generert")
        return 0

    # Save JSON for review
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(filepath).stem.replace(" ", "_")
    json_file = os.path.join(os.path.dirname(__file__), f"from_file_{safe_name}_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON lagret: {Path(json_file).name}")

    # Save to database
    print(f"  Lagrer til database...")
    inserted = await save_to_database(all_questions, filepath)

    return inserted


async def main():
    # Parse args
    args = sys.argv[1:]
    antall = 5  # default questions per image
    files = []

    i = 0
    while i < len(args):
        if args[i] == "--antall" and i + 1 < len(args):
            antall = int(args[i + 1])
            i += 2
        elif args[i].startswith("--"):
            i += 1
        else:
            files.append(args[i])
            i += 1

    print("\n" + "=" * 55)
    print("  Thai2Drive - Sporsmal Generator fra Fil")
    print("=" * 55)

    if not files:
        print("\n  Bruk:")
        print("    python generate_from_file.py bilde.jpg")
        print("    python generate_from_file.py skilt.png --antall 5")
        print("    python generate_from_file.py trafikkloven.pdf --antall 10")
        print("\n  Tips: dra og slipp filer pa .bat-snarveien!")
        return

    print(f"  Filer: {len(files)}")
    print(f"  Sporsmal per bilde/side: {antall}")
    print("=" * 55)

    total_inserted = 0
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"\nFil ikke funnet: {filepath}")
            continue
        inserted = await process_file(filepath, antall)
        total_inserted += inserted

    print(f"\n{'=' * 55}")
    print(f"  FERDIG! {total_inserted} nye sporsmal er live i Thai2Drive!")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    asyncio.run(main())
