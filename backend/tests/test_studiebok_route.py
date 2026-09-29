"""
Offline route test: GET /api/studiebok must return HTTP 200 with valid JSON including `screens`.

Imports the real FastAPI app from server.py but swaps the database for an in-memory fake seeded
from the content pack, so nothing touches MongoDB or production. Startup events are not run
(TestClient is used without a context manager).

Skipped only if server.py's own dependencies are missing in the current environment.

    cd backend && python -m pytest tests/test_studiebok_route.py -v
"""

import os
import unittest

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=200")
os.environ.setdefault("DB_NAME", "t2d_route_test")

try:
    import studiebok_screens as ss
except ImportError:  # running from repo root
    from backend import studiebok_screens as ss

try:
    from fastapi.testclient import TestClient
    import server
    _IMPORT_ERROR = None
except Exception as exc:  # missing deps in this environment
    server = None
    _IMPORT_ERROR = exc


class _Cursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, key, direction=1):
        self._docs = sorted(self._docs, key=lambda d: d.get(key), reverse=direction < 0)
        return self

    async def to_list(self, length):
        return self._docs[:length]


class _Collection:
    def __init__(self, docs):
        self._docs = docs

    def find(self, query=None, projection=None):
        drop = {k for k, v in (projection or {}).items() if v == 0}
        return _Cursor([{k: v for k, v in d.items() if k not in drop} for d in self._docs])


class _FakeDb:
    def __init__(self, docs):
        self.studiebok_chapters = _Collection(docs)


@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class StudiebokRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pack = ss.load_pack()
        docs = [{
            "_id": f"oid{c['order']}", "order": c["order"], "icon": "📖",
            "title_no": f"Kapittel {c['order']}", "content_no": "<p>norsk</p>",
            "screens": c["screens"], "screen_count": len(c["screens"]),
        } for c in pack["chapters"]]
        cls._orig_db = server.db
        server.db = _FakeDb(docs)
        cls.client = TestClient(server.app)
        cls.response = cls.client.get("/api/studiebok")

    @classmethod
    def tearDownClass(cls):
        server.db = cls._orig_db

    def test_returns_http_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_body_is_valid_json_list_of_15_chapters_in_order(self):
        data = self.response.json()
        self.assertEqual([c["order"] for c in data], list(range(1, 16)))

    def test_every_returned_chapter_has_valid_screens(self):
        for ch in self.response.json():
            self.assertNotIn("_id", ch)
            self.assertEqual(ss.validate_chapter(ch), [], f"kap {ch['order']}")
            self.assertEqual(ch["screen_count"], len(ch["screens"]))


if __name__ == "__main__":
    unittest.main()
