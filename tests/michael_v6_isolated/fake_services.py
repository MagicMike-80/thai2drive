"""Fail-closed services to install only AFTER OS-level isolation is proven.

Never call this in a process holding real credentials. This is defense in depth,
not a network sandbox, and is not wired to bootstrap while review is pending.
"""
import sys
import types


def install():
    class UnexpectedCollection:
        def __getattr__(self, name):
            raise AssertionError("Unexpected synthetic database operation: " + name)

    class SyntheticDatabase:
        def __getitem__(self, name):
            if name not in ("teacher_chats", "teacher_feedback"):
                raise AssertionError("Unexpected import-time database collection: " + str(name))
            return UnexpectedCollection()

        def __getattr__(self, name):
            raise AssertionError("Unexpected import-time database access: " + name)

    class SyntheticClient:
        def __init__(self, *args, **kwargs):
            pass

        def __getitem__(self, name):
            return SyntheticDatabase()

    motor = types.ModuleType("motor")
    motor_asyncio = types.ModuleType("motor.motor_asyncio")
    motor_asyncio.AsyncIOMotorClient = SyntheticClient
    motor.motor_asyncio = motor_asyncio

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda *args, **kwargs: False

    litellm = types.ModuleType("litellm")
    async def forbidden_model(*args, **kwargs):
        raise AssertionError("Unexpected model call")
    litellm.acompletion = forbidden_model
    litellm.suppress_debug_info = True

    smtp = types.ModuleType("smtplib")
    def forbidden_smtp(*args, **kwargs):
        raise AssertionError("Unexpected SMTP call")
    smtp.SMTP = forbidden_smtp
    smtp.SMTP_SSL = forbidden_smtp

    sys.modules.update({"motor": motor, "motor.motor_asyncio": motor_asyncio,
                        "dotenv": dotenv, "litellm": litellm, "smtplib": smtp})


def install_network_audit_guard(*, allow_test_mongo=False):
    """Deny external network and child processes; optionally allow loopback Mongo only."""
    def guard(event, args):
        if allow_test_mongo and event in ("socket.connect", "socket.connect_ex"):
            address = args[1] if len(args) > 1 else None
            if isinstance(address, tuple) and len(address) >= 2 and address[:2] == ("127.0.0.1", 27017):
                return
        if allow_test_mongo and event == "socket.getaddrinfo":
            if len(args) >= 2 and args[0] == "127.0.0.1" and str(args[1]) == "27017":
                return
        if event in ("socket.connect", "socket.connect_ex", "socket.sendto",
                     "socket.getaddrinfo", "socket.gethostbyname", "os.system"):
            raise RuntimeError("Unexpected network or shell operation")
        if event.startswith(("subprocess.", "os.spawn", "os.exec")):
            raise RuntimeError("Unexpected child process operation")
    sys.addaudithook(guard)
