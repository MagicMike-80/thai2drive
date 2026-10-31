"""Focused API checks for held questions, railway imagery, and Klar-score."""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


RAILWAY_ID = "fe7657b8-5755-495b-aefd-56b595c73194"
RAILWAY_URL = "/api/sign-images/135_0.jpg"


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    async def to_list(self, _limit):
        return self.rows


class _Questions:
    def __init__(self, railway):
        self.railway = railway
        self.pipelines = []

    async def find_one(self, query, _projection):
        return self.railway if query.get("id") == RAILWAY_ID else None

    def aggregate(self, pipeline):
        self.pipelines.append(pipeline)
        return _Cursor([])


def test_railway_image_and_held_questions_are_served_safely():
    source = {
        "id": RAILWAY_ID,
        "question": {"no": "Uten bom", "th": "ไม่มีไม้กั้น", "en": "Without barriers"},
        "options": [],
        "bildeUrl": "/api/sign-images/134_0.jpg",
    }
    questions = _Questions(source)
    with patch.object(server, "db", SimpleNamespace(questions=questions)):
        client = TestClient(server.app)
        result = client.get(f"/api/questions/{RAILWAY_ID}")
        assert result.status_code == 200
        for language in ("no", "th", "en"):
            assert result.json()["question"][language] == source["question"][language]
            assert result.json()["bildeUrl"] == RAILWAY_URL
        image = client.get(RAILWAY_URL)
        assert image.status_code == 200
        assert image.headers["content-type"] == "image/jpeg"
        for held_id in server.HELD_QUESTION_IDS:
            assert client.get(f"/api/questions/{held_id}").status_code == 404

        asyncio.run(server.get_random_questions(
            category=None, sign_id=None, count=5, has_image=True,
            mode=None, x_device_id="", user=None,
        ))
        assert questions.pipelines[0][0]["$match"]["id"]["$nin"] == list(server.HELD_QUESTION_IDS)
        asyncio.run(server._get_exam_questions(45, "", None))
        for pipeline in questions.pipelines[1:]:
            assert set(server.HELD_QUESTION_IDS).issubset(
                set(pipeline[0]["$match"]["id"]["$nin"]))


class _Attempts:
    def __init__(self):
        self.pipelines = []

    def aggregate(self, pipeline):
        self.pipelines.append(pipeline)
        if len(self.pipelines) == 1:
            return _Cursor([{"total": 50, "correct": 40}])
        return _Cursor([{"count": 3, "average_score": 82.5}])


async def _no_user(_query, _projection):
    return None


async def _zero_count(_query):
    return 0


def test_klar_score_uses_recent_full_exam_history():
    attempts = _Attempts()
    fake_db = SimpleNamespace(
        users=SimpleNamespace(find_one=_no_user),
        quiz_attempts=attempts,
        user_mistakes=SimpleNamespace(count_documents=_zero_count),
    )
    with patch.object(server, "db", fake_db):
        result = asyncio.run(server.get_user_readiness({"sub": "learner-1"}))
    assert result["exam_attempt_count"] == 3
    assert result["exam_score"] == 83
    exam_pipeline = attempts.pipelines[1]
    assert exam_pipeline[0]["$match"]["mode"] == "exam"
    assert exam_pipeline[0]["$match"]["total_questions"] == 45
    assert exam_pipeline[2]["$limit"] == 5
