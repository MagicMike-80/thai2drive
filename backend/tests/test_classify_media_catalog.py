import json
import tempfile
import unittest
from pathlib import Path

from backend.scripts.classify_media_catalog import (
    load_area_map,
    plan_classification,
    snapshot_before,
)


class ClassifyMediaCatalogTests(unittest.TestCase):
    def test_area_map_matches_the_fourteen_reviewed_video_ids(self):
        areas = load_area_map(Path(__file__).resolve().parents[1] / "media_catalog_area_map.json")
        self.assertEqual(len(areas), 14)
        self.assertEqual(set(areas.values()), {"right_of_way", "speed_distance"})

    def test_plan_is_exact_and_never_changes_approval_flags(self):
        areas = {"video-a": "right_of_way", "video-b": "speed_distance"}
        documents = [
            {"_id": 1, "media_id": "video-a", "is_active": False, "approved_for_michael": False},
            {"_id": 2, "media_id": "video-b", "learning_area_id": "speed_distance"},
        ]
        changes = plan_classification(documents, areas)
        self.assertEqual([(item["media_id"], area) for item, area in changes], [("video-a", "right_of_way")])
        self.assertIs(documents[0]["is_active"], False)
        self.assertIs(documents[0]["approved_for_michael"], False)
        with self.assertRaises(ValueError):
            plan_classification(documents, {"video-a": "right_of_way"})
        with self.assertRaises(ValueError):
            plan_classification([{"media_id": "video-a", "learning_area_id": "other_topics"}],
                                {"video-a": "right_of_way"})

    def test_snapshot_contains_only_rollback_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "before.json"
            snapshot_before(path, [{
                "media_id": "video-a", "is_active": False,
                "approved_for_michael": False, "secret": "do-not-copy",
            }])
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["rows"][0]["media_id"], "video-a")
            self.assertNotIn("secret", str(snapshot))


if __name__ == "__main__":
    unittest.main()
