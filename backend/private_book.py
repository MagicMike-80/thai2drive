"""Account-restricted editorial book. No writes to learner progress or public catalog."""
from __future__ import annotations

import hashlib
import asyncio
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from bildebok_michael import teacher_payload
from private_book_storage import PrivateBookStorage

BASE = Path(__file__).resolve().parent
COOKIE = 't2d_book_review'
PREFIX = '/api/book-preview'
PRIVATE_HEADERS = {'Cache-Control': 'no-store, private', 'Vary': 'Cookie, Authorization',
                   'X-Robots-Tag': 'noindex, nofollow, noarchive', 'Referrer-Policy': 'no-referrer'}
Language = Literal['no', 'th', 'en']


class StrictBody(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Begin(StrictBody):
    row_id: str = Field(max_length=80)
    version: str = Field(pattern=r'^[a-f0-9]{12}$')
    language: Language


class Answer(Begin):
    option: StrictInt


def load_catalog():
    return json.loads((BASE / 'private_book_data/catalog.json').read_text(encoding='utf8'))


def create_private_book_router(get_db, verify_token, complete=None):
    router = APIRouter(prefix=PREFIX)
    storage = PrivateBookStorage(BASE)
    rows, overrides = {}, {}
    catalog_lock = asyncio.Lock()
    if not storage.remote and (BASE / 'private_book_data/catalog.json').is_file():
        rows = {r['id']: r for r in load_catalog()['rows']}
        overrides = json.loads(storage.document('michael_safe_overrides.json'))

    async def ensure_catalog():
        nonlocal overrides
        if rows:
            return
        async with catalog_lock:
            if rows:
                return
            try:
                catalog = json.loads(await asyncio.to_thread(storage.document, 'catalog.json'))
                basis = json.loads(await asyncio.to_thread(storage.document, 'michael_safe_overrides.json'))
                loaded = {r['id']: r for r in catalog['rows']}
                if not loaded or len(loaded) != len(catalog['rows']):
                    raise ValueError('Invalid private catalog')
                overrides = basis
                rows.update(loaded)
            except Exception:
                raise HTTPException(503, 'Private book unavailable', headers=PRIVATE_HEADERS)

    async def reviewer(request: Request):
        # Permission is server-owned, deny by default. Neither email nor role in JWT grants access.
        if os.environ.get('PRIVATE_BOOK_ENABLED', '0') != '1':
            raise HTTPException(404, 'Not found', headers=PRIVATE_HEADERS)
        authorization = request.headers.get('authorization', '')
        # Only the HTML shell can use the cookie. Data and images require the live webapp bearer.
        token = authorization[7:] if authorization.lower().startswith('bearer ') else (
            request.cookies.get(COOKIE, '') if request.url.path == PREFIX + '/view' else '')
        identity = verify_token(token) if token else None
        if not identity or not identity.get('sub'):
            raise HTTPException(401, 'Authentication required', headers=PRIVATE_HEADERS)
        user = await get_db().users.find_one({'id': identity['sub']}, {'_id': 0, 'password_hash': 0})
        allowed = {s.strip() for s in os.environ.get('PRIVATE_BOOK_REVIEWER_IDS', '').split(',') if s.strip()}
        if not user or user.get('id') not in allowed:
            raise HTTPException(403, 'Private review only', headers=PRIVATE_HEADERS)
        await ensure_catalog()
        return user

    def row_for(body):
        row = rows.get(body.row_id)
        if not row:
            raise HTTPException(404, 'Unknown lesson', headers=PRIVATE_HEADERS)
        if row['version'] != body.version:
            raise HTTPException(409, 'Lesson version changed', headers=PRIVATE_HEADERS)
        return row

    def local(value, lang):
        return value.get(lang, '') if isinstance(value, dict) else ''

    def projected(row, lang):
        image = row['preview_image']
        image_available = bool(image['file']) and lang in image.get('languages', [])
        question = row.get('check_question', {})
        return {
            'id': row['id'], 'version': row['version'], 'printed_page': row['printed_page'], 'pdf_page': row['pdf_page'],
            'part': row['index'].get('part'), 'section_no': row['index'].get('section_no'),
            # Original headings exist only in Norwegian; never leak them to TH/EN.
            'chapter': row['chapter'] if lang == 'no' else '',
            'section': row['section'] if lang == 'no' else '',
            'title': local(row.get('title'), lang), 'text': local(row.get('core_sentence'), lang),
            'points': [local(p, lang) for p in row.get('points', [])],
            'question': local(question.get('q'), lang),
            'options': [local(o, lang) for o in question.get('options', [])],
            'image_status': image['status'] if not image['file'] or image_available else 'image_translation_missing', 'review_status': row['review_status'],
            'has_unconfirmed': bool(row.get('open_questions')) or any(c.get('kind') == 'apent' for c in row.get('michael_claims', [])),
            'image_url': PREFIX + '/image/' + row['id'] + '/' + image['sha256'] if image_available else '',
            'image_sha256': image['sha256'], 'publication_approved': False,
        }

    @router.get('/enter', response_class=HTMLResponse)
    async def enter():
        # No book data here. Uses the existing webapp login token to establish an HttpOnly review session.
        return HTMLResponse((BASE / 'private_book_enter.html').read_text(encoding='utf8'), headers=PRIVATE_HEADERS)

    @router.post('/session')
    async def session(request: Request, user=Depends(reviewer)):
        authorization = request.headers.get('authorization', '')
        if not authorization.lower().startswith('bearer '):
            raise HTTPException(401, 'Bearer login required', headers=PRIVATE_HEADERS)
        token = authorization[7:]
        identity = verify_token(token)
        remaining = max(0, min(3600, int(identity.get('exp', 0)) - int(datetime.now(timezone.utc).timestamp())))
        response = Response(status_code=204, headers=PRIVATE_HEADERS)
        response.set_cookie(COOKIE, token, max_age=remaining, httponly=True, secure=request.url.scheme == 'https',
                            samesite='strict', path=PREFIX)
        return response

    @router.post('/logout')
    async def logout():
        response = Response(status_code=204, headers=PRIVATE_HEADERS)
        response.delete_cookie(COOKIE, path=PREFIX)
        return response

    @router.get('/view', response_class=HTMLResponse)
    async def view(language: Language = 'no', user=Depends(reviewer)):
        page = (BASE / 'private_book.html').read_text(encoding='utf8')
        page = page.replace('__HTML_LANG__', 'nb' if language == 'no' else language).replace('__LANG__', language)
        page = page.replace('__LANGUAGE_LABEL__', {'no': 'Språk', 'th': 'ภาษา', 'en': 'Language'}[language])
        return HTMLResponse(page, headers=PRIVATE_HEADERS)

    @router.get('/catalog')
    async def get_catalog(response: Response, language: Language = 'no', user=Depends(reviewer)):
        response.headers.update(PRIVATE_HEADERS)
        return {'rows': [projected(r, language) for r in rows.values()], 'language': language, 'review_only': True}

    @router.get('/image/{row_id}/{digest}')
    async def image(row_id: str, digest: str, user=Depends(reviewer)):
        row = rows.get(row_id)
        media = row.get('preview_image', {}) if row else {}
        filename = media.get('file', '')
        if not filename or media.get('sha256') != digest or Path(filename).name != filename:
            raise HTTPException(404, 'Image unavailable', headers=PRIVATE_HEADERS)
        try:
            path = await asyncio.to_thread(storage.image, filename, digest)
        except Exception:
            raise HTTPException(404, 'Image version mismatch', headers=PRIVATE_HEADERS)
        return FileResponse(path, headers=PRIVATE_HEADERS)

    @router.post('/attempt')
    async def begin(body: Begin, response: Response, user=Depends(reviewer)):
        row = row_for(body)
        question = row.get('check_question', {})
        if not local(question.get('q'), body.language) or not question.get('options') or any(not local(o, body.language) for o in question['options']):
            raise HTTPException(409, 'Missing translation', headers=PRIVATE_HEADERS)
        attempt_id = secrets.token_urlsafe(24)
        await get_db().private_book_attempts.insert_one({
            'id': attempt_id, 'owner_id': user['id'], 'row_id': row['id'], 'version': row['version'],
            'language': body.language, 'image_sha256': row['preview_image']['sha256'], 'used': False,
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=1),
        })
        response.headers.update(PRIVATE_HEADERS)
        return {'attempt_id': attempt_id}

    @router.post('/attempt/{attempt_id}/answer')
    async def answer(attempt_id: str, body: Answer, response: Response, user=Depends(reviewer)):
        row = row_for(body)
        options = row['check_question']['options']
        if not 0 <= body.option < len(options):
            raise HTTPException(422, 'Invalid option', headers=PRIVATE_HEADERS)
        record = await get_db().private_book_attempts.find_one_and_update({
            'id': attempt_id, 'owner_id': user['id'], 'row_id': row['id'], 'version': row['version'],
            'language': body.language, 'image_sha256': row['preview_image']['sha256'],
            'used': False, 'expires_at': {'$gt': datetime.now(timezone.utc)},
        }, {'$set': {'used': True, 'option': body.option}})
        if not record:
            raise HTTPException(409, 'Invalid, expired or already answered attempt', headers=PRIVATE_HEADERS)
        response.headers.update(PRIVATE_HEADERS)
        basis = teacher_payload(row, body.language, overrides)
        # This is the reviewed deterministic Michael explanation, not a claimed live model run.
        return {'correct': body.option == row['check_question']['answer'],
                'correct_option': row['check_question']['answer'], 'teacher': basis}

    @router.post('/attempt/{attempt_id}/michael')
    async def michael(attempt_id: str, body: Begin, response: Response, user=Depends(reviewer)):
        row = row_for(body)
        attempt = await get_db().private_book_attempts.find_one({
            'id': attempt_id, 'owner_id': user['id'], 'row_id': row['id'], 'version': row['version'],
            'language': body.language, 'image_sha256': row['preview_image']['sha256'],
            'used': True, 'expires_at': {'$gt': datetime.now(timezone.utc)},
        })
        if not attempt:
            raise HTTPException(409, 'Answered attempt required', headers=PRIVATE_HEADERS)
        payload = teacher_payload(row, body.language, overrides)
        media = row['preview_image']
        if media['file']:
            try:
                await asyncio.to_thread(storage.image, media['file'], media['sha256'])
            except Exception:
                raise HTTPException(409, 'Image version mismatch', headers=PRIVATE_HEADERS)
        if not payload['basis'] or complete is None:
            raise HTTPException(409, 'Controlled teacher basis unavailable', headers=PRIVATE_HEADERS)
        # Claim once atomically before calling the provider: replay cannot multiply model calls.
        claimed = await get_db().private_book_attempts.find_one_and_update({
            'id': attempt_id, 'owner_id': user['id'], 'model_called': {'$ne': True}, 'used': True,
        }, {'$set': {'model_called': True}})
        if not claimed:
            raise HTTPException(409, 'Explanation already requested', headers=PRIVATE_HEADERS)
        response.headers.update(PRIVATE_HEADERS)
        return {'reply': await complete(payload, attempt['option'], row['check_question']['answer']), 'model_generated': True}

    return router
