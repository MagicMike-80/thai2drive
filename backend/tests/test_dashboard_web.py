"""Offline web Dashboard wiring and language-isolation contracts."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from webapp import WEBAPP_HTML, webapp_router


app = FastAPI()
app.include_router(webapp_router, prefix="/api")
client = TestClient(app)


def test_dashboard_is_reachable_from_home_without_premium_gate():
    html = client.get("/api/web/th").text
    assert 'id="screenDashboard"' in html
    assert 'onclick="showTab(\'dashboard\')"' in html
    assert "dashboard:'screenDashboard'" in html
    assert "if (tab === 'dashboard') loadDashboard();" in html
    assert "var premiumTabs = ['history', 'signs', 'bookmarks'];" in html


def test_dashboard_uses_selected_language_and_localized_api_fields():
    assert "'/api/user/dashboard?lang=' + encodeURIComponent(appLang)" in WEBAPP_HTML
    assert "data.lang !== appLang" in WEBAPP_HTML
    assert "escH(data.readiness.status || '')" in WEBAPP_HTML
    assert "escH(topic.name || '')" in WEBAPP_HTML
    assert "escH(topic.advice)" in WEBAPP_HTML
    assert "escH(session.mode_label || '')" in WEBAPP_HTML
    assert "escH(session.category_name || '')" in WEBAPP_HTML
    assert "escH(t('history_load_error'))" in WEBAPP_HTML


def test_home_video_button_uses_existing_language_key():
    assert 'data-key="lib_videos"' in WEBAPP_HTML
    assert 'data-key="home_open_library"' not in WEBAPP_HTML
    assert 'data-key="library_sub"' not in WEBAPP_HTML
