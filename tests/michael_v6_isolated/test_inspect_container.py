"""Validate inspector logic using synthetic Docker metadata only."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("v6_inspect", Path(__file__).with_name("inspect_container.py"))
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def record(source):
    return {
        "Image": "sha256:synthetic",
        "HostConfig": {"NetworkMode": "none", "Privileged": False, "ReadonlyRootfs": True,
                       "CapDrop": ["ALL"], "CapAdd": None, "SecurityOpt": ["no-new-privileges:true"],
                       "PidMode": "", "IpcMode": "private", "UTSMode": "",
                       "Devices": [], "Links": None, "VolumesFrom": None,
                       "PidsLimit": 128, "Memory": 1073741824, "NanoCpus": 2000000000,
                       "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=512m"}},
        "Mounts": [{"Type": "bind", "Destination": "/sandbox/input", "RW": False, "Source": source}],
        "Config": {"User": "65534:65534", "WorkingDir": "/sandbox/input", "Entrypoint": ["/usr/bin/env"],
                   "Cmd": ["-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/tmp", "TMPDIR=/tmp", "LANG=C.UTF-8",
                           "PYTHONDONTWRITEBYTECODE=1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                           "MICHAEL_TEST_MODE=synthetic", "/usr/local/bin/python", "-I", "-B",
                           "/sandbox/input/tests/michael_v6_isolated/bootstrap.py"]}}


class InspectorTests(unittest.TestCase):
    def test_accepts_expected_configuration(self):
        inspector.validate(record("synthetic-input"), "synthetic-input", "sha256:synthetic")

    def test_rejects_changed_isolation_settings(self):
        for key, value in (("NetworkMode", "host"), ("Privileged", True), ("ReadonlyRootfs", False),
                           ("CapDrop", []), ("SecurityOpt", []), ("PidMode", "host"),
                           ("SecurityOpt", ["no-new-privileges:true", "seccomp=unconfined"]),
                           ("Devices", ["synthetic-device"]), ("PidsLimit", 0), ("Tmpfs", {})):
            item = record("synthetic-input")
            item["HostConfig"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                inspector.validate(item, "synthetic-input", "sha256:synthetic")
        item = record("synthetic-input")
        del item["HostConfig"]["IpcMode"]
        with self.assertRaises(ValueError):
            inspector.validate(item, "synthetic-input", "sha256:synthetic")

    def test_rejects_extra_mount_and_changed_command(self):
        for change in ("extra_mount", "writeable", "source", "image", "command", "user"):
            item = record("synthetic-input")
            if change == "extra_mount": item["Mounts"].append(copy.deepcopy(item["Mounts"][0]))
            elif change == "writeable": item["Mounts"][0]["RW"] = True
            elif change == "source": item["Mounts"][0]["Source"] = "other-input"
            elif change == "image": item["Image"] = "sha256:other"
            elif change == "command": item["Config"]["Cmd"].append("unexpected")
            else: item["Config"]["User"] = "0:0"
            with self.subTest(change=change), self.assertRaises(ValueError):
                inspector.validate(item, "synthetic-input", "sha256:synthetic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
