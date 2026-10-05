import json
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from webapp import webapp_router  # noqa: E402

app = FastAPI()
app.include_router(webapp_router)
client = TestClient(app)


class FlippFloppPageTests(unittest.TestCase):
    def test_page_is_rendered_in_requested_language(self):
        for lang, html_lang in (("no", "nb"), ("th", "th"), ("en", "en")):
            with self.subTest(lang=lang):
                response = client.get(f"/{lang}/flipp-flopp")
                self.assertEqual(response.status_code, 200)
                self.assertIn(f'<html lang="{html_lang}"', response.text)
                self.assertIn('hreflang="th" href="/th/flipp-flopp"', response.text)
                self.assertIn('hreflang="en" href="/en/flipp-flopp"', response.text)
                self.assertNotIn("__FLIPP_FLOPP_LANG__", response.text)
                self.assertIn("flipp_flopp_training_loop.mp3", response.text)
                self.assertIn("flipp_flopp_test_loop.mp3", response.text)

    def test_unknown_language_fails_closed(self):
        self.assertEqual(client.get("/fr/flipp-flopp").status_code, 404)

    def test_all_scenario_cards_have_complete_no_th_en_copy_and_images(self):
        cards = json.loads((BACKEND / "public_assets" / "flipp_flopp_cards.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cards), 10)
        self.assertEqual(sum(card["truth"] for card in cards), 5)
        for card in cards:
            for key in ("statement", "answer", "explanation", "alt"):
                for lang in ("no", "th", "en"):
                    self.assertTrue(card[key][lang].strip(), (card["id"], key, lang))
            self.assertTrue((BACKEND / "public_assets" / card["image"]).is_file())

    def test_each_mapped_audio_asset_exists(self):
        assets = BACKEND / "public_assets"
        for name in (
            "flashcard_intro.mp3", "flashcard_flip.mp3", "flashcard_sonar.mp3",
            "michael_correct_applause.mp3", "michael_round_complete.mp3",
            "michael_age_rule_chime.mp3", "flipp_flopp_clock.mp3", "flipp_flopp_wrong_fallback.mp3", "flipp_flopp_training_loop.mp3",
            "flipp_flopp_test_loop.mp3", "flipp_flopp_test_siren.mp3",
        ):
            self.assertTrue((assets / name).is_file(), name)

    def test_answer_feedback_has_distinct_visual_and_wrong_answer_audio(self):
        html = (BACKEND / "flipp_flopp.html").read_text(encoding="utf-8")
        self.assertIn("answer-correct", html)
        self.assertIn("answer-wrong", html)
        self.assertIn("function wrongHorn()", html)
        self.assertIn("wrongHorn();feedback(S.answers[S.index]);", html)
        self.assertIn("classList.remove(\u0027urgent\u0027)", html)
        self.assertIn("AUDIO[kind]=new Audio(SOUND[kind])", html)
        self.assertIn("S.clock=playTrack(a)", html)
        self.assertIn("function ensureLoops()", html)
        self.assertIn("if(S.muted)return;ensureLoops();try{var A=window.AudioContext", html)
        self.assertIn("S.introTimeout=setTimeout(startAudio,ms)", html)
        self.assertIn("document.addEventListener('visibilitychange'", html)
        self.assertIn("ageRule:s.ageRule===true||s.age_rule===true", html)
        self.assertIn("intro.addEventListener(\u0027error\u0027,startAudio", html)
        self.assertIn("fmt(t('result'),{score:String(score),total:String(S.deck.length)})", html)
        self.assertIn("var button=e.target.closest('button');if(button&&button.id!=='imageButton')return", html)
        self.assertIn("sound(S.mode==='test'?'testEntry':'entry')", html)
        self.assertIn("flipp_flopp_master.json", html)
        master = json.loads((BACKEND / "public_assets" / "flipp_flopp_master.json").read_text(encoding="utf-8"))
        self.assertEqual(len(master), 100)
        self.assertEqual([card["source_id"] for card in master], list(range(1, 101)))
        self.assertTrue(all(card["preview"] for card in master))
        for card in master:
            self.assertTrue((BACKEND / "public_assets" / card["image"]).is_file())
            for key in ("statement", "answer", "explanation", "alt"):
                for lang in ("no", "th", "en"):
                    self.assertTrue(card[key][lang].strip(), (card["id"], key, lang))

    def test_home_entry_uses_the_selected_app_language(self):
        webapp = (BACKEND / "webapp.py").read_text(encoding="utf-8")
        self.assertIn("location.href='/' + appLang + '/flipp-flopp'", webapp)
        self.assertNotIn("location.pathname.split('/')[1] + '/flipp-flopp'", webapp)
        self.assertIn("location.href='/' + appLang + '/flipp-flopp?pack=signs'", webapp)

    def test_home_and_sign_entries_have_separate_card_sources(self):
        html = (BACKEND / "flipp_flopp.html").read_text(encoding="utf-8")
        self.assertIn("var SIGN_GAME=new URLSearchParams(location.search).get('pack')==='signs'", html)
        self.assertIn('<div class="field" hidden><label for="packSelect"', html)
        self.assertNotIn('<option value=\\"mixed\\">', html)
        self.assertNotIn('<option value=\\"scenes\\">', html)
        self.assertIn("S.signs=SIGN_GAME?buildSigns(x[1]):[]", html)
        self.assertIn("S.master=SIGN_GAME?[]:validatedMaster(x[2])", html)
        self.assertIn("SIGN_GAME?S.signs:(S.master.length>=50?S.master:S.scenes)", html)

    def test_non_norwegian_legal_references_omit_norwegian_number_label(self):
        html = (BACKEND / "flipp_flopp.html").read_text(encoding="utf-8")
        self.assertIn("LANG==='no'?rawRef:'§ '+citation[1]", html)
        self.assertIn("(citation[2]?' ('+citation[2]+')':'')", html)
        self.assertNotIn("LANG==='no'?rawRef:citation[0]", html)

    def test_service_worker_does_not_cache_app_or_game_routes(self):
        service_worker = (BACKEND / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("thai2drive-offline-v1.0.8", service_worker)
        self.assertIn(r"/^\/(?:no|th|en)\/(?:app|flipp-flopp)\/?$/", service_worker)


if __name__ == "__main__":
    unittest.main()
