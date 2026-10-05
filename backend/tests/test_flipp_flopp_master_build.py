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
                    "category": "skilt" if i == 1 else categories[(i - 1) // 10],
                    "answer": i % 2 == 1,
                    "no": {"statement": f"Påstand {i}", "explanation": f"Forklaring {i}"},
                    "th": {"statement": f"คำถาม {i}", "explanation": f"คำอธิบาย {i}"},
                    "en": {"statement": f"Statement {i}", "explanation": f"Explanation {i}"},
                    "alt": {"no": "Trafikksituasjon", "th": "สถานการณ์จราจร", "en": "Traffic situation"},
                    "image": "flipp_flopp_01.jpg",
                    "norwegian_fagord": "Vikeplikt",
                    "source": "Trafikkreglene § 7",
                    "fasit_godkjent_av_michael": True,
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

    def test_pack_without_sign_card_is_rejected(self):
        self.source["cards"][0]["category"] = "vikeplikt"
        with self.assertRaisesRegex(ValueError, "inkludert skilt"):
            build_cards(self.source, BACKEND / "public_assets")

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
