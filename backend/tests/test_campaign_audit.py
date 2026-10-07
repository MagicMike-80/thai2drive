"""Offline guardrails for the aggregate-only A2 inspection script."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

spec = importlib.util.spec_from_file_location('audit_campaign', Path(__file__).resolve().parents[1] / 'scripts' / 'audit_campaign_legacy.py')
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


@pytest.mark.parametrize('sequence,expected,invalid', [(7, 7, False), ('PRIVATE_CONTACT', None, True),
                                                      ({'secret': 'PRIVATE_CONTACT'}, None, True),
                                                      (True, None, True), (-1, None, True)])
def test_only_aggregates_and_valid_counter_leave_audit(sequence, expected, invalid):
    db = MagicMock()
    db.campaign_counters.find_one.return_value = {'sequence': sequence}
    db.users.aggregate.return_value = []
    db.campaign_users.aggregate.return_value = []
    db.trial_grants.aggregate.return_value = []
    db.users.count_documents.return_value = 0
    db.__getitem__.return_value.list_indexes.return_value = []
    result = audit_module.audit(db, datetime(2026, 10, 7, tzinfo=timezone.utc))
    assert result['legacy_signup_sequence'] == expected
    assert result['legacy_signup_counter_invalid'] is invalid
    assert 'PRIVATE_CONTACT' not in json.dumps(result)
    assert result['reservations']['total'] == 0
    for call in db.mock_calls:
        assert call[0].split('.')[-1] in {'aggregate', 'find_one', 'count_documents', '__getitem__', 'list_indexes'}
        assert '$out' not in repr(call) and '$merge' not in repr(call)

def test_connection_error_never_prints_connection_or_exception(monkeypatch, capsys):
    secret = 'mongodb://PRIVATE_USER:PRIVATE_PASSWORD@invalid.example/'
    monkeypatch.setenv('MONGO_URL', secret)
    monkeypatch.setenv('DB_NAME', 'synthetic')
    def fail(*args, **kwargs):
        raise RuntimeError(secret)
    monkeypatch.setattr(audit_module, 'MongoClient', fail)
    with pytest.raises(SystemExit) as error:
        audit_module.main()
    assert error.value.code == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'status': 'failed', 'error_type': 'RuntimeError'}
    assert 'PRIVATE_' not in captured.out + captured.err
