"""Isolated unit tests for the Exam Simulator domain logic and language purity."""

import re
import pytest
from exam_logic import (
    EXAM_TOTAL_QUESTIONS,
    EXAM_TIME_LIMIT_SECONDS,
    EXAM_MAX_ERRORS,
    EXAM_PASS_THRESHOLD,
    evaluate_exam_attempt,
    generate_michael_exam_prompt,
)


class TestExamSimulatorRules:
    def test_exam_constants(self):
        """Verify official theory test parameters (Statens vegvesen rules)."""
        assert EXAM_TOTAL_QUESTIONS == 45
        assert EXAM_TIME_LIMIT_SECONDS == 5400  # 90 minutes
        assert EXAM_MAX_ERRORS == 7
        assert EXAM_PASS_THRESHOLD == 38  # 45 - 7

    def test_evaluate_exam_pass_threshold_exact_38(self):
        """Exactly 38 correct out of 45 (7 errors) must pass."""
        res = evaluate_exam_attempt(total_questions=45, correct_answers=38, duration_seconds=3000)
        assert res["passed"] is True
        assert res["errors"] == 7
        assert res["correct_answers"] == 38
        assert res["timed_out"] is False
        assert pytest.approx(res["score_percentage"], 0.1) == 84.4

    def test_evaluate_exam_fail_threshold_37(self):
        """37 correct out of 45 (8 errors) must fail."""
        res = evaluate_exam_attempt(total_questions=45, correct_answers=37, duration_seconds=3000)
        assert res["passed"] is False
        assert res["errors"] == 8
        assert res["correct_answers"] == 37
        assert res["timed_out"] is False
        assert pytest.approx(res["score_percentage"], 0.1) == 82.2

    def test_evaluate_exam_perfect_score(self):
        """45 correct out of 45 (0 errors) must pass."""
        res = evaluate_exam_attempt(total_questions=45, correct_answers=45, duration_seconds=1200)
        assert res["passed"] is True
        assert res["errors"] == 0
        assert res["score_percentage"] == 100.0
        assert res["timed_out"] is False

    def test_evaluate_exam_zero_score(self):
        """0 correct out of 45 must fail."""
        res = evaluate_exam_attempt(total_questions=45, correct_answers=0, duration_seconds=1800)
        assert res["passed"] is False
        assert res["errors"] == 45
        assert res["score_percentage"] == 0.0

    def test_evaluate_exam_time_limit_detection(self):
        """Time exceeded past grace period (> 5430s) must be flagged as timed out."""
        on_time = evaluate_exam_attempt(45, 40, duration_seconds=5300)
        assert on_time["timed_out"] is False

        over_time = evaluate_exam_attempt(45, 40, duration_seconds=5500)
        assert over_time["timed_out"] is True


class TestExamMichaelCoachingLanguageIsolation:
    """Zero tolerance for language bleed-through in Michael AI coaching prompts."""

    NORWEGIAN_CHAR_PATTERN = re.compile(r"[æøåÆØÅ]")

    def test_thai_coaching_prompt_purity_with_weak_topic(self):
        # Case: Failed exam with weak topic in Thai
        prompt_data = generate_michael_exam_prompt(
            lang="th",
            passed=False,
            score=32,
            total=45,
            weak_topic="กฎการให้ทาง",
        )
        assert prompt_data["lang"] == "th"
        display = prompt_data["display_message"]
        chat = prompt_data["chat_prompt"]

        assert "32/45" in display or "32" in display
        assert "กฎการให้ทาง" in display
        assert "กฎการให้ทาง" in chat

        # Absolute rule: No Norwegian characters in Thai prompts
        assert not self.NORWEGIAN_CHAR_PATTERN.search(display)
        assert not self.NORWEGIAN_CHAR_PATTERN.search(chat)

    def test_thai_coaching_prompt_purity_passed(self):
        # Case: Passed exam in Thai
        prompt_data = generate_michael_exam_prompt(
            lang="th",
            passed=True,
            score=42,
            total=45,
            weak_topic="ป้ายจราจร",
        )
        display = prompt_data["display_message"]
        chat = prompt_data["chat_prompt"]

        assert "ป้ายจราจร" in display
        assert "Statens vegvesen" not in display  # Clean Thai
        assert not self.NORWEGIAN_CHAR_PATTERN.search(display)
        assert not self.NORWEGIAN_CHAR_PATTERN.search(chat)

    def test_norwegian_and_english_prompts(self):
        no_prompt = generate_michael_exam_prompt("no", False, 30, 45, "vikeplikt")
        assert "vikeplikt" in no_prompt["chat_prompt"]
        assert "eksamenssimulatoren" in no_prompt["chat_prompt"]

        en_prompt = generate_michael_exam_prompt("en", False, 30, 45, "right of way")
        assert "right of way" in en_prompt["chat_prompt"]
        assert "exam simulation" in en_prompt["chat_prompt"]


class TestWebappExamIntegration:
    """Verify webapp UI translations and script hooks for Exam Simulator."""

    def test_webapp_translations_contain_exam_keys(self):
        from webapp import WEBAPP_HTML

        required_keys = [
            "result_exam_pass_head",
            "result_exam_pass_body",
            "result_exam_fail_head",
            "result_exam_focus_body",
            "result_coach_topic",
            "result_michael_coach",
            "exam_submit",
        ]
        for key in required_keys:
            assert f"{key}:" in WEBAPP_HTML or f"'{key}'" in WEBAPP_HTML, f"Missing key in webapp: {key}"

    def test_webapp_thai_translations_have_no_norwegian_bleed(self):
        """Verify that newly added Thai translations do not contain Norwegian characters."""
        import re
        from webapp import WEBAPP_HTML

        # Extract result_coach_topic and result_michael_coach
        match_coach = re.search(r"result_coach_topic:\{th:'([^']+)'", WEBAPP_HTML)
        assert match_coach, "result_coach_topic not found in WEBAPP_HTML"
        th_val = match_coach.group(1)
        assert not re.search(r"[æøåÆØÅ]", th_val)

        match_review = re.search(r"result_michael_coach:\{th:'([^']+)'", WEBAPP_HTML)
        assert match_review, "result_michael_coach not found in WEBAPP_HTML"
        th_review = match_review.group(1)
        assert not re.search(r"[æøåÆØÅ]", th_review)

    def test_webapp_contains_consult_michael_and_exam_retry(self):
        from webapp import WEBAPP_HTML

        assert "consultMichaelFromExam" in WEBAPP_HTML
        assert "endCoachMichaelPriBtn" in WEBAPP_HTML
        assert "if (isExamMode) startExam();" in WEBAPP_HTML


class TestServerQuizAttemptExamEvaluation:
    """Verify server-side enforcement of exam rules in save_quiz_attempt."""

    def test_server_enforces_exam_pass_and_fail(self):
        import asyncio
        from unittest.mock import AsyncMock, patch
        from server import save_quiz_attempt, QuizAttemptCreate

        async def _run():
            mock_db = AsyncMock()
            mock_db.quiz_attempts.insert_one = AsyncMock(return_value=None)

            # 1. Attempt with 37/45 (8 errors) must be evaluated as passed=False by server
            attempt_fail = QuizAttemptCreate(
                device_id="test-device-1",
                mode="exam",
                total_questions=45,
                correct_answers=37,
                score_percentage=82.2,
                passed=True,  # Tampered client says True, server must correct to False
                questions_answered=[],
                started_at="2026-09-18T10:00:00+00:00",
                completed_at="2026-09-18T10:45:00+00:00",
            )

            with patch("server.db", mock_db):
                res_fail = await save_quiz_attempt(attempt_fail, current_user=None)
                assert res_fail["passed"] is False
                assert res_fail["score_percentage"] == 82.2
                assert res_fail["duration_seconds"] == 2700

            # 2. Attempt with 38/45 (7 errors) must be evaluated as passed=True by server
            attempt_pass = QuizAttemptCreate(
                device_id="test-device-2",
                mode="exam",
                total_questions=45,
                correct_answers=38,
                score_percentage=84.4,
                passed=False,  # Client says False, server evaluates correct >= 38
                questions_answered=[],
                started_at="2026-09-18T10:00:00+00:00",
                completed_at="2026-09-18T10:50:00+00:00",
            )

            with patch("server.db", mock_db):
                res_pass = await save_quiz_attempt(attempt_pass, current_user=None)
                assert res_pass["passed"] is True
                assert res_pass["score_percentage"] == 84.4
                assert res_pass["duration_seconds"] == 3000

        asyncio.run(_run())
