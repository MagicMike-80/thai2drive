"""Build the reviewed traffic-sign catalog without touching MongoDB."""

from __future__ import annotations

import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SOURCE = BACKEND / "signs_content.json"
TRANSLATIONS = BACKEND / "sign_catalog_translations.json"
ID_RENAMES = {
    "521_0": "521_1",
    "521.1": "521_2",
    "556_0": "556_1",
    "556.2": "556_2",
    "807-10": "807_10",
}
REMOVED_IDS = {"808_42", "902_0", "904_0", "906_0", "930"}


def main() -> None:
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    assert len(records) == len(translations) == 316
    assert [row["id"] for row in records] == [row["id"] for row in translations]
    corrected = []
    for record, translation in zip(records, translations, strict=True):
        old_id = record["id"]
        if old_id in REMOVED_IDS:
            continue
        record["id"] = ID_RENAMES.get(old_id, old_id)
        record["name"] = translation["name"]
        corrected.append(record)
    ids = [row["id"] for row in corrected]
    assert len(corrected) == 311
    assert len(ids) == len(set(ids))
    SOURCE.write_text(
        json.dumps(corrected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(corrected)} corrected records to {SOURCE}")


if __name__ == "__main__":
    main()
