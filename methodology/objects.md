---
title: Objects
sideMenu: true
weight: 8
aliases:
- /cbom/methodology/objects.html
linkTitle: Objects
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The methodology defines about a dozen objects, each introduced on the page where it is first needed. They are listed together here. For each object, the list gives the party or tool that creates it and how it is identified. It also names what the methodology deliberately leaves out. Nothing here is new: every object is defined on another page.

[Model](../model/) covers the subject matter, meaning the cryptography a document describes. This page covers the documents themselves and the things that check them.

## What there is

| Object | What it is | Written by |
| --- | --- | --- |
| **Subject** | The product, service or component a document describes. A profile declares which kind it accepts as its `subjectType`. | nobody; it is the thing being described |
| **Interface** | A cryptographic relationship the subject exposes at its boundary. Most rules apply to interfaces. See [Model](../model/). | producer, as part of a document |
| **CBOM revision** | One revision of the record for one subject, in one carrier format (the document format that carries the CBOM). It is extracted from an inventory and does not exist on its own. See [Inventory](../inventory/). | producer |
| **Variant** | A revision exists in a public form and a restricted form. The two variants differ in who may hold them. Where the restricted variant carries a value, the public variant carries a marker in its place. See [Confidentiality](../confidentiality/). | producer |
| **Profile** | The minimum reporting requirements for one stated consumer making one stated decision. A profile is a rules file, not a schema. | profile author |
| **Profile family** | A set of profiles in which each profile extends another. The profiles are ordered by [depth](../maturity/), meaning how much each one requires a producer to disclose. Each profile contains all the requirements of the one below it. The shallowest is the entry profile. A profile that changes the consumer decision is a branch: it starts a separate line instead of adding a level (a rung) to the existing one. | nobody declares it; it follows from each profile's `extends` field |
| **Rule** | One requirement. Rules with ids beginning `P` are evaluated once per product. Rules beginning `I` are evaluated once per interface. Rules beginning `G` are evaluated once for each entry in a group. A rule belongs to its own profile and is cited as `tag#id`. | profile author |
| **Vocabulary** | A controlled list a rule constrains values against, such as the cryptographic purposes. | profile author, or inherited |
| **Conformance report** | The full result of evaluating one document against one profile. It gives the result for each rule and the disclosure state of each rule. | a validator, where the evaluation ran |
| **Conformance claim** | A portable record of one or more evaluations. It is bound to a document by the document's digest. The claim is the artifact that is passed from one organisation to another. | whoever ran the evaluation |
| **Policy** | Held outside the CBOM, and versioned. Holds the judgements a CBOM deliberately does not carry, such as whether an algorithm is still acceptable. See [Policy Evaluation](../policy-evaluation/). | the consuming organisation |
| **Vulnerability statement** | Held outside the CBOM. It is linked to a document rather than contained in one. It cites the document by the same digest that a conformance claim uses to bind to it. Conformance asserts nothing about the vulnerability statement. See [Vulnerabilities](../vulnerabilities/). | whoever issues it, usually not the producer |

## How they connect

{{< figure src="../assets/figures/methodology-objects-1.svg" alt="A subject exposes interfaces, which are recorded in a CBOM revision that exists as a public and a restricted variant. A profile, belonging to a family and holding rules, is evaluated against the revision to produce a report and then a claim. A separate external policy reads the same revision and produces judgements the revision does not carry." >}}

*A profile constrains a revision and is evaluated against it. Policy reads the same revision and produces judgements the revision does not carry. A vulnerability statement cites the revision by the same digest that a claim uses to bind to it.*

## How each one is identified

How each object is identified is a recurring question, and the answers were spread across five pages. Identity matters because a conformance claim has to be reproducible years later by somebody who was not present at the original evaluation.

| Object | Identified by | Stable across |
| --- | --- | --- |
| Subject | An identifier in the form the profile names, usually a `purl` | revisions of the document |
| Interface | `interfaceId`, chosen by the producer. No profile constrains it. | nothing; it is a label |
| CBOM revision | Content revision, and a digest when a claim or a vulnerability statement cites it | nothing; a new revision is a new document |
| Profile | `profileId` and version, cited together | a published version is never altered |
| Profile, in a citation | `profileTag`, the short handle | the life of the profile |
| Rule | `tag#id`, such as `interface-disclosure#I9`. The id belongs to the profile that introduced it, not to one that later tightened it. | every version after it appears; a released id is never reused |
| Claim | The digest of the document it is about | nothing; a new revision needs a new claim |
| Policy | Its own version, recorded alongside any judgement it produced | whatever the consuming organisation decides |

## Two axes that get confused

Capture phase and revision state were described by a single word until [decision 0021](https://github.com/pkic/cbom/blob/main/decisions/0021-one-word-one-meaning.md). They are different things and must be kept apart.

**Capture phase** belongs to a fact. `lifecycleStage` says whether a value was intended, implemented, configured or observed. This tells a reader how much weight the value carries. It can differ between two attributes in the same document. See [Lifecycle Data](../lifecycle/).

**Revision state** belongs to a document. A document can be created, signed, published or superseded. Its revision state is the same for every attribute in the document. Governance controls how a document moves from one state to the next. See [Governance](../governance/).

## What is deliberately not an object here

**A judgement.** A judgement states, for example, whether an interface is adequate or how mature a supplier's disclosure is. Policy produces the judgement at evaluation time. The judgement records the policy version and the date the policy was applied. Storing a judgement in a document would freeze an answer whose criteria change over time. A depth is a profile. A maturity level is a judgement derived from a depth.

**An attestation.** Nothing here establishes that a disclosed value is true. A signature shows where a document came from and that it has not been altered. A claim shows what was evaluated. A producer who states the wrong protocol version still produces a document that can be signed, passes validation, and has a signature that verifies.

**A registry.** Profiles, documents and claims all have to be stored and served somewhere, and the model says nothing about where. Storage is left to whoever operates the inventory. The only requirement placed on that operator is the archive obligation in [Governance](../governance/).

[← Model](../model/) [Next: Profile →](../profile/)
