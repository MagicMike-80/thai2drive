"""Offline unit tests for official theory exam UI and logic in webapp.py."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


class TestExamUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        webapp_path = Path(__file__).resolve().parent.parent / "webapp.py"
        cls.content = webapp_path.read_text(encoding="utf-8")

    def test_exam_button_exists_on_dashboard(self):
        """Dashboard must contain the prominent official exam button."""
        self.assertIn('id="startExamBtn"', self.content)
        self.assertIn('class="home-cta home-cta-exam"', self.content)
        self.assertIn('onclick="startExam()"', self.content)
        self.assertIn('data-key="home_exam_action"', self.content)

    def test_exam_css_conforms_to_color_palette(self):
        """CSS for .home-cta-exam must use dark mode and allowed cyberpunk neon colors without yellow/green."""
        match = re.search(r'\.home-cta-exam\s*\{([^}]+)\}', self.content)
        self.assertIsNotNone(match, ".home-cta-exam CSS rule must be defined")
        css_body = match.group(1)
        self.assertIn('#00F5FF', css_body)  # Cyan
        # Verify forbidden neon colors (yellow/green) are not in the border glow
        self.assertNotIn('#FFFF00', css_body)
        self.assertNotIn('#00FF00', css_body)

    def test_start_exam_requests_45_questions_mode_exam(self):
        """startExam must request 45 questions with has_image=true and mode=exam."""
        match = re.search(r'(?:async\s+)?function\s+startExam\s*\(\)\s*\{([\s\S]+?)\n\}', self.content)
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertIn("count=45", body)
        self.assertIn("mode=exam", body)
        self.assertIn("isExamMode = true", body)

    def test_exam_timer_90_minutes(self):
        """Exam timer must be set to exactly 90 minutes (90 * 60 = 5400 seconds)."""
        match = re.search(r'function\s+startExamTimer\s*\(\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', self.content)
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertIn("90 * 60", body)
        self.assertIn("examTimerBadge", body)
        self.assertIn("examSubmitBtn", body)

    def test_submit_exam_button_and_confirmation(self):
        """Topbar must include exam submit button with confirmation dialog."""
        self.assertIn('id="examSubmitBtn"', self.content)
        self.assertIn('onclick="confirmSubmitExam()"', self.content)
        self.assertIn('data-key="exam_submit"', self.content)

        match = re.search(r'function\s+confirmSubmitExam\s*\(\)\s*\{([^}]+)\}', self.content)
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertIn("confirm(", body)
        self.assertIn("showEnd()", body)

    def test_pass_criteria_max_7_errors(self):
        """Pass criteria for official theory test must allow up to 7 errors (errors <= 7)."""
        # Check debrief logic
        self.assertIn("var examErrors = Math.max(0, total - qScore);", self.content)
        self.assertIn("var examPassed = examErrors <= 7;", self.content)
        # Check attempt saving logic
        self.assertIn("passed: isExamMode ? ((total - qScore) <= 7) : null", self.content)

    def test_passing_math_simulation(self):
        """Verify mathematical simulation of 45-question exam with max 7 errors."""
        def evaluate_exam(total, score):
            errors = total - score
            return errors <= 7

        # 38 correct out of 45 (7 errors) MUST pass
        self.assertTrue(evaluate_exam(45, 38))
        # 39 to 45 correct MUST pass
        for score in range(39, 46):
            self.assertTrue(evaluate_exam(45, score))

        # 37 correct out of 45 (8 errors) MUST fail
        self.assertFalse(evaluate_exam(45, 37))
        # 0 to 36 correct MUST fail
        for score in range(0, 38):
            self.assertEqual(evaluate_exam(45, score), score >= 38)

    def test_exam_translations_isolation(self):
        """All exam-related keys must have non-empty translations in NO, TH, and EN."""
        keys = ["home_exam_action", "home_exam_sub", "exam_submit", "exam_submit_confirm",
                "exam_incomplete", "readiness_exam_breakdown"]
        for key in keys:
            pattern = rf"{key}\s*:\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}"
            match = re.search(pattern, self.content)
            self.assertIsNotNone(match, f"Translation key '{key}' must be defined in TRANSLATIONS")
            trans_body = match.group(1)
            for lang in ["no", "th", "en"]:
                self.assertIn(f"{lang}:", trans_body, f"Key '{key}' missing '{lang}' translation")

    def test_exam_render_has_no_hardcoded_norwegian_fallback(self):
        """Exam rendering must not leak Norwegian before or after language selection."""
        self.assertIn('<span data-key="home_exam_action"></span>', self.content)
        self.assertRegex(
            self.content,
            r'id="examSubmitBtn"[^>]*data-key="exam_submit"></button>',
        )
        self.assertNotRegex(
            self.content,
            r"t\('(exam_submit_confirm|time_is_up)'\)\s*\|\|\s*['\"]",
        )

    def test_runtime_requires_45_image_questions_before_starting_timer(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        code = self.content.split("async function loadQuiz(url) {", 1)[1].split("\nfunction pickLang(", 1)[0]
        script = "async function loadQuiz(url) {" + code + """
var questions, isExamMode, currentCat, qCard, timerStarted, rendered;
var document = {getElementById: function() {return qCard;}};
function showScreen() {}
async function loadAccessStatus() {}
function t(key) {return key;}
function stopExamTimer() {}
function startExamTimer() {timerStarted = true;}
function renderQuestion() {rendered = true;}
async function run(count) {
  isExamMode = true; currentCat = null; qCard = {innerHTML:''};
  timerStarted = false; rendered = false;
  api = async function() {return Array.from({length:count}, function() {return {bildeUrl:'/image.jpg'};});};
  await loadQuiz('/api/questions/random?mode=exam');
  return {count:questions.length, exam:isExamMode, timer:timerStarted,
          rendered:rendered, message:qCard.innerHTML.includes('exam_incomplete')};
}
(async function() {console.log(JSON.stringify([await run(44), await run(45)]));})();
"""
        result = subprocess.run([node, "-e", script], capture_output=True, text=True, encoding="utf-8", check=True)
        short, full = json.loads(result.stdout)
        self.assertEqual(short, {"count": 0, "exam": False, "timer": False,
                                 "rendered": False, "message": True})
        self.assertEqual(full["count"], 45)
        self.assertTrue(full["exam"] and full["timer"] and full["rendered"])

    def test_runtime_timer_uses_elapsed_time(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        code = self.content.split("function startExamTimer() {", 1)[1].split("\nasync function startQuiz(", 1)[0]
        script = "function startExamTimer() {" + code + """
var examTimerInterval = null, examSecondsLeft = 0, examDeadline = 0, now = 0, tick, ended = false;
var elements = {};
var document = {getElementById: function(id) {
  return elements[id] || (elements[id] = {style:{}, textContent:''});
}};
Date.now = function() {return now;};
function setInterval(fn) {tick = fn; return 1;}
function clearInterval() {}
function toast() {}
function t(key) {return key;}
function showEnd() {ended = true;}
startExamTimer();
var initial = examSecondsLeft;
now = 60000; tick();
var afterMinute = examSecondsLeft;
now = 5400000; tick();
console.log(JSON.stringify({initial:initial, afterMinute:afterMinute,
                            final:examSecondsLeft, ended:ended}));
"""
        result = subprocess.run([node, "-e", script], capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(result.stdout),
                         {"initial": 5400, "afterMinute": 5340, "final": 0, "ended": True})


if __name__ == "__main__":
    unittest.main()
