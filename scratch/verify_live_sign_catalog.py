"""Independent read-only verification of the live traffic-sign catalog."""

import json
import os
import sys
from pathlib import Path

from pymongo import MongoClient


root = Path(sys.argv[1])
catalog = json.loads((root / "backend" / "signs_content.json").read_text(encoding="utf-8"))
ids = {row["id"] for row in catalog}
images = {}
for path in (root / "backend" / "sign_images").glob("*.jpg"):
    matches = [sign_id for sign_id in ids if path.stem == sign_id or path.stem.startswith(sign_id + "_")]
    if len(matches) == 1:
        images[matches[0]] = f"/api/sign-images/{path.name}"

db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
docs = list(db.traffic_signs.find({}))
by_id = {row.get("id"): row for row in docs}
audio_keys = {"audio", "audio_url", "sound_url", "tts"}
errors = []
if len(docs) != 311 or len(by_id) != 311 or set(by_id) != ids:
    errors.append("ID/count mismatch")
for row in catalog:
    live = by_id.get(row["id"], {})
    if live.get("name") != row["name"]:
        errors.append(f"{row['id']}: name")
    if live.get("image_url") != images.get(row["id"]):
        errors.append(f"{row['id']}: image_url")
    if audio_keys.intersection(live):
        errors.append(f"{row['id']}: audio")
indexes = db.traffic_signs.index_information()
unique_id_index = any(info.get("unique") and info.get("key") == [("id", 1)] for info in indexes.values())
if not unique_id_index:
    errors.append("missing unique id index")
run_id = "sign-catalog-20260923T183247Z"
snapshot_count = db.traffic_signs_migration_snapshots.count_documents({"run_id": run_id})
if snapshot_count != 340:
    errors.append(f"snapshot count {snapshot_count}")
stats = db.command("dbStats", scale=1048576)
report = {
    "database": os.environ["DB_NAME"],
    "active_signs": len(docs),
    "unique_ids": len(by_id),
    "name_matches": sum(by_id.get(row["id"], {}).get("name") == row["name"] for row in catalog),
    "image_url_matches": sum(by_id.get(row["id"], {}).get("image_url") == images.get(row["id"]) for row in catalog),
    "audio_references": sum(bool(audio_keys.intersection(row)) for row in docs),
    "unique_id_index": unique_id_index,
    "migration_snapshot_documents": snapshot_count,
    "database_logical_mb": stats.get("dataSize"),
    "errors": errors,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
