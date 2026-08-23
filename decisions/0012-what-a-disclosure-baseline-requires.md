# 0012. A disclosure baseline identifies its subject, states its completeness, and names its identifier schemes

- **Status:** Proposed
- **Date:** 2026-08-21
- **Aspect:** 3.1 — Profile objective & scope (with consequences for 3.3 and 3.7)
- **Topic / issue:** #4, and #1 for the attribute half
- **Deciders:** not yet taken; settles Q34, and settles Q38 for this profile
- **Decision rule applied:** lazy consensus (pending)

<!--
Implemented in the worked example, like 0008 to 0011. The baseline moves to v0.6 and the migration
profile to v0.5.
-->

## Context

The Interface Disclosure Baseline was reviewed against the methodology's own tests rather than
read as a list. Four things came out of it, and the first explains why the others were hard to see.

**The objective was circular.** The decision was *"whether the cryptography the product applies at
its boundaries … is disclosed in enough detail to be recorded in a cryptographic inventory and
assessed against policy."* That is a decision about the document, not about the product. It
satisfies C1 in letter, and it generates no questions: Method step 3 says derive the questions from
the decision, and a decision whose answer is "whatever this profile requires" cannot be used to
argue that any particular attribute belongs. Every subsequent question — is `endpointRoles`
pulling its weight, should `implementationPurl` be withholdable — had no ground to be settled on.

**Nothing required the document to say what it described.** The worked example carries
`purl: pkg:generic/nginx@1.27.0` on `metadata.component` and no rule asked for it. A conforming
document could describe "nginx" with no version, which cannot be matched to a deployment, compared
with the same product's record from last quarter, or joined to an SBOM.

**Nothing required a completeness statement.** P1 and P2 constrain which *kinds* of interface must
appear; nothing said whether the declared set was the whole set. The Conformance section already
names "that the document is complete" and "that every relevant interface was declared" as the two
non-assertions most likely to cause difficulty in procurement, and offers a remedy — a product rule
strong enough to catch the omission — that the baseline did not implement. The migration profile
had the rule. Q34 asked whether it should move down.

**The identifier constraints were the wrong way round.** I9 required a `pkg:` Package URL for the
implementing library. I1 and I3 to I5 required only that a value be present, so `protocol: "our
secure channel"` and `keyExchange: "elliptic curve"` conformed. The profile constrained the form of
the least contested identifier and left the most contested free — and Challenges item 3, Q20 and
Q21 all identify those as the hard cases. An inventory assembled from twelve suppliers cannot
correlate on free text, which is the decision the profile exists to serve.

A fifth item is a defect of a different kind. **P2 could not be satisfied honestly by a subject
that has no management interface.** A library, a hardware token or an embedded component with no
configuration surface hides nothing by having none, and failed.

## Options considered

- **Option A — leave the baseline and fix the derived profiles.** Sector and procurement profiles
  add what they need (trade-off: every sector adds the same three rules under different names,
  which is the fragmentation the methodology exists to prevent, and a baseline-conforming document
  remains unusable as an inventory record).
- **Option B — settle Q20 first**, then constrain the algorithm identifiers properly (trade-off:
  Q20 is a genuine argument about registries and will not be settled quickly; meanwhile the
  baseline keeps accepting free text).
- **Option C — fix the objective, add the two missing product rules, revise P2, and require the
  profile to *name* the identifier scheme per asset class without settling which registry wins.**

## Decision

Proposed: Option C. Baseline v0.5 → **v0.6**.

**The objective becomes the consumer's actual job:**

> When a weakness is published against an algorithm, a protocol version, or a library, which of the
> deployed interfaces are affected — and, holding this record beside the one from last quarter,
> what has changed.

Every rule now derives from it. I1 to I5 and I9 are the matchable facts. I8 says how far to trust
them. I7 and P2 say which interfaces must be present at all. P3 and P4 are what make the document a
record rather than only a description.

**P3 (new, MUST).** The document identifies its subject in the form the profile names.

**P4 (new, MUST).** The product states how complete its declared interface set is. Moved down from
the migration profile, which now inherits it. This settles Q34.

**P2 (revised).** Satisfied by declaring a management interface, or by stating why there is none,
from a small vocabulary — `no-configuration-surface`, `configured-out-of-band`,
`not-applicable-to-subject`. Silence satisfies neither. This is the disclosure model applied to
structure rather than to an attribute, and it is the only relaxing change in this profile's
history.

**`identifierSchemes` (new).** The profile names the required form per asset class: `purl` for the
subject and for the implementing library, a named registry for algorithms and protocols. **C14**
checks that the declaration and the rules agree in both directions. It does not check that a value
belongs to a registry — the checker does not hold the registry and would be guessing — which is
stated rather than glossed. Q20 remains open; what is settled is that a profile says which naming
it means.

**Not changed, and deliberately.** I8 stays: it is the rule that tells a consumer how far to trust
every other value. I6's `minCount: 2` bakes in the two-party assumption, which is Q08 and is
recorded rather than accidental. I9 stays withholdable: a supplier who cannot disclose would
otherwise not participate at all. But the objective now carries a note saying that a conforming
document exercising that permission answers the second half of the decision and not the first,
because library-level matching is the use the profile is built for. A procurement profile should
tighten it, as the migration profile does.

## Rationale

The circular objective is the finding that matters most, because it is what allowed the other three
to persist. A profile whose decision refers to its own output cannot be argued with: any proposed
attribute is as justified as any other, and any omission is as defensible. Naming the consumer's
real job makes the rule set falsifiable — and the three gaps above are what fell out of the first
honest attempt to falsify it.

Requiring the *scheme* rather than settling the *registry* is the compromise that lets this land
now. Q38 already framed it: identity cannot be solved in general because some asset classes have no
agreed identifier, but it can be solved per profile. A consumer who knows they are reading CycloneDX
registry names can correlate; one who does not know which naming they hold cannot, whichever
registry eventually wins.

P2's relaxation deserves its own defence, since relaxations are otherwise forbidden in this
methodology. The rule exists to catch omission, and a document that omits its management interface
still fails. What changed is that a subject which genuinely has none can now say so, rather than
being non-conforming for a fact about its own design. A rule that cannot be satisfied honestly by a
legitimate subject is not strict; it is wrong, and it teaches producers that conformance is a
formality to be worked around.

## Consequences

- Baseline v0.5 → v0.6: two new MUST product rules and one revised, so this is a **tightening** and
  a document conforming to v0.5 does not necessarily conform to v0.6.
- Migration profile v0.4 → v0.5: re-pins the base, and drops its own coverage rule, which it now
  inherits. Its remaining product rule is renumbered under decision 0011, because the baseline
  needed the P-space back — the collision is a hard `ProfileError`, not a tidiness question.
- `validate_cbom` gains two constraint kinds: `subjectIdentified`, and `orDeclaredAbsent` on a
  structural rule. `check_profile` gains C14.
- All four example documents gain the product-level facts. The failing baseline example declares
  `coverage: partial`, which is the honest answer for it and still fails P2 — a partial list does
  not excuse omitting the one interface kind the profile insists on, and the example keeps
  isolating a single failure.
- The demo gains the two product rules, a fourth example showing a subject with no administrative
  surface, and a product header that follows the selected subject rather than naming nginx always.
- Nine new tests. The suite runs 123 and passes.
- C14 found a drift on its first run: `subject` was declared as a scheme and P3 did not reference
  it. That is the check doing precisely what it was written for.

## Links

- Q34, which this settles; Q38, settled for this profile; Q20 and Q21, which remain open and are
  the reason the registry itself is not pinned here.
- Decision 0011, which this forced, and 0001, which established that rules constrain kinds and
  counts rather than instances — the principle P3 follows by requiring an identifier form rather
  than an identifier value.
- Conformance requirement C14 and the "what a conformance verdict does not assert" table, which
  named the two gaps P3 and P4 close.
