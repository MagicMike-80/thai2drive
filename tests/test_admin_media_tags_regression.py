"""Regression coverage for the admin media tag validation."""
from pathlib import Path


ADMIN = (Path(__file__).resolve().parents[1] / "backend" / "admin.html").read_text(encoding="utf-8")


def test_media_form_marks_tags_required_and_stops_before_request():
    """Empty tags must be rejected in the form before the backend request."""
    function = ADMIN[ADMIN.index("async function saveAdminMedia"):ADMIN.index("async function uploadAdminMediaFile")]

    assert "Emnetagger (kommaseparert, påkrevd)" in ADMIN
    assert "if (!tags.length)" in function
    assert "Minst én emnetagg er påkrevd" in function
    assert function.index("if (!tags.length)") < function.index("await fetch(url")
