# 0011. A derived profile numbers its rules in its own space, and retired ids are not reused

- **Status:** Proposed
- **Date:** 2026-08-21
- **Aspect:** 3.2 — Profile identity & metadata (with consequences for 3.9)
- **Topic / issue:** #5, and #9 for the composition half
- **Deciders:** not yet taken; settles Q33
- **Decision rule applied:** lazy consensus (pending)

## Context

Q33 asks how requirement numbers are allocated across a family of profiles. It has been
comfortably theoretical with two profiles. It stopped being theoretical the moment the baseline
needed a third product rule.

The baseline uses `P1`, `P2` for product rules and `I1` to `I9` for interface rules. The migration
profile uses `M1` to `M10` for its own interface and group rules — and `P3`, `P4` for its two
product rules, continuing the baseline's sequence into a space the baseline did not reserve. Adding
a product rule to the baseline therefore does not merely look untidy; `load_profile` raises
`ProfileError: rule id P3 collides with an inherited rule` and refuses to evaluate any document at
all. The base cannot grow while a derived profile is squatting in its numbering.

## Options considered

- **Option A — reserve ranges.** The base takes `P1` to `P9`, derived profiles take `P10` upward
  (trade-off: works until a base needs a tenth rule, and the reservation is invisible in any file,
  so the next author has to be told about it).
- **Option B — namespace every id by profile**, as `interface-disclosure/P3` (trade-off:
  unambiguous, and every existing reference in the documentation, the examples and the reports
  becomes longer and harder to say aloud. The kind letter already carries most of the value).
- **Option C — each profile numbers in its own letter space.** The base keeps the kind letters `P`
  and `I`; every derived profile numbers all of its own rules under its own letter, whatever kind
  they are (trade-off: a rule id no longer tells a reader whether the rule is product-level or
  per-interface).

## Decision

Proposed: Option C, with one addition.

**The base profile of a family keeps the kind letters.** `P` for product-level rules, `I` for
per-interface rules. This is what the baseline does today and no existing reference changes.

**A derived profile numbers every rule it adds under a single letter of its own**, in one sequence,
regardless of kind. The migration profile's product rules move from `P3` and `P4` to `M13` and
`M14`, joining `M1` to `M10` in the `M` space.

The trade-off Option C carries — that an id no longer says what kind of rule it is — is smaller
than it looks. A reader who needs to know reads the report, which already groups product-level
rules separately from each interface, or the profile, which declares them under `productRules` and
`interfaceRules`. The id's job is to be citable in a conformance claim and stable across versions,
and for that a flat sequence per profile is better than a kind letter shared between profiles.

**Retired ids are not reused.** `M11` and `M12` were retired when capability moved into a group
rule in v0.4, so the migration profile's new product rules take `M13` and `M14` rather than filling
the gap. A conformance report, a stored claim, or a supplier's own tracking may cite `M11` against
a document evaluated under v0.3; a later rule reusing that id would make an old report silently
wrong rather than merely stale.

## Rationale

The collision is not a naming preference, it is a hard failure: the validator refuses the profile,
so the base cannot gain a rule while a derived profile holds an id in the base's space. Any of the
three options fixes that. Option C is preferred because it makes the ownership of an id readable
from the id itself — `M` means the migration profile put it there — which is the property that
matters when a sector profile derives from a derived profile and a reader is looking at a rule
three levels from where it was written.

Reserving ranges was rejected because the reservation lives nowhere. Namespacing was rejected
because the cost falls on every reference in exchange for disambiguating a case the letter already
disambiguates.

Not reusing retired ids is the smaller half of this record and the one more likely to be skipped.
It costs nothing — the id space is unbounded — and it protects the only thing a rule id is for,
which is citing a rule in a claim that someone may read years later.

## Consequences

- The migration profile's `P3` (coverage) and `P4` (minimum providers) become `M13` and `M14`.
  Since coverage moves down into the baseline under decision 0012, only the provider rule survives
  the move, as `M14`.
- The baseline is free to add `P3` and `P4`, which decision 0012 does.
- No document changes: rule ids appear in reports and claims, not in CBOMs.
- The methodology gains a stated numbering convention, which C4 already half-enforces by requiring
  a stable identifier on every rule. Whether the checker should enforce the letter convention as
  well is left open: it would reject a legitimate profile that chose a different scheme
  deliberately, and the failure it would catch is caught already by the collision check.

## Links

- Q33, which this settles, and Q24, which asks how a claim names conformance to several profiles
  and therefore depends on ids being stable.
- Decision 0012, which is what forced the question.
- `check_override_tightens` and the collision check in `load_profile`, which is where the failure
  surfaces today.
