# 0016. Product-level rules are not evaluable from SPDX alone, and a claim says so

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.6 — Mapping to serialization formats
- **Topic / issue:** #2
- **Deciders:** not yet taken; settles Q48
- **Decision rule applied:** lazy consensus (pending)

## Context

In the current arrangement an SPDX document satisfies a profile by referencing a CycloneDX CBOM as
an external artifact. That works for the attribute rules, which are evaluated against the referenced
CBOM. It does not work for the product-level rules, because the SPDX side has **one element for the
whole product** and the product rules count and classify interfaces. There is nothing there to
count.

The mapping document previously filled those rows in — an annotation per interface, a count of
annotated elements — describing a structure the linkage arrangement does not produce. Q48 recorded
the gap after they were marked unresolved.

The consequence is not academic. A consumer receiving an SPDX-only conformance claim would read
"conforms to the interface disclosure baseline" and reasonably assume that included P2, the rule
requiring a management interface to be declared or its absence explained — the rule that exists
because the administrative interface is the one most often left out. It did not, and nothing said so.

## Options considered

- **Option A — one SPDX element per interface**, with the CBOM linked per interface rather than
  once. Gives the product rules something to count (trade-off: multiplies the linkage, and it is
  not clear which SPDX element class should stand for an interface. It also asks SPDX to model
  something it has not chosen to model).
- **Option B — carry the interface classifiers as annotations** on the single reference element,
  encoded so several interfaces can be distinguished within it (trade-off: an encoding convention
  invented by this group inside another format's extension point, which is the kind of thing
  harmonisation is supposed to avoid).
- **Option C — state that product-level rules are not evaluable from SPDX alone**, and bound what an
  SPDX-only claim may assert.

## Decision

Proposed: Option C, made machine-readable rather than left in prose.

A claim carries **`evaluableFromCarrier`**: which kinds of rule the carrier holds enough structure
to evaluate. For CycloneDX, all three. For SPDX in the linkage arrangement, `productRules: false`.

Where a kind is not evaluable, the claim's **`notAsserted`** list gains a line saying so in the same
place a consumer already reads what a verdict does not cover. The bound is therefore visible to
whoever is holding the claim, rather than to whoever reads the mapping document.

The mapping document keeps its rows marked unresolved. That is the honest state, and Option A or B
would change it by inventing a structure rather than by discovering one.

## Rationale

The three options are not equally weighted, and it is worth being explicit about why. Options A and
B both propose that this group invent something inside a format it does not own — either a modelling
convention SPDX has not adopted, or an encoding inside an extension point. Either would produce
documents that only our tools can read, which is precisely the fragmentation the methodology exists
to prevent, arriving under the banner of format independence.

Option C concedes something real: the claim "one profile, two formats" holds for the attribute rules
and not for the product rules. Saying so costs less than it appears to, because the alternative is
not a stronger claim — it is the same weak claim with the weakness undocumented.

Making the bound a field rather than a paragraph is the part that does the work. A prose caveat in a
mapping document is read by people implementing the mapping. A field in the claim is read by the
person deciding whether to accept a supplier's submission, which is where the misunderstanding would
otherwise be expensive.

SPDX is adding cryptographic modelling. If it grows a structure that carries interfaces as distinct
elements, this decision is superseded and `CARRIER_CAPABILITY` is where that change lands — one
table, not a rewrite.

## Consequences

- `CARRIER_CAPABILITY` in `validate_cbom.py` records, per carrier, which rule kinds are evaluable.
  A claim carries the entry for the carrier it was evaluated against.
- A kind that is not evaluable adds a line to `notAsserted`, so it appears where a consumer already
  looks for the limits of a verdict.
- `claim.schema.json` documents the field and the SPDX case.
- The validator itself reads CycloneDX only, so the SPDX row is declarative today. It is written
  down now because the claim format is being fixed now, and adding the field later would mean every
  claim issued in between is silent about a bound that applied to it.
- Q48 is settled. The mapping document's unresolved rows stay unresolved, which is the point.

## Links

- Q48, which this settles, and Q16 to Q18 on the format mapping generally.
- Decision 0015, which defines the claim this field lives in.
- `mapping-cyclonedx-spdx.md`, whose unresolved rows are the evidence for this rather than a defect
  to be tidied away.
