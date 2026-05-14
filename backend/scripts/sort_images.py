"""
sort_images.py
==============
Scanner Trafikkbildet-mappen og skiller ekte trafikkbilder
fra app-skjermbilder (mørk bakgrunn fra Thai2Drive-appen).

App-skjermbilder flyttes til: Trafikkbildet/_skjermbilder/
Ekte bilder blir liggende.

Kjør: python scripts/sort_images.py
"""

from pathlib import Path
from PIL import Image
import shutil

IMAGES_DIR = Path(r"C:\Users\Stein Hoang\CrossDevice\Michael sin Z Flip5\storage\DCIM\Trafikkbildet")
OUT_DIR    = IMAGES_DIR / "_skjermbilder"
SUPPORTED  = {'.jpg', '.jpeg', '.png', '.webp'}

# App-bakgrunn: #0B1226 = RGB(11, 18, 38) — sjekker hjørner og topp/bunn
APP_BG_R, APP_BG_G, APP_BG_B = 11, 18, 38
TOLERANCE = 40  # hvor mye avvik tillates


def is_app_screenshot(img_path: Path) -> bool:
    try:
        img = Image.open(img_path).convert("RGB")
        w, h = img.size

        # App-skjermbilder er portrett (høyere enn brede)
        if w >= h:
            return False  # Landskap = sannsynlig ekte bilde

        # Sjekk 8 punkter langs kantene for mørk bakgrunn
        check_points = [
            (5, 5), (w-5, 5),           # topp
            (5, h-5), (w-5, h-5),       # bunn
            (5, h//2), (w-5, h//2),     # midten
            (w//2, 5), (w//2, h-5),     # midten topp/bunn
        ]

        dark_count = 0
        for x, y in check_points:
            r, g, b = img.getpixel((x, y))
            if (abs(r - APP_BG_R) < TOLERANCE and
                abs(g - APP_BG_G) < TOLERANCE and
                abs(b - APP_BG_B) < TOLERANCE):
                dark_count += 1

        # Hvis 4+ punkter har app-bakgrunn → sannsynlig skjermbilde
        return dark_count >= 4

    except Exception as e:
        print(f"  Feil på {img_path.name}: {e}")
        return False


def main():
    images = [p for p in sorted(IMAGES_DIR.iterdir())
              if p.suffix.lower() in SUPPORTED and not p.parent.name.startswith('_')]

    print(f"Fant {len(images)} bilder i {IMAGES_DIR.name}")
    OUT_DIR.mkdir(exist_ok=True)

    screenshots = []
    real_photos = []

    for img_path in images:
        if is_app_screenshot(img_path):
            screenshots.append(img_path)
        else:
            real_photos.append(img_path)

    print(f"\nEkte trafikkbilder: {len(real_photos)}")
    print(f"App-skjermbilder:   {len(screenshots)}")

    if screenshots:
        print(f"\nFlytter skjermbilder til: {OUT_DIR.name}/")
        for p in screenshots:
            dest = OUT_DIR / p.name
            shutil.move(str(p), str(dest))
            print(f"  Flyttet: {p.name}")

    print(f"\nFERDIG! {len(real_photos)} ekte bilder gjenstår i mappen.")
    print(f"Sjekk '{OUT_DIR.name}/' og slett manuelt de som ikke skal brukes.")


if __name__ == "__main__":
    main()
