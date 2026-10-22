# Local Markdown Issue Tracker

Use this template for `docs/agents/issue-tracker.md` when work is tracked as local Markdown files.

```markdown
# Issue Tracker

Issues are tracked as Markdown files under `.scratch/issues/`.

## File Format

Each issue is one file named `<slug>.md` with:

- Title
- Status or triage role
- Body
- Acceptance criteria
- Links to related files or parent issues

## Rules

- Create `.scratch/issues/` if it does not exist.
- Keep one issue per file.
- Use the role strings from `docs/agents/triage-labels.md`.
- Do not delete or rewrite existing issue files unless the user asks.
```
