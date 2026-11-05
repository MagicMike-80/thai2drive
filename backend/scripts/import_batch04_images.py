"""Validated, resumable Batch 04 quiz-image import via the shared media layer.

Dry-run by default. Requires explicit --apply and a fresh read-only target snapshot.
Never seeds questions or changes their text/answers.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from pathlib import Path

from gridfs import GridFSBucket
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.media_storage import prepare_media_upload


def _candidate_files(manifest: Path, images_dir: Path) -> list[tuple[dict, object]]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    rows = data.get("items") or []
    if len(rows) != 44 or len({row.get("question_id") for row in rows}) != 44:
        raise ValueError("Batch 04 manifest must contain 44 distinct question IDs")
    prepared = []
    for row in rows:
        if row.get("review") not in ("STRONG", "STRONG_CONTEXT"):
            raise ValueError(f"Unverified candidate: {row.get('question_id')}")
        name = row.get("image_file") or ""
        if Path(name).name != name or not name.endswith(".png"):
            raise ValueError(f"Invalid image filename: {name}")
        raw = (images_dir / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != row.get("manifest_sha256") or digest != row.get("actual_sha256"):
            raise ValueError(f"Image hash mismatch: {name}")
        media = prepare_media_upload(raw, name, "image/png")
        if media.media_type != "image" or media.content_type != "image/webp":
            raise ValueError(f"Image validation failed: {name}")
        prepared.append((row, media))
    return prepared


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--target-state", required=True, type=Path)
    parser.add_argument("--images-dir", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    rows = _candidate_files(args.manifest, args.images_dir)
    state_data = json.loads(args.target_state.read_text(encoding="utf-8"))
    state = {row["question_id"]: row for row in state_data.get("items", [])}
    if len(state) != 44:
        raise ValueError("Target snapshot must contain 44 distinct questions")
    uri = os.environ.get("MONGO_URL")
    if not uri:
        raise RuntimeError("MONGO_URL missing")
    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    database = client[os.environ.get("DB_NAME") or "thai2drive"]
    questions = database.questions
    bucket = GridFSBucket(database)
    pending = []
    already_imported = []
    for row, media in rows:
        question_id = row["question_id"]
        expected = state.get(question_id)
        if not expected or not expected.get("active") or not expected.get("question_no_matches"):
            raise ValueError(f"Snapshot does not approve {question_id}")
        question = questions.find_one({"id": question_id}, {
            "_id": 0, "active": 1, "bildeUrl": 1, "bildeUrl_original_backup": 1,
            "question.no": 1,
        })
        if not question or not question.get("active") or (question.get("question") or {}).get("no") != row["candidate_question_no"]:
            raise ValueError(f"Question changed or inactive: {question_id}")
        current = question.get("bildeUrl") or ""
        if current.startswith("/api/media/files/"):
            from bson import ObjectId
            try:
                file_id = ObjectId(current.rsplit("/", 1)[-1])
                file_doc = database.fs.files.find_one({"_id": file_id}, {"metadata": 1}) or {}
            except Exception:
                file_doc = {}
            metadata = file_doc.get("metadata") or {}
            if metadata.get("original_filename") == row["image_file"] and metadata.get("source_sha256") == row["manifest_sha256"]:
                already_imported.append(question_id)
                continue
        expected_current = expected.get("image_url") or ""
        if current != expected_current:
            raise ValueError(f"Image state changed since export: {question_id}")
        pending.append((row, media, question))

    summary = {"manifest_count": len(rows), "ready": len(pending),
               "already_imported": len(already_imported),
               "replacements": sum(bool(q.get("bildeUrl")) for _, _, q in pending),
               "mode": "apply" if args.apply else "dry_run"}
    print(json.dumps(summary))
    if not args.apply:
        client.close()
        return

    args.journal.parent.mkdir(parents=True, exist_ok=True)
    with args.journal.open("a", encoding="utf-8") as journal:
        for row, media, question in pending:
            question_id = row["question_id"]
            old = question.get("bildeUrl") or ""
            file_id = bucket.upload_from_stream(media.filename, io.BytesIO(media.data), metadata={
                "content_type": media.content_type,
                "media_type": media.media_type,
                "original_filename": media.original_filename,
                "transformed": media.transformed,
                "source_sha256": row["manifest_sha256"],
                "question_id": question_id,
                "batch": "04",
            })
            url = f"/api/media/files/{file_id}"
            selector = {"id": question_id, "active": True,
                        "question.no": row["candidate_question_no"]}
            if old:
                selector["bildeUrl"] = old
            else:
                selector["$or"] = [{"bildeUrl": {"$exists": False}},
                                   {"bildeUrl": None}, {"bildeUrl": ""}]
            backup = old or question.get("bildeUrl_original_backup")
            try:
                result = questions.update_one(selector, {"$set": {
                    "bildeUrl": url, "bildeUrl_original_backup": backup,
                }})
                if result.matched_count != 1:
                    raise RuntimeError(f"Concurrent question change: {question_id}")
            except Exception:
                bucket.delete(file_id)
                raise
            journal.write(json.dumps({"question_id": question_id, "file_id": str(file_id),
                                      "url": url, "replaced": bool(old)}) + "\n")
            journal.flush()
            print(json.dumps({"question_id": question_id, "url": url}))

    verified = 0
    for row, _ in rows:
        question = questions.find_one({"id": row["question_id"]}, {"bildeUrl": 1}) or {}
        current = question.get("bildeUrl") or ""
        if not current.startswith("/api/media/files/"):
            raise RuntimeError(f"Missing imported image: {row['question_id']}")
        from bson import ObjectId
        media = database.fs.files.find_one({"_id": ObjectId(current.rsplit("/", 1)[-1])}, {"metadata": 1}) or {}
        metadata = media.get("metadata") or {}
        if metadata.get("source_sha256") != row["manifest_sha256"]:
            raise RuntimeError(f"Image hash metadata mismatch: {row['question_id']}")
        verified += 1
    print(json.dumps({"verified_batch04_links": verified}))
    client.close()


if __name__ == "__main__":
    run()
