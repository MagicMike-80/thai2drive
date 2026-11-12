"""Inventory existing cache by default; --apply copies and verifies private S3 bytes.

Run inside the current production container before redeploying, with tts_storage.py
available beside server.py. Never deploy merely to install this backup tool.
No text, credentials, public URLs or non-cache files are included in the report.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tts_storage import TTSAudioStorage, audio_digest, legacy_key, read_audio


def backup(cache_dir, *, apply=False, storage=None):
    cache_dir = Path(cache_dir)
    if not cache_dir.is_dir():
        raise ValueError("Cache directory does not exist")
    if apply and storage is None:
        raise ValueError("Explicitly enabled private TTS storage is required")
    report = {"mode": "apply" if apply else "dry-run", "files": [], "errors": [],
              "candidate_bytes": 0, "verified_files": 0, "verified_bytes": 0}
    for path in sorted(cache_dir.glob("*.mp3")):
        try:
            key = legacy_key(path)
            if path.is_symlink():
                raise ValueError("Symlink cache entry refused")
            data = read_audio(path)
            row = {"key": key, "bytes": len(data), "sha256": audio_digest(data), "verified": False}
            report["candidate_bytes"] += len(data)
            if apply:
                verified = storage.store(key, path)
                if verified != {"bytes": row["bytes"], "sha256": row["sha256"]}:
                    raise ValueError("Cache changed during backup; verification required")
                row["verified"] = True
                report["verified_files"] += 1
                report["verified_bytes"] += row["bytes"]
            report["files"].append(row)
        except Exception as exc:
            # Error types, never provider messages or arbitrary filenames.
            report["errors"].append({"entry": len(report["files"]) + len(report["errors"]) + 1,
                                     "type": type(exc).__name__})
    report["complete"] = bool(apply and report["files"] and not report["errors"]
                              and report["verified_files"] == len(report["files"]))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("public_assets/audio"))
    parser.add_argument("--apply", action="store_true", help="Upload and read back existing MP3s; no synthesis")
    args = parser.parse_args()
    try:
        storage = TTSAudioStorage.from_environment() if args.apply else None
        report = backup(args.cache_dir, apply=args.apply, storage=storage)
        print(json.dumps(report, sort_keys=True))
        return 1 if report["errors"] or (args.apply and not report["complete"]) else 0
    except Exception as exc:
        print(json.dumps({"complete": False, "error_type": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
