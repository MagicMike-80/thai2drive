---
name: translation-checker
description: 'Validate Thai/Norwegian/English translation completeness. Use when: before sprint planning, pre-deploy checks, adding new content, reviewing quiz questions. Finds missing translations, language bleed-through, and ensures 100% coverage across all three languages.'
argument-hint: 'File or section to check (e.g., "quiz questions", "study book chapter 3", "Michael pedagogy", or leave blank to check all)'
user-invocable: true
---

# Translation Checker for Thai2Drive

## Purpose

Ensure **zero language bleed-through** and **100% translation coverage** across Thai, Norwegian, and English. This skill catches missing translations before they reach production.

---

## When to Use

✅ **Before every sprint planning** — Verify all new content is translated  
✅ **Pre-deploy** — Confirm no language is incomplete  
✅ **Adding new quiz questions** — Check all 3 languages are present  
✅ **New study book sections** — Validate translations  
✅ **Traffic signs updates** — Verify explanations in all languages  
✅ **Michael pedagogy updates** — Check tone/examples translate correctly  

---

## What We Check

### 1. **Missing Translations** (Critical)
Find strings that have Norwegian or English but **missing Thai** (or vice versa).

**Example (BAD):**
```json
{
  "question": {
    "no": "Hva er maksimal hastighet?",
    "th": "ความเร็วสูงสุด",
    "en": "What is max speed?"
  },
  "explanation": {
    "no": "50 km/h i byer",
    "th": "",  // ❌ MISSING THAI
    "en": "50 km/h in cities"
  }
}
```

**Example (GOOD):**
```json
{
  "question": {
    "no": "Hva er maksimal hastighet?",
    "th": "ความเร็วสูงสุด",
    "en": "What is max speed?"
  },
  "explanation": {
    "no": "50 km/h i byer",
    "th": "50 กม./ชม. ในเมือง",  // ✅ COMPLETE
    "en": "50 km/h in cities"
  }
}
```

### 2. **Language Bleed-Through** (Critical)
Detect when Thai mode shows Norwegian/English text (or vice versa).

**Example (BAD):**
```
User selects Thai mode
Quiz screen shows:
  "Maksimal hastighet?" (Norwegian text!) ❌
  Should be: "ความเร็วสูงสุด" (Thai) ✅
```

### 3. **Empty Strings** (Warning)
Find translation fields that exist but are empty (`""`, `null`, `undefined`).

### 4. **Coverage Report**
Summarize:
- Total strings
- Thai coverage %
- Norwegian coverage %
- English coverage %
- Missing per language

---

## Workflow

### Step 1: Identify Scope
What are we checking?
- [ ] Quiz questions (`content/quiz_michael_v5.json`)
- [ ] Study book (`content/studybook_chapters_v5.json`)
- [ ] Traffic signs (`backend/signs_content.json`)
- [ ] Michael pedagogy (teacher chat responses)
- [ ] API responses
- [ ] All of above

### Step 2: Extract Strings
Scan the target file(s) for all `LocalizedText` objects:
```json
{
  "no": "Norwegian",
  "th": "ไทย",
  "en": "English"
}
```

### Step 3: Validate Each Language
For each localized string, check:
- [ ] Thai (`th`) is present and not empty
- [ ] Norwegian (`no`) is present and not empty
- [ ] English (`en`) is present and not empty
- [ ] No language contains text from another language (bleed-through)

### Step 4: Generate Report

**Missing Translations Report:**
```
File: content/quiz_michael_v5.json
Total LocalizedText objects: 1247

Missing Thai translations: 5
  - Question ID #342: explanation field empty
  - Question ID #589: options[2] text empty
  - Question ID #756: explanation field empty
  - Sign ID #104: description empty
  - Sign ID #201: warning empty

Missing Norwegian translations: 2
  - Question ID #445: question field empty
  - Sign ID #305: category_explanation empty

Missing English translations: 0 ✅

OVERALL COVERAGE:
Thai:       99.6% (5 missing)
Norwegian:  99.8% (2 missing)
English:    100% ✅
```

**Language Bleed-Through Report:**
```
⚠️ WARNING: Potential language bleed-through detected:

Location: Question #234 (Thai text in Norwegian field)
  Field: explanation.no
  Current value: "เข้าใจความสำคัญของการขับขี่ที่ปลอดภัย"
  Should be: Norwegian translation

Recommendation: Fix or replace with correct Norwegian text
```

### Step 5: Action Plan
- [ ] List all missing translations
- [ ] Assign to thai2drive-innhold for translation
- [ ] Fix bleed-through issues
- [ ] Re-validate after fixes
- [ ] Mark as complete

---

## Quick Checklist

- [ ] All Thai strings (`th`) are present and not empty?
- [ ] All Norwegian strings (`no`) are present and not empty?
- [ ] All English strings (`en`) are present and not empty?
- [ ] No Norwegian text in Thai fields?
- [ ] No English text in Norwegian fields?
- [ ] Thai uses Thai Unicode characters (not Latin)?
- [ ] Coverage %: Thai ≥99%, Norwegian ≥99%, English ≥99%?
- [ ] Report generated and saved?

---

## Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing Thai translation | Thai field empty | Assign to thai2drive-innhold |
| Norwegian-in-Thai | Thai shows Norwegian text | Replace with correct Thai translation |
| Encoding issues | Thai characters show as ??? | Check UTF-8 encoding in file |
| Copy-paste error | Thai text duplicated in multiple languages | Manually review and replace |
| API mismatch | Web shows complete, mobile doesn't | Check if backend is seeded correctly |

---

## Files to Check (Thai2Drive)

| File | Type | Contains |
|------|------|----------|
| `content/quiz_michael_v5.json` | Quiz | Questions, options, explanations |
| `content/studybook_chapters_v5.json` | Study Book | Chapter titles, sections, text |
| `backend/signs_content.json` | Traffic Signs | Sign names, descriptions, warnings |
| `backend/content_packs/studiebok_i18n_v2.json` | Study Book (I18N) | Localized book content |
| API responses | Backend | All endpoint responses |

---

## How to Use This Skill

**Option 1: Check specific file**
```
/translation-checker
Check completeness of: content/quiz_michael_v5.json
```

**Option 2: Check section**
```
/translation-checker
Validate Thai/Norwegian/English for: traffic signs (backend/signs_content.json)
```

**Option 3: Pre-deploy check**
```
/translation-checker
Full coverage report before deploy to Railway
```

**Option 4: Via superpowers-workflow**
```
/superpowers-workflow
Debug: Why does Thai mode show some Norwegian text?
(Delegate to translation-checker for systematic language audit)
```

---

## Integration with Other Skills

- **superpowers-workflow** — Delegate translation checking to this skill
- **thai2drive-innhold** — Send missing translations here for completion
- **thai2drive-vakt** — Sync check includes translation validation
- **skill-creator** — Example of a domain-specific workflow skill

---

## Expected Output

After running translation-checker, you get:

1. **Missing Translations List** — Exact locations and fields
2. **Coverage Report** — Percentage complete per language
3. **Bleed-Through Warnings** — Language contamination issues
4. **Action Items** — What to fix and who to assign it to
5. **Validation Checklist** — Before/after verification

---

## Pro Tips

- Run before every sprint to catch issues early
- Run before every deploy to production
- Run after thai2drive-innhold adds new content
- Export report to share with content team
- Document fixes in memory for future reference

---

## Related Skills

- [superpowers-workflow](../superpowers-workflow/SKILL.md) — Delegate to this skill
- [skill-creator](../skill-creator/SKILL.md) — How this skill was created
- [memory-write](../memory-write/SKILL.md) — Save translation lessons learned
