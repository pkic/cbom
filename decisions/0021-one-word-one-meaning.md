# 0021. A word means one thing: keyCoverage, and revision states

- **Status:** Proposed
- **Date:** 2026-09-15
- **Aspect:** 3.7 — Vocabularies & normalisation (with consequences for 3.11)
- **Topic / issue:** #3
- **Deciders:** not yet taken
- **Decision rule applied:** lazy consensus (pending)

## Context

Two words in this methodology were each doing two jobs.

**`coverage`** appeared twice in the same rules file meaning different things. As a product attribute
it says how complete a document's declared interface set is, with values `all-external`, `all` and
`partial`, and a producer writes it into a CBOM. As a field on a group rule it says which keys of a
vocabulary need an entry, with values `all-purposes` and `in-scope`, and a profile author writes it
into a profile. Both read as "how much is covered". Which one a reader was looking at depended on
position in the JSON.

The group enum also admitted `all`, which is a *product* coverage value and means nothing for keys.
That was the collision leaking across: a profile could have declared its key coverage using a value
from the other vocabulary and been evaluated without complaint.

**`lifecycle`** named both the capture phase of a reported fact, which is what `lifecycleStage` has
always meant, and the sequence of states a document passes through on the Governance page. The Roles
table said the producer records "provenance and lifecycle stage" twenty lines under a heading using
the other sense.

Neither collision produced a wrong answer from the tools. Both made a reader do work the writing
should have done, and the group one would have become a format break the moment a profile family
shipped.

## Options considered

- **Option A — leave them and disambiguate in prose.** Say which sense is meant wherever it comes up
  (trade-off: the fix has to be repeated forever and it does not reach the rules file, the schema, or
  the error messages, which is where the confusion actually lands).
- **Option B — rename the product attribute.** `coverage` becomes something like
  `interfaceSetCompleteness` (trade-off: producers write that attribute into documents, so every
  existing CBOM and every generator changes. It is the expensive side of the collision).
- **Option C — rename the group field and retire the overloaded heading.** `coverage` on a group rule
  becomes `keyCoverage`, and the Governance sequence becomes *revision states* with `lifecycle` left
  to mean the capture phase (trade-off: touches the schema, both tools, one example profile and three
  fixtures, and any profile already drafted against the group syntax).

## Decision

Proposed: Option C.

**`keyCoverage`.** A group rule's coverage over the keys of its vocabulary is `keyCoverage`, with
values `all-purposes` and `in-scope`. `all` is dropped from that enum, because it belonged to the
other sense. The product attribute keeps the name `coverage`.

**Revision states.** The Governance sequence is *revision states*: created, signed, published,
superseded. `lifecycle` means the capture phase of a fact and nothing else.

**The general rule, which is the part worth keeping.** Where one word would name two things in this
methodology, the one written into *documents* keeps the word and the one written into *profiles*
gives way. Producers outnumber profile authors by a wide margin, and a producer changing an attribute
name has to reissue documents, while a profile author changing a field name reissues one file.

## Rationale

The collision was cheap to fix and getting more expensive. Nothing had shipped, so `keyCoverage`
costs a rename in six files; after a family publishes, the same change breaks every profile derived
from it and every tool that reads one.

Dropping `all` from the group enum is what shows the collision was real rather than cosmetic. It had
been accepted as a synonym for `all-purposes` since decision 0014, so a profile could have mixed the
two vocabularies and been evaluated without complaint. Nobody wrote that, and nothing would have told
them.

The tie-break rule at the end is the reusable half. Both collisions here were found by accident, one
while writing an unrelated section and one while looking hard at a diagram. The rule does not help
find the next one, but it settles it in a minute once found, rather than reopening the argument about
which sense deserves the word. The Confidentiality section reached for the same rule independently,
reserving `variant` and `audience` as its normative terms and keeping "confidentiality" only as a
title, because `confidentialityLifetime` already means something else.

Option B was rejected on cost rather than on merit. `interfaceSetCompleteness` is arguably the better
name, and it is not worth what it costs to impose on producers.

## Consequences

- `keyCoverage` replaces `coverage` on group rules and on overrides that widen it, in the schema, in
  `validate_cbom` (`KEY_COVERAGE_STRENGTH`, `check_key_coverage_tightens`), in `check_profile`'s C13,
  in the migration profile, and in three fixtures. The suite passes unchanged, which is weaker
  evidence than it looks: a rename that broke the check would have failed the C13 and Q49 fixtures,
  and those do still fail for their stated reasons.
- The Governance sequence is renamed, and `Validate` is no longer drawn as one of its states. That
  was a separate defect found at the same time: validation happens to a published revision
  repeatedly, by parties who never coordinate, and leaves a claim rather than moving the document.
- Naming who may cause each transition exposed a power nobody had written down. A profile authority
  revising a published profile changes whether existing revisions conform, with no producer acting and
  no document changing. Q15 asks how long a supplier then has. Q61, new, asks whether anyone has to
  tell them.
- Terms gains an entry for key coverage that names both senses together, since a reader who has met
  one will meet the other.
- No document changes. No producer is affected.

## Links

- Decision 0005, which set the attribute naming conventions this extends from names to fields.
- Decisions 0010 and 0014, which introduced group coverage and the rule that it may be widened and
  never narrowed; both are amended to the new name.
- The Confidentiality section, which applies the same principle to `confidentiality` and settles on
  `variant` and `audience`.
