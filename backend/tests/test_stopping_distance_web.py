"""Offline contracts for the web screen and its real deterministic API."""
import re
import json
import subprocess
import shutil
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stopping_distance_web import CSS, HOME, SCREEN, SCRIPT, install
from webapp import WEBAPP_HTML, webapp_router
from traffic_math_routes import math_router
import traffic_math

app = FastAPI()
app.include_router(webapp_router, prefix='/api')
app.include_router(math_router, prefix='/api')
client = TestClient(app)


def test_real_home_placement_and_existing_actions():
    html = client.get('/api/web').text
    assert html.index('id="startExamBtn"') < html.index('id="stoppingHomeBtn"') < html.index('<div class="home-main-actions">')
    assert 'onclick="startRandomQuiz()"' in html
    assert 'onclick="startExam()"' in html
    assert 'src="/api/assets/developer-icon-512.png"' in html
    assert html.count('id="screenStopping"') == 1
    assert "stopping:'screenStopping'" in html
    assert "if (tab === 'stopping')  loadStopping(false)" in html


def test_wide_web_screen_and_all_controls():
    assert 'width:min(1100px,96vw)' in CSS
    assert 'grid-template-columns:1fr' in CSS
    assert 'prefers-reduced-motion' in CSS and 'prefers-reduced-motion' in SCRIPT
    for speed in (30, 50, 80, 100, 120):
        assert f'data-speed="{speed}"' in SCREEN
    for condition in ('dry', 'wet', 'snow', 'ice'):
        assert f'data-condition="{condition}"' in SCREEN
    assert 'data-seconds="2"' in SCREEN and 'data-seconds="3"' in SCREEN
    assert 'aria-expanded="false"' in SCREEN
    assert 'closeStopping()' in SCREEN
    assert 'tesla-red' in HOME and 'tesla-road' in SCREEN
    assert 'reaction=1' in SCRIPT
    assert 'car.animate' in SCRIPT
    assert 'request!==stoppingState.request' in SCRIPT
    assert "stopEl('stopResults').hidden=true" in SCRIPT
    assert 'throw new Error' in SCRIPT


def test_every_new_label_has_three_languages_without_fallback():
    entries = re.findall(r'(stop_\w+):\{([^}]+)\}', SCRIPT)
    assert len(entries) >= 20
    keys = {key for key, _ in entries}
    for key, value in entries:
        for lang in ('no', 'th', 'en'):
            assert re.search(rf"{lang}:'[^']+'", value), (key, lang)
    for key in re.findall(r'data-key="(stop_\w+)"', SCREEN + HOME):
        assert key in keys
    assert "note[appLang] || ''" in SCRIPT
    assert "label[appLang] || ''" in SCRIPT
    assert '|| TR.' not in SCRIPT and '|| UI.' not in SCRIPT


def test_existing_math_all_speeds_and_conditions():
    for speed in (30, 50, 80, 100, 120):
        for condition, multiplier in [('dry', 1), ('wet', 2), ('snow', 4), ('ice', 8)]:
            response = client.get('/api/math/stopping-distance', params={'speed': speed, 'condition': condition, 'reaction': 1})
            assert response.status_code == 200
            data = response.json()
            r = data['results']
            assert r['braking_distance_m'] == (speed / 10) ** 2 * multiplier
            assert r['stopping_distance_m'] == round(r['reaction_distance_m'] + r['braking_distance_m'], 1)
            assert len(data['steps']) == 4
            for step in data['steps']:
                assert all(step['label'][lang] for lang in ('no', 'th', 'en'))
    r = client.get('/api/math/stopping-distance?speed=80&condition=dry&reaction=1').json()['results']
    assert (r['reaction_distance_m'], r['braking_distance_m'], r['stopping_distance_m']) == (22.2, 64.0, 86.2)
    for seconds, expected in [(2, 44.4), (3, 66.7)]:
        data = client.get(f'/api/math/following-distance?speed=80&seconds={seconds}').json()
        assert data['results']['following_distance_m'] == expected


def test_install_does_not_remove_any_existing_markup():
    rendered = install(WEBAPP_HTML)
    assert rendered.replace(CSS + '\n', '', 1).replace(HOME + '\n', '', 1).replace(SCREEN + '\n', '', 1).replace(SCRIPT + '\n', '', 1) == WEBAPP_HTML


def test_assets_exist():
    assets = Path(__file__).resolve().parents[1] / 'public_assets'
    for filename in ('stopping-distance-teslas-v1.png', 'stopping-distance-road-v1.png'):
        assert (assets / filename).stat().st_size > 1000


def test_actual_javascript_behaviors():
    node = shutil.which('node')
    assert node, 'Node is required for the executable JavaScript regression test'
    harness = Path(__file__).with_name('stopping_distance_harness.cjs')
    payload = {'script': SCRIPT, 'payloads': [traffic_math.stopping_distance_full(80, 'dry'), traffic_math.following_distance(80, 2)]}
    result = subprocess.run([node, str(harness)], input=json.dumps(payload), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS' in result.stdout
