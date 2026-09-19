"""Visual contract tests for global neon design, perimeter border flow, and color palette compliance.

Enforces Protocol Null & AGENTS.md rules:
- Allowed neon palette: Deep Blue (#0066FF, #3B82F6), Cyan (#00F5FF), Magenta (#FF00E5), Amber/Orange (#FF9933, #FFAA00).
- Forbidden neon colors: Yellow (#FFFF00, #FFD700, #FFE033, #FFFF33) and Green (#00FF00, #00FF80, #00E676, #10B981, #00FF6A, #AAFF00).
- Border flow must circulate continuously (360 deg) via @property --neon-angle and @keyframes neonFlow.
- Both webapp.py and landing.py must be 100% compliant.
"""
import re
import unittest
from pathlib import Path


FORBIDDEN_NEON_HEX = [
    "#00FF00", "#00FF80", "#00E676", "#10B981", "#00FF6A", "#AAFF00",
    "#FFFF00", "#FFD700", "#FFE033", "#FFFF33"
]

APPROVED_NEON_HEX = [
    "#00F5FF",  # Electric Cyan
    "#0066FF",  # Deep Neon Blue
    "#FF00E5",  # Neon Magenta
    "#FF9933",  # Warm Amber / Neon Orange
    "#3B82F6",  # Bright Blue accent
    "#FFAA00",  # Amber accent
]


def extract_webapp_css(code: str) -> str:
    start = code.find("<style")
    if start == -1:
        return ""
    open_tag = code.find(">", start)
    close = code.find("</style>", open_tag)
    return code[open_tag + 1:close] if close != -1 else ""


def extract_landing_css(code: str) -> str:
    start = code.find('LANDING_CSS = """')
    if start != -1:
        close = code.find('"""', start + 17)
        return code[start + 17:close] if close != -1 else ""
    start = code.find("LANDING_CSS = '''")
    if start != -1:
        close = code.find("'''", start + 17)
        return code[start + 17:close] if close != -1 else ""
    return ""


class TestNeonDesignContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parents[1]
        cls.webapp_path = cls.root_dir / "backend" / "webapp.py"
        cls.landing_path = cls.root_dir / "backend" / "landing.py"

        cls.webapp_code = cls.webapp_path.read_text(encoding="utf-8")
        cls.landing_code = cls.landing_path.read_text(encoding="utf-8")

        cls.webapp_css = extract_webapp_css(cls.webapp_code)
        cls.landing_css = extract_landing_css(cls.landing_code)

    def test_property_neon_angle_declared_in_webapp_and_landing(self):
        """@property --neon-angle must be declared with <angle> syntax in both webapp and landing."""
        for name, css in [("webapp.py", self.webapp_css), ("landing.py", self.landing_css)]:
            with self.subTest(file=name):
                self.assertTrue("@property --neon-angle" in css, f"{name} missing @property --neon-angle")
                self.assertTrue("syntax: '<angle>'" in css, f"{name} missing syntax: '<angle>'")
                self.assertTrue("inherits: false" in css, f"{name} missing inherits: false")
                self.assertTrue("initial-value: 0deg" in css, f"{name} missing initial-value: 0deg")

    def test_keyframes_neon_flow_declared_in_webapp_and_landing(self):
        """@keyframes neonFlow must interpolate --neon-angle to 360deg."""
        for name, css in [("webapp.py", self.webapp_css), ("landing.py", self.landing_css)]:
            with self.subTest(file=name):
                self.assertTrue("@keyframes neonFlow" in css, f"{name} missing @keyframes neonFlow")
                self.assertTrue("--neon-angle: 360deg" in css, f"{name} missing --neon-angle: 360deg target")

    def test_root_neon_flow_gradient_tokens_compliance(self):
        """CSS root tokens must use approved 4-color palette and avoid forbidden yellow/green."""
        match = re.search(r'--neon-flow-gradient:\s*conic-gradient\([^;]+;', self.webapp_css)
        self.assertIsNotNone(match, "--neon-flow-gradient must be defined in webapp.py")
        token_def = match.group(0)

        # Must include all 4 cyber accents
        self.assertIn("#00F5FF", token_def)  # Cyan
        self.assertIn("#0066FF", token_def)  # Deep Blue
        self.assertIn("#FF00E5", token_def)  # Magenta
        self.assertIn("#FF9933", token_def)  # Amber/Orange

        # Must not contain any forbidden colors
        for forbidden in FORBIDDEN_NEON_HEX:
            self.assertNotIn(forbidden.lower(), token_def.lower(), f"Forbidden color {forbidden} in --neon-flow-gradient")

    def test_no_forbidden_colors_in_conic_gradients(self):
        """All conic-gradient definitions across webapp and landing must be free of forbidden colors."""
        for name, css in [("webapp.py", self.webapp_css), ("landing.py", self.landing_css)]:
            conic_matches = re.findall(r'conic-gradient\([^;]+', css, re.IGNORECASE)
            self.assertGreater(len(conic_matches), 0, f"{name} must contain conic gradients")
            for gradient in conic_matches:
                for forbidden in FORBIDDEN_NEON_HEX:
                    self.assertNotIn(
                        forbidden.lower(),
                        gradient.lower(),
                        f"Forbidden color {forbidden} found in {name} gradient: {gradient[:60]}"
                    )

    def test_no_forbidden_colors_in_neon_glow_rules(self):
        """Rules using neonFlow animation (excluding root variable definitions) must not use forbidden yellow or green."""
        for name, css in [("webapp.py", self.webapp_css), ("landing.py", self.landing_css)]:
            rules = css.split("}")
            neon_rules = [r for r in rules if ("neonFlow" in r or "conic-gradient" in r) and ":root" not in r]
            self.assertGreater(len(neon_rules), 0, f"{name} must have neon rules")
            for r in neon_rules:
                for forbidden in FORBIDDEN_NEON_HEX:
                    self.assertNotIn(
                        forbidden.lower(),
                        r.lower(),
                        f"Forbidden color {forbidden} in {name} rule: {r.strip()[:60]}"
                    )

    def test_universal_neon_button_selectors_coverage(self):
        """Webapp universal neon button styles must cover all major interactive and action buttons."""
        required_button_classes = [
            ".home-cta",
            ".home-cta-exam",
            ".auth-btn",
            ".auth-guest-btn",
            ".paywall-buy-btn",
            ".end-btn-pri",
            ".end-btn-sec",
            ".ask-michael-btn",
            ".teacher-send-btn",
            ".quiz-coach-trigger-btn",
        ]
        start_idx = self.webapp_css.find("Universal neon border")
        self.assertNotEqual(start_idx, -1, "Universal neon border section must exist in webapp.py")
        section = self.webapp_css[start_idx:start_idx + 2500]

        for btn_class in required_button_classes:
            self.assertIn(btn_class, section, f"Missing button class {btn_class} in neon buttons section")

    def test_dual_glow_aura_on_neon_buttons(self):
        """Rotating neon buttons must feature dual cyan (#00F5FF) and magenta (#FF00E5) box-shadow glows."""
        start_idx = self.webapp_css.find("Universal neon border")
        self.assertNotEqual(start_idx, -1)
        section = self.webapp_css[start_idx:start_idx + 2500]
        self.assertIn("rgba(0, 245, 255", section)  # Cyan aura
        self.assertIn("rgba(255, 0, 229", section)  # Magenta aura

    def test_landing_cta_and_lang_button_neon_effects(self):
        """Landing page CTA and active language switcher must have perimeter neon border flow."""
        self.assertTrue(".cta-primary" in self.landing_css)
        self.assertTrue(".cta-secondary" in self.landing_css)
        self.assertTrue(".lang-row .lang-btn.active" in self.landing_css)
        self.assertTrue("neonFlow" in self.landing_css)
        self.assertTrue("conic-gradient(from var(--neon-angle" in self.landing_css)

    def test_carousel_3d_active_ring_perimeter_flow(self):
        """Active 3D category card ring must circulate 360 degrees without gaps or forbidden colors."""
        start_idx = self.webapp_css.find(".carousel-3d-active-ring {")
        self.assertNotEqual(start_idx, -1, ".carousel-3d-active-ring must exist")
        end_idx = self.webapp_css.find("}", start_idx)
        ring_css = self.webapp_css[start_idx:end_idx]

        self.assertIn("conic-gradient(from var(--neon-angle", ring_css)
        self.assertIn("neonFlow", ring_css)
        self.assertIn("#00F5FF", ring_css)
        self.assertIn("#FF00E5", ring_css)
        self.assertIn("#0066FF", ring_css)
        self.assertIn("#FF9933", ring_css)

        for forbidden in FORBIDDEN_NEON_HEX:
            self.assertNotIn(forbidden.lower(), ring_css.lower())

    def test_cyber_categories_in_webapp_js_compliance(self):
        """CYBER_CATEGORIES mapping in webapp.py JS must not use forbidden neon green/yellow."""
        start_idx = self.webapp_code.find("CYBER_CATEGORIES = [")
        self.assertNotEqual(start_idx, -1, "CYBER_CATEGORIES array must be defined in webapp.py")
        end_idx = self.webapp_code.find("];", start_idx)
        cat_body = self.webapp_code[start_idx:end_idx]

        for forbidden in FORBIDDEN_NEON_HEX:
            self.assertNotIn(
                forbidden.lower(),
                cat_body.lower(),
                f"Forbidden color {forbidden} in CYBER_CATEGORIES definition"
            )


if __name__ == "__main__":
    unittest.main()
