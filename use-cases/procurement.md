---
title: Procurement
sideMenu: true
weight: 3
aliases:
- /cbom/use-cases/procurement.html
linkTitle: Procurement
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A procurement profile is applied to the Keycloak document written for the [PQC migration](../pqc-migration/) use case. The document is not changed. This is the first worked example in the [disclosure](../disclosure/#procurement-and-tender-conformance) group.

Draft for discussion. The rules file and the failing example are in `drafts/procurement/`, and the profile extends the interface disclosure baseline v0.8 draft of decision 0022. Verdicts below were checked by reading the documents, not by the published validator.

## What this shows

The Keycloak document written for the PQC migration profile is read, **unchanged**, against a procurement profile. This is the first worked example in the disclosure group. It is also the first example to demonstrate with real documents that one detailed document can serve several consumers. Each consumer applies the profile that matches its own decision.

It also shows the limit of this reuse. The migration document contains every fact the procurement profile asks for, so the document can answer that profile. The reverse is not true. A document written only for procurement could not answer the migration profile, because nobody collected the capability attributes.

## Files

| File | Status |
| --- | --- |
| `profile-procurement.rules.json` | v0.1 draft. Extends the interface disclosure baseline v0.8 draft. Well-formed under C1–C17 with `--strict` |
| `examples/cbom-keycloak-procurement-fail.cyclonedx.json` | The conforming (pass) document with the storage interface removed. Fails `procurement#P5` only |
| Conforming example | `../pqc-migration-depths/examples/cbom-keycloak-pqc-pass.cyclonedx.json`, not copied |

## What the profile adds

The profile chooses which existing facts are required and makes some rules stricter. It does not add any new per-interface attribute.

| Rule | Requirement | Why a buyer needs it |
| --- | --- | --- |
| scope | Lifecycle stages `implemented`, `configured`, `observed`; excludes `intended` | A tender response describes what is offered. An intention is a promise and belongs in the commercial response |
| `I9` (override) | Implementing library, no longer withholdable | The buyer has to match advisories for the life of the contract. The tender's confidentiality terms deal with the supplier's reason to withhold it |
| `P5` (new) | A storage interface for key material at rest, or a stated reason for having none | Responses tend to describe the paths that traffic takes and say nothing about where keys are kept |
| `P6` (new) | Coverage `all` or `all-external`, not `partial` | A partial disclosure cannot be compared across responses |

## Verdicts

| Document | Expected | Published validator |
| --- | --- | --- |
| `cbom-keycloak-pqc-pass` | Conforms. `sto-realm-keys` satisfies P5, coverage is `all-external`, every interface reaches a library purl through `provides` | Does not conform: P5, and I9 on the TLS interfaces |
| `cbom-keycloak-procurement-fail` | Fails `procurement#P5` only | Same failures as the pass document |

The published validator cannot tell the two documents apart. It does not read CycloneDX services as interfaces (K7), so it never sees the storage interface. It does not inherit implementation facts through `dependencies[].provides` (K9), so I9 fails on every TLS interface. It also counts the two shared TLS configuration components as interfaces. The same gaps prevent the migration examples from getting tool verdicts. They are listed under `$pendingTooling` in the extended profile. The expected verdicts were checked by reading the documents against the rules, not by a patched tool.

P6 is the procurement-specific rule the tool can evaluate today. It passes on both documents, as intended.

## What this asks of the group

-   **The evaluator work now holds back two groups.** Until it reads services and inherits through `provides`, no Keycloak example in either group gets a tool verdict. So far the group has agreed that tooling waits until the profiles are right. This example is a reason to revisit that position for two adapter features only: reading services as interfaces, and inheriting through `provides`.
-   **Is P5 a procurement rule, or a baseline rule?** If every consumer needs to know where keys are kept, it belongs in the baseline beside P2. P4's coverage rule was handled the same way (Q34). It is kept here for now because no other drafted profile has asked for it.
-   **Should a tender be the restricted audience pair of the baseline rather than a profile?** If the only change were to remove the permission to withhold attributes for readers under an agreement, Confidentiality says to publish a pair at one depth. P5 and P6 add requirements beyond that. They are the reason this is a profile and not a pair.

[← Disclosure](../disclosure/) [Next: Change Planning →](../change-planning/)
