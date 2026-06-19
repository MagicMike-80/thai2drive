# -*- coding: utf-8 -*-
"""Samler ALLE spørsmål med bilde via /api/questions/random?has_image=true
(åpen lese-API, ingen device-id => ingen kvote). Coupon-collector til metning."""
import json
from pathlib import Path

import requests

BASE = "https://www.thai2drive.no/api"
OUT = Path(__file__).resolve().parent / "image_audit"

seen = {}
stale = 0
rounds = 0
while stale < 6 and rounds < 80:
    rounds += 1
    qs = requests.get(f"{BASE}/questions/random", params={"count": 200, "has_image": "true"}, timeout=120).json()
    before = len(seen)
    for q in qs:
        seen[q["id"]] = q
    new = len(seen) - before
    print(f"runde {rounds}: +{new} nye, totalt {len(seen)}/735")
    stale = stale + 1 if new == 0 else 0
    if len(seen) >= 735:
        break

Path(OUT / "image_questions.json").write_text(
    json.dumps(list(seen.values()), ensure_ascii=False), encoding="utf-8"
)
print(f"\nLagret {len(seen)} bildespørsmål.")

hits = [q for q in seen.values()
        if "ikke beveger seg" in json.dumps(q.get("question"), ensure_ascii=False)
        or "ikke beveger seg" in str(q.get("question_text_no", ""))]
print(f"Treff på målteksten blant bildespørsmål: {len(hits)}")
for q in hits:
    print(q["id"], q.get("category"), str(q.get("bildeUrl"))[:60])
