"""Shared registered-account quota when the V6 registered pilot is enabled."""
import hashlib
import json
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError
from pymongo.write_concern import WriteConcern


async def consume_registered(db, user_id, event, day_key_for, daily_limit, *, delivery=None):
    """Commit one ordinary answer or V6 delivery against the same Oslo-day counter.

    Legacy usage rows retain their Mongo ID. New rows have a deterministic ID,
    so two simultaneous first answers cannot create independent counters.
    """
    if not isinstance(user_id, str) or not user_id or not isinstance(event["event_id"], str):
        raise ValueError("Missing quota identity")
    if event["event_id"].startswith("v6:") != (delivery is not None):
        return "conflict"
    selector = {"scope": "user", "key": user_id}
    event_key = hashlib.sha256(json.dumps([user_id, event["event_id"]], separators=(",", ":")).encode()).hexdigest()
    receipt_id = "registered:" + event_key
    account_id = "registered:" + hashlib.sha256(user_id.encode()).hexdigest()

    async def commit(session):
        receipt = await db.access_events.find_one({"_id": receipt_id}, session=session)
        if receipt:
            if (receipt.get("key") != user_id or receipt.get("scope") != "user"
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
        used = usage.get("daily_used", 0) if usage.get("day_key") == day else 0
        if type(used) is not int or used < 0:
            raise ValueError("Invalid registered quota")
        if used >= daily_limit:
            return "limited"
        timestamp = now.isoformat()
        fields = {**selector, "user_id": user_id, "day_key": day, "daily_used": used + 1,
                  "updated_at": timestamp}
        if event.get("device_id"):
            fields["device_id"] = event["device_id"]
        await db.access_usage.update_one({"_id": usage.get("_id", account_id), **selector},
            {"$set": fields, "$setOnInsert": {"created_at": timestamp}}, upsert=True, session=session)
        await db.access_events.insert_one({**event, **selector, "_id": receipt_id, "user_id": user_id,
                                           "v6_delivery": delivery, "created_at": timestamp}, session=session)
        return "consumed"

    for attempt in range(2):
        try:
            async with await db.client.start_session() as session:
                return await session.with_transaction(commit, write_concern=WriteConcern("majority"))
        except DuplicateKeyError:
            if attempt:
                raise
