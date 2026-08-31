"""Validate or explicitly apply the curated media catalog manifest.

Dry-run is the default and never creates a MongoDB client. Production content
is intentionally not embedded in this source file.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin
from urllib.request import Request, urlopen

try:
    from media_catalog import MediaCatalogValidationError, validate_catalog_documents
except ImportError:  # package-style imports used by isolated tests
    from backend.media_catalog import MediaCatalogValidationError, validate_catalog_documents


EXPECTED_MEDIA = {
    "vid_stopp_01": ("video", "stoppelengde"),
    "vid_stopp_02": ("video", "stoppelengde"),
    "vid_stopp_03": ("video", "stoppelengde"),
    "pod_stopp_01": ("podcast", "stoppelengde"),
    "vid_vike_01": ("video", "vikeplikt"),
    "vid_vike_02": ("video", "vikeplikt"),
    "pod_vike_01": ("podcast", "vikeplikt"),
    "vid_hav_01": ("video", "hav_regelen"),
    "vid_skilt_01": ("video", "skilt"),
    "vid_skilt_02": ("video", "skilt"),
}
CURATED_FIELDS = (
    "media_id",
    "type",
    "category",
    "tags",
    "media_url",
    "thumbnail_url",
    "is_active",
    "content_language",
    "i18n",
)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaCatalogValidationError(f"cannot read manifest: {exc}") from exc
    documents = payload.get("media") if isinstance(payload, dict) else payload
    if not isinstance(documents, list):
        raise MediaCatalogValidationError("manifest must be a list or contain a media list")
    normalized = validate_catalog_documents(documents)
    actual_ids = {item["media_id"] for item in normalized}
    expected_ids = set(EXPECTED_MEDIA)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise MediaCatalogValidationError(
            f"manifest IDs do not match; missing={missing}, extra={extra}"
        )
    for item in normalized:
        expected_type, expected_category = EXPECTED_MEDIA[item["media_id"]]
        if (item["type"], item["category"]) != (expected_type, expected_category):
            raise MediaCatalogValidationError(
                f"{item['media_id']} must be {expected_type}/{expected_category}"
            )
    return normalized


def _resolved_url(url: str, base_url: str) -> str:
    if url.startswith("/api/assets/"):
        if not base_url or not base_url.startswith("https://"):
            raise MediaCatalogValidationError(
                "--base-url https://... is required for relative asset validation"
            )
        return urljoin(base_url.rstrip("/") + "/", url.lstrip("/"))
    return url


def verify_manifest_urls(
    documents: list[dict[str, Any]],
    base_url: str,
    opener: Callable[..., Any] = urlopen,
) -> None:
    """Verify every URL before the caller is allowed to create a DB client."""
    for item in documents:
        checks = (
            (item["media_url"], ("video/",) if item["type"] == "video" else ("audio/",)),
            (item["thumbnail_url"], ("image/",)),
        )
        for raw_url, accepted_types in checks:
            request = Request(
                _resolved_url(raw_url, base_url),
                headers={"User-Agent": "Thai2Drive-media-seed-validator/1.0"},
            )
            try:
                with opener(request, timeout=20) as response:
                    status = int(getattr(response, "status", response.getcode()))
                    content_type = response.headers.get_content_type().lower()
                    response.read(1)
            except Exception as exc:
                raise MediaCatalogValidationError(
                    f"URL verification failed for {item['media_id']}"
                ) from exc
            if status != 200 or not any(content_type.startswith(prefix) for prefix in accepted_types):
                raise MediaCatalogValidationError(
                    f"unexpected URL response for {item['media_id']}: {status} {content_type}"
                )


def _curated(document: dict[str, Any]) -> dict[str, Any]:
    return {field: document[field] for field in CURATED_FIELDS}


async def seed_collection(collection: Any, documents: list[dict[str, Any]], now: datetime) -> dict[str, int]:
    """Idempotently upsert changed documents; identical input performs no write."""
    ids = [item["media_id"] for item in documents]
    existing_documents = await collection.find(
        {"media_id": {"$in": ids}}
    ).to_list(length=len(ids))
    existing = {item.get("media_id"): item for item in existing_documents}
    counts = {"matched": 0, "modified": 0, "upserted": 0, "unchanged": 0}
    for item in documents:
        previous = existing.get(item["media_id"])
        if previous is not None:
            counts["matched"] += 1
            if all(previous.get(field) == item[field] for field in CURATED_FIELDS):
                counts["unchanged"] += 1
                continue
        update = {
            "$set": {**_curated(item), "updated_at": now},
            "$setOnInsert": {"created_at": now},
        }
        result = await collection.update_one(
            {"media_id": item["media_id"]}, update, upsert=True
        )
        counts["modified"] += int(getattr(result, "modified_count", 0) or 0)
        if getattr(result, "upserted_id", None) is not None:
            counts["upserted"] += 1
    return counts


def write_before_snapshot(path: Path, documents: list[dict[str, Any]], target_ids: list[str]) -> None:
    from bson import json_util

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": datetime.now(timezone.utc),
        "target_media_ids": target_ids,
        "existing_documents": documents,
        "rollback": "Restore existing documents; set newly inserted target IDs is_active=false. Do not delete.",
    }
    path.write_text(json_util.dumps(payload, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Approved JSON manifest")
    parser.add_argument("--apply", action="store_true", help="Write validated data")
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--base-url", default="", help="HTTPS origin for /api/assets URLs")
    parser.add_argument("--snapshot-dir", type=Path, default=Path("seed_snapshots"))
    return parser


async def async_main(args: argparse.Namespace) -> int:
    documents = load_manifest(args.manifest)
    if not args.apply:
        print(f"DRY RUN OK: validated {len(documents)} media items; no database connection or write")
        return 0

    # All local validation and external URL checks finish before Mongo is created.
    verify_manifest_urls(documents, args.base_url)
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).with_name(".env"))
    except ImportError:
        pass
    mongo_url = os.environ.get("MONGO_URL", "").strip()
    db_name = os.environ.get("DB_NAME", "").strip()
    if not mongo_url or not db_name:
        raise MediaCatalogValidationError("MONGO_URL and DB_NAME are required for --apply")
    if not args.confirm_db_name or args.confirm_db_name != db_name:
        raise MediaCatalogValidationError("--confirm-db-name must exactly match DB_NAME")

    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(mongo_url)
    try:
        collection = client[db_name]["media_catalog"]
        ids = [item["media_id"] for item in documents]
        before = await collection.find({"media_id": {"$in": ids}}).to_list(length=len(ids))
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_path = args.snapshot_dir / f"media_catalog_before_{stamp}.json"
        write_before_snapshot(snapshot_path, before, ids)
        counts = await seed_collection(collection, documents, datetime.now(timezone.utc))
        print(
            f"APPLY OK database={db_name} matched={counts['matched']} "
            f"modified={counts['modified']} upserted={counts['upserted']} "
            f"unchanged={counts['unchanged']} snapshot={snapshot_path}"
        )
    finally:
        client.close()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        return asyncio.run(async_main(args))
    except MediaCatalogValidationError as exc:
        print(f"VALIDATION FAILED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
