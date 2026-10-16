---
title: Formats
sideMenu: true
weight: 17
aliases:
- /cbom/methodology/formats.html
linkTitle: Formats
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The profile is defined independently of any format. A mapping locates each attribute, and the interface count, within a concrete document. CycloneDX provides a native cryptographic model. SPDX 3.0.1 does not, so a CBOM is currently expressed in CycloneDX and referenced from an SPDX SBOM. The SPDX community has indicated that a cryptographic object model is planned, so this position is expected to change; the working group has not verified the current state at field level, and the SPDX column below is hedged accordingly.

Because both formats permit the same information to be encoded in more than one valid way, the mapping also normalizes the encoding. It defines a single, canonical location for each attribute. A consumer that relies on the mapping reads each required value from one place. It does not have to handle every valid variant, and this reduces parsing complexity. See [Challenges](../challenges/).

The format comparisons in this section describe the position at the time of writing. Both specifications are being developed actively. When a format gains capability, the mapping is revised and the profile is unaffected. This is the practical benefit of keeping the profile separate from any format.

{{< figure src="../assets/figures/methodology-formats-1.svg" alt="A format-independent Profile box branching down to two panels, CycloneDX 1.7 and SPDX 3.0.1, each listing what that format supports for cryptographic data today" >}}

*The same profile can be satisfied in either format, given a mapping. The areas of strength differ between the two, and both are changing.*

## Two valid encodings of the same fact

The encoding problem is easier to see with a concrete case. Take a single fact from the worked example: the HTTPS interface uses X25519 for key exchange. CycloneDX allows a producer to record this in at least two ways, both correct.

{{< figure src="../assets/figures/methodology-formats-2.svg" alt="One fact in two CycloneDX encodings side by side, X25519 reached through a cipher suite and X25519 in a flat reference list, converging on a single canonical location" >}}

*One fact, two valid CycloneDX encodings. Without an agreed convention, a consumer that reads only one location will report the key exchange as absent when the producer used the other.*

Neither encoding is wrong, and a producer may use both together. A consumer therefore cannot assume that the value is in a single location. The validator in this example reads both locations. Before it evaluates any rule, it merges the cipher-suite algorithm list with the flat reference array. Without this step, the validator could not tell a CBOM that omits the key exchange from a CBOM that records it in the less common location.

The same pattern appears for authentication. A TLS interface usually reaches its signature algorithm through the certificate, using `certificateProperties.signatureAlgorithmRef`. An SSH interface has no certificate, so the host key algorithm is referenced directly by the interface. Both forms satisfy the profile requirement for an authentication algorithm, and a consumer has to handle each. The mapping records which form applies in which case. A consumer then knows what to expect and does not have to find out by experiment.

The mapping therefore does more than locate attributes. It also prevents a type of error in which a CBOM is complete but a consumer reports it as deficient. That error arises only because the producer chose a different valid structure.

## Representation of an interface

An interface, meaning a cryptographic relationship, is represented as a `cryptographic-asset` component with `assetType: protocol`. The profile's model and the format's model do not align at this point.

The format treats the protocol as an asset, in the same category as an algorithm or a certificate. The profile treats the interface as a relationship between endpoints. The mapping bridges the two models. It uses the protocol asset as the carrier for the relationship, meaning the object that holds the relationship's attributes. Those attributes are attached to the protocol asset as properties. CycloneDX supports this today. It has a `cryptographic-asset` component with an `assetType` of `protocol` that can serve as the carrier. SPDX 3.0.1 has neither. For that reason the SPDX column reaches the same attributes through a linked CycloneDX document rather than natively. In both formats, attaching relationship attributes to the carrier is a convention agreed in the mapping. Neither format enforces it as a structure.

This arrangement has several consequences for an implementation:

-   The document does not declare the set of interfaces directly. A consumer derives the set by listing the components with `assetType: protocol` and counting them. Product rules P1 and P2 are evaluated against that derived set, including the count of components carrying `interfaceType = management`.
-   Nothing in the format prevents a protocol asset from being used for something other than an interface. A producer might record a protocol that a product implements in general, even though the protocol does not correspond to a deployed interface. The `interfaceType` property distinguishes an interface from such a general protocol record. For this reason the profile requires `interfaceType` on every interface.
-   An interface is identified by the producer's own `interfaceId`, which the profile does not constrain. Consumers should treat it as a label, not as a stable cross-organization identifier.
-   The algorithms belonging to an interface are reached by reference, through the encodings described above, rather than being contained within it. If a reference is broken or missing, the attribute appears to be absent.
-   Where one deployed interface is described by more than one component, for example when a product and an operator each report the same connection, correlation happens in the inventory rather than in the document. See [Inventory](../inventory/).

A format may later introduce a dedicated object for the relationship. If it does, this part of the mapping changes and the profile's requirements do not.

## Mapping table

| # | Requirement | CycloneDX 1.7 (illustrative) | SPDX 3.0.1 |
| --- | --- | --- | --- |
| P1 | ≥1 interface | count of `assetType:protocol` components carrying `interfaceType` | unresolved |
| P2 | ≥1 `management` | count where `interfaceType==management` | unresolved |
| I1 | protocol | `protocolProperties.type` | via linked CBOM |
| I2 | protocolVersion | `protocolProperties.version` | via linked CBOM |
| I3 | keyExchange | algorithm `primitive=key-agree/kem` | via linked CBOM |
| I4 | encryption | algorithm `primitive=ae` | via linked CBOM |
| I5 | authentication | certificate `signatureAlgorithmRef` or host key | via linked CBOM |
| I6 | endpointRoles | `properties[endpointRole:*]` (no edge model) | unresolved |
| I7 | interfaceType | `properties[interfaceType]` (no native field) | unresolved |
| I8 | lifecycleStage | `properties[lifecycleStage]` | unresolved |
| G1 | capabilityStatus, blockedBy, roadmapRef (per purpose) | `properties[capabilityByPurpose:<purpose>:<attribute>]` | unresolved |
| — | interfaceId (carried, not constrained) | `properties[interfaceId]`, defaulting to `bom-ref` | unresolved |
| I9 | implementationPurl | `purl` on library component | `packageUrl` on a `Package` |

**Seven SPDX entries are unresolved: P1, P2, I6, I7, I8, G1 and `interfaceId`.** I1 to I5 reach their values *via a linked CycloneDX CBOM*, which means the SPDX document references one external artifact. The SPDX document therefore contains one element for the linked CBOM, not one element per interface. As a result, SPDX has no element to which a per-interface annotation could be attached, and no set of elements that could be counted. The entries previously shown in these rows described a structure that the linked-CBOM arrangement does not produce. The options, and the contributor expertise needed to choose between them, are set out in the [mapping document](https://github.com/pkic/cbom/blob/main/docs/methodology/mapping-cyclonedx-spdx.md) and recorded as Q48. Until it is settled, SPDX can carry I1 to I5 only through the linked CBOM, and I9 through `packageUrl`. The product-level rules and the remaining per-interface attributes cannot be expressed in SPDX.

## Interpretation of the columns

In **CycloneDX**, the cryptographic assets (I1–I5 and the provider in I9) are represented in native fields. This is an area where the format is strong. The profile also depends on three interface-level classifiers: `interfaceType` (I7), endpoint roles (I6), and lifecycle stage (I8). These have no native field. They are carried in `component.properties` under the `pkic:profile:` namespace. Product rule P2 can only be evaluated because the `interfaceType` attribute is present.

In **SPDX**, version 3.0.1 has no cryptographic model, so most detail is obtained through the linked CycloneDX CBOM. SPDX is strong on provider identity (I9). It identifies the OpenSSL and OpenSSH packages by `packageUrl`. That value is cross-referenced against vulnerability feeds, as described in [Vulnerabilities](../vulnerabilities/). As SPDX gains a cryptographic object model, entries in this column will move from the linked CBOM to native SPDX fields. The requirement numbers will stay the same. Stable requirement numbers are the reason for expressing the profile independently of the format.

## The edge gap

`interfaceType` and endpoint roles describe the interface itself. In the relationship model, the interface is an edge: the connection between two endpoints. Neither format provides an object that represents the interface. Both formats attach these attributes to the protocol asset instead. This is sufficient for the disclosure baseline. However, it cannot record a finding that belongs to the connection itself. One example is whether a particular session negotiated a key-exchange group that is not post-quantum. The working group's first-class attributed-edge model aims to provide an object for the connection that can carry such findings.

## Normalization

Normalization covers two separate questions: where a value is written in the document, and how the value itself is expressed. Both questions have to be settled before CBOMs from different producers can be compared. The second question, how the value is expressed, causes more difficulty in practice.

The mapping normalizes identity as well as encoding. Naming a canonical location settles where a value is read. It does not establish whether two documents that carry the value describe the same component, certificate, key, or interface. Where an identifier scheme exists the mapping can require it, as requirement I9 does for the implementing library and as the registry does for algorithms. Where no scheme exists, and for the producer-chosen `interfaceId` in particular, a mapping cannot supply an identity the formats do not define. Identity normalization is therefore the harder of the two questions. The remaining work of matching records that describe the same asset is done in the inventory. See [Challenges](../challenges/).

### Why it matters

Every automated use of a CBOM depends on matching a value against something, whether a policy, a deprecation list, a vulnerability feed, or the same attribute in another CBOM. Those matches are exact. A value that means the right thing but is written differently will not match, and nothing in the process reports an error. A policy engine looking for AES-256-GCM that encounters `AES256` finds no match, and depending on how the rule is written it treats the interface either as compliant or as having no encryption at all. Both results are incorrect, and both look like ordinary output.

The problem grows with the size of the estate. A single supplier using an unusual spelling can be handled by hand. The same variance across many suppliers and a large number of interfaces makes estate-wide questions impractical to answer, such as how many interfaces still use a deprecated algorithm, or which services an advisory affects. Inconsistent naming seen in real deployments is the reason the registry was introduced.

### What the registry solves

CycloneDX 1.7 introduces the Cryptography Registry, which assigns stable identifiers to algorithm families and their parameters. Elliptic curve names show the problem clearly. The same curve is commonly written three ways, depending on which standards body or library the producer follows:

| As written by the producer | Origin | Refers to |
| --- | --- | --- |
| `P-256` | NIST | The same curve. The three strings have no form in common, so a text comparison treats them as unrelated. |
| `secp256r1` | SECG |
| `prime256v1` | ANSI, used by OpenSSL |

Compared as text, these are three distinct values. Compared as registry identifiers, they are one value. Symmetric algorithms raise a related difficulty: `AES256`, `AES-256-GCM`, and `AES_256_GCM` may or may not denote the same thing, because the first omits the mode that the others state. The registry also separates the algorithm from its parameters, so a query for deprecated key sizes does not depend on parsing a name.

For requirements I3, I4, and I5 a registry identifier is preferred wherever one exists. CBOMs written to version 1.6 carry free-text names. The adapter normalizes these names using a versioned name map, so that rules only ever see canonical values. See [Versioning](../versioning/).

### Protocols need normalizing too

Algorithm naming receives most of the attention, but protocol identity presents the same difficulty. The protocol and its version are recorded as free text in `protocolProperties`, and producers write them inconsistently: `TLS`, `tls`, and `TLSv1.3`; a version given as `1.3`, `TLS 1.3`, or `0x0304`; SSH as `2.0` or `SSH-2.0`. Some protocols have more than one accepted name, such as MACsec and IEEE 802.1AE.

There are several practical reasons to normalize protocol names and versions.

-   Profiles gate on protocol version. A rule requiring TLS 1.2 or higher has to compare versions, and comparison needs a defined ordering. Strings do not provide one: `1.10` sorts before `1.9` as text, and `TLSv1.3` does not parse as a number at all.
-   Deprecation is expressed per protocol version. Guidance withdraws TLS 1.0 and 1.1, not TLS generally, so a policy cannot be applied unless the version is canonical.
-   The protocol determines which algorithm roles exist. TLS authenticates with a certificate signature, SSH with a host key, IPsec through IKE negotiation. A consumer that misreads the protocol looks for the wrong attribute and reports it as missing, as the authentication case above illustrates.
-   Aggregation depends on it. Counting how many interfaces across an estate still run a given protocol version is a routine migration question, and it cannot be answered by grouping on inconsistent strings.
-   Sector vocabularies differ. The same interface may be named by a 3GPP reference point in one document and by its IETF protocol in another. Without a canonical protocol identity these do not reconcile.

The mapping therefore specifies the expected form for protocol type and version, and the adapter normalizes what it receives before any rule is evaluated. Where a registry provides protocol identifiers, those are preferred for the same reasons they are preferred for algorithms.

[← Method](../method/) [Next: Data Exposure →](../data-exposure/)
