"""Shared validation and lookup helpers for the curated media catalog."""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable, Optional
from urllib.parse import urlsplit


SUPPORTED_LANGUAGES = ("no", "th", "en")
CONTENT_LANGUAGES = (*SUPPORTED_LANGUAGES, "neutral")
MEDIA_TYPES = ("video", "podcast")
CATEGORIES = (
    "vikeplikt",
    "stoppelengde",
    "skilt",
    "morkekjoring",
    "hav_regelen",
)
CATEGORY_ORDER = {category: index for index, category in enumerate(CATEGORIES)}
TYPE_ORDER = {"video": 0, "podcast": 1}


class MediaCatalogValidationError(ValueError):
    """Raised when curated media metadata is incomplete or unsafe."""


def normalize_catalog_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def is_safe_catalog_url(value: Any) -> bool:
    url = str(value or "").strip()
    if not url or any(char.isspace() for char in url):
        return False
    if url.startswith("/api/assets/"):
        path = urlsplit(url).path
        return (
            not url.startswith("/api/assets//")
            and ".." not in path.split("/")
            and not urlsplit(url).query
            and not urlsplit(url).fragment
        )
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
    )


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MediaCatalogValidationError(f"{field} must be a non-empty string")
    return value.strip()


def validate_catalog_document(document: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one database/manifest document without fallback."""
    if not isinstance(document, dict):
        raise MediaCatalogValidationError("media item must be an object")

    media_id = _required_text(document.get("media_id"), "media_id")
    media_type = _required_text(document.get("type"), "type")
    category = _required_text(document.get("category"), "category")
    content_language = _required_text(
        document.get("content_language"), "content_language"
    )
    if media_type not in MEDIA_TYPES:
        raise MediaCatalogValidationError("type must be video or podcast")
    if category not in CATEGORIES:
        raise MediaCatalogValidationError("unsupported category")
    if content_language not in CONTENT_LANGUAGES:
        raise MediaCatalogValidationError("unsupported content_language")

    raw_tags = document.get("tags")
    if not isinstance(raw_tags, list) or not raw_tags:
        raise MediaCatalogValidationError("tags must be a non-empty list")
    tags: list[str] = []
    for index, value in enumerate(raw_tags):
        tag = normalize_catalog_text(value)
        if not tag:
            raise MediaCatalogValidationError(f"tags[{index}] is empty")
        if tag in tags:
            raise MediaCatalogValidationError("tags must be unique after normalization")
        tags.append(tag)

    media_url = _required_text(document.get("media_url"), "media_url")
    thumbnail_url = _required_text(document.get("thumbnail_url"), "thumbnail_url")
    if not is_safe_catalog_url(media_url):
        raise MediaCatalogValidationError("media_url is not an approved URL")
    if not is_safe_catalog_url(thumbnail_url):
        raise MediaCatalogValidationError("thumbnail_url is not an approved URL")

    is_active = document.get("is_active", True)
    if not isinstance(is_active, bool):
        raise MediaCatalogValidationError("is_active must be boolean")

    raw_i18n = document.get("i18n")
    if not isinstance(raw_i18n, dict):
        raise MediaCatalogValidationError("i18n must be an object")
    i18n: dict[str, dict[str, str]] = {}
    for language in SUPPORTED_LANGUAGES:
        localized = raw_i18n.get(language)
        if not isinstance(localized, dict):
            raise MediaCatalogValidationError(f"i18n.{language} must be an object")
        i18n[language] = {
            "title": _required_text(localized.get("title"), f"i18n.{language}.title"),
            "description": _required_text(
                localized.get("description"), f"i18n.{language}.description"
            ),
        }

    normalized = {
        "media_id": media_id,
        "type": media_type,
        "category": category,
        "tags": tags,
        "media_url": media_url,
        "thumbnail_url": thumbnail_url,
        "is_active": is_active,
        "content_language": content_language,
        "i18n": i18n,
    }
    for timestamp_field in ("created_at", "updated_at"):
        if timestamp_field in document:
            normalized[timestamp_field] = document[timestamp_field]
    return normalized


def validate_catalog_documents(documents: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for document in documents:
        item = validate_catalog_document(document)
        if item["media_id"] in seen_ids:
            raise MediaCatalogValidationError("media_id values must be unique")
        seen_ids.add(item["media_id"])
        normalized.append(item)
    return normalized


def serialize_catalog_document(document: dict[str, Any], language: str) -> Optional[dict[str, Any]]:
    """Return one language-pure API item, or hide invalid/incompatible content."""
    if language not in SUPPORTED_LANGUAGES:
        return None
    try:
        item = validate_catalog_document(document)
    except MediaCatalogValidationError:
        return None
    if not item["is_active"]:
        return None
    if item["content_language"] not in (language, "neutral"):
        return None
    localized = item["i18n"][language]
    return {
        "id": item["media_id"],
        "media_id": item["media_id"],
        "type": item["type"],
        "category": item["category"],
        "tags": list(item["tags"]),
        "url": item["media_url"],
        "thumbnail_url": item["thumbnail_url"],
        "title": localized["title"],
        "description": localized["description"],
        "caption": localized["description"],
    }


def catalog_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        CATEGORY_ORDER.get(str(item.get("category")), len(CATEGORY_ORDER)),
        TYPE_ORDER.get(str(item.get("type")), len(TYPE_ORDER)),
        normalize_catalog_text(item.get("title")),
        str(item.get("media_id", "")),
    )


def rank_catalog_media(
    documents: Iterable[dict[str, Any]], query: str, language: str, limit: int = 1
) -> list[dict[str, Any]]:
    """Rank whole approved tag phrases deterministically; never fuzzy match."""
    if language not in SUPPORTED_LANGUAGES or limit <= 0:
        return []
    normalized_query = f" {normalize_catalog_text(query)} "
    ranked: list[tuple[Any, ...]] = []
    for document in documents:
        payload = serialize_catalog_document(document, language)
        if not payload:
            continue
        matches = sum(1 for tag in payload["tags"] if f" {tag} " in normalized_query)
        if not matches:
            continue
        ranked.append((-matches, *catalog_sort_key(payload), payload))
    ranked.sort(key=lambda item: item[:-1])
    return [item[-1] for item in ranked[: min(limit, 1)]]


LAW_MAPPING: dict[str, dict[str, list[str]]] = {
    "3": {
        "tags": ["3", "hav", "grunnregel", "hensynsfull", "aktpågivende", "varsom"],
        "synonyms": ["paragraf 3", "hav-regelen", "aktpågivende", "hensynsfull", "varsom"],
    },
    "7_2": {
        "tags": ["7", "7_2", "vikeplikt", "høyreregel", "venstresving", "møtende"],
        "synonyms": [
            "paragraf 7",
            "høyreregelen",
            "vikeplikt venstresving",
            "møtende trafikk",
        ],
    },
    "7_5": {
        "tags": ["7", "7_5", "bussregelen", "vikeplikt_buss"],
        "synonyms": [
            "paragraf 7 nr 5",
            "bussregelen",
            "vikeplikt buss",
            "กฎรถบัส",
            "รถบัสออกจากป้าย",
            "การให้ทางรถบัส",
        ],
    },
}


def expand_law_synonyms(text: str) -> set[str]:
    """Resolve legal-paragraph synonyms (e.g. "paragraf 7") to their canonical tags.

    Only whole textual synonyms are matched (never bare digits): "§ 3" would
    normalize to the single character "3" and match any unrelated message
    containing that digit, so section-sign forms are intentionally excluded.

    Longer synonyms are matched first and consumed from the text before
    shorter ones are checked, so a narrow phrase like "paragraf 7 nr 5"
    (bussregelen) is not also read as the broader "paragraf 7" (§7 nr 2) —
    the broader synonym is literally a substring of the narrower one.
    """
    remaining = f" {normalize_catalog_text(text)} "
    candidates = sorted(
        (
            (normalize_catalog_text(synonym), entry)
            for entry in LAW_MAPPING.values()
            for synonym in entry["synonyms"]
        ),
        key=lambda pair: len(pair[0]),
        reverse=True,
    )
    resolved: set[str] = set()
    for normalized_synonym, entry in candidates:
        if normalized_synonym and normalized_synonym in remaining:
            resolved.update(entry["tags"])
            remaining = remaining.replace(normalized_synonym, " ", 1)
    return resolved


async def list_localized_catalog_media(collection: Any, language: str) -> list[dict[str, Any]]:
    if language not in SUPPORTED_LANGUAGES:
        return []
    cursor = collection.find(
        {"is_active": True, "content_language": {"$in": [language, "neutral"]}}
    )
    documents = await cursor.to_list(length=500)
    payloads = [
        payload
        for document in documents
        if (payload := serialize_catalog_document(document, language)) is not None
    ]
    return sorted(payloads, key=catalog_sort_key)
