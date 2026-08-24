# 0014. A derived profile may tighten one member of an inherited group, and widen its coverage

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.9 — Building one profile on another
- **Topic / issue:** #9
- **Deciders:** not yet taken; settles Q49
- **Decision rule applied:** lazy consensus (pending)

## Context

A group rule constrains a repeated group keyed by a controlled vocabulary, and its member rules are
evaluated inside an entry. A derived profile could add a whole group and could tighten an ordinary
inherited rule. It could not tighten one *member* of a group it inherited: group rules were
concatenated, and an override naming a member matched nothing.

The case is not hypothetical. The migration profile's capability group requires a status for every
cryptographic purpose, the full attribute set for the purposes in scope, and a roadmap reference at
MAY. A settlement or telecom profile sequencing a cutover across counterparties needs that roadmap
reference for every purpose, not only where a supplier volunteers one. There was no way to say so.

The two workarounds were both worse than the gap:

- **Restate the group.** A restated group replaces the inherited one, and with it the base's
  `coverage`. The property most worth inheriting — that a deferred purpose still owes a status,
  which is what stops a staged profile becoming a permanent floor — would be silently replaced by
  whatever the derived profile happened to write.
- **Add a parallel group** over the same vocabulary. A producer is then asked for the same fact
  twice under two names, and a report shows both.

Q49 recorded this. The limitation had previously existed only as a comment in `load_profile`.

## Options considered

- **Option A — leave it**, and let a derived profile declare its own group (trade-off: the two
  workarounds above, one of which quietly discards the guarantee the base was carrying).
- **Option B — allow an override to name a member** by qualified id, tightened under the same rules
  as any other rule (trade-off: a member has a `requiredWhen` guard as well as a constraint, and a
  guard is a different kind of thing to compare).
- **Option C — allow coverage to be widened** without touching members (trade-off: solves breadth
  and not depth, which is the case a sector profile actually raises).

## Decision

Proposed: **Option B and Option C together**. They are the two halves of the same question — depth
per member, and breadth across keys — and each is cheap once the override machinery reaches inside a
group.

**A member is overridden by qualified id.** `pqc-migration#G1.3`. Level, withholdability and
constraint are compared exactly as for any other rule, under decision 0013.

**The group shell is overridden by its own id**, and the only field an override may change there is
`coverage`, which may be widened and never narrowed. Narrowing it is how a staged profile becomes
the permanent floor decision 0010 exists to prevent, arriving by a different route.

**A `requiredWhen` guard may be removed, and may not be added or changed.** The guard says when a
rule applies:

- Removing it makes the rule apply always, which is strictly more demanding. Permitted, and recorded
  as a composition note.
- Adding one where the base has none makes the rule apply less often. Refused.
- Changing an existing guard is **refused rather than compared**. Whether one condition is broader
  than another depends on the values a document carries, which the profile does not hold. A profile
  that wants a different condition removes the guard, or adds a rule under its own id.

**The members a derived profile does not name are inherited unchanged**, as is the group's key
vocabulary. That is the whole point: sharpening one member costs nothing else.

## Rationale

The guard is the part worth dwelling on, because it is the relaxation hardest to see by reading. A
narrowed guard leaves the rule listed in the profile, present in every report, and named in the
conformance claim — and quietly not firing. Compare that with a lowered `minCount`, which at least
shows a different number on the page. Refusing a changed guard rather than attempting to compare two
conditions is the same choice decision 0013 made for unrecognised constraint kinds, and for the same
reason: a checker that waves through what it cannot assess produces the same green report as one
that has checked.

Coverage moving in only one direction matters more than it looks. The staged-profile argument in
0010 rests entirely on a deferred purpose still owing a status. If a sector profile could narrow
coverage to its own purposes, every sector would quietly opt out of the questions it found
inconvenient, and the vocabulary would stop meaning anything across profiles — which is the
fragmentation this methodology exists to prevent.

Option A was rejected on the strength of what the workarounds cost rather than on the difficulty of
implementing B. A gap whose workarounds both damage the base's guarantees is not a gap that can be
left open once someone needs it.

## Consequences

- `load_profile` resolves overrides against inherited group shells and members before concatenating.
  `check_guard_tightens` and `check_coverage_tightens` are new; `check_override_tightens` calls the
  first.
- Members are deep-copied on inheritance, so tightening one in a derived profile cannot mutate the
  base's own object — a bug that would have been invisible until two profiles derived from one base
  in the same process.
- The third-level test fixture now tightens `pqc-migration#G1.3` from MAY to MUST and removes its
  withholdability, which is exactly the case Q49 described. Three new invalid fixtures: a guard
  added where the base has none, a guard narrowed, and coverage narrowed.
- Twelve new tests. The suite runs 185 and passes.
- Q49 is settled. Q25 loses one of its blockers: a finance profile can now sharpen the capability
  group rather than restate it.

## Links

- Q49, which this settles, and Q25, which it partly unblocks.
- Decision 0010, which created the group rule and the coverage guarantee this protects; 0013, whose
  constraint comparison this reuses and whose refuse-what-you-cannot-assess principle it extends to
  guards; 0011, which made a member citable as `<profileTag>#G1.3` in the first place.
