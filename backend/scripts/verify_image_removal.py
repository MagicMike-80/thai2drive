# -*- coding: utf-8 -*-
"""Verifiserer via åpen lese-API at de 6 fasit-skjermbildene er fjernet."""
import requests

IDS = [
    "0f925c43-4cd6-4cbc-9041-937ed8980f4b",
    "39a42016-a9ad-4a7a-b755-8d8dddf5cccd",
    "6c140067-2b88-43d7-b682-fd89e552cf7c",
    "76b6e8c4-2253-4fe4-89a7-1c55bb9af15a",
    "be10baef-683d-4d0b-afab-965d3c9fb8b2",
    "f08447d9-fd46-48dc-8957-39f0f280387a",
]

clean = 0
for qid in IDS:
    r = requests.get(f"https://www.thai2drive.no/api/questions/{qid}", timeout=60)
    if r.status_code != 200:
        print(f"{qid[:8]}  HTTP {r.status_code}")
        continue
    q = r.json()
    b = q.get("bildeUrl") or q.get("image_url")
    if b:
        print(f"{qid[:8]}  BILDE FORTSATT DER ({len(str(b))//1024} KB)")
    else:
        print(f"{qid[:8]}  OK - bilde fjernet")
        clean += 1

print(f"\n{clean}/6 renset")
