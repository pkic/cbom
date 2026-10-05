# 0023. Use cases are grouped by their relation to the baseline, and change planning shares a core

- **Status:** Proposed (draft; promotes to `decisions/` with the change-core rules file)
- **Date:** 2026-10-04
- **Aspect:** 3.9 — Building one profile on another (with consequences for 3.1 and 3.13)
- **Topic / issue:** #9
- **Deciders:** not yet taken
- **Decision rule applied:** lazy consensus (pending)

## Context

The use-case pages list nine purposes in one flat table, and two drafts (IoT, substation
automation) are adding more. The pages already argue that what matters is whether a profile
selects baseline facts or adds new ones, because that decides whether one document serves several
consumers. The list does not show it. Separately, Q64 blocks the IoT profile until the group says
what it extends. The substation draft needs the same answer, and a profile has a single base.

## Options considered

- **Option A — group by sector** (trade-off: how members arrive; breaks "use case = decision" and
  duplicates disclosure profiles per sector).
- **Option B — group by relation to the baseline, with subject as a second axis** (trade-off:
  predicts document reuse and profile structure; two groups is coarse).
- **Option C — group by product lifecycle or consumer role** (trade-off: easy to read; predicts
  nothing about profiles).

## Decision

Option B.

1. Use cases fall into **disclosure** (select and tighten baseline facts, orientation `inventory`)
   or **change planning** (add capability facts, orientation `both`). Entries that describe a way
   of applying any profile, the CI quality gate and the comparison of versions, are listed apart
   and are not use cases.
2. The subject (`scope.subjectType`: product, device model, system, and possibly estate) is shown
   for every use case. Sector is never a grouping; a sector adds vocabulary to a row.
3. Change-planning profiles extend a **change core**: the attributes the migration, IoT and
   substation drafts all ask for, plus the update-path facts IoT and substation share as
   conditional rules on update interfaces. This answers Q64 with its Option C.
4. The core is published beside pqc-migration v0.7 as a sibling, declaring each shared rule under
   the id pqc-migration already uses. No rule id moves. `tests/check-family.py` checks the
   relation. Re-parenting is left to the same choice as Q51.
5. Catalogue numbers are identifiers and do not change when an entry moves. Entries 10 to 16 are
   added as placeholders: a named consumer and decision, nothing more.

## Rationale

The relation to the baseline is what a buyer has to know before asking for a CBOM, and it is
already enforced by the composition rules, so the grouping costs no new mechanism. A shared core
is the only way two branches can share a fact under single inheritance without each defining it.
Publishing it as a sibling repeats the technique the entry profile used with the baseline, so the
reviewed migration profile is not revised. The eight use cases in the telecom paper all fall into a
cell without a new group, which is the test that the grouping is not shaped around the two drafts.

## Consequences

- `docs/use-cases/index.html` and `docs/methodology/use-cases.html` are grouped. The CI gate moves
  to "Applying a profile". A second emphasis table compares change-planning purposes across the
  core.
- `docs/methodology/maturity.html` names the overlay as a fourth relation.
- New open questions: Q66 (is the core target-neutral), Q67 (is an estate a subject type), Q68
  (how an overlay's verdict relates to the documents it cites).
- The substation draft's decisions become 0024, and its component profile extends the core.
- Follow-on work: write `profile-change-core.rules.json` and extend `check-family.py` to cover it.

## Amendment, 4 October 2026: two further groups

The two groups above are defined by what a profile asks for. Two more are defined by who produces
the document and who relies on it. Both are proposed with this record and can be accepted or
rejected separately from the first two.

- **Operation.** The producer is the operator of a system, not the supplier of a product. The
  subject is a deployed system, a service or an estate, mostly at lifecycle stages `configured` and
  `observed`. The upper bound on what may be asked moves, because the black-box constraint does not
  apply: an operator can state the data an interface carries, its confidentiality lifetime, what
  was negotiated, and what changed since the last report. An operator document cites supplier
  documents rather than repeating them, so it is an overlay. A profile in this group may extend the
  baseline or the change core. Members: managed and cloud service disclosure and stored data
  (moved from disclosure and change planning), harvest-now-decrypt-later exposure, migration
  progress over time, and the operator's migration register. Owns Q36, Q37, Q45, Q67 and Q68.
- **Assurance.** The reader is an auditor, assessor or regulator who relies on the document as
  evidence. The cryptographic facts are usually the disclosure facts; what is added is provenance,
  freshness and integrity. Members: regulatory and compliance reporting (moved from disclosure),
  certification and validation evidence, and readiness assessment evidence. Owns Q14, Q29, Q60 and
  Q44, and Discussions #18 and #37. This group may turn out to be requirements on the conformance
  claim rather than a kind of profile; its first worked example decides.

**Revival condition for merging Assurance back into Disclosure:** the first assurance profile adds
no rule that a disclosure profile with a stricter claim could not carry.
