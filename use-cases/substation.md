---
title: Substation Automation (OT)
sideMenu: true
weight: 7
aliases:
- /cbom/use-cases/substation.html
linkTitle: Substation Automation (OT)
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A grid operator plans the post-quantum migration of one substation automation system. For each communication path, the operator decides whether to migrate it in place, migrate only the key plane, carry it on a conduit, or replace the device at its next refurbishment. This is an operational technology (OT) use case in the [change-planning](../change-planning/#substation-automation-ot) group.

Draft for discussion. The values are illustrative. They are taken from the profiles in the published standards, and they stay illustrative until a supplier volunteers a real product. The attribute and profile names are proposals, not agreed names. The component profile extends the change core, the core profile shared by the change-planning use cases (draft decision 0023). The decisions proposed on this page are numbered for draft decision 0024. The working text is kept in `drafts/ot-substation/`.

## Choice of case

The OT use case is the **substation automation system (SAS) of an electricity grid operator**.

| Candidate | Case for it | Case against | Verdict |
| --- | --- | --- | --- |
| Substation automation (IEC 61850, IEC 62351) | Energy is the first sector in NIS2 and the clearest high-risk case under the EU roadmap. Protection traffic is the hardest real-time case in OT. The security standards are published, so capability can be checked against them. The system is assembled by an integrator from several suppliers' products | No open-source product with public crypto documentation as complete as Keycloak's | **Chosen** |
| OPC UA plant cell (open62541) | A real product with public documentation of its security policies | It follows the same pattern as the Keycloak use case: one product that secures sessions. It would add little that is new to the method | Kept as a possible second component |
| Water utility telemetry (DNP3, Modbus) | High sector relevance | Most of it has no cryptography at all. The planner would answer "carry it on a conduit" for almost every path, so the case would test too little of the profile | Mention only |
| Secure remote access into OT | Real harvest-now-decrypt-later exposure | It is an IT product that sits at the OT boundary. It is too similar to the Keycloak use case | Mention only |

## 1\. The decision being supported

A grid operator plans the PQC migration of one substation automation system: the station level, the bay level, and the link to the control centre. For each communication path it decides one of four actions:

-   **migrate in place**, by configuration or firmware;
-   **migrate the key plane only**, where the data plane is already symmetric. The data plane is the protected traffic itself. The key plane is the mechanism that distributes the keys for that traffic;
-   **carry the path on a conduit**, such as the WAN tunnel to the control centre. A conduit is a protected channel that carries traffic between security zones;
-   **replace the device** at its next scheduled refurbishment.

The operator also needs to know whether any trust anchor will stay in service longer than the algorithm that protects it stays safe.

**Consumer:** the grid operator's protection and control engineering function, working with its system integrator. **Supporting consumer:** the national competent authority under NIS2, which uses the same facts in less detail.

The operator's questions:

1.  Where does asymmetric cryptography sit in this system, and which paths depend on it?
2.  Which of those can be migrated without replacing hardware, and what does each change cost in outage time and re-certification?
3.  Which paths can a conduit carry while the devices wait?
4.  Can each device accept firmware signed with a new algorithm? Can its trust anchor be replaced in the field?
5.  What blocks each step: the product, a standard, a provider, or certification?

{{< figure src="../assets/figures/use-cases-substation-1.svg" alt="The reference substation automation system. A station zone holds a station server with the GDOI key server and HMI, an engineering workstation, a protection IED, a bay controller and a station gateway. The protection IED and the bay controller exchange GOOSE and sampled values over multicast, protected by a symmetric MAC. The station server distributes group keys to them over GDOI and reaches them over MMS on TLS. The engineering workstation downloads configuration and firmware to the IED. The station gateway reaches the IEDs over MMS on TLS and the control centre over IEC 60870-5-104 on TLS. That link leaves the station through a WAN router that straddles the boundary between the station zone and the WAN, carrying the traffic in an IPsec tunnel set up with IKEv2." >}}

*The reference system. Protection traffic stays inside the station zone and is protected with a symmetric MAC. All asymmetric cryptography sits elsewhere: the group key distribution, the TLS sessions to the HMI (human-machine interface) and the gateway, the engineering download, and the tunnel that carries the control-centre link across the conduit. Values are illustrative.*

**The threats are weighted differently from the Keycloak use case.** Protection and control traffic needs to stay confidential only for a short time. The quantum risk is that an attacker forges something that carries authority: firmware, configuration downloads, commands or group keys. The WAN link to the control centre is the main harvest-now-decrypt-later exposure. The profile asks for the facts for each purpose and does not rank them (decision 0002).

## 2\. Producer constraints

There are two producers. The black-box constraint applies to both: each producer can describe only what it can see from its own position.

-   **The IED supplier** publishes a component CBOM. An IED (intelligent electronic device) is a protection relay, bay controller or similar field device. The supplier's CBOM covers one product at one firmware version. The supplier does not know the substation, the zones or which interfaces are switched on.
-   **The integrator** publishes a system document, built from the substation configuration description (SCL). It knows which component interfaces are in use, how the system is divided into zones, and which device implements each conduit. It does not see inside the components.
-   **The operator** supplies instance data. Instance data describes the operator's own deployments, such as how many substations use the same design. No profile covers that data.

Constraints that shape the attributes:

| Constraint | Effect on the profile | Source |
| --- | --- | --- |
| GOOSE (protection event messages) and SV (sampled values) are authenticated with a message authentication code (MAC): HMAC or GMAC with group keys | The data plane, meaning the messages themselves, is not a migration target. The key plane, meaning how the group keys are distributed, is a migration target. Keys reach devices through IEC 62351-9 group key distribution (GDOI, RFC 8052) | IEC 62351-6:2020 |
| GOOSE is a layer-2 multicast message with a 3 ms budget for trip messages | Per-message signatures are not feasible. An ML-DSA-44 signature is 2,420 bytes. This limit will not change. The profile records it once, as an integration constraint | IEC 61850-5 performance class P2/P3; FIPS 204 |
| MMS and IEC 60870-5-104 run over TLS as profiled by IEC 62351-3:2023 | A device can only claim 62351-3 conformance for the key exchange groups and signature schemes that the 62351-3 profile lists. That profile lists no post-quantum ones. Conformance to 62351-3 therefore blocks migration on its own, even if the device's TLS library supports post-quantum algorithms | IEC 62351-3:2023 |
| GDOI as used by RFC 8052 builds on RFC 6407 | No post-quantum key exchange is defined for it. G-IKEv2 (RFC 9838) is the IKEv2-based successor. It mixes in preshared keys for quantum resistance, but it does not profile an ML-KEM exchange | RFC 8052, RFC 9838 |
| A device's firmware is verified by its bootloader or boot ROM | If the verification algorithm and its trust anchor can be changed in the field, the device can be updated. If they cannot, the device must be replaced | EU PQC roadmap: products should accept updates signed with quantum-safe algorithms |
| IEDs are certified per product version | A change to cryptography can trigger re-testing (IEC 61850 conformance), re-certification (IEC 62443-4-2), or the operator's own type approval | ISASecure CSA |
| Field life of 20 to 30 years, aligned to primary-plant refurbishment | How long trust anchors stay valid, and when each device is due for replacement, matter more than product release dates |  |

{{< figure src="../assets/figures/use-cases-substation-2.svg" alt="Five paths, each traced from the message to what protects it to where its keys or trust come from, with its post-quantum status. GOOSE and sampled values are protected by HMAC or GMAC with a group key that comes from the GDOI key server over IKEv1 phase 1: the data plane is already quantum-resistant and the key plane is blocked by a standard. MMS is protected by TLS under IEC 62351-3 with ECDHE and ECDSA, keyed by a device certificate enrolled over EST or SCEP: blocked by a standard. Role-based access tokens under IEC 62351-8 are protected by a token signature from the token issuer's key: blocked by a standard. A firmware image is protected by a signature checked at boot against a key and algorithm in boot ROM or the loader: blocked by the product, or replaced at refurbishment. The control-centre link under IEC 60870-5-104 is protected by TLS inside a tunnel set up by the WAN router with IKEv2: it can move first, with hybrid ML-KEM at the conduit." >}}

*Data plane and key plane. The protection messages that the 3 ms budget applies to already use symmetric cryptography, so they are not the migration target. Every asymmetric dependency sits one column to the right, where the keys or trust come from: key distribution, certificate enrolment, token signing and firmware verification. Most of those are blocked until a standard adds post-quantum algorithms. The only path that can migrate first is the control-centre link, by upgrading the conduit that carries it. Status values are illustrative.*

## 3\. From questions to attributes

The baseline attributes, which the pqc-migration profile already defines, answer most of the operator's questions. Only two new component attributes are needed. The system document adds two more.

| What the operator needs to know | Attribute | Source |
| --- | --- | --- |
| Which interface, of what type | `interfaceType` | Baseline |
| What it uses now and could use | `keyExchange`, `authentication`, and their `Supported` forms | Baseline |
| What blocks PQC, per purpose, and who can change it | `capabilityStatus`, `blockedBy`, `roadmapRef` | Baseline |
| Can it migrate while the other end still uses classical algorithms | `coexistence`, `negotiationControl` | Baseline. One-way multicast needs a defined value: `not-applicable` |
| What breaks if the cryptography changes | `integrationConstraints` | Baseline. Records the GOOSE frame size and timing limits as a structured entry |
| Which interface delivers this interface's keys | `keyStoreRef` | Extended. **Promoted to MUST** for group-keyed interfaces |
| Can the trust anchor be replaced in the field | `keyReplaceable` | IoT draft |
| Who can push an update, and how | `updateAuthority`, `updateMechanism` | IoT draft |
| Can the firmware verification algorithm change in the field | `verifierReplaceable` | **New**. `yes`, `no` (boot ROM), `via-bootloader-update`, `unknown` |
| What does enabling the capability cost in certification | `certificationImpact` with `certificationScheme` | **New**. `none`, `retest`, `recertification`, `unknown` |
| Which component interfaces are actually used | `usage` | System document. **New**. `in-use`, `disabled`, `not-connected` |
| Which conduit carries an inter-zone path, and which interface implements it | `conduitRef` | System document. **New** |

**Tried and rejected:**

-   **A crypto-plane attribute.** It is not needed. The data plane and the key plane are already separate interfaces (K2), and the purpose of each interface tells them apart.
-   **`timingClass`.** A timing limit is an integration constraint, so it does not need a new attribute.
-   **Per-path latency budgets.** They are the operator's requirement, not a supplier fact.
-   **`compensatingControl`.** It is a design decision. It belongs in the operator's register, not in either CBOM.

## 4\. Profiles

There are two profiles: one for the component, one for the system.

**`pqc-migration-ot`** (component). It extends the change core monotonically: it adds rules and does not relax any (decision 0004). The core supplies the baseline capability attributes. It also supplies `keyReplaceable`, `updateAuthority` and `updateMechanism`, as conditional rules that apply to update interfaces.

| Rule | Requirement | Level |
| --- | --- | --- |
| Inherited | All change-core rules, including the conditional update-path rules | same as in the core |
| I-OT1 | `certificationImpact` on every interface whose `capabilityStatus` is not `not-planned` | MUST |
| I-OT2 | `keyStoreRef` on every interface keyed by a group key service | MUST |
| I-OT3 | `verifierReplaceable` on every update interface | MUST |
| I-OT5 | Real-time limits stated in `integrationConstraints` where they exist | SHOULD |
| P-OT1 | Declare at least one update interface, or state why there is none | MUST |

**`sas-system`** (integrator). This is a derived overlay. An overlay is a document that adds facts on top of other CBOMs. It references the component CBOMs and does not copy them.

| Rule | Requirement | Level |
| --- | --- | --- |
| S1 | Reference every component CBOM by link and digest | MUST |
| S2 | State `usage` for every interface of every referenced component | MUST |
| S3 | Declare zones, and for each inter-zone path name the conduit with `conduitRef` | MUST |
| S4 | Name the component that provides the key plane: the GDOI key server and the certificate authority's enrolment interface | MUST |
| S5 | State the IEC 62443-3-3 security level achieved by the system as delivered | SHOULD |

**Dependencies:**

-   The update-path attributes are now part of the change core, so the IoT profile uses them too. If IoT question Q63 (permanent versus temporary limits) changes them, both profiles change with them.
-   Open question Q68 asks how the overlay's verdict relates to the component documents it cites.
-   The scope declaration (decision 0008) must accept a whole system, not only a product, as the subject of a CBOM.

{{< figure src="../assets/figures/use-cases-substation-3.svg" alt="Five supplier documents on the left, one per component: protection IED, bay controller, station gateway, station server and WAN router, each a component CBOM conforming to pqc-migration-ot. On the right, the integrator's system document, conforming to sas-system, cites each of them by link and digest and states the use of every interface, the zones and conduits, who provides the key plane, and the IEC 62443-3-3 level as delivered. Below both, the operator holds instance data and its migration register, outside both profiles." >}}

*Two kinds of document. Each supplier describes one product, which it can see in full. The integrator describes how the products are put together, and cites the supplier documents rather than repeating them. It is still an open question what the system verdict says about a component that conforms to no profile (Q68).*

**The edge model stays parked.** The edge model would treat a path between devices as an object with its own facts. It was parked, to be revived only when a fact belongs to a path and not to any device. In a substation every conduit is implemented by a device: a firewall, a VPN router or a gateway. A conduit's cryptography is therefore a fact on that device's interface, so the condition for reviving the edge model is not met. A fact that belongs to the path itself would meet it, such as an end-to-end GOOSE transfer time. That fact is an operator requirement, so it stays out of the profiles.

## 5\. The worked example

The worked example is a reference SAS. It uses generic components, and its values are taken from the profiles in the published standards. Every value is marked illustrative until a supplier volunteers a real product.

**Components:**

-   a protection IED;
-   a bay controller;
-   a station gateway, which talks IEC 60870-5-104 to the control centre;
-   a station server, which hosts the GDOI key server and the HMI;
-   an engineering workstation;
-   a WAN router, which implements the conduit to the control centre.

**Two zones:** the station zone and the WAN.

{{< figure src="../assets/figures/use-cases-substation-4.svg" alt="A box labelled protection IED, firmware as shipped, internals not disclosed. On its left edge, four service interfaces: GOOSE trip messages, sampled values, TLS for MMS, and MMS with role-based access; and two management interfaces: firmware update and engineering download. On its right edge, the GDOI group key interface of type interconnect and the certificate enrolment interface of type management. On its bottom edge, time synchronisation of type peer, which carries no cryptography, and the store for device keys and trust anchors of type storage." >}}

*The protection IED as its supplier describes it: ten interfaces, described from the outside. The diagram has the same layout as the Keycloak diagram, but the cryptography is distributed differently. Most of the asymmetric cryptography is on the management side and in the key plane, not on the service interfaces that carry protection traffic.*

**Protection IED interfaces:**

| Interface | Type | Protocol | Expected finding |
| --- | --- | --- | --- |
| `svc-goose` | service | GOOSE, IEC 62351-6 | Integrity by HMAC-SHA256 with a group key. Already quantum-resistant. Its keys come from `int-gdoi` |
| `svc-sv` | service | Sampled values, IEC 62351-6 | As `svc-goose` |
| `tls-mms` | service | TLS 1.2 and 1.3, IEC 62351-3 | ECDHE and ECDSA. `blockedBy: standard`, because 62351-3 lists no PQC groups |
| `svc-mms` | service | MMS, with IEC 62351-8 role-based access tokens | The token signature is what grants authority. `blockedBy: standard` |
| `int-gdoi` | interconnect | GDOI over IKEv1 phase 1 | This interface is the key plane. `blockedBy: standard`. The successor, G-IKEv2, is published but not profiled for IEC 62351-9 |
| `mgmt-enrol` | management | Certificate enrolment (EST or SCEP), IEC 62351-9 | Device identity certificates with long validity. Can it enrol an ML-DSA certificate? |
| `upd-fw` | management | Firmware update | `verifierReplaceable` decides update versus replacement |
| `mgmt-eng` | management | Configuration download from the engineering tool | Often protected only by TLS and access control. Is the configuration itself signed? |
| `peer-ptp` | peer | IEEE 1588 time synchronisation | Commonly no cryptography: `none` |
| `sto-keys` | storage | — | Device private key and trust anchors. Is a secure element present? `unknown` is acceptable |

**What a planner is expected to conclude:**

-   **The protection traffic itself is not the migration target.** Its integrity is already symmetric.
-   **The key plane will take the longest.** GDOI, role-based access tokens and certificate enrolment are all blocked by standards.
-   **The control-centre link can be protected now at the conduit.** IKEv2 with ML-KEM is in the RFC Editor queue, and RFC 9370 already allows hybrid exchanges. This works even while the gateway's 62351-3 TLS is still blocked by the standard.
-   **For each device model, `verifierReplaceable` splits the fleet** into devices that can be updated and devices that must be replaced at refurbishment.
-   **`certificationImpact` turns every one of these actions into a schedule.** It shows the testing and certification cost of each action. An inventory that lists only algorithms shows none of this.

## 6\. What the profiles deliberately exclude

-   Migration priority, risk scores, target dates and compensating controls. These belong in the operator's register (decisions 0002 and 0007, and CycloneDX 2.0 `risks`).
-   Per-path latency budgets and safety analysis.
-   Site topology in supplier documents. The system document carries the zone structure for one design, not for a specific site.
-   Exploitability. It stays a separate artefact.

## 7\. Expressing it in CycloneDX

-   **Components are modelled as in the Keycloak use case (K7).** TLS is a protocol component. GOOSE, SV, MMS, IEC 60870-5-104 and GDOI are services, because the CycloneDX protocol types do not include them. Each service has a dependency on the component that carries it.
-   **The group-key relationship is a dependency.** `svc-goose` depends on the key material, and the key material on `int-gdoi`. `keyStoreRef` points to `int-gdoi`.
-   **The system document is a separate BOM.** It references component BOMs through BOM-Link with a hash. `usage` and `conduitRef` are `pkic:profile:` properties.
-   **CycloneDX 1.7 has no native way to express zones.** In CycloneDX 2.0, the blueprint model (zones, boundaries and flows) is the candidate for expressing them. This case is the first worked use of the blueprint model, and a concrete input to the CycloneDX feedback on the edge gap.
-   **Certification.** In CycloneDX 2.0, `certificationScheme` maps to `certifications`. In 1.7 it is a property, in the same way as module validation.

## 8\. Proposed decisions and open questions

**Proposed decisions** (for a draft decision 0024):

-   **O1.** The OT use case is the substation automation system, named by its decision.
-   **O2.** Two profiles: a component profile extending the change core, and a system overlay.
-   **O3.** The data plane and the key plane are separate interfaces, linked by `keyStoreRef`, which is MUST for group-keyed interfaces.
-   **O4.** Real-time limits are integration constraints, not a new attribute.
-   **O5.** A conduit is an interface of the device that implements it. The edge model stays parked.
-   **O6.** Values are illustrative until a supplier volunteers a product.

**Open questions:**

1.  Does IEC 62351-9:2023 already profile G-IKEv2, or only GDOI over IKEv1? The answer changes the `int-gdoi` finding.
2.  Has IEC TC 57 WG 15 started PQC work on IEC 62351-3, -6, -8 and -9?
3.  Is `certificationImpact` a product fact, or a deployment fact that belongs in the system document?
4.  Should `usage` stay in the system overlay, or become a general facility for derived CBOMs?
5.  Who can bring a protection IED supplier and a transmission or distribution operator to review the draft? The best route is to ask named people directly.

## Sources

-   [IEC 62351-6:2020 preview](https://cdn.standards.iteh.ai/samples/102476/88f51459928e44f3b051832d08a7518a/IEC-62351-6-2020.pdf)
-   [IEC 62351-3:2023 preview](https://cdn.standards.iteh.ai/samples/105100/b7a344cdd98f47e4a67e4a94e9df50b5/IEC-62351-3-2023.pdf)
-   [RFC 8052, GDOI support for IEC 62351](https://www.rfc-editor.org/info/rfc8052/)
-   [draft-ietf-ipsecme-g-ikev2, published as RFC 9838](https://datatracker.ietf.org/doc/draft-ietf-ipsecme-g-ikev2/23/)
-   [draft-ietf-ipsecme-ikev2-mlkem, RFC Editor queue](https://datatracker.ietf.org/doc/draft-ietf-ipsecme-ikev2-mlkem/)
-   [GOOSE transfer time, IEC 61850-5 P2/P3](https://www.igrid-td.com/smartguide/iec61850/goose-messaging/)
-   [EU PQC roadmap (Industrial Cyber)](https://industrialcyber.co/regulation-standards-and-compliance/eu-begins-coordinated-effort-for-member-states-to-switch-critical-infrastructure-to-quantum-resistant-encryption-by-2030/)
-   [DHS/CISA OT PQC guidance (Industrial Cyber)](https://industrialcyber.co/cisa/dhs-and-cisa-prescribe-proactive-steps-toward-post-quantum-cryptography-across-ot-environments/)

[← IoT Device Estate](../iot/) [Next: Proposing a Use Case →](../proposing/)
