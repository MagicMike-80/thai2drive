# -*- coding: utf-8 -*-
"""
A/B-test av Michaels Master Prompt via OpenRouter.

Kjører samme system-prompt (_build_system_prompt fra teacher_chat.py) mot flere
modeller og sjekker:
  1. Language Purity — thai-modus skal være 100 % thai (ingen norsk/engelsk)
  2. Pedagogikk — bruker modellen "Kongen og tjeneren" og HAV-regelen riktig?
     (vurderes manuelt fra rapporten)
  3. Kostnad — tokens + USD per svar fra OpenRouter

Bruk:
  set OPENROUTER_API_KEY=sk-or-...     (PowerShell: $env:OPENROUTER_API_KEY="sk-or-...")
  cd backend
  python scripts/ab_test_openrouter.py

Output: scripts/ab_test_report.md
Kun lokal evaluering — rører ALDRI produksjon, database eller /api/teacher/chat.
"""
import json
import os
import re
import sys
import time

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("MONGO_URL", "mongodb://localhost")  # teacher_chat importerer motor; ingen tilkobling skjer
from teacher_chat import _build_system_prompt  # noqa: E402

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

# Kandidater (ANTI sine forslag + dagens raskeste/billigste tilsvarende).
# Modell-ID-er som ikke finnes lenger gir bare en feilrad i rapporten.
MODELS = [
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-haiku-4.5",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "google/gemini-2.5-flash",
]

# Testspørsmål slik thai-elever faktisk stiller dem (thai-modus = strengest krav)
QUESTIONS_TH = [
    ("kongen-tjeneren", "ใครต้องให้ทางตรงทางแยกที่ไม่มีป้าย ฉันสับสนเรื่อง vikeplikt มาก ช่วยอธิบายหน่อย"),
    ("hav-regelen", "มาตรา 3 ของกฎหมายจราจรนอร์เวย์คืออะไร ทำไมถึงสำคัญ"),
    ("scenario", "ฉันกำลังขับเข้าวงเวียน มีรถมาจากทางซ้ายในวงเวียน ฉันต้องหยุดไหม"),
]

THAI_RE = re.compile(r"[฀-๿]")
LATIN_WORD_RE = re.compile(r"[A-Za-zÆØÅæøå]{2,}")
# Tillatt latin i thai-svar: media-tagger, URL-er og norske fagord i parentes er
# IKKE tillatt iht. 100 % purity — men tagger som [video: /path | ...] er app-syntaks.
TAG_RE = re.compile(r"\[(?:video|podcast|audio|image|img)\s*:[^\]]*\]", re.IGNORECASE)


def purity_check(text: str) -> dict:
    """Andel thai-tegn og liste over latinske ord utenfor media-tagger."""
    stripped = TAG_RE.sub("", text)
    thai = len(THAI_RE.findall(stripped))
    latin_words = LATIN_WORD_RE.findall(stripped)
    letters = thai + sum(len(w) for w in latin_words)
    return {
        "thai_ratio": round(thai / letters, 4) if letters else 0.0,
        "latin_words": sorted(set(latin_words))[:25],
        "pure": not latin_words,
    }


def call_model(model: str, system_prompt: str, user_msg: str) -> dict:
    r = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://thai2drive.no",
            "X-Title": "Thai2Drive AB-test",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            "max_tokens": 1200,
            "usage": {"include": True},
        },
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    usage = data.get("usage", {})
    return {
        "text": data["choices"][0]["message"]["content"],
        "tokens_in": usage.get("prompt_tokens"),
        "tokens_out": usage.get("completion_tokens"),
        "cost_usd": usage.get("cost"),
    }


def main():
    if not API_KEY:
        sys.exit("Sett OPENROUTER_API_KEY først.")
    system_prompt = _build_system_prompt("th")
    rows = []
    for model in MODELS:
        for qid, q in QUESTIONS_TH:
            print(f"→ {model} / {qid} ...", flush=True)
            try:
                res = call_model(model, system_prompt, q)
                res.update(purity_check(res["text"]))
                res.update(model=model, qid=qid, error=None)
            except Exception as e:  # 404 ukjent modell, timeout osv.
                res = {"model": model, "qid": qid, "error": str(e)[:300]}
            rows.append(res)
            time.sleep(1)

    out = os.path.join(os.path.dirname(__file__), "ab_test_report.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# A/B-test: Master Prompt via OpenRouter (thai-modus)\n\n")
        f.write("| Modell | Spørsmål | 100% thai | Thai-andel | Latinske ord | Tokens ut | Kost USD |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            if r.get("error"):
                f.write(f"| {r['model']} | {r['qid']} | FEIL | — | {r['error']} | — | — |\n")
            else:
                f.write(
                    f"| {r['model']} | {r['qid']} | {'JA' if r['pure'] else 'NEI'} | "
                    f"{r['thai_ratio']:.0%} | {', '.join(r['latin_words']) or '—'} | "
                    f"{r['tokens_out']} | {r['cost_usd']} |\n"
                )
        f.write("\n---\n\n## Fullstendige svar (for manuell pedagogikk-vurdering)\n")
        for r in rows:
            f.write(f"\n### {r['model']} — {r['qid']}\n\n")
            f.write((r.get("text") or f"FEIL: {r['error']}") + "\n")
    with open(out.replace(".md", ".json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\nFerdig — rapport: {out}")


if __name__ == "__main__":
    main()
