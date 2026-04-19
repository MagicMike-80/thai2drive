"""Re-categorize questions based on Norwegian keywords in question text.

Strategy: Run keyword-based classifier over all questions. New categories:
- Traffic Signs  — sign-related (skilt, symbol, trekantet, ...)
- Right of Way   — vikeplikt, forkjørsrett, høyreregel, kryss, rundkjøring
- Speed Limits   — fartsgrense, km/t, fartsovertredelse
- Safety         — belte, mobil, alkohol, trøtt, barn, dekk, last, speil
- Driving Conditions (NEW) — regn, mørke, tåke, snø, is, glatt, tunnel, vind, vannplaning
- Road Rules     — catch-all for resten (blinklys, forbikjøring, rygging, parkering, osv.)
"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


def classify(qtext: str, explanation: str = "") -> str:
    t = (qtext + " " + explanation).lower()

    # Traffic Signs
    sign_keywords = [
        "skilt", "åttekantet", "trekantet", "rundt skilt", "rund skilt",
        "pil på", "rødt skilt", "blått skilt", "grønt skilt", "symbol",
        "vikeplikt-skilt", "opplysningsskilt", "varselskilt", "påbudsskilt",
        "forbudsskilt", "hva betyr dette:", "hva betyr et", "hva betyr skiltet",
        "hva indikerer et", "stiplet linje", "sperrelinje", "heltrukket",
        "rød diagonal stripe", "sykkelvei", "sykkelfelt",
    ]
    if any(k in t for k in sign_keywords):
        return "Traffic Signs"

    # Right of Way
    row_keywords = [
        "vikeplikt", "forkjørsrett", "høyreregel", "høyreregelen",
        "hvem har", "utrykningskjøretøy", "blålys", "utrykning",
        "hvem skal kjøre først", "hvem må stoppe",
    ]
    if any(k in t for k in row_keywords):
        return "Right of Way"
    # Roundabout vikeplikt
    if "rundkjøring" in t and any(k in t for k in ["vike", "forkjørs"]):
        return "Right of Way"
    # Kryss uten skilt — right of way
    if "kryss" in t and ("skilt" not in t or "uten" in t):
        if any(k in t for k in ["vike", "først", "kommer samtidig"]):
            return "Right of Way"

    # Speed Limits
    speed_keywords = [
        "fartsgrense", "fartsgrensen", "fartsovertredelse",
        "km/t", "km/h", "30-sone", "50-sone", "60-sone", "80-sone", "110-sone",
        "fart i", "fart på", "fart forbi", "fart i tunneler", "miste førerkort",
        "høy fart", "gatetun", "boligområder",
    ]
    if any(k in t for k in speed_keywords):
        # but exclude when it's really about technique not the limit
        if any(k in t for k in ["øke fart", "redusere fart", "senke fart", "tilpasse fart", "øk fart"]):
            pass  # not speed limit question
        else:
            return "Speed Limits"

    # Driving Conditions
    cond_keywords = [
        "regn", "mørke", "mørket", "tåke", "snø", "is", "glatt", "glatte",
        "vannplaning", "aquaplaning", "sidevind", "vind", "kraftig sol",
        "lav sol", "mot lav sol", "sterk sol",
        "tunnel", "bakke", "oppoverbakke", "nedoverbakke", "motbakke",
        "bakketopp", "dyp", "skarp sving", "mange svinger", "smal vei",
        "løs grus", "grus", "gatebelysning", "uten gatebelysning",
        "nattkjøring", "dårlig sikt", "redusert sikt", "spor",
    ]
    if any(k in t for k in cond_keywords):
        return "Driving Conditions"

    # Safety
    safety_keywords = [
        "sikkerhetsbelte", "belte", "mobil", "mobiltelefon", "alkohol",
        "promille", "ruspåvirket", "trøtt", "trøtthet", "pause",
        "barn", "passasjer", "hest", "dyr", "husdyr", "syklist",
        "fotgjenger", "fotgjengere", "gangfelt", "gang-", "skole",
        "skolebuss", "busstopp", "nødblink", "varselblink",
        "last", "tilhenger", "taket", "speil og belte", "dekktrykk", "dekk",
        "førerkort", "nærlys", "fjernlys", "tåkelys", "lys virker",
        "bildør", "parkerings", "ulykkessted", "veiarbeid", "jernbane",
        "fotgjengerfelt",
    ]
    if any(k in t for k in safety_keywords):
        return "Safety"

    return "Road Rules"


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
        new_cat = classify(qtext, expl)
        old_cat = q.get("category", "")
        counts[new_cat] = counts.get(new_cat, 0) + 1
        if new_cat != old_cat:
            await db.questions.update_one({"_id": q["_id"]}, {"$set": {"category": new_cat}})
            changes += 1

    print(f"\nUpdated {changes} questions.")
    print("\nNew category distribution:")
    for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    client.close()


asyncio.run(main())
