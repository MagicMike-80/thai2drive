"""
Quality check — simulate 100 exam sessions and report:
  1. Difficulty distribution (hard/medium/easy)
  2. Correct-answer position distribution (A/B/C/D after shuffle)

Usage:
  python check_quiz_quality.py

Reads from MongoDB directly using MONGO_URL from .env
"""
import asyncio, os, random, sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from collections import Counter

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parent / ".env")
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME   = os.environ["DB_NAME"]

IMAGE_FILTER = {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}
LETTERS = ["A", "B", "C", "D"]


def shuffle_opts_correct(opts: list, correct_id: str) -> str:
    """Simulate frontend shuffleOpts — returns new display letter of correct answer."""
    arr = opts[:]
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    for i, o in enumerate(arr):
        if o["id"] == correct_id:
            return LETTERS[i]
    return correct_id  # fallback (shouldn't happen)


async def fetch_exam_questions(db, count: int = 45) -> list:
    """Mirror of _get_exam_questions (no user history — clean session)."""
    hard_slot   = round(count * 0.90)
    medium_slot = count - hard_slot

    hard_qs = await db.questions.aggregate([
        {"$match": {**IMAGE_FILTER, "difficulty": "hard"}},
        {"$sample": {"size": hard_slot}},
        {"$project": {"_id": 0, "id": 1, "difficulty": 1, "correctOptionId": 1,
                       "correct_answer": 1, "options": 1}},
    ]).to_list(hard_slot)

    exclude = [q["id"] for q in hard_qs if q.get("id")]

    medium_match = {**IMAGE_FILTER, "difficulty": "medium"}
    if exclude:
        medium_match["id"] = {"$nin": exclude}
    medium_qs = await db.questions.aggregate([
        {"$match": medium_match},
        {"$sample": {"size": medium_slot}},
        {"$project": {"_id": 0, "id": 1, "difficulty": 1, "correctOptionId": 1,
                       "correct_answer": 1, "options": 1}},
    ]).to_list(medium_slot)

    # Top up if not enough
    all_qs = hard_qs + medium_qs
    if len(all_qs) < count:
        needed = count - len(all_qs)
        done_ids = [q["id"] for q in all_qs if q.get("id")]
        topup = await db.questions.aggregate([
            {"$match": {**IMAGE_FILTER, "id": {"$nin": done_ids}}},
            {"$sample": {"size": needed}},
            {"$project": {"_id": 0, "id": 1, "difficulty": 1, "correctOptionId": 1,
                           "correct_answer": 1, "options": 1}},
        ]).to_list(needed)
        all_qs += topup

    random.shuffle(all_qs)
    return all_qs


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    SESSIONS   = 100
    Q_PER_EXAM = 45

    diff_counter    = Counter()
    position_counter = Counter()
    total_questions = 0

    print(f"Simulating {SESSIONS} exam sessions × {Q_PER_EXAM} questions each …")

    for s in range(SESSIONS):
        questions = await fetch_exam_questions(db, Q_PER_EXAM)
        for q in questions:
            total_questions += 1
            diff = q.get("difficulty") or "unknown"
            diff_counter[diff] += 1

            # Simulate answer shuffle
            correct_id = (q.get("correctOptionId") or q.get("correct_answer") or "").upper()
            opts = q.get("options") or []
            if isinstance(opts, list) and len(opts) > 1 and correct_id:
                opt_objs = [{"id": str(o.get("id", o.get("key", ""))).upper()} for o in opts]
                new_letter = shuffle_opts_correct(opt_objs, correct_id)
                position_counter[new_letter] += 1
            else:
                position_counter[correct_id or "?"] += 1

    client.close()

    print(f"\n{'='*50}")
    print(f"  {SESSIONS} sessions × {Q_PER_EXAM} questions = {total_questions} total")
    print(f"{'='*50}")

    print("\n── Difficulty distribution ──")
    for diff in ("hard", "medium", "easy", "unknown"):
        n = diff_counter[diff]
        pct = 100 * n / total_questions if total_questions else 0
        bar = "█" * int(pct / 2)
        print(f"  {diff:<8} {n:>6}  ({pct:5.1f}%)  {bar}")

    print("\n── Correct-answer position after shuffle ──")
    for letter in LETTERS:
        n = position_counter[letter]
        pct = 100 * n / total_questions if total_questions else 0
        bar = "█" * int(pct / 2)
        expected_diff = abs(pct - 25.0)
        flag = "  ⚠️  off by >{:.1f}%".format(expected_diff) if expected_diff > 5 else ""
        print(f"  {letter}  {n:>6}  ({pct:5.1f}%)  {bar}{flag}")

    print("\n── Summary ──")
    hard_pct = 100 * diff_counter["hard"] / total_questions if total_questions else 0
    positions_ok = all(
        abs(100 * position_counter[l] / total_questions - 25.0) <= 5
        for l in LETTERS if total_questions
    )
    print(f"  Hard questions : {hard_pct:.1f}%  (target ≥ 85%)")
    print(f"  Position balance: {'✅ OK' if positions_ok else '⚠️  IMBALANCED'}")


if __name__ == "__main__":
    asyncio.run(main())
