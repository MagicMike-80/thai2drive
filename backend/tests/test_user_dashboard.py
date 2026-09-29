"""
Isolated unit tests for User Dashboard and Student Progress in MongoDB and backend API.
Zero external network calls; Motor MongoDB is fully mocked for 100% deterministic test execution.

SECURITY (2026-09-29): GET /api/user/dashboard used to accept a free `user_id`/`device_id` query
parameter and return that identity's email, name, premium status and quiz history without any
login (IDOR). It now requires a valid JWT; identity comes only from the token, never from the
URL. Free users get a summary only (weak_topics/completed_sessions come back empty, with an
upgrade prompt); the detailed breakdown — including Studiebok progress and sign mastery — is a
paid feature. See backend/dashboard.py.
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

    def __aiter__(self):
        return iter(self._items)


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
    database.user_studybook_progress.find_one = AsyncMock(return_value=None)
    database.studiebok_chapters.find = MagicMock(return_value=AsyncCursorMock([]))
    database.questions.find = MagicMock(return_value=AsyncCursorMock([]))

    with patch.object(server, "db", database), \
         patch.object(server, "SEGMENT_WRITE_KEY", None):
        client = TestClient(server.app)
        yield client, database


def auth_header(uid="usr_1", email="u@example.com", is_premium=False):
    token = server.create_token(uid, email, is_premium=is_premium)
    return {"Authorization": f"Bearer {token}"}


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


# ══════════════════════════════════════════════════════════════════════════════
#  Security: JWT required, no free-form identity parameters
# ══════════════════════════════════════════════════════════════════════════════
def test_dashboard_requires_login(test_env):
    client, _ = test_env
    assert client.get("/api/user/dashboard").status_code == 401
    assert client.get("/api/user/dashboard", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_user_id_query_parameter_no_longer_selects_another_identity(test_env):
    """The old IDOR: ?user_id=<anyone> used to return that person's data without a token."""
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "usr_me", "email": "me@example.com"})
    r = client.get("/api/user/dashboard?user_id=usr_someone_else", headers=auth_header("usr_me"))
    assert r.status_code == 200
    assert r.json()["user"]["id"] == "usr_me"   # the query parameter is simply not read


def test_device_id_query_parameter_no_longer_selects_another_identity(test_env):
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "usr_me", "email": "me@example.com"})
    r = client.get("/api/user/dashboard?device_id=some_other_device", headers=auth_header("usr_me"))
    assert r.status_code == 200
    assert r.json()["user"]["id"] == "usr_me"


def test_unauthenticated_device_id_only_access_is_rejected(test_env):
    """The former guest-via-device_id path (no token at all) must now be a 401, not a 200."""
    client, _ = test_env
    assert client.get("/api/user/dashboard?device_id=guest_device_abc&lang=no").status_code == 401


def test_deleted_user_token_is_rejected(test_env):
    client, database = test_env
    database.users.find_one = AsyncMock(return_value=None)
    assert client.get("/api/user/dashboard", headers=auth_header("ghost")).status_code == 401


def test_route_accessible_under_both_api_and_direct_paths_with_auth(test_env):
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "d1", "email": "d1@example.com"})
    headers = auth_header("d1")
    assert client.get("/api/user/dashboard?lang=no", headers=headers).status_code == 200
    assert client.get("/user/dashboard?lang=no", headers=headers).status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  Free vs. premium: summary only vs. full breakdown
# ══════════════════════════════════════════════════════════════════════════════
def test_dashboard_invalid_language_returns_400(test_env):
    """Language parameter must be strictly validated to no, th, en."""
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "usr_1"})
    response = client.get("/api/user/dashboard?lang=xx", headers=auth_header("usr_1"))
    assert response.status_code == 400
    assert response.json()["detail"]["key"] == "invalid_language"


def test_free_user_gets_a_summary_and_an_upgrade_prompt_not_the_detail(test_env):
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "usr_free", "is_premium": False})
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {"id": "a1", "mode": "practice", "category": "Traffic Signs", "total_questions": 10,
         "correct_answers": 6, "score_percentage": 60.0, "completed_at": "2026-09-19T18:00:00Z"},
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "Traffic Signs", "attempts": 1, "total_q": 10, "total_correct": 6, "wrong_count": 4, "accuracy": 60.0},
    ]))
    r = client.get("/api/user/dashboard?lang=no", headers=auth_header("usr_free"))
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["is_premium"] is False
    assert data["weak_topics"] == []
    assert data["completed_sessions"] == []
    assert data["signs"] is None
    assert set(data["locked"]) == {"quiz_by_category", "studybook_chapters", "signs"}
    assert data["upgrade"] == {"show_button": True, "gate": "upgrade"}
    # ... but the summary numbers are still real
    assert data["stats"]["total_questions"] == 10
    assert "chapters" not in data["studybook"]


def test_premium_user_gets_the_full_breakdown(test_env):
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={
        "id": "usr_prem", "email": "prem@example.com", "full_name": "Premium Student",
        "is_premium": True, "current_streak": 5, "best_streak": 10,
    })
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {"id": "att_1", "mode": "exam", "category": "Right of Way", "total_questions": 45,
         "correct_answers": 41, "score_percentage": 91.1, "passed": True,
         "completed_at": "2026-09-19T18:00:00Z", "duration_seconds": 2100},
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "Right of Way", "attempts": 1, "total_q": 45, "total_correct": 41, "wrong_count": 4, "accuracy": 91.1},
    ]))
    database.studiebok_chapters.find = MagicMock(return_value=AsyncCursorMock([
        {"order": 1, "screens": [{"id": "s1"}, {"id": "s2"}]},
    ]))
    r = client.get("/api/user/dashboard?lang=th", headers=auth_header("usr_prem"))
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["is_premium"] is True
    assert data["user"]["is_authenticated"] is True
    assert len(data["completed_sessions"]) == 1
    assert data["locked"] == []
    assert data["upgrade"] == {"show_button": False}
    assert data["streak"]["current_streak"] == 5
    assert "chapters" in data["studybook"]
    assert data["signs"] is not None
    assert data["signs"]["catalog_total"] >= 0


def test_database_tier_wins_over_a_stale_jwt_claim(test_env):
    """A token minted while premium was active must not grant the full view once the DB says no."""
    client, database = test_env
    database.users.find_one = AsyncMock(return_value={"id": "usr_lapsed", "is_premium": False})
    token = server.create_token("usr_lapsed", "l@example.com", is_premium=True)
    r = client.get("/api/user/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["user"]["is_premium"] is False
    assert r.json()["upgrade"]["show_button"] is True


# ══════════════════════════════════════════════════════════════════════════════
#  Language isolation (unchanged behaviour, now reached via a valid token)
# ══════════════════════════════════════════════════════════════════════════════
def test_dashboard_thai_100_percent_language_isolation(test_env):
    """Dashboard on lang=th must return 100% Thai labels and advice with zero bleed-through."""
    client, database = test_env

    database.users.find_one = AsyncMock(return_value={
        "id": "usr_thai",
        "email": "student@thai2drive.com",
        "full_name": "Somchai",
        "is_premium": True,
        "current_streak": 4,
        "best_streak": 7,
    })

    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {
            "id": "att_1", "mode": "exam", "category": "Right of Way", "total_questions": 45,
            "correct_answers": 41, "score_percentage": 91.1, "passed": True,
            "completed_at": "2026-09-19T18:00:00Z", "duration_seconds": 2100,
        },
        {
            "id": "att_2", "mode": "practice", "category": "Traffic Signs", "total_questions": 10,
            "correct_answers": 6, "score_percentage": 60.0, "passed": False,
            "completed_at": "2026-09-19T17:00:00Z", "duration_seconds": 300,
        },
    ]))

    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "Traffic Signs", "attempts": 2, "total_q": 20, "total_correct": 12, "wrong_count": 8, "accuracy": 60.0}
    ]))

    response = client.get("/api/user/dashboard?lang=th", headers=auth_header("usr_thai"))
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["lang"] == "th"

    assert data["user"]["name"] == "Somchai"
    assert data["user"]["is_premium"] is True

    sessions = data["completed_sessions"]
    assert len(sessions) == 2
    assert sessions[0]["mode_label"] == "สอบจำลองเสมือนจริง"
    assert sessions[0]["category_name"] == "การให้ทางและกฎสิทธิ์ผ่าน"
    assert sessions[1]["mode_label"] == "ฝึกซ้อม"
    assert sessions[1]["category_name"] == "ป้ายจราจรและเครื่องหมายจราจร"

    weak = data["weak_topics"]
    assert len(weak) == 1
    assert weak[0]["name"] == "ป้ายจราจรและเครื่องหมายจราจร"
    assert "ครูไมเคิลแนะนำ" in weak[0]["advice"]
    assert "Trafikklærer" not in weak[0]["advice"]
    assert "høyreregelen" not in weak[0]["advice"]

    assert any("฀" <= c <= "๿" for c in data["readiness"]["status"])


def test_dashboard_norwegian_language_isolation(test_env):
    """Dashboard on lang=no must return pure Norwegian labels."""
    client, database = test_env

    database.users.find_one = AsyncMock(return_value={
        "id": "usr_no", "full_name": "Ola Nordmann", "is_premium": True,
    })

    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {"id": "att_no_1", "mode": "exam", "category": "Right of Way", "total_questions": 45,
         "correct_answers": 38, "score_percentage": 84.4, "passed": True, "completed_at": "2026-09-19T18:00:00Z"}
    ]))

    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "Right of Way", "attempts": 1, "total_q": 10, "total_correct": 5, "wrong_count": 5, "accuracy": 50.0}
    ]))

    response = client.get("/api/user/dashboard?lang=no", headers=auth_header("usr_no"))
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

    database.users.find_one = AsyncMock(return_value={"id": "usr_en", "is_premium": True})
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {"id": "att_en_1", "mode": "practice", "category": "Speed Limits", "total_questions": 10,
         "correct_answers": 6, "score_percentage": 60.0, "passed": False, "completed_at": "2026-09-19T18:00:00Z"}
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "Speed Limits", "attempts": 1, "total_q": 10, "total_correct": 6, "wrong_count": 4, "accuracy": 60.0}
    ]))

    response = client.get("/api/user/dashboard?lang=en", headers=auth_header("usr_en"))
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

    database.users.find_one = AsyncMock(return_value={"id": "usr_unmapped", "is_premium": True})
    database.quiz_attempts.find = MagicMock(return_value=AsyncCursorMock([
        {"id": "att_unknown", "mode": "custom_mode_xyz", "category": "random_internal_db_key_999",
         "total_questions": 10, "correct_answers": 4, "score_percentage": 40.0, "completed_at": "2026-09-19T18:00:00Z"}
    ]))
    database.quiz_attempts.aggregate = MagicMock(return_value=AsyncCursorMock([
        {"category": "random_internal_db_key_999", "attempts": 1, "total_q": 10, "total_correct": 4, "wrong_count": 6, "accuracy": 40.0}
    ]))

    resp_th = client.get("/api/user/dashboard?lang=th", headers=auth_header("usr_unmapped"))
    assert resp_th.status_code == 200
    data_th = resp_th.json()
    assert "random_internal_db_key_999" not in data_th["completed_sessions"][0]["category_name"]
    assert data_th["completed_sessions"][0]["category_name"] == "ทฤษฎีทั่วไป"
    assert data_th["completed_sessions"][0]["mode_label"] == "แบบทดสอบ"
    assert data_th["weak_topics"][0]["name"] == "ทฤษฎีทั่วไป"

    resp_no = client.get("/api/user/dashboard?lang=no", headers=auth_header("usr_unmapped"))
    assert resp_no.status_code == 200
    assert resp_no.json()["completed_sessions"][0]["category_name"] == "Generell teori"
