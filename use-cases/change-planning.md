---
title: Change Planning
sideMenu: true
weight: 4
aliases:
- /cbom/use-cases/change-planning.html
linkTitle: Change planning
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

In these use cases, the profile adds facts that the interface disclosure baseline does not have. For each cryptographic purpose, it asks what the interface is capable of, what blocks that capability and who can clear the blocker, and what enabling it requires. It also asks whether the other end of the connection can still use classical cryptography. The orientation is `both`, which means the document reports what the product uses today and what it could use. A document produced against the baseline alone cannot be evaluated against these profiles at all.

The grouping and the change core are proposed in draft decision 0023 and are not yet settled.

## The change core

The profiles in this group share most of what they ask for. Each profile extends exactly one base profile. A fact that two profiles both need therefore has to be defined in a profile that both of them extend, rather than defined twice. That shared base profile is the change core.

-   **In the core:** `capabilityStatus`, `blockedBy` and `roadmapRef` per purpose; the `Supported` forms of the algorithm attributes; `enablementMethod` and `providerLocation`; `coexistence` and `negotiationControl`; `integrationConstraints`; `keyWrapping` and `keyWrappingSupported`.
-   **In the core as conditional rules:** `updateMechanism`, `updateAuthority` and `keyReplaceable`, which apply only to update interfaces. The IoT and substation profiles need them. A product with no update interface does not have to supply them.
-   **Not in the core:** what each profile adds for its own subject, shown in the last column of the table below.

The core is published as a sibling of the PQC migration profile. Both the core and the PQC migration profile extend the interface disclosure baseline. The core declares each shared rule under the id that the migration profile already uses, so no rule id changes. The tree below shows the intended structure, with the PQC migration profile moved under the core. That move is deferred, and is the same choice as Q51. It is still open whether the core assumes a post-quantum target or works for any target algorithm (Q66). If it works for any target, crypto-agility assessment needs no profile of its own.

```
interface-disclosure baseline
└─ change-core                     orientation: both
   ├─ pqc-migration                product        └─ pqc-migration-extended (depth)
   ├─ iot-estate                   device model
   └─ pqc-migration-ot             product (component)
sas-system                         overlay over component documents (system)
```

## Worked examples

| Page | Subject | What it shows | State |
| --- | --- | --- | --- |
| **[PQC Migration](../pqc-migration/)** | product | Keycloak 26.7.3: thirteen interfaces, four different blockers, two depths of one family | Developed. In review |
| **[IoT Device Estate](../iot/)** | device model | Permanent limits, a third party that controls updates, and a document that describes a device model while decisions are made about deployed instances | Drafted. Blocked on Q62, Q63, Q65 |
| **[Substation Automation](../substation/)** | system | A symmetric data plane with an asymmetric key plane; certification cost; a component profile and a system overlay | Drafted. Illustrative values |

## Attributes emphasised

The table compares the change-planning use cases across the attributes of the core.

| Change-planning use case | capability per purpose, blocker | enablement, provider location | coexistence | update path (conditional) | added by the profile itself |
| --- | --- | --- | --- | --- | --- |
| PQC migration | ● | ● | ● | ○ | module validation, the extended key-management depth |
| IoT device estate | ● | ● | ○ | ● | resource limits, model against instance |
| Substation automation | ● | ○ | ● | ● | certification impact, verifier replaceability, the system overlay |
| Crypto-agility | ● | ● | ○ | ○ | nothing, if the core is target-neutral |

Placeholder entries have no row until they are drafted. Any emphasis marked for them now would only be a guess.

## The use cases in this group

### PQC migration

An operator has to decide which systems to migrate, in what order, and what each will cost. That means separating the systems needing only a configuration change from those requiring a software update, and both from those tied to hardware that must be replaced. The consumers are migration programme leads and, increasingly, the regulators they report to.

A profile for this purpose requires the algorithms an interface currently uses and the algorithms it is able to use. This lets a reader compare what the interface could do with what it actually does. The profile also requires the lifecycle stage, which says which of the two is being reported. It does not ask for a readiness verdict. That judgement depends on criteria which change over time, so it belongs in an external policy. This use case is developed in detail on the [PQC Migration](../pqc-migration/) tab.

### IoT device estates

An operator of a large deployed estate of constrained devices decides, per device model, whether the cryptography can be changed in place, whether the device has to be replaced, whether something in front of it can carry the cryptography instead, or whether the exposure is accepted and documented. Scale changes the problem. Each action costs the unit price multiplied by the number deployed, plus the cost of physically reaching each one.

Three things make this more than a sector variant of PQC migration. First, a capability answer of no can be permanent. The limit may be the available flash memory, or a frame size fixed by a radio standard. Neither is a decision somebody could take differently. Second, the party able to install new firmware is often neither the manufacturer nor the operator. Third, the document describes a device model, while the decision is made about deployed instances of it. The producer cannot state the things that vary between instances, so the operator has to add them from its own records. A profile for this purpose therefore needs attributes none of the others do: whether an update mechanism exists, who can trigger it, and whether key material fixed at manufacture can be replaced at all. This use case is drafted on the [IoT Device Estate](../iot/) tab, where the choice of consumer is still open.

### Substation automation (OT)

A grid operator plans the migration of one substation automation system. For each communication path, it chooses one of four actions. It can migrate the path in place. Where the messages themselves are already protected with symmetric cryptography, it can migrate only the key plane, meaning the mechanisms that distribute and manage the keys. It can carry the path on a conduit. Or it can replace the device at its next refurbishment. Protection messages have a time budget of 3 ms and cannot carry a post-quantum signature. The exposure lies instead in group key distribution, certificate enrolment and firmware verification.

Two things distinguish it from PQC migration. The subject is a system assembled by an integrator from several suppliers' products. It therefore needs a component profile for the products and a system overlay, which is a document that references the component documents. And the cost of a change includes re-certification. **Drafted**, with illustrative values, on the [Substation Automation](../substation/) page.

### Crypto-agility assessment

Before an algorithm needs replacing, an architecture or risk function wants to know how hard replacing it would be. The answer is rarely the same across an estate. Where an assessment has been carried out, the interfaces that will cause trouble can usually be identified in advance.

The determining factor is whether cryptography is reachable through a replaceable provider or fixed in place, which makes the implementing library and its location the central attributes. Keeping key exchange, encryption and authentication as separate attributes rather than a single cipher-suite string also matters, because how easily each can be replaced usually differs.

### PKI and certificate estate migration

A PKI owner decides which hierarchies and certificate profiles move to post-quantum algorithms, in what order, and whether to run a parallel or a composite hierarchy while relying parties catch up. The deciding fact is one no other profile asks for: whether the relying parties that validate a given certificate population can process the new algorithms at all.

The subject is a system, not a product: certification authorities, registration and validation services, the HSMs that hold the keys, and the populations they serve. **Proposed.**

### Code and firmware signing migration

A publisher of software or firmware decides when it can move its signing keys to a new algorithm. It is constrained less by its own signing service than by the verifiers already deployed: a boot ROM that verifies one algorithm with one fixed key decides the timetable for every device that carries it.

This use case needs the same update-path facts as the IoT and substation use cases. That is why those facts belong in the change core rather than in any one profile. **Proposed.**

### Stored data and archive protection

A data owner decides which stores and archives to re-encrypt or re-wrap, and in what order. The order follows from how long the data has to stay confidential, set against the key establishment and key wrapping that protect it today. This is where harvest-now-decrypt-later exposure is most direct.

The producer is the operator, not a vendor, because only the operator knows what a store holds and for how long. The use case depends on how data is modelled alongside cryptography. That is still an open design note. **Proposed.**

### Shared-trust network migration

The operator of a closed network with many participants, such as a payment or settlement scheme, decides whether and when every participant can move to a new shared trust anchor. No participant can move alone, and the slowest participant sets the date.

The baseline describes relationships between two parties. It cannot yet describe a trust anchor shared by many participants. This use case is waiting on the multi-party trust model, which is set out in the design note of that name. **Proposed.**

[← Procurement](../procurement/) [Next: PQC Migration →](../pqc-migration/)
