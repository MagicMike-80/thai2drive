"""M-01/M-02 reply preservation: fake Mongo, fake model, no learner data/network."""
import asyncio
import sys
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))


class Cursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, *args):
        return self

    async def to_list(self, length=None):
        return list(reversed(self.rows))[:length] if length else list(self.rows)


class Collection:
    def __init__(self):
        self.rows = []

    def find(self, *args, **kwargs):
        return Cursor(self.rows)

    def aggregate(self, *args, **kwargs):
        return Cursor([])

    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, row):
        self.rows.append(row)

    async def insert_many(self, rows):
        self.rows.extend(rows)


class Database:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, Collection())

    def __getattr__(self, name):
        return self[name]


# Prevent even the import-time construction of a real Mongo client or dotenv load.
with patch('dotenv.load_dotenv'), patch('motor.motor_asyncio.AsyncIOMotorClient', return_value={'thai2drive': Database()}), patch.dict('os.environ', {'DB_NAME': 'thai2drive', 'LITELLM_LOCAL_MODEL_COST_MAP': 'True'}):
    import backend.teacher_chat as tc


CASES = {
    'no': ('Jeg er usikker i et kryss. Forklar enkelt før du spør meg.',
           'Se etter skilt først. I et vanlig kryss gjelder høyreregelen.',
           'Du må vurdere trafikken før du kjører.', 'Hva ser du etter først?',
           'Er jeg klar til teoriprøven? Hvilke resultater kan du se?',
           'Jeg har ingen resultater om deg her. Start med en øvingsøkt.'),
    'th': ('ฉันไม่มั่นใจที่ทางแยก ช่วยสอนฉันทีละขั้นตอนครับ',
           'ดูป้ายก่อนครับ ทางแยกทั่วไปใช้กฎให้ทางรถด้านขวา',
           'ต้องดูการจราจรก่อนขับไปครับ', 'คุณจะดูอะไรก่อนครับ?',
           'ฉันพร้อมสอบหรือยัง คุณเห็นผลการฝึกของฉันไหมครับ?',
           'ผมยังไม่มีผลการฝึกของคุณครับ เริ่มจากการฝึกหนึ่งครั้งก่อนครับ'),
    'en': ('I am unsure at a junction. Explain simply before asking me.',
           'Look for signs first. An ordinary junction uses the right-hand rule.',
           'Check the traffic before moving.', 'What do you look for first?',
           'Am I ready for the theory test? Which results can you see?',
           'I have no results about you here. Start with one practice session.'),
}


@pytest.fixture
def chat():
    database = Database()
    model = AsyncMock()
    with ExitStack() as stack:
        stack.enter_context(patch.multiple(tc, _db=database, _chat_col=database['teacher_chats'], LLM_KEY='offline-fixture'))
        stack.enter_context(patch.object(tc, '_completion_with_fallback', model))
        stack.enter_context(patch.object(tc, 'send_admin_alert_email', side_effect=AssertionError('No email allowed')))
        # The full model entrypoint is mocked; also forbid accidental provider calls.
        stack.enter_context(patch('litellm.acompletion', side_effect=AssertionError('No live model allowed')))
        yield database, model


def invoke(chat, language, message, reply, mode='normal_chat', **context):
    database, model = chat
    model.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=reply))])
    request = tc.TeacherChatRequest(session_id='offline-synthetic', message=message, language=language, mode=mode, **context)
    return asyncio.run(tc.teacher_chat(request))


@pytest.mark.parametrize('language', CASES)
@pytest.mark.parametrize('question', [False, True])
@pytest.mark.parametrize('old_stage', ['1', '5'])
def test_normal_explanation_survives_multiple_turns_and_old_stage(chat, language, question, old_stage):
    message, first, second, followup, _, _ = CASES[language]
    expected = first + '\n\n' + second + ('\n\n' + followup if question else '')
    chat[0]['teacher_chats'].rows.append({'role': 'assistant', 'content': 'old synthetic turn', 'v4_stage': old_stage})
    for _ in range(3):
        result = invoke(chat, language, message, expected)
        assert result.reply == expected
        system = chat[1].await_args.args[0][0]['content']
        assert 'ORDINARY CHAT' in system
        assert 'LEARNING EVIDENCE' in system
        assert 'MICHAEL V4 CURRENT STAGE' not in system
        assert 'Withhold the answer, explanation' not in system


@pytest.mark.parametrize('language', CASES)
def test_readiness_without_data_keeps_honest_answer_not_welcome(chat, language):
    *_, message, expected = CASES[language]
    assert invoke(chat, language, message, expected).reply == expected


@pytest.mark.parametrize('language', CASES)
def test_explicit_quiz_still_uses_guided_response(chat, language):
    message, first, second, question, _, _ = CASES[language]
    result = invoke(chat, language, message + '\n<quiz_context>Synthetic junction question</quiz_context>',
                    first + '\n\n' + question, mode='quiz_coach')
    expected = {'no': 'Se etter skilt først. Hva ser du etter først?',
                'th': question, 'en': 'Look for signs first. What do you look for first?'}[language]
    assert result.reply == expected
    assert chat[0]['teacher_chats'].rows[-1]['v4_stage'] == '1'
    assert 'MICHAEL V4 CURRENT STAGE' in chat[1].await_args.args[0][0]['content']


@pytest.mark.parametrize('language', CASES)
@pytest.mark.parametrize('failure', ['empty', 'exception'])
def test_provider_failure_is_localized_error_not_welcome(chat, language, failure):
    if failure == 'exception':
        chat[1].side_effect = TimeoutError('synthetic timeout')
    result = invoke(chat, language, CASES[language][0], '')
    assert result.reply == tc._fallback_reply(language)


@pytest.mark.parametrize('language', CASES)
def test_concrete_question_with_existing_weakness_keeps_explanation(chat, language):
    message, first, second, question, _, _ = CASES[language]
    expected = first + '\n\n' + second + '\n\n' + question
    memory = {'weak_topic': {'name': 'synthetic topic', 'accuracy': 0.3, 'total': 10},
              'total_attempts': 10, 'accuracy_pct': 30, 'is_returning': True}
    with patch.object(tc, 'fetch_student_learning_memory', AsyncMock(return_value=memory)):
        assert invoke(chat, language, message, expected).reply == expected


def test_existing_thai_direct_explanation_contract_stays_concise(chat):
    message = 'ฉันไม่มั่นใจที่ทางแยก ช่วยอธิบายก่อนถามฉันครับ'
    first, second = CASES['th'][1:3]
    assert invoke(chat, 'th', message, first + '\n\n' + second).reply == first + ' ' + second


@pytest.mark.parametrize('mode', ['weak_topics', 'vision', 'simplify'])
def test_marked_guided_conversation_continues_then_releases_normal_chat(chat, mode):
    history = chat[0]['teacher_chats']
    context = {'document_context': 'Synthetic junction description without learner data.'} if mode == 'vision' else {}
    invoke(chat, 'no', 'Jeg vil se på situasjonen videre.', 'Se på trafikken.\n\nHva legger du merke til?',
           mode='normal_chat' if mode == 'vision' else mode, **context)
    assert history.rows[-1]['v4_stage'] == ('1' if mode == 'vision' else '0')
    assert history.rows[-1]['guided_mode'] == mode
    for stage in (('3', '5') if mode == 'vision' else ('0.1', '0.2', '1', '3', '5')):
        invoke(chat, 'no', 'Jeg vil se på situasjonen videre.', 'Se på trafikken.\n\nHva legger du merke til?')
        assert history.rows[-1]['v4_stage'] == stage
        assert history.rows[-1]['guided_mode'] == mode
    expected = 'Jeg har ingen resultater om deg her. Start med en øvingsøkt.'
    assert invoke(chat, 'no', CASES['no'][4], expected).reply == expected
