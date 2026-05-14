"""
Thai2Drive - Question Generator with Images
Genererer spørsmål med matching bilder (offisielle skilt + AI-genererte situasjoner)
Bruk: python generate_with_images.py [antall] [stil]
Eks:  python generate_with_images.py 50 anime
Eks:  python generate_with_images.py 50 realistic
"""

import asyncio
import json
import uuid
import os
import sys
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(override=True)

# Read API key directly
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

# Official Norwegian traffic sign images (Wikimedia Commons - public domain)
OFFICIAL_SIGNS = {
    "fareskilt barn": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "fareskilt sving": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "fareskilt veikryss": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Norwegian-road-sign-120.svg/240px-Norwegian-road-sign-120.svg.png",
    "fareskilt gangfelt": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "fareskilt togovergang": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-107.svg/240px-Norwegian-road-sign-107.svg.png",
    "fareskilt is": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "stopp skilt": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "vikeplikt": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Norwegian-road-sign-204.svg/240px-Norwegian-road-sign-204.svg.png",
    "forkjorsvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",
    "forbudt innkjoring": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",
    "parkering forbudt": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "rundkjoring": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "motorvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "gangvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Norwegian-road-sign-519.svg/240px-Norwegian-road-sign-519.svg.png",
    "fartsgrense 30": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Norwegian-road-sign-362.1.svg/240px-Norwegian-road-sign-362.1.svg.png",
    "fartsgrense 50": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "fartsgrense 80": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Norwegian-road-sign-362.4.svg/240px-Norwegian-road-sign-362.4.svg.png",
}


def get_ai_image_url(description: str, style: str = "anime") -> str:
    """Generate image URL using Pollinations.ai (free, no API key needed)"""
    if style == "anime":
        prompt = f"anime style, cute illustration, Norwegian traffic scene: {description}, simple clean design, bright colors, manga art style"
    else:
        prompt = f"realistic photo, Norwegian road traffic: {description}, daylight, clear weather"

    encoded = urllib.parse.quote(prompt)
    # Pollinations.ai - completely free image generation
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=384&model=flux&seed={hash(description) % 10000}&nologo=true"
    return url


def find_official_sign(question_text: str) -> str | None:
    """Try to match question to an official sign image"""
    q_lower = question_text.lower()
    for keyword, url in OFFICIAL_SIGNS.items():
        if any(word in q_lower for word in keyword.split()):
            return url
    return None


def generate_batch(count: int) -> list:
    """Generate a single batch of questions"""
    prompt = f"""Du er ekspert på norsk trafikklære. Lag nøyaktig {count} varierte spørsmål til teoriprøven for klasse B.

KRAV:
- Spørsmål fra ALLE disse kategoriene (fordel jevnt):
  * Trafikkskilt (fareskilt, forbudsskilt, påbudsskilt)
  * Trafikkregler (vikeplikt, kjørefelt, forbikjøring)
  * Fartsgrenser og fartsjustering
  * Kryss og rundkjøringer
  * Trafikksikkerhet (bilbelte, rus, trøtthet)
  * Fotgjengere og syklister
  * Kjøretøykunnskap
  * Miljø og økonomi
- Hvert spørsmål har 4 alternativer (A, B, C, D) - kun ETT riktig
- VIKTIG: riktigSvar MÅ variere — bruk en blanding av A, B, C og D. IKKE samme bokstav på alle spørsmål!
- Alle tekster på tre språk: norsk (no), thai (th), engelsk (en)
- Variert vanskelighetsgrad
- Legg til "bildeType" felt som beskriver hvilket bilde som passer:
  * "skilt: [skiltnavn]" for skiltspørsmål
  * "situasjon: [kort beskrivelse på engelsk]" for situasjonsbilder

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
    "kategori": "Traffic Signs",
    "bildeType": "skilt: fareskilt barn ELLER situasjon: car approaching zebra crossing with children",
    "forklaring": {{"no": "...", "th": "...", "en": "..."}}
  }}
]"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())


def generate_questions_with_images(count: int, style: str) -> list:
    print(f"\n🤖 Genererer {count} spørsmål med bilder (stil: {style})...")

    BATCH_SIZE = 10
    all_questions = []
    remaining = count

    while remaining > 0:
        batch = min(BATCH_SIZE, remaining)
        batch_num = (count - remaining) // BATCH_SIZE + 1
        print(f"\n  Batch {batch_num}: genererer {batch} spørsmål...")
        try:
            questions = generate_batch(batch)
            all_questions.extend(questions)
            print(f"  ✅ Batch {batch_num}: {len(questions)} spørsmål")
            remaining -= batch
        except Exception as e:
            print(f"  ❌ Batch {batch_num} feilet: {e}")
            remaining -= batch  # skip and continue

    print(f"\n✅ Genererte totalt {len(all_questions)} spørsmål")
    return all_questions


def assign_images(questions: list, style: str) -> list:
    """Assign images to questions"""
    print(f"\n🖼️  Tildeler bilder ({style}-stil)...")

    for i, q in enumerate(questions):
        bilde_type = q.get("bildeType", "")

        if bilde_type.startswith("skilt:"):
            sign_name = bilde_type.replace("skilt:", "").strip().lower()
            official_url = find_official_sign(sign_name)
            if official_url:
                q["bildeUrl"] = official_url
                print(f"  [{i+1}] 🇳🇴 Offisielt skilt: {sign_name[:40]}")
            else:
                q["bildeUrl"] = get_ai_image_url(f"Norwegian traffic sign: {sign_name}", style)
                print(f"  [{i+1}] 🎨 AI-skilt: {sign_name[:40]}")

        elif bilde_type.startswith("situasjon:"):
            situation = bilde_type.replace("situasjon:", "").strip()
            q["bildeUrl"] = get_ai_image_url(situation, style)
            print(f"  [{i+1}] 🎨 AI-situasjon: {situation[:40]}")

        else:
            # Generate from question text
            q["bildeUrl"] = get_ai_image_url(q["sporsmal"]["en"][:100], style)
            print(f"  [{i+1}] 🎨 AI-generert")

    return questions


async def save_to_database(questions: list) -> int:
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
            "bildeUrl": q.get("bildeUrl"),
            "category": q.get("kategori", "Traffic Rules"),
            "difficulty": q.get("vanskelighetsgrad", "medium"),
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "ai_generator_v2_with_images"
        }

        await db.questions.insert_one(doc)
        inserted += 1

    total = await db.questions.count_documents({})
    with_images = await db.questions.count_documents({"bildeUrl": {"$ne": None}})
    mongo_client.close()

    print(f"\n💾 Lagret: {inserted} nye | Hoppet over: {skipped} duplikater")
    print(f"📊 Totalt i DB: {total} | Med bilder: {with_images}")
    return inserted


async def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    style = sys.argv[2] if len(sys.argv) > 2 else "anime"

    if style not in ["anime", "realistic"]:
        style = "anime"

    print("\n" + "=" * 50)
    print("  Thai2Drive - Sporsmal Generator med Bilder")
    print("=" * 50)
    print(f"  Antall: {count}")
    print(f"  Bildestil: {style}")
    print("=" * 50)

    # Generate questions
    questions = generate_questions_with_images(count, style)

    # Assign images
    questions = assign_images(questions, style)

    # Save to JSON for review
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(os.path.dirname(__file__), f"generated_with_images_{timestamp}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n📁 JSON lagret: {filename}")

    # Save to database
    print("\n💾 Lagrer til database...")
    result = await save_to_database(questions)

    print(f"\n✅ FERDIG! {result} nye spørsmål med bilder er live i Thai2Drive!")

    # Show preview
    q = questions[0]
    print(f"\n📝 Eksempel:")
    print(f"  NO: {q['sporsmal']['no']}")
    print(f"  TH: {q['sporsmal']['th']}")
    print(f"  Bilde: {q.get('bildeUrl', 'ingen')[:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
