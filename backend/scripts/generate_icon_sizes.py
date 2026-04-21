"""Generate all iOS/Android app icon sizes from the master 1024x1024 icon."""
from pathlib import Path
from PIL import Image

ICONS_DIR = Path("/app/frontend/assets/icons")
MASTER = ICONS_DIR / "master_1024.png"

IOS_DIR = ICONS_DIR / "ios"
ANDROID_DIR = ICONS_DIR / "android"
ADAPTIVE_DIR = ICONS_DIR / "android_adaptive"
for d in [IOS_DIR, ANDROID_DIR, ADAPTIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

IOS_SIZES = [
    (1024, "icon-1024.png"),
    (180, "icon-180.png"),
    (120, "icon-120.png"),
    (87, "icon-87.png"),
    (60, "icon-60.png"),
]
ANDROID_SIZES = [
    (512, "icon-512.png"),
    (192, "icon-192.png"),
    (144, "icon-144.png"),
    (96, "icon-96.png"),
    (72, "icon-72.png"),
    (48, "icon-48.png"),
]

master = Image.open(MASTER).convert("RGB")
assert master.size == (1024, 1024)
print(f"Master: {master.size}")


def save(img: Image.Image, path: Path, size: int):
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(path, "PNG", optimize=True)
    print(f"  {path.relative_to(ICONS_DIR)}  {size}x{size}  {path.stat().st_size // 1024} KB")


print("\n=== iOS Icons ===")
for size, name in IOS_SIZES:
    save(master, IOS_DIR / name, size)

print("\n=== Android Icons ===")
for size, name in ANDROID_SIZES:
    save(master, ANDROID_DIR / name, size)

print("\n=== Android Adaptive Icon ===")
# Foreground: use master icon, resized to 512, with transparent background
# Since the master has a dark blue background, we need to crop/isolate the foreground.
# For simplicity: use the master as foreground (with its dark bg) — Android will layer it on top of bg.
# For a proper adaptive icon, best practice is to have the central graphic on transparent bg.
# Here we'll use a centered, scaled-down version of the master as foreground on transparent bg,
# so the adaptive background (solid dark blue) shows around edges during animations.
fg = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
inner = master.resize((340, 340), Image.LANCZOS).convert("RGBA")
fg.paste(inner, ((512 - 340) // 2, (512 - 340) // 2), inner)
fg.save(ADAPTIVE_DIR / "foreground.png", "PNG", optimize=True)
print(f"  android_adaptive/foreground.png  512x512  {(ADAPTIVE_DIR / 'foreground.png').stat().st_size // 1024} KB")

# Background: solid dark blue gradient 1080x1080
bg = Image.new("RGB", (1080, 1080), (11, 28, 64))  # deep navy
# Simple vertical gradient
import math
for y in range(1080):
    t = y / 1080
    r = int(11 + (25 - 11) * t)
    g = int(28 + (50 - 28) * t)
    b = int(64 + (108 - 64) * t)
    for x in range(1080):
        bg.putpixel((x, y), (r, g, b))
# More efficient: use numpy for gradient instead
import numpy as np
arr = np.zeros((1080, 1080, 3), dtype=np.uint8)
for y in range(1080):
    t = y / 1080
    arr[y, :, 0] = int(11 + (25 - 11) * t)
    arr[y, :, 1] = int(28 + (50 - 28) * t)
    arr[y, :, 2] = int(64 + (108 - 64) * t)
bg = Image.fromarray(arr)
bg.save(ADAPTIVE_DIR / "background.png", "PNG", optimize=True)
print(f"  android_adaptive/background.png  1080x1080  {(ADAPTIVE_DIR / 'background.png').stat().st_size // 1024} KB")

print("\n✅ All icons generated!")
