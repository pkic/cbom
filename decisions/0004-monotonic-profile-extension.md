# 0004. A derived profile may add and tighten, never relax

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.9 — Extensibility & profile composition
- **Topic / issue:** #9
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

The PQC migration profile shares most of its content with the interface disclosure baseline.
Restating the shared rules would let the two drift apart. Once one profile builds on another,
the question is what the derived profile is allowed to change, and what a claim of conformance
to it tells a consumer about the base.

## Options considered

- **Option A — free override.** A derived profile may change any inherited rule in any direction
  (trade-off: conformance to the derived profile implies nothing about the base, so a consumer
  must evaluate both and the inheritance saves only editing effort).
- **Option B — monotonic extension.** A derived profile may add rules, raise an obligation level
  and narrow a permitted value set, but may not lower a level, widen a set, or remove a rule
  (trade-off: a sector needing genuinely weaker requirements cannot derive and must write a
  separate profile evaluated independently).

## Decision

Option B. Overrides are checked mechanically against the inherited rule; an override that
relaxes is a defect in the profile and is refused before any document is examined. Conformance
to a derived profile therefore implies conformance to its base, transitively.

## Rationale

The implication is the practical benefit of composition. A consumer who accepts the baseline can
accept any derived profile's conformance claim without reading it, which is what allows a sector
to specialise a common baseline without every consumer having to re-examine the result. Free
override saves editing effort and yields no such implication.

## Consequences

Independent evaluation remains available for the unrelated case: one CBOM assessed against
several profiles yields several separate verdicts, with no relationship asserted between them.
Profiles pin the base by identifier and version, so a base revision does not silently change the
meaning of a derived claim. Multiple inheritance is not currently defined.

## Links

- Composition subsection of the Profile section.
- `tests/fixtures/profile-invalid-relaxing.rules.json` and the composition tests.
