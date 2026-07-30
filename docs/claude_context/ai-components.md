# AI Components & Michael Roadmap

> Load this when: touching Michael's chat, AI explanations, adaptive learning, or model routing.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Michael Teacher Chat (`backend/teacher_chat.py`)

- System prompt in Michael's voice (calm, real driving instructor tone)
- Enforces Thai/Norwegian/English language purity (no code-switching)
- No visible AI system messages
- Uses Gemini/OpenAI via LiteLLM for routing

**Michael should feel like a calm real driving instructor, not a generic chatbot or visible AI system.**

## AI Explanations (`backend/ai_explanations.py`)

- Explains quiz answers with a pedagogy focus
- Follows the exam tips and common mistakes pattern
- Respects question difficulty level in explanation depth

## Adaptive Learning (`backend/ai_learning.py`)

- Personal weak-topic analysis per user
- Suggests practice based on quiz history
- Tracks improvement over time

## Models used (via LiteLLM)

- Default: `gpt-4-turbo` or `gpt-3.5-turbo`
- Alternative: `gemini-1.5-pro`
- Cost-aware: falls back based on `LITELLM_LOG=DEBUG`

See [`performance.md`](performance.md) for AI cost optimization rules.

---

## Michael Roadmap

- **V1:** Michael as a good chat teacher.
- **V2:** Michael connected to approved Thai2Drive content.
- **V3:** Mini-practice and coaching.
- **V4:** Personal weak-topic learning.
- **V5:** Voice, video, visual explanations, and adaptive AI instructor.
