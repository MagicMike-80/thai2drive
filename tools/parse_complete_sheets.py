import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path("Michael Trafikklærer AI materialer/Thai2Drive_spørsmål_og_svar_med_bilder")

def parse_html_table(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    table_data = []
    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
        row_cells = []
        for c in cells:
            # Check for img src
            img_src = re.findall(r'src=["\']([^"\']+)["\']', c)
            text = re.sub(r"<[^>]+>", "", c).strip()
            row_cells.append({
                "text": text,
                "images": img_src
            })
        if row_cells:
            table_data.append(row_cells)
    return table_data

# 1. Parse Sheet 1: Bilder og spørsmål.html
sheet1_data = parse_html_table(BASE / "Bilder og spørsmål.html")
print(f"Sheet 1 rows: {len(sheet1_data)}")

# 2. Parse Sheet 2: Spørsmål og fasit.html
sheet2_data = parse_html_table(BASE / "Spørsmål og fasit.html")
print(f"Sheet 2 rows: {len(sheet2_data)}")

# 3. Parse Sheet 3: OCR og kilder.html
sheet3_data = parse_html_table(BASE / "OCR og kilder.html")
print(f"Sheet 3 rows: {len(sheet3_data)}")

# Inspect headers
if len(sheet1_data) > 4:
    h1 = [c["text"] for c in sheet1_data[4]]
    print("Sheet 1 headers (row 4):", h1[:10])

if len(sheet2_data) > 4:
    h2 = [c["text"] for c in sheet2_data[4]]
    print("Sheet 2 headers (row 4):", h2[:10])

if len(sheet3_data) > 3:
    h3 = [c["text"] for c in sheet3_data[3]]
    print("Sheet 3 headers (row 3):", h3[:10])
