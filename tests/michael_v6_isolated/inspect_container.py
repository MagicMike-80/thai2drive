"""Inspect docker create's configuration before starting its entrypoint.

Candidate for reviewed GitHub-hosted runners only. Input JSON comes from
`docker inspect`; never changes Docker state or starts the container.
"""
import json
from pathlib import Path
import sys


def validate(record, source, image_id):
    if not isinstance(record, dict):
        raise ValueError("Missing container record")
    host = record.get("HostConfig") or {}
    config = record.get("Config") or {}
    required_host = {"NetworkMode", "Privileged", "ReadonlyRootfs", "CapDrop", "CapAdd", "SecurityOpt",
                     "PidMode", "IpcMode", "UTSMode", "Devices", "Links", "VolumesFrom",
                     "PidsLimit", "Memory", "NanoCpus", "Tmpfs"}
    required_config = {"User", "Entrypoint", "Cmd", "WorkingDir"}
    if not required_host.issubset(host) or not required_config.issubset(config):
        raise ValueError("Container metadata is incomplete")
    if (host.get("NetworkMode") != "none" or host.get("Privileged") is not False
            or host.get("ReadonlyRootfs") is not True or config.get("User") != "65534:65534"):
        raise ValueError("Isolation settings do not match")
    if host.get("CapDrop") != ["ALL"] or host.get("CapAdd"):
        raise ValueError("Capabilities are not restricted")
    if host.get("SecurityOpt") != ["no-new-privileges:true"]:
        raise ValueError("No-new-privileges is missing")
    if host.get("PidMode") != "" or host.get("IpcMode") not in ("private", "shareable") or host.get("UTSMode") != "":
        raise ValueError("Host namespace is forbidden")
    if host.get("Devices") or host.get("Links") or host.get("VolumesFrom"):
        raise ValueError("Unexpected host devices, links, or volumes")
    if host.get("PidsLimit") != 128 or host.get("Memory") != 1073741824 or host.get("NanoCpus") != 2000000000:
        raise ValueError("Resource limits do not match")
    tmpfs = host.get("Tmpfs") or {}
    if set(tmpfs) != {"/tmp"} or not {"rw", "nosuid", "nodev", "noexec", "size=128m"}.issubset(set(tmpfs["/tmp"].split(","))):
        raise ValueError("Temporary filesystem does not match")
    mounts = record.get("Mounts") or []
    if len(mounts) != 1:
        raise ValueError("Exactly one input bind mount is required")
    mount = mounts[0]
    if (mount.get("Type") != "bind" or mount.get("Destination") != "/sandbox/input"
            or mount.get("RW") is not False
            or Path(mount.get("Source", "")).resolve() != Path(source).resolve()):
        raise ValueError("Unexpected input mount")
    if record.get("Image") != image_id:
        raise ValueError("Container is not using the built image")
    expected_entrypoint = ["/usr/bin/env"]
    expected_args = ["-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/tmp", "TMPDIR=/tmp", "LANG=C.UTF-8",
                     "PYTHONDONTWRITEBYTECODE=1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                     "MICHAEL_TEST_MODE=synthetic", "/usr/local/bin/python", "-I", "-B",
                     "/sandbox/input/tests/michael_v6_isolated/bootstrap.py"]
    if config.get("Entrypoint") != expected_entrypoint or config.get("Cmd") != expected_args:
        raise ValueError("Unexpected entrypoint or test environment")
    if config.get("WorkingDir") != "/sandbox/input":
        raise ValueError("Unexpected working directory")


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: inspect_container.py INSPECT_JSON INPUT IMAGE_ID")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 1:
        raise ValueError("Expected exactly one container")
    validate(data[0], sys.argv[2], sys.argv[3])
    print("Docker configuration passed the candidate pre-start inspection")


if __name__ == "__main__":
    main()
