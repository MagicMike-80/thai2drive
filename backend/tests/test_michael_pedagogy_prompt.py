"""Offline contract test for Michael's 4-step pedagogy lock.

Verifies that the system prompt in ``backend/teacher_chat.py`` *enforces* the
SE ➔ TENKE ➔ SPØRRE ➔ SVARE decision loop (SEE ➔ THINK ➔ ASK ➔ ANSWER in
th/en) and that a clarifying question is mandated on broad enquiries — in all
three languages, with the legal section pushed to the very end of the answer.

No network, no MongoDB, no LLM call, no prod writes. The teacher_chat module is
loaded with stubbed fastapi/pydantic/motor/dotenv/litellm via the existing
``_load_teacher_chat`` helper.
"""
import sys
import unittest
from pathlib import Path

# Make ``backend`` importable when this file is run directly (pytest path arg).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.tests.test_teacher_chat_fallback import _load_teacher_chat  # noqa: E402


class MichaelPedagogyPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_teacher_chat()
        cls.prompts = {
            lang: cls.module._build_system_prompt(lang) for lang in ("no", "th", "en")
        }

    # ── 1. Decision loop is present and in order ─────────────────────────────

    def test_loop_marker_present_in_every_language(self):
        for prompt in self.prompts.values():
            self.assertIn("SE → TENK → SPØR → SVAR", prompt)

    def test_norwegian_loop_steps_appear_in_order(self):
        p = self.prompts["no"]
        i_se = p.find("**SE:**")
        i_tenke = p.find("**TENK**")
        i_sporre = p.find("**SPØR:**")
        i_svare = p.find("**SVAR:**") if "**SVAR:**" in p else p.find("**SVAR**")
        self.assertNotIn(-1, (i_se, i_tenke, i_sporre, i_svare))
        self.assertLess(i_se, i_tenke)
        self.assertLess(i_tenke, i_sporre)
        self.assertLess(i_sporre, i_svare)

    def test_think_step_names_the_three_cognitive_traps(self):
        # NO spells them out; th/en describe them inline on the THINK line.
        no = self.prompts["no"]
        self.assertIn("språkstøy", no)
        self.assertIn("eksamensstress", no)
        self.assertIn("blikkbruk", no)
        for lang in ("th", "en"):
            self.assertIn("språkstøy", self.prompts[lang])

    # ── 2. No heavy rule-text up front on broad questions ────────────────────

    def test_broad_questions_forbid_leading_with_law(self):
        self.assertIn("forbudt å gi forklaring eller sitere lovparagrafer", self.prompts["no"])
        for lang in ("th", "en"):
            self.assertIn("forbudt å gi forklaring", self.prompts[lang].lower())

    # ── 3. SPØRRE: one clarifying question first, never chained ──────────────

    def test_clarifying_question_is_mandatory_on_broad_enquiries(self):
        for lang in ("no", "th", "en"):
            low = self.prompts[lang].lower()
            self.assertIn("klargjøringsspørsmål", low)
            self.assertIn("4-5", low)

    def test_exactly_one_question_no_chaining(self):
        self.assertIn("Aldri to spørsmål på rad", self.prompts["no"])
        for lang in ("no", "th", "en"):
            self.assertIn("at most one clarifying question", self.prompts[lang].lower())

    # ── 4. SVARE: 5-step order with theory LAST ─────────────────────────────

    def test_answer_step_order_puts_theory_before_the_followup_only(self):
        for prompt in self.prompts.values():
            self.assertIn("Situasjon", prompt)
            self.assertIn("Forklar hva regelen betyr", prompt)
            self.assertIn("ett konkret kjørehandlingstips", prompt)
            self.assertNotIn("🚗 Situasjon", prompt)

    def test_theory_is_explicitly_marked_last(self):
        for prompt in self.prompts.values():
            self.assertIn("Teori og lov kommer alltid sist", prompt)

    def test_no_stale_theory_test_focus_header_remains(self):
        # Old 4th step "📝 Teoriprøve-vinkel / Theory test focus" was replaced
        # by "🔧 Praktisk råd" + "📖 Teori".
        for lang in ("no", "th", "en"):
            self.assertNotIn("📝 Teoriprøve-vinkel", self.prompts[lang])
            self.assertNotIn("📝 Theory test focus", self.prompts[lang])
            self.assertNotIn("📝 จุดเน้นข้อสอบทฤษฎี", self.prompts[lang])

    # ── 5. Language isolation header still injected first ────────────────────

    def test_language_header_is_first(self):
        self.assertTrue(self.prompts["no"].startswith("[LANGUAGE: no]"))
        self.assertTrue(self.prompts["th"].startswith("[ภาษา: th]"))
        self.assertTrue(self.prompts["en"].startswith("[LANGUAGE: en]"))

    # ── 6. _is_clarifying_question actually fires on a broad-style reply ─────

    def test_detector_true_for_option_style_clarifying_reply(self):
        reply = (
            "Selvfølgelig 😊\n\nHvilken situasjon gjelder det?\n\n"
            "🚗 Høyreregelen\n🛑 Vikepliktskilt\n🔴 Stoppskilt\n"
            "⭕ Rundkjøring\n🚶 Gangfelt"
        )
        self.assertTrue(self.module._is_clarifying_question(reply))

    def test_detector_true_for_thai_option_style_reply(self):
        reply = (
            "แน่นอนครับ 😊\n\nคุณอยากเน้นเรื่องไหนเป็นพิเศษครับ?\n\n"
            "🚗 กฎการให้ทางจากขวา\n🛑 ป้ายให้ทาง\n🔴 ป้ายหยุด\n⭕ วงเวียน\n🚶 ทางข้าม"
        )
        self.assertTrue(self.module._is_clarifying_question(reply))

    def test_detector_false_for_textbook_answer(self):
        reply = "Stoppelengde er summen av reaksjonsstrekning og bremsestrekning."
        self.assertFalse(self.module._is_clarifying_question(reply))

    def test_detector_false_for_bare_question_without_options(self):
        # A question mark alone must not count — it needs options/emoji/keywords.
        reply = "Bremselengden blir mye lengre på våt vei. Skjønner du hvorfor?"
        self.assertFalse(self.module._is_clarifying_question(reply))


if __name__ == "__main__":
    unittest.main(verbosity=2)
