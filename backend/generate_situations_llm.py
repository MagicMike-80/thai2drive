"""Generate 200 Situations questions using Emergent LLM (Gemini).

Batches of 50 → insert each batch before next.
Topics derived from Trinn 4 Trafikalt PDF themes.
"""
import asyncio, os, json, uuid, re
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY") or "sk-emergent-b48A3D57008C8350c6"

LETTERS = ["A", "B", "C", "D"]

# Batches with themes
BATCHES = [
    {"name": "obs_risk_A", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: kjøredyktighet, oversikt, sansning, blindsoner, oppmerksomhet."},
    {"name": "obs_risk_B", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: risikoforståelse, selvinnsikt, distraksjoner (mobil/passasjerer/musikk), press fra venner."},
    {"name": "speed_A", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: fart, reaksjonstid, bremselengde (fartens kvadrat), stopplengde."},
    {"name": "speed_B", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: forbikjøring (sikt/avstand/luke/retur), 3-sekunder-regelen, riktig fart for forhold."},
    {"name": "comm_A", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: kommunikasjon i trafikk — blinklys, blikk, tegn, horn, lyssignal."},
    {"name": "comm_B", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: plassering i kjørebanen, før sving, i rundkjøring, smal vei, samhandling med syklister/fotgjengere/trikk/lastebil."},
    {"name": "complex_A", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: mørkekjøring (blending, nær-/fjernlys, refleks, fotgjengere i mørke), ulykker (førstemann, 113, sikring, førstehjelp)."},
    {"name": "complex_B", "count": 25, "prompt": "Generer 25 norske trafikkspørsmål om: vinterkjøring/glatt føre, kjetting, vinterdekk, bilens tilstand (bremser/dekk/lys/speil/sikt)."},
]

SCHEMA_INSTRUCTION_TEMPLATE = """
Returner KUN et gyldig JSON-array med {count} objekter — ingen annen tekst.
Hvert objekt MÅ ha denne strukturen:

{{
  "q": {{"no": "...", "th": "คำถาม...", "en": "..."}},
  "opts": [
    {{"no": "alt1", "th": "...", "en": "..."}},
    {{"no": "alt2", "th": "...", "en": "..."}},
    {{"no": "alt3", "th": "...", "en": "..."}},
    {{"no": "alt4", "th": "...", "en": "..."}}
  ],
  "correct": "A",
  "expl": {{"no": "kort forklaring 1-2 setninger", "th": "...", "en": "..."}},
  "difficulty": "easy|medium|hard"
}}

Regler:
- Alle spørsmål MÅ være UNIKE.
- 4 alternativer: 1 riktig + 3 realistiske feil.
- Fordel difficulty ca: 30% easy, 50% medium, 20% hard.
- correct = "A", "B", "C" eller "D".
- Thai (th) kort og korrekt oversettelse.
- Returner KUN JSON — ingen markdown, ingen tekst rundt.
"""


def extract_json(text: str):
    """Extract a JSON array from LLM response, handling markdown fences."""
    # Remove code fences
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    # Find first [ and last ]
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found")
    return json.loads(text[start : end + 1])


async def generate_batch(prompt_topics: str, count: int, session_id: str) -> list:
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=session_id,
        system_message=(
            "Du er en erfaren norsk trafikklærer som lager realistiske flervalgsspørsmål "
            "på norsk, thai og engelsk. Svar KUN med JSON — ingen annen tekst."
        ),
    ).with_model("openai", "gpt-4o-mini")

    schema = SCHEMA_INSTRUCTION_TEMPLATE.format(count=count)
    user_msg = UserMessage(text=prompt_topics + "\n\n" + schema)
    resp = await chat.send_message(user_msg)
    return extract_json(resp)


async def insert_batch(db, items: list) -> tuple[int, int]:
    inserted = 0
    skipped = 0
    for r in items:
        try:
            qno = r["q"]["no"].strip()
            existing = await db.questions.find_one({"question.no": qno})
            if existing:
                skipped += 1
                continue
            diff = r.get("difficulty", "medium")
            if diff not in ("easy", "medium", "hard"):
                diff = "medium"
            correct = r.get("correct", "A").upper()
            if correct not in LETTERS:
                correct = "A"
            doc = {
                "id": str(uuid.uuid4()),
                "question": r["q"],
                "options": [{"id": LETTERS[i], "text": r["opts"][i]} for i in range(4)],
                "correctOptionId": correct,
                "explanation": r["expl"],
                "bildeUrl": None,
                "category": "Situations",
                "difficulty": diff,
                "active": True,
                "schema_version": 2,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "LLM-generated (Trinn 4 PDF themes)",
            }
            await db.questions.insert_one(doc)
            inserted += 1
        except Exception as e:
            print(f"  Skip (error): {e}")
            skipped += 1
    return inserted, skipped


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    start_total = await db.questions.count_documents({})
    print(f"Starting total: {start_total}")

    grand_inserted = 0
    for i, batch in enumerate(BATCHES, 1):
        print(f"\n=== Batch {i}/{len(BATCHES)}: {batch['name']} ===")
        try:
            items = await generate_batch(batch["prompt"], batch["count"], f"sit-{batch['name']}-{i}")
            print(f"  LLM returned {len(items)} items")
            ins, skp = await insert_batch(db, items)
            grand_inserted += ins
            print(f"  Inserted: {ins}, Skipped: {skp}")
            current = await db.questions.count_documents({})
            print(f"  Current DB total: {current}")
            if current >= 500:
                print("  Reached 500 target — stopping.")
                break
        except Exception as e:
            print(f"  BATCH FAILED: {e}")

    final_total = await db.questions.count_documents({})
    sit = await db.questions.count_documents({"category": "Situations"})
    print(f"\n=== FINAL ===")
    print(f"Total DB: {final_total}")
    print(f"Situations: {sit}")
    print(f"Grand inserted: {grand_inserted}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
