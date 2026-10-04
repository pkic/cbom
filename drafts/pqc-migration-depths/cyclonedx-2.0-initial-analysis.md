# CycloneDX 2.0: initial analysis for the PKIC CBOM profiles

Working note, 30 September 2026. For meeting 12, agenda item on CycloneDX 2.0.

## Source

- Repository `CycloneDX/specification`, branch `2.0-dev-safety`, commit `78f96fe` of 20 September
  2026. The bundled schema is `schema/2.0/cyclonedx-2.0-bundled.schema.json`.
- This is a development branch, not a release. Field names can still change. Ratification by Ecma
  is expected around December 2026.
- Compared against `bom-1.7.schema.json` from the same repository and our draft 0022 material:
  the four rules files, the two mapping notes and the Keycloak examples.

## Summary

- **The wire format breaks.** Our Keycloak extended example (CycloneDX 1.7) fails the 2.0 schema
  with 19 errors. Six mechanical changes fix all of them. Nothing in the profile content had to
  change.
- **Services disappear as a separate list.** A service is now a component of `type: "service"`.
  K7 survives. The adapter and every rule that reads `services` must follow.
- **The crypto model grows modestly.** Key rotation and certificate renewal, key usage, security
  properties, `cavp`, more modes and functions. Protocol types and cipher suites are unchanged.
- **Three new native homes for our attributes.** `certifications` on any component, `agility` on
  any component, and `rotation`/`renewal` on keys and certificates.
- **The migration-management fields sit in the risk model, not the crypto model.** Risk, response,
  owner, target date and status are a risk register. Decisions 0002 and 0007 keep them out of a
  supplier CBOM.
- **"Perspectives" overlap with what a PKIC profile is.** A perspective is a set of JSONPath
  expressions, each marked required, recommended, optional or informative. That is a light
  profile carried in the document.
- **The edge gap is not closed.** The blueprint model has interfaces, boundaries and flows, but it
  is a threat-modelling structure, not a place to state a product's cryptographic boundary.

## Conversion test

The Keycloak extended-pass example was converted with a throwaway script and validated offline
against the bundled 2.0 schema. The script is in the session scratch space only. It is not
tooling.

| 1.7 construct | Occurrences | 2.0 form |
|---|---|---|
| `bomFormat` | 1 | `specFormat` |
| `services[]` | 13 | `components[]` with `type: "service"` |
| `purl` | 5 | `identifiers[]`. Each entry needs an asserting `party` |
| `supplier`, `manufacturer` on a component | 3 | `parties[]` with a role |
| `protocolProperties.cryptoRefArray` | 7 | `relatedCryptographicAssets[]` |
| `relatedCryptoMaterialProperties.algorithmRef` | 4 | `relatedCryptographicAssets[]` |
| `algorithmProperties.curve` | 1 | `ellipticCurve`, an enumeration: `other/Curve25519` |

After these changes the example validates with no errors. All 297 `pkic:profile:` properties
carry over unchanged. `dependencies[].provides` is unchanged, so K9 inheritance works as before.

The `curve` finding applies to 1.7 as well. `curve` was already deprecated there. The examples
should use `ellipticCurve` now.

## Changes that matter to the profiles

### Structure

- **No root `services`.** Components of type `service` keep `endpoints` and gain `dataProfiles`.
  `authenticated`, `x-trust-boundary`, `trustZone` and `data` are gone from the service. They move
  to the blueprint and data models. We did not use them.
- **A service component can carry anything a component can,** including `cryptoProperties`,
  `agility` and `certifications`. Only `endpoints` and `dataProfiles` are restricted by type.
- **Identity is claimed by a party.** `purl`, `cpe`, `swid` and `swhid` move into `identifiers`,
  alongside 20 other schemes (GTIN, serial number, MAC address and more). Rule P3 (the subject has
  a Package URL) needs a new path, and a producer must declare who asserts the identifier.
- **Supplier and manufacturer become roles on parties.** They remain at `metadata` level, but not
  on `metadata.component` or on components.

### Cryptography

| Change | Where | Relevance to us |
|---|---|---|
| `rotation`, `renewal` (`lifecycleControl`: automation `not-supported`, `manual`, `on-demand`, `automatic`, plus a mechanism) | Keys and certificates | Native home for part of the extended key-management rules |
| `keyUsage` (cryptographic functions) | Key material | Per key. Our `keyOperations` is per surface, so it stays |
| `secProperties` (IND-CCA, EUF-CMA and similar) | Algorithms | Helps classify KEMs. Optional for us |
| `certificationLevel` adds `cavp` | Algorithms | Still no ISO/IEC 19790 or national schemes |
| New modes, padding and functions (`keyagree`, `wrap`, `unwrap`, `keyver`, `paramgen`) | Algorithms | `wrap` and `unwrap` fit `keyWrappingSupported` evidence |
| `implementationPlatform` becomes an array | Algorithms | Adapter change only |
| `certificateState` gains states and a custom option | Certificates | None |
| `securedBy.algorithmRef` becomes an array | Key material | Adapter change only |
| `cryptoRefArray`, `algorithmRef`, `signatureAlgorithmRef`, `subjectPublicKeyRef` removed | Several | All become `relatedCryptographicAssets`. See the in-use convention below |

Unchanged: the protocol type enumeration (still no OIDC, SAML or HTTP, so K7 stands), cipher
suites with `tlsGroups` and `tlsSignatureSchemes`, and `nistQuantumSecurityLevel`.

**The in-use convention needs restating.** The mapping says `cipherSuites` means supported and
`cryptoRefArray` means in use. `cryptoRefArray` is gone. `relatedCryptographicAssets` has a
free-text `type`, meant for the kind of asset (`publicKey`, `algorithm`), not its state. The
convention moves to `relatedCryptographicAssets`, and the feedback item for a supported/in-use
distinction stays open.

### New native homes

| Our attribute | 2.0 field | Fit |
|---|---|---|
| `moduleValidationScheme`, `moduleValidationRef` (I10, I11) | `certifications[]` on the implementing library: `standard`, `identifier`, `level`, `url`, `issuer`, dates | Good. Put it on the library and inherit through `provides` (K9). This also answers our feedback on ISO/IEC 19790 and national approval, because `standard` is free text |
| `productCertificationScheme` (extended P2) | `certifications[]` on the subject | Good |
| `negotiationControl` (I8) | `agility.negotiated` | Partial. It says whether the configuration is negotiated, not whether the far end can be pinned |
| `enablementMethod` | `agility.changeMechanism` | Partial. It describes changing the current configuration. It has no `licence` and no "not available" in the product's sense |
| `enablementSetting` (extended) | `agility.configurationRef` to a `data` component of type `configuration` | Plausible. Needs a worked example |
| Key rotation and certificate renewal (extended) | `rotation`, `renewal` | Good, where the extended rules ask how keys are replaced |

The capability group (`capabilityByPurpose`, about 200 of the properties in the Keycloak example)
still has no native home. `agility` describes the component as it is. The group states what each
purpose can do and what blocks it. That remains the core of what the profiles add.

## Migration management: risk, response, owner, target date, status

The announcement says each crypto asset can carry a risk, a response, an owner, a target date and a
status. In the schema these are not crypto fields. They are the root `risks` array:

- `risk.affects` points at any component, including a cryptographic asset;
- `risk.status`: identified, assessed, treated, monitored, retired;
- `risk.owner` is a party;
- `risk.responses[]` carries `strategy` (avoid, reduce, share, accept), `controls`, `status`
  (proposed, planned, in-progress, implemented, verified), `owner` and `targetDate`;
- `controls` bind implementing components to the requirements they satisfy.

This is an operator's migration register expressed in the BOM. It is judgement, not product fact.

- Decision 0002 (facts in the CBOM, judgements in policy) puts it outside a supplier's
  conformance claim.
- Decision 0007 (availability as status and blocker, not a date) already rejected dates for
  supplier capability. A `targetDate` in a supplier CBOM would bring the same problem back.
- It fits well in an operator's CBOM for their own estate. That is a different document, and a
  candidate for a later profile.

A profile could say that `risks` are ignored for conformance, or that a supplier-issued
pqc-migration CBOM should not contain them. The group should choose.

## Perspectives and the word "profile"

- **Perspectives** name a domain (`cryptographic-security` is predefined) and list JSONPath
  expressions with a relevance of required, recommended, optional or informative. The schema's own
  example is `$.components[?(@.type=='cryptographic-asset')]` named "Cryptographic Inventory".
- They cannot express conditions (`requiredWhen`), enumerations, groups, withholding or
  monotonic extension. They are not a replacement for the rules files.
- They could be a companion. Each PKIC profile could publish a perspective that lists its native
  fields, so generic 2.0 tooling can filter and check presence without our validator.
- **The word "profile" collides.** CycloneDX 2.0 has a root `profiles` object holding
  `dataProfiles` and `threatProfiles`, which are reusable characterizations of a subject. Decision
  0021 (one word, one meaning) suggests we always say "PKIC CBOM profile" in anything that also
  talks about CycloneDX.
- **"Interface" collides too.** The blueprint model defines an `interface` with types such as
  `rest`, `grpc` and `cli`. That is a different concept from our cryptographic boundary (K2).

## The edge gap

The blueprint model has `boundaries` between `zones`, and `flows` with a source, a destination,
protocols and an `encrypted` flag. Source and destination come close to our endpoint roles.

It does not close the gap:

- a blueprint models a deployed system for threat analysis, not a product's cryptographic
  surface;
- `flow.protocols` and `interface.protocol` are free text, with no link to protocol components;
- `encrypted` is a boolean, which loses everything the profiles care about.

Our `interfaceType` and `endpointRole` properties stay for now. The feedback item for an interface
and endpoint-role model on service components stays open, and is worth raising while 2.0 is still
in development.

## Effect on our material

| Item | Effect |
|---|---|
| Rules files | Paths change for P3 (Package URL) and anything reading supplier or `services`. Attribute names and levels do not change |
| Decision 0006 (carrier acceptance range) | Needs a line on 2.0. A 1.7 document is not valid 2.0, whatever the announcement says about backward compatibility |
| `mapping-cyclonedx-spdx.md` and `mapping-native-fields-review.md` | Add a 2.0 column. Move I10, I11 and P2 to `certifications`. Mark I8 and `enablementMethod` as partial fits |
| Keycloak examples | Replace `curve` with `ellipticCurve` now. Produce a 2.0 variant once the schema settles |
| Validator adapter (deferred) | Read services from `components`, identifiers from `identifiers`, and both reference forms |
| cbomgen feedback | Add: emit `ellipticCurve` and `relatedCryptographicAssets`, and put module validation in `certifications` |

## Proposed questions for meeting 12

1. Stay on 1.7 as the normative carrier for the v0.x profiles, and add 2.0 when Ecma ratifies it?
2. Adopt `certifications` for module validation and product certification, in both 1.7-era
   guidance (as a property) and the 2.0 mapping?
3. Keep `risks` out of supplier conformance, consistent with 0002 and 0007?
4. Publish a CycloneDX perspective alongside each PKIC CBOM profile?
5. Send the edge-gap and in-use feedback to CycloneDX now, while 2.0 is open?

## Not yet looked at

- The XML and Protocol Buffers forms of 2.0.
- The threat model's `threatProfiles` and `trustBoundary`, and the standard and requirement
  models as a way to publish profile rules.
- Whether the 2.0 SPDX mapping changes anything in decision 0016.
