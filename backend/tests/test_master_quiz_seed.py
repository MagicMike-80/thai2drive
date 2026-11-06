import unittest
from backend.seed_master_quiz import (
    DEFAULT_PAYLOAD_PATH,
    VALID_AREAS,
    build_master_quiz_operations,
    seed_master_quiz_sync,
)

class _BulkResult:
    def __init__(self, matched_count=0, upserted_count=0, modified_count=0):
        self.matched_count = matched_count
        self.upserted_count = upserted_count
        self.modified_count = modified_count
        self.upserted_ids = {}

class _MockCollection:
    def __init__(self):
        self.operations = []

    def bulk_write(self, operations, ordered=False):
        self.operations = operations
        return _BulkResult(
            matched_count=0,
            upserted_count=len(operations),
            modified_count=0,
        )

class MasterQuizSeedTests(unittest.TestCase):
    def test_default_payload_file_exists_and_has_239_valid_questions(self):
        self.assertTrue(DEFAULT_PAYLOAD_PATH.is_file())
        import json
        payload = json.loads(DEFAULT_PAYLOAD_PATH.read_text(encoding="utf-8"))
        questions = payload.get("questions", [])
        self.assertEqual(len(questions), 239)

        for q in questions:
            self.assertIn("id", q)
            self.assertIn(q["learning_area_id"], VALID_AREAS)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["correctOptionId"], ("A", "B", "C", "D"))
            self.assertIn("bildeUrl", q)

    def test_seeding_executes_bulk_write_with_240_operations(self):
        mock_col = _MockCollection()
        result = seed_master_quiz_sync(mock_col)
        self.assertEqual(result["total"], 240)
        self.assertEqual(result["upserted"], 240)
        self.assertEqual(len(mock_col.operations), 240)

    def test_seeding_never_overwrites_existing_image_links(self):
        operations = build_master_quiz_operations()
        for operation in operations[:-1]:
            self.assertNotIn("bildeUrl", operation._doc["$set"])
            image_url = operation._doc["$setOnInsert"].get("bildeUrl", "")
            self.assertTrue(
                not image_url or image_url.startswith("/api/public_assets/quiz_images/")
            )

if __name__ == "__main__":
    unittest.main()
