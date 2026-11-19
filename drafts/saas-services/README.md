# Draft: service profiles of the SaaS domain document

Three draft profiles for the SaaS and cloud services domain document, and their examples. Draft
only: none of these files is part of Release 1. All records start from the published restricted
service record (`docs/methodology/examples/cbom-keycloak-service-restricted.cdx.json`). Values are
illustrative.

Run `python3 build.py` in this folder to regenerate every file.

## Profiles

| File | SaaS document | Extends | Adds |
| --- | --- | --- | --- |
| `profile-service-key-custody.rules.json` | 8.4 | Service Disclosure, Restricted v0.1 | On every storage interface: `keyStoreRef` (I1, a component of this or a cited record, or the PQC Migration Extended literals `none`, `out-of-band` and `product-managed`), `replicaProtection` (I2: `same-as-primary`, `differs-from-primary` or `no-replicas`), `moduleValidationScheme` (I3, SHOULD) |
| `profile-service-change-planning.rules.json` | 8.5 | Change core v0.2 | Narrowed to `service` and `configured`; P1: cite the records it builds on, by hash. No new attribute |
| `profile-tenant-disclosure.rules.json` | 8.6 | Deployment Disclosure v0.2 | On every storage interface: the tenant's `keyCustody` (I1); for `external`, `externalKeyService` in a cited record (I2) |

The baseline already requires `keyWrapping` on every storage interface, so the key-custody depth
does not repeat it.

## Verdicts

From `docs/methodology/`:

| Document | Profile | Verdict |
| --- | --- | --- |
| `cbom-keycloak-service-key-custody` | service-key-custody | conforms |
| `cbom-keycloak-service-key-custody-fail-replica` | service-key-custody | fails I2 |
| `cbom-keycloak-service-change-planning` | service-change-planning | conforms (also conforms to both service disclosure profiles) |
| `cbom-keycloak-tenant-configured` | tenant-disclosure, `--with examples/cbom-keycloak-service-restricted.cdx.json` | conforms |
| `cbom-keycloak-tenant-fail-custody` | tenant-disclosure, same | fails I1 |

## What the examples showed

- The change-planning record takes its capability facts from the Keycloak product record, interface
  by interface, through `correspondsTo`. Only the ingress, which the provider runs itself, needs
  facts of its own. The provider writes little that the vendor has not already written.
- The tenant's choice is bounded by the service: Keycloak keeps realm keys in its database, so the
  service offers only `provider-managed` and the tenant can choose nothing else. The external-key
  rule (I2) is not exercised by this example. A service that offers external keys is needed for that.
- Nothing checks that a tenant's `keyCustody` is one the service record offers. That would need a
  constraint that compares a value with a list in a cited record.
