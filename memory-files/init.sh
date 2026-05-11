#!/usr/bin/env bash
# init.sh — scaffold a memory/ subfolder for one Claude Code project.
#
# Usage:
#   ./init.sh <project-memory-path>
# Example:
#   ./init.sh ~/.claude/projects/-home-you-myproject

set -eu

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <project-memory-path>" >&2
  echo "example: $0 ~/.claude/projects/-home-you-myproject" >&2
  exit 2
fi

base="$1"
mem_dir="${base%/}/memory"

if [[ -e "$mem_dir" ]]; then
  echo "error: $mem_dir already exists" >&2
  exit 1
fi

mkdir -p "$mem_dir"

cat > "$mem_dir/MEMORY.md" <<'EOF'
# Memory Index

<!--
  One line per memory file. Format:
    - [Short Title](filename.md) — one-line hook
  Keep this file under 200 lines (runtime truncates beyond that).
-->
EOF

cat > "$mem_dir/_template.md" <<'EOF'
---
name: type_topic_keyword
description: One precise sentence — used to decide relevance in future turns
type: user|feedback|project|reference
---

Lead with the rule, decision, or fact.

**Why:** the reason it matters (often an incident, a deadline, a preference).
**How to apply:** when this kicks in; how to act on it.
EOF

echo "initialised:"
echo "  $mem_dir/"
echo "  $mem_dir/MEMORY.md"
echo "  $mem_dir/_template.md"
echo ""
echo "next: copy _template.md into named memory files, then add a line"
echo "      pointing to each one in MEMORY.md."
