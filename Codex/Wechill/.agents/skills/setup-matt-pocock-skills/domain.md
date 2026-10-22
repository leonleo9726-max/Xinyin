# Domain Docs

Use this template for `docs/agents/domain.md`.

```markdown
# Domain Docs

## Layout

Single-context repo:

- Domain glossary: `CONTEXT.md`
- Architecture decisions: `docs/adr/`

For multi-context repos, read `CONTEXT-MAP.md` first and follow it to the relevant context-specific glossary and ADR directory.

## Consumer Rules

- Read the relevant `CONTEXT.md` before naming domain concepts in issues, PRDs, tests, or architecture notes.
- Read ADRs in the area before proposing architectural changes.
- If code and docs disagree, surface the conflict before editing.
- Add domain terms only when they are meaningful to domain experts.
```
