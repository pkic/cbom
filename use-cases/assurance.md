---
title: Assurance
sideMenu: true
weight: 9
aliases:
- /cbom/use-cases/assurance.html
linkTitle: Assurance
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

In these use cases, the reader is an auditor, an assessor or a regulator. The reader did not produce the document, cannot ask follow-up questions, and has to rely on it as evidence. The cryptographic facts are usually the disclosure facts. What changes is what the document has to show about itself: who made it, when, from what, whether it has been altered since, and whether it is still current.

Proposed in October 2026 as an amendment to draft decision 0023, which defined the first two groups. Not yet settled.

This is the least settled of the four groups. The working group may find that its requirements belong on the conformance claim, which any profile can carry, rather than in profiles of their own. The first worked example will show which.

## What the group shares

In this group, provenance and freshness matter most. Provenance is who produced the document and from what. Freshness is whether it is still current. A reported position only means something to an external reader if it says when it was produced and from what. That makes the lifecycle stage and the date of each statement as important as the statement itself. An assurance reader also needs to know that the document it holds is the one that was evaluated, and that nothing has replaced it.

The methodology already provides part of this. A conformance claim is bound to one document by the document's digest, and it lists each profile separately (decision 0015). A claim can also be re-checked. What it does not yet say is how the digest is computed so that two producers agree, whether profiles themselves are signed, who may declare conformance, and what a claim means once the document it binds is superseded.

One document can serve both the disclosure and the assurance use cases. This is because an assurance profile adds no new cryptographic facts. It adds requirements on the document's provenance and on its conformance claim.

## Questions this group owns

| Question | Why it belongs to this group |
| --- | --- |
| Q14 | Whether a supplier may declare its own conformance, or someone else has to check it |
| Q29 | Whether published profiles are signed, or identified by fingerprint |
| Q60 | What happens to a claim when the document it is bound to is superseded |
| Q44 | Whether a conforming CBOM is proposed as evidence in readiness assessments |
| Discussions #18 and #37 | How a digest is computed so that two producers agree, and whether an informative annex should describe transparency services for shared CBOMs |

## Worked examples

None yet. A first one could take the Keycloak supplier document, add a conformance claim bound by digest, and work through what a regulator receiving it under NIS2 would still need to know before relying on it.

## The use cases in this group

### Regulatory and compliance reporting

An organization must demonstrate its cryptographic position against a framework such as the EU Cyber Resilience Act, NIS2, the BSI technical guidelines, or a national directive. The consumer is an auditor or regulator who did not generate the data and cannot ask follow-up questions of the system.

The cryptographic facts are largely the disclosure baseline's. A profile encodes what a given framework expects, so that conformance can be evidenced by a dated artifact that an auditor can re-check. Because the reader is external, provenance and lifecycle stage carry more weight than usual. A reported position only means something if it says when it was produced and from what. A jurisdiction-specific profile also lets a global vendor satisfy the requirement once and report against it in several places.

### Certification and validation evidence

An evaluator or certification body checks a product against a scheme such as FIPS 140-3 module validation, Common Criteria or IEC 62443-4-2, and decides whether the cryptography a CBOM describes matches what was evaluated. A buyer asks the same question when it relies on a supplier's claim of validation. The cryptographic facts already exist: the module validation attributes of the PQC migration profile, and the `certifications` field of CycloneDX 2.0. What matters for evidence is whether the document is bound to the version and configuration that were evaluated, and whether it still is.

**Proposed.**

### Readiness assessment evidence

An assessor scores an organization against a readiness or maturity model, or against a national migration roadmap, and decides what level or status to record. A conforming CBOM could serve as evidence for some of the criteria, provided the assessor can tell when and from what it was produced. Whether to propose CBOMs as evidence to the owners of such models is Q44, and is an outreach decision as much as a methodology one.

**Proposed.**

[← Operation](../operation/) [Next: Proposing a Use Case →](../proposing/)
