"""generate_thumbnails.py — generate default video thumbnail images."""
import os
from PIL import Image, ImageDraw

THUMB_DIR = os.path.join(os.path.dirname(__file__), "..", "public_assets", "thumbs")
os.makedirs(THUMB_DIR, exist_ok=True)

W, H = 320, 180

def make_thumbnail(title: str, filename: str):
    img = Image.new("RGB", (W, H), "#0F172A")
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(15 + (y / H) * 10)
        g = int(23 + (y / H) * 15)
        b = int(42 + (y / H) * 25)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    cx, cy = W // 2, H // 2
    pts = [(cx - 18, cy - 14), (cx - 18, cy + 14), (cx + 16, cy)]
    draw.polygon(pts, fill="#FF9933")
    for x in range(0, W, 4):
        draw.point((x, 0), fill="#FF9933")
        draw.point((x, H - 1), fill="#FF9933")
    for y in range(0, H, 4):
        draw.point((0, y), fill="#FF9933")
        draw.point((W - 1, y), fill="#FF9933")
    out = os.path.join(THUMB_DIR, filename)
    img.save(out, "JPEG", quality=85)
    print(f"  OK: {out}")
    return filename


VIDEOS = [
    ("KI-revolusjonen innen laring", "thumb_ki_revolusjon_laering.jpg"),
    ("Mestre HAV-regelen", "thumb_mestre_hav_regelen.jpg"),
    ("HAV-regelen trygge reflekser", "thumb_hav_regelen_reflekser.jpg"),
    ("Vegtrafikkloven 3 grunnregelen", "thumb_vegtrafikkloven_3.jpg"),
    ("Utviklingen av AI-laring", "thumb_utvikling_ai_laering.jpg"),
    ("Trafikkakosystemet i Norge", "thumb_trafikk_okosystem_norge.jpg"),
    ("Michaels gatelogikk", "thumb_michaels_gatelogikk.jpg"),
    ("Mestring av vikeplikt", "thumb_mestring_vikeplikt.jpg"),
    ("AI i trafikkopplaring", "thumb_ai_trafikkopplaering.jpg"),
    ("Veien til norsk forerkort", "thumb_veien_norsk_forerkort.jpg"),
    ("Uhell dine plikter", "thumb_uhell_dine_plikter.jpg"),
    ("Offisielle trafikkskilt", "thumb_offisielle_trafikkskilt.jpg"),
    ("Thai2Drive brukermanual", "thumb_thai2drive_brukermanual.jpg"),
    ("Thai til norsk forerkort", "thumb_thai_til_norsk_forerkort.jpg"),
    ("Laereren ved siden av", "thumb_th_kru_naung_baew.jpg"),
    ("Pichit bai khapkhi", "thumb_th_pichit_bai_khapkhi.jpg"),
    ("Thot rahat HAV", "thumb_th_thot_rahat_hav.jpg"),
    ("Kot su sanchat", "thumb_th_kot_su_sanchat.jpg"),
    ("Thalai kamphaeng", "thumb_th_thalai_kamphaeng.jpg"),
    ("Bai Norway class B", "thumb_th_bai_norway_class_b.jpg"),
    ("Kasat hab vikeplikt", "thumb_th_kasat_hab_vikeplikt.jpg"),
    ("Kot thanon vs kotmai", "thumb_th_kot_thanon_vs_kotmai.jpg"),
    ("Hai thang pro", "thumb_th_hai_thang_pro.jpg"),
    ("Kham upsak phasa", "thumb_th_kham_upsak_phasa.jpg"),
    ("Nang lang phuang", "thumb_th_nang_lang_phuang.jpg"),
    ("Sathapatayakam phasa", "thumb_th_sathapatayakam_phasa.jpg"),
    ("Kot hai thang 6", "thumb_th_kot_hai_thang_6.jpg"),
    ("Pichit khan 1", "thumb_th_pichit_khan_1.jpg"),
    ("Khamnanam khapkhi", "thumb_th_khamnanam_khapkhi.jpg"),
    ("Klum pai Norway", "thumb_th_klum_pai_norway.jpg"),
]

if __name__ == "__main__":
    print(f"Generating {len(VIDEOS)} thumbnails...")
    for title, fn in VIDEOS:
        make_thumbnail(title, fn)
    print(f"Done — all saved to {THUMB_DIR}")
