"""Private S3 reads pinned to immutable SHA256; never issue browser storage URLs."""
from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

from botocore.config import Config

MAX_IMAGE_BYTES = 16 * 1024 * 1024
MAX_DOCUMENT_BYTES = 32 * 1024 * 1024


def digest(value):
    if not re.fullmatch(r'[a-f0-9]{64}', value or ''):
        raise ValueError('Full SHA256 required')
    return value


def image_name(filename, expected):
    digest(expected)
    if not re.fullmatch(re.escape(expected) + r'\.(png|jpg|jpeg|webp)', filename):
        raise ValueError('Invalid private image name')
    return filename


class PrivateBookStorage:
    def __init__(self, base: Path, client=None):
        self.base = base
        self.bucket = os.environ.get('PRIVATE_BOOK_S3_BUCKET', '')
        self.client = client

    @property
    def remote(self):
        return bool(self.bucket)

    def _client(self):
        if self.client is None:
            import boto3
            endpoint = os.environ['PRIVATE_BOOK_S3_ENDPOINT']
            if not endpoint.startswith('https://'):
                raise ValueError('Private storage requires HTTPS')
            self.client = boto3.client('s3', endpoint_url=endpoint,
                region_name=os.environ['PRIVATE_BOOK_S3_REGION'],
                aws_access_key_id=os.environ['PRIVATE_BOOK_S3_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['PRIVATE_BOOK_S3_SECRET_ACCESS_KEY'],
                config=Config(connect_timeout=5, read_timeout=15, retries={'max_attempts': 1},
                              s3={'addressing_style': 'virtual'}))
        return self.client

    def _read(self, key, expected, maximum):
        digest(expected)
        response = self._client().get_object(Bucket=self.bucket, Key=key)
        stream = response['Body']
        try:
            if response.get('ContentLength', maximum + 1) > maximum:
                raise ValueError('Private resource too large')
            data = stream.read(maximum + 1)
        finally:
            stream.close()
        if len(data) > maximum or hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Private resource hash mismatch')
        return data

    def document(self, name):
        if name not in {'catalog.json', 'michael_safe_overrides.json'}:
            raise ValueError('Unknown private document')
        if not self.remote:
            return (self.base / 'private_book_data' / name).read_bytes()
        catalog_sha = digest(os.environ.get('PRIVATE_BOOK_CATALOG_SHA256'))
        expected = catalog_sha if name == 'catalog.json' else digest(os.environ.get('PRIVATE_BOOK_BASIS_SHA256'))
        return self._read('releases/' + catalog_sha + '/' + name, expected, MAX_DOCUMENT_BYTES)

    def image(self, filename, expected):
        image_name(filename, expected)
        path = self.base / 'private_book_assets' / filename
        if path.is_file():
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('Private cached image mismatch')
            return path
        if not self.remote:
            raise FileNotFoundError(filename)
        data = self._read('images/' + filename, expected, MAX_IMAGE_BYTES)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as target:
                temporary = Path(target.name)
                target.write(data)
            os.replace(temporary, path)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
        return path
