# CBOM Profiles — Application domain: Healthcare (Outline)

> This outline has been drafted as Working Draft 0.1, in [`publications/src/domain-healthcare.md`](../../publications/src/domain-healthcare.md). The outline is kept as a record of the plan.

Outline · 26 November 2026 · Mike

## Purpose and sources

The document would cover the cryptography of healthcare: connected medical devices, hospital clinical systems, health information exchange, and the services that hold health records. It is written for readers outside the working group: medical device manufacturers, hospital biomedical engineering and security teams, health information exchange operators, notified bodies and regulators. It follows the shape of the financial services, OT, telecom and SaaS documents.

Healthcare is a domain of its own for four reasons:

- Medical devices stay in service for ten years or more, and many cannot be updated without re-approval. The decision for each device model is usually update, replace, shield or accept, which is the decision IoT Device Estate was written for.
- Health data must stay confidential for decades. That makes harvest-now-decrypt-later a strong concern for the interfaces that carry it, unlike payment data.
- Regulators already ask for an SBOM in premarket submissions, so a CBOM that cites its SBOM fits a process that exists.
- Hospitals do not write the device records. They depend on what manufacturers disclose, and they buy through procurement.

Candidate sources, to confirm before drafting: section 524B of the US Federal Food, Drug, and Cosmetic Act and the FDA guidance on cybersecurity in premarket submissions; the EU Medical Device Regulation and In Vitro Diagnostic Regulation, with MDCG 2019-16 on cybersecurity; IEC 81001-5-1 and IEC 62443; the HIPAA Security Rule, including the proposed update on encryption and asset inventory; the European Health Data Space Regulation; DICOM, HL7 FHIR and SMART on FHIR, and IHE profiles such as ATNA; and the post-quantum work of Health-ISAC.

## Proposed chapters

### 1. Scope and readers
- Connected medical devices: imaging, infusion pumps, patient monitors, implantable devices and their programmers.
- Hospital clinical systems: electronic health records, picture archiving, laboratory systems.
- Health information exchange between providers, payers and public health bodies.
- Out of scope for a first version: genomic data platforms and research environments, unless a member offers an example.

### 2. CBOM profiles in brief
- The same short primer as the other domain documents.

### 3. What is different about cryptography in healthcare
- Long device lifetimes and re-approval when cryptography changes. `certificationImpact` records the approval a change triggers.
- Long confidentiality of health data, which raises the priority of key establishment on interfaces that carry it.
- Devices that cannot be updated, recorded as permanent limits under IoT Device Estate.
- Clinical safety: a cryptographic change must not interrupt care, which constrains `coexistence` and timing.

### 4. Healthcare in the methodology's terms
- A device model: a product record under IoT Device Estate, written by the manufacturer.
- A hospital's fleet of a model: deployment records, written by the hospital.
- A clinical system as built in one hospital: a system record.
- A health information exchange or cloud health record: a service record.

### 5. Protocols and their cryptography
- DICOM over TLS, HL7 v2 over TLS (MLLP), HL7 FHIR with SMART on FHIR (OAuth 2.0 and OpenID Connect), IHE ATNA, device programming links (often proprietary, sometimes short-range radio), Bluetooth Low Energy for wearables and home devices.

### 6. Healthcare use cases
- Device procurement: a hospital decides whether a manufacturer's disclosure is complete enough to compare.
- Premarket submission: a manufacturer supplies evidence to a regulator or notified body.
- Fleet migration: a hospital decides, per device model, whether to update, replace, shield or accept.
- Health record protection: a records owner decides which stores and links to protect first, given how long the data must stay confidential.
- Vulnerability response: a hospital decides which devices an advisory reaches.

### 7. Records across the life of a medical device
- Design and premarket submission, approval, deployment in a hospital, updates and re-approval, end of support, decommissioning.

### 8. Profiles healthcare relies on
- IoT Device Estate, with a medical device extension in the future devices document: approval reference, whether a cryptographic change needs re-approval, and the support end date.
- Procurement and Service Disclosure from Release 1.
- A data-lifetime extension, which depends on cluster J of the decision backlog (data and harvest-now-decrypt-later).

### 9. Policies in healthcare
- Algorithm transition with the NIST IR 8547 dates, weighted by data lifetime.
- Fleet readiness: for each device model, whether it can move, and whether the hospital has moved it.

### 10. Worked examples
- Proposed: an open-source DICOM toolkit (dcmtk) or an open-source FHIR server (HAPI FHIR), written from its public source as a product record.
- Proposed: an illustrative infusion pump as a device-model record.

### 11. Standards and regulation
- For each: which evidence questions a CBOM answers, added to the regulatory sufficiency register.

### 12. Positions and open work

## Decisions needed before drafting
1. Ownership: which body to approach, for example Health-ISAC, IHE or a manufacturers' association.
2. Whether the medical device extension is drafted in the future devices document, as the card and terminal extensions are.
3. Which open-source product to build the first example on.
