import copy
import json
from pathlib import Path
import unittest

from backend.scripts.repair_sign202_thai import validated_patch


class Sign202RepairTests(unittest.TestCase):
    def setUp(self):
        catalog = json.loads((Path(__file__).resolve().parents[1] / "signs_content.json").read_text(encoding="utf-8"))
        self.source = next(row for row in catalog if row["id"] == "202_0")
        self.live = copy.deepcopy(self.source)

    def test_actual_old_thai_stop_claim_changes_only_two_thai_fields(self):
        for field in ("explanation", "driver_action"):
            self.live[field]["th"] = "คุณต้องหยุดรอและให้รถอื่นผ่านก่อน"
        before = copy.deepcopy(self.live)
        patch = validated_patch(self.source, self.live)
        self.assertEqual(set(patch), {"explanation.th", "driver_action.th"})
        self.assertEqual(patch["driver_action.th"], self.source["driver_action"]["th"])
        self.assertEqual(self.live, before)

    def test_import_is_idempotent_and_cannot_target_another_sign(self):
        self.assertEqual(validated_patch(self.source, self.live), {})
        self.live["id"] = "204_0"
        with self.assertRaises(ValueError):
            validated_patch(self.source, self.live)

    def test_incomplete_or_mixed_language_source_fails_before_import(self):
        for value in ("give way", "", None):
            with self.subTest(value=value):
                source = copy.deepcopy(self.source)
                source["driver_action"]["th"] = value
                with self.assertRaises(ValueError):
                    validated_patch(source, self.live)
