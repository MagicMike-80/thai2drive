"""
Offline tests for Studiebok learning screens (studiebok_screens.py + studiebok_screens_v6.json).

No network, no production database. Seeding is tested against mongomock.

    cd backend && python -m pytest tests/test_studiebok_screens.py -v
"""

import copy
import json
import re
import unittest

import mongomock

try:
    import studiebok_screens as ss
except ImportError:  # running from repo root
    from backend import studiebok_screens as ss

PACK = ss.load_pack()


def _chapter(order=1):
    return copy.deepcopy(next(c for c in PACK["chapters"] if c["order"] == order))


def _errors_after(mutate, order=1):
    ch = _chapter(order)
    mutate(ch)
    return ss.validate_chapter(ch)


class PackContent(unittest.TestCase):
    def test_pack_validates_without_errors(self):
        self.assertEqual(ss.validate_pack(PACK), [])

    def test_all_fifteen_studiebok_chapters_are_covered(self):
        self.assertEqual([c["order"] for c in PACK["chapters"]], list(range(1, 16)))

    def test_every_chapter_has_15_to_18_screens(self):
        for ch in PACK["chapters"]:
            self.assertTrue(15 <= len(ch["screens"]) <= 18, f"kap {ch['order']}: {len(ch['screens'])}")

    def test_total_screen_count_matches_sum(self):
        self.assertEqual(ss.total_screens(PACK), sum(len(c["screens"]) for c in PACK["chapters"]))
        self.assertGreaterEqual(ss.total_screens(PACK), 15 * 15)

    def test_road_check_after_every_3_to_5_screens(self):
        for ch in PACK["chapters"]:
            gap = 0
            for s in ch["screens"]:
                if s["type"] == "road_check":
                    self.assertTrue(3 <= gap <= 5, f"kap {ch['order']} {s['id']}: gap {gap}")
                    gap = 0
                else:
                    gap += 1
            self.assertLessEqual(gap, 5, f"kap {ch['order']}: for lang hale uten veisjekk")

    def test_every_chapter_has_what_changed_pairs_with_hotspots(self):
        for ch in PACK["chapters"]:
            pairs = [s for s in ch["screens"] if s["type"] == "what_changed"]
            self.assertGreaterEqual(len(pairs), 2, f"kap {ch['order']}")
            for s in pairs:
                self.assertIn("image_before", s)
                self.assertIn("image_after", s)
                self.assertTrue(2 <= len(s["hotspots"]) <= 4)

    def test_english_ui_labels_do_not_leak_into_content(self):
        raw = json.dumps(PACK, ensure_ascii=False)
        for label in ("ROAD CHECK", "WHAT CHANGED", "Road check", "What changed"):
            self.assertNotIn(label, raw)

    def test_badges_are_localized_thai_and_norwegian(self):
        rc = next(s for c in PACK["chapters"] for s in c["screens"] if s["type"] == "road_check")
        wc = next(s for c in PACK["chapters"] for s in c["screens"] if s["type"] == "what_changed")
        self.assertEqual(rc["badge_no"], "Veisjekk ⚡")
        self.assertEqual(rc["badge_th"], "ตรวจถนน ⚡")
        self.assertEqual(wc["badge_no"], "Hva er endret?")

    def test_no_english_fields_are_present(self):
        for ch in PACK["chapters"]:
            for s in ch["screens"]:
                self.assertFalse([k for k in s if k.endswith("_en")], s["id"])

    def test_thai_fields_never_show_latin_outside_parentheses(self):
        for ch in PACK["chapters"]:
            for s in ch["screens"]:
                for key, text in ss._strings(s):
                    if key.endswith("_th") or "_th[" in key:
                        outside = ss.PAREN_RE.sub("", text)
                        self.assertIsNone(ss.LATIN_RE.search(outside), f"{s['id']}.{key}: {text}")

    def test_norwegian_fields_have_no_thai(self):
        for ch in PACK["chapters"]:
            for s in ch["screens"]:
                for key, text in ss._strings(s):
                    if re.search(r"_no(\[\d+\])?$", key):
                        self.assertIsNone(ss.THAI_RE.search(text), f"{s['id']}.{key}")

    def test_json_roundtrip_is_lossless(self):
        self.assertEqual(json.loads(json.dumps(PACK, ensure_ascii=False)), PACK)

    def test_screen_ids_are_unique_across_pack(self):
        ids = [s["id"] for c in PACK["chapters"] for s in c["screens"]]
        self.assertEqual(len(ids), len(set(ids)))


class ValidatorCatchesErrors(unittest.TestCase):
    def test_english_word_in_norwegian_field(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(body_no="Du må check the road."))
        self.assertTrue(any("engelsk" in e for e in errs))

    def test_thai_characters_in_norwegian_field(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(title_no="Vegtrafikkloven กฎหมาย"))
        self.assertTrue(any("thai-tegn i norsk" in e for e in errs))

    def test_latin_letters_outside_parentheses_in_thai(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(body_th="กฎหมายจราจร Vegtrafikkloven ใช้กับทุกคน"))
        self.assertTrue(any("latinske bokstaver" in e for e in errs))

    def test_english_word_inside_fagord_parentheses(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(body_th="กฎหมายจราจรทางถนน (road rules) ใช้กับทุกคน"))
        self.assertTrue(any("engelsk ord i fagord" in e for e in errs))

    def test_fagord_must_follow_thai_explanation(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(body_th="ขีดจำกัด 80 (fartsgrense) ในเขตชุมชน"))
        self.assertTrue(any("ikke rett etter thai-forklaring" in e for e in errs))

    def test_unbalanced_parenthesis(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(body_th="กฎหมายจราจร (Vegtrafikkloven ใช้กับทุกคน"))
        self.assertTrue(any("ubalansert parentes" in e for e in errs))

    def test_too_few_screens(self):
        errs = _errors_after(lambda ch: ch["screens"].__delitem__(slice(14, None)))
        self.assertTrue(any("skjermer, forventer" in e for e in errs))

    def test_missing_road_check_gives_gap_error(self):
        def drop_first_road_check(ch):
            i = next(i for i, s in enumerate(ch["screens"]) if s["type"] == "road_check")
            del ch["screens"][i]
            for n, s in enumerate(ch["screens"], start=1):
                s["n"] = n
        errs = _errors_after(drop_first_road_check)
        self.assertTrue(any("veisjekk" in e for e in errs))

    def test_hotspot_out_of_range(self):
        def bad(ch):
            next(s for s in ch["screens"] if s["type"] == "what_changed")["hotspots"][0]["x"] = 140
        self.assertTrue(any("hotspot 0 ugyldig" in e for e in _errors_after(bad)))

    def test_correct_index_out_of_range(self):
        def bad(ch):
            next(s for s in ch["screens"] if s["type"] == "road_check")["correct_index"] = 3
        self.assertTrue(any("correct_index" in e for e in _errors_after(bad)))

    def test_unknown_screen_type(self):
        errs = _errors_after(lambda ch: ch["screens"][0].update(type="quiz"))
        self.assertTrue(any("ukjent type" in e for e in errs))

    def test_duplicate_ids(self):
        errs = _errors_after(lambda ch: ch["screens"][1].update(id=ch["screens"][0]["id"]))
        self.assertTrue(any("duplisert id" in e for e in errs))


def _seed(db, orders=range(1, 16)):
    for o in orders:
        db.studiebok_chapters.insert_one({
            "order": o, "icon": "📖", "title_no": f"Kapittel {o}", "title_th": f"บทที่ {o}",
            "content_no": f"<p>norsk {o}</p>", "content_th": f"<p>ไทย {o}</p>",
            "content_en": f"<p>english {o}</p>", "image_url": "", "video_url": "",
        })


class ApplyPackToMockDb(unittest.TestCase):
    def setUp(self):
        self.db = mongomock.MongoClient().t2d_test

    def test_dry_run_writes_nothing(self):
        _seed(self.db)
        report = ss.apply_pack(self.db, PACK, commit=False)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["updated"], list(range(1, 16)))
        self.assertEqual(self.db.studiebok_chapters.count_documents({"screens": {"$exists": True}}), 0)

    def test_commit_sets_screens_and_count_on_every_chapter(self):
        _seed(self.db)
        ss.apply_pack(self.db, PACK, commit=True)
        for ch in PACK["chapters"]:
            doc = self.db.studiebok_chapters.find_one({"order": ch["order"]})
            self.assertEqual(doc["screens"], ch["screens"])
            self.assertEqual(doc["screen_count"], len(ch["screens"]))

    def test_commit_leaves_existing_content_untouched(self):
        _seed(self.db)
        before = {d["order"]: {k: v for k, v in d.items() if k not in ("_id", "screens", "screen_count")}
                  for d in self.db.studiebok_chapters.find()}
        ss.apply_pack(self.db, PACK, commit=True)
        after = {d["order"]: {k: v for k, v in d.items() if k not in ("_id", "screens", "screen_count")}
                 for d in self.db.studiebok_chapters.find()}
        self.assertEqual(before, after)

    def test_missing_chapters_are_reported_not_created(self):
        _seed(self.db, orders=range(1, 15))
        report = ss.apply_pack(self.db, PACK, commit=True)
        self.assertEqual(report["missing"], [15])
        self.assertEqual(self.db.studiebok_chapters.count_documents({}), 14)

    def test_invalid_pack_writes_nothing_at_all(self):
        _seed(self.db)
        bad = copy.deepcopy(PACK)
        bad["chapters"][-1]["screens"][0]["body_no"] = "You must check the road."
        report = ss.apply_pack(self.db, bad, commit=True)
        self.assertTrue(report["errors"])
        self.assertEqual(self.db.studiebok_chapters.count_documents({"screens": {"$exists": True}}), 0)

    def test_commit_is_idempotent(self):
        _seed(self.db)
        ss.apply_pack(self.db, PACK, commit=True)
        first = list(self.db.studiebok_chapters.find({}, {"_id": 0}).sort("order", 1))
        ss.apply_pack(self.db, PACK, commit=True)
        second = list(self.db.studiebok_chapters.find({}, {"_id": 0}).sort("order", 1))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
