# Draft: PQC migration family depths

Working drafts for decision 0022. Nothing here is published by the site.

| File | Status |
|---|---|
| `profile-interface-enumeration.rules.json` | v0.2 draft. Channel rules I1, I2 skip storage interfaces. Well-formed, clean |
| `profile-interface-disclosure.rules.json` | v0.8 draft. Channel rules skip storage; adds I10 `keyWrapping`. Well-formed, clean |
| `profile-pqc-migration.rules.json` | Baseline v0.7 draft, pinned to the disclosure draft above. Well-formed under C1–C17 with `--strict` |
| `profile-pqc-migration-extended.rules.json` | Extended v0.1 draft. Well-formed under C1–C17 with `--strict`. The evaluator work these drafts need is listed under `$pendingTooling` |
| `0022-pqc-migration-family-depths.md` | Decision record draft |
| `examples/cbom-keycloak-pqc-pass.cyclonedx.json` | Conforms to pqc-migration v0.7 (and the shallower depths). Uses native fields (K8), inheritance from the providing library (K9) and document-level references (K10) |
| `examples/cbom-keycloak-pqc-fail.cyclonedx.json` | Fails pqc-migration#I12 only |
| `examples/cbom-keycloak-pqc-extended-pass.cyclonedx.json` | Conforms to pqc-migration-extended v0.1 and every shallower depth |
| `examples/cbom-keycloak-pqc-extended-fail.cyclonedx.json` | Fails pqc-migration-extended#I3 only |
| `mapping-cyclonedx-spdx.md` | Draft mapping: application-layer interfaces as CycloneDX services (K7). Replaces the published mapping on promotion |
| `mapping-native-fields-review.md` | Which properties have a native CycloneDX home; applied as K8 |
| `examples-keycloak-plan.md` | Review of the Keycloak cprofile and the design of the example pairs |

Only the files listed here belong to this draft. Keep third-party or confidential CBOMs used for
comparison outside the repository.

The example verdicts hold once the evaluator gaps in the extended profile's `$pendingTooling`
are closed. With the published validator unchanged, every example fails on attributes it does
not read.

Check with:

    python3 docs/methodology/check_profile.py drafts/pqc-migration-depths/<file>

On promotion: move all four rules files and the mapping into `docs/methodology/`, set every `artifacts` path
back to a sibling path (drop the `../../docs/methodology/` prefix), remove the DRAFT sentence from
each top-level `$comment`, move the record to `decisions/` and add it to the index. The
`extends.file` hints are already sibling paths.

## Site pages to update on promotion

The published site is not edited while these are drafts. On promotion, these pages change:

| Page | Change |
|---|---|
| `formats.html`, `mapping-cyclonedx-spdx.md` | Replace with the draft mapping: interfaces as protocol components or services (K7), native locations (K8), inheritance (K9), document-level references (K10) |
| `model.html`, `terms.html` | An interface is a logical boundary, not a port (K2); when an application-layer service is an interface (K7); storage interfaces are data at rest; `none` as a value (K3) |
| `profile.html`, `profile-interface-disclosure.md` | Disclosure baseline v0.8: storage guards, `keyWrapping`, `$commentInterface` |
| `maturity.html` | The family: enumeration v0.2, disclosure v0.8, pqc-migration v0.7, pqc-migration-extended v0.1 |
| `pqc-migration.html`, `use-cases/pqc-migration.html` | Two depths; module validation and validated-mode availability; inheritance of implementation facts |
| `conformance.html` | Rules are evaluated on effective values (K9) |
| `files.html` | New rules file and the four Keycloak examples in place of the gateway pair |
| `demo.html` | Loads the published rules (decision 0018), so it follows the rules files; its examples need the Keycloak pair once the validator reads services |
| `decisions/README.md` | Index entry for 0022 |
