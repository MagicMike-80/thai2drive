"""
migrate_glossary_forkjorsvei.py — rename the legacy glossary term
"Prioritert vei" -> "Forkjørsvei" in learning_glossary.

Idempotent and SAFE BY DEFAULT: prints what it would do and exits. Pass --apply
to actually write. Uses the document's own _id so re-runs never create dupes.

    cd thai2drive/backend && python scripts/migrate_glossary_forkjorsvei.py           # dry-run
    cd thai2drive/backend && python scripts/migrate_glossary_forkjorsvei.py --apply   # write

Cases handled:
  * No "Prioritert vei" doc            -> nothing to do (already migrated / never existed).
  * "Prioritert vei" doc, no clash     -> set term_no = "Forkjørsvei" on that _id.
  * Both docs exist                    -> deactivate the stale "Prioritert vei" doc
                                          (active=False) rather than delete, to avoid
                                          a duplicate active "Forkjørsvei".
"""

import asyncio
import os
import sys

from motor.motor_asyncio import AsyncIOMotorClient

OLD = "Prioritert vei"
NEW = "Forkjørsvei"
DB_NAME = "thai2drive"


def _mongo_url() -> str:
    url = os.environ.get("MONGO_URL", "")
    if not url:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("MONGO_URL="):
                        url = line.split("=", 1)[1].strip('"').strip("'")
                        break
    if not url:
        raise RuntimeError("MONGO_URL not found in environment or .env")
    return url


async def main(apply: bool) -> None:
    client = AsyncIOMotorClient(_mongo_url())
    db = client[DB_NAME]
    try:
        old_doc = await db.learning_glossary.find_one({"term_no": OLD})
        new_doc = await db.learning_glossary.find_one({"term_no": NEW})

        if not old_doc:
            print(f'No "{OLD}" document found — nothing to migrate.')
            if new_doc:
                print(f'  ("{NEW}" already present, id={new_doc.get("id")})')
            return

        print(f'Found "{OLD}"  _id={old_doc["_id"]}  id={old_doc.get("id")}')
        print("  definition_no:", (old_doc.get("definition_no") or "")[:80])

        if new_doc:
            action = f'"{NEW}" already exists (id={new_doc.get("id")}) -> deactivate the stale "{OLD}" doc'
            change = {"filter": {"_id": old_doc["_id"]}, "update": {"$set": {"active": False}}}
        else:
            action = f'rename term_no "{OLD}" -> "{NEW}" on _id={old_doc["_id"]}'
            change = {"filter": {"_id": old_doc["_id"]}, "update": {"$set": {"term_no": NEW}}}

        if not apply:
            print("\nDRY-RUN — would:", action)
            print("  ", change)
            print("\nRe-run with --apply to write.")
            return

        res = await db.learning_glossary.update_one(change["filter"], change["update"])
        print(f"\nAPPLIED: {action}")
        print(f"  matched={res.matched_count} modified={res.modified_count}")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main(apply="--apply" in sys.argv[1:]))
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Set MONGO_URL (or add it to backend/.env) and run this from the backend environment.")
        sys.exit(1)
