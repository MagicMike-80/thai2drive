"""
glossary_match.py — pure matching logic for the "Se norsk fagord" (Fagordkort) feature.

No database, no network, no import-time environment reads. Everything here is a
plain function over in-memory data so it can be unit-tested offline
(see backend/tests/test_quiz_terms.py) the same way media_catalog.py is.

A "term" is a learning_glossary document:
    {
      "term_no": "Vikeplikt", "term_th": "การให้ทาง", "term_en": "...",
      "definition_no": "...", "definition_th": "...", "definition_en": "...",
      "example_no": "...",    "example_th": "...",    "example_en": "...",
      "topic_tags": ["Vikeplikt", "Kryss"],
      "active": True,
    }
"""

import re

SUPPORTED_LANGS = ("th", "no", "en")
DEFAULT_LIMIT = 4


def _norm(s) -> str:
    return (s or "").strip().lower()


def _term_in_text(term_no: str, text_no: str) -> bool:
    """Whole-word, case-insensitive hit of ``term_no`` inside ``text_no``.

    Word boundaries keep this an *exact* match: the term "Vikeplikt" hits
    "Hva betyr vikeplikt?" but not the compound "vikepliktskilt" (which is its
    own separate term).
    """
    term_no = (term_no or "").strip()
    if not term_no or not text_no:
        return False
    return re.search(r"\b" + re.escape(term_no) + r"\b", text_no, re.IGNORECASE) is not None


def match_glossary_terms(question_text_no, category, terms, limit=DEFAULT_LIMIT):
    """Return the glossary terms that apply to a question.

    A term matches when either:
      * its ``term_no`` appears as a whole word in ``question_text_no``, or
      * ``category`` exactly equals (case-insensitive) one of its ``topic_tags``.

    Text hits rank ahead of tag-only hits; ties break alphabetically on
    ``term_no``. Inactive terms are ignored. At most ``limit`` terms are returned.
    """
    text_no = question_text_no or ""
    cat = _norm(category)
    ranked = []
    for term in terms or []:
        if term.get("active") is False:
            continue
        term_no = term.get("term_no", "")
        text_hit = _term_in_text(term_no, text_no)
        tag_hit = bool(cat) and cat in {_norm(t) for t in term.get("topic_tags", [])}
        if not (text_hit or tag_hit):
            continue
        ranked.append((0 if text_hit else 1, _norm(term_no), term))

    ranked.sort(key=lambda r: (r[0], r[1]))
    return [term for _, _, term in ranked[: max(0, limit)]]


def terms_for_lang(matched, lang):
    """Project matched terms to a single language for the response.

    Fail-stop: a term missing a non-empty ``term_<lang>`` or ``definition_<lang>``
    is dropped entirely — never backfilled with Norwegian or English. ``term_no``
    is always included because it is the term the learner is being taught (the
    "[Term Thai] -> [Term Norsk]" card), but no other-language *definition* is
    ever returned.
    """
    if lang not in SUPPORTED_LANGS:
        return []
    out = []
    for term in matched or []:
        term_loc = (term.get(f"term_{lang}") or "").strip()
        def_loc = (term.get(f"definition_{lang}") or "").strip()
        if not term_loc or not def_loc:
            continue  # fail-stop
        row = {
            "term_no": (term.get("term_no") or "").strip(),
            f"term_{lang}": term_loc,
            f"definition_{lang}": def_loc,
        }
        ex_loc = (term.get(f"example_{lang}") or "").strip()
        if ex_loc:
            row[f"example_{lang}"] = ex_loc
        out.append(row)
    return out
