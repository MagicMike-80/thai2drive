"""The Railway pre-deploy gate verifies quiz data without modifying it."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import patch_exam_question_content as script


@pytest.mark.parametrize('environment', ['production', 'unexpected', ''])
@pytest.mark.parametrize('valid', [True, False])
def test_production_apply_is_read_only(monkeypatch, valid, environment):
    monkeypatch.setattr(Path, 'is_file', lambda _: True)
    monkeypatch.setattr(script, 'load_dotenv', lambda _: None)
    monkeypatch.setenv('MONGO_URL', 'mongodb://not-used')
    monkeypatch.setenv('DB_NAME', 'synthetic')
    monkeypatch.setenv('RAILWAY_ENVIRONMENT_NAME', environment)
    monkeypatch.setattr(sys, 'argv', ['patch_exam_question_content.py', '--apply'])
    questions = MagicMock()
    values = {script.RAILWAY_QUESTION_ID:{'bildeUrl':script.RAILWAY_IMAGE_URL},
              **{qid:{'active':False} for qid in script.HELD_QUESTION_IDS}}
    if not valid:
        values[script.HELD_QUESTION_IDS[0]] = {'active':True}
    questions.find_one.side_effect = lambda query, projection: values.get(query['id'])
    client = MagicMock()
    client.__getitem__.return_value = SimpleNamespace(questions=questions)
    monkeypatch.setattr(script, 'MongoClient', lambda *args, **kwargs: client)
    if valid:
        script.main()
    else:
        with pytest.raises(RuntimeError, match='verification failed'):
            script.main()
    questions.update_one.assert_not_called()
    client.close.assert_called_once()


def test_explicit_manual_override_preserves_repair_capability(monkeypatch):
    monkeypatch.setattr(Path, 'is_file', lambda _: True)
    monkeypatch.setattr(script, 'load_dotenv', lambda _: None)
    monkeypatch.setenv('MONGO_URL', 'mongodb://not-used')
    monkeypatch.setenv('DB_NAME', 'synthetic')
    monkeypatch.setattr(sys, 'argv', ['patch_exam_question_content.py', '--apply', '--allow-quiz-write'])
    client = MagicMock()
    client.__getitem__.return_value = SimpleNamespace(questions=MagicMock())
    monkeypatch.setattr(script, 'MongoClient', lambda *args, **kwargs: client)
    patch = MagicMock(return_value=[])
    verify = MagicMock()
    monkeypatch.setattr(script, 'patch_questions', patch)
    monkeypatch.setattr(script, 'verify_questions', verify)
    script.main()
    assert patch.call_args.kwargs == {'apply': True}
    verify.assert_called_once()
