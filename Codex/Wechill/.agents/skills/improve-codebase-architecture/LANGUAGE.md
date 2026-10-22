# Architecture Language

Use this vocabulary consistently when discussing architecture.

- **Module**: Anything with an interface and an implementation, including a function, class, package, feature slice, or service.
- **Interface**: Everything a caller must know to use a module: types, invariants, error modes, ordering, configuration, and side effects.
- **Implementation**: The code and behavior hidden behind the interface.
- **Depth**: Leverage at the interface. Deep modules hide substantial behavior behind a small, stable interface.
- **Shallow module**: A module whose interface is almost as complex as its implementation.
- **Seam**: A place where behavior can vary without editing callers in place.
- **Adapter**: A concrete implementation that satisfies an interface at a seam.
- **Leverage**: What callers gain from the interface.
- **Locality**: How much change, knowledge, and bug fixing can stay concentrated in one module.

## Principles

- **Deletion test**: If deleting a module makes complexity disappear, it was a pass-through. If deleting it spreads complexity across callers, it was earning its keep.
- **The interface is the test surface**: Tests should verify behavior through the interface that callers actually use.
- **One adapter is a hypothetical seam; two adapters make it real**: Avoid abstracting around a single concrete path unless the seam is already paying for itself.
