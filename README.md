# skynet-public

Two small, opinionated tools I keep around the workstation for working
with [Claude Code](https://docs.claude.com/en/docs/claude-code) and
shell-level automation. Stdlib + msmtp only, no framework, no daemons.

## Modules

### [`memory-files/`](memory-files/) — file-based memory for LLM agents

A markdown convention that survives Claude Code's auto-compact. One
file per memory entry, an index file (`MEMORY.md`) for cheap lookup,
typed frontmatter to make memories retrievable by category (`user`,
`feedback`, `project`, `reference`).

Solves the practical problem of repeating context every conversation.
Inverts the usual approach: instead of larger context windows, smaller
durable artefacts the agent re-reads on demand.

### [`send-email/`](send-email/) — drop-in shell wrapper around `msmtp`

`send_email <to> <subject> <body|->`

Removes the boilerplate of authoring a `--From:` / `--Subject:` /
`--Content-Type:` header block by hand. Reads SMTP credentials from a
600-mode file, logs every dispatch with timestamp, declines to run if
the config is incomplete.

Useful as the `mailx` replacement when you want a single line in cron
or a systemd-timer ExecStart.

## Why a repo for this

Each module is small enough to live in a `~/dotfiles` directory. They
are public because the patterns are reusable and worth referencing in
conversation — not because the code is precious.

## License

MIT. See `LICENSE`.
