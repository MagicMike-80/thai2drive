"""
Traffic Math Engine — Thai2Drive
----------------------------------
Deterministic calculation engine for Norwegian driving theory.
Zero external dependencies. Zero database calls. Zero AI.

All public functions return plain dicts — structured for any
consumer (API, test, future UI component, AI explanation layer).

Norwegian theory standard formulas:
  reaction_distance = speed_ms × reaction_time_s
  braking_distance  = (speed_kmh / 10)² × road_multiplier
  stopping_distance = reaction + braking
  kinetic_energy    ∝ v²  (doubling speed → ×4 energy)
  following_distance = speed_ms × seconds
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


# ─── Road conditions ──────────────────────────────────────────────────────────

ROAD_CONDITIONS: dict[str, dict] = {
    "dry": {
        "key":        "dry",
        "multiplier": 1.0,
        "label":      {"no": "Tørr asfalt",   "th": "ถนนแห้ง",        "en": "Dry asphalt"},
        "note":       {"no": "Normale forhold", "th": "สภาพปกติ",       "en": "Normal conditions"},
    },
    "wet": {
        "key":        "wet",
        "multiplier": 2.0,
        "label":      {"no": "Våt vei",        "th": "ถนนเปียก",        "en": "Wet road"},
        "note":       {"no": "Doblet bremseavstand", "th": "ระยะเบรกเพิ่มเป็น 2 เท่า", "en": "Double braking distance"},
    },
    "snow": {
        "key":        "snow",
        "multiplier": 4.0,
        "label":      {"no": "Snø / is-blandet", "th": "หิมะ/ถนนปน",   "en": "Snow / mixed ice"},
        "note":       {"no": "4× bremseavstand", "th": "ระยะเบรก 4 เท่า", "en": "4× braking distance"},
    },
    "ice": {
        "key":        "ice",
        "multiplier": 8.0,
        "label":      {"no": "Glatt is",       "th": "ถนนน้ำแข็ง",     "en": "Black ice"},
        "note":       {"no": "8× bremseavstand — ekstremt farlig",
                       "th": "ระยะเบรก 8 เท่า — อันตรายมาก",
                       "en": "8× braking distance — extremely dangerous"},
    },
}

DEFAULT_REACTION_TIME_S = 1.0   # seconds (Norwegian theory standard)
CAR_LENGTH_M            = 4.5   # meters  (used in danger-context analogies)
BUS_LENGTH_M            = 12.0
HOUSE_WIDTH_M           = 8.0


# ─── Core maths ───────────────────────────────────────────────────────────────

def kmh_to_ms(speed_kmh: float) -> float:
    """Convert km/h to m/s."""
    return round(speed_kmh / 3.6, 2)


def reaction_distance_m(speed_kmh: float, reaction_time_s: float = DEFAULT_REACTION_TIME_S) -> float:
    """Distance covered during driver reaction (before braking starts)."""
    return round(kmh_to_ms(speed_kmh) * reaction_time_s, 1)


def braking_distance_m(speed_kmh: float, condition: str = "dry") -> float:
    """
    Braking distance using the Norwegian theory formula:
        bremseavstand = (fart ÷ 10)²  (dry road)
    Multiplied by road condition factor for other surfaces.
    """
    multiplier = ROAD_CONDITIONS.get(condition, ROAD_CONDITIONS["dry"])["multiplier"]
    base = (speed_kmh / 10) ** 2
    return round(base * multiplier, 1)


def stopping_distance_m(
    speed_kmh: float,
    condition: str = "dry",
    reaction_time_s: float = DEFAULT_REACTION_TIME_S,
) -> float:
    return round(
        reaction_distance_m(speed_kmh, reaction_time_s)
        + braking_distance_m(speed_kmh, condition),
        1,
    )


# ─── Step-by-step breakdown ───────────────────────────────────────────────────

def _danger_context(distance_m: float) -> dict:
    """
    Translate a stopping distance into relatable real-world comparisons.
    Helps students feel the danger — not just see a number.
    """
    cars  = round(distance_m / CAR_LENGTH_M, 1)
    buses = round(distance_m / BUS_LENGTH_M, 1)
    return {
        "car_lengths":  cars,
        "bus_lengths":  buses,
        "description":  {
            "no": f"Tilsvarer ca. {int(cars)} bilers lengde",
            "th": f"เทียบเท่ารถยนต์ประมาณ {int(cars)} คัน",
            "en": f"Roughly {int(cars)} car lengths",
        },
    }


def stopping_distance_full(
    speed_kmh: float,
    condition: str = "dry",
    reaction_time_s: float = DEFAULT_REACTION_TIME_S,
) -> dict:
    """
    Full calculation breakdown for a given speed + road condition.
    Returns structured data with step-by-step formulas + danger context.
    """
    if speed_kmh <= 0:
        raise ValueError("speed_kmh must be positive")
    if condition not in ROAD_CONDITIONS:
        condition = "dry"

    speed_ms     = kmh_to_ms(speed_kmh)
    react_m      = reaction_distance_m(speed_kmh, reaction_time_s)
    brake_m      = braking_distance_m(speed_kmh, condition)
    stop_m       = round(react_m + brake_m, 1)
    multiplier   = ROAD_CONDITIONS[condition]["multiplier"]
    cond_info    = ROAD_CONDITIONS[condition]

    steps = [
        {
            "order":   1,
            "concept": "speed_conversion",
            "label":   {"no": "Fart i m/s",         "th": "ความเร็วในหน่วย ม./วินาที", "en": "Speed in m/s"},
            "formula": f"{speed_kmh} ÷ 3.6",
            "result":  speed_ms,
            "unit":    "m/s",
            "note":    {
                "no": f"Bilen tilbakelegger {speed_ms} meter hvert sekund",
                "th": f"รถเคลื่อนที่ {speed_ms} เมตรต่อวินาที",
                "en": f"The car covers {speed_ms} metres every second",
            },
        },
        {
            "order":   2,
            "concept": "reaction_distance",
            "label":   {"no": "Reaksjonsavstand",    "th": "ระยะปฏิกิริยา",   "en": "Reaction distance"},
            "formula": f"{speed_ms} × {reaction_time_s}",
            "result":  react_m,
            "unit":    "m",
            "note":    {
                "no": f"Bilen kjører {react_m} m mens hjernen reagerer",
                "th": f"รถวิ่ง {react_m} ม. ขณะสมองตอบสนอง",
                "en": f"Car travels {react_m} m while your brain reacts",
            },
        },
        {
            "order":   3,
            "concept": "braking_distance",
            "label":   {"no": "Bremseavstand",       "th": "ระยะเบรก",         "en": "Braking distance"},
            "formula": (
                f"({speed_kmh} ÷ 10)² × {multiplier}"
                if multiplier != 1.0
                else f"({speed_kmh} ÷ 10)²"
            ),
            "result":  brake_m,
            "unit":    "m",
            "note":    cond_info["note"],
        },
        {
            "order":   4,
            "concept": "stopping_distance",
            "label":   {"no": "Stoppeavstand totalt", "th": "ระยะหยุดรวม",     "en": "Total stopping distance"},
            "formula": f"{react_m} + {brake_m}",
            "result":  stop_m,
            "unit":    "m",
            "note":    {
                "no": f"Fra du ser faren til bilen stopper: {stop_m} m",
                "th": f"ตั้งแต่เห็นอันตรายจนรถหยุด: {stop_m} ม.",
                "en": f"From seeing the danger to full stop: {stop_m} m",
            },
        },
    ]

    return {
        "input": {
            "speed_kmh":       speed_kmh,
            "condition":       condition,
            "reaction_time_s": reaction_time_s,
        },
        "results": {
            "speed_ms":             speed_ms,
            "reaction_distance_m":  react_m,
            "braking_distance_m":   brake_m,
            "stopping_distance_m":  stop_m,
        },
        "condition_info":  cond_info,
        "steps":           steps,
        "danger_context":  _danger_context(stop_m),
    }


# ─── Speed comparison ─────────────────────────────────────────────────────────

def compare_speeds(
    speed1_kmh: float,
    speed2_kmh: float,
    condition: str = "dry",
) -> dict:
    """
    Side-by-side comparison of two speeds.
    Highlights how energy and stopping distance scale non-linearly.
    Shows the real danger of speed increases.
    """
    if speed1_kmh <= 0 or speed2_kmh <= 0:
        raise ValueError("Speeds must be positive")
    if condition not in ROAD_CONDITIONS:
        condition = "dry"

    a = stopping_distance_full(speed1_kmh, condition)
    b = stopping_distance_full(speed2_kmh, condition)

    stop_a = a["results"]["stopping_distance_m"]
    stop_b = b["results"]["stopping_distance_m"]

    # Kinetic energy ratio (KE ∝ v²)
    energy_ratio = round((speed2_kmh / speed1_kmh) ** 2, 2)
    # Braking distance ratio
    brake_ratio  = round(
        b["results"]["braking_distance_m"] / a["results"]["braking_distance_m"], 2
    ) if a["results"]["braking_distance_m"] > 0 else 0

    extra_m = round(stop_b - stop_a, 1)

    insight = {
        "no": (
            f"Ved {speed2_kmh} km/t er stoppeavstanden {extra_m} m lenger "
            f"og energien {energy_ratio}× høyere enn ved {speed1_kmh} km/t."
        ),
        "th": (
            f"ที่ {speed2_kmh} กม./ชม. ระยะหยุดยาวกว่า {extra_m} ม. "
            f"และพลังงาน {energy_ratio} เท่าของ {speed1_kmh} กม./ชม."
        ),
        "en": (
            f"At {speed2_kmh} km/h the stopping distance is {extra_m} m longer "
            f"and the kinetic energy is {energy_ratio}× that at {speed1_kmh} km/h."
        ),
    }

    return {
        "condition":     condition,
        "speed_a":       a,
        "speed_b":       b,
        "comparison": {
            "energy_ratio":       energy_ratio,
            "brake_ratio":        brake_ratio,
            "extra_stopping_m":   extra_m,
            "insight":            insight,
        },
    }


# ─── Following distance ───────────────────────────────────────────────────────

def following_distance(speed_kmh: float, seconds: float = 2.0) -> dict:
    """
    Recommended following distance using the time-gap rule.
    Norwegian theory: minimum 2 seconds, recommended 3 seconds.
    """
    if speed_kmh <= 0:
        raise ValueError("speed_kmh must be positive")

    speed_ms = kmh_to_ms(speed_kmh)
    dist_m   = round(speed_ms * seconds, 1)
    car_lengths = round(dist_m / CAR_LENGTH_M, 1)

    rule_note = {
        "no": (
            "2-sekunders regel er minimum. "
            "I dårlig vær: bruk 3-4 sekunder."
        ),
        "th": "กฎ 2 วินาทีคือขั้นต่ำ สภาพอากาศเลว: ใช้ 3-4 วินาที",
        "en": "2-second rule is the minimum. Bad weather: use 3-4 seconds.",
    }

    return {
        "input": {
            "speed_kmh": speed_kmh,
            "seconds":   seconds,
        },
        "results": {
            "speed_ms":          speed_ms,
            "following_distance_m": dist_m,
            "car_lengths":       car_lengths,
        },
        "formula": f"{speed_ms} m/s × {seconds} s",
        "rule_note": rule_note,
    }
