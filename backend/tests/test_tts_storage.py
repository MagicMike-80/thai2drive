"""Offline persistence/backup tests; no server startup or external service calls."""
import ast
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
import logging
import json
import uuid
from types import SimpleNamespace
from typing import Optional
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from botocore.exceptions import ClientError
from tts_storage import TTSAudioStorage, audio_digest, cache_key, legacy_key, write_audio_atomic

spec = importlib.util.spec_from_file_location("backup_tts", Path(__file__).resolve().parents[1] / "scripts" / "backup_tts_cache.py")
backup_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup_module)
AUDIO = (Path(__file__).resolve().parents[1] / "public_assets" / "flashcard_flip.mp3").read_bytes()


def drive(coroutine):
    """All injected I/O completes immediately; never starts a real event loop."""
    try:
        coroutine.send(None)
    except StopIteration as done:
        return done.value
    raise AssertionError("Unexpected asynchronous I/O")


def server_functions():
    source = Path(__file__).resolve().parents[1] / "server.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names = {"_tts_cache_path", "_tts_cached_audio", "_tts_archive_audio", "text_to_speech",
             "_elevenlabs_voice_id", "_elevenlabs_model_id"}
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id.startswith(
                ("_DEFAULT_ELEVENLABS_", "_ELEVENLABS_", "_GOOGLE_TTS_")) for target in node.targets):
            nodes.append(node)
    async def inline_thread(fn, *args):
        return fn(*args)
    ns = dict(Path=Path, os=os, json=json, hashlib=hashlib, Optional=Optional, Request=object,
              uuid=uuid, logger=logging.getLogger("tts-offline-test"), asyncio=SimpleNamespace(to_thread=inline_thread),
              _tts_provider_available=lambda *args: True, _tts_record_success=lambda *args: None,
              _tts_record_failure=lambda *args: None,
              _stream_mp3_file=lambda path, request, headers=None: SimpleNamespace(content=Path(path).read_bytes(), headers=headers))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), ns)
    return ns


class MemoryS3:
    def __init__(self):
        self.objects = {}
        self.puts = []

    def get_object(self, *, Bucket, Key):
        if Key not in self.objects:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        data, metadata = self.objects[Key]
        return {"Body": io.BytesIO(data), "ContentLength": len(data), "Metadata": dict(metadata)}

    def put_object(self, **kwargs):
        self.puts.append(kwargs)
        if kwargs["Key"] in self.objects:
            raise ClientError({"Error": {"Code": "PreconditionFailed"}}, "PutObject")
        self.objects[kwargs["Key"]] = (bytes(kwargs["Body"]), dict(kwargs["Metadata"]))


class TTSStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / ("a" * 32 + ".mp3")
        write_audio_atomic(self.path, AUDIO)
        self.client = MemoryS3()
        self.storage = TTSAudioStorage("private-test", self.client)
        self.key = cache_key("elevenlabs:model", "voice", "th-TH", "PRIVATE-TEXT-123")

    def test_identity_is_stable_and_separates_all_voice_inputs(self):
        base = ["elevenlabs:model", "voice", "th-TH", "PRIVATE-TEXT-123"]
        self.assertEqual(self.key, cache_key(*base))
        for i in range(4):
            changed = base.copy()
            changed[i] += "changed"
            self.assertNotEqual(self.key, cache_key(*changed))
        self.assertNotEqual(self.key, cache_key(*base, settings={"style": 1}))
        self.assertNotEqual(self.key, cache_key(*base, version="2"))
        self.assertNotIn(base[3], self.key)

    def test_roundtrip_survives_fresh_storage_and_empty_local_cache(self):
        result = self.storage.store(self.key, self.path)
        self.path.unlink()
        fresh = TTSAudioStorage("private-test", self.client)
        self.assertTrue(fresh.restore(self.key, self.path))
        self.assertEqual(self.path.read_bytes(), AUDIO)
        self.assertEqual(result["sha256"], hashlib.sha256(AUDIO).hexdigest())
        put = self.client.puts[0]
        self.assertNotIn("ACL", put)
        self.assertNotIn("PRIVATE-TEXT-123", repr(put))
        self.assertEqual(put["CacheControl"], "private, no-store")
        self.assertEqual(set(put["Metadata"]), {"sha256"})

    def test_repeated_backup_reuses_verified_object_without_overwrite(self):
        self.storage.store(self.key, self.path)
        self.storage.store(self.key, self.path)
        self.assertEqual(len(self.client.puts), 1)

    def test_conflict_preserves_original_object(self):
        self.storage.store(self.key, self.path)
        self.path.write_bytes(AUDIO + b"different")
        with self.assertRaises(ValueError):
            self.storage.store(self.key, self.path)
        self.assertEqual(self.client.objects[self.key][0], AUDIO)

    def test_bad_hash_or_truncation_never_replaces_valid_local_file(self):
        for data, digest in [(AUDIO, "0" * 64), (AUDIO[:-5], hashlib.sha256(AUDIO).hexdigest())]:
            self.client.objects[self.key] = (data, {"sha256": digest})
            with self.assertRaises(ValueError):
                self.storage.restore(self.key, self.path)
            self.assertEqual(self.path.read_bytes(), AUDIO)

    def test_invalid_payload_is_not_saved(self):
        for data in (b"", b"ID", b"ID3", b"ID3\x04\x00\x00\x00\x00\x00\x00",
                     b"ID3\x04\x00\x00\x00\x00\x01\x00", AUDIO[:-1],
                     b'{"error":"payment"}', b"<html>Error</html>"):
            with self.assertRaises(ValueError):
                write_audio_atomic(self.path, data)
            self.assertEqual(self.path.read_bytes(), AUDIO)

    def test_interrupted_local_replace_preserves_old_bytes_and_cleans_temp(self):
        with patch("tts_storage.os.replace", side_effect=OSError("blocked")):
            with self.assertRaises(OSError):
                write_audio_atomic(self.path, AUDIO)
        self.assertEqual(self.path.read_bytes(), AUDIO)
        self.assertEqual(len(list(self.path.parent.iterdir())), 1)

    def test_timeout_propagates_without_false_success(self):
        self.client.get_object = lambda **kwargs: (_ for _ in ()).throw(TimeoutError())
        with self.assertRaises(TimeoutError):
            self.storage.store(self.key, self.path)

    def test_keys_cannot_escape_tts_prefix(self):
        for key in ("images/private.mp3", "tts/v1/../../secret", "tts/v1/private-text.mp3"):
            with self.assertRaises(ValueError):
                self.storage.read(key)

    def test_disabled_or_partial_configuration_does_not_connect(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(TTSAudioStorage.from_environment())
            os.environ["TTS_STORAGE_ENABLED"] = "1"
            os.environ["TTS_S3_BUCKET"] = "partial"
            with self.assertRaises(ValueError):
                TTSAudioStorage.from_environment()

    def test_backup_dry_run_does_not_claim_protection_or_write(self):
        report = backup_module.backup(self.path.parent)
        self.assertFalse(report["complete"])
        self.assertEqual(report["verified_files"], 0)
        self.assertEqual(len(self.client.puts), 0)

    def test_backup_apply_readback_and_legacy_restore(self):
        report = backup_module.backup(self.path.parent, apply=True, storage=self.storage)
        self.assertTrue(report["complete"])
        self.assertEqual(report["verified_bytes"], len(AUDIO))
        old_key = legacy_key(self.path)
        self.path.unlink()
        self.assertTrue(self.storage.restore(self.key, self.path, legacy=old_key))
        self.assertEqual(self.path.read_bytes(), AUDIO)

    def test_failed_backup_is_not_complete(self):
        self.client.put_object = lambda **kwargs: (_ for _ in ()).throw(PermissionError("secret ignored"))
        report = backup_module.backup(self.path.parent, apply=True, storage=self.storage)
        self.assertFalse(report["complete"])
        self.assertEqual(report["verified_files"], 0)
        self.assertNotIn("secret ignored", repr(report))

    def test_metadata_only_mp3_never_claims_successful_backup(self):
        self.path.write_bytes(b"ID3")
        report = backup_module.backup(self.path.parent, apply=True, storage=self.storage)
        self.assertFalse(report["complete"])
        self.assertEqual(report["verified_bytes"], 0)
        self.assertEqual(len(self.client.puts), 0)

    def test_real_route_archives_complete_stream_and_restores_without_provider_after_restart(self):
        class ProviderResponse:
            status_code = 200
            async def aiter_bytes(self):
                yield AUDIO[:1000]
                yield AUDIO[1000:]
            async def aclose(self): pass
        class ProviderClient:
            def __init__(self, **kwargs): pass
            def build_request(self, *args, **kwargs): return None
            async def send(self, *args, **kwargs): return ProviderResponse()
            async def aclose(self): pass
        previous = os.getcwd()
        os.chdir(self.temp.name)
        try:
            with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "synthetic-test-only"}, clear=True), \
                    patch("tts_storage.TTSAudioStorage.from_environment", return_value=self.storage), \
                    patch("httpx.AsyncClient", ProviderClient):
                ns = server_functions()
                response = drive(ns["text_to_speech"](SimpleNamespace(method="GET"), "PRIVATE-TEXT-123", "th"))
                received = []
                while True:
                    try:
                        received.append(drive(response.body_iterator.__anext__()))
                    except StopAsyncIteration:
                        break
                self.assertEqual(b"".join(received), AUDIO)
                self.assertEqual(len(self.client.puts), 0)  # Archive only after the response.
                drive(response.background())
                self.assertEqual(len(self.client.puts), 1)
                self.assertNotIn("PRIVATE-TEXT-123", repr(self.client.puts))
                for cached in Path("public_assets/audio").glob("*.mp3"):
                    cached.unlink()
                fresh = server_functions()
                with patch("httpx.AsyncClient", side_effect=AssertionError("Provider must not be called")):
                    restored = drive(fresh["text_to_speech"](SimpleNamespace(method="GET"), "PRIVATE-TEXT-123", "th"))
                self.assertEqual(restored.content, AUDIO)
                self.assertEqual(restored.headers["X-TTS-Provider"], "elevenlabs-cached")
        finally:
            os.chdir(previous)

    def test_archive_failure_is_fail_soft_and_does_not_disclose_provider_error(self):
        ns = server_functions()
        self.client.get_object = lambda **kwargs: (_ for _ in ()).throw(PermissionError("SECRET-DO-NOT-LOG"))
        with patch("tts_storage.TTSAudioStorage.from_environment", return_value=self.storage), \
                self.assertLogs("tts-offline-test", level="WARNING") as captured:
            drive(ns["_tts_archive_audio"](str(self.path), "elevenlabs:model", "voice", "th-TH", "PRIVATE-TEXT-123"))
        self.assertNotIn("SECRET-DO-NOT-LOG", repr(captured.output))
        self.assertNotIn("PRIVATE-TEXT-123", repr(captured.output))
        self.assertEqual(self.path.read_bytes(), AUDIO)

    def test_server_can_restore_backup_of_current_cache_filename_without_old_identity(self):
        self.storage.store(legacy_key(self.path), self.path)
        self.path.unlink()
        ns = server_functions()
        with patch("tts_storage.TTSAudioStorage.from_environment", return_value=self.storage):
            restored = drive(ns["_tts_cached_audio"](str(self.path), "elevenlabs:model:new-settings",
                             "voice", "th-TH", "PRIVATE-TEXT-123", version="2"))
        self.assertTrue(restored)
        self.assertEqual(self.path.read_bytes(), AUDIO)


if __name__ == "__main__":
    unittest.main()
