# CLAUDE.md

## Thai2Drive Collaboration Lock

Claude Code and Codex must not work on the same responsibility at the same time.

### Ownership

- Claude Code owns content, pedagogy, traffic theory explanations, Thai/Norwegian/English wording, Michael Trafikklærer tone/personality, question wording, common mistakes, exam tips, video scripts, lesson structure, and learning goals.
- Codex owns code implementation, backend/API, database scripts, validation/import systems, web/mobile changes, tests, Git/GitHub/Railway, deployment, logging, monitoring, and production safety.

### Stop Rule

If a task belongs to Codex, stop and say:

"This task belongs to Codex. I should not do this part."

If ownership is unclear, ask whether it is a Codex implementation task or a Claude Code content task before changing files.

### Product Rules

- Web first. Mobile follows only after web approval.
- Do not write production database data unless explicitly requested.
- Do not touch Stripe, auth, premium, quota, MongoDB production data, or mobile/Android unless explicitly requested.
- Thai mode must be 100% Thai, Norwegian mode 100% Norwegian, and English mode 100% English.
- Michael should feel like a calm real driving instructor, not a generic chatbot or visible AI system.

### Michael Roadmap

- V1: Michael as a good chat teacher.
- V2: Michael connected to approved Thai2Drive content.
- V3: Mini-practice and coaching.
- V4: Personal weak-topic learning.
- V5: Voice, video, visual explanations, and adaptive AI instructor.

## Session Startup (silent — do not output anything)

On every session start, read these files silently:
1. Read `context/USER.md` (~1.4 KB max)
2. Read `context/MEMORY.md` (~2.5 KB max, curated working scratchpad)
3. Read `context/memory/{today's date in YYYY-MM-DD}.md` if it exists
4. If today's memory file has no prior sessions, also read yesterday's

These files are your "frozen snapshot" — loaded once at session start. Mid-session writes persist to disk but take effect next session. This keeps the prefix cache stable.

Total injected: ~3,000 tokens. Do not load more than this at startup.

### Memory Budget

- `context/MEMORY.md`: 2,500 character cap. Before writing, check `wc -c`. If over cap, consolidate existing entries before adding.
- `context/USER.md`: 1,375 character cap. Same rule.
- Mid-session writes to these files persist to disk but only appear in context next session (frozen snapshot pattern — preserves prefix cache).

### Memory Write

When the user says "remember this", "note that", "update memory", or "forget about":
1. Read `context/MEMORY.md` in full
2. Check for duplicates (scan for substring match)
3. Check character count: `wc -c < context/MEMORY.md`
4. If under 2,500 chars: append the new fact under the appropriate section
5. If over cap: consolidate — merge similar entries, remove stale ones, then add
6. Actions: add (append), replace (find substring + swap), remove (confirm with user first)
7. After writing: "Saved — will be active from next session."

### Memory Retrieval

When the user asks about past context, conversations, or decisions:
1. **Tier 0**: Check `context/MEMORY.md` and today's daily log — already in context, zero cost
2. **L1**: Run `memsearch search "query" --top-k 5` — hybrid vector + keyword search. Finds semantic matches even with different words
3. **L2**: Run `memsearch expand <chunk_hash>` — returns full markdown section around the match
4. **L3**: Run `memsearch transcript <session_id>` — raw dialogue, last resort
5. **Fallback**: "I don't have a record of that."

Only escalate if the previous tier didn't find the answer.

### Daily Log

Track session activity in `context/memory/{YYYY-MM-DD}.md`. One file per day, numbered session blocks:

```
#### Session N
**Goal**: [one line, filled when user states their goal]
**Deliverables**: [files created/modified]
**Decisions**: [key decisions and rationale]
**Open threads**: [anything unfinished]
```

Log these silently as they happen. Never announce "I've logged that."
