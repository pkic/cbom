# 0011. A rule id is local to its profile and is cited against a profile tag

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.2 — Profile identity & metadata (with consequences for 3.9)
- **Topic / issue:** #5, and #9 for the composition half
- **Deciders:** not yet taken; settles Q33
- **Decision rule applied:** lazy consensus (pending)

<!--
Implemented in the worked example. The baseline moves to v0.7, the migration profile to v0.6 and
is renumbered entirely. Nothing had been released, so the family was renumbered clean rather than
migrated.
-->

## Context

Q33 asks how requirement numbers are allocated across a family of profiles. It was comfortably
theoretical with two profiles. It stopped being theoretical the moment the baseline needed a third
product rule.

The baseline used `P1`, `P2` for product rules and `I1` to `I9` for interface rules. The migration
profile used `M1` to `M10` for its own rules — and `P3`, `P4` for its two product rules,
continuing the baseline's sequence into a space the baseline had not reserved. Adding a product
rule to the baseline therefore did not merely look untidy: `load_profile` raised
`ProfileError: rule id P3 collides with an inherited rule` and refused to evaluate any document at
all. **A base could not grow while a derived profile held an id in its space.**

Two things settled the shape of the answer.

**Nothing has been released.** No conformance report, stored claim or supplier tracking cites any
of these ids against a document evaluated under any version. So the family can be renumbered clean
and no id is retired. This removes the constraint that would otherwise have forced a compromise:
there is nothing to be compatible with.

**A rule is always cited alongside the profile that imposed it.** A conformance report already
prints the profile; a claim already names it. If the citation carries the profile anyway, the id
does not have to be globally unique — and once that is true, most of the difficulty disappears.

## Options considered

- **Option A — reserve ranges.** The base takes `P1` to `P9`, derived profiles take `P10` upward
  (trade-off: works until a base needs a tenth rule, and the reservation is invisible in any file,
  so the next author has to be told about it. It also does not survive a third level, which needs
  its own range in a space nobody is coordinating).
- **Option B — one letter per profile.** The base keeps `P` and `I`; every derived profile numbers
  all of its own rules under a single letter of its own, whatever their kind (trade-off: a rule id
  stops saying whether the rule is product-level or per-interface, and single letters are a
  namespace nobody administers. This was the earlier proposal in this record, and it was
  implemented in migration v0.5 before being replaced here).
- **Option C — the id is local, and the citation carries the profile.** Every profile numbers its
  own rules from 1 in each kind, at every level. Uniqueness moves off the id and onto a short
  profile tag (trade-off: `I1` alone stops naming a rule, so every citation is longer and every
  reference in prose has to be written as `interface-disclosure#I1` or be ambiguous).

## Decision

Proposed: Option C.

**Every profile carries a `profileTag`** — a short kebab-case handle, defaulting to the last
segment of the `profileId`. `interface-disclosure`, `pqc-migration`.

**A rule id is local to the profile that declares it.** The citable form is `<profileTag>#<ruleId>`
and nothing shorter names a rule. Three profiles in one family may each declare an `I1`, and in the
worked example three of them now do.

**The letter is fixed by the kind of rule**, not chosen by the author: `P` evaluated once per
product, `I` once per declared interface, `G` once per entry in a group, members numbered under
their group as `G1.2`. Because the tag already says which profile a rule belongs to, the letter is
free to carry the thing a reader actually wants from it.

**Numbering restarts at 1 in each kind, in every profile, at every level.**

**A rule keeps the id of the profile that introduced it**, however far down the family it is later
tightened. An override therefore names its target in full — `interface-disclosure#I9` — and an
unqualified override is rejected rather than guessed at, because a bare `I9` in the migration
profile is that profile's own ninth interface rule, which is a different rule.

**The tag is the only thing that must be unique along a chain.** This is what replaces the old
rule-id collision check. **C15** rejects a tag an ancestor already uses; **C16** rejects a rule id
whose letter contradicts the section it sits in, and rejects an unqualified override.

**A released id is never reused.** Nothing is released, so the rule starts from the versions issued
here. Once it bites, an id retired in a later version stays retired and the sequence carries a gap:
a report or claim may cite it against a document evaluated under the earlier version, and reusing
it would make that report silently wrong rather than merely stale. C16 deliberately does not check
for contiguity, because a dense sequence is exactly what this forbids.

## Rationale

The collision was not a naming preference, it was a hard failure, and any of the three options
fixes it. What separates them is what happens at the third level and beyond.

Option A needs a range per profile in a space nobody administers, and the reservation lives in no
file. Option B needs a letter per profile in the same unadministered space, and buys that by giving
up the one thing the letter was good for. Both are schemes for sharing a single global id space
between authors who never meet. Option C stops sharing it. An author numbers their own rules from
1 and coordinates on exactly one token — the tag — which they choose once and which a checker can
verify against the chain they actually extend.

That is why depth stops being a question. A third-level profile is not a harder case under Option
C; it is the same case. The worked example now carries a third-level test fixture that declares its
own `P1` and its own `I1`, both of which *both* ancestors also use, and the report shows
`interface-disclosure#I1`, `pqc-migration#I1` and `sector-settlement#I1` side by side.

The cost is real and worth naming: `I1` on its own no longer means anything, so prose that used to
say "rule I3" now has to say which profile's. Every reference in the methodology has been rewritten
accordingly. The compensation is that a report is now unambiguous when read out of context, which
is how reports are usually read.

Enforcing the letter convention was left open in the earlier form of this record, on the grounds
that it would reject a profile that chose a different scheme deliberately. That objection does not
survive Option C. The letter no longer competes with ownership — the tag carries that — so it has
one job, and there is no legitimate reason for a profile to give its per-interface rules a `P`. C16
enforces it.

## Consequences

- Baseline v0.6 → **v0.7**: gains `profileTag`. No rule id changes; the baseline was already the
  base of its family and already used the kind letters.
- Migration profile v0.5 → **v0.6**: renumbered entirely. `M1`–`M9` → `I1`–`I9`, `M10` → `G1` with
  members `G1.1`–`G1.3`, `M14` → `P1`. The override on the baseline's `implementationPurl` rule now
  names `interface-disclosure#I9`. No requirement on any document changes and no rule changes
  meaning: rule ids appear in reports and claims, not in CBOMs. The mapping is in the profile's
  changelog.
- `validate_cbom` keys rules, origins and report rows by qualified id, orders a report by chain
  position then kind then number, prints the chain above the report, and rejects a repeated tag and
  an unqualified override. `check_profile` gains C15 and C16.
- Three new test fixtures exercise the third level: a valid one, one relaxing a rule its
  *grandparent* introduced, and one taking its grandparent's tag. The first proves the scheme, the
  second proves monotonicity holds transitively, the third proves the tag check is what now carries
  the load. Twenty-six new tests; the suite runs 149 and passes.
- Migration v0.5's own changelog entry is kept and marked superseded rather than deleted, because
  it is what that file did.

## Links

- Q33, which this settles, and Q24, which asks how a claim names conformance to several profiles
  and therefore depends on ids being stable and on the claim carrying the tags.
- Decision 0012, which is what forced the question by needing `P3` and `P4` back in the baseline.
- Conformance requirements C15 and C16; `check_override_tightens` and the tag check in
  `load_profile`, which is where a violation surfaces.
