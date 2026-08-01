"""
usage.py — Thai2Drive access tier engine
=========================================
Single source of truth for all question access decisions.

Tiers
-----
  guest       → 5 questions lifetime (tracked by device_id)
  registered  → 10 questions per Oslo calendar day
  premium     → unlimited

Design principles
-----------------
• All decisions are server-authoritative. Clients display what the server
  tells them; they never compute access themselves.
• Usage is incremented when questions are *served*, not when submitted.
  This is simpler and prevents batch-fetch abuse.
• Date resets use Europe/Oslo time so the day boundary feels natural to
  Norwegian users (midnight local, not 1-2am).
• Gate responses are a shared contract — the same JSON shape is returned
  to the mobile app and the web app, so both parse one format.

Gate response shape (HTTP 402)
-------------------------------
  {
    "error":  "limit_reached",
    "gate":   "register" | "upgrade",
    "tier":   "guest" | "registered",
    "used":   int,
    "limit":  int,
    "resets_at": null | ISO-8601 string   # null for guest (no reset)
  }

Usage status shape (GET /api/usage/status)
------------------------------------------
  {
    "tier":           "guest" | "registered" | "premium",
    "used":           int,
    "limit":          int | null,           # null = unlimited
    "remaining":      int | null,
    "streak":         int,
    "best_streak":    int,
    "resets_at":      null | ISO-8601 str,
    "gate":           null | "register" | "upgrade"
  }
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("usage")

# ── Tier limits ───────────────────────────────────────────────────────────────
GUEST_LIFETIME_LIMIT    = 5
REGISTERED_DAILY_LIMIT  = 10

# ── Tier names ────────────────────────────────────────────────────────────────
TIER_GUEST      = "guest"
TIER_REGISTERED = "registered"
TIER_PREMIUM    = "premium"


# ── Oslo date helper ──────────────────────────────────────────────────────────

try:
    from zoneinfo import ZoneInfo
    _OSLO = ZoneInfo("Europe/Oslo")
except ImportError:
    # Python < 3.9 fallback (Railway uses 3.11+, so this is a safety net only)
    import pytz  # type: ignore
    _OSLO = pytz.timezone("Europe/Oslo")


def _today_oslo() -> str:
    """Return today's date in Europe/Oslo time as YYYY-MM-DD string."""
    return datetime.now(_OSLO).strftime("%Y-%m-%d")


def _next_oslo_midnight_utc() -> str:
    """Return the next Oslo midnight expressed as a UTC ISO-8601 string."""
    # Get today's Oslo date, advance to tomorrow, convert back to UTC
    now_oslo = datetime.now(_OSLO).replace(tzinfo=None)
    tomorrow_oslo = now_oslo.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    # Attach Oslo tz and convert to UTC
    tomorrow_oslo_aware = datetime(
        tomorrow_oslo.year, tomorrow_oslo.month, tomorrow_oslo.day,
        tzinfo=_OSLO
    )
    return tomorrow_oslo_aware.astimezone(timezone.utc).isoformat()


# ── Tier resolution ───────────────────────────────────────────────────────────

def premium_is_active(user: Optional[dict]) -> bool:
    """True only if the caller has premium access *right now*.

    Closes the 168-hour JWT loophole: a token minted while premium was active
    stays valid for authentication for its full lifetime, but it carries the
    expiry of the access itself in `premium_until`. We re-check that on every
    request, so a free week (or a lapsed subscription) stops granting premium
    the moment it runs out — without logging the user out.

    Accepts both shapes:
      • decoded JWT payload  → is_premium + premium_until
      • raw users document   → is_admin / is_premium + premium_expires_at + trial_expires_at
    """
    if not user:
        return False
    if user.get("is_admin"):
        return True

    now = datetime.now(timezone.utc)

    def _parse(value) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    # Active free week — granted in MongoDB, never on the client.
    trial_until = _parse(user.get("trial_expires_at"))
    if trial_until and trial_until > now:
        return True

    if not user.get("is_premium"):
        return False

    until = user.get("premium_until") or user.get("premium_expires_at")
    if not until:
        return True  # lifetime premium, or a legacy token minted before this field existed
    expires = _parse(until)
    if expires is None:
        return False  # unparseable expiry → fail closed
    return expires > now


def resolve_tier(user: Optional[dict]) -> str:
    """Determine the access tier from a decoded JWT payload (or None for guest)."""
    if not user:
        return TIER_GUEST
    if premium_is_active(user):
        return TIER_PREMIUM
    return TIER_REGISTERED


# ── Guest usage ───────────────────────────────────────────────────────────────

async def get_guest_usage(db: AsyncIOMotorDatabase, device_id: str) -> int:
    """Return how many questions have been served to this guest device (lifetime)."""
    doc = await db.guest_usage.find_one({"device_id": device_id})
    return doc["questions_served"] if doc else 0


async def increment_guest_usage(db: AsyncIOMotorDatabase, device_id: str, count: int) -> int:
    """Increment guest usage and return the new total."""
    now = datetime.now(timezone.utc).isoformat()
    result = await db.guest_usage.find_one_and_update(
        {"device_id": device_id},
        {
            "$inc": {"questions_served": count},
            "$set": {"updated_at": now},
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=True,
    )
    return result["questions_served"]


# ── Registered daily usage ────────────────────────────────────────────────────

async def get_daily_usage(db: AsyncIOMotorDatabase, user_id: str) -> int:
    """Return how many questions have been served to this user today (Oslo day)."""
    doc = await db.daily_usage.find_one({"user_id": user_id, "date_oslo": _today_oslo()})
    return doc["questions_served"] if doc else 0


async def increment_daily_usage(db: AsyncIOMotorDatabase, user_id: str, count: int) -> int:
    """Increment daily usage and return today's total."""
    today = _today_oslo()
    now   = datetime.now(timezone.utc).isoformat()
    result = await db.daily_usage.find_one_and_update(
        {"user_id": user_id, "date_oslo": today},
        {
            "$inc": {"questions_served": count},
            "$set": {"updated_at": now},
            "$setOnInsert": {"created_at": now, "date_oslo": today},
        },
        upsert=True,
        return_document=True,
    )
    return result["questions_served"]


# ── Streak ────────────────────────────────────────────────────────────────────

async def update_streak(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """
    Update the user's streak based on today's Oslo date.
    Returns {current_streak, best_streak}.

    Rules:
    - If last_activity_date == today → already counted, no change
    - If last_activity_date == yesterday → streak continues (+1)
    - Otherwise → streak resets to 1
    """
    today     = _today_oslo()
    yesterday = (datetime.now(_OSLO).replace(tzinfo=None) - timedelta(days=1)).strftime("%Y-%m-%d")

    user = await db.users.find_one({"id": user_id}, {"current_streak": 1, "best_streak": 1, "last_activity_date": 1})
    if not user:
        return {"current_streak": 1, "best_streak": 1}

    last = user.get("last_activity_date")
    current = user.get("current_streak", 0)
    best    = user.get("best_streak", 0)

    if last == today:
        # Already updated today — nothing to do
        return {"current_streak": current, "best_streak": best}

    if last == yesterday:
        current += 1
    else:
        current = 1

    best = max(best, current)

    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "current_streak":    current,
            "best_streak":       best,
            "last_activity_date": today,
        }}
    )
    return {"current_streak": current, "best_streak": best}


async def get_streak(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Return current streak info without modifying it."""
    user = await db.users.find_one(
        {"id": user_id},
        {"current_streak": 1, "best_streak": 1, "last_activity_date": 1}
    )
    if not user:
        return {"current_streak": 0, "best_streak": 0}

    # Check if streak is still alive (last activity was today or yesterday)
    today     = _today_oslo()
    yesterday = (datetime.now(_OSLO).replace(tzinfo=None) - timedelta(days=1)).strftime("%Y-%m-%d")
    last      = user.get("last_activity_date", "")

    if last not in (today, yesterday):
        # Streak has expired — reset, but don't write (read-only path)
        return {"current_streak": 0, "best_streak": user.get("best_streak", 0)}

    return {
        "current_streak": user.get("current_streak", 0),
        "best_streak":    user.get("best_streak", 0),
    }


# ── Core gate function ────────────────────────────────────────────────────────

async def check_and_consume(
    db:        AsyncIOMotorDatabase,
    device_id: str,
    user:      Optional[dict],
    count:     int = 1,
) -> int:
    """
    Check whether `count` questions can be served to this caller, consume
    the allocation, and return the number of questions actually approved
    (may be less than count if close to limit).

    Raises HTTPException(402) with gate detail if no questions remain.
    Premium users always get count back unchanged.
    """
    tier = resolve_tier(user)

    if tier == TIER_PREMIUM:
        return count  # unlimited

    if tier == TIER_GUEST:
        used      = await get_guest_usage(db, device_id)
        remaining = max(0, GUEST_LIFETIME_LIMIT - used)

        if remaining == 0:
            raise HTTPException(status_code=402, detail={
                "error":     "limit_reached",
                "gate":      "register",
                "tier":      TIER_GUEST,
                "used":      used,
                "limit":     GUEST_LIFETIME_LIMIT,
                "resets_at": None,
            })

        approved = min(count, remaining)
        await increment_guest_usage(db, device_id, approved)
        return approved

    # TIER_REGISTERED
    user_id   = user["sub"]
    used      = await get_daily_usage(db, user_id)
    remaining = max(0, REGISTERED_DAILY_LIMIT - used)

    if remaining == 0:
        raise HTTPException(status_code=402, detail={
            "error":     "limit_reached",
            "gate":      "upgrade",
            "tier":      TIER_REGISTERED,
            "used":      used,
            "limit":     REGISTERED_DAILY_LIMIT,
            "resets_at": _next_oslo_midnight_utc(),
        })

    approved = min(count, remaining)
    await increment_daily_usage(db, user_id, approved)

    # Update streak on first question of the day
    if used == 0:
        await update_streak(db, user_id)

    return approved


# ── Status endpoint payload ───────────────────────────────────────────────────

async def build_usage_status(
    db:        AsyncIOMotorDatabase,
    device_id: str,
    user:      Optional[dict],
) -> dict:
    """
    Build the full usage status payload returned by GET /api/usage/status.
    This is the single object the client uses to decide what to show.
    """
    tier = resolve_tier(user)

    if tier == TIER_PREMIUM:
        user_id = user["sub"]
        streak  = await get_streak(db, user_id)
        daily   = await get_daily_usage(db, user_id)
        return {
            "tier":        TIER_PREMIUM,
            "used":        daily,
            "limit":       None,
            "remaining":   None,
            "streak":      streak["current_streak"],
            "best_streak": streak["best_streak"],
            "resets_at":   _next_oslo_midnight_utc(),
            "gate":        None,
        }

    if tier == TIER_GUEST:
        used      = await get_guest_usage(db, device_id)
        remaining = max(0, GUEST_LIFETIME_LIMIT - used)
        return {
            "tier":        TIER_GUEST,
            "used":        used,
            "limit":       GUEST_LIFETIME_LIMIT,
            "remaining":   remaining,
            "streak":      0,
            "best_streak": 0,
            "resets_at":   None,
            "gate":        "register" if remaining == 0 else None,
        }

    # TIER_REGISTERED
    user_id   = user["sub"]
    used      = await get_daily_usage(db, user_id)
    remaining = max(0, REGISTERED_DAILY_LIMIT - used)
    streak    = await get_streak(db, user_id)

    return {
        "tier":        TIER_REGISTERED,
        "used":        used,
        "limit":       REGISTERED_DAILY_LIMIT,
        "remaining":   remaining,
        "streak":      streak["current_streak"],
        "best_streak": streak["best_streak"],
        "resets_at":   _next_oslo_midnight_utc(),
        "gate":        "upgrade" if remaining == 0 else None,
    }


# ── Premium entitlement guard ─────────────────────────────────────────────────
# Lightweight helpers used by feature-gated endpoints.
# Import these in server.py: from usage import require_premium, require_registered

async def require_registered(user: Optional[dict]) -> dict:
    """
    FastAPI dependency — ensures the caller is at least a registered user.
    Returns the user dict on success; raises 402 if guest.
    """
    if not user:
        raise HTTPException(status_code=402, detail={
            "error": "auth_required",
            "gate":  "register",
            "tier":  TIER_GUEST,
        })
    return user


async def require_premium(user: Optional[dict]) -> dict:
    """
    FastAPI dependency — ensures the caller is a premium subscriber.
    Returns the user dict on success; raises 402 if not premium.
    """
    if not user:
        raise HTTPException(status_code=402, detail={
            "error": "auth_required",
            "gate":  "register",
            "tier":  TIER_GUEST,
        })
    if not premium_is_active(user):
        raise HTTPException(status_code=402, detail={
            "error": "premium_required",
            "gate":  "upgrade",
            "tier":  TIER_REGISTERED,
        })
    return user


# ── DB index bootstrap ────────────────────────────────────────────────────────

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create MongoDB indexes needed by this module. Call once at startup."""
    from pymongo import ASCENDING, IndexModel
    await db.guest_usage.create_indexes([
        IndexModel([("device_id", ASCENDING)], unique=True),
    ])
    await db.daily_usage.create_indexes([
        IndexModel([("user_id", ASCENDING), ("date_oslo", ASCENDING)], unique=True),
    ])
    logger.info("usage: indexes ensured")
