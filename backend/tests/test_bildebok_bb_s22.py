from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "scripts"))

from backend import teacher_chat as tc  # noqa: E402
from bildebok_lookup import find_active_page, get_active_page_by_id, load_pack, row_hash  # noqa: E402


class Cursor:
    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return []


class Collection:
    def find(self, *args, **kwargs):
        return Cursor()

    async def insert_many(self, *args, **kwargs):
        return None


class Database:
    def __getitem__(self, name):
        return Collection()


class BildebokLessonTests(unittest.TestCase):
    def test_bb_s22_is_active_hash_bound_and_language_isolated(self):
        pack = load_pack()
        self.assertEqual(len(pack["pages"]), 1)
        row = pack["pages"][0]
        self.assertEqual(row["id"], "bb-s22")
        self.assertEqual(row["status"], "aktiv")
        self.assertEqual(row["image_status"], "godkjent")
        self.assertEqual(row["approval_hash"], row_hash(row))
        altered = copy.deepcopy(row)
        altered["points"][0]["no"] += " endret"
        self.assertIsNone(get_active_page_by_id("bb-s22", "no", {"pages": [altered]}))
        altered_image = copy.deepcopy(row)
        altered_image["image_sha256"] = "0" * 64
        self.assertIsNone(get_active_page_by_id("bb-s22", "no", {"pages": [altered_image]}))
        image = BACKEND / "public_assets" / "bildebok" / row["image_file"]
        self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), row["image_sha256"])
        self.assertEqual(tc._bildebok_media_card(get_active_page_by_id("bb-s22", "no"))["id"], "bildebok:bb-s22")

        self.assertIsNone(find_active_page("How do I change my password?", "en"))
        queries = {
            "no": "Forklar snever og bred oppmerksomhet med lastebilen og motorsykkelen",
            "th": "อธิบายความสนใจแบบแคบและกว้างในภาพรถบรรทุกและรถจักรยานยนต์",
            "en": "Explain narrow and wide attention with the lorry and motorcycle",
        }
        markers = {"no": "GODKJENT BILDEBOKLEKSJON", "th": "บทเรียนจากหนังสือภาพที่อนุมัติแล้ว", "en": "APPROVED PICTURE-BOOK LESSON"}
        for lang, query in queries.items():
            with self.subTest(lang=lang):
                page = find_active_page(query, lang)
                self.assertEqual(page["id"], "bb-s22")
                context = tc._bildebok_prompt_context(page, lang)
                self.assertIn(markers[lang], context)
                self.assertEqual(page["title"], row["title"][lang])
                self.assertEqual(page["core_sentence"], row["core_sentence"][lang])
                card = tc._bildebok_media_card(page)
                self.assertEqual(card["title"], row["title"][lang])
                self.assertEqual(card["caption"], row["core_sentence"][lang])

    def test_teacher_chat_uses_approved_bb_s22_context_and_image_in_all_languages(self):
        old_db, old_chat = tc._db, tc._chat_col
        tc._db, tc._chat_col = Database(), Collection()
        messages = {
            "no": "Forklar snever og bred oppmerksomhet med lastebilen og motorsykkelen",
            "th": "อธิบายความสนใจแบบแคบและกว้างในภาพรถบรรทุกและรถจักรยานยนต์",
            "en": "Explain narrow and wide attention with the lorry and motorcycle",
        }
        replies = {
            "no": "Løft blikket og se hele krysset.",
            "th": "เงยสายตาขึ้นและมองภาพรวมของทางแยก",
            "en": "Lift your gaze and look across the whole junction.",
        }
        try:
            for lang in ("no", "th", "en"):
                captured = {}
                async def completion(prompt):
                    captured["prompt"] = prompt
                    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=replies[lang]))])

                req = tc.TeacherChatRequest(message=messages[lang], language=lang, session_id=f"bb-s22-{lang}")
                with patch.object(tc, "LLM_KEY", "mock-only"), \
                     patch.object(tc, "_completion_with_fallback", new=completion), \
                     patch.object(tc, "_v4_next_stage", return_value="5"), \
                     patch.object(tc, "fetch_student_learning_memory", new=AsyncMock(return_value=None)), \
                     patch.object(tc, "resolve_traffic_concept", new=AsyncMock(return_value=None)), \
                     patch.object(tc, "_get_curriculum_context", new=AsyncMock(return_value="")), \
                     patch.object(tc, "get_relevant_resources", new=AsyncMock(return_value={"videos": [], "podcasts": []})), \
                     patch.object(tc, "_get_relevant_michael_materials", new=AsyncMock(return_value=[])), \
                     patch.object(tc, "_get_relevant_catalog_media", new=AsyncMock(return_value=[])), \
                     patch.object(tc, "_get_exact_sign_media", new=AsyncMock(return_value=[])):
                    response = asyncio.run(tc.teacher_chat(req))

                with self.subTest(lang=lang):
                    self.assertIn(tc._bildebok_prompt_context(find_active_page(messages[lang], lang), lang), captured["prompt"][0]["content"])
                    self.assertEqual(response.reply, replies[lang])
                    self.assertEqual(len(response.media), 1)
                    self.assertEqual(response.media[0]["id"], "bildebok:bb-s22")
                    self.assertEqual(response.media[0]["type"], "image")
                    self.assertTrue(response.media[0]["url"].endswith("/bb_s22_advisor_v1_40ab410483d4.png"))
                    self.assertEqual(response.media[0]["title"], load_pack()["pages"][0]["title"][lang])
        finally:
            tc._db, tc._chat_col = old_db, old_chat

    def test_sign_202_thai_yields_without_claiming_a_mandatory_stop(self):
        signs = json.loads((BACKEND / "signs_content.json").read_text(encoding="utf-8"))
        sign = next(item for item in signs if item["id"] == "202_0")
        expected = "คุณต้องให้ทางโดยไม่กีดขวางหรือรบกวนรถอื่น ชะลอความเร็วหรือหยุดเมื่อจำเป็นเท่านั้น"
        self.assertEqual(sign["explanation"]["th"], expected)
        self.assertEqual(sign["driver_action"]["th"], expected)
        self.assertNotIn("คุณต้องหยุดรอ", json.dumps(sign, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
