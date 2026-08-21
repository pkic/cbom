# 0008. A profile declares its subject, its boundary, and the lifecycle stages it accepts

- **Status:** Proposed
- **Date:** 2026-08-21
- **Aspect:** 3.1 — Profile objective & scope (with consequences for 3.2)
- **Topic / issue:** #4, and #5 for the identity fields
- **Deciders:** not yet taken; raised from a member submission on the profile preamble
- **Decision rule applied:** lazy consensus (pending)

<!--
Like records 0001 to 0007, this one is implemented in the worked example, so the group is asked
to ratify or reverse a position that exists in the drafting rather than to decide in the
abstract. The Consequences section records what reversing it would involve.
-->

## Context

A member proposed that every profile begin with a mandatory structured preamble carrying
`profileId`, `version`, `objective`, `intendedConsumers`, `supportedDecision`, `orientation`,
`subjectType`, `inScope`, `outOfScope`, `lifecycleStages` and `exclusionsRationale`, with the
decision phrased as an action choice and the boundary expressed as a tuple of subject, asset or
relationship types, interfaces or domains, and lifecycle stage.

Six of the eleven fields already exist in the rules file under established names and are checked
by `check_profile.py`: `profileId` and `version` (C2), `objective.consumer` and
`objective.decision` (C1), and `exclusions[].item` with `exclusions[].reason` (C8). The
submission's substance is therefore narrower than its field list, and rests on three points that
are not currently met.

**The subject is undeclared.** Method step 2 asks an author to decide whether the subject is a
product, a service, a component, or a bounded part of an estate. That vocabulary exists only in
prose. A consumer holding a profile cannot determine mechanically whether it applies to the thing
in front of them.

**The accepted lifecycle stages are undeclared, and this affects verdicts.** `lifecycleStage` is
a per-interface attribute, rule I8, constrained to `intended`, `implemented`, `configured` or
`observed`. Any of the four satisfies the rule. A document declaring every interface as
`intended` — cryptography the producer plans to implement — conforms to the Interface Disclosure
Baseline. A procurement consumer would not knowingly accept that, and the profile has no way to
say so.

**The action-choice test is unenforceable.** Method step 1 states the test: a decision must
contain a choice, so "whether to schedule this system for upgrade, replacement, or no action"
passes and "to understand our cryptographic position" does not. C1 checks only that a `decision`
string is present, so the test lives in guidance a profile author may not read.

## Options considered

- **Option A — adopt the preamble as submitted.** Eleven flat fields, all mandatory (trade-off:
  four are renames of existing fields, costing a sweep of two rules files, the validator, the
  checker, nine fixtures, Terms and Conformance, for no change in what a profile expresses;
  `orientation` has no consumer that acts on it; and the flat list obscures that four of the
  fields are one boundary).
- **Option B — take the three substantive points as a `scope` object, and reject the renames.**
  Add `scope` with `subjectType`, `relationshipTypes` and `lifecycleStages`, extend `objective`
  with `decisionOptions`, and leave the six existing fields alone (trade-off: the submission is
  only partly accepted, and the group has to be willing to say that four of the names were
  already there).
- **Option C — record the gaps in the open questions register and defer.** No schema change
  before the August release (trade-off: the lifecycle-stage hole stays open, and it is the kind a
  buyer discovers after relying on a verdict).

## Decision

Proposed: Option B.

```json
"objective": {
  "consumer": "...",
  "decision": "...",
  "decisionOptions": ["upgrade", "replace", "accept as is", "investigate further"]
},
"scope": {
  "subjectType": "product",
  "relationshipTypes": ["interface"],
  "lifecycleStages": ["implemented", "configured", "observed"]
}
```

`subjectType` takes one of `product`, `service`, `component`, `estate-subset`, the vocabulary
Method step 2 already names. `lifecycleStages` is an acceptance constraint, not a description: a
document whose interface declares a stage outside the set fails I8, in the same way a carrier
version outside `appliesTo` is refused. `decisionOptions` requires two or more entries, which is
what makes the action-choice test mechanical.

Conformance changes: C1 gains the `decisionOptions` requirement; a new **C11 (MUST)** requires
the `scope` object with `subjectType` and `lifecycleStages` populated. Both are checked by
`check_profile.py`.

`relationshipTypes` is declared but derived-and-checked rather than trusted: the checker compares
the declaration against what the rules actually constrain and fails on disagreement. A hand-
maintained scope statement that drifts from the rules is worse than no statement, because it
reads as authoritative.

`orientation`, `intendedConsumers`, `supportedDecision`, `inScope`, `outOfScope` and
`exclusionsRationale` are not adopted. The middle four duplicate existing fields; `orientation`
classifies profiles without any consumer acting on the classification, and if profiles are ever
catalogued it belongs to the registry rather than to the profile.

## Rationale

The lifecycle-stage constraint is the item that changes outcomes. The other two improve a
profile's legibility; this one closes a case where a document can conform while disclosing
intentions rather than facts, and the consumer reading the verdict cannot tell.

It is also cheap to adopt. The Interface Disclosure Baseline is a disclosure baseline and would
declare all four stages, so its behaviour does not change. The field's value is that a
procurement or migration profile can then narrow it, which is exactly the case that needs the
lever.

Rejecting the renames matters as much as accepting the additions. `objective.consumer` is
singular by design: a named consumer with a named decision is what stops a profile growing until
it demands everything, and `intendedConsumers` reopens that. The group should take the singular
as a position rather than absorb its reversal inside a rename.

## Consequences

Implemented in the worked example. What it took, and what reversing it would cost:

- Baseline profile v0.3 → **v0.4**: gains `scope` and `decisionOptions`. Both changes are
  classified editorial, because the baseline accepts all four lifecycle stages and so no document
  that conformed to v0.3 stops conforming.
- Migration profile v0.1 → **v0.2**: gains the same, and narrows the accepted stages to
  `implemented`, `configured` and `observed`. That narrowing is a **tightening** — an interface
  reporting `intended` conformed under v0.1 and does not now — and it is the first rule in either
  profile that discriminates on how the reported data was obtained rather than on what it says.
  The profile also re-pins its base from v0.3 to v0.4, since a pin names an exact version.
- `check_profile.py` gains the C1 extension and C11, and `validate_cbom.py` applies
  `scope.lifecycleStages` by narrowing the enum on the rule that constrains the stage, so an
  unaccepted stage fails that rule rather than through a parallel check. A stage the methodology
  defines but the profile excludes is reported distinctly from a value that is not a stage.
- `check_scope_narrows` rejects a derived profile that widens the accepted stages, or that
  changes the subject type, with the same profile-error exit code as a relaxing override.
- Three new fixtures — an unactionable decision, a missing scope, and a derived profile widening
  the stages — plus a `scope` and `decisionOptions` block added to every existing fixture so that
  each still fails exactly one requirement. The suite runs 83 tests and passes.
- Conformance gains C11, the C1 amendment, a table describing the three scope members, and tool
  requirements T8 and T9. Terms gains profile scope, subject type, accepted lifecycle stages and
  decision options. Method step 1 asks for the options and step 2 for the scope.

Reversing it means unwinding two profile versions and the tightening in the migration profile,
which is the expensive half: any document produced against v0.2 was produced under the narrower
stage set.

Open after this record: whether `scope` should also bound the interface types or domains a
profile applies to, which the submission raised as part of its tuple and which overlaps the
product-rule `interfaceType` constraints already available. Left out because the two mechanisms
would need reconciling first.

## Links

- Member submission on a mandatory structured preamble, August 2026.
- Conformance section, requirements C1, C2 and C8; `docs/methodology/check_profile.py`.
- Method section, steps 1 and 2, for the decision test and the subject vocabulary.
- Decision 0006, which established carrier acceptance ranges and is the precedent this follows.
- `review-2026-08-structured-preamble.md` for the field-by-field disposition.
