"""A2 read-only campaign inventory. Prints aggregate counts only.

Run with MONGO_URL and DB_NAME supplied securely (e.g. railway run).
Never imports server, runs startup hooks, creates indexes, or writes documents.
No personal identifiers, contact values, tokens, connection strings, or raw
exceptions are printed. Collections are read on primary; this is not a snapshot.
"""
import json
import os
from datetime import datetime, timezone

from pymongo import MongoClient


def date(field):
    return {'$convert': {'input': '$' + field, 'to': 'date', 'onError': None, 'onNull': None}}


def total(condition):
    return {'$sum': {'$cond': [condition, 1, 0]}}


def group(collection, fields, before=None):
    rows = list(collection.aggregate((before or []) + [{'$group': {'_id': None, **fields}},
                                                      {'$project': {'_id': 0}}], maxTimeMS=30000))
    return rows[0] if rows else {key: 0 for key in fields}


def audit(db, now):
    active_trial = {'$gt': [date('trial_expires_at'), now]}
    expired_trial = {'$and': [{'$ne': [date('trial_expires_at'), None]},
                             {'$lte': [date('trial_expires_at'), now]}]}
    is_admin = {'$eq': ['$is_admin', True]}
    paid_flag = {'$eq': ['$is_premium', True]}
    historic_signup = {'$and': [{'$isNumber': '$campaign_index'},
                              {'$gte': ['$campaign_index', 1]}, {'$lte': ['$campaign_index', 50]}]}
    counter = db.campaign_counters.find_one({'_id': 'signup_50'}, {'_id': 0, 'sequence': 1})
    users = group(db.users, {
        'total_accounts': {'$sum': 1}, 'admin_accounts': total(is_admin),
        'accounts_with_campaign_index': total({'$isNumber': '$campaign_index'}),
        'signup_index_1_to_50': total(historic_signup),
        'admin_with_signup_index_1_to_50': total({'$and': [is_admin, historic_signup]}),
        'nonadmin_signup_index_1_to_50': total({'$and': [{'$ne': ['$is_admin', True]}, historic_signup]}),
        'active_trial': total(active_trial),
        'active_trial_with_signup_index_1_to_50': total({'$and': [active_trial, historic_signup]}), 'expired_trial': total(expired_trial),
        'trial_used_flag': total({'$eq': ['$trial_used', True]}),
        'premium_flag_nonadmin': total({'$and': [paid_flag, {'$ne': ['$is_admin', True]}]}),
        'premium_flag_without_expiry_nonadmin': total({'$and': [paid_flag, {'$ne': ['$is_admin', True]},
            {'$eq': [{'$ifNull': ['$premium_expires_at', None]}, None]}]}),
        'premium_flag_expired_nonadmin': total({'$and': [paid_flag, {'$ne': ['$is_admin', True]},
            {'$ne': [date('premium_expires_at'), None]}, {'$lte': [date('premium_expires_at'), now]}]}),
        'premium_and_active_trial_nonadmin': total({'$and': [paid_flag, active_trial, {'$ne': ['$is_admin', True]}]}),
        'invalid_trial_expiry': total({'$and': [{'$ne': [{'$ifNull': ['$trial_expires_at', None]}, None]},
                                               {'$eq': [date('trial_expires_at'), None]}]}),
    })
    # Reproduce the OLD exact email-OR-phone account matching, in a read-only lookup.
    matching = [{'$lookup': {'from': 'users', 'let': {'e': '$email', 'p': '$phone'}, 'pipeline': [
        {'$match': {'$expr': {'$or': [
            {'$and': [{'$ne': [{'$ifNull': ['$$e', '']}, '']}, {'$eq': ['$email', '$$e']}]},
            {'$and': [{'$ne': [{'$ifNull': ['$$p', '']}, '']}, {'$eq': ['$phone', '$$p']}]}]}}},
        {'$project': {'_id': 0, 'match': {'$literal': 1}}}], 'as': 'matches'}}]
    reservations = group(db.campaign_users, {
        'total': {'$sum': 1},
        'without_account_match': total({'$eq': [{'$size': '$matches'}, 0]}),
        'one_account_match': total({'$eq': [{'$size': '$matches'}, 1]}),
        'multiple_account_matches': total({'$gt': [{'$size': '$matches'}, 1]}),
        'active_recorded_expiry': total({'$gt': [date('premium_until'), now]}),
        'expired_recorded_expiry': total({'$and': [{'$ne': [date('premium_until'), None]},
                                                 {'$lte': [date('premium_until'), now]}]}),
    }, matching)
    duplicates = {}
    for field in ('email', 'phone', 'campaign_index'):
        rows = list(db.campaign_users.aggregate([
            {'$match': {field: {'$exists': True, '$nin': [None, '']}}},
            {'$group': {'_id': '$' + field, 'n': {'$sum': 1}}},
            {'$match': {'n': {'$gt': 1}}},
            {'$group': {'_id': None, 'duplicate_groups': {'$sum': 1}, 'extra_rows': {'$sum': {'$subtract': ['$n', 1]}}}},
            {'$project': {'_id': 0}}], maxTimeMS=30000))
        duplicates[field] = rows[0] if rows else {'duplicate_groups': 0, 'extra_rows': 0}
    indexes = {}
    for name in ('users', 'campaign_users', 'campaign_counters', 'trial_grants'):
        indexes[name] = [{'fields': list(i['key']), 'unique': bool(i.get('unique')) or list(i['key']) == ['_id'], 'sparse': bool(i.get('sparse'))}
                         for i in db[name].list_indexes()]
    sequence = (counter or {}).get('sequence')
    valid_sequence = type(sequence) is int and sequence >= 0
    return {'users': users, 'legacy_signup_sequence': sequence if valid_sequence else None,
            'legacy_signup_counter_present': counter is not None,
            'legacy_signup_counter_invalid': counter is not None and not valid_sequence,
            'reservations': reservations, 'reservation_duplicates': duplicates,
            'older_trial_grants': group(db.trial_grants, {
                'total': {'$sum': 1},
                'with_account_match': total({'$gt': [{'$size': '$matches'}, 0]}),
                'without_account_match': total({'$eq': [{'$size': '$matches'}, 0]}),
                'active_recorded_expiry': total({'$gt': [date('expires_at'), now]}),
            }, [{'$lookup': {'from': 'users', 'localField': 'user_id', 'foreignField': 'id',
                             'pipeline': [{'$project': {'_id': 0, 'match': {'$literal': 1}}}], 'as': 'matches'}}]), 'indexes': indexes,
            'accounts_at_end': db.users.count_documents({}),
            'limitations': ['Non-snapshot reads; concurrent changes may occur.',
                'Premium flags do not establish payment provenance.',
                'No owner, children or test identities inferred from names.',
                'Exact old-route contact matching; no new normalization or deduplication.']}


def main():
    uri = os.environ.get('MONGO_URL')
    name = os.environ.get('DB_NAME')
    if not uri or not name:
        raise SystemExit('Required database configuration unavailable; no access attempted.')
    started = datetime.now(timezone.utc)
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=15000, connectTimeoutMS=15000,
                         socketTimeoutMS=45000, appname='Thai2Drive-A2-read-only-audit') as client:
            report = audit(client[name], started)
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__}))
        raise SystemExit(1)  # Never print connection details or documents.
    print(json.dumps({'status': 'complete', 'started_at': started.isoformat(),
                      'finished_at': datetime.now(timezone.utc).isoformat(), **report}, indent=2))


if __name__ == '__main__':
    main()
