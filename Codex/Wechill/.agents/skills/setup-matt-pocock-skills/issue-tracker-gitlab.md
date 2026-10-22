# GitLab Issue Tracker

Use this template for `docs/agents/issue-tracker.md` when work is tracked in GitLab Issues.

```markdown
# Issue Tracker

Issues are tracked in GitLab Issues for this repository.

## Commands

- List issues: `glab issue list`
- Read an issue: `glab issue view <id> --comments`
- Create an issue: `glab issue create --title "<title>" --description-file <file>`
- Edit labels: `glab issue update <id> --label "<label>"`

## Rules

- Read the full body and comments before changing labels or posting comments.
- Do not close parent planning issues unless the user explicitly asks.
- Use the label strings from `docs/agents/triage-labels.md`.
```
