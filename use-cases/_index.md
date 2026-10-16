---
title: Use Cases
sideMenu: true
weight: 20
aliases:
- /cbom/use-cases/index.html
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A CBOM profile is written for someone who has a decision to make. A use case names that person and that decision: a buyer comparing tenders, a responder tracing an advisory, a grid operator planning a migration. This section collects the use cases the working group has identified. The most developed ones are taken further: each is turned into a profile, the profile is applied to a real product, and the resulting documents can be checked against it.

| Kind of page | What it gives you |
| --- | --- |
| **Group pages** | What the use cases in a group have in common, and a description of each: [Disclosure](disclosure/), [Change planning](change-planning/) |
| **Worked examples** | One use case taken through to a profile, applied to a real product, with a document that conforms and one that does not. The only complete one is [PQC migration](pqc-migration/), applied to Keycloak |
| **Writing a use case** | [How to propose a use case](proposing/), and the [template](template/) a worked example follows |

## Use case groups

Use cases are split into groups. A group clusters use cases that share a common goal and need similar information in the CBOM. There are currently two groups. In [Disclosure](disclosure/), the goal is to know what cryptography a product uses. In [Change planning](change-planning/), the goal is to decide how to change it. The table below compares the two groups. Two further groups, [Operation](operation/) and [Assurance](assurance/), are proposed but not yet settled.

| [Disclosure](disclosure/): know what a product uses | [Change planning](change-planning/): decide how to change it |
| --- | --- |
| The profile chooses which facts a CBOM must carry from the set every CBOM already describes: interfaces, protocols, algorithms and the libraries that implement them. | The profile adds facts a basic CBOM does not have: what each interface could support, what is blocking it, and what changing it costs. |
| One CBOM from a supplier can answer every profile in this group. | A supplier has to produce a richer CBOM. That CBOM then answers the disclosure profiles as well. |
| Procurement, vulnerability response, compliance reporting, due diligence. | PQC migration, IoT device estates, substation automation, crypto-agility. |

Use cases are not grouped by sector. A telecom operator and a grid operator planning a migration make the same kind of decision, so they share a use case. Terms specific to a sector go into the profile, not into a separate use case.

## All use cases

| Use case | Who decides, and what | Group | Status | Worked example |
| --- | --- | --- | --- | --- |
| [Procurement and tender conformance](disclosure/#procurement-and-tender-conformance) | A buyer: whether a tender's cryptographic disclosure is complete enough to compare and hold the supplier to | Disclosure | Draft worked example | [Read](procurement/) |
| [Supply-chain transparency](disclosure/#supply-chain-transparency) | A supplier: how to disclose once to every customer | Disclosure | Described | — |
| [Vulnerability management and incident response](disclosure/#vulnerability-management-and-incident-response) | A responder: which services a published advisory reaches | Disclosure | Described | — |
| [Regulatory and compliance reporting](disclosure/#regulatory-and-compliance-reporting) | An auditor or regulator: whether a position meets a framework | Disclosure | Described | — |
| [Mergers and third-party due diligence](disclosure/#mergers-and-third-party-risk-due-diligence) | An acquirer: where the cryptographic risk sits in an estate it cannot inspect | Disclosure | Described | — |
| [Managed and cloud service disclosure](disclosure/#managed-and-cloud-service-disclosure) | A customer: whether to rely on a service it does not run | Disclosure | Proposed | — |
| [Service assurance](disclosure/#service-assurance) | An assurance team: which customer services a weakness or a change reaches | Disclosure | Proposed | — |
| [PQC migration](change-planning/#pqc-migration) | A migration lead: which interfaces to migrate, in what order, at what cost | Change planning | Worked example | [Read](pqc-migration/) |
| [IoT device estate](change-planning/#iot-device-estates) | A fleet operator: for each device model, update, replace, shield or accept | Change planning | Draft worked example | [Read](iot/) |
| [Substation automation (OT)](change-planning/#substation-automation-ot) | A grid operator: for each communication path, migrate, shield or replace | Change planning | Draft worked example | [Read](substation/) |
| [Crypto-agility assessment](change-planning/#crypto-agility-assessment) | An architect: how hard replacing an algorithm would be | Change planning | Described | — |
| [PKI and certificate estate migration](change-planning/#pki-and-certificate-estate-migration) | A PKI owner: which hierarchies move, in what order, while relying parties catch up | Change planning | Proposed | — |
| [Code and firmware signing migration](change-planning/#code-and-firmware-signing-migration) | A publisher: when signing keys can move, given the verifiers already deployed | Change planning | Proposed | — |
| [Stored data and archive protection](change-planning/#stored-data-and-archive-protection) | A data owner: which stores and archives to re-encrypt first | Change planning | Proposed | — |
| [Shared-trust network migration](change-planning/#shared-trust-network-migration) | A scheme operator: when every participant can move to a new trust anchor | Change planning | Proposed | — |

**Worked example**: a checked profile with conforming and non-conforming documents. **Draft worked example**: written in that shape, not yet settled. **Described**: consumer, decision and what the profile needs are written. **Proposed**: consumer and decision named. Full definitions are on [Proposing a use case](proposing/#status).

## What is not a use case

Two things are often suggested as use cases. Both are ways of applying a profile instead.

-   **Continuous integration quality gate.** A pipeline fails a build when a CBOM does not conform. Any profile can be applied this way. What the gate needs is a validator that returns a usable exit status and report. This is covered in [Conformance](../methodology/conformance/) and the [Demo](../methodology/demo/).
-   **Change impact between versions.** Comparing two CBOMs of the same product to see what changed. This is a comparison between two documents. It is covered in [Versioning](../methodology/versioning/).

## How this section relates to the methodology

The [methodology](../methodology/) is the working group's deliverable. It says how to define a profile, and [Starting from a use case](../methodology/use-cases/) explains why every profile begins with a consumer and a decision. The methodology illustrates its concepts with a small nginx example. It does not list any use cases. Everything about particular use cases, including the worked examples, is in this section.

The worked examples use the draft profiles of decision 0022 (interface disclosure baseline v0.8, PQC migration v0.7 and its extended depth, a more detailed level of the same profile). The methodology still describes the published versions (v0.7 and v0.6). The methodology and the worked examples will match once the drafts are adopted.

[Next: Disclosure →](disclosure/)
