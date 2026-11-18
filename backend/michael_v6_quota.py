"""Shared registered-account quota when the V6 registered pilot is enabled."""
import hashlib
import json
import re
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError
from pymongo.write_concern import WriteConcern


GUEST_PREFIX = "web_guest_v6-"


def guest_device(proof):
    """A public guest ID cannot be used as its 256-bit browser credential."""
    if not isinstance(proof, str) or not re.fullmatch(r"[0-9a-f]{64}", proof):
        return None
    return GUEST_PREFIX + hashlib.sha256(b"v6-guest\0" + bytes.fromhex(proof)).hexdigest()


async def consume_quota(db, user_id, event, day_key_for, limit, *, delivery=None, guest=False):
    """Commit one ordinary answer or V6 delivery against the same Oslo-day counter.

    Legacy usage rows retain their Mongo ID. New rows have a deterministic ID,
    so two simultaneous first answers cannot create independent counters.
    """
    if not isinstance(user_id, str) or not user_id or not isinstance(event["event_id"], str):
        raise ValueError("Missing quota identity")
    if event["event_id"].startswith("v6:") != (delivery is not None):
        return "conflict"
    scope = "guest" if guest else "user"
    prefix = "guest-session:" if guest else "registered:"
    selector = {"scope": scope, "key": user_id}
    event_key = hashlib.sha256(json.dumps([user_id, event["event_id"]], separators=(",", ":")).encode()).hexdigest()
    receipt_id = prefix + event_key
    account_id = prefix + hashlib.sha256(user_id.encode()).hexdigest()

    async def commit(session):
        receipt = await db.access_events.find_one({"_id": receipt_id}, session=session)
        if receipt:
            if (receipt.get("key") != user_id or receipt.get("scope") != scope
                    or receipt["question_id"] != event["question_id"] or receipt.get("v6_delivery") != delivery):
                return "conflict"
            return "replayed"
        if delivery is None:
            legacy = await db.access_events.find_one({**selector, "event_id": event["event_id"]}, session=session)
            if legacy:
                return "replayed" if legacy.get("question_id") == event["question_id"] else "conflict"
        rows = await db.access_usage.find(selector, session=session).limit(2).to_list(2)
        if len(rows) > 1:
            raise ValueError("Ambiguous registered quota")
        usage = rows[0] if rows else {}
        now = datetime.now(timezone.utc)
        day = day_key_for(now)
        counter = "total_used" if guest else "daily_used"
        used = usage.get(counter, 0) if guest or usage.get("day_key") == day else 0
        if type(used) is not int or used < 0:
            raise ValueError("Invalid registered quota")
        if used >= limit:
            return "limited"
        timestamp = now.isoformat()
        owner = None if guest else user_id
        fields = {**selector, "user_id": owner, counter: used + 1, "updated_at": timestamp}
        if not guest:
            fields["day_key"] = day
        if event.get("device_id"):
            fields["device_id"] = event["device_id"]
        await db.access_usage.update_one({"_id": usage.get("_id", account_id), **selector},
            {"$set": fields, "$setOnInsert": {"created_at": timestamp}}, upsert=True, session=session)
        await db.access_events.insert_one({**event, **selector, "_id": receipt_id, "user_id": owner,
                                           "v6_delivery": delivery, "created_at": timestamp}, session=session)
        return "consumed"

    for attempt in range(2):
        try:
            async with await db.client.start_session() as session:
                return await session.with_transaction(commit, write_concern=WriteConcern("majority"))
        except DuplicateKeyError:
            if attempt:
                raise
