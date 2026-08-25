# Profile-to-format mapping: CycloneDX and SPDX (nginx example)

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

An interface (cryptographic relationship) is represented as a `cryptographic-asset` component
with `assetType: protocol`. The product-level rules are evaluated by enumerating those
components and counting them, including the number that carry `interfaceType = management`.
There is no native object representing the set of interfaces; the count is derived.

## Per-interface attribute mapping

| # | Profile attribute (abstract) | CycloneDX 1.7 location (illustrative) | SPDX 3.0.1 location |
|---|---|---|---|
| I1 | `protocol` | `protocolProperties.type` (`tls`, `ssh`, etc.) | via linked CycloneDX CBOM |
| I2 | `protocolVersion` | `protocolProperties.version` | via linked CycloneDX CBOM |
| I3 | `keyExchange` | algorithm component (`primitive = key-agree`/`kem`) referenced by the interface | via linked CycloneDX CBOM |
| I4 | `encryption` | algorithm component (`primitive = ae`) referenced by the interface | via linked CycloneDX CBOM |
| I5 | `authentication` | `certificateProperties.signatureAlgorithmRef` (TLS) or a referenced signature algorithm / host key (SSH) | via linked CycloneDX CBOM |
| I6 | `endpointRoles` | `component.properties[name="pkic:profile:endpointRole:*"]` (no edge/endpoint model) | **unresolved** — see below |
| I7 | `interfaceType` | `component.properties[name="pkic:profile:interfaceType"]` (no native field) | **unresolved** — see below |
| I8 | `lifecycleStage` | `component.properties[name="pkic:profile:lifecycleStage"]` (flat lifecycle tag, per lifecycle model v1) | **unresolved** — see below |
| I9 | `implementationPurl` | `purl` on the library component | SPDX `Package` with `packageUrl` |

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

## Product-level rule mapping

| # | Product rule | CycloneDX | SPDX |
|---|---|---|---|
| P1 | At least one interface declared | count of `cryptographic-asset` components with `assetType: protocol` **carrying `interfaceType`** | **unresolved** — see below |
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
