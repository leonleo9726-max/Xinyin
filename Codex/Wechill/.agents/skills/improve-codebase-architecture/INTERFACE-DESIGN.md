# Interface Design

Use this when a candidate refactor needs concrete interface options.

## Compare Options

For each proposed interface, describe:

- **Call site**: What callers need to know.
- **Invariants**: What the module guarantees.
- **Errors**: What can fail and how failures surface.
- **Dependencies**: What is injected, configured, or hidden.
- **Test surface**: Which behavior can be tested through the interface.

## Prefer

- Small method sets over broad utility surfaces.
- Domain terms over technical placeholders.
- Explicit invariants over comments at call sites.
- Returning values over mutating hidden state, unless the module's purpose is to own state.

## Avoid

- Interfaces that mirror every implementation step.
- Parameters that must be passed together but are not named as a concept.
- Seams with one adapter and no current variation.
