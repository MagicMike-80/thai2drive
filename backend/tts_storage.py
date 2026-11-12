"""Opt-in private persistence for TTS audio; no text or public storage URLs."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

MAX_AUDIO_BYTES = 32 * 1024 * 1024
PREFIX = "tts/v1/"


def audio_digest(data: bytes) -> str:
    if not 4 <= len(data) <= MAX_AUDIO_BYTES:
        raise ValueError("Invalid audio size")
    # Validate complete MPEG Layer III frames, not merely an ID3/file signature.
    # This is structural integrity, not a decoder or pronunciation assessment.
    position = 0
    if data.startswith(b"ID3"):
        if len(data) < 10 or data[3] not in (2, 3, 4) or any(v & 0x80 for v in data[6:10]):
            raise ValueError("Invalid ID3 header")
        tag_size = sum(value << shift for value, shift in zip(data[6:10], (21, 14, 7, 0)))
        position = 10 + tag_size + (10 if data[3] == 4 and data[5] & 0x10 else 0)
        if position > len(data):
            raise ValueError("Truncated ID3 tag")
    frames = 0
    while position < len(data):
        remaining_length = len(data) - position
        if (remaining_length == 128 and data[position:position + 3] == b"TAG") or (data[position] == 0 and not any(data[position:])):
            break
        if remaining_length < 4:
            raise ValueError("Truncated MP3 frame header")
        header = int.from_bytes(data[position:position + 4], "big")
        version, layer = (header >> 19) & 3, (header >> 17) & 3
        bitrate_index, rate_index = (header >> 12) & 15, (header >> 10) & 3
        if (header >> 21 != 0x7FF or version == 1 or layer != 1
                or bitrate_index in (0, 15) or rate_index == 3):
            raise ValueError("Invalid MPEG Layer III frame")
        sample_rate = (44100, 48000, 32000)[rate_index] // (1 if version == 3 else 2 if version == 2 else 4)
        bitrates = ((32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)
                    if version == 3 else (8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160))
        frame_size = (144000 if version == 3 else 72000) * bitrates[bitrate_index - 1] // sample_rate + ((header >> 9) & 1)
        if position + frame_size > len(data):
            raise ValueError("Truncated MP3 frame")
        position += frame_size
        frames += 1
    if not frames:
        raise ValueError("MP3 contains no complete audio frames")
    return hashlib.sha256(data).hexdigest()


def read_audio(path: Path) -> bytes:
    with Path(path).open("rb") as source:
        data = source.read(MAX_AUDIO_BYTES + 1)
    audio_digest(data)
    return data


def write_audio_atomic(path: Path, data: bytes) -> None:
    audio_digest(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as target:
            temporary = Path(target.name)
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def cache_key(provider, voice, language, text, *, settings=None, version="1"):
    identity = json.dumps([provider, voice, language, text, settings or {}, version],
                          ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return PREFIX + hashlib.sha256(identity.encode("utf-8")).hexdigest() + ".mp3"


def legacy_key(path):
    name = Path(path).name
    if not re.fullmatch(r"[a-f0-9]{32}\.mp3", name):
        raise ValueError("Expected legacy cache filename")
    return PREFIX + "legacy/" + name


class TTSAudioStorage:
    def __init__(self, bucket, client):
        self.bucket = bucket
        self.client = client

    @classmethod
    def from_environment(cls):
        if os.environ.get("TTS_STORAGE_ENABLED") != "1":
            return None
        fields = ("ENDPOINT", "REGION", "BUCKET", "ACCESS_KEY_ID", "SECRET_ACCESS_KEY")
        # Never silently combine partial credentials from different stores.
        prefix = "TTS_S3_" if any(os.environ.get("TTS_S3_" + field) for field in fields) else "PRIVATE_BOOK_S3_"
        values = {field: os.environ.get(prefix + field, "").strip() for field in fields}
        if not all(values.values()) or not values["ENDPOINT"].startswith("https://"):
            raise ValueError("Complete HTTPS TTS storage configuration required")
        import boto3
        from botocore.config import Config
        client = boto3.client("s3", endpoint_url=values["ENDPOINT"], region_name=values["REGION"],
                              aws_access_key_id=values["ACCESS_KEY_ID"],
                              aws_secret_access_key=values["SECRET_ACCESS_KEY"],
                              config=Config(connect_timeout=5, read_timeout=15,
                                            retries={"max_attempts": 1},
                                            s3={"addressing_style": "virtual"}))
        return cls(values["BUCKET"], client)

    @staticmethod
    def _validate_key(key):
        if not re.fullmatch(r"tts/v1/(?:[a-f0-9]{64}|legacy/[a-f0-9]{32})\.mp3", key):
            raise ValueError("Invalid TTS storage key")

    def read(self, key):
        self._validate_key(key)
        from botocore.exceptions import ClientError
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                return None
            raise
        stream = response["Body"]
        try:
            expected_length = response.get("ContentLength")
            if not isinstance(expected_length, int) or not 4 <= expected_length <= MAX_AUDIO_BYTES:
                raise ValueError("Invalid stored audio length")
            data = stream.read(MAX_AUDIO_BYTES + 1)
        finally:
            stream.close()
        expected = response.get("Metadata", {}).get("sha256", "")
        if len(data) != expected_length or audio_digest(data) != expected:
            raise ValueError("Stored audio checksum mismatch")
        return data

    def store(self, key, path):
        self._validate_key(key)
        data = read_audio(Path(path))
        expected = audio_digest(data)
        existing = self.read(key)
        if existing is None:
            from botocore.exceptions import ClientError
            try:
                self.client.put_object(Bucket=self.bucket, Key=key, Body=data,
                                       IfNoneMatch="*", ContentType="audio/mpeg",
                                       CacheControl="private, no-store",
                                       Metadata={"sha256": expected})
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") not in {"PreconditionFailed", "412"}:
                    raise
            existing = self.read(key)
        if existing is None or hashlib.sha256(existing).hexdigest() != expected:
            raise ValueError("TTS archive verification failed; existing object preserved")
        return {"bytes": len(data), "sha256": expected}

    def restore(self, key, path, *, legacy=None):
        data = self.read(key)
        candidates = [legacy] if isinstance(legacy, str) else (legacy or [])
        for candidate in candidates:
            if data is not None:
                break
            data = self.read(candidate)
        if data is None:
            return False
        write_audio_atomic(Path(path), data)
        return True
