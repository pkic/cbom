# 0006. A profile declares the carrier versions it accepts

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.2 — Profile identity & metadata
- **Topic / issue:** #5
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

CycloneDX 1.7 introduced cryptography features the example profile relies on, while documents in
circulation were produced under earlier versions. A profile has to say something about documents
it was not written against, both older and newer, and a consumer has to be able to tell a stale
document from a non-conforming one.

## Options considered

- **Option A — a single supported version.** Unambiguous (trade-off: every carrier release
  invalidates the existing corpus, and a profile revision becomes necessary for a change that
  does not affect its content).
- **Option B — a declared range with a tested version.** `appliesTo` states a minimum and the
  version the profile was exercised against (trade-off: the validator must classify and report
  bands, and results outside the tested version are qualified rather than definitive).

## Decision

Option B. Each profile declares `appliesTo` per carrier with `min` and `tested`. Documents are
classified into four bands: below `min` is unsupported and refused with an explanation; between
`min` and `tested` is legacy, evaluated and flagged; at `tested` is the target band; above
`tested` is newer, evaluated with the result qualified.

## Rationale

Refusing a document because it predates the profile discards information the consumer already
has. Evaluating it and saying so lets the consumer weigh the result. Separating the three
version axes — carrier format, profile version and content revision — keeps a carrier release
from being confused with a change in what the profile requires.

## Consequences

The distinction between "refused" and "does not conform" must survive into tooling, so the
validator returns distinct exit codes and the tests assert both. A carrier release does not by
itself require a profile revision; raising `tested` is a maintenance step recorded in the
profile changelog.

## Links

- Versioning section of the methodology documentation.
- `versioning-and-legacy-cboms.md`.
- Carrier version band tests in `tests/run-profile-tests.sh`.
