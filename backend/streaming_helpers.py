"""Small, dependency-free helpers for HTTP byte-range media streaming."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Optional


class RangeNotSatisfiable(ValueError):
    """Raised when a single HTTP byte range cannot be served."""


def gridfs_file_length(document) -> int:
    """Read a GridFS file length from either a mapping or GridOut object."""
    value = (
        document.get("length")
        if isinstance(document, Mapping)
        else getattr(document, "length", None)
    )
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("GridFS document has no valid length")
    return value


def gridfs_content_type(document, default: str = "audio/mpeg") -> str:
    """Read content type safely from both new and legacy GridFS documents."""
    metadata = (
        document.get("metadata", {})
        if isinstance(document, Mapping)
        else getattr(document, "metadata", None) or {}
    )
    if not isinstance(metadata, Mapping):
        return default
    return metadata.get("content_type") or metadata.get("contentType") or default


def parse_byte_range(value: str, total: int) -> Optional[tuple[int, int]]:
    """Parse one HTTP byte range and return inclusive bounds."""
    if not value:
        return None
    if total <= 0:
        raise RangeNotSatisfiable("empty resource")

    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if not match or (not match.group(1) and not match.group(2)):
        raise RangeNotSatisfiable("invalid byte range")

    start_text, end_text = match.groups()
    if not start_text:
        suffix_length = int(end_text)
        if suffix_length <= 0:
            raise RangeNotSatisfiable("invalid suffix range")
        start = max(0, total - suffix_length)
        end = total - 1
    else:
        start = int(start_text)
        end = int(end_text) if end_text else total - 1
        if start >= total or end < start:
            raise RangeNotSatisfiable("range outside resource")
        end = min(end, total - 1)

    return start, end
