from datetime import datetime, timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from backend.ai_learning import record_user_mistake


class UserMistakeTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.collection = MagicMock()
        self.collection.update_one = AsyncMock()
        self.collection.find_one = AsyncMock(return_value={"wrong_count": 1})
        self.collection.find_one_and_update = AsyncMock()
        self.db = MagicMock(user_mistakes=self.collection)
        self.now = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)

    async def test_wrong_answer_upserts_and_reactivates_one_question(self):
        await record_user_mistake(self.db, "u1", "q1", False, "daily", self.now)

        args, kwargs = self.collection.update_one.await_args
        self.assertEqual(args[0], {"user_id": "u1", "question_id": "q1"})
        self.assertTrue(kwargs["upsert"])
        self.assertEqual(args[1]["$inc"], {"wrong_count": 1})
        self.assertEqual(args[1]["$set"]["correct_streak"], 0)
        self.assertTrue(args[1]["$set"]["active"])
        self.assertFalse(args[1]["$set"]["mastered"])

    async def test_normal_correct_answer_does_not_change_mistake(self):
        result = await record_user_mistake(
            self.db, "u1", "q1", True, "daily", self.now
        )

        self.assertIsNone(result)
        self.collection.update_one.assert_not_awaited()
        self.collection.find_one_and_update.assert_not_awaited()

    async def test_correct_in_mistakes_mode_uses_atomic_mastery_pipeline(self):
        self.collection.find_one_and_update.return_value = {
            "correct_streak": 2, "active": False, "mastered": True
        }

        result = await record_user_mistake(
            self.db, "u1", "q1", True, "mistakes", self.now
        )

        args, kwargs = self.collection.find_one_and_update.await_args
        self.assertEqual(
            args[0], {"user_id": "u1", "question_id": "q1", "active": True}
        )
        pipeline = args[1]
        self.assertEqual(pipeline[1]["$set"]["active"], {"$lt": ["$correct_streak", 2]})
        self.assertEqual(pipeline[1]["$set"]["mastered"], {"$gte": ["$correct_streak", 2]})
        self.assertTrue(result["mastered"])
        self.assertIsNotNone(kwargs["return_document"])

    async def test_missing_identity_is_ignored(self):
        self.assertIsNone(
            await record_user_mistake(self.db, "", "q1", False, "daily", self.now)
        )
        self.collection.update_one.assert_not_awaited()
