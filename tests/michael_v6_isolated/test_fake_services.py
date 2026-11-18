"""Test only the fakes; never imports application modules or real services."""
import importlib.util
from pathlib import Path
import socket
import sys
import unittest

spec = importlib.util.spec_from_file_location("v6_fake_services", Path(__file__).with_name("fake_services.py"))
fakes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fakes)
fakes.install()
fakes.install_network_audit_guard()


class FakeServicesTests(unittest.TestCase):
    def test_import_only_database_fails_on_reads(self):
        from motor.motor_asyncio import AsyncIOMotorClient
        db = AsyncIOMotorClient("synthetic")["synthetic"]
        with self.assertRaises(AssertionError):
            db["questions"]
        with self.assertRaises(AssertionError):
            db["teacher_chats"].find

    def test_dotenv_and_smtp_are_fake(self):
        from dotenv import load_dotenv
        import smtplib
        self.assertFalse(load_dotenv())
        with self.assertRaises(AssertionError):
            smtplib.SMTP("synthetic.invalid")

    def test_external_connection_is_denied_before_network(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with self.assertRaises(RuntimeError):
                sock.connect(("192.0.2.1", 443))
        finally:
            sock.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
