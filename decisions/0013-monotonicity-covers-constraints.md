# 0013. Monotonicity is checked for constraints, and a rule that cannot fail is not a rule

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.9 — Building one profile on another, and 3.5 — Conformance & validation
- **Topic / issue:** #9, and #7 for the well-formedness half
- **Deciders:** not yet taken
- **Decision rule applied:** lazy consensus (pending)

<!--
Found by probing the tools rather than by reading them: four defects, three of which produce a
green report where a red one is due. Implemented in the worked example; no profile version changes,
because no rule changed — what changed is which profiles the tools will accept at all.
-->

## Context

The composition model rests on one guarantee: **extension is monotonic**, so a document conforming
to a derived profile conforms to its base. The Profile page states it, the Conformance section
relies on it, and a conformance claim naming a derived profile is only worth reading because of it.

`check_override_tightens` compared two fields: `level` and `withholdable`. An override carrying a
`constraint` replaced the inherited one outright, with nothing compared. So this was accepted:

```json
"overrides": [
  { "id": "interface-disclosure#I6", "constraint": { "minCount": 1 } },
  { "id": "interface-disclosure#I9", "constraint": { "present": true } }
]
```

The first halves an inherited minimum. The second replaces "the implementing library is identified
by a `pkg:` Package URL" with "something is there", so free text satisfies the rule that exists to
make records correlatable across suppliers. Both documents were evaluated against the weakened
rules, both were reported as conforming, and `check_profile` reported **C7 as passing** with the
words *no override relaxes it*. That is worse than an unchecked property: it is a false assurance,
issued in the place a reader would look to confirm the guarantee holds.

Three further defects came out of the same probing, and they share a shape.

**An unimplemented constraint key passes everything.** `startswith` instead of `startsWith`,
`enumref` instead of `enumRef`: the evaluator recognised nothing in the constraint and fell through
to `return (True, "ok")`. The rule reported `ok` against every value. C4 passed it, because a
constraint object was present.

**An unresolvable vocabulary reference fails everything.** `enumRef` naming a vocabulary the
profile does not declare resolved to the empty list, so every value failed, and the report said
only `= 'TLS'` — not that the profile was broken. C13 already caught this for group *keys*, and
nowhere else.

**A rule with no constraint raised an exception mid-evaluation.** `check_profile` reported it
correctly as C4; `validate_cbom` produced a traceback rather than the exit code its own contract
defines for a bad profile. The two tools disagreed about the same file.

## Options considered

- **Option A — document the limits and leave the tools.** State on the Profile page that constraint
  overrides are not checked (trade-off: the guarantee then holds by convention among people who
  read the caveat, which is not what the composition model claims, and the tool keeps printing
  *no override relaxes it*).
- **Option B — compare constraints structurally**: require an override's constraint to be a
  superset of the base's obligations, comparing each kind on its own terms (trade-off: needs a
  comparator per constraint kind, and a rule for kinds nobody has written yet).
- **Option C — forbid constraint overrides entirely.** A derived profile wanting a stricter
  constraint adds a new rule under its own id (trade-off: two rules then constrain one attribute
  and a report shows both, which is confusing where one is strictly stronger; and it removes the
  one mechanism that lets a sector profile sharpen a baseline rule in place).

## Decision

Proposed: Option B, with the unknown case refused rather than permitted, plus a new requirement for
the three evaluability defects.

**Constraints are compared kind by kind.** A minimum may rise and not fall. A list of permitted
values may shrink and not grow, whether written inline or reached through `enumRef`. A required
prefix may lengthen and not shorten. A structural rule may not change which interface type it
counts, and an override may not change which attribute a rule is about — that is a different rule,
which a derived profile adds under its own id.

**An override may add an obligation and may not drop one.** Adding a constraint the base did not
carry is a tightening and is recorded as a composition note. Removing one the base carried is a
relaxation, and it is the relaxation most easily written by accident, because the rule still looks
present in the file. Removing `orDeclaredAbsent` is the exception and is a tightening: it takes
away an escape hatch.

**A constraint the comparison does not recognise is refused.** This is the part worth arguing over,
because it means a constraint kind added later breaks every override that uses it until a
comparator is written for it. That is the intended cost. A checker that waves through what it
cannot assess produces the same green report as one that has checked, and the whole value of the
check is that the two look different.

**C17 (new, MUST).** Every rule can pass a document and can fail one: it carries a constraint, the
constraint is one the evaluator implements, and any vocabulary it names is declared. Checked in
`check_profile`, and enforced in `validate_cbom` at load, so a profile with such a rule is refused
rather than evaluated. The two silent fall-throughs in the evaluator now raise.

## Rationale

The four defects have one shape: **the tool reported success where it had established nothing.**
A relaxing override passed the check that exists to catch it. A misspelled key produced a rule that
passed everything. An unresolvable vocabulary produced one that failed everything for an unstated
reason. A missing constraint crashed rather than refusing. In three of the four the report is green.

This is the same failure the methodology already named for group rules — C13 exists because a group
keyed by an undeclared vocabulary requires an entry for no keys, so every document satisfies it and
the rule reads as passing. The principle was right and was applied in one place. C17 applies it
generally, and the constraint comparison applies it to composition.

Refusing the unknown constraint kind deserves its own defence, since it will eventually block
someone. The alternative is to permit what cannot be assessed, and the cost of that is not
theoretical: it is exactly how `minCount` came to be relaxable in the first place. A comparator is
a few lines; a silently unenforced guarantee is discovered by whoever relied on it.

Option C was rejected because tightening a rule in place is the mechanism working as intended, and
the migration profile already depends on it.

## Consequences

- `check_override_tightens` gains a constraint comparison with a comparator per kind, and rejects
  an override whose constraint it cannot compare. Tightenings are recorded as composition notes and
  printed above the report, so a reader sees what the derived profile sharpened.
- `validate_cbom` gains `check_evaluable`, run on the resolved profile at both ends of
  `load_profile`; the two `return (True, "ok")` fall-throughs raise; `validate` is wrapped so a
  profile error exits 3 rather than tracebacking. `check_profile` gains C17.
- No profile version changes. No rule changed and no document's verdict changes; what changed is
  which profiles the tools will accept at all.
- Five new fixtures: two relaxations that used to pass, one tightening that must still pass, and
  one for each half of C17. The tightening fixture is the important one — a check that rejects
  relaxations is only worth having if it still admits the extensions the mechanism exists for, so
  the suite asserts that the raised minimum is accepted *and* that it then fails a document.
- Twenty-four new tests. The suite runs 173 and passes.
- The Profile page said a validator "rejects any override that relaxes an inherited rule". That was
  false when written and is now true; the page also says what "relaxes" means for a constraint,
  which is the part that was doing the work.

## Links

- Decision 0004, which established monotonic extension, and which this makes enforceable rather
  than declared.
- Conformance requirements C7, C13 and C17. C13 is the precedent: the same defect, caught in one
  place, which is what suggested looking for it elsewhere.
- Q35, which asks whether an inherited vocabulary may be *widened*. The comparison implemented here
  answers the narrowing half and rejects widening, which is the conservative reading — if Q35
  settles the other way, the `enumRef` comparator is where it lands.
