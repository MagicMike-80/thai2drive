"""
quiz_language.py — språkisolasjon for quiz-spørsmål.

Regelen (samme som Studiebok og webappens pickStrict):
  * Thai-modus viser KUN thai. Norsk fagord er tillatt bare i parentes: «ให้ทาง (vikeplikt)».
    Norske/engelske ord utenfor parentes, eller et felt uten thai i det hele tatt, er brudd.
  * Norsk og engelsk modus skal aldri inneholde thai-tegn.
  * Forkortelser og enheter (EU, ABS, km/t, 50 km/t ...) er språknøytrale og godtas.

Ren funksjonsmodul: ingen database, ingen nettverk. Brukes av GET /api/questions/random?lang=…
og av testene (tests/test_quiz_and_signs.py) som revisjon av hele spørsmålsbanken.
"""

import re
from typing import Iterable, List, Optional

THAI = re.compile(r"[฀-๿]")
PARENS = re.compile(r"\([^()]*\)")
WORD = re.compile(r"[A-Za-zÆØÅæøå][A-Za-zÆØÅæøå/]*")
NEUTRAL = re.compile(
    r"^(?:[A-Z]{1,5}\d*|km|h|m|cm|mm|kg|t|km/t|km/h|m/s|mph|[A-Za-zÆØÅæøå]{1,2})$"
)

LANGS = ("th", "no", "en")


def _localized_fields(q: dict, lang: str) -> Iterable[tuple]:
    """(label, text) for spørsmål, forklaring og hvert svaralternativ, i valgt språk."""
    yield "question", (q.get("question") or {}).get(lang)
    yield "explanation", (q.get("explanation") or {}).get(lang)
    for opt in q.get("options") or []:
        yield f"option {opt.get('id')}", (opt.get("text") or {}).get(lang)


def field_violation(text: Optional[str], lang: str) -> Optional[str]:
    """Kort årsak hvis feltet bryter isolasjonen i `lang`, ellers None. Tomme felt vurderes ikke."""
    if text is None or not str(text).strip():
        return None
    text = str(text)
    if lang == "th":
        outside = PARENS.sub("", text)
        foreign = [w for w in WORD.findall(outside) if not NEUTRAL.match(w)]
        if foreign:
            return "latin_outside_parentheses: " + ", ".join(foreign[:3])
        return None
    if THAI.search(text):
        return "thai_in_" + lang
    return None


def question_violations(q: dict, lang: str = "th") -> List[str]:
    """Alle brudd for spørsmålet (v2-format, se server.normalize_question) i `lang`."""
    out = []
    for label, text in _localized_fields(q, lang):
        why = field_violation(text, lang)
        if why:
            out.append(f"{label}: {why}")
    return out


def is_language_isolated(q: dict, lang: str = "th") -> bool:
    return not question_violations(q, lang)


def filter_isolated(questions: List[dict], lang: Optional[str]) -> List[dict]:
    """Behold bare spørsmål som er 100 % isolert i `lang`. Ukjent/tomt språk = ingen filtrering."""
    if lang not in LANGS:
        return questions
    return [q for q in questions if is_language_isolated(q, lang)]
