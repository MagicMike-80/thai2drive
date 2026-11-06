"""Genererer master quiz-katalog fra de utpakkede Google Sheets:
- Bilder og spørsmål.html (182 med motivbilder og grønn fasit)
- Spørsmål og fasit.html (239 med 4 svar og grønn fasit)
- OCR og kilder.html (SHA-256, OCR-tillit og originalstier)
- resources/cellImage_*.jpg (185 ekstraherte cell-bilder)
"""

import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "Michael Trafikklærer AI materialer" / "Thai2Drive_spørsmål_og_svar_med_bilder"

def clean_ocr_text(text: str) -> str:
    """Fjerner vanlige OCR-artefakter fra spørsmålstekst."""
    if not text:
        return ""
    t = text.strip()
    # Fjerner OCR-markører som (*), (+), (%), (>), V, o, GO, CE), KN, KA, etc.
    t = re.sub(r"\s*\(\*\)\s*", " ", t)
    t = re.sub(r"\s*\(\+\)\s*", " ", t)
    t = re.sub(r"\s*\(%\)\s*", " ", t)
    t = re.sub(r"\s*\(>\)\s*", " ", t)
    t = re.sub(r"\s*\(CE\)\s*", " ", t)
    t = re.sub(r"\s*CE\)\s*", " ", t)
    t = re.sub(r"\s*GO\s*", " ", t)
    t = re.sub(r"\s*V\s*$", "", t)
    t = re.sub(r"\s*VO\s*$", "", t)
    t = re.sub(r"\s*;\s*$", "", t)
    t = re.sub(r"i70km/\s*t", "i 70 km/t", t)
    t = re.sub(r"0\)\s*planovergang", "planovergang", t)
    t = re.sub(r"på\s+KN\s+Hva", "Hva", t)
    t = re.sub(r"er\s+KA\s+Vær\s+Hva", "Hva", t)
    t = re.sub(r"på\s+AP\s+—\s+i\s+væ\s+Å\s+€\s+Når", "Når", t)
    t = re.sub(r"Hva\s+er\s+O\s+førerstøttesystemer", "Hva er førerstøttesystemer", t)
    t = re.sub(r"Hvordan\s+kontrollerer\s+du\s+om\s+O\s+bremsekraftforsterker\s*en", "Hvordan kontrollerer du om bremsekraftforsterkeren", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def categorize_question(q_text: str) -> str:
    """Kategoriserer spørsmålet inn i de 7 kanoniske læringsområdene."""
    ql = q_text.lower()
    if any(k in ql for k in ["vikeplikt", "høyreregel", "forkjørs", "kryss", "rekkefølge"]):
        return "right_of_way"
    elif any(k in ql for k in ["felt", "feltskifte", "plassering", "rundkjøring", "sving", "enveiskjørt"]):
        return "lane_positioning"
    elif any(k in ql for k in ["buss", "fotgjenger", "sykkel", "syklist", "utrykningskjøretøy", "hest", "samhandling", "trikk"]):
        return "interaction"
    elif any(k in ql for k in ["fart", "avstand", "reaksjon", "brems", "stopplengde", "sekund"]):
        return "speed_distance"
    elif any(k in ql for k in ["tunnel", "mørke", "glatt", "snø", "regn", "vannplaning", "lys", "føre"]):
        return "road_conditions"
    elif any(k in ql for k in ["skilt", "oppmerking", "linje", "sperreområde", "trafikklys", "symbol"]):
        return "traffic_signs"
    else:
        return "other_topics"

def parse_html_table(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    table_data = []
    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
        row_cells = []
        for c in cells:
            img_src = re.findall(r'src=["\']([^"\']+)["\']', c)
            text = re.sub(r"<[^>]+>", "", c).strip()
            row_cells.append({
                "text": text,
                "images": img_src
            })
        if row_cells:
            table_data.append(row_cells)
    return table_data

def main():
    print("Leser tabeller fra Thai2Drive_spørsmål_og_svar_med_bilder...")
    s1 = parse_html_table(SHEET_DIR / "Bilder og spørsmål.html")
    s2 = parse_html_table(SHEET_DIR / "Spørsmål og fasit.html")
    s3 = parse_html_table(SHEET_DIR / "OCR og kilder.html")

    # Bygg oppslag fra Sheet 3 (Kilder og metadata)
    meta_map = {}
    for r in s3[4:]:
        if len(r) > 5 and r[0]["text"]:
            bfile = r[0]["text"]
            meta_map[bfile] = {
                "ocr_raw": r[1]["text"],
                "ocr_confidence": r[2]["text"],
                "orig_path": r[3]["text"],
                "stable_copy": r[4]["text"],
                "sha256": r[5]["text"]
            }

    # Bygg oppslag fra Sheet 1 (Motivbilder med logo og cellImage)
    sheet1_map = {}
    for r in s1[4:]:
        if len(r) > 7 and r[1]["text"]:
            bfile = r[1]["text"]
            img_src = r[0]["images"]
            cell_img = img_src[0] if img_src else ""
            logo_path = r[9]["text"] if len(r) > 9 else ""
            sheet1_map[bfile] = {
                "cell_image": cell_img,
                "logo_path": logo_path,
                "question": r[2]["text"],
                "options": [r[3]["text"], r[4]["text"], r[5]["text"], r[6]["text"]],
                "correct_answer": r[7]["text"],
                "status": r[8]["text"] if len(r) > 8 else ""
            }

    master_questions = []

    # Parse fra Sheet 2 (Den mest komplette listen med 239 spørsmål)
    seen_files = set()
    for r in s2[4:]:
        if len(r) > 6 and r[0]["text"]:
            bfile = r[0]["text"]
            q_raw = r[1]["text"]
            a1 = r[2]["text"]
            a2 = r[3]["text"]
            a3 = r[4]["text"]
            a4 = r[5]["text"]
            correct_raw = r[6]["text"]
            status = r[7]["text"] if len(r) > 7 else ""
            conf = r[8]["text"] if len(r) > 8 else ""
            stable = r[9]["text"] if len(r) > 9 else ""

            if not (q_raw and a1 and a2 and a3 and a4 and correct_raw):
                continue

            seen_files.add(bfile)
            q_clean = clean_ocr_text(q_raw)
            cat = categorize_question(q_clean)
            correct_idx = int(correct_raw) if correct_raw.isdigit() else 1

            s1_info = sheet1_map.get(bfile, {})
            m_info = meta_map.get(bfile, {})

            cell_img = s1_info.get("cell_image", "")
            # Sjekk om cell_img finnes på disk i resources
            has_cell_img = False
            cell_img_rel = ""
            if cell_img:
                local_cell = SHEET_DIR / cell_img
                if local_cell.is_file():
                    has_cell_img = True
                    cell_img_rel = str(cell_img).replace("\\", "/")

            entry = {
                "id": len(master_questions) + 1,
                "file": bfile,
                "learning_area": cat,
                "question_clean": q_clean,
                "question_raw": q_raw,
                "options": [clean_ocr_text(a1), clean_ocr_text(a2), clean_ocr_text(a3), clean_ocr_text(a4)],
                "correct_option_index": correct_idx,  # 1-indexed (1, 2, 3, 4)
                "correct_option_letter": ["A", "B", "C", "D"][correct_idx - 1] if 1 <= correct_idx <= 4 else "A",
                "cell_image": cell_img_rel,
                "has_cell_image": has_cell_img,
                "logo_path": s1_info.get("logo_path", ""),
                "status": status,
                "ocr_confidence": conf or m_info.get("ocr_confidence", ""),
                "sha256": m_info.get("sha256", ""),
                "orig_disk_path": m_info.get("orig_path", "")
            }
            master_questions.append(entry)

    # Inkluder eventuelle fra Sheet 1 som manglet i Sheet 2
    for bfile, s1_info in sheet1_map.items():
        if bfile not in seen_files:
            q_raw = s1_info["question"]
            opts = s1_info["options"]
            c_ans = s1_info["correct_answer"]
            if q_raw and len(opts) == 4 and c_ans:
                q_clean = clean_ocr_text(q_raw)
                cat = categorize_question(q_clean)
                c_idx = int(c_ans) if c_ans.isdigit() else 1
                cell_img = s1_info.get("cell_image", "")
                has_cell_img = False
                cell_img_rel = ""
                if cell_img and (SHEET_DIR / cell_img).is_file():
                    has_cell_img = True
                    cell_img_rel = str(cell_img).replace("\\", "/")

                m_info = meta_map.get(bfile, {})
                entry = {
                    "id": len(master_questions) + 1,
                    "file": bfile,
                    "learning_area": cat,
                    "question_clean": q_clean,
                    "question_raw": q_raw,
                    "options": [clean_ocr_text(opt) for opt in opts],
                    "correct_option_index": c_idx,
                    "correct_option_letter": ["A", "B", "C", "D"][c_idx - 1] if 1 <= c_idx <= 4 else "A",
                    "cell_image": cell_img_rel,
                    "has_cell_image": has_cell_img,
                    "logo_path": s1_info.get("logo_path", ""),
                    "status": s1_info.get("status", ""),
                    "ocr_confidence": m_info.get("ocr_confidence", ""),
                    "sha256": m_info.get("sha256", ""),
                    "orig_disk_path": m_info.get("orig_path", "")
                }
                master_questions.append(entry)

    # Lagre samlet masterkatalog
    dest = ROOT / "backend" / "content_packs" / "thai2drive_master_image_questions.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump({
            "total_questions": len(master_questions),
            "source_sheets": ["Bilder og spørsmål.html", "Spørsmål og fasit.html", "OCR og kilder.html"],
            "questions": master_questions
        }, f, ensure_ascii=False, indent=2)

    # Statistikk per læringsområde
    area_counts = {}
    for q in master_questions:
        area_counts[q["learning_area"]] = area_counts.get(q["learning_area"], 0) + 1

    print(f"\n🎉 Vellykket! Genererte {len(master_questions)} komplette spørsmål.")
    print(f"📁 Lagret til: {dest.relative_to(ROOT)}")
    print("\nFordeling per læringsområde:")
    for a, cnt in sorted(area_counts.items(), key=lambda x: -x[1]):
        print(f" - {a}: {cnt} spørsmål")

if __name__ == "__main__":
    main()
