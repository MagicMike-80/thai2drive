"""
Traffic Math Routes — Thai2Drive
----------------------------------
All endpoints are prefixed /api/math/* when mounted in server.py.

Endpoints:
  GET  /math/stopping-distance  – full stopping distance breakdown
  GET  /math/compare            – side-by-side speed comparison
  GET  /math/following-distance – time-gap rule calculation
  GET  /math/conditions         – list all road condition options

No database. No AI. Pure deterministic calculation.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

import traffic_math

logger = logging.getLogger("traffic_math_routes")

math_router = APIRouter()


# ─── Endpoints ────────────────────────────────────────────────────────────────

@math_router.get("/math/stopping-distance")
def get_stopping_distance(
    speed:     float = Query(...,  description="Speed in km/h", gt=0, le=250),
    condition: str   = Query("dry", description="Road condition key: dry | wet | snow | ice"),
    reaction:  float = Query(1.0,  description="Reaction time in seconds", gt=0, le=5),
):
    """
    Full stopping distance breakdown for a given speed + road condition.

    Returns step-by-step formulas with multilingual labels (no/th/en),
    danger context (car lengths / bus lengths), and condition metadata.
    """
    if condition not in traffic_math.ROAD_CONDITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown condition '{condition}'. Choose from: {list(traffic_math.ROAD_CONDITIONS.keys())}",
        )
    try:
        result = traffic_math.stopping_distance_full(
            speed_kmh       = speed,
            condition       = condition,
            reaction_time_s = reaction,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@math_router.get("/math/compare")
def get_speed_comparison(
    speed1:    float = Query(...,  description="First speed in km/h",  gt=0, le=250),
    speed2:    float = Query(...,  description="Second speed in km/h", gt=0, le=250),
    condition: str   = Query("dry", description="Road condition key: dry | wet | snow | ice"),
):
    """
    Side-by-side comparison of two speeds.

    Shows how kinetic energy and stopping distance scale non-linearly —
    the core insight for understanding why small speed increases are dangerous.
    """
    if condition not in traffic_math.ROAD_CONDITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown condition '{condition}'. Choose from: {list(traffic_math.ROAD_CONDITIONS.keys())}",
        )
    try:
        result = traffic_math.compare_speeds(
            speed1_kmh = speed1,
            speed2_kmh = speed2,
            condition  = condition,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@math_router.get("/math/following-distance")
def get_following_distance(
    speed:   float = Query(...,  description="Speed in km/h", gt=0, le=250),
    seconds: float = Query(2.0, description="Time gap in seconds (2 = minimum, 3 = recommended)", gt=0, le=10),
):
    """
    Recommended following distance using the time-gap rule.

    Norwegian theory: minimum 2 seconds, recommended 3 seconds in good weather.
    Returns distance in metres, car lengths, and the formula string.
    """
    try:
        result = traffic_math.following_distance(
            speed_kmh = speed,
            seconds   = seconds,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@math_router.get("/math/conditions")
def get_conditions():
    """
    Return all road condition options with multilingual labels and multipliers.

    Used by the frontend to populate condition pickers without hardcoding values.
    """
    return {
        "conditions": list(traffic_math.ROAD_CONDITIONS.values()),
        "default":    "dry",
    }
