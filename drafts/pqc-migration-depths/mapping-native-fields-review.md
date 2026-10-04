# Review: which `pkic:profile:` properties have a native CycloneDX 1.7 home

**Applied 27 September 2026** (decision 0022, K8): the first table is now in the draft mapping and the Keycloak examples. The extended example carries 454 properties, down from 575.

Written 27 September 2026 against the CycloneDX 1.7 JSON schema (as bundled in
cyclonedx-python-lib 11.12.0) and the extended Keycloak example, which carries 575
`pkic:profile:` properties.

## Test

A property moves to a native field only if all three hold:

1. **Same meaning.** The field records the same fact, not a neighbouring one.
2. **Same or derivable granularity.** A per-interface attribute can come from a per-algorithm
   field only if the value can be derived deterministically.
3. **The value set covers the vocabulary.** Otherwise the field needs an escape value that loses
   the distinction the profile exists to make.

## Move to native fields

| Profile attribute | CycloneDX 1.7 location | Notes |
|---|---|---|
| `interfaceId` | `bom-ref` | Redundant. Drop the property. |
| `implementationPurl` | `dependencies[].provides` from the library component (which carries `purl`) to the protocol component or service | The examples already emit `provides` for the JDK. Two statements of one fact can disagree; keep one. |
| `providerLocation` | `algorithmProperties.executionEnvironment` on the algorithms the interface uses | `software-plain-ram`/`software-encrypted-ram` → `software`, `software-tee` → `tee`, `hardware` → `hsm`. Derivable if the interface's algorithms agree; a mixed answer is a finding, not an error. |
| `keyTypes` (present state) | `related-crypto-material` components (`type: private-key` or `secret-key`, `algorithmRef`, `size`, `state`) that the management surface or service depends on | The realm key is already one. Richer than the property: size, state and dates come with it. |
| `keyStoreFormats` | `relatedCryptoMaterialProperties.format` | Values are free text in CycloneDX; the profile's vocabulary becomes a convention on that field. |
| `keyWrapping` | `relatedCryptoMaterialProperties.securedBy` (`mechanism`, `algorithmRef`) on the stored key | Exactly the fact. An unwrapped key has no `securedBy`, which is ambiguous with "not stated", so keep `none` explicit (K3) as `mechanism: "none"`. |
| `keyExchangeSupported`, `authenticationSupported` (TLS only) | `protocolProperties.cipherSuites[].tlsGroups` and `.tlsSignatureSchemes` | New in 1.7. Needs one convention: `cipherSuites` lists the **supported** set, `cryptoRefArray` the algorithms **in use**. That preserves the bare/`Supported` distinction (decision 0005) natively. Removes about 80 properties from the example. Not available for SSH, IPsec or services. |
| `moduleValidationRef` | `externalReferences[type="certification-report"]` on the implementing library component | Exactly the fact, one level down: the certificate belongs to the module, not the interface. |
| `coverage` (P4) | `compositions[]` with `aggregate` over an `assemblies` list of the interfaces | `all` → `complete`; `partial` → `incomplete`. `all-external` has no value; carry it as `complete` over an assembly that lists only external interfaces, and say so in the mapping. |

## Partial fits: native field for part of the case, property for the rest

| Profile attribute | CycloneDX 1.7 location | Why only partial |
|---|---|---|
| `moduleValidationScheme` | `algorithmProperties.certificationLevel` on each algorithm | Per algorithm, not per module. Its enum covers FIPS 140-1/2/3 levels and CC EAL, not ISO/IEC 19790 or national approval (`other`). It also puts FIPS and CC in one list, the conflation decision 0022 separated. Use it where it fits; the property stays authoritative. |
| `lifecycleStage` | `metadata.lifecycles[].phase` | Document-level only. The Keycloak document mixes `implemented` and `configured`, which a single phase cannot say. Phases also differ in kind (`post-build`, `operations`, `discovery`). Use when uniform; keep the per-interface property. |
| `externalDependencies` | External `services` (the CA, the directory, the identity provider) with `tags` from the profile's vocabulary, and `dependsOn` edges | Native and more informative, and heavier: the producer declares services it does not operate. Reasonable for an extended-depth document. |
| `roadmapRef` | `externalReferences[type="issue-tracker"]` or `"release-notes"` | Loses the per-purpose key. Usable only where one reference covers the interface. |

## No native home

These stay `pkic:profile:` properties. Most are exactly what the methodology adds that CycloneDX
does not model.

- **The edge and its roles:** `interfaceType`, `endpointRole:*`. The edge gap the mapping
  already names.
- **Service-level protocol identity:** `protocol`, `protocolVersion` on services. `service.version`
  is the service's version, not its protocol's. The endpoint URL scheme gives a hint only.
- **Explicit absence:** `keyExchange`, `encryption`, `authentication` with value `none` (K3), and
  the `unknown` and `withheld` markers.
- **Capability and roadmap:** the `capabilityByPurpose` group (`capabilityStatus`, `blockedBy`,
  `validatedModeAvailability`), `enablementMethod`, `minimumProductVersion`, `coexistence`,
  `negotiationControl`, `integrationConstraints`, `enablementSetting`. CycloneDX records what
  is; Q26 is precisely whether a CBOM should record what will be. `declarations.claims` could
  in principle carry supplier commitments, but they are built for attestation against standards
  and would be a stretch.
- **Capability of key management:** `keyTypesSupported`, `keyStoreFormatsSupported`,
  `keyOperations` (`cryptoFunctions` is per algorithm, not per surface), `keyManagementFunction`,
  `keyStoreLocation`, `keyStoreRef`.
- **Everything with no TLS-style native list:** `protocolVersionsSupported` everywhere, and
  `keyExchangeSupported`/`authenticationSupported` for services and non-TLS protocols.
- **Product certification scheme:** a reference could go in `externalReferences`; the scheme
  itself has no field.

## Effect on the example

Moving the first table removes about 125 of the 575 properties, most of them the TLS supported-group and signature-scheme lists. About 200 of what remains is
the capability group: seven purposes per interface, two to four values each. That is the
irreducible part. Only a CycloneDX change would move it.

## Consequences

- **The mapping draft changes.** The first table becomes the mapping; the second is stated with
  its limits.
- **Two conventions are needed** and belong in the mapping: `cipherSuites` means supported and
  `cryptoRefArray` means in use; and `securedBy.mechanism: "none"` for an unwrapped key.
- **The adapter changes** accordingly. Deferred with the rest of the tooling.
- **Candidate feedback to CycloneDX,** in the same spirit as the `cprofile` feedback:
  - an `interfaceType` and endpoint-role model, which is the edge gap;
  - a way to carry protocol identity on a service;
  - a supported/in-use distinction on `cryptoRefArray` that works beyond TLS;
  - `iso-19790` and national approval in `certificationLevel`, with module validation kept apart
    from product evaluation.
