import asyncio
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from backend.seed_media_catalog import EXPECTED_MEDIA, load_manifest, seed_collection
from backend.media_catalog import MediaCatalogValidationError


def _manifest_item(media_id, media_type, category):
    return {
        "media_id": media_id,
        "type": media_type,
        "category": category,
        "tags": [category],
        "media_url": "https://media.example/file.mp4" if media_type == "video" else "https://media.example/file.mp3",
        "thumbnail_url": "https://media.example/thumb.jpg",
        "is_active": True,
        "content_language": "neutral",
        "i18n": {
            "no": {"title": f"NO {media_id}", "description": "NO test"},
            "th": {"title": f"TH {media_id}", "description": "TH test"},
            "en": {"title": f"EN {media_id}", "description": "EN test"},
        },
    }


class _Result:
    def __init__(self, modified_count=0, upserted_id=None):
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return list(self.docs[:length])


class _Collection:
    def __init__(self):
        self.docs = {}
        self.writes = []

    def find(self, query):
        ids = query["media_id"]["$in"]
        return _Cursor([self.docs[item] for item in ids if item in self.docs])

    async def update_one(self, query, update, upsert=False):
        media_id = query["media_id"]
        existed = media_id in self.docs
        document = dict(self.docs.get(media_id, {}))
        if not existed:
            document.update(update["$setOnInsert"])
        document.update(update["$set"])
        self.docs[media_id] = document
        self.writes.append((query, update, upsert))
        return _Result(modified_count=int(existed), upserted_id=None if existed else media_id)


class MediaCatalogSeedTests(unittest.TestCase):
    def _documents(self):
        return [
            _manifest_item(media_id, media_type, category)
            for media_id, (media_type, category) in EXPECTED_MEDIA.items()
        ]

    def test_manifest_requires_exact_ids_and_locked_type_category(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_text(json.dumps({"media": self._documents()}), encoding="utf-8")
            self.assertEqual(len(load_manifest(path)), 10)
            incomplete = self._documents()[:-1]
            path.write_text(json.dumps({"media": incomplete}), encoding="utf-8")
            with self.assertRaises(MediaCatalogValidationError):
                load_manifest(path)

    def test_seed_is_idempotent_and_never_deletes(self):
        documents = self._documents()
        collection = _Collection()
        now = datetime(2026, 8, 31, tzinfo=timezone.utc)
        first = asyncio.run(seed_collection(collection, documents, now))
        self.assertEqual(first, {"matched": 0, "modified": 0, "upserted": 10, "unchanged": 0})
        self.assertEqual(len(collection.writes), 10)
        for _, update, upsert in collection.writes:
            self.assertTrue(upsert)
            self.assertIn("$set", update)
            self.assertIn("$setOnInsert", update)
            self.assertNotIn("$unset", update)
        collection.writes.clear()
        second = asyncio.run(seed_collection(collection, documents, now))
        self.assertEqual(second, {"matched": 10, "modified": 0, "upserted": 0, "unchanged": 10})
        self.assertEqual(collection.writes, [])


if __name__ == "__main__":
    unittest.main()
