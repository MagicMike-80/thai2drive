# -*- coding: utf-8 -*-
"""Sjekker via åpen lese-API hvilke bok-seksjoner som mangler no/th/en-innhold."""
import requests

BASE = "https://www.thai2drive.no/api"

chapters = requests.get(f"{BASE}/chapters", timeout=60).json()
print(f"{len(chapters)} kapitler\n")

missing = {"no": [], "th": [], "en": []}
total = 0
for ch in chapters:
    num = ch.get("chapter_num")
    secs = requests.get(f"{BASE}/chapters/{num}", timeout=60).json()
    for s in secs:
        total += 1
        for lang in ("no", "th", "en"):
            c = s.get(f"content_{lang}") or (s.get("content") or {}).get(lang) if isinstance(s.get("content"), dict) else s.get(f"content_{lang}")
            if not (c and str(c).strip()):
                title = s.get(f"title_{lang}") or s.get("title_no") or s.get("id", "?")
                missing[lang].append((num, s.get("section_num"), str(title)[:50]))

print(f"Totalt {total} seksjoner")
for lang in ("no", "th", "en"):
    print(f"\nMangler {lang.upper()}: {len(missing[lang])}")
    for m in missing[lang][:30]:
        print("  kap", m[0], "seksjon", m[1], "-", m[2])
