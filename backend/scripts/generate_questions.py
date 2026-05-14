"""
Thai2Drive - Question Generator
Genererer nye spørsmål basert på norsk trafikkregelverket.
Bruk: python generate_questions.py [kategori] [antall]
Eks:  python generate_questions.py "Traffic Signs" 20
"""

import asyncio
import json
import uuid
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(override=True)

# Read API key directly from .env file if not in environment
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break

client = anthropic.Anthropic(api_key=api_key)

# Offisielle norske trafikkskilt (Wikimedia Commons - stabile bilder)
SIGN_IMAGES = {
    "barn": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "skoleelev": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "sving": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "kurve": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "veikryss": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Norwegian-road-sign-120.svg/240px-Norwegian-road-sign-120.svg.png",
    "gangfelt": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "fotgjenger": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "togovergang": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-107.svg/240px-Norwegian-road-sign-107.svg.png",
    "jernbane": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-107.svg/240px-Norwegian-road-sign-107.svg.png",
    "glatt": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "is": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "vegarbeid": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Norwegian-road-sign-151.svg/240px-Norwegian-road-sign-151.svg.png",
    "elg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Norwegian-road-sign-140.svg/240px-Norwegian-road-sign-140.svg.png",
    "dyr": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Norwegian-road-sign-140.svg/240px-Norwegian-road-sign-140.svg.png",
    "stopp": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "vikeplikt": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Norwegian-road-sign-204.svg/240px-Norwegian-road-sign-204.svg.png",
    "forkjørsvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",
    "forkjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",
    "parkering": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "stans": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "forbikjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Norwegian-road-sign-316.svg/240px-Norwegian-road-sign-316.svg.png",
    "forbikjøre": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Norwegian-road-sign-316.svg/240px-Norwegian-road-sign-316.svg.png",
    "30 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Norwegian-road-sign-362.1.svg/240px-Norwegian-road-sign-362.1.svg.png",
    "50 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "60 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Norwegian-road-sign-362.3.svg/240px-Norwegian-road-sign-362.3.svg.png",
    "80 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Norwegian-road-sign-362.4.svg/240px-Norwegian-road-sign-362.4.svg.png",
    "100 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Norwegian-road-sign-362.5.svg/240px-Norwegian-road-sign-362.5.svg.png",
    "fartsgrense": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "hastighet": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "rundkjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "motorvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "sykkel": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Norwegian-road-sign-519.svg/240px-Norwegian-road-sign-519.svg.png",
    "kryss": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Norwegian-road-sign-120.svg/240px-Norwegian-road-sign-120.svg.png",
    "promille": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "alkohol": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "bilbelte": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "trøtt": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-160.svg/240px-Norwegian-road-sign-160.svg.png",
    "innkjøring forbudt": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",
}

def find_sign_image(question_text: str) -> str | None:
    """Finn offisielt skiltbilde basert på spørsmålstekst"""
    q_lower = question_text.lower()
    for keyword in sorted(SIGN_IMAGES.keys(), key=len, reverse=True):
        if keyword in q_lower:
            return SIGN_IMAGES[keyword]
    return None

CATEGORIES = {
    "Traffic Signs":    "trafikkskilt (fareskilt, forbudsskilt, påbudsskilt, opplysningsskilt, vegoppmerking)",
    "Traffic Rules":    "trafikkregler (vikeplikt, kjørefelt, forbikjøring, parkering, stans)",
    "Speed Limits":     "fartsgrenser og fartsjustering (tettbygd strøk, motorvei, skole, glatt vei)",
    "Road Rules":       "vegtrafikkloven og kjøreregler (avstand, lys, sikt, feltskifte)",
    "Safety":           "trafikksikkerhet (bilbelte, ruspåvirkning, trøtthet, barn i bil, ulykker)",
    "Environment":      "miljø og økonomisk kjøring (drivstoff, utslipp, dekk, vedlikehold)",
    "Vehicle":          "kjøretøykunnskap (bremser, dekk, lys, last, tilhenger)",
    "Intersections":    "kryss og rundkjøringer (vikeplikt, lysregulering, sving, plassering)",
    "Pedestrians":      "fotgjengere og syklister (gangfelt, sykkelvei, skole, barn)",
    "First Aid":        "førstehjelp ved ulykker (varsling, livreddende førstehjelp, brann)",
}

LETTERS = ["A", "B", "C", "D"]


def generate_questions_for_category(category: str, topic: str, count: int) -> list:
    print(f"\n🤖 Genererer {count} spørsmål for: {category}")

    prompt = f"""Du er ekspert på norsk trafikklære og lager spørsmål til teoriprøven for klasse B (personbil).

Lag nøyaktig {count} UNIKE og VARIERTE spørsmål om: {topic}

REGLER:
- Spørsmålene skal baseres på gjeldende norsk trafikkregelverket
- Hvert spørsmål har 4 svaralternativer (A, B, C, D)
- Kun ETT svar er riktig
- Spørsmål skal være på tre språk: norsk (no), thai (th), engelsk (en)
- Svaralternativer og forklaringer også på tre språk
- Forklaringen skal forklare HVORFOR svaret er riktig (1-2 setninger)
- Varier vanskelighetsgrad: noen enkle, noen middels, noen vanskelige
- IKKE lag spørsmål som starter med "Hva er riktig..." - varier starten!
- Bruk realistiske situasjoner fra norsk trafikk

Svar KUN med gyldig JSON-array, ingen annen tekst:

[
  {{
    "sporsmal": {{
      "no": "Norsk spørsmål her?",
      "th": "คำถามภาษาไทย?",
      "en": "English question here?"
    }},
    "alternativer": [
      {{"text": {{"no": "Alt A norsk", "th": "ตัวเลือก A ไทย", "en": "Option A english"}}}},
      {{"text": {{"no": "Alt B norsk", "th": "ตัวเลือก B ไทย", "en": "Option B english"}}}},
      {{"text": {{"no": "Alt C norsk", "th": "ตัวเลือก C ไทย", "en": "Option C english"}}}},
      {{"text": {{"no": "Alt D norsk", "th": "ตัวเลือก D ไทย", "en": "Option D english"}}}}
    ],
    "riktigSvar": "B",
    "vanskelighetsgrad": "medium",
    "forklaring": {{
      "no": "Forklaring norsk",
      "th": "คำอธิบายภาษาไทย",
      "en": "English explanation"
    }}
  }}
]"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()

    # Clean up JSON if needed
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    questions = json.loads(text.strip())
    print(f"✅ Genererte {len(questions)} spørsmål")
    return questions


async def save_to_database(questions: list, category: str):
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")

    if not mongo_url or not db_name:
        print("⚠️  Ingen database tilkobling - lagrer til JSON-fil")
        return None

    mongo_client = AsyncIOMotorClient(mongo_url)
    db = mongo_client[db_name]

    inserted = 0
    skipped = 0

    for q in questions:
        existing = await db.questions.find_one({"question.no": q["sporsmal"]["no"]})
        if existing:
            skipped += 1
            continue

        # Auto-assign sign image if available
        bilde_url = find_sign_image(q["sporsmal"]["no"])

        doc = {
            "id": str(uuid.uuid4()),
            "question": q["sporsmal"],
            "options": [
                {"id": LETTERS[i], "text": q["alternativer"][i]["text"]}
                for i in range(4)
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": q["forklaring"],
            "bildeUrl": bilde_url,
            "category": category,
            "difficulty": q.get("vanskelighetsgrad", "medium"),
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "ai_generator_v1"
        }

        await db.questions.insert_one(doc)
        inserted += 1

    total = await db.questions.count_documents({})
    mongo_client.close()

    print(f"💾 Lagret: {inserted} nye | Hoppet over: {skipped} duplikater | Totalt i DB: {total}")
    return inserted


def save_to_json(questions: list, category: str, filename: str):
    """Lagre til JSON-fil for manuell gjennomgang"""
    LETTERS_MAP = ["A", "B", "C", "D"]
    output = []

    for q in questions:
        doc = {
            "id": str(uuid.uuid4()),
            "question": q["sporsmal"],
            "options": [
                {"id": LETTERS_MAP[i], "text": q["alternativer"][i]["text"]}
                for i in range(4)
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": q["forklaring"],
            "bildeUrl": None,
            "category": category,
            "difficulty": q.get("vanskelighetsgrad", "medium"),
            "active": True,
            "schema_version": 2,
        }
        output.append(doc)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"📁 Lagret til: {filename}")
    return filename


async def main():
    category = sys.argv[1] if len(sys.argv) > 1 else None
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print("\n🚗 Thai2Drive - Spørsmål Generator")
    print("=" * 40)

    if not category:
        print("\nTilgjengelige kategorier:")
        for i, (cat, desc) in enumerate(CATEGORIES.items(), 1):
            print(f"  {i}. {cat}")
        print("\nVelg kategori (nummer eller navn): ", end="")
        choice = input().strip()

        if choice.isdigit():
            cat_list = list(CATEGORIES.keys())
            idx = int(choice) - 1
            if 0 <= idx < len(cat_list):
                category = cat_list[idx]
            else:
                print("❌ Ugyldig valg")
                return
        else:
            category = choice

    if category not in CATEGORIES:
        print(f"❌ Ukjent kategori: {category}")
        print(f"Tilgjengelige: {', '.join(CATEGORIES.keys())}")
        return

    topic = CATEGORIES[category]
    print(f"\n📚 Kategori: {category}")
    print(f"📖 Tema: {topic}")
    print(f"🔢 Antall: {count}")

    # Generate questions
    questions = generate_questions_for_category(category, topic, count)

    # Save to JSON file first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_{category.replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    save_to_json(questions, category, filepath)

    # Try to save to database
    print("\n💾 Lagrer til database...")
    result = await save_to_database(questions, category)

    if result is None:
        print(f"\n✅ Ferdig! {len(questions)} spørsmål lagret til {filename}")
        print("👉 Kjør import_questions.py for å laste inn i databasen")
    else:
        print(f"\n✅ Alt ferdig! {result} nye spørsmål er nå live i Thai2Drive!")

    # Preview first question
    if questions:
        q = questions[0]
        print("\n📝 Eksempel på generert spørsmål:")
        print(f"  NO: {q['sporsmal']['no']}")
        print(f"  TH: {q['sporsmal']['th']}")
        print(f"  EN: {q['sporsmal']['en']}")
        print(f"  Svar: {q['riktigSvar']}")


if __name__ == "__main__":
    asyncio.run(main())
