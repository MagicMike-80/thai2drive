"""Execute the real question-option renderer with synthetic data, offline.

No application/server import, database client, browser or HTTP request is used.
The renderer block and its actual helpers are extracted from WEBAPP_HTML.
"""
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import unittest


class QuestionLanguageIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (Path(__file__).resolve().parents[1] / "webapp.py").read_text(encoding="utf-8")
        html = next(
            ast.literal_eval(node.value)
            for node in ast.parse(source).body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "WEBAPP_HTML" for target in node.targets)
        )
        names = ("pickStrict", "pickLang", "pickField", "pickQuestionLang",
                 "pickFieldForQuestion", "questionOptionText", "shuffleOpts")
        functions = []
        for name in names:
            match = re.search(r"function " + name + r"\([^)]*\) \{.*?\n\}", html, re.S)
            if not match:
                raise AssertionError(f"Missing actual renderer helper: {name}")
            functions.append(match.group(0))
        render = html.split("function renderQuestion() {", 1)[1]
        options = "var opts = [];" + render.split("var opts = [];", 1)[1].split("var chosenOption", 1)[0]
        cls.script = "\n".join(functions) + """
var appLang = 'no', isExamMode = false, currentCorrect = '', randomCalls = 0;
// Deterministic Fisher-Yates input; the production shuffle implementation runs.
Math.random = function() { randomCalls++; return 0; };
function renderOptions(q) {
  currentCorrect = (q.correctOptionId || q.correct_answer || '').toUpperCase();
""" + options + """
  return JSON.parse(JSON.stringify({options: opts, cachedOptions: q._shuffledOpts.opts,
                                   correct: currentCorrect, randomCalls: randomCalls}));
}
function translated(id) { return {no:'NO_' + id, th:'ไทย_' + id, en:'EN_' + id}; }
function structuredQuestion() {
  return {correctOptionId:'B', options:['A','B','C','D'].map(function(id) {
    return {id:id, text:translated(id)};
  })};
}
function renderAcross(q, languages, exam) {
  isExamMode = exam; randomCalls = 0;
  return languages.map(function(language) {
    appLang = language;
    return {language:language, result:renderOptions(q)};
  });
}
"""
        cls.node = os.environ.get("NODE_BINARY") or shutil.which("node")
        if not cls.node and Path("C:/Program Files/nodejs/node.exe").is_file():
            cls.node = "C:/Program Files/nodejs/node.exe"
        if not cls.node:
            raise RuntimeError("Node.js is required to execute the actual renderer; set NODE_BINARY")

    def run_renderer(self, body):
        result = subprocess.run(
            [self.node, "-e", self.script + "\n" + body], check=True,
            capture_output=True, text=True, encoding="utf-8", timeout=15,
        )
        return json.loads(result.stdout)

    def assert_language_roundtrip(self, rows):
        expected_mapping = None
        for row in rows:
            language, result = row["language"], row["result"]
            options = result["options"]
            self.assertEqual(len(options), 4)
            mapping = {option["id"]: option["sourceId"] for option in options}
            if expected_mapping is None:
                expected_mapping = mapping
            self.assertEqual(mapping, expected_mapping, "Language change must not reshuffle answer letters")
            self.assertEqual(result["randomCalls"], 3, "Only the initial four-option shuffle may draw randomness")
            self.assertEqual(result["correct"], "A", "Original B is displayed as A with this shuffle")
            correct = next(option for option in options if option["id"] == result["correct"])
            self.assertEqual(correct["sourceId"], "B")
            prefix = {"no": "NO_", "th": "ไทย_", "en": "EN_"}[language]
            self.assertEqual([option["text"] for option in options],
                             [prefix + option["sourceId"] for option in options])
            self.assertEqual(result["cachedOptions"], options,
                             "History must not read stale-language text from the cache")

    def test_structured_options_relocalize_without_reshuffle_or_correct_letter_change(self):
        for exam in (False, True):
            with self.subTest(exam=exam):
                rows = self.run_renderer("console.log(JSON.stringify(renderAcross(structuredQuestion(), ['no','th','en','no'], "
                                         + json.dumps(exam) + "))); ")
                self.assert_language_roundtrip(rows)

    def test_flat_answer_fields_relocalize_with_stable_correct_letter(self):
        rows = self.run_renderer("""
var q = {correct_answer:'B'};
['A','B','C','D'].forEach(function(id) {
  var text = translated(id);
  ['no','th','en'].forEach(function(lang) { q['answer_' + id.toLowerCase() + '_' + lang] = text[lang]; });
});
console.log(JSON.stringify(renderAcross(q, ['no','th','en'], true)));
""")
        self.assert_language_roundtrip(rows)

    def test_missing_translation_is_hidden_and_returns_in_next_language(self):
        rows = self.run_renderer("""
var q = structuredQuestion();
delete q.options[2].text.th;
console.log(JSON.stringify(renderAcross(q, ['no','th','en'], true)));
""")
        self.assertEqual([len(row["result"]["options"]) for row in rows], [4, 3, 4])
        for row in rows:
            options = row["result"]["options"]
            self.assertEqual(row["result"]["correct"], "A")
            self.assertEqual(row["result"]["randomCalls"], 3)
            for option in options:
                prefix = {"no": "NO_", "th": "ไทย_", "en": "EN_"}[row["language"]]
                self.assertEqual(option["text"], prefix + option["sourceId"])
            if row["language"] == "th":
                self.assertFalse(any(option["sourceId"] == "C" for option in options))

    def test_missing_translation_on_first_render_never_becomes_object_string(self):
        result = self.run_renderer("""
appLang = 'th'; isExamMode = true;
console.log(JSON.stringify(renderOptions({correctOptionId:'A', options:[{id:'A',text:{no:'NORSK'}}]})));
""")
        self.assertEqual(result["options"], [])

    def test_option_missing_in_initial_language_returns_when_translation_exists(self):
        for flat in (False, True):
            with self.subTest(flat=flat):
                rows = self.run_renderer("""
var q = structuredQuestion();
delete q.options[2].text.th;
if (""" + json.dumps(flat) + """) {
  q.options.forEach(function(option) {
    ['no','th','en'].forEach(function(language) {
      q['answer_' + option.id.toLowerCase() + '_' + language] = option.text[language] || '';
    });
  });
  delete q.options;
}
console.log(JSON.stringify(renderAcross(q, ['th','en','no'], true)));
""")
                self.assertEqual([len(row["result"]["options"]) for row in rows], [3, 4, 4])
                for row in rows[1:]:
                    option = next(option for option in row["result"]["options"] if option["sourceId"] == "C")
                    self.assertEqual(option["text"], {"en": "EN_C", "no": "NO_C"}[row["language"]])

    def test_direct_language_options_and_lowercase_keys_keep_source_identity(self):
        result = self.run_renderer("""
var q = {correctOptionId:'B', options:['a','b','c','d'].map(function(key) {
  return Object.assign({key:key}, translated(key.toUpperCase()));
})};
var original = JSON.stringify(q.options);
var rows = renderAcross(q, ['no','th','en'], false);
console.log(JSON.stringify({rows:rows, original_options_unchanged:original === JSON.stringify(q.options)}));
""")
        self.assertTrue(result["original_options_unchanged"])
        self.assert_language_roundtrip(result["rows"])


if __name__ == "__main__":
    unittest.main()
