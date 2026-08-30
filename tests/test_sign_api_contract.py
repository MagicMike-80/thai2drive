import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")


class SignApiContractTests(unittest.TestCase):
    def test_additive_sign_endpoints_use_existing_traffic_signs(self):
        self.assertIn('@api_router.get("/signs/{sign_id}")', SERVER)
        self.assertIn('db.traffic_signs.find_one({"id": sign_id}', SERVER)
        self.assertIn('async def get_signs(tag:', SERVER)
        self.assertIn('"signs": matches', SERVER)

    def test_sign_specific_questions_never_fall_back_to_unrelated_questions(self):
        self.assertIn("sign_id: Optional[str]", SERVER)
        self.assertIn("and not sign_id", SERVER)
        self.assertIn('match_stage["$or"]', SERVER)

    def test_sign_payload_is_trilingual_and_uses_existing_images(self):
        for field in ("name", "explanation", "driver_action", "group_name"):
            self.assertIn(f'"{field}": _multilang', SERVER)
        self.assertIn('ROOT_DIR / "sign_images"', SERVER)


if __name__ == "__main__":
    unittest.main()
