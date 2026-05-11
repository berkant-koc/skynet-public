# memory-files

File-based persistent memory for [Claude Code](https://docs.claude.com/en/docs/claude-code)
and similar long-lived LLM agents.

## The problem

Long conversations get auto-compacted: earlier exchanges are summarised
to fit a moving context window. Anything that was decided, calibrated,
or trusted in turn 12 may be lost by turn 200. Re-explaining the user's
role, the project state, and the agreed-upon conventions on every
session is wasteful and lossy.

## The shape

One markdown file per discrete memory. An index file
(`MEMORY.md`) lists every entry as a single line. Both live under

```
~/.claude/projects/<project-id>/memory/
```

The agent reads `MEMORY.md` on startup (cheap), and only opens the
individual memory file when the entry looks relevant to the current
turn (lazy).

## Frontmatter schema

Every memory file starts with a small YAML frontmatter block:

```markdown
---
name: feedback_no_silent_failures
description: User wants explicit error reporting; no silent catch-all swallows.
type: feedback
---

Lead with the rule. Then **Why:** + **How to apply:** lines so future
self can judge edge cases instead of blindly following the rule.
```

### Types

| Type | What goes in it |
|---|---|
| `user` | Stable facts about the user — role, expertise, goals, preferences |
| `feedback` | Corrections + confirmations that should shape future behaviour |
| `project` | Time-bound facts about ongoing work — deadlines, decisions, stakeholders |
| `reference` | Pointers into external systems (URLs, tracker IDs, dashboard names) |

### MEMORY.md format

A flat index. One line per file. No frontmatter:

```markdown
# Memory Index

- [Feedback: no silent failures](feedback_no_silent_failures.md) — explicit error reporting, no catch-all swallows
- [Project: Q3 migration to Postgres](project_q3_pg_migration.md) — cutover 2026-09-15, blocked on schema review
- [Reference: status dashboard](reference_status_dashboard.md) — internal/observability/status link
```

Lines > 200 in the index file get truncated by the runtime; keep each
entry under ~150 characters and the index file under 200 lines total.

## Initialise a new project

```bash
./init.sh ~/.claude/projects/-home-you-myproject
```

Creates the `memory/` subfolder, drops in a stub `MEMORY.md`, and
prints the path so you can `cd` into it.

## When to write a memory

- After the user states a stable preference ("I never want X")
- After you make a non-obvious call that they confirmed ("yes, that
  approach was right")
- When you learn an external system reference you will need again
- When you learn the user's role or context

## When NOT to write a memory

- Code conventions visible from reading the project. The codebase is
  the memory for those.
- Git history. `git log` is the memory.
- One-off task state. That belongs in your task tracker, not memory.
- Anything CLAUDE.md already documents.

## Behaviour notes

- Memories drift. Before acting on a memory that names a specific
  file or function, verify it still exists.
- Treat memory as **what was true when written**. The current code is
  the authoritative source of what is true now.
- If a memory contradicts what you observe, trust observation and
  update or remove the stale entry.

## License

MIT. See repository `LICENSE`.
