"""Public-safe access tests using only synthetic content, never private book data."""
import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_book as pb


class Users:
    async def find_one(self, query, projection=None):
        return {'id': query['id']} if query['id'] in {'reviewer', 'other'} else None


@pytest.fixture
def preview(monkeypatch):
    monkeypatch.setenv('PRIVATE_BOOK_ENABLED', '1')
    monkeypatch.setenv('PRIVATE_BOOK_REVIEWER_IDS', 'reviewer')
    monkeypatch.setenv('PRIVATE_BOOK_S3_BUCKET', 'synthetic-private-bucket')
    row = {'id': 'synthetic-row', 'version': '123456789abc', 'printed_page': 1, 'pdf_page': 2,
           'index': {'part': 1, 'section_no': '1'}, 'chapter': 'Synthetic', 'section': 'Synthetic',
           'title': {'no': 'Eksempel', 'th': 'ตัวอย่าง', 'en': 'Example'},
           'core_sentence': {'en': 'Synthetic test text'}, 'points': [], 'review_status': 'draft',
           'preview_image': {'file': '', 'sha256': '', 'status': 'missing', 'languages': []},
           'check_question': {'q': {'en': 'Synthetic question'}, 'options': [{'en': 'A'}, {'en': 'B'}],
                              'answer': 0}, 'private_teacher_basis': {'en': 'DO_NOT_EXPOSE'}}
    calls = []
    def document(self, name):
        calls.append(name)
        return json.dumps({'rows': [row]} if name == 'catalog.json' else {})
    monkeypatch.setattr(pb.PrivateBookStorage, 'document', document)
    db = type('DB', (), {'users': Users()})()
    app = FastAPI()
    app.include_router(pb.create_private_book_router(lambda: db,
        lambda token: {'sub': token} if token in {'reviewer', 'other'} else None))
    return TestClient(app), calls


@pytest.mark.parametrize('path', ['/view', '/catalog', '/image/synthetic-row/' + 'a' * 64])
def test_unauthorized_requests_never_read_private_storage(preview, path):
    client, calls = preview
    assert client.get(pb.PREFIX + path).status_code == 401
    assert client.get(pb.PREFIX + path, headers={'Authorization': 'Bearer other'}).status_code == 403
    assert calls == []


def test_reviewer_catalog_omits_answer_and_teacher_material(preview):
    client, calls = preview
    response = client.get(pb.PREFIX + '/catalog?language=en', headers={'Authorization': 'Bearer reviewer'})
    assert response.status_code == 200
    assert len(response.json()['rows']) == 1
    assert 'DO_NOT_EXPOSE' not in response.text
    assert '"answer"' not in response.text
    assert 'no-store' in response.headers['cache-control']
    assert calls == ['catalog.json', 'michael_safe_overrides.json']


def test_missing_private_storage_fails_closed_after_auth(preview, monkeypatch):
    client, _ = preview
    def unavailable(*args):
        raise OSError('sensitive provider detail')
    monkeypatch.setattr(pb.PrivateBookStorage, 'document', unavailable)
    response = client.get(pb.PREFIX + '/catalog', headers={'Authorization': 'Bearer reviewer'})
    assert response.status_code == 503
    assert 'sensitive' not in response.text


def test_disabled_preview_does_not_fetch_storage(preview, monkeypatch):
    client, calls = preview
    monkeypatch.delenv('PRIVATE_BOOK_ENABLED')
    assert client.get(pb.PREFIX + '/catalog', headers={'Authorization': 'Bearer reviewer'}).status_code == 404
    assert calls == []
