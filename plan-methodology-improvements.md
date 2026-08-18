# Plan: addressing the methodology review findings

Working note for the PKIC CBOM Profiles Working Group.
Written 7 August 2026, against the state of `docs/methodology/` at that date.

## Purpose

Fifteen sections of methodology documentation are published. A review of the whole found
that the individual sections hold up and the weaknesses sit at the seams between them. This
note turns those findings into sequenced work, identifies what the working group has to decide
rather than what can simply be drafted, and proposes how to reconcile the backlog with the
review cadence already announced to members.

## Two principles for sequencing

**Fix the seams before adding sections.** Two of the findings, terminology and profile
composition, will generate review comments on every section a member reads until they are
resolved. Producing more content first means collecting the same objection repeatedly.

**Keep the review batches clean.** Members have been asked to review Challenges, Inventory and
Lifecycle Data by 14 August. None of those three contains the terminology clash, so that batch
can proceed untouched. The clash lives in Profile and PQC Migration, which gives a window to
fix it before those sections reach anyone.

---

## Workstream 1 — The method itself

**Finding.** The deliverable is a methodology for defining profiles, and no section states the
procedure. The sequence exists only as a closing banner on the PQC Migration section.

**Work.** Promote it to a section of its own, placed immediately after Policy Evaluation and
before Use Cases, setting out the steps: identify the consumer and the decision; derive the
questions that decision raises; convert each question into an attribute declarable at the
subject's boundary; assign conformance levels; state what is deliberately excluded and why;
define the format mapping; record the decisions and their revival triggers. PQC Migration then
becomes the worked illustration of that procedure and should reference it explicitly.

**Size.** Medium. New writing, but the material is already distributed across existing sections.

**Depends on.** Nothing. Can start immediately.

**Decision needed.** Whether the working group accepts this as *the* procedure. It is currently
my inference from how we built the example, not an agreed position.

---

## Workstream 2 — Terminology reconciliation

**Finding.** The baseline profile uses `keyExchange`, `encryption`, `authentication`. The PQC
Migration profile uses `keyExchangeCurrent` and `keyExchangeSupported`. One concept, two names,
depending on the section.

**Work.** Settle a convention and apply it everywhere. The proposal: a bare attribute name
denotes present state, and a `*Supported` suffix denotes declared capability. Under that rule
the baseline is unchanged and PQC Migration drops the `Current` suffix. Sweep all fifteen
sections, the rules file, the validator, the two example CBOMs and the mapping document.

**Size.** Small to medium. Mostly mechanical once the convention is agreed, but it touches the
executable artifacts, so the validator and demo need re-running afterwards.

**Depends on.** A decision on the convention.

**Urgency.** Before Profile and PQC Migration enter a review batch.

---

## Workstream 3 — Profile composition

**Finding.** The site asserts twice that one CBOM may satisfy several profiles, and PQC
Migration says it "builds on" the baseline, without defining what either means.

**Work.** Specify how profiles relate. At minimum: whether a profile may extend another, whether
an extending profile may raise a level (SHOULD to MUST) or only add attributes, whether it may
relax anything, and how a conformance claim names a composed set. Add it to the Profile section
and reflect it in the rules-file schema with a `extends` key.

**Size.** Medium, and more design than drafting.

**Depends on.** Nothing, though it interacts with Workstream 4.

**Decision needed.** The composition semantics are a genuine methodology choice with more than
one defensible answer.

---

## Workstream 4 — Make the PQC Migration profile executable

**Finding.** The baseline profile has a rules file, example CBOMs, a validator and a demo. The
PQC Migration profile has prose, so a reader cannot tell whether it is a specification or a
sketch.

**Work.** Produce `profile-pqc-migration.rules.json`, extend the validator to handle conditional
rules and list-valued attributes, and add an example CBOM covering at least three interfaces
with differing capability status and blockers. If the working group prefers, the alternative is
to label the section a design study and leave it in prose.

**Size.** Medium to large. The conditional rules and list attributes are new validator
capability, not configuration.

**Depends on.** Workstreams 2 and 3.

**Value beyond the deliverable.** Implementing it will test the design. Conditional rules and
list-valued attributes are the parts most likely to have problems that prose conceals.

---

## Workstream 5 — An SPDX artifact

**Finding.** Format-independence is the central claim, and every artifact is CycloneDX. The
SPDX column of the mapping is untested.

**Work.** Produce a minimal SPDX document for the same nginx subject, with the CBOM referenced
as an external artifact and the profile attributes carried as annotations, then extend the
validator with an SPDX adapter so the same rules evaluate both. Even a partial adapter would
substantiate the claim.

**Size.** Medium, with an important caveat.

**Caveat.** I do not have verified knowledge of SPDX 3.0.1 structures at field level. This
workstream needs either a member who works with SPDX or time budgeted for reading the
specification properly. Producing a plausible-looking SPDX document from memory would be worse
than having none.

---

## Workstream 6 — Standards hygiene

**Finding.** No terms section and no conformance clause.

**Work.** Two additions. A terms section collecting the vocabulary now defined in place:
relationship, endpoint, asset, `interfaceType`, `lifecycleStage`, the disclosure states,
`capabilityStatus`, `blockedBy`, `coverage`. And a conformance clause stating what conformance
means, who may claim it, how a claim is expressed, and what the three disclosure states do to a
verdict. Both draw on existing text and mostly consolidate it.

**Size.** Small.

**Depends on.** Workstream 2, since a glossary written before the naming is settled will need
rewriting.

---

## Workstream 7 — Practise the versioning discipline

**Finding.** The example profile moved from v0.1 to v0.2 with no record, while the Versioning
section argues for pinned versions and dated grace windows.

**Work.** Add a changelog to the profile specification covering the v0.2 changes, which were the
three-state disclosure model and the `withholdable` flag on I9. Move the "Recorded decisions"
block out of the PQC Migration section and into the repository's `/decisions` folder, which
Governance cites and nothing currently uses. Adopt the existing decision-record template.

**Size.** Small.

---

## Workstream 8 — Consolidate the open questions

**Finding.** Unresolved items are scattered: five in PQC Migration, a limitation in Model, gaps
in Challenges, plus the deferred attributed-edge model and the group-relationship case.

**Work.** Collect them into one register and map each to the thirteen methodology aspects the
Issues page already tracks, so the working group can set an agenda from a single list. Where an
item has no matching aspect, that is itself worth knowing.

**Size.** Small, but needs someone familiar with how the thirteen aspects are currently framed.

---

## Workstream 9 — Presentation and access

Four smaller items, independent of each other and of everything above.

- **Reading paths.** Fifteen tabs with no suggested route. Three short paths on the Overview for
  a vendor, an operator and a regulator. Small.
- **Demo coverage.** The version bands and the three disclosure states work but are visible only
  on the command line. Showing a 1.6 CBOM accepted with a warning would make the versioning
  argument concrete. Small.
- **Diagram accessibility.** The inline SVGs carry no `role="img"` or accessible title. For a
  public standards site this should be fixed. Small but touches every section.
- **Visual verification.** Nothing has been rendered. The wide tables, the four-panel governance
  diagram and the header at narrow widths all need a browser and a person. Small, but it needs
  someone other than me.

---

## Workstream 10 — A second worked subject

**Finding.** Sector-independence is claimed and demonstrated on one subject.

**Work.** A second short example from a different domain, reusing the same profile to show it
applies unchanged. The retired N32 telecommunications example could be revived in compressed
form.

**Size.** Large.

**Recommendation.** Defer. It is the most expensive item and the least urgent, and it will be
more convincing once composition and the method section exist.

---

## Sequencing

**Now, before the 14 August review closes.** Workstream 1 drafted for comment. Workstream 7,
which is cheap and unblocking. The Workstream 9 items that touch no section under review.

**Next, before Profile and PQC Migration enter a review batch.** Workstreams 2 and 3, in that
order, then Workstream 6. This is the critical path, because everything downstream inherits the
naming and composition decisions.

**Following.** Workstream 4, then Workstream 5 if a member with SPDX knowledge is available.
Workstream 8 alongside, since it is independent.

**Deferred.** Workstream 10, revisited once the method section has settled.

## The August target needs scoping

The cadence announced to members is three sections every two weeks, with an initial methodology
document in August. Fifteen sections at that rate is roughly ten weeks, so both statements
cannot hold as written and it is better to resolve that now than in September.

Two options.

**Scope the initial release to the conceptual core.** Overview, Challenges, Inventory, Lifecycle
Data, Model, Profile, Policy Evaluation and the new method section, published as a numbered
draft, with the applied and operational sections following in a second release. This produces
something coherent in August and keeps the cadence honest.

**Or release everything as a draft at once**, clearly marked, and run the review cadence against
an already-published document rather than gating publication on it.

I would take the first. It gives members a document with a beginning and an end, and it lets the
applied sections benefit from the terminology and composition decisions before they are frozen.

## Decisions the working group needs to take

Drafting is blocked on some of these, so they are worth taking early.

1. Whether the procedure in Workstream 1 is accepted as the methodology's method.
2. The attribute naming convention (Workstream 2).
3. Profile composition semantics (Workstream 3).
4. Whether the PQC Migration profile is normative or an illustrative design study.
5. Whether a CBOM should carry forward-looking data at all, and whether the answer may differ
   between profiles.
6. The scope of the August release.
7. Whether the `specs` category added to the reference register stays. It was added to hold the
   protocol and algorithm specifications the worked example cites, and was my decision rather
   than the group's.

## Risks

**The naming and composition decisions arrive late.** Everything downstream depends on them, and
they are the two items most likely to attract discussion. Taking them at the next meeting, ahead
of further drafting, is the main scheduling lever available.

**SPDX work proceeds on assumption.** Covered under Workstream 5. The failure mode is a
convincing but wrong artifact, which would be worse than the current honest gap.

**Review capacity.** Three sections per fortnight assumes members read them. If the first batch
returns little, the cadence is the thing to change, not the scope of each batch.
