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

## Codex / Claude Code Ownership
- Codex owns implementation work: code, backend/API, database scripts, validation/import systems, web/mobile changes, tests, Git/GitHub/Railway, deployment, logging, monitoring, and production safety.
- Claude Code owns content work: pedagogy, traffic theory explanations, Thai/Norwegian/English wording, Michael tone/personality, question wording, common mistakes, exam tips, video scripts, lesson structure, and learning goals.
- Do not do the other assistant's job. If a task belongs to the other assistant, stop and say: "This task belongs to Codex/Claude Code. I should not do this part."
- Do not build web and mobile in parallel. Michael Trafikklærer features must be built and approved on web first; mobile follows only after explicit approval.
- Claude Code prepares learning content and teaching logic. Codex implements approved technical changes safely.
- If ownership is unclear, ask whether the task is a Codex implementation task or a Claude Code content task before changing files.

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
- Michael should feel like a calm real driving instructor, not a generic chatbot.
- Prioritize clarity, practical examples, common mistakes, theory-test angle, one relevant follow-up question, calm tone, and no visible AI profiling.

## Michael Roadmap
- V1: Michael as a good chat teacher.
- V2: Michael connected to approved Thai2Drive content.
- V3: Mini-practice and coaching.
- V4: Personal weak-topic learning.
- V5: Voice, video, visual explanations, and adaptive AI instructor.

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
