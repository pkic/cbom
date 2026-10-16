---
title: Disclosure
sideMenu: true
weight: 2
aliases:
- /cbom/use-cases/disclosure.html
linkTitle: Disclosure
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

In these use cases, the profile works only with facts that the interface disclosure baseline already defines. The baseline is the common profile that every profile in this group extends. Each profile chooses which of the baseline's facts are mandatory and makes some of its rules stricter. The orientation is `inventory`, which means the document reports what the product uses today. One document can answer every profile in this group, provided it meets the baseline and names the implementing library. The supplier does not need to reissue it for each profile.

The grouping is proposed in draft decision 0023 and is not yet settled.

## What the group shares

Every profile here extends the [interface disclosure baseline](../../methodology/profile/), or is one of its depths. A depth is a version of the baseline that asks for more or fewer of the same facts. The facts are the baseline's: what the product is, which interfaces it exposes, the protocol and version of each, the algorithms for each cryptographic job, the endpoint roles, the implementing library, the lifecycle stage of the report, and whether the list is complete. A profile in this group chooses which of them are mandatory, removes the producer's permission to withhold an attribute (to mark it as deliberately not disclosed), or adds a structural rule about which kinds of interface must be present. It does not add new attributes.

Because no profile in this group adds new attributes, one document can serve several consumers. A buyer, a vulnerability responder and an acquirer can each apply their own profile to the same unchanged document. The depths described in [Maturity](../../methodology/maturity/) apply here too. The entry depth is the lowest level and asks for fewer of the same facts. It suits cases where broad coverage matters more than detail, as in due diligence.

This reuse works in one direction only. A document produced only for this group cannot answer a [change-planning](../change-planning/) profile. It does not contain the capability facts, such as what each interface could support, because nobody collected them. A document produced for change planning answers this group as well.

## Worked examples

| Page | What it shows | State |
| --- | --- | --- |
| **[Procurement](../procurement/)** | A procurement profile applied, unchanged, to the Keycloak document written for PQC migration: one document read by two profiles | Drafted. The rules file is well-formed. Tool verdicts are waiting for changes to the evaluator |

## Attributes emphasised

The profiles in this group draw on the same attributes. They differ in which attributes they make mandatory. The table shows where each profile puts its emphasis.

| Use case | lifecycleStage | implementationPurl | keyExchange / auth | interfaceType | disclosure markers |
| --- | --- | --- | --- | --- | --- |
| Supply-chain transparency | ● | ○ | ● | ● | ● |
| Procurement | ○ | ● | ● | ● | ○ |
| Vulnerability / incident | ○ | ● | ○ | ○ | ○ |
| M&A due diligence | ○ | ● | ● | ○ | ● |

● emphasised by a profile for this use case · ○ relevant but not the focus. Placeholders have no row until they are drafted.

Supply-chain transparency does *not* emphasise `implementationPurl`, the identifier of the implementing library. That use case limits how much a profile may ask of a supplier. The library is the attribute a supplier is most likely to withhold. For that reason the baseline marks it as withholdable. Procurement does emphasise it, because the drafted procurement profile removes that permission. The migration profile removes it too.

## The use cases in this group

### Supply-chain transparency

A supplier at any tier needs to tell its customers what cryptography its product uses, and would prefer to do so once rather than in a different format for each customer. Downstream, an integrator needs disclosures it can compare across suppliers.

A disclosure baseline meets this need. What makes this use case unusual is that it sets an upper limit on what a profile may ask. A supplier must be able to satisfy the profile without exposing information it has a legitimate reason to protect. For that reason it matters here that an attribute can be marked as withheld (deliberately not disclosed), rather than silently left out.

### Procurement and tender conformance

An operator states cryptographic requirements in a tender and needs to check what comes back without reading it by hand. Today this is done with security questionnaires, whose answers are prose and cannot be compared between vendors. A profile expresses the requirement in a form a machine can evaluate, and the vendor's CBOM is the response to it.

Some of the requirements concern the structure of the document, not only its attributes. In addition to a description of each interface, a procurement profile usually requires certain kinds of interface to be present. This is how it catches a vendor that describes its service interface and says nothing about how the product is administered.

Drafted as a worked example on the [Procurement](../procurement/) page.

### Vulnerability management and incident response

An advisory is published against a cryptographic library. The question is which services are affected, and it has to be answered in hours rather than weeks. This use case has the least tolerance for manual work.

Almost everything depends on one attribute: the identifier of the implementing library, expressed in a form that can be matched against a vulnerability feed. Endpoint roles, interface types and lifecycle stages contribute little here. A profile written for this purpose is deliberately narrow.

It is also the only use case in this list that the baseline hinders. The baseline allows a producer to withhold the library identifier, which is the attribute this use case depends on. [Vulnerabilities](../../methodology/vulnerabilities/) sets out what a CBOM contributes when an advisory lands, which kinds of weakness it is the only evidence for, and why no profile for this purpose has been written yet.

### Regulatory and compliance reporting

An organization must demonstrate its cryptographic position against a framework such as the EU Cyber Resilience Act, NIS2, the BSI technical guidelines, or a national directive. The consumer is an auditor or regulator who did not generate the data and cannot ask follow-up questions of the system.

A profile encodes what a given framework expects, so that conformance can be evidenced by a dated artifact that an auditor can re-check. Because the reader is external, provenance and lifecycle stage carry more weight than usual. A reported position is only meaningful if it says when it was derived and from what. A jurisdiction-specific profile also lets a global vendor satisfy the requirement once and report against it in several places.

### Mergers and third-party risk due diligence

An acquiring organization, or one onboarding a significant partner, needs a view of cryptographic exposure across an estate it does not operate and cannot inspect directly. The work is usually done under time pressure and with limited cooperation.

Covering the whole estate matters more than detail on each product. A broad disclosure across the estate, with the absence of data recorded explicitly rather than left blank, tells the assessor where the risk concentrates: deprecated algorithms still in use, and cryptography bound to hardware that will not be upgraded.

### Managed and cloud service disclosure

A customer relies on a service it does not operate: an identity provider, a key management service, a payment gateway, a managed network. It has to decide whether to rely on it, and what to require of the provider. Here the producer is the operator of the service, not a vendor shipping a product. The operator knows the service's configuration and deployment, which a vendor cannot see.

A profile can therefore ask more of the operator than of a vendor. That is the reason to develop this use case separately. The operator can report the lifecycle stage `configured` or `observed`. It can also state facts that the product profiles exclude because they depend on the deployment. **Proposed.** So far only the consumer and the decision are named.

### Service assurance

An assurance team responsible for customer-facing services, including critical communications, needs to know which services a cryptographic weakness or a planned change reaches. The facts about each component already exist in that component's document. What is missing is the mapping from components to the services they carry.

This use case therefore needs a system overlay, not a new set of attributes. An overlay is a document that references the component documents rather than repeating them. Here the overlay states which services depend on which interfaces. The use case comes from the telecom sector paper. Its structure is the same as that of the substation overlay. **Proposed.**

[← Use Cases: Overview](../) [Next: Procurement →](../procurement/)
