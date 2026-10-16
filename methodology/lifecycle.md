---
title: Lifecycle Data
sideMenu: true
weight: 6
aliases:
- /cbom/methodology/lifecycle.html
linkTitle: Lifecycle Data
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The significance of a cryptographic fact depends on the phase at which, and the party by which, it was captured. The `lifecycleStage` attribute of a CBOM records that phase, which allows the statement that a product uses a given algorithm to be interpreted precisely.

## The four lifecycle stages

The lifecycle model (version 1) defines four values: `intended`, `implemented`, `configured` and `observed`. The values form a flat list with no sub-values, and one value is attached to each interface. Each value corresponds to one phase of the software lifecycle. Each phase has its own producer and its own data source.

{{< figure src="../assets/figures/methodology-lifecycle-1.svg" alt="A left-to-right timeline of four lifecycle stages, Design, Build, Deploy and Runtime, each box giving the stage name, who produces it and the data source, with a bracket linking Build to Runtime" >}}

*Each stage answers a different question, using a different source of data. From left to right, the producer changes from architects at design to operators at runtime.*

## Information available at each phase

| Stage | Phase | Establishes | Does not establish |
| --- | --- | --- | --- |
| `intended` | Design | What the architecture is specified to use. | What was actually built. |
| `implemented` | Build | What the shipped code or binary is capable of (the vendor build CBOM). | What a deployment enables. A capability present in the code is not proof that it is used. |
| `configured` | Deploy | What the deployed configuration permits. | Whether the configuration matches live sessions. Running systems can drift away from their configuration. |
| `observed` | Runtime | What was negotiated on the wire. | Whether the observation will stay true. A later configuration change can make it out of date. |

## Relationship to SBOM Generation Context

The 2026 minimum elements guidance adds an element called SBOM Generation Context, defined as the relative software lifecycle phase and the data available when the author generated the SBOM. The reasoning given there matches the reasoning here: component data differs according to the phase at which it was captured, and a consumer assessing risk needs to know which phase that was.

The guidance gives "before build", "build", and "after build" as acceptable values and permits more specific identifiers. Our four stages map onto those values. The last value, "after build", is split into two stages, `configured` and `observed`. The split is needed because PQC migration depends on the difference between what a deployment permits and what it actually negotiates.

| Lifecycle stage used here | Corresponding generation context |
| --- | --- |
| `intended` | before build |
| `implemented` | build |
| `configured` | after build, as a more specific identifier |
| `observed` | after build, as a more specific identifier |

A producer that follows the minimum elements guidance therefore already records what a profile needs, although possibly in less detail. Sometimes only the coarser value, such as "after build", is available. A consumer can then place the CBOM in the right part of the lifecycle. The consumer cannot tell whether a configured algorithm was actually used. The consumer should record this as a limitation and should not guess the finer stage. See [References](../../references/).

## False positives and false negatives across the lifecycle

No single stage gives a complete or perfectly accurate picture. Each is prone to two kinds of error: a **false positive**, where cryptography is reported but is not actually in effect, and a **false negative**, where cryptography is in effect but is not reported. The balance between the two kinds of error changes as the product or service described moves from design to runtime.

| Stage | Typical false positive (reported, not in effect) | Typical false negative (in effect, not reported) |
| --- | --- | --- |
| `intended` | An algorithm specified in the design but never implemented. | Cryptography introduced during implementation, such as that inside libraries and dependencies, which the design did not foresee. |
| `implemented` | Compiled-in capability, such as cipher suites or providers, that no deployment ever uses. | Cryptography loaded dynamically at runtime, provided by hardware (an HSM or TEE), or reached through dependencies the scanner does not cover. |
| `configured` | An algorithm permitted by the configuration but never negotiated in practice. | Cryptography outside the inspected configuration, such as built-in defaults or out-of-band channels. |
| `observed` | Cryptography seen only in a scan probe or a transient session, not representative of normal use. | Cryptography on paths not exercised during the observation window, such as failover, administrative, or rarely used interfaces. |

False positives are most common at the early stages. At those stages a design or a build reports what is possible rather than what runs. False positives are least common at runtime, because what is observed has actually happened. False negatives do not simply decrease from one stage to the next. Instead, the kind of cryptography that is missed changes. A design misses implementation detail. A static scan misses dynamic and hardware cryptography. A configuration misses whatever it does not govern. A runtime scan misses whatever was not exercised during the observation window.

For this reason, a product CBOM and a service CBOM are combined rather than used separately. A product CBOM describes what a product contains and comes from the `implemented` stage. It tends to over-report capability and to under-report runtime and hardware cryptography. A service CBOM describes what a running service uses and comes from the `configured` and `observed` stages. It under-reports paths that were not exercised while it was being captured. Reading the two together reduces both kinds of error.

## The readiness gap

The readiness gap is the difference between what a product is capable of and what is actually running. PQC-capable software and hardware do not, in themselves, guarantee that post-quantum cryptography is configured and active. Nor do they guarantee that it stays active after configuration changes. A product may be `implemented` with support for a given algorithm that is never `configured` and therefore never `observed`. In large migrations, interoperability and performance problems regularly appear as a system moves from one of these stages to the next.

For this reason, a CBOM should record each fact together with its lifecycle stage, rather than as a bare fact. A vendor's `implemented` CBOM and an operator's `observed` scan may both be correct and still differ. The difference between them is itself an important finding. A CBOM that records both views shows that difference explicitly.

## Product CBOM and service CBOM

There are two kinds of CBOM: the product CBOM and the service CBOM. They are kept separate because they answer different questions and are produced by different parties.

A **product CBOM** describes the cryptography a product contains or is able to use. It is usually produced by the vendor at build time and ships with a release, so it reflects the `implemented` stage: what the product can do. A **service CBOM** describes the cryptography a running service actually uses. It is produced by the operator from the deployed configuration and from what is observed on the wire, so it reflects the `configured` and `observed` stages: what a particular deployment does.

A service is usually built from several products, so a service CBOM draws on the product CBOMs of its components and adds the configuration and runtime picture that exists only once the service is deployed. A cryptographic relationship is a place where cryptography is applied between two endpoints. These relationships exist at the service level. They do not exist within any single product.

### Why the distinction matters for PQC migration

PQC migration depends on the difference between what a product can do and what a deployment actually uses. A product CBOM tells you whether a product can be made quantum-safe, and whether that requires a software update or a hardware change. A service CBOM tells you whether a given deployment is quantum-safe today. One kind of CBOM cannot replace the other:

-   A product CBOM on its own can overstate readiness. A product may support ML-KEM, but that says nothing about whether any deployment has enabled it.
-   A service CBOM on its own cannot show the upgrade path. Knowing that a service still negotiates a classical group does not tell you whether the underlying products can be reconfigured or must be replaced.

Migration planning needs both kinds. Product CBOMs identify which products can reach a quantum-safe target, and how. Service CBOMs identify which deployments have actually reached it, and which have not. Compare the two kinds of CBOM one interface at a time. The comparison shows whether an interface needs a software update or a hardware refresh. It also shows whether a quantum-safe state is only planned or is actually running.

## Multiple producers of a single interface's data

In the worked example, the two interfaces are recorded at different lifecycle stages because different producers captured them:

-   The HTTPS service interface is recorded as `observed`, captured by scanning the running server (a runtime, operator view).
-   The SSH management interface is recorded as `configured`, captured from the deployment configuration (an integrator view).

A profile may require the stage to be declared, as the baseline profile (the Interface Disclosure Baseline) does. Alternatively, a profile may require a specific stage. A runtime-assurance profile might require every interface to be `observed`, whereas a procurement profile might accept `implemented` from a vendor build.

## Stakeholders at each stage

Each stage has a different producer. In most cases, the party that produces the data is not the party that needs it. For that reason, the lifecycle stage has to be recorded rather than assumed. A consumer who receives a CBOM usually did not generate it. The consumer cannot tell from the content alone which phase the CBOM describes.

The table sets out who produces a CBOM at each stage, who typically consumes it, and which [use cases](../use-cases/) the data at that stage can support. Some use cases appear against more than one stage, because they draw on data from each of those stages. This is common. Several use cases depend on comparing one stage with another rather than reading a single stage.

| Stage | Produced by | Consumed by | Use cases it supports |
| --- | --- | --- | --- |
| `intended`
design | Architects and security architects, from design documents and threat models. | Architecture review boards; procurement teams writing requirements; the working group or sector body defining a profile. | [Crypto-agility assessment](../../use-cases/change-planning/#crypto-agility-assessment)
[Procurement](../../use-cases/disclosure/#procurement-and-tender-conformance), for stating the requirement rather than checking it |
| `implemented`
build | Development and build teams, from source and dependency analysis in the pipeline. | The vendor's own product security function; downstream integrators; operator procurement; security operations holding a component inventory. | [Procurement and tender conformance](../../use-cases/disclosure/#procurement-and-tender-conformance)
[CI quality gate](../../use-cases/#what-is-not-a-use-case)
[Vulnerability management](../../use-cases/disclosure/#vulnerability-management-and-incident-response)
[Supply-chain transparency](../../use-cases/disclosure/#supply-chain-transparency)
[Crypto-agility assessment](../../use-cases/change-planning/#crypto-agility-assessment) |
| `configured`
deploy | Integrators, platform and infrastructure teams, from deployment configuration and policy bundles. | Deployment gates; internal risk and assurance; migration programme leads. | [PQC migration readiness](../../use-cases/change-planning/#pqc-migration)
[CI quality gate](../../use-cases/#what-is-not-a-use-case), at the admission step
[Compliance reporting](../../use-cases/assurance/#regulatory-and-compliance-reporting) |
| `observed`
runtime | Operations and monitoring teams, from scanning and telemetry against the running service. | Assurance and audit; incident responders; regulators receiving a reported position; customers asking what a service actually uses. | [PQC migration readiness](../../use-cases/change-planning/#pqc-migration), for actual rather than declared state
[Incident response](../../use-cases/disclosure/#vulnerability-management-and-incident-response)
[Compliance reporting](../../use-cases/assurance/#regulatory-and-compliance-reporting)
[Due diligence](../../use-cases/disclosure/#mergers-and-third-party-risk-due-diligence) |

### Consumers who never produce

Several stakeholders only consume CBOMs and never produce them. Their needs shape what a profile has to require. Regulators and auditors read a reported position that they had no part in generating. For that reason, provenance and lifecycle stage matter more to them than to anyone else. Customers and partners who send a supply-chain request are in the same position. They are usually the reason a CBOM has to be scoped and redacted before release, as described in the [Inventory](../inventory/) section. Organizations performing due diligence before an acquisition read CBOMs across an entire estate that they do not operate. For them, missing data is as significant as the data that is present.

### Where the hand-offs fail

The stages are separated by a change of organization as often as by a change of time. Data is lost or becomes less reliable when it passes across these organizational boundaries.

-   Between `implemented` and `configured` the producer changes organization, from vendor to operator. A vendor cannot state what a deployment will enable, and an operator cannot see inside the binary. Neither party can produce a complete picture alone. This is the reason to combine a product CBOM with a service CBOM rather than choose between them.
-   Between `configured` and `observed` the producer usually stays within one organization but changes team. Drift appears at this hand-off: the running system stops matching its configuration. Drift happens because configuration is authored once and running systems change afterwards.
-   Between `intended` and `implemented` the data is frequently lost entirely. Design intent is rarely carried into a machine-readable form, so a consumer cannot tell whether cryptography present in a build was deliberate or incidental.

A profile can require the lifecycle stage to be declared. This makes these gaps visible. A profile cannot close the gaps. Closing them would require some party to produce data that it does not produce today. Whether that happens depends on adoption by those parties, not on what the specification says.

## Progress tracking over time

Successive revisions of a CBOM's content form an audit trail. The [Versioning](../versioning/) section describes content revision as one of the things that carry their own version. Suppose an interface moves from `implemented` to `configured` to `observed` with post-quantum cryptography enabled. The series of revisions then gives internal governance and regulators a verifiable record of the migration.

[← Inventory](../inventory/) [Next: Model →](../model/)
