"""Offline regressions from actual candidate43 responses; no model or database calls."""
import ast
import json
import logging
from pathlib import Path
import re
import unittest


BACKEND = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures/kai-ploy/candidate43-mastery-history-ranking-2026-10-17.json"


def load_helpers():
    names = {
        "_reported_progress", "_guard_unreported_success",
        "_ground_sign124_recall", "_guard_unsupported_exam_ranking",
    }
    path = BACKEND / "teacher_chat.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    namespace = {
        "re": re, "logger": logging.getLogger(__name__),
        "_fallback_reply": lambda lang: "offline-fallback",
    }
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


class Candidate44Regressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_helpers()
        cls.records = {row["request_id"]: row for row in json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]}

    def test_thai_answer_noun_does_not_establish_reported_practice(self):
        report = self.helpers["_reported_progress"]
        question = next(turn["content"] for turn in self.records["ploy-26"]["history"]
                        if turn["role"] == "user" and "ช่วยบอกคำตอบข้อสอบ" in turn["content"])
        self.assertFalse(report(question))
        self.assertFalse(report("ขอคำตอบข้อสอบ"))
        self.assertTrue(report("ฉันตอบไปหกข้อ ถูกสี่ข้อ"))
        self.assertTrue(report("วันนี้ฉันทำคำถามหกข้อ ถูกสี่ข้อ ผิดสองข้อ"))

    def test_actual_unchecked_roundabout_mastery_is_removed_without_losing_support(self):
        row = self.records["ploy-26"]
        reply = row["response"]["reply"]
        clause = "และวันนี้คุณเข้าใจถูกเรื่องวงเวียนแล้ว ตรงนั้นเอาไปใช้ได้จริง"
        guard = self.helpers["_guard_unreported_success"]
        self.assertIn(clause, reply)
        fixed = guard(reply, row["history"], row["request"]["message"], None, "th")
        self.assertEqual(fixed, reply.replace(clause, ""))
        self.assertIn("คุณเพิ่งทบทวนป้ายจราจรเมื่อคืน", fixed)
        self.assertIn("พักผ่อนให้เต็มที่ก่อนครับ", fixed)
        # Actual results or an explicit practice report retain the existing evidence gate.
        self.assertEqual(guard(reply, [], "ฉันตอบไปหกข้อ", None, "th"), reply)
        self.assertEqual(guard(reply, [], "", {"total_attempts": 6}, "th"), reply)

    def test_actual_false_no_teaching_paragraph_requires_verified_recalled124(self):
        row = self.records["kai-35"]
        reply = row["response"]["reply"]
        paragraph = (
            "Det jeg kan se, er at vi i denne samtalen ikke har gått gjennom noen regler med fasit i det hele tatt "
            "– vi har snakket om planen og om hva jeg er. Så det er ikke noe herfra som kan ha lært deg noe galt."
        )
        guard = self.helpers["_ground_sign124_recall"]
        self.assertIn(paragraph, reply)
        self.assertEqual(guard(reply, ["124_0"], "no"), reply.replace(paragraph, ""))
        for ids, lang in (([], "no"), (["202_0"], "no"), (["124_0"], "en")):
            with self.subTest(ids=ids, lang=lang):
                self.assertEqual(guard(reply, ids, lang), reply)

    def test_actual_ranking_qualifiers_do_not_remove_the_lesson_or_next_step(self):
        guard = self.helpers["_guard_unsupported_exam_ranking"]
        no_reply = self.records["kai-35"]["response"]["reply"]
        no_clause = ", som er der de fleste mister poeng"
        self.assertIn(no_clause, no_reply)
        self.assertEqual(guard(no_reply), no_reply.replace(no_clause, ""))
        th_reply = self.records["ploy-27"]["response"]["reply"]
        th_clause = "ที่คุณยังพลาดบ่อยที่สุด"
        self.assertIn(th_clause, th_reply)
        fixed = guard(th_reply)
        self.assertEqual(fixed, th_reply.replace(th_clause, ""))
        self.assertIn("กฎทางขวาและลำดับความสำคัญที่ทางแยก", fixed)
        self.assertIn("ลองอ่านสั้น ๆ เรื่องนี้รอบเดียว", fixed)
        measured = "Du rapporterte to feil av seks svar. คุณบอกว่าตอบผิดสองข้อ"
        self.assertEqual(guard(measured), measured)


if __name__ == "__main__":
    unittest.main()
