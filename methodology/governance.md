---
title: Governance
sideMenu: true
weight: 20
aliases:
- /cbom/methodology/governance.html
linkTitle: Governance
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

Governance covers the processes and controls that apply to CBOMs and profiles over their lifetime: how they are produced, signed, distributed, changed and retired.

## Revision states

A CBOM revision passes through four states. Governance controls each transition between them. In this methodology the word *lifecycle* is used only for the capture phase of a reported fact, which is a separate matter described under [Lifecycle Data](../lifecycle/). A revision has states. A fact has a capture phase. The two are easy to confuse because the same word was previously used for both.

{{< figure src="../assets/figures/methodology-governance-1.svg" alt="Four boxes joined left to right by arrows: Create from build or scan, Sign for integrity and provenance, Publish to a registry, and Supersede by revision or retirement. Three dashed arrows lead down from Publish to three separate validation events, each producing a conformance claim, showing that validation does not advance the document." >}}

*The four states of a revision, and the validation events against a published one. A new revision re-enters at Create; superseded revisions are retained for audit. The dashed arrows are not transitions.*

### Validation is not a state

A document does not change when somebody validates it. Validation is applied to a published revision. It can happen any number of times, carried out by parties who do not coordinate with each other. Each validation produces a [conformance claim](../conformance/), a recorded statement of whether the document met a profile. It does not move the document to another state. The producer and the curator control the four states. Each claim belongs to the party that made it.

Governance has to account for this difference. A revision is produced once, but it is used for as long as anyone keeps a copy. Two consumers who validate the same document against the same profile a year apart can reach different verdicts (pass or fail results), because the profile may have been revised in between. For that reason, a claim is bound to the digest of the document and records the exact profile version used.

### A profile authority can change a verdict without anyone touching the document

When a profile authority tightens a published profile, existing revisions that conformed to it may stop conforming. The verdict changes even though no producer acted and no document changed. Only the profile authority has this power. No other role in the model can change a verdict in this way.

This power has two consequences. First, a profile authority that revises a published profile should state what happens to documents that conformed to the previous version. This is the grace-window question recorded as Q15. Second, the earlier verdict can be checked only if the superseded profile text is kept. That is the purpose of the archive obligation set out under "The archive obligation". Without the superseded text, the old claim cannot be reproduced, and nobody can show that the change was a tightening rather than a rewrite.

### Where public and restricted variants separate

A CBOM can exist in two variants: a public variant that anyone may hold, and a restricted variant released only to named recipients. The two variants separate at Create, not at Publish. The markers that make a document public are written into the document itself. A producer therefore creates two documents, signs both, and publishes each to its own audience. The two must also be superseded together. If a new restricted revision is issued without a matching public revision, the public record describes a version that no longer exists.

This methodology does not cover how a producer makes the two variants. In practice, both are extracts taken from one inventory at two redaction settings. Governance covers the pair of documents that recipients receive and the relationship between them. See [Confidentiality](../confidentiality/).

## Roles

Two of the four roles, the producer and the curator, can move a revision between states. The consumer validates a revision but does not move it. The profile authority cannot move a revision either. It has a larger power instead: by revising a profile, it can change the verdict on revisions that nobody has touched.

| Role | Transitions it may cause | Responsibility |
| --- | --- | --- |
| Producer | Create, Sign, revise | Generates the CBOM (build pipeline or scanner), and records provenance and the `lifecycleStage` of what it captured. |
| Consumer | None | Validates a published revision against the applicable profiles and records the conformance claim. Validating does not change the document, and a consumer may validate the same revision again whenever a profile is revised. |
| Curator / registry | Publish, retire | Stores, versions, and serves revisions, and enforces retention and access control. |
| Profile authority | None | Defines and versions profiles, and manages the controlled vocabulary and its deprecation. Revising a profile can change the verdict on every published revision evaluated against it. |

## Integrity and authenticity (signing)

Signing is now an expected practice. The 2026 minimum elements guidance lists SBOM Author Signature among its minimum elements, defined as a digital signature attributable to the SBOM author, alongside SBOM Author, SBOM Tool Name and SBOM Tool Version. A bill of materials that cannot be attributed and verified no longer meets the stated baseline. See [References](../../references/).

A CBOM should be signed so that a consumer can verify its origin and detect subsequent modification. Two distinct objects may be signed:

-   **The CBOM document**, by a detached digital signature over the serialized file, so that any alteration is detectable.
-   **The process that produced it**, as a build attestation (for example, in the in-toto or SLSA model), so that the provenance of the CBOM is itself verifiable.

Signing depends on key management: the protection and rotation of signing keys, and a means for consumers to establish trust in the signing identity. Because the subject matter is cryptography, the signature algorithms are themselves in scope. A signature gives assurance only for as long as its algorithm remains strong. A CBOM signed with a classical algorithm can therefore be relied on only until that algorithm can be broken. For that reason, the choice of signing algorithm should follow the same rules as the cryptography the CBOM describes. The minimum elements guidance takes the same view, referring authors to the ENISA agreed cryptographic mechanisms for the signature itself.

Signing establishes that a CBOM originates from a stated party and has not been altered. It does not establish that the CBOM is accurate. Accuracy depends on the process that produced the CBOM. For that reason, provenance and lifecycle stage are recorded alongside the signature.

## Provenance

A CBOM should record how it was produced: the generating tool and its version, the inputs, the lifecycle stage at which it was captured, and any mechanical upgrade applied to it (see [Versioning](../versioning/)). Provenance supports both trust and reproducibility, and is a precondition for a meaningful conformance claim. The tool name and version are now named minimum elements, so a producer meeting the SBOM baseline already carries most of what a CBOM consumer needs to judge how the data was obtained.

Provenance also has to account for information that is missing. Where an attribute is unavailable, the record should state whether the producer lacks the information or is withholding it, rather than leaving the field empty. See the discussion in [Challenges](../challenges/).

## Relating a CBOM to an SBOM

Cryptography does not exist apart from the software and hardware that implement it, so a CBOM is of limited use without some way to reach the component context. There is more than one way to arrange that, and the choice is a governance decision. It determines what is signed, who is accountable for which document, how often each is regenerated, and what a consumer has to fetch before it can act.

Four arrangements are in use. Arrangements A and B each produce a single document. Arrangements C and D each produce a pair of documents, with a reference from one to the other.

{{< figure src="../assets/figures/methodology-governance-2.svg" alt="Four arrangements side by side: a unified document holding software components and crypto assets, a standalone CBOM, a CBOM with an arrow to an SBOM, and an SBOM with an arrow to a CBOM" >}}

*The four arrangements. A and B are single documents. C and D are pairs that differ in which document is the entry point and which is discovered from it.*

### A · Unified document

One bill of materials contains both the software components and the cryptographic assets, with dependencies expressed between them. CycloneDX supports this directly, since cryptographic assets are components like any other. The worked example on this site is of this kind: the OpenSSH and OpenSSL library components sit in the same document as the interfaces and algorithms that use them.

The advantage is that there is no reference to resolve and no second document to keep in step. A single signature covers the whole claim, one author is accountable, and a consumer holding the document has everything it needs. The disadvantage appears when the two kinds of data have different lifetimes or different owners. A vendor's software inventory changes on release. A deployment's cryptographic configuration can change without any software changing at all. Binding them into one artifact forces the slower-moving part to be republished whenever the faster-moving part changes. It also means that a consumer entitled to the software inventory necessarily receives the cryptographic detail as well.

### B · Standalone CBOM

The CBOM is a single document that describes cryptography without reference to any software inventory. This is the appropriate arrangement when the subject is not a software artifact, for instance an operator describing the cryptography observed on a service it did not build, or a survey of an estate assembled from network discovery.

It is simple to produce and to distribute, and it avoids publishing software composition that the producer may not wish to disclose. However, it cannot answer the question that usually follows. If an algorithm needs replacing, the next question is which library implements it and whether that library can be updated. A standalone CBOM does not carry that information. The profile asks for `implementationPurl` to reduce this problem. That attribute names the implementing package even when no SBOM is linked.

### C · CBOM referencing an external SBOM

The CBOM is the entry point and carries a reference to the SBOM for the same subject. A consumer starts from the cryptography and resolves outward to component detail when it needs it.

This suits consumers whose question is cryptographic: migration planners, and anyone assessing an interface rather than a release. The two documents keep independent lifecycles, so a configuration change can produce a new CBOM revision without reissuing the SBOM. The cost is that the reference between the two documents has to be kept correct. A reference that names a document without pinning its revision will eventually point at something that has moved on, and a consumer that cannot resolve the reference is left with an incomplete picture and no indication that anything is missing.

### D · SBOM referencing an external CBOM

The SBOM is the entry point and links to the CBOM as an external artifact. This is the arrangement the site describes for SPDX, because SPDX 3.0.1 has no cryptographic object model, so the practical option today is an SPDX SBOM alongside a CycloneDX CBOM.

Its strengths are distributional. Existing supply-chain processes already request, store and verify SBOMs, so a CBOM reached from an SBOM inherits those processes rather than requiring its own. Access can also be separated, which matters when an organization is willing to publish software composition more widely than cryptographic configuration. The weakness is that cryptography becomes a secondary artifact. A consumer that stops at the SBOM, or whose tooling ignores unfamiliar external references, never sees the CBOM at all, and there is no signal in the SBOM that anything is missing.

### Comparison

| Governance question | A · Unified | B · Standalone | C · CBOM → SBOM | D · SBOM → CBOM |
| --- | --- | --- | --- | --- |
| Documents to produce | one | one | two | two |
| Signature covers the whole claim | yes | yes, but the claim is narrower | no, each signed separately | no, each signed separately |
| Independent regeneration | no | not applicable | yes | yes |
| Separate access control | no | not applicable | yes | yes |
| Risk of version skew | none | none | present | present |
| Risk of the CBOM being missed | none | none | low | higher |
| Answers "which library implements this" | directly | only via `implementationPurl` | after resolution | directly, from the entry point |
| Available in SPDX today | no | no | no | yes |

### Requirements that apply whichever is chosen

Where two documents are used, the reference between them needs governance. Without it, the reference becomes inaccurate over time.

-   **Pin the revision.** A reference should identify a specific revision of the target, not merely the target. CycloneDX provides a link form that identifies a BOM by serial number and version, which is the mechanism to prefer over a bare URL. Confirm the exact syntax against the current schema before relying on it.
-   **Give the pair a shared subject identifier.** Both documents should name the same subject in the same way, so that a consumer holding one can find the other without following a link that may have rotted.
-   **State whether resolution is required for conformance.** A profile should say whether an unresolvable reference is a failure or a warning. If the profile does not say, two consumers will reach different verdicts on the same document.
-   **Sign both, and record the relationship.** Two signatures do not by themselves attest that the two documents belong together. The reference should be inside the signed content of at least one of them.
-   **Retain both documents for the same period.** A retained CBOM whose SBOM has been deleted is an audit record that can no longer be interpreted.

A defensible default is to use a unified document for a product CBOM generated at build time. In that case the software and cryptographic views share an author and a release cadence. For an operator or service CBOM, use a referenced pair, because the cryptographic configuration changes independently of any software release. Where the consumer requires SPDX, arrangement D is currently the only option. The reference should then be treated as part of the deliverable rather than as a convenience.

## Evolution and change control

Profiles, the controlled vocabulary, and the methodology evolve over time. Changes are managed through explicit versioning (see [Versioning](../versioning/)), recorded decisions, and, within the working group, lazy consensus (a proposal is accepted unless someone objects). When a requirement is tightened, it takes effect only after a dated grace window. Vocabulary values are deprecated rather than removed. Both practices make changes predictable and auditable.

The working group's own record is kept in the repository. Decisions taken while drafting are written up in [decisions/](https://github.com/pkic/cbom/tree/main/decisions), one file per decision. Each file states the options considered and what reversing the decision would involve. A decision is superseded rather than deleted. Unresolved items are collected in the [open questions register](https://github.com/pkic/cbom/blob/main/open-questions.md), and each one is mapped to the methodology aspect that tracks it. Profiles follow the same practice. The example baseline profile carries a changelog that classifies each change as tightening, relaxing, or editorial. A producer can then tell from the record whether a new version requires further work from it.

## Stewardship of profiles and mappings

Change control describes what happens when a profile is revised. Stewardship describes what happens over the years in which the profile is in use. It is a separate question because a profile outlives the circumstances that produced it. A conformance claim made against a profile can be examined long after the group that wrote the profile has disbanded. The claim is meaningful only if the profile it cites can still be obtained in the form it had at the time.

Profiles and mappings need different treatment. A profile changes when its author decides to change it. A mapping changes because a carrier format changed. A carrier format is the concrete file format, such as CycloneDX or SPDX, in which a CBOM is written. Carrier formats change on a schedule that nobody in this working group controls. Mapping maintenance is therefore a continuing obligation. Profile maintenance is an occasional decision.

### Areas to be assigned

| Area | What has to be settled |
| --- | --- |
| **Ownership** | Who maintains a profile after publication. A tiered arrangement is available: the working group owns the baseline, a sector body owns the profiles it derives, and the consortium maintains the register and the archive. |
| **Review cadence** | A stated review period, and a trigger on each carrier format release, so that a profile is examined on a schedule instead of when somebody notices a problem. |
| **Deprecation and withdrawal** | How a profile is retired, the minimum notice, and what becomes of claims that cite it. A withdrawn profile does not invalidate past claims, which were correct when made. |
| **Archive** | Every published version retained and served indefinitely, addressed by version. See below. |
| **Mapping maintenance** | Named responsibility for tracking each carrier format, and a method for recording that a stated limitation has been addressed upstream. |
| **Succession** | What happens when a working group closes or a sector body withdraws, including whether an unmaintained profile is transferred or marked dormant. |

### The archive obligation

A conformance claim cites a profile version so that the result can be reproduced. An auditor examining a claim years later needs the text of that version as it stood when the claim was made, because a later version may require different things. If published versions are not retained and served, every claim becomes unverifiable as soon as the profile is revised. The conformance model depends on claims being reproducible.

Whoever publishes a profile therefore has an obligation. They must retain every published version indefinitely, addressable by its version identifier, and must not alter a published version in place. A correction is issued as a new version. Superseded CBOM revisions are treated the same way, for the same reason (see "Distribution, retention, and immutability").

The conformance model assumes this obligation, but the obligation is not currently stated anywhere. A profile published without a durable, versioned address undermines every claim that cites it, and the failure is not apparent until a claim is checked.

### Mappings track something the group does not control

A mapping states where each attribute sits in a concrete format. When CycloneDX or SPDX publishes a release, the mapping may become incomplete, or a limitation the documentation records may cease to be true. Neither event is triggered by anything the working group does, so neither will be noticed unless somebody is watching. Assigning that responsibility, and deciding how a superseded limitation is recorded, prevents the documentation from stating things about the formats that are no longer accurate.

### Related open questions

Several questions already recorded in the open questions register belong to stewardship. They are best settled together rather than one at a time:

-   who may publish under a consortium namespace, and who maintains the register;
-   whether a published profile is signed, and by whom;
-   who tracks the carrier formats;
-   whether raising the tested carrier version requires a profile version increment;
-   how long a producer has to comply when a profile is tightened.

## Distribution, retention, and immutability

Published CBOM revisions should be immutable. A correction or update is issued as a new revision rather than as a change to the existing one. A new revision replaces its predecessor but does not delete it. The registry governs access control and retention. Retention of superseded revisions provides the audit trail on which progress tracking and incident investigation depend.

Immutability does not remove the obligation to correct. The minimum elements guidance expects organizations to accommodate updates to bill-of-materials data, including corrections, and expects authors to correct errors promptly. The two work together: the erroneous revision is retained for audit and a corrected revision supersedes it.

## Conformance-claim governance

A conformance claim references the profile version, the carrier format version, and the CBOM content revision (see [Versioning](../versioning/)). Claims are recorded so that a stated result can be reproduced and audited. A claim that omits any of these three references is not reproducible. The form of a claim, the identification of the party making it, and the distinction between a self-declared and an attested claim are specified in [Conformance](../conformance/).

## Confidentiality and disclosure

Governance also addresses the boundary between disclosure and the protection of intellectual property. A profile sets the minimum that must be disclosed. Governance covers information beyond that minimum, including any redaction policy and the conditions under which more detailed CBOMs are shared. [Confidentiality](../confidentiality/) explains how a public and a restricted variant of one document relate to each other and to the profiles they satisfy. It also explains why two risks belong to governance rather than to a profile: the risk from combining many CBOMs (aggregation) and the risk from comparing successive CBOMs (differencing). Both are questions about distribution. See also the discussion of how much detail a CBOM discloses (depth of disclosure) in [Challenges](../challenges/).

In summary: governance defines who may produce, sign, publish, and revise a CBOM; how integrity, authenticity, and provenance are established; how profiles evolve; and how conformance claims are recorded and audited. Versioning provides the mechanisms, and governance provides the process around them.

[← Versioning](../versioning/) [Next: Terms →](../terms/)
