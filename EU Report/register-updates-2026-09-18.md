# Register and decision-record updates needed

**Why this file exists.** The report cites `register.md`, `decisions.md`, `pkic-feedback.md` and
`verification-log.md`, and none of them is in the connected `EU Report` folder — only the built
draft is. The `decisions/` directory in the repository root holds the *methodology's* numbered
records (0001 onward), which are a different series from the report's `DR-01`…`DR-12`. So these
entries could not be applied. Paste them into the files where they live.

---

## 1. `decisions.md` — amend DR-05

DR-05 set a six-page cap on chapters 6, 7 and 8. Chapter 8 now carries §8.7 and §8.8, which answer
objections rather than account for gaps, and it exceeds the cap.

> **DR-05 (amended, September 2026).** The six-page cap stands for chapters 6 and 7. It is lifted for
> chapter 8, which now also answers the aggregation-risk and proportionality objections (§8.7, §8.8).
> Those sections respond to readers rather than accounting for gaps, and the alternative considered —
> promoting them to a chapter of their own — was rejected because it would renumber chapters 9 to 12
> and every cross-reference to them.

The chapter 8 header in the draft already says "Cap lifted (DR-05 amended)" and carries a blockquote
flagging that this entry is outstanding. Delete the blockquote once the record exists.

---

## 2. `register.md` — no new IDs, four revised entries

**The count is unchanged.** No `GAP-*`, `RDY-*`, `LSN-*` or `LYR-*` identifier was created or
retired, so the report's "twenty-five gaps" and "nine readiness criteria" both still hold. Four
existing entries need their wording brought into line with the body.

**GAP-STD-01, format asymmetry.** The body no longer says the SPDX cryptography workstream
"describes itself as at the beginning". As at mid-2026 it had six algorithm classes defined,
inclusion and removal criteria agreed, parameter representation in progress, and post-quantum status
being added as an orthogonal property. The asymmetry claim survives; "at the beginning" does not. The
body also now carries the market shares (CycloneDX 44%, SPDX 29%).

**GAP-STD-07, protocol profiling.** Retitle from "still landing" to "uneven by family". The TLS
family closed between June and September 2026: RFC 9954, RFC 10024, and two drafts in the RFC Editor
queue. IPsec was already mature. JOSE, COSE and the sector protocols are not.

**GAP-LIFE-02, hardware cannot move on a software cadence.** Add the second form of the gap. A module
may offer post-quantum algorithms while the cryptography protecting the module stays classical:
firmware authentication, secure boot, administrative authentication, key backup and attestation.
Those migrate on the vendor's architecture cycle rather than on a firmware release.

**GAP-TOOL-02, opaque firmware and modules.** Add the granularity point. Opacity forces the operator
to accept a vendor summary, and vendor summaries are made at the wrong granularity: a single claim
about a product cannot be true of six cryptographic interfaces that migrate separately.

**One count to re-check.** §7.8 previously said thirteen of twenty-five gaps bite at LYR-C-04; the
table lists twelve, and the body now says twelve. If the register's layer tags say thirteen, one gap
is missing from the §7.8 table rather than the count being wrong. Worth resolving in the register
rather than the body.

---

## 3. `verification-log.md` — facts verified 18 September 2026

New or corrected entries, each with the source that was read.

| Claim | Verified position | Source |
|---|---|---|
| TLS hybrid key agreement | RFC 9954, Informational, July 2026 | IETF datatracker |
| TLS hybrid groups (ECDHE-MLKEM) | RFC 10024, Standards Track, August 2026 | IETF datatracker |
| TLS ML-KEM-only key agreement | `draft-ietf-tls-mlkem-11`, 17 Sep 2026, RFC Editor queue | IETF datatracker |
| TLS ML-DSA authentication | `draft-ietf-tls-mldsa-06`, 11 Sep 2026, RFC Editor queue | IETF datatracker |
| HSM Level 3 validations covering PQC | Two: Thales TCT Luna T-Series, 29 July 2026; Crypto4A QASM, 20 August 2026. Mainstream commercial lines still queued | Industry analysis — **confirm against the CMVP validated-modules list** |
| HSM internal vs external PQC support | Almost all vendors expose PQC through the API; few have migrated roots of trust, boot and internal key wrapping | ABI Research; `draft-reddy-pquip-pqc-hsm` covers firmware signing only |
| ENISA SBOM survey | 334 respondents, ~two thirds EU, >80% in CRA scope. CRA accelerator 43% significant / 29% moderate. Receive: 2% always, 39% rarely, 39% never. Gap: 44% moderate, 23% significant, 7% none. Maturity: 9% mature, 25% broad, 44% pilot, 78% started. Formats: CycloneDX 44%, SPDX 29%, proprietary 17%, non-standard 11%. Skills barrier 28% | ENISA, *SBOM Adoption State of Play – 2026*, 9 June 2026 |
| The "seven in ten" expertise figure | Comes from separate stakeholder-group research, not from ENISA, whose own skills-barrier figure is 28%. The body now reconciles the two | Kloeg et al. — **full citation still needed** |
| NIS CG roadmap, CBOM naming | §6.2, First Steps: "Using a standardised format for a cryptographic inventory, like CBOM (Cryptographic Bill of Materials, an extension of the SBOM standard), is recommended." | Roadmap PDF, p. 11 |
| NIS CG roadmap milestones | 31 Dec 2026 First Steps and initial national roadmaps; 31 Dec 2030 complete for high-risk use cases; 31 Dec 2035 medium-risk and low-risk where feasible. **2035 is in the roadmap**, separate from NIST IR 8547's 2035 date | Roadmap PDF |
| Earlier milestone wording | A secondary source described the end-2026 milestone as "a completed cryptographic inventory covering all systems using public-key cryptography". The primary does not say that. Corrected in the executive summary and §5.1 | — |
| COM(2026) 13 | Proposed NIS2 amendment, 20 January 2026. Feedback closed 22 April 2026, TTE Council 9 June 2026, no agreement as at September 2026 | NIS2 timeline; DLA Piper |
| COM(2026) 11 | Proposal for a Regulation on the EU Cybersecurity Act (CSA2), 20 January 2026. Same package as COM(2026) 13 | Commission digital-strategy library |
| CRA status | Reporting obligations apply from 11 September 2026, ENISA platform live. Full application 11 December 2027. No harmonised standard cited in the OJ. Core horizontals expected 31 Oct 2026, verticals 31 Dec 2026, remaining horizontals late 2027. 17 ETSI vertical drafts in public enquiry, comments closing mid-Sept to mid-Nov 2026 | cyberresilienceact.eu — **confirm against the OJ and the CEN-CENELEC/ETSI work programmes** |
| EUCC | 29 certificates in the first operational year, 28 accredited CABs. Commission aspiration of sufficient notified bodies by Dec 2026. Roughly two thirds of Member States lack the national accreditation infrastructure. ENISA runs 18 EUCC-to-CRA presumption-of-conformity pilots | Conference report — **confirm against ENISA's certificate list** |
| EO 14412 | Signed 22 June 2026, Federal Register 25 June 2026. §5(d): within 270 days, "the Secretary of Homeland Security, through the Director of CISA, and in coordination with the Director of NIST, shall release public guidance describing the agencies' considered view as to the minimum elements for a cryptographic bill of materials" | Federal Register full text |
| CycloneDX / ECMA-424 | v1.7 released 21 October 2025; ratified as ECMA-424 2nd Edition December 2025 | ECMA |
| CycloneDX field names | `cryptoProperties` and its enumerations, `compositions`, `declarations` (assessors, attestations, claims, evidence, targets, affirmation, signature), `definitions.standards`, `metadata.lifecycles[].phase`, and component `evidence` down to `identity.methods[].technique` — all read from the 1.7 schema | CycloneDX 1.7 schema; python library docs |
| SPDX | 3.0.1 (17 Dec 2024) is still the current full release; 3.1 at release candidate. Nine compliance points, **no cryptography profile**. `Relationship` is a first-class Element with from/to/relationshipType/completeness/startTime/endTime and can carry extensions | SPDX 3.0.1 specification |
| BSI TR-03183 | Now four parts. Part 1 v1.0.0, 31 July 2026, controls in OSCAL. Part 2 v2.1.0, 20 August 2025, unchanged. Part 3 v1.0.0, September 2025. Part H v1.1.0, 30 May 2026. **No part covers cryptography or a CBOM** | BSI; sbomify analysis |
| NIST IR 8547 | **Still an initial public draft** (12 November 2024), not finalised as at September 2026. Deprecates RSA and ECC after 2030, disallows after 2035, on a timeline that may shift | Secondary — confirm on CSRC |
| CA/Browser Forum | No merged requirement permitting ML-DSA in publicly trusted certificates. Chrome 150 ships ML-DSA trust anchors for private PKI; Microsoft piloting ML-DSA X.509 outside Web PKI; CT-log carve-out unresolved. SC-081v3 validity: 200 days from 15 Mar 2026, 100 from 15 Mar 2027, 47 from 15 Mar 2029 | SCWG minutes, 21 May 2026 |
| Quantum Act | Commission work programme 2026, Q2 2026. Research coordination, industrial capability, quantum supply chains. **Not an instrument about migrating existing cryptography** | EP Legislative Train |
| ENISA NIS2 guidance | *Technical Implementation Guidance on Commission Implementing Regulation (EU) 2024/2690*, v1.0, June 2025. **The claim that it recommends inventorying cryptographic assets could not be confirmed from a full-text search.** Read its cryptography section against Annex point 9 of CIR 2024/2690 | ENISA PDF |

---

## 4. `pkic-feedback.md` — unchanged, but no longer surfaced in the report

The report no longer routes its own open questions back to the working group. `P-08`, `P-11`, `P-12`,
`P-17` and `P-18` are gone from the body, and §9.5 no longer says "twenty findings are routed back".

Nothing was withdrawn. The findings stand as working-group input; the Commission report simply stops
being the place they are announced. Two of them are now answered inside the report instead, and the
feedback file should record where:

- **P-12**, what a conforming producer does while a format gap is open, is answered at Annex B §B.6:
  emit the attribute in a namespace tied to the profile, never simulate a native field, and re-check
  on every format release.
- **P-08**, whether an extending profile may narrow obligations or only add them, is framed at §11.6
  as a rule the EU baseline has to settle centrally, with the consequence stated: if a sector profile
  may relax a baseline obligation, a supplier conforming to the sector profile is not necessarily
  conforming to the baseline.

---

## 5. Also outstanding, and needing a person rather than a source

- **The attribution line** in the title block still reads "PKI Consortium CBOM Profiles Working
  Group _(confirm attribution and any co-signatories before submission)_".
- **Kloeg et al.** needs a full citation in Annex D.6, given the weight §6.1 puts on it.
- **Word or PDF conversion.** The markdown copy is not the deliverable for a government-facing
  output, and pagination comes from that step.
