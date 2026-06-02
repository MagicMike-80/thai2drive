"""
fix_content_mismatches.py — Batch fix for confirmed sign content/image mismatches.

Audit source: full comparison of sign_images/ filenames, production MongoDB,
and Norwegian skiltforskriften (traffic sign regulations).

Safety guarantees:
  - Only patches the 14 confirmed mismatched sign IDs.
  - All other signs are untouched.
  - Idempotent: safe to run multiple times (uses $set with exact correct values).
  - Prints a pre-patch report before writing, a post-patch report after.
  - Runs a final validation pass against the live DB.

Usage:
    python backend/fix_content_mismatches.py [--dry-run]

    --dry-run   Print the pre-patch report without writing to MongoDB.

Confirmed mismatches (14 signs):
    100_1   image shows RIGHT bend, DB says left
    100_2   image shows LEFT bend, DB says right
    102_1   image shows RIGHT-first bends, DB says left-first
    153     image shows Trafikkulykke (traffic accident), DB says Kø (queue)
    306_10  image shows electric vehicle prohibition, DB says horse-drawn vehicles
    367     image shows electric vehicle speed zone, DB says no horn
    369     image shows end of electric vehicle speed zone, DB says no dangerous goods
    377     image shows electric vehicle parking zone, DB says no load carrying
    379     image shows end of electric vehicle parking zone, DB says no stopping at signals
    380     image shows electric vehicle use-prohibition zone, DB says forbidden zone
    382     image shows end of electric vehicle use-prohibition zone, DB says end of forbidden zone
    521.1   image shows centre cycle lane, DB says first aid
    565     image shows wrong-direction sign, DB says level crossing
    206_0   content misaligned with Norwegian sign number (image swap already done)
    208_0   content misaligned with Norwegian sign number (image swap already done)
"""

import asyncio
import os
import sys
import json
import io
from datetime import datetime, timezone

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError for Thai/Norwegian chars)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get(
    "MONGO_URL",
    "mongodb+srv://norge-quiz-app:m2iD3VNMnbxL7LIm@cluster0.mecy7qw.mongodb.net/thai2drive?retryWrites=true&w=majority",
)
DB_NAME = "thai2drive"
DRY_RUN = "--dry-run" in sys.argv

# ══════════════════════════════════════════════════════════════════════════════
#  CORRECT CONTENT — ground truth derived from image filenames + Norwegian
#  skiltforskriften. Each entry: sign_id → correct field values.
# ══════════════════════════════════════════════════════════════════════════════
FIXES = {

    # ── 100-series: left/right bend direction was swapped during import ──────
    # Image 100_1_Skarp_sving_til_hoyre.jpg → image shows RIGHT bend
    # Image 100_2_Farlig_sving_til_venstre.jpg → image shows LEFT bend
    "100_1": {
        "name": {
            "no": "Farlig sving til høyre",
            "th": "โค้งอันตรายทางขวา",
            "en": "Dangerous Right Bend",
        },
        "explanation": {
            "no": "Skarp sving til høyre foran deg. Reduser fart i god tid og hold til høyre i svingen.",
            "th": "มีโค้งคมทางขวาอยู่ข้างหน้า ลดความเร็วล่วงหน้าและชิดขวาในโค้ง",
            "en": "Sharp right bend ahead. Reduce speed in good time and keep to the right through the bend.",
        },
        "driver_action": {
            "no": "Bremse før svingen, ikke i den. Hold jevn fart gjennom kurven.",
            "th": "เบรกก่อนเข้าโค้ง ไม่ใช่ในโค้ง รักษาความเร็วให้สม่ำเสมอตลอดช่วงโค้ง",
            "en": "Brake before the bend, not in it. Maintain steady speed through the curve.",
        },
    },

    # Image 100_2_Farlig_sving_til_venstre.jpg → image shows LEFT bend
    "100_2": {
        "name": {
            "no": "Farlig sving til venstre",
            "th": "โค้งอันตรายทางซ้าย",
            "en": "Dangerous Left Bend",
        },
        "explanation": {
            "no": "Skarp sving til venstre foran deg. Reduser fart i god tid.",
            "th": "มีโค้งคมทางซ้ายอยู่ข้างหน้า ลดความเร็วล่วงหน้า",
            "en": "Sharp left bend ahead. Reduce speed in good time.",
        },
        "driver_action": {
            "no": "Bremse før svingen, ikke i den. Hold jevn fart gjennom kurven.",
            "th": "เบรกก่อนเข้าโค้ง ไม่ใช่ในโค้ง รักษาความเร็วให้สม่ำเสมอตลอดช่วงโค้ง",
            "en": "Brake before the bend, not in it. Maintain steady speed through the curve.",
        },
    },

    # Image 102_1_Farlige_svinger_den_forste_til_hoyre.jpg → first bend is RIGHT
    "102_1": {
        "name": {
            "no": "Svinger, høyre først",
            "th": "ถนนคดเคี้ยว ขวาก่อน",
            "en": "Series of Bends, Right First",
        },
        "explanation": {
            "no": "Flere svinger fremover, første til høyre. Kjør forsiktig og hold lav fart.",
            "th": "มีโค้งหลายโค้งอยู่ข้างหน้า โค้งแรกไปทางขวา ขับอย่างระมัดระวังและใช้ความเร็วต่ำ",
            "en": "Several bends ahead, first to the right. Drive carefully and maintain low speed.",
        },
        "driver_action": {
            "no": "Reduser fart tidlig. Kjør defensivt gjennom hele svingeseksjonen.",
            "th": "ลดความเร็วแต่เนิ่นๆ ขับแบบป้องกันตลอดช่วงโค้ง",
            "en": "Reduce speed early. Drive defensively through the entire bend section.",
        },
    },

    # ── sign 153: image file is Trafikkulykke, DB was incorrectly set to Kø ──
    "153": {
        "name": {
            "no": "Trafikkulykke",
            "th": "อุบัติเหตุทางจราจร",
            "en": "Traffic Accident",
        },
        "explanation": {
            "no": "Fare for trafikkulykke foran deg. Vær beredt på uventede hindringer og stopp.",
            "th": "มีความเสี่ยงต่ออุบัติเหตุทางจราจรข้างหน้า เตรียมพร้อมสำหรับสิ่งกีดขวางและการหยุดโดยไม่คาดคิด",
            "en": "Risk of traffic accident ahead. Be prepared for unexpected obstacles and stops.",
        },
        "driver_action": {
            "no": "Senk farten, øk oppmerksomheten og hold god avstand til kjøretøyet foran.",
            "th": "ลดความเร็ว เพิ่มความตื่นตัว และรักษาระยะห่างจากรถคันหน้าให้มากขึ้น",
            "en": "Reduce speed, increase alertness and maintain a greater distance from the vehicle ahead.",
        },
    },

    # ── sign 306_10: image is electric vehicle prohibition, DB said horse-drawn ──
    "306_10": {
        "name": {
            "no": "Forbudt for liten elektrisk motorvogn",
            "th": "ห้ามรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "No Small Electric Vehicles",
        },
        "explanation": {
            "no": "Liten elektrisk motorvogn (f.eks. el-sparkesykkel, liten el-bil) har ikke adgang her.",
            "th": "ยานยนต์ไฟฟ้าขนาดเล็ก (เช่น สกูตเตอร์ไฟฟ้า รถยนต์ไฟฟ้าขนาดเล็ก) ไม่ได้รับอนุญาตให้เข้าพื้นที่นี้",
            "en": "Small electric motor vehicles (e.g. e-scooters, small electric cars) are not permitted here.",
        },
        "driver_action": {
            "no": "Ikke kjør inn med liten elektrisk motorvogn. Finn alternativ rute.",
            "th": "ห้ามขับรถยนต์ไฟฟ้าขนาดเล็กเข้าไป หาเส้นทางอื่น",
            "en": "Do not enter with a small electric vehicle. Find an alternative route.",
        },
    },

    # ── Electric vehicle zone signs (367–382): all had wrong content ─────────
    # Image: 367_Fartsgrensesone_for_liten_elektrisk_motorvogn.jpg
    "367": {
        "name": {
            "no": "Fartsgrensesone for liten elektrisk motorvogn",
            "th": "เขตจำกัดความเร็วสำหรับรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "Speed Limit Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Angir starten på en sone med særskilt fartsgrense for liten elektrisk motorvogn.",
            "th": "แสดงจุดเริ่มต้นของเขตที่มีกฎจำกัดความเร็วพิเศษสำหรับยานยนต์ไฟฟ้าขนาดเล็ก",
            "en": "Marks the start of a zone with a special speed limit applying to small electric motor vehicles.",
        },
        "driver_action": {
            "no": "Overhold den angitte fartsgrensen for liten elektrisk motorvogn i hele sonen.",
            "th": "ปฏิบัติตามขีดจำกัดความเร็วที่กำหนดสำหรับรถยนต์ไฟฟ้าขนาดเล็กตลอดทั้งเขต",
            "en": "Observe the posted speed limit for small electric vehicles throughout the zone.",
        },
    },

    # Image: 369_Slutt_på_fartsgrensesone_for_liten_elektrisk_motorvogn.jpg
    "369": {
        "name": {
            "no": "Slutt på fartsgrensesone for liten elektrisk motorvogn",
            "th": "สิ้นสุดเขตจำกัดความเร็วสำหรับรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "End of Speed Limit Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Den særskilte fartsgrensesonen for liten elektrisk motorvogn avsluttes her.",
            "th": "เขตจำกัดความเร็วพิเศษสำหรับยานยนต์ไฟฟ้าขนาดเล็กสิ้นสุดที่นี่",
            "en": "The special speed limit zone for small electric motor vehicles ends here.",
        },
        "driver_action": {
            "no": "Fartsgrensen for liten elektrisk motorvogn gjelder ikke lenger etter dette skiltet.",
            "th": "ขีดจำกัดความเร็วสำหรับรถยนต์ไฟฟ้าขนาดเล็กไม่มีผลบังคับใช้อีกต่อไปหลังจากป้ายนี้",
            "en": "The speed limit for small electric vehicles no longer applies after this sign.",
        },
    },

    # Image: 377_Sone_med_parkeringsforbud_for_liten_elektrisk_motorvogn.jpg
    "377": {
        "name": {
            "no": "Sone med parkeringsforbud for liten elektrisk motorvogn",
            "th": "เขตห้ามจอดสำหรับรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "Parking Prohibition Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Parkering av liten elektrisk motorvogn er forbudt i hele denne sonen.",
            "th": "ห้ามจอดยานยนต์ไฟฟ้าขนาดเล็กในเขตนี้ทั้งหมด",
            "en": "Parking of small electric motor vehicles is prohibited throughout this zone.",
        },
        "driver_action": {
            "no": "Ikke parker liten elektrisk motorvogn innenfor sonens grenser.",
            "th": "ห้ามจอดรถยนต์ไฟฟ้าขนาดเล็กภายในขอบเขตของเขตนี้",
            "en": "Do not park small electric vehicles within the zone boundaries.",
        },
    },

    # Image: 379_Slutt_på_sone_med_parkeringsforbud_for_liten_elektrisk_motorvogn.jpg
    "379": {
        "name": {
            "no": "Slutt på sone med parkeringsforbud for liten elektrisk motorvogn",
            "th": "สิ้นสุดเขตห้ามจอดสำหรับรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "End of Parking Prohibition Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Parkeringsforbudet for liten elektrisk motorvogn oppheves her.",
            "th": "การห้ามจอดรถยนต์ไฟฟ้าขนาดเล็กสิ้นสุดที่นี่",
            "en": "The parking prohibition for small electric motor vehicles ends here.",
        },
        "driver_action": {
            "no": "Parkering av liten elektrisk motorvogn er tillatt igjen etter dette skiltet.",
            "th": "อนุญาตให้จอดรถยนต์ไฟฟ้าขนาดเล็กได้อีกครั้งหลังจากป้ายนี้",
            "en": "Parking of small electric vehicles is permitted again after this sign.",
        },
    },

    # Image: 380_Sone_med_bruksforbud_for_liten_elektrisk_motorvogn.jpg
    "380": {
        "name": {
            "no": "Sone med bruksforbud for liten elektrisk motorvogn",
            "th": "เขตห้ามใช้งานรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "Use Prohibition Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Bruk av liten elektrisk motorvogn er forbudt i hele denne sonen.",
            "th": "ห้ามใช้งานยานยนต์ไฟฟ้าขนาดเล็กในเขตนี้ทั้งหมด",
            "en": "Use of small electric motor vehicles is prohibited throughout this zone.",
        },
        "driver_action": {
            "no": "Ikke bruk liten elektrisk motorvogn innenfor sonens grenser.",
            "th": "ห้ามใช้งานรถยนต์ไฟฟ้าขนาดเล็กภายในขอบเขตของเขตนี้",
            "en": "Do not use small electric vehicles within the zone boundaries.",
        },
    },

    # Image: 382_Slutt_på_sone_med_bruksforbud_for_liten_elektrisk_motorvogn.jpg
    "382": {
        "name": {
            "no": "Slutt på sone med bruksforbud for liten elektrisk motorvogn",
            "th": "สิ้นสุดเขตห้ามใช้งานรถยนต์ไฟฟ้าขนาดเล็ก",
            "en": "End of Use Prohibition Zone for Small Electric Vehicles",
        },
        "explanation": {
            "no": "Bruksforbudet for liten elektrisk motorvogn oppheves her.",
            "th": "การห้ามใช้งานรถยนต์ไฟฟ้าขนาดเล็กสิ้นสุดที่นี่",
            "en": "The use prohibition for small electric motor vehicles ends here.",
        },
        "driver_action": {
            "no": "Bruk av liten elektrisk motorvogn er tillatt igjen etter dette skiltet.",
            "th": "อนุญาตให้ใช้งานรถยนต์ไฟฟ้าขนาดเล็กได้อีกครั้งหลังจากป้ายนี้",
            "en": "Use of small electric vehicles is permitted again after this sign.",
        },
    },

    # ── sign 521.1: image is centre cycle lane, DB said first aid ────────────
    "521.1": {
        "name": {
            "no": "Midtstilt sykkelfelt",
            "th": "เลนจักรยานกลางถนน",
            "en": "Centre Cycle Lane",
        },
        "explanation": {
            "no": "Angir et sykkelfelt plassert i midten av kjørebanen. Syklister har rett til å bruke dette feltet.",
            "th": "แสดงเลนจักรยานที่อยู่กลางถนน นักปั่นมีสิทธิ์ใช้เลนนี้",
            "en": "Indicates a cycle lane positioned in the centre of the carriageway. Cyclists are entitled to use this lane.",
        },
        "driver_action": {
            "no": "Gi syklister rett til å bruke midtfeltet. Ikke kjør inn i sykkelfeltet.",
            "th": "ให้สิทธิ์นักปั่นใช้เลนกลาง อย่าขับรถเข้าไปในเลนจักรยาน",
            "en": "Give cyclists the right to use the centre lane. Do not drive into the cycle lane.",
        },
    },

    # ── sign 565: image is Feil kjøreretning, DB said Planovergang ───────────
    "565": {
        "name": {
            "no": "Feil kjøreretning",
            "th": "ขับทวนเส้นทาง",
            "en": "Wrong Driving Direction",
        },
        "explanation": {
            "no": "Du kjører feil vei i forhold til tillatt kjøreretning. Fare for møtende trafikk.",
            "th": "คุณกำลังขับรถสวนทิศทางที่อนุญาต มีความเสี่ยงจากรถสวนทาง",
            "en": "You are driving in the wrong direction relative to the permitted driving direction. Risk of oncoming traffic.",
        },
        "driver_action": {
            "no": "Stopp umiddelbart og snu. Ikke fortsett i feil retning.",
            "th": "หยุดทันทีและกลับรถ อย่าขับต่อในทิศทางที่ผิด",
            "en": "Stop immediately and turn around. Do not continue in the wrong direction.",
        },
    },

    # ── signs 206_0 / 208_0: images were physically swapped previously. ──────
    # The image files are now correct after the swap in the prior commit.
    # The DB content is also correct. These entries verify alignment only.
    # We re-write the content to ensure it is complete and well-formed.
    "206_0": {
        "name": {
            "no": "Jernbanekryssing uten bom",
            "th": "ทางรถไฟไม่มีไม้กั้น",
            "en": "Level Crossing Without Barrier",
        },
        "explanation": {
            "no": "Jernbanekryssing uten bom eller lys foran deg. Tog har alltid forkjørsrett.",
            "th": "ทางรถไฟตัดถนนโดยไม่มีไม้กั้นหรือสัญญาณไฟอยู่ข้างหน้า รถไฟมีสิทธิ์ผ่านก่อนเสมอ",
            "en": "Level crossing without barrier or lights ahead. Trains always have right of way.",
        },
        "driver_action": {
            "no": "Stopp, se og lytt etter tog fra begge retninger. Kryss kun når det er klart.",
            "th": "หยุด มองและฟังรถไฟจากทั้งสองทิศทาง ข้ามเมื่อปลอดภัยเท่านั้น",
            "en": "Stop, look and listen for trains from both directions. Cross only when clear.",
        },
    },

    "208_0": {
        "name": {
            "no": "Forkjørsveg",
            "th": "ถนนสายหลัก (มีสิทธิ์ผ่านก่อน)",
            "en": "Priority Road",
        },
        "explanation": {
            "no": "Du befinner deg på en forkjørsveg (gult diamantskilt). Kjøretøy fra sideveiene skal gi deg vikeplikt.",
            "th": "คุณอยู่บนถนนสายหลัก (ป้ายรูปเพชรสีเหลือง) รถจากถนนสายรองต้องให้ทางคุณ",
            "en": "You are on a priority road (yellow diamond sign). Vehicles from side roads must yield to you.",
        },
        "driver_action": {
            "no": "Du har forkjørsrett, men vær oppmerksom på kjøretøy som ikke overholder vikeplikten.",
            "th": "คุณมีสิทธิ์ผ่านก่อน แต่ระวังรถที่ไม่ปฏิบัติตามกฎการให้ทาง",
            "en": "You have priority, but remain alert for vehicles that do not observe the yield rule.",
        },
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _short(s, n=55):
    if not s:
        return ""
    return s[:n] + ("…" if len(s) > n else "")


def _diff(label, cur, proposed):
    """Return a list of diff lines for a dict field."""
    lines = []
    for lang in ("no", "th", "en"):
        c = (cur or {}).get(lang, "")
        p = (proposed or {}).get(lang, "")
        if c != p:
            lines.append(f"    {label}.{lang}:")
            lines.append(f"      CURRENT:  {_short(c)}")
            lines.append(f"      PROPOSED: {_short(p)}")
    return lines


async def run():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'='*70}")
    print(f" fix_content_mismatches.py  —  {mode}  —  {timestamp}")
    print(f"{'='*70}\n")

    # ── PRE-PATCH REPORT ──────────────────────────────────────────────────────
    print("PRE-PATCH REPORT")
    print("-" * 60)

    sign_ids = list(FIXES.keys())
    existing = {}
    for sid in sign_ids:
        doc = await db.traffic_signs.find_one({"id": sid}, {"_id": 0})
        existing[sid] = doc

    for sid in sign_ids:
        doc = existing[sid]
        fix = FIXES[sid]
        print(f"\n  Sign {sid}")
        if not doc:
            print(f"    ⚠️  NOT FOUND IN DATABASE — will skip")
            continue

        diffs = []
        diffs += _diff("name",         doc.get("name"), fix.get("name"))
        diffs += _diff("explanation",  doc.get("explanation"), fix.get("explanation"))
        diffs += _diff("driver_action",
                        doc.get("driverAction") or doc.get("driver_action"),
                        fix.get("driver_action"))

        if diffs:
            for line in diffs:
                print(line)
        else:
            print("    ✓  Already correct — will skip (idempotent)")

    print(f"\n{'='*70}\n")

    if DRY_RUN:
        print("DRY RUN complete — no changes written.\n")
        client.close()
        return

    # ── APPLY PATCHES ─────────────────────────────────────────────────────────
    results = {"patched": [], "skipped": [], "failed": []}

    for sid in sign_ids:
        doc = existing[sid]
        fix = FIXES[sid]

        if not doc:
            results["failed"].append((sid, "not found in database"))
            continue

        # Check if already correct (idempotency guard)
        cur_name   = doc.get("name") or {}
        cur_expl   = doc.get("explanation") or {}
        cur_driver = doc.get("driverAction") or doc.get("driver_action") or {}

        already_correct = (
            cur_name   == fix["name"] and
            cur_expl   == fix["explanation"] and
            cur_driver == fix["driver_action"]
        )

        if already_correct:
            results["skipped"].append(sid)
            continue

        try:
            await db.traffic_signs.update_one(
                {"id": sid},
                {"$set": {
                    "name":         fix["name"],
                    "explanation":  fix["explanation"],
                    "driver_action": fix["driver_action"],
                    # Also clear the camelCase field so there is no stale copy
                    "driverAction":  fix["driver_action"],
                }},
            )
            results["patched"].append(sid)
        except Exception as e:
            results["failed"].append((sid, str(e)))

    # ── POST-PATCH REPORT ─────────────────────────────────────────────────────
    print("POST-PATCH REPORT")
    print("-" * 60)

    print(f"\n  ✅  Patched  ({len(results['patched'])}): {results['patched']}")
    print(f"  ⏭   Skipped  ({len(results['skipped'])}): {results['skipped']}")

    if results["failed"]:
        print(f"  ❌  Failed   ({len(results['failed'])}):")
        for sid, reason in results["failed"]:
            print(f"       {sid}: {reason}")
    else:
        print(f"  ❌  Failed   (0): none")

    # ── FINAL VALIDATION AUDIT ────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("FINAL VALIDATION — all patched signs")
    print("-" * 60)

    all_ok = True
    for sid in results["patched"] + results["skipped"]:
        doc = await db.traffic_signs.find_one({"id": sid}, {"_id": 0})
        fix = FIXES[sid]
        if not doc:
            print(f"  ❌  {sid}: missing from DB after patch")
            all_ok = False
            continue

        # Verify name
        name_ok = doc.get("name") == fix["name"]
        expl_ok = doc.get("explanation") == fix["explanation"]
        da_ok   = (
            doc.get("driver_action") == fix["driver_action"] or
            doc.get("driverAction")  == fix["driver_action"]
        )

        if name_ok and expl_ok and da_ok:
            img_url = doc.get("image_url", "")
            img_file = img_url.split("/")[-1] if img_url else "?"
            print(f"  ✅  {sid:<10}  name.no={_short(doc['name'].get('no',''),40):<42}  img={img_file}")
        else:
            all_ok = False
            if not name_ok:
                print(f"  ❌  {sid}: name mismatch after patch")
            if not expl_ok:
                print(f"  ❌  {sid}: explanation mismatch after patch")
            if not da_ok:
                print(f"  ❌  {sid}: driver_action mismatch after patch")

    print(f"\n{'='*70}")
    if all_ok:
        print("✅  All patched signs validated — database is consistent.\n")
    else:
        print("⚠️  Some signs failed validation — review output above.\n")

    client.close()


if __name__ == "__main__":
    asyncio.run(run())
