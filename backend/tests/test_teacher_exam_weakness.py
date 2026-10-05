"""Offline contract: Michael uses real quiz and exam history for weak topics."""

import asyncio
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
for directory in (ROOT, ROOT / "backend"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import backend.teacher_chat as teacher_chat


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, *args):
        return self

    def limit(self, count):
        self.rows = self.rows[:count]
        return self

    async def to_list(self, length=None):
        return self.rows[:length] if length is not None else self.rows


class _Collection:
    def __init__(self, rows=(), aggregate_rows=()):
        self.rows = list(rows)
        self.aggregate_rows = list(aggregate_rows)
        self.queries = []

    def find(self, query, *args):
        self.queries.append(query)
        return _Cursor(self.rows)

    def aggregate(self, pipeline):
        self.queries.append(pipeline[0]["$match"])
        return _Cursor(self.aggregate_rows)

    async def find_one(self, *args):
        return None

    async def insert_many(self, documents):
        self.rows.extend(documents)

    async def insert_one(self, document):
        self.rows.append(document)


def test_exam_results_20_percent_beats_stronger_ai_quiz(monkeypatch):
    database = {
        "ai_attempts": _Collection(aggregate_rows=[{"_id": "Traffic Signs", "total": 10, "correct": 8}]),
        "exam_results": _Collection(rows=[{
            "device_id": "student-1",
            "category_stats": [{"category": "Trafikkregler", "total": 10, "correct": 2}],
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    weakness = asyncio.run(teacher_chat._get_student_weakness(device_id="student-1", lang="no"))

    assert weakness["key"] == "trafikkregler"
    assert weakness["accuracy"] == 20.0
    assert "student-1" in str(database["exam_results"].queries)
    assert "student-1" in str(database["ai_attempts"].queries)


def test_real_web_exam_attempt_question_categories_are_used(monkeypatch):
    database = {
        "ai_attempts": _Collection(),
        "exam_results": _Collection(),
        "quiz_attempts": _Collection(rows=[{
            "device_id": "student-2",
            "mode": "exam",
            "category": None,
            "questions_answered": [
                {"question_obj": {"category": "Trafikkregler"}, "is_correct": i == 0}
                for i in range(5)
            ],
        }]),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    weakness = asyncio.run(teacher_chat._get_student_weakness(device_id="student-2", lang="en"))

    assert weakness["key"] == "trafikkregler"
    assert weakness["accuracy"] == 20.0
    assert weakness["name"] == "traffic rules"


def test_exam_summary_percentage_without_question_breakdown(monkeypatch):
    database = {
        "ai_attempts": _Collection(),
        "exam_results": _Collection(rows=[{
            "device_id": "student-4", "category": "Trafikkregler", "score_percentage": 20,
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    weakness = asyncio.run(teacher_chat._get_student_weakness(device_id="student-4", lang="th"))

    assert weakness["key"] == "trafikkregler"
    assert weakness["accuracy"] == 20.0
    assert weakness["name"] == "กฎจราจรและข้อบังคับพื้นฐาน"


def test_failed_exam_without_category_uses_broad_theory_topic(monkeypatch):
    database = {
        "ai_attempts": _Collection(),
        "exam_results": _Collection(rows=[{
            "device_id": "student-5", "passed": False,
            "total_questions": 45, "correct_answers": 37,
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    memory = asyncio.run(teacher_chat.fetch_student_learning_memory(device_id="student-5", lang="no"))

    assert memory["weak_topic"]["key"] == "trafikkregler"
    assert memory["weak_topic"]["has_failed_exam"] is True
    assert memory["weak_topic"]["accuracy"] > 60
    assert memory["is_returning"] is True
    assert "NY ELEV" not in teacher_chat._build_system_prompt("no", memory)
    welcome = asyncio.run(teacher_chat.teacher_welcome(lang="no", device_id="student-5"))
    assert "trafikkregler og grunnregler" in welcome["welcome"]
    assert "Hva kan jeg hjelpe" not in welcome["welcome"]


def test_low_exam_score_without_category_or_pass_flag_is_not_lost(monkeypatch):
    database = {
        "ai_attempts": _Collection(),
        "exam_results": _Collection(rows=[{
            "device_id": "student-8", "score_percentage": 20,
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    weakness = asyncio.run(teacher_chat._get_student_weakness(device_id="student-8", lang="th"))

    assert weakness["key"] == "trafikkregler"
    assert weakness["accuracy"] == 20
    assert teacher_chat._needs_topic_focus(weakness)


def test_single_wrong_ai_answer_is_visible_to_teacher(monkeypatch):
    database = {
        "ai_attempts": _Collection(aggregate_rows=[{"_id": "Stoppelengde", "total": 1, "correct": 0}]),
        "exam_results": _Collection(),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)

    weakness = asyncio.run(teacher_chat._get_student_weakness(device_id="student-6", lang="en"))

    assert weakness["key"] == "stoppelengde"
    assert weakness["accuracy"] == 0
    assert "stopping distance" in teacher_chat._weak_topic_start(weakness, "en")
    assert "junction" not in teacher_chat._weak_topic_start(weakness, "en")


def test_focus_boundary_includes_failed_exam_above_60_percent():
    assert teacher_chat._needs_topic_focus({"accuracy": 59.9})
    assert not teacher_chat._needs_topic_focus({"accuracy": 60})
    assert teacher_chat._needs_topic_focus({"accuracy": 82.2, "has_failed_exam": True})
    for question in ("Hva føler du er vanskelig?", "What do you struggle with?", "อยากฝึกเรื่องอะไรครับ?"):
        assert teacher_chat._asks_for_topic_selection(question)


def test_web_teacher_requests_resolve_a_device_id():
    source = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")
    assert "device_id: _teacherDeviceId()" in source
    assert "function _teacherDeviceId()" in source
    assert "device_id:_teacherDeviceId()" in source  # quiz-coach POST
    assert "kind === 'strengths' ? 'weak_topics'" in source


def test_web_chat_javascript_parses():
    from backend.webapp import WEBAPP_HTML

    scripts = re.findall(r"<script>(.*?)</script>", WEBAPP_HTML, re.S)
    assert scripts
    node = shutil.which("node")
    assert node, "Node is required for web chat JavaScript syntax validation"
    for script in scripts:
        result = subprocess.run([node, "--check", "-"], input=script, text=True,
                                encoding="utf-8", capture_output=True, timeout=20)
        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("lang,expected", [
    ("no", "trafikkregler og grunnregler"),
    ("th", "กฎจราจรและข้อบังคับพื้นฐาน"),
    ("en", "traffic rules"),
])
def test_local_chat_post_uses_exam_history_not_open_topic_question(monkeypatch, lang, expected):
    database = {
        "ai_attempts": _Collection(aggregate_rows=[{"_id": "Traffic Signs", "total": 10, "correct": 8}]),
        "exam_results": _Collection(rows=[{
            "device_id": "student-3",
            "category_stats": [{"category": "Trafikkregler", "total": 10, "correct": 2}],
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
        "users": _Collection(),
        "teacher_chat_logs": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)
    monkeypatch.setattr(teacher_chat, "_chat_col", _Collection())
    monkeypatch.setattr(teacher_chat, "LLM_KEY", "offline-test-key")
    monkeypatch.setattr(teacher_chat, "resolve_traffic_concept", AsyncMock(return_value=None))
    monkeypatch.setattr(teacher_chat, "_get_curriculum_context", AsyncMock(return_value=""))
    monkeypatch.setattr(teacher_chat, "_active_sign_context", AsyncMock(return_value=""))
    completion = AsyncMock(return_value=SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content="Hva føler du er vanskeligst?")
    )]))
    monkeypatch.setattr(teacher_chat, "_completion_with_fallback", completion)
    app = FastAPI()
    app.include_router(teacher_chat.teacher_router, prefix="/api")

    response = TestClient(app).post("/api/teacher/chat", json={
        "message": "Hva bør jeg øve på?", "language": lang,
        "device_id": "student-3", "mode": "weak_topics",
    })

    assert response.status_code == 200
    reply = response.json()["reply"]
    assert expected in reply
    assert "Hva føler" not in reply
    assert "?" in reply
    if lang == "th":
        assert not re.search(r"[A-Za-zÆØÅæøå]", reply)
    elif lang == "en":
        assert not re.search(r"[\u0e00-\u0e7fÆØÅæøå]", reply)
    prompt = completion.call_args.args[0][0]["content"]
    assert expected in prompt
    assert "20.0% accuracy" in prompt
    assert "Never ask what the learner feels is hardest" in prompt


def test_failed_exam_starts_normal_chat_on_subject(monkeypatch):
    database = {
        "ai_attempts": _Collection(),
        "exam_results": _Collection(rows=[{
            "device_id": "student-7", "passed": False,
            "total_questions": 45, "correct_answers": 37,
        }]),
        "quiz_attempts": _Collection(),
        "mistakes": _Collection(),
        "users": _Collection(),
        "teacher_chat_logs": _Collection(),
    }
    monkeypatch.setattr(teacher_chat, "_db", database)
    monkeypatch.setattr(teacher_chat, "_chat_col", _Collection())
    monkeypatch.setattr(teacher_chat, "LLM_KEY", "offline-test-key")
    monkeypatch.setattr(teacher_chat, "resolve_traffic_concept", AsyncMock(return_value=None))
    monkeypatch.setattr(teacher_chat, "_get_curriculum_context", AsyncMock(return_value=""))
    monkeypatch.setattr(teacher_chat, "_active_sign_context", AsyncMock(return_value=""))
    completion = AsyncMock(return_value=SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content="Hva føler du er vanskeligst?")
    )]))
    monkeypatch.setattr(teacher_chat, "_completion_with_fallback", completion)
    app = FastAPI()
    app.include_router(teacher_chat.teacher_router, prefix="/api")

    response = TestClient(app).post("/api/teacher/chat", json={
        "message": "Hei Michael", "language": "no",
        "device_id": "student-7", "mode": "normal_chat",
    })

    assert response.status_code == 200
    assert "trafikkregler og grunnregler" in response.json()["reply"]
    assert "Hva føler" not in response.json()["reply"]
    assert "Hva ser du etter når du nærmer deg et kryss?" in response.json()["reply"]
