# Thai2Drive Language System

Purpose: prevent Norwegian, Thai, and English from bleeding into each other in the learner experience.

## Core Rules

- Norwegian mode must show only Norwegian learner-facing text.
- Thai mode must show only Thai learner-facing text.
- English mode must show only English learner-facing text.
- Do not use another language as a visible fallback.
- If a translation is missing, hide the optional content or use a neutral same-language label.
- Language switch must update visible UI immediately without page reload.
- Michael must answer in the selected/user language only.
- Old Michael chat context must not continue across language changes.

## Implementation Rules

- Store content as explicit `no`, `th`, and `en` fields.
- Sanitize language once at API entry points and use that value throughout the request.
- Keep prompts, examples, shortcuts, fallback replies, chips, video titles, and side panels language-specific.
- Do not put Norwegian examples inside shared Thai or English AI prompts.
- Avoid hardcoded learner-facing strings in event handlers.
- Avoid fallback chains like `thai || norwegian` for visible text.

## Test Checklist

### Norwegian

- Switch to Norwegian.
- Open Home, Quiz, Study Book, Traffic Signs, Michael, Settings, Login/Register, and Premium dialogs.
- Confirm all visible text is Norwegian.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm replies, chips, suggestions, and video titles stay Norwegian.

### Thai

- Switch to Thai.
- Open Home, Quiz, Study Book, Traffic Signs, Michael, Settings, Login/Register, and Premium dialogs.
- Confirm no Norwegian or English learner-facing text is visible.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm replies, chips, suggestions, fallback text, and video titles stay Thai.
- Switch from Norwegian to Thai and confirm old Norwegian Michael messages are cleared.

### English

- Switch to English.
- Open Home, Quiz, Study Book, Traffic Signs, Michael, Settings, Login/Register, and Premium dialogs.
- Confirm all visible text is English.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm replies, chips, suggestions, and video titles stay English.

## Release Rule

Any new learner-facing feature must pass the NO, TH, and EN checklist before release.
