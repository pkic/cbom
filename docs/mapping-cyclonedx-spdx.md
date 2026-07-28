# Profile → format mapping: CycloneDX and SPDX (nginx example)

> **Status:** Illustrative. Aligned to CycloneDX 1.7 / ECMA-424 (2nd Edition) and SPDX 3.0.1
> as understood at time of writing. CycloneDX crypto field names are *illustrative* and
> should be checked against the live schema. CycloneDX 1.7 adds the Cryptography Registry
> (stable algorithm identifiers) — for I3/I4/I5 prefer a registry id where present; older
> 1.6 CBOMs carry free-text names normalized at the adapter (see `versioning-and-legacy-cboms.md`).

## Why a mapping exists

The profile (`profile-interface-disclosure.md`) is written in **format-independent** and
**product-independent** terms. It has two kinds of rule:

- **Product-level (cardinality)** — e.g. "the product declares at least one interface, and
  at least one of them is a `management` interface." These constrain the *set* of interfaces.
- **Per-interface** — an attribute set every declared interface must carry.

A mapping locates each of these in a concrete document. The same profile can be satisfied by
a CycloneDX CBOM, an SPDX document, or a future format, provided a mapping exists.

Three realities shape it:

1. **CycloneDX has a native cryptographic object model** — `cryptographic-asset` components
   with `cryptoProperties`. Most *asset* attributes map to first-class fields.
2. **SPDX 3.0.1 has no dedicated crypto object model yet.** Common practice is to keep the
   CBOM in CycloneDX and *link* it from the SPDX SBOM as an external artifact.
3. **Neither format has a first-class "cryptographic relationship" (edge).** The
   relationship-level attributes are carried in `properties` / annotations.

## Where "an interface" lives

An interface (cryptographic relationship) is represented as a **`cryptographic-asset`
component with `assetType: protocol`**. The product-level rules are answered by *enumerating*
those components and counting them — including counting how many carry
`interfaceType = management`. There is no native "interface set" object; the count is derived.

## Per-interface attribute mapping

| # | Profile attribute (abstract) | CycloneDX 1.7 location *(illustrative)* | SPDX 3.0.1 location |
|---|---|---|---|
| I1 | `protocol` | `protocolProperties.type` (`tls`, `ssh`, …) | via linked CycloneDX CBOM |
| I2 | `protocolVersion` | `protocolProperties.version` | via linked CycloneDX CBOM |
| I3 | `keyExchange` | algorithm component (`primitive = key-agree`/`kem`) referenced by the interface | via linked CycloneDX CBOM |
| I4 | `encryption` | algorithm component (`primitive = ae`/`aead`) referenced by the interface | via linked CycloneDX CBOM |
| I5 | `authentication` | `certificateProperties.signatureAlgorithmRef` (TLS) **or** a referenced signature algorithm / host key (SSH) | via linked CycloneDX CBOM |
| I6 | `endpointRoles` | `component.properties[name="pkic:profile:endpointRole:*"]` (no edge/endpoint model) | `Relationship` records + annotation (approx.) |
| I7 | `interfaceType` | `component.properties[name="pkic:profile:interfaceType"]` (no native field) | `Annotation` on linked element |
| I8 | `lifecycleStage` | `component.properties[name="pkic:profile:lifecycleStage"]` (flat lifecycle tag, per WG lifecycle model v1) | `Annotation` on linked element |
| I9 | `pqcPosture` | `component.properties[name="pkic:profile:pqcPosture"]` (can be derived from `nistQuantumSecurityLevel`) | `Annotation` on linked element |
| I10 | `implementationPurl` | `purl` on the OpenSSL/OpenSSH SBOM component, or property | native SPDX `Package` + `packageUrl` (SPDX strength) |

## Product-level rule mapping

| # | Product rule | CycloneDX | SPDX |
|---|---|---|---|
| P1 | ≥1 interface declared | count of `cryptographic-asset` components with `assetType: protocol` | count of linked interface elements / annotations |
| P2 | ≥1 `management` interface | count of those whose `pkic:profile:interfaceType == management` | count of linked elements annotated `interfaceType=management` |

## Reading the columns

**CycloneDX.** The cryptographic *assets* (I1–I5, I10 provider) sit on native fields —
CycloneDX's strength. The interface-level classifiers the profile depends on — `interfaceType`
(I7), endpoint roles (I6), lifecycle (I8), PQC posture (I9) — have **no native field** and ride
in `component.properties` under a `pkic:profile:` namespace. Crucially, `interfaceType` is what
makes the product-level rule P2 answerable at all; without an agreed way to say "this interface
is the management one," a profile cannot require that a management interface exist.

**SPDX.** With no crypto object model in 3.0.1, most detail is reached *through the linked
CycloneDX CBOM*. Where SPDX is strong is the provider identity (I10): it already names the
OpenSSL / OpenSSH packages by `packageUrl`, which is what you cross-reference against CVE feeds.

## The edge gap, concretely

`interfaceType` and `endpointRoles` both describe *the interface itself* — the edge — yet
neither format has an object that *is* the interface. CycloneDX pins these classifiers to the
protocol *asset* (treating the edge as a node); SPDX approximates with relationships and
annotations. This works for the disclosure baseline, but it cannot hold a verdict that belongs
to the connection itself. Closing that is the working group's first-class attributed-edge model.
