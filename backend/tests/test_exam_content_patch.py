"""The content repair changes only the three intended MongoDB records."""

import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from patch_exam_question_content import (  # noqa: E402
    HELD_QUESTION_IDS,
    RAILWAY_IMAGE_URL,
    RAILWAY_QUESTION_ID,
    patch_questions,
    verify_questions,
)


class _Result:
    matched_count = 1


class _Questions:
    def __init__(self):
        self.rows = {
            RAILWAY_QUESTION_ID: {"id": RAILWAY_QUESTION_ID,
                                  "bildeUrl": "/api/sign-images/134_0.jpg", "active": True},
            HELD_QUESTION_IDS[0]: {"id": HELD_QUESTION_IDS[0], "active": True},
            HELD_QUESTION_IDS[1]: {"id": HELD_QUESTION_IDS[1], "active": True},
            "untouched": {"id": "untouched", "active": True},
        }

    def find_one(self, query, _projection):
        return self.rows.get(query["id"])

    def update_one(self, query, update):
        self.rows[query["id"]].update(update["$set"])
        return _Result()


def test_dry_run_apply_and_repeat_are_scoped():
    questions = _Questions()
    planned = patch_questions(questions)
    assert len(planned) == 3
    assert questions.rows[RAILWAY_QUESTION_ID]["bildeUrl"] == "/api/sign-images/134_0.jpg"
    assert all(questions.rows[qid]["active"] for qid in HELD_QUESTION_IDS)

    assert patch_questions(questions, apply=True) == planned
    assert questions.rows[RAILWAY_QUESTION_ID]["bildeUrl"] == RAILWAY_IMAGE_URL
    assert all(questions.rows[qid]["active"] is False for qid in HELD_QUESTION_IDS)
    assert questions.rows["untouched"] == {"id": "untouched", "active": True}
    assert patch_questions(questions, apply=True) == []
    verify_questions(questions)


def test_verification_rejects_unrepaired_record():
    questions = _Questions()
    with pytest.raises(RuntimeError, match="verification failed"):
        verify_questions(questions)


def test_missing_question_stops_without_upsert():
    questions = _Questions()
    del questions.rows[HELD_QUESTION_IDS[1]]
    with pytest.raises(LookupError, match=HELD_QUESTION_IDS[1]):
        patch_questions(questions, apply=True)
    assert questions.rows[RAILWAY_QUESTION_ID]["bildeUrl"] == "/api/sign-images/134_0.jpg"
