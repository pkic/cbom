# 0003. Absence is distinguished from withholding

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.4 — Obligation levels & conformance semantics
- **Topic / issue:** #6
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

A required attribute may be missing for several reasons: the producer chose not to disclose it,
the producer looked and could not determine it, or the producer never addressed it. Under a
plain present-or-absent model these are indistinguishable, so a consumer cannot tell a
deliberate commercial redaction from an incomplete document. The 2026 SBOM minimum elements
make the same distinction, requiring that a field with no value carry a reason.

## Options considered

- **Option A — present or absent.** Minimal to specify and to check (trade-off: a producer who
  redacts one field for legitimate reasons is scored identically to one who produced nothing,
  which discourages disclosure of the remaining fields).
- **Option B — three declared states plus absence.** `value`, `withheld` and `unknown` are
  asserted in the document; `undeclared` is the residue (trade-off: the carrier must be able to
  express a marker, and profiles must state per rule whether withholding is permitted).

## Decision

Option B. Every rule carries a `withholdable` flag. A conforming producer either supplies a
value or asserts `withheld` or `unknown` using the profile's declared marker prefix. Withholding
satisfies a rule only where `withholdable` is true. `undeclared` never satisfies a rule.

## Rationale

The three states carry different meanings to a consumer. `withheld` invites a commercial
conversation, `unknown` indicates a gap in the producer's own visibility and is often the more
serious finding, and `undeclared` indicates the document was not built against the profile.
Collapsing them discards the information a consumer would act on.

## Consequences

Validator output reports the state alongside the verdict, so a conforming document that withholds
material is visibly different from one that does not. Profile authors must decide `withholdable`
for each rule, which is a substantive negotiation between producers and consumers rather than a
formatting detail. Alignment with the 2026 minimum elements comes without further work.

## Links

- Profile and Policy Evaluation sections of the methodology documentation.
- `analysis-2026-sbom-minimum-elements.md`.
