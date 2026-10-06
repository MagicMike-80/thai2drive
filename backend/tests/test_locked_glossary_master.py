"""The approved Norwegian–Thai glossary copy survives seeding and re-runs."""

import asyncio
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:27017")
_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "seed_glossary.py"
_SPEC = importlib.util.spec_from_file_location("seed_glossary_locked_test", _SCRIPT)
seed = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(seed)

APPROVED_THAI = {
    "Vikeplikt": "การให้ทาง",
    "Forkjørsvei": "ถนนที่มีสิทธิ์ผ่านก่อน",
    "Forkjørsrett": "สิทธิ์ในการผ่านก่อน",
    "Vikepliktskilt": "ป้ายให้ทาง",
    "Stoppskilt": "ป้ายหยุด",
    "Varselskilt": "ป้ายเตือน",
    "Forbudsskilt": "ป้ายห้าม",
    "Påbudsskilt": "ป้ายบังคับ",
    "Stopplengde": "ระยะทางในการหยุดรถ",
    "Reaksjonslengde": "ระยะทางในการตอบสนอง",
    "Bremselengde": "ระยะทางในการเบรก",
    "Fartsgrense": "ขีดจำกัดความเร็ว",
    "Rundkjøring": "วงเวียน",
    "Gangfelt": "ทางม้าลาย",
    "Trafikklys": "สัญญาณไฟจราจร",
}

APPROVED_NEW_COPY = {
    "Forkjørsrett": (
        "สิทธิ์ของผู้ใช้ทางในการผ่านหรือเคลื่อนที่ไปก่อนผู้ใช้ทางคนอื่นตามกฎจราจร",
        "รถที่มีสิทธิ์ผ่านก่อนสามารถขับผ่านไปได้ แต่ยังต้องระมัดระวังและปฏิบัติตามกฎจราจร",
    ),
    "Stoppskilt": (
        "ป้ายที่กำหนดให้ผู้ขับขี่ต้องหยุดรถให้สนิทก่อนขับต่อไป",
        "เมื่อเจอป้ายหยุด คุณต้องหยุดรถให้สนิทและตรวจดูการจราจรก่อนขับต่อ",
    ),
    "Varselskilt": (
        "ป้ายที่เตือนผู้ขับขี่ให้ทราบถึงอันตรายหรือสภาพถนนที่ต้องระมัดระวังข้างหน้า",
        "เมื่อเห็นป้ายเตือน ผู้ขับขี่ควรลดความเร็วและเตรียมพร้อมรับอันตรายข้างหน้า",
    ),
    "Forbudsskilt": (
        "ป้ายที่แสดงข้อห้ามหรือข้อจำกัดที่ผู้ใช้ทางต้องปฏิบัติตาม",
        "ป้ายห้ามอาจกำหนดว่าห้ามเข้า ห้ามจอด หรือห้ามใช้ความเร็วเกินที่กำหนด",
    ),
    "Påbudsskilt": (
        "ป้ายที่กำหนดว่าผู้ใช้ทางต้องปฏิบัติหรือขับไปในทิศทางที่ระบุ",
        "หากป้ายบังคับให้ขับตรงไป ผู้ขับขี่ต้องขับไปตามทิศทางที่ป้ายกำหนด",
    ),
    "Reaksjonslengde": (
        "ระยะทางที่รถเคลื่อนที่ตั้งแต่ผู้ขับขี่รับรู้ถึงอันตรายจนเริ่มเบรก",
        "เมื่อความเร็วเพิ่มขึ้น ระยะทางในการตอบสนองก็จะเพิ่มขึ้นด้วย",
    ),
}


class FakeCollection:
    def __init__(self, docs=()):
        self.docs = [dict(doc, _id=index + 1) for index, doc in enumerate(docs)]

    async def find_one(self, query):
        return next(
            (doc for doc in self.docs if all(doc.get(key) == value for key, value in query.items())),
            None,
        )

    async def update_one(self, query, update):
        doc = await self.find_one(query)
        if doc:
            doc.update(update["$set"])
        return SimpleNamespace(matched_count=int(doc is not None))

    async def insert_one(self, doc):
        self.docs.append({**doc, "_id": len(self.docs) + 1})


def test_locked_master_inserts_exact_approved_thai_and_is_repeatable():
    collection = FakeCollection()
    db = SimpleNamespace(learning_glossary=collection)

    assert asyncio.run(seed.sync_locked_master(db)) == (15, 0)
    assert asyncio.run(seed.sync_locked_master(db)) == (0, 0)
    assert len(collection.docs) == 15

    by_no = {doc["term_no"]: doc for doc in collection.docs}
    assert {doc["term_no"]: doc["term_th"] for doc in collection.docs} == APPROVED_THAI
    for term_no, term_th, extra in seed.LOCKED_MASTER:
        doc = by_no[term_no]
        assert doc["term_th"] == term_th
        assert doc["active"] is True
        for field, approved_value in extra.items():
            assert doc[field] == approved_value

    for term_no, (definition, example) in APPROVED_NEW_COPY.items():
        assert by_no[term_no]["definition_th"] == definition
        assert by_no[term_no]["example_th"] == example

    assert by_no["Fartsgrense"]["term_th"] == "ขีดจำกัดความเร็ว"
    assert by_no["Trafikklys"]["term_th"] == "สัญญาณไฟจราจร"
    assert by_no["Reaksjonslengde"]["term_th"] != by_no["Bremselengde"]["term_th"]
    assert by_no["Stopplengde"]["term_th"] != by_no["Bremselengde"]["term_th"]
    assert by_no["Varselskilt"]["aliases_no"] == ["Fareskilt"]


def test_locked_master_updates_legacy_names_without_losing_other_copy():
    collection = FakeCollection([
        {"term_no": "Stopp-skilt", "term_th": "old", "definition_no": "Behold norsk", "active": True},
        {"term_no": "Forkjørsvei", "term_th": "old", "definition_en": "Keep English", "active": True},
    ])
    db = SimpleNamespace(learning_glossary=collection)

    asyncio.run(seed.sync_locked_master(db))
    by_no = {doc["term_no"]: doc for doc in collection.docs}
    assert "Stopp-skilt" not in by_no
    assert by_no["Stoppskilt"]["definition_no"] == "Behold norsk"
    assert by_no["Stoppskilt"]["term_th"] == "ป้ายหยุด"
    assert by_no["Forkjørsvei"]["definition_en"] == "Keep English"
    assert by_no["Forkjørsvei"]["term_th"] == "ถนนที่มีสิทธิ์ผ่านก่อน"
    assert len(collection.docs) == 15


def test_locked_master_only_mode_does_not_seed_unrelated_terms(monkeypatch):
    collection = FakeCollection()
    db = SimpleNamespace(learning_glossary=collection)

    class FakeClient:
        def __init__(self, _url):
            self.closed = False

        def __getitem__(self, _name):
            return db

        def close(self):
            self.closed = True

    client = FakeClient("unused")
    monkeypatch.setattr(seed, "AsyncIOMotorClient", lambda _url: client)
    asyncio.run(seed.main(locked_master_only=True))

    assert client.closed
    assert {doc["term_no"] for doc in collection.docs} == set(APPROVED_THAI)
