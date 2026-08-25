# 0017. The rules file and the claim have published schemas, and a schema is not a conformance checker

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.13 — Templates, worked examples & tooling (with consequences for 3.5)
- **Topic / issue:** #13
- **Deciders:** not yet taken
- **Decision rule applied:** lazy consensus (pending)

## Context

A profile is a JSON file whose shape was described only by two examples and by whatever
`check_profile.py` happened to reject. Anyone writing a third profile had to infer the format, and
anyone writing a tool that consumes profiles had to reimplement our validator's assumptions.

The same is now true of the claim format, which is worse: a claim crosses an organisational
boundary, so the party reading it is the least likely to have our tooling.

## Decision

Proposed: publish `profile.schema.json` and `claim.schema.json`, and state plainly what they are
not.

**A schema says what shape a file has. It does not say whether a profile is well-formed under this
methodology.** That is C1 to C17. A schema can see that `objective` is an object with a `decision`
string; it cannot see whether the decision is one a consumer could act on, whether the rules trace
to it, or whether an attribute name asserts a conclusion. Both checks are worth having and neither
substitutes for the other, so both run in the suite.

Two places where the schema does carry real meaning rather than shape:

- **`constraint` sets `additionalProperties: false`.** A constraint key the evaluator does not
  implement produces a rule that reports `ok` against every value — decision 0013's silent success.
  Encoding the closed set structurally means a third party validating a profile catches it without
  our checker.
- **The claim schema encodes two consistency rules.** A refused entry carries no rule results and
  asserts `assessed: false`; an entry claiming conformance may not also list a failed MUST. Both are
  internal contradictions a schema can catch, and the first is T1 written where a machine can read
  it.

`jsonschema` is not a dependency of the methodology. `tests/check-schemas.py` skips itself with a
message when it is absent, so a contributor without it can still run the rest of the suite; CI
installs it.

## Rationale

The temptation with a schema is to make it the checker, because it is the artifact other people can
run. Resisting that is the point of this record. Almost everything that makes a profile good under
this methodology — a decision a consumer could act on, rules that trace to it, names that disclose
rather than conclude, a rule that can actually fail — is invisible to a structural schema. A group
that published only a schema would be publishing the least important half and implying it was the
whole.

What the schema is genuinely good at is the part a third party needs: the shape, and the closed sets
where a typo would otherwise pass silently.

## Consequences

- Two schemas published under `docs/methodology/`, drafted against draft-07 for the widest tool
  support.
- `tests/check-schemas.py` validates both example profiles, the third-level fixture and the example
  claim, and asserts that the schema **rejects** the unimplemented-constraint fixture — a schema
  that cannot reject is the same defect as a rule that cannot fail.
- CI installs `jsonschema`.
- The `$comment` fields in both schemas carry the reasoning rather than pointing elsewhere, since a
  schema is often read alone.

## Links

- Decisions 0013 (the closed constraint set, and C17), 0015 (the claim format), 0016 (the carrier
  bound the claim schema documents).
- Conformance requirements C1 to C17, which are what the schemas are explicitly not.
