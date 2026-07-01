# Architecture

The system intentionally avoids a web app. Codex chat is the interface, and the repo is packaged as a Codex plugin.

```text
User answer in chat
  -> Codex calls plugin MCP tool
  -> SQLite records answer
  -> MCP tool returns next question
  -> finish tool generates report
  -> Obsidian-friendly Markdown notes
  -> optional disabled-by-default Notion sync plan on request
```

## Components

```text
.codex-plugin/plugin.json
  Codex plugin manifest

.mcp.json
  Local stdio MCP server declaration

cert_study/
  cli.py          command interface
  db.py           SQLite schema and connection
  engine.py       session selection, answer recording, scoring, review scheduling
  mcp_server.py   stdio MCP server used by Codex plugin loading
  notion_sync.py  Notion write-plan harness, disabled by default
  obsidian.py     Obsidian vault/session/concept note writer
  reporting.py    Markdown report rendering
  seed_sqld.py    SQLD synthetic question seed

skills/cert-study/SKILL.md
  Codex behavior contract for CBT sessions

scripts/sync_notion.py
  disabled-by-default Notion sync-plan helper

tests/
  harness checks for core behavior
```

## Source of Truth

SQLite is the source of truth.

Obsidian/Markdown is the default readable notebook. The plugin writes session notes, concept notes, and a review queue under `obsidian_vault/` or the path set by `CERT_STUDY_OBSIDIAN_VAULT`.

Notion is an optional projection for users who want a database view. This avoids slow or unavailable Notion queries during CBT and keeps scoring deterministic.

The public plugin does not automatically write to Notion. It prepares a sync plan through `prepare_notion_sync`; actual Notion MCP writes require user-selected database targets and `CERT_STUDY_ENABLE_NOTION_SYNC=1`.

## Extension Path

Add a new exam by adding:

1. exam metadata
2. domain metadata
3. concept metadata
4. synthetic or user-owned question bank
5. scoring rules if different
6. harness test for official question count and pass-line reporting

## Harness Contract

Minimum checks before publishing changes:

```bash
python3 -m unittest discover -s tests
python3 /Users/isanginn/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Expected coverage:

- DB initialization
- SQLD bank size
- domain allocation
- session answer progression
- scoring
- report content
- Obsidian session, concept, and review-queue note creation
- plugin manifest shape
- Notion sync disabled-by-default behavior
