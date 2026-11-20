"""Fail-closed isolated integration bootstrap, with a disposable loopback database.

The workflow must inspect the Docker configuration before starting this file.
All in-container checks run again before any application import.
"""
from pathlib import Path
import errno
import os
import socket
import sys

INPUT = Path("/sandbox/input")
EXPECTED_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/tmp", "TMPDIR": "/tmp",
                "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1",
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "MICHAEL_TEST_MODE": "synthetic"}
ALLOWED_INPUT_FILES = {
    "backend/server.py", "backend/teacher_chat.py", "backend/michael_v6_policy.py", "backend/ai_learning.py",
    "backend/michael_v6_quota.py", "backend/michael_v6_stop_sign.json",
    "backend/michael_greetings.py", "backend/media_catalog.py",
    "backend/webapp.py", "backend/site_config.py", "backend/i18n_routing.py",
    "backend/stopping_distance_web.py", "backend/studybook_web.py",
    "backend/learning_areas.json", "backend/regelbank.json",
    "backend/docs/1_JURIDISK_TRAFIKKFASIT_2026.md",
    "backend/docs/2_MICHAEL_PEDAGOGIKK_OG_GATELOGIKK_2026.md",
    "backend/docs/3_NORSK_THAI_FELLEORD_OG_KULTUR_2026.md",
    "tests/michael_v6_isolated/bootstrap.py", "tests/michael_v6_isolated/fake_services.py",
    "tests/michael_v6_isolated/v6_endpoint_scenarios.py",
    "tests/michael_v6_isolated/stop_sign_candidate_v1.json",
    "tests/michael_v6_isolated/stop_sign_dialogues.json",
}
ALLOWED_MOUNTS = {
    "/", "/proc", "/dev", "/dev/pts", "/sys", "/sys/fs/cgroup", "/dev/mqueue",
    "/dev/shm", "/etc/resolv.conf", "/etc/hostname", "/etc/hosts", "/proc/bus",
    "/proc/fs", "/proc/irq", "/proc/sys", "/proc/sysrq-trigger", "/proc/acpi",
    "/proc/interrupts", "/proc/kcore", "/proc/keys", "/proc/latency_stats",
    "/proc/timer_list", "/proc/scsi", "/sys/firmware", "/tmp", "/sandbox/input",
}


def check_environment(env):
    if dict(env) != EXPECTED_ENV:
        raise RuntimeError("Environment does not match the synthetic allowlist")


def check_interfaces(names):
    if set(names) != {"lo"}:
        raise RuntimeError("Only the loopback interface is allowed")


def check_routes(ipv4, ipv6):
    # No non-loopback IPv4 routes; malformed entries fail closed.
    lines = ipv4.splitlines()
    if not lines or not lines[0].startswith("Iface"):
        raise RuntimeError("Cannot verify IPv4 routes")
    for row in lines[1:]:
        fields = row.split()
        if len(fields) < 8 or fields[0] != "lo":
            raise RuntimeError("Non-loopback or unreadable IPv4 route")
    # Linux may show an unreachable default IPv6 route on lo, but any route
    # bound to another interface breaks the isolation requirement.
    if not ipv6.strip():
        raise RuntimeError("Cannot verify IPv6 routes")
    for row in ipv6.splitlines():
        fields = row.split()
        if len(fields) != 10 or fields[-1] != "lo":
            raise RuntimeError("Non-loopback or unreadable IPv6 route")


def check_mounts(text):
    root_ro = False
    input_ro = False
    for row in text.splitlines():
        parts = row.split()
        if len(parts) < 10 or "-" not in parts:
            raise RuntimeError("Cannot parse mount information")
        point = parts[4]
        flags = set(parts[5].split(","))
        if point not in ALLOWED_MOUNTS:
            raise RuntimeError("Unexpected mount point")
        if point == "/":
            root_ro = "ro" in flags
        if point == "/sandbox/input":
            input_ro = "ro" in flags
        if point in ("/var/run/docker.sock", "/run/docker.sock"):
            raise RuntimeError("Docker socket is mounted")
    if not root_ro or not input_ro:
        raise RuntimeError("Root and input must be mounted read-only")
    for forbidden in (INPUT / ".env", INPUT / "backend/.env", INPUT / ".git",
                      Path("/var/run/docker.sock"), Path("/run/docker.sock")):
        if forbidden.exists():
            raise RuntimeError("A forbidden path is accessible")


def check_input_files(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("Input directory is missing or is a symlink")
    found = set()
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            if (Path(parent) / name).is_symlink():
                raise RuntimeError("Input symlink is forbidden")
        for name in files:
            path = Path(parent) / name
            if path.is_symlink() or not path.is_file():
                raise RuntimeError("Input file must be a regular file")
            found.add(path.relative_to(root).as_posix())
    if found != ALLOWED_INPUT_FILES:
        raise RuntimeError("Input files do not match the exact allowlist")


def check_no_external_connectivity(sockmod=socket):
    """Probe only RFC-reserved addresses; no production hostnames or services."""
    expected = {errno.ENETUNREACH, errno.EHOSTUNREACH}
    probes = ((sockmod.AF_INET, ("192.0.2.1", 443), ("192.0.2.53", 53)),
              (sockmod.AF_INET6, ("2001:db8::1", 443), ("2001:db8::53", 53)))
    # A DNS-format UDP query for a reserved name; success means STOP. It never
    # uses the runner's resolver and is sent only to reserved TEST-NET addresses.
    dns_query = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01x\x07invalid\x00\x00\x01\x00\x01"
    for family, address, dns_server in probes:
        try:
            with sockmod.socket(family, sockmod.SOCK_STREAM) as tcp:
                tcp.settimeout(0.5)
                if tcp.connect_ex(address) not in expected:
                    raise RuntimeError("TCP probe did not prove network isolation")
            with sockmod.socket(family, sockmod.SOCK_DGRAM) as udp:
                udp.settimeout(0.5)
                try:
                    udp.sendto(dns_query, dns_server)
                except OSError as exc:
                    if exc.errno not in expected:
                        raise RuntimeError("DNS probe failure was inconclusive") from exc
                else:
                    raise RuntimeError("DNS packet was sent; isolation is not proven")
        except OSError as exc:
            raise RuntimeError("Unable to perform network probes") from exc


def audit_container():
    if sys.platform != "linux" or not hasattr(os, "geteuid") or os.geteuid() == 0:
        raise RuntimeError("A non-root Linux container is required")
    check_environment(os.environ)
    check_interfaces(name for _, name in socket.if_nameindex())
    check_routes(Path("/proc/net/route").read_text(), Path("/proc/net/ipv6_route").read_text())
    check_mounts(Path("/proc/self/mountinfo").read_text())
    check_input_files(INPUT)
    check_no_external_connectivity()


def run_integration_after_review():
    audit_container()
    import runpy
    import subprocess
    import time
    from pymongo import MongoClient
    from motor.motor_asyncio import AsyncIOMotorClient

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        if probe.connect_ex(("127.0.0.1", 27017)) == 0:
            raise RuntimeError("Test MongoDB port was already in use")
    dbpath = Path("/tmp/v6-mongodb")
    dbpath.mkdir(mode=0o700, exist_ok=False)
    startup_log = open("/tmp/v6-mongod-startup.log", "wb")
    process = subprocess.Popen(["/usr/local/bin/mongod", "--bind_ip", "127.0.0.1", "--port", "27017",
                                "--dbpath", str(dbpath), "--nounixsocket", "--quiet", "--replSet", "v6test",
                                "--oplogSize", "32",
                                "--wiredTigerCacheSizeGB", "0.25", "--logpath", "/tmp/v6-mongod.log"],
                               stdin=subprocess.DEVNULL, stdout=startup_log, stderr=subprocess.STDOUT)
    try:
        client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true", serverSelectionTimeoutMS=500)
        for _ in range(30):
            try:
                client.admin.command("ping")
                break
            except Exception:
                if process.poll() is not None:
                    log = Path("/tmp/v6-mongod.log")
                    log = log if log.exists() else Path("/tmp/v6-mongod-startup.log")
                    detail = log.read_text(encoding="utf-8", errors="replace")[-4000:]
                    raise RuntimeError(f"Isolated MongoDB exited ({process.returncode}): {detail}")
                time.sleep(0.2)
        else:
            raise RuntimeError("Isolated MongoDB did not become ready")
        client.admin.command("replSetInitiate", {"_id": "v6test", "members": [{"_id": 0, "host": "127.0.0.1:27017"}]})
        for _ in range(60):
            if client.admin.command("hello").get("isWritablePrimary"):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("Isolated replica set did not elect a primary")
        client.close()
        fakes = runpy.run_path(str(INPUT / "tests/michael_v6_isolated/fake_services.py"))
        fakes["install"]()
        fakes["install_network_audit_guard"](allow_test_mongo=True)
        sys.path[:0] = [str(INPUT), str(INPUT / "backend")]
        import michael_v6_policy as policy
        import backend.teacher_chat as tc
        tests = runpy.run_path(str(INPUT / "tests/michael_v6_isolated/v6_endpoint_scenarios.py"))
        result = tests["run_suite"](tc, policy, AsyncIOMotorClient)
        if not result.wasSuccessful():
            raise RuntimeError("Synthetic V6 integration tests failed")
    finally:
        process.terminate()
        process.wait(timeout=10)
        startup_log.close()


def main():
    run_integration_after_review()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Isolation gate failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
