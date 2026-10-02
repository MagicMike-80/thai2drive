"""Contract checks for the web-first glossary flashcards."""
from pathlib import Path


WEBAPP = Path(__file__).resolve().parents[1] / "webapp.py"


def test_flashcards_load_the_existing_glossary_for_the_selected_language():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "api('GET', '/api/glossary?lang=' + encodeURIComponent(appLang))" in source
    assert "var termKey = 'term_' + appLang;" in source
    assert "var definitionKey = 'definition_' + appLang;" in source
    assert "typeof term[termKey] === 'string'" in source
    assert "typeof term[definitionKey] === 'string'" in source


def test_flashcards_use_an_accessible_responsive_3d_flip():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "perspective:1200px" in source
    assert "transform-style:preserve-3d" in source
    assert "rotateY(180deg)" in source
    assert "prefers-reduced-motion:reduce" in source
    assert 'aria-modal="true"' in source
    assert "aria-hidden" in source


def test_flip_controls_and_audio_have_thai_norwegian_and_english_labels():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "fc_flip:               {th:'ดูคำอธิบาย', no:'Snu kortet', en:'Flip card'}" in source
    assert "fc_audio_play:" in source
    assert "fc_previous:" in source
    assert "fc_next:" in source
    assert "ttsStreamUrl(spokenText, appLang)" in source


def test_card_content_is_inserted_as_text_and_keeps_norwegian_term_on_back():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "flashcardFrontTerm').textContent = front" in source
    assert "flashcardDefinition').textContent = definition" in source
    assert "flashcardNorwegianTerm').textContent = t('fc_norwegian_term') + ': ' + wordNo" in source
