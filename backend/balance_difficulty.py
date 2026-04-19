"""Balance question difficulty based on text complexity and keyword analysis.

Strategy:
- Easy: basic rules, short text, obvious answers (mobile, belte, fart i boligområder...)
- Medium: everyday scenarios (regn, forbikjøring, rundkjøring...)
- Hard: edge cases, multi-factor (vannplaning, sidevind+tilhenger, uoversiktlig bakketopp, jernbane uten bom, utkjøring gang/sykkelvei...)

Target distribution for 300 questions: ~100 easy / ~140 medium / ~60 hard
"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


# Hard keywords — complex multi-factor scenarios, advanced technique, edge cases
HARD_KEYWORDS = [
    "vannplaning", "aquaplaning",
    "sidevind", "kraftig sidevind",
    "jernbaneovergang", "uten bom",
    "uoversiktlig bakketopp", "blind", "bakketopp",
    "gang- og sykkelvei", "gang-og sykkelvei",
    "felt som opphører", "opphører",
    "heltrukket sperrelinje",
    "motorbrems", "motorbrems)",
    "tilhenger", "med tilhenger",
    "forbikjøring før",
    "aktsomhet", "ekstra aktsom",
    "bytte felt inne", "rundkjøring—bytte",
    "lang bakke", "lange bakker",
    "fri gir", "fri gir?",
    "last på taket",
    "sideavstand", "1,5 m",
    "tett tåke", "flere felt",
    "bakke med snø", "ned bakke i snø",
    "dyp spor", "dype spor",
    "vippe", "skrens",
    "miste førerkort", "grove",
    "piggdekk", "vinterdekk",
    "gatetun",
    "påsken", "første mandag",
    "skolebuss", "skolebussen",
    "brå", "brått",
]

# Easy keywords — basic definitions, obvious rules
EASY_KEYWORDS = [
    # Sign identification ("Hva betyr...")
    "hva betyr et rødt", "hva betyr et trekantet", "hva betyr et rundt",
    "hva betyr et vikeplikt", "hva betyr dette skiltet", "hva indikerer",
    "hva betyr et blått", "hva betyr et grønt", "hva betyr skiltet",
    "hva betyr et skilt", "hva betyr 'sykkelvei'", "hva betyr 'gangfelt'",
    "hva betyr heltrukket",  # will still be hard if sperre is present
    # Basic knowledge
    "hva er den generelle fartsgrensen",
    "hva er fartsgrensen på motorvei",
    "hva er fartsgrensen i en",
    "hva er fartsgrensen i boligområder",
    "hva er fartsgrensen på vanlige",
    "hva er fartsgrensen forbi en skole",
    "minstealderen", "minste alder",
    "hva er regelen for bruk av",
    "hva er reglene for",
    "når må du bruke nærlys",
    "er det lov å bruke mobil",
    "hva er riktig om blinklys",
    "hva er riktig om",
    "hva er riktig ved bruk av",
    "hva skal du gjøre når du nærmer deg",
    "hvem har vikeplikt",
    "hvem har forkjørsrett",
    "har utrykningskjøretøy",
    "hva gjør du når trafikklyset",
    "hva er reglene for parkering",
    "hvem skal kjøre først",
    "hva er minstealderen",
    "hva er riktig før du starter",
    "sikkerhetsbelte",
    "hva er riktig ved kjøring bak lastebil",
    "hva er riktig ved kjøring i regn?",
    "hva er riktig ved kjøring i kø?",
    "hva er riktig ved kjøring i sving?",
    "hva er riktig ved kjøring i bakke?",
    "hva er riktig ved kjøring i kraftig regn",
    "hva er riktig ved kjøring i sterk sol",
    "hva er riktig ved kjøring med barn i bilen",
    "hva er riktig ved kjøring med passasjerer",
    "hva er riktig ved kjøring i tett bebyggelse",
    "hva er riktig ved kjøring i mørke med møtende",
    "hva er riktig ved møtende trafikk",
    "hva er riktig ved rygging",
    "hva er riktig ved parkering",
    "hva er riktig ved forbikjøring",
    "hva er riktig når du blir forbikjørt",
    "hva er riktig når du ser barn",
    "hva er riktig når du er trøtt",
    "kan du miste førerkortet",
    "gangfart",
    "fartsgrensen i gatetun",
    "hva er fartsgrensen i tunneler",
    "hva skjer hvis du kjører",
]


def classify_difficulty(qtext: str, expl: str = "", current_diff: str = "medium") -> str:
    t = (qtext + " " + expl).lower()

    # HARD first — most specific
    if any(k in t for k in HARD_KEYWORDS):
        return "hard"

    # EASY — only very specific basics
    if any(k in t for k in EASY_KEYWORDS):
        return "easy"

    # Scenario-driven questions → medium (most questions)
    if any(k in t for k in [
        "ved kjøring", "ved møte", "nær et", "nær en", "med kø",
        "med passasjer", "med barn", "med regn", "med dårlig", "med mange",
        "på våt", "når du", "når veien", "i tett", "i høy fart", "når du er",
    ]):
        return "medium"

    # Default: medium (no more auto-easy based on length)
    return "medium"


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    total = await db.questions.count_documents({})
    print(f"Processing {total} questions...")

    counts: dict[str, int] = {}
    changes = 0

    cursor = db.questions.find({})
    async for q in cursor:
        qtext = q.get("question", {}).get("no", "") if isinstance(q.get("question"), dict) else q.get("question_text_no", "")
        expl = q.get("explanation", {}).get("no", "") if isinstance(q.get("explanation"), dict) else q.get("explanation_no", "")
        current = q.get("difficulty", "medium")
        new_diff = classify_difficulty(qtext, expl, current)
        counts[new_diff] = counts.get(new_diff, 0) + 1
        if new_diff != current:
            await db.questions.update_one({"_id": q["_id"]}, {"$set": {"difficulty": new_diff}})
            changes += 1

    print(f"\nUpdated {changes} questions.")
    print("\nNew difficulty distribution:")
    order = {"easy": 1, "medium": 2, "hard": 3}
    for diff, count in sorted(counts.items(), key=lambda x: order.get(x[0], 99)):
        pct = (count / total) * 100
        print(f"  {diff}: {count} ({pct:.1f}%)")

    client.close()


asyncio.run(main())
