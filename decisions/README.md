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
| [0011](./0011-rule-numbering-across-a-family.md) | A derived profile numbers its rules in its own space, and retired ids are not reused | 3.2 | Proposed | 2026-08-21 |
| [0012](./0012-what-a-disclosure-baseline-requires.md) | A disclosure baseline identifies its subject, states its completeness, and names its identifier schemes | 3.1 | Proposed | 2026-08-21 |

<!-- Add a row per decision, newest at the bottom:
| 0008 | Attribute model is a standalone cited artifact | 3.3 | Accepted | 2026-__-__ |
-->
