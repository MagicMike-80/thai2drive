"""Isolated API tests backed by an in-memory Mongo-compatible test double.

These tests must never make requests to the production website or mutate its
database. The FastAPI routes run locally with a fresh fake database per test.
"""
from __future__ import annotations

import copy
import random
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
for directory in (ROOT, BACKEND_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import server


TEST_DEVICE_ID = "test_device_thai2drive_123"
CATEGORIES = [
    "Traffic Signs", "Road Rules", "Right of Way", "Speed Limits", "Safety",
    "Driving Conditions", "Road Conditions", "Situations", "Traffic Rules",
]


def _matches(document, query):
    for key, value in (query or {}).items():
        if key == "$or":
            if not any(_matches(document, branch) for branch in value):
                return False
        elif isinstance(value, dict) and "$in" in value:
            if document.get(key) not in value["$in"]:
                return False
        elif document.get(key) != value:
            return False
    return True


class _Cursor:
    def __init__(self, documents):
        self.documents = list(documents)

    def sort(self, key, direction=None):
        if isinstance(key, list):
            for field, order in reversed(key):
                self.documents.sort(key=lambda item: item.get(field, ""), reverse=order < 0)
        else:
            self.documents.sort(key=lambda item: item.get(key, ""), reverse=direction == -1)
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    async def to_list(self, length=None):
        values = self.documents[:length] if length is not None else self.documents
        return copy.deepcopy(values)


class _Collection:
    def __init__(self, documents=None):
        self.documents = copy.deepcopy(documents or [])

    async def count_documents(self, query):
        return sum(_matches(item, query) for item in self.documents)

    async def insert_one(self, document):
        self.documents.append(copy.deepcopy(document))

    async def insert_many(self, documents):
        self.documents.extend(copy.deepcopy(list(documents)))

    async def find_one(self, query, projection=None):
        found = next((item for item in self.documents if _matches(item, query)), None)
        return copy.deepcopy(found)

    def find(self, query=None, projection=None):
        return _Cursor(item for item in self.documents if _matches(item, query or {}))

    def aggregate(self, pipeline):
        rows = copy.deepcopy(self.documents)
        for stage in pipeline:
            if "$match" in stage:
                rows = [item for item in rows if _matches(item, stage["$match"])]
            elif "$sample" in stage:
                rows = random.sample(rows, min(len(rows), stage["$sample"]["size"]))
            elif "$project" in stage and stage["$project"].get("_id") == 0:
                rows = [{key: value for key, value in item.items() if key != "_id"} for item in rows]
            elif "$group" in stage:
                group_spec = stage["$group"]
                field = group_spec["_id"].removeprefix("$")
                counts = {}
                for item in rows:
                    key = item.get(field)
                    counts[key] = counts.get(key, 0) + 1
                rows = [
                    {"_id": key, "count": count}
                    for key, count in counts.items()
                ]
            elif "$sort" in stage:
                key, order = next(iter(stage["$sort"].items()))
                rows.sort(key=lambda item: item.get(key) or "", reverse=order < 0)
        return _Cursor(rows)

    async def update_one(self, query, update, upsert=False):
        document = next((item for item in self.documents if _matches(item, query)), None)
        if document is None and upsert:
            document = {k: v for k, v in query.items() if not k.startswith("$")}
            self.documents.append(document)
        if document is not None:
            document.update(copy.deepcopy(update.get("$set", {})))
            for key, value in update.get("$inc", {}).items():
                document[key] = document.get(key, 0) + value
            for key, value in update.get("$setOnInsert", {}).items():
                document.setdefault(key, value)

    async def delete_one(self, query):
        for index, item in enumerate(self.documents):
            if _matches(item, query):
                del self.documents[index]
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()


class _Database:
    def __init__(self, questions=None):
        self.collections = {"questions": _Collection(questions)}

    def __getitem__(self, name):
        return self.collections.setdefault(name, _Collection())

    def __getattr__(self, name):
        return self[name]


def _question_fixture():
    questions = []
    for category in CATEGORIES:
        for index in range(5):
            questions.append({
                "id": f"{category.lower().replace(' ', '-')}-{index}",
                "question": {"no": "Norsk spørsmål", "th": "คำถามภาษาไทย", "en": "English question"},
                "options": [
                    {"id": key, "text": {"no": f"Svar {key}", "th": f"คำตอบ {key}", "en": f"Answer {key}"}}
                    for key in ("A", "B", "C", "D")
                ],
                "correctOptionId": "A",
                "explanation": {"no": "Forklaring", "th": "คำอธิบาย", "en": "Explanation"},
                "category": category,
                "difficulty": "medium",
                "bildeUrl": f"/static/test/{category}-{index}.png",
                "active": True,
            })
    return questions


@pytest.fixture
def api(monkeypatch):
    database = _Database(_question_fixture())
    monkeypatch.setattr(server, "db", database)
    # Do not enter the TestClient context manager: these route tests need no
    # application startup hooks or real database/network connections.
    return TestClient(server.app), database


class TestDatabaseSeeding:
    def test_seed_database(self, api):
        client, database = api
        database.questions.documents.clear()

        response = client.post("/api/seed")

        assert response.status_code == 200
        data = response.json()
        assert data["seeded"] is True
        assert "Seeded 45 questions" in data["message"]
        assert len(database.questions.documents) == 45


class TestCategories:
    def test_get_categories_returns_9_categories(self, api):
        client, _ = api
        response = client.get("/api/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert {item["name"] for item in categories} == set(CATEGORIES)
        assert all(item["count"] == 5 for item in categories)


class TestQuestions:
    def test_get_random_questions_count_10(self, api):
        client, _ = api
        response = client.get("/api/questions/random", params={"count": 10})
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 10
        for question in questions:
            assert {"id", "question", "correctOptionId", "category"} <= question.keys()
            assert {"no", "th", "en"} <= question["question"].keys()
            assert question["correctOptionId"] in {"A", "B", "C", "D"}

    def test_get_random_questions_with_category(self, api):
        client, _ = api
        response = client.get("/api/questions/random", params={"count": 5, "category": "Safety"})
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 5
        assert all(question["category"] == "Safety" for question in questions)


class TestProgress:
    def test_get_progress_creates_new_if_not_exists(self, api):
        client, _ = api
        response = client.get(f"/api/progress/{TEST_DEVICE_ID}")
        assert response.status_code == 200
        progress = response.json()
        assert progress["device_id"] == TEST_DEVICE_ID
        assert progress["total_questions_answered"] == 0
        assert progress["correct_answers"] == 0
        assert progress["questions_by_category"] == {}

    def test_update_progress_correct_answer(self, api):
        client, _ = api
        response = client.put(f"/api/progress/{TEST_DEVICE_ID}", params={"answered_correct": "true", "category": "Safety"})
        assert response.status_code == 200
        progress = client.get(f"/api/progress/{TEST_DEVICE_ID}").json()
        assert progress["total_questions_answered"] == 1
        assert progress["correct_answers"] == 1
        assert progress["questions_by_category"]["Safety"] == {"answered": 1, "correct": 1}

    def test_update_progress_incorrect_answer(self, api):
        client, _ = api
        client.put(f"/api/progress/{TEST_DEVICE_ID}", params={"answered_correct": "false", "category": "Road Rules"})
        progress = client.get(f"/api/progress/{TEST_DEVICE_ID}").json()
        assert progress["total_questions_answered"] == 1
        assert progress["correct_answers"] == 0
        assert progress["questions_by_category"]["Road Rules"] == {"answered": 1, "correct": 0}


class TestBookmarks:
    def test_create_bookmark(self, api):
        client, _ = api
        question_id = client.get("/api/questions/random", params={"count": 1}).json()[0]["id"]
        response = client.post("/api/bookmarks", json={"device_id": TEST_DEVICE_ID, "question_id": question_id})
        assert response.status_code == 200
        assert response.json()["device_id"] == TEST_DEVICE_ID
        assert response.json()["question_id"] == question_id
        assert response.json()["id"]

    def test_get_bookmarks(self, api):
        client, _ = api
        client.post("/api/bookmarks", json={"device_id": TEST_DEVICE_ID, "question_id": "safety-0"})
        response = client.get(f"/api/bookmarks/{TEST_DEVICE_ID}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["question_id"] == "safety-0"

    def test_get_bookmarked_questions(self, api):
        client, _ = api
        client.post("/api/bookmarks", json={"device_id": TEST_DEVICE_ID, "question_id": "safety-0"})
        response = client.get(f"/api/bookmarked-questions/{TEST_DEVICE_ID}")
        assert response.status_code == 200
        assert [question["id"] for question in response.json()] == ["safety-0"]
        assert "correctOptionId" in response.json()[0]


class TestQuizAttempts:
    def test_save_quiz_attempt(self, api):
        client, _ = api
        response = client.post("/api/quiz-attempts", json={
            "device_id": TEST_DEVICE_ID, "mode": "practice", "category": "Safety",
            "total_questions": 10, "correct_answers": 7, "score_percentage": 70.0,
            "questions_answered": [], "started_at": "2026-01-01T10:00:00Z",
        })
        assert response.status_code == 200, response.text
        attempt = response.json()
        assert attempt["device_id"] == TEST_DEVICE_ID
        assert attempt["mode"] == "practice"
        assert attempt["score_percentage"] == 70.0
        assert attempt["id"]

    def test_get_quiz_attempts(self, api):
        client, _ = api
        client.post("/api/quiz-attempts", json={
            "device_id": TEST_DEVICE_ID, "mode": "practice", "total_questions": 10,
            "correct_answers": 7, "score_percentage": 70.0, "questions_answered": [],
            "started_at": "2026-01-01T10:00:00Z",
        })
        response = client.get(f"/api/quiz-attempts/{TEST_DEVICE_ID}", params={"limit": 20})
        assert response.status_code == 200
        attempts = response.json()
        assert len(attempts) == 1
        assert {"id", "mode", "score_percentage", "completed_at"} <= attempts[0].keys()


class TestExamMode:
    def test_exam_mode_45_questions(self, api):
        client, _ = api
        response = client.get("/api/questions/random", params={"count": 45})
        assert response.status_code == 200
        assert len(response.json()) == 45

    def test_exam_attempt_with_pass_status(self, api):
        client, _ = api
        response = client.post("/api/quiz-attempts", json={
            "device_id": TEST_DEVICE_ID, "mode": "exam", "total_questions": 45,
            "correct_answers": 40, "score_percentage": 88.89, "passed": True,
            "questions_answered": [], "started_at": "2026-01-01T11:00:00Z",
        })
        assert response.status_code == 200, response.text
        assert response.json()["passed"] is True
        assert response.json()["score_percentage"] == pytest.approx(88.9)
