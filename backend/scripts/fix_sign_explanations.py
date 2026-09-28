"""Sync explanation/driver_action of selected signs from signs_content.json to MongoDB.

Dry-run is the default. --apply first copies the current documents to the
traffic_signs_migration_snapshots collection, then updates only the two text
fields. Needs MONGO_URL and DB_NAME in the environment.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

CATALOG = Path(__file__).resolve().parents[1] / "signs_content.json"
DEFAULT_IDS = ["206_0", "208_0"]
FIELDS = ("explanation", "driver_action")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ids", nargs="+", default=DEFAULT_IDS)
    args = parser.parse_args()

    catalog = {row["id"]: row for row in json.loads(CATALOG.read_text(encoding="utf-8"))}
    db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    run_id = "sign-explanations-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    changes = []
    for sign_id in args.ids:
        live = db.traffic_signs.find_one({"id": sign_id})
        if live is None or sign_id not in catalog:
            raise SystemExit(f"{sign_id}: missing in {'db' if live is None else 'catalog'}")
        for field in FIELDS:
            new = catalog[sign_id][field]
            if live.get(field) != new:
                print(f"{sign_id}.{field}:")
                print(f"  - {json.dumps(live.get(field), ensure_ascii=False)}")
                print(f"  + {json.dumps(new, ensure_ascii=False)}")
        update = {f: catalog[sign_id][f] for f in FIELDS if live.get(f) != catalog[sign_id][f]}
        if not update:
            print(f"{sign_id}: up to date")
        else:
            changes.append((live, update))

    if not args.apply:
        print("dry-run: no writes (use --apply)")
        return 0

    for live, update in changes:
        snapshot = {k: v for k, v in live.items() if k != "_id"}
        snapshot.update({"run_id": run_id, "snapshot_of": live["id"]})
        db.traffic_signs_migration_snapshots.insert_one(snapshot)
        db.traffic_signs.update_one({"id": live["id"]}, {"$set": update})
    print(f"applied {len(changes)} update(s), snapshot run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
