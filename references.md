---
title: References
sideMenu: true
weight: 30
aliases:
- /cbom/references/
description: Standards, regulation and guidance relevant to Cryptography Bills of
  Materials.
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The complete editorial register is published below. Use the site search or your browser’s find command to locate an entry. [Open the original interactive register](https://pkic.github.io/cbom/references/).

## F1

**Category:** BOM formats & CBOM specifications

\[F1\] ECMA-424, 2nd edition Current

### [CycloneDX Bill of Materials Standard](https://ecma-international.org/publications-and-standards/standards/ecma-424/)

Ecma International · 2025-12 · Global

Second edition aligns to CycloneDX v1.7. The first edition (June 2024) aligned to v1.6 — cite the edition, not just the ECMA number.

cyclonedx standard

## F2

**Category:** BOM formats & CBOM specifications

\[F2\] CycloneDX v1.7 Current

### [CycloneDX Specification v1.7](https://cyclonedx.org/specification/overview/)

OWASP CycloneDX · 2025-10 · Global

Released 21 October 2025; final release of the 1.x line and backward compatible with 1.4–1.6. Adds the algorithm-family and elliptic-curve properties \`algorithmFamily\` and \`ellipticCurve\`, both constrained to enumerations held in the \`cryptography-defs\` subschema, and deprecates the free-text \`curve\` property carried since v1.6. Field names confirmed against the published 1.7 schema.

cyclonedx cbom

## F3

**Category:** BOM formats & CBOM specifications

\[F3\] CycloneDX Cryptography Registry Current

### [Cryptography Registry](https://cyclonedx.org/registry/cryptography/)

OWASP CycloneDX · 2025-10 · Global

Authoritative machine-readable registry of algorithm families and curves, published as the \`cryptography-defs\` JSON Schema and carrying its own \`lastUpdated\` timestamp rather than the specification's version. Enumerates 93 algorithm families and 246 elliptic curves, and records per-curve aliases tagged by category — which is the naming problem of Q20 expressed as data, and what makes it the natural normalisation target for a format-independent profile.

cyclonedx registry normalisation

## F4

**Category:** BOM formats & CBOM specifications

\[F4\] CycloneDX CBOM Current

### [Cryptography Bill of Materials (CBOM) capability](https://cyclonedx.org/capabilities/cbom/)

OWASP CycloneDX · Global

cyclonedx cbom

## F5

**Category:** BOM formats & CBOM specifications

\[F5\] OWASP CycloneDX Current

### [Authoritative Guide to CBOM](https://cyclonedx.org/guides/OWASP_CycloneDX-Authoritative-Guide-to-CBOM-en.pdf)

OWASP CycloneDX · Global

cyclonedx cbom guide

## F6

**Category:** BOM formats & CBOM specifications

\[F6\] SPDX 3.0.1 Draft / not binding verify

### [SPDX Specification](https://spdx.dev/)

Linux Foundation · Global

No dedicated cryptographic-asset object model equivalent to CycloneDX CBOM in the released 3.0.1 line. Work has since become concrete: an SPDX Cryptography Group now maintains a Cryptographic Algorithm List \[F9\], and a 3.1 release candidate is in progress. Confirm the 3.1 status and the standing of the algorithm list with the SPDX project before citing.

spdx

## F7

**Category:** BOM formats & CBOM specifications

\[F7\] ISO/IEC 5962:2021 Current

### Information technology — SPDX Specification V2.2.1

ISO/IEC · 2021 · Global

spdx iso

## F8

**Category:** BOM formats & CBOM specifications

\[F8\] RFC 2119 / RFC 8174 Current

### [Key words for use in RFCs to Indicate Requirement Levels (BCP 14)](https://www.rfc-editor.org/rfc/rfc8174)

IETF · 1997-03 · Global

Normative keyword vocabulary for profile conformance language.

ietf conformance

## F9

**Category:** BOM formats & CBOM specifications

\[F9\] SPDX Cryptographic Algorithm List Draft / not binding verify

### [SPDX Cryptographic Algorithm List](https://github.com/spdx/cryptographic-algorithm-list)

SPDX Cryptography Group (Linux Foundation) · Global

A community-curated vocabulary of cryptographic algorithms, modelled on the SPDX License List and maintained alongside the specification rather than inside it. It is the SPDX-side counterpart to the CycloneDX Cryptography Registry \[F3\], and therefore the normalisation target an SPDX mapping would have to use. No numbered release; its normative standing within SPDX is not established. Confirm both before citing.

spdx registry normalisation

## M1

**Category:** Methodology, sector work & tooling

\[M1\] PKIC CBOM WG Current

### [CBOM Profiles Working Group](/wg/cbom/)

PKI Consortium · Global

Vendor-neutral, format-independent methodology for defining CBOM profiles that map onto CycloneDX and SPDX. Deliverables in development: CBOM Profile Methodology and Standards Mapping Guidance.

pkic profiles

## M2

**Category:** Methodology, sector work & tooling

\[M2\] PKIC CBOM WG Charter Current

### [CBOM Profiles Working Group Charter](https://pkic.org/wg/cbom/charter/)

PKI Consortium · Global

The motivating precedent for the profile-first, format-independent methodology. Cite this — not the PQC Maturity Model, which is a separate effort.

pkic profiles

## M3

**Category:** Methodology, sector work & tooling

\[M3\] PQCC Current

### [Transitioning to Quantum-Safe Cryptography: Exploring the Role and Value of Developing and Implementing a Cryptographic Bill of Materials](https://pqcc.org)

Post-Quantum Cryptography Coalition (MITRE) · Global

pqcc cbom

## M4

**Category:** Methodology, sector work & tooling

\[M4\] PQCC Migration Roadmap Current

### [PQC Migration Roadmap](https://pqcc.org)

Post-Quantum Cryptography Coalition (MITRE) · 2025-05 · Global

Prioritise inventoried assets by data sensitivity and protection lifetime.

pqcc migration

## M5

**Category:** Methodology, sector work & tooling

\[M5\] GSMA PQ.03 v2.0 Current

### [Post Quantum Cryptography — Guidelines for Telecom Use Cases](https://www.gsma.com/solutions-and-impact/technologies/security/post-quantum-cryptography-documents/)

GSMA PQTN · 2024-10-04 · Global

gsma telecom sector-profile

## M6

**Category:** Methodology, sector work & tooling

\[M6\] GSMA PQ.06 / PQ.07 Current

### [Implementation and Prototype Verification of Post-Quantum Use (PQ.06); Post Quantum Cryptography for Non-Terrestrial Networks (PQ.07)](https://www.gsma.com/solutions-and-impact/technologies/security/post-quantum-cryptography-documents/)

GSMA PQTN · 2026-02 · Global

gsma telecom

## M7

**Category:** Methodology, sector work & tooling

\[M7\] ATIS Current

### Preparing Telecom for the Quantum-Safe Future: Why a Telecom-Specific CBOM Matters

Alliance for Telecommunications Industry Solutions · United States

atis telecom sector-profile

## M8

**Category:** Methodology, sector work & tooling

\[M8\] CBOMkit Current

### [CBOMkit — CBOM generation and analysis tooling](https://pqca.org/projects/cbomkit/)

Post-Quantum Cryptography Alliance (Linux Foundation) · Global

tooling open-source

## M9

**Category:** Methodology, sector work & tooling

\[M9\] GSMA PQ tracker Current

### [Post Quantum Government Initiatives by Country and Region](https://www.gsma.com/newsroom/post-quantum-government-initiatives-by-country-and-region/)

GSMA · Global

Maintained tracker of national PQC mandates; useful for keeping this register current.

tracker

## M10

**Category:** Methodology, sector work & tooling

\[M10\] PQCMM v1.0.1 Current

### [PQC Maturity Model](https://pkic.org/wg/pqc/pqcmm/)

PKI Consortium (Post-Quantum Cryptography Working Group) · Global

Assesses products and services in the supply chain rather than an organisation's internal posture, which makes its subject the same as this methodology's. Level 3 requires a cryptographic inventory and SBOM support; Level 4 requires CBOM support without defining what a CBOM must contain, and names no format. That undefined requirement is the dependency the profile methodology addresses.

pkic maturity cbom inventory

## M11

**Category:** Methodology, sector work & tooling

\[M11\] PQCCM Current verify

### [PQC Capabilities Matrix](https://pkic.org/wg/pqc/pqccm/)

PKI Consortium (Post-Quantum Cryptography Working Group) · Global

Aggregates vendor-declared post-quantum capability across products, recording support for ML-KEM, ML-DSA, SLH-DSA, LMS and XMSS as available, planned, unavailable or not applicable. Its subject overlaps the migration profile's declared capability attributes. No version or release date is published for the matrix itself.

pkic capabilities

## M12

**Category:** Methodology, sector work & tooling

\[M12\] PKIMM v1.0.0 Current

### [PKI Maturity Model](https://pkic.org/wg/pkimm/)

PKI Consortium (PKI Maturity Model Working Group) · Global

Assesses an organisation's PKI operation across five levels, with a separate PQC Readiness Extension. Its subject is the operator rather than the product, so it sits at a different level from both the PQCMM \[M10\] and this methodology.

pkic maturity

## M13

**Category:** Methodology, sector work & tooling

\[M13\] FS-ISAC PQC Working Group Current verify

### [Post-Quantum Cryptography Working Group papers, including Infrastructure Inventory and Building Cryptographic Agility in the Financial Sector](https://www.fsisac.com/knowledge/pqc)

FS-ISAC · Global

Sector guidance directing financial institutions to inventory cryptographic assets together with the keys, systems and business processes that depend on them. Names no format, which makes the sector a candidate consumer of a profile rather than a competing specification. Individual papers are undated on the landing page; take dates from each paper before citing.

finance inventory sector-profile agility

## M14

**Category:** Methodology, sector work & tooling

\[M14\] PCI DSS v4.0.1, requirement 12.3.3 Current verify

### [Payment Card Industry Data Security Standard](https://www.pcisecuritystandards.org/document_library/)

PCI Security Standards Council · Global

Requirement 12.3.3 obliges an entity to document an inventory of the cryptographic cipher suites and protocols in use, with where and why each is used, and to review it at least every twelve months; it became mandatory on 31 March 2025. A binding commercial inventory mandate that names no format. Confirm the requirement text and the current DSS revision against the PCI SSC library before citing.

finance inventory compliance

## M15

**Category:** Methodology, sector work & tooling

\[M15\] ETSI TR 103 619 V1.1.1 Current

### [CYBER; Migration strategies and recommendations to Quantum Safe schemes](https://www.etsi.org/deliver/etsi_tr/103600_103699/103619/01.01.01_60/tr_103619v010101p.pdf)

ETSI · 2020-07 · Global

Frames the move to a fully quantum-safe state in three stages, of which the first is compiling an inventory of cryptographic assets. The earliest inventory-first migration framework this register carries, predating the national roadmaps by several years, and it names no format.

etsi inventory migration

## E1

**Category:** Regulation & government guidance

\[E1\] Regulation (EU) 2024/2847 Current

### Cyber Resilience Act (CRA)

European Union · 2024-12 · European Union

Main obligations apply from 11 December 2027. Mandates SBOM-based supply-chain transparency; contains no direct CBOM reference.

cra sbom procurement

## E2

**Category:** Regulation & government guidance

\[E2\] Recommendation (EU) 2024/1101 Current

### Commission Recommendation on a Coordinated Implementation Roadmap for the transition to Post-Quantum Cryptography

European Commission · 2024-04-11 · European Union

pqc roadmap

## E3

**Category:** Regulation & government guidance

\[E3\] NIS CG PQC Roadmap Current

### [A Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography)

NIS Cooperation Group · 2025-06 · European Union

Milestones: 31 Dec 2026 national roadmaps plus identification and awareness (i.e. cryptographic inventory); 31 Dec 2030 high-risk use cases; 31 Dec 2035 full transition. Annual reporting from April 2026. Recommends a standardised format for cryptographic inventories — the clearest hook for a CBOM profile in EU policy.

pqc roadmap inventory

## E4

**Category:** Regulation & government guidance

\[E4\] ENISA NIS2 TIG Current

### Technical Implementation Guidance on the Cybersecurity Risk-Management Measures of NIS2 Implementing Regulation (EU) 2024/2690

ENISA · 2025-06-26 · European Union

Recommends inventorying cryptographic assets.

nis2 inventory

## E5

**Category:** Regulation & government guidance

\[E5\] BSI TR-03183-2 v2.1.0 Current

### [Cyber Resilience Requirements for Manufacturers and Products — Part 2: Software Bill of Materials (SBOM)](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TR03183/BSI-TR-03183-2_v2_1_0.html)

BSI (Germany) · 2025-08-20 · European Union

Raises CycloneDX 1.5 to 1.6 and SPDX 2.2.1 to 3.0.1. Supersedes v2.0.0.

bsi sbom cra

## E6

**Category:** Regulation & government guidance

\[E6\] BSI TR-02102-1 (2026) Current

### Cryptographic Mechanisms: Recommendations and Key Lengths

BSI (Germany) · 2026 · European Union

The German baseline for algorithm and key-length adequacy against which a CBOM profile's conformance rules would be assessed.

bsi algorithms

## E7

**Category:** Regulation & government guidance

\[E7\] BSI PQC migration guidance Current

### BSI guidance on cryptographic inventory and PQC migration

BSI (Germany) · European Union

The NIS-2 cryptographic-procedures framework follows Inventarisieren → Bewerten → Umsetzen. BSI has no official German term for CBOM; recommended first use is "CBOM (kryptografische Stückliste)".

bsi inventory pqc

## E8

**Category:** Regulation & government guidance

\[E8\] DE/FR/NL joint statement Current

### Joint statement on the transition to post-quantum cryptography

Germany, France, Netherlands · European Union

pqc

## E9

**Category:** Regulation & government guidance

\[E9\] NCSC PQC timelines Current

### [Timelines for migration to post-quantum cryptography](https://www.ncsc.gov.uk/guidance/pqc-migration-timelines)

NCSC (United Kingdom) · 2025-03 · United Kingdom

Three phases: by 2028 discovery, cryptographic inventory and migration plan; 2028–2031 high-priority upgrades; 2031–2035 full migration.

pqc inventory roadmap

## E10

**Category:** Regulation & government guidance

\[E10\] PQC Migration Handbook, 2nd edition Current

### [The PQC Migration Handbook](https://publications.tno.nl/publication/34643386/fXcPVHsX/TNO-2024-pqc-en.pdf)

AIVD, CWI and TNO (Netherlands) · 2024-12 · Netherlands

Second edition of the March 2023 handbook, presented on 3 December 2024. Covers cryptographic asset management and the creation of a cryptographic inventory, with expanded advice on discovering cryptography inside software and on crypto-agility. Guidance rather than a mandate, and it names no format.

inventory migration pqc

## E11

**Category:** Regulation & government guidance

\[E11\] ANSSI follow-up position paper Current

### [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up)](https://cyber.gouv.fr/en/publications/anssi-views-post-quantum-cryptography-transition)

ANSSI (France) · 2023 · France

Follow-up to the March 2022 position paper. Requires hybridisation wherever post-quantum mitigation is needed, on the grounds that post-quantum algorithms are not yet mature enough to stand alone, and sets the agenda for French security visas covering hybrid implementations. Bears directly on how a profile represents hybrid and coexistence as facts rather than as a judgement.

pqc hybrid certification

## E12

**Category:** Regulation & government guidance

\[E12\] NÚKIB minimum requirements Current verify

### [Minimum Requirements for Cryptographic Algorithms](https://nukib.gov.cz/download/publications_en/Minimum%20Requirements%20for%20Cryptographic%20Algorithms.pdf)

NÚKIB (Czechia) · 2025-05 · Czechia

A national algorithm and key-length baseline of the same kind as BSI TR-02102-1 \[E6\], against which a profile's conformance rules would be assessed. Revised more than once during 2025; confirm the current revision and its date against NÚKIB before citing.

algorithms pqc

## U1

**Category:** Regulation & government guidance

\[U1\] EO 14306 Current

### Sustaining Select Efforts to Strengthen the Nation's Cybersecurity and Amending Executive Order 13694 and Executive Order 14144

The White House (United States) · 2025-06-06 · United States

Amends rather than rescinds EO 14144. Directs CISA to publish a list of product categories supporting PQC; removes the 90-day solicitation trigger and the "as soon as practicable" hybrid-adoption mandate.

executive-order pqc

## U2

**Category:** Regulation & government guidance

\[U2\] CISA PQC Product Categories List Current

### [Product Categories for Technologies That Use Post-Quantum Cryptography Standards](https://www.cisa.gov/resources-tools/resources/product-categories-technologies-use-post-quantum-cryptography-standards)

CISA (with NSA) · 2026-01-23 · United States

Two tiers — Widely Available (cloud, browsers, endpoint security) and Transitioning (networking, SAN, IAM, containers). Advisory, not a procurement mandate.

pqc procurement

## U3

**Category:** Regulation & government guidance

\[U3\] EO 14144 Superseded

### Strengthening and Promoting Innovation in the Nation's Cybersecurity

The White House (United States) · 2025-01-16 · United States

Substantially amended by EO 14306.

executive-order

## U4

**Category:** Regulation & government guidance

\[U4\] EO 14028 Current

### Improving the Nation's Cybersecurity

The White House (United States) · 2021-05-12 · United States

Origin of federal SBOM procurement expectations.

executive-order sbom

## U5

**Category:** Regulation & government guidance

\[U5\] OMB M-23-02 Current

### Migrating to Post-Quantum Cryptography

Office of Management and Budget (United States) · 2022-11-18 · United States

Directs federal agencies to maintain a cryptographic inventory.

inventory pqc

## U6

**Category:** Regulation & government guidance

\[U6\] 6 U.S.C. §1526 Current

### Quantum Computing Cybersecurity Preparedness Act

United States Congress · United States

Statutory basis for federal inventories of cryptographic systems and migration prioritisation.

inventory statute

## U7

**Category:** Regulation & government guidance

\[U7\] NIST IR 8547 (ipd) Draft / not binding

### [Transition to Post-Quantum Cryptography Standards](https://csrc.nist.gov/pubs/ir/8547/ipd)

NIST · 2024-11 · United States

RSA/ECC deprecated 2030, disallowed 2035. Still an initial public draft, so the report itself binds nothing — but OMB M-26-15 \[U15\] directs agencies to align their migration plans with it "or successor document", which gives the draft timeline force it does not carry on its own. Cite it as the referenced timeline, not as a standard.

nist pqc timeline

## U8

**Category:** Regulation & government guidance

\[U8\] FIPS 203 / 204 / 205 Current

### ML-KEM, ML-DSA and SLH-DSA standards

NIST · 2024-08 · United States

nist algorithms

## U9

**Category:** Regulation & government guidance

\[U9\] NIST SP 1800-38 Draft / not binding

### [Migration to Post-Quantum Cryptography (Volumes A, B, C)](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc)

NIST NCCoE · United States

Volume B covers public-key application discovery tools and a multi-tool discovery approach — directly relevant to how a conforming CBOM is produced.

discovery tooling inventory

## U10

**Category:** Regulation & government guidance

\[U10\] CISA discovery strategy Current

### Strategy for Migrating to Automated Post-Quantum Cryptography Discovery and Inventory Tools

CISA · 2024 · United States

discovery inventory tooling

## U11

**Category:** Regulation & government guidance

\[U11\] CISA/NSA/NIST factsheet Current

### Quantum-Readiness: Migration to Post-Quantum Cryptography

CISA, NSA, NIST · 2023-08-21 · United States

inventory pqc

## U12

**Category:** Regulation & government guidance

\[U12\] NIST SP 800-218 Current

### Secure Software Development Framework (SSDF) v1.1

NIST · United States

ssdf sdlc

## U13

**Category:** Regulation & government guidance

\[U13\] CNSA 2.0 Current

### Commercial National Security Algorithm Suite 2.0

NSA · United States

algorithms nss

## U14

**Category:** Regulation & government guidance

\[U14\] EO 14412 Current

### [Securing the Nation Against Advanced Cryptographic Attacks](https://www.federalregister.gov/documents/2026/06/25/2026-12909/securing-the-nation-against-advanced-cryptographic-attacks)

The White House (United States) · 2026-06-22 · United States

Signed 22 June 2026 and published 25 June 2026. Accelerates the migration of federal systems to the NIST PQC standards and directs assistance to critical infrastructure owners and operators. The operative timetable is set out in OMB M-26-15 \[U15\], which implements it two days later.

executive-order pqc

## U15

**Category:** Regulation & government guidance

\[U15\] OMB M-26-15 Current

### [Execution of the Migration to Post-Quantum Cryptography](https://www.whitehouse.gov/wp-content/uploads/2026/06/M-26-15-Execution-of-the-Migration-to-Post-Quantum-Cryptography.pdf)

Office of Management and Budget (United States) · 2026-06-24 · United States

Implements EO 14412 \[U14\] and discharges OMB's duty under the Quantum Computing Cybersecurity Preparedness Act \[U6\]. Sets five migration phases from 2026 to 2035, and requires each agency's plan to state "the methodologies and automated tools used for the cryptographic inventory". Of that inventory it says the data "should populate a central Cryptographic Bill of Materials (CBOM)" — and names no CBOM format, which makes it the most direct statement to date of the gap this working group exists to fill. Excludes national security systems.

inventory pqc cbom discovery

## U16

**Category:** Regulation & government guidance

\[U16\] NIST CSWP 39 Current verify

### [Considerations for Achieving Crypto Agility: Strategies and Practices](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)

NIST · 2025-12 · United States

The reference OMB M-26-15 \[U15\] cites for cryptographic agility. Relevant because agility is a judgement formed from disclosed facts rather than an attribute a CBOM records, which is the separation decision 0002 rests on. An updated revision (upd1) exists; confirm which revision and date apply before citing.

nist agility

## U17

**Category:** Regulation & government guidance

\[U17\] NTIA minimum elements (2021) Superseded

### [The Minimum Elements For a Software Bill of Materials (SBOM)](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)

National Telecommunications and Information Administration (United States) · 2021-07 · United States

Issued under EO 14028 \[U4\] and the origin of the seven baseline SBOM data fields. Updated and replaced by the 2026 minimum elements \[X1\]. Retained because procurement language and existing tooling still cite it by name.

sbom minimum-elements

## A1

**Category:** Regulation & government guidance

\[A1\] CERT-In Technical Guidelines v2.0 Current

### [Technical Guidelines on SBOM, QBOM & CBOM, AIBOM and HBOM](https://www.cert-in.org.in/PDF/TechnicalGuidelines-on-SBOM,QBOM&CBOM,AIBOM_and_HBOM_ver2.0.pdf)

CERT-In / MeitY (India) · 2025-07-09 · India

The most CBOM-explicit national guideline published to date. Defines five BOM types; the CBOM is an inventory of cryptographic assets carrying metadata such as usage patterns and expiry, with a separate QBOM for quantum algorithms and quantum-safe technologies. Currently voluntary, addressed to the public sector, government, essential services and the software export industry. A strong candidate consumer of a PKIC-defined profile.

cbom qbom inventory

## A2

**Category:** Regulation & government guidance

\[A2\] MAS Circular MAS/TCRS/2024/01 Current

### [Advisory on Addressing the Cybersecurity Risks Associated with Quantum](https://www.mas.gov.sg/-/media/mas-media-library/regulation/circulars/trpd/mas-quantum-advisory/mas-quantum-advisory.pdf)

Monetary Authority of Singapore · 2024-02 · Singapore

Directs financial institutions to maintain an inventory of all cryptographic assets and identify priority assets for migration. Names no format.

inventory finance

## A3

**Category:** Regulation & government guidance

\[A3\] CSA Quantum-Safe Handbook Current

### [Quantum-Safe Handbook and Quantum Readiness Index](https://www.csa.gov.sg/)

Cyber Security Agency of Singapore · Singapore

Handbook covers discovery of cryptographic assets, risk-based prioritisation, phased migration, testing and post-migration monitoring. The Readiness Index is a five-domain self-assessment: governance, risk assessment, training and capability, external engagement, technology and agility.

inventory maturity

## A4

**Category:** Regulation & government guidance

\[A4\] CyberSecurity Malaysia PQC framework Current

### [Post-Quantum Cryptography Migration Framework](https://www.cybersecurity.my/portal-main/services/post-quantum-overview)

CyberSecurity Malaysia · Malaysia

migration

## A5

**Category:** Regulation & government guidance

\[A5\] ASD ISM / ACSC guidance Current

### [Planning for post-quantum cryptography; Information Security Manual](https://www.cyber.gov.au/business-government/secure-design/planning-for-post-quantum-cryptography)

Australian Signals Directorate · Australia

The most aggressive timeline of any jurisdiction: traditional asymmetric cryptography to cease by end 2030, pure PQC rather than hybrid, ML-KEM-1024 preferred. Control ISM-1917 already requires cryptographic dependencies to be considered in procurement.

pqc timeline procurement

## A6

**Category:** Regulation & government guidance

\[A6\] NCO interim report / CRYPTREC guidelines Current

### National Cyber Command Office PQC transition target; CRYPTREC Cryptographic Technology Guidelines (Post-Quantum Cryptography), 2024 Edition

NCO / CRYPTREC (Japan) · 2025-03 · Japan

Sets a 2035 government PQC transition target; CRYPTREC will fold NIST PQC algorithms into Japan's recommended-algorithm lists.

pqc timeline

## A7

**Category:** Regulation & government guidance

\[A7\] ASEAN — no regional framework Gap — no framework

### Absence of a regional ASEAN PQC or CBOM framework

ASEAN · ASEAN

No regional ASEAN PQC or CBOM framework exists; the ASEAN Digital Masterplan 2025 does not mention quantum. Activity is national — Singapore leads (nationwide quantum-safe network; MAS quantum-safe sandbox with DBS, HSBC, OCBC and UOB), with Malaysia and Indonesia (BSSN) following. Recorded as an engagement opportunity for the working group rather than a citable reference.

gap engagement

## A8

**Category:** Regulation & government guidance

\[A8\] KpqC master plan Current verify

### Master plan for the transition to post-quantum cryptography

National Intelligence Service and Ministry of Science and ICT (Republic of Korea) · 2023 · Republic of Korea

Sets a 2035 target for transitioning national cryptographic systems, organised in six tracks covering technology, regulation, procedure, transition support, assurance infrastructure and industrial base. Korea also runs its own KpqC algorithm selection alongside the NIST standards, so a profile applied here must carry algorithm names that are not in either carrier's registry. Primary sources are Korean-language and the document designation is not confirmed against them.

pqc timeline algorithms

## X1

**Category:** Regulation & government guidance

\[X1\] 2026 SBOM Minimum Elements Current

### [2026 Minimum Elements for a Software Bill of Materials (SBOM)](https://media.defense.gov/2026/Jul/29/2003971159/-1/-1/1/CSI_2026_cisa_sbom_minimum_elements_508c.PDF)

CISA, NSA and FBI, co-sealed with ACSC, Cyber Centre, NÚKIB, ANSSI, BSI, CERT-In, ACN, METI, NCO, NIS/NCSC, KISA, NCSC-NL, NCSC-NZ, NASK and NBU · 2026-07-29 · Global

Updates the 2021 NTIA minimum elements. Adds SBOM Generation Context (the lifecycle phase at which the data was captured), SBOM Author Signature, data format name and version, and tool provenance. Requires authors to distinguish information that is unknown from information deliberately withheld, and states that supporting automation means supporting all widely used formats rather than mandating one — both positions the profile methodology depends on. Updates and replaces the 2021 NTIA minimum elements \[U17\].

sbom minimum-elements provenance signing

## N1

**Category:** Regulation & government guidance

\[N1\] ITSM.40.001 Current

### [Roadmap for the Migration to Post-Quantum Cryptography for the Government of Canada](https://www.cyber.gc.ca/en/guidance/roadmap-migration-post-quantum-cryptography-government-canada-itsm40001)

Canadian Centre for Cyber Security · 2025-06-23 · Canada

April 2026 initial departmental migration plan with annual reporting; end 2031 high-priority systems migrated; end 2035 remaining systems.

pqc roadmap

## S1

**Category:** Protocol & algorithm specifications

\[S1\] RFC 8446 Current

### [The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/info/rfc8446)

IETF · 2018-08 · Global

The protocol behind the worked example's service interface. Defines the handshake whose negotiated result, rather than either endpoint's capability, determines the cryptography actually in use.

ietf tls protocol

## S2

**Category:** Protocol & algorithm specifications

\[S2\] RFC 4253 (with RFC 4251) Current

### [The Secure Shell (SSH) Transport Layer Protocol](https://www.rfc-editor.org/info/rfc4253)

IETF · 2006-01 · Global

The protocol behind the worked example's management interface. Authenticates with a host key rather than a certificate, which is why a profile has to name the authentication role abstractly rather than in TLS terms.

ietf ssh protocol

## S3

**Category:** Protocol & algorithm specifications

\[S3\] RFC 7748 Current

### [Elliptic Curves for Security](https://www.rfc-editor.org/info/rfc7748)

IETF · 2016-01 · Global

Defines X25519, used for key exchange in the worked example. The same curve appears in the wild as P-256-style SECG and ANSI names elsewhere, which is the naming problem the CycloneDX Cryptography Registry addresses.

ietf curves key-exchange

## S4

**Category:** Protocol & algorithm specifications

\[S4\] RFC 8032 Current

### [Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/info/rfc8032)

IETF · 2017-01 · Global

Defines Ed25519, the host key algorithm in the worked example's SSH interface.

ietf signatures

## S5

**Category:** Protocol & algorithm specifications

\[S5\] RFC 8439 Current

### [ChaCha20 and Poly1305 for IETF Protocols](https://www.rfc-editor.org/info/rfc8439)

IETF · 2018-06 · Global

The AEAD construction used by the worked example's SSH interface.

ietf aead

## S6

**Category:** Protocol & algorithm specifications

\[S6\] RFC 8017 Current

### [PKCS #1: RSA Cryptography Specifications Version 2.2](https://www.rfc-editor.org/info/rfc8017)

IETF · 2016-11 · Global

RSA, used for the server certificate signature in the worked example. Quantum vulnerable, and therefore one of the facts a post-quantum posture evaluation is derived from.

ietf rsa signatures

## S7

**Category:** Protocol & algorithm specifications

\[S7\] NIST SP 800-38D Current

### [Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)

NIST · 2007-11 · Global

Defines GCM, the mode in AES-256-GCM. Mode matters for identity: a bare "AES256" omits it, which is why encoding an algorithm name without its parameters cannot be compared reliably.

nist aead modes

## S8

**Category:** Protocol & algorithm specifications

\[S8\] Package URL (purl) Current

### [Package URL Specification](https://github.com/package-url/purl-spec)

Package URL community · Global

The identifier scheme the methodology uses to name the library implementing an interface, and the value that links a CBOM entry to vulnerability feeds and to the corresponding SBOM component.

purl identifiers

## S9

**Category:** Protocol & algorithm specifications

\[S9\] RFC 9794 Current

### [Terminology for Post-Quantum Traditional Hybrid Schemes](https://www.rfc-editor.org/info/rfc9794)

IETF · 2025-06 · Global

Informational, and the agreed vocabulary for schemes combining post-quantum and traditional algorithms — hybrid, composite, combiner. A profile describing coexistence or hybrid capability should take its terms from here rather than coin its own.

ietf hybrid terminology

## S10

**Category:** Protocol & algorithm specifications

\[S10\] ETSI TS 103 744 V1.2.1 Current verify

### [CYBER; Quantum-Safe Cryptography (QSC); Quantum-safe Hybrid Key Establishment](https://www.etsi.org/deliver/etsi_ts/103700_103799/103744/)

ETSI · 2025-03 · Global

Normative constructions for combining elliptic-curve key exchange with ML-KEM, superseding V1.1.1 of December 2020. A named construction of this kind is what an interface disclosure records when it states a hybrid key exchange, rather than the two algorithms listed separately. Confirm the published version against the ETSI portal before citing.

etsi hybrid key-exchange
