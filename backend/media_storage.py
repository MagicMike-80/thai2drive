"""Shared validation and image processing for persistent admin media uploads."""
from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


class MediaUploadError(ValueError):
    """Raised when an uploaded file is unsafe or unsupported."""


@dataclass(frozen=True)
class PreparedMedia:
    data: bytes
    content_type: str
    media_type: str
    filename: str
    original_filename: str
    transformed: bool = False


ALLOWED_MEDIA_TYPES = {
    "image/jpeg": ("image", ".jpg", 20 * 1024 * 1024),
    "image/png": ("image", ".png", 20 * 1024 * 1024),
    "image/webp": ("image", ".webp", 20 * 1024 * 1024),
    "video/mp4": ("video", ".mp4", 250 * 1024 * 1024),
    "video/webm": ("video", ".webm", 250 * 1024 * 1024),
    "audio/mpeg": ("audio", ".mp3", 120 * 1024 * 1024),
    "audio/mp4": ("audio", ".m4a", 120 * 1024 * 1024),
    "audio/x-m4a": ("audio", ".m4a", 120 * 1024 * 1024),
    "audio/wav": ("audio", ".wav", 120 * 1024 * 1024),
    "audio/x-wav": ("audio", ".wav", 120 * 1024 * 1024),
    "application/pdf": ("document", ".pdf", 40 * 1024 * 1024),
}


def make_link_name(filename: str) -> str:
    """Create a stable, readable ASCII identifier from an uploaded filename."""
    stem = Path(filename or "materiale").stem.strip().casefold()
    stem = stem.replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return (stem or "materiale")[:80]


def _normalized_content_type(content_type: str, filename: str) -> str:
    value = (content_type or "").split(";", 1)[0].strip().lower()
    aliases = {"image/jpg": "image/jpeg", "audio/mp3": "audio/mpeg"}
    value = aliases.get(value, value)
    if value in ALLOWED_MEDIA_TYPES:
        return value
    suffix = Path(filename or "").suffix.casefold()
    by_suffix = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".mp4": "video/mp4", ".webm": "video/webm",
        ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav",
        ".pdf": "application/pdf",
    }
    inferred = by_suffix.get(suffix)
    if inferred:
        return inferred
    raise MediaUploadError("Filtypen støttes ikke")


def prepare_media_upload(
    data: bytes,
    filename: str,
    content_type: str,
    *,
    max_image_edge: int = 1920,
) -> PreparedMedia:
    """Validate an upload and normalize images to bounded WebP files."""
    normalized_type = _normalized_content_type(content_type, filename)
    media_type, extension, max_bytes = ALLOWED_MEDIA_TYPES[normalized_type]
    if not data:
        raise MediaUploadError("Filen er tom")
    if len(data) > max_bytes:
        raise MediaUploadError(f"Filen er for stor (maks {max_bytes // (1024 * 1024)} MB)")

    link_name = make_link_name(filename)
    if media_type != "image":
        return PreparedMedia(
            data=data,
            content_type=normalized_type,
            media_type=media_type,
            filename=f"{link_name}{extension}",
            original_filename=filename,
        )

    try:
        with Image.open(io.BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source)
            image.thumbnail((max_image_edge, max_image_edge), Image.Resampling.LANCZOS)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")
            output = io.BytesIO()
            image.save(output, format="WEBP", quality=84, method=6)
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise MediaUploadError("Bildefilen er ugyldig") from exc

    return PreparedMedia(
        data=output.getvalue(),
        content_type="image/webp",
        media_type="image",
        filename=f"{link_name}.webp",
        original_filename=filename,
        transformed=True,
    )
