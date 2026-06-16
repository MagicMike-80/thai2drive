"""
Import a Thai2Drive content pack into MongoDB.

Default: DRY-RUN only. Pass --commit to write to the database.

Usage:
  python import_content_pack.py <pack_name> [--dry-run] [--commit]

Examples:
  python import_content_pack.py stoppelengde_intensiv
  python import_content_pack.py stoppelengde_intensiv --dry-run
  python import_content_pack.py stoppelengde_intensiv --commit

Exit codes:
  0 — success (or clean dry-run)
  1 — validation errors found (nothing was written)
  2 — argument / file error
"""
import asyncio
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ── Encoding safety on Windows ────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent          # backend/content_packs/
BACKEND_DIR  = SCRIPT_DIR.parent              # backend/
ENV_FILE     = BACKEND_DIR / ".env"

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except ImportError:
    # Manual .env parse — no dependency on python-dotenv
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME   = os.environ.get("DB_NAME", "thai2drive")

# ── Constants ─────────────────────────────────────────────────────────────────
REQUIRED_FIELDS = [
    "id", "category", "difficulty",
    "question_no", "question_th", "question_en",
    "options_no", "options_th", "options_en",
    "correct_index",
    "explanation_no", "explanation_th", "explanation_en",
]
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_LETTERS      = ["A", "B", "C", "D"]

# ── Language Purity constants ─────────────────────────────────────────────────
# Thai Unicode block: U+0E00 – U+0E7F
_THAI_RE = __import__("re").compile(r"[\u0e00-\u0e7f]")

# Minimum number of Thai characters required in a _th field to be considered Thai.
_THAI_MIN_CHARS = 3

# Fields that MUST contain Thai characters
_THAI_FIELDS = [
    "question_th", "explanation_th",
    "options_th",  # checked individually per option
]
# Fields that must NOT contain Thai characters
_NON_THAI_FIELDS = [
    "question_no", "explanation_no",
    "question_en", "explanation_en",
]


def _has_thai(text: str) -> bool:
    """Return True if *text* contains at least _THAI_MIN_CHARS Thai characters."""
    return len(_THAI_RE.findall(text)) >= _THAI_MIN_CHARS


def _has_any_thai(text: str) -> bool:
    """Return True if *text* contains even a single Thai character."""
    return bool(_THAI_RE.search(text))

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ok(msg: str)  -> None: print(f"  ✅ {msg}")
def _err(msg: str) -> None: print(f"  ❌ {msg}")
def _warn(msg: str)-> None: print(f"  ⚠️  {msg}")
def _info(msg: str)-> None: print(f"     {msg}")


def _validate_question(q: dict, images_dir: Path) -> list[str]:
    """Return a list of error strings (empty = valid)."""
    errors: list[str] = []
    qid = q.get("id", "(no id)")

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in q or q[field] is None or q[field] == "":
            errors.append(f"[{qid}] Missing required field: '{field}'")

    # Translations — non-empty strings for all three languages
    for lang_suffix in ("no", "th", "en"):
        for prefix in ("question", "explanation"):
            key = f"{prefix}_{lang_suffix}"
            val = q.get(key, "")
            if not isinstance(val, str) or not val.strip():
                errors.append(f"[{qid}] Translation missing or empty: '{key}'")

    # Options — each language must have exactly 4 non-empty entries
    for lang_suffix in ("no", "th", "en"):
        key = f"options_{lang_suffix}"
        opts = q.get(key)
        if not isinstance(opts, list):
            errors.append(f"[{qid}] '{key}' must be a list")
        elif len(opts) < 2:
            errors.append(f"[{qid}] '{key}' must have at least 2 options, got {len(opts)}")
        elif len(opts) > 4:
            errors.append(f"[{qid}] '{key}' has more than 4 options ({len(opts)})")
        else:
            for i, o in enumerate(opts):
                if not isinstance(o, str) or not o.strip():
                    errors.append(f"[{qid}] '{key}[{i}]' is empty")

    # correct_index must be valid for options_no length
    opts_no = q.get("options_no") or []
    if isinstance(opts_no, list) and len(opts_no) >= 2:
        ci = q.get("correct_index")
        if not isinstance(ci, int) or ci < 0 or ci >= len(opts_no):
            errors.append(
                f"[{qid}] 'correct_index' ({ci!r}) is out of range "
                f"for options_no (len={len(opts_no)})"
            )

    # difficulty must be known
    diff = q.get("difficulty", "")
    if diff not in VALID_DIFFICULTIES:
        errors.append(f"[{qid}] 'difficulty' must be one of {sorted(VALID_DIFFICULTIES)}, got {diff!r}")

    # image file check — only if image is non-empty
    image_val = q.get("image", "")
    if isinstance(image_val, str) and image_val.strip():
        img_path = images_dir / image_val.strip()
        if not img_path.exists():
            errors.append(f"[{qid}] Image file not found: images/{image_val.strip()}")

    # ── Language Purity checks (fail-stop) ───────────────────────────────────
    # Rule 1: _th fields MUST contain Thai characters.
    for th_key in ("question_th", "explanation_th"):
        val = q.get(th_key, "")
        if isinstance(val, str) and val.strip() and not _has_thai(val):
            errors.append(
                f"[{qid}] Language Purity FAIL: '{th_key}' contains no Thai characters "
                f"(min {_THAI_MIN_CHARS} required). Got: {val[:60]!r}"
            )

    opts_th = q.get("options_th")
    if isinstance(opts_th, list):
        for i, opt in enumerate(opts_th):
            if isinstance(opt, str) and opt.strip() and not _has_thai(opt):
                errors.append(
                    f"[{qid}] Language Purity FAIL: 'options_th[{i}]' contains no Thai characters. "
                    f"Got: {opt[:40]!r}"
                )

    # Rule 2: _no and _en fields must NOT contain Thai characters.
    for non_thai_key in _NON_THAI_FIELDS:
        val = q.get(non_thai_key, "")
        if isinstance(val, str) and _has_any_thai(val):
            errors.append(
                f"[{qid}] Language Purity FAIL: '{non_thai_key}' must not contain Thai characters. "
                f"Got: {val[:60]!r}"
            )

    opts_no = q.get("options_no") or []
    opts_en = q.get("options_en") or []
    for lang_label, opts in (("no", opts_no), ("en", opts_en)):
        if isinstance(opts, list):
            for i, opt in enumerate(opts):
                if isinstance(opt, str) and _has_any_thai(opt):
                    errors.append(
                        f"[{qid}] Language Purity FAIL: 'options_{lang_label}[{i}]' "
                        f"must not contain Thai characters. Got: {opt[:40]!r}"
                    )

    return errors


def _to_db_doc(q: dict) -> dict:
    """
    Convert pack schema → Thai2Drive v2 DB schema.

    Pack field          DB field
    ─────────────────────────────────────────────
    id                  id
    topic               topic (extra metadata)
    category            category
    difficulty          difficulty
    image               bildeUrl  (filename only — no upload needed if already hosted)
    question_no/th/en   question.no/th/en
    options_no/th/en    options[].text.no/th/en  + options[].id = A/B/C/D
    correct_index       correctOptionId  (0→A, 1→B, 2→C, 3→D)
    explanation_*       explanation.no/th/en
    tags                tags
    """
    opts_no = q.get("options_no", [])
    opts_th = q.get("options_th", [])
    opts_en = q.get("options_en", [])
    n_opts  = len(opts_no)

    options = []
    for i in range(n_opts):
        options.append({
            "id":   VALID_LETTERS[i],
            "text": {
                "no": opts_no[i] if i < len(opts_no) else "",
                "th": opts_th[i] if i < len(opts_th) else "",
                "en": opts_en[i] if i < len(opts_en) else "",
            },
        })

    correct_idx   = q.get("correct_index", 0)
    correct_id    = VALID_LETTERS[correct_idx] if 0 <= correct_idx < len(VALID_LETTERS) else "A"
    image_val     = (q.get("image") or "").strip()

    return {
        "id":            q["id"],
        "topic":         q.get("topic", ""),
        "category":      q.get("category", ""),
        "difficulty":    q.get("difficulty", "medium"),
        "bildeUrl":      image_val,          # filename for now; update to full URL after upload
        "question": {
            "no": q.get("question_no", ""),
            "th": q.get("question_th", ""),
            "en": q.get("question_en", ""),
        },
        "options":          options,
        "correctOptionId":  correct_id,
        "explanation": {
            "no": q.get("explanation_no", ""),
            "th": q.get("explanation_th", ""),
            "en": q.get("explanation_en", ""),
        },
        "tags":          q.get("tags", []),
        "active":        True,
        "source_pack":   q.get("_pack_name", ""),
        "created_at":    datetime.now(timezone.utc).isoformat(),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

async def run(pack_name: str, commit: bool) -> int:
    mode_label = "COMMIT" if commit else "DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  import_content_pack  —  {mode_label}")
    print(f"  Pack: {pack_name}")
    print(f"{'='*60}\n")

    # ── Locate pack ───────────────────────────────────────────────────────
    pack_dir    = SCRIPT_DIR / pack_name
    json_file   = pack_dir / "questions_no_th_en.json"
    images_dir  = pack_dir / "images"

    if not pack_dir.is_dir():
        print(f"ERROR: Pack folder not found: {pack_dir}")
        return 2
    if not json_file.exists():
        print(f"ERROR: questions file not found: {json_file}")
        return 2

    # ── Load questions ────────────────────────────────────────────────────
    try:
        questions = json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: JSON parse error in {json_file.name}: {exc}")
        return 2

    if not isinstance(questions, list) or not questions:
        print("ERROR: questions file must be a non-empty JSON array.")
        return 2

    print(f"Loaded {len(questions)} questions from {json_file.name}\n")

    # ── Validation pass ───────────────────────────────────────────────────
    print("── Validation ──────────────────────────────────────────")
    all_errors: list[str] = []
    seen_ids:   set[str]  = set()

    for q in questions:
        # Tag with pack name for DB tracking
        q["_pack_name"] = pack_name

        qid = q.get("id", "")

        # Duplicate ID check (within this file)
        if qid in seen_ids:
            all_errors.append(f"[{qid}] Duplicate id in this pack file")
        else:
            seen_ids.add(qid)

        errs = _validate_question(q, images_dir)
        all_errors.extend(errs)

    if all_errors:
        print(f"  Found {len(all_errors)} validation error(s):\n")
        for e in all_errors:
            _err(e)
        print(f"\nFix errors before importing. Nothing was written.")
        return 1
    else:
        _ok(f"All {len(questions)} questions passed validation")

    # ── DB duplicate check ────────────────────────────────────────────────
    print("\n── Duplicate check (MongoDB) ───────────────────────────")
    if not MONGO_URL:
        _warn("MONGO_URL not set — skipping DB duplicate check")
        existing_ids: set[str] = set()
    else:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=8000)
            db     = client[DB_NAME]
            pack_ids   = list(seen_ids)
            cursor     = db.questions.find({"id": {"$in": pack_ids}}, {"_id": 0, "id": 1})
            found_docs = await cursor.to_list(len(pack_ids))
            existing_ids = {d["id"] for d in found_docs}
            client.close()
        except Exception as exc:
            _warn(f"Could not reach MongoDB: {exc}")
            existing_ids = set()

    new_ids      = seen_ids - existing_ids
    skipped_ids  = seen_ids & existing_ids

    if skipped_ids:
        _warn(f"{len(skipped_ids)} question(s) already exist in DB — will SKIP:")
        for sid in sorted(skipped_ids):
            _info(f"skip: {sid}")
    if new_ids:
        _ok(f"{len(new_ids)} new question(s) to import")

    # ── Preview ───────────────────────────────────────────────────────────
    print("\n── Preview (first 3 new questions) ─────────────────────")
    preview_count = 0
    for q in questions:
        if q["id"] not in new_ids:
            continue
        doc = _to_db_doc(q)
        print(f"\n  id          : {doc['id']}")
        print(f"  difficulty  : {doc['difficulty']}")
        print(f"  category    : {doc['category']}")
        print(f"  bildeUrl    : {doc['bildeUrl'] or '(none)'}")
        print(f"  correctId   : {doc['correctOptionId']}")
        print(f"  question.no : {doc['question']['no'][:70]}…" if len(doc['question']['no']) > 70 else f"  question.no : {doc['question']['no']}")
        preview_count += 1
        if preview_count >= 3:
            remaining = len(new_ids) - 3
            if remaining > 0:
                print(f"\n  … and {remaining} more")
            break

    # ── Dry-run summary ───────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    print(f"  Total in file  : {len(questions)}")
    print(f"  New (to import): {len(new_ids)}")
    print(f"  Skipped (exist): {len(skipped_ids)}")
    print(f"  Errors         : {len(all_errors)}")

    if not commit:
        print(f"\n  Mode: DRY-RUN — nothing written.")
        print(f"  Run with --commit to import {len(new_ids)} question(s).")
        print()
        return 0

    # ── Commit ────────────────────────────────────────────────────────────
    if not new_ids:
        print("\n  Nothing to import (all questions already exist).")
        print()
        return 0

    if not MONGO_URL:
        print("\nERROR: MONGO_URL not set — cannot commit.")
        return 2

    print(f"\n── Importing {len(new_ids)} question(s) ─────────────────────")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(MONGO_URL)
        db     = client[DB_NAME]

        inserted = 0
        for q in questions:
            if q["id"] not in new_ids:
                continue
            doc = _to_db_doc(q)
            await db.questions.insert_one(doc)
            _ok(f"Inserted: {doc['id']}")
            inserted += 1

        client.close()
        print(f"\n  Done. {inserted} question(s) imported into '{DB_NAME}.questions'.")
    except Exception as exc:
        print(f"\nERROR during import: {exc}")
        return 1

    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a Thai2Drive content pack into MongoDB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pack_name", help="Name of the pack folder under content_packs/")
    parser.add_argument(
        "--dry-run", "--dryrun", dest="dry_run", action="store_true",
        help="Validate and preview only — do not write to DB (default if --commit absent)",
    )
    parser.add_argument(
        "--commit", dest="commit", action="store_true",
        help="Actually write to MongoDB after validation passes",
    )
    args = parser.parse_args()

    if args.commit and args.dry_run:
        print("ERROR: --dry-run and --commit are mutually exclusive.")
        sys.exit(2)

    # Default: dry-run
    commit = args.commit

    exit_code = asyncio.run(run(args.pack_name, commit=commit))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
