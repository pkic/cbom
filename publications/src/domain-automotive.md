CBOM Profiles — Application domain: Automotive
==============================================

Working Draft 0.1 · Nov 26, 2026 · \@Mike

Purpose
-------

This draft covers the cryptography of road vehicles and the infrastructure around them: electronic control units (ECUs) and in-vehicle networks, over-the-air updates, vehicle-to-everything communication, electric vehicle charging, and the back-end services that manage vehicles. It is written for readers outside the working group: vehicle manufacturers, suppliers of ECUs and software, charging operators, type-approval authorities and technical services.

Automotive is a domain of its own for four reasons:

-   A vehicle stays on the road for fifteen years or more. Its cryptography is fixed at design, years before the vehicle is sold, so a vehicle designed today will still be verifying signatures well into the 2040s.

-   Many ECUs have tight limits on memory, processing and bus bandwidth. Post-quantum signatures and keys are much larger than the ones they replace, so these limits decide what can move. The domain is close to operational technology and to IoT Device Estate in this respect.

-   Several large PKIs serve the sector: the credential systems for vehicle-to-everything communication, the charging PKI, and the manufacturers' own PKIs for updates and diagnostics. Each has many verifiers that must all accept a new algorithm before signers can use it.

-   Type approval already requires a cybersecurity management system and a software update management system. A CBOM can serve as evidence in processes that exist.

This is a working draft. It sits outside Release 1 and starts from the positions that Release 1 ratified. Positions proposed here are listed in chapter 12.

1. Scope and readers
--------------------

The draft covers:

-   **the vehicle**: ECUs, in-vehicle networks, gateways and telematics units;

-   **updates**: over-the-air and in-workshop software updates;

-   **vehicle-to-everything communication** between vehicles, roadside units and back ends;

-   **electric vehicle charging**, including Plug and Charge, both the vehicle's end and the charging station's end;

-   **back-end services**: telematics, remote functions and fleet management.

Charging is included here, although it also sits at the edge of operational technology. A charging session is a conversation between a vehicle and a station, and the vehicle's end cannot be described without the station's. The charging station's own grid side, its link to the grid operator, stays with the operational technology document.

The readers are:

| Reader | What they decide |
|---|---|
| Vehicle manufacturers | Which ECUs and links can move on the current platform, and which wait for the next |
| ECU and software suppliers | What to disclose about an ECU or a software stack |
| Charging operators and station manufacturers | When stations can accept new certificates and algorithms |
| Operators of sector PKIs | When every verifier can accept signatures under a new algorithm |
| Type-approval authorities and technical services | Whether the evidence for a cybersecurity or update management system covers cryptography |

2. CBOM profiles in brief
-------------------------

A cryptographic bill of materials (CBOM) lists the cryptography that a product, service or system uses. It is usually written in CycloneDX. On its own, a CBOM does not say whether it contains what a reader needs, and two CBOMs of similar ECUs can describe different things in different places.

A **profile** fixes that. It states, for one decision, which facts a CBOM must contain and how they are written. A tool can then check a CBOM against the profile and give a **verdict**: the CBOM conforms or does not conform, and the verdict names any rule that failed. A profile asks only for facts. Judgements, such as whether an algorithm is still acceptable, are made by a separate **policy**, which reads the facts and gives a dated result.

A CBOM describes its subject one **interface** at a time. For an ECU, the interfaces include each in-vehicle bus it talks on, its diagnostic access, the channel that delivers its updates, and the store where it keeps its keys. For each interface, the CBOM records the protocol, the algorithms for each purpose and the library or hardware that implements them.

Records cite each other by link and digest. A reader joins them when reading and never merges them. A producer that does not want to disclose a fact can mark it as withheld, where the profile allows this, and the record can still conform.

PKI Consortium Publications 1 to 3 define all of this in full. This draft uses only what a reader needs to apply the method to vehicles.

3. What is different about cryptography in automotive
------------------------------------------------------

**Lifetimes are long and fixed early.** A platform's cryptography is chosen years before production starts, and the vehicles built on it stay in service for fifteen years or more. A manufacturer therefore reads the transition dates of NIST IR 8547 and CNSA 2.0 against the last day a vehicle will be in service, not the day it is sold.

**ECUs are constrained.** A small ECU may have too little memory to hold a post-quantum public key, too little processing to verify a post-quantum signature in the time allowed, or a bus too narrow to carry one. CAN frames, for example, carry a few bytes, and message authentication on them uses truncated symmetric tags for that reason. IoT Device Estate records these as hard limits of the device model, so that a policy can tell an ECU that will never move from one that needs only a software update.

**Update signing is the root of trust.** The algorithm an ECU uses to verify its updates decides whether anything else on it can migrate. If the verifier can be replaced by an update, the ECU can move to post-quantum signatures in service. If the verifier is fixed in boot ROM, it cannot, and the ECU stays on its algorithm until it is replaced. The question register proposes moving the update verification facts into the change core (R2-30), so that every device profile records them in the same way.

**Symmetric cryptography carries most of the in-vehicle traffic.** Message authentication between ECUs is usually symmetric, so it is not exposed to a quantum computer at the key sizes in use. What is exposed is how the symmetric keys are distributed, which is often asymmetric, and the signatures on updates and diagnostics. A record that lists only the bus authentication misses the exposure.

**Several PKIs, each with many verifiers.** Each sector PKI can move to a new algorithm only when enough verifiers accept it, and its verifiers are in vehicles and stations that change slowly. The decision is the PKI operator's, but the facts are in each participant's records.

4. Automotive in the methodology's terms
-----------------------------------------

| Automotive term | Record | Written by |
|---|---|---|
| An ECU model and software release | Product record, under IoT Device Estate | The supplier |
| A vehicle platform | System record, citing the records of its ECUs | The manufacturer |
| A vehicle in service | Deployment record of a deployed device, where needed | The manufacturer or fleet operator |
| A charging station model | Product record | The station manufacturer |
| A charging network | Service record | The charging operator |
| A sector PKI | System record of what the operator runs. Each participant records its own end, as for a payment scheme | The PKI operator and each participant |
| A telematics back end | Service record | The manufacturer or its provider |

5. Protocols and their cryptography
-----------------------------------

| Protocol or mechanism | Where | Governing specification | Cryptography | Quantum exposure |
|---|---|---|---|---|
| Secure Onboard Communication (SecOC) | Between ECUs on CAN, CAN FD and automotive Ethernet | AUTOSAR SecOC | Truncated symmetric message authentication codes, often AES-CMAC, with freshness values | Not exposed, if keys are 128 bits or more. Key distribution may be exposed |
| TLS and IPsec | Telematics unit to back end | IETF | Key exchange, certificates and symmetric ciphers | Key exchange and certificates exposed |
| Vehicle-to-everything messages | Vehicle to vehicle and to roadside units | IEEE 1609.2 and ETSI TS 103 097, with the US Security Credential Management System and the EU C-ITS Credential Management System | ECDSA signatures on broadcast messages, with short-lived pseudonym certificates | Signatures exposed |
| ISO 15118 charging communication | Vehicle to charging station | ISO 15118-2 and ISO 15118-20 | TLS with certificates from the charging PKI; Plug and Charge contract certificates | Key exchange and signatures exposed |
| Software updates | Back end to vehicle, and inside the vehicle | UN Regulation No. 156, ISO 24089, and often the Uptane framework | Signatures on update metadata and images, verified in the vehicle | The verifier is exposed if it is RSA or ECDSA |
| Diagnostic authentication | Workshop tool to ECU | ISO 14229 (UDS), with the manufacturer's scheme | Challenge and response, often with certificates | Depends on the scheme |
| Key stores | In the ECU, often a hardware security module or secure element | — | Key wrapping and storage | Usually symmetric |

The protocol names this draft adds to the working group's list are `secoc`, `ieee-1609.2`, `iso-15118-2`, `iso-15118-20` and `uptane`. They are proposed, and they will be checked against the CycloneDX cryptography registry before they are adopted.

6. Automotive use cases
-----------------------

| Use case | Who decides, and what | Profile |
|---|---|---|
| ECU procurement | A manufacturer: whether a supplier's disclosure is complete enough to compare ECUs | Procurement (Release 1), with IoT Device Estate |
| Type approval | A manufacturer: what evidence to supply for its cybersecurity and update management systems, and a technical service: whether it covers cryptography | System Disclosure for the platform, with the ECU records |
| Platform migration | A manufacturer: which ECUs and links can move on the current platform, and which wait for the next | IoT Device Estate, read over the platform's system record |
| Fleet migration in service | A manufacturer: which vehicles can be updated over the air to new algorithms | IoT Device Estate, with deployment records where needed |
| PKI migration | A PKI operator: when enough verifiers accept new signatures for signers to use them | Each participant's records, read by a readiness policy (9) |
| Charging interoperability | A charging operator: whether its stations and the vehicles that use them can move together | Product records of stations, with the vehicle's records |

7. Records across the life of a vehicle
---------------------------------------

**Platform design.** The manufacturer chooses the cryptography of the platform and writes a first system record of the design, citing the records its suppliers provide for each ECU.

**ECU sourcing.** Each supplier writes a product record for its ECU and software release. The manufacturer compares candidates under Procurement and IoT Device Estate.

**Type approval.** The manufacturer supplies its cybersecurity and update management evidence. The platform's system record, with its ECU records, shows the cryptography that evidence relies on.

**Production.** The system record is fixed for each production release of the platform. Vehicles usually do not need records of their own, because the platform's record describes them.

**Updates in service.** Each update produces new product records for the ECUs it changes, and a new system record for the platform. A vehicle that has not received an update is described by the earlier record, which is why a fleet migration may need deployment records of which vehicles run which release.

**End of support.** When the manufacturer stops offering updates for a platform, the record says so (IoT Device Estate P2). From then on, the vehicles keep their algorithms for the rest of their lives.

8. Profiles automotive relies on
--------------------------------

### 8.1 ECU extension of IoT Device Estate (proposed, for the future devices document)

An ECU is a device model, so IoT Device Estate applies. The extension would add the facts that decide whether an ECU can move:

-   **bus limits**: the bus types and the largest payload a message can carry;

-   **signature verification limits**: the largest public key and signature the ECU can hold and verify, and in how much time;

-   **the update verification algorithm**, and whether it can be replaced in service. This is the fact R2-30 proposes for the change core. If the change core adopts it, the extension cites it rather than repeating it.

The extension belongs in the future devices document, beside the medical device, payment card and terminal extensions. This draft states what automotive needs from it.

### 8.2 System Disclosure for a vehicle platform

A vehicle platform is a system of ECUs and links, so System Disclosure applies without change. Each in-vehicle link appears once, with the ECUs at each end citing their product records.

### 8.3 The change core

The change core already records whether a change can be made, who can make it and what approval it triggers. For a vehicle, `certificationImpact` records whether a change to cryptography affects type approval.

9. Policies in automotive
-------------------------

**Algorithm transition against service life.** The NIST IR 8547 schedule, read against the last day the platform's vehicles will be in service. An ECU whose algorithm will be disallowed before the end of service, and whose verifier cannot be replaced, is flagged. The schedule is `mechanical`; the expected service life is an input that the manufacturer supplies.

**PKI readiness.** For each participant of a sector PKI, whether it can verify the new algorithm, whether its configuration allows it, and whether it does. The result says when signers can start using it. The shape is the same as the scheme-readiness policy of the financial services document and the exchange-readiness policy of the healthcare document, and the three should be written once.

10. Worked examples
-------------------

### 10.1 An open-source charging stack: EVerest (proposed first)

**EVerest**, the open-source charging station software, is the proposed first example. It implements ISO 15118 with TLS and the charging PKI, its source is public, and a charging station shows both sides of the domain: the vehicle-facing interface under ISO 15118 and the back-end interface to the charging network. It is also the place where automotive meets operational technology.

### 10.2 The Uptane reference implementation (proposed)

The **Uptane** reference implementation would show the update path: the metadata roles, the signature algorithms each role uses, and where the verifier sits in the vehicle. It is the example that tests the update verification facts of 8.1.

### 10.3 An illustrative ECU (proposed)

An illustrative gateway ECU with SecOC on CAN FD, a telematics link with TLS, and a boot-ROM verifier that cannot be replaced. It would show an ECU whose bus traffic is fine, whose telematics can move by update, and whose update signing cannot move at all.

11. Standards and regulation
----------------------------

| Source | What it asks for that a CBOM can supply | What stays outside the CBOM |
|---|---|---|
| UN Regulation No. 155, cybersecurity and cybersecurity management system | Mandatory for new vehicle types since July 2022, and for all new vehicles since July 2024, in the countries that apply it. A platform's system record evidences the cryptography behind the mitigations | The management system and the risk assessment |
| UN Regulation No. 156, software update and update management system | Same dates. A record of the update interface states how updates are signed and verified | The update management processes |
| ISO/SAE 21434 | The engineering standard used to meet UN Regulation No. 155. A product record evidences the cryptographic outcome of its activities | The processes themselves |
| ISO 24089 | The engineering standard used to meet UN Regulation No. 156. The update interface's record supplies the cryptographic facts | The processes themselves |
| EU Cyber Resilience Act | Vehicles type-approved under Regulation (EU) 2019/2144 are excluded (Article 2(2)(c)), and two- and three-wheel L-category vehicles are excluded by Delegated Regulation (EU) 2025/1535. Charging equipment is not a vehicle, so the CRA applies to it, and the register's CRA questions apply to charging stations | The conformity assessment |
| IEEE 1609.2, ETSI TS 103 097 and the credential management systems | The algorithms of each participant's end of the vehicle-to-everything PKI | The PKI's certificate policy |
| ISO 15118 | The algorithms and certificates on the charging interface | The charging PKI's certificate policy |

12. Positions and open work
---------------------------

### 12.1 Release 1 positions this draft starts from

| Position | Ratified in |
|---|---|
| Facts go in the CBOM, and judgements go in a versioned policy. | Publication 2 |
| Records cite each other by link and digest, and are joined, not merged. | Publication 2 |
| Each document declares its subject type, so a CBOM can describe a device model or a deployed device. | Publication 3, position 28 |
| An IoT profile extends the change core and is not a depth of the PQC migration family. | Publication 3, position 30 |

### 12.2 Positions proposed in this draft

| Position | Chapter |
|---|---|
| An ECU is a device model under IoT Device Estate, with an ECU extension in the future devices document. | 4, 8.1 |
| A vehicle platform is a system record citing the records of its ECUs. Vehicles in service need records of their own only for fleet migration. | 4, 7 |
| Charging is part of this document. The charging station's grid side stays with the operational technology document. | 1 |
| A sector PKI is read through each participant's own records, as a payment scheme is. | 4, 9 |
| The update verification algorithm, and whether it can be replaced, is the first fact to establish for every ECU. | 3, 8.1 |

### 12.3 Open work

1.  Build the EVerest product record from its source.

2.  Send the needs in 8.1 to the future devices document, and settle R2-30.

3.  Add UN Regulations No. 155 and No. 156, ISO/SAE 21434, ISO 24089 and the CRA questions for charging equipment to the regulatory sufficiency register.

4.  Check the proposed protocol names (chapter 5) against the CycloneDX cryptography registry.

5.  Write the readiness policy once, for payment schemes, health information exchanges and sector PKIs.

Annex A. Automotive terms and methodology terms
-----------------------------------------------

| Automotive term | Methodology term |
|---|---|
| ECU | A product, a device model under IoT Device Estate |
| Vehicle platform, E/E architecture | A system record |
| Vehicle | A deployed device, where a record is needed |
| In-vehicle bus (CAN, CAN FD, automotive Ethernet) | An interface between two ECUs in the platform's system record |
| Over-the-air update | A new product record; `updateMechanism` and `updateAuthority` on the update interface |
| Secure boot, boot ROM verifier | The update verification facts (8.1, R2-30) |
| Pseudonym certificate | A certificate on the vehicle-to-everything interface |
| Plug and Charge contract certificate | A certificate on the charging interface |
| Type approval | Not a record. `certificationImpact` records whether a change affects it |
