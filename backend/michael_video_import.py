"""Deterministic draft catalog for Michael's new local learning videos.

The source folders are user-provided workspace inputs.  Records stay inactive
until a local database import is explicitly published after language/content QA.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VIKEPLIKT_SOURCE_DIR = "vikeplit mp4"
STOPPING_SOURCE_DIR = "Mp4 video  Reaksjonslende+Bremselengde+ Stoppelengde"
ASSET_DIR = Path("backend/public_assets")
THUMB_DIR = ASSET_DIR / "thumbs"


@dataclass(frozen=True)
class VideoSpec:
    slug: str
    source_dir: str
    source_name: str
    titles: dict[str, str]
    captions: dict[str, str]
    topic_tags: tuple[str, ...]
    category: str
    speed_limit: int | None = None
    learner_languages: tuple[str, ...] = ("no", "th")

    @property
    def video_id(self) -> str:
        return f"michael_{self.slug}"

    @property
    def material_id(self) -> str:
        return f"material_{self.slug}"

    @property
    def asset_name(self) -> str:
        return f"video_{self.slug}.mp4"

    @property
    def thumbnail_name(self) -> str:
        return f"thumb_{self.slug}.jpg"

    @property
    def subtitle_name(self) -> str:
        return f"video_{self.slug}.th.vtt"


def _localized(no: str, th: str, en: str) -> dict[str, str]:
    return {"no": no, "th": th, "en": en}


def _law_spec(
    slug: str,
    source_name: str,
    number: str,
    variant: str = "",
    *,
    title: dict[str, str] | None = None,
    caption: dict[str, str] | None = None,
    extra_tags: Iterable[str] = (),
) -> VideoSpec:
    suffix = f" – {variant}" if variant else ""
    titles = title or _localized(
        f"Vikeplikt – § 7 nr. {number}{suffix}",
        f"การให้ทาง – มาตรา 7 ข้อ {number}{suffix}",
        f"Right-of-way – section 7 no. {number}{suffix}",
    )
    captions = caption or _localized(
        f"Kort visuell forklaring av vikeplikt etter § 7 nr. {number}.",
        f"คำอธิบายแบบภาพสั้น ๆ เกี่ยวกับการให้ทางตามมาตรา 7 ข้อ {number}",
        f"A short visual explanation of right-of-way under section 7 no. {number}.",
    )
    return VideoSpec(
        slug=slug,
        source_dir=VIKEPLIKT_SOURCE_DIR,
        source_name=source_name,
        titles=titles,
        captions=captions,
        topic_tags=("Vikeplikt", "vikeplikt", "7", f"7_{number}", *extra_tags),
        category="vikeplikt",
    )


def _distance_spec(
    slug: str,
    source_name: str,
    concept: str,
    speed: int | None,
    variant: str = "",
) -> VideoSpec:
    names = {
        "braking": _localized("Bremselengde", "ระยะเบรก", "Braking distance"),
        "reaction": _localized("Reaksjonslengde", "ระยะตอบสนอง", "Reaction distance"),
        "stopping": _localized("Stoppelengde", "ระยะหยุด", "Stopping distance"),
    }[concept]
    tag = {
        "braking": "Bremsing",
        "reaction": "Reaksjonstid",
        "stopping": "Avstand og tid",
    }[concept]
    speed_text = f" – {speed} km/t" if speed else ""
    variant_text = f" ({variant})" if variant else ""
    titles = {
        lang: f"{name}{speed_text}{variant_text}"
        for lang, name in names.items()
    }
    speed_no = f"ved {speed} km/t" if speed else "ved ulike hastigheter"
    speed_th = f"ที่ความเร็ว {speed} กม./ชม." if speed else "ที่ความเร็วต่าง ๆ"
    speed_en = f"at {speed} km/h" if speed else "at different speeds"
    captions = {
        "braking": _localized(
            f"Videoen viser bremselengden {speed_no}.",
            f"วิดีโอนี้แสดงระยะเบรก{speed_th}",
            f"The video shows the braking distance {speed_en}.",
        ),
        "reaction": _localized(
            f"Videoen viser reaksjonslengden {speed_no}, før bremsingen begynner.",
            f"วิดีโอนี้แสดงระยะตอบสนอง{speed_th} ก่อนเริ่มเบรก",
            f"The video shows the reaction distance {speed_en}, before braking begins.",
        ),
        "stopping": _localized(
            f"Videoen viser stoppelengden {speed_no}: reaksjonslengde pluss bremselengde.",
            f"วิดีโอนี้แสดงระยะหยุด{speed_th}: ระยะตอบสนองบวกระยะเบรก",
            f"The video shows the stopping distance {speed_en}: reaction distance plus braking distance.",
        ),
    }[concept]
    tags = (tag, concept, "stoppelengde")
    if speed:
        tags = (*tags, f"{speed}_km_t")
    return VideoSpec(
        slug=slug,
        source_dir=STOPPING_SOURCE_DIR,
        source_name=source_name,
        titles=titles,
        captions=captions,
        topic_tags=tags,
        category="stoppelengde",
        speed_limit=speed,
    )


VIDEO_SPECS: tuple[VideoSpec, ...] = (
    _law_spec("vikeplikt_7_1a", "7.1a vikeplikt punt 1.mp4", "1", "A"),
    _law_spec("vikeplikt_7_2a", "7.2a vikeplikt punt 2.mp4", "2", "A"),
    _law_spec("vikeplikt_7_2ak", "7.2aK vikeplikt punt 2.mp4", "2", "A-K"),
    _law_spec("vikeplikt_7_2b", "7.2b vikeplikt punt 2.mp4", "2", "B"),
    _law_spec("vikeplikt_7_3", "7.3 vikeplikt punt 3.mp4", "3"),
    _law_spec("vikeplikt_7_4", "7.4 vikeplikt punt 4.mp4", "4"),
    _law_spec(
        "vikeplikt_7_4a_utkjoring",
        "7.4a vikeplikt for all trafikk ved utkjøring fra privat, punt 4.mp4",
        "4",
        title=_localized(
            "Vikeplikt ved utkjøring fra privat område",
            "การให้ทางเมื่อออกจากพื้นที่ส่วนบุคคล",
            "Right-of-way when leaving private property",
        ),
        caption=_localized(
            "Du har vikeplikt for all trafikk når du kjører ut fra privat område.",
            "คุณต้องให้ทางแก่การจราจรทั้งหมดเมื่อขับออกจากพื้นที่ส่วนบุคคล",
            "You must give way to all traffic when leaving private property.",
        ),
        extra_tags=("utkjøring", "privat_område"),
    ),
    _law_spec(
        "vikeplikt_7_5a_buss",
        "7.5a vikeplikt punt 6_bussregel.mp4",
        "5",
        title=_localized(
            "Bussregelen – vikeplikt ved 60 km/t eller lavere",
            "กฎรถโดยสารประจำทาง – ต้องให้ทางที่ 60 กม./ชม. หรือต่ำกว่า",
            "The bus rule – give way at 60 km/h or lower",
        ),
        caption=_localized(
            "Ved 60 km/t eller lavere skal du gi bussen mulighet til å kjøre ut fra holdeplassen.",
            "ที่ความเร็ว 60 กม./ชม. หรือต่ำกว่า คุณต้องเปิดทางให้รถโดยสารประจำทางออกจากป้าย",
            "At 60 km/h or lower, you must let the bus leave the bus stop.",
        ),
        extra_tags=("bussregelen", "vikeplikt_buss", "60_km_t"),
    ),
    _law_spec(
        "vikeplikt_7_5b_buss_70",
        "7.5b ikke  vikeplikt punt 6_bussregel.mp4",
        "5",
        title=_localized(
            "Bussregelen – særregelen gjelder ikke ved 70 km/t eller høyere",
            "กฎรถโดยสารประจำทาง – กฎพิเศษไม่ใช้ที่ 70 กม./ชม. หรือสูงกว่า",
            "The bus rule – the special rule does not apply at 70 km/h or higher",
        ),
        caption=_localized(
            "Ved 70 km/t eller høyere gjelder ikke den særlige vikeplikten, men du må fortsatt kjøre aktsomt.",
            "ที่ 70 กม./ชม. หรือสูงกว่า กฎการให้ทางพิเศษนี้ไม่ใช้ แต่คุณยังต้องขับอย่างระมัดระวัง",
            "At 70 km/h or higher the special duty to give way does not apply, but you must still drive carefully.",
        ),
        extra_tags=("bussregelen", "70_km_t"),
    ),
    _law_spec("vikeplikt_7_6", "7.6 vikeplikt punt 6.mp4", "6"),
    _law_spec(
        "vikeplikt_oversikt",
        "norwegian_traffic_instructor.mp4",
        "1–6",
        title=_localized(
            "Vikeplikt – oversikt med Michael",
            "การให้ทาง – ภาพรวมกับไมเคิล",
            "Right-of-way – overview with Michael",
        ),
        caption=_localized(
            "En kort visuell oversikt over vikepliktsreglene.",
            "ภาพรวมแบบภาพสั้น ๆ ของกฎการให้ทาง",
            "A short visual overview of the right-of-way rules.",
        ),
    ),
    _distance_spec("bremselengde_40", "braking_40 km h.mp4", "braking", 40),
    _distance_spec("bremselengde_80", "braking_80 km h.mp4", "braking", 80),
    _distance_spec("reaksjonslengde_40", "reaction_distance 40km h.mp4", "reaction", 40),
    _distance_spec("reaksjonslengde_80", "reaction_distance 80km h.mp4", "reaction", 80, "A"),
    _distance_spec("reaksjonslengde_80_b", "Reactions_distance 80.mp4", "reaction", 80, "B"),
    _distance_spec("stoppelengde_40", "stopping_distance_40km h.mp4", "stopping", 40),
    _distance_spec("stoppelengde_80", "stopping_distance_80km h.mp4", "stopping", 80),
    _distance_spec("tesla_bremsing_40_a", "tesla_braking_40km y.mp4", "braking", 40, "Tesla A"),
    _distance_spec("tesla_bremsing_40_b", "tesla_braking_distance 40km h.mp4", "braking", 40, "Tesla B"),
    _distance_spec("tesla_bremsing_80", "tesla_braking_distance 80km h.mp4", "braking", 80, "Tesla"),
    _distance_spec("tesla_reaksjonslengde_40", "tesla_reaction_distance 40km h.mp4", "reaction", 40, "Tesla"),
    _distance_spec("tesla_reaksjonslengde_80", "tesla_reaction_distance_80km h.mp4", "reaction", 80, "Tesla"),
    _distance_spec("tesla_reaksjonslengde_visuell", "tesla_reaction_distance_visualization.mp4", "reaction", None, "Tesla"),
    _distance_spec("tesla_stoppelengde_80", "tesla_stopping_distance_80km h.mp4", "stopping", 80, "Tesla"),
)


EXCLUDED_DUPLICATES = {
    "car_yielding_cyclist.mp4": "7.3 vikeplikt punt 3.mp4",
}


def source_path(workspace: Path, spec: VideoSpec) -> Path:
    return workspace / spec.source_dir / spec.source_name


def learning_video_document(spec: VideoSpec, *, publish: bool = False) -> dict:
    return {
        "id": spec.video_id,
        "title_no": spec.titles["no"],
        "title_th": spec.titles["th"],
        "title_en": spec.titles["en"],
        "youtube_url": "",
        "file_path": f"/public_assets/{spec.asset_name}",
        "thumbnail_url": f"/api/assets/thumbs/{spec.thumbnail_name}",
        "duration_seconds": 10,
        "language": "no",
        "audio_language": "no",
        "learner_languages": list(spec.learner_languages),
        "subtitle_tracks": [{
            "lang": "th",
            "label": "ไทย",
            "url": f"/api/assets/subtitles/{spec.subtitle_name}",
        }],
        "category": spec.category,
        "speed_limit": spec.speed_limit,
        "topic_tags": list(spec.topic_tags),
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "",
        "understand_context": "",
        "choose_context": "",
        "instructor_summary_no": spec.captions["no"],
        "instructor_summary_th": spec.captions["th"],
        "instructor_summary_en": spec.captions["en"],
        "active": publish,
        "import_source": "michael_video_patch_a_2026_09_05",
    }


def michael_material_document(spec: VideoSpec, *, publish: bool = False) -> dict:
    return {
        "id": spec.material_id,
        "type": "video",
        "source_id": spec.video_id,
        "source_url": f"/api/assets/{spec.asset_name}",
        "title": dict(spec.titles),
        "caption": dict(spec.captions),
        "topic_tags": list(spec.topic_tags),
        "sign_ids": [],
        "situation_tags": list(spec.topic_tags),
        "active": publish,
        "approved_for_michael": publish,
        "priority": 40,
        "import_source": "michael_video_patch_a_2026_09_05",
    }
