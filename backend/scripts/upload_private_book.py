"""Upload a verified private release; never publishes it or changes account access."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from private_book_storage import PrivateBookStorage, image_name, MAX_IMAGE_BYTES, MAX_DOCUMENT_BYTES


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(base):
    catalog_bytes = (base / 'private_book_data/catalog.json').read_bytes()
    if len(catalog_bytes) > MAX_DOCUMENT_BYTES:
        raise ValueError('Private catalog too large')
    catalog = json.loads(catalog_bytes)
    catalog_sha = sha(catalog_bytes)
    prefix = 'releases/' + catalog_sha + '/'
    objects = {}
    ids = [row['id'] for row in catalog['rows']]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('Empty or duplicate lesson ids')
    for row in catalog['rows']:
        media = row['preview_image']
        filename = media.get('file', '')
        if not filename:
            continue
        if Path(filename).name != filename or '/' in filename or '\\' in filename:
            raise ValueError('Invalid image path')
        image_name(filename, media['sha256'])
        data = (base / 'private_book_assets' / filename).read_bytes()
        if len(data) > MAX_IMAGE_BYTES:
            raise ValueError('Private image too large')
        if sha(data) != media['sha256'] or Path(filename).stem != media['sha256']:
            raise ValueError('Image bytes do not match catalog: ' + row['id'])
        objects['images/' + filename] = data
    basis = (base / 'private_book_data/michael_safe_overrides.json').read_bytes()
    if len(basis) > MAX_DOCUMENT_BYTES:
        raise ValueError('Private teacher document too large')
    json.loads(basis)
    objects[prefix + 'michael_safe_overrides.json'] = basis
    provenance = base / 'private_book_data/provenance.json'
    if provenance.is_file():
        data = provenance.read_bytes()
        if len(data) > MAX_DOCUMENT_BYTES:
            raise ValueError('Private provenance too large')
        objects[prefix + 'provenance.json'] = data
    # Catalog is uploaded last; activation is a separate, explicit server config step.
    objects[prefix + 'catalog.json'] = catalog_bytes
    return objects, {'rows': len(ids), 'images': sum(key.startswith('images/') for key in objects),
                     'catalog_sha256': catalog_sha, 'basis_sha256': sha(basis)}


def remote_digest(client, bucket, key):
    try:
        result = client.get_object(Bucket=bucket, Key=key)
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') in {'NoSuchKey', '404'}:
            return None
        raise
    stream = result['Body']
    digest = hashlib.sha256()
    try:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    finally:
        stream.close()
    return digest.hexdigest()


def upload(base, client, bucket):
    objects, evidence = prepare(base)  # Validate every local object before the first write.
    written = reused = 0
    for key, data in objects.items():
        expected = sha(data)
        current = remote_digest(client, bucket, key)
        if current is not None:
            if current != expected:
                raise ValueError('Existing private object differs; refusing overwrite: ' + key)
            reused += 1
            continue
        try:
            client.put_object(Bucket=bucket, Key=key, Body=data, IfNoneMatch='*',
                              ContentType='application/json' if key.endswith('.json') else 'application/octet-stream',
                              CacheControl='private, no-store', Metadata={'sha256': expected})
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') not in {'PreconditionFailed', '412'}:
                raise
        if remote_digest(client, bucket, key) != expected:
            raise ValueError('Uploaded private object did not verify: ' + key)
        written += 1
    return dict(evidence, written=written, reused=reused, activated=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--content-root', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.dry_run:
        objects, evidence = prepare(args.content_root)
        print(json.dumps(dict(evidence, objects=len(objects), dry_run=True)))
    else:
        storage = PrivateBookStorage(args.content_root)
        if not storage.remote:
            raise SystemExit('Private storage must be explicitly configured')
        print(json.dumps(upload(args.content_root, storage._client(), storage.bucket)))
