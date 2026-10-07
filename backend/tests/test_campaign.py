"""A1 safety contract: the retired campaign cannot read or mutate accounts."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
import webapp


@pytest.mark.parametrize('language', ['no', 'th', 'en'])
@pytest.mark.parametrize('authorization', [None, 'Bearer invalid', 'valid'])
def test_retired_route_never_touches_database(language, authorization):
    database = MagicMock()
    headers = {}
    if authorization == 'valid':
        authorization = 'Bearer ' + server.create_token('account-a', 'a@example.test', False)
    if authorization:
        headers['Authorization'] = authorization
    with patch.object(server, 'db', database):
        response = TestClient(server.app).post('/api/campaign/register', headers=headers, json={
            'name': 'Synthetic', 'email': 'account-b@example.test',
            'phone': '+4700000000', 'language': language,
        })
    assert response.status_code == 410
    assert response.json()['error'] == 'campaign_closed'
    assert response.json()['success'] is False
    assert response.headers['cache-control'] == 'no-store'
    assert database.mock_calls == []  # no reads, grants, counter increments, or account writes


@pytest.mark.parametrize('body', [None, {}, {'email': 'a@example.test'}])
def test_retired_route_does_not_require_contact_data(body):
    with patch.object(server, 'db', MagicMock()) as database:
        response = TestClient(server.app).post('/api/campaign/register', json=body)
    assert response.status_code == 410
    assert database.mock_calls == []


@pytest.mark.parametrize('registered', [0, 7, 50, 51])
def test_status_preserves_historical_counts_but_never_opens(registered):
    database = MagicMock()
    database.campaign_users.count_documents = AsyncMock(return_value=registered)
    with patch.object(server, 'db', database):
        data = TestClient(server.app).get('/api/campaign/status').json()
    assert data == {'success': True, 'total_seats': 50, 'registered': registered,
                    'remaining': max(0, 50-registered), 'is_active': False}
    database.campaign_users.count_documents.assert_awaited_once_with({})
    assert len(database.mock_calls) == 1


def test_enrollment_elements_removed_but_normal_signup_remains():
    html = webapp.WEBAPP_HTML
    for element in ('homeCampaignBanner', 'campaignModal', 'campaignForm', 'campSubmitBtn'):
        assert f'id="{element}"' not in html
    assert 'onclick="doRegister()"' in html
    assert '/api/campaign/register' not in html
