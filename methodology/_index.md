---
title: Overview
sideMenu: true
weight: 10
aliases:
- /cbom/methodology/index.html
linkTitle: Methodology
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A Cryptography Bill of Materials (CBOM) profile defines the subset of attributes that a CBOM is required to contain for a stated objective. It establishes a minimum reporting requirement rather than exhaustive coverage. This documentation describes the profile methodology using a worked example: an nginx web server whose CBOM is expressed in CycloneDX 1.7 and evaluated against a small, product-independent profile.

**Meeting this for the first time?** Read the [Introduction](introduction/) first. It follows one product, its CBOM and one question a buyer asks about it, from start to finish. It takes about five minutes to read. This overview is easier to use once you have read it.

## Scope of this documentation

The example profile, the Interface Disclosure Baseline, requires a product to declare its cryptographic interfaces, including the interface used to configure the product, and to describe each one. It does not reference a specific product or interface instance, and therefore applies to any product that terminates TLS, SSH, or IPsec. nginx serves only as the example subject. A single CBOM may satisfy several profiles at once.

The sidebar lists the sections in the order a newcomer should read them. Concrete examples come first. Definitions come last, under Reference, so that you can look up a term when it is unfamiliar.

## Suggested reading paths

Each section can be read on its own. You can read the sections in sidebar order, or follow one of the three routes below. Each route suits a particular role, and each assumes you have read the [Introduction](introduction/).

### Producing CBOMs

For a vendor, or a build or release team.

**Read in this order:** [Model](model/) → [Profile](profile/) → [Maturity](maturity/) → [Confidentiality](confidentiality/) → [Formats](formats/) → [Versioning](versioning/)

-   **Model:** the terms used throughout.
-   **Profile:** what a profile requires you to declare.
-   **Maturity:** which profile in a family to aim for first, and how to move on to a more detailed one.
-   **Confidentiality:** which information you publish openly, which you release only under agreement, and how a profile allows for that.
-   **Formats:** where each attribute is written in a CycloneDX or SPDX document.
-   **Versioning:** what happens to CBOMs you have already published when a format or profile version changes.

### Requiring and reading CBOMs

For an operator or buyer assessing a supplier, an auditor or regulator.

**Read in this order:** [Use Cases](use-cases/) → [Challenges](challenges/) → [Profile](profile/) → [Conformance](conformance/) → [Maturity](maturity/) → [Confidentiality](confidentiality/) → [Vulnerabilities](vulnerabilities/) → [Governance](governance/)

-   **Use Cases:** what a profile can be written to require.
-   **Challenges:** why the CBOM data supplied today is hard to use.
-   **Profile** and **Conformance:** what a passing result confirms, and what it does not. Conformance matters most for this role.
-   **Maturity:** how to write a requirement that a supplier can meet now, with a date for meeting a more demanding profile later.
-   **Confidentiality:** why a conforming CBOM can still have information withheld, and how to ask for the more complete version.
-   **Vulnerabilities:** how to use a CBOM when a security advisory is published, and why a passing result says nothing about whether the cryptography is safe.
-   **Governance:** the signing, provenance and retention that a conformance claim relies on.

### Writing or approving a profile

For working group members, sector bodies.

**Read in this order:** [Model](model/) → [Method](method/) → [Profile](profile/) → [PQC Migration](../use-cases/pqc-migration/) → [Governance](governance/)

-   **Model:** the terms used throughout.
-   **Method:** the procedure for writing a profile.
-   **Profile:** an example of the result.
-   **PQC Migration:** one profile taken through the procedure from start to finish.
-   **Governance:** what happens after a profile is published.

Two sections are not part of any route. Read them when the topic comes up. [Data Exposure](data-exposure/) is a design note on the harvest-now-decrypt-later threat and the data attributes needed to measure it. [Related Work](related-work/) explains how CBOM profiles relate to other PKI Consortium work.

## Contents

### [Introduction](introduction/)

*start here*

A worked example. A buyer asks a question about one product, and the product's CBOM cannot answer it. The example shows why, and how a profile makes the answer possible.

### [Demo](demo/)

*interactive*

Review four example CBOMs and open the interactive source demo to evaluate them against the example profile. They show a conforming document, a document with a missing interface, the four disclosure outcomes (value, withheld, unknown and undeclared), and a product with no management interface.

### [Use Cases](use-cases/)

*applied*

Why every profile starts from a use case: a named consumer and the decision that consumer has to make.

### [Challenges](challenges/)

*background*

What SBOM adoption has taught, the further difficulties that are specific to cryptography, and the limits of current CBOM standards. These problems are the reason for a profile-based approach.

### [Inventory](inventory/)

*background*

How a CBOM differs from a cryptographic inventory. CBOMs feed an inventory. An organization can also extract a CBOM from its inventory for a particular consumer: an internal team, a client or auditor, or a customer in its supply chain.

### [Lifecycle Data](lifecycle/)

*background*

Cryptographic facts are captured at four stages: design, build, deployment and operation. What each stage can show, who captures it, and why the stage is recorded with each fact.

### [Model](model/)

*concept*

The three terms the methodology is built on: a cryptographic relationship (where cryptography is applied between two parties), the endpoints at each end, and the cryptographic assets it uses. Illustrated with worked examples.

### [Objects](objects/)

*concept*

A reference list of every object the methodology defines. For each one: which party or tool creates it and how it is identified. Also lists what the methodology deliberately leaves out.

### [Profile](profile/)

*core*

The rules of the example profile, for the product as a whole and for each interface. The same rules serve two purposes: a specification for the party that produces a CBOM, and a checklist for the party that checks it.

### [Conformance](conformance/)

*core*

What can be assessed, what a pass or fail result means, who may claim conformance, how a claim is recorded, and what a passing result does not tell you.

### [Maturity](maturity/)

*concept*

How to publish a family of profiles that ask for progressively more detail. A supplier can start with a profile it can meet now and move to more demanding ones later. A buyer can see which profile a supplier has met.

### [Confidentiality](confidentiality/)

*concept*

Most suppliers will publish one version of a CBOM and release a more complete version only under agreement. How a profile marks the attributes a supplier may withhold, and what a consumer can tell from the version it holds.

### [Policy Evaluation](policy-evaluation/)

*core*

Why a judgement such as "this interface is post-quantum safe" is not stored in a CBOM. The criteria change over time, so the judgement is made by an external, versioned policy applied to the facts in the CBOM.

### [Vulnerabilities](vulnerabilities/)

*concept*

How information about cryptographic weaknesses is linked to a CBOM. The three documents involved (the CBOM, the advisory and the VEX statement) and who writes each. The difference between an implementation bug and a weak choice of algorithm. What a conforming CBOM does not tell you.

### [Method](method/)

*core*

The procedure for writing a profile: twelve steps in five stages (scope, content, rules, realisation and proof). Each stage has tests to apply, and the common mistakes are listed.

### [Worked use cases](../use-cases/)

*another section*

Use cases taken through to a finished profile, in a separate section. PQC migration is complete. IoT device estates, substation automation and procurement are drafts.

### [Formats](formats/)

*mapping*

Where each attribute of one profile is written in CycloneDX and in SPDX. Neither format has an object that represents an interface, so both attach interface attributes to the protocol asset, and some facts about a connection cannot be recorded.

### [Data Exposure](data-exposure/)

*design note*

Traffic recorded today can be decrypted once a quantum computer exists. The algorithms in a CBOM do not show this exposure on their own: it also depends on how long the data must stay confidential and whether the traffic can be captured. A design note on the data attributes needed to measure it.

### [Versioning](versioning/)

*operations*

Three things carry their own version: the document format (for example CycloneDX 1.7), the profile, and the CBOM's content. How a profile declares the format versions it accepts, so that a tool can check this automatically.

### [Governance](governance/)

*operations*

How CBOMs and profiles are managed over their lifetime: signing and provenance, how a CBOM relates to an SBOM, change control, retention, and who maintains a profile after publication.

### [Terms](terms/)

*reference*

Definitions of the terms used across the methodology, every attribute and its permitted values, and the terms the methodology considered and chose not to use, with the reason for each.

### [Related Work](related-work/)

*reference*

How CBOM profiles relate to the PQC Maturity Model and other PKI Consortium work, and where one depends on another.

### [Files](files/)

*reference*

The profile rules file, the example CBOMs and the validator, with the commands to reproduce every result in this documentation.

**Note for standards authors.** The numbered draft of the methodology orders its clauses differently from the sidebar. In the draft, Scope, Terms and Conformance come early, because a normative document must define its terms before it uses them. The working group maintains both orders.

This material is illustrative and is intended to demonstrate the methodology. It is not a normative deliverable of the PKIC CBOM Profiles Working Group. Field names are aligned to CycloneDX v1.7 / ECMA-424 (2nd Edition) and should be validated against the current schema before operational use.

[← Introduction](introduction/) [Next: Demo →](demo/)
