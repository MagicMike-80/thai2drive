"""Offline contract tests; real Mongo atomicity requires an isolated Mongo test."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "v6_progress_policy", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def run_immediate(coro):
    try:
        coro.send(None)
    except StopIteration as done:
        return done.value
    finally:
        coro.close()
    raise AssertionError("Synthetic collection unexpectedly suspended")


class FakeCollection:
    def __init__(self):
        self.records = {}
        self.last_request = None

    async def delete_many(self, query):
        self.last_delete_query = query
        keys = [key for key, value in self.records.items() if value.get("actor_marker") == query.get("actor_marker")]
        for key in keys:
            del self.records[key]
        return type("Result", (), {"deleted_count": len(keys)})()

    async def find_one_and_update(self, query, pipeline, *, upsert, return_document):
        self.last_request = (query, pipeline, upsert, return_document)
        event = pipeline[1]["$set"]["events"]["$cond"][1]["$concatArrays"][1][0]["$mergeObjects"][0]["$literal"]
        actor = pipeline[0]["$set"]["actor_marker"]["$ifNull"][1]["$literal"]
        record = self.records.setdefault(query["_id"], {"level": 0, "events": [], "actor_marker": actor})
        if record["actor_marker"] != actor:
            raise RuntimeError("synthetic actor mismatch")
        if not any(row["id"] == event["id"] for row in record["events"]) and len(record["events"]) < 128:
            if event["verdict"] == "incorrect":
                record["level"] = min(2, record["level"] + 1)
            elif event["verdict"] == "correct":
                record["level"] = 0
            record["events"].append(dict(event, level=record["level"]))
        return {"level": record["level"], "events": list(record["events"]), "actor_marker": record["actor_marker"]}


class ProgressStoreTest(unittest.TestCase):
    def test_scope_retry_conflict_and_data_minimization(self):
        store_data = FakeCollection()
        store = policy.MongoGuidanceStore(store_data)
        alice = {"principal": "alice-private", "delivery_session": "delivery-a",
                 "language": "no", "question_id": "question-a"}
        bob = dict(alice, principal="bob-private")
        event = "synthetic-event-0001"
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            advance = lambda scope, eid, verdict: run_immediate(store.advance_once(scope, eid, verdict))
            self.assertEqual(advance(alice, event, "incorrect"), 1)
            self.assertEqual(advance(alice, event, "incorrect"), 1)
            self.assertIsNone(advance(alice, event, "correct"))
            self.assertEqual(advance(alice, "synthetic-event-0002", "incorrect"), 2)
            self.assertEqual(advance(bob, event, "unknown"), 0)
            self.assertEqual(advance(alice, "synthetic-event-0003", "correct"), 0)
            self.assertNotIn("alice-private", repr(store_data.records))
            self.assertNotIn("question-a", repr(store_data.records))
            self.assertNotIn(event, repr(store_data.records))
            self.assertTrue(store_data.last_request[2])
            self.assertEqual(len(store_data.last_request[1]), 2)
            markers = {record["actor_marker"] for record in store_data.records.values()}
            self.assertEqual(markers, {policy.guidance_actor_marker("alice-private"),
                                       policy.guidance_actor_marker("bob-private")})

    def test_internal_erasure_is_scoped_and_fails_closed(self):
        collection = FakeCollection()
        store = policy.MongoGuidanceStore(collection)
        scope = {"principal": "alice-private", "delivery_session": "delivery", "language": "no", "question_id": "q"}
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            self.assertIsNotNone(run_immediate(store.advance_once(scope, "synthetic-event-0001", "incorrect")))
            self.assertIsNotNone(run_immediate(store.advance_once(dict(scope, principal="bob-private"), "synthetic-event-0001", "incorrect")))
            self.assertEqual(run_immediate(store.delete_for_verified_principal("alice-private")), 1)
            self.assertEqual(collection.last_delete_query, {"actor_marker": policy.guidance_actor_marker("alice-private")})
            self.assertEqual(len(collection.records), 1)
            self.assertEqual(next(iter(collection.records.values()))["actor_marker"], policy.guidance_actor_marker("bob-private"))
            self.assertEqual(run_immediate(store.delete_for_verified_principal("alice-private")), 0)
            self.assertIsNone(run_immediate(store.delete_for_verified_principal("")))
            os.environ["MICHAEL_V6_PROGRESS_KEY"] = ""
            self.assertIsNone(run_immediate(store.delete_for_verified_principal("bob-private")))
            self.assertEqual(len(collection.records), 1)

    def test_fails_closed_for_missing_key_invalid_scope_and_storage_error(self):
        class BrokenCollection:
            async def find_one_and_update(self, *args, **kwargs):
                raise RuntimeError("offline")

        scope = {"principal": "p", "delivery_session": "d", "language": "no", "question_id": "q"}
        store = policy.MongoGuidanceStore(BrokenCollection())
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "", "MICHAEL_V6_PROGRESS_KEY": ""}):
            self.assertIsNone(run_immediate(store.advance_once(scope, "synthetic-event-0001", "correct")))
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            self.assertIsNone(run_immediate(store.advance_once(scope, "synthetic-event-0001", "correct")))
            self.assertIsNone(run_immediate(store.advance_once(dict(scope, language="xx"), "synthetic-event-0001", "correct")))

    def test_rejects_new_events_at_the_bounded_limit(self):
        data = FakeCollection()
        store = policy.MongoGuidanceStore(data)
        scope = {"principal": "p", "delivery_session": "d", "language": "no", "question_id": "q"}
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            for i in range(128):
                self.assertIsNotNone(run_immediate(store.advance_once(scope, f"synthetic-event-{i:04d}", "unknown")))
            self.assertIsNone(run_immediate(store.advance_once(scope, "synthetic-event-overflow", "incorrect")))
            self.assertEqual(run_immediate(store.advance_once(scope, "synthetic-event-0000", "unknown")), 0)

    def test_lost_write_response_retries_same_event_without_double_counting(self):
        class LostReply(FakeCollection):
            first = True
            async def find_one_and_update(self, *args, **kwargs):
                result = await super().find_one_and_update(*args, **kwargs)
                if self.first:
                    self.first = False
                    raise RuntimeError("synthetic lost response after write")
                return result

        collection = LostReply()
        scope = {"principal": "p", "delivery_session": "d", "language": "en", "question_id": "q"}
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            level = run_immediate(policy.MongoGuidanceStore(collection).advance_once(
                scope, "synthetic-event-0001", "incorrect"))
        self.assertEqual(level, 1)
        self.assertEqual(len(next(iter(collection.records.values()))["events"]), 1)

    def test_signing_rotation_preserves_actor_lookup_but_identical_keys_fail_closed(self):
        collection = FakeCollection()
        store = policy.MongoGuidanceStore(collection)
        scope = {"principal": "p", "delivery_session": "d", "language": "no", "question_id": "q"}
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            marker = policy.guidance_actor_marker("p")
            self.assertEqual(run_immediate(store.advance_once(scope, "synthetic-event-0001", "incorrect")), 1)
            os.environ["MICHAEL_V6_SIGNING_KEY"] = "t" * 32
            self.assertEqual(policy.guidance_actor_marker("p"), marker)
            self.assertEqual(run_immediate(store.advance_once(scope, "synthetic-event-0001", "incorrect")), 1)
            os.environ["MICHAEL_V6_PROGRESS_KEY"] = "t" * 32
            self.assertIsNone(policy.guidance_actor_marker("p"))
            self.assertIsNone(run_immediate(store.advance_once(scope, "synthetic-event-0002", "incorrect")))

    def test_replayed_answer_keeps_first_verdict_and_rejects_changed_text(self):
        collection = FakeCollection()
        store = policy.MongoGuidanceStore(collection)
        scope = {"principal": "p", "delivery_session": "d", "language": "en", "question_id": "q"}
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "s" * 32, "MICHAEL_V6_PROGRESS_KEY": "p" * 32}):
            first = run_immediate(store.record_answer(scope, "synthetic-event-0001", "synthetic answer", "incorrect"))
            retry = run_immediate(store.record_answer(scope, "synthetic-event-0001", "synthetic answer", "correct"))
            self.assertEqual(run_immediate(store.record_answer(scope, "synthetic-event-0002", "another answer", "incorrect")), (2, "incorrect"))
            late_retry = run_immediate(store.record_answer(scope, "synthetic-event-0001", "synthetic answer", "correct"))
            changed = run_immediate(store.record_answer(scope, "synthetic-event-0001", "different answer", "correct"))
            other = run_immediate(store.record_answer(dict(scope, principal="other"), "synthetic-event-0001", "synthetic answer", "incorrect"))
        self.assertEqual(first, (1, "incorrect"))
        self.assertEqual(retry, (1, "incorrect"))
        self.assertEqual(late_retry, (1, "incorrect"))
        self.assertIsNone(changed)
        self.assertEqual(other, (1, "incorrect"))
        hashes = {record["events"][0]["answer_hash"] for record in collection.records.values()}
        self.assertEqual(len(hashes), 2, "answer fingerprints must not correlate across students")
        self.assertNotIn("synthetic answer", repr(collection.records))


if __name__ == "__main__":
    unittest.main()
