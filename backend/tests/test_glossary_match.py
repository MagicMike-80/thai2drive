"""
Offline unit tests for the Fagordkort matching logic (glossary_match.py).

Pure functions only — no network, no MongoDB, no server import. Run from the
repo root or from backend/:

    python -m unittest tests.test_quiz_terms      # from backend/
    python -m unittest backend.tests.test_quiz_terms   # from repo root
"""

import unittest

try:
    from glossary_match import match_glossary_terms, terms_for_lang
except ImportError:  # running from repo root
    from backend.glossary_match import match_glossary_terms, terms_for_lang


def _term(term_no, **overrides):
    base = {
        "term_no": term_no,
        "term_th": "TH-" + term_no,
        "term_en": "EN-" + term_no,
        "definition_no": "NO definisjon for " + term_no,
        "definition_th": "TH definisjon for " + term_no,
        "definition_en": "EN definition for " + term_no,
        "example_th": "TH eksempel",
        "topic_tags": [],
        "active": True,
    }
    base.update(overrides)
    return base


GLOSSARY = [
    _term("Vikeplikt", topic_tags=["Vikeplikt", "Kryss"]),
    _term("Forkjørsvei", topic_tags=["Vikeplikt", "Skilt", "Kryss"]),
    _term("Rundkjøring", topic_tags=["Rundkjøring", "Kryss"]),
    _term("Fartsgrense", topic_tags=["Fart", "Skilt"]),
]


class MatchByText(unittest.TestCase):
    def test_question_mentioning_vikeplikt_returns_that_term(self):
        matched = match_glossary_terms(
            "Hva betyr vikeplikt i et uregulert kryss?", "", GLOSSARY
        )
        self.assertEqual([t["term_no"] for t in matched], ["Vikeplikt"])

    def test_match_is_case_insensitive_and_whole_word(self):
        # "vikepliktskilt" must NOT trigger the "Vikeplikt" term (different word).
        matched = match_glossary_terms("Et vikepliktskilt er trekantet.", "", GLOSSARY)
        self.assertEqual(matched, [])


class MatchByCategory(unittest.TestCase):
    def test_category_matches_topic_tag(self):
        matched = match_glossary_terms("Helt uten nøkkelord her.", "Rundkjøring", GLOSSARY)
        self.assertIn("Rundkjøring", [t["term_no"] for t in matched])

    def test_limit_is_respected(self):
        matched = match_glossary_terms("tekst", "Kryss", GLOSSARY, limit=2)
        self.assertEqual(len(matched), 2)


class NoMatch(unittest.TestCase):
    def test_no_keyword_and_no_category_returns_empty(self):
        matched = match_glossary_terms("En helt nøytral setning.", "Ukjent", GLOSSARY)
        self.assertEqual(matched, [])
        self.assertEqual({"terms": terms_for_lang(matched, "th")}, {"terms": []})


class LanguagePurity(unittest.TestCase):
    def test_missing_thai_definition_drops_the_term(self):
        glossary = [
            _term("Vikeplikt", definition_th="", topic_tags=["Vikeplikt"]),
        ]
        matched = match_glossary_terms("Forklar vikeplikt.", "", glossary)
        self.assertEqual([t["term_no"] for t in matched], ["Vikeplikt"])
        self.assertEqual(terms_for_lang(matched, "th"), [])  # fail-stop

    def test_thai_response_never_leaks_norwegian_or_english(self):
        matched = match_glossary_terms("Forklar vikeplikt.", "", GLOSSARY)
        rows = terms_for_lang(matched, "th")
        self.assertTrue(rows)
        for row in rows:
            for key in row:
                self.assertFalse(
                    key.endswith("_no") and key != "term_no",
                    "unexpected NO field: " + key,
                )
                self.assertFalse(key.endswith("_en"), "unexpected EN field: " + key)
            self.assertIn("term_th", row)
            self.assertIn("definition_th", row)


if __name__ == "__main__":
    unittest.main()
