# Profile-to-format mapping: CycloneDX and SPDX (nginx example)

> **Draft, 27 September 2026 (decision 0022, K7).** Changed from the published version in
> seven places: "Representation of an interface", rows I1 to I5 and I9 of the per-interface
> table, new sections on native locations, inheritance and document-level references, a
> section on attributes added by the migration family, and rows P1 and P2. Nothing else
> differs. Native fields are preferred wherever the
> CycloneDX field records the same fact at a derivable granularity with a sufficient value set
> (review in `mapping-native-fields-review.md`).

> **Status:** Illustrative, and describing the position at the time of writing. Both
> specifications are under active development, so the format columns should be checked against
> the current releases. Aligned to CycloneDX 1.7 / ECMA-424 (2nd Edition) and SPDX 3.0.1
> as understood at the time of writing. CycloneDX crypto field names are illustrative and
> should be validated against the current schema. CycloneDX 1.7 introduces the Cryptography
> Registry (stable algorithm identifiers); for I3, I4, and I5 a registry identifier is
> preferred where present, while version 1.6 CBOMs carry free-text names normalized at the
> adapter (see `versioning-and-legacy-cboms.md`).

## Purpose of a mapping

The profile (`profile-interface-disclosure.md`) is defined in format-independent and
product-independent terms. It contains two kinds of rule:

- **Product-level (cardinality)** — for example, the requirement that a product declare at
  least one interface, and that at least one of them be a `management` interface. These rules
  constrain the set of interfaces.
- **Per-interface** — an attribute set that every declared interface must carry.

A mapping locates each of these within a concrete document. The same profile can be satisfied
by a CycloneDX CBOM, an SPDX document, or a future format, provided that a mapping exists.

Three considerations shape the mapping:

1. CycloneDX provides a native cryptographic object model: `cryptographic-asset` components
   with `cryptoProperties`. Most asset attributes correspond to first-class fields.
2. SPDX 3.0.1 provides no dedicated cryptographic object model. Common practice is to express
   the CBOM in CycloneDX and reference it from the SPDX SBOM as an external artifact. SPDX is
   adding a cryptographic object model, so this position is expected to change; when it does,
   the SPDX column below is revised and the profile is unaffected.
3. Neither format provides a first-class object representing the cryptographic relationship
   (the edge). Relationship-level attributes are carried in properties or annotations.

## Representation of an interface

An interface maps to one of two CycloneDX objects, according to its layer.

- **A security protocol instance** (TLS, SSH, IPsec, IKE, QUIC, DTLS) is a
  `cryptographic-asset` component with `assetType: protocol`. The protocol type is one of
  CycloneDX's enumerated security protocols. The component describes the security protocol
  only: TLS on port 8443, not "the HTTPS listener".
- **Every application protocol is a CycloneDX `service`**, HTTPS included: HTTP over TLS is an
  HTTP service that depends on a TLS component. OIDC token issuance, SAML, an administrative
  API, JDBC, LDAP, SMTP and plain HTTP are services too, and so is a key store the product writes
  to. CycloneDX has no protocol type for any of them, and representing them as protocol
  components with type `other` loses the name and misstates what they are.

**Layering is carried by the dependency graph.** A service lists, in its `dependencies` entry,
what carries it, if anything, and the algorithm and key components it uses itself. OIDC token
issuance depends on the HTTPS service, and the HTTPS service depends on the TLS component. A service with no carrying protocol, such as plain HTTP, has no transport protection,
and the document shows it structurally. A library that implements a protocol says so with
`provides`.

**Which services are interfaces.** A service is an interface when it applies cryptography of its
own (it signs, verifies, encrypts or decrypts content), or when it is reachable without any
transport protection. A service that only rides a declared protocol, and applies nothing of its
own, may be declared for completeness and is not an interface: the protocol component that
carries it already is. Without this test, interface counts and the coverage statement would
vary with how thoroughly a producer lists its services.

**How a reader tells them apart.** A service that is an interface carries the interface
attributes (`pkic:profile:interfaceType` and the rest). A service declared only for its layering
carries none of them, only `pkic:profile:protocol` and `pkic:profile:protocolVersion`.

The product-level rules are evaluated by enumerating protocol components and services that carry
`interfaceType`, and counting them,
including the number that carry `interfaceType = management`. There is no native object
representing the set of interfaces; the count is derived.

## Per-interface attribute mapping

| # | Profile attribute (abstract) | CycloneDX 1.7 location (illustrative) | SPDX 3.0.1 location |
|---|---|---|---|
| I1 | `protocol` | Protocol component: `protocolProperties.type` (`tls`, `ssh`, etc.). Service: `service.properties[name="pkic:profile:protocol"]` (for example `OIDC`, `SAML`, `HTTP`) | via linked CycloneDX CBOM |
| I2 | `protocolVersion` | Protocol component: `protocolProperties.version`. Service: `service.properties[name="pkic:profile:protocolVersion"]` | via linked CycloneDX CBOM |
| I3 | `keyExchange` | Algorithm component (`primitive = key-agree`/`kem`) referenced by the protocol's `cryptoRefArray`, or listed in the service's `dependsOn`. Where none applies, the property `pkic:profile:keyExchange` with value `none` | via linked CycloneDX CBOM |
| I4 | `encryption` | Algorithm component (`primitive = ae`) referenced or depended on as above, or the property with value `none` | via linked CycloneDX CBOM |
| I5 | `authentication` | `certificateProperties.signatureAlgorithmRef` (TLS), a referenced signature algorithm or host key (SSH), or for a service the signature algorithm in its `dependsOn` (for example RS256 for OIDC tokens); or the property with value `none` | via linked CycloneDX CBOM |
| I6 | `endpointRoles` | `component.properties[name="pkic:profile:endpointRole:*"]` (no edge/endpoint model) | **unresolved** — see below |
| I7 | `interfaceType` | `component.properties[name="pkic:profile:interfaceType"]` (no native field) | **unresolved** — see below |
| I8 | `lifecycleStage` | `component.properties[name="pkic:profile:lifecycleStage"]` (flat lifecycle tag, per lifecycle model v1) | **unresolved** — see below |
| I9 | `implementationPurl` | `purl` of the library component whose `dependencies[].provides` lists the interface (protocol component or service). No property | SPDX `Package` with `packageUrl` |

### Group attributes

Capability is stated per cryptographic purpose (rule `pqc-migration#G1`), which needs a repeated group rather
than a single value. CycloneDX properties are flat name/value pairs, so the group is carried in
the name, following the `endpointRole:<role>` convention already in use:

    pkic:profile:capabilityByPurpose:<purpose>:<attribute>

For example `pkic:profile:capabilityByPurpose:entity-authentication:blockedBy`. Three segments
after the prefix is what marks a group entry, so a reader needs no knowledge of which profile
declares which groups. A disclosure marker on a group attribute takes the same shape with the
marker prefix in front.

Note what the group is *not* mapped to. CycloneDX `cryptoFunctions` records operations —
`sign`, `verify`, `encrypt` — and a purpose is not an operation: one `sign`/`verify` covers both
a certificate signature and a firmware signature, which migrate a decade apart. Reusing that
field would lose the distinction the group exists to carry.

The SPDX column for these rows is **unresolved** for the same reason as the rest of the
per-interface attributes: see above.

## Native locations

These attributes are carried by CycloneDX fields and not by properties. A consumer derives the
attribute from the field.

| Profile attribute | CycloneDX 1.7 location | Convention |
|---|---|---|
| interface identity | `bom-ref` of the protocol component or service | No `interfaceId` property. References to an interface, such as `keyStoreRef`, use the `bom-ref` |
| `implementationPurl` | `dependencies[].provides` from a library component with `purl` | One library provides each interface |
| `providerLocation` | `algorithmProperties.executionEnvironment` of the algorithms the interface references or depends on | `software-plain-ram` and `software-encrypted-ram` → `software`; `software-tee` → `tee`; `hardware` → `hsm`. A property is used only where the interface references no algorithm |
| `keyExchangeSupported`, `authenticationSupported` (TLS) | `protocolProperties.cipherSuites[].tlsGroups` and `.tlsSignatureSchemes`, as IANA names | `cipherSuites` lists the **supported** set; `cryptoRefArray` lists what is **in use**. Suites carry no `algorithms` references, so the two cannot mix. Other protocols and services keep properties |
| `keyTypes` | `related-crypto-material` components the service depends on: the name of each one's `algorithmRef` | Size, state and dates come with the component |
| `keyStoreFormats` | `relatedCryptoMaterialProperties.format` of those components, lower-cased | Values from the profile's vocabulary |
| `keyWrapping` | `relatedCryptoMaterialProperties.securedBy` of the keys a storage interface depends on | `mechanism: "none"` states an unwrapped key (K3). Otherwise the name of `securedBy.algorithmRef` |
| `moduleValidationRef` | `externalReferences[type="certification-report"]` on the implementing library | — |
| `coverage` (`all`, `partial`) | `compositions[]` with `aggregate` `complete` or `incomplete` over an `assemblies` list of the interfaces | `all-external` has no CycloneDX value and stays a property beside a `complete` composition |

Two locations are used alongside a property, not instead of it. `certificationLevel` on
algorithms may state the validation (`none`, `fips140-3-l1`, ...), but it has no value for
ISO/IEC 19790 or national approval, so `moduleValidationScheme` stays authoritative.
`metadata.lifecycles` may state the phase when every interface shares it; `lifecycleStage` stays
per interface.

## Inheritance from the providing library (K9)

The library component that `provides` an interface may carry, as `pkic:profile:` properties, the
implementation facts listed in pqc-migration's `$commentInheritance`: `moduleValidationScheme`,
`moduleValidationRef`, `providerLocation`, `enablementMethod`, `minimumProductVersion`,
`coexistence` and `capabilityByPurpose` entries. The interface inherits them and carries only the
values that differ. For the capability group, an interface's entry for a purpose replaces the
library's entry for that purpose.

**Shared TLS configurations.** A TLS configuration used by several interfaces is one protocol
component with `cipherSuites` and no `interfaceType`, so it is not an interface. Each TLS
interface references it from `protocolProperties.relatedCryptographicAssets` with
`type: "protocol-configuration"`. CycloneDX attaches `tlsGroups` and `tlsSignatureSchemes` to
each suite, so they still repeat inside the shared component. In TLS 1.3 both are negotiated
independently of the suite, and a protocol-level location would remove the repetition. That is
candidate feedback to CycloneDX.

## Document-level references (K10)

A CBOM links to what it does not restate.

| What | CycloneDX 1.7 location | Convention |
|---|---|---|
| Companion SBOM | `externalReferences[type="bom"]` at document level, with `hashes` | The SBOM of the same subject. Only its reference and hash appear here |
| A library's SBOM entry | `externalReferences[type="bom"]` on the library component, as a BOM-Link (`urn:cdx:<serial>/<version>#<bom-ref>`) | Replaces a copied SBOM `bom-ref` property |
| Vulnerability statements | `externalReferences[type="vulnerability-assertion"]` for a VEX or equivalent; `type="advisories"` for an advisories page | Joined, not merged (decision 0020) |
| Who produced the document, and what it describes | `metadata.tools`, `metadata.supplier`; `metadata.component.supplier`, `.manufacturer`, `.licenses` | Native fields; no properties |

None of these is required by a rule in the family. They are what makes a conforming document
usable beside the SBOM and the vulnerability feed it will be read with.

## Attributes added by the migration family

The remaining attributes that interface-disclosure v0.8, pqc-migration v0.7 and
pqc-migration-extended v0.1 add have no native CycloneDX field. Each is carried as
`pkic:profile:<attribute>` on the protocol component or service, with list-valued attributes as
repeated properties of the same name: `moduleValidationScheme`, `keyWrappingSupported`,
`keyManagementFunction`, `keyOperations`, `keyTypesSupported`, `keyStoreFormatsSupported`,
`keyStoreLocation`, `keyStoreRef`, `externalDependencies`, `enablementSetting`. The capability
group member `validatedModeAvailability` follows the group convention above. The product
attribute `productCertificationScheme` is a property on `metadata.component`. `keyStoreRef`
names the `bom-ref` of the managing interface, or one of the literals `out-of-band`,
`product-managed` and `none`.

A service can also carry `data` entries (flow and classification) and a `trustZone`. The
data-exposure attributes, such as `confidentialityLifetime`, would sit naturally there. They are
not required by any profile in this family, and are parked until a deployment-scope profile
needs them.

## Product-level rule mapping

| # | Product rule | CycloneDX | SPDX |
|---|---|---|---|
| P1 | At least one interface declared | count of protocol components and services **carrying `interfaceType`** | **unresolved** — see below |
| P2 | At least one `management` interface | count of those whose `pkic:profile:interfaceType == management` | **unresolved** — see below |

### The unresolved SPDX rows

The rows above are marked unresolved rather than filled in, because the entries they previously
carried do not compose with the rest of the column. I1 to I5 are satisfied *via a linked
CycloneDX CBOM*: the SPDX document references one external artifact. There is therefore one SPDX
element, not one per interface — so there is nothing for a per-interface annotation to attach to,
and no set of elements to count. The earlier entries (`Annotation` on linked element, *count of
linked elements annotated `interfaceType=management`*) described a structure the linkage
arrangement does not produce, and never named the SPDX element class involved.

Three ways out were visible: represent each interface as its own SPDX element and link the CBOM
per interface; carry the interface-level classifiers as SPDX annotations on the single reference
element, encoded so that several interfaces can be distinguished within it; or accept that
product-level rules cannot be evaluated from the SPDX side at all and say so.

**Decision 0016 takes the third, and the rows above stay unresolved deliberately.** The first two
would have this group invent something inside a format it does not own — a modelling convention
SPDX has not adopted, or an encoding inside an extension point — producing documents only our tools
can read. That is the fragmentation this methodology exists to prevent, arriving under the banner
of format independence.

What changed is where the limitation is written down. A conformance claim now carries
`evaluableFromCarrier`, which for SPDX in this arrangement sets `productRules: false`, and each
kind of rule that is not evaluable adds a line to the claim's `notAsserted` list. So the bound is
visible to the person deciding whether to accept a submission, rather than only to whoever reads
this document. A prose caveat here is read by people implementing the mapping; a field in the claim
is read by the person the misunderstanding would otherwise cost.

The honest summary stands: the claim that one profile can be expressed in two formats holds for the
per-interface attributes and not for the product-level rules. If SPDX's cryptographic modelling
grows a structure carrying interfaces as distinct elements, decision 0016 is superseded and
`CARRIER_CAPABILITY` in the validator is the single table that changes. Settling *that* still needs
a contributor who works with SPDX 3.x at field level.

## Interpretation of the columns

In CycloneDX, the cryptographic assets (I1–I5 and the provider in I9) are represented in
native fields, which is an area of strength for the format. The profile also depends on
interface-level classifiers: `interfaceType` (I7), endpoint roles (I6), and lifecycle stage
(I8). These have no native field and are carried in `component.properties` under the
`pkic:profile:` namespace. The `interfaceType` attribute makes product rule P2
evaluable; without an agreed means of indicating which interface is the management interface, a
profile cannot require that one exist.

In SPDX, the absence of a cryptographic object model in 3.0.1 means that most detail is
obtained through the linked CycloneDX CBOM. The area of strength for SPDX is provider identity
(I9): it identifies the OpenSSL and OpenSSH packages by `packageUrl`, which is the value
cross-referenced against vulnerability feeds. As SPDX gains a cryptographic object model,
entries in this column move from the linked CBOM to native SPDX fields while the requirement
numbers stay the same.

## Disclosure markers

The profile distinguishes an attribute that is unknown to the producer from one the producer is
withholding, following the 2026 SBOM minimum elements. Neither format has a native field for this,
so the convention is fixed here:

| State | CycloneDX | SPDX |
|---|---|---|
| unknown | `component.properties[name="pkic:profile:disclosure:<attribute>"]` with value `unknown` | `Annotation` on the linked element |
| withheld | the same property with value `withheld` | `Annotation` on the linked element |

The marker replaces the attribute rather than accompanying it. A producer supplying a value does
not also supply a marker, and a consumer reads the marker only where the value is absent. Silent
omission remains distinguishable, because it produces neither.

## The edge gap

`interfaceType` and `endpointRoles` both describe the interface itself (the edge), yet neither
format provides an object that represents the interface. CycloneDX attaches these classifiers
to the protocol asset (representing the edge as a node); SPDX approximates them with
relationships and annotations. This is sufficient for the disclosure baseline, but it cannot
represent a determination that belongs to the connection itself. Providing such an object is
the objective of the working group's first-class attributed-edge model.
