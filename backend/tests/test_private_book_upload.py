"""Synthetic-only immutable upload tests; no network or private source content."""
import io
import json
import sys
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.upload_private_book import prepare, upload, sha
from scripts import upload_private_book as uploader


class Objects:
    def __init__(self):
        self.data, self.writes = {}, []

    def get_object(self, Bucket, Key):
        if Key not in self.data:
            raise ClientError({'Error': {'Code': 'NoSuchKey'}}, 'GetObject')
        return {'Body': io.BytesIO(self.data[Key])}

    def put_object(self, **kwargs):
        assert kwargs['IfNoneMatch'] == '*'
        assert kwargs['CacheControl'] == 'private, no-store'
        assert 'ACL' not in kwargs
        key = kwargs['Key']
        if key in self.data:
            raise ClientError({'Error': {'Code': 'PreconditionFailed'}}, 'PutObject')
        self.data[key] = kwargs['Body']
        self.writes.append(key)


@pytest.fixture
def content(tmp_path):
    image = b'synthetic image bytes'
    digest = sha(image)
    (tmp_path / 'private_book_assets').mkdir()
    (tmp_path / 'private_book_data').mkdir()
    (tmp_path / 'private_book_assets' / (digest + '.png')).write_bytes(image)
    row = {'id': 'synthetic', 'preview_image': {'file': digest + '.png', 'sha256': digest}}
    (tmp_path / 'private_book_data/catalog.json').write_text(json.dumps({'rows': [row]}), encoding='utf8')
    (tmp_path / 'private_book_data/michael_safe_overrides.json').write_text('{}', encoding='utf8')
    return tmp_path


def test_upload_verifies_bytes_publishes_catalog_last_and_reuses_identical(content):
    client = Objects()
    result = upload(content, client, 'private')
    assert result['written'] == 3 and result['activated'] is False
    assert client.writes[-1].endswith('/catalog.json')
    assert upload(content, client, 'private')['reused'] == 3
    assert len(client.writes) == 3


def test_conflicting_existing_image_is_never_overwritten(content):
    client = Objects()
    objects, _ = prepare(content)
    key = next(iter(objects))
    client.data[key] = b'existing different version'
    with pytest.raises(ValueError, match='refusing overwrite'):
        upload(content, client, 'private')
    assert client.data[key] == b'existing different version'
    assert client.writes == []


def test_invalid_local_image_blocks_all_writes(content):
    next((content / 'private_book_assets').iterdir()).write_bytes(b'changed')
    client = Objects()
    with pytest.raises(ValueError, match='Image bytes'):
        upload(content, client, 'private')
    assert client.writes == []


def test_unsupported_image_type_blocks_all_writes(content):
    path = content / 'private_book_data/catalog.json'
    catalog = json.loads(path.read_text(encoding='utf8'))
    media = catalog['rows'][0]['preview_image']
    media['file'] = media['sha256'] + '.gif'
    path.write_text(json.dumps(catalog), encoding='utf8')
    client = Objects()
    with pytest.raises(ValueError, match='image name'):
        upload(content, client, 'private')
    assert client.writes == []


@pytest.mark.parametrize('limit', ['MAX_IMAGE_BYTES', 'MAX_DOCUMENT_BYTES'])
def test_oversize_input_blocks_all_writes(content, monkeypatch, limit):
    monkeypatch.setattr(uploader, limit, 1)
    client = Objects()
    with pytest.raises(ValueError, match='too large'):
        upload(content, client, 'private')
    assert client.writes == []
