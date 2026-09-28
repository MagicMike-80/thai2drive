import asyncio
import base64
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.teacher_chat as tc
from backend.teacher_chat import TeacherChatRequest, teacher_chat

WEBAPP = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")


class _Cursor:
    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return []


class _Collection:
    def find(self, *args, **kwargs):
        return _Cursor()

    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, *args, **kwargs):
        return None

    async def insert_many(self, *args, **kwargs):
        return None


class _Database:
    def __getitem__(self, name):
        return _Collection()

    def __getattr__(self, name):
        return _Collection()


PNG_DATA = "data:image/png;base64," + base64.b64encode(
    b"\x89PNG\r\n\x1a\n" + b"test-image"
).decode("ascii")


def test_image_payload_validation_accepts_supported_data_and_rejects_unsafe_sources():
    assert tc._validate_vision_image(None, PNG_DATA) == PNG_DATA

    with pytest.raises(HTTPException) as both:
        tc._validate_vision_image("https://example.com/a.png", PNG_DATA)
    assert both.value.status_code == 400

    with pytest.raises(HTTPException):
        tc._validate_vision_image("http://127.0.0.1/private.png", None)
    with pytest.raises(HTTPException):
        tc._validate_vision_image(None, "data:image/png;base64,bm90LXBuZw==")


def test_vision_model_routing_excludes_text_only_models():
    assert not tc._model_supports_vision("deepseek/deepseek-chat")
    assert tc._model_supports_vision("openrouter/google/gemini-2.5-flash")
    assert tc._model_supports_vision("gpt-4o-mini")


@pytest.mark.parametrize(
    ("lang", "message", "required_sections"),
    [
        ("no", "Hva gjelder her?", ("Situasjon / Vikeplikt / Farepunkter / Teoriprøven",)),
        ("th", "ในภาพนี้ใครต้องให้ทางครับ", ("สถานการณ์ / การให้ทาง / จุดอันตราย / ข้อสอบทฤษฎี",)),
        ("en", "Who has right-of-way here?", ("Situation / Right-of-way / Hazards / Theory test",)),
    ],
)
def test_vision_chat_builds_multimodal_message_with_language_pure_safety_contract(
    lang, message, required_sections
):
    captured = {}

    async def complete(messages, require_vision=False):
        captured["messages"] = messages
        captured["require_vision"] = require_vision
        replies = {
            "no": "Bildet gir ikke nok informasjon til å avgjøre vikeplikten. Skilt og vegoppmerking mangler.",
            "th": "ภาพนี้มีข้อมูลไม่เพียงพอที่จะตัดสินเรื่องการให้ทาง เพราะมองไม่เห็นป้ายและเครื่องหมายบนถนนครับ",
            "en": "The image does not provide enough information to determine right-of-way. Signs and road markings are missing.",
        }
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=replies[lang]))]
        )

    request = TeacherChatRequest(message=message, language=lang, image_data=PNG_DATA)
    with patch.object(tc, "_db", _Database()), patch.object(tc, "_chat_col", _Collection()), patch.object(
        tc, "LLM_KEY", "test-key"
    ), patch.object(tc, "_completion_with_fallback", new=complete):
        response = asyncio.run(teacher_chat(request))

    assert captured["require_vision"] is True
    user_content = captured["messages"][-1]["content"]
    assert user_content[0] == {"type": "text", "text": message}
    assert user_content[1]["type"] == "image_url"
    assert user_content[1]["image_url"]["url"] == PNG_DATA

    prompt = captured["messages"][0]["content"]
    assert "Never invent hidden signs" in prompt
    assert "does not provide enough information" in prompt
    assert "Vegtrafikkloven § 3" in prompt
    assert "Vegtrafikkloven § 7" in prompt
    assert "Skiltforskriften" in prompt
    for section in required_sections:
        assert section in prompt
    other_headings = {
        "no": ("สถานการณ์ / การให้ทาง", "Situation / Right-of-way"),
        "th": ("Situasjon / Vikeplikt", "Situation / Right-of-way"),
        "en": ("Situasjon / Vikeplikt", "สถานการณ์ / การให้ทาง"),
    }[lang]
    assert all(heading not in prompt for heading in other_headings)
    assert response.reply


def test_request_schema_accepts_public_image_url_for_backward_compatible_chat():
    request = TeacherChatRequest(
        message="Analyse this image", language="en", image_url="https://example.com/junction.webp"
    )
    assert request.image_url.endswith("junction.webp")
    assert request.image_data is None


def test_web_chat_converts_supported_images_and_sends_them_in_chat_payload():
    assert "reader.readAsDataURL(file)" in WEBAPP
    assert "file.size > 4 * 1024 * 1024" in WEBAPP
    assert "chatPayload.image_data = _teacherUploadedImage.data" in WEBAPP
    assert "if (!msg && _teacherUploadedImage) msg = t('teacher_image_prompt')" in WEBAPP
    assert "if (_teacherUploadedImage) _teacherClearDoc()" in WEBAPP


def test_web_image_labels_are_present_in_all_three_languages():
    for key in ("teacher_image_ready", "teacher_image_error", "teacher_image_prompt"):
        match = __import__("re").search(rf"{key}:\{{([^\r\n]+)\}}", WEBAPP)
        assert match, f"Missing UI key {key}"
        value = match.group(1)
        assert "th:" in value
        assert "no:" in value
        assert "en:" in value
