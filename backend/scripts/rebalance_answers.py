"""
Rebalance correctOptionId distribution across all questions.
Target: A/B/C/D each ~25%.

Data model:
  {
    "options": [{"id": "A", "text": {"no": ..., "th": ..., "en": ..., ...}}, ...],
    "correctOptionId": "A"
  }

Strategy: for each question, swap the "text" payload between the current correct
slot and the desired new slot. IDs remain A/B/C/D. Only the content moves.
"""
import os
import random
from collections import Counter
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('/app/backend/.env')

client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'thai2drive')]
col = db['questions']

LETTERS = ['A', 'B', 'C', 'D']


def distribution():
    dist = Counter()
    total = 0
    for q in col.find({}, {'correctOptionId': 1}):
        c = q.get('correctOptionId')
        if c in LETTERS:
            dist[c] += 1
            total += 1
    return dist, total


def rebalance():
    before, total = distribution()
    print(f"Total: {total}")
    for L in LETTERS:
        print(f"  {L}: {before[L]:4d} ({before[L]/total*100:.1f}%)")

    # Build ideal target count per letter
    base = total // 4
    rem = total - base * 4
    targets = {L: base + (1 if i < rem else 0) for i, L in enumerate(LETTERS)}

    # Create a shuffled list of desired correct letters
    desired = []
    for L, n in targets.items():
        desired.extend([L] * n)
    random.seed(42)
    random.shuffle(desired)

    all_q = list(col.find({}, {'_id': 1, 'options': 1, 'correctOptionId': 1}))
    random.shuffle(all_q)

    assert len(desired) == len(all_q), f"Mismatch {len(desired)} vs {len(all_q)}"

    updates = 0
    for q, want_letter in zip(all_q, desired):
        options = q.get('options', [])
        old_letter = q.get('correctOptionId')

        if len(options) != 4 or old_letter not in LETTERS:
            continue
        if old_letter == want_letter:
            continue

        # Locate the two option objects by id
        old_opt = next((o for o in options if o.get('id') == old_letter), None)
        new_opt = next((o for o in options if o.get('id') == want_letter), None)
        if not old_opt or not new_opt:
            continue

        # Swap the "text" payload (the only mutable content) — IDs stay A/B/C/D
        swapped_options = []
        for o in options:
            new_o = dict(o)
            if o.get('id') == old_letter:
                new_o['text'] = new_opt.get('text', {})
            elif o.get('id') == want_letter:
                new_o['text'] = old_opt.get('text', {})
            swapped_options.append(new_o)

        col.update_one(
            {'_id': q['_id']},
            {'$set': {'options': swapped_options, 'correctOptionId': want_letter}}
        )
        updates += 1

    print(f"\nApplied {updates} updates")

    after, total_after = distribution()
    print(f"\nAfter ({total_after} questions):")
    for L in LETTERS:
        pct = after[L] / total_after * 100 if total_after else 0
        bar = '█' * int(pct / 2)
        print(f"  {L}: {after[L]:4d} ({pct:5.1f}%) {bar}")

    # Quality check: no letter should deviate more than 2% from 25%
    max_dev = max(abs(after[L] / total_after * 100 - 25) for L in LETTERS)
    print(f"\nMax deviation from 25%: {max_dev:.2f}%")


if __name__ == '__main__':
    rebalance()
