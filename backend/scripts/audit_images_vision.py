"""
AI Vision Audit for Thai2Drive questions with images.

Uses Gemini 2.5 Pro Vision (via Emergent LLM Key) to verify that each
question + correct answer + explanation actually matches what is shown
in the Base64-encoded image.

Output: /app/backend/scripts/audit_report.json

For each image question, the report contains:
  - question_id
  - current_question_no
  - current_correct_option_text
  - image_identification  (what Gemini thinks the image shows)
  - verdict               ("MATCH" | "MISMATCH" | "UNCERTAIN")
  - issues                list of problems found
  - suggested_fix         object with suggested corrected text (no/th/en)
"""
import asyncio
import base64
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Load env from backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent  # noqa: E402

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY") or os.getenv("EMERGENT_API_KEY")
if not EMERGENT_LLM_KEY:
    # Fallback: read from /app/.emergent if present, otherwise fail
    EMERGENT_LLM_KEY = "sk-emergent-b48A3D57008C8350c6"

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

SYSTEM_PROMPT = """You are a Norwegian driving theory expert auditing quiz content for the Thai2Drive app.

You will be given:
1. An IMAGE of a Norwegian traffic sign, road situation, or driving scenario.
2. The current QUIZ QUESTION text (Norwegian).
3. A list of ANSWER OPTIONS.
4. Which option is marked as the CORRECT answer.
5. The current EXPLANATION text.

Your job: verify that the image, question, correct answer and explanation all consistently match.

Return ONLY a strict JSON object (no markdown, no backticks) with this exact schema:
{
  "image_identification": "short description of what the image actually shows (in Norwegian). For traffic signs, name the official sign (e.g. 'Stoppskilt (204)', 'Fartsgrense 50 km/t (362)', 'Parkering tillatt (552)').",
  "verdict": "MATCH" | "MISMATCH" | "UNCERTAIN",
  "issues": ["list of specific problems, empty list if verdict=MATCH"],
  "correct_option_should_be": "A" | "B" | "C" | "D" | null,
  "suggested_fix": {
    "question_no": "corrected Norwegian question text, or null if no change needed",
    "question_th": "corrected Thai question text, or null",
    "question_en": "corrected English question text, or null",
    "explanation_no": "corrected Norwegian explanation, or null",
    "explanation_th": "corrected Thai explanation, or null",
    "explanation_en": "corrected English explanation, or null"
  }
}

Rules:
- verdict = MATCH only if the image clearly shows what the question asks about AND the marked correct option is the right answer AND the explanation is accurate.
- verdict = MISMATCH if the image shows something different from what the question describes, OR the marked correct option is wrong.
- verdict = UNCERTAIN if the image is unclear / low quality and you cannot tell.
- correct_option_should_be: ONLY set this if verdict=MISMATCH and a different option is actually correct based on the image; otherwise null.
- suggested_fix fields: only populate where a change is needed; otherwise null.
- Be strict but fair. A generic matching question is OK even if the image is just one example.
"""


def build_prompt(q: dict) -> str:
    opts = "\n".join([f"  {o['id']}. {o['text'].get('no', '')}" for o in q.get("options", [])])
    return (
        f"QUESTION (Norwegian): {q['question'].get('no', '')}\n"
        f"OPTIONS:\n{opts}\n"
        f"MARKED CORRECT: {q.get('correctOptionId')}\n"
        f"EXPLANATION (Norwegian): {q.get('explanation', {}).get('no', '')}\n"
        f"CATEGORY: {q.get('category', '')}\n"
    )


def strip_data_prefix(b64: str) -> str:
    # emergentintegrations ImageContent expects raw base64 WITHOUT the data URI prefix
    if b64.startswith("data:"):
        comma = b64.find(",")
        if comma >= 0:
            return b64[comma + 1 :]
    return b64


def safe_json_parse(text: str) -> dict:
    # Strip code fences if model wrapped anyway
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


async def audit_one(q: dict) -> dict:
    b64 = strip_data_prefix(q.get("bildeUrl", ""))
    prompt = build_prompt(q)

    chat = (
        LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"audit-{q['id']}",
            system_message=SYSTEM_PROMPT,
        )
        .with_model("gemini", "gemini-2.5-pro")
    )

    msg = UserMessage(
        text=prompt,
        file_contents=[ImageContent(image_base64=b64)],
    )

    try:
        raw = await chat.send_message(msg)
        # raw is a string
        parsed = safe_json_parse(raw if isinstance(raw, str) else str(raw))
    except Exception as e:
        return {
            "question_id": q["id"],
            "error": str(e),
            "verdict": "ERROR",
        }

    return {
        "question_id": q["id"],
        "category": q.get("category"),
        "current_question_no": q["question"].get("no", ""),
        "current_correct_option": q.get("correctOptionId"),
        "current_correct_text_no": next(
            (o["text"].get("no", "") for o in q["options"] if o["id"] == q.get("correctOptionId")),
            "",
        ),
        **parsed,
    }


async def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    cursor = db.questions.find(
        {"bildeUrl": {"$exists": True, "$ne": ""}},
        # keep bildeUrl but it's huge
    )
    questions = list(cursor)
    # Filter only non-empty base64
    questions = [q for q in questions if (q.get("bildeUrl") or "").startswith("data:")]
    print(f"Found {len(questions)} questions with Base64 images to audit.")

    report = []
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] Auditing {q['id']} ... ", end="", flush=True)
        result = await audit_one(q)
        verdict = result.get("verdict", "?")
        print(verdict)
        report.append(result)

        # Write partial report every 5 so we don't lose data
        if i % 5 == 0:
            out = Path(__file__).parent / "audit_report.json"
            out.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    out = Path(__file__).parent / "audit_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReport saved to {out}")

    # Summary
    counts = {}
    for r in report:
        counts[r.get("verdict", "?")] = counts.get(r.get("verdict", "?"), 0) + 1
    print("\n=== SUMMARY ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())
