"""Synthetic checks of the gate; this never imports application code."""
import importlib.util
import errno
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

path = Path(__file__).with_name("bootstrap.py")
spec = importlib.util.spec_from_file_location("v6_bootstrap_gate", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class BootstrapChecks(unittest.TestCase):
    def test_mongo_guard_allows_only_expected_loopback(self):
        fake_spec = importlib.util.spec_from_file_location("v6_fake_guard", path.with_name("fake_services.py"))
        fakes = importlib.util.module_from_spec(fake_spec)
        fake_spec.loader.exec_module(fakes)
        captured = []
        with patch.object(fakes.sys, "addaudithook", side_effect=captured.append):
            fakes.install_network_audit_guard(allow_test_mongo=True)
        guard = captured[0]
        guard("socket.connect", (None, ("127.0.0.1", 27017)))
        guard("socket.getaddrinfo", ("127.0.0.1", 27017))
        for event, args in (("socket.connect", (None, ("127.0.0.1", 27018))),
                            ("socket.connect", (None, ("192.0.2.1", 27017))),
                            ("socket.getaddrinfo", ("example.invalid", 27017)),
                            ("socket.sendto", (None, ("127.0.0.1", 27017)))):
            with self.subTest(event=event, args=args), self.assertRaises(RuntimeError):
                guard(event, args)

    def test_environment_fails_closed(self):
        clean = dict(gate.EXPECTED_ENV)
        gate.check_environment(clean)
        for bad in ({}, {**clean, "MONGO_URL": "redacted"}, {**clean, "HOME": "/home/user"}):
            with self.subTest(keys=sorted(bad)), self.assertRaises(RuntimeError):
                gate.check_environment(bad)

    def test_interfaces(self):
        gate.check_interfaces(["lo"])
        for bad in ([], ["lo", "eth0"]):
            with self.subTest(names=bad), self.assertRaises(RuntimeError):
                gate.check_interfaces(bad)

    def test_routes(self):
        v4 = "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\n"
        v6 = "00000000000000000000000000000000 00 00000000000000000000000000000000 00 00000000000000000000000000000000 00000000 00000000 00000000 00000000 lo\n"
        gate.check_routes(v4, v6)
        for bad4, bad6 in (("", v6), (v4, ""), (v4 + "eth0 0 0 0 0 0 0 0\n", v6),
                           (v4, v6.replace(" lo", " eth0"))):
            with self.subTest(v4=bad4, v6=bad6), self.assertRaises(RuntimeError):
                gate.check_routes(bad4, bad6)

    def test_mounts_rejects_write_access_and_sockets(self):
        root = "1 0 0:1 / / ro - overlay overlay ro\n"
        input_mount = "2 1 0:2 / /sandbox/input ro - bind bind ro\n"
        # Paths are checked only for known forbidden files; no app files imported.
        gate.check_mounts(root + input_mount)
        for mounts in (root, root.replace(" ro ", " rw ") + input_mount,
                       root + input_mount + "3 1 0:3 / /var/run/docker.sock rw - bind bind rw\n"):
            with self.subTest(mounts=mounts), self.assertRaises(RuntimeError):
                gate.check_mounts(mounts)

    def test_network_probe_requires_unreachable_tcp_and_dns(self):
        class FakeSocket:
            def __init__(self, kind, unsafe=False):
                self.kind, self.unsafe = kind, unsafe
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def settimeout(self, value): pass
            def connect_ex(self, address):
                return 0 if self.unsafe else errno.ENETUNREACH
            def sendto(self, data, address):
                raise OSError(errno.ENETUNREACH, "synthetic unreachable")

        class FakeNetworking:
            AF_INET, AF_INET6, SOCK_STREAM, SOCK_DGRAM = 1, 2, 3, 4
            def __init__(self, unsafe=False): self.unsafe = unsafe
            def socket(self, family, kind): return FakeSocket(kind, self.unsafe)

        gate.check_no_external_connectivity(FakeNetworking())
        with self.assertRaises(RuntimeError):
            gate.check_no_external_connectivity(FakeNetworking(unsafe=True))

    def test_input_manifest_requires_exact_set(self):
        expected = gate.ALLOWED_INPUT_FILES
        try:
            gate.ALLOWED_INPUT_FILES = {"backend/synthetic.py"}
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / "backend").mkdir()
                target = root / "backend" / "synthetic.py"
                target.write_text("synthetic", encoding="utf-8")
                gate.check_input_files(root)
                (root / "extra.env").write_text("synthetic", encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    gate.check_input_files(root)
        finally:
            gate.ALLOWED_INPUT_FILES = expected

    def test_unverified_environment_stops_before_app_import(self):
        with self.assertRaisesRegex(RuntimeError, "non-root Linux container"):
            gate.run_integration_after_review()


if __name__ == "__main__":
    unittest.main(verbosity=2)
