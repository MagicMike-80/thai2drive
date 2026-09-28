"""
"Send message to real Michael" — human handoff from the AI chat.
--------------------------------------------------------------------
POST /teacher/contact-human reuses teacher_chat.py's existing
send_admin_alert_email() SMTP helper (already used for one other admin
alert) rather than duplicating email infrastructure or reaching into
support_chat.py's AI-escalation-shaped function. It never raises to the
caller on a delivery failure — the student always gets a clear ok/sent
response, and every attempt (sent or not) is logged to Mongo for follow-up.

Runs fully offline: send_admin_alert_email is monkeypatched (no real
network/SMTP calls), and _db is a fake in-memory collection.
"""
import asyncio
import sys
import unittest
from pathlib import Path

import pydantic

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.teacher_chat as tc
from backend.teacher_chat import ContactHumanRequest


class _RecordingCollection:
    def __init__(self):
        self.inserted = []

    async def insert_one(self, doc):
        self.inserted.append(doc)


class ContactHumanEndpointTests(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        self._orig_send = tc.send_admin_alert_email
        tc._db = {"teacher_human_requests": _RecordingCollection()}

    def tearDown(self):
        tc._db = self._orig_db
        tc.send_admin_alert_email = self._orig_send

    def test_unsupported_language_is_rejected_by_the_model_itself(self):
        # Same guarantee TeacherChatRequest relies on: Literal["no","th","en"]
        # rejects anything else before the endpoint ever runs.
        with self.assertRaises(pydantic.ValidationError):
            ContactHumanRequest(message="Hjelp meg", language="xx")

    def test_successful_send_is_reported_and_logged(self):
        calls = []

        def fake_send(subject, body):
            calls.append((subject, body))
            return True, "sent to lexuz.zxc@gmail.com"

        tc.send_admin_alert_email = fake_send
        req = ContactHumanRequest(message="Jeg trenger hjelp fra en ekte lærer", language="no", device_id="d1")
        response = asyncio.run(tc.teacher_contact_human(req))

        self.assertTrue(response.ok)
        self.assertTrue(response.sent)
        self.assertEqual(len(calls), 1)
        self.assertIn("Jeg trenger hjelp fra en ekte lærer", calls[0][1])

        log = tc._db["teacher_human_requests"].inserted
        self.assertEqual(len(log), 1)
        self.assertTrue(log[0]["email_sent"])
        self.assertEqual(log[0]["language"], "no")

    def test_delivery_failure_is_reported_not_raised(self):
        def fake_send(subject, body):
            return False, "SMTP not configured — logged only"

        tc.send_admin_alert_email = fake_send
        req = ContactHumanRequest(message="ช่วยด้วยครับ", language="th", user_id="u1")
        response = asyncio.run(tc.teacher_contact_human(req))

        self.assertTrue(response.ok)
        self.assertFalse(response.sent)
        log = tc._db["teacher_human_requests"].inserted
        self.assertFalse(log[0]["email_sent"])

    def test_session_id_is_generated_when_not_provided(self):
        def fake_send(subject, body):
            return True, "sent"

        tc.send_admin_alert_email = fake_send
        req = ContactHumanRequest(message="Help please", language="en")
        response = asyncio.run(tc.teacher_contact_human(req))

        log = tc._db["teacher_human_requests"].inserted
        self.assertTrue(log[0]["session_id"])


if __name__ == "__main__":
    unittest.main()
