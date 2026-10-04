# Use case draft: migrating a substation automation system

Working draft, 4 October 2026. Follows the eight-part shape of the worked use cases. Catalogue entry 12, in the change-planning group (draft decision 0023). Attribute and profile names are proposals of this draft.

*Revised 4 October 2026 for the grouping:* the component profile extends the change core rather than the pqc-migration baseline. The update-path rules (I-OT3 and I-OT4) move into the core as conditional rules, shared with IoT. The decisions below are numbered for draft decision 0024.

## Choice of case

The OT use case is the **substation automation system (SAS) of an electricity grid operator**.

| Candidate | Case for it | Case against | Verdict |
|---|---|---|---|
| Substation automation (IEC 61850, IEC 62351) | Energy is the first sector in NIS2 and the clearest high-risk case under the EU roadmap. Protection traffic is the hardest real-time case in OT. The security standards are published, so capability can be checked against them. The system is assembled by an integrator from several suppliers' products | No open-source product with public crypto documentation as complete as Keycloak's | **Chosen** |
| OPC UA plant cell (open62541) | A real product with public documentation of its security policies | Close to the Keycloak pattern: one product, session security. It would teach the method little that is new | Kept as a possible second component |
| Water utility telemetry (DNP3, Modbus) | High sector relevance | Mostly no cryptography at all. The planner's answer would be "conduit" for almost everything, which tests too little | Mention only |
| Secure remote access into OT | Real harvest-now-decrypt-later exposure | An IT product at an OT boundary. Too close to Keycloak | Mention only |

## 1. The decision being supported

A grid operator plans the PQC migration of one substation automation system: the station level, the bay level, and the link to the control centre. For each communication path it decides one of four actions:

- **migrate in place**, by configuration or firmware;
- **migrate the key plane only**, where the data plane is already symmetric;
- **carry the path on a conduit**, such as the WAN tunnel to the control centre;
- **replace the device** at its next scheduled refurbishment.

It also needs to know whether any trust anchor will outlive the algorithm that protects it.

**Consumer:** the grid operator's protection and control engineering function, working with its system integrator. **Supporting consumer:** the national competent authority under NIS2, which reads the same facts at a higher level.

The operator's questions:

1. Where does asymmetric cryptography sit in this system, and which paths depend on it?
2. Which of those can be migrated without replacing hardware, and what does each change cost in outage time and re-certification?
3. Which paths can a conduit carry while the devices wait?
4. Can each device accept firmware signed with a new algorithm? Can its trust anchor be replaced in the field?
5. What blocks each step: the product, a standard, a provider, or certification?

**The threat weighting differs from Keycloak's.** Protection and control traffic is confidential only for a short time. The quantum risk is forged authority: forged firmware, configuration downloads, commands and group keys. The WAN link to the control centre is the main harvest-now-decrypt-later exposure. The profile asks for facts per purpose and does not rank them (decision 0002).

## 2. Producer constraints

There are two producers, and the black-box constraint applies to both.

- **The IED supplier** publishes a component CBOM for one product at one firmware version. The supplier does not know the substation, the zones or which interfaces are switched on.
- **The integrator** publishes a system document, built from the substation configuration description (SCL). It knows which component interfaces are in use, how the zones are cut, and which device implements each conduit. It does not see inside the components.
- **The operator** supplies instance data, such as how many substations use the same design. That data stays out of every profile.

Constraints that shape the attributes:

| Constraint | Effect on the profile | Source |
|---|---|---|
| GOOSE and SV are authenticated with a MAC: HMAC or GMAC with group keys | The data plane is not a migration target. The key plane is. Keys reach devices through IEC 62351-9 group key distribution (GDOI, RFC 8052) | IEC 62351-6:2020 |
| GOOSE is a layer-2 multicast message with a 3 ms budget for trip messages | Per-message signatures are not feasible. An ML-DSA-44 signature is 2,420 bytes. This limit is permanent and is stated once, as an integration constraint | IEC 61850-5 performance class P2/P3; FIPS 204 |
| MMS and IEC 60870-5-104 run over TLS as profiled by IEC 62351-3:2023 | A device can only claim 62351-3 conformance for the groups and signature schemes that profile lists. The profile lists none that are post-quantum, so conformance to the profile is itself a blocker, separate from what the TLS library could do | IEC 62351-3:2023 |
| GDOI as used by RFC 8052 builds on RFC 6407 | No post-quantum key exchange is defined for it. G-IKEv2 (RFC 9838) is the IKEv2-based successor. It mixes preshared keys for quantum resistance but profiles no ML-KEM exchange | RFC 8052, RFC 9838 |
| A device's firmware is verified by its bootloader or boot ROM | Whether the verification algorithm and anchor can change in the field decides between update and replacement | EU PQC roadmap: products should accept updates signed with quantum-safe algorithms |
| IEDs are certified per product version | A change to cryptography can trigger re-testing (IEC 61850 conformance), re-certification (IEC 62443-4-2), or the operator's own type approval | ISASecure CSA |
| Field life of 20 to 30 years, aligned to primary-plant refurbishment | Trust anchor validity and the replacement window matter more than release dates | |

## 3. From questions to attributes

The baseline pqc-migration attributes carry most of the load. Only two new ones are needed.

| What the operator needs to know | Attribute | Source |
|---|---|---|
| Which interface, of what type | `interfaceType` | Baseline |
| What it uses now and could use | `keyExchange`, `authentication`, and their `Supported` forms | Baseline |
| What blocks PQC, per purpose, and who can change it | `capabilityStatus`, `blockedBy`, `roadmapRef` | Baseline |
| Can it migrate while the far end is still classical | `coexistence`, `negotiationControl` | Baseline. One-way multicast needs a defined value: `not-applicable` |
| What breaks | `integrationConstraints` | Baseline. Carries the GOOSE frame and timing limit as a structured entry |
| Which interface delivers this interface's keys | `keyStoreRef` | Extended. **Promoted to MUST** for group-keyed interfaces |
| Can the trust anchor be replaced in the field | `keyReplaceable` | IoT draft |
| Who can push an update, and how | `updateAuthority`, `updateMechanism` | IoT draft |
| Can the firmware verification algorithm change in the field | `verifierReplaceable` | **New**. `yes`, `no` (boot ROM), `via-bootloader-update`, `unknown` |
| What does enabling the capability cost in certification | `certificationImpact` with `certificationScheme` | **New**. `none`, `retest`, `recertification`, `unknown` |
| Which component interfaces are actually used | `usage` | System document. **New**. `in-use`, `disabled`, `not-connected` |
| Which conduit carries an inter-zone path, and which interface implements it | `conduitRef` | System document. **New** |

**Tried and rejected:**

- **A crypto-plane attribute.** Separate interfaces (K2) combined with purpose already separate the data plane from the key plane.
- **`timingClass`.** It is an integration constraint, not a new attribute.
- **Per-path latency budgets.** They are the operator's requirement, not a supplier fact.
- **`compensatingControl`.** It is a design decision. It belongs in the operator's register, not in either CBOM.

## 4. Profiles

There are two profiles: one for the component, one for the system.

**`pqc-migration-ot`** (component). It extends the change core monotonically (decision 0004). The core supplies the baseline capability attributes and, as conditional rules on update interfaces, `keyReplaceable`, `updateAuthority` and `updateMechanism`.

| Rule | Requirement | Level |
|---|---|---|
| Inherited | All change-core rules, including the conditional update-path rules | as the core |
| I-OT1 | `certificationImpact` on every interface whose `capabilityStatus` is not `not-planned` | MUST |
| I-OT2 | `keyStoreRef` on every interface keyed by a group key service | MUST |
| I-OT3 | `verifierReplaceable` on every update interface | MUST |
| I-OT5 | Real-time limits stated in `integrationConstraints` where they exist | SHOULD |
| P-OT1 | Declare at least one update interface, or state why there is none | MUST |

**`sas-system`** (integrator). This is a derived overlay: it references the component CBOMs and does not copy them.

| Rule | Requirement | Level |
|---|---|---|
| S1 | Reference every component CBOM by link and digest | MUST |
| S2 | State `usage` for every interface of every referenced component | MUST |
| S3 | Declare zones, and for each inter-zone path name the conduit with `conduitRef` | MUST |
| S4 | Name the component that provides the key plane: the GDOI key server and the certificate authority's enrolment interface | MUST |
| S5 | State the IEC 62443-3-3 security level achieved by the system as delivered | SHOULD |

**Dependencies:**

- The update-path attributes now sit in the change core and are shared with IoT. If IoT question Q63 (permanent versus temporary limits) changes them, both profiles follow.
- How the overlay's verdict relates to the component documents it cites is Q68.
- A system as the subject has to be accepted by the scope declaration (decision 0008).

**The edge model stays parked.** In a substation every conduit is implemented by a device: a firewall, a VPN router or a gateway. A conduit's cryptography is therefore a fact on that device's interface, so the revival trigger is not met. It would be met by a fact owned by the path rather than by any device, such as an end-to-end GOOSE transfer time. That fact is an operator requirement, so it stays out.

## 5. The worked example

The worked example is a reference SAS with generic components and values taken from the standards' profiles. Every value is marked illustrative until a supplier volunteers a real product.

**Components:**

- a protection IED;
- a bay controller;
- a station gateway, which talks IEC 60870-5-104 to the control centre;
- a station server, which hosts the GDOI key server and the HMI;
- an engineering workstation;
- a WAN router, which implements the conduit to the control centre.

**Two zones:** the station zone and the WAN.

**Protection IED interfaces:**

| Interface | Type | Protocol | Expected finding |
|---|---|---|---|
| `svc-goose` | service | GOOSE, IEC 62351-6 | Integrity by HMAC-SHA256 with a group key. Already quantum-resistant. Its keys come from `int-gdoi` |
| `svc-sv` | service | Sampled values, IEC 62351-6 | As `svc-goose` |
| `tls-mms` | service | TLS 1.2 and 1.3, IEC 62351-3 | ECDHE and ECDSA. `blockedBy: standard`, because 62351-3 lists no PQC groups |
| `svc-mms` | service | MMS, with IEC 62351-8 role-based access tokens | The token signature is the authority. `blockedBy: standard` |
| `int-gdoi` | interconnect | GDOI over IKEv1 phase 1 | The key plane. `blockedBy: standard`. The successor, G-IKEv2, is published but not profiled for IEC 62351-9 |
| `mgmt-enrol` | management | Certificate enrolment (EST or SCEP), IEC 62351-9 | Device identity certificates with long validity. Can it enrol an ML-DSA certificate? |
| `upd-fw` | management | Firmware update | `verifierReplaceable` decides update versus replacement |
| `mgmt-eng` | management | Configuration download from the engineering tool | Often protected only by TLS and access control. Is the configuration itself signed? |
| `peer-ptp` | peer | IEEE 1588 time synchronisation | Commonly no cryptography: `none` |
| `sto-keys` | storage | — | Device private key and trust anchors. Is a secure element present? `unknown` is acceptable |

**What a planner is expected to conclude:**

- **The protection traffic itself is not the migration target.** Its integrity is already symmetric.
- **The key plane is the long pole.** GDOI, role-based access tokens and certificate enrolment are all blocked by standards.
- **The control-centre link can be protected now at the conduit.** IKEv2 with ML-KEM is in the RFC Editor queue, and RFC 9370 already allows hybrid exchanges. This holds while the gateway's 62351-3 TLS waits on the standard.
- **For each device model, `verifierReplaceable` splits the fleet** into those that can be updated and those that must be replaced at refurbishment.
- **`certificationImpact` turns every one of these actions into a schedule.** No algorithm inventory shows any of this.

## 6. What the profiles deliberately exclude

- Migration priority, risk scores, target dates and compensating controls. These belong in the operator's register (decisions 0002 and 0007, and CycloneDX 2.0 `risks`).
- Per-path latency budgets and safety analysis.
- Site topology in supplier documents. The system document carries the zone structure for one design, not for a specific site.
- Exploitability. It stays a separate artefact.

## 7. Expressing it in CycloneDX

- **Components follow the Keycloak pattern (K7).** TLS is a protocol component. GOOSE, SV, MMS, IEC 60870-5-104 and GDOI are services, because the CycloneDX protocol types do not include them. Each service depends on what carries it.
- **The group-key relationship is a dependency.** `svc-goose` depends on the key material, and the key material on `int-gdoi`. `keyStoreRef` points to `int-gdoi`.
- **The system document is a separate BOM.** It references component BOMs through BOM-Link with a hash. `usage` and `conduitRef` are `pkic:profile:` properties.
- **Zones have no native home in 1.7.** In 2.0 the blueprint model (zones, boundaries and flows) is the candidate. This case is the first worked use for it, and a concrete input to the CycloneDX feedback on the edge gap.
- **Certification.** `certificationScheme` maps to `certifications` in 2.0 and is a property in 1.7, as for module validation.

## 8. Proposed decisions and open questions

**Proposed decisions** (for a draft decision 0024):

- **O1.** The OT use case is the substation automation system, named by its decision.
- **O2.** Two profiles: a component profile extending the change core, and a system overlay.
- **O3.** The data plane and the key plane are separate interfaces, linked by `keyStoreRef`, which is MUST for group-keyed interfaces.
- **O4.** Real-time limits are integration constraints, not a new attribute.
- **O5.** A conduit is an interface of the device that implements it. The edge model stays parked.
- **O6.** Values are illustrative until a supplier volunteers a product.

**Open questions:**

1. Does IEC 62351-9:2023 already profile G-IKEv2, or only GDOI over IKEv1? This changes the `int-gdoi` finding.
2. Has IEC TC 57 WG 15 started PQC work on IEC 62351-3, -6, -8 and -9?
3. Is `certificationImpact` a product fact, or a deployment fact that belongs in the system document?
4. Should `usage` stay in the system overlay, or become a general facility for derived CBOMs?
5. Who can bring a protection IED supplier and a transmission or distribution operator to review the draft? Targeted requests to named people are the route.

## Sources

- [IEC 62351-6:2020 preview](https://cdn.standards.iteh.ai/samples/102476/88f51459928e44f3b051832d08a7518a/IEC-62351-6-2020.pdf)
- [IEC 62351-3:2023 preview](https://cdn.standards.iteh.ai/samples/105100/b7a344cdd98f47e4a67e4a94e9df50b5/IEC-62351-3-2023.pdf)
- [RFC 8052, GDOI support for IEC 62351](https://www.rfc-editor.org/info/rfc8052/)
- [draft-ietf-ipsecme-g-ikev2, published as RFC 9838](https://datatracker.ietf.org/doc/draft-ietf-ipsecme-g-ikev2/23/)
- [draft-ietf-ipsecme-ikev2-mlkem, RFC Editor queue](https://datatracker.ietf.org/doc/draft-ietf-ipsecme-ikev2-mlkem/)
- [GOOSE transfer time, IEC 61850-5 P2/P3](https://www.igrid-td.com/smartguide/iec61850/goose-messaging/)
- [EU PQC roadmap (Industrial Cyber)](https://industrialcyber.co/regulation-standards-and-compliance/eu-begins-coordinated-effort-for-member-states-to-switch-critical-infrastructure-to-quantum-resistant-encryption-by-2030/)
- [DHS/CISA OT PQC guidance (Industrial Cyber)](https://industrialcyber.co/cisa/dhs-and-cisa-prescribe-proactive-steps-toward-post-quantum-cryptography-across-ot-environments/)
