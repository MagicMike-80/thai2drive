"""
Dry-run audit for Thai2Drive traffic sign image/title mapping.

Reads only local files:
- backend/sign_images/
- backend/signs_content.json
- backend/generate_signs_content.py

No MongoDB writes. No production writes. No frontend changes.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SIGN_IMAGES_DIR = ROOT / "backend" / "sign_images"
SIGNS_CONTENT = ROOT / "backend" / "signs_content.json"
GENERATOR = ROOT / "backend" / "generate_signs_content.py"

# These are visual checks confirmed manually from the local committed image files.
# The script is intentionally conservative: it does not claim computer vision.
KNOWN_VISUAL_EXPECTATIONS = {
    "206_0": "Slutt på forkjørsveg",
    "208_0": "Forkjørsveg",
    "214_0": "Forkjørsrett over møtende trafikk",
    "126_0": "Rundkjøring / rundkjøring foran",
}

SUGGESTED_ACTIONS = {
    "206_0": "Mismatch: image appears to be end of priority road, but data says railway crossing. Move/rename image or correct sign record after choosing canonical sign IDs.",
    "208_0": "Image/title appear close, but name should be canonical: Forkjørsveg / Priority Road, not generic Forkjørsrett.",
    "214_0": "Mismatch: image appears to be priority over oncoming traffic, but data says end of priority road. Reassign image/content to correct sign ID.",
    "126_0": "Mismatch: image appears to be roundabout warning, but data says railway crossing. Reassign image/content to correct warning sign ID.",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_sign_data(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SIGN_DATA":
                    return ast.literal_eval(node.value)
    return {}


def _sign_id_from_image(filename: str) -> str:
    match = re.match(r"^(\d+(?:[.-]\d+|_(?:\d+[A-Za-z]*|[A-Z]+(?:\d+)?)(?=$|_))?)", Path(filename).stem)
    return match.group(1) if match else ""


def _title_no(record: dict[str, Any] | None) -> str:
    if not record:
        return ""
    name = record.get("name") or {}
    return str(name.get("no") or "")


def _find_image_files() -> dict[str, list[str]]:
    files: dict[str, list[str]] = {}
    for path in sorted(SIGN_IMAGES_DIR.glob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        sign_id = _sign_id_from_image(path.name)
        if sign_id:
            files.setdefault(sign_id, []).append(path.name)
    return files


def _status(current_title: str, expected_title: str) -> str:
    if not expected_title:
        return "review"
    if current_title.strip().casefold() == expected_title.strip().casefold():
        return "ok"
    if expected_title.casefold() in current_title.casefold() or current_title.casefold() in expected_title.casefold():
        return "near-match"
    return "mismatch"


def _md_row(values: list[str]) -> str:
    escaped = [v.replace("|", "\\|").replace("\n", " ") for v in values]
    return "| " + " | ".join(escaped) + " |"


def main() -> int:
    signs = {str(item.get("id")): item for item in _read_json(SIGNS_CONTENT)}
    generated = _extract_sign_data(GENERATOR)
    image_files = _find_image_files()

    rows: list[list[str]] = []

    for sign_id, expected_title in KNOWN_VISUAL_EXPECTATIONS.items():
        record = signs.get(sign_id)
        current_title = _title_no(record) or "<missing in signs_content.json>"
        generator_title = _title_no(generated.get(sign_id)) or "<missing in SIGN_DATA>"
        images = ", ".join(image_files.get(sign_id, [])) or "<missing image file>"
        rows.append([
            sign_id,
            current_title,
            images,
            expected_title,
            _status(current_title, expected_title),
            generator_title,
            SUGGESTED_ACTIONS.get(sign_id, "Review image/title mapping."),
        ])

    missing_images = sorted(sign_id for sign_id in signs if sign_id not in image_files)
    missing_content = sorted(sign_id for sign_id in image_files if sign_id not in signs)
    generator_diffs = []
    for sign_id, record in signs.items():
        generated_record = generated.get(sign_id)
        if not generated_record:
            continue
        if _title_no(record) != _title_no(generated_record):
            generator_diffs.append((sign_id, _title_no(record), _title_no(generated_record)))

    duplicate_titles: dict[str, list[str]] = {}
    for sign_id, record in signs.items():
        title = _title_no(record).strip()
        if title:
            duplicate_titles.setdefault(title, []).append(sign_id)
    duplicate_titles = {title: ids for title, ids in duplicate_titles.items() if len(ids) > 1}

    print("# Traffic Sign Image/Title Mapping Dry-Run Audit")
    print()
    print("No MongoDB writes. No production writes. Local files inspected only.")
    print()
    print(_md_row(["sign_id", "current title_no", "image file", "visual expected title", "status", "generator title_no", "suggested action"]))
    print(_md_row(["---", "---", "---", "---", "---", "---", "---"]))
    for row in rows:
        print(_md_row(row))

    print()
    print("## General Integrity Summary")
    print(f"- signs_content records: {len(signs)}")
    print(f"- image IDs found: {len(image_files)}")
    print(f"- records missing local image file: {len(missing_images)}")
    print(f"- local image IDs missing signs_content record: {len(missing_content)}")
    print(f"- signs_content vs SIGN_DATA title diffs: {len(generator_diffs)}")
    print(f"- duplicate Norwegian titles: {len(duplicate_titles)}")

    if missing_images:
        print("\n## Records Missing Local Image File")
        for sign_id in missing_images[:80]:
            print(f"- {sign_id}: {_title_no(signs.get(sign_id))}")
        if len(missing_images) > 80:
            print(f"- ... {len(missing_images) - 80} more")

    if missing_content:
        print("\n## Local Image IDs Missing signs_content.json")
        for sign_id in missing_content[:80]:
            print(f"- {sign_id}: {', '.join(image_files[sign_id])}")
        if len(missing_content) > 80:
            print(f"- ... {len(missing_content) - 80} more")

    if duplicate_titles:
        print("\n## Duplicate Norwegian Titles")
        for title, ids in sorted(duplicate_titles.items())[:80]:
            print(f"- {title}: {', '.join(ids)}")
        if len(duplicate_titles) > 80:
            print(f"- ... {len(duplicate_titles) - 80} more")

    if generator_diffs:
        print("\n## signs_content.json vs generate_signs_content.py Title Differences")
        for sign_id, content_title, generator_title in generator_diffs[:80]:
            print(f"- {sign_id}: signs_content='{content_title}' | SIGN_DATA='{generator_title}'")
        if len(generator_diffs) > 80:
            print(f"- ... {len(generator_diffs) - 80} more")

    print("\n## Suggested Minimal Correction Plan")
    print("1. Pick one canonical sign ID system before changing data.")
    print("2. Fix generate_signs_content.py first so regenerated content cannot reintroduce the mismatch.")
    print("3. Update signs_content.json from the corrected source.")
    print("4. Reassign or rename the affected image files so image_url, sign_id, and title agree.")
    print("5. Run this audit again, then use the safe import pipeline with dry-run/backups before MongoDB changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


