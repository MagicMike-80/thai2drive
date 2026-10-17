import json
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import unittest
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("completed_day_fallback_helpers", Path(__file__).with_name("test_teacher_chat_fallback.py"))
fallback_helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback_helpers)
_load_teacher_chat = fallback_helpers._load_teacher_chat


class CompletedDayRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.teacher = _load_teacher_chat()
        cls.rows = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual43-completed-day-2026-10-17.json").read_text(encoding="utf-8"))["responses"]

    def test_actual_complete_reports_advance_without_measuring_mastery(self):
        for row in self.rows[:3]:
            with self.subTest(request=row["request_id"]):
                question = row["request"]["message"]
                self.assertTrue(self.teacher._reported_complete_first_day({}, question))
                contract = self.teacher._complete_request_contract({}, {}, question)
                self.assertIn("advance to day 2", contract)
                self.assertIn("not measured mastery", contract)

    def test_counts_partial_and_negated_completion_do_not_advance(self):
        for report in ["Jeg har gjort seks oppgaver", "Jeg har ikke fullført hele dag 1, både lesing og alle oppgavene", "I have not completed all of day 1, both the reading and all exercises", "ยังไม่เสร็จวันแรก ทั้งการอ่านและแบบฝึกหัดทั้งหมด"]:
            with self.subTest(report=report):
                self.assertFalse(self.teacher._reported_complete_first_day({"reported_progress": [report]}))

    def test_actual_thai_recall_uses_stored_second_day_and_keeps_unknown_time(self):
        row = next(row for row in self.rows if row["request_id"] == "control-th-3")
        raw = row["response"]["reply"]
        fixed = self.teacher._ground_completed_first_day(raw, row["verified_plan"], row["request"]["message"], "th")
        self.assertNotEqual(raw, fixed)
        self.assertIn("ขั้นตอนถัดไป: วันที่สอง", fixed)
        self.assertIn("ส่วนเวลาที่ใช้จริงยังไม่ทราบ", fixed)
        self.assertNotIn("สิ่งที่ยังไม่ทราบสถานะ คือข้อสอบ", fixed)
        self.assertNotIn("เพื่อที่เราจะได้ไปต่อวันที่สอง", fixed)
        self.assertEqual(raw, self.teacher._ground_completed_first_day(raw, {}, "", "th"))

    def test_new_plan_does_not_inherit_completed_day(self):
        report = "I completed all of day 1 on right-of-way, both the reading and all exercises."
        old = {"summary": "Day 1: yielding\nDay 2: signs", "reported_progress": [report]}
        self.assertFalse(self.teacher._reported_complete_first_day(old, "Create a new study plan"))
        new = self.teacher._study_plan_after_reply(old, "Create a new study plan", "Day 1: signs\nDay 2: stopping distance")
        self.assertEqual(new["reported_progress"], [])
        self.assertFalse(self.teacher._reported_complete_first_day(new, "What next?"))
        self.assertEqual(old["reported_progress"], [report])
        combined = report + " Create a new study plan."
        self.assertFalse(self.teacher._reported_complete_first_day(old, combined))
        combined_plan = self.teacher._study_plan_after_reply(old, combined, "Day 1: signs\nDay 2: stopping distance")
        self.assertEqual(combined_plan["reported_progress"], [])
        unchanged = self.teacher._study_plan_after_reply(old, "What is my plan?", "Day 1: yielding\nDay 2: signs")
        self.assertEqual(unchanged["reported_progress"], [report])

    def test_actual44_unmeasured_time_and_absent_practice_are_removed(self):
        rows = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual44-unsupported-practice-2026-10-17.json").read_text(encoding="utf-8"))["records"]
        for row in rows:
            reply = row["response"]["reply"]
            lang = row["request"]["language"]
            fixed = self.teacher._guard_unsupported_practice_claims(reply, lang)
            self.assertNotEqual(fixed, reply)
            if lang == "th":
                self.assertIn("ส่วนเวลาที่ใช้จริงผมไม่ทราบ", fixed)
                self.assertNotIn("เวลาที่เหลือ", fixed)
            else:
                self.assertIn("Neste steg: ta venstresvingen", fixed)
                self.assertNotIn("Det du ikke har trent på", fixed)
            self.assertEqual("Actual reported practice is known.", self.teacher._guard_unsupported_practice_claims("Actual reported practice is known.", lang))

    def test_actual45_mastery_is_discussion_not_demonstrated_skill(self):
        data = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual45-mastery-language-2026-10-17.json").read_text(encoding="utf-8"))
        row = next(row for row in data["records"] if row["request_id"] == "kai-32")
        reply = row["response"]["reply"]
        fixed = self.teacher._guard_unreported_success(reply, row["history"][-10:], row["request"]["message"], None, "no")
        self.assertIn("dem har vi snakket om", fixed)
        self.assertNotIn("dem kan du allerede forklare", fixed)
        grounded = self.teacher._guard_unsupported_practice_claims(fixed, "no")
        self.assertNotIn("ville du strøket", grounded)
        self.assertIn("still det her, så svarer jeg", grounded)

    def test_actual45_language_retry_names_embedded_rejected_characters_and_fails_closed(self):
        data = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual45-mastery-language-2026-10-17.json").read_text(encoding="utf-8"))
        first, failed_retry = [call["choices"][0]["message"]["content"] for call in data["control_th_5_model_calls"]]
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=failed_retry))])
        completion = AsyncMock(return_value=response)
        with patch.object(self.teacher, "_completion_with_fallback", completion):
            result = asyncio.run(self.teacher._guard_selected_language(first, [], "th"))
        instruction = completion.call_args.args[0][-1]["content"]
        self.assertIn("只看", instruction)
        self.assertIn('"bb"', instruction)
        self.assertIn("including characters embedded inside Thai words", instruction)
        self.assertIn("Preserve every answered part", instruction)
        self.assertEqual(self.teacher._fallback_reply("th"), result)
        clean = failed_retry.replace("只看", "")
        response.choices[0].message.content = clean
        with patch.object(self.teacher, "_completion_with_fallback", completion):
            self.assertEqual(clean, asyncio.run(self.teacher._guard_selected_language(first, [], "th")))


if __name__ == "__main__":
    unittest.main()
