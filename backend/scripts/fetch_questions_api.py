# -*- coding: utf-8 -*-
"""
Henter alle spørsmål via appens ÅPNE lese-API (samme vei som appen selv).
Ingen databasetilkobling, ingen skriving — kun HTTPS GET mot thai2drive.no.

Mål (godkjent av Michael): identifisere spørsmålet med fasit-skjermbildet
og finne alle andre spørsmål med lignende skjermbilder.
"""
import base64
import json
import re
from pathlib import Path

import requests

BASE = "https://www.thai2drive.no/api"
OUT = Path(__file__).resolve().parent / "image_audit"
OUT.mkdir(exist_ok=True)

cats = requests.get(f"{BASE}/categories", timeout=60).json()
all_q = {}
for c in cats:
    name, count = c["name"], c["count"]
    fetched = []
    if count <= 200:
        fetched = requests.get(f"{BASE}/questions", params={"category": name, "limit": 200}, timeout=120).json()
    else:
        for diff in ["easy", "medium", "hard"]:
            fetched += requests.get(
                f"{BASE}/questions",
                params={"category": name, "difficulty": diff, "limit": 200},
                timeout=120,
            ).json()
    for q in fetched:
        all_q[q["id"]] = q
    print(f"{name}: {count} i DB, {len(fetched)} hentet")

print(f"\nTotalt unike hentet: {len(all_q)}")
Path(OUT / "all_questions.json").write_text(
    json.dumps(list(all_q.values()), ensure_ascii=False), encoding="utf-8"
)

# Målspørsmålet
DATA_URI = re.compile(r"^data:image/(\w+);base64,(.*)$", re.DOTALL)
hits = [q for q in all_q.values() if "ikke beveger seg" in (q.get("question") or "")]
print(f"\n=== MAALSPOERSMAAL: {len(hits)} treff ===")
for q in hits:
    print(f"id: {q['id']}")
    print(f"category: {q.get('category')} | difficulty: {q.get('difficulty')}")
    print(f"question: {q.get('question')}")
    url = q.get("bildeUrl") or ""
    m = DATA_URI.match(url)
    if m:
        ext, b64 = m.groups()
        f = OUT / f"TARGET_{q['id']}.{ext}"
        f.write_bytes(base64.b64decode(b64))
        print(f"bilde: {ext}, {len(b64)//1024} KB -> {f.name}")
    else:
        print(f"bildeUrl: {url[:100]}")
