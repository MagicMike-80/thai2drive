# Thai2Drive Language System

Purpose: prevent language bleed-through between Norwegian, Thai, and English.

## Core Rule

Learner-facing text must always match the active language:

- `no`: Norwegian only
- `th`: Thai only
- `en`: English only

Do not use another language as visible fallback. If optional translated content is missing, hide it or use a neutral label in the active language.

## Developer Rules

- Store learner text as explicit `no`, `th`, and `en` values.
- Sanitize language once at API entry points and use the sanitized value everywhere.
- Avoid fallback chains like `title_th || title_no` for visible text.
- Avoid hardcoded learner-facing strings in click handlers, templates, and API fallbacks.
- Language switching must update visible text immediately without page reload.
- Old language-specific chat or UI state must be cleared when switching language.

## Surface Rules

- UI text: buttons, headings, placeholders, labels, empty states, errors, and dialogs must use the active language.
- Video titles: never fall back to Norwegian in Thai or English mode. Hide the video card if the active-language title is missing.
- Side panel/chips: chip labels and `data-msg` values must exist per language. Do not send Norwegian shortcut text in Thai or English mode.
- Premium gate: paywall titles, benefits, buttons, restore text, and error messages must match the active language.
- Settings: language labels, account text, logout/login, and subscription text must update instantly.
- Quiz: question text, answer labels, helper text, feedback, next button, and image captions must match the active language.
- Result screen: score labels, pass/fail text, explanations, review actions, and retry buttons must match the active language.
- Michael Trafikklærer: welcome message, prompts, suggestions, fallback replies, examples, formulas, side panel, and video cards must stay in the selected/user language only.

## AI Prompt Rules

- Keep Michael prompts language-specific.
- Do not put Norwegian examples inside Thai or English prompt paths.
- Conversation context must be language-scoped or reset on language change.
- Fallback replies must be language-specific.

## Manual Test Checklist

### Norwegian

- Switch to Norwegian.
- Check Home, Quiz, Results, Traffic Signs, Study Book, Michael, Settings, Login/Register, and Premium gate.
- Confirm all visible text is Norwegian.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm chips, side panel, suggestions, replies, and video cards stay Norwegian.

### Thai

- Switch to Thai.
- Check Home, Quiz, Results, Traffic Signs, Study Book, Michael, Settings, Login/Register, and Premium gate.
- Confirm no Norwegian or English learner-facing text is visible.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm chips, side panel, suggestions, replies, fallback text, and video cards stay Thai.
- Switch from Norwegian to Thai and confirm old Norwegian Michael messages/context are cleared.

### English

- Switch to English.
- Check Home, Quiz, Results, Traffic Signs, Study Book, Michael, Settings, Login/Register, and Premium gate.
- Confirm all visible text is English.
- Ask Michael about signs, right-of-way, and formulas.
- Confirm chips, side panel, suggestions, replies, and video cards stay English.

## Release Rule

Any learner-facing feature must pass the NO, TH, and EN checklist before release.
