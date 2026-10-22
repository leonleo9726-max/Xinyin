# GitHub Issue Tracker

Use this template for `docs/agents/issue-tracker.md` when work is tracked in GitHub Issues.

```markdown
# Issue Tracker

Issues are tracked in GitHub Issues for this repository.

## Commands

- List issues: `gh issue list`
- Read an issue: `gh issue view <number> --comments`
- Create an issue: `gh issue create --title "<title>" --body-file <file>`
- Edit labels: `gh issue edit <number> --add-label "<label>" --remove-label "<label>"`

## Rules

- Read the full body and comments before changing labels or posting comments.
- Do not close parent planning issues unless the user explicitly asks.
- Use the label strings from `docs/agents/triage-labels.md`.
```
