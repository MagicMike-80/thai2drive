"""Pure helpers for canonical local learning-video thumbnail paths."""
from __future__ import annotations

from pathlib import PurePosixPath


THUMBNAIL_PREFIX = "/api/assets/thumbs/thumb_"


def thumbnail_url_for_video(file_path: str) -> str:
    """Return the canonical thumbnail URL for a local ``video_*.mp4`` path."""
    normalized = str(file_path or "").strip().replace("\\", "/")
    if not normalized:
        return ""
    stem = PurePosixPath(normalized).stem
    if stem.startswith("video_"):
        stem = stem[len("video_") :]
    if not stem:
        return ""
    return f"{THUMBNAIL_PREFIX}{stem}.jpg"


def normalize_video_thumbnail_url(thumbnail_url: str, file_path: str = "") -> str:
    """Repair only the legacy URL derived from the full ``video_`` stem."""
    current = str(thumbnail_url or "").strip()
    expected = thumbnail_url_for_video(file_path)
    if not current:
        return expected

    normalized_file = str(file_path or "").strip().replace("\\", "/")
    full_stem = PurePosixPath(normalized_file).stem if normalized_file else ""
    legacy = f"{THUMBNAIL_PREFIX}{full_stem}.jpg" if full_stem else ""
    if expected and full_stem.startswith("video_") and current == legacy:
        return expected
    return current
