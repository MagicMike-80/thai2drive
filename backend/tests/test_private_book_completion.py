"""Offline completion boundary tests; fake modules prevent production runtime imports."""
import asyncio
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from private_book_completion import complete_private_book


@pytest.fixture
def provider(monkeypatch):
    teacher = ModuleType('teacher_chat')
    teacher.LLM_ATTEMPTS = [{'model': 'offline-model', 'api_key': 'SECRET_KEY'}]
    lite = ModuleType('litellm')
    calls = []
    state = {'text': 'Slow down.', 'finish': 'stop', 'error': None}

    async def complete(**kwargs):
        calls.append(kwargs)
        if state['error']:
            raise state['error']
        return SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=state['text']), finish_reason=state['finish'])])

    lite.acompletion = complete
    monkeypatch.setitem(sys.modules, 'teacher_chat', teacher)
    monkeypatch.setitem(sys.modules, 'litellm', lite)
    return teacher, calls, state


def payload(lang='en'):
    return {'language': lang, 'printed_page': 22, 'pdf_page': 17,
            'id': 'bb-s22', 'version': '123456789abc', 'basis': 'CONTROLLED_BASIS',
            'question': 'QUESTION', 'options': ['A', 'B', 'C']}


@pytest.mark.parametrize('lang,text,label', [
    ('no', 'Senk farten.', 'Norwegian'), ('en', 'Slow down.', 'English'),
    ('th', '\u0e25\u0e14\u0e04\u0e27\u0e32\u0e21\u0e40\u0e23\u0e47\u0e27', 'Thai')])
def test_localized_success_and_bounded_provider_call(provider, lang, text, label):
    _, calls, state = provider
    state['text'] = '  ' + text + '  '
    assert asyncio.run(complete_private_book(payload(lang), 1, 0)) == text
    assert len(calls) == 1
    call = calls[0]
    assert call['model'] == 'offline-model'
    assert call['max_tokens'] == 450 and call['num_retries'] == 0
    assert call['timeout'] <= 30
    instruction = call['messages'][0]['content']
    for fragment in (label, 'CONTROLLED_BASIS', 'bb-s22', '123456789abc', '22', '17', 'Selected option B', 'correct option A', 'SERVER_RESULT: INCORRECT'):
        assert fragment in instruction
    assert 'ONLY the controlled basis' in instruction
    assert 'QUESTION' in instruction and '"options_by_label": {"A": "A", "B": "B", "C": "C"}' in instruction
    assert '"selected_text": "B"' in instruction and '"correct_text": "A"' in instruction


def test_missing_provider_fails_without_completion(provider):
    teacher, calls, _ = provider
    teacher.LLM_ATTEMPTS = []
    with pytest.raises(HTTPException) as error:
        asyncio.run(complete_private_book(payload(), 0, 0))
    assert error.value.status_code == 503 and calls == []


@pytest.mark.parametrize('lang,text,finish', [
    ('en', '', 'stop'), ('en', None, 'stop'), ('en', 'partial', 'length'),
    ('en', '\u0e44\u0e17\u0e22', 'stop'), ('no', '\u0e44\u0e17\u0e22', 'stop'),
    ('th', 'English only', 'stop'), ('th', '\u0e44\u0e17\u0e22 English', 'stop')])
def test_empty_truncated_and_wrong_script_responses_fail_closed(provider, lang, text, finish):
    _, _, state = provider
    state.update(text=text, finish=finish)
    with pytest.raises(HTTPException) as error:
        asyncio.run(complete_private_book(payload(lang), 0, 0))
    assert error.value.status_code == 503
    assert error.value.detail == 'Private explanation unavailable'


@pytest.mark.parametrize('failure', [RuntimeError('SECRET_KEY raw prompt'), asyncio.TimeoutError('SECRET_KEY')])
def test_provider_errors_and_timeout_are_redacted(provider, failure):
    _, calls, state = provider
    state['error'] = failure
    with pytest.raises(HTTPException) as error:
        asyncio.run(complete_private_book(payload(), 0, 0))
    assert len(calls) == 1
    assert error.value.status_code == 503
    assert 'SECRET' not in error.value.detail


@pytest.mark.parametrize('lang,text', [('no', 'Du valgte riktig svar.'), ('th', 'คุณเลือกข้อหนึ่งถูกต้องแล้ว'),
                                      ('en', 'You chose the correct answer.')])
def test_real_provider_regrading_regression_fails_closed(provider, lang, text):
    _, _, state = provider
    state['text'] = text
    with pytest.raises(HTTPException) as error:
        asyncio.run(complete_private_book(payload(lang), 1, 0))
    assert error.value.status_code == 503
