---
title: Terms
sideMenu: true
weight: 21
aliases:
- /cbom/methodology/terms.html
linkTitle: Terms
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The vocabulary this methodology uses, collected in one place. Definitions here are summaries; the section named against each term is where it is developed and is authoritative if the two differ.

## How to read this section

Terms are grouped by what they describe. Where a term is borrowed from elsewhere, the source is named, because a methodology that quietly redefines an established term causes more difficulty than one that invents a new word. Attribute names follow the conventions recorded in [Method](../method/): a bare name denotes present state and a `Supported` suffix denotes declared capability.

The last table lists terms that were considered and not used, with the reason for each. They are recorded so that the same discussion does not have to be repeated.

## The model

| Term | Definition | Developed in |
| --- | --- | --- |
| **Cryptographic relationship** also: edge | The place where cryptography is applied between parties. A relationship is not itself a cryptographic asset. The term was introduced by this methodology. | [Model](../model/) |
| **Endpoint** also: node | A party to a cryptographic relationship. An endpoint need not be a running host, and the parties to a relationship need not exist at the same time. | [Model](../model/) |
| **Cryptographic asset** | An algorithm, protocol, certificate, or key used by a relationship. Corresponds to the CycloneDX component type of the same name. | [Model](../model/) |
| **Interface** | A cryptographic relationship that is a communication interface between two parties. Interfaces are a subset of relationships. The term is kept because the profile's rules are written about interfaces. | [Model](../model/) |
| **Node fact / edge fact** | A node fact is a property of a thing, such as a product (an endpoint, or node). An edge fact is a property of one use of that thing in a cryptographic relationship (an edge). "The product supports AES-256-GCM" is a node fact. "This connection negotiated AES-256-GCM" is an edge fact. | [Model](../model/) |

## Profiles and conformance

| Term | Definition | Developed in |
| --- | --- | --- |
| **Profile** | A defined subset of mandatory attributes for a stated objective, expressed independently of any format. It sets a minimum reporting requirement and does not aim at exhaustive coverage. | [Profile](../profile/) |
| **Profile scope** | The boundary a profile declares: the *subject type* it describes, the *relationship types* its rules constrain, and the *lifecycle stages* of reported data it accepts. The three parts are decided together in Method step 2 and recorded as one object, because together they form a single boundary. | [Conformance](../conformance/) |
| **Identifier scheme** | The form a profile requires for identifying a class of asset: a Package URL for a library and for the subject, and a named registry for algorithms and protocols. The profile declares the scheme, rather than leaving it to be agreed separately for each document, so that two disclosures about the same thing can be matched. Requirement C14 checks that the declaration and the rules agree. | [Conformance](../conformance/) |
| **Stated absence** | A structural rule is satisfied in one of two ways. Either the required thing is present, or the document states explicitly that it is absent. Saying nothing satisfies neither. A subject with no administrative surface can state that it has none, and it then conforms. A subject that simply leaves out its management interface does not conform. Stated absence applies the disclosure model to the structure of a document (which interfaces it declares) rather than to the value of one attribute. | [Profile](../profile/) |
| **Cryptographic purpose** | The job that cryptography does at a relationship: establishing a key, encrypting, proving identity, protecting a message, signing for the long term, protecting keys, or deriving keys. A purpose is *not* the same as an operation. For example, `sign`/`verify` is one operation. It covers both a certificate signature and a firmware signature, and those two migrate a decade apart. A migration timetable attaches only to a purpose, so capability is stated per purpose. An entry is admitted to the vocabulary only if it passes a four-part test. The entry is declarable at the boundary, it can be migrated independently, it is actionable, and it is not an ingredient of another purpose. Purposes do not divide algorithms into separate sets. AES-GCM, for example, serves encryption and data integrity at once. | [PQC Migration](../../use-cases/pqc-migration/) |
| **Group rule** | A rule that constrains a repeated group of entries. Each entry is identified by a key from a controlled vocabulary, so an interface gives one answer for each key. The rules inside the group are evaluated within a single entry. A conditional guard (the condition that decides whether a rule applies) therefore refers to that entry and not to the interface as a whole. `keyCoverage` says whether an entry is required for every value in the vocabulary or only for the values the scope declares. This setting is what distinguishes a profile that addresses a problem one depth at a time from one that drops the part it defers. | [Conformance](../conformance/) |
| **Orientation** | Whether a profile reports present state (`inventory`), forward-looking capability (`migration`), or both. The orientation is declared in the scope, and requirement C12 checks it against the rules. This ensures that a capability attribute is never supplied in place of the present-state attribute it describes a capability for. | [Conformance](../conformance/) |
| **Forward-looking attribute** | An attribute describing what an interface could do or will do rather than what it does: any name with a `Supported` suffix, and `capabilityStatus`, `blockedBy` and `roadmapRef`, which describe a future state with no present-state counterpart. | [PQC Migration](../../use-cases/pqc-migration/) |
| **Subject type** | What a profile describes: a `product`, a `service`, a `component`, or an `estate-subset`. It determines what a producer can reasonably be asked for. For example, a consumer that operates a service can be asked for more than a consumer that holds a product it cannot inspect. | [Method](../method/) |
| **Accepted lifecycle stages** | The subset of lifecycle stages a profile will evaluate. An interface that reports a stage outside the set fails the rule that constrains the stage. This mirrors the way a document is refused when its carrier format version (the version of the format it is written in) is outside `appliesTo`. A derived profile may narrow the set and may not widen it. | [Conformance](../conformance/) |
| **Decision options** | The actions a profile's consumer chooses between, stated explicitly. Listing the options is what makes the action-choice test checkable. A decision that can be answered in only one way is not a real decision. A profile written for such a decision has no principled point at which to stop adding rules. | [Method](../method/) |
| **Product-level rule** also: structural rule | A rule constraining the set of interfaces a product declares, such as a required count or a required kind. A product-level rule can detect an omitted interface, which per-attribute rules cannot do. | [Profile](../profile/) |
| **Per-interface rule** | A rule applied uniformly to every declared interface. | [Profile](../profile/) |
| **Conformance level** also: obligation level | MUST, SHOULD or MAY, following BCP 14 (RFC 2119 and RFC 8174). Only MUST rules determine the verdict, which is the result of an evaluation. | [Conformance](../conformance/) |
| **Withholdable** | A property of a rule. If a rule is withholdable, the producer can satisfy it with a `withheld` marker, which states that the producer holds the value and declines to publish it. If the rule is not withholdable, a `withheld` marker fails the rule. | [Profile](../profile/) |
| **Audience** | Who may hold a document, which in turn determines what the document may contain. A profile expresses audience in only one way: through its choice of which rules are `withholdable`. Suppose a profile permits no withholding on the contested rules. Only a restricted variant of a document (one released to a limited audience) can then conform to it. Such a profile is therefore a derived profile of the public one. A rules file cannot yet declare an audience. This is open question Q54. | [Confidentiality](../confidentiality/) |
| **Verdict** | The result of evaluating one document revision against one profile version: *conforms*, *does not conform*, or *refused*. | [Conformance](../conformance/) |
| **Refused** | An outcome that is distinct from non-conformance. A document is refused when its carrier format version is below the minimum the profile declares. No assessment is then performed. A refusal says nothing about the document's content. | [Conformance](../conformance/) |
| **Well-formed profile** | A profile satisfying the methodology's own requirements C1 to C17. A verdict issued against a profile that is not well-formed establishes nothing. | [Conformance](../conformance/) |
| **Conformance claim** | A statement by an identified party that a named document revision was assessed against a named profile version and produced a stated verdict, citing the profile version, the carrier format version and the content revision. | [Conformance](../conformance/) |
| **Self-declared claim** | A claim in which the evaluating party is the producer of the document. Self-declared claims are permitted and are labelled as self-declared. | [Conformance](../conformance/) |
| **Attested claim** | A claim in which the evaluating party is other than the producer. | [Conformance](../conformance/) |
| **Dual use** | The property that one profile is both a specification for the producer and a checklist for the consumer. | [Profile](../profile/) |
| **Independent evaluation** | Evaluating one CBOM against several profiles, each producing its own verdict. The profiles need not know of each other and are not combined. | [Profile](../profile/) |
| **Extension** | A profile declaring that it inherits every rule of another and states only additions and tightenings. | [Profile](../profile/) |
| **Base and derived profile** | The profile named in `extends`, and the one naming it. A derived profile inherits every rule and may add to or tighten them. For a public and a restricted variant, the public profile is the base. | [Profile](../profile/) |
| **Profile tag** | A short handle such as `interface-disclosure`. A rule citation has two parts, and the tag is the part that says which profile the rule belongs to. The tag is the only identifier that has to be unique along an inheritance chain (a chain of profiles that extend one another). | [Objects](../objects/) |
| **Rule identifier** | An identifier that is local to the profile declaring the rule. It is cited as `tag#id`. The letter says how often the rule is evaluated: `P` per product, `I` per interface, `G` per group entry. A tightened rule keeps the identifier of the profile that introduced it. | [Objects](../objects/) |
| **Key coverage** | A group rule's `keyCoverage`: whether an entry is required for every key in its vocabulary (`all-purposes`) or only for the keys the profile's scope declares (`in-scope`). Distinct from the product attribute `coverage`, which says how complete a document's interface list is. Both were called coverage until decision 0021. | [Profile](../profile/) |
| **Claim verification** | Re-running the evaluation a claim records, against the document its digest names, to establish that the claim still holds. It does not establish that the disclosed values are true. | [Conformance](../conformance/) |
| **Monotonic extension** | The rule that a derived profile may add and tighten but never relax. It guarantees that conforming to the derived profile means conforming to the base. | [Profile](../profile/) |
| **Profile family** | A set of profiles related by extension. In a family ordered by *depth*, each deeper profile asks more about the same consumer decision. The shallowest member is the entry profile. A document that conforms at one depth also conforms at every shallower depth. Monotonic extension is what guarantees this. | [Maturity](../maturity/) |
| **Depth** | How much a profile asks about the same subject matter and the same decision. A deeper profile adds rules but does not change what the family is about. Depth differs from *coverage*, which brings more subject matter into scope at the same depth. It also differs from a *branch*, which changes the decision the profile serves. | [Maturity](../maturity/) |
| **Entry profile** | The shallowest profile in a family: the least a producer can disclose and still be checked against something. It asks for more than untargeted scanner output provides and for less than full disclosure. A producer that starts disclosing today therefore has a verdict to show for its work. | [Maturity](../maturity/) |
| **Branch** | A derived profile serving a *different* consumer decision. A branch is recognised by a different `objective` or a different `scope.orientation`. Like any extension, a branch is monotonic: it only adds and tightens rules. It is not a greater depth, however. For example, the PQC migration profile is a branch of the interface family, not a deeper level within it. | [Maturity](../maturity/) |
| **Deferral** | Something a profile does not require *at this depth*, as distinct from something excluded on principle at every depth. A rules file lists both kinds in one `exclusions` list and gives no mechanical way to tell them apart. This is recorded as open question Q52. | [Maturity](../maturity/) |
| **Tightening** | Raising a conformance level, narrowing a constraint, or removing withholdability. Permitted in an extension. | [Profile](../profile/) |
| **Relaxing** | Lowering a level, widening a constraint, removing a rule, or adding withholdability. Not permitted in an extension. A profile that needs to relax a rule is written as an independent profile. | [Profile](../profile/) |

## Disclosure states

Four outcomes are possible for any attribute. The 2026 SBOM minimum elements guidance requires the last three to be distinguished from one another. Neither carrier format can express that distinction natively.

| State | Meaning | Effect on a MUST rule |
| --- | --- | --- |
| `value` | A value was supplied and checked against the constraint. | Passes if valid. |
| `withheld` | The producer holds the information and declines to publish it. | Passes only where the rule is withholdable. |
| `unknown` | The producer does not have the information. | Fails, reported separately from an absent attribute. |
| `undeclared` | Neither a value nor a marker was supplied. | Fails. |

## Attributes

Attributes shared across profiles, followed by those introduced by the PQC migration profile.

| Attribute | Definition | Introduced in |
| --- | --- | --- |
| `interfaceId` | The producer's own label for an interface. Profiles do not constrain its value, and consumers should not treat it as a stable cross-organization identifier. | [Profile](../profile/) |
| `interfaceType` | The role of an interface, from a controlled vocabulary. The controlled vocabulary is what allows a rule such as "declare a management interface" to be evaluated. | [Profile](../profile/) |
| `protocol` | The protocol securing the interface, such as TLS, SSH or IPsec. | [Profile](../profile/) |
| `protocolVersion` / `protocolVersionsSupported` | The version in use, and the set of versions the interface can negotiate. | [Profile](../profile/) / [PQC Migration](../../use-cases/pqc-migration/) |
| `keyExchange` / `keyExchangeSupported` | The key-agreement or key-encapsulation algorithm in use, and the set the interface is able to use. | [Profile](../profile/) / [PQC Migration](../../use-cases/pqc-migration/) |
| `encryption` | The bulk or AEAD algorithm protecting data on the interface. | [Profile](../profile/) |
| `authentication` / `authenticationSupported` | The signature algorithm authenticating the server or host: a certificate signature for TLS, a host key for SSH. | [Profile](../profile/) / [PQC Migration](../../use-cases/pqc-migration/) |
| `endpointRoles` | The roles of the parties to the interface, such as client and server. | [Profile](../profile/) |
| `lifecycleStage` | The phase at which the data was captured. See the lifecycle table below. | [Lifecycle Data](../lifecycle/) |
| `implementationPurl` | The Package URL of the library implementing the interface's cryptography. This is the value that is matched against vulnerability feeds. | [Profile](../profile/) |
| `coverage` | A product-level statement of how complete the declared interface set is. | [PQC Migration](../../use-cases/pqc-migration/) |
| `capabilityStatus` | The class of commitment the producer makes to a capability the interface does not yet have, expressed without a date. | [PQC Migration](../../use-cases/pqc-migration/) |
| `blockedBy` | What must change before a capability becomes available. The value therefore also shows who is able to make that change. | [PQC Migration](../../use-cases/pqc-migration/) |
| `roadmapRef` | A reference to a roadmap entry carrying a target release and, where offered, a date. Kept outside the interface so that a slipping date does not force a CBOM revision. | [PQC Migration](../../use-cases/pqc-migration/) |
| `enablementMethod` | What a consumer must do to turn a capability on. | [PQC Migration](../../use-cases/pqc-migration/) |
| `minimumProductVersion` | The product version at which a capability becomes available. Required where enablement is by software update. | [PQC Migration](../../use-cases/pqc-migration/) |
| `providerLocation` | Where key operations execute. This determines whether a new algorithm can be adopted through software at all. | [PQC Migration](../../use-cases/pqc-migration/) |
| `coexistence` | Whether the interface can serve classical and post-quantum peers at the same time. Determines whether migration requires a coordinated cutover. | [PQC Migration](../../use-cases/pqc-migration/) |
| `negotiationControl` | Whether the interface can be configured to require post-quantum key exchange and refuse a classical fallback. | [PQC Migration](../../use-cases/pqc-migration/) |
| `integrationConstraints` | Known effects of enabling a capability, such as handshake size limits or intermediary incompatibilities. | [PQC Migration](../../use-cases/pqc-migration/) |

## Controlled vocabularies

| Attribute | Permitted values |
| --- | --- |
| `interfaceType` | `management` · `service` · `interconnect` · `peer` · `storage` |
| `lifecycleStage` | `intended` · `implemented` · `configured` · `observed` a profile accepts a subset of these; see profile scope |
| `subjectType` | `product` · `service` · `component` · `estate-subset` |
| `orientation` | `inventory` · `migration` · `both` |
| `cryptographicPurpose` | `key-establishment` · `encryption` · `entity-authentication` · `data-integrity` · `non-repudiation` · `key-protection` · `key-derivation` a sector profile might add values to this list; whether it is allowed to do so mirrors question Q35 and is unresolved |
| `coverage` | `all-external` · `all` · `partial` |
| `capabilityStatus` | `available` · `committed` · `planned` · `under-evaluation` · `not-planned` |
| `blockedBy` | `provider` · `product` · `hardware` · `standard` · `certification` |
| `enablementMethod` | `already-enabled` · `configuration` · `software-update` · `hardware-change` · `licence` · `not-available` |
| `providerLocation` | `software` · `hsm` · `tee` · `unspecified` |
| `coexistence` | `simultaneous` · `exclusive` · `unknown` |

## Lifecycle and provenance

| Term | Definition | Developed in |
| --- | --- | --- |
| **Capture phase** | What `lifecycleStage` records: whether a value was intended, implemented, configured or observed. It is a property of a single fact, so two attributes in the same document can have different capture phases. It is not a revision state. | [Lifecycle Data](../lifecycle/) |
| **Revision state** | The states a document passes through: created, signed, published and superseded. A revision state is a property of a whole document, and it is what governance controls. Validation is not a revision state. A published revision can be validated many times, and validation does not change it. | [Governance](../governance/) |
| `intended` | Cryptography specified at design time. Says nothing about what was built. | [Lifecycle Data](../lifecycle/) |
| `implemented` | Cryptography present in the shipped binary. Indicates capability rather than use. | [Lifecycle Data](../lifecycle/) |
| `configured` | Cryptography the deployed configuration permits. | [Lifecycle Data](../lifecycle/) |
| `observed` | Cryptography negotiated on the wire. It is a snapshot, and a later configuration change makes it invalid. | [Lifecycle Data](../lifecycle/) |
| **Readiness gap** | The difference between what a product is capable of and what a deployment actually runs. | [Lifecycle Data](../lifecycle/) |
| **Product CBOM** | A CBOM describing what a product contains or can use. Vendor-produced, normally `implemented`. | [Lifecycle Data](../lifecycle/) |
| **Service CBOM** | A CBOM describing what a running deployment uses. Operator-produced, normally `configured` or `observed`. | [Lifecycle Data](../lifecycle/) |
| **Provenance** | The record of how a CBOM was produced: generating tool and version, inputs, lifecycle stage, and any mechanical upgrade applied. | [Governance](../governance/) |
| **SBOM Generation Context** (CISA) | The lifecycle phase and data available when an SBOM was generated. This is the equivalent concept in the 2026 minimum elements guidance. It is less fine-grained than the capture phase. | [Lifecycle Data](../lifecycle/) |

## Formats, mapping and versions

| Term | Definition | Developed in |
| --- | --- | --- |
| **Carrier format** | The format in which a CBOM is serialized, such as CycloneDX or SPDX. Distinct from the profile expressed in it. | [Versioning](../versioning/) |
| **Mapping** | The statement of where each profile attribute lives in a given format, including a canonical location where the format permits several. | [Formats](../formats/) |
| **Format adapter** | The format-specific part of a validator, which extracts abstract attributes from a concrete document. It is the only part of a validator that changes from one format to another. | [Formats](../formats/) |
| **Acceptance range** also: appliesTo | The carrier format versions a profile accepts, expressed as a minimum version and a tested version. | [Versioning](../versioning/) |
| **Version bands** | The four bands into which a carrier format version can fall, measured against the acceptance range: unsupported below the minimum, legacy between the minimum and the tested version, target at the tested version, and newer above it. | [Versioning](../versioning/) |
| **Encoding normalization** | Agreement on where a value is written, where a format permits more than one valid location. | [Formats](../formats/) |
| **Naming normalization** | Agreement on how a value is expressed, so that equivalent values match. Addressed by the CycloneDX Cryptography Registry for algorithms. | [Formats](../formats/) |
| **Content revision** | A successive version of a CBOM for the same subject. The sequence of revisions is the audit trail that progress tracking relies on. | [Versioning](../versioning/) |

## Inventory and exchange

| Term | Definition | Developed in |
| --- | --- | --- |
| **Cryptographic inventory** | An organization-wide, continuously maintained record of cryptography in use, aggregated from CBOMs and other sources. | [Inventory](../inventory/) |
| **Extracted CBOM** also: output CBOM | A scoped snapshot drawn from an inventory for a specific consumer, filtered and redacted as required. | [Inventory](../inventory/) |
| **Disclosure variant** public variant / restricted variant | One of two or more documents describing the same subject at the same content revision, differing only in which values have been replaced by a `withheld` marker. Each variant is prepared for the audience that may hold it. A variant is not a version. [Versioning](../versioning/) tracks three axes: carrier format, profile and content revision. Audience is not one of them. | [Confidentiality](../confidentiality/) |
| **Redaction** | Replacing a value with a `withheld` marker on release. Redaction by *deletion* is a different act, and a worse one. A deleted value reads as `undeclared` and fails the rule. The reader then cannot tell a deliberate policy decision from a gap in the producer's tooling. | [Confidentiality](../confidentiality/) |
| **Central / distributed / federated inventory** | Arrangements for where inventory data is held. In a federated arrangement, a profile defines the subset of data that is published upward. This makes inventories that are held separately comparable with one another. | [Inventory](../inventory/) |
| **Supersedence** | The replacement of a CBOM revision by a newer one for the same subject, with the earlier revision retained for audit. | [Governance](../governance/) |

## Evaluation and policy

| Term | Definition | Developed in |
| --- | --- | --- |
| **Fact** | Something a producer observes or declares, recorded in the CBOM. | [Policy Evaluation](../policy-evaluation/) |
| **Evaluation** also: derived judgement | A conclusion drawn from facts against criteria that change over time. An external policy produces it at the time the question is asked, and it is dated. It is never stored as a CBOM attribute. | [Policy Evaluation](../policy-evaluation/) |
| **Post-quantum posture** | An evaluation, not an attribute. Whether an interface's algorithms are considered quantum-safe, assessed against current guidance. | [Policy Evaluation](../policy-evaluation/) |
| **Cryptographic maturity** | An evaluation, not an attribute, for the same reason as post-quantum posture. The [PQC Maturity Model](../related-work/) is an instance of this kind of external policy. | [Policy Evaluation](../policy-evaluation/) |
| **Advisory** | A third party's statement that a named component, in a stated version range, carries a named weakness. An advisory is written by a maintainer, a numbering authority or a research team. It is not written by the subject's producer, and it is not part of a CBOM. | [Vulnerabilities](../vulnerabilities/) |
| **VEX statement** | A producer's judgement that its product is or is not affected by a named advisory. Where the product is not affected, the statement carries a justification. The judgement combines the CBOM's facts with knowledge held elsewhere, and it is revised whenever either of them changes. For that reason it is kept as a separate artifact from the document it is about. | [Vulnerabilities](../vulnerabilities/) |
| **Implementation defect** | A weakness in code that performs cryptography. It has a version range, a patch and an identifier in a vulnerability feed. It is found by matching the implementing library (`I9`) against that feed. The CBOM contributes by showing which interfaces use that library. | [Vulnerabilities](../vulnerabilities/) |
| **Algorithm or parameter weakness** | A weakness in a choice rather than in code: a deprecated algorithm, an inadequate key length, or a classical key exchange used against a quantum adversary. Such a weakness usually has no identifier and never has a patch. The remedy is to use a different algorithm or parameter. It is found by a [policy evaluation](../policy-evaluation/) of the disclosed facts, and the CBOM is the only evidence for that evaluation. | [Vulnerabilities](../vulnerabilities/) |
| **Harvest now, decrypt later** | Capturing encrypted traffic or stored ciphertext now, to decrypt once a cryptographically relevant quantum computer exists. The exposure depends on how long the data must stay confidential, so it cannot be seen by examining the cryptography alone. | [Data Exposure](../data-exposure/) |
| **Confidentiality lifetime** proposed | How long data carried over an interface must remain confidential after transmission. It is recorded in bands (fixed ranges of time) so that it is comparable between organizations. It is an attribute of a deployment, not of a product. It describes the traffic and not the document. The confidentiality of the CBOM itself is a separate subject, covered in [Confidentiality](../confidentiality/). | [Data Exposure](../data-exposure/) |
| **Urgency ranking** | An evaluation, not an attribute. An ordering of interfaces by exposure to the harvest-now-decrypt-later threat. It is computed from disclosed facts and from an external estimate of when a cryptographically relevant quantum computer will exist. | [Data Exposure](../data-exposure/) |

## Related artifacts

| Term | Definition |
| --- | --- |
| **CBOM** | Cryptography Bill of Materials. A structured description of the cryptography a subject contains or uses, at a point in time. |
| **SBOM** | Software Bill of Materials. It is read alongside a CBOM so that cryptography can be linked to the components that implement it. |
| **HBOM** | Hardware Bill of Materials. It is relevant where cryptography is bound to hardware, so that changing the cryptography means replacing the hardware. |
| **VEX** (external) | Vulnerability Exploitability eXchange. The statement that a product is or is not affected by a known vulnerability, expressed as a CSAF VEX document, an OpenVEX document, or a `vulnerabilities` array in a CycloneDX BOM. The four statuses are *affected*, *not affected*, *fixed* and *under investigation*, and *not affected* carries a justification. |
| **CSAF** (OASIS) | Common Security Advisory Framework 2.0. The machine-readable advisory format, which includes a VEX profile. |
| **CVE** (external) | An identifier for one vulnerability in a component. CVEs are issued for implementation defects. They are not issued when a product uses an algorithm that guidance has deprecated. |
| **CWE** (external) | A classification of weakness *types*. CWE-327, CWE-326 and CWE-328 are the cryptographic entries. A CWE names a class of weakness rather than an instance, so it cannot serve as the identifier of a particular finding. See Q59. |
| **purl** (external) | Package URL. The identifier scheme used to name implementing libraries. |
| **BCP 14** (IETF) | RFC 2119 with RFC 8174, defining the requirement keywords MUST, SHOULD and MAY. |
| **Cryptography Registry** (CycloneDX) | The registry of stable algorithm identifiers introduced in CycloneDX 1.7. It addresses naming normalization. |

## Terms considered and not used

Each of these was considered and set aside. Recording the reasoning prevents the discussion recurring.

| Term | Why it is not used |
| --- | --- |
| **Interface**, as the general term | The word is too narrow for the general case. It suggests two parties communicating at the same time over a link. That excludes relationships whose parties are separated in time, and relationships that transfer no data. The word is kept for the subset of relationships that genuinely are interfaces. |
| **Cryptographic context** | Collides with established usage, where a context is the runtime state held by a cipher implementation. |
| `pqcPosture` | Removed from the profile. It encodes an evaluation, and its correct value changes when guidance changes without the product changing. |
| `vulnerable`, and any vulnerability status | Not an attribute. It encodes a judgement that combines the document's facts with an advisory held by a third party. Its correct value can therefore change while the product itself does not change. It is communicated as a [VEX statement](../vulnerabilities/) alongside the CBOM. Decision 0020. |
| `plannedAvailability` | Replaced by `capabilityStatus`, `blockedBy` and `roadmapRef`. A date recorded on an interface copies one underlying change event onto every interface that inherits it. |
| **Maturity level**, for a profile | In this documentation, a maturity level is a judgement about a product. External versioned policy derives it from disclosed facts. A [PQC Maturity Model](../related-work/) level is one example. A profile defines the facts that such a judgement reads. Using the same phrase for both would give one term two meanings, and one of those meanings, the judgement, is excluded from a CBOM on principle. A level within a profile family is therefore called a *depth*. See [Maturity](../maturity/). |
| **Tier**, for a depth | The word already has two meanings in this area. It means a supplier's position in a supply chain. It also names the ownership arrangement in [Governance](../governance/), where the working group owns a baseline profile and sector bodies own the profiles they derive from it. |
| `*Current` suffix | Redundant under the naming conventions, where a bare name already denotes present state. |

[← Governance](../governance/) [Next: Related Work →](../related-work/)
