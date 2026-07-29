# Profile-to-format mapping: CycloneDX and SPDX (nginx example)

> **Status:** Illustrative. Aligned to CycloneDX 1.7 / ECMA-424 (2nd Edition) and SPDX 3.0.1
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

1. CycloneDX provides a native cryptographic object model — `cryptographic-asset` components
   with `cryptoProperties`. Most asset attributes correspond to first-class fields.
2. SPDX 3.0.1 provides no dedicated cryptographic object model. Common practice is to express
   the CBOM in CycloneDX and reference it from the SPDX SBOM as an external artifact.
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
| I4 | `encryption` | algorithm component (`primitive = ae`/`aead`) referenced by the interface | via linked CycloneDX CBOM |
| I5 | `authentication` | `certificateProperties.signatureAlgorithmRef` (TLS) or a referenced signature algorithm / host key (SSH) | via linked CycloneDX CBOM |
| I6 | `endpointRoles` | `component.properties[name="pkic:profile:endpointRole:*"]` (no edge/endpoint model) | `Relationship` records with annotation (approximate) |
| I7 | `interfaceType` | `component.properties[name="pkic:profile:interfaceType"]` (no native field) | `Annotation` on linked element |
| I8 | `lifecycleStage` | `component.properties[name="pkic:profile:lifecycleStage"]` (flat lifecycle tag, per lifecycle model v1) | `Annotation` on linked element |
| I9 | `implementationPurl` | `purl` on the OpenSSL/OpenSSH SBOM component, or a property | native SPDX `Package` with `packageUrl` (SPDX strength) |

## Product-level rule mapping

| # | Product rule | CycloneDX | SPDX |
|---|---|---|---|
| P1 | At least one interface declared | count of `cryptographic-asset` components with `assetType: protocol` | count of linked interface elements or annotations |
| P2 | At least one `management` interface | count of those whose `pkic:profile:interfaceType == management` | count of linked elements annotated `interfaceType=management` |

## Interpretation of the columns

In CycloneDX, the cryptographic assets (I1–I5 and the provider in I9) are represented in
native fields, which is an area of strength for the format. The interface-level classifiers on
which the profile depends — `interfaceType` (I7), endpoint roles (I6), and lifecycle stage (I8)
— have no native field and are carried in `component.properties` under the
`pkic:profile:` namespace. The `interfaceType` attribute is what makes product rule P2
evaluable; without an agreed means of indicating which interface is the management interface, a
profile cannot require that one exist.

In SPDX, the absence of a cryptographic object model in 3.0.1 means that most detail is
obtained through the linked CycloneDX CBOM. The area of strength for SPDX is provider identity
(I9): it identifies the OpenSSL and OpenSSH packages by `packageUrl`, which is the value
cross-referenced against vulnerability feeds.

## The edge gap

`interfaceType` and `endpointRoles` both describe the interface itself (the edge), yet neither
format provides an object that represents the interface. CycloneDX attaches these classifiers
to the protocol asset (representing the edge as a node); SPDX approximates them with
relationships and annotations. This is sufficient for the disclosure baseline, but it cannot
represent a determination that belongs to the connection itself. Providing such an object is
the objective of the working group's first-class attributed-edge model.
