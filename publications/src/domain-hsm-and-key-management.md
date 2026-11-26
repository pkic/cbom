CBOM Profiles — Application domain: HSMs and key management
===========================================================

Working Draft 0.1 · Nov 26, 2026 · \@Mike

Purpose
-------

This draft covers hardware security modules (HSMs) and the key management built on them, in every sector that relies on them: payments, certificate authorities and trust services, code signing, cloud key management and telecom. It is written for readers outside the working group: HSM vendors, the teams that buy and operate HSMs, certificate authorities, providers of cloud HSM and key management services, and the assessors who validate modules and audit how they are used.

HSMs and key management form a domain of their own for four reasons:

-   They sit underneath the other domains. A payment estate, a certificate authority and a code-signing service each depend on HSMs. Without a document of their own, each sector document would have to describe them again.

-   The keys they hold protect other keys. In a key hierarchy, a change at one level forces a change in everything below it, so the hierarchy, not the applications, sets the order of a migration.

-   Validation sets the pace. A new algorithm usually arrives in firmware before that firmware is validated, and a module that runs outside its validated mode can break a buyer's compliance. Whether a change triggers re-validation often decides between a firmware update and a new module.

-   The PKI Consortium's own members include HSM vendors and certificate authorities, so the domain has owners and reviewers within the consortium.

This is a working draft. It sits outside Release 1 and starts from the positions that Release 1 ratified. Positions proposed here are listed in chapter 12.

1. Scope and readers
--------------------

The draft covers three kinds of subject:

-   **HSMs as products**: general-purpose, payment and signing HSMs, and smaller hardware modules such as tokens used for signing keys.

-   **Cloud HSM and key management services**: services whose purpose is to hold keys and use them for a customer. Examples are a managed HSM, a cloud key management service and a payment cryptography service.

-   **Key vaults and key management systems**: software that holds keys and uses them for applications, with or without an HSM underneath.

Two boundaries are drawn with other documents:

-   **Cloud key management belongs here, and key custody stays in the SaaS document.** A service whose purpose is to hold and use keys for others is described in this document, with the profiles of chapter 8. The SaaS document keeps the customer's view of key custody in every other service: who holds the keys that protect a customer's data in a collaboration or database service. Where such a service relies on a key management service, its record names that service with `externalKeyService`, and the key management service has its own record under this document. The two documents therefore meet at one reference and do not overlap.

-   **Software key vaults are included.** Many estates hold their keys in a software vault, either alone or in front of an HSM. The questions a buyer asks are the same: which algorithms the vault supports, how its keys are protected, and whether the keys can move. Only validation differs. The key hierarchy records where the hierarchy is rooted: `hardware-root` where a hardware module protects the top key, and `software-root` where it is protected in software. A reader can therefore tell a vault with a hardware root from one without.

The readers are:

| Reader | What they decide |
|---|---|
| HSM and vault buyers and operators | Which models and releases to buy, and when to update firmware or replace a module |
| Certificate authorities and trust service providers | When to generate new root and issuing keys, and in which modules |
| Code-signing teams | Which module can sign with LMS, XMSS or ML-DSA, and how signature state is managed |
| Providers of cloud HSM and key management services | What to disclose about their services |
| Validation laboratories and auditors | Whether the modules in use are validated for the algorithms in use |

2. CBOM profiles in brief
-------------------------

A cryptographic bill of materials (CBOM) lists the cryptography that a product, service or system uses. It is usually written in CycloneDX. On its own, a CBOM does not say whether it contains what a reader needs, and two CBOMs of similar products can describe different things in different places.

A **profile** fixes that. It states, for one decision, which facts a CBOM must contain and how they are written. A tool can then check a CBOM against the profile and give a **verdict**: the CBOM conforms or does not conform, and the verdict names any rule that failed. A profile asks only for facts. Judgements, such as whether an algorithm is still acceptable, are made by a separate **policy**, which reads the facts and gives a dated result.

A CBOM describes its subject one **interface** at a time. For an HSM, the interfaces are the places where it uses cryptography with another party: the PKCS #11 or host command interface that applications call, the management console, the link to other HSMs in a cluster, the channel for backups, and each store that holds keys. For each interface, the CBOM records the protocol, the algorithms for each purpose and the module that implements them.

Records cite each other by link and digest. A reader joins them when reading and never merges them. A producer that does not want to disclose a fact can mark it as withheld, where the profile allows this, and the record can still conform.

PKI Consortium Publications 1 to 3 define all of this in full. This draft uses only what a reader needs to apply the method to HSMs and key management.

3. What is different about HSMs and key management
---------------------------------------------------

**Key hierarchies set the order of a migration.** An HSM holds a master key, which protects the keys stored outside the module, which in turn protect the keys that applications use. If the algorithm that wraps one level is deprecated, every key below that level has to be re-wrapped or re-issued. A buyer therefore needs to know the hierarchy before planning anything else, and the key hierarchy depth records it (8.2).

**Validation lags capability.** A vendor can add a post-quantum algorithm in firmware months or years before that firmware is validated under FIPS 140-3. Until it is, a buyer who needs validated cryptography can use the algorithm only outside the validated mode, if at all. The methodology already records this per purpose, with `validatedModeAvailability`, and per interface, with `certificationImpact` and `certificationScheme`. The FIPS 140-2 certificates moved to the CMVP Historical list on 21 September 2026. Modules validated only under FIPS 140-2 can still be used in existing systems, but not cited for new ones.

**Applications and operators use different interfaces.** Applications reach an HSM through PKCS #11, KMIP or a vendor's host command set. Operators reach it through a management console, custodian smart cards and key ceremonies. The two are different interfaces with different cryptography, and they migrate at different times. A record that describes only the application interface misses the keys that protect the HSM itself.

**Stateful hash-based signatures need special handling.** LMS and XMSS are approved for firmware and software signing, and CNSA 2.0 prefers them for that use. NIST SP 800-208 requires their keys and signatures to be generated in hardware modules that do not allow the private keys to be exported. NIST is working on a revision that would allow export while managing the risk. A signature must never be produced twice from the same one-time key, so the module has to manage the signature state. RFC 10033 (September 2026) describes the ways to do that.

**Moving keys between vendors is hard.** Keys leave an HSM, if at all, in a vendor format or in a standard key block. Whether a buyer can move to another vendor, or to a cloud service, depends on the formats both ends support and on what the export rules allow. The HSM product profile records the key block formats (8.1).

4. HSMs in the methodology's terms
-----------------------------------

| HSM term | Record | Written by |
|---|---|---|
| An HSM model and firmware release | Product record, under HSM Product | The vendor |
| A partition or cluster as configured | Deployment record, citing the product record | The owner |
| A key hierarchy | Storage interfaces linked by `protectedBy`, under HSM Key Hierarchy | The vendor for the structure, the owner for what is loaded |
| A cloud HSM or key management service | Service record, under the key management service profile (8.4) | The provider |
| A software key vault | Product record, under HSM Product, with `keyStoreLocation` `software` and its root recorded as `software-root` | The vendor or project |
| A key ceremony | Not a record. It changes keys, not cryptography, unless it changes an algorithm or a store | — |

5. Interfaces and their cryptography
------------------------------------

| Interface | Used by | Governing specification | What a record states |
|---|---|---|---|
| PKCS #11 | Applications | OASIS PKCS #11. Version 3.1 added LMS, and version 3.2 adds ML-KEM, ML-DSA and SLH-DSA | The mechanisms supported, the key types, and the transport, if the interface is reached over a network |
| KMIP | Applications and key managers | OASIS KMIP | The operations, key types and transport |
| Vendor host commands | Payment applications | The vendor's specification | The commands' cryptography and the key block formats |
| REST or gRPC API | Applications of a cloud service or vault | The provider's or project's specification | TLS, the request signing or token algorithm, and the key types |
| Management console | Security officers | The vendor's specification | TLS or a local link, and how officers authenticate |
| Custodian smart cards | Key custodians | The vendor's specification | How key components are split and protected |
| Cluster synchronisation | Other HSMs of the same owner | The vendor's specification | How keys are protected between modules |
| Backup and export | Operators | Vendor format or standard key block | The wrapping algorithm and format |
| Remote key loading | Terminals and devices | TR-34 and similar | The key transport algorithm |
| Key store | The module itself | — | The wrapping algorithm, the format and `protectedBy` |

6. Use cases
------------

| Use case | Who decides, and what | Profile |
|---|---|---|
| HSM procurement | A buyer: whether a vendor's disclosure is complete enough to compare models and releases | HSM Product |
| Firmware and validation planning | An owner: whether a needed algorithm arrives by firmware, when it is validated, and what re-validation costs | HSM Product |
| Key hierarchy migration | An owner: which keys must be re-wrapped or re-issued, and in which order | HSM Key Hierarchy |
| Code and firmware signing | A signing team: whether a module supports LMS, XMSS or ML-DSA, and how it manages signature state | HSM Product, with the signature state attribute proposed in 8.1 |
| Moving to another vendor or a cloud service | An owner: whether keys can be exported in a format the target accepts | HSM Product |
| Reliance on a cloud key management service | A customer: what it can learn from the provider, and what it must ask for | The key management service profile (8.4) |
| Root key generation for a certificate authority | A CA: which module, algorithm and hierarchy to use for a new root | HSM Product and HSM Key Hierarchy |

7. Records across the life of an HSM
------------------------------------

**Release and validation.** The vendor writes a product record for each model and firmware release, with the module validation that applies to it. When a new firmware release adds an algorithm before it is validated, the record says so with `validatedModeAvailability`.

**Procurement.** The buyer reads the product records of the candidate models and compares them under HSM Product.

**Installation and key ceremonies.** The owner writes a deployment record of its partitions, the mechanisms it has enabled and the key types it has loaded, citing the product record. Key ceremonies load keys. They do not change the record unless they add a store or change an algorithm.

**Firmware updates and re-validation.** A firmware update produces a new product record from the vendor and, once the owner applies it, a new deployment record. If the update changes the validated boundary, the vendor's record states the re-validation it triggers.

**Backup and cluster changes.** Adding a module to a cluster, or changing how backups are protected, changes interfaces, so the owner writes a new deployment record.

**Decommissioning.** The last deployment record states that the keys have been destroyed, and the module leaves the estate.

8. Profiles
-----------

The two drafted profiles are in [`drafts/hsm-product/`](../../drafts/hsm-product/), with an illustrative payment HSM that conforms to both.

### 8.1 HSM Product (drafted)

HSM Product extends PQC Migration Extended, which already carries key management, key stores, module validation and certification impact. It makes four inherited rules mandatory: `certificationImpact`, `certificationScheme`, `keyStoreFormatsSupported` and `keyStoreRef`. It adds two facts that no inherited rule could carry:

-   **`hsmApproval`**: the PCI PTS HSM approval, or `none`. PCI PTS HSM is a device approval, not a module validation, so the module validation vocabulary does not hold it, and a derived profile may not widen an inherited vocabulary.

-   **`keyBlockFormatsSupported`**: the key block formats the HSM can import and export, from X9.143, TR-31, ISO 20038, a proprietary format or none. Payment key blocks bind each key to its permitted usage, and they are not key store files such as PKCS #12.

A signing module needs one more fact, which this draft proposes for the next version: whether it supports stateful hash-based signatures, and how it protects the signature state against reuse after a restore or a failover. The vocabulary would follow the approaches of RFC 10033.

### 8.2 HSM Key Hierarchy (drafted)

HSM Key Hierarchy is a depth of HSM Product. On every key store it adds `protectedBy`, the store whose key protects this one, and `keyBlockFormat`, the format of the key blocks in the store. Following `protectedBy` from any store reaches the root, which is `hardware-root` for a hardware module and `software-root` for a vault without one.

### 8.3 HSM Deployment (proposed)

The owner's record of a partition or cluster, under Deployment Disclosure. It cites the product record and states which mechanisms are enabled, which key types are loaded at each level of the hierarchy, and how cluster members and backups are protected.

### 8.4 Key management service (proposed)

The provider's record of a cloud HSM or key management service, under Service Disclosure with the key custody depth of the SaaS document. Its interfaces are the service's APIs, its import and export methods, and its stores. The worked example of the financial services document, a payment cryptography service, is the first record of this kind.

9. Policies
-----------

**Validated-mode readiness.** For each interface an owner uses, the policy asks whether the algorithms it needs are available in a validated mode, on the evaluation date. The facts come from `validatedModeAvailability` and `moduleValidationScheme`. The policy is `mechanical`.

**Hierarchy order.** When the wrapping algorithm of one level is deprecated, the policy lists the stores below it, in the order they must move. The facts come from `protectedBy` and `keyWrapping`. The policy is `mechanical`.

**Historical validation.** The policy flags every module whose only validation is on the CMVP Historical list, such as a module validated only under FIPS 140-2. The policy is `mechanical`.

10. Worked examples
-------------------

### 10.1 An illustrative payment HSM (drafted)

"Example Payment HSM 9000", firmware 4.2.0, invented but realistic. It has a host command interface over TLS 1.3 with hybrid ML-KEM key exchange committed for the next firmware, a management console with custodian smart cards, remote key loading with TR-34, a master key store with `hardware-root`, and a working key database protected by the master key. It conforms to both profiles. A variant without key block formats fails exactly the rule that requires them.

### 10.2 A real product: Kryoptic (proposed first)

The first real example should be **Kryoptic**, an open-source PKCS #11 software token written in Rust. It is the best fit for three reasons:

-   It offers PKCS #11 3.2 by default, the version that adds ML-KEM, ML-DSA and SLH-DSA (LMS came in version 3.1), and it supports ML-KEM and ML-DSA.

-   Its cryptography comes from OpenSSL 3.5 or later, and it can be built to use only the OpenSSL FIPS provider. The record would therefore show how a module's post-quantum capability and its validated mode depend on a provider underneath, which is a question every HSM buyer faces.

-   As a software token, it tests the `software-root` side of the key hierarchy, which no example covers yet.

**SoftHSM version 2** is better known, and its documentation lists ML-DSA mechanisms when it is built against OpenSSL 3 with ML-DSA enabled. It would make a good second example, to compare two tokens behind the same interface.

### 10.3 A software vault: OpenBao (proposed)

**OpenBao**, the open-source key and secrets manager, is the right example of a vault. Version 2.7 adds ML-DSA to its Transit and PKI engines, lets its listeners require post-quantum key exchange in TLS, and can keep keys in an external HSM through PKCS #11 plugins. One record would show a vault, a hybrid TLS listener and a hierarchy whose root can be either software or hardware, depending on the deployment.

### 10.4 A cloud service (drafted in the financial services document)

The financial services document describes AWS Payment Cryptography as a service record, written from public documentation. It shows what a customer can learn about a cloud key service without the provider's help, and lists the 21 facts it cannot.

11. Standards, validation and regulation
----------------------------------------

| Source | What it asks for that a CBOM can supply | What stays outside the CBOM |
|---|---|---|
| FIPS 140-3 and ISO/IEC 19790, with the CMVP | Which module implements each interface, its validation reference, and whether each algorithm is available in the validated mode | The security policy of the module and its test results |
| CMVP handling of FIPS 140-2 | Which modules are validated only under FIPS 140-2, now on the Historical list | — |
| PCI PTS HSM | Whether a model is approved, and the approval reference | The approval conditions |
| CA/Browser Forum Code Signing Baseline Requirements | Since 1 June 2023, code-signing keys must be generated and held in a hardware module meeting FIPS 140-2 Level 2, Common Criteria EAL 4+ or equivalent. A record shows the module and its validation | How the CA verifies the key was generated in hardware |
| NIST SP 800-208 | Whether a module supports LMS or XMSS in hardware without key export | How the owner manages signature state day to day |
| CNSA 2.0 | Whether a signing module supports the CNSA 2.0 algorithms, and from which firmware | The national security system's own approvals |
| OASIS PKCS #11 3.2 and KMIP | Which mechanisms and key types an interface supports | — |
| NIS2 implementing regulation, point 9.2(c), and DORA technical standards, Article 7 | What a module's key management can do, and where keys are held. See the regulatory sufficiency register | The entity's key management procedures |

12. Positions and open work
---------------------------

### 12.1 Release 1 positions this draft starts from

| Position | Ratified in |
|---|---|
| Facts go in the CBOM, and judgements go in a versioned policy. | Publication 2 |
| Records cite each other by link and digest, and are joined, not merged. | Publication 2 |
| A sector profile extends a Release 1 profile, directly or through another, and adds only rules specific to its sector. | Publication 3, position 27 |
| Key material is excluded at every depth. | Publication 2 |

### 12.2 Positions proposed in this draft

| Position | Chapter |
|---|---|
| A service whose purpose is to hold and use keys for others is described in this document. The SaaS document keeps key custody in other services, and the two meet at `externalKeyService`. | 1 |
| Software key vaults are included. The key hierarchy records whether its root is in hardware or in software. | 1, 8.2 |
| The PCI PTS HSM approval is a device approval, recorded separately from module validation. | 8.1 |
| Payment key block formats are recorded separately from key store formats. | 8.1 |
| A key hierarchy is recorded as key stores linked by `protectedBy`, up to a hardware or software root. | 8.2 |
| The first real example is Kryoptic, followed by OpenBao for the vault case. | 10 |

### 12.3 Open work

1.  Build the Kryoptic product record from its source, and check it against HSM Product.

2.  Add the signature state attribute for stateful hash-based signatures to HSM Product (8.1).

3.  Write HSM Deployment (8.3) and the key management service profile (8.4).

4.  Add a check that following `protectedBy` from every store reaches a root without a cycle.

5.  Build the OpenBao record.

6.  Add FIPS 140-3, PCI PTS HSM and the code-signing requirements to the regulatory sufficiency register.

Annex A. HSM terms and methodology terms
----------------------------------------

| HSM term | Methodology term |
|---|---|
| HSM, hardware crypto module | A product, under HSM Product |
| Partition, slot, token | A deployment of the module, in a deployment record |
| Mechanism (PKCS #11) | An algorithm on an interface, in the `Supported` attributes |
| Master key, local master key | The key that protects a key store at the top of a hierarchy, behind a store with `protectedBy` `hardware-root` |
| Key-encryption key, wrapping key | The key of a store that another store's `protectedBy` points to |
| Validated mode, approved mode | `validatedModeAvailability` for each purpose |
| Module validation, certificate | `moduleValidationScheme` and `moduleValidationRef` |
| Key ceremony | A procedure, not a record |
| Signature state (LMS, XMSS) | Proposed attribute (8.1) |
