---
title: Policy Evaluation
sideMenu: true
weight: 13
aliases:
- /cbom/methodology/policy-evaluation.html
linkTitle: Policy Evaluation
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A CBOM records facts. A judgement about those facts (for example, whether an interface is post-quantum-safe) is a separate matter. Such judgements should be produced by an external policy applied to the facts at evaluation time, rather than stored as attributes within the CBOM, because the criteria on which they depend change over time.

## Facts versus evaluations

A CBOM states **facts**: the protocols, versions, algorithms, key material, and certificate signature algorithms an interface uses. These are primary data, observed or declared by the producer.

An **evaluation** is a judgement *derived* from those facts against a set of criteria. "Is this interface post-quantum-safe?" is not a fact recorded by the producer. The answer is a conclusion drawn from the algorithms the interface uses, assessed against current guidance. The conclusion depends on criteria that are external to the facts and that are revised as guidance develops.

{{< figure src="../assets/figures/methodology-policy-evaluation-1.svg" alt="A box of CBOM facts and a box of policy criteria both feeding an evaluation step, which outputs a derived verdict carrying the policy version and the date applied" >}}

*The same CBOM facts, re-evaluated later under revised policy criteria, may yield a different verdict. The facts do not change; the judgement does.*

## Why the evaluation must be external to the data

If a derived value such as post-quantum posture is stored as an attribute within the CBOM, three problems follow:

-   **The value becomes stale.** When the criteria change (for example, when an algorithm is reclassified), the stored value no longer reflects current guidance, yet the CBOM presents it as though it did.
-   **Producers evaluate inconsistently.** Different producers apply different or outdated criteria. They therefore record different verdicts (conclusions such as "post-quantum-safe") for equivalent facts, and their CBOMs cannot be compared.
-   **The record and the judgement are conflated.** A CBOM is intended to be a durable record of facts. Embedding a time-dependent judgement in it undermines that role.

Keeping the evaluation external avoids these problems. The CBOM remains a stable record of facts. A single, versioned policy evaluates all CBOMs consistently. The same unchanged facts can be re-evaluated at any time under the criteria in force at that time.

## Examples of evaluations

| Evaluation | Derived from (facts) | Against (criteria, external) |
| --- | --- | --- |
| Post-quantum posture | the key-exchange and authentication algorithms an interface uses, and whether they are classical, hybrid, or post-quantum | current guidance on which algorithms and combinations are considered quantum-safe, which is revised over time |
| Cryptographic maturity | algorithm strength, key sizes, deprecation status, library currency, and cryptographic agility | a maturity rubric that is revised as recommendations and deprecations change |

Both evaluations draw on the same kind of primary data, and the same point applies to both. Their criteria are not fixed. The evaluation must therefore be applied externally and dated, rather than frozen into the CBOM.

Vulnerability status is a third case. It is the case where the pressure to store a verdict in the CBOM is strongest, because the format offers a field for it. Vulnerability status also differs from post-quantum posture and cryptographic maturity. Its criteria can be revised, and in addition they are held by someone other than the producer: whether an interface is affected depends on an advisory that a third party publishes. The same reasoning applies. [Vulnerabilities](../vulnerabilities/) works through the consequences. That page also sets out what a profile must require so that a CBOM can be matched against an advisory at all.

## Consequence for this profile

For this reason, `pqcPosture` has been removed from the profile's attributes. The attribute was carried in an early working draft, before v0.1, and no document was ever authored against that draft. The changelog records only changes between published versions. The removal therefore appears in the profile specification's revision rationale rather than in its changelog. The removal is recorded as decision 0002. The profile requires disclosure of the facts from which posture is derived. These facts are the protocol, the key exchange, encryption and authentication algorithms, and the implementing library. The posture itself is computed by an external policy at evaluation time. The same applies to any cryptographic maturity assessment.

## Relationship to profiles and governance

An evaluation policy is versioned, dated, and governed in the same manner as a profile (see [Versioning](../versioning/) and [Governance](../governance/)). A conformance claim (a producer's statement that a CBOM conforms to a profile) references the profile version. In the same way, a posture or maturity determination references the policy version and the date on which the policy was applied. Anyone can then reproduce the determination and audit the basis on which it was made.

In summary: the CBOM holds facts; an external, versioned policy derives judgements such as post-quantum posture and cryptographic maturity from those facts. Separating the two allows the facts to remain stable while the criteria evolve, and allows any CBOM to be re-evaluated under current criteria at any time.

[← Confidentiality](../confidentiality/) [Next: Vulnerabilities →](../vulnerabilities/)
