CBOM Profiles — Application domain: Financial services
======================================================

Working Draft 0.1 · Nov 26, 2026 · \@Mike

Purpose
-------

This draft covers the cryptography of financial services: card payments, account-to-account payments, interbank messaging, market infrastructures and the banking services that customers use. It is written for readers outside the working group: payment security and key management teams, card scheme and payment system operators, HSM and terminal vendors, PCI assessors and internal auditors, and supervisors. It follows the shape of the OT, telecom and SaaS documents.

Financial services is a domain of its own for four reasons:

-   Most keys live in hardware security modules (HSMs), under key hierarchies. A record has to follow each working key up to the key that protects it.

-   Much of the cryptography is symmetric. Its quantum risk is low, but Triple DES is being retired at the same time as the post-quantum migration runs, so two migrations share one estate.

-   Payment schemes set the algorithms, the trust anchors and the dates. A bank cannot change its cryptography on its own, because its counterparties must change too.

-   Regulators and payment standards already ask for an inventory of cryptography. PCI DSS asks for one, and so do the DORA technical standards.

This is a working draft. It sits outside Release 1 and starts from the positions that Release 1 ratified. Positions proposed here are listed in chapter 13.

1. Scope and readers
--------------------

The draft covers:

-   **card payments**: issuing, acquiring, ATMs and points of sale;

-   **account-to-account and instant payments**, and **interbank messaging**;

-   **market infrastructures**, such as central securities depositories and central counterparties;

-   **online and open banking**;

-   behind all of these, **HSM estates**, **key management** and **long-term archives**.

Crypto-assets and distributed-ledger systems are out of scope. Their cryptography sits mainly in wallets, custody services and the signatures of a ledger, which raise questions that the rest of the domain does not. They will be considered for a later document when a member organisation that runs such a system offers to contribute a worked example.

The readers are:

| Reader | What they decide |
|---|---|
| Payment security and key management teams | Which keys and HSMs move first, and when |
| Card scheme and payment system operators | When every participant can move to a new trust anchor |
| HSM, terminal and card vendors | What to disclose about their products, and how |
| PCI assessors and internal audit | Whether the inventory and the annual review are complete |
| Supervisors | Whether a bank's migration is on track |

2. CBOM profiles in brief
-------------------------

A cryptographic bill of materials (CBOM) lists the cryptography that a product, service or system uses. It is usually written in CycloneDX. On its own, a CBOM does not say whether it contains what a reader needs, and two CBOMs of similar products can describe different things in different places.

A **profile** fixes that. It states, for one decision, which facts a CBOM must contain and how they are written. A tool can then check a CBOM against the profile and give a **verdict**: the CBOM conforms or does not conform, and the verdict names any rule that failed. A profile asks only for facts. Judgements, such as whether an algorithm is still acceptable, are made by a separate **policy**, which reads the facts and gives a dated result.

A CBOM describes its subject one **interface** at a time. An interface is a place where the subject uses cryptography with another party. In financial services, examples are a host command interface on an HSM, a TR-34 key exchange with a terminal, a TLS link to a payment network, and the store where an HSM keeps its key blocks. For each interface, the CBOM records the protocol, the algorithms for each purpose and the library that implements them.

Four kinds of record matter here:

-   a **product record**, written by a vendor, for an HSM model, a payment switch or a terminal model;

-   a **deployment record**, written by the bank or processor, for what it has configured and observed;

-   a **service record**, written by a provider, for a managed HSM or payment processing service;

-   a **system record**, written by the operator of a system, for a payment scheme's own components.

Records cite each other by link and digest. A reader joins them when reading and never merges them. A producer that does not want to disclose a fact can mark it as withheld, where the profile allows this, and the record can still conform.

PKI Consortium Publications 1 to 3 define all of this in full. This draft uses only what a reader needs to apply the method to financial services.

3. What is different about cryptography in financial services
------------------------------------------------------------

**Keys live in HSMs, in hierarchies.** A payment HSM holds a master key. The master key protects key-encryption keys, also called zone master keys, which are exchanged with each counterparty. These in turn protect working keys, such as PIN encryption keys and card verification keys. A record follows this chain. On each interface, `keyStoreRef` names the store that delivers its keys, and the store's `providerLocation` is almost always `hsm`. Where the HSM has its own record, `keyStoreRef` points into it by BOM-Link (question register, R2-27). Where no record exists, the value is `out-of-band` (R2-22).

**Most of the load is symmetric.** PIN blocks, message authentication codes, card session keys and key derivation for each transaction all use symmetric cryptography. A quantum computer does not break AES, so these mechanisms are not part of the post-quantum migration. Many of them still use Triple DES, which is being retired. Chapter 6 treats the two migrations together.

**Public-key cryptography sits in a few critical places.** Card authentication uses public keys certified by the scheme's certificate authority. Remote key loading and the exchange of key-encryption keys with counterparties use RSA (TR-34) or elliptic-curve Diffie-Hellman. TLS protects links to networks, processors and open banking partners. These are the interfaces that a quantum computer would break.

**Key exchange is where harvest-now-decrypt-later matters.** Payment data is short-lived, and EMVCo has stated that chip authentication does not need long-term confidentiality. A key-encryption key is different. It is exchanged once and then protects every working key sent under it for years. An adversary that records a TR-34 or ECDH exchange today, and breaks it later, recovers every key that was later wrapped under the key it carried. The interfaces that carry key-encryption keys therefore come first in a payment estate's migration, even though the data they protect does not need to stay secret for long.

**Schemes set the rules.** The algorithms, the trust anchors and the dates are set by the card schemes, by EMVCo, by the PCI Security Standards Council and by payment system operators. An issuer or acquirer cannot move until the scheme and its counterparties can.

**Estates are long-lived and certified.** Cards stay in the field for three to five years, and terminals much longer. A change to an HSM or a terminal can trigger re-validation under FIPS 140-3, PCI HSM or PCI PTS POI. The change core and the PQC migration profile record this with `certificationImpact` and `certificationScheme` (R2-23).

**Inventories are already required.** PCI DSS 4.0.1 requires an inventory of the cipher suites and protocols in use (requirement 12.3.3), and an inventory of the trusted keys and certificates that protect card numbers in transit (requirement 4.2.1.1). The DORA technical standards require a register of certificates and certificate-storing devices. Chapter 12 shows how far CBOMs answer these requirements.

4. The financial system in the methodology's terms
---------------------------------------------------

| Financial term | Record | Written by |
|---|---|---|
| An HSM model and firmware release | Product record | The vendor |
| An HSM partition or estate, as configured | Deployment record | The bank or processor |
| A payment switch or processing platform | Product record, then deployment record | The vendor, then the operator |
| A card product or a terminal model | Product record of a device model, under IoT Device Estate | The card or terminal vendor |
| A managed HSM or payment cryptography service | Service record | The provider |
| A card scheme or payment system | System record of what the scheme operator runs | The scheme operator |

**A scheme is a system, and its participants describe their own ends.** The scheme operator writes records only for what it runs: its certificate authority, its directory servers and its key distribution. Each issuer, acquirer and processor describes its own end of every connection to the scheme, in the same way that telecom operators each describe their own end of an interconnect. The model stays within two-party relationships (Publication 2, position 34). Whether every participant can move to a new trust anchor is a question for a policy that reads all the participants' records together (R2-26).

**A scheme's certificate authority is a scheme-administered trust anchor.** PQC Migration Extended already has the values for this: `trustDomain` is `scheme-administered`, and `verifierPopulation` is `scheme-members`, because every terminal in the scheme must be able to verify what the authority signs.

**The boundary between scheme and participant uses the telecom names.** Each interface that crosses it states `boundary`, and `boundaryProxy` names the component that guards the crossing, such as a network access gateway (R2-25).

5. Protocols and their cryptography
-----------------------------------

| Mechanism | Where | Governing specification | Cryptography | Quantum exposure |
|---|---|---|---|---|
| EMV offline card authentication | Card to terminal | EMV specifications | RSA under scheme certificate authorities; elliptic-curve cryptography from EMV Specification Bulletin 243 | Public-key signatures: exposed |
| EMV application cryptograms | Card to issuer | EMV specifications | Symmetric session keys, Triple DES or AES | Symmetric: not exposed to a quantum computer; Triple DES is being retired |
| PIN blocks and PIN translation | Terminal, acquirer, issuer | ISO 9564 | ISO formats 0 to 3 with Triple DES; format 4 with AES | Symmetric |
| Key derivation for each transaction (DUKPT) | Terminal to acquirer | ANSI X9.24-3 | Triple DES or AES | Symmetric |
| Key blocks | Between HSMs, and between parties | ANSI X9.143, which superseded TR-31; ISO 20038 | Key wrapped with its usage bound to it, under Triple DES or AES | Symmetric |
| Exchange of key-encryption keys | Host to terminal, host to counterparty | TR-34, implementing ANSI X9.24-2; ECDH with a key derivation function | RSA; elliptic-curve Diffie-Hellman | Public-key: exposed, and the first priority (chapter 3) |
| Card and payment messaging | Between institutions | ISO 8583, ISO 20022 | Message authentication codes; TLS and PKI on interbank networks | MACs symmetric; TLS and PKI exposed |
| 3-D Secure 2 | Cardholder device, merchant, issuer | EMV 3-D Secure | JWE and JWS, with ECDH between the SDK and the issuer's access control server | Exposed |
| Open banking APIs | Bank to third party | National and regional open banking standards | Mutual TLS and signed tokens | Exposed |
| HSM management and key ceremonies | Operator to HSM | Vendor specifications; PKCS #11; KMIP | Vendor host command sets and management consoles; smart cards for key custodians | Depends on the vendor |

The protocol names this draft adds to the working group's list are `emv-offline-auth`, `iso9564-pin`, `dukpt`, `x9.143-keyblock`, `tr-34`, `iso8583`, `iso20022`, `emv-3ds` and `pkcs11`. They are proposed, and they will be checked against the CycloneDX cryptography registry before they are adopted.

6. Two migrations in one estate: Triple DES and post-quantum
-------------------------------------------------------------

Financial services is migrating its cryptography twice. The retirement of Triple DES is well under way. The post-quantum migration is starting. Both touch the same HSMs, the same key hierarchies and the same counterparties, so a bank that plans them separately does the expensive work twice.

### 6.1 Where each migration stands

**Triple DES.** NIST SP 800-131A Revision 2 disallowed encryption with Triple DES after 2023. In payments, the PCI PIN Security Requirements disallowed fixed-key Triple DES PIN encryption from 1 January 2023, in terminals and between hosts. The same standard requires symmetric keys to be held and exchanged in key blocks, which bind each key to its permitted usage. Key blocks were required within service provider environments from June 2019, for external connections to associations and networks from 1 January 2023, and for merchant hosts, points of sale and ATMs from 1 January 2025. The dates for supporting ISO format 4 PIN blocks, the only ISO PIN block format that uses AES, were suspended in 2021 while the Council considers how to support the move from Triple DES to AES across the ecosystem.

**Post-quantum.** The final NIST IR 8547 deprecates quantum-vulnerable signature and key-establishment algorithms after 2030 and disallows them after 2035. EMVCo does not expect quantum computers to threaten EMV chip payments before 2040, and its August 2026 position paper treats symmetric cryptography as outside the quantum threat. In January 2026 the G7 Cyber Expert Group published a non-binding roadmap for a coordinated transition across the financial sector.

### 6.2 One record for both

The two migrations use the same attributes. A product record states the algorithms in use (`keyExchange`, `encryption`, `authentication`, `keyWrapping`) and the algorithms supported (`keyExchangeSupported` and the other `Supported` forms). A deployment record states what is configured and observed. Nothing in the record says which migration a value belongs to.

The difference lies in the policy. The algorithm-transition policy takes a schedule as data. A financial services policy holds two schedules:

-   **the symmetric schedule**: Triple DES and short RSA keys, with the dates set by NIST, PCI and the schemes;

-   **the post-quantum schedule**: the NIST IR 8547 dates for quantum-vulnerable public-key algorithms.

Both schedules use the shared classification set, which already states the security strength and quantum vulnerability of each algorithm name. A bank evaluates its records once and gets both answers. An interface that fails only the symmetric schedule, such as a PIN path that still uses Triple DES, needs a change of symmetric algorithm. An interface that fails only the post-quantum schedule, such as a TR-34 exchange, needs a new public-key mechanism.

### 6.3 Planning the two together

Four facts in a record help a bank combine the two migrations:

-   **`enablementMethod`** shows whether moving to AES or to a post-quantum mechanism needs a configuration change, a firmware update or new hardware. If both need the same firmware update, one change window serves both.

-   **`certificationImpact`** shows whether the change triggers re-validation of the HSM or terminal. Two migrations that each trigger a re-validation cost twice as much as one that combines them.

-   **`keyStoreRef`** follows each working key to its key-encryption key. When a key-encryption key moves to a new exchange mechanism, every working key under it can be re-issued under AES at the same time.

-   **`coexistence`** shows whether old and new algorithms can run side by side, which decides whether counterparties can move one at a time.

### 6.4 What stays outside the record

The record does not say which migration comes first. That is the bank's decision, and the dates of the schemes and its counterparties constrain it. The record does not hold the keys either, and it does not record how many working keys sit under each key-encryption key. A bank that wants to size the work counts its keys in its key management system and joins that count to the record by interface.

7. Financial services use cases
-------------------------------

| Use case | Who decides, and what | Profile |
|---|---|---|
| Procurement of HSMs and payment platforms | A bank or processor: whether a tender's disclosure is complete enough to compare | Procurement (Release 1); the HSM product profile in the Change planning group document (9.1) |
| Shared-trust network migration | A scheme operator: when every participant can move to a new trust anchor | The scheme profile (9.3) for the scheme's own components, the participants' own records, and the scheme-readiness policy (10.2) |
| Card estate migration | An issuer: which card products can carry new keys and which need reissue | IoT Device Estate, with the card extension in a future devices document (9.2) |
| Terminal estate migration | An acquirer: which terminals can be updated and which must be replaced | IoT Device Estate, with the terminal extension in a future devices document (9.2) |
| Key hierarchy migration | An HSM owner: which keys move first, and what each depends on | PQC Migration Extended, with the key hierarchy depth proposed for the Change planning group document (9.1) |
| Vulnerability response | A security operations centre: which services an HSM or library advisory reaches | The baseline, through I9 with R2 and R3. A restricted vulnerability-response profile is not yet written |
| Annual review of cryptography | A bank: the cipher suites and protocols in use, reviewed against policy (PCI DSS 12.3.3) | Deployment Disclosure (Release 1), read by a policy |
| Third-party register | A bank: the cryptography of each ICT provider, beside what DORA asks for | Service Disclosure (Release 1) |
| Migration progress | A supervisor: whether a bank's migration is on track | Migration progress over time (Operation group) |
| Archive protection | A records owner: which archives to re-encrypt first | Stored data and archive protection (Change planning group) |

8. Records across the life of a payment product
------------------------------------------------

**An HSM.** The vendor writes a product record for each model and firmware release, with its validation under FIPS 140-3 and PCI HSM. The bank reads it at procurement. When the HSM is installed, the bank writes a deployment record of its partitions, its loaded keys and the interfaces it has enabled. Key ceremonies change the keys, but not the record, unless they change an algorithm or a store. A firmware update produces a new product record from the vendor, and a new deployment record from the bank when the update is applied. At decommissioning, the last deployment record states that the keys have been destroyed.

**A card.** The card vendor writes a product record for each card product, as a device model. The issuer reads it when it chooses a card product and again when it plans a reissue. A card stays in the field for three to five years, so a migration that cannot be done in the field happens at reissue.

**A terminal.** The terminal vendor writes a product record for each terminal model, with its PCI PTS POI approval and the date that approval expires. The acquirer reads it when it buys terminals and when it plans their replacement. Expiry of the approval often decides the replacement date, so a migration that needs new hardware is cheapest when it is aligned with that date.

**A managed payment cryptography service.** The provider writes a service record and states what triggers a new one. The bank reads it when it onboards, and again whenever the provider announces a change. The bank's own deployment record cites the service record and states which of the offered key types and exchange methods it actually uses.

9. Profiles financial services relies on
----------------------------------------

The HSM profile and the card and terminal extensions serve every sector that uses HSMs and payment devices, so they are drafted in the generic documents and not here. This chapter states what financial services needs from each.

### 9.1 HSM product profile and key hierarchy depth (Change planning group document)

The HSM profile extends PQC Migration Extended, which already carries module validation and certification impact (R2-23). Financial services needs it to state, for each firmware release:

-   the algorithms and key block formats the HSM supports;

-   its validation under FIPS 140-3 and PCI HSM, with the certificate references;

-   whether a new algorithm arrives by firmware or needs new hardware (`enablementMethod`);

-   what re-validation a change triggers (`certificationImpact`).

The key hierarchy depth adds, for each working key, its chain to the master key through `keyStoreRef`, with the key block format and key length at each level. Where the HSM has its own record, `keyStoreRef` names the key store by BOM-Link in that record. Where it does not, the value is `out-of-band`.

### 9.2 Card and terminal extensions of IoT Device Estate (future devices document)

Cards and terminals are device models in a fleet, so IoT Device Estate applies to both (R2-24). Financial services needs the extensions to state:

-   the EMV kernel and specification version;

-   the PCI PTS POI approval and its expiry date, for terminals;

-   whether card keys and terminal keys can be replaced in the field.

### 9.3 Scheme profile (this document)

The scheme profile is the one profile that belongs here, because it describes something only payment schemes have. It extends System Disclosure and covers the components that the scheme operator runs:

-   its trust anchors, with `trustDomain` `scheme-administered` and `verifierPopulation` `scheme-members`;

-   the interfaces that depend on each trust anchor;

-   the boundary between the scheme and its participants, with `boundary` and `boundaryProxy`.

Participants' records stay their own. The scheme record does not cite them, and the readiness of the scheme as a whole is computed by a policy (10.2).

10. Policies in financial services
----------------------------------

### 10.1 Algorithm transition with two schedules

This policy is the existing algorithm-transition policy with a second schedule added (chapter 6). The symmetric schedule covers Triple DES and short RSA keys, with the dates set by NIST, PCI and the schemes. The post-quantum schedule covers quantum-vulnerable public-key algorithms, with the NIST IR 8547 dates. Both read the shared classification set. The policy is `mechanical`, because both schedules are dates and strengths taken from their sources, so it can become a `reference` policy once each date has been checked against its source.

### 10.2 Scheme readiness

This policy reads the scheme's record and the records of its participants. For each participant and each interface that depends on a scheme trust anchor, it asks three questions:

1.  Could the participant use the new trust anchor? The product record's supported algorithms answer this.

2.  Does its configuration allow it? The deployment record's configured values answer this.

3.  Does it use the new trust anchor? The deployment record's observed values answer this.

The result lists the participants that block the scheme's move, and the reason for each. The policy belongs to the Operation group, and it is `interpretive`, because the scheme decides what counts as ready.

### 10.3 Record currency for third-party registers

This policy checks whether a bank holds its provider's current service record, by comparing the record it holds with the provider's change notices. The SaaS domain document proposes the same policy (chapter 9), and the two should be written once.

11. Worked examples
-------------------

### 11.1 A managed payment cryptography service

The first worked example is a service record for AWS Payment Cryptography, written from the provider's public documentation. It is chosen because the documentation states the key types, key exchange methods and storage protection in enough detail to write a record without the provider's help. The record has not been reviewed by the provider.

The documentation describes these interfaces:

| Interface | Type | Cryptography, as documented |
|---|---|---|
| Control plane API | Management | Creating, importing and exporting keys |
| Data plane API | Service | Payment operations, such as PIN translation, card verification values and EMV cryptograms |
| Import and export of key-encryption keys | Key transport | TR-34 with RSA 2048, 3072 or 4096; RSA wrap; ECDH on NIST P-256, P-384 or P-521, with the key derivation function of NIST SP 800-56A or ANSI X9.63 |
| Import and export of working keys | Key transport | TR-31 and ANSI X9.143 key blocks under a key-encryption key, with Triple DES or AES |
| Key storage | Storage | Keys held in TR-31 key blocks, protected by AES-256 main keys in the service's HSMs |

The documentation lists Triple DES (two-key and three-key) and AES (128, 192 and 256 bits) as symmetric key algorithms, and RSA and NIST elliptic curves as asymmetric ones. The pages consulted for this draft list no post-quantum key types.

Three findings are expected from the record, before any policy is applied:

-   The quantum-exposed interfaces are the two that carry key-encryption keys: TR-34 and ECDH. Everything sent under those keys inherits their exposure (chapter 3).

-   Working keys and storage are symmetric. Their migration concern is Triple DES, which the service still supports for compatibility with counterparties.

-   The TLS versions and key exchange groups of the two APIs have not yet been checked against the provider's documentation. Until they are, the record marks them as unknown rather than assuming them.

The record will be built by a script under `drafts/fs-payment-cryptography-service/`, in the same way as the other worked examples, and checked against Service Disclosure.

### 11.2 Examples proposed for later

-   An open-source payment switch, such as jPOS, written from its public source as a product record.

-   An illustrative EMV card product and a terminal model, as device-model records, once the devices document defines their extensions.

12. Standards, schemes and regulation
-------------------------------------

The working group's regulatory sufficiency register records, for each instrument, which questions a CBOM answers and which it does not ([coverage matrix](../../regulation/coverage.md)). Two financial instruments have been added to it:

| Instrument | Evidence question | Verdict | Why |
|---|---|---|---|
| PCI DSS 4.0.1, requirement 12.3.3 | Which protocols and cipher suites are in use, where, and for what purpose? | Partial | The baseline requires the protocols and algorithms of every interface, but the purpose of an interface (I12) is optional. A payment-environment profile could make it mandatory |
| PCI DSS 4.0.1, requirement 12.3.3 | Which protocols and cipher suites are losing their viability, and what is the plan? | Judgement | Viability is decided by a versioned policy, evaluated again at each annual review |
| PCI DSS 4.0.1, requirement 4.2.1.1 | Which keys and certificates are trusted to protect card numbers in transit? | Partial | A CBOM names the algorithms and stores, but individual keys and certificates stay outside it by design |
| DORA technical standards, Article 6 | How is data protected at rest, in transit and on internal networks? | Sufficient | The baseline requires the algorithms and type of every interface |
| DORA technical standards, Article 7 | Which certificates and certificate-storing devices support each critical or important function? | Partial | A CBOM names the certificate-storing devices, but not individual certificates or which functions are critical |
| DORA technical standards, Article 7 | Can keys be managed through their whole lifecycle? | Partial | A CBOM states what a product can do. The entity's procedures stay outside it |

The register's general instruments also apply: NIST IR 8547, NIS2 where it applies (DORA takes precedence for financial entities), and the Cyber Resilience Act for products such as HSMs and terminals.

Other sources this draft relies on:

-   **Card and payment security**: PCI PIN Security Requirements, PCI PTS POI, PCI HSM, the EMV specifications, and EMVCo's August 2026 position paper on quantum computing and EMV chip cryptography.

-   **Key management**: ANSI X9.24 parts 1 to 3, ANSI X9.143, TR-34, ISO 9564, ISO 11568, ISO 13491 and ISO 20038.

-   **Messaging**: ISO 8583, ISO 20022 and the SWIFT Customer Security Programme.

-   **Post-quantum guidance for the sector**: the G7 Cyber Expert Group's roadmap of January 2026, FS-ISAC, the Europol Quantum Safe Financial Forum and the BIS Innovation Hub.

13. Positions and open work
---------------------------

### 13.1 Release 1 positions this draft starts from

| Position | Ratified in |
|---|---|
| Facts go in the CBOM, and judgements go in a versioned policy. | Publication 2 |
| Records cite each other by link and digest, and are joined, not merged. | Publication 2 |
| The model is limited to two-party relationships. | Publication 2, position 34 |
| A sector profile extends a Release 1 profile, directly or through another, and adds only rules specific to its sector. | Publication 3, position 27 |
| Each document declares its subject type, so a CBOM can describe a device model or a deployed device. | Publication 3, position 28 |
| A policy takes its algorithm facts from a shared classification set, pinned by digest. | Publication 2, position 44 |

### 13.2 Positions proposed in this draft

| Position | Chapter |
|---|---|
| Crypto-assets and distributed-ledger systems are out of scope, until a member offers a worked example. | 1 |
| A payment scheme is a system. The scheme operator records what it runs, and each participant records its own end. | 4 |
| A scheme's certificate authority is a scheme-administered trust anchor, verified by the scheme's members. | 4, 9.3 |
| The interfaces that carry key-encryption keys come first in a payment estate's post-quantum migration, because every key sent under them inherits their exposure. | 3, 11.1 |
| The Triple DES retirement and the post-quantum migration are recorded with the same attributes. A policy with two schedules decides which migration an interface needs. | 6 |
| The HSM profile and the card and terminal extensions are drafted in the generic documents. Financial services states its needs and refers to them. | 9 |

### 13.3 Questions for the working group

-   Should the symmetric schedule be published as part of the example algorithm-transition policy, or as a separate financial services policy?

-   Which body should be approached to co-own this document: X9, the European Payments Council or FS-ISAC?

### 13.4 Open work

1.  Build the AWS Payment Cryptography service record (11.1), check it against Service Disclosure, and offer it to the provider for review.

2.  Add the symmetric schedule to the algorithm-transition policy (10.1), with each date checked against its source.

3.  Write the scheme profile (9.3) and the scheme-readiness policy (10.2), with an illustrative scheme of three participants.

4.  Send the needs in 9.1 and 9.2 to the Change planning group document and to the devices document.

5.  Check the proposed protocol names (chapter 5) against the CycloneDX cryptography registry.

Annex A. Financial terms and methodology terms
----------------------------------------------

| Financial term | Methodology term |
|---|---|
| Hardware security module (HSM) | A product. Its key store is a storage interface with `providerLocation` `hsm` |
| HSM partition | A deployment of the HSM, described by a deployment record |
| Host command interface | A management or service interface of the HSM |
| Key block (TR-31, X9.143, ISO 20038) | The key-wrapping format of a storage or key-transport interface (`keyWrapping`, `keyStoreFormats`) |
| Master key (local master key) | The key that protects a key store. Named by the store; its value is never recorded |
| Key-encryption key (zone master key) | A key delivered over a key-transport interface and held in a key store, reached through `keyStoreRef` |
| Working key (PIN, MAC or data key) | A key held in a key store under a key-encryption key |
| Key ceremony | A procedure. It changes keys, not the record, unless it changes an algorithm or a store |
| Scheme | A system, described by a system record of what the scheme operator runs |
| Issuer, acquirer, processor | Participants, each writing records of its own end |
| Remote key loading | A key-transport interface between a host and a terminal |
