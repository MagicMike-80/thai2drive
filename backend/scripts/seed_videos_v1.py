"""
seed_videos_v1.py — legg til 30 lokale mp4-videoer i learning_videos.
Trygt å kjøre på nytt — hopper over eksisterende (by file_path).
Kjør: cd thai2drive/backend && python scripts/seed_videos_v1.py
"""

import asyncio, os, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    MONGO_URL = line.split("=", 1)[1].strip('"').strip("'")
                    break
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found in environment or .env")

DB_NAME = "thai2drive"

VIDEOS = [
    # ── Norwegian-language videos ────────────────────────────────────────────
    {
        "file_path": "/public_assets/video_ki_revolusjon_laering.mp4",
        "title_no": "KI-revolusjonen innen læring",
        "title_th": "การปฏิวัติ AI ในการเรียนรู้",
        "title_en": "The AI revolution in learning",
        "topic_tags": ["AI", "Læring", "Teknologi"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_mestre_hav_regelen.mp4",
        "title_no": "Mestre HAV-regelen",
        "title_th": "เชี่ยวชาญกฎ HAV",
        "title_en": "Master the HAV rule",
        "topic_tags": ["HAV-regelen", "Vikeplikt", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_hav_regelen_reflekser.mp4",
        "title_no": "HAV-regelen — trygge reflekser",
        "title_th": "กฎ HAV — สร้างปฏิกิริยาอัตโนมัติที่ปลอดภัย",
        "title_en": "The HAV rule — building safe reflexes",
        "topic_tags": ["HAV-regelen", "Vikeplikt", "Reflekser"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_vegtrafikkloven_3.mp4",
        "title_no": "Vegtrafikkloven § 3 — grunnregelen",
        "title_th": "กฎหมายจราจร มาตรา 3 — กฎพื้นฐาน",
        "title_en": "Road Traffic Act § 3 — the basic rule",
        "topic_tags": ["Vegtrafikkloven", "Grunnregler", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_utvikling_ai_laering.mp4",
        "title_no": "Utviklingen av AI-læring",
        "title_th": "วิวัฒนาการของการเรียนรู้ด้วย AI",
        "title_en": "The evolution of AI-based learning",
        "topic_tags": ["AI", "Læring", "Teknologi"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_trafikk_okosystem_norge.mp4",
        "title_no": "Trafikkøkosystemet i Norge",
        "title_th": "ระบบนิเวศจราจรในนอร์เวย์",
        "title_en": "The traffic ecosystem in Norway",
        "topic_tags": ["Trafikkregler", "Norge", "System"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_michaels_gatelogikk.mp4",
        "title_no": "Michaels gatelogikk",
        "title_th": "ตรรกะถนนของไมเคิล",
        "title_en": "Michael's street logic",
        "topic_tags": ["Trafikkregler", "Pedagogikk", "Michael"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_mestring_vikeplikt.mp4",
        "title_no": "Mestring av vikeplikt",
        "title_th": "เชี่ยวชาญการให้ทาง",
        "title_en": "Mastering right of way",
        "topic_tags": ["Vikeplikt", "HAV-regelen", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_ai_trafikkopplaering.mp4",
        "title_no": "AI i trafikkopplæring",
        "title_th": "AI ในการฝึกอบรมจราจร",
        "title_en": "AI in traffic education",
        "topic_tags": ["AI", "Opplæring", "Teknologi"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_veien_norsk_forerkort.mp4",
        "title_no": "Veien til norsk førerkort",
        "title_th": "เส้นทางสู่ใบขับขี่นอร์เวย์",
        "title_en": "The road to a Norwegian driving licence",
        "topic_tags": ["Teoriprøve", "Førerkort", "Norge"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_uhell_dine_plikter.mp4",
        "title_no": "Uhell — dine plikter",
        "title_th": "อุบัติเหตุ — หน้าที่ของคุณ",
        "title_en": "Accidents — your obligations",
        "topic_tags": ["Uhell", "Plikter", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_offisielle_trafikkskilt.mp4",
        "title_no": "Offisielle trafikkskilt",
        "title_th": "ป้ายจราจรทางการ",
        "title_en": "Official traffic signs",
        "topic_tags": ["Trafikkskilt", "Skilt", "Teoriprøve"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_thai2drive_brukermanual.mp4",
        "title_no": "Thai2Drive brukermanual",
        "title_th": "คู่มือการใช้งาน Thai2Drive",
        "title_en": "Thai2Drive user manual",
        "topic_tags": ["Thai2Drive", "Brukermanual", "App"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    {
        "file_path": "/public_assets/video_thai_til_norsk_forerkort.mp4",
        "title_no": "Thai til norsk førerkort",
        "title_th": "จากใบขับขี่ไทยสู่นอร์เวย์",
        "title_en": "Thai to Norwegian driving licence",
        "topic_tags": ["Thailand", "Norge", "Førerkort"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "no", "active": True,
    },
    # ── Thai-language videos ─────────────────────────────────────────────────
    {
        "file_path": "/public_assets/video_th_kru_naung_baew.mp4",
        "title_no": "Læreren ved siden av — kjøreopplæring",
        "title_th": "ครูฝึกในเบาะผู้โดยสาร",
        "title_en": "The instructor in the passenger seat",
        "topic_tags": ["Opplæring", "Michael", "Kjøring"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_pichit_bai_khapkhi.mp4",
        "title_no": "Knus teoriprøven — Thai2Drive",
        "title_th": "Thai2Drive — พิชิตใบขับขี่",
        "title_en": "Thai2Drive — conquer your driving licence",
        "topic_tags": ["Teoriprøve", "Thai2Drive", "Motivasjon"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_thot_rahat_hav.mp4",
        "title_no": "Dekod trafikken — HAV-regelen",
        "title_th": "ถอดรหัสการจราจร — กฎ HAV",
        "title_en": "Decode traffic — the HAV rule",
        "topic_tags": ["HAV-regelen", "Vikeplikt", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_kot_su_sanchat.mp4",
        "title_no": "Trafikkregler som instinkt",
        "title_th": "กฎจราจรสู่สัญชาตญาณ",
        "title_en": "Traffic rules as instinct",
        "topic_tags": ["Trafikkregler", "Læring", "Instinkt"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_thalai_kamphaeng.mp4",
        "title_no": "Thai2Drive — bryt språkbarrieren",
        "title_th": "Thai2Drive — ทลายกำแพงภาษา",
        "title_en": "Thai2Drive — break the language barrier",
        "topic_tags": ["Thai2Drive", "Språk", "Thailand"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_bai_norway_class_b.mp4",
        "title_no": "Norsk førerkort klasse B",
        "title_th": "ใบขับขี่นอร์เวย์ คลาส B",
        "title_en": "Norwegian driving licence class B",
        "topic_tags": ["Førerkort", "Klasse B", "Norge"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_kasat_hab_vikeplikt.mp4",
        "title_no": "Kongen og tjeneren — vikeplikt",
        "title_th": "กษัตริย์กับคนรับใช้ — กฎให้ทาง",
        "title_en": "King and servant — right of way",
        "topic_tags": ["Vikeplikt", "Atferd", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_kot_thanon_vs_kotmai.mp4",
        "title_no": "Regler på veien vs. trafikkloven",
        "title_th": "กฎบนถนน vs กฎหมายจราจร",
        "title_en": "Road rules vs. traffic law",
        "topic_tags": ["Trafikkregler", "Vegtrafikkloven", "Teoriprøve"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_hai_thang_pro.mp4",
        "title_no": "Å gi vikeplikt som en proff",
        "title_th": "การให้ทางอย่างมืออาชีพ",
        "title_en": "Giving way like a professional",
        "topic_tags": ["Vikeplikt", "Kjøreteknikk", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_kham_upsak_phasa.mp4",
        "title_no": "Thai2Drive — over språkbarrieren",
        "title_th": "Thai2Drive — ข้ามอุปสรรคภาษา",
        "title_en": "Thai2Drive — crossing the language barrier",
        "topic_tags": ["Thai2Drive", "Språk", "Thailand"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_nang_lang_phuang.mp4",
        "title_no": "Første gang bak rattet",
        "title_th": "นั่งหลังพวงมาลัยครั้งแรก",
        "title_en": "First time behind the wheel",
        "topic_tags": ["Nybegynnere", "Kjøring", "Erfaring"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_sathapatayakam_phasa.mp4",
        "title_no": "Thai2Drive — språkarkitekturen",
        "title_th": "สถาปัตยกรรมภาษา Thai2Drive",
        "title_en": "Thai2Drive — language architecture",
        "topic_tags": ["Thai2Drive", "Språk", "Teknologi"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_kot_hai_thang_6.mp4",
        "title_no": "Vikeplikt — 6 viktige regler",
        "title_th": "กฎการให้ทาง — 6 ข้อสำคัญ",
        "title_en": "Right of way — 6 key rules",
        "topic_tags": ["Vikeplikt", "HAV-regelen", "Trafikkregler"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_pichit_khan_1.mp4",
        "title_no": "Knus trinn 1 — trafikkurs",
        "title_th": "พิชิตขั้นที่ 1 — หลักสูตรจราจร",
        "title_en": "Conquer step 1 — traffic course",
        "topic_tags": ["Teoriprøve", "Trinn 1", "Opplæring"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_khamnanam_khapkhi.mp4",
        "title_no": "Råd for trygg kjøring",
        "title_th": "คำแนะนำการขับขี่ปลอดภัย",
        "title_en": "Safe driving tips",
        "topic_tags": ["Sikkerhet", "Kjøring", "Råd"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
    {
        "file_path": "/public_assets/video_th_klum_pai_norway.mp4",
        "title_no": "9 grupper norske trafikkskilt",
        "title_th": "9 กลุ่มป้ายจราจรนอร์เวย์",
        "title_en": "9 groups of Norwegian traffic signs",
        "topic_tags": ["Trafikkskilt", "Skilt", "Teoriprøve"],
        "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "language": "th", "active": True,
    },
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = skipped = 0
    for v in VIDEOS:
        existing = await db.learning_videos.find_one({"file_path": v["file_path"]})
        if existing:
            print(f"  SKIP: {v['file_path']}")
            skipped += 1
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "youtube_url": "",
            "thumbnail_url": "",
            "duration_seconds": 0,
            "see_context": "",
            "understand_context": "",
            "choose_context": "",
            "instructor_summary_no": "",
            "instructor_summary_th": "",
            "instructor_summary_en": "",
            **v,
        }
        await db.learning_videos.insert_one(doc)
        print(f"  INSERT [{v['language'].upper()}]: {v['title_no']}")
        inserted += 1
    print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
