"""
enrich_sign_content.py
━━━━━━━━━━━━━━━━━━━━━
Generates multilingual names + explanations for all 316 traffic signs
using Claude API. Writes results directly to MongoDB.

Usage:
  python enrich_sign_content.py              # run all missing signs
  python enrich_sign_content.py --dry-run    # preview first batch only
  python enrich_sign_content.py --start 40  # skip first 40 signs (resume)

Norwegian skiltforskriften sign number series:
  100s = Fareskilt (Warning)
  200s = Vikeplikt + Forbudtskilt (Yield / Prohibition)
  300s = Forbudtskilt (Prohibition)
  400s = Påbudsskilt (Mandatory)
  500s = Opplysningsskilt (Information)
  600s = Serviceskilt (Service)
  700s = Veivisningsskilt (Direction)
  800s = Underskilt (Supplementary)
  900s = Markeringsskilt (Road marking)
"""

import os, sys, json, time, re, argparse
from pathlib import Path
from dotenv import load_dotenv
import pymongo
import anthropic

from dotenv import dotenv_values as _dv
_env = _dv(Path(__file__).parent / '.env')
load_dotenv(Path(__file__).parent / '.env', override=True)

MONGO_URL  = _env.get('MONGO_URL') or os.environ['MONGO_URL']
DB_NAME    = _env.get('DB_NAME')   or os.environ['DB_NAME']
ANTH_KEY   = _env.get('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_API_KEY', '')
BATCH_SIZE = 20
SLEEP_BETWEEN_BATCHES = 2  # seconds, be polite to API

SIGN_GROUPS = {
    1: {"no": "Vikepliktskilt",   "th": "ป้ายให้ทาง",        "en": "Yield signs"},
    2: {"no": "Fareskilt",        "th": "ป้ายเตือน",          "en": "Warning signs"},
    3: {"no": "Forbudtskilt",     "th": "ป้ายห้าม",           "en": "Prohibition signs"},
    4: {"no": "Påbudsskilt",      "th": "ป้ายบังคับ",         "en": "Mandatory signs"},
    5: {"no": "Opplysningsskilt", "th": "ป้ายแจ้ง",           "en": "Information signs"},
    6: {"no": "Serviceskilt",     "th": "ป้ายบริการ",         "en": "Service signs"},
    7: {"no": "Veivisningsskilt", "th": "ป้ายนำทาง",          "en": "Direction signs"},
    8: {"no": "Underskilt",       "th": "ป้ายเสริม",          "en": "Supplementary signs"},
    9: {"no": "Markeringsskilt",  "th": "ป้ายเครื่องหมาย",    "en": "Road marking signs"},
}

SYSTEM_PROMPT = """You are an expert on Norwegian traffic law and the Norwegian Skiltforskriften (sign regulations).
You generate short, beginner-friendly, multilingual content for traffic signs used in a Norwegian driving theory app for Thai learners.

Content style rules:
- Names: official Norwegian name (2–5 words). No jargon.
- Explanations: 1 short sentence — what the sign means + what the driver must do.
  Example: "Stopp for annen trafikk og la dem passere før du kjører videre."
- Thai explanations must be natural Thai, not word-for-word translations — easy for beginners.
- English explanations must be clear and simple — learner level.
- Do NOT add sign numbers, prefixes, or footnotes.
- Do NOT add sign numbers in the name field — just the name."""

def build_prompt(batch: list[dict]) -> str:
    lines = []
    for s in batch:
        g = s['group']
        gname_no = SIGN_GROUPS.get(g, {}).get('no', f'Group {g}')
        lines.append(f'  sign_id: "{s["id"]}"  group: {g} ({gname_no})')
    signs_block = "\n".join(lines)

    return f"""Generate content for these Norwegian traffic signs. Return ONLY a valid JSON array.

Signs:
{signs_block}

For each sign return exactly this JSON object:
{{
  "id": "<sign_id>",
  "name": {{"no": "<Norwegian name>", "th": "<Thai name>", "en": "<English name>"}},
  "explanation": {{"no": "<Norwegian 1-sentence explanation>", "th": "<Thai 1-sentence explanation>", "en": "<English 1-sentence explanation>"}}
}}

Rules:
- name.no = official Norwegian name from Skiltforskriften (2–5 words, no sign number)
- explanation = what the sign means + what driver must do (1 sentence each language)
- Thai must be natural and beginner-friendly
- Return a JSON array and nothing else — no markdown, no code fences, no commentary

Sign number reference:
  100-series = Fareskilt (warning hazards ahead)
  202-210     = Vikeplikt (yield/priority)
  212-220     = Specific yield scenarios (railway, etc.)
  300-series  = Forbudtskilt (prohibition: no entry, no parking, speed limits)
  400-series  = Påbudsskilt (mandatory: direction, roundabout)
  500-series  = Opplysningsskilt (information: hospital, parking, motorway)
  600-series  = Serviceskilt (fuel, food, rest areas)
  700-series  = Veivisningsskilt (direction markers)
  800-series  = Underskilt (supplementary: distance, condition, time)
  900-series  = Markeringsskilt (delineators, chevrons)"""


def parse_response(text: str) -> list[dict]:
    """Extract JSON array from model response robustly."""
    # Strip code fences if present
    text = re.sub(r'```(?:json)?\s*', '', text).strip().rstrip('`').strip()
    # Find the outermost [ ... ]
    start = text.find('[')
    end   = text.rfind(']')
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in response:\n{text[:400]}")
    return json.loads(text[start:end+1])


def enrich(dry_run: bool = False, start_offset: int = 0):
    client_mongo = pymongo.MongoClient(MONGO_URL)
    db = client_mongo[DB_NAME]
    client_anth  = anthropic.Anthropic(api_key=ANTH_KEY)

    # Fetch signs that need enrichment (name.no is empty or equals the sign ID)
    all_signs = list(db.traffic_signs.find(
        {},
        {'id': 1, 'group': 1, 'name': 1}
    ).sort('group', 1))

    to_enrich = [
        s for s in all_signs
        if not s.get('name', {}).get('no') or s['name']['no'] == s['id']
    ]

    print(f"Total signs: {len(all_signs)}")
    print(f"Need enrichment: {len(to_enrich)}")

    if start_offset:
        to_enrich = to_enrich[start_offset:]
        print(f"Skipping first {start_offset} (resume from #{start_offset + 1})")

    if not to_enrich:
        print("Nothing to enrich — all signs already have content.")
        return

    batches = [to_enrich[i:i+BATCH_SIZE] for i in range(0, len(to_enrich), BATCH_SIZE)]
    print(f"Batches: {len(batches)} × up to {BATCH_SIZE} signs")

    if dry_run:
        print("\n--- DRY RUN: only processing first batch ---")
        batches = batches[:1]

    total_updated = 0

    for batch_idx, batch in enumerate(batches, 1):
        ids = [s['id'] for s in batch]
        print(f"\n[Batch {batch_idx}/{len(batches)}] Signs: {ids[:5]}{'...' if len(ids)>5 else ''}")

        prompt = build_prompt(batch)

        try:
            resp = client_anth.messages.create(
                model="claude-opus-4-5",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text
        except Exception as e:
            print(f"  ERROR calling API: {e}")
            print("  Skipping batch — will need manual retry.")
            continue

        try:
            results = parse_response(raw)
        except Exception as e:
            print(f"  ERROR parsing response: {e}")
            print(f"  Raw response (first 500 chars):\n{raw[:500]}")
            continue

        # Build a lookup by id
        result_map = {r['id']: r for r in results}

        batch_updated = 0
        for sign in batch:
            sid = sign['id']
            if sid not in result_map:
                print(f"  WARNING: no result for sign {sid}")
                continue

            r = result_map[sid]
            name = r.get('name', {})
            expl = r.get('explanation', {})

            # Validate minimally
            if not name.get('no') or not expl.get('no'):
                print(f"  WARNING: incomplete result for {sid}: {r}")
                continue

            if dry_run:
                print(f"  [{sid}] name.no={name['no']!r}")
                print(f"         expl.no={expl['no']!r}")
                print(f"         name.th={name['th']!r}")
                print(f"         expl.th={expl['th']!r}")
            else:
                db.traffic_signs.update_one(
                    {'id': sid},
                    {'$set': {
                        'name.no': name.get('no', ''),
                        'name.th': name.get('th', ''),
                        'name.en': name.get('en', ''),
                        'explanation.no': expl.get('no', ''),
                        'explanation.th': expl.get('th', ''),
                        'explanation.en': expl.get('en', ''),
                    }}
                )
                batch_updated += 1

        total_updated += batch_updated
        print(f"  Updated {batch_updated} signs" + (" (dry-run)" if dry_run else ""))

        if not dry_run and batch_idx < len(batches):
            time.sleep(SLEEP_BETWEEN_BATCHES)

    print(f"\n{'DRY RUN complete' if dry_run else f'Done — {total_updated} signs updated in MongoDB'}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enrich traffic sign content via Claude API')
    parser.add_argument('--dry-run', action='store_true', help='Preview first batch, no DB writes')
    parser.add_argument('--start',   type=int, default=0, help='Skip first N signs (resume)')
    args = parser.parse_args()
    enrich(dry_run=args.dry_run, start_offset=args.start)
