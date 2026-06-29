"""Quick validation: check all 13 questions for structure, language purity and distractor quality."""
import json, sys

path = r"c:\Users\Stein Hoang\thai2drive\content\quiz_michael_v5.json"
data = json.load(open(path, encoding="utf-8"))

errors = []
for i, q in enumerate(data, 1):
    # Structure checks
    for key in ["question_no","question_th","question_en","options","explanation_no","explanation_th","explanation_en","topic_tags","difficulty","podcast_reference"]:
        if key not in q:
            errors.append(f"Q{i}: missing key '{key}'")
    
    opts = q.get("options", [])
    if len(opts) < 3:
        errors.append(f"Q{i}: only {len(opts)} options (need >=3)")
    
    correct_count = sum(1 for o in opts if o.get("correct"))
    if correct_count != 1:
        errors.append(f"Q{i}: {correct_count} correct answers (need exactly 1)")
    
    # Language purity: no Norwegian in Thai fields (simple heuristic: check for Norwegian chars)
    for o in opts:
        th = o.get("text_th","")
        if any(c in th for c in "æøåÆØÅ"):
            errors.append(f"Q{i}: Norwegian chars found in Thai option: {th[:40]}")
    
    th_expl = q.get("explanation_th","")
    if any(c in th_expl for c in "æøåÆØÅ"):
        errors.append(f"Q{i}: Norwegian chars found in Thai explanation")

    # All 3 language fields must be non-empty for each option
    for j, o in enumerate(opts, 1):
        for lang in ["text_no","text_th","text_en"]:
            if not o.get(lang,"").strip():
                errors.append(f"Q{i} opt{j}: empty {lang}")

    # Difficulty check
    diff = q.get("difficulty","")
    if diff == "hard":
        print(f"  Q{i} [HARD]: {q['question_no'][:60]}...")
    else:
        print(f"  Q{i} [{diff.upper()}]: {q['question_no'][:60]}...")

print(f"\n{'='*50}")
print(f"Total questions: {len(data)}")
print(f"Hard questions: {sum(1 for q in data if q['difficulty']=='hard')}")
if errors:
    print(f"\n❌ {len(errors)} ERRORS FOUND:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("✅ All validations passed! No errors found.")
