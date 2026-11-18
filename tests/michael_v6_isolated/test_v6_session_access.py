"""Synthetic component checks; no application import or real external services."""
import ast
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import types
import unittest
from unittest.mock import patch


def deny_external_operations(event, args):
    if event.startswith(("socket.", "subprocess.", "os.system", "os.spawn")):
        raise RuntimeError("External operations are forbidden")


sys.addaudithook(deny_external_operations)
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("michael_v6_policy", ROOT / "backend" / "michael_v6_policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
sys.modules["michael_v6_policy"] = policy
os.environ["MICHAEL_V6_SIGNING_KEY"] = "synthetic-test-key-for-isolated-controls-12345"
server = types.ModuleType("server")
server.AVAILABLE_QUESTION_FILTER = {"active": {"$ne": False}}
sys.modules["server"] = server


class Cursor:
    def __init__(self, rows):
        self.rows = rows
    def limit(self, count):
        return self
    async def to_list(self, count):
        return self.rows[:count]


class Collection:
    rows = []
    def find(self, query):
        assert query["$and"][0] is server.AVAILABLE_QUESTION_FILTER
        return Cursor(self.rows)


class Response:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def run_immediate(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError("A synthetic dependency unexpectedly suspended")


collection = Collection()
namespace = {"TeacherChatRequest": object, "TeacherChatResponse": Response,
             "_db": {"questions": collection}, "_v6_access_authorizer": None,
             "_v6_globally_ready": lambda policy: True,
             "_v6_content_ready": lambda policy, question_id, question: True}
async def synthetic_verified_user(request):
    return {"id": "synthetic-user"}
namespace["_v6_verified_user"] = synthetic_verified_user
source = (ROOT / "backend" / "teacher_chat.py").read_text(encoding="utf-8")
node = next(item for item in ast.parse(source).body
            if isinstance(item, ast.AsyncFunctionDef) and item.name == "_v6_quiz_pilot")
module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
exec(compile(module, "<synthetic V6 component>", "exec"), namespace)


class SessionAccessTests(unittest.TestCase):
    def setUp(self):
        self.question = {
            "id": "synthetic", "active": True,
            "question": {"no": "Oppgave", "th": "โจทย์", "en": "Question"},
            "options": [
                {"id": "A", "text": {"no": "Rød", "th": "สีแดง", "en": "Red"}},
                {"id": "B", "text": {"no": "Blå", "th": "สีน้ำเงิน", "en": "Blue"}},
            ],
            "correctOptionId": "B",
        }
        collection.rows = [self.question]
        policy.APPROVED_CONTENT_DIGESTS.clear()
        policy.APPROVED_GUIDANCE.clear()
        policy.APPROVED_CONTENT_DIGESTS["synthetic"] = policy._content_digest(self.question)
        self.token = policy.issue_delivery_token(self.question)
        namespace["_v6_access_authorizer"] = None
        namespace["_v6_guidance_store"] = None
        namespace["_v6_semantic_judge"] = None

    def request(self, lang="no", answer="Rød", level=0):
        return types.SimpleNamespace(v6_question_id="synthetic", v6_delivery_token=self.token,
                                     language=lang, v6_intent="answer", v6_answer_text=answer,
                                     message=answer, v6_hint_level=level)

    def invoke(self, request, session):
        return run_immediate(namespace["_v6_quiz_pilot"](request, session))

    def test_access_port_is_closed_without_validator(self):
        session = policy.delivery_session_id(self.token, "no")
        response = self.invoke(self.request(), session)
        self.assertEqual(response.suggestions[0]["v6_feedback"], "unavailable")
        self.assertEqual(len(response.suggestions), 1)

    def test_global_activation_requires_all_gates_and_supports_rollback(self):
        node = next(item for item in ast.parse(source).body
                    if isinstance(item, ast.FunctionDef) and item.name == "_v6_globally_ready")
        local = {"os": os, "_v6_access_authorizer": lambda *args: True,
                 "_v6_text_delivery_authorizer": lambda *args: True,
                 "_v6_guidance_store": types.SimpleNamespace(record_answer=lambda *args: None),
                 "_v6_semantic_judge": lambda *args: None}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     "<synthetic gate>", "exec"), local)
        policy.APPROVED_GUIDANCE["synthetic"] = {"test": True}
        keys = {"MICHAEL_V6_ENABLED": "0", "MICHAEL_V6_SIGNING_KEY": "s" * 32,
                "MICHAEL_V6_PROGRESS_KEY": "p" * 32}
        with patch.dict(os.environ, keys):
            self.assertFalse(local["_v6_globally_ready"](policy))
            os.environ["MICHAEL_V6_ENABLED"] = "1"
            self.assertTrue(local["_v6_globally_ready"](policy))
            local["_v6_semantic_judge"] = None
            self.assertFalse(local["_v6_globally_ready"](policy))
            local["_v6_semantic_judge"] = lambda *args: None
            os.environ["MICHAEL_V6_ENABLED"] = "0"
            self.assertFalse(local["_v6_globally_ready"](policy))

    def test_verified_binding_progression_and_failure_are_isolated(self):
        class MemoryStore:
            def __init__(self):
                self.events = {}
                self.levels = {}
            async def record_answer(self, scope, event_id, answer, verdict):
                key = tuple(scope[k] for k in ("principal", "delivery_session", "language", "question_id"))
                seen = (key, event_id)
                if seen not in self.events:
                    self.events[seen] = (answer, verdict)
                    current = self.levels.get(key, 0)
                    self.levels[key] = min(2, current + 1) if verdict == "incorrect" else 0 if verdict == "correct" else current
                elif self.events[seen][0] != answer:
                    return None
                return self.levels[key], self.events[seen][1]

        async def allow(user, request, session):
            return True

        namespace["_v6_access_authorizer"] = allow
        store = MemoryStore()
        namespace["_v6_guidance_store"] = store
        session = policy.delivery_session_id(self.token, "no")
        request = self.request()
        request.v6_actor_binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "synthetic-user")
        request.v6_event_id = "synthetic-event-0001"
        first = self.invoke(request, session)
        self.assertEqual(first.suggestions[0]["v6_feedback"], "incorrect")
        self.assertIn("prøv et annet alternativ", first.reply)
        self.assertEqual(self.invoke(request, session).reply, first.reply)
        request.v6_event_id = "synthetic-event-0002"
        second = self.invoke(request, session)
        self.assertIn("ett om gangen", second.reply)
        request.v6_answer_text = "uklart"
        request.v6_event_id = "synthetic-event-0003"
        self.assertEqual(self.invoke(request, session).suggestions[0]["v6_feedback"], "unknown")
        request.v6_actor_binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "another-user")
        self.assertEqual(self.invoke(request, session).suggestions[0]["v6_feedback"], "unavailable")
        request.v6_intent = "explain"
        self.assertEqual(self.invoke(request, session).suggestions[0]["v6_feedback"], "unavailable")
        self.assertEqual(len(store.events), 3)

    def test_semantic_proposal_is_opt_in_and_requires_valid_actor_and_event(self):
        class Store:
            def __init__(self): self.verdicts = []
            async def record_answer(self, scope, event, answer, verdict):
                self.verdicts.append(verdict)
                return 0, verdict
        calls = []
        async def allow(user, req, session): return True
        async def judge(messages):
            calls.append(messages)
            return json.dumps({"verdict": "correct", "evidence": "bilen er blå"})
        namespace["_v6_access_authorizer"] = allow
        namespace["_v6_guidance_store"] = Store()
        session = policy.delivery_session_id(self.token, "no")
        req = self.request(answer="Jeg tror bilen er blå")
        req.v6_actor_binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "synthetic-user")
        req.v6_event_id = "synthetic-event-0001"
        self.assertEqual(self.invoke(req, session).suggestions[0]["v6_feedback"], "unknown")
        namespace["_v6_semantic_judge"] = judge
        req.v6_event_id = "synthetic-event-0002"
        self.assertEqual(self.invoke(req, session).suggestions[0]["v6_feedback"], "correct")
        self.assertEqual(len(calls), 2)
        req.v6_actor_binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "other-user")
        self.assertEqual(self.invoke(req, session).suggestions[0]["v6_feedback"], "unavailable")
        self.assertEqual(len(calls), 2)
        req.v6_actor_binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "synthetic-user")
        req.v6_event_id = None
        self.assertEqual(self.invoke(req, session).suggestions[0]["v6_feedback"], "unavailable")
        self.assertEqual(len(calls), 2)

    def test_reviewed_hints_follow_the_selected_wrong_option(self):
        class Store:
            async def record_answer(self, scope, event, answer, verdict): return 1, verdict
        async def allow(user, req, session): return True
        self.question["options"].append({"id": "C", "text": {"no": "Hvit", "th": "สีขาว", "en": "White"}})
        digest = policy._content_digest(self.question)
        policy.APPROVED_CONTENT_DIGESTS["synthetic"] = digest
        policy.APPROVED_GUIDANCE["synthetic"] = {"question_digest": digest, "reviewer": "synthetic",
            "approval_reference": "synthetic-evidence", "reviewed_at": "2026-01-01T00:00:00Z",
            "reviewed_languages": ["no"], "confirmation": {"no": "Riktig, valget er blått."}, "options": {"no": {
            "A": {"hint": "Se på det røde valget.", "alternative": "Sammenlign det røde valget."},
            "C": {"hint": "Se på det hvite valget.", "alternative": "Sammenlign det hvite valget."},
        }}}
        self.token = policy.issue_delivery_token(self.question)
        namespace["_v6_access_authorizer"] = allow
        namespace["_v6_guidance_store"] = Store()
        namespace["_reply_matches_language_script"] = lambda text, lang: lang == "no"
        session = policy.delivery_session_id(self.token, "no")
        binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "synthetic-user")
        for answer, expected in (("Rød", "Se på det røde valget."), ("Hvit", "Se på det hvite valget.")):
            req = self.request(answer=answer)
            req.v6_actor_binding = binding
            req.v6_event_id = "synthetic-event-" + answer.ljust(16, "0")
            result = self.invoke(req, session)
            self.assertEqual(result.suggestions[0]["v6_feedback"], "incorrect")
            self.assertEqual(result.reply, expected)
        req = self.request(answer="Blå")
        req.v6_actor_binding, req.v6_event_id = binding, "synthetic-event-right"
        self.assertEqual(self.invoke(req, session).reply, "Riktig, valget er blått.")
        policy.APPROVED_GUIDANCE["synthetic"]["question_digest"] = "stale"
        req = self.request(answer="Rød")
        req.v6_actor_binding, req.v6_event_id = binding, "synthetic-event-stale"
        self.assertIn("Ikke helt", self.invoke(req, session).reply)

    def test_v6_bearer_verification_uses_server_identity_and_fresh_user(self):
        node = next(item for item in ast.parse(source).body
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == "_v6_verified_user")
        local = {"_db": {}}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     "<synthetic identity component>", "exec"), local)

        class Users:
            def __init__(self, rows):
                self.rows = rows
                self.queries = []
            def find(self, query, projection):
                self.queries.append((query, projection))
                return Cursor(self.rows)

        users = Users([{"id": "verified-user"}])
        local["_db"]["users"] = users
        server.JWT_SECRET = "synthetic-configured-key"
        server.verify_token = lambda token: {"sub": "verified-user"} if token == "valid-synthetic" else None
        request = types.SimpleNamespace(headers={"authorization": "Bearer valid-synthetic"})
        verify = lambda req: run_immediate(local["_v6_verified_user"](req))
        self.assertEqual(verify(request), {"id": "verified-user"})
        self.assertEqual(users.queries[0][0], {"id": "verified-user"})
        self.assertIsNone(verify(None))
        self.assertIsNone(verify(types.SimpleNamespace(headers={})))
        self.assertIsNone(verify(types.SimpleNamespace(headers={"authorization": "Bearer expired"})))
        server.JWT_SECRET = "fallback-secret-change-me"
        self.assertIsNone(verify(request))
        server.JWT_SECRET = "synthetic-configured-key"
        users.rows = [{"id": "verified-user"}, {"id": "verified-user"}]
        self.assertIsNone(verify(request))
        users.rows = []
        self.assertIsNone(verify(request))
        users.rows = [{"id": "verified-user", "disabled": True}]
        self.assertIsNone(verify(request))
        users.rows = [{"id": "verified-user", "deleted_at": "2026-01-01T00:00:00Z"}]
        self.assertIsNone(verify(request))

    def test_disabled_text_entry_and_synthetic_delivery(self):
        node = next(item for item in ast.parse(source).body
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == "teacher_v6_text_start")
        node.decorator_list = []

        class TextResponse:
            def __init__(self, **kwargs):
                self.ready = kwargs.pop("ready", False)
                self.__dict__.update(kwargs)

        local = {"V6TextStartRequest": object, "V6TextStartResponse": TextResponse,
                 "Request": object, "secrets": secrets, "_db": {"questions": collection},
                 "_v6_verified_user": synthetic_verified_user, "_v6_text_delivery_authorizer": None}
        local["_v6_globally_ready"] = lambda policy: (callable(local["_v6_text_delivery_authorizer"])
            and callable(getattr(local.get("_v6_guidance_store"), "record_answer", None)))
        local["_v6_content_ready"] = lambda policy, question_id, question: True
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     "<synthetic text entry>", "exec"), local)
        req = types.SimpleNamespace(language="no")
        invoke = lambda: run_immediate(local["teacher_v6_text_start"](req, object()))
        self.assertFalse(invoke().ready)

        async def allow_test_only(user, request):
            return True
        local["_v6_text_delivery_authorizer"] = allow_test_only
        self.assertFalse(invoke().ready)  # Delivery is closed without a progress store.
        local["_v6_guidance_store"] = types.SimpleNamespace(record_answer=lambda *args: None)
        delivery = invoke()
        self.assertTrue(delivery.ready)
        self.assertEqual(delivery.question_id, "synthetic")
        self.assertEqual(delivery.question, "Oppgave")
        self.assertEqual(set(delivery.choices), {"Rød", "Blå"})
        self.assertTrue(policy.verify_delivery_token(delivery.delivery_token, "synthetic", self.question))
        self.assertTrue(policy.verify_actor_binding(delivery.actor_binding, delivery.delivery_token, "synthetic-user"))
        self.assertEqual(delivery.session_id, policy.delivery_session_id(delivery.delivery_token, "no"))
        self.assertFalse(hasattr(delivery, "correct_text"))
        collection.rows = [self.question, self.question]
        self.assertFalse(invoke().ready)
        collection.rows = [self.question]
        self.question["bildeUrl"] = "/synthetic.png"
        self.assertFalse(invoke().ready)

        async def deny_test_only(user, request):
            return False
        local["_v6_text_delivery_authorizer"] = deny_test_only
        self.assertFalse(invoke().ready)

    def test_language_session_and_client_hint_level_is_ignored(self):
        async def allow_test_only(user, req, session):
            return True
        class FixedStore:
            async def record_answer(self, scope, event_id, answer, verdict):
                return 0, verdict
        namespace["_v6_access_authorizer"] = allow_test_only
        namespace["_v6_guidance_store"] = FixedStore()
        binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "synthetic-user")
        for lang, wrong in (("no", "Rød"), ("th", "สีแดง"), ("en", "Red")):
            session = policy.delivery_session_id(self.token, lang)
            self.assertNotEqual(session, policy.delivery_session_id(self.token, {"no": "en", "en": "th", "th": "no"}[lang]))
            requests = [self.request(lang, wrong, level) for level in range(3)]
            for request in requests:
                request.v6_actor_binding = binding
                request.v6_event_id = "synthetic-event-0001"
            replies = [self.invoke(request, session) for request in requests]
            self.assertEqual(len({reply.reply for reply in replies}), 1)
            self.assertTrue(all(reply.suggestions[0]["v6_feedback"] == "incorrect" for reply in replies))
            self.assertTrue(all(len(reply.suggestions) == 3 for reply in replies))
            wrong_session = self.invoke(self.request(lang, wrong), "wrong-session")
            self.assertEqual(wrong_session.suggestions[0]["v6_feedback"], "unavailable")

    def test_access_without_persistent_store_fails_closed(self):
        async def allow_test_only(user, req, session):
            return True
        namespace["_v6_access_authorizer"] = allow_test_only
        session = policy.delivery_session_id(self.token, "no")
        self.assertEqual(self.invoke(self.request(), session).suggestions[0]["v6_feedback"], "unavailable")

    def test_access_error_fails_closed(self):
        async def deny_by_error(user, req, session):
            raise RuntimeError("synthetic error")
        namespace["_v6_access_authorizer"] = deny_by_error
        session = policy.delivery_session_id(self.token, "no")
        self.assertEqual(self.invoke(self.request(), session).suggestions[0]["v6_feedback"], "unavailable")

    def test_proposed_actor_binding_cannot_be_transferred(self):
        binding = policy.issue_verified_actor_binding(
            self.token, "synthetic", self.question, "verified-user-a")
        self.assertIsNotNone(binding)
        self.assertTrue(policy.verify_actor_binding(binding, self.token, "verified-user-a"))
        self.assertFalse(policy.verify_actor_binding(binding, self.token, "verified-user-b"))
        second_token = policy.issue_delivery_token(self.question)
        self.assertFalse(policy.verify_actor_binding(binding, second_token, "verified-user-a"))
        parts = binding.split(".")
        parts[1] = ("A" if parts[1][0] != "A" else "B") + parts[1][1:]
        self.assertFalse(policy.verify_actor_binding(".".join(parts), self.token, "verified-user-a"))
        self.assertIsNone(policy.issue_verified_actor_binding(self.token, "other", self.question, "verified-user-a"))
        self.assertIsNone(policy.issue_verified_actor_binding(self.token, "synthetic", self.question, ""))

    def test_unwired_premium_adapter_checks_fresh_status_and_actor(self):
        node = next(item for item in ast.parse(source).body
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == "_v6_premium_test_authorizer")
        local = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     "<synthetic premium component>", "exec"), local)
        server._user_has_active_premium = lambda user: user.get("current_premium") is True
        binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "verified-user-a")
        req = types.SimpleNamespace(v6_actor_binding=binding, v6_delivery_token=self.token, language="no")
        session = policy.delivery_session_id(self.token, "no")
        check = lambda user: run_immediate(local["_v6_premium_test_authorizer"](user, req, session))
        self.assertTrue(check({"id": "verified-user-a", "current_premium": True}))
        self.assertFalse(check({"id": "verified-user-a", "current_premium": False}))
        self.assertFalse(check({"id": "verified-user-b", "current_premium": True}))
        self.assertFalse(check({"id": "verified-user-a"}))
        req.v6_actor_binding = None
        self.assertFalse(check({"id": "verified-user-a", "current_premium": True}))

    def test_unwired_preview_and_answer_access_stays_closed_without_completed_proof(self):
        selected = {"_v6_existing_preview_check", "_v6_existing_access_check", "_v6_premium_test_authorizer"}
        nodes = [item for item in ast.parse(source).body
                 if isinstance(item, ast.AsyncFunctionDef) and item.name in selected]
        local = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])),
                     "<synthetic access adapters>", "exec"), local)
        reads = []
        async def read_usage(user, device):
            reads.append((user["id"], device))
            return {"synthetic": True}
        server._get_access_usage = read_usage
        server._access_policy_payload = lambda user, usage: {"can_answer": user.get("can_answer") is True}
        server._user_has_active_premium = lambda user: user.get("current_premium") is True
        binding = policy.issue_verified_actor_binding(self.token, "synthetic", self.question, "verified-user-a")
        session = policy.delivery_session_id(self.token, "no")
        req = types.SimpleNamespace(v6_actor_binding=binding, v6_delivery_token=self.token,
                                    language="no", v6_intent="start")
        premium = {"id": "verified-user-a", "current_premium": True, "can_answer": True}
        free = {"id": "verified-user-a", "current_premium": False, "can_answer": True}
        check = lambda user: run_immediate(local["_v6_existing_access_check"](user, req, session))
        self.assertTrue(check(premium))
        self.assertFalse(check(free))  # a preview must not lead to a paid-but-blocked answer
        self.assertTrue(reads)  # read-only status, not a consume operation
        req.v6_intent = "answer"
        self.assertTrue(check(premium))
        self.assertFalse(check(free))  # an incomplete event cannot prove quota completion
        req.v6_intent = "explain"
        self.assertFalse(check(free))
        self.assertFalse(check({"id": "verified-user-b", "current_premium": True, "can_answer": True}))
        self.assertFalse(run_immediate(local["_v6_existing_preview_check"](None, None)))
        server._access_policy_payload = lambda user, usage: {"can_answer": False}
        req.v6_intent = "start"
        self.assertFalse(check(premium))

    def test_proposed_verified_guidance_history(self):
        class FakeAtomicHistory:
            def __init__(self):
                self.levels = {}
                self.events = {}

            async def advance_once(self, scope, event_id, verdict):
                key = (scope["principal"], scope["delivery_session"], scope["language"], scope["question_id"])
                event_key = (key, event_id)
                if event_key in self.events:
                    return self.levels[key]
                current = self.levels.get(key, 0)
                next_level = min(2, current + 1) if verdict == "incorrect" else 0 if verdict == "correct" else current
                self.levels[key] = next_level
                self.events[event_key] = next_level
                return next_level

        async def verified_identity(context):
            return {"first": "verified-user-a", "second": "verified-user-b"}.get(context)

        history = FakeAtomicHistory()

        def advance(context, event, verdict, *, lang="no", verifier=verified_identity, store=history, token=None):
            return run_immediate(policy.verified_guidance_level(
                verifier, store, context, self.token if token is None else token,
                "synthetic", self.question, lang, verdict, event))

        first = "synthetic-event-0001"
        self.assertEqual(advance("first", first, "incorrect"), 1)
        self.assertEqual(advance("first", first, "incorrect"), 1)  # idempotent retry
        self.assertEqual(advance("first", "synthetic-event-0002", "incorrect"), 2)
        self.assertEqual(advance("first", first, "incorrect"), 2)  # stale retry cannot roll state back
        self.assertEqual(advance("first", "synthetic-event-0003", "unknown"), 2)
        self.assertEqual(advance("second", "synthetic-event-0004", "unknown"), 0)
        self.assertEqual(advance("first", "synthetic-event-0005", "unknown", lang="en"), 0)
        self.assertEqual(advance("first", "synthetic-event-0006", "correct"), 0)
        self.assertIsNone(advance("no-identity", "synthetic-event-0007", "incorrect"))
        self.assertIsNone(advance("first", "synthetic-event-0008", "incorrect", store=None))
        self.assertIsNone(advance("first", "synthetic-event-0009", "incorrect", verifier=None))
        self.assertIsNone(advance("first", "short", "incorrect"))
        self.assertIsNone(advance("first", "synthetic-event-0010", "incorrect", token="invalid"))

        class BrokenHistory:
            async def advance_once(self, scope, event_id, verdict):
                raise RuntimeError("synthetic storage failure")

        self.assertIsNone(advance("first", "synthetic-event-0011", "incorrect", store=BrokenHistory()))

    def test_proposed_read_only_consumption_contract(self):
        async def identity(context):
            return {"alice": "verified-alice", "bob": "verified-bob"}.get(context)

        class SyntheticEvents:
            def __init__(self, rows):
                self.rows = rows
                self.find_calls = 0
            def find(self, query):
                self.find_calls += 1
                return Cursor([row for row in self.rows if all(row.get(k) == v for k, v in query.items())])

        event = {
            "event_id": "synthetic-consumption", "scope": "user", "key": "verified-alice",
            "user_id": "verified-alice", "question_id": "synthetic",
            "v6_delivery_fingerprint": hashlib.sha256(self.token.encode("ascii")).hexdigest(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        events = SyntheticEvents([event])

        def check(context="alice", store=events, event_id="synthetic-consumption", verifier=identity):
            return run_immediate(policy.verified_consumption_principal(
                verifier, store, context, self.token, "synthetic", self.question, event_id))

        self.assertEqual(check(), "verified-alice")
        self.assertIsNone(check("bob"))
        self.assertIsNone(check("guest"))
        self.assertIsNone(check(verifier=None))
        self.assertIsNone(check(store=None))
        self.assertIsNone(check(event_id="other"))
        self.assertIsNone(check(store=SyntheticEvents([event, event])))
        missing_binding = dict(event)
        missing_binding.pop("v6_delivery_fingerprint")
        self.assertIsNone(check(store=SyntheticEvents([missing_binding])))
        old = dict(event, created_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat())
        self.assertIsNone(check(store=SyntheticEvents([old])))
        bad_time = dict(event, created_at="invalid")
        self.assertIsNone(check(store=SyntheticEvents([bad_time])))
        self.assertEqual(events.find_calls, 3)

    def test_proposed_existing_event_bound_to_signed_delivery(self):
        async def identity(context):
            return {
                "user": {"scope": "user", "key": "verified-user"},
                "other-user": {"scope": "user", "key": "other-user"},
                "guest": {"scope": "guest", "key": "verified-guest-capability"},
            }.get(context)

        class SyntheticEvents:
            def __init__(self, rows):
                self.rows = rows
                self.find_calls = 0
            def find(self, query):
                self.find_calls += 1
                return Cursor([row for row in self.rows if all(row.get(k) == v for k, v in query.items())])

        event_id = policy.delivery_consumption_event_id(self.token, "synthetic", self.question)
        self.assertTrue(event_id.startswith("v6:"))
        self.assertIsNone(policy.delivery_consumption_event_id("bad", "synthetic", self.question))
        event = {"event_id": event_id, "scope": "user", "key": "verified-user",
                 "user_id": "verified-user", "question_id": "synthetic",
                 "created_at": datetime.now(timezone.utc).isoformat()}

        def check(context, rows, verifier=identity, token=None):
            store = SyntheticEvents(rows)
            result = run_immediate(policy.verified_existing_consumption(
                verifier, store, context, self.token if token is None else token,
                "synthetic", self.question))
            return result, store.find_calls

        self.assertEqual(check("user", [event])[0], {"scope": "user", "key": "verified-user"})
        self.assertIsNone(check("other-user", [event])[0])
        self.assertIsNone(check("unknown", [event])[0])
        self.assertIsNone(check("user", [], verifier=None)[0])
        self.assertIsNone(check("user", [event, event])[0])
        self.assertIsNone(check("user", [event], token="bad")[0])
        guest_event = dict(event, scope="guest", key="verified-guest-capability", user_id=None)
        self.assertEqual(check("guest", [guest_event])[0], {"scope": "guest", "key": "verified-guest-capability"})
        self.assertIsNone(check("user", [guest_event])[0])
        old = dict(event, created_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat())
        self.assertIsNone(check("user", [old])[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
