"""Sender én melding til Michael (POST /api/teacher/chat) som en navngitt test-elev.

Bruk:  python tools/michael_probe/chat.py <persona> <no|th|en> "<melding>" [--new-session]

- Stabil device_id per persona ("qa-persona-<persona>") slik at Michael ser samme elev over tid.
- Lagrer session_id i state/<persona>.json (gjenbrukes til neste kall = samme samtale).
- Logger hver tur til docs/michael-testelever/transcripts/<persona>-<dato>.jsonl.
- Rører kun /teacher/chat. Ingen konto, ingen quiz-/stats-/Stripe-endepunkter.
- Logger og skriver ut `media` (bilde/lyd/video) fra svaret og sjekker med HEAD at hver media-URL
  på thai2drive.no faktisk finnes (status + content-type). Leser bare URL-er Michael selv returnerte.
"""
import json
import sys
import datetime
import pathlib
import re
import urllib.request

BASE = "https://www.thai2drive.no/api"
ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = pathlib.Path(__file__).parent / "state"
LOGS = ROOT / "docs" / "michael-testelever" / "transcripts"


MAX_MESSAGES = 30

def _reserve_message(persona, day=None):
    """30 attempted messages per persona/day across NO/TH/EN and new sessions.

    Exclusive slot creation prevents concurrent sends exceeding the cap. Failed
    sends consume a slot too. Existing transcript messages count before first use.
    """
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", persona):
        raise ValueError("Invalid probe persona")
    family = re.sub(r"-(?:no|th|en)$", "", persona)
    day = day or datetime.date.today().isoformat()
    used = 0
    for path in LOGS.glob(f"{family}*-{day}.jsonl"):
        name = path.name[:-len(f"-{day}.jsonl")]
        if re.sub(r"-(?:no|th|en)$", "", name) != family:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)  # Corrupt evidence must stop, never reset quota.
                used += 1
    budget = STATE / "message-budget" / day / family
    budget.mkdir(parents=True, exist_ok=True)
    for number in range(used + 1, MAX_MESSAGES + 1):
        try:
            with (budget / f"{number:02d}.reserved").open("x", encoding="utf-8") as handle:
                handle.write(persona)
            return number
        except FileExistsError:
            continue
    raise RuntimeError("30-message probe limit reached; no request sent")


def _check_url(url):
    """HEAD a media URL on thai2drive.no (relative or same host only). Returns 'status content-type'."""
    if url.startswith("/"):
        full = "https://www.thai2drive.no" + url
    elif url.startswith(("https://www.thai2drive.no/", "https://thai2drive.no/")):
        full = url
    else:
        return "SKIPPED (external host)"
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            req = urllib.request.Request(full, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                size = (r.headers.get("Content-Range") or "").rsplit("/", 1)[-1] or r.headers.get("Content-Length", "?")
                return f"{r.status} {r.headers.get('Content-Type', '?')} size={size}"
        except Exception as e:
            last = f"FAILED {type(e).__name__}: {e}"
    return last


def check_length(text, persona):
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    fam = re.sub(r"-(?:no|th|en)$", "", persona).lower()
    if fam == 'kai' and len(sentences) > 4:
        return False, f"For lang for Kai ({len(sentences)} setninger > 4)"
    if fam == 'ploy' and len(sentences) > 6:
        return False, f"For lang for Ploy ({len(sentences)} setninger > 6)"
    return True, f"OK ({len(sentences)} setninger)"


def main():
    args = [a for a in sys.argv[1:] if a != "--new-session"]
    new = "--new-session" in sys.argv
    if len(args) != 3 or args[1] not in {"no", "th", "en"}:
        raise ValueError("Expected persona, no|th|en and message")
    persona, lang, msg = args
    _reserve_message(persona)  # Before any HTTP, including failures/new sessions.
    STATE.mkdir(exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    sf = STATE / f"{persona}.json"
    st = {} if new or not sf.exists() else json.loads(sf.read_text(encoding="utf-8"))
    body = {"message": msg, "language": lang, "device_id": f"qa-persona-{persona}",
            "mode": "normal_chat"}
    if st.get("session_id"):
        body["session_id"] = st["session_id"]
    req = urllib.request.Request(BASE + "/teacher/chat", json.dumps(body).encode("utf-8"),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        res = json.loads(r.read().decode("utf-8"))
    sf.write_text(json.dumps({"session_id": res["session_id"]}), encoding="utf-8")
    now = datetime.datetime.now()
    entry = {"ts": now.isoformat(timespec="seconds"), "persona": persona, "lang": lang,
             "session_id": res["session_id"], "student": msg, "michael": res["reply"],
             "suggestions": res.get("suggestions"), "sign_ids": res.get("sign_ids"),
             "media": res.get("media")}
    with open(LOGS / f"{persona}-{now:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print(res["reply"])
    ok, len_msg = check_length(res["reply"], persona)
    print(f"\n[LENGDE-VOKTER] {'✅' if ok else '⚠️'} {len_msg}")
    media = res.get("media") or []
    print(f"\n[MEDIA] count={len(media)} sign_ids={res.get('sign_ids')}")
    for m in media:
        url = str(m.get("url") or m.get("media_url") or "")
        print("[MEDIA] " + json.dumps({k: m.get(k) for k in ("id", "type", "title", "caption", "audio_language", "media_id")},
                                      ensure_ascii=False) + f" url={url} -> {_check_url(url) if url else 'NO URL'}")


if __name__ == "__main__":
    main()
