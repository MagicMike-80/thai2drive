from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class Phase3ContractTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
        cls.webapp = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")

    def test_existing_freemium_quotas_remain_backend_owned(self):
        self.assertIn("ACCESS_GUEST_TOTAL_LIMIT = 5", self.server)
        self.assertIn("ACCESS_REGISTERED_DAILY_LIMIT = 10", self.server)
        self.assertIn('@api_router.post("/access/consume")', self.server)
        self.assertIn("'/api/access/consume'", self.webapp)

    def test_home_has_three_clear_action_groups(self):
        self.assertIn('data-key="home_primary_action"', self.webapp)
        self.assertIn('data-key="home_ask_michael"', self.webapp)
        self.assertIn('data-key="home_targeted"', self.webapp)
        self.assertIn("toggleTargetPracticeMenu()", self.webapp)

    def test_library_has_four_micro_lessons(self):
        self.assertIn('data-tab="micro"', self.webapp)
        for lesson_id in ("road-side", "yield", "winter", "roundabout"):
            self.assertEqual(self.webapp.count("{id:'" + lesson_id + "'"), 1)

    def test_new_learner_copy_has_all_three_languages(self):
        keys = (
            "home_choose_action",
            "home_primary_action",
            "home_ask_michael",
            "home_targeted",
            "home_open_signs",
            "lib_micro",
            "micro_intro",
            "micro_road_side_title",
            "micro_road_side_body",
            "micro_road_side_action",
            "micro_yield_title",
            "micro_yield_body",
            "micro_yield_action",
            "micro_winter_title",
            "micro_winter_body",
            "micro_winter_action",
            "micro_roundabout_title",
            "micro_roundabout_body",
            "micro_roundabout_action",
        )
        lines = self.webapp.splitlines()
        for key in keys:
            line = next(line for line in lines if line.lstrip().startswith(key + ":"))
            self.assertIn("th:", line, key)
            self.assertIn("no:", line, key)
            self.assertIn("en:", line, key)

    def test_checkout_price_display_stays_server_driven(self):
        self.assertIn("loadPremiumPricing()", self.webapp)
        self.assertIn("'/api/pricing?_='", self.webapp)
        self.assertIn("Live Stripe price mismatch", self.server)

