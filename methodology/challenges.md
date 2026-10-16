---
title: Challenges
sideMenu: true
weight: 4
aliases:
- /cbom/methodology/challenges.html
linkTitle: Challenges
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

CBOMs inherit the benefits and the limitations of software bills of materials, and introduce further difficulties specific to cryptography. These constraints are the primary motivation for a profile-based, format-independent methodology.

The items below are observations of the position at the time of writing, not permanent properties of the formats. Both CycloneDX and SPDX are under active development and several of these points are already being addressed: CycloneDX 1.7 introduced the Cryptography Registry, and SPDX is adding a cryptographic object model. Readers should check the current status of each specification. A profile methodology that stays independent of any one format remains useful as the formats change. When a format changes, the mapping is revised and the profile stays the same.

## Lessons from SBOM adoption

Three properties have consistently distinguished successful SBOM deployments from difficult ones. Each applies equally to CBOMs in a multi-vendor environment.

| Lesson | Problem observed | Implication for CBOMs |
| --- | --- | --- |
| **Harmonization** | A proliferation of vendor-specific formats and delivery methods prevented reconciliation at scale. | Agree how attributes are expressed, rather than mandating one format. A profile states what must be disclosed, and a mapping fixes how each attribute is encoded in each format, so several formats can coexist and still be reconciled. |
| **Profiling** | Listing everything does not make a bill of materials more useful. A large number of entries hides the ones that matter for a given decision. | Define a minimum, purpose-specific subset of attributes for each objective. This is the function of a [profile](../profile/). |
| **Sequencing** | The published minimum elements were read as the most a producer needed to supply, rather than as a floor. Producers met the minimum and stopped, and consumers had no basis for asking for more, because nothing in the minimum said what came next. | A CBOM profile may ask for only part of the information at first and defer the rest. When it does, it has to place an obligation on the deferred part. Otherwise the first stage becomes the permanent answer. A profile could simply state that a deferred subject is out of scope. That costs the producer nothing, but it also tells the consumer nothing. A profile could instead require a one-word status for the deferred subject. That costs the producer almost nothing, and it tells the consumer how far the work has progressed. |
| **Normalization** | Different producers represent the same value differently, which prevents automated processing. | Agree identifiers (syntactic normalization) and attribute meanings (semantic normalization) so that CBOMs can be compared. |

Harmonization is often read as a requirement to adopt a single format. A single format is neither achievable nor necessary. Organizations have existing commitments to CycloneDX or SPDX, regulators and customers ask for different things, and the formats themselves continue to change. What has to be consistent is the information: which attributes are disclosed, and where each one sits in a given document. A profile and its mapping provide that consistency. The profile is written once, independently of any format. A mapping is then defined for each format that the profile needs to support. A consumer can then reconcile CBOMs from several formats, and a producer is not forced to abandon the format it already uses. Consistency is achieved through agreed encoding rather than through a single target format. See [Formats](../formats/).

This is also the position taken by the 2026 minimum elements guidance, which states that minimum support for automation means supporting all data formats that are widely used, open source, and compatible with existing formats, and that the set of supported formats should be reassessed periodically. The guidance names both SPDX and CycloneDX. A consumer is therefore expected to handle more than one format. A profile and its mappings are designed for exactly that situation. See [References](../../references/).

Coverage is a separate question from attribute selection, and the two are sometimes confused. The same guidance requires an SBOM to include all components of the target software, including transitive dependencies, and states that there is no minimum depth. That requirement sets a minimum for which components appear in the SBOM and which elements each component carries. A profile does something different. It states which attributes are mandatory for a stated purpose. A profile does not permit a producer to leave components out. The worked example on this site follows this distinction. It evaluates only the interfaces a product declares. It says nothing about the other entries that a production CBOM would contain.

## Challenges specific to CBOMs

In addition to the properties inherited from SBOMs, cryptography introduces difficulties that current standards address only in part. The points below describe the position at the time of writing.

### 1 · No first-class model for relationships (the edge gap)

Current CBOM standards model cryptographic *assets* (algorithms, keys, certificates, protocols) as nodes. They provide no object that represents the *relationship*, meaning the point at which cryptography is applied between two parties. In graph terms, the relationship is an edge that connects two parties. A TLS connection is an example. It is a place where assets are used, not an asset in itself. Some classifiers belong to the connection itself, such as the endpoint roles in a specific session. Because no object exists for the connection, these classifiers are attached to a protocol asset instead. The standards therefore represent the edge as though it were a node.

{{< figure src="../assets/figures/methodology-challenges-1.svg" alt="Two side-by-side panels: assets as nodes, covering algorithms, keys, certificates and protocols, marked as well modelled today, and relationships as edges, marked as having no first-class object" >}}

*The principal modelling gap: standards describe the cryptography a component contains, not the connections in which it is used. See [the relationship model](../model/).*

### 2 · Cryptographic coverage differs between the formats

SPDX 3.0.1 has no dedicated cryptographic model equivalent to the one in CycloneDX, so organizations that standardize on SPDX today usually pair it with a CycloneDX-format CBOM referenced as a linked artifact. This arrangement works. However, it means that CBOM interoperability depends on a single format.

This position is changing. SPDX is adding a cryptographic object model. Once that model is available, linking a CycloneDX CBOM becomes a choice rather than a necessity. In this methodology, the profile does not change when that happens. Only the SPDX column of the mapping changes. Readers should confirm the current state of both specifications rather than relying on the position described here. See [Formats](../formats/).

### 3 · Inconsistent algorithm naming

Deployments have shown the same algorithm expressed in several forms (`AES256`, `AES-256-GCM`, `AES_256_CBC`). This inconsistency makes it harder to enforce policy and to analyse data across organizations. The CycloneDX 1.7 Cryptography Registry provides stable identifiers to address the problem. CBOMs written to earlier versions carry free-text names. A consumer has to normalize those names when it takes the CBOM in. See [Versioning](../versioning/).

### 4 · Multiple valid encodings of the same information

Both CycloneDX and SPDX permit the same cryptographic information to be encoded correctly in more than one way. A given fact (for example an algorithm reference, a protocol version, or the association between a certificate and its signature algorithm) may be represented in different but equally valid locations or structures within a single document. A consumer that must accept any valid encoding has to implement and maintain parsing logic for each variant, which increases complexity and the risk of inconsistent interpretation.

The mapping addresses this problem. It defines a single, canonical encoding for each profile attribute in each format. When producers follow the mapping, a consumer reads each required value from one defined location rather than from several. This reduces parsing complexity and makes interpretation more consistent. Normalizing the encoding complements normalizing the names (item 3). Encoding normalization concerns where and how a value is represented. Naming normalization concerns the value itself. See [Formats](../formats/).

### 5 · Ambiguity of lifecycle and state

The statement that a product uses a given algorithm can mean four different things: the algorithm may be *intended* in the design, *implemented* in the binary, *configured* in a deployment, or *observed* on the wire. A vendor's build-time CBOM and an operator's runtime scan may legitimately differ. Without an explicit lifecycle indicator, a consumer cannot tell whether the product is merely capable of using the algorithm or is actually using it. See [Lifecycle Data](../lifecycle/).

### 6 · Depth of disclosure

Depth of disclosure means how much detail a CBOM is required to report. Excessive reporting reduces the value of the data and may expose intellectual property. Insufficient reporting conceals risk. Consumers need enough detail to act on, and vendors have a legitimate interest in keeping some details confidential. These two needs pull against each other. A well-defined profile sets a minimum, which prevents underreporting. It also limits how much the producer is required to disclose.

Time is a third factor, and it is the one most often missed. At the start, few suppliers can answer everything a mature profile asks for. A profile set at the level that suppliers can produce today will still be set at that level in three years. Depth is therefore a question of how much to ask for now and also of how to ask for more later. The profile has to do this without freezing the current answer and without making the first request impossible to answer. This is the sequencing lesson from SBOM adoption. It is also the reason why a profile that defers a subject should still require the producer to state where that subject stands.

### 7 · Value, withheld, unknown and undeclared are four different outcomes

Most CBOM tooling treats an attribute as either present or missing. That approach merges four situations that a consumer needs to tell apart:

-   The producer holds the information and has supplied it (**value**).
-   The producer holds the information and is **withholding** it under a confidentiality policy.
-   The value is **unknown** to the producer.
-   The attribute is **undeclared**. There is no value and no marker saying which of the other three cases applies.

Each situation calls for a different response from the consumer. An unknown value points to a limitation in the producing process. It may justify better tooling, or it may justify giving the result less weight. A withheld value reflects a policy decision. In that case the consumer knows that the information exists and could be released under other terms, such as a non-disclosure agreement. Reporting both cases as an empty field loses that difference. In procurement, it also misrepresents the supplier. A vendor whose scanner cannot see hardware cryptography is not in the same position as a vendor that has chosen not to publish a library version.

The undeclared case is the one most easily overlooked. In a document that carries no markers at all, it looks the same as an unknown or withheld value. An undeclared attribute means that the producer did not build the document against the profile. The producer never addressed the attribute, so a consumer cannot infer anything about whether the information exists. The 2026 minimum elements guidance requires an SBOM author to state whether missing information is unknown or withheld. The guidance treats this as a practice maintained across the SBOM lifecycle rather than as a single data field. An attribute is undeclared when the author has not made that statement. Neither CycloneDX nor SPDX has a native field for recording these cases, so the mapping has to define a convention. The [Conformance](../conformance/) page sets out the four outcomes and how each one affects the verdict, which is the result of evaluating a CBOM against a profile. That page makes it a MUST for any evaluation tool to distinguish the four outcomes. The withheld case also relates to redaction, which is described in the [Inventory](../inventory/) section. Redaction deliberately reduces a CBOM that is extracted for an external party.

### 8 · Tooling coverage and confidence

Automated tools may fail to detect cryptography that is dynamically loaded, configuration-driven, or provided by hardware. A CBOM can be no more reliable than the process that produces it. Provenance is therefore important, and so is signing where it is feasible. The confidence that a consumer can place in a CBOM also depends on the lifecycle phase at which the CBOM was captured.

### 9 · Linking cryptography to its environment

Knowing that a system uses a given algorithm is not enough on its own. A consumer also needs the version of the library that implements the algorithm. The library version determines whether modes such as hybrid key exchange are available. A consumer also needs to know whether the algorithm runs in software, in a Hardware Security Module, or in a Trusted Execution Environment. Cryptography in a Trusted Execution Environment may require hardware replacement rather than a software update. For these reasons, CBOMs are produced and consumed alongside SBOMs, and in some cases alongside Hardware Bills of Materials. The links between these artifacts are not yet mature.

### 10 · Versioning and legacy artifacts

Standards are revised (CycloneDX 1.6 to 1.7), profiles are tightened, and a product's CBOM is regenerated over time. A CBOM can therefore be "older" in three separate senses: the version of the standard, the version of the profile, and the generation of the product's CBOM. Treating "older" as a single concept produces incorrect verdicts, meaning incorrect results when a CBOM is evaluated against a profile. Each of the three version axes must be handled explicitly. See [Versioning](../versioning/).

### 11 · Identifying the same asset across different tools

An inventory is assembled from several sources: a vendor CBOM, a build-time scan, and a runtime discovery tool. Each names things in its own way, and for some classes of asset there is no agreed name at all. Sometimes nobody can show whether two records describe the same asset. The inventory then either counts one asset twice or merges two distinct assets into one. The process that builds the inventory does not report either error.

The difficulty varies between asset classes. Some classes have an established identifier, and producers only need to use it. Other classes have no identifier.

| Asset class | Identity available today | Assessment |
| --- | --- | --- |
| **Software components** | Package URL, and formerly CPE | Workable. Baseline rule I9 already requires the `pkg:` form for the implementing library. |
| **Certificates** | SHA-256 fingerprint of the DER encoding, or issuer and serial number | Workable, though tools disagree on which of the two to use, so a consumer may hold two records of one certificate. |
| **Keys** | No agreed identifier | The hard case. A public key can be thumbprinted. A private key held in a hardware module has only a local label or handle. When the same key material is present in a module and in a backup, the two records are genuinely ambiguous. |
| **Algorithms** | Registry identifiers, of which several compete | An open question, and the subject of item 3 above. |
| **Interfaces** | `interfaceId`, chosen by the producer and unconstrained by design | Undefined across documents. Nothing connects an interface record in one document to an interface record in another. |

The position for interfaces results from a deliberate decision. The profile does not constrain `interfaceId`, so that profiles remain independent of any product's internal naming. The cost of that independence is that the identifier has no meaning outside the document that contains it. A consumer should treat it as a label rather than as a stable cross-organization identifier. See [Formats](../formats/).

Matching records that describe the same asset is called correlation. Correlation has to work across tools and also across time. An inventory may be unable to determine whether today's record describes the same interface as last quarter's record. Such an inventory cannot report migration progress, which is one of the stated use cases. The same requirement applies to any attempt to link several CBOMs into a picture of a deployment, because the links are expressed between identified assets. The [Inventory](../inventory/) page describes what an inventory does about these problems. It chooses a join key for each asset class, records the basis for each merge, and constructs a stable key for interfaces. This page classifies the problem, and the Inventory page sets out the practice.

The profile mechanism provides a partial remedy. A profile can require a particular identifier form. Baseline rule I9 does this by requiring a `pkg:` Package URL for the implementing library. More generally, identity requirements belong in the profile. A profile intended to feed an inventory states which identifier form it requires for each asset class it covers. The identity problem has no general solution, but this approach turns it into a decision that is made once for each profile. As with the other items here, this describes the position at the time of writing. Identifier schemes may yet be defined for the classes that lack one.

These challenges reduce to a small number of requirements that a profile methodology is designed to satisfy. The methodology has to set limits on the information that must be disclosed (profiling). It has to establish how the information is encoded and what the disclosed values mean (normalization of encoding and of naming). It also has to represent lifecycle state and cryptographic relationships explicitly. The formats continue to develop, so the methodology is deliberately kept separate from them. When a specification adds capability, the mapping is updated and the profile is unchanged.

[← Demo](../demo/) [Next: Inventory →](../inventory/)
