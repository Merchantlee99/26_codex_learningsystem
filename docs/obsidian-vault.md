# Obsidian Vault

Obsidian is the default notebook projection for this plugin.

SQLite remains the source of truth for scoring, attempts, and review scheduling. Markdown files are generated so the learner can inspect wrong answers without depending on Notion MCP availability.

## Default Location

By default, finished sessions write notes under:

```text
obsidian_vault/
  certifications/
    SQLD/
      sessions/
      concepts/
      review-queue.md
```

To write directly into an existing Obsidian vault, set:

```bash
export CERT_STUDY_OBSIDIAN_VAULT="/absolute/path/to/your/Obsidian Vault"
```

## Generated Notes

| Path | Purpose |
| --- | --- |
| `certifications/<EXAM>/sessions/*.md` | One finished CBT session with score, pass line, weak areas, wrong questions, explanations, and next review date |
| `certifications/<EXAM>/concepts/*.md` | One cumulative note per wrong concept, including recent wrong-answer history |
| `certifications/<EXAM>/review-queue.md` | Review schedule generated from the local SQLite review queue |

## Privacy Boundary

Generated vault Markdown files are ignored by git:

```text
obsidian_vault/**/*.md
```

The public repo keeps only the code and an empty `.gitkeep`. Personal study records should stay local.

## Notion Relationship

Notion is optional. Use it only as a secondary database view after the user chooses target databases.

The default study loop does not need Notion:

```text
Codex chat -> MCP tool -> SQLite -> Markdown -> Obsidian
```
