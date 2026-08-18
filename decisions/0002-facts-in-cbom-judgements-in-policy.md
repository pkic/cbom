# 0002. A CBOM records facts; judgements are made by external policy

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.3 — Format-independent attribute model
- **Topic / issue:** #1
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

The baseline profile originally carried a `pqcPosture` attribute with values `classical`,
`hybrid` and `pqc`. Whether a given algorithm set counts as quantum-safe is assessed against
guidance that is still being revised, so the correct value of that attribute can change without
the product changing.

## Options considered

- **Option A — keep the derived value in the CBOM.** The consumer reads a verdict directly
  (trade-off: the stored value goes stale silently, and different producers apply different
  criteria to the same facts).
- **Option B — record only the inputs.** An external, versioned policy computes the verdict at
  the time of asking and dates it (trade-off: a consumer must run or obtain a policy evaluation
  rather than reading an answer from the document).

## Decision

Option B. `pqcPosture` was removed. Profiles require the facts a judgement is derived from,
such as the algorithms an interface uses and supports. Post-quantum posture and cryptographic
maturity are computed externally and carry the policy version and the date applied.

## Rationale

A CBOM revision is an immutable point-in-time record. Embedding a time-dependent judgement in
one produces a document that is authoritative in appearance and wrong in substance as soon as
criteria move. Keeping the inputs allows the same immutable facts to be re-evaluated whenever
the criteria change.

## Consequences

Applies to the naming conventions as well: an attribute name describes what is disclosed, never
what it implies, so `keyExchangeSupported` is acceptable and `pqcReady` is not. Any profile
proposing a score, rating or readiness verdict should be checked against this record.

## Links

- Policy Evaluation section of the methodology documentation.
- Decision 0005 (naming conventions).
