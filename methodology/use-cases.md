---
title: Starting from a Use Case
sideMenu: true
weight: 15
aliases:
- /cbom/methodology/use-cases.html
linkTitle: Starting from a Use Case
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A profile exists to support a decision. A use case names who makes the decision and what the decision is. Every profile has to start from a use case, because the decision determines which facts the CBOM must contain. The use cases the working group has identified, and its worked examples, are in the [Use Cases](../../use-cases/) section.

## What a use case is

A use case consists of a consumer and a decision. The consumer is whoever reads the CBOM and has to act on it. The decision is a choice between stated actions. To make the decision, the consumer has to answer a small number of questions, and the CBOM has to help answer them. Three things are needed before a profile can be written:

-   **The consumer**, named by role: a buyer, a vulnerability responder, a migration lead.
-   **The actions being chosen between.** A decision that can be answered in only one way is not a decision. A profile written from such a decision has no principled point at which to stop.
-   **The questions** the consumer has to answer to choose. Step 3 of [Method](../method/) turns each into the facts a CBOM must carry.

A sector, a product category or a field offered by a CBOM format is not a use case. Each of these can be the setting for a use case. Vocabulary specific to a sector belongs in the profile written for that use case.

## Why the use case comes first

A profile answers the question "what must be disclosed so that a particular decision can be made". That is a different question from "what cryptography does this contain". The first question cannot be answered in the abstract, because an attribute that is indispensable for one purpose is irrelevant to another. For example, a vulnerability responder needs the implementing library and can ignore endpoint roles. A procurement team checking an interface baseline needs the endpoint roles and can ignore the implementing library.

Starting from the use case also sets a limit on what must be disclosed. Without a stated purpose there is no principled way to decide where a profile stops. The profile then drifts in one of two directions. Either it demands everything, which vendors reasonably resist, or it settles on a lowest common denominator that supports no decision at all. A profile with a named consumer and a named decision can be assessed on its merits.

## One document, several profiles, and the limit

Different consumers can apply different profiles to the same unchanged CBOM. A supplier that produces one complete document may find it evaluated against a procurement profile by one customer and a vulnerability profile by another, with nothing republished in between.

That holds only while each profile selects from facts the document already carries. Some profiles add facts that the baseline profile does not define. For example, knowing which algorithms an interface uses today answers none of a migration planner's questions. A migration profile therefore adds facts about capability, instead of selecting among the facts the baseline already defines. A document produced against the baseline cannot be evaluated against such a profile at all, because the added facts were never collected. [Profile](../profile/) describes these differences as the depth and coverage axes of composition.

In practice, therefore, "supply a CBOM" is not a single request. A buyer has to name the profile. A supplier that has produced baseline documents has not met a migration request by producing more of them. The [Use Cases](../../use-cases/) section groups its use cases by this distinction. It also groups them by two other distinctions that follow from the same starting point: whether the producer is the supplier of a product or the operator of a system, and whether the reader relies on the document as evidence.

## Where the use cases are

The register of use cases, their descriptions and the worked examples are in the [Use Cases](../../use-cases/) section. The nginx example used throughout this methodology illustrates its concepts. The worked examples in the Use Cases section apply those concepts to real products.

Entries once listed on this page, by their former numbers: [1 PQC migration readiness and planning](../../use-cases/change-planning/#pqc-migration) · [2 Procurement and tender conformance](../../use-cases/disclosure/#procurement-and-tender-conformance) · [3 Vulnerability management and incident response](../../use-cases/disclosure/#vulnerability-management-and-incident-response) · [4 Regulatory and compliance reporting](../../use-cases/assurance/#regulatory-and-compliance-reporting) · [5 Continuous integration quality gate](../../use-cases/#what-is-not-a-use-case) · [6 Crypto-agility assessment](../../use-cases/change-planning/#crypto-agility-assessment) · [7 Supply-chain transparency](../../use-cases/disclosure/#supply-chain-transparency) · [8 Mergers and third-party risk due diligence](../../use-cases/disclosure/#mergers-and-third-party-risk-due-diligence) · [9 IoT device estates](../../use-cases/change-planning/#iot-device-estates) · [10 Managed and cloud service disclosure](../../use-cases/operation/#managed-and-cloud-service-disclosure) · [11 Service assurance](../../use-cases/disclosure/#service-assurance) · [12 Substation automation](../../use-cases/change-planning/#substation-automation-ot) · [13 PKI and certificate estate migration](../../use-cases/change-planning/#pki-and-certificate-estate-migration) · [14 Code and firmware signing migration](../../use-cases/change-planning/#code-and-firmware-signing-migration) · [15 Stored data and archive protection](../../use-cases/operation/#stored-data-and-archive-protection) · [16 Shared-trust network migration](../../use-cases/change-planning/#shared-trust-network-migration).

[← Vulnerabilities](../vulnerabilities/) [Next: Method →](../method/)
