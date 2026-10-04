# Grouping the use cases

Working note, 4 October 2026. Draft for the working group. Not yet discussed.

## Position

- **Group use cases by how their profile relates to the baseline.** That relation decides whether one
  document can serve several consumers. The index page already makes this argument in its last
  banner, and the methodology's use-case page makes it under "attributes emphasised". The flat list
  of nine does not show it.
- **Two groups, plus one entry that is not a use case.**
  - **Disclosure.** Each profile selects and tightens facts the baseline already defines. One rich
    document serves every profile in the group.
  - **Change planning.** Each profile adds capability facts the baseline does not have. A document
    produced against the baseline cannot be evaluated against them.
  - **The CI quality gate is a way of applying a profile, not a use case.** It moves out of the
    count and into Conformance.
- **Subject is the second axis.** Product, device model, system or estate decides what kind of
  document is produced and who can produce it. It is already a field: `scope.subjectType`.
- **Sector is not an axis.** Telecom, energy and OT pick a cell and add vocabulary. This follows the
  existing rule that sector vocabulary is pushed into profiles.
- **The change-planning group resolves Q64 with Option C.** A shared change core sits under the
  migration, IoT and substation profiles. It is published as a sibling first, so no rule ids move.

## Options considered

| Grouping | Case for it | Case against | Verdict |
|---|---|---|---|
| By relation to the baseline (selection or extension) | It predicts whether a document can be reused. It matches the composition rules and the profile tree | Two groups is coarse | **Chosen** as the primary axis |
| By subject (product, model, system, estate) | It decides the producer and the kind of document. It is already in `scope` | It cuts across decisions: procurement and PQC migration share a subject but not a document | **Chosen** as the second axis |
| By sector (telecom, energy, IoT, OT) | It is how members arrive | It breaks "use case = decision". It would duplicate every disclosure profile per sector | Rejected. Sectors are instances |
| By product lifecycle (procure, operate, respond, migrate, retire) | It is the easiest order for a reader | It predicts nothing about profiles or documents | Use it as the reading order within each group, not as structure |
| By consumer role (buyer, operator, regulator, responder) | Familiar | The same role makes different decisions. An operator both responds and migrates | Rejected |

## The groups

### Disclosure: one document, many profiles

These profiles select and tighten baseline facts, with orientation `inventory`. The depth ladder of
decision 0019 applies here.

| Use case | Relation to the baseline | Subject | State |
|---|---|---|---|
| Supply-chain transparency | The baseline itself, bounded by what a supplier may withhold | product | Served by the baseline |
| Procurement and tender conformance | Selects and adds structural rules (interfaces present at all) | product | Catalogue |
| Vulnerability response | Tightens `I9` to non-withholdable. Joins to VEX (0020) | product | Blocked on Q57 |
| Regulatory and compliance reporting | One profile per framework, so a sub-family keyed by framework | product or estate | Catalogue |
| Mergers and due diligence | The entry depth applied across an estate. Coverage over depth | estate | Catalogue. Probably no new profile |

### Change planning: a richer document, orientation `both`

These profiles add capability, blocker and enablement facts.

| Use case | Subject | Adds over the change core | State |
|---|---|---|---|
| Crypto-agility assessment | any | Nothing, if the core is target-neutral. This is a test of the core, not a new profile | Catalogue |
| PQC migration | product | Product rules, module validation, the extended depth | Developed (Keycloak) |
| IoT device estate | device model | `resourceBound`, model-versus-instance rules (Q62, Q63) | Draft. Blocked on Q62 to Q65 |
| Substation automation (OT) | system | `certificationImpact`, `verifierReplaceable`, plus a system overlay | Draft, October 2026 |

**Not a use case:** the CI quality gate. Any profile can gate a pipeline. The requirement falls on
the validator's exit status and report, which Conformance and the Demo already cover.

## The profile tree this implies

Each profile has a single base: the schema takes one `extends` object. So the shared attributes
have to sit in a common ancestor. They cannot be mixed in from two places.

```
interface-enumeration                  depth 0   (orientation: inventory)
└─ interface-disclosure baseline       depth 1   ← the disclosure group: depths, tightenings, audience pairs
   └─ change-core                      branch    (orientation: both; subjectType: product | device-model | system)
      ├─ pqc-migration                 product       └─ pqc-migration-extended (depth)
      ├─ iot-estate                    device-model
      └─ pqc-migration-ot              product (component)
sas-system                             overlay over component documents (system)
```

**The change core holds what the migration, IoT and substation drafts all ask for:**

- `capabilityStatus`, `blockedBy` and `roadmapRef` per purpose;
- the `Supported` forms of the algorithm attributes;
- `enablementMethod` and `providerLocation`;
- `coexistence` and `negotiationControl`;
- `integrationConstraints`;
- `keyWrapping` and `keyWrappingSupported`.

The update-path facts that IoT and OT share (`updateMechanism`, `updateAuthority`, `keyReplaceable`)
go into the core as **conditional rules**: they apply only to update interfaces. Keycloak has no
update interface, so it is not burdened. This is how single inheritance carries a fact two branches
share.

**No rule ids move.** The core is published beside pqc-migration v0.7 as a sibling, declaring each
shared rule under the id pqc-migration already uses. This is the same technique the entry profile
used with the baseline. `tests/check-family.py` then enforces the ladder. Re-parenting
pqc-migration onto the core is deferred, and is the same choice as Q51.

**The system overlay is a fourth relation.** Depth, branch and audience pair all relate a profile to
a profile. An overlay is a profile for a document that references other documents. Maturity's
"Depth and branch" section needs one more paragraph, and the derived-CBOM work is where it belongs.

## Test: the telecom use cases

The eight use cases in the telecom CBOM paper all fall into a cell without forcing:

| Telecom use case | Group | Subject |
|---|---|---|
| Supply-chain risk management | Disclosure: supply-chain transparency | product |
| Vulnerability detection and incident response | Disclosure: vulnerability response | product, then deployed |
| Regulatory compliance and audit | Disclosure: compliance, framework sub-family | estate |
| Procurement (section 5.4) | Disclosure: procurement | product |
| Cloud-native NF lifecycle (DevSecOps) | Not a use case: the CI gate | product |
| O-RAN ecosystem governance | Disclosure: procurement or supply chain, per component | product (component) |
| Service assurance | Overlay: components mapped to services | system |
| Third-party software change impact | Versioning: a diff between two documents, not a profile | product |

Two results matter here:

- **No telecom entry needs a new group.** Two of them need nothing from the profile layer at all:
  the CI gate and the version diff.
- **Service assurance lands next to the substation overlay.** That makes the system subject a
  cross-sector need, not an OT peculiarity.

## Consequences

| Item | Change |
|---|---|
| `docs/use-cases/index.html` | Replace the flat table with the two group tables and a subject column. Move the CI gate under "ways of applying a profile". Change the tag "1 of 9 developed" to a count per group |
| `docs/methodology/use-cases.html` | Split "Attributes emphasised" by group. Change-planning columns are core attributes, which fixes the IoT row the page admits it serves badly |
| `docs/methodology/maturity.html` | Add the overlay as a fourth relation |
| Q64 | Answered by Option C, via a sibling core, with no revision to the reviewed migration profile |
| Q50 (where a family is recorded) | The two groups give the register its top level |
| Substation draft | `pqc-migration-ot` extends `change-core`, not pqc-migration. Its update rules move into the core |
| Decision numbering | Grouping becomes draft decision 0023. The substation draft's O1 to O6 become 0024 |

## Open questions

1. **Is the change core target-neutral?** `capabilityStatus` has a neutral vocabulary, but
   pqc-migration's objective makes "capability" mean quantum-safe. If the target is stated per
   document or per policy, crypto-agility needs no profile of its own. If not, the core is
   PQC-specific and crypto-agility becomes a sibling.
2. **Should compliance reporting be listed as one use case or as a family?** The index already calls
   it a family of use cases.
3. **Does vulnerability response stay in disclosure?** It does as long as it only tightens `I9`.
   Q57 decides it.
4. **Is an estate a subject type, or an aggregation of product documents?** M&A and compliance both
   reach for it, and no profile yet declares it.

## Placeholders added, 4 October 2026

Catalogue entries 10 to 16. Each names a consumer and a decision and nothing more.

| # | Entry | Group | Subject | Origin |
|---|---|---|---|---|
| 10 | Managed and cloud service disclosure | Disclosure | operated service | The producer is the service operator, so the upper bound on what may be asked moves |
| 11 | Service assurance | Disclosure (overlay) | system | Telecom paper |
| 12 | Substation automation | Change planning | system | Drafted: `drafts/ot-substation/` |
| 13 | PKI and certificate estate migration | Change planning | system | Relying-party capability is the new fact |
| 14 | Code and firmware signing migration | Change planning | signing service and verifiers | Shares update-path rules with IoT and substation |
| 15 | Stored data and archive protection | Change planning | operated estate | `design-note-data-and-hndl.md` |
| 16 | Shared-trust network migration | Change planning | network of parties | `design-note-multiparty-trust.md` |

Change impact between versions, from the telecom paper, is listed under "Applying a profile" with
the CI gate, and points to Versioning.

The open questions in this note are now Q66 (target-neutral core) and Q67 (estate as subject),
plus Q68 (overlay obligations), in `open-questions.md`.
