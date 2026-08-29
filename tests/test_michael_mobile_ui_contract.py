import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBAPP = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")


class MichaelMobileUiContractTests(unittest.TestCase):
    def test_real_michael_portrait_is_packaged_and_used(self):
        portrait = ROOT / "backend" / "public_assets" / "michael_profile.jpg"
        self.assertTrue(portrait.is_file())
        self.assertGreater(portrait.stat().st_size, 10_000)
        self.assertGreaterEqual(WEBAPP.count("/api/assets/michael_profile.jpg"), 6)

    def test_mobile_topics_are_collapsible_and_touch_friendly(self):
        self.assertIn('id="teacherMoreBtn"', WEBAPP)
        self.assertIn("function toggleTeacherTopics()", WEBAPP)
        self.assertIn("min-height:50px", WEBAPP)
        self.assertIn("teacher-suggestions:not(.expanded)", WEBAPP)
        self.assertIn("#app.teacher-mode .flag-bg { display:none; }", WEBAPP)

    def test_new_learner_text_has_all_three_languages(self):
        for key in (
            "teacher_role",
            "teacher_experience",
            "teacher_more_topics",
            "teacher_fewer_topics",
        ):
            match = re.search(rf"{key}:\{{([^}}]+)\}}", WEBAPP)
            self.assertIsNotNone(match, key)
            value = match.group(1)
            self.assertIn("th:", value)
            self.assertIn("no:", value)
            self.assertIn("en:", value)

    def test_teacher_chat_contract_remains_in_place(self):
        self.assertIn("/api/teacher/chat", WEBAPP)
        self.assertIn("function _teacherAppendBubble(role, text)", WEBAPP)
        self.assertIn("function _teacherShowTyping()", WEBAPP)


if __name__ == "__main__":
    unittest.main()
