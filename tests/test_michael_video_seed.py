import asyncio
import tempfile
import unittest
from pathlib import Path

from backend.michael_video_import import VIDEO_SPECS
from backend.michael_video_seed import MIGRATION_ID, seed_michael_video_catalog


class _Cursor:
    def __init__(self, docs):
        self.docs = list(docs)

    async def to_list(self, length=None):
        return self.docs[:length] if length else self.docs


class _Collection:
    def __init__(self):
        self.docs = []

    async def find_one(self, query):
        return next((doc for doc in self.docs if all(doc.get(k) == v for k, v in query.items())), None)

    def find(self, query):
        wanted = set(query.get("id", {}).get("$in", []))
        return _Cursor([doc for doc in self.docs if doc.get("id") in wanted])

    async def update_one(self, query, update, upsert=False):
        doc = await self.find_one(query)
        if doc is None:
            if not upsert:
                return
            doc = dict(query)
            self.docs.append(doc)
            doc.update(update.get("$setOnInsert", {}))
        doc.update(update.get("$set", {}))


class _Database:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, _Collection())


class MichaelVideoSeedTests(unittest.TestCase):
    def _bundle(self, root: Path):
        for spec in VIDEO_SPECS:
            for path in (
                root / spec.asset_name,
                root / "thumbs" / spec.thumbnail_name,
                root / "subtitles" / spec.subtitle_name,
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"ok")

    def test_seed_publishes_once_and_snapshots_before_upsert(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._bundle(root)
            db = _Database()
            first = asyncio.run(seed_michael_video_catalog(db, root))
            second = asyncio.run(seed_michael_video_catalog(db, root))
        self.assertEqual(first, {"status": "published", "videos": 25})
        self.assertEqual(second, {"status": "already-complete", "videos": 25})
        self.assertEqual(len(db["learning_videos"].docs), 25)
        self.assertEqual(len(db["michael_materials"].docs), 25)
        self.assertTrue(all(doc["active"] for doc in db["learning_videos"].docs))
        self.assertTrue(all(doc["approved_for_michael"] for doc in db["michael_materials"].docs))
        self.assertIsNotNone(asyncio.run(db["content_migration_snapshots"].find_one({"_id": MIGRATION_ID})))

    def test_missing_asset_fails_before_database_write(self):
        with tempfile.TemporaryDirectory() as raw:
            db = _Database()
            with self.assertRaisesRegex(RuntimeError, "Missing Michael video asset"):
                asyncio.run(seed_michael_video_catalog(db, Path(raw)))
        self.assertEqual(db.collections, {})


if __name__ == "__main__":
    unittest.main()
