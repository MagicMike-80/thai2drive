"""Canonical traffic-sign catalog served by ``/api/signs``."""

from __future__ import annotations

import json
from pathlib import Path


TYPE_META = {
    "vikeplikt": {"no": "Vikeplikt- og forkjorsskilt", "th": "ป้ายให้ทางและป้ายสิทธิ์ผ่านก่อน", "en": "Priority signs", "color": "#EF4444", "shape": "special"},
    "fare": {"no": "Fareskilt", "th": "ป้ายเตือน", "en": "Warning signs", "color": "#F59E0B", "shape": "triangle"},
    "forbud": {"no": "Forbudsskilt", "th": "ป้ายห้าม", "en": "Prohibition signs", "color": "#EF4444", "shape": "circle"},
    "pabud": {"no": "Pabudsskilt", "th": "ป้ายบังคับ", "en": "Mandatory signs", "color": "#3B82F6", "shape": "circle"},
    "opplysning": {"no": "Opplysningsskilt", "th": "ป้ายข้อมูล", "en": "Information signs", "color": "#0EA5E9", "shape": "rect"},
    "service": {"no": "Serviceskilt", "th": "ป้ายบริการ", "en": "Service signs", "color": "#06B6D4", "shape": "rect"},
    "visning": {"no": "Vegvisningsskilt", "th": "ป้ายบอกทาง", "en": "Direction signs", "color": "#8B5CF6", "shape": "rect"},
    "underskilt": {"no": "Underskilt", "th": "ป้ายเสริม", "en": "Supplementary signs", "color": "#A855F7", "shape": "rect"},
    "markering": {"no": "Markeringsskilt", "th": "ป้ายเครื่องหมาย", "en": "Marker signs", "color": "#EC4899", "shape": "special"},
}

GROUP_TYPES = {
    1: "vikeplikt", 2: "fare", 3: "forbud", 4: "pabud", 5: "opplysning",
    6: "service", 7: "visning", 8: "underskilt", 9: "markering",
}


def _load_signs() -> list[dict]:
    records = json.loads(Path(__file__).with_name("signs_content.json").read_text(encoding="utf-8"))
    return [
        {
            "num": row["id"],
            "type": GROUP_TYPES[row["group"]],
            "name": row["name"],
            "desc": row["explanation"],
            "driver_action": row["driver_action"],
        }
        for row in records
    ]


SIGNS = _load_signs()


def get_signs_grouped() -> dict:
    grouped = {}
    for sign in SIGNS:
        sign_type = sign["type"]
        grouped.setdefault(sign_type, {"meta": TYPE_META[sign_type], "signs": []})
        grouped[sign_type]["signs"].append(sign)
    return grouped
