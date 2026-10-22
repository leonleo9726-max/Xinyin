# CONTEXT.md Format

Use `CONTEXT.md` to capture domain language that domain experts would recognise. Do not include implementation details unless the domain term cannot be understood without them.

## Structure

```markdown
# Context

## Glossary

### Term

Definition in domain language.

- Also called: optional aliases
- Not: nearby terms this should not be confused with
- Example: short concrete scenario
```

## Rules

- Add terms as soon as they are resolved.
- Prefer one precise paragraph over long background.
- Record disagreements as open questions instead of inventing certainty.
- Keep implementation file paths, class names, and database details out unless they are part of the domain language.
