"""
studiebok_screens.py — validering og seeding av læringsskjermer (v6) for Studieboken.

Hvert kapittel i `studiebok_chapters` får feltet `screens` (15–18 skjermer) og
`screen_count`. Eksisterende felt (content_*, title_*, image_url ...) røres aldri.

Språkregler for skjermene (kun thai + norsk, ingen engelsk):
  *_no  — ren norsk, ingen thai-tegn.
  *_th  — thai. Fagbegreper skrives «thai-forklaring (norsk fagord)»; latinske
          bokstaver er kun lov inne i parentes.

Bruk (dry-run er standard):
  python studiebok_screens.py              # validerer og viser hva som ville skjedd
  python studiebok_screens.py --commit     # skriver til databasen i MONGO_URL/DB_NAME
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

PACK_PATH = Path(__file__).parent / "content_packs" / "studiebok_screens_v6.json"

CONTENT_TYPES = {"theory", "rule", "trap", "summary"}
SCREEN_TYPES = CONTENT_TYPES | {"what_changed", "road_check"}
MIN_SCREENS, MAX_SCREENS = 15, 18
MIN_GAP, MAX_GAP = 3, 5  # skjermer mellom veisjekker

THAI_RE = re.compile(r"[฀-๿]")
LATIN_RE = re.compile(r"[A-Za-zÆØÅæøåÉéÈè]")
PAREN_RE = re.compile(r"\(([^()]*)\)")
# Heuristikk for engelsk i norsk/thai-felt (bevisst uten ord som også er norske: is, for, over, man ...)
ENGLISH_RE = re.compile(
    r"\b(the|and|you|your|with|that|this|from|have|will|road|check|driver|driving|speed|"
    r"limit|right|left|what|changed|when|should|must|before|after|always|never|because)\b",
    re.I,
)

BADGES = {
    "road_check": {"badge_no": "Veisjekk ⚡", "badge_th": "ตรวจถนน ⚡"},
    "what_changed": {"badge_no": "Hva er endret?", "badge_th": "อะไรเปลี่ยนไป?"},
}


def _strings(screen):
    """Yield (key, text) for every *_no / *_th string in a screen, incl. lists and hotspots."""
    for key, val in screen.items():
        if key == "hotspots" and isinstance(val, list):
            for i, hs in enumerate(val):
                if isinstance(hs, dict):
                    for k2, v2 in hs.items():
                        if k2.endswith(("_no", "_th")) and isinstance(v2, str):
                            yield f"hotspots[{i}].{k2}", v2
        elif key.endswith(("_no", "_th")):
            if isinstance(val, str):
                yield key, val
            elif isinstance(val, list):
                for i, item in enumerate(val):
                    if isinstance(item, str):
                        yield f"{key}[{i}]", item


def check_no(text):
    errs = []
    if THAI_RE.search(text):
        errs.append("thai-tegn i norsk felt")
    if ENGLISH_RE.search(text):
        errs.append("engelsk ord i norsk felt")
    return errs


def check_th(text):
    errs = []
    if len(THAI_RE.findall(text)) < 3:
        errs.append("for lite thai")
    if text.count("(") != text.count(")"):
        errs.append("ubalansert parentes")
        return errs
    outside = PAREN_RE.sub("", text)
    if "(" in outside or ")" in outside:
        errs.append("nøstet parentes")
    if LATIN_RE.search(outside):
        errs.append("latinske bokstaver utenfor parentes")
    for m in PAREN_RE.finditer(text):
        term = m.group(1).strip()
        if not term or not LATIN_RE.search(term):
            errs.append("tom parentes eller fagord uten norske bokstaver")
        if THAI_RE.search(term):
            errs.append("thai inne i norsk fagord-parentes")
        if ENGLISH_RE.search(term):
            errs.append(f"engelsk ord i fagord: {term!r}")
        before = text[: m.start()].rstrip()
        if not before or not THAI_RE.match(before[-1]):
            errs.append(f"fagord ({term}) står ikke rett etter thai-forklaring")
    return errs


def validate_chapter(ch):
    """Return a list of error strings (empty = valid)."""
    errors = []
    order = ch.get("order")
    tag = f"kap {order}"
    screens = ch.get("screens")
    if not isinstance(order, int):
        errors.append(f"{tag}: order må være heltall")
    if not isinstance(screens, list):
        return errors + [f"{tag}: screens må være liste"]
    if not MIN_SCREENS <= len(screens) <= MAX_SCREENS:
        errors.append(f"{tag}: {len(screens)} skjermer, forventer {MIN_SCREENS}–{MAX_SCREENS}")

    seen_ids = set()
    since_check = 0
    for idx, s in enumerate(screens):
        sid = s.get("id")
        stag = f"{tag} #{idx + 1} ({sid})"
        if sid in seen_ids:
            errors.append(f"{stag}: duplisert id")
        seen_ids.add(sid)
        if s.get("n") != idx + 1:
            errors.append(f"{stag}: n={s.get('n')} men posisjon {idx + 1}")
        stype = s.get("type")
        if stype not in SCREEN_TYPES:
            errors.append(f"{stag}: ukjent type {stype!r}")
            continue

        required = ["title_no", "title_th"]
        if stype in CONTENT_TYPES | {"what_changed"}:
            required += ["body_no", "body_th"]
        if stype == "road_check":
            required += ["question_no", "question_th", "explanation_no", "explanation_th"]
        for f in required:
            if not isinstance(s.get(f), str) or not s[f].strip():
                errors.append(f"{stag}: mangler {f}")

        if stype == "road_check":
            opts_no, opts_th = s.get("options_no"), s.get("options_th")
            if not (isinstance(opts_no, list) and isinstance(opts_th, list)
                    and len(opts_no) == len(opts_th) == 3
                    and all(isinstance(o, str) and o.strip() for o in opts_no + opts_th)):
                errors.append(f"{stag}: options_no/options_th må ha 3 tekster hver")
            ci = s.get("correct_index")
            if not isinstance(ci, int) or isinstance(ci, bool) or not 0 <= ci <= 2:
                errors.append(f"{stag}: correct_index må være 0–2")
            if not MIN_GAP <= since_check <= MAX_GAP:
                errors.append(f"{stag}: {since_check} skjermer siden forrige veisjekk, forventer {MIN_GAP}–{MAX_GAP}")
            since_check = 0
        else:
            since_check += 1
            if since_check > MAX_GAP:
                errors.append(f"{stag}: mer enn {MAX_GAP} skjermer uten veisjekk")

        if stype == "what_changed":
            if not isinstance(s.get("image_brief_no"), str) or not s["image_brief_no"].strip():
                errors.append(f"{stag}: mangler image_brief_no")
            for k in ("image_before", "image_after"):
                if k not in s:
                    errors.append(f"{stag}: mangler {k}")
            hs = s.get("hotspots")
            if not (isinstance(hs, list) and 2 <= len(hs) <= 4):
                errors.append(f"{stag}: hotspots må ha 2–4 punkter")
            else:
                for i, h in enumerate(hs):
                    ok = (isinstance(h, dict)
                          and all(isinstance(h.get(a), int) and 0 <= h[a] <= 100 for a in ("x", "y"))
                          and isinstance(h.get("label_no"), str) and h["label_no"].strip()
                          and isinstance(h.get("label_th"), str) and h["label_th"].strip())
                    if not ok:
                        errors.append(f"{stag}: hotspot {i} ugyldig (x,y 0–100 + label_no/label_th)")

        for key, text in _strings(s):
            if key.startswith("badge_"):
                continue
            if re.search(r"_no(\[\d+\])?$", key):
                errs = check_no(text)
            else:
                errs = check_th(text)
            for e in errs:
                errors.append(f"{stag}.{key}: {e}")

    if not any(s.get("type") == "what_changed" for s in screens):
        errors.append(f"{tag}: minst én what_changed-skjerm kreves")
    if not any(s.get("type") == "road_check" for s in screens):
        errors.append(f"{tag}: minst én road_check-skjerm kreves")
    return errors


def load_pack(path=PACK_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_pack(pack):
    errors = []
    orders = [c.get("order") for c in pack.get("chapters", [])]
    if len(orders) != len(set(orders)):
        errors.append("duplisert kapittel-order i pakken")
    for ch in pack.get("chapters", []):
        errors.extend(validate_chapter(ch))
    return errors


def total_screens(pack):
    return sum(len(c["screens"]) for c in pack["chapters"])


def apply_pack(db, pack, commit=False):
    """
    Sett `screens` + `screen_count` på eksisterende kapitler i db.studiebok_chapters (match på order).
    Alt-eller-ingenting: ved valideringsfeil skrives ingenting. Uten commit skrives heller ingenting.
    Returnerer dict med errors/updated/missing.
    """
    errors = validate_pack(pack)
    report = {"errors": errors, "updated": [], "missing": []}
    if errors:
        return report
    coll = db.studiebok_chapters
    for ch in pack["chapters"]:
        if coll.find_one({"order": ch["order"]}) is None:
            report["missing"].append(ch["order"])
            continue
        if commit:
            coll.update_one(
                {"order": ch["order"]},
                {"$set": {"screens": ch["screens"], "screen_count": len(ch["screens"])}},
            )
        report["updated"].append(ch["order"])
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commit", action="store_true", help="skriv til databasen (standard er dry-run)")
    ap.add_argument("--pack", default=str(PACK_PATH))
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    pack = load_pack(args.pack)
    errors = validate_pack(pack)
    print(f"Kapitler: {len(pack['chapters'])}, skjermer totalt: {total_screens(pack)}")
    if errors:
        print(f"{len(errors)} valideringsfeil — ingenting skrevet:")
        for e in errors:
            print("  ✗", e)
        return 1
    if not args.commit:
        print("Validering OK (dry-run, ingen databaseoppkobling).")
        return 0

    from dotenv import load_dotenv
    from pymongo import MongoClient
    load_dotenv(Path(__file__).parent / ".env")
    db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    report = apply_pack(db, pack, commit=True)
    print(f"Oppdatert: {report['updated']}  Mangler i DB: {report['missing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
