"""Unit tests for Michael Scaffolding Ladder (Idé 1) and Dynamic Tone (Idé 7).

Verifies:
1. Parsing of attempt_count from <quiz_context> (1, 2, or 3).
2. Scaffolding ladder prompt levels:
   - Attempt 1: Encourage rethink, strictly forbid revealing fasit.
   - Attempt 2: Pedagogical hint, strictly forbid revealing fasit.
   - Attempt 3: Full explanation with fasit and approved mnemonic.
3. Dynamic tone detection and instruction (warm, strict, dry, calm).
4. Thai glossary rule: Thai text with Norwegian technical terms in parentheses, zero English.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.teacher_chat as tc


class TestScaffoldingAttemptParsing(unittest.TestCase):
    def test_extract_attempt_count_when_present(self):
        self.assertEqual(tc._extract_attempt_count("attempt_count: 1\nQuestion: Hva er vikeplikt?"), 1)
        self.assertEqual(tc._extract_attempt_count("attempt_count: 2\nQuestion: Hva er vikeplikt?"), 2)
        self.assertEqual(tc._extract_attempt_count("attempt_count: 3\nQuestion: Hva er vikeplikt?"), 3)

    def test_extract_attempt_count_bounds(self):
        # Clamped to [1, 3]
        self.assertEqual(tc._extract_attempt_count("attempt_count: 0\nQuestion: test"), 1)
        self.assertEqual(tc._extract_attempt_count("attempt_count: 5\nQuestion: test"), 3)

    def test_extract_attempt_count_when_missing(self):
        self.assertIsNone(tc._extract_attempt_count("Question: Hva er vikeplikt?\nExplanation: ..."))
        self.assertIsNone(tc._extract_attempt_count(""))
        self.assertIsNone(tc._extract_attempt_count(None))


class TestScaffoldingLadderInstructions(unittest.TestCase):
    def test_attempt_1_instruction(self):
        prompt = tc._scaffolding_instruction(attempt=1, explicit_request=False, lang="no")
        self.assertIn("STEP 1", prompt)
        self.assertIn("Do NOT reveal", prompt)
        self.assertIn("attempt number 1", prompt)

    def test_attempt_2_instruction(self):
        prompt = tc._scaffolding_instruction(attempt=2, explicit_request=False, lang="no")
        self.assertIn("STEP 2", prompt)
        self.assertIn("PEDAGOGICAL HINT", prompt)
        self.assertIn("DO NOT reveal the correct answer", prompt)
        self.assertIn("attempt number 2", prompt)

    def test_attempt_3_instruction(self):
        prompt = tc._scaffolding_instruction(attempt=3, explicit_request=False, lang="no")
        self.assertIn("STEP 3", prompt)
        self.assertIn("FULL EXPLANATION & FASIT", prompt)
        self.assertIn("Reveal the correct answer", prompt)
        self.assertIn("attempt number 3", prompt)

    def test_explicit_request_forces_step_3(self):
        # Even on attempt 1, explicit request for fasit gives STEP 3
        prompt = tc._scaffolding_instruction(attempt=1, explicit_request=True, lang="no")
        self.assertIn("STEP 3", prompt)
        self.assertIn("Reveal the correct answer", prompt)


class TestDynamicToneSelection(unittest.TestCase):
    def test_detect_strict_tone_from_dangerous_driving(self):
        self.assertEqual(tc._detect_tone("Jeg kjørte 50 i 30 sonen"), "strict")
        self.assertEqual(tc._detect_tone("Må jeg stoppe for rødt lys?"), "strict")
        self.assertEqual(tc._detect_tone("Glemte å sjekke blindsone"), "strict")
        self.assertEqual(tc._detect_tone("Drikke og kjøre går fint"), "strict")
        # Thai safety violations
        self.assertEqual(tc._detect_tone("ขับรถฝ่าไฟแดง"), "strict")
        self.assertEqual(tc._detect_tone("ดื่มแล้วขับได้ไหม"), "strict")

    def test_detect_strict_tone_from_quiz_context(self):
        # Even if user message is short, dangerous question in quiz_context triggers strict
        context = "Question: Hva skjer hvis du kjører mot rødt lys?\nStudent answer: Kjøre videre"
        self.assertEqual(tc._detect_tone("Hvorfor er dette feil?", context), "strict")

    def test_detect_warm_tone_from_anxiety_or_stress(self):
        self.assertEqual(tc._detect_tone("Jeg gruer meg så fælt til oppkjøring, er kjempenervøs"), "warm")
        self.assertEqual(tc._detect_tone("Jeg bommer på alt og klarer ikke dette"), "warm")
        self.assertEqual(tc._detect_tone("เครียดมาก กลัวสอบไม่ผ่าน"), "warm")
        self.assertEqual(tc._detect_tone("I am so stressed and nervous about the test"), "warm")

    def test_detect_dry_tone_from_humour(self):
        self.assertEqual(tc._detect_tone("haha lol 555"), "dry")
        self.assertEqual(tc._detect_tone("hjernen min består av spaghetti"), "dry")

    def test_default_to_calm_tone_for_standard_enquiry(self):
        self.assertIsNone(tc._detect_tone("Hva betyr skilt 208?"))
        self.assertIsNone(tc._detect_tone("ป้ายนี้หมายถึงอะไร"))
        self.assertIsNone(tc._detect_tone("What is the speed limit outside towns?"))
        self.assertIn("CALM", tc._tone_instruction(tc._detect_tone("Hva betyr skilt 208?") or "calm", "no"))

    def test_tone_instruction_content(self):
        strict_p = tc._tone_instruction("strict", "no")
        self.assertIn("STRICT", strict_p)
        self.assertIn("Norwegian", strict_p)

        warm_p = tc._tone_instruction("warm", "th")
        self.assertIn("WARM", warm_p)
        self.assertIn("Thai", warm_p)

        calm_p = tc._tone_instruction("calm", "no")
        self.assertIn("CALM", calm_p)


class TestThaiGlossaryAndLanguagePurity(unittest.TestCase):
    def test_thai_output_contract_enforces_glossary_parentheses(self):
        contract = tc._master_output_contract("th")
        self.assertIn("thai-forklaring (norsk fagord)", contract)
        self.assertIn("Zero English allowed", contract)

    def test_thai_quiz_purity_block_allows_norwegian_parentheses_and_bans_english(self):
        block = tc._thai_quiz_purity_block()
        self.assertIn("thai-forklaring (norsk fagord)", block)
        self.assertIn("ZERO ENGLISH", block)
        self.assertIn("NO LATIN LETTERS OUTSIDE PARENTHESES", block)


if __name__ == "__main__":
    unittest.main()
