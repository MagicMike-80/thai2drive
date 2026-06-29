---
name: quiz-quality-audit
description: 'Audit quiz question quality: difficulty balance, clarity, pedagogical soundness, proper translations, and exam alignment. Use before sprint planning, pre-deploy, or after bulk question import. Catches low-quality questions before production.'
argument-hint: 'Category or range (e.g., "all questions", "category: trafikkregler", "ID: 100-200", or blank for full audit)'
user-invocable: true
---

# Quiz Quality Audit for Thai2Drive

## Purpose

Ensure every quiz question meets thai2drive's **pedagogical standards, clarity, and exam alignment**. Catch low-quality questions before they confuse learners.

---

## When to Use

✅ **Before sprint planning** — Validate bulk content adds  
✅ **After importing new questions** — Quality check new batches  
✅ **Pre-deploy** — Final quality gate  
✅ **Periodic maintenance** — Audit existing question pool  
✅ **After pedagogy changes** — Re-validate existing questions against new standards  
✅ **Student feedback review** — Investigate reported confusing questions  

---

## What We Audit

### 1. **Difficulty Balance** (Warning)

Check that question pool has healthy distribution:
- **Easy (30%):** Confidence builders, fundamental concepts
- **Medium (50%):** Core exam content, application
- **Hard (20%):** Edge cases, advanced reasoning

**Example Report:**
```
Current distribution:
Easy:    12% ❌ (Too few! Learners need confidence builders)
Medium:  63% ⚠️ (Too many! Exam will have easier questions)
Hard:    25% ✅ (Good)

Recommendation: Add 8-10 easy questions about basic traffic rules
```

### 2. **Question Clarity** (Critical)

Does the question clearly test ONE concept?

**Bad question:**
```
"Hva er reglene for parkering og bremsing når du møter en syklist som krysser?"
❌ Tests MULTIPLE concepts (parking + braking + cyclist interaction)
❌ Confusing phrasing
❌ Learner doesn't know what is being tested
```

**Good question:**
```
"Hva skal du gjøre når du møter en syklist som krysser foran deg?"
✅ Tests ONE concept (cyclist interaction)
✅ Clear phrasing
✅ Single correct answer makes sense
```

### 3. **Answer Quality** (Critical)

Check that:
- ✅ Exactly ONE correct answer
- ✅ Distractors are plausible but wrong
- ✅ Distractors don't give away the answer
- ✅ All options are similar length (no obvious correct answer by length)
- ✅ No duplicate options

**Bad options:**
```
A) Bremse immediately (✅ correct)
B) Brake immediately (duplicate of A)
C) Very slowly apply brakes while honking the horn and turning the wheel (too specific)
D) Keep going (obvious wrong)
```

**Good options:**
```
A) Brake and avoid the cyclist    (✅ correct)
B) Honk the horn to warn cyclist  (plausible but wrong)
C) Turn left to avoid             (plausible but wrong)
D) Maintain speed                 (plausible but wrong)
```

### 4. **Explanation Quality** (Important)

Does the explanation help learner understand WHY?

**Bad explanation:**
```
"Answer is A"
❌ No learning value
❌ Doesn't teach the concept
```

**Good explanation:**
```
"When a cyclist crosses your path, you must brake and avoid them. 
This follows the HAV-regelen (respectful, attentive, cautious):
- Respectful: Cyclists are vulnerable road users
- Attentive: Watch for unexpected movements
- Cautious: Give space and brake early
Honking distracts them. Turning may hit them. Speeding is dangerous."
✅ Teaches the concept
✅ References pedagogical framework (HAV-regelen)
✅ Explains why other options are wrong
```

### 5. **Exam Alignment** (Important)

Does this question match actual Norwegian driving exam?

**Mappings to check:**
- Category (trafikkregler, skilter, sikkerhet, etc.)
- Difficulty (exam typically 70% medium, 20% hard, 10% easy)
- Topics (coverage of all main exam areas)
- Question type (yes/no, multiple choice, etc.)

**Warning signs:**
```
⚠️ Question about "Thai traffic laws" in Norwegian exam app
❌ Not aligned with actual exam
→ Remove or replace
```

### 6. **Thai/Norwegian/English Equivalence** (Critical)

When question exists in multiple languages, do all versions test the SAME concept?

**Bad (different languages test different things):**
```
Norwegian: "Hva er maksimal hastighet i by?" (What is max speed in city?)
Thai:      "คุณควรโยกหลักในกรณีใด" (When should you change lanes?)
❌ Different questions!
```

**Good (all languages test the same):**
```
Norwegian: "Hva er maksimal hastighet i by?"
Thai:      "ความเร็วสูงสุดในเมืองคือเท่าไร"
English:   "What is the maximum speed in the city?"
✅ Same question, different languages
```

### 7. **Image Quality** (If applicable)

If question has an image (`bildeUrl`):
- [ ] Image is relevant to question
- [ ] Image is clear and readable
- [ ] Image loads without errors
- [ ] Image is properly licensed

---

## Audit Workflow

### Step 1: Define Scope
- [ ] All questions?
- [ ] Specific category?
- [ ] Recent additions (last 100)?
- [ ] Flagged questions?

### Step 2: Sample & Analyze
For each question, check:
1. **Clarity:** Does it test ONE concept? ✅/❌
2. **Answers:** Exactly one correct, plausible distractors? ✅/❌
3. **Explanation:** Does it teach? ✅/❌
4. **Alignment:** Matches exam standards? ✅/❌
5. **Languages:** All match (if multi-lang)? ✅/❌

### Step 3: Generate Report

**Quality Report:**
```
QUIZ QUALITY AUDIT REPORT
Date: 2026-06-25
Scope: All questions in category "Trafikkregler"
Sample size: 147 questions

CLARITY ISSUES (Questions that test multiple concepts):
  ❌ Question #234: Tests both speed AND intersection rules
  ❌ Question #567: Tests parking AND cyclist safety
  → Action: Rewrite or split into 2 questions
  
ANSWER QUALITY ISSUES (Weak distractors or duplicates):
  ⚠️ Question #123: Distractors too obvious (Question length gives it away)
  ⚠️ Question #456: Options B and C are almost identical
  → Action: Rework distractor phrasing

EXPLANATION ISSUES (Missing or unclear):
  ⚠️ Question #789: Explanation just says "Correct!" with no teaching
  → Action: Add pedagogical explanation

DIFFICULTY DISTRIBUTION:
  Easy:    28% (target 30%) ✅
  Medium:  52% (target 50%) ✅
  Hard:    20% (target 20%) ✅

LANGUAGE ALIGNMENT (Thai/Norwegian/English):
  ✅ All 147 questions have complete translations
  ⚠️ Question #111: Thai and Norwegian test slightly different concepts
  → Action: Harmonize Thai translation

OVERALL QUALITY SCORE: 87/100
  (Good quality; address 5 flagged questions)
```

### Step 4: Action Plan
- [ ] Fix clarity issues (rewrite/split)
- [ ] Improve weak answers (rework distractors)
- [ ] Add missing explanations
- [ ] Harmonize multi-language questions
- [ ] Re-audit after fixes

### Step 5: Re-validate
After fixes, re-run audit to confirm improvements.

---

## Quality Scoring Rubric

| Dimension | Excellent (10) | Good (7-9) | OK (5-6) | Poor (<5) |
|-----------|---|---|---|---|
| **Clarity** | Tests exactly ONE concept | Clear intent but could be sharper | Slightly ambiguous | Tests multiple concepts |
| **Answers** | 1 correct, 3 plausible distractors | 1 correct, 2-3 decent distractors | 1 correct, obvious wrong answers | Ambiguous correct answer |
| **Explanation** | Teaches WHY, references framework | Good explanation, minor gaps | Explains answer, not concept | Just says "correct" |
| **Alignment** | Perfect exam match | Good match | Some alignment | Doesn't match exam |
| **Languages** | Perfect equivalence | Slight variation acceptable | Different nuance | Tests different concepts |

**Formula:** `Average of all dimensions = Quality Score (0-100)`

---

## Red Flags (Immediate Fix Required)

🚨 **CRITICAL** (Question must be removed or heavily rewritten):
- [ ] Correct answer is ambiguous
- [ ] More than one answer could be correct
- [ ] Question tests content NOT in exam
- [ ] Explanation is factually wrong
- [ ] Thai/Norwegian/English test different concepts

⚠️ **WARNING** (Should be improved before production):
- [ ] Distractors are too weak or obvious
- [ ] Explanation doesn't teach
- [ ] Question is poorly phrased
- [ ] Image is missing or broken
- [ ] Translation is awkward or unclear

---

## Quick Checklist

- [ ] One concept per question?
- [ ] Exactly one correct answer?
- [ ] Distractors are plausible?
- [ ] Explanation teaches?
- [ ] Matches exam content?
- [ ] Thai/Norwegian/English equivalent (if multi-lang)?
- [ ] Images load correctly?
- [ ] Difficulty balanced (30% easy, 50% medium, 20% hard)?
- [ ] Quality score ≥85?

---

## How to Use This Skill

**Option 1: Full audit**
```
/quiz-quality-audit
Run full quality check on all questions
```

**Option 2: Category audit**
```
/quiz-quality-audit
Audit category: trafikkregler (traffic rules)
```

**Option 3: Range audit**
```
/quiz-quality-audit
Audit questions ID 100-200 (recently added questions)
```

**Option 4: Flag review**
```
/quiz-quality-audit
Re-audit flagged questions after fixes
```

**Option 5: Via superpowers-workflow**
```
/superpowers-workflow
Debug: Students report question #567 is confusing
(Delegate to quiz-quality-audit for systematic analysis)
```

---

## Integration with Other Skills

- **superpowers-workflow** — Delegate audit to this skill
- **thai2drive-innhold** — Send low-quality questions here for rewriting
- **translation-checker** — Verify multi-language equivalence
- **skill-creator** — Example of QA workflow skill

---

## Expected Output

After running quiz-quality-audit, you get:

1. **Clarity Issues List** — Questions that need rewriting
2. **Answer Quality Issues** — Weak distractors to improve
3. **Explanation Report** — Missing or weak explanations
4. **Difficulty Distribution** — Balanced or imbalanced
5. **Language Alignment** — Multi-language equivalence check
6. **Overall Quality Score** — 0-100 rating
7. **Action Items** — Prioritized fixes with owner

---

## Pro Tips

- Run after bulk imports to catch problems early
- Run quarterly on existing question pool (questions degrade over time)
- Use Quality Score as a gate: only deploy if ≥85
- Track scores over time (trending report)
- Celebrate when all audits pass 90+! 🎉

---

## Related Skills

- [superpowers-workflow](../superpowers-workflow/SKILL.md) — Delegate to this skill
- [translation-checker](../translation-checker/SKILL.md) — For language equivalence
- [skill-creator](../skill-creator/SKILL.md) — How this skill was created
- [memory-write](../memory-write/SKILL.md) — Save quality standards
