---
title: CBOM Profiles
sideMenu: true
weight: 0
summary: Illustrative working draft methodology, worked use cases, references, tools,
  and meeting material. Not an adopted deliverable.
aliases:
- /cbom/
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

PKI Consortium · Working Group

The working home of the PKI Consortium CBOM Profiles Working Group. We are developing a single deliverable: a vendor-neutral, format-independent methodology for defining CBOM *profiles* — one that any sector can follow and that maps cleanly onto both CycloneDX and SPDX.

[Read the methodology](methodology/introduction/) [See what we're working on](issues/) [Read the charter](https://pkic.org/wg/cbom/charter/)

## What we're building

A profile, not another format.

A **CBOM profile** is a constrained, use-case-specific specification of what a Cryptography Bill of Materials should contain, how its fields are interpreted, and what validation rules apply. Our methodology describes how to define one — independently of any single base standard.

Profiles are designed to **map onto existing BOM standards** such as CycloneDX and SPDX rather than compete with them. The PKIC output is intended to become the reference any industry consults when creating a CBOM profile for a particular use case.

## The methodology, worked through

The draft, explained against a subject anyone can check.

The [methodology documentation](methodology/) sets out the approach in full and applies it to an ordinary example: an **nginx** web server, its CBOM expressed in CycloneDX 1.7, checked against a small product-independent profile. One CBOM conforms and one does not, and you can run the check yourself.

It covers the vocabulary the methodology rests on, how a profile is written and validated, how the same profile maps onto CycloneDX and SPDX, how cryptographic weakness is communicated alongside a CBOM rather than inside one, what happens to older CBOM files, and how profiles are governed over time. Start with [the introduction](methodology/introduction/), the [model](methodology/model/), the [profile itself](methodology/profile/), or the [conformance example](methodology/demo/).

## Explore the project

### [Methodology](methodology/)

*Working draft*

The deliverable itself — profiles, the relationship model, format mappings and governance — with a worked nginx example and a conformance check you can run.

### [Use cases](use-cases/)

*1 developed · 3 drafted*

Every purpose a profile has been proposed for, in four groups: disclosure, change planning, operation and assurance. PQC migration on Keycloak is developed in full; procurement, IoT device estates and substation automation are drafted; the rest are described or held as placeholders.

### [Issues](issues/)

*13 aspects*

The thirteen methodology aspects, each tracked as a discussion block. This is where the work happens — read a topic, weigh in, or raise one.

### [References](references/)

*73 sources*

The evidence base — standards, regulation and guidance the methodology aligns to. The source register provides category, status, and jurisdiction filters.

### [Tooling](tooling/)

*39 tools*

Software that generates, consumes, validates or analyses CBOMs, each linked to where its maintainer states CBOM support. A listing, not an endorsement.

### [Meetings](meetings/)

*Agendas and recordings*

When the group meets and what it plans to settle. Upcoming meetings carry an agenda; past ones carry the recording and the slides presented, ready to download.

### [Contributing](contributing/)

*No install required*

How to take part — join a discussion, raise an aspect topic, or suggest a reference by email. No command line, no YAML.

### [Working group](/wg/cbom/)

*PKI Consortium*

The charter, membership and standing of the CBOM Profiles Working Group within the PKI Consortium.

## Why a profile is needed

The gap the methodology fills.

Almost every jurisdiction now requires organisations to hold **a cryptographic inventory**. Almost none of them says what that inventory should look like.

India's CERT-In guidelines are the exception that proves the rule — they name the CBOM outright. Everywhere else the obligation is stated and the format is left open. A neutral CBOM profile is what turns "keep an inventory" into something producers and consumers can actually exchange and verify. The [reference register](references/) is the evidence base for that argument.

## How we work

Deliberation, decision and artifact are kept deliberately separate.

### Deliberation

The open argument — options, trade-offs and questions — lives in a GitHub [Issue](https://github.com/pkic/cbom/issues) or [Discussion](https://github.com/pkic/cbom/discussions).

### Decision

The agreed outcome, with its reasoning, is captured as a short record in the `/decisions` folder — the project's permanent memory.

### Artifact

The specification text itself changes only through a pull request, so every edit is reviewed line by line. We work by lazy consensus.

## Take part

You don't need to be a developer or install anything. If you can use a web forum, you can contribute fully — pick an aspect and say your piece.

[How to contribute](contributing/)
