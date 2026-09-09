"""Deterministic multilingual retrieval phrases for Michael's bundled media.

``michael_material_document`` folds these into every ``michael_materials``
record.  Downstream, ``teacher_chat._get_relevant_michael_materials`` matches
each phrase as a plain *normalized substring* of the student's message and adds
a large score (weight 5000) on a hit, so the entries here decide which of the
25 video sets — plus the curated right-hand-rule image — Michael surfaces.

Rules the lists follow, because nothing downstream is forgiving:

* Lower-case, single-spaced, punctuation already stripped the way
  ``_normalize_material_match_text`` would: ``§ 7 nr. 5`` -> ``7 nr 5``,
  ``60 km/t`` -> ``60 km t``.  Never rely on characters that normalization
  turns into spaces.
* No stemming happens anywhere, so inflected Norwegian forms
  (``bussregel`` / ``bussregelen``) and keyboard-folded forms
  (``hoyreregel`` for ``høyreregel``) are listed explicitly.
* No bare digits or single generic words that would substring-match unrelated
  messages (``7``, ``buss``, ``bus``, ``skilt``).  Every phrase carries its own
  topic.
* The three languages share one list per slug: language purity is enforced
  later by ``_material_lang_value`` (the card is only shown if the material has
  a title+caption in the active language) and by ``learner_languages`` on the
  video, so a cross-language key never leaks foreign text into a reply.
"""
from __future__ import annotations


# ── The 25 imported video sets ──────────────────────────────────────────────
MEDIA_MATCH_PHRASES: dict[str, list[str]] = {
    # § 7 nr. 1 — general duty to give way. Content is a generic illustration,
    # so only paragraph-anchored and unambiguous "who gives way" phrases.
    "vikeplikt_7_1a": [
        "vikeplikt nr 1", "vikeplikt punkt 1", "paragraf 7 nr 1", "7 nr 1",
        "hvem har vikeplikt", "hvem skal vike", "vise vikeplikt",
        "give way section 7 no 1", "who has to give way", "who gives way",
        "การให้ทางมาตรา 7 ข้อ 1", "ใครต้องให้ทาง",
    ],
    # § 7 nr. 2 — right-hand rule at equal-priority junctions.
    "vikeplikt_7_2a": [
        "vikeplikt nr 2", "paragraf 7 nr 2", "7 nr 2",
        "hoyreregel", "hoyreregelen", "høyreregel", "høyreregelen",
        "vike for hoyre", "vike for høyre", "vikeplikt for hoyre",
        "vikeplikt for høyre", "bil fra hoyre", "bil fra høyre",
        "kommer fra hoyre", "kommer fra høyre", "vikeplikt i kryss",
        "right hand rule", "right-hand rule", "give way to the right",
        "yield to the right", "traffic from the right",
        "กฎให้ทางด้านขวา", "ให้ทางรถทางขวา", "รถมาจากทางขวา", "กฎมือขวา",
    ],
    # § 7 nr. 2 variant — unsigned crossing.
    "vikeplikt_7_2ak": [
        "kryss uten skilt", "uskiltet kryss", "likeverdig kryss",
        "hvem kjorer forst i kryss", "hvem kjører først i kryss",
        "hoyreregel i kryss uten skilt", "høyreregel i kryss uten skilt",
        "unmarked intersection", "junction without signs",
        "uncontrolled junction", "who goes first at a junction",
        "ทางแยกไม่มีป้าย", "ใครไปก่อนที่สี่แยก",
    ],
    # § 7 nr. 2 variant — exception to the right-hand rule.
    "vikeplikt_7_2b": [
        "unntak hoyreregelen", "unntak høyreregelen",
        "nar gjelder ikke hoyreregelen", "når gjelder ikke høyreregelen",
        "forkjorsveg", "forkjørsveg", "forkjorsvei", "forkjørsvei",
        "vikepliktskilt", "skilt vikeplikt",
        "exception to the right hand rule",
        "when the right hand rule does not apply", "priority road",
        "ข้อยกเว้นกฎด้านขวา", "ถนนสายหลัก", "ป้ายให้ทาง",
    ],
    # § 7 nr. 3 — give way to crossing cyclists (EXCLUDED_DUPLICATES ties the
    # source clip to a cyclist scene).
    "vikeplikt_7_3": [
        "vikeplikt nr 3", "paragraf 7 nr 3", "7 nr 3",
        "vikeplikt syklist", "vike for syklist", "syklist i kryss",
        "sykkel vikeplikt", "kryssende sykkel",
        "give way to cyclist", "yield to cyclist", "cyclist crossing",
        "ให้ทางจักรยาน", "รถจักรยานข้ามถนน", "คนขี่จักรยาน",
    ],
    # § 7 nr. 4 — give way to all traffic when entering a road.
    "vikeplikt_7_4": [
        "vikeplikt nr 4", "paragraf 7 nr 4", "7 nr 4",
        "vikeplikt for all trafikk", "kjore ut pa veg", "kjøre ut på veg",
        "vegs ende", "veis ende",
        "give way to all traffic", "entering a road", "pulling out onto the road",
        "มาตรา 7 ข้อ 4", "ให้ทางแก่รถทุกคัน", "ออกสู่ถนน",
    ],
    # § 7 nr. 4 — leaving private property. Clear, distinct content.
    "vikeplikt_7_4a_utkjoring": [
        "utkjoring privat", "utkjøring privat", "utkjoring fra privat omrade",
        "utkjøring fra privat område", "privat omrade", "privat område",
        "vikeplikt utkjoring", "vikeplikt utkjøring",
        "kjore ut fra gardsplass", "kjøre ut fra gårdsplass",
        "ut fra innkjorsel", "ut fra innkjørsel", "ut fra parkeringsplass",
        "ut fra bensinstasjon", "ut fra eiendom", "gagate", "gågate", "gatetun",
        "vikeplikt for all trafikk ved utkjoring",
        "vikeplikt for all trafikk ved utkjøring",
        "leaving private property", "exiting private property",
        "driving out of a driveway", "leaving a car park",
        "leaving a parking lot", "leaving a petrol station",
        "leaving a gas station", "private road exit",
        "ออกจากพื้นที่ส่วนบุคคล", "ขับออกจากบ้าน", "ออกจากลานจอดรถ",
        "ออกจากปั๊มน้ำมัน", "ทางเข้าบ้าน", "ถนนส่วนบุคคล",
    ],
    # § 7 nr. 5 — the bus rule at 60 km/h or lower. The reported failure case.
    "vikeplikt_7_5a_buss": [
        "bussregel", "bussregelen", "buss regel", "buss regelen",
        "vikeplikt buss", "vikeplikt for buss", "vike for buss",
        "vike for bussen", "slippe ut buss", "slippe bussen ut",
        "buss fra holdeplass", "bussen kjorer ut", "bussen kjører ut",
        "bussholdeplass", "busslomme", "holdeplass", "holdeplassen",
        "60 km t", "60 sone", "paragraf 7 nr 5", "7 nr 5",
        "bus rule", "the bus rule", "give way to bus", "give way to the bus",
        "yield to bus", "let the bus out", "bus leaving the bus stop",
        "bus pulling out", "bus stop", "bus bay",
        "กฎรถบัส", "กฎรถโดยสาร", "กฎรถโดยสารประจำทาง", "ให้ทางรถบัส",
        "การให้ทางรถบัส", "รถบัสออกจากป้าย", "รถเมล์ออกจากป้าย",
        "ป้ายรถเมล์", "ป้ายรถประจำทาง", "ช่องจอดรถบัส",
    ],
    # § 7 nr. 5 — the special rule does NOT apply at 70 km/h or higher.
    "vikeplikt_7_5b_buss_70": [
        "bussregel 70", "bussregelen 70", "ikke vikeplikt buss",
        "nar gjelder ikke bussregelen", "når gjelder ikke bussregelen",
        "unntak bussregelen", "70 km t", "70 sone", "buss hoy fart",
        "buss høy fart", "buss landeveg", "buss landevei",
        "bus rule does not apply", "exception to the bus rule",
        "no duty to give way to bus", "70 km h", "bus on a fast road",
        "กฎรถบัส 70", "ไม่ต้องให้ทางรถบัส", "ข้อยกเว้นกฎรถบัส",
    ],
    # § 7 nr. 6.
    "vikeplikt_7_6": [
        "vikeplikt nr 6", "vikeplikt punkt 6", "paragraf 7 nr 6", "7 nr 6",
        "right of way rule 6", "section 7 no 6", "มาตรา 7 ข้อ 6",
    ],
    # Overview clip covering § 7 nr. 1–6.
    "vikeplikt_oversikt": [
        "vikeplikt oversikt", "oversikt vikeplikt", "alle vikepliktregler",
        "vikepliktreglene", "forklar vikeplikt", "vikeplikt sammendrag",
        "vikeplikt generelt", "hele paragraf 7",
        "right of way overview", "overview of give way rules",
        "all give way rules", "explain right of way", "right of way summary",
        "ภาพรวมการให้ทาง", "สรุปการให้ทาง", "กฎการให้ทางทั้งหมด",
        "อธิบายการให้ทาง",
    ],

    # ── Reaction / braking / stopping distance ──────────────────────────────
    # Generic concept words live in EXTRA_TOPIC_TAGS (weight 100); the
    # phrases below are speed/vehicle qualified (weight 5000) so a query that
    # names a speed resolves to exactly one clip.
    "bremselengde_40": [
        "bremselengde 40", "bremselengde ved 40", "bremseveg 40", "bremsevei 40",
        "bremse i 40", "braking distance 40", "brake distance 40",
        "ระยะเบรก 40", "ระยะเบรกที่ 40",
    ],
    "bremselengde_80": [
        "bremselengde 80", "bremselengde ved 80", "bremseveg 80", "bremsevei 80",
        "bremse i 80", "braking distance 80", "brake distance 80",
        "ระยะเบรก 80", "ระยะเบรกที่ 80",
    ],
    "reaksjonslengde_40": [
        "reaksjonslengde 40", "reaksjonsveg 40", "reaksjonsvei 40",
        "reaksjonstid 40", "reaction distance 40", "reaction time 40",
        "ระยะตอบสนอง 40", "ระยะปฏิกิริยา 40",
    ],
    "reaksjonslengde_80": [
        "reaksjonslengde 80", "reaksjonsveg 80", "reaksjonsvei 80",
        "reaksjonstid 80", "reaction distance 80", "reaction time 80",
        "ระยะตอบสนอง 80", "ระยะปฏิกิริยา 80",
    ],
    "reaksjonslengde_80_b": [
        "reaksjonslengde 80 variant b", "reaksjonslengde 80 alternativ",
        "reaction distance 80 variant b",
    ],
    "stoppelengde_40": [
        "stoppelengde 40", "stopplengde 40", "stoppelengde ved 40",
        "stoppestrekning 40", "stopping distance 40", "how far to stop at 40",
        "ระยะหยุด 40", "ระยะหยุดรถ 40",
    ],
    "stoppelengde_80": [
        "stoppelengde 80", "stopplengde 80", "stoppelengde ved 80",
        "stoppestrekning 80", "stopping distance 80", "how far to stop at 80",
        "ระยะหยุด 80", "ระยะหยุดรถ 80",
    ],
    "tesla_bremsing_40_a": [
        "tesla bremselengde 40", "tesla bremsing 40", "tesla bremser i 40",
        "elbil bremselengde 40", "tesla braking distance 40",
        "เทสลา ระยะเบรก 40",
    ],
    "tesla_bremsing_40_b": [
        "tesla bremselengde 40 variant b", "tesla braking distance 40 variant b",
    ],
    "tesla_bremsing_80": [
        "tesla bremselengde 80", "tesla bremsing 80", "tesla bremser i 80",
        "elbil bremselengde 80", "tesla braking distance 80",
        "เทสลา ระยะเบรก 80",
    ],
    "tesla_reaksjonslengde_40": [
        "tesla reaksjonslengde 40", "tesla reaksjonstid 40",
        "tesla reaction distance 40", "เทสลา ระยะตอบสนอง 40",
    ],
    "tesla_reaksjonslengde_80": [
        "tesla reaksjonslengde 80", "tesla reaksjonstid 80",
        "tesla reaction distance 80", "เทสลา ระยะตอบสนอง 80",
    ],
    "tesla_reaksjonslengde_visuell": [
        "tesla reaksjonslengde visualisering", "reaksjonslengde visualisert",
        "reaksjonslengde animasjon", "reaksjonslengde ulike hastigheter",
        "reaksjonslengde forskjellige farter", "sammenlign reaksjonslengde",
        "reaction distance visualization", "reaction distance animation",
        "reaction distance at different speeds", "compare reaction distance",
        "ภาพจำลองระยะตอบสนอง", "เปรียบเทียบระยะตอบสนอง",
    ],
    "tesla_stoppelengde_80": [
        "tesla stoppelengde 80", "tesla stopplengde 80", "tesla stopper i 80",
        "elbil stoppelengde 80", "tesla stopping distance 80",
        "เทสลา ระยะหยุด 80",
    ],
}


# Concept-level words (weight 100 via topic_tags): they broaden recall for
# un-qualified questions without overriding a speed-qualified phrase hit.
EXTRA_TOPIC_TAGS: dict[str, list[str]] = {
    "bremselengde_40": ["bremselengde", "bremseveg", "bremsevei", "braking distance", "ระยะเบรก"],
    "bremselengde_80": ["bremselengde", "bremseveg", "bremsevei", "braking distance", "ระยะเบรก"],
    "reaksjonslengde_40": ["reaksjonslengde", "reaksjonsveg", "reaksjonsvei", "reaksjonstid", "reaction distance", "ระยะตอบสนอง"],
    "reaksjonslengde_80": ["reaksjonslengde", "reaksjonsveg", "reaksjonsvei", "reaksjonstid", "reaction distance", "ระยะตอบสนอง"],
    "reaksjonslengde_80_b": ["reaksjonslengde", "reaction distance", "ระยะตอบสนอง"],
    "stoppelengde_40": ["stoppelengde", "stopplengde", "stoppestrekning", "stopping distance", "ระยะหยุด"],
    "stoppelengde_80": ["stoppelengde", "stopplengde", "stoppestrekning", "stopping distance", "ระยะหยุด"],
    "tesla_bremsing_40_a": ["bremselengde", "tesla", "elbil", "braking distance"],
    "tesla_bremsing_40_b": ["bremselengde", "tesla", "elbil", "braking distance"],
    "tesla_bremsing_80": ["bremselengde", "tesla", "elbil", "braking distance"],
    "tesla_reaksjonslengde_40": ["reaksjonslengde", "reaksjonstid", "tesla", "reaction distance"],
    "tesla_reaksjonslengde_80": ["reaksjonslengde", "reaksjonstid", "tesla", "reaction distance"],
    "tesla_reaksjonslengde_visuell": ["reaksjonslengde", "tesla", "reaction distance"],
    "tesla_stoppelengde_80": ["stoppelengde", "tesla", "elbil", "stopping distance"],
    "vikeplikt_7_4a_utkjoring": ["utkjoring", "utkjøring", "privat", "smal veg", "smal vei"],
    "vikeplikt_7_5a_buss": ["buss", "holdeplass", "bussregel", "bussregelen"],
}


# ── Curated non-video materials seeded alongside the 25 sets ────────────────
# Folds the previous stand-alone right-hand-rule linker into the single
# migration path so every topic ships through one mechanism.
EXTRA_MATERIALS: tuple[dict, ...] = (
    {
        "id": "sit_kryss_hoyreregel_7",
        "type": "intersection_image",
        "source_id": "",
        "source_url": "/api/assets/michael_hoyreregel.svg",
        "static_url": "",
        "thumbnail_url": "/api/assets/michael_hoyreregel.svg",
        "title": {
            "no": "Høyreregelen i et kryss uten skilt",
            "th": "กฎให้ทางแก่รถจากขวาที่ทางแยกไม่มีป้าย",
            "en": "The right-hand rule at an unsigned intersection",
        },
        "caption": {
            "no": (
                "I et likeverdig kryss der ingen skilt, signaler eller andre "
                "regler bestemmer, har du vikeplikt for kjøretøy som kommer fra "
                "høyre (Trafikkreglene § 7 nr. 2)."
            ),
            "th": (
                "ที่ทางแยกซึ่งถนนมีลำดับความสำคัญเท่ากัน และไม่มีป้าย สัญญาณไฟ "
                "หรือกฎอื่นกำหนดสิทธิ์ทาง คุณต้องให้ทางแก่รถที่มาจากด้านขวา "
                "(กฎจราจร มาตรา 7 ข้อ 2)"
            ),
            "en": (
                "At an equal-priority intersection where no sign, signal, or "
                "other rule decides, you must yield to vehicles approaching "
                "from the right (Traffic Rules § 7(2))."
            ),
        },
        "language": "no",
        "learner_languages": ["no", "th", "en"],
        "category": "vikeplikt",
        "topic_tags": [
            "7_2", "vikeplikt", "hoyreregel", "høyreregel", "hoyreregelen",
            "høyreregelen", "right-hand rule", "การให้ทาง",
        ],
        "situation_tags": ["kryss", "uskiltet kryss", "intersection"],
        "match_phrases": [
            "hoyreregel", "hoyreregelen", "høyreregel", "høyreregelen",
            "vike for hoyre", "vike for høyre", "hoyreregel i kryss",
            "høyreregel i kryss", "bil fra hoyre", "bil fra høyre",
            "kommer fra hoyre", "kommer fra høyre",
            "right hand rule", "right-hand rule", "give way to the right",
            "yield to the right", "traffic from the right",
            "กฎให้ทางด้านขวา", "ให้ทางรถทางขวา", "รถมาจากทางขวา", "กฎมือขวา",
        ],
        "sign_ids": [],
        "priority": 10,
    },
)


def phrases_for(slug: str) -> list[str]:
    """Return the de-duplicated match phrases for one video slug."""
    seen: dict[str, None] = {}
    for phrase in MEDIA_MATCH_PHRASES.get(slug, ()):
        key = " ".join(str(phrase).split()).casefold()
        if key:
            seen.setdefault(key, None)
    return list(seen)


def extra_topic_tags_for(slug: str) -> list[str]:
    """Return concept-level tags to append to a video slug's topic_tags."""
    return list(EXTRA_TOPIC_TAGS.get(slug, ()))
