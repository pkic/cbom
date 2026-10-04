# Draft: procurement profile, and one document read by two profiles

Working draft, 4 October 2026. Disclosure group (draft decision 0023), catalogue entry 2. Nothing
here is published by the site.

## What this shows

The Keycloak document written for the PQC migration profile is read, **unchanged**, against a
procurement profile. This is the first worked example in the disclosure group. It is also the
first demonstration of the claim the use-case pages make without showing: one rich document
serves several consumers, each applying the profile that matches its decision.

It also shows the limit. The procurement profile asks for nothing the migration document lacks,
so the document answers it. The reverse does not hold: a document written only for procurement
could not answer the migration profile, because the capability attributes were never collected.

## Files

| File | Status |
|---|---|
| `profile-procurement.rules.json` | v0.1 draft. Extends the interface disclosure baseline v0.8 draft. Well-formed under C1–C17 with `--strict` |
| `examples/cbom-keycloak-procurement-fail.cyclonedx.json` | The pass document with the storage interface removed. Fails `procurement#P5` only |
| Conforming example | `../pqc-migration-depths/examples/cbom-keycloak-pqc-pass.cyclonedx.json`, not copied |

## What the profile adds

The profile selects and tightens. It adds no per-interface attribute.

| Rule | Requirement | Why a buyer needs it |
|---|---|---|
| scope | Lifecycle stages `implemented`, `configured`, `observed`; drops `intended` | A tender response describes what is offered. An intention is a promise and belongs in the commercial response |
| `I9` (override) | Implementing library, no longer withholdable | The buyer has to match advisories for the life of the contract. The tender's confidentiality terms answer the supplier's reason to withhold |
| `P5` (new) | A storage interface for key material at rest, or a stated reason for having none | Responses describe the paths traffic crosses and stay silent about where keys are kept |
| `P6` (new) | Coverage `all` or `all-external`, not `partial` | A partial disclosure cannot be compared across responses |

## Verdicts

| Document | Expected | Published validator |
|---|---|---|
| `cbom-keycloak-pqc-pass` | Conforms. `sto-realm-keys` satisfies P5, coverage is `all-external`, every interface reaches a library purl through `provides` | Does not conform: P5, and I9 on the TLS interfaces |
| `cbom-keycloak-procurement-fail` | Fails `procurement#P5` only | Same failures as the pass document |

The published validator cannot tell the two documents apart. It does not read CycloneDX services
as interfaces (K7), so it never sees the storage interface. It does not inherit implementation facts
through `dependencies[].provides` (K9), so I9 fails on every TLS interface. It also counts the two
shared TLS configuration components as interfaces. These are the same gaps that hold back the
migration examples, listed under `$pendingTooling` in the extended profile. The expected verdicts
were checked by reading the documents against the rules, not by a patched tool.

The procurement-specific rule the tool can read today, P6, passes on both documents, as intended.

## What this asks of the group

- **The evaluator work is now the bottleneck for two groups, not one.** Until it reads services and
  inherits through `provides`, no Keycloak example in either group gets a tool verdict. The standing
  position has been that tooling waits until the profiles are right. This example is a reason to
  look at that again for these two adapter features only.
- **Is P5 a procurement rule, or a baseline rule?** If every consumer needs to know where keys are
  kept, it belongs beside P2 in the baseline, as P4's coverage rule did (Q34). It is kept here for
  now because no other drafted profile has asked for it.
- **Should a tender be the restricted audience pair of the baseline rather than a profile?** If the
  only change were removing withholdability under an agreement, Confidentiality says to publish a
  pair at one depth. P5 and P6 are why this is a profile and not a pair.
