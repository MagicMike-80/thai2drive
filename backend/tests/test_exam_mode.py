"""
Offline unit tests for the Exam Mode klar-score (quiz_readiness.py).

Pure function only — no network, no MongoDB, no server import.

    python -m unittest tests.test_exam_mode              # from backend/
    python -m unittest backend.tests.test_exam_mode      # from repo root
"""

import unittest

try:
    from quiz_readiness import compute_quiz_readiness
except ImportError:  # running from repo root
    from backend.quiz_readiness import compute_quiz_readiness


def att(correct, category="Fart", ms=10000):
    return {"is_correct": bool(correct), "category": category, "time_taken_ms": ms}


class ColdStart(unittest.TestCase):
    def test_under_ten_attempts_is_cold_start(self):
        r = compute_quiz_readiness([att(True) for _ in range(9)])
        self.assertTrue(r["cold_start"])
        self.assertEqual(r["ready_score"], 0)
        self.assertIsNone(r["pace_score"])
        self.assertEqual(r["attempts_considered"], 9)

    def test_ten_attempts_leaves_cold_start(self):
        r = compute_quiz_readiness([att(True) for _ in range(10)])
        self.assertFalse(r["cold_start"])
        self.assertGreater(r["ready_score"], 0)


class RecencyWeighting(unittest.TestCase):
    def test_recent_wrongs_hurt_more_than_old_wrongs(self):
        # Same multiset (10 right + 10 wrong), only the order differs.
        recent_wrong = [att(False) for _ in range(10)] + [att(True) for _ in range(10)]
        recent_right = [att(True) for _ in range(10)] + [att(False) for _ in range(10)]
        worse = compute_quiz_readiness(recent_wrong)
        better = compute_quiz_readiness(recent_right)
        self.assertLess(worse["error_trend"], better["error_trend"])
        self.assertLess(worse["ready_score"], better["ready_score"])


class VikepliktConfidence(unittest.TestCase):
    def test_few_vikeplikt_answers_barely_count(self):
        base = [att(True, "Fart") for _ in range(20)]
        one_vp_wrong = compute_quiz_readiness(base + [att(False, "Vikeplikt")])
        eight_vp_wrong = compute_quiz_readiness(base + [att(False, "Vikeplikt") for _ in range(8)])
        self.assertEqual(one_vp_wrong["vikeplikt_attempts"], 1)
        self.assertEqual(eight_vp_wrong["vikeplikt_attempts"], 8)
        self.assertEqual(one_vp_wrong["vikeplikt_mastery"], 0.0)
        self.assertEqual(eight_vp_wrong["vikeplikt_mastery"], 0.0)
        # Full-confidence 0% vikeplikt mastery drags the score much harder.
        self.assertGreater(one_vp_wrong["ready_score"], eight_vp_wrong["ready_score"] + 10)

    def test_roundabout_category_counts_as_vikeplikt(self):
        r = compute_quiz_readiness([att(True, "Rundkjøring") for _ in range(12)])
        self.assertEqual(r["vikeplikt_attempts"], 12)
        self.assertEqual(r["vikeplikt_mastery"], 100.0)


class Pace(unittest.TestCase):
    def test_pace_band(self):
        fast = compute_quiz_readiness([att(True, ms=1000) for _ in range(20)])
        good = compute_quiz_readiness([att(True, ms=10000) for _ in range(20)])
        slow = compute_quiz_readiness([att(True, ms=50000) for _ in range(20)])
        self.assertEqual(fast["pace_score"], 0.0)
        self.assertEqual(good["pace_score"], 100.0)
        self.assertEqual(slow["pace_score"], 0.0)
        self.assertEqual(good["pace_median_s"], 10.0)

    def test_pace_omitted_when_too_few_timed_correct_answers(self):
        # 3 correct (with time) + 17 wrong → below PACE_MIN_SAMPLES.
        attempts = [att(True, ms=10000) for _ in range(3)] + [att(False, ms=10000) for _ in range(17)]
        r = compute_quiz_readiness(attempts)
        self.assertIsNone(r["pace_score"])
        self.assertIsNone(r["pace_median_s"])
        self.assertFalse(r["cold_start"])  # still computed a score


class Clamping(unittest.TestCase):
    def test_perfect_history_scores_100(self):
        attempts = ([att(True, "Vikeplikt") for _ in range(10)]
                    + [att(True, "Fart") for _ in range(20)])
        self.assertEqual(compute_quiz_readiness(attempts)["ready_score"], 100)

    def test_all_wrong_scores_0(self):
        attempts = ([att(False, "Vikeplikt") for _ in range(10)]
                    + [att(False, "Fart") for _ in range(20)])
        self.assertEqual(compute_quiz_readiness(attempts)["ready_score"], 0)


if __name__ == "__main__":
    unittest.main()
