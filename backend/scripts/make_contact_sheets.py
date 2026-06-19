# -*- coding: utf-8 -*-
"""Dekoder alle bildespørsmål og lager kontaktark (rutenett med nummer)
for visuell gjennomgang. Kun lokale filer."""
import base64
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw
from io import BytesIO

HERE = Path(__file__).resolve().parent / "image_audit"
qs = json.loads((HERE / "image_questions.json").read_text(encoding="utf-8"))
DATA_URI = re.compile(r"^data:image/(\w+);base64,(.*)$", re.DOTALL)

THUMB = (300, 225)
COLS, ROWS = 5, 6
PER = COLS * ROWS

entries = []  # (idx, qid, image or None, note)
for i, q in enumerate(sorted(qs, key=lambda x: x["id"]), 1):
    url = q.get("bildeUrl") or ""
    img, note = None, ""
    m = DATA_URI.match(url) if isinstance(url, str) else None
    if m:
        try:
            img = Image.open(BytesIO(base64.b64decode(m.group(2)))).convert("RGB")
            note = f"{img.width}x{img.height} {m.group(1)}"
        except Exception as e:
            note = f"dekodefeil: {e}"
    elif isinstance(url, str) and url.startswith("http"):
        note = f"URL: {url[:70]}"
    else:
        note = f"annet: {str(url)[:50]}"
    entries.append((i, q["id"], img, note, q))

# Indeksfil
with open(HERE / "index.tsv", "w", encoding="utf-8") as f:
    for i, qid, img, note, q in entries:
        qt = q.get("question")
        no = (qt.get("no") if isinstance(qt, dict) else q.get("question_text_no") or str(qt) or "")
        f.write(f"{i}\t{qid}\t{q.get('category')}\t{note}\t{(no or '')[:100]}\n")

# Kontaktark
sheet_n = 0
for start in range(0, len(entries), PER):
    sheet_n += 1
    sheet = Image.new("RGB", (COLS * THUMB[0], ROWS * (THUMB[1] + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for j, (i, qid, img, note, q) in enumerate(entries[start:start + PER]):
        x = (j % COLS) * THUMB[0]
        y = (j // COLS) * (THUMB[1] + 22)
        if img:
            t = img.copy()
            t.thumbnail(THUMB)
            sheet.paste(t, (x + (THUMB[0] - t.width) // 2, y))
        d.rectangle([x, y + THUMB[1], x + THUMB[0], y + THUMB[1] + 22], fill="black")
        d.text((x + 4, y + THUMB[1] + 4), f"#{i}  {note[:34]}", fill="white")
    sheet.save(HERE / f"sheet_{sheet_n:02d}.jpg", quality=80)

print(f"{len(entries)} bilder, {sheet_n} kontaktark i {HERE}")
