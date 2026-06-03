# Thai2Drive Agent Instructions

## Project
Thai2Drive is a Norwegian driving theory app/course for Thai-speaking learners in Norway.

## Core Rules
- Production stability first.
- Make small patches only.
- Do not rewrite unrelated code.
- Do not change Stripe, RevenueCat, auth, premium, quota, or MongoDB logic unless explicitly requested.
- Web app first. Do not change mobile unless requested.
- Backend is source of truth.

## Language Rules
- Norwegian UI must be 100% Norwegian.
- Thai UI must be 100% Thai.
- English UI must be 100% English.
- No fallback text from another language in learner-facing UI.
- Never mix Norwegian into Thai UI or Thai into Norwegian UI.
- Michael Trafikklærer must answer in the same language as the user message.

## Premium Rules
- Guest: 5 questions total.
- Free account: 10 questions per day.
- Premium: unlimited questions plus deeper guidance.
- Premium should feel calm and helpful, not aggressive.

## AI Teacher Rules
- Explain like a calm driving instructor.
- Keep answers short and practical.
- Ask one clarifying question when the user asks a broad question.
- For specific questions, answer directly.
- Stay inside driving theory, signs, right-of-way, traffic rules, quiz help, and app guidance.

## Before Editing
- Inspect existing code first.
- Identify exact files and line areas.
- Explain the planned patch.
- Keep changes minimal.

## After Editing
- List changed files.
- Explain what changed.
- Mention what was not changed.
- Suggest simple tests for Norwegian, Thai, and English.
