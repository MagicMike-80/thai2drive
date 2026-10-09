"""Bygger elevvisning (HTML) og rapporttabell for Bilde-bok-piloten fra JSON-pakken.

Bruk:  cd backend && python scripts/build_bildebok_preview.py
Ut:    ../output/bildebok/elevvisning.html  og  ../docs/bildebok/RAPPORT_25_SIDER.md
Bilder hentes fra ../output/bildebok/images/<image_file> hvis de finnes, ellers vises en plassholder.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

NL = chr(10)

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "backend" / "content_packs" / "bildebok" / "pilot_s11_s35.json"
OUT_HTML = ROOT / "output" / "bildebok" / "elevvisning.html"
IMG_DIR = ROOT / "output" / "bildebok" / "images"
OUT_MD = ROOT / "docs" / "bildebok" / "RAPPORT_25_SIDER.md"
OUT_MAP = ROOT / "docs" / "bildebok" / "SIDEKART.md"
OUT_APPROVAL = ROOT / "docs" / "bildebok" / "GODKJENNING.md"
OUT_BRIEFS = ROOT / "docs" / "bildebok" / "BILDEBRIEFER_TIL_CHATGPT.md"
OUT_CONTENT = ROOT / "docs" / "bildebok" / "INNHOLD_ALLE_RADER.md"

UI = {
    "no": {"book": "Lærebok Klasse B", "page": "side", "check": "Sjekk deg selv", "michael": "Michael sier", "ok": "Riktig!", "no": "Prøv igjen", "soon": "Bilde kommer", "title": "Michaels bildebok", "lang": "Språk"},
    "th": {"book": "หนังสือเรียนชั้น B", "page": "หน้า", "check": "ทดสอบตัวเอง", "michael": "ไมเคิลพูดว่า", "ok": "ถูกต้อง!", "no": "ลองอีกครั้ง", "soon": "ภาพกำลังจะมา", "title": "หนังสือภาพของไมเคิล", "lang": "ภาษา"},
    "en": {"book": "Class B textbook", "page": "page", "check": "Check yourself", "michael": "Michael says", "ok": "Correct!", "no": "Try again", "soon": "Image coming", "title": "Michael's picture book", "lang": "Language"},
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def card(row: dict, lang: str) -> str:
    ui = UI[lang]
    img = IMG_DIR / row["image_file"]
    if img.exists():
        media = f'<img src="images/{esc(row["image_file"])}" alt="{esc(row["title"][lang])}" style="object-position:{row["image_focus"]["x"]}% {row["image_focus"]["y"]}%">'
    else:
        media = f'<div class="ph"><span>{esc(ui["soon"])}</span></div>'
    labels = "".join(f'<span class="pill">{esc(l[lang])}</span>' for l in row["image_labels"])
    points = "".join(f"<li>{esc(p[lang])}</li>" for p in row["points"])
    opts = "".join(
        f'<button class="opt" data-ok="{1 if i == row["check_question"]["answer"] else 0}">{esc(o[lang])}</button>'
        for i, o in enumerate(row["check_question"]["options"])
    )
    brief = ''
    return f"""
<article class="card" data-id="{esc(row['id'])}">
  <div class="media">{media}<div class="pills">{labels}</div></div>
  <div class="body">
    <h2>{esc(row['title'][lang])}</h2>
    <p class="core">{esc(row['core_sentence'][lang])}</p>
    <ul>{points}</ul>
    <p class="src">📖 {esc(ui['book'])} · {esc(ui['page'])} {row['printed_page']}</p>
    <details class="more"><summary>🧑‍🏫 {esc(ui['michael'])} · {esc(ui['check'])}</summary>
    <p class="michael"><b>{esc(ui['michael'])}:</b> {esc(row['michael_says'][lang])}</p>
    <div class="quiz"><p class="q">{esc(row['check_question']['q'][lang])}</p>{opts}<p class="fb" data-ok="{esc(ui['ok'])}" data-no="{esc(ui['no'])}"></p></div>
    {brief}</details>
  </div>
</article>"""


def build_html(pack: dict) -> str:
    json_titles = json.dumps({l: UI[l]['title'] for l in UI}, ensure_ascii=False)
    sections = {
        lang: "\n".join(card(r, lang) for r in pack["pages"]) for lang in ("no", "th", "en")
    }
    views = "\n".join(f'<section class="view" id="v-{l}" hidden>{sections[l]}</section>' for l in sections)
    return f"""<!doctype html>
<html lang="no"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Michaels bildebok</title>
<style>
:root{{--bg:#0f1720;--card:#16212d;--ink:#eef3f8;--mut:#9fb0c1;--acc:#4cc2ff;--ok:#3ecf8e;--bad:#ff7a7a}}
@media (prefers-color-scheme:light){{:root{{--bg:#f3f6fa;--card:#fff;--ink:#14202b;--mut:#51636f;--acc:#0a6fb5;--ok:#157a50;--bad:#b3261e}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif}}
header{{position:sticky;top:0;background:var(--bg);padding:12px 16px;display:flex;gap:8px;align-items:center;z-index:2;border-bottom:1px solid #8883}}
header b{{flex:1}}header button{{border:1px solid var(--acc);background:none;color:var(--ink);padding:6px 12px;border-radius:8px;cursor:pointer}}
header button.on{{background:var(--acc);color:#fff}}
main{{max-width:680px;margin:0 auto;padding:16px}}
.card{{background:var(--card);border-radius:16px;overflow:hidden;margin:0 0 20px;box-shadow:0 2px 10px #0003}}
.media{{position:relative;aspect-ratio:4/5;background:#223}}@media(min-width:520px){{.media{{aspect-ratio:4/3}}}}
.media img{{width:100%;height:100%;object-fit:cover;display:block}}
.ph{{position:absolute;inset:0;display:grid;place-items:center;background:repeating-linear-gradient(45deg,#2a3a4a,#2a3a4a 14px,#25333f 14px,#25333f 28px);color:#cfe}}
.pills{{position:absolute;left:10px;bottom:10px;display:flex;gap:6px;flex-wrap:wrap}}
.pill{{background:#000b;color:#fff;border-radius:999px;padding:3px 10px;font-size:13px}}
.body{{padding:10px 14px 12px;font-size:15px}}h2{{margin:0 0 2px;font-size:18px}}.core{{font-weight:600;margin:0 0 6px}}.more summary{{cursor:pointer;color:var(--acc);margin-top:6px}}
ul{{margin:0 0 6px;padding-left:18px}}li{{margin:1px 0}}
.michael{{background:#4cc2ff22;border-left:4px solid var(--acc);padding:8px 10px;border-radius:6px;margin:10px 0}}
.q{{margin:8px 0 6px;font-weight:600}}.opt{{display:block;width:100%;text-align:left;margin:4px 0;padding:10px;border-radius:10px;border:1px solid #8886;background:none;color:var(--ink);font:inherit;cursor:pointer}}
.opt.good{{border-color:var(--ok);background:#3ecf8e22}}.opt.bad{{border-color:var(--bad);background:#ff7a7a22}}
.fb{{min-height:1.2em;margin:4px 0;font-weight:600}}.src{{color:var(--mut);font-size:13px;margin:8px 0 0}}
.brief{{color:var(--mut);font-size:12px;margin-top:6px}}
</style></head><body>
<header><b id="ttl">Michaels bildebok</b><button data-l="no" class="on" aria-label="Norsk">NO</button><button data-l="th" aria-label="ภาษาไทย">ไทย</button><button data-l="en" aria-label="English">EN</button></header>
<main>{views}</main>
<script>
const TT={json_titles};
const show=l=>{{document.getElementById('ttl').textContent=TT[l];document.title=TT[l];document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!=='v-'+l);
document.querySelectorAll('header button').forEach(b=>b.classList.toggle('on',b.dataset.l===l));document.documentElement.lang=l==='th'?'th':l;}};
document.querySelectorAll('header button').forEach(b=>b.onclick=()=>show(b.dataset.l));
document.addEventListener('click',e=>{{const o=e.target.closest('.opt');if(!o)return;
const q=o.closest('.quiz'),fb=q.querySelector('.fb'),ok=o.dataset.ok==='1';
o.classList.add(ok?'good':'bad');fb.textContent=ok?fb.dataset.ok:fb.dataset.no;fb.style.color=ok?'var(--ok)':'var(--bad)';}});
show('no');
</script></body></html>"""


def build_md(pack: dict) -> str:
    rows = [
        "| # | Boknavn | Trykt side | PDF-side | Kapittel | Avsnitt | Bildefil | Bildestatus | Status |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(pack["pages"], 1):
        rows.append(
            f"| {i} | {r['book']} | {r['printed_page']} | {r['pdf_page']} | {r['chapter']} | {r['section']} | "
            f"`{r['image_file']}` | {r['image_status']} | {r['status']} |"
        )
    words = [
        len(r["core_sentence"]["no"].split()) + sum(len(p["no"].split()) for p in r["points"]) for r in pack["pages"]
    ]
    rows.append("")
    rows.append(f"Rader: {len(pack['pages'])} · originalsider: {len({r['printed_page'] for r in pack['pages']})} · "
                f"snitt kjernetekst+punkter: {sum(words) / len(words):.0f} ord per rad (norsk).")
    return "\n".join(rows) + "\n"


APPROVAL_FIELDS = ("id", "asset_id", "title", "core_sentence", "points", "michael_says", "check_question",
                   "image_labels", "michael_basis", "image_brief")


def row_hash(row: dict) -> str:
    import hashlib
    payload = json.dumps({k: row[k] for k in APPROVAL_FIELDS}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def build_approval(pack: dict) -> str:
    out = ["# Godkjenningsstatus per rad", "",
           "Hash dekker elevtekst, spørsmål, bildeetiketter, bildebrief og Michael-grunnlag. Endres en rad, endres hashen,",
           "og bare den raden trenger ny godkjenning. Uendrede rader beholder godkjenningen.", "",
           "| Rad | Hash | Godkjent av | Dato | Merknad |", "|---|---|---|---|---|"]
    for r in pack["pages"]:
        out.append(f"| {r['id']} | `{row_hash(r)}` | _venter_ | | {len(r['open_questions'])} åpne spørsmål |")
    return NL.join(out) + NL


def build_map(pack: dict) -> str:
    out = ["# Sidekart – Bilde-bok pilot (trykt s. 11–35)", "",
           "| Innholds-ID | Kapittel | Avsnitt | Bildefil | Kilde | Neste steg | Åpne spørsmål |",
           "|---|---|---|---|---|---|---|"]
    for r in pack["pages"]:
        out.append(f"| {r['id']} | {r['chapter']} | {r['section']} | `{r['image_file']}` | {r['source_ref']} | "
                   f"{r['next_step'] or '— (slutt på pilot)'} | {len(r['open_questions'])} |")
    return NL.join(out) + NL


def build_briefs(pack: dict) -> str:
    out = ["# Bildebriefer samlet til ChatGPT (29 bilder)", "",
           "Lim inn ett bilde av gangen. Be om fotorealistisk bilde i 3:2 liggende format uten tekst (unntatt skiltsifre i bb-s21).",
           "Lagre hvert bilde som oppgitt filnavn og legg det i `backend/public_assets/bildebok/`.",
           "Kontroller hvert bilde: høyrekjøring, norske forhold, ingen tekst, riktige aktører, og at alle sentrale elementer",
           "ligger i midten (tåler beskjæring til 4:5 og 4:3).", ""]
    for r in pack["pages"]:
        out += [f"## {r['image_file']}", f"Rad {r['id']} – {r['title']['en']} (trykt s. {r['printed_page']})", "", "```", r["image_brief"], "```", ""]
    return NL.join(out) + NL


def build_content(pack: dict) -> str:
    out = ["# Innhold for alle 29 rader (til faglig godkjenning)", "",
           "Åpne spørsmål som gjelder alle rader:", ""]
    out += [f"- {q}" for q in pack["global_open_questions"]]
    for r in pack["pages"]:
        out += ["", f"## {r['id']} – {r['title']['no']}", f"Kilde: {r['source_ref']} · {r['chapter']} · {r['section']}",
                f"Bilde: `{r['image_file']}` ({r['image_status']})", ""]
        for lang, name in (("no", "Norsk"), ("th", "ไทย"), ("en", "English")):
            out.append(f"**{name}** – {r['title'][lang]}")
            out.append(f"> {r['core_sentence'][lang]}")
            out += [f"- {p[lang]}" for p in r["points"]]
            out.append(f"- Michael: {r['michael_says'][lang]}")
            cq = r["check_question"]
            out.append(f"- Spørsmål: {cq['q'][lang]} → {cq['options'][cq['answer']][lang]}")
            out.append(f"- Michael-grunnlag: {r['michael_basis'][lang]}")
            out.append("")
        out.append(f"**Bildebrief (engelsk, til Codex/ChatGPT):** {r['image_brief']}")
        out.append("")
        if r["open_questions"]:
            out.append("**Uavklart (faglig):**")
            out += [f"- {q}" for q in r["open_questions"]]
        else:
            out.append("**Uavklart (faglig):** ingen utover de generelle.")
    return NL.join(out) + NL


def main() -> None:
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(pack), encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(build_md(pack), encoding="utf-8")
    OUT_MAP.write_text(build_map(pack), encoding="utf-8")
    OUT_CONTENT.write_text(build_content(pack), encoding="utf-8")
    OUT_BRIEFS.write_text(build_briefs(pack), encoding="utf-8")
    if not OUT_APPROVAL.exists():
        OUT_APPROVAL.write_text(build_approval(pack), encoding="utf-8")
    print(f"wrote {OUT_HTML}, {OUT_MD}, {OUT_MAP}, {OUT_CONTENT}")


if __name__ == "__main__":
    main()
