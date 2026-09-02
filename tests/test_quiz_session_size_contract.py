import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBAPP = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")
SERVER = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")


class QuizSessionSizeContractTests(unittest.TestCase):
    def test_backend_random_quiz_default_is_ten(self):
        route = SERVER[SERVER.index('@api_router.get("/questions/random")'):]
        route = route[:route.index('@api_router.get(', 1)]
        self.assertRegex(route, r"count:\s*int\s*=\s*Query\(default=10,")

    def test_normal_quiz_flows_share_ten_question_constant(self):
        self.assertIn("var QUIZ_SESSION_SIZE = 10;", WEBAPP)
        self.assertNotIn("/api/questions/random?count=30", WEBAPP)
        self.assertIn("/api/quiz/mistakes?limit=' + QUIZ_SESSION_SIZE", WEBAPP)
        self.assertGreaterEqual(WEBAPP.count("count=' + QUIZ_SESSION_SIZE"), 4)

    def test_progress_and_summary_offer_expected_next_steps(self):
        self.assertIn('id="qProgLbl">Spørsmål 1 av 10</div>', WEBAPP)
        self.assertIn("(qIdx + 1) + ' ' + t('of') + ' ' + displayTotal", WEBAPP)
        self.assertIn('onclick="retryQuiz()" data-key="result_retry"', WEBAPP)
        self.assertIn('onclick="showTab(\'teacher\')" data-key="result_michael"', WEBAPP)
        match = re.search(r"result_michael:\{([^}]+)\}", WEBAPP)
        self.assertIsNotNone(match)
        for language in ("th:", "no:", "en:"):
            self.assertIn(language, match.group(1))

    def test_exam_and_single_sign_practice_keep_their_own_sizes(self):
        self.assertIn("count=45&has_image=true&mode=exam", WEBAPP)
        self.assertIn("count=1&has_image=true&sign_id=", WEBAPP)


if __name__ == "__main__":
    unittest.main()
