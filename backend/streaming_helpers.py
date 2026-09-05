"""Small, dependency-free helpers for HTTP byte-range media streaming."""

from __future__ import annotations

import re
from typing import Optional


class RangeNotSatisfiable(ValueError):
    """Raised when a single HTTP byte range cannot be served."""


def gridfs_content_type(grid_out, default: str = "audio/mpeg") -> str:
    """Read content type safely from both new and legacy GridFS documents."""
    metadata = getattr(grid_out, "metadata", None) or {}
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
