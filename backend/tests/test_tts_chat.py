"""Contract tests for Michael's ElevenLabs-first TTS routes."""

import base64
import hashlib
import json
import sys
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


@pytest.fixture
def tts_client(monkeypatch, tmp_path):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-elevenlabs-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    for name in (
        "ELEVENLABS_MODEL_ID", "ELEVENLABS_VOICE_ID",
        "ELEVENLABS_TH_VOICE_ID", "ELEVENLABS_NO_VOICE_ID", "ELEVENLABS_EN_VOICE_ID",
        "ELEVENLABS_VOICE_ID_TH", "ELEVENLABS_VOICE_ID_NO", "ELEVENLABS_VOICE_ID_EN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(server, "_TTS_PROVIDER_STATE", {})

    def cache_path(provider, voice, lang, text):
        key = hashlib.sha256(f"{provider}:{voice}:{lang}:{text}".encode()).hexdigest()
        return str(tmp_path / f"{key}.mp3")

    monkeypatch.setattr(server, "_tts_cache_path", cache_path)
    return TestClient(server.app)


@pytest.mark.parametrize(
    ("lang", "locale", "language_code"),
    [("th", "th-TH", "th"), ("no", "nb-NO", "no"), ("en", "en-US", "en")],
)
def test_all_languages_use_michael_clone_and_eleven_v3_first(
    monkeypatch, tts_client, lang, locale, language_code
):
    requests = []

    def handle(request):
        requests.append(request)
        assert request.url.host == "api.elevenlabs.io"
        return httpx.Response(200, content=b"ID3-michael-audio")

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handle))
    )

    response = tts_client.get("/api/tts", params={"text": "Test voice", "lang": lang})

    assert response.status_code == 200
    assert response.content == b"ID3-michael-audio"
    assert response.headers["x-tts-provider"] == "elevenlabs"
    assert len(set(server._DEFAULT_ELEVENLABS_VOICE_IDS.values())) == 1
    assert response.headers["x-tts-voice"] == server._DEFAULT_ELEVENLABS_VOICE_IDS[locale]
    assert len(requests) == 1
    payload = json.loads(requests[0].content)
    assert payload["model_id"] == "eleven_v3"
    assert payload["language_code"] == language_code
    assert payload["voice_settings"]["stability"] == 0.5
    assert payload["voice_settings"]["similarity_boost"] == 0.75
    if lang == "th":
        assert payload["voice_settings"]["style"] == 1.0
    else:
        assert "style" not in payload["voice_settings"]


def test_google_is_used_only_after_elevenlabs_failure(monkeypatch, tts_client):
    hosts = []

    def handle(request):
        hosts.append(request.url.host)
        if request.url.host == "api.elevenlabs.io":
            return httpx.Response(503, text="temporarily unavailable")
        assert request.url.host == "texttospeech.googleapis.com"
        return httpx.Response(
            200, json={"audioContent": base64.b64encode(b"ID3-google-audio").decode()}
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handle))
    )

    response = tts_client.get("/api/tts", params={"text": "Fallback test", "lang": "th"})

    assert response.status_code == 200
    assert response.content == b"ID3-google-audio"
    assert response.headers["x-tts-provider"] == "google"
    assert hosts == ["api.elevenlabs.io", "texttospeech.googleapis.com"]
