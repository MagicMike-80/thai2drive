"""Offline storage trust-boundary tests with synthetic bytes, no real book content."""
import hashlib
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from private_book_storage import PrivateBookStorage


class Client:
    def __init__(self, data, length=None):
        self.data, self.length, self.calls = data, length, []

    def get_object(self, **kwargs):
        self.calls.append(kwargs)
        self.stream = io.BytesIO(self.data)
        return {'ContentLength': len(self.data) if self.length is None else self.length, 'Body': self.stream}


def storage(tmp_path, monkeypatch, data=b'fictional bytes', length=None):
    monkeypatch.setenv('PRIVATE_BOOK_S3_BUCKET', 'fictional-private-bucket')
    client = Client(data, length)
    return PrivateBookStorage(tmp_path, client), client, hashlib.sha256(data).hexdigest()


def test_verified_asset_is_cached_and_never_returns_remote_url(tmp_path, monkeypatch):
    store, client, sha = storage(tmp_path, monkeypatch)
    filename = sha + '.png'
    path = store.image(filename, sha)
    assert path.read_bytes() == b'fictional bytes'
    assert store.image(filename, sha) == path
    assert len(client.calls) == 1
    assert client.calls[0]['Key'] == 'images/' + filename
    assert client.stream.closed


@pytest.mark.parametrize('filename', ['../elsewhere.png', 'candidate.png', 'a' * 64 + '.html'])
def test_rejects_non_content_addressed_names(tmp_path, monkeypatch, filename):
    store, client, sha = storage(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        store.image(filename, sha)
    assert not client.calls


def test_corrupt_download_is_never_cached(tmp_path, monkeypatch):
    store, client, _ = storage(tmp_path, monkeypatch)
    wrong = 'a' * 64
    with pytest.raises(ValueError):
        store.image(wrong + '.png', wrong)
    assert not list(tmp_path.rglob('*.png'))
    assert client.stream.closed


def test_oversize_response_is_closed(tmp_path, monkeypatch):
    store, client, sha = storage(tmp_path, monkeypatch, length=20 * 1024 * 1024)
    with pytest.raises(ValueError):
        store.image(sha + '.png', sha)
    assert client.stream.closed


def test_catalog_and_basis_require_full_pinned_digests(tmp_path, monkeypatch):
    store, client, sha = storage(tmp_path, monkeypatch, data=b'{}')
    monkeypatch.setenv('PRIVATE_BOOK_CATALOG_SHA256', sha)
    monkeypatch.setenv('PRIVATE_BOOK_BASIS_SHA256', sha)
    assert store.document('catalog.json') == b'{}'
    assert store.document('michael_safe_overrides.json') == b'{}'
    assert all(c['Key'].startswith('releases/' + sha + '/') for c in client.calls)
    monkeypatch.setenv('PRIVATE_BOOK_CATALOG_SHA256', sha[:8])
    with pytest.raises(ValueError):
        store.document('catalog.json')


def test_local_corruption_is_not_silently_replaced(tmp_path, monkeypatch):
    store, client, sha = storage(tmp_path, monkeypatch)
    path = tmp_path / 'private_book_assets' / (sha + '.png')
    path.parent.mkdir()
    path.write_bytes(b'changed')
    with pytest.raises(ValueError):
        store.image(path.name, sha)
    assert path.read_bytes() == b'changed'
    assert not client.calls
