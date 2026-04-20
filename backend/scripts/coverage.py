"""
Image coverage tracker for Thai2Drive quiz questions.

Usage (CLI):
    python scripts/coverage.py            # print current coverage
    python scripts/coverage.py --log      # append to coverage log file

Usage (as module):
    from scripts.coverage import log_coverage
    log_coverage("Added bridge crosswind question")
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

LOG_FILE = Path("/app/memory/image_coverage_log.md")
GOALS = [20, 30, 50, 75, 100]  # percent milestones


def get_counts() -> tuple[int, int]:
    client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DB_NAME", "test_database")]
    total = db.questions.count_documents({"active": True})
    with_img = db.questions.count_documents(
        {"active": True, "bildeUrl": {"$regex": "^data:"}}
    )
    return total, with_img


def format_line(total: int, with_img: int, note: str = "") -> str:
    pct = (with_img / total * 100) if total else 0
    # progress bar (20 chars)
    bar_width = 20
    filled = int(pct / 5)
    bar = "█" * filled + "░" * (bar_width - filled)

    # Next goal
    next_goal = next((g for g in GOALS if pct < g), None)
    if next_goal:
        needed = int(total * next_goal / 100) - with_img
        goal_str = f" → need +{needed} to reach {next_goal}%"
    else:
        goal_str = " 🎉 all goals reached"

    line = f"Image coverage: {pct:.1f}% ({with_img} / {total})  [{bar}]{goal_str}"
    if note:
        line = f"{note}\n  {line}"
    return line


def log_coverage(note: str = "") -> str:
    total, with_img = get_counts()
    line = format_line(total, with_img, note)
    print(line)

    # Append to markdown log
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build or update log file
    if not LOG_FILE.exists():
        header = (
            "# Thai2Drive — Image Coverage Log\n\n"
            "Tracks progress of pairing Norwegian driving theory questions with verified images.\n\n"
            "**Goals:** 20% → 30% → 50% → 75% → 100%\n\n"
            "| Timestamp | Questions | With image | Coverage | Note |\n"
            "|-----------|-----------|------------|----------|------|\n"
        )
        LOG_FILE.write_text(header, encoding="utf-8")

    pct = (with_img / total * 100) if total else 0
    row = f"| {ts} | {total} | {with_img} | **{pct:.1f}%** | {note or '-'} |\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(row)

    return line


if __name__ == "__main__":
    note = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    log_coverage(note)
