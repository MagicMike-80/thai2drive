# -*- coding: utf-8 -*-
"""Bygger content_packs/studiebok_screens_v6.json fra content_packs/studiebok_screens_v6/src/chNN.json.

Kildefilene har kun innholdet per skjerm. Her settes id (chNN-sMM), n og de lokaliserte
merkelappene (badge_no/badge_th) for road_check og what_changed, så validerer vi hele pakken.

Bruk: cd backend && python scripts/build_studiebok_screens_v6.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from studiebok_screens import BADGES, PACK_PATH, total_screens, validate_pack  # noqa: E402

SRC = BASE / "content_packs" / "studiebok_screens_v6" / "src"


def main():
    chapters = []
    for path in sorted(SRC.glob("ch*.json")):
        ch = json.loads(path.read_text(encoding="utf-8"))
        order = ch["order"]
        for i, s in enumerate(ch["screens"], start=1):
            s["id"] = f"ch{order:02d}-s{i:02d}"
            s["n"] = i
            s.update(BADGES.get(s.get("type"), {}))
        chapters.append({"order": order, "screens": ch["screens"]})

    pack = {
        "pack": "studiebok_screens_v6",
        "collection": "studiebok_chapters",
        "description": "Læringsskjermer per Studiebok-kapittel (thai + norsk). Setter kun screens/screen_count.",
        "chapters": chapters,
    }
    errors = validate_pack(pack, check_files=True)
    print(f"Kapitler: {len(chapters)}, skjermer: {total_screens(pack)}")
    if errors:
        for e in errors:
            print("  ✗", e)
        print(f"{len(errors)} feil — pakken ble IKKE skrevet.")
        return 1
    PACK_PATH.write_text(json.dumps(pack, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Skrev {PACK_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
