"""Auto-crop the icon out of its white background and save as 1024x1024 square."""
import numpy as np
from PIL import Image
from pathlib import Path

SRC = Path("/app/frontend/assets/icons/master_1024_v2.png")
DST = Path("/app/frontend/assets/icons/master_1024.png")

img = Image.open(SRC).convert("RGB")
arr = np.array(img)
print("Source:", arr.shape)

# Find non-white pixels (anything darker than near-white)
# White detection: R,G,B all > 240
is_dark = np.any(arr < 240, axis=2)

# Find bounding box
rows = np.any(is_dark, axis=1)
cols = np.any(is_dark, axis=0)
if not rows.any() or not cols.any():
    print("ERROR: no content detected")
    raise SystemExit(1)

r0, r1 = np.where(rows)[0][[0, -1]]
c0, c1 = np.where(cols)[0][[0, -1]]
print(f"Content bbox: rows {r0}-{r1}, cols {c0}-{c1}")

# Crop with small margin
margin = 10
r0 = max(0, r0 - margin)
c0 = max(0, c0 - margin)
r1 = min(arr.shape[0] - 1, r1 + margin)
c1 = min(arr.shape[1] - 1, c1 + margin)
cropped = img.crop((c0, r0, c1 + 1, r1 + 1))
print("Cropped:", cropped.size)

# Make square by padding with dark navy (matching icon background)
w, h = cropped.size
side = max(w, h)
# Use the icon's dark navy as fill
navy = (13, 29, 68)  # matches the icon's dark navy
sq = Image.new("RGB", (side, side), navy)
sq.paste(cropped, ((side - w) // 2, (side - h) // 2))

# Resize to 1024x1024
final = sq.resize((1024, 1024), Image.LANCZOS)
final.save(DST, "PNG", optimize=True)
print(f"Saved master (1024x1024) -> {DST}")
