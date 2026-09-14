"""Offline unit tests for the Fagordkortet glossary lookup (quiz_terms.py).

Isolated import (stubs motor/fastapi/pydantic/dotenv) following the pattern
in test_teacher_chat_fallback.py::_load_teacher_chat. Zero network, zero prod:
_match_terms / _build_terms_response are called directly on fake in-memory
glossary caches and fake question dicts — never through HTTP, never through
a real Mongo connection.
"""
import importlib.util
import os
import re
import sys
import types
import unittest
from pathlib import Path


class _Router:
    def get(self, *args, **kwargs):
        return lambda func: func


def _load_module(filename, module_name):
    fastapi = types.ModuleType("fastapi")
    fastapi.APIRouter = lambda *args, **kwargs: _Router()
    fastapi.Query = lambda default=None, **kwargs: default

    pydantic = types.ModuleType("pydantic")
    pydantic.BaseModel = object
    pydantic.Field = lambda default=None, **kwargs: default

    class _Mongo:
        def __getitem__(self, key):
            return self

        def __getattr__(self, name):
            return self

    motor = types.ModuleType("motor")
    motor_asyncio = types.ModuleType("motor.motor_asyncio")
    motor_asyncio.AsyncIOMotorClient = lambda *args, **kwargs: _Mongo()
    motor.motor_asyncio = motor_asyncio

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda: None

    stubs = {
        "fastapi": fastapi,
        "pydantic": pydantic,
        "motor": motor,
        "motor.motor_asyncio": motor_asyncio,
        "dotenv": dotenv,
    }
    previous = {name: sys.modules.get(name) for name in stubs}
    old_env = {name: os.environ.get(name) for name in ("MONGO_URL", "DB_NAME")}
    try:
        sys.modules.update(stubs)
        os.environ["MONGO_URL"] = "mongodb://test"
        os.environ["DB_NAME"] = "thai2drive_test"

        path = Path(__file__).resolve().parents[1] / filename
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _load_quiz_terms():
    return _load_module("quiz_terms.py", "quiz_terms_test_module")


def _load_seed_glossary():
    return _load_module("scripts/seed_glossary.py", "seed_glossary_test_module")


def _fake_cache():
    return [
        {
            "id": "1",
            "term_no": "Vikeplikt",
            "term_th": "การให้ทาง",
            "definition_no": "Plikten til å la andre trafikanter passere før deg.",
            "definition_th": "หน้าที่ที่ต้องยอมให้ผู้ใช้ถนนคนอื่นผ่านก่อนคุณ",
            "definition_en": "The obligation to let other road users pass before you.",
            "topic_tags": ["Vikeplikt", "Kryss"],
        },
        {
            "id": "2",
            "term_no": "Rundkjøring",
            "term_th": "วงเวียน",
            "definition_no": "Vegkryss der trafikken kjører i sirkel.",
            "definition_th": "สี่แยกที่การจราจรวนเป็นวงกลม ผู้ที่เข้าวงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้ว",
            "definition_en": "Road junction where traffic moves in a circle.",
            "topic_tags": ["Vikeplikt", "Kryss", "Rundkjøring"],
        },
        {
            "id": "3",
            "term_no": "Fartsgrense",
            "term_th": "ขีดจำกัดความเร็ว",
            "definition_no": "Høyeste tillatte hastighet på en vegstrekning.",
            "definition_th": "ความเร็วสูงสุดที่อนุญาตบนถนนช่วงนั้น หน่วยเป็น กม./ชม. (50/80)",
            "definition_en": "Maximum permitted speed on a road section.",
            "topic_tags": ["Fart", "Skilt"],
        },
        # No definition_th — must be dropped from any lang="th" response even
        # though it matches strongly on text (weight 2).
        {
            "id": "4",
            "term_no": "Blindsone",
            "term_th": "จุดบอด",
            "definition_no": "Området rundt bilen som ikke er synlig i speilene.",
            "definition_th": "",
            "definition_en": "The area around the car not visible in mirrors.",
            "topic_tags": ["Sikkerhet"],
        },
    ]


def _fake_cache_six_matching(category="Sikkerhet"):
    cache = []
    for i in range(6):
        cache.append({
            "id": str(100 + i),
            "term_no": "Term" + str(i),
            "term_th": "คำที่" + str(i),
            "definition_no": "Norsk definisjon " + str(i) + ".",
            "definition_th": "คำนิยามภาษาไทย " + str(i),
            "definition_en": "English definition " + str(i) + ".",
            "topic_tags": [category],
        })
    return cache


class QuizTermsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_quiz_terms()

    def test_vikeplikt_question_returns_vikeplikt(self):
        question = {"question_text_no": "Når har du vikeplikt i et kryss?", "category": "Vikeplikt"}
        result = self.module._build_terms_response("q1", question, _fake_cache(), "th")
        term_nos = [t["term_no"] for t in result["terms"]]
        self.assertIn("Vikeplikt", term_nos)

    def test_question_without_match_returns_empty(self):
        question = {"question_text_no": "Hvilken farge har bilen?", "category": "Diverse"}
        result = self.module._build_terms_response("q2", question, _fake_cache(), "th")
        self.assertEqual(result["terms"], [])

    def test_thai_definition_no_latin_leak(self):
        question = {"question_text_no": "Hva er fartsgrensen her, og gjelder høyreregelen i rundkjøring?", "category": "Fart"}
        result = self.module._build_terms_response("q3", question, _fake_cache(), "th")
        self.assertGreater(len(result["terms"]), 0)
        for term in result["terms"]:
            self.assertTrue(term["definition_th"])
            self.assertIsNone(re.search(r"[A-Za-z]{2,}", term["definition_th"]))

    def test_fail_stop_drops_term_without_thai_def(self):
        question = {"question_text_no": "Hva er en blindsone, og har jeg vikeplikt der?", "category": "Sikkerhet"}
        result = self.module._build_terms_response("q4", question, _fake_cache(), "th")
        term_nos = [t["term_no"] for t in result["terms"]]
        self.assertNotIn("Blindsone", term_nos)
        self.assertIn("Vikeplikt", term_nos)

    def test_cap_four_terms(self):
        question = {"question_text_no": "Ukjent tekst uten treff", "category": "Sikkerhet"}
        result = self.module._build_terms_response("q5", question, _fake_cache_six_matching(), "th")
        self.assertEqual(len(result["terms"]), 4)

    def test_unknown_question_id_returns_empty_not_error(self):
        result = self.module._build_terms_response("missing", None, _fake_cache(), "th")
        self.assertEqual(result, {"question_id": "missing", "lang": "th", "terms": []})

    def test_unknown_lang_falls_back_to_th_resolution(self):
        question = {"question_text_no": "Vikeplikt i kryss", "category": "Vikeplikt"}
        result = self.module._build_terms_response("q6", question, _fake_cache(), "xx")
        self.assertEqual(result["lang"], "th")


class SeedGlossaryMigrationTests(unittest.TestCase):
    def test_forkjorsvei_naming(self):
        module = _load_seed_glossary()
        term_names = [t["term_no"] for t in module.TERMS]
        self.assertIn("Forkjørsvei", term_names)
        self.assertNotIn("Prioritert vei", term_names)


if __name__ == "__main__":
    unittest.main()
