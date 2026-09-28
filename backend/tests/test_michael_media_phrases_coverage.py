"""Offline coverage check for the full 25-set media retrieval taxonomy.

Runs the real ``teacher_chat._get_relevant_michael_materials`` +
``_compose_teacher_media`` against an in-memory database built from the real
``michael_video_import`` documents.  No network, no MongoDB, no prod writes.

The five topics mirror the driftsordre: bus rule, stopping distance 80,
right-hand rule, leaving private property, reaction distance.
"""
import asyncio
import unittest

from backend.michael_video_import import (
    EXTRA_MATERIALS,
    VIDEO_SPECS,
    learning_video_document,
    michael_material_document,
)
from backend.tests.test_teacher_chat_fallback import _load_teacher_chat
from backend.tests.test_michael_material_retrieval import _Database


def _all_materials():
    materials = [michael_material_document(spec, publish=True) for spec in VIDEO_SPECS]
    materials += [
        {**extra, "active": True, "approved_for_michael": True}
        for extra in EXTRA_MATERIALS
    ]
    return materials


def _all_videos():
    return [learning_video_document(spec, publish=True) for spec in VIDEO_SPECS]


class MichaelMediaPhrasesCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_teacher_chat()

    def _retrieve(self, message, lang="no"):
        self.module._db = _Database(_all_materials(), _all_videos())
        return asyncio.run(
            self.module._get_relevant_michael_materials(
                message, lang, sign_ids=[], explicit_sign_ids=[]
            )
        )

    # ── the five independent topics ────────────────────────────────────────
    def test_five_topics_each_return_a_valid_media_link(self):
        cases = {
            "bussregel": (
                "kan du forklare bussregel bilde takk",
                "material_vikeplikt_7_5a_buss",
            ),
            "stoppelengde 80": (
                "vis meg stoppelengde 80 bilde",
                "material_stoppelengde_80",
            ),
            "høyreregel": (
                "høyreregel bilde",
                "sit_kryss_hoyreregel_7",
            ),
            "vikeplikt utkjøring": (
                "vikeplikt utkjøring bilde",
                "material_vikeplikt_7_4a_utkjoring",
            ),
            "reaksjonslengde": (
                "reaksjonslengde bilde",
                "material_reaksjonslengde_40",
            ),
        }
        for topic, (message, expected_id) in cases.items():
            with self.subTest(topic=topic):
                media = self._retrieve(message)
                self.assertTrue(media, f"{topic!r} returned no media")
                top = media[0]
                self.assertEqual(top["id"], expected_id, f"{topic!r} resolved to {top['id']}")
                self.assertTrue(
                    self.module._safe_michael_material_url(top["url"]),
                    f"{topic!r} url is not app-safe: {top['url']!r}",
                )
                self.assertTrue(top["title"], f"{topic!r} missing localized title")
                self.assertTrue(top["caption"], f"{topic!r} missing localized caption")

    # ── the exact reported regression: no article, mixed spelling ──────────
    def test_bare_bussregel_without_article_returns_bus_video(self):
        media = self._retrieve("bussregel")
        self.assertTrue(media, "bare 'bussregel' still returns nothing")
        self.assertEqual(media[0]["id"], "material_vikeplikt_7_5a_buss")
        self.assertEqual(media[0]["type"], "video")

    # ── speed qualifier must pick the matching clip, not bremselengde_40 ───
    def test_speed_qualifier_disambiguates_distance_videos(self):
        self.assertEqual(
            self._retrieve("hvor lang er stoppelengden i 80")[0]["id"],
            "material_stoppelengde_80",
        )
        self.assertEqual(
            self._retrieve("bremselengde ved 40")[0]["id"],
            "material_bremselengde_40",
        )
        self.assertEqual(
            self._retrieve("reaksjonslengde 80")[0]["id"],
            "material_reaksjonslengde_80",
        )

    # ── composed response media (what TeacherChatResponse.media carries) ───
    def test_compose_teacher_media_fills_response_media(self):
        self.module._db = _Database(_all_materials(), _all_videos())
        approved = asyncio.run(
            self.module._get_relevant_michael_materials(
                "bussregel bilde", "no", sign_ids=[], explicit_sign_ids=[]
            )
        )
        composed = self.module._compose_teacher_media(approved, [], explicit_sign_ids=[])
        self.assertTrue(composed)
        self.assertEqual(composed[0]["id"], "material_vikeplikt_7_5a_buss")
        self.assertLessEqual(len(composed), 2)

    # ── every set is reachable by at least one phrase ─────────────────────
    def test_every_video_set_has_match_phrases(self):
        for spec in VIDEO_SPECS:
            with self.subTest(slug=spec.slug):
                doc = michael_material_document(spec, publish=True)
                self.assertTrue(
                    doc["match_phrases"],
                    f"{spec.slug} has no match_phrases",
                )

    def test_thai_bus_query_returns_bus_video(self):
        media = self._retrieve("ขอรูปกฎรถบัส", lang="th")
        self.assertTrue(media, "Thai bus-rule query returned nothing")
        self.assertEqual(media[0]["id"], "material_vikeplikt_7_5a_buss")


if __name__ == "__main__":
    unittest.main(verbosity=2)
