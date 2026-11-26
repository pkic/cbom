CBOM Profiles — Application domain: Healthcare
==============================================

Working Draft 0.1 · Nov 26, 2026 · \@Mike

Purpose
-------

This draft covers the cryptography of healthcare: connected medical devices, hospital clinical systems, the exchange of health information between organisations, and the services that hold health records. It is written for readers outside the working group: medical device manufacturers, hospital clinical engineering and security teams, operators of health information exchanges, notified bodies and regulators.

Healthcare is a domain of its own for four reasons:

-   Medical devices stay in service for ten years or more, and many cannot change their cryptography without re-approval. For each device model, a hospital usually chooses between updating it, replacing it, shielding it behind something else, or accepting the risk. That is the decision IoT Device Estate was written for.

-   Health data must stay confidential for decades. Harvest-now-decrypt-later is therefore a real concern for every interface that carries it, unlike payment data, which loses its value quickly.

-   Regulators already ask manufacturers for an SBOM in premarket submissions. A CBOM that cites its SBOM fits a process that exists.

-   Hospitals do not write the device records. They depend on what manufacturers disclose, and they buy devices through procurement.

This is a working draft. It sits outside Release 1 and starts from the positions that Release 1 ratified. Positions proposed here are listed in chapter 12.

1. Scope and readers
--------------------

The draft covers:

-   **connected medical devices**, such as imaging systems, infusion pumps, patient monitors, and implantable devices with their programmers;

-   **hospital clinical systems**, such as electronic health records, picture archiving and laboratory systems;

-   **health information exchange** between providers, payers and public health bodies;

-   **cloud services that hold health records**, as services the hospital does not run.

Genomic data platforms and research environments are out of scope for a first version. They will be considered when a member offers a worked example.

The readers are:

| Reader | What they decide |
|---|---|
| Medical device manufacturers | What to disclose about a device, and how |
| Hospital clinical engineering and security | Which devices to update, replace, shield or accept, and in which order |
| Health information exchange operators | When their participants can move to new algorithms |
| Notified bodies and regulators | Whether a submission's cryptographic documentation is complete |

2. CBOM profiles in brief
-------------------------

A cryptographic bill of materials (CBOM) lists the cryptography that a product, service or system uses. It is usually written in CycloneDX. On its own, a CBOM does not say whether it contains what a reader needs, and two CBOMs of similar devices can describe different things in different places.

A **profile** fixes that. It states, for one decision, which facts a CBOM must contain and how they are written. A tool can then check a CBOM against the profile and give a **verdict**: the CBOM conforms or does not conform, and the verdict names any rule that failed. A profile asks only for facts. Judgements, such as whether an algorithm is still acceptable, are made by a separate **policy**, which reads the facts and gives a dated result.

A CBOM describes its subject one **interface** at a time. For a medical device, the interfaces include the link to the hospital network, the link to the programmer or the companion app, the channel that delivers software updates, and the store where the device keeps patient data. For each interface, the CBOM records the protocol, the algorithms for each purpose and the library that implements them.

Records cite each other by link and digest. A reader joins them when reading and never merges them. A producer that does not want to disclose a fact can mark it as withheld, where the profile allows this, and the record can still conform.

PKI Consortium Publications 1 to 3 define all of this in full. This draft uses only what a reader needs to apply the method to healthcare.

3. What is different about cryptography in healthcare
------------------------------------------------------

**Devices live long and change slowly.** A medical device is often in service for more than a decade. A change to its cryptography may need a new submission to the regulator. IoT Device Estate records the hard limits of a device model, whether the manufacturer will still offer firmware, and whether the device's keys and update verifier can be replaced. The change core and the PQC migration profile record the approval a change triggers, with `certificationImpact` and `certificationScheme`.

**Health data stays sensitive for decades.** A patient record, an image or a genome stays sensitive for the patient's lifetime and often beyond. An adversary who records traffic today could read it once a quantum computer can break the key exchange that protected it. The interfaces that carry health data therefore come first, and a hospital needs to know how long the data on each interface must stay confidential. That lifetime is held in the operator's data register, which a deployment record points to (`data-register`). How the register is linked is open as cluster J of the decision backlog.

**Some devices can never change.** A device whose verifier is fixed in boot ROM can never accept firmware signed with a new algorithm. IoT Device Estate records this as a permanent limit, and the question register proposes moving the update verification facts into the change core (R2-30). For such a device the choice is to shield it or to replace it.

**Clinical safety constrains timing.** A cryptographic change must not interrupt care. Whether old and new algorithms can run side by side (`coexistence`) decides whether a hospital can move one device at a time, without a maintenance window across a ward.

**Hospitals rely on what manufacturers disclose.** A hospital cannot inspect most of its devices. It reads the manufacturer's product record and writes its own deployment record of what it has configured and observed. The hospital's record cites the manufacturer's.

4. Healthcare in the methodology's terms
-----------------------------------------

| Healthcare term | Record | Written by |
|---|---|---|
| A medical device model and software release | Product record, under IoT Device Estate | The manufacturer |
| A hospital's fleet of one model | Deployment records, citing the product record | The hospital |
| A clinical system as built in one hospital, such as a picture archive with its modalities | System record, citing the product records | The integrator or the hospital |
| A health information exchange | Each participant records its own end. The exchange operator records what it runs | Each party |
| A cloud health record service | Service record | The provider |

5. Protocols and their cryptography
-----------------------------------

| Protocol or mechanism | Where | Governing specification | Cryptography | Quantum exposure |
|---|---|---|---|---|
| DICOM over TLS | Modality to archive, archive to viewer | DICOM PS3.15 secure transport connection profiles | TLS, often with device certificates | Key exchange and certificates exposed |
| HL7 version 2 over TLS | Between clinical systems | HL7 version 2 with TLS on the transport | TLS | Exposed |
| HL7 FHIR with SMART on FHIR | Apps and systems to health record APIs | HL7 FHIR, SMART App Launch | TLS, with OAuth 2.0 and OpenID Connect tokens signed by the authorisation server | TLS and token signatures exposed |
| IHE ATNA | Between systems that exchange records | IHE IT Infrastructure, Audit Trail and Node Authentication | Mutually authenticated TLS, and audit records | Exposed |
| Device programming links | Programmer or app to implant or wearable | The manufacturer's specification, sometimes Bluetooth Low Energy | Often proprietary, sometimes symmetric only | Depends on the device |
| Software update channel | Manufacturer to device | The manufacturer's specification | A signature over the update, verified on the device | The verifier is exposed if it is RSA or ECDSA |
| Stored patient data | On the device or in the archive | — | Disk or record encryption | Symmetric: not exposed |

The protocol names this draft adds to the working group's list are `dicom-tls`, `hl7v2-mllp-tls`, `fhir-smart` and `ihe-atna`. They are proposed, and they will be checked against the CycloneDX cryptography registry before they are adopted.

6. Healthcare use cases
-----------------------

| Use case | Who decides, and what | Profile |
|---|---|---|
| Device procurement | A hospital: whether a manufacturer's disclosure is complete enough to compare devices | Procurement (Release 1), with IoT Device Estate |
| Premarket submission | A manufacturer: what cryptographic documentation to submit, and a reviewer: whether it is complete | IoT Device Estate, with the medical device extension (8.1) |
| Fleet migration | A hospital: for each device model, whether to update, replace, shield or accept | IoT Device Estate |
| Health record protection | A records owner: which stores and links to protect first, given how long the data must stay confidential | Deployment Disclosure, read with the data register |
| Vulnerability response | A hospital: which devices an advisory about a library reaches | The baseline, through I9 with R2 and R3 |
| Exchange readiness | A health information exchange: when every participant can move to new algorithms | Each participant's records, read by a readiness policy (9) |

7. Records across the life of a medical device
-----------------------------------------------

**Design and submission.** The manufacturer writes a product record for each device model and software release, citing its SBOM. In the United States the SBOM is already part of the premarket submission for a cyber device. The CBOM can travel with it.

**Approval and deployment.** The hospital reads the product record when it buys the device. When the device is installed, the hospital writes a deployment record of what it has configured: the certificates loaded, the network it sits on, and which interfaces are enabled.

**Updates and re-approval.** A software update produces a new product record. If the update changes the cryptography in a way that needs re-approval, the record states it with `certificationImpact`.

**End of support.** When the manufacturer stops offering software for the model, the product record says so (IoT Device Estate P2). From then on, the hospital's only choices are to shield the device or replace it.

**Decommissioning.** The hospital's last deployment record states that the device's keys and stored data have been destroyed.

8. Profiles healthcare relies on
--------------------------------

### 8.1 Medical device extension of IoT Device Estate (proposed, for the future devices document)

A medical device is a device model in a fleet, so IoT Device Estate applies (question register, R2-24). The extension would add three facts:

-   **the regulatory approval** of the device, such as a 510(k) number or a CE certificate, and whether a cryptographic change needs a new submission;

-   **the support end date**, after which the manufacturer offers no software;

-   **the clinical safety constraint** on changing cryptography in service, such as whether the device must be taken out of use to be updated.

The extension belongs in the future devices document, beside the payment card and terminal extensions, and this draft states what healthcare needs from it.

### 8.2 Release 1 profiles

Procurement, Deployment Disclosure, System Disclosure and Service Disclosure apply without change.

### 8.3 Data lifetime

How long the data on each interface must stay confidential is the operator's fact, held in its data register. A healthcare policy needs it to rank interfaces. The working group has not yet settled how the register is linked (cluster J). Until it has, a hospital supplies the lifetime as a policy input.

9. Policies in healthcare
-------------------------

**Algorithm transition, weighted by data lifetime.** The NIST IR 8547 schedule, read together with how long each interface's data must stay confidential. An interface that carries data needing protection beyond the expected arrival of a quantum computer is ranked before one that does not. The schedule is `mechanical`; the weighting by lifetime is `interpretive`, because the expected arrival date is a judgement.

**Fleet readiness.** For each device model, whether it can move (product record), whether the manufacturer still supports it (IoT Device Estate), and whether the hospital has moved it (deployment record). The result sorts the fleet into update, replace, shield and accept.

**Exchange readiness.** For each participant of a health information exchange, whether it can use the new algorithms, whether its configuration allows them, and whether it uses them. This is the same shape as the scheme-readiness policy of the financial services document, and the two should be written once.

10. Worked examples
-------------------

### 10.1 An open-source DICOM toolkit (proposed first)

**DCMTK**, the open-source DICOM toolkit, is a good first example. It implements DICOM network communication with TLS through OpenSSL, it is used in many imaging products, and its source is public. The record would show a DICOM TLS interface whose key exchange and certificate algorithms depend on the OpenSSL version and configuration underneath.

### 10.2 An open-source FHIR server (proposed)

**HAPI FHIR** would show the token side: a FHIR API protected by OAuth 2.0 and OpenID Connect, where the signature algorithm of the tokens matters as much as TLS.

### 10.3 An illustrative infusion pump (proposed)

An illustrative device-model record, with a fixed verifier in boot ROM and an end-of-support date, to show a device that can only be shielded or replaced.

11. Standards and regulation
----------------------------

| Source | What it asks for that a CBOM can supply | What stays outside the CBOM |
|---|---|---|
| US Federal Food, Drug, and Cosmetic Act, section 524B | Since 29 March 2023, a premarket submission for a cyber device must include an SBOM and show that the device is cybersecure. A CBOM that cites the SBOM adds the cryptography per interface | The manufacturer's processes and the regulator's assessment |
| FDA guidance on cybersecurity in medical devices | The guidance, last replaced on 3 February 2026, describes the documentation FDA expects, including encryption, authentication, firmware signing and key management. A product record supplies the facts for each interface | The threat model and the risk assessment |
| EU Medical Device Regulation and In Vitro Diagnostic Regulation, with MDCG 2019-16 | IT security requirements across the device's lifecycle. The Cyber Resilience Act does not apply to these devices (Article 2(2)(a) and (b)), so these regulations are the ones that count | The conformity assessment |
| IEC 81001-5-1 | Security activities across the lifecycle of health software. A product record evidences the cryptographic outcome | The processes themselves |
| HIPAA Security Rule, proposed update of 6 January 2025 | The proposal would require an inventory of technology assets that handle electronic health information, and encryption at rest and in transit. It is not final; final action is now expected in July 2027. Deployment records would supply the cryptographic part of the inventory | The rest of the inventory, such as owners and network maps |
| NIS2, through national transposition | Healthcare providers are covered entities. The cryptography policy questions of the regulatory sufficiency register apply | The entity's policy and procedures |
| European Health Data Space Regulation | Requirements on the security of electronic health record systems. To be mapped in the regulatory sufficiency register | — |

12. Positions and open work
---------------------------

### 12.1 Release 1 positions this draft starts from

| Position | Ratified in |
|---|---|
| Facts go in the CBOM, and judgements go in a versioned policy. | Publication 2 |
| Records cite each other by link and digest, and are joined, not merged. | Publication 2 |
| Each document declares its subject type, so a CBOM can describe a device model or a deployed device. | Publication 3, position 28 |
| An IoT profile extends the change core and is not a depth of the PQC migration family. | Publication 3, position 30 |
| The operator's data register holds what data each interface carries, linked by a context pointer. | Publication 2 |

### 12.2 Positions proposed in this draft

| Position | Chapter |
|---|---|
| A medical device is a device model under IoT Device Estate, with a medical device extension in the future devices document. | 4, 8.1 |
| In healthcare, the interfaces that carry health data come first in a post-quantum migration, because the data must stay confidential for decades. | 3 |
| A CBOM travels with the SBOM in a premarket submission and cites it. | 7, 11 |
| A health information exchange is read through each participant's own records, as a payment scheme is. | 4, 9 |

### 12.3 Open work

1.  Build the DCMTK product record from its source.

2.  Send the needs in 8.1 to the future devices document.

3.  Add section 524B, the FDA guidance, the Medical Device Regulation, IEC 81001-5-1 and the proposed HIPAA update to the regulatory sufficiency register.

4.  Check the proposed protocol names (chapter 5) against the CycloneDX cryptography registry.

5.  Settle with cluster J how a deployment record links to the data register, so that data lifetime can be read by a policy.

Annex A. Healthcare terms and methodology terms
-----------------------------------------------

| Healthcare term | Methodology term |
|---|---|
| Medical device, cyber device | A product, a device model under IoT Device Estate |
| Device fleet | Deployment records of one model |
| Modality, archive, viewer | Products in a system record |
| Premarket submission | Not a record. The CBOM travels with it |
| Software update, patch | A new product record; `updateMechanism` and `updateAuthority` on the update interface |
| End of support | IoT Device Estate P2 |
| Protected health information | Data carried by an interface, in the operator's data register |
