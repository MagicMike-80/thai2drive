"""
Apply AI Vision Audit fixes.

Strategy:
- 12 MATCH questions -> keep image as is
- 20 MISMATCH questions -> REMOVE the misleading image (set bildeUrl = "")
  (correct options are all correct per audit, so only image needs removing)
- Backup original bildeUrl into bildeUrl_original_backup for rollback

Also generates a human-readable audit report markdown.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "test_database")]

report_path = Path(__file__).parent / "audit_report.json"
report = json.loads(report_path.read_text())

mismatches = [r for r in report if r.get("verdict") == "MISMATCH"]
matches = [r for r in report if r.get("verdict") == "MATCH"]
errors = [r for r in report if r.get("verdict") not in ("MATCH", "MISMATCH")]

print(f"MATCH: {len(matches)}  MISMATCH: {len(mismatches)}  ERROR: {len(errors)}")

# --- Apply fixes: remove bildeUrl from mismatches, backup original ---
removed = 0
for r in mismatches:
    qid = r["question_id"]
    q = db.questions.find_one({"id": qid})
    if not q:
        continue
    orig = q.get("bildeUrl", "")
    if not orig:
        continue
    db.questions.update_one(
        {"id": qid},
        {
            "$set": {
                "bildeUrl": "",
                "bildeUrl_original_backup": orig,
                "audit_verdict": "MISMATCH",
                "audit_image_identification": r.get("image_identification", ""),
                "audit_issues": r.get("issues", []),
            }
        },
    )
    removed += 1

for r in matches:
    db.questions.update_one(
        {"id": r["question_id"]},
        {"$set": {"audit_verdict": "MATCH"}},
    )

print(f"Removed {removed} misleading images. Questions still intact (text-only).")

# --- Generate human-readable markdown report ---
lines = [
    "# Thai2Drive — AI Vision Audit Report",
    "",
    f"- **Total image questions audited:** {len(report)}",
    f"- **✅ MATCH (bilde + spørsmål stemmer):** {len(matches)}",
    f"- **❌ MISMATCH (bilde fjernet, spørsmålstekst beholdt):** {len(mismatches)}",
    f"- **⚠️ ERROR (audit feilet):** {len(errors)}",
    "",
    "All riktige svar er bekreftet korrekte. Kun villedende bilder er fjernet.",
    "Original bilder er sikkerhetskopiert i `bildeUrl_original_backup` for rollback.",
    "",
    "---",
    "",
    "## ❌ MISMATCHES (bilde fjernet)",
    "",
]
for i, r in enumerate(mismatches, 1):
    lines.append(f"### {i}. `{r['question_id'][:8]}…` — {r.get('category', '')}")
    lines.append(f"**Bildet viste faktisk:** {r.get('image_identification', 'ukjent')}")
    lines.append("")
    lines.append(f"**Spørsmål:** {r.get('current_question_no', '')}")
    lines.append(f"**Riktig svar (uendret):** {r.get('current_correct_option')} — {r.get('current_correct_text_no', '')}")
    lines.append("")
    lines.append("**Problemer funnet:**")
    for issue in r.get("issues", []):
        lines.append(f"- {issue}")
    fix = r.get("suggested_fix") or {}
    sq = fix.get("question_no")
    se = fix.get("explanation_no")
    if sq or se:
        lines.append("")
        lines.append("**AI-foreslått tekst-fix (ikke brukt, men til referanse):**")
        if sq:
            lines.append(f"- Spørsmål: _{sq}_")
        if se:
            lines.append(f"- Forklaring: _{se}_")
    lines.append("")

lines += ["---", "", "## ✅ MATCHES (bilde beholdt)", ""]
for i, r in enumerate(matches, 1):
    lines.append(f"{i}. `{r['question_id'][:8]}…` — {r.get('image_identification', '')}  — _{r.get('current_question_no', '')[:70]}_")

out = Path(__file__).parent / "audit_report.md"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote markdown report: {out}")
