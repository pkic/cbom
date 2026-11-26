# CBOM Profiles — Application domain: Automotive (Outline)

Outline · 26 November 2026 · Mike

## Purpose and sources

The document would cover the cryptography of road vehicles and the infrastructure around them: electronic control units (ECUs) and in-vehicle networks, over-the-air updates, vehicle-to-everything communication, electric vehicle charging, and the back-end services that manage vehicles. It is written for readers outside the working group: vehicle manufacturers, suppliers of ECUs and software, charging operators, type-approval authorities and technical services. It follows the shape of the other domain documents.

Automotive is a domain of its own for four reasons:

- A vehicle stays on the road for fifteen years or more. Its cryptography is fixed at design, years before the vehicle is sold.
- Many ECUs have tight limits on memory, processing and bus bandwidth. Post-quantum signatures and keys are much larger, so the limits decide what can move. This is close to OT and to IoT Device Estate.
- Several large PKIs serve the sector: vehicle-to-everything security credentials, charging certificates, and the manufacturers' own PKIs for updates and diagnostics.
- Type approval already requires a cybersecurity management system and a software update management system, so a CBOM can serve as evidence in processes that exist.

Candidate sources, to confirm before drafting: UN Regulations No. 155 and No. 156; ISO/SAE 21434 and ISO 24089; AUTOSAR Secure Onboard Communication (SecOC); IEEE 1609.2 and ETSI TS 103 097 for vehicle-to-everything security, with the US Security Credential Management System and the EU C-ITS Credential Management System; ISO 15118 for charging; the Uptane framework for updates; and whether the Cyber Resilience Act excludes vehicles covered by type approval.

## Proposed chapters

### 1. Scope and readers
- The vehicle: ECUs, in-vehicle networks, gateways and telematics units.
- Updates: over-the-air and in-workshop software updates.
- Vehicle-to-everything communication.
- Electric vehicle charging, including Plug and Charge.
- Back-end services: telematics, remote functions and fleet management.

### 2. CBOM profiles in brief
- The same short primer as the other domain documents.

### 3. What is different about cryptography in automotive
- Design lifetimes of fifteen years or more, fixed long before sale.
- Constrained ECUs and bus bandwidth, recorded as hard limits under IoT Device Estate.
- Update signing as the root of trust: the algorithm that verifies updates, and whether it can be replaced, decide whether anything else can migrate. This connects to the change-core candidate attribute raised by the CNSA 2.0 entry in the regulatory register.
- Several sector PKIs, each with its own trust anchors and many verifiers.

### 4. Automotive in the methodology's terms
- An ECU model: a product record, written by its supplier.
- A vehicle platform: a system record, written by the manufacturer, citing its ECUs' records.
- A vehicle in service: a deployed device, where needed.
- A charging station model: a product record. A charging network: a service record.
- A sector PKI: a system record of what its operator runs, with each participant describing its own end, as for a payment scheme.

### 5. Protocols and their cryptography
- SecOC message authentication on CAN and automotive Ethernet; TLS and IPsec for telematics; IEEE 1609.2 signed messages for vehicle-to-everything; ISO 15118 with TLS and the charging PKI; Uptane metadata signatures for updates; diagnostic authentication.

### 6. Automotive use cases
- ECU procurement: a manufacturer decides whether a supplier's disclosure is complete enough to compare.
- Type approval: a manufacturer supplies evidence for its cybersecurity and update management systems.
- Platform migration: a manufacturer decides which ECUs and links can move, and which wait for the next platform.
- Fleet migration in service: a manufacturer decides which vehicles can be updated over the air.
- PKI migration: a PKI operator decides when every verifier can accept new signatures.

### 7. Records across the life of a vehicle
- Platform design, ECU sourcing, type approval, production, updates in service, end of support.

### 8. Profiles automotive relies on
- IoT Device Estate, with an ECU extension in the future devices document: bus limits, signature verification limits, and the update verification algorithm.
- System Disclosure for a vehicle platform.
- The change core, especially the update path.

### 9. Policies in automotive
- Algorithm transition with the NIST IR 8547 dates, read against the platform's production and service dates.
- PKI readiness, read over the participants' records, as the scheme-readiness policy in financial services does.

### 10. Worked examples
- Proposed: an open-source charging stack (EVerest, ISO 15118) or the Uptane reference implementation, written from its public source as a product record.

### 11. Standards and regulation
- For each: which evidence questions a CBOM answers, added to the regulatory sufficiency register.

### 12. Positions and open work

## Decisions needed before drafting
1. Ownership: which body to approach, for example Auto-ISAC, AUTOSAR or CharIN for charging.
2. Whether charging is part of this document or of a later energy document, since charging also sits at the edge of OT.
3. Whether the ECU extension is drafted in the future devices document.
