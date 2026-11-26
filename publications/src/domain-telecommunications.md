CBOM Profiles — Application domain: Telecommunications
======================================================

Working Draft 0.1 · Nov 16, 2026 · \@Mike

Purpose and sources
-------------------

This document would cover telecommunications networks across all four use-case groups, for readers outside the working group: operators, network equipment vendors, regulators and enterprise customers of critical communications. It follows the shape of the OT domain document. Profiles written for telecom live here. Profiles that serve every sector stay in Release 1.

The main source is the existing telecom paper, *CBOM for Telecommunications* v1.0. It already sets out the network domains in scope, a use-case-led approach, the operator use cases and procurement. This document would take that material, tie each use case to a profile and a decision, and add worked examples.

Telecom is the second domain because it tests the methodology in a different way from OT. Its interfaces are defined by standards bodies as reference points, its products are increasingly software run by the operator, and its estates are very large and multi-vendor.

This is a working draft. Every chapter is drafted. Chapter 5 and Annex A give the cryptography each specification defines and its post-quantum status as of November 2026, against 3GPP Release 20 and TR 33.703.

Chapters
--------

### 1. Scope and readers

This document covers public mobile networks. Their domains are radio access, the core, transport and interconnect, operations and management, and the platform beneath them (the telecom paper, section 2). A private 5G network is in scope where an operator runs it. The industrial systems it connects belong to the OT domain document.

It is written for operator security, PQC migration and procurement teams, for network equipment vendors, for regulators, and for enterprise customers of critical communications services, such as public safety agencies.

The main source is the GSMA draft *CBOM for Telecommunications* v1.0. That paper makes the case for profiles and names the use cases. This document ties each use case to a profile published in Release 1 or drafted here, and adds worked examples.

### 2. CBOM profiles in brief

A CBOM profile is a set of rules for one kind of reader. It says which facts a record must state and which it may withhold. A required fact reported as unknown fails. A tool evaluates a record against a profile and gives a verdict: conforms or does not conform, with the rules that failed.

A verdict says the record is complete enough for its reader. It does not say the cryptography is good. That judgement belongs to a policy, which reads a conforming record and reports, for example, which algorithms are deprecated after a given date.

The unit of a record is the interface: a place where the subject uses cryptography with something else, such as N32-c on a SEPP. Each interface states its protocol, key exchange, encryption and authentication, and the library and provider behind them.

Three kinds of record matter in telecom. A vendor writes a product record for a network function release. An operator writes a deployment record for what it runs. An operator or integrator writes a system record for a service, citing the product records it is built from. Publication 1 defines them; Publication 2 sets out the profiles.

### 3. What is different about cryptography in telecom

-   Interfaces are defined by standards bodies as reference points, with their security set by 3GPP, the O-RAN ALLIANCE, GSMA or ETSI. The telecom paper treats a reference point as a cryptographic dependency of the network function.

-   Network functions are increasingly cloud-native software that the operator runs on its own platform, so the vendor's product record and the operator's deployment record split differently from OT.

-   Estates are very large and multi-vendor, so comparability between vendors matters more than detail from one.

-   Some cryptography is fixed at issue and outlives the network: subscriber credentials on SIM cards and the algorithms on deployed devices.

-   Roaming and interconnect cross operator boundaries, so two operators each hold one end of a connection.

Most of what a telecom consumer needs is already in the Release 1 baseline: the protocol, key exchange, encryption and authentication of every interface, and the library and provider behind them. Telecom adds three things. It names the reference point an interface implements. It splits the vendor's record from the operator's for software the operator runs. And some of its records span an operator boundary.

### 4. The telecom system in the methodology's terms

| Telecom term                                                                                 | Record                                    | Written by                    | Subject type and stage                                                                                                 |
|-----------------------------------------|-------------------|---------------|-------------------------|
| A network function release                                                                   | Product record                            | The vendor                    | `product`, `implemented`                                           |
| A deployed network function, cluster or site                                                 | Deployment record                         | The operator                  | `deployment`, `configured` or `observed` |
| A service carried across network functions, such as mission-critical push-to-talk or roaming | System record, citing the product records | The operator or an integrator | `system`, `configured`                                             |
| A managed platform or service from a provider                                                | Service record                            | The provider                  | `service`, `configured` or `observed`    |

A reference point is an interface of the network function that implements it. The interface carries the protocol name and, in the proposed network function profile, the reference point and the specification that profiles it (8.1). N32 on a SEPP is one interface; each service-based interface the function exposes is another.

Interconnect between operators is a connection read from both ends. Each operator's record holds its own end, and the edge-posture policy reads the two records together. Neither operator describes the other's end.

A cloud-native network function splits three ways. The vendor's product record states what the function implements and supports. The operator's deployment record states what is configured. The platform beneath, such as the container platform, the service mesh and the HSM, has its own record. Where a service mesh terminates TLS on the function's behalf, the interface belongs to the mesh, and the deployment record says so. Release 1 records it: each interface of a deployment record names what terminates its cryptography with `terminatedBy` (8.4).

### 5. Protocols and their cryptography

Telecom cryptography is mostly fixed by specification. A vendor implements what 3GPP, the O-RAN ALLIANCE or GSMA profile, and an operator configures within it. For each protocol below, a record states the values in use; the specification sets what values are allowed. Annex A gives one row per reference point.

| Protocol                                      | Where                                    | Specification                                                  | Cryptography it defines                                                                                                                                     |
|-----------------|--------------------|------------------|---------------------------------------------|
| TLS and OAuth 2.0 on service-based interfaces | Between network functions in the 5G core | TS 33.501                                                      | TLS 1.3 mandatory to support, TLS 1.2 allowed and to be phased out, with mutual certificate authentication; OAuth 2.0 access tokens signed as JWS           |
| N32-c                                         | Between SEPPs of roaming partners        | TS 33.501                                                      | TLS between the SEPPs                                                                                                                                       |
| N32-f with PRINS                              | Between SEPPs, through IPX providers     | TS 33.501                                                      | Application-layer protection with JWE and JWS, keys derived from the N32-c session                                                                          |
| Subscriber identity concealment (SUCI)        | Device to home network                   | TS 33.501                                                      | ECIES with X25519 or P-256 under the home network's public key                                                                                              |
| 5G AKA and EAP-AKA'                           | Device, serving network and home network | TS 33.501, TS 35.205 to 35.208, TS 35.231, TS 35.234 to 35.236 | Symmetric algorithms (MILENAGE, MILENAGE-256 or TUAK) on the long-term subscriber key                                                                       |
| Air interface                                 | Device to base station                   | TS 33.501, TS 35.240 to 35.248                                 | 128-bit SNOW 3G, AES and ZUC algorithms; 256-bit algorithms specified for Release 20 (256-NEA4, NIA4 and NCA4 on SNOW 5G, NEA5 on AES-256, NEA6 on ZUC-256) |
| NDS/IP                                        | Between network elements on transport    | TS 33.210, TS 33.310                                           | IPsec with IKEv2 and certificates from the operator's PKI                                                                                                   |
| MACsec                                        | Transport links                          | IEEE 802.1AE                                                   | AES-GCM with keys from MKA                                                                                                                                  |
| O-RAN management and fronthaul                | O-RU, O-DU, O-CU and the RIC             | O-RAN ALLIANCE security specifications                         | SSH or TLS on the management plane; TLS or IPsec elsewhere                                                                                                  |
| SIM over-the-air                              | Operator to SIM                          | ETSI TS 102 225 and 102 226                                    | Symmetric keys on the card                                                                                                                                  |
| Remote SIM provisioning                       | Provisioning server to eSIM              | GSMA SGP.22 and SGP.32                                         | ECDSA and ECDH with P-256 or brainpool curves, with SM curves as an option                                                                                  |
| Signed software packages                      | Vendor to operator                       | Vendor practice; ETSI NFV for packages                         | Code signing by the vendor                                                                                                                                  |

For most of these, the post-quantum question is not whether the library can do it. OpenSSL 3.5 and OpenSSH 9.9 already offer hybrid key exchange. The question is whether the specification names a post-quantum option, and whether the peer, often another operator, can use it. A record shows the first by the library and capability attributes. The second needs the specification, which is why this document proposes naming it on the interface (8.1).

Reference points such as N32-c, N32-f and the SBI go in the `referencePoint` vocabulary of the network function profile (8.1), not in the protocol list. This document would add these protocols to the working group's list of protocol names, in its existing style: PRINS, 5G-AKA, EAP-AKA', SCP80, SCP81 and the remote SIM provisioning protocols.

### 6. Telecom use cases

Each use case names its reader, the decision the reader makes, and the profile that serves it. Sources: sections 3.2 to 3.4 of the telecom paper and the working group's use-case register.

| Use case                                      | Who decides, and what                                                                                               | Profile                                                                                                                                                                               |
|---------------------|-------------------------------------------|------------------------------------|
| Procurement of network functions              | Operator procurement: whether a tender's disclosure is complete enough to compare and to hold the vendor to         | Procurement (Release 1); a telecom procurement profile is proposed (8.3)                                                                                                              |
| Supply-chain transparency                     | A vendor: how to disclose once to every operator                                                                    | The interface disclosure baseline. A restricted variant of the baseline is proposed, on the pattern of Service Disclosure (Publication 2, 11.3)                                       |
| Vulnerability response                        | A SOC or CSIRT: which network functions and services a published advisory reaches                                   | The baseline, through I9 with R2 and R3, read with the service assurance record. A restricted vulnerability-response profile is described in Publication 3 (16.3) and not yet written |
| PQC migration of the core and interconnect    | A migration lead: which service-based interfaces, N32 links and transport paths to migrate, in what order           | PQC Migration and PQC Migration Extended (Release 1)                                                                                                                                  |
| SIM and eSIM estates                          | The owner of a subscriber credential estate: which credentials can be renewed over the air and which need new cards | Proposed; follows the IoT Device Estate profile (decision 4)                                                                                                                          |
| O-RAN components                              | RAN engineering: whether to onboard an O-RU, O-DU, O-CU or RIC application                                          | The baseline; the network function profile is drafted (8.1)                                                                                                                           |
| Deployed estate and change impact             | An operator: which weakness affects each deployed function, and what changes between vendor releases                | Deployment Disclosure (Release 1)                                                                                                                                                     |
| Service assurance for critical communications | An assurance team: which customer services a weakness or a change reaches                                           | Service assurance, drafted (8.2)                                                                                                                                                      |
| Regulatory reporting                          | A regulator: whether an operator's position meets NIS2 and national telecom security law                            | Regulatory and compliance reporting (Assurance group)                                                                                                                                 |

### 7. Records across the life of a network function

| Stage           | Who writes                    | Record                                                                               | Who reads, and for what                                                      |
|-----------------------|-------------|------------------------|----------------------------------------|
| Vendor release  | The vendor                    | Product record, `implemented`                              | Operator procurement, against Procurement or the telecom procurement profile |
| Onboarding      | The operator                  | The vendor's record, evaluated                                                       | The operator's onboarding pipeline, before the function is admitted          |
| Deployment      | The operator                  | Deployment record, `configured`, citing the product record | Security operations, against Deployment Disclosure                           |
| Operation       | The operator                  | Deployment record, `observed`                              | The SOC, when an advisory is published                                       |
| Service design  | The operator or integrator    | System record, citing every product record                                           | Service assurance, against the service assurance profile                     |
| Upgrade         | The vendor, then the operator | A new product record; a new deployment record                                        | Change impact: the two product records compared, interface by interface      |
| Decommissioning | The operator                  | None new                                                                             | Retained records and claims, as Publication 3 sets out                       |

A system record cites each product record by digest. When the vendor issues a new release, the digest changes, and the service assurance record has to be written again. That is the point at which a service's dependence on a changed interface becomes visible.

### 8. Telecom profiles

Vulnerability response and PQC migration need nothing telecom-specific beyond the reference point, so the Release 1 profiles serve them. Four telecom profiles are drafted or proposed. Each extends a Release 1 profile. The drafts are in the repository under drafts/telecom-network-function/ and drafts/telecom-service-assurance/.

#### 8.1 Network function product profile (drafted)

A product profile for a network function release, drafted as `telecom-network-function` v0.1-draft. It extends the interface disclosure baseline and adds two rules. Every interface states the reference point it implements (`referencePoint`, I1), from a vocabulary that starts with `n32-c`, `n32-f`, `sbi`, `n2`, `n3`, `n4`, `n9`, `nds-ip`, the O-RAN interfaces, `ota` and `rsp`, or `not-a-reference-point` for a key store. Where it implements one, it names the specification and clause that profile its security (`referenceSpecification`, I2), such as TS 33.501 13.1.

A generic profile is not enough because a reference point and its governing specification are telecom concepts, and an operator compares vendors by reference point. The draft extends the baseline, not the change core, because comparison is a disclosure need. A planning depth on the change core can follow, using the same two attributes.

#### 8.2 Service assurance (drafted)

The service assurance profile is drafted as a rules file. It extends System Disclosure from Release 1. A service assurance record therefore cites the product record of each network function by link and digest, states the usage of every interface of every cited product, and names the key provider of every interface in use. The evaluator checks that every interface of each cited record is listed, and reports each cited record's verdict beside the system record's.

The profile, telecom-service-assurance v0.1-draft, adds four telecom rules. Service levels, availability targets, customers and criticality stay in the operator's service model, which the record joins by service name.

| Rule | Requirement                                                                                                                                                                                                                                                   | Level              | Check                                     |
|--------|-----------------------------------------------------|---------------------|-------------------|
| P1   | `services`: the services the system delivers, as the operator's service model names them                                                                                                                                            | MUST               | present                                   |
| I1   | `carriesService` on each interface in use: the services that depend on it, from the record's `services`, or `none`                                                              | MUST, withholdable | `inSubjectList` |
| I2   | `boundary` on each interface in use: `intra-operator` or `inter-operator`                                                                                                       | MUST               | vocabulary                                |
| I3   | `boundaryProxy` where `boundary` is `inter-operator`: the component that terminates or relays the connection, such as the SEPP, a security gateway or the interconnect provider | MUST, withholdable | `refersToLocal` |

The operator boundary is the telecom counterpart of an IEC 62443 conduit. Release 1 keeps such boundaries as sector rules (Publication 3, Step 2), so the rule lives here. The key provider rule matters in telecom because N32 and service-based interface certificates come from the operator's PKI, not from the network function.

#### 8.3 Telecom procurement profile (proposed)

A procurement profile for network function tenders, extending Procurement. It would require the reference point on every interface, and the roadmap of each capability by reference point, so that tenders compare like with like.

#### 8.4 Network function deployment (in Release 1)

A network function the operator runs needs no telecom deployment profile. The rule first drafted here moved into Release 1 on 19 November 2026. The baseline defines `terminatedBy` (I14), and Deployment Disclosure v0.3 requires it on every interface other than storage: `workload` where the network function does it itself; the bom-ref of the platform interface that does it for the workload, such as a service mesh sidecar or an ingress; or `platform` on that platform interface. The evaluator checks that a bom-ref names a component of the same record.

The rule settles the cloud-native case in chapter 4. Behind a mesh, the record lists two interfaces where there was one: the workload's, often plain HTTP inside the pod, and the mesh's, with the TLS that protects the traffic. Without the rule, the record would show either plain HTTP and nothing about the protection, or the mesh's TLS as if the network function did it.

The rule is not specific to telecom: the Keycloak records in Release 1 use it for the ingress in front of Keycloak's HTTP listener.

### 9. Policies in telecom

The three Release 1 policies apply to telecom records without change. Telecom changes what their results mean.

The algorithm transition policy reads the algorithms on each interface and says whether each is acceptable on a given date. In telecom, many of those algorithms are fixed by a specification. The policy already reports a value decided by the peer and a value not fixed by the product. A telecom reading adds a third case: a value fixed by the standard, which neither the vendor nor the operator can change alone.

The edge-posture policy reads both ends of a connection. For interconnect, one end is in each operator's record, so each operator runs the policy with its partner's record. N32-c is the first case: both SEPPs must offer the same hybrid group before either can use it.

The readiness-gap policy reads a product record and a deployment record together. For a service, it reads the system record and every product record it cites. It reports, for each service, the interfaces that could use post-quantum cryptography, those the configuration allows, and those in use.

### 10. Worked examples

-   Drafted: a roaming interconnect, with an illustrative SEPP (10.1), in [`drafts/telecom-service-assurance/`](../../drafts/telecom-service-assurance/).

-   Drafted: the Open5GS SEPP at v2.8.0, written from its public source (10.2), and an operator's deployment of it behind a service mesh (10.3), in [`drafts/telecom-network-function/`](../../drafts/telecom-network-function/).

None of these has yet been reviewed.

#### 10.1 A roaming interconnect

The SEPP is the network function at N32, the interface between roaming partners. The example SEPP 5.1.0 is illustrative, not a real product. Its product record has five interfaces: N32-c over TLS 1.3, N32-f with PRINS and JWE keys derived from the N32-c session, the service-based interface to the operator's own network functions over TLS 1.3 with OAuth 2.0, management over NETCONF and SSH, and key storage. It is built on OpenSSL 3.5.4, OpenSSH 9.9p1 and an illustrative JOSE library.

The system record describes the operator's roaming interconnect. It delivers three services: inbound roaming, outbound roaming, and roaming for mission-critical users. All five SEPP interfaces are in use. N32-c, N32-f and the service-based interface carry all three services. Two interfaces cross the operator boundary: N32-c, terminated by the SEPP, and N32-f, relayed by the interconnect provider. The N32 and service-based interface certificates come from the operator's PKI, and the key-encryption key from the operator's HSM.

| Document                                       | Baseline v0.10 | System Disclosure | Service assurance |
|----------------------------------|-------------------|------------------------|-----------------------|
| SEPP product record                            | Conforms       | Not applicable    | Not applicable    |
| Roaming interconnect                           | Conforms       | Conforms          | Conforms          |
| N32-f without the services it carries          | Conforms       | Conforms          | Fails I1          |
| N32-c without the component that terminates it | Conforms       | Conforms          | Fails I3          |

The SEPP record fails the change core, as the public-source OT records do, because it states no capability per purpose and no update mechanism.

The record answers the question the GSMA paper asks of a SEPP. Every service the interconnect delivers depends on N32-c, which uses X25519 alone. The libraries already support hybrid key exchange: X25519MLKEM768 in OpenSSL 3.5, and mlkem768x25519-sha256 in OpenSSH 9.9. The SEPP leaves it out because the 3GPP profile for N32-c does not yet name it, and enabling it needs the roaming partner too. TR 33.703 recommends hybrid key exchange for TLS 1.3, and Release 20 work will profile it in TS 33.210 and TS 33.310. The change is a configuration agreed with each partner. No software release is needed.

#### 10.2 The Open5GS SEPP

Open5GS is an open-source 5G core. Its SEPP record is written by the working group from the public source at the v2.8.0 tag (June 2026), not by the Open5GS maintainers. The library versions are those of the Ubuntu 24.04 packages: OpenSSL 3.0.13, nghttp2 1.59.0 and libcurl 8.5.0. The negotiated values are still to be confirmed on a build.

The record has four interfaces: N32-c, N32-f, the service-based interface, and the PEM files that hold the keys and certificates. The source shows four things.

-   N32-c and N32-f both use TLS. PRINS is not implemented: the SEPP offers TLS as its only N32-f security capability.

-   When built with OpenSSL 3, the TLS server context sets the group list to P-256 only. The server negotiates ECDHE on P-256 whatever the client offers, and there is no setting to change it. The code is in the shared SBI library, so it applies to every Open5GS network function. The client side uses libcurl with OpenSSL's default groups.

-   The code allows TLS 1.0 to 1.3; OpenSSL 3 refuses 1.0 and 1.1 at its default security level. Client certificate verification is off unless the operator sets it, and the shipped configuration does not set it. N32-c therefore runs without client authentication by default, where TS 33.501 expects mutual TLS between SEPPs.

-   The shipped configuration runs the service-based interface over HTTP without TLS.

| Document                          | Baseline v0.10 | Network function |
|-------------------------------------------------|------------------------|---------------------------|
| Open5GS SEPP product record       | Conforms       | Conforms         |
| N32-c without its reference point | Conforms       | Fails I1         |

Post-quantum key exchange on N32 is blocked in the product itself, because the group list is fixed in code. Linking OpenSSL 3.5 would not change it. This is the case the change core's blocker `product` describes, and it is visible only because the record reads the source.

#### 10.3 The SEPP behind a service mesh

An illustrative operator runs the Open5GS SEPP in Kubernetes with a service mesh. N32 is terminated by the SEPP. The service-based interface runs as plain HTTP inside the pod, and the mesh sidecar terminates mutual TLS with certificates from the mesh's own CA, RSA-2048 by default. Those certificates do not follow the operator's SBA certificate profile in TS 33.310, which the record makes visible.

| Document                                         | Deployment Disclosure v0.3                                  |
|---------------------------------------------------------|-------------------------------------------|
| Deployment record                                | Conforms                                                    |
| The SBI without the component that terminates it | Fails `interface-disclosure#I14` |

### 11. Standards and regulation

A CBOM does not replace an assurance scheme or a regulator's assessment. It supplies the cryptographic facts they rest on, per interface, in a form a tool can read.

| Scheme or law                                               | What it asks for                                                                                                                                                                                           | What a CBOM can supply                                                                   | What it cannot                        |
|--------------------|-----------------------------------|----------------------------|-----------------|
| 3GPP TS 33.501, 33.210, 33.310                              | The security of each reference point                                                                                                                                                                       | The values a product implements and a deployment uses, to compare with the specification | Whether the specification is adequate |
| 3GPP SCAS and GSMA NESAS                                    | Security assurance of network equipment and of the vendor's development                                                                                                                                    | The product record as an input to the evaluation                                         | The evaluation result                 |
| GSMA PQ.03 v2.0 and PQ.05                                   | Post-quantum guidance for telecom use cases (PQ.03), and for 4G and 5G roaming, including N32 and the SEPP (PQ.05)                                                                                         | The inventory and capability facts the guidance asks operators to gather                 | The migration decision                |
| O-RAN ALLIANCE security work                                | Security of open RAN interfaces                                                                                                                                                                            | Product records for O-RU, O-DU, O-CU and RIC applications                                | Assurance of the RAN as integrated    |
| NIS2, and the EU Coordinated Implementation Roadmap for PQC | Policies and procedures on cryptography (NIS2 Art. 21(2)(h)). The inventory of cryptographic assets is asked for by the EU Coordinated Implementation Roadmap for PQC, with first steps by the end of 2026 | The inventory, by function and by service                                                | The risk assessment                   |
| National telecom security laws                              | Operator duties on network security and supply chain                                                                                                                                                       | Evidence of what each vendor's function uses                                             | Compliance itself                     |
| EU 5G toolbox                                               | Supplier risk measures                                                                                                                                                                                     | Comparable records across vendors                                                        | Supplier risk profiles                |
| Cyber Resilience Act                                        | Security of products with digital elements, with an SBOM                                                                                                                                                   | The CBOM beside the SBOM the act already asks for                                        | Conformity assessment                 |

### 12. Positions and open work

#### 12.1 Release 1 positions this document starts from

| Position                                                                                                                                     | Ratified in           |
|------------------------------------------------------------------|----------------------------------|
| Each party states what it knows.                                                                                                             | Publication 2         |
| A sector profile extends a Release 1 profile, directly or through another, and adds only rules specific to its sector.                       | Publication 3         |
| A system record cites its product records by link and digest, and their verdicts are reported beside its own.                                | Publication 2         |
| Boundaries inside a subject, such as zones and operator boundaries, stay sector rules.                                                       | Publication 3         |
| A public and a restricted variant of one record; the restricted profile derives from the public one by tightening.                           | Publication 2         |
| A deployment record names what terminates each interface's cryptography (interface-disclosure\#I14, required by Deployment Disclosure v0.3). | Publication 2, row 41 |

#### 12.2 Positions proposed in this document

| Position                                                                                                                                | Chapter    |
|-------------------------------------------------------------------------------|---------------------|
| A reference point is an attribute of an interface, naming the reference point and its governing specification beside the protocol name. | 4, 8.1     |
| Interconnect is read from both ends. Each operator describes its own end.                                                               | 4          |
| A network function the operator runs has a vendor product record and an operator deployment record. The platform beneath has its own.   | 4          |
| The service assurance profile records the operator boundary and the component that guards it.                                           | 8.2        |
| This document cites the GSMA paper and does not replace it.                                                                             | Decision 1 |
| Behind a service mesh, the deployment record names the platform interface that terminates the network function's cryptography.          | 4, 8.4     |

#### 12.3 Open work

-   Review the service assurance profile and its record (8.2, 10).

-   Review the network function profile (8.1) and the Open5GS records (10.2, 10.3).

-   Build Open5GS v2.8.0 and confirm the library versions and negotiated values in its record, and ask the Open5GS maintainers to review it.

-   Use terminatedBy in the service assurance record where a mesh terminates a network function's SBI (8.2, 8.4).

-   Complete the reference point catalogue (Annex A). Check the post-quantum status against TR 33.703 itself, and confirm the SIM OTA key lengths and the O-RAN E2 requirement.

-   Approach GSMA PQTN to co-own this document (decision 6).

Annexes
-------

### A. Reference point catalogue

A first set of rows. Post-quantum status as of November 2026.

| Reference point            | Specification        | Cryptography                                 | Post-quantum status                                                                                                                           | In CycloneDX                                |
|-----------------|-----------------|-----------------|---------------------------------|-----------------|
| N32-c                      | TS 33.501            | TLS between SEPPs                            | Libraries offer hybrid key exchange. TR 33.703 recommends hybrid key exchange for TLS 1.3 (RFC 9954); Release 20 will profile it in TS 33.210 | One interface of the SEPP, protocol TLS     |
| N32-f                      | TS 33.501            | PRINS: JWE and JWS, or TLS                   | With PRINS, depends on N32-c for its keys. With TLS, as N32-c                                                                                 | One interface of the SEPP                   |
| Service-based interfaces   | TS 33.501            | TLS and OAuth 2.0                            | As N32-c                                                                                                                                      | One interface per exposed service           |
| SUCI                       | TS 33.501            | ECIES with X25519 or P-256                   | No post-quantum profile yet. TR 33.703 recommends one standalone and one hybrid ML-KEM profile; none is selected                              | An interface of the UDM and of the device   |
| N2, N3 and other transport | TS 33.210, TS 33.310 | IPsec with IKEv2; DTLS is also allowed on N2 | No post-quantum option yet. TR 33.703 recommends RFC 9370 and ML-KEM for IKEv2                                                                | One interface per protected link            |
| O-RAN management plane     | O-RAN ALLIANCE       | SSH or TLS                                   | Libraries offer hybrid key exchange                                                                                                           | One interface of the O-RU, O-DU or O-CU     |
| E2                         | O-RAN ALLIANCE       | TLS or IPsec                                 | None in O-RAN specifications yet; WG11 is studying ML-KEM and ML-DSA options. The E2 requirement is to confirm                                | One interface of the RIC and of the E2 node |
| SIM over-the-air           | ETSI TS 102 225      | Symmetric keys                               | Symmetric; key length to confirm                                                                                                              | An interface of the SIM product record      |
| Remote SIM provisioning    | GSMA SGP.22, SGP.32  | ECDSA and ECDH                               | None in SGP.22 or SGP.32 yet; GSMA is extending the specifications, with an impact analysis due by the end of 2026                            | An interface of the eUICC and of the server |

### B. Telecom terms and methodology terms

| Telecom term                         | Methodology term                                    | Note                                                                                                              |
|-----------------------|-----------------------------|-----------------------------------------------|
| Network function                     | Subject of a product record                         | One record per release                                                                                            |
| Reference point                      | Interface                                           | The proposed attribute names it (8.1)                                                                             |
| PLMN                                 | One side of an operator boundary                    | `boundary` is `inter-operator` where the connection leaves it |
| SEPP, security gateway, IPX provider | Target of `boundaryProxy` | A component of the system record                                                                                  |
| Service                              | An entry in `services`    | Named as the operator's service model names it                                                                    |
| Network slice                        | None yet                                            | To decide: a service, or a coverage statement                                                                     |
| Telco cloud, NFVI                    | Subject of a platform record                        | Cited by the deployment record                                                                                    |

### C. Mapping from the telecom paper

| Paper section | Use case                            | Here                              |
|------------------|-------------------------------------------|---------------------------------------|
| 3.1.1         | PQC readiness                       | Chapter 6; PQC Migration          |
| 3.1.4         | Reference points as dependencies    | Chapters 4 and 8.1                |
| 3.2.1         | Supply-chain risk management        | Chapter 6; baseline               |
| 3.2.2         | Vulnerability management            | Chapter 6; Vulnerability Response |
| 3.2.3         | Regulatory and compliance reporting | Chapters 6 and 11                 |
| 3.2.4         | Service assurance                   | 8.2 and 10.1                      |
| 3.3           | Cloud-native function lifecycle     | Chapters 4 and 7                  |
| 3.3           | O-RAN governance                    | Chapter 6; 8.1                    |
| 3.3           | Infrastructure exposure             | Chapter 4: the platform record    |
| 3.3           | Third-party change impact           | Chapter 7                         |
| 3.4           | Procurement                         | Chapter 6; 8.3                    |

### D. Example documents

In [`drafts/telecom-service-assurance/`](../../drafts/telecom-service-assurance/) in the repository: the service assurance profile, the SEPP 5.1.0 product record and its SBOM, the roaming interconnect system record, and its two non-conforming variants. In [`drafts/telecom-network-function/`](../../drafts/telecom-network-function/): the network function profile, the Open5GS SEPP v2.8.0 product record and its SBOM, the deployment record, and one non-conforming variant of each record.

Decisions
---------

1.  **Relation to the telecom paper.** Whether this document replaces the paper's use-case material, or the paper stays as a separate position paper that this document cites. Proposed: the paper stays, and Annex C maps its use cases to this document.

2.  **Reference points as an interface type.** Whether a reference point is a new value in the interface vocabulary, or an attribute that names the standard behind an existing interface type. Proposed: an attribute (8.1).

3.  **Product or deployment for cloud-native functions.** Where the vendor's record ends and the operator's begins when the operator runs the vendor's software on its own platform. Proposed: three records, for the vendor, the operator and the platform (4).

4.  **SIM and eSIM estates.** Whether they belong here or in a future IoT and devices domain document, since both deal with keys fixed at issue. Release 1 now has the IoT Device Estate profile for device models. Proposed: SIM estates stay here and follow IoT Device Estate, because a SIM or eSIM is a device model in a fleet (question register, R2-24).

5.  **A real product.** Whether to build the first example on an open-source 5G core function. Decided: the Open5GS SEPP (10.2).

6.  **Ownership.** Whether to approach a telecom industry body to co-own the document.
