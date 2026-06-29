---
name: superpowers-workflow
description: 'Superpowers Plugin for Thai2Drive. Use when: planning complex features, debugging production issues, delegating to subagents (thai2drive-innhold, thai2drive-vakt, Explore). Enforces brainstorming-first, systematic debugging, and efficient task delegation.'
argument-hint: 'Task type: plan feature, debug issue, delegate content, or sync check'
user-invocable: true
---

# Superpowers Workflow for Thai2Drive

## Purpose

This skill packages the **Superpowers Plugin** methodology specifically for thai2drive. It ensures every complex task follows a structured approach: **Plan → Brainstorm → Execute → Validate**.

---

## Three Core Superpowers

### 1. **Brainstorming Before Coding** (Planning Phase)

Before touching code, ask clarifying questions:

- **What problem are we solving?** (Be specific about pain point)
- **What are the constraints?** (Scope, performance, languages, platforms)
- **What are the alternatives?** (Option A, B, C with trade-offs)
- **What could go wrong?** (Edge cases, regressions, production risks)
- **What's the rollback plan?** (If this breaks, how do we revert?)

**Output:** A clear **plan document** with decided approach, before any coding starts.

**When to use:** 
✅ Feature design  
✅ Database migrations  
✅ API changes  
✅ UI overhauls  
✅ Performance optimization  
✅ Deployment changes  

---

### 2. **Systematic Debugging** (Problem-Solving Phase)

When something breaks, follow this process:

1. **Isolate the problem**
   - What changed last? (Git log, recent commits)
   - Which component/layer is affected? (Frontend, Backend, API, DB)
   - Is it deterministic or intermittent?

2. **Gather evidence**
   - Error logs (backend, mobile, web)
   - Network requests (DevTools, API traces)
   - Database state (check MongoDB, SQLite)
   - Environment variables (correct Rails config, API keys?)

3. **Form hypotheses** (3+ theories, ranked by likelihood)
   - Hypothesis A: Why this might be broken
   - Hypothesis B: Alternative explanation
   - Hypothesis C: Worst-case scenario

4. **Test hypotheses systematically**
   - Write a minimal test case
   - Run one hypothesis at a time
   - Document results

5. **Fix the root cause** (not the symptom)
   - Fix the core issue, not a band-aid
   - Update tests to prevent regression
   - Verify across all affected platforms (web, mobile)

6. **Document the fix** (for future reference)
   - What was broken, why, and how we fixed it
   - Add to memory or project wiki

**When to use:**
✅ Production bugs  
✅ Test failures  
✅ Intermittent crashes  
✅ Performance degradation  
✅ Language/translation issues  
✅ Platform-specific problems (Android vs iOS, web)  

---

### 3. **Subagent-Driven Delegation** (Efficiency Phase)

Instead of doing everything myself, delegate to specialists:

| Subagent | Expertise | When to Use |
|----------|-----------|------------|
| **thai2drive-innhold** | Content, pedagogy, Michael's tone, quiz questions, translations (no/th/en) | New quiz questions, study book sections, video scripts, translation issues, pedagogy review |
| **thai2drive-vakt** | Sync check between web/mobile, API contracts, translation completeness | After code changes, before deploy, checking if platforms match |
| **Explore** | Fast codebase exploration, Q&A, code patterns | Finding how something works, searching for examples, understanding architecture |
| **Em** | Cost-conscious, token-efficient assistant | Optimizing workflow, suggesting faster approaches |

**How to delegate:**
```
"Use thai2drive-innhold: Create 10 new quiz questions about traffic lights 
with full Thai/Norwegian/English translations and explanation."

"Use thai2drive-vakt: Check if mobile quiz screen matches web API response format 
for questions with images."

"Use Explore: Find all places where we use RevenueChat, show usage patterns."
```

**Benefit:** 
- Get expert answers faster
- Avoid context bloat (each subagent has its own context)
- Parallelize work (run multiple subagents at once)
- Save tokens (specialized agents = more efficient)

---

## Workflow: The Perfect Task

### Phase 1: Brainstorm (5 min)
```
User: "We need dark mode for the app."

Before coding, I ask:
- What components need dark mode first? (Quiz, Teacher, Settings?)
- Should we use React Native theme provider or inline styles?
- Do we need dark mode for the backend/web separately?
- How do we test it across Thai, Norwegian, English?
- What's the fallback if dark mode fails on old Android?
```

### Phase 2: Plan & Decide
```
Recommendation (Superpowers planning output):
- Option A: Use React Native theme provider (recommended)
  Pros: Centralized, easy to toggle
  Cons: Refactor all components
  
- Option B: CSS variables + inline styles
  Pros: Granular control
  Cons: More maintenance

Decision: Go with Option A, implement in phases
(Quiz → Teacher → Settings → Full App)
```

### Phase 3: Execute with Clarity
```
Step 1: Create theme constants in frontend/src/theme.ts
Step 2: Wrap app in ThemeProvider
Step 3: Refactor Quiz component first (test thoroughly)
Step 4: Use thai2drive-vakt to verify web matches mobile
Step 5: Delegate review to thai2drive-innhold (check Michael's teacher UI)
```

### Phase 4: Validate Before Shipping
```
Checklist:
□ All languages render correctly (Thai, Norwegian, English)
□ Contrast ratios pass WCAG AA (4.5:1)
□ Mobile and web look identical
□ No regressions in quiz, teacher, book modes
□ Tested on Android, iOS, and web
□ Revert plan ready (rollback tested)
```

---

## Superpowers Triggers (When to Use)

**Use Superpowers Workflow when:**
- Feature is complex (>4 hours of work)
- Multiple platforms affected (web, mobile, backend)
- Risk of breaking production (authentication, payments, data)
- Not sure of the best approach (need alternatives)
- Debugging takes >30 minutes (use systematic approach)
- Delegating to specialists (subagents)

**Don't overthink small tasks:**
- Fixing a typo → Just fix it
- Adding a comment → Just add it
- Renaming a variable → Just rename it

---

## Quick Checklist

- [ ] Did I brainstorm BEFORE coding?
- [ ] Did I ask clarifying questions?
- [ ] Do I have 2–3 alternatives?
- [ ] Have I identified risks and edge cases?
- [ ] Am I delegating to the right subagent?
- [ ] Did I run systematic debugging steps?
- [ ] Did I test across all platforms/languages?
- [ ] Did I document the fix?

---

## Thai2Drive-Specific Context

### Key Subagents
- **thai2drive-innhold:** Owns Michael's pedagogy, all translations
- **thai2drive-vakt:** Owns sync verification, never changes code
- **Explore:** Owns fast codebase navigation

### Critical Platforms
- **Web:** Expo web app (frontend/app/)
- **Mobile:** Android via Expo (frontend/app/ same codebase)
- **Backend:** FastAPI (backend/server.py)

### Always Verify
- ✅ Thai mode is 100% Thai (no Norwegian bleed)
- ✅ Responsive on all screen sizes
- ✅ API contracts match between web/mobile
- ✅ Translations are complete (no missing keys)

---

## Example Prompts

1. **Plan a complex feature:**
   `/superpowers-workflow Plan feature: Add offline quiz mode for premium users`

2. **Debug a production issue:**
   `/superpowers-workflow Debug: Premium users can't start quiz (works for free users)`

3. **Delegate to subagent:**
   `/superpowers-workflow Delegate: thai2drive-innhold create quiz about cyclist rules (Thai/Norwegian/English)`

4. **Systematic debugging:**
   `/superpowers-workflow Systematically debug: Thai text shows as ??? on Android but works on web`

---

## Related Skills

- [frontend-design-thai2drive](../frontend-design-thai2drive/SKILL.md) — Design decisions
- [memory-write](../memory-write/SKILL.md) — Document lessons learned
- [context-audit](../context-audit/SKILL.md) — Check token efficiency
