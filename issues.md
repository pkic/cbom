---
title: Issues
sideMenu: true
weight: 70
aliases:
- /cbom/issues/
description: The methodology is built one aspect at a time. Each aspect is a discussion
  block — a single question the working group needs to settle — tracked as a GitHub
  issue.
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

**New to how we work?** A topic moves through four stages, shown by its `status:` label — *Raised → Deliberating → Converging → Decided*. Open exploration starts as a [Discussion](https://github.com/pkic/cbom/discussions); once it narrows to a concrete choice it becomes an [Issue](https://github.com/pkic/cbom/issues), which is closed and linked to the change that implements it. The decision rule is **lazy consensus**.

[All issues on GitHub ↗](https://github.com/pkic/cbom/issues) [Discussions ↗](https://github.com/pkic/cbom/discussions) [Raise a topic ↗](https://github.com/pkic/cbom/issues/new/choose)

## The thirteen aspects

From Section 3 of the scoping document, *Defining CBOM Profiles*. Each aspect has **one** canonical tracking issue — please comment on the existing thread rather than opening a parallel one.

1.  3.1 [Profile objective & scope](https://github.com/pkic/cbom/issues/4) Deliberating

    What a given profile is for and where its boundaries lie — the use case it serves and what it deliberately leaves out.

    [Issue #4](https://github.com/pkic/cbom/issues/4) · orientation: both

2.  3.2 [Profile identity & metadata](https://github.com/pkic/cbom/issues/5) Deliberating

    How a profile names and versions itself so it can be referenced, compared and pinned to a specific revision.

    [Issue #5](https://github.com/pkic/cbom/issues/5) · orientation: both

3.  3.3 [Format-independent attribute model](https://github.com/pkic/cbom/issues/1) Deliberating keystone

    The core set of cryptographic attributes a profile constrains, defined independently of any serialization format. Most other aspects build on this — settle it first.

    [Issue #1](https://github.com/pkic/cbom/issues/1) · orientation: both

4.  3.4 [Obligation levels & conformance semantics](https://github.com/pkic/cbom/issues/6) Deliberating

    How MUST / SHOULD / MAY (BCP 14) apply to profile attributes, and what "conforming" actually means for a producer and a consumer.

    [Issue #6](https://github.com/pkic/cbom/issues/6) · orientation: both

5.  3.5 [Conformance & validation](https://github.com/pkic/cbom/issues/7) Deliberating

    How a CBOM is checked against a profile — the validation rules and the machinery that turns a profile into a pass/fail result.

    [Issue #7](https://github.com/pkic/cbom/issues/7) · orientation: both

6.  3.6 [Mapping to serialization formats (CycloneDX, SPDX)](https://github.com/pkic/cbom/issues/2) Deliberating

    cross-cutting

    Normative mappings from the format-independent model onto CycloneDX and SPDX. Cross-cutting — discussed here and linked from other aspects rather than re-argued.

    [Issue #2](https://github.com/pkic/cbom/issues/2) · orientation: both

7.  3.7 [Vocabularies & normalisation](https://github.com/pkic/cbom/issues/3) Deliberating

    cross-cutting

    Agreeing identifiers and value vocabularies (e.g. the CycloneDX Cryptography Registry, purl) so the same thing is named the same way. Cross-cutting.

    [Issue #3](https://github.com/pkic/cbom/issues/3) · orientation: both

8.  3.8 [Relationship to SBOM / HBOM & layering](https://github.com/pkic/cbom/issues/8) Deliberating

    How a CBOM profile sits alongside and links to software and hardware BOMs rather than duplicating them.

    [Issue #8](https://github.com/pkic/cbom/issues/8) · orientation: both

9.  3.9 [Extensibility & profile composition](https://github.com/pkic/cbom/issues/9) Deliberating

    How profiles extend the base model and how several profiles combine, so one CBOM can satisfy more than one profile at once.

    [Issue #9](https://github.com/pkic/cbom/issues/9) · orientation: both

10.  3.10 [Forward-looking / roadmap information](https://github.com/pkic/cbom/issues/10) Deliberating

     migration

     Expressing migration intent and PQC-readiness (planned vs implemented state). Mainly relevant to migration-oriented profiles.

     [Issue #10](https://github.com/pkic/cbom/issues/10) · orientation: migration

11.  3.11 [Profile governance & lifecycle](https://github.com/pkic/cbom/issues/11) Deliberating

     How a profile is proposed, versioned, revised and retired over time, and who is accountable for it.

     [Issue #11](https://github.com/pkic/cbom/issues/11) · orientation: both

12.  3.12 [Regulatory & policy alignment](https://github.com/pkic/cbom/issues/12) Deliberating

     Keeping profiles aligned with the regulations and guidance in the reference register — so a profile demonstrably satisfies what regulators ask for.

     [Issue #12](https://github.com/pkic/cbom/issues/12) · orientation: both

13.  3.13 [Templates, worked examples & tooling](https://github.com/pkic/cbom/issues/13) Deliberating

     The concrete outputs that make the methodology usable: a profile template, worked examples, and tooling hooks.

     [Issue #13](https://github.com/pkic/cbom/issues/13) · orientation: both


## Where to start

### Begin with 3.3

The format-independent attribute model underpins most other aspects — settling it first avoids rework.

### 3.6 and 3.7 are cross-cutting

Format mapping and normalisation are discussed in their own issues and linked from others, rather than re-argued in every thread.

### 3.10 is migration-flavoured

Roadmap and PQC-readiness information mainly concern migration-oriented profiles; related topics carry an `orientation:` label.

### See the whole board

The [project board](https://github.com/orgs/pkic/projects) shows all thirteen at once, so you can see what's stuck, converging or decided at a glance.

Status and issue numbers here mirror the repository's start-here table. If they drift, the [README](https://github.com/pkic/cbom/blob/main/README.md) and the live [issues](https://github.com/pkic/cbom/issues) are authoritative.
