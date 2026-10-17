"""Validate and import only the two reviewed Thai 202 text fields.

Dry-run by default. Apply requires an explicit content-approval reference,
snapshots the existing document, and compares the old values before updating.
Use Railway's environment injection; never pass credentials on the command line.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

FIELDS = ("explanation.th", "driver_action.th")
CATALOG = Path(__file__).resolve().parents[1] / "signs_content.json"


def validated_patch(source: dict, live: dict) -> dict:
    if source.get("id") != "202_0" or live.get("id") != "202_0":
        raise ValueError("Only existing sign 202_0 is allowed")
    patch = {}
    for dotted in FIELDS:
        field, lang = dotted.split(".")
        values = source.get(field)
        old = live.get(field)
        if not isinstance(values, dict) or not isinstance(old, dict):
            raise ValueError("Text fields must be localized maps")
        if any(not isinstance(values.get(key), str) or not values[key].strip() for key in ("no", "th", "en")):
            raise ValueError("Source must contain complete trilingual text")
        text = values[lang]
        if not re.search(r"[\u0e00-\u0e7f]", text) or re.search(r"[A-Za-zÆØÅæøå]", text):
            raise ValueError("Thai text must not contain foreign prose")
        if text != old.get(lang):
            patch[dotted] = text
    return patch


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approval-reference")
    args = parser.parse_args()
    if args.apply and not args.approval_reference:
        parser.error("--apply requires --approval-reference from the content owner")
    from pymongo import MongoClient
    source_bytes = CATALOG.read_bytes()
    source = next(row for row in json.loads(source_bytes) if row.get("id") == "202_0")
    db = MongoClient(os.environ["MONGO_URL"])[os.environ.get("DB_NAME") or "thai2drive"]
    live = db.traffic_signs.find_one({"id": "202_0"})
    if not live:
        raise ValueError("Existing sign 202_0 is missing; never create a replacement")
    patch = validated_patch(source, live)
    proof = {"utc": datetime.now(timezone.utc).isoformat(), "id": "202_0",
             "catalog_sha256": hashlib.sha256(source_bytes).hexdigest(),
             "fields": patch, "apply": args.apply, "approval_reference": args.approval_reference}
    if args.apply and patch:
        query = {"_id": live["_id"], **{key: live[key.split(".")[0]].get("th") for key in patch}}
        snapshot = {key: value for key, value in live.items() if key != "_id"}
        snapshot.update(run_id="sign202-thai-" + proof["utc"], snapshot_of="202_0",
                        approval_reference=args.approval_reference, source_sha256=proof["catalog_sha256"])
        db.traffic_signs_migration_snapshots.insert_one(snapshot)
        result = db.traffic_signs.update_one(query, {"$set": patch}, upsert=False)
        if result.matched_count != 1:
            raise RuntimeError("Concurrent text change; update was not applied")
        after = db.traffic_signs.find_one({"_id": live["_id"]})
        if any(after[key.split(".")[0]]["th"] != value for key, value in patch.items()):
            raise RuntimeError("Read-back did not match the approved patch")
        proof["modified_count"] = result.modified_count
    print(json.dumps(proof, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
