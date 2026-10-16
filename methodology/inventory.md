---
title: Inventory and CBOMs
sideMenu: true
weight: 5
aliases:
- /cbom/methodology/inventory.html
linkTitle: Inventory
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A CBOM and a cryptographic inventory are related but not the same thing. A CBOM describes one product or system and is exchanged between parties. An inventory is an organization's own record of the cryptography it uses, and it can be built from many CBOMs and other sources.

## How a CBOM and an inventory differ

A **CBOM** is a bill of materials for a single artifact: a structured, machine-readable description of the cryptography that a specific component contains or uses, produced at a defined point in time. It is analogous to a software bill of materials.

A **cryptographic inventory** is an organization-wide record of the cryptography in use across systems, aggregated from many sources and maintained continuously. It supports risk management, compliance, and migration planning across the estate.

| Property | CBOM | Cryptographic inventory |
| --- | --- | --- |
| Scope | a single artifact or component | the whole estate |
| Unit | a document (for example, CycloneDX) | a maintained dataset or register |
| Producer | a build pipeline or a scan of one component | a central function that aggregates many sources |
| Temporal character | point-in-time, versioned revisions | continuously maintained, longitudinal |
| Correlation | describes one component's cryptography | correlates cryptography across components and over time |
| Primary purpose | disclosure and conformance for one component | risk analysis, compliance, and migration planning for the organization |

## How they relate

CBOMs are a primary input to a cryptographic inventory. The inventory is built by normalizing and correlating CBOMs from across the estate, together with data from other sources such as network and configuration discovery. A CBOM describes one component at one point in time; the inventory spans many components and is maintained over time.

{{< figure src="../assets/figures/methodology-inventory-1.svg" alt="Three source boxes, vendor CBOM, build CBOM and runtime or config scan, feeding a normalization step, then the cryptographic inventory, which feeds risk, compliance, migration and supply-chain uses" >}}

*CBOMs and discovery data are normalized and correlated to form the cryptographic inventory, which then supports risk, compliance, migration, and the handling of supply-chain requests.*

## Correlating records from different sources

The normalization step in the diagram above is drawn as a single box, but it is where most of the difficulty lies. Records can arrive from a vendor CBOM, a build-time scan and a runtime discovery tool. These sources describe overlapping sets of things. The inventory therefore has to decide which records describe the same thing. If it decides wrongly, it either counts one asset twice or merges two distinct assets. Neither error is visible in the resulting inventory.

[Challenges](../challenges/#11--identifying-the-same-asset-across-different-tools) explains why identity is hard and how far the problem is solved for each class of asset. The paragraphs that follow describe what an inventory can do about it.

**Decide the join key per asset class, and record which was used.** A join key is the attribute, or set of attributes, used to decide that two records describe the same thing. If an inventory merges records without recording the basis for each merge, nobody can audit the merge later. Nor can anyone correct it when a producer changes its identifier scheme. For example, two records may have been merged on a certificate fingerprint and a third on issuer and serial number. The inventory should record that fact.

**Correlation has to hold across time as well as across tools.** To track migration progress, an inventory compares this quarter's records against last quarter's. If it cannot determine whether two records describe the same interface, it will report changes that did not occur and miss changes that did. Interfaces are where this problem is most severe. The reason is that `interfaceId` is deliberately unconstrained and has no meaning outside the document that contains it. In practice an inventory has to build its own stable key from attributes that do not change: the subject, the protocol, and the endpoint roles. The inventory also has to accept that this key will break if a producer restructures its interfaces.

**A profile turns part of the problem into a procurement requirement.** A profile can require a particular identifier form for each asset class it covers. Baseline rule I9 does this by requiring a `pkg:` Package URL for the implementing library. An organization can specify the identifier forms its suppliers must use. For those asset classes, records then share an identifier, and the organization no longer has a correlation problem. This does not help with asset classes that have no identifier scheme. The remaining correlation work lies with those classes.

## Extracting a CBOM from the inventory

The inventory is a source of CBOMs as well as a destination for them. A CBOM can be extracted from the inventory to serve a specific consumer. That consumer may be internal, such as a security or architecture team that needs a description of the cryptography in a given system, or external, such as a client, an auditor, or a regulator. A common external case is a supply-chain request, where a customer or partner asks the organization for a CBOM covering a product or service it supplies.

An extracted CBOM is a scoped snapshot of the inventory. It is generated for a defined subject, such as a product, a service, or a bounded part of the estate. It is filtered to the content the consumer needs, redacted where confidentiality requires it, marked with its provenance (the inventory revision and the time it was drawn from), and signed where appropriate. See [Governance](../governance/).

{{< figure src="../assets/figures/methodology-inventory-2.svg" alt="The cryptographic inventory feeding an extract and scope step that selects, filters, redacts, signs and timestamps, producing an output CBOM for internal, external client and supply-chain consumers" >}}

*A CBOM is extracted from the inventory for a specific consumer (an internal team, an external client, or a supply-chain request), scoped and redacted as required, and validated against the requesting profile before release.*

A single profile applies in both directions. On input, it validates the CBOMs supplied to the inventory. On output, it validates a CBOM extracted from the inventory before that CBOM is released. A consumer making a supply-chain request can state which profile the returned CBOM must satisfy, and the producer checks the output against that profile before sending it. One set of rules therefore governs both the assembly of the inventory and the disclosures drawn from it.

## The role of profiles

CBOMs produced by different tools and vendors can only be aggregated into a coherent inventory if they are comparable. A [profile](../profile/) defines the attributes each CBOM is required to contain. The profile and the normalization applied at the adapter together ensure that values are expressed consistently. This comparability is a precondition for reliable aggregation. Without it, an inventory assembled from heterogeneous CBOMs cannot be relied upon. The same profile also applies to CBOMs extracted from the inventory, as noted above. See [Challenges](../challenges/) and [Formats](../formats/).

## Distributed and central inventories

An inventory does not have to be a single database. In practice organizations tend to land somewhere between two arrangements, and the choice affects how profiles and normalization are applied.

A **central inventory** holds the collected data in one place. Data is gathered from across the estate, normalized on the way in, and queried centrally. Queries that span the estate are straightforward, and normalization happens once. The cost is that the central store must be kept current, and it can become a bottleneck for teams that own the underlying systems.

A **distributed inventory** leaves the data with the business units, subsidiaries, or regions that own it. Each maintains its own inventory, and estate-wide questions are answered by querying across them or by collecting summaries. This suits organizations where ownership is already devolved, or where data residency or confidentiality rules prevent detail from being pooled. The difficulty is that each participant may normalize differently, so an estate-wide answer is only as good as the agreement between them.

A common middle position is a federated arrangement. Detail stays local, and an agreed subset is published upward for estate-wide reporting. A shared profile is most useful in this arrangement. If every participant validates against the same profile, the published subsets are comparable, even though the underlying inventories are separate and independently run. The profile defines the content that every participant must provide. Each participant applies normalization itself, rather than the centre applying it once. Mergers, acquisitions, and outsourced operations tend to push organizations toward this arrangement whether or not it was planned.

## End-to-end posture across a deployment

A recurring question is how CBOMs can be linked to show the cryptographic posture of a whole transaction path, rather than of one product. A single CBOM cannot show the posture of a path. The inventory has to assemble it.

A CBOM describes the cryptography at one subject's boundary. It does not record what sits on the other side of any of the subject's interfaces, and it cannot do so. The same product is deployed into a different topology at every site. A CBOM that named the product's peers would therefore describe only one deployment. The same constraint, called instance independence, is what keeps a profile applicable to any product: a product CBOM describes the product, not one installation of it.

{{< figure src="../assets/figures/methodology-inventory-3.svg" alt="A four-node transaction path from client through content delivery network and gateway to a service, with three hops. The middle hop is marked classical only and identified as the constraint. A separate bracket shows a signature relationship spanning the whole path. Below, four CBOM documents feed an inventory that holds the topology" >}}

*Each CBOM describes one boundary and cannot see the path. The inventory holds the topology, which is deployment knowledge, and the posture of the path is computed from the two together.*

### What linking requires

Three things are needed, and the methodology currently defines none of them.

-   **Stable identity for the things being linked.** A link is expressed between identified endpoints, and the interface identifier carries no meaning outside its own document. This is the correlation problem described above, and it is the first obstacle.
-   **A topology record.** Something has to state that this product's interface connects to that product's interface. Only the operator knows that, and it changes when the deployment changes rather than when any product changes.
-   **A rule for composing posture along a path.** The posture of the whole path has to be derived from the hops and their cryptography.

### Composition is not simply the weakest hop

For protection in transit, the weakest hop governs. A path is only as protected as its least protected segment. The diagram above shows a path where one classical hop in the middle makes the two strong hops on either side irrelevant. The [Model](../model/) section explains why. It also explains why the weakest-hop rule does not apply to every kind of protection. A cryptographic relationship does not always cover a single hop. Some relationships span several hops, so they overlap along a path instead of dividing it into separate segments. For example, a signature applied by the originator and verified by the service spans every hop at once. The strength of that signature does not depend on the cryptography of any individual hop. A path that is adequately protected in transit may therefore still carry a signature that a quantum computer will be able to forge. For this reason, posture is composed separately for each relationship, and each relationship covers a different extent of the path.

### Where this leaves the methodology

End-to-end posture is therefore something the inventory produces. CBOMs supply the facts about each boundary. The inventory supplies the topology. The inventory then computes the posture of the path and records the date of the computation, in the same way as any other derived judgement described in [Policy Evaluation](../policy-evaluation/). A service or deployment CBOM extracted from the inventory can legitimately include links to other components, because it describes deployed instances rather than a product. [Lifecycle Data](../lifecycle/) distinguishes a product CBOM from a deployment CBOM. That distinction allows deployment CBOMs to carry links while product CBOMs stay independent of any deployment.

It has not been decided whether the methodology should define a topology record itself, or state that topology is out of scope and leave it to inventory tooling. Defining a topology record would extend the methodology beyond describing documents. Leaving it undefined means every organization builds its own, and comparison across an estate remains impracticable.

## Context data that is not itself cryptographic

A cryptographic inventory that records only cryptography is difficult to act on. Knowing that a service negotiates X25519 says nothing about whether that matters. Deciding whether it matters, and how urgently, depends on data that is not cryptographic at all and usually already exists elsewhere in the organization.

| Context | Typical source | What it supports |
| --- | --- | --- |
| Business criticality and service ownership | CMDB, service catalogue | Prioritizing which systems to migrate first, and identifying who is accountable for doing it. |
| Data classification and retention period | Data governance records | Assessing harvest-now-decrypt-later exposure. Data that must stay confidential for decades is more urgent than data that expires next quarter. |
| Regulatory scope and jurisdiction | Compliance register | Determining which deadlines and cryptographic requirements apply to a given system. |
| Deployment topology and network exposure | Network and infrastructure records | Distinguishing an internet-facing interface from one confined to a private segment. |
| Software and hardware composition | SBOM, HBOM, asset register | Establishing whether a change is a library update, a configuration change, or a hardware replacement. An SBOM meeting the 2026 minimum elements also carries the component hash algorithm, which is itself cryptographic data of interest to the inventory. |
| Lifecycle and support status | Asset management, vendor roadmaps | Identifying systems that will never receive a quantum-safe update and must be replaced. |
| Third-party and contractual relationships | Procurement records | Establishing which suppliers to approach, and what they are obliged to provide. |

Two consequences follow. First, the inventory needs stable identifiers so that a cryptographic record can be joined to the corresponding entries in these other systems. Linking to those systems is usually better than copying from them. The inventory should reference the CMDB entry rather than copy its contents, because a copy would drift out of date. Second, this context belongs outside the CBOM. A CBOM describes the cryptography of its subject. Criticality and data classification are properties of the business, and they change on their own schedule. The same reasoning keeps derived evaluations out of the CBOM, as the [Policy Evaluation](../policy-evaluation/) section explains.

## Multiple data sources and lifecycle stage

A cryptographic inventory typically combines CBOM data with runtime discovery data. CBOM data is frequently at the `implemented` or `configured` lifecycle stage. Runtime discovery data is at the `observed` stage. The `lifecycleStage` attribute lets the inventory distinguish what a product is declared to be capable of from what has been observed in use, rather than treating the two as the same. See [Lifecycle Data](../lifecycle/).

## Relationship to SBOM and HBOM inventories

A cryptographic inventory is generally maintained alongside software and, where relevant, hardware inventories. CBOMs are consumed together with SBOMs, and in some cases Hardware Bills of Materials, so that cryptography can be related to the components and hardware that implement it. This relationship determines, for example, whether a change requires a software update or a hardware replacement.

## Foundational considerations for CBOM exchange

Using the inventory as both a source and a destination raises several points that a fuller treatment of this topic should cover:

-   **Subject and scope.** An extracted CBOM should state its subject precisely (for example, a product, a service, or a defined portion of the estate) and the criteria used to select its content.
-   **Provenance and point-in-time.** The inventory changes continuously, so an extracted CBOM is a snapshot. It should record the inventory revision and the time from which it was produced.
-   **Authenticity.** An output CBOM issued to an external party should be signed, so that the recipient can verify its origin and integrity. See [Governance](../governance/).
-   **Redaction and confidentiality.** External disclosure may require redaction. The profile sets the minimum that must be disclosed. The organization's policy decides what is withheld beyond that. Redaction should be recorded rather than performed silently. An attribute removed on release is marked as withheld. The recipient can then see that the information exists and was not disclosed. Without the marker, the recipient might read the missing attribute as a limitation of the producer's tooling. See [Challenges](../challenges/). See also [Confidentiality](../confidentiality/) for how the public and restricted extracts of the same subject must be consistent with each other.
-   **Format and version negotiation.** A consumer may require a particular document format (the carrier format) and version. Two things determine what can be produced and validated: the mapping to that format, and the range of format versions the profile accepts. See [Formats](../formats/) and [Versioning](../versioning/).
-   **Derived evaluations excluded.** Post-quantum posture and cryptographic maturity are not embedded in the extracted CBOM. The recipient derives them from the disclosed facts by applying its own policy. See [Policy Evaluation](../policy-evaluation/).
-   **Identity and re-request.** Stable identifiers allow the recipient to correlate the CBOM with the corresponding SBOM and HBOM, and to request an updated CBOM when the subject changes. The minimum elements guidance makes the same point for SBOMs through its Component Identifiers element, which expects machine-processable unique identifiers to support automated analysis.
-   **Request and response.** A supply-chain request should state the profile and scope required. The producer validates the response against that profile and retains it for audit.
-   **Trust asymmetry.** Inputs to the inventory may come from lower-trust sources, so they require verification and normalization. Outputs produced by the organization carry the organization's own attestation.

In summary: a CBOM describes one component at a point in time, while a cryptographic inventory is the organization-wide record built and maintained from many CBOMs and other sources. CBOMs move in both directions: into the inventory as inputs, and out of it as scoped disclosures for internal and external consumers. Normalization and a shared profile keep the two consistent, and the same profile validates CBOMs on the way in and on the way out.

[← Challenges](../challenges/) [Next: Lifecycle Data →](../lifecycle/)
