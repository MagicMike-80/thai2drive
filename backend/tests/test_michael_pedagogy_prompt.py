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
        self.assertIn("SE ➔ TENKE ➔ SPØRRE ➔ SVARE", self.prompts["no"])
        self.assertIn("SEE ➔ THINK ➔ ASK ➔ ANSWER", self.prompts["th"])
        self.assertIn("SEE ➔ THINK ➔ ASK ➔ ANSWER", self.prompts["en"])

    def test_norwegian_loop_steps_appear_in_order(self):
        p = self.prompts["no"]
        i_se = p.find("STEG 1: SE")
        i_tenke = p.find("STEG 2: TENKE")
        i_sporre = p.find("STEG 3: SPØRRE")
        i_svare = p.find("STEG 4: SVARE")
        self.assertNotIn(-1, (i_se, i_tenke, i_sporre, i_svare))
        self.assertLess(i_se, i_tenke)
        self.assertLess(i_tenke, i_sporre)
        self.assertLess(i_sporre, i_svare)

    def test_think_step_names_the_three_cognitive_traps(self):
        # NO spells them out; th/en describe them inline on the THINK line.
        no = self.prompts["no"]
        self.assertIn("Språkstøy", no)
        self.assertIn("Stress", no)
        self.assertIn("blikkbruk", no)
        for lang in ("th", "en"):
            think_line = next(
                ln for ln in self.prompts[lang].splitlines()
                if "THINK" in ln and "trap" in ln
            )
            self.assertIn("language noise", think_line)
            self.assertIn("nerves", think_line)
            self.assertIn("eye use", think_line)

    # ── 2. No heavy rule-text up front on broad questions ────────────────────

    def test_broad_questions_forbid_leading_with_law(self):
        self.assertIn("ABSOLUTT FORBUD", self.prompts["no"])
        self.assertIn("Ingen juridisk døråpner", self.prompts["no"])
        for lang in ("th", "en"):
            self.assertIn("forbidden", self.prompts[lang].lower())

    # ── 3. SPØRRE: one clarifying question first, never chained ──────────────

    def test_clarifying_question_is_mandatory_on_broad_enquiries(self):
        self.assertIn("CLARIFYING QUESTION RULE", self.prompts["no"])
        self.assertIn("CLARIFYING QUESTION RULE", self.prompts["th"])
        for lang in ("no", "th", "en"):
            low = self.prompts[lang].lower()
            self.assertIn("clarifying question", low)
            self.assertIn("4", low)  # "4-5 options" / "4–5 alternativer"

    def test_exactly_one_question_no_chaining(self):
        self.assertIn("Aldri to spørsmål på rad", self.prompts["no"])
        self.assertIn("Never two questions in a row", self.prompts["th"])
        self.assertIn("Never two questions in a row", self.prompts["en"])
        for lang in ("no", "th", "en"):
            self.assertIn("chain questions", self.prompts[lang].lower())

    # ── 4. SVARE: 5-step order with theory LAST ─────────────────────────────

    def test_answer_step_order_puts_theory_before_the_followup_only(self):
        for lang, labels in {
            "no": ["🚗 Situasjon", "💡 Forklaring", "⚠️ Vanlig feil",
                   "🔧 Praktisk råd", "📖 Teori", "❓"],
            "th": ["🚗 สถานการณ์", "💡 คำอธิบาย", "⚠️ ข้อผิดพลาดที่พบบ่อย",
                   "🔧 คำแนะนำในทางปฏิบัติ", "📖 ทฤษฎีและกฎหมาย", "❓"],
            "en": ["🚗 Situation", "💡 Explanation", "⚠️ Common mistake",
                   "🔧 Practical advice", "📖 Theory", "❓"],
        }.items():
            positions = [self.prompts[lang].find(lbl) for lbl in labels]
            self.assertNotIn(-1, positions, f"missing label in {lang}: {positions}")
            self.assertEqual(
                positions, sorted(positions),
                f"5-step headers out of order for {lang}: {list(zip(labels, positions))}",
            )

    def test_theory_is_explicitly_marked_last(self):
        self.assertIn("KUN TIL SLUTT", self.prompts["no"])
        self.assertIn("LAST ONLY", self.prompts["th"])
        self.assertIn("LAST ONLY", self.prompts["en"])
        self.assertIn("NEVER put the legal section before step 5", self.prompts["th"])
        self.assertIn("Never put the legal section before step 5", self.prompts["en"])

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
