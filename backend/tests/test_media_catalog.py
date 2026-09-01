import asyncio
import unittest

from backend.media_catalog import (
    LAW_MAPPING,
    MediaCatalogValidationError,
    expand_law_synonyms,
    list_localized_catalog_media,
    rank_catalog_media,
    serialize_catalog_document,
    validate_catalog_document,
    validate_catalog_documents,
)


def _item(media_id="vid_test_no", **overrides):
    item = {
        "media_id": media_id,
        "type": "video",
        "category": "stoppelengde",
        "tags": ["stoppelengde", "reaksjonslengde"],
        "media_url": "https://media.example/video.mp4",
        "thumbnail_url": "/api/assets/thumbs/video.jpg",
        "is_active": True,
        "content_language": "no",
        "i18n": {
            "no": {"title": "NO-TITTEL", "description": "NO-BESKRIVELSE"},
            "th": {"title": "TH-TITTEL", "description": "TH-BESKRIVELSE"},
            "en": {"title": "EN-TITLE", "description": "EN-DESCRIPTION"},
        },
    }
    item.update(overrides)
    return item


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs[:length]


class _Collection:
    def __init__(self, docs):
        self.docs = docs
        self.query = None

    def find(self, query):
        self.query = query
        return _Cursor(self.docs)


class MediaCatalogTests(unittest.TestCase):
    def test_schema_normalizes_tags_and_defaults_active(self):
        item = _item(tags=["  Stoppelengde ", "Reaksjons-lengde"])
        item.pop("is_active")
        normalized = validate_catalog_document(item)
        self.assertEqual(normalized["tags"], ["stoppelengde", "reaksjons lengde"])
        self.assertTrue(normalized["is_active"])

    def test_schema_rejects_invalid_enums_urls_duplicate_tags_and_ids(self):
        cases = [
            _item(type="image"),
            _item(category="annet"),
            _item(content_language="nb"),
            _item(media_url="http://media.example/video.mp4"),
            _item(thumbnail_url="/api/sign-images/204_0.png"),
            _item(tags=["Stopp", "stopp"]),
            _item(i18n={"no": {"title": "x", "description": "y"}}),
        ]
        for item in cases:
            with self.subTest(item=item):
                with self.assertRaises(MediaCatalogValidationError):
                    validate_catalog_document(item)
        with self.assertRaises(MediaCatalogValidationError):
            validate_catalog_documents([_item("duplicate"), _item("duplicate")])

    def test_serializer_is_language_pure_and_never_exposes_i18n(self):
        norwegian = serialize_catalog_document(_item(), "no")
        self.assertEqual(norwegian["title"], "NO-TITTEL")
        self.assertEqual(norwegian["description"], "NO-BESKRIVELSE")
        self.assertNotIn("i18n", norwegian)
        self.assertNotIn("content_language", norwegian)
        self.assertNotIn("TH-", str(norwegian))
        self.assertIsNone(serialize_catalog_document(_item(), "th"))
        self.assertIsNone(serialize_catalog_document(_item(), "en"))
        self.assertIsNone(serialize_catalog_document(_item(), "nb"))

    def test_neutral_media_uses_only_requested_metadata(self):
        item = _item(content_language="neutral")
        for language, sentinel in (("no", "NO-TITTEL"), ("th", "TH-TITTEL"), ("en", "EN-TITLE")):
            with self.subTest(language=language):
                payload = serialize_catalog_document(item, language)
                self.assertEqual(payload["title"], sentinel)

    def test_law_synonyms_resolve_paragraf_and_venstresving_to_7_2_tags(self):
        for query in ("Hva sier paragraf 7 om vikeplikt?", "vikeplikt venstresving"):
            with self.subTest(query=query):
                resolved = expand_law_synonyms(query)
                self.assertEqual(resolved, set(LAW_MAPPING["7_2"]["tags"]))

    def test_law_synonyms_resolve_paragraf_3_to_hav_regelen_tags(self):
        resolved = expand_law_synonyms("Kan du forklare hav-regelen fra paragraf 3?")
        self.assertEqual(resolved, set(LAW_MAPPING["3"]["tags"]))

    def test_law_synonyms_ignore_bare_section_sign_digits(self):
        # "§ 3" would normalize to the bare digit "3" and cause false positives
        # on any unrelated message mentioning that number, so it must not match.
        self.assertEqual(expand_law_synonyms("Spørsmål 3 av 10 i teoriprøven"), set())

    def test_law_synonyms_narrow_bus_rule_does_not_leak_generic_paragraf_7(self):
        resolved = expand_law_synonyms("paragraf 7 nr 4 om bussregelen")
        self.assertTrue(set(LAW_MAPPING["7_4"]["tags"]).issubset(resolved))

    def test_ranker_uses_whole_tags_and_deterministic_order_with_max_one(self):
        unrelated = _item("unrelated", tags=["stopp"])
        best = _item("best", tags=["stoppelengde", "bremselengde"])
        other = _item("other", tags=["stoppelengde"])
        ranked = rank_catalog_media(
            [other, unrelated, best], "Forklar stoppelengde og bremselengde", "no", limit=9
        )
        self.assertEqual([item["media_id"] for item in ranked], ["best"])
        self.assertEqual(rank_catalog_media([unrelated], "stoppelengde", "no"), [])

    def test_inactive_incomplete_and_language_mismatch_are_hidden(self):
        inactive = _item("inactive", is_active=False)
        incomplete = _item("incomplete")
        incomplete["i18n"]["th"]["description"] = ""
        self.assertEqual(rank_catalog_media([inactive, incomplete], "stoppelengde", "no"), [])

    def test_library_query_and_sort_are_active_and_language_scoped(self):
        podcast = _item(
            "pod",
            type="podcast",
            content_language="neutral",
            media_url="https://media.example/audio.mp3",
        )
        video = _item("vid", content_language="neutral")
        collection = _Collection([podcast, video])
        result = asyncio.run(list_localized_catalog_media(collection, "en"))
        self.assertEqual([item["media_id"] for item in result], ["vid", "pod"])
        self.assertEqual(
            collection.query,
            {"is_active": True, "content_language": {"$in": ["en", "neutral"]}},
        )

    def test_empty_library_is_a_normal_empty_result(self):
        collection = _Collection([])
        self.assertEqual(
            asyncio.run(list_localized_catalog_media(collection, "th")),
            [],
        )


if __name__ == "__main__":
    unittest.main()
