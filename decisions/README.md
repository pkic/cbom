# Decision records

This directory is the durable record of **what the Working Group decided and why**. Each file
captures one decision; the discussion behind it lives in the linked issue.

## How to add one

1. A topic reaches the **Decided** state (see [`../CONTRIBUTING.md`](../CONTRIBUTING.md)).
2. Copy [`0000-template.md`](./0000-template.md) to `NNNN-short-title.md`, using the next
   sequential, zero-padded number.
3. Fill it in, commit it, and link it from the issue.
4. A decision is never deleted. If it is reversed, add a new record and set the old one's
   status to `Superseded by NNNN`.

## Records drafted ahead of a decision

Records 0001 to 0007 were written from choices taken while building the worked example in
`docs/methodology/`. They are marked **Proposed** rather than Accepted: each one is already
implemented in the example artifacts, so the group is being asked to ratify or reverse a
position that exists in the drafting, not to decide in the abstract. Reversing one means
changing the example, and the Consequences section of each record says what that would involve.

Records 0008 and 0009 were written the same way and are implemented alongside the others. They
differ in one respect worth noting on an agenda: 0001 to 0007 describe the example as it was
first built, whereas 0008 and 0009 changed it. Reversing 0008 means undoing a tightening that
documents may already have been produced against; reversing 0009 costs less, because its
constraint falls on profiles rather than on documents.

0009 also reverses a clause of 0008, which is the first time one record has revised another.
Neither is superseded: 0008 is annotated at the clause concerned and otherwise stands.

Record 0010 is now implemented alongside 0008 and 0009. It is the largest of the three: it
introduces a rule shape the validator did not have, and it tightens the migration profile, so a
document conforming to the previous version does not conform to this one. It also leaves two
points open rather than deciding them — whether `randomness` is a purpose, and how a sector
profile widens the vocabulary — so it can be accepted in part.

## Index

| # | Title | Aspect | Status | Date |
|---|---|---|---|---|
| [0001](./0001-product-independent-profile-rules.md) | Profile rules are product- and instance-independent | 3.1 | Proposed | 2026-08-07 |
| [0002](./0002-facts-in-cbom-judgements-in-policy.md) | A CBOM records facts; judgements are made by external policy | 3.3 | Proposed | 2026-08-07 |
| [0003](./0003-three-state-disclosure-model.md) | Absence is distinguished from withholding | 3.4 | Proposed | 2026-08-07 |
| [0004](./0004-monotonic-profile-extension.md) | A derived profile may add and tighten, never relax | 3.9 | Proposed | 2026-08-07 |
| [0005](./0005-attribute-naming-conventions.md) | Attribute names state what is disclosed, not what it implies | 3.7 | Proposed | 2026-08-07 |
| [0006](./0006-carrier-acceptance-range.md) | A profile declares the carrier versions it accepts | 3.2 | Proposed | 2026-08-07 |
| [0007](./0007-availability-as-status-and-blocker.md) | Forward-looking capability is stated as a status and a blocker, not a date | 3.10 | Proposed | 2026-08-07 |
| [0008](./0008-profile-scope-declaration.md) | A profile declares its subject, its boundary, and the lifecycle stages it accepts | 3.1 | Proposed | 2026-08-21 |
| [0009](./0009-orientation-is-declared-and-checked.md) | A profile declares its orientation, and the declaration constrains its rules | 3.1 | Proposed | 2026-08-21 |
| [0010](./0010-cryptographic-purpose-vocabulary.md) | Capability is stated per cryptographic purpose, from a fixed vocabulary | 3.10 | Proposed | 2026-08-21 |
| [0011](./0011-rule-numbering-across-a-family.md) | A rule id is local to its profile and is cited against a profile tag | 3.2 | Proposed | 2026-08-24 |
| [0012](./0012-what-a-disclosure-baseline-requires.md) | A disclosure baseline identifies its subject, states its completeness, and names its identifier schemes | 3.1 | Proposed | 2026-08-21 |
| [0013](./0013-monotonicity-covers-constraints.md) | Monotonicity is checked for constraints, and a rule that cannot fail is not a rule | 3.9 | Proposed | 2026-08-24 |
| [0014](./0014-tightening-an-inherited-group.md) | A derived profile may tighten one member of an inherited group, and widen its coverage | 3.9 | Proposed | 2026-08-24 |
| [0015](./0015-a-conformance-claim-is-checkable.md) | A conformance claim is bound to a document, lists each profile separately, and can be re-checked | 3.5 | Proposed | 2026-08-24 |
| [0016](./0016-what-an-spdx-only-claim-asserts.md) | Product-level rules are not evaluable from SPDX alone, and a claim says so | 3.6 | Proposed | 2026-08-24 |
| [0017](./0017-published-schemas.md) | The rules file and the claim have published schemas, and a schema is not a conformance checker | 3.13 | Proposed | 2026-08-24 |
| [0018](./0018-the-demonstration-is-checked-against-the-tool.md) | The demonstration loads the published rules and is checked against the reference tool | 3.13 | Proposed | 2026-09-12 |
| [0019](./0019-a-family-ordered-by-depth.md) | Adoption is staged by a family of profiles ordered by depth, not by a maturity field | 3.9 | Proposed | 2026-09-12 |
| [0020](./0020-cbom-joined-to-vulnerability-statements.md) | A CBOM is joined to vulnerability statements, not merged with them | 3.3 | Proposed | 2026-09-12 |
| [0021](./0021-one-word-one-meaning.md) | A word means one thing: keyCoverage, and revision states | 3.7 | Proposed | 2026-09-15 |

<!-- Add a row per decision, newest at the bottom:
| 0008 | Attribute model is a standalone cited artifact | 3.3 | Accepted | 2026-__-__ |
-->

## Why every record says Proposed

All twenty-one carry the status **Proposed**, and for an alpha that is the correct status rather than
a backlog.

These records are written while building the methodology and its worked example, so that the
reasoning behind a choice survives the choice. Writing one is not a request for a decision; it is a
way of making a choice arguable later, by whoever inherits it. A record says what was rejected and
why, which is the half that is normally lost.

Adoption comes per aspect, as each one stops moving, and it is not close for most of them: of the 64
items in the open-questions register, 52 are still open and eight are settled by a record here and
waiting on the group, and every aspect is unassigned. The last two records each opened four items
rather than closing any, which is the normal shape of a decision that draws a boundary: 0019 settles
what shape staged adoption takes and leaves where a family is recorded to the group, and 0020 settles
that a CBOM is joined to vulnerability statements rather than merged with them, leaving the
withholdability that blocks the use case depending on it (Q57) open. What *ready* means — no open question
that would change a rule, the suite covering it, no open defect in the tools touching it, and an
owner — and how a batch runs once an aspect is ready, is set out in
[adoption-and-readiness.md](./adoption-and-readiness.md). Nothing is currently open for adoption.
