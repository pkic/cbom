# 0019. Adoption is staged by a family of profiles ordered by depth, not by a maturity field

- **Status:** Proposed
- **Date:** 2026-09-12
- **Aspect:** 3.9 — Building one profile on another (with consequences for 3.1 and 3.5)
- **Topic / issue:** #9
- **Deciders:** not yet taken; opens Q50 to Q53
- **Decision rule applied:** lazy consensus (pending)

## Context

A profile states one bar and a document either clears it or does not. That is correct for a
conformance decision and wrong for adoption. The shallowest thing this methodology offered to
conform to was the Interface Disclosure Baseline, which requires nine facts about every declared
interface — the algorithms for each cryptographic job and the implementing library among them — and
four about the product, including a management interface or a stated reason for its absence. A
producer that can enumerate its interfaces this quarter, and cannot
attribute algorithms to them until it has instrumented its build, conformed to nothing at all and
had no verdict to show for the work it had done. A buyer asking for "a CBOM" got either a
conforming document or silence, with nothing in between and no way to ask for a first step.

The request that prompted this was for a baseline a supplier could reach quickly and extend later.
The question is what shape that takes: a new declaration inside a profile, or a way of publishing
profiles.

Two things in the methodology already bear on it. Monotonic extension guarantees that conformance
to a derived profile carries conformance to its base (decision 0004), which is exactly the
implication a staged family needs. And the migration profile already stages a problem at a finer
grain: it takes three cryptographic purposes in depth while requiring a status for all seven, so a
supplier cannot conform while behaving as though entity authentication does not exist
(decision 0010). That is the same idea one level down.

## Options considered

- **Option A — a maturity field in the profile.** A profile declares `maturityLevel: 2`, and a
  document's claim carries the level (trade-off: it invents a second ranking alongside the rules
  and nothing ties the two together, so two profiles could both claim level 2 and require
  different things. It also has to be maintained by hand as a family grows).
- **Option B — obligation levels as the ladder.** Publish one profile and stage adoption by moving
  rules from SHOULD to MUST over time (trade-off: a SHOULD does not decide a verdict, so the early
  adopter gets no verdict for satisfying it, and every promotion changes the verdict on documents
  already published without changing the documents).
- **Option C — a family of profiles ordered by depth**, each extending or containing the one below
  it, with the entry profile set where a producer starting today can reach it (trade-off: more
  artifacts to publish and govern, and the family's shape is not visible from any single one of
  them).
- **Option D — leave adoption to the consumer.** Let each buyer write its own reduced profile
  (trade-off: the reduced profiles would not agree, which loses the one property that makes a
  disclosure comparable across suppliers).

## Decision

Option C. A depth is a profile; there is no new field, no new artifact type and no new verdict.
A family is a set of profiles ordered so that each contains the one below it, and "maturity" names
the decision to publish the family with its entry depth low enough to be reachable.

The entry profile of the interface family is published as
`profile-interface-enumeration.rules.json` v0.1. It requires the subject's identity, at least one
interface, a completeness statement, and for every interface a protocol, a version, a type and a
lifecycle stage. It requires nothing about algorithms, endpoint roles or the implementing library,
which is what the disclosure baseline adds at the next depth. Each shared rule is declared under
the id the baseline uses for the same rule, so the gaps in the numbering are where the next depth
adds.

Three positions follow.

**The word "maturity" is not used normatively.** In this documentation a maturity level is a
judgement derived from disclosed facts by external versioned policy, deliberately not a CBOM
attribute (decision 0002), and the PQC Maturity Model is an instance of exactly that. A profile is
what such a judgement reads. The normative term for a family's ordering is **depth**; `level`,
`stage`, `band` and `tier` are all already in use for other things.

**Depth and branch are different relations.** A deeper profile serves the same consumer decision
with the same orientation and asks for more. A branch changes the decision — the migration profile
declares orientation `both` and plans a migration rather than maintaining an inventory — and is not
a rung. Ranking suppliers along a family that mixes the two compares answers to different
questions.

**The family is not declared inside its profiles.** A profile cannot name the profiles deeper than
it: they do not exist when it is published, and requiring it to name them would invert the
direction of extension and force a re-release of the entry profile every time the family grew. The
family belongs to the register described in Governance, which is Q50.

## Rationale

Option C adds no mechanism, which is the main argument for it. Everything it needs — monotonicity,
local rule ids, scope and carrier narrowing, tightening in place — was already decided and is
already checked, and the one genuinely new thing is a judgement about where to set the entry depth.

Option A fails on the same ground the methodology already rejected `pqcPosture`: it records a
ranking rather than the facts a ranking is computed from, and nothing makes the ranking agree with
the rules. Two profiles at "level 2" requiring different things is not a hypothetical failure; it
is what happens the first time two sector bodies both number their families.

Option B is worse than doing nothing. Its early adopter satisfies SHOULD rules and receives the
same verdict as one who ignored them, so the ladder is invisible at exactly the moment it is meant
to be encouraging, and each promotion breaks documents already published.

The objection to Option C is that suppliers will stop at the entry depth. That is real and it is
not the artifact's problem to solve: a profile states a bar and which bar to require is the
consumer's decision. What a family changes is that the ask becomes expressible — a buyer names the
profile and version it requires and a date by which the deeper one is required — and that
"conforms" stops being ambiguous about which bar was cleared, because a claim names the profile.

The entry depth is set above untargeted scanner output and below the disclosure bar. Both ends are
demonstrated by documents in the repository rather than asserted: `cbom-fail`, named for the verdict
the baseline gives it, conforms to the entry profile; `cbom-entry-fail`, which is roughly what a
scanner emits with no profile in mind, conforms to neither.

## Consequences

- A new published artifact and a new example document, both covered by the suite. The entry profile
  passes C1 to C17 including `--strict`.
- The baseline does **not** declare `extends` on the entry profile, so the ladder is currently an
  assertion about two sibling profiles rather than a structural fact. `tests/check-family.py`
  checks it: rules only added, shared rules identical, shared vocabularies and identifier schemes
  identical, the disclosure convention identical, scope and carrier range not widened, orientation
  unchanged, and conformance carrying downwards over every committed document. Re-parenting is
  Q51; it would retire most of that file and move seven rule ids to another profile tag.
- `exclusions` now carries two kinds of statement — permanent exclusion and deferral to a greater
  depth — and distinguishes them only in prose. Q52.
- Whether depths are numbered, and whether a consortium profile may be published as an entry depth
  at all, interacts with who may publish under a PKI Consortium name (Q03). Q53.
- A consumer's requirement should now name a profile and version rather than "a CBOM". This is a
  change to what the methodology tells a buyer to write, and it interacts with the grace-window
  question in Q15.
- Reversing this means withdrawing the entry profile. Documents authored against it would be left
  claiming conformance to a withdrawn profile, which is the archival obligation in Q41, and the
  producers who reached it would be back to conforming to nothing.

## Links

- Opens Q50 to Q53 in [`../open-questions.md`](../open-questions.md).
- Implemented in `docs/methodology/maturity.html`,
  `docs/methodology/profile-interface-enumeration.rules.json`,
  `docs/methodology/cbom-entry-fail.cyclonedx.json`, `tests/check-family.py` and
  `tests/run-profile-tests.sh`.
- Related: [0004](./0004-monotonic-profile-extension.md), which supplies the implication a family
  rests on; [0002](./0002-facts-in-cbom-judgements-in-policy.md), which is why a maturity rating is
  not an attribute and therefore why the word is not reused here;
  [0010](./0010-cryptographic-purpose-vocabulary.md), which stages a problem inside one profile and
  states the anti-floor argument this generalises;
  [0011](./0011-rule-numbering-across-a-family.md), which makes a shared rule id legible at two
  depths; [0014](./0014-tightening-an-inherited-group.md), on sharpening an inherited group in place.
