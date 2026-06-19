"""
Thai2Drive - Slå sammen kategorier
Oppdaterer alle spørsmål i databasen fra 15 til 9 kategorier.
Bruk: python merge_categories.py
"""

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(override=True)

MONGO_URL = os.environ.get("MONGODB_URL") or os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("MONGO_DB", "thai2drive")

# Mapping: gammel kategori → ny kategori
MAPPING = {
    # Runde 1
    "Traffic Safety":               "Safety",
    "Driving Behavior":             "Situations",
    "Environment and Economy":      "Driving Conditions",
    "Intersections and Roundabouts":"Right of Way",
    "Parkering":                    "Traffic Rules",
    "Vehicle Knowledge":            "Road Conditions",
    "Pedestrians and Cyclists":     "Road Rules",
    # Runde 2 - stray kategorier
    "Traffic Situations":           "Situations",
    "Vikeplikt":                    "Right of Way",
    "Intersections":                "Right of Way",
    "Driving Behaviour":            "Situations",
    "Driver Behavior":              "Situations",
    "Parking Rules":                "Traffic Rules",
    "Traffic Control":              "Road Rules",
    "Trafikksituasjon":             "Situations",
    "Road Markings":                "Road Rules",
    "Sykling og vikeplikt":         "Right of Way",
    "Kjøreatferd":             "Situations",
    "Trafikklys":                   "Road Rules",
    "Driving Rules":                "Road Rules",
    "Trafikkregler":                "Road Rules",
    "Veiarbeid og hindringer":      "Driving Conditions",
    "Forbikjøring":            "Road Rules",
    "Interaction with Cyclists":    "Road Rules",
}

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("\n========================================")
    print("  Thai2Drive - Slå sammen kategorier")
    print("========================================\n")

    total_updated = 0

    for old_cat, new_cat in MAPPING.items():
        count = await db.questions.count_documents({"category": old_cat})
        if count == 0:
            print(f"  --  '{old_cat}' -- ingen sporsmal funnet, hopper over")
            continue

        result = await db.questions.update_many(
            {"category": old_cat},
            {"$set": {"category": new_cat}}
        )
        total_updated += result.modified_count
        print(f"  OK  '{old_cat}' -> '{new_cat}'  ({result.modified_count} sporsmal)")

    print(f"\n  Totalt oppdatert: {total_updated} sporsmal")
    print("\n  Kategorier na i databasen:")

    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    async for doc in db.questions.aggregate(pipeline):
        print(f"    • {doc['_id']}: {doc['count']}")

    print("\n  Ferdig!\n")
    client.close()

asyncio.run(main())
