"""
compress_signs.py — resize + compress sign images and copy to backend/sign_images/.
Run from repo root: python compress_signs.py

Target: max 400px on longest side, JPEG quality 72 (~30-60 KB per image).
Signs are displayed at ~100x100 on mobile — 400px is plenty.
"""
import os
import re
import shutil
from pathlib import Path
from PIL import Image

SRC_BASE = Path(r"C:\Users\Stein Hoang\Telia Sky\Thai2Drive1\9skiltgrupper")
DST      = Path(r"C:\Users\Stein Hoang\thai2drive\backend\sign_images")
DST.mkdir(parents=True, exist_ok=True)

FOLDERS = [
    "vikeplikt-jpg (1)",
    "fareskilt-jpg",
    "forbudsskilt-jpg-png",
    "pabudsskilt-jpg (1)",
    "opplysningsskilt-jpg",
    "vegvisningsskilt-jpg",
    "underskilt-jpg-og-png",
    "markeringsskilt-jpg",
]

MAX_DIM = 400
QUALITY = 72

total_in = 0
total_out = 0
count = 0

for folder in FOLDERS:
    src_dir = SRC_BASE / folder
    if not src_dir.exists():
        print(f"skip (not found): {folder}")
        continue

    files = sorted(f for f in src_dir.iterdir()
                   if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not files:
        print(f"skip (empty): {folder}")
        continue

    print(f"\n{folder}  ({len(files)} images)")
    for src in files:
        # Normalise filename — replace spaces with underscores, keep .jpg
        safe_name = re.sub(r"\s+", "_", src.stem) + ".jpg"
        dst_path  = DST / safe_name

        try:
            img = Image.open(src).convert("RGB")
            # Resize — keep aspect ratio
            w, h = img.size
            if max(w, h) > MAX_DIM:
                scale = MAX_DIM / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            img.save(dst_path, "JPEG", quality=QUALITY, optimize=True)
            total_in  += src.stat().st_size
            total_out += dst_path.stat().st_size
            count += 1
            print(f"  {safe_name}  {src.stat().st_size//1024}KB → {dst_path.stat().st_size//1024}KB")
        except Exception as e:
            print(f"  ERROR {src.name}: {e}")

print(f"\n{'='*50}")
print(f"Done: {count} images")
print(f"Total before: {total_in//1024//1024:.1f} MB")
print(f"Total after:  {total_out//1024//1024:.1f} MB")
print(f"Reduction:    {100*(1-total_out/total_in):.0f}%")
print(f"Images in:    {DST}")
