# Profile-to-format mapping: CycloneDX and SPDX (Keycloak example)

> **Status:** Illustrative. Part of the consolidated baseline of 25 October 2026 (decision 0025).
> The target carrier is **CycloneDX 2.0**, pinned to `CycloneDX/specification` branch `2.0-dev`,
> commit `76f185c` (23 October 2026). Ecma is expected to ratify the release in December 2026.
> The pinned schema is in `tests/schemas/cyclonedx-2.0/` in the repository. When 2.0 is
> released, the working group replaces the schema, regenerates the examples and revises any
> location that moved.
>
> The validator still reads **CycloneDX 1.6 and 1.7** documents and flags them as legacy,
> because the tools that produce CBOMs today emit 1.x. The legacy column records where a 1.x
> document carries each fact. `cdx17_to_20.py` converts a 1.6 or 1.7 CBOM to 2.0, and its
> docstring lists every conversion. The SPDX column is aligned to SPDX 3.0.1 and keeps its
> stated gaps. SPDX 3 is not a target carrier.
>
> The reference for every location is the way `validate_cbom.py` reads a document (the
> functions `document_parts`, `identities`, `extract_product` and `extract_interfaces`) and the
> example files in `examples/`. Where the two disagree with a mapping table, the code and
> the examples are right and the table is wrong.

## Purpose of a mapping

A PKIC CBOM profile (`profile-interface-disclosure.md`) is defined in format-independent and
product-independent terms. It contains four kinds of rule:

- **Document-level rules (P)** constrain the set of cryptographic interfaces and the facts about
  the subject. For example, a document must declare at least one cryptographic interface, and
  it must declare a management interface or state why it has none.
- **Per-interface rules (I)** name an attribute set that every declared cryptographic interface
  must carry.
- **Group rules (G)** require one entry per cryptographic purpose on an interface.
- **Reference rules (R)** require a pointer to context that the document does not carry, such as
  the companion SBOM or the place where vulnerability statements are published.

A mapping locates each of these within a concrete document. The same profile can be satisfied
by a CycloneDX CBOM, an SPDX document, or a future format, provided that a mapping exists.

Four considerations shape the mapping:

1. CycloneDX provides a native cryptographic object model: `cryptographic-asset` components
   with `cryptoProperties`. Most asset attributes correspond to first-class fields.
2. SPDX 3.0.1 provides no dedicated cryptographic object model. Common practice is to express
   the CBOM in CycloneDX and reference it from the SPDX SBOM as an external artifact. SPDX is
   adding a cryptographic object model. When it does, the working group revises the SPDX column
   and the profiles are unaffected.
3. Neither format provides a first-class object representing the cryptographic relationship
   (the edge). Relationship-level attributes are carried in properties.
4. CycloneDX 2.0 uses two of our words for its own concepts. Its root `profiles` element holds
   reusable data and threat characterisations, and its blueprint model defines an `interface`
   with types such as `rest` and `cli`. Neither is the concept the PKIC CBOM profiles use. We write **"PKIC CBOM profile"**
   and **"cryptographic interface"** wherever the CycloneDX concept could be meant
   (decision 0021).

## Where the parts of a document sit

CycloneDX 2.0 moved the subject and the services. A reader finds the parts of a document as
follows.

| Part | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) |
|---|---|---|
| Format name | `specFormat: "CycloneDX"` | `bomFormat: "CycloneDX"` |
| The subject the document describes | `inventories[0].subject` | `metadata.component` |
| Components, cryptographic assets and services | `inventories[0].components[]`, nested components included | `components[]`, nested components included |
| Services | components with `type: "service"` in the same list | a separate `services[]` list |
| Package URL of a component or the subject | `identifiers[]`: an entry names the asserting `party` and lists `identities` with `scheme: "purl"` | `purl` |
| Supplier and manufacturer of a component | `parties[]` on the component, each with a role (`supplier`, `manufacturer`) | `supplier`, `manufacturer` |
| Who asserts the identifiers | a party with role `author` in the subject's `parties[]`, referenced by `bom-ref` | not expressed |
| A note for human readers | a top-level `$comment` (valid in 2.0) | property `pkic:example:comment` in `metadata.properties` |

The validator reads only the first inventory. A document with more than one inventory is read,
and the other inventories are not evaluated.

## Representation of a cryptographic interface

A cryptographic interface maps to one of two CycloneDX objects, according to its layer.

- **A security protocol instance** (TLS, SSH, IPsec, IKE, QUIC, DTLS) is a
  `cryptographic-asset` component with `assetType: protocol`. The protocol type is one of
  CycloneDX's enumerated security protocols. The component describes the security protocol
  only. In the Keycloak example, `crypto:protocol:tls-https` is TLS on port 8443, not "the HTTPS
  listener".
- **Every application protocol is a service**, HTTPS included. HTTP over TLS is an HTTP service
  that depends on a TLS component. OIDC token issuance, SAML, the Admin REST API, JDBC, LDAP,
  SMTP and plain HTTP are services too. So is a key store the product writes to, such as
  Keycloak's realm key persistence in its database. CycloneDX has no protocol type for any of
  them. Representing them as protocol components with type `other` loses the name and misstates
  what they are. In CycloneDX 2.0 a service is a component with `type: "service"`. In 1.x it is
  an entry in `services[]`.

**The dependency graph carries layering.** A service lists, in its `dependencies` entry, what
carries it, if anything, and the algorithm and key components it uses itself. In the Keycloak
example, OIDC token issuance depends on the HTTPS service, and the HTTPS service depends on the
TLS component. Plain HTTP has no carrying protocol, so the document shows structurally that it
has no transport protection. A library that implements an interface says so with
`dependencies[].provides`. The graph has the same shape in 2.0 and 1.x.

**Which services are cryptographic interfaces.** A service is a cryptographic interface when it
applies cryptography of its own (it signs, verifies, encrypts or decrypts content), or when it
is reachable without any transport protection. A service that only rides a declared protocol,
and applies nothing of its own, may be declared for completeness. It is not an interface,
because the protocol component that carries it already is one. Without this test, interface
counts and the coverage statement would vary with how thoroughly a producer lists its services.
In the Keycloak example, OIDC, SAML, the Admin API, brokered token verification and plain HTTP
are interfaces. HTTPS, JDBC, LDAP, SMTP and JGroups only ride TLS, so they are declared for
layering and are not interfaces.

**How a reader tells them apart.** A component that is a cryptographic interface carries the
property `pkic:profile:interfaceType`. A service declared only for its layering carries none of
the interface attributes, only `pkic:profile:protocol` and `pkic:profile:protocolVersion`.

The validator enumerates the components that carry `interfaceType` and counts them. There is no
native object for the set of interfaces, so the count is derived.

## Document-level rule mapping

Rule ids are local to the profile that declares them. `interface-disclosure#P1` is the
baseline's P1, and `procurement#P5` is the procurement profile's P5.

| Rule | What it requires | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) | SPDX 3.0.1 |
|---|---|---|---|---|
| interface-disclosure#P1 | At least one cryptographic interface | count of components in `inventories[0].components[]` that carry `pkic:profile:interfaceType` | the same count over `components[]` and `services[]` | **unresolved**, see [The unresolved SPDX rows](#the-unresolved-spdx-rows) |
| interface-disclosure#P2 | A management interface, or a stated reason for none | count of those with `interfaceType = management`; otherwise the subject property `pkic:profile:managementInterfaceAbsence` with a value from `managementAbsenceVocabulary`. At `observed`, a management interface declared in a cited configured record also satisfies it, and the reason `not-reached` is accepted only with coverage `partial` | the same, with the subject property on `metadata.component` | **unresolved** |
| interface-disclosure#P3 | The subject's identifier: a package URL for a product, a tag URI (RFC 4151) for a deployment | product: `inventories[0].subject.identifiers[].identities[]` with `scheme: "purl"`. Deployment: an identity with the custom scheme `{"name": "tag-uri", "description": "A tag URI (RFC 4151)."}` and a value such as `tag:example.org,2026:deployment/sso-prod` | product: `metadata.component.purl`. Deployment: property `pkic:profile:subjectIdentifier` on `metadata.component` | **unresolved** |
| interface-disclosure#P4 | Coverage: `all`, `all-external` or `partial` | subject property `pkic:profile:coverage`; or `compositions[]` with `kind: "components"`, `targets` naming the inventory's `bom-ref`, and `aggregate` `complete` (read as `all`) or `incomplete` (read as `partial`). `all-external` has no CycloneDX value and is always the property | the property; or `compositions[]` with `aggregate` over an `assemblies` list of the interfaces | **unresolved** |
| interface-disclosure#P5 | The document declares its subject type (`product` or `deployment`) | subject property `pkic:profile:subjectType` | property on `metadata.component` | **unresolved** |
| interface-disclosure#P6 | One lifecycle stage per document | `metadata.lifecycles[].phase`: `build` → implemented, `operations` → configured, `discovery` → observed, `design` → intended. A per-interface `pkic:profile:lifecycleStage`, where present, must agree | `metadata.lifecycles[].phase`, the same values | **unresolved** |
| deployment-disclosure#P1 | Cites the documents the record builds on, each by BOM-Link and SHA-256 | `externalReferences[]` at document level with `type: "bom"`, property `pkic:profile:context = cited-document`, `url` a BOM-Link `urn:cdx:<serial>/<version>`, and `hashes` with SHA-256. See [Joins across documents](#joins-across-documents) | the same | not mapped |
| pqc-migration#P1 | At least one implementing library identified (SHOULD) | count of `type: "library"` components with a package URL in `identifiers[]` | count of `library` components with `purl` | **unresolved** |
| pqc-migration-extended#P1 and procurement#P5 | A storage interface, or a stated reason for none | count of interfaces with `interfaceType = storage`; otherwise the subject property `pkic:profile:storageInterfaceAbsence` | the same, on `metadata.component` | **unresolved** |
| pqc-migration-extended#P2 | Product certification scheme (SHOULD) | `inventories[0].subject.certifications[]`: the first entry's `standard`. The validator reads "Common Criteria" (or "ISO/IEC 15408") as `common-criteria` and "EUCC" as `eucc`; any other text is read lower-cased and must be a value of `productCertificationVocabulary`. `none` is the subject property `pkic:profile:productCertificationScheme`, because `certifications[]` cannot state an absence | property `pkic:profile:productCertificationScheme` on `metadata.component` | **unresolved** |
| procurement#P6 | Coverage is `all` or `all-external` | as interface-disclosure#P4, with the narrower vocabulary | as interface-disclosure#P4 | **unresolved** |

The Keycloak product record states coverage `all-external` as a property beside a `complete`
composition. The observed deployment record states `partial`.

## Per-interface attribute mapping

| # | Attribute | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) | SPDX 3.0.1 |
|---|---|---|---|---|
| I1 | `protocol` | protocol component: `protocolProperties.type` (`tls`, `ssh`, etc.). Service: property `pkic:profile:protocol` (for example `OIDC`, `SAML`, `HTTP`) | the same | via linked CycloneDX CBOM |
| I2 | `protocolVersion` | protocol component: `protocolProperties.version`. Service: property `pkic:profile:protocolVersion` | the same | via linked CycloneDX CBOM |
| I3 | `keyExchange` | the algorithm components with `primitive` `key-agree` or `kem` among the protocol's `protocolProperties.relatedCryptographicAssets`, or among a service's `dependsOn`. Otherwise the property `pkic:profile:keyExchange` with a literal | the same algorithms reached through `protocolProperties.cryptoRefArray`, or through a service's `dependsOn` | via linked CycloneDX CBOM |
| I4 | `encryption` | algorithm components with `primitive: "ae"` reached as for I3, or the property `pkic:profile:encryption` with a literal | as for I3 | via linked CycloneDX CBOM |
| I5 | `authentication` | a signature algorithm reached as for I3, or through a certificate component's `certificateProperties.relatedCryptographicAssets`. A service names its token signature algorithm in `dependsOn` (RS256 for Keycloak's OIDC tokens). Otherwise the property `pkic:profile:authentication` with a literal | as for I3, or through `certificateProperties.signatureAlgorithmRef` | via linked CycloneDX CBOM |
| I6 | `endpointRoles` | properties `pkic:profile:endpointRole:<role>` (no edge or endpoint model) | the same | **unresolved** |
| I7 | `interfaceType` | property `pkic:profile:interfaceType` (no native field) | the same | **unresolved** |
| I8 | `lifecycleStage` | taken from the document's stage (P6). A property `pkic:profile:lifecycleStage` is optional and must agree | the same | **unresolved** |
| I9 | `implementationPurl` | the package URL, in `identifiers[]`, of the library component whose `dependencies[].provides` lists the interface. No property. Withholdable in the baseline | the library's `purl` | `Package` with `packageUrl` |
| I10 | `keyWrapping` (storage interfaces) | `relatedCryptoMaterialProperties.securedBy` of the keys the storage service depends on. `mechanism: "none"` states an unwrapped key. Otherwise the names of the algorithms in `securedBy.algorithmRef`, which is an array in 2.0 | `securedBy.algorithmRef` as a single string | via linked CycloneDX CBOM |
| I11 | `defaultState` (SHOULD, at `implemented`) | property `pkic:profile:defaultState`: `enabled` or `disabled` | the same | **unresolved** |
| deployment-disclosure#I1 | `correspondsTo` | property `pkic:profile:correspondsTo`: a BOM-Link `urn:cdx:<serial>/<version>#<bom-ref>`, or the literal `no-product-document` | the same | not mapped |
| deployment-disclosure#I2 | `observationMethod` (at `observed`) | property `pkic:profile:observationMethod`, such as `active-probe`, `passive-sensor`, `endpoint-query` or `inspection`. A list is written as repeated properties | the same | not mapped |
| deployment-disclosure#I3 | `observedAt` (at `observed`) | property `pkic:profile:observedAt`, an ISO 8601 interval such as `2026-10-18T00:00:00Z/2026-10-25T00:00:00Z` | the same | not mapped |

An interface is identified by its `bom-ref`. There is no `interfaceId` property in the examples.
References to an interface, such as `keyStoreRef` and `correspondsTo`, use the `bom-ref`.

### Literal values for I3 to I5

Where no algorithm component applies, the producer writes the attribute as a property with one
literal value. A literal stands alone; it is never mixed with algorithm names.

| Literal | Meaning | Accepted at |
|---|---|---|
| `none` | No algorithm does this job, for example Keycloak's token encryption, which is off by default | every stage |
| `deployment-defined` | The product does not fix the value; the operator chooses it, for example the server certificate on Keycloak's HTTPS listener | `implemented` only |
| `peer-defined` | The other endpoint decides, or the value is negotiated with it, for example on the connection Keycloak opens to its database | `implemented` only |

A `deployment-defined` value requires a configuration-guidance pointer on the same interface
(`interface-disclosure#R5`). The Keycloak HTTPS listener points to
`https://www.keycloak.org/server/enabletls`. At `configured` and `observed` the deployment record
states the value itself. `cbom-keycloak-deployment-configured-fail-literal.cdx.json` keeps
`peer-defined` at `configured` and fails I3, I4 and I5 on the database connection.

## Supported and in use

CycloneDX lists two different sets on a protocol component, and the mapping reads them
differently.

- **In use:** `protocolProperties.relatedCryptographicAssets` lists the algorithms the interface
  uses. Only entries that point to algorithm components count. In 1.x the same set is
  `cryptoRefArray`, which CycloneDX 2.0 removed.
- **Supported:** `protocolProperties.cipherSuites[]` lists what the interface can offer. The
  validator reads `cipherSuites[].tlsGroups` as `keyExchangeSupported` and
  `cipherSuites[].tlsSignatureSchemes` as `authenticationSupported`, as IANA names. These feed
  the pqc-migration rules I2 and I3. Suites carry no algorithm references, so the two sets
  cannot mix.

**Shared TLS configurations.** A TLS configuration that several interfaces use is one protocol
component with `cipherSuites` and no `interfaceType`, so it is not an interface. Each TLS
interface references it from `relatedCryptographicAssets` with `type: "protocol-configuration"`.
The validator follows that reference for the supported set and ignores it for the in-use set.
In the Keycloak example, `crypto:protocol:cfg-jdk21-tls-defaults` holds what the JDK 21 in the
image offers, with X25519 first. CycloneDX attaches `tlsGroups` and `tlsSignatureSchemes` to each
suite, so they still repeat inside the shared component. In TLS 1.3 both are negotiated
independently of the suite, and a protocol-level location would remove the repetition. That is
candidate feedback to CycloneDX.

Services and other protocols have no `cipherSuites`. They declare the supported sets as repeated
properties `pkic:profile:keyExchangeSupported` and `pkic:profile:authenticationSupported`.

## Native locations

The following attributes are carried by CycloneDX fields and not by properties. The validator
derives the attribute from the field.

| Attribute | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) | Convention |
|---|---|---|---|
| interface identity | `bom-ref` of the protocol component or service | the same | No `interfaceId` property |
| `implementationPurl` | `dependencies[].provides` from a library component with a package URL in `identifiers[]` | the same, with `purl` | One library provides each interface |
| `providerLocation` | `algorithmProperties.executionEnvironment` of the algorithms the interface uses | the same | `software-plain-ram` and `software-encrypted-ram` → `software`; `software-tee` → `tee`; `hardware` → `hsm`. A property is used only where the interface uses no algorithm |
| `keyExchangeSupported`, `authenticationSupported` (TLS) | `cipherSuites[].tlsGroups`, `.tlsSignatureSchemes` | the same | See [Supported and in use](#supported-and-in-use) |
| `keyTypes` | `related-crypto-material` components the service depends on: the algorithm each one names in `relatedCryptoMaterialProperties.relatedCryptographicAssets` | the same, through `relatedCryptoMaterialProperties.algorithmRef` | Size, state and dates come with the component |
| `keyStoreFormats` | `relatedCryptoMaterialProperties.format` of those components, lower-cased | the same | Values from the profile's vocabulary |
| `keyWrapping` | `securedBy` of the keys a storage interface depends on | the same, with a single `algorithmRef` | See I10 |
| `moduleValidationScheme`, `moduleValidationRef` | `certifications[]` on the implementing library | property `pkic:profile:moduleValidationScheme`, and `externalReferences[type="certification-report"]` on the library | See [Certifications](#certifications) |
| `productCertificationScheme` | `certifications[]` on `inventories[0].subject` | property on `metadata.component` | See pqc-migration-extended#P2 |
| `coverage` (`all`, `partial`) | `compositions[]` with `aggregate` `complete` or `incomplete`, targeting the inventory | `compositions[]` over an `assemblies` list | `all-external` stays a property |
| document stage | `metadata.lifecycles[].phase` | the same | See P6 |

Two fields changed shape in 2.0 without changing meaning. `algorithmProperties.curve` became
`ellipticCurve`, an enumerated value such as `other/Curve25519`. `implementationPlatform` became
an array. `algorithmProperties.certificationLevel` is gone; module validation moved to
`certifications[]`.

## Certifications

CycloneDX 2.0 has a native `certifications[]` array on any component. Each entry names a
`standard` and may carry an `identifier`, an `issuer`, dates and a `url`. The mapping uses it for
two different facts, on two different objects.

- **Module validation** sits on the library that implements the interface. The validator reads
  the first entry's `standard` as `moduleValidationScheme`: `FIPS 140-3` → `fips-140-3`,
  `FIPS 140-2` → `fips-140-2`, `ISO/IEC 19790` → `iso-19790`. It reads `url`, or failing that
  `identifier`, as `moduleValidationRef`. The interface inherits both from the library (K9). The
  value `none` stays a property, because an empty array is not a statement.
- **Product certification** sits on the subject. Common Criteria and EUCC evaluate a product
  against a protection profile, which is a different object from a cryptographic module, so the
  two facts are never mixed in one attribute.

In 1.x the same facts are properties: `pkic:profile:moduleValidationScheme` with a
`certification-report` external reference on the library, and
`pkic:profile:productCertificationScheme` on the subject. The converter turns a library's
property and report into a `certifications[]` entry. In the Keycloak example the JDK states
`moduleValidationScheme = none` and the product states `productCertificationScheme = none`, so
neither record carries a `certifications[]` entry.

## Inheritance from the providing library (K9)

The library component that `provides` an interface may carry implementation facts as
`pkic:profile:` properties: `moduleValidationScheme`, `moduleValidationRef`, `providerLocation`,
`enablementMethod`, `minimumProductVersion`, `coexistence` and `capabilityByPurpose` entries. In
2.0, module validation may come from the library's `certifications[]` instead. The interface
inherits these facts and states only the values that differ. For the capability group, an
interface's entry for a purpose replaces the library's entry for that purpose.

In the Keycloak example, `lib:openjdk` provides all seven TLS interfaces. It states key
establishment as `planned`, blocked by the provider, with roadmap JEP 527. Every TLS interface
inherits that entry.

Inheritance across documents is narrower. Only `implementationPurl` follows a `correspondsTo`
join from a deployment record to the record it realises. See
[Joins across documents](#joins-across-documents).

## Group attributes

Capability is stated per cryptographic purpose (rule `pqc-migration#G1`), which needs a repeated
group rather than a single value. CycloneDX properties are flat name and value pairs, so the
group is carried in the name, following the `endpointRole:<role>` convention:

    pkic:profile:capabilityByPurpose:<purpose>:<attribute>

For example `pkic:profile:capabilityByPurpose:entity-authentication:blockedBy`. Three segments
after the prefix mark a group entry, so a reader needs no knowledge of which profile declares
which groups. A disclosure marker on a group attribute takes the same shape, with the marker
prefix in front. The location is the same in 2.0 and 1.x.

The per-purpose `roadmapRef` stays a group attribute holding a URL. Keycloak's ML-DSA token
signing is `committed`, blocked by the standard, with `roadmapRef`
`https://github.com/keycloak/keycloak/issues/43690`.

The group is not mapped to CycloneDX `cryptoFunctions`. That field records operations such as
`sign`, `verify` and `encrypt`, and a purpose is not an operation. One `sign`/`verify` covers
both a certificate signature and a firmware signature, which migrate a decade apart. Reusing
that field would lose the distinction the group exists to carry. CycloneDX 2.0 adds `agility`,
which describes how a component's configuration changes. It does not state what each purpose
can do or what blocks it, so the group still has no native field.

The SPDX column for the group is **unresolved**, for the same reason as the other per-interface
classifiers.

## Attributes with no native field

The remaining attributes of the family have no native CycloneDX field in 2.0 or 1.x. Each is
carried as `pkic:profile:<attribute>` on the protocol component or service. List-valued
attributes are repeated properties of the same name. They are `protocolVersionsSupported`,
`enablementMethod`, `minimumProductVersion`, `coexistence`, `negotiationControl`,
`integrationConstraints`, `keyWrappingSupported`, `keyManagementFunction`, `keyOperations`,
`keyTypesSupported`, `keyStoreFormatsSupported`, `keyStoreLocation`, `keyStoreRef`,
`externalDependencies` and `enablementSetting`. The capability group member
`validatedModeAvailability` follows the group convention. `keyStoreRef` names the `bom-ref` of
the managing interface, or one of the literals `out-of-band`, `product-managed` and `none`.

CycloneDX 2.0 adds `rotation` on keys and `renewal` on certificates. They describe how a key or
certificate is replaced. No rule in the family reads them yet.

CycloneDX 1.x let a service carry `data` entries and a `trustZone`. CycloneDX 2.0 removed both
from the service, and the converter drops them. The operator's data facts, such as data
classification and confidentiality lifetime, now live in a data register that a deployment
record points to (`deployment-disclosure#R3`, context kind `data-register`).

## Joins across documents

One document describes one subject at one stage. The vendor writes the product record
(`implemented`). The operator writes deployment records (`configured`, `observed`). The records
are joined, not merged (decision 0025, generalising decision 0020).

| What | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) | Convention |
|---|---|---|---|
| Cited document | `externalReferences[]` at document level: `type: "bom"`, property `pkic:profile:context = cited-document`, `url` `urn:cdx:<serial>/<version>`, `hashes` with SHA-256 | the same | Required by `deployment-disclosure#P1` |
| Interface realised | property `pkic:profile:correspondsTo` = `urn:cdx:<serial>/<version>#<bom-ref>`, or `no-product-document` | the same | Required by `deployment-disclosure#I1` |

When the evaluator is given a cited document (`--with`), it checks the serial number, the version
and the hash. A changed revision fails `deployment-disclosure#P1`.
`cbom-keycloak-deployment-observed-fail-P1.cdx.json` shows this case. When the cited document is
not supplied, the validator checks the citation for form only. It reports an inherited value as
unresolved, not as failed.

Only implementation facts follow a join, and today that is `implementationPurl`. Present-state
facts never do: each stage reports its own. The Keycloak observed record follows the library
through two joins, from observed to configured and from configured to the product record. The
readiness gap is computed from the join by a policy and is never stored in a record.

## Reference rules and context pointers

A reference rule requires a pointer to an artefact that the document does not carry. Each
PKIC CBOM profile defines `contextKinds`. For each kind it names the CycloneDX
`externalReferences` types that can carry it, and its form:

- `document`: a fixed artefact, bound by a hash;
- `endpoint`: a feed or API whose content changes, which names its access protocol;
- `document-or-endpoint`: either.

| Part of a pointer | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) |
|---|---|---|
| The pointer | an entry in `externalReferences[]`, at document level or on the interface the rule names | the same |
| Its kind | property `pkic:profile:context` on the reference, naming the kind. Reference types are shared between kinds, so the type alone does not say which kind is meant | the same |
| Access protocol (endpoints) | property `pkic:profile:accessProtocol`: `web-page`, `csaf-provider`, `osv-api`, `ghsa-api`, `vex-document` or `other` | the same |
| Binding (documents) | `hashes[]` on the reference | the same |
| Stated absence | subject property `pkic:profile:contextAbsent:<kind>` with a value from `contextAbsenceVocabulary` (`not-published`, `not-applicable-to-subject`), where the rule accepts one | the same, on `metadata.component` |
| Withheld | property `pkic:profile:disclosure:<kind>` = `withheld`, where the rule permits it | the same |

| Rule | Kind | Carrier types | Form |
|---|---|---|---|
| interface-disclosure#R1 (MUST, product) | `sbom` | `bom` | document |
| interface-disclosure#R2 (MUST, product) | `vulnerability-statements` | `vulnerability-assertion`, `exploitability-statement` | document or endpoint; or the absence `not-published` |
| interface-disclosure#R3 (SHOULD, product) | `advisories` | `advisories` | endpoint |
| interface-disclosure#R4 (SHOULD, product) | `security-contact` | `security-contact`, `rfc-9116` | endpoint |
| interface-disclosure#R5 (MUST on an interface where I3 to I5 is `deployment-defined`) | `configuration-guidance` | `documentation`, `configuration` | endpoint |
| interface-disclosure#R6 (MAY) | `design-intent` | `threat-model`, `adversary-model`, `documentation` | document or endpoint |
| deployment-disclosure#R1 (MUST, at `configured`) | `configuration-source` | `configuration`, `codified-infrastructure`, `vcs` | document or endpoint |
| deployment-disclosure#R2 (SHOULD, at `observed`, withholdable) | `observation-evidence` | `evidence`, `runtime-analysis-report`, `log` | document |
| deployment-disclosure#R3 (SHOULD, withholdable) | `data-register` | `risk-assessment`, `other` | document or endpoint |
| deployment-disclosure#R4 (MAY) | `issuer-policy` | `documentation` | endpoint |
| pqc-migration#R1 (SHOULD) | `support-lifecycle` | `support`, `release-notes`, `documentation` | endpoint; or a stated absence |

The Keycloak product record points to its companion SBOM by BOM-Link and hash. It points to two
advisory sources: the GitHub advisories page (`web-page`) and the OSV API (`osv-api`). It points
to the security policy as its security contact. Upstream Keycloak publishes no VEX, so the record
states `contextAbsent:vulnerability-statements = not-published`.

**Conformance checks the pointer, never the target.** The validator checks that the pointer
exists, that its type is a carrier for the kind, that a document has a hash and that an endpoint
names a protocol from the vocabulary. It does not fetch the target.

**Direction follows time.** A record points to artefacts that exist when it is written, such as
the SBOM, a configuration revision or evidence. It also points to the places where later
statements will appear, such as a VEX feed or an advisory API. Judgements made afterwards, such as
conformance claims and policy results, point to the record by digest. A record never points to
them.

## Other document-level references

| What | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 (legacy) | Convention |
|---|---|---|---|
| A library's SBOM entry | `externalReferences[type="bom"]` on the library component, as a BOM-Link `urn:cdx:<serial>/<version>#<bom-ref>` | the same | No property |
| Who produced the document | `metadata.tools`, `metadata.supplier` | the same | Native fields |
| Supplier, manufacturer and licence of the subject | `inventories[0].subject.parties[]` with roles; `inventories[0].subject.licenses` | `metadata.component.supplier`, `.manufacturer`, `.licenses` | Native fields; no properties |

No rule requires these entries. They make a conforming document usable beside the SBOM it will
be read with.

## What the mapping does not use

- **`risks`.** CycloneDX 2.0 adds a root risk register with status, owner, responses and target
  dates. These are judgements, not product facts. The validator ignores `risks` for
  conformance, and a supplier's product record should not contain them (decisions 0002 and
  0007).
- **CycloneDX `profiles`.** These hold reusable data and threat characterisations. They are not
  PKIC CBOM profiles.
- **CycloneDX perspectives.** A perspective lists JSONPath expressions into a document, each
  marked required, recommended or optional. It cannot express conditions, vocabularies, groups,
  withholding or extension. Each PKIC CBOM profile publishes a perspective generated from its
  rules (`perspectives/`), as an informative companion. The rules file stays normative.
- **The blueprint model.** Its `interface`, zones, boundaries and flows describe a deployed system
  for threat analysis. Its protocols are free text and its encryption flag is a boolean. It does
  not describe a cryptographic interface. See [The edge gap](#the-edge-gap).

## The unresolved SPDX rows

The SPDX rows marked unresolved stay unresolved, because the entries they once carried do not
compose with the rest of the column. I1 to I5 are satisfied *via a linked CycloneDX CBOM*: the
SPDX document references one external artifact. There is therefore one SPDX element, not one per
interface. A per-interface annotation has nothing to attach to, and there is no set of elements
to count. The earlier entries (`Annotation` on linked element, *count of linked elements
annotated `interfaceType=management`*) described a structure the linkage arrangement does not
produce, and never named the SPDX element class involved.

Three ways out were visible:

1. represent each interface as its own SPDX element and link the CBOM per interface;
2. carry the interface-level classifiers as SPDX annotations on the single reference element,
   encoded so that several interfaces can be distinguished within it;
3. accept that product-level rules cannot be evaluated from the SPDX side, and say so.

**Decision 0016 takes the third, and the rows stay unresolved deliberately.** The first two would
have the working group invent something inside a format it does not own: a modelling convention
SPDX has not adopted, or an encoding inside an extension point. The result would be documents
that only our tools can read. That is the fragmentation the methodology exists to prevent.

The limitation is written into the conformance claim. A claim carries `evaluableFromCarrier`.
For SPDX in this arrangement it sets `productRules: false`, and each kind of rule that is not
evaluable adds a line to the claim's `notAsserted` list. So the person who decides whether to
accept a submission sees the bound, not only the person who implements the mapping.

The rows added since decision 0016 are marked **not mapped**: the deployment profile's citations,
`correspondsTo` and observation attributes, and the reference rules. SPDX 3 is not a target
carrier, so the working group has not mapped them.

The summary stands. The claim that one PKIC CBOM profile can be expressed in two formats holds
for the per-interface attributes and not for the document-level rules. If SPDX's cryptographic
modelling grows a structure that carries interfaces as distinct elements, decision 0016 is
superseded, and `CARRIER_CAPABILITY` in the validator is the single table that changes. Settling
that still needs a contributor who works with SPDX 3.x at field level.

## Interpretation of the columns

In CycloneDX, the cryptographic assets (I1 to I5, I10 and the provider in I9) are represented
in native fields, which is an area of strength for the format. CycloneDX 2.0 adds native homes
for module validation and product certification. The family also depends on interface-level
classifiers: `interfaceType` (I7), endpoint roles (I6) and the subject type (P5). These have no
native field and are carried as properties under the `pkic:profile:` namespace. The
`interfaceType` attribute makes rule P2 evaluable. Without an agreed way to say which interface
is the management interface, a profile cannot require that one exist. The document stage (P6)
moved to the native `metadata.lifecycles`.

The 2.0 and legacy columns hold the same facts in different places. The validator reads both and
produces the same abstract record, so every rule is written once. The legacy Keycloak product
record (`examples/legacy/cbom-keycloak-product-1.7.cdx.json`) receives the same verdicts as the
2.0 record, and the report flags it as legacy.

In SPDX, the absence of a cryptographic object model in 3.0.1 means that most detail comes
through the linked CycloneDX CBOM. The area of strength for SPDX is provider identity (I9). It
identifies the implementing library by `packageUrl`, which is the value a consumer
cross-references against vulnerability feeds. For Keycloak, the consumer queries the OSV API with
the library package URLs. As SPDX gains a cryptographic object model, entries in its column move
from the linked CBOM to native SPDX fields, and the requirement numbers stay the same.

## Disclosure markers

A PKIC CBOM profile distinguishes an attribute that is unknown to the producer from one the
producer is withholding, following the 2026 SBOM minimum elements. Neither format has a native
field for this, so the mapping fixes the convention:

| State | CycloneDX 2.0 and 1.6 / 1.7 | SPDX |
|---|---|---|
| unknown | property `pkic:profile:disclosure:<attribute>` with value `unknown` | `Annotation` on the linked element |
| withheld | the same property with value `withheld` | `Annotation` on the linked element |

The marker replaces the attribute rather than accompanying it. A producer that supplies a value
does not also supply a marker, and a consumer reads the marker only where the value is absent.
Silent omission remains distinguishable, because it produces neither.
`cbom-keycloak-product-disclosure-states.cdx.json` shows all four outcomes: a withheld library
(permitted), an unknown authentication algorithm and an undeclared encryption algorithm (both
fail), and a value disclosed normally.

## The edge gap

`interfaceType` and `endpointRoles` both describe the interface itself (the edge), yet neither
format provides an object that represents it. CycloneDX attaches these classifiers to the
protocol component or service, so it represents the edge as a node. SPDX approximates them with
relationships and annotations. This is enough for the disclosure baseline. It cannot represent a
determination that belongs to the connection itself, such as which group a given session
negotiated. CycloneDX 2.0 does not close the gap: its blueprint flows have a source and a
destination, but they describe a deployed system for threat analysis. Providing such an object is
the objective of the working group's first-class attributed-edge model.
