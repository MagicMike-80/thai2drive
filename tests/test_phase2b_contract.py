from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase2BContractTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
        cls.webapp = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")

    def test_readiness_endpoint_is_authenticated(self):
        self.assertIn('@api_router.get("/user/readiness")', self.server)
        self.assertIn("Depends(get_current_user)", self.server)

    def test_quiz_coach_is_fail_soft_and_language_scoped(self):
        self.assertIn("openMichaelQuizCoach()", self.webapp)
        self.assertIn("'/api/teacher/chat'", self.webapp)
        self.assertIn("language:appLang", self.webapp)
        self.assertIn("t('coach_unavailable')", self.webapp)

    def test_all_new_ui_keys_have_three_languages(self):
        for key in (
            "readiness_keep",
            "readiness_close",
            "readiness_ready",
            "coach_loading",
            "coach_unavailable",
            "coach_practical",
        ):
            line = next(line for line in self.webapp.splitlines() if f"{key}:" in line)
            self.assertIn("th:", line)
            self.assertIn("no:", line)
            self.assertIn("en:", line)
