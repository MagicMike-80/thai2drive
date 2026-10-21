"""Explicit private-book teacher projection; never pass editorial notes to the model."""
from __future__ import annotations
import hashlib
import json
import re

LABEL = {
    'no': {'lov': 'Lovkrav', 'rettesnor': 'Rettesnor (ikke lovkrav)'},
    'th': {'lov': 'ข้อกำหนดตามกฎหมาย', 'rettesnor': 'แนวทาง (ไม่ใช่ข้อกำหนดตามกฎหมาย)'},
    'en': {'lov': 'Legal requirement', 'rettesnor': 'Guideline (not a legal requirement)'},
}


def controlled_basis(row, lang, overrides):
    """Reuse reviewed safe overrides and classified claims; never export open claims."""
    if lang not in LABEL:
        raise ValueError('Unsupported language')
    override = overrides.get('rows', {}).get(row['id'])
    if row.get('private_revision'):
        # Revisions must carry their own explicit controlled basis, not stale overrides.
        return row.get('private_teacher_basis', {}).get(lang, '')
    source = override if override is not None else row
    claims = source.get('claims', source.get('michael_claims'))
    if claims is not None:
        return '\n'.join(
            LABEL[lang][c['kind']] + ': ' + c.get('text', {}).get(lang, '')
            for c in claims if c.get('kind') in LABEL[lang] and c.get('text', {}).get(lang)
            and c.get('source') and re.fullmatch(r'\d{4}-\d{2}-\d{2}', c.get('checked_at', ''))
        )
    if source.get('has_unconfirmed') or (override is None and row.get('open_questions')):
        return ''
    # Raw legacy basis is an editorial draft, not a checked teaching rule.
    return ''


def basis_digest(row, overrides):
    basis = {lang: controlled_basis(row, lang, overrides) for lang in LABEL}
    return hashlib.sha256(json.dumps(basis, ensure_ascii=False, sort_keys=True).encode('utf8')).hexdigest()


def teacher_payload(row, lang, overrides):
    return {
        'id': row['id'], 'version': row['version'], 'language': lang,
        'printed_page': row['printed_page'], 'pdf_page': row['pdf_page'],
        'basis': controlled_basis(row, lang, overrides) if basis_digest(row, overrides) == row.get('teacher_basis_sha256') else '',
        'question': row.get('check_question', {}).get('q', {}).get(lang, ''),
        'options': [option.get(lang, '') for option in row.get('check_question', {}).get('options', [])],
        'image_sha256': row.get('preview_image', {}).get('sha256', ''),
        'publication_approved': False,
    }
