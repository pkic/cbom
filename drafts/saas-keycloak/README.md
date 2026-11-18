# Draft: Keycloak as a managed service

The first worked example for the SaaS and cloud services domain document (10.1). Draft only:
none of these files is part of Release 1. The service profiles extend the published interface
disclosure baseline v0.10, which accepts the subject type `service` (R2-11, applied 17 November 2026).
The draft baseline written for R2-11 is in `_to_delete/`; delete the folder.

Run `python3 build.py` in this folder to regenerate every file.

## Files

| File | What it is |
| --- | --- |
| `profile-service-disclosure.rules.json` | The public service profile (domain document 8.2). Orientation `both`. |
| `profile-service-disclosure-restricted.rules.json` | Its restricted pair (8.3): coverage `all`, implementing library not withholdable. |
| `examples/cbom-keycloak-service-restricted.cdx.json` | The restricted variant. Coverage `all`. |
| `examples/cbom-keycloak-service-public.cdx.json` | The public variant. Coverage `all-external`; the database, directory, cluster and health links are left out. |
| `examples/cbom-keycloak-service-fail-custody.cdx.json` | The restricted variant with the key-custody attributes removed from the realm-key store. |

The service records are built from `cbom-keycloak-deployment-configured.cdx.json`. They cite the
Keycloak product record by BOM-Link and hash, as the deployment record does.

## Verdicts

Run from the repository root, with
`--with docs/methodology/examples/cbom-keycloak-product.cdx.json`:

| Document | service-disclosure | service-disclosure-restricted |
| --- | --- | --- |
| restricted | conforms | conforms |
| public | conforms | fails restricted#P1 (coverage) |
| fail-custody | fails I1 and I3 | fails I1 and I3 |
| restricted, against the baseline v0.9 | fails P3 and P5: v0.9 does not accept `service` | |
| restricted, against the baseline v0.10 | conforms | |

Both draft profiles are well formed under `check_profile.py`.

## What the example showed

- R2-11 was needed and was enough; it is now applied. The validator already handles the subject type `service`. Only the
  baseline's accepted subject types and its identifier form stop a service record today.
- `keyCustodySupported` is a capability under the naming convention, so requirement C12 rejects it in an
  inventory profile. The service profiles therefore declare orientation `both` and require the
  present-state attribute `keyCustody`: the custody model a new tenant gets by default.
- The public variant can keep the storage interface. It leaves out the internal links instead, which
  coverage `all-external` permits.
- The realm-key store records encryption `none` under `provider-managed` custody. That is the finding a
  customer would want from this record.

The CycloneDX schema check was skipped in this environment (it needs jsonschema 4.18 or later with
`referencing`). The published test suite passes: 337 passed, 0 failed.
