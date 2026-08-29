from datetime import datetime, timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from backend.ai_learning import (
    compute_user_readiness,
    get_active_user_mistakes,
    record_user_mistake,
)


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

    async def test_active_mistakes_use_expected_filter_and_priority(self):
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.to_list = AsyncMock(return_value=[{"question_id": "q2"}])
        self.collection.find.return_value = cursor

        result = await get_active_user_mistakes(self.db, "u1", 250)

        self.collection.find.assert_called_once_with(
            {"user_id": "u1", "active": True, "mastered": {"$ne": True}},
            {"_id": 0},
        )
        cursor.sort.assert_called_once_with(
            [("wrong_count", -1), ("last_practiced_at", 1)]
        )
        cursor.limit.assert_called_once_with(100)
        cursor.to_list.assert_awaited_once_with(100)
        self.assertEqual(result, [{"question_id": "q2"}])


class ReadinessTests(IsolatedAsyncioTestCase):
    def test_readiness_uses_70_30_formula(self):
        result = compute_user_readiness(40, 50, 6, 4)
        self.assertEqual(result["recent_accuracy"], 80.0)
        self.assertEqual(result["mistake_mastery"], 60.0)
        self.assertEqual(result["score"], 74)

    def test_readiness_is_zero_for_new_user(self):
        self.assertEqual(compute_user_readiness(0, 0, 0, 0)["score"], 0)

    def test_perfect_answers_without_mistakes_are_fully_ready(self):
        self.assertEqual(compute_user_readiness(50, 50, 0, 0)["score"], 100)

    def test_readiness_is_clamped_to_0_100(self):
        result = compute_user_readiness(999, 50, 999, 0)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
