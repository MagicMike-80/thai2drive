import copy
import sys
import unittest
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.build_flipp_flopp_master import build_cards  # noqa: E402


class FlippFloppMasterBuildTests(unittest.TestCase):
    def setUp(self):
        categories = ("vikeplikt", "plassering", "se", "stopp", "myndighet")
        self.source = {
            "total_cards": 50,
            "cards": [
                {
                    "id": i,
                    "source_card_id": i,
                    "category": categories[(i - 1) // 10],
                    "answer": i % 2 == 1,
                    "no": {"statement": f"Påstand {i}", "explanation": f"Forklaring {i}"},
                    "th": {"statement": f"คำถาม {i}", "explanation": f"คำอธิบาย {i}"},
                    "en": {"statement": f"Statement {i}", "explanation": f"Explanation {i}"},
                    "alt": {"no": "Trafikksituasjon", "th": "สถานการณ์จราจร", "en": "Traffic situation"},
                    "image": "flipp_flopp_01.jpg",
                    "norwegian_fagord": "Vikeplikt",
                    "source": "Trafikkreglene § 7",
                    "fasit_godkjent_av_michael": True,
                    "th_reviewed": True,
                }
                for i in range(1, 51)
            ],
        }

    def test_complete_approved_pack_maps_all_fifty_yes_no_cards(self):
        cards = build_cards(self.source, BACKEND / "public_assets")
        self.assertEqual(len(cards), 50)
        self.assertEqual([card["source_id"] for card in cards], list(range(1, 51)))
        self.assertEqual(cards[0]["answer"], {"no": "Ja", "th": "ใช่", "en": "Yes"})
        self.assertEqual(cards[1]["answer"], {"no": "Nei", "th": "ไม่ใช่", "en": "No"})
        self.assertTrue(all(card["approved_by_michael"] for card in cards))

    def test_unapproved_card_rejects_entire_pack(self):
        self.source["cards"][0]["fasit_godkjent_av_michael"] = False
        with self.assertRaisesRegex(ValueError, "ikke godkjent"):
            build_cards(self.source, BACKEND / "public_assets")

    def test_dedicated_sign_category_is_rejected(self):
        self.source["cards"][0]["category"] = "skilt"
        with self.assertRaisesRegex(ValueError, "kategori"):
            build_cards(self.source, BACKEND / "public_assets")

    def test_second_pack_extends_master_to_one_hundred(self):
        second = copy.deepcopy(self.source)
        for card in second["cards"]:
            card["id"] += 50
            card["source_card_id"] += 50
        cards = build_cards([self.source, second], BACKEND / "public_assets")
        self.assertEqual(len(cards), 100)
        self.assertEqual(cards[-1]["id"], "master-100")

    def test_thai_review_is_required(self):
        self.source["cards"][0]["th_reviewed"] = False
        with self.assertRaisesRegex(ValueError, "ikke gjennomgått"):
            build_cards(self.source, BACKEND / "public_assets")

    def test_test_month_keeps_approval_flag_and_uses_category_image(self):
        self.source["cards"][0]["fasit_godkjent_av_michael"] = False
        self.source["cards"][0]["th_reviewed"] = False
        self.source["cards"][0].pop("image")
        self.source["cards"][0].pop("alt")
        card = build_cards(
            self.source,
            BACKEND / "public_assets",
            {"vikeplikt": {"image": "flipp_flopp_theme_vikeplikt.png", "alt": {"no": "Kryss", "th": "ทางแยก", "en": "Junction"}}},
            test_month=True,
        )[0]
        self.assertFalse(card["approved_by_michael"])
        self.assertTrue(card["preview"])
        self.assertEqual(card["image"], "flipp_flopp_theme_vikeplikt.png")

    def test_missing_translation_or_image_rejects_entire_pack(self):
        missing_translation = copy.deepcopy(self.source)
        missing_translation["cards"][0]["th"]["explanation"] = ""
        with self.assertRaisesRegex(ValueError, "th.explanation"):
            build_cards(missing_translation, BACKEND / "public_assets")
        self.source["cards"][0]["image"] = "absent.jpg"
        with self.assertRaisesRegex(ValueError, "finnes ikke"):
            build_cards(self.source, BACKEND / "public_assets")


if __name__ == "__main__":
    unittest.main()
