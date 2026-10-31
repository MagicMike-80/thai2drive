"""Check all four web culture comparisons and their translations."""
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from webapp import WEBAPP_HTML

TOPICS = ("priority", "right", "pedestrian", "dark")
FIELDS = ("title", "thailand", "norway", "action")


def test_comparison_cards_use_localized_fields():
    renderer = WEBAPP_HTML.split("function renderMicroLessons(container) {", 1)[1].split(
        "function toggleMicroLesson(id) {", 1
    )[0]
    for topic in TOPICS:
        for field in FIELDS:
            assert f"'{'micro_' + topic + '_' + field}'" in renderer
    for key in ("micro_in_thailand", "micro_in_norway"):
        assert f"t('{key}')" in renderer
    assert "escH(t(lesson.thailand))" in renderer
    assert "escH(t(lesson.norway))" in renderer


def test_comparison_text_has_no_language_bleed():
    keys = ("micro_in_thailand", "micro_in_norway") + tuple(
        f"micro_{topic}_{field}" for topic in TOPICS for field in FIELDS
    )
    for key in keys:
        line = next((line for line in WEBAPP_HTML.splitlines() if line.strip().startswith(key + ":{")), "")
        assert line, key
        match = re.search(r"th:'([^']+)', no:'([^']+)', en:'([^']+)'", line)
        assert match, key
        thai, norwegian, english = match.groups()
        assert re.search("[ก-๙]", thai), key
        assert not re.search("[A-Za-z]", thai), key
        assert not re.search("[ก-๙]", norwegian + english), key
