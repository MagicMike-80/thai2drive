"""
Isolated unit tests for User Dashboard and Student Progress in MongoDB and backend API.
Zero external network calls; Motor MongoDB is fully mocked for 100% deterministic test execution.
"""
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


class AsyncCursorMock:
    """Async cursor mock that behaves like Motor cursor with sort/limit/to_list."""
    def __init__(self, items):
        self._items = items

    def sort(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        if length is not None:
            return self._items[:length]
        return self._items


@pytest.fixture
def test_env():
    database = MagicMock()
    # Default mocks for collections
    database.users.find_one = AsyncMock(return_value=None)
    database.users.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    database.users.count_documents = AsyncMock(return_value=1)
    database.quiz_attempts.insert_one = AsyncMock()
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([]))
    database.user_mistakes.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    database.user_mistakes.find = MagicMock(return_value=AsyncCursorMock([]))
    database.user_mistakes.count_documents = AsyncMock(return_value=0)
    database.user_progress.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    database.questions.find = MagicMock(return_value=AsyncCursorMock([]))

    with patch.object(server, "db", database), \
         patch.object(server, "SEGMENT_WRITE_KEY", None):
        client = TestClient(server.app)
        yield client, database


def test_quiz_attempt_saves_and_updates_user_profile_in_mongodb(test_env):
    """Verifies that quiz attempts update quiz_attempts, user_mistakes and db.users."""
    client, database = test_env

    payload = {
        "device_id": "dev_test_1",
        "user_id": "usr_42",
        "mode": "practice",
        "category": "Right of Way",
        "total_questions": 10,
        "correct_answers": 7,
        "score_percentage": 70.0,
        "questions_answered": [
            {"question_id": "q1", "correct": True},
            {"question_id": "q2", "correct": False},
            {"question_id": "q3", "is_correct": False},
        ],
        "started_at": "2026-09-19T18:00:00Z",
    }

    response = client.post("/api/quiz-attempts", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["user_id"] == "usr_42"
    assert res_data["mode"] == "practice"

    # 1. Stored in quiz_attempts
    database.quiz_attempts.insert_one.assert_awaited_once()
    saved_attempt = database.quiz_attempts.insert_one.await_args.args[0]
    assert saved_attempt["user_id"] == "usr_42"
    assert saved_attempt["category"] == "Right of Way"

    # 2. Mistakes recorded in user_mistakes
    assert database.user_mistakes.update_one.await_count >= 2

    # 3. User profile updated in db.users
    database.users.update_one.assert_awaited_once()
    filter_arg, update_arg = database.users.update_one.await_args.args
    assert filter_arg == {"id": "usr_42"}
    assert update_arg["$inc"]["total_quizzes_completed"] == 1
    assert update_arg["$inc"]["total_questions_answered"] == 10
    assert update_arg["$inc"]["total_correct_answers"] == 7
    assert "last_quiz_completed_at" in update_arg["$set"]


def test_exam_attempt_updates_user_profile_in_mongodb(test_env):
    """Verifies that official exam attempt updates total_exams_completed and evaluation."""
    client, database = test_env

    payload = {
        "device_id": "dev_test_2",
        "user_id": "usr_exam_1",
        "mode": "exam",
        "category": "All Categories",
        "total_questions": 45,
        "correct_answers": 40,
        "score_percentage": 88.9,
        "questions_answered": [],
        "started_at": "2026-09-19T18:00:00Z",
        "completed_at": "2026-09-19T18:45:00Z",
    }

    response = client.post("/api/quiz-attempts", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["passed"] is True

    # Check that db.users was updated with exam count
    database.users.update_one.assert_awaited_once()
    _, update_arg = database.users.update_one.await_args.args
    assert update_arg["$inc"]["total_exams_completed"] == 1
    assert update_arg["$inc"]["total_quizzes_completed"] == 0


def test_dashboard_invalid_language_returns_400(test_env):
    """Language parameter must be strictly validated to no, th, en."""
    client, _ = test_env
    response = client.get("/api/user/dashboard?lang=xx")
    assert response.status_code == 400
    assert response.json()["detail"]["key"] == "invalid_language"


def test_dashboard_thai_100_percent_language_isolation(test_env):
    """Dashboard on lang=th must return 100% Thai labels and advice with zero bleed-through."""
    client, database = test_env

    # Mock user in DB
    database.users.find_one = AsyncMock(return_value={
        "id": "usr_thai",
        "email": "student@thai2drive.com",
        "full_name": "Somchai",
        "is_premium": True,
        "current_streak": 4,
        "best_streak": 7,
    })

    # Mock attempts for completed_sessions
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {
            "id": "att_1",
            "mode": "exam",
            "category": "Right of Way",
            "total_questions": 45,
            "correct_answers": 41,
            "score_percentage": 91.1,
            "passed": True,
            "completed_at": "2026-09-19T18:00:00Z",
            "duration_seconds": 2100,
        },
        {
            "id": "att_2",
            "mode": "practice",
            "category": "Traffic Signs",
            "total_questions": 10,
            "correct_answers": 6,
            "score_percentage": 60.0,
            "passed": False,
            "completed_at": "2026-09-19T17:00:00Z",
            "duration_seconds": 300,
        },
    ]))

    # Mock weak topics aggregation
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {
            "category": "Traffic Signs",
            "attempts": 2,
            "total_q": 20,
            "total_correct": 12,
            "wrong_count": 8,
            "accuracy": 60.0,
        }
    ]))

    response = client.get("/api/user/dashboard?user_id=usr_thai&lang=th")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["lang"] == "th"

    # User profile
    assert data["user"]["name"] == "Somchai"
    assert data["user"]["is_premium"] is True

    # Completed sessions: check Thai localization
    sessions = data["completed_sessions"]
    assert len(sessions) == 2
    assert sessions[0]["mode_label"] == "สอบจำลองเสมือนจริง"
    assert sessions[0]["category_name"] == "การให้ทางและกฎสิทธิ์ผ่าน"
    assert sessions[1]["mode_label"] == "ฝึกซ้อม"
    assert sessions[1]["category_name"] == "ป้ายจราจรและเครื่องหมายจราจร"

    # Weak topics: check Thai localization and advice
    weak = data["weak_topics"]
    assert len(weak) == 1
    assert weak[0]["name"] == "ป้ายจราจรและเครื่องหมายจราจร"
    assert "ครูไมเคิลแนะนำ" in weak[0]["advice"]
    # Check that no Norwegian words leak into Thai advice
    assert "Trafikklærer" not in weak[0]["advice"]
    assert "høyreregelen" not in weak[0]["advice"]

    # Readiness status in Thai
    assert any("\u0e00" <= c <= "\u0e7f" for c in data["readiness"]["status"])


def test_dashboard_norwegian_language_isolation(test_env):
    """Dashboard on lang=no must return pure Norwegian labels."""
    client, database = test_env

    database.users.find_one = AsyncMock(return_value={
        "id": "usr_no",
        "full_name": "Ola Nordmann",
        "is_premium": False,
    })

    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {
            "id": "att_no_1",
            "mode": "exam",
            "category": "Right of Way",
            "total_questions": 45,
            "correct_answers": 38,
            "score_percentage": 84.4,
            "passed": True,
            "completed_at": "2026-09-19T18:00:00Z",
        }
    ]))

    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {
            "category": "Right of Way",
            "attempts": 1,
            "total_q": 10,
            "total_correct": 5,
            "wrong_count": 5,
            "accuracy": 50.0,
        }
    ]))

    response = client.get("/api/user/dashboard?user_id=usr_no&lang=no")
    assert response.status_code == 200
    data = response.json()
    assert data["lang"] == "no"

    sessions = data["completed_sessions"]
    assert sessions[0]["mode_label"] == "Offisiell teoriprøve"
    assert sessions[0]["category_name"] == "Vikeplikt og forkjørsrett"

    weak = data["weak_topics"]
    assert weak[0]["name"] == "Vikeplikt og forkjørsrett"
    assert "Trafikklærer Michael råder" in weak[0]["advice"]


def test_dashboard_english_language_isolation(test_env):
    """Dashboard on lang=en must return pure English labels."""
    client, database = test_env

    database.users.find_one = AsyncMock(return_value={"id": "usr_en"})
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {
            "id": "att_en_1",
            "mode": "practice",
            "category": "Speed Limits",
            "total_questions": 10,
            "correct_answers": 6,
            "score_percentage": 60.0,
            "passed": False,
            "completed_at": "2026-09-19T18:00:00Z",
        }
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {
            "category": "Speed Limits",
            "attempts": 1,
            "total_q": 10,
            "total_correct": 6,
            "wrong_count": 4,
            "accuracy": 60.0,
        }
    ]))

    response = client.get("/api/user/dashboard?user_id=usr_en&lang=en")
    assert response.status_code == 200
    data = response.json()
    assert data["lang"] == "en"

    sessions = data["completed_sessions"]
    assert sessions[0]["mode_label"] == "Practice"
    assert sessions[0]["category_name"] == "Speed limits and speed adaptation"

    weak = data["weak_topics"]
    assert weak[0]["name"] == "Speed limits and speed adaptation"
    assert "Driving instructor Michael advises" in weak[0]["advice"]


def test_dashboard_unmapped_category_fails_safe(test_env):
    """An unmapped category must never leak raw DB keys to user; must fall back safely."""
    client, database = test_env

    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {
            "id": "att_unknown",
            "mode": "custom_mode_xyz",
            "category": "random_internal_db_key_999",
            "total_questions": 10,
            "correct_answers": 4,
            "score_percentage": 40.0,
            "completed_at": "2026-09-19T18:00:00Z",
        }
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {
            "category": "random_internal_db_key_999",
            "attempts": 1,
            "total_q": 10,
            "total_correct": 4,
            "wrong_count": 6,
            "accuracy": 40.0,
        }
    ]))

    # On Thai:
    resp_th = client.get("/api/user/dashboard?device_id=dev_guest&lang=th")
    assert resp_th.status_code == 200
    data_th = resp_th.json()
    # Ensure raw internal string was NOT leaked
    assert "random_internal_db_key_999" not in data_th["completed_sessions"][0]["category_name"]
    assert data_th["completed_sessions"][0]["category_name"] == "ทฤษฎีทั่วไป"
    assert data_th["completed_sessions"][0]["mode_label"] == "แบบทดสอบ"
    assert data_th["weak_topics"][0]["name"] == "ทฤษฎีทั่วไป"

    # On Norwegian:
    resp_no = client.get("/api/user/dashboard?device_id=dev_guest&lang=no")
    assert resp_no.status_code == 200
    data_no = resp_no.json()
    assert data_no["completed_sessions"][0]["category_name"] == "Generell teori"


def test_dashboard_authenticated_user_via_jwt(test_env):
    """Dashboard works seamlessly when caller provides Authorization: Bearer <jwt>."""
    client, database = test_env

    token = server.create_token(
        user_id="usr_auth_99",
        email="student99@thai2drive.com",
        is_premium=True,
    )

    database.users.find_one = AsyncMock(return_value={
        "id": "usr_auth_99",
        "email": "student99@thai2drive.com",
        "full_name": "Premium Student",
        "is_premium": True,
        "current_streak": 5,
        "best_streak": 10,
    })

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/user/dashboard?lang=th", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "usr_auth_99"
    assert data["user"]["is_authenticated"] is True
    assert data["user"]["is_premium"] is True
    assert data["streak"]["current_streak"] == 5


def test_dashboard_device_id_fallback_for_guests(test_env):
    """Guest learners can retrieve their dashboard via device_id without auth token."""
    client, database = test_env

    response = client.get("/api/user/dashboard?device_id=guest_device_abc&lang=no")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "guest_device_abc"
    assert data["user"]["is_authenticated"] is False


def test_dashboard_accessible_under_both_api_and_direct_routes(test_env):
    """Ensure both /api/user/dashboard and /user/dashboard resolve successfully."""
    client, _ = test_env
    res1 = client.get("/api/user/dashboard?device_id=d1&lang=no")
    assert res1.status_code == 200
    res2 = client.get("/user/dashboard?device_id=d1&lang=no")
    assert res2.status_code == 200
