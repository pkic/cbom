---
title: Related Work
sideMenu: true
weight: 22
aliases:
- /cbom/methodology/related-work.html
linkTitle: Related Work
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

Several other efforts address related parts of the same problem, and two of them are within the PKI Consortium. Knowing how they relate to CBOM profiles tells an adopter which artifact answers which question, and where one depends on another.

## PQC Maturity Model

The [PQC Maturity Model](https://pkic.org/wg/pqc/pqcmm/) is maintained by the PKI Consortium Post-Quantum Cryptography Working Group and is at version 1.0.1 at the time of writing. Unlike most maturity models, which assess an organization's internal posture, the PQCMM assesses products and services in the supply chain. That makes its subject the same as the subject of the interface model used here: a product treated from the outside, by a party that did not build it.

The model defines six cumulative levels. A product claiming a level satisfies every requirement of the levels below it.

| Level | Summary | Bearing on this methodology |
| --- | --- | --- |
| **0** None | No post-quantum capability implemented |  |
| **1** Initial | Capabilities available for testing and evaluation | Corresponds to a `capabilityStatus` below `available` in the migration profile |
| **2** Foundational | Production-ready and standards-conformant support | Corresponds to declared support in the migration profile's `Supported` attributes |
| **3** Advanced | Cryptographic inventory, SBOM support, cryptographic agility | The inventory requirement is the subject of [Inventory](../inventory/) |
| **4** Managed | **CBOM support**, hybrid cryptography, zero-legacy capability | The dependency described below |
| **5** Optimized | Post-quantum by default, benchmarked, certified implementations |  |

### Where the two efforts meet

PQCMM Level 4 requires CBOM support. It does not define what a CBOM must contain. The working group is not aware of any published definition that an assessor could be referred to. That gap is the reason this methodology exists. The statement should therefore be read as an explanation of why the work was started, not as the result of a survey. Without a definition, an assessor evaluating a product against Level 4 decides for itself what a sufficient CBOM looks like. A vendor then produces whatever satisfies the particular assessor it is dealing with. The PQCMM was created to remove this kind of ambiguity from the phrase "quantum-ready". The same ambiguity reappears one level down, in the phrase "CBOM support".

A profile is a definition of what a CBOM must contain for a stated purpose, expressed so that a document can be checked against it mechanically. A level requirement such as Level 4 needs this kind of definition if different assessors are to assess it consistently.

The relationship is a dependency, not just a general alignment. The two efforts are not competing descriptions of the same thing. The PQCMM requires an artifact, the CBOM, and CBOM profiles define what that artifact must contain.

### How the two divide the work

The two efforts complement each other without overlapping, and the architecture of this methodology already allows for this. [Policy Evaluation](../policy-evaluation/) states that derived judgements (conclusions drawn from facts against criteria that change over time) are computed by external versioned policy from the facts a CBOM discloses, and names cryptographic maturity as one of its examples. The PQCMM is an instance of exactly that external policy.

|  | PQC Maturity Model | CBOM profiles |
| --- | --- | --- |
| **Question answered** | How ready is this product, on a scale of 0 to 5 | Does this document disclose what the purpose requires |
| **Result** | A graded level, cumulative | A verdict per profile: conforms, does not conform, or refused |
| **Subject** | A product or service as named, released and shipped | One revision of one document |
| **Assessed by** | Self-assessment, or an accredited third-party assessor | A validator, mechanically |
| **Changes when** | The criteria are revised, or the product advances | The profile is revised, or a new document revision is produced |
| **Role** | Consumes the facts and forms a judgement | Specifies and supplies the facts |

Because the PQCMM assesses products, its levels and the depths of a profile family (successive profiles that each ask for more about the same decision) are easy to confuse, and they are different kinds of thing. A PQCMM level is a judgement about a product, computed from disclosed facts against criteria that are revised over time. A depth in a profile family is a set of rules a document is checked against, fixed at a version. For that reason [Maturity](../maturity/) does not call a deeper profile a maturity level. A profile defines the facts that the judgement reads. A maturity level is the judgement itself.

The relationship runs in one direction. A maturity level is derived from disclosed facts, so a change in the criteria changes the level without any document changing. Keeping the level separate from the CBOM protects this property. It is also why the level is not recorded as a CBOM attribute. See the treatment of derived judgements in [Policy Evaluation](../policy-evaluation/) and decision 0002 in the repository.

### Attributes that read as evidence

The migration profile was developed from a consumer's planning questions and not from any maturity model. Several of its attributes nevertheless correspond to what an assessment at Levels 2 to 4 appears to require. This is a reasonable indication that the two efforts address the same subject matter.

| Attribute | What an assessment could use it for |
| --- | --- |
| `keyExchangeSupported`, `authenticationSupported` | Which post-quantum algorithms the product can be configured to use |
| `coexistence` | Whether hybrid operation is possible, which Level 4 requires |
| `enablementMethod`, `minimumProductVersion` | Whether a capability is available in a shipped release, and what a customer must do to reach it |
| `capabilityStatus`, `blockedBy` | Where a capability stands, and what is preventing it |
| `implementationPurl` | Which library provides the capability, which bears on agility and on zero-legacy claims |
| `lifecycleStage` | Whether a stated fact was intended, implemented, configured or observed, which determines how far the evidence goes |

The mapping above is offered as an observation and has not been agreed with the PQC Working Group. Establishing whether a conforming CBOM could serve as evidence for a PQCMM assessment is work for the two groups together.

### A difference to reconcile

The two efforts treat external schemes differently, and both positions are correct for their purpose. The PQCMM references schemes such as CycloneDX and Package URL by name. It deliberately accepts whichever version is current, so that the model does not go out of date as those schemes are revised. This methodology fixes the versions of the carrier format (the format a CBOM is written in, such as CycloneDX) that a profile accepts, using a declared acceptance range. It does so because a validator has to know which structures it can read before it evaluates anything. See [Versioning](../versioning/).

The two positions do not conflict. A maturity criterion that asks whether a product supports CBOMs is satisfied by support for the scheme in general. A validator that checks a specific document needs to know which version that document uses. Anyone reading both should not take the difference as a disagreement about how schemes are referenced.

### Timing

A certification programme is planned, under which independent assessors validate vendor evidence and formal certificates are issued. It is targeted for announcement at the Post-Quantum Cryptography Conference in Amsterdam on 1 to 3 December 2026. Assessment practice for Level 4 will settle while that programme is being designed. Work done before then can help shape what "CBOM support" is taken to mean. Work done afterwards will have to be reconciled with an interpretation that is already in use.

## PQC Capabilities Matrix

The [PQC Capabilities Matrix](https://pkic.org/wg/pqc/pqccm/) is a further output of the same working group, recording which products support which post-quantum capabilities. Its subject overlaps with the declared capability attributes of the migration profile. The relationship has not been examined and is recorded as an open question.

## PKI Maturity Model

The [PKI Maturity Model](https://pkic.org/wg/pkimm/) assesses an organization's PKI operation rather than a product, and includes a post-quantum category within a broader framework. It sits at a different level from both the PQCMM and this methodology. An operator may run a mature PKI operation and still deploy products with no post-quantum capability. The reverse is equally possible. The two assessments therefore answer different questions about different subjects.

## What the working group is asked to decide

-   Whether to approach the PQC Working Group about a profile defining what CBOM support means for PQCMM Level 4. This is a commitment between working groups and not a drafting decision.
-   Whether a conforming CBOM should be proposed as evidence within a PQCMM assessment, and if so which profile.
-   Whether the relationship to the PQC Capabilities Matrix needs to be worked out before either effort publishes further.

Descriptions of other efforts on this page summarise material published by those efforts at the time of writing and are not agreed positions of either working group. The linked sources are authoritative.

[← Terms](../terms/) [Next: Files →](../files/)
