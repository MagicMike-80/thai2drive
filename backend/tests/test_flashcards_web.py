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


def test_flashcard_sounds_use_local_assets_and_can_be_muted():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "window.AudioContext || window.webkitAudioContext" in source
    assert "context.createBuffer(1, length, context.sampleRate)" in source
    assert "function flashcardPlaySfx(kind)" in source
    assert "function toggleFlashcardSfxMute()" in source
    assert "aria-pressed', _flashcardSfxMuted ? 'true' : 'false'" in source
    assert "if (_flashcardSfxMuted) return;" in source
    assert "new Audio('/api/assets/flashcard_' + kind + '.mp3')" in source
    assert "flashcardPlayTrack('intro')" in source
    assert "var _flashcardPendingSfx = '';" in source
    assert "_flashcardPendingSfx = kind;" in source
    assert "function flashcardAfterNarration(labelKey)" in source


def test_flashcard_flip_and_confidence_choices_trigger_their_own_sfx():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "flashcardPlayTrack('flip')" in source
    assert "flashcardPlaySfx(choice)" in source
    assert "if (kind === 'know')" in source
    assert "kind === 'unsure' ? 430 : 330" in source
    assert "function resetFlashcardConfidence()" in source


def test_flashcard_confidence_choices_and_mute_are_localized():
    source = WEBAPP.read_text(encoding="utf-8")

    assert "fc_know:" in source and "no:'Kan det'" in source and "en:'I know it'" in source
    assert "fc_unsure:" in source and "no:'Usikker'" in source and "en:'Not sure'" in source
    assert "fc_cant:" in source and "no:'Kan ikke'" in source and "en:'Not yet'" in source
    assert "fc_sound_on:" in source and "fc_sound_off:" in source
