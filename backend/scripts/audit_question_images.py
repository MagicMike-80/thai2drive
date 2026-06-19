# -*- coding: utf-8 -*-
"""
audit_question_images.py — KUN LESING mot produksjonsdatabasen.

Godkjent av Michael 2026-06-12: «Ja, gå for Valg 1 ... sjekk absolutt alle
andre spørsmål for lignende skjermbilder.»

Gjør to ting:
  1. Finner spørsmålet «Du blir stående i en kø som ikke beveger seg ...»
     og skriver ut id + felter.
  2. Eksporterer ALLE spørsmålsbilder (bildeUrl) til scripts/image_audit/
     som png/jpg-filer + en index.md, slik at de kan inspiseres visuelt.

Skriver ALDRI til databasen.
"""
import base64
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND / ".env")

from pymongo import MongoClient  # noqa: E402

OUT = Path(__file__).resolve().parent / "image_audit"
OUT.mkdir(exist_ok=True)

client = MongoClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

# --- 1) Målspørsmålet ---
target = db.questions.find_one(
    {"$or": [
        {"question": {"$regex": "kø som ikke beveger seg", "$options": "i"}},
        {"question_no": {"$regex": "kø som ikke beveger seg", "$options": "i"}},
        {"sporsmaal": {"$regex": "kø som ikke beveger seg", "$options": "i"}},
    ]}
)
print("=== MAALSPOERSMAAL ===")
if target:
    for k, v in target.items():
        s = str(v)
        print(f"  {k}: {s[:120]}{'...' if len(s) > 120 else ''}")
else:
    print("  IKKE FUNNET med regex — sjekk feltnavn manuelt.")
    sample = db.questions.find_one()
    if sample:
        print("  Feltnavn i et tilfeldig dokument:", list(sample.keys()))

# --- 2) Alle bilder ---
DATA_URI = re.compile(r"^data:image/(\w+);base64,(.+)$", re.DOTALL)
count = 0
rows = []
for doc in db.questions.find({"bildeUrl": {"$nin": [None, ""]}}):
    count += 1
    qid = str(doc.get("_id"))
    qtext = (doc.get("question") or doc.get("question_no")
             or doc.get("sporsmaal") or "")[:90]
    cat = doc.get("category", "?")
    url = doc["bildeUrl"]
    m = DATA_URI.match(url) if isinstance(url, str) else None
    if m:
        ext, b64 = m.group(1), m.group(2)
        fname = f"{count:03d}_{qid}.{ext}"
        try:
            (OUT / fname).write_bytes(base64.b64decode(b64))
            note = f"{len(b64)//1024} KB base64"
        except Exception as e:
            note = f"DEKODEFEIL: {e}"
            fname = "-"
    elif isinstance(url, str) and url.startswith("http"):
        fname = "-"
        note = f"ekstern URL: {url[:80]}"
    else:
        fname = "-"
        note = f"ukjent format: {str(url)[:60]}"
    rows.append((count, qid, cat, qtext, fname, note))

with open(OUT / "index.md", "w", encoding="utf-8") as f:
    f.write("| # | _id | kategori | spørsmål | fil | notat |\n|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in r) + " |\n")

print(f"\n=== BILDER === {count} spørsmål har bildeUrl — eksportert til {OUT}")
total = db.questions.count_documents({})
print(f"Totalt antall spørsmål: {total}")
client.close()
