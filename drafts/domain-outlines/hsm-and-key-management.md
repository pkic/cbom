# CBOM Profiles — Application domain: HSMs and key management (Outline)

> This outline has been drafted as Working Draft 0.1, in [`publications/src/domain-hsm-and-key-management.md`](../../publications/src/domain-hsm-and-key-management.md). The outline is kept as a record of the plan. Decisions 2 to 4 are answered as proposed positions in chapters 1, 8.2 and 10 of the draft. The first real example is the Thales Luna T7, written from its FIPS 140-3 security policy, with Kryoptic and OpenBao after it. Ownership remains open.

Outline · 26 November 2026 · Mike

## Purpose and sources

The document would cover hardware security modules (HSMs) and the key management built on them, in every sector that relies on them: payments, certificate authorities and trust services, code signing, cloud key management, and telecom. It is written for readers outside the working group: HSM vendors, the teams that buy and operate HSMs, certificate authorities, cloud providers that offer HSM and key management services, and the assessors who validate modules and audit their use.

HSMs and key management form a domain of their own for four reasons:

- They sit underneath the other domains. A payment estate, a certificate authority and a code-signing service each depend on HSMs, and each sector document would otherwise describe them again.
- The keys they hold protect other keys. A key hierarchy means that a change at one level forces a change in everything below it, so the order of a migration is set by the hierarchy, not by the applications.
- Validation sets the pace. A new algorithm usually arrives in firmware before that firmware is validated, and a module that runs outside its validated mode can break a buyer's compliance. Whether a change triggers re-validation often decides between a firmware update and a new module.
- The PKI Consortium's own members include HSM vendors and certificate authorities, so the document has natural owners and reviewers inside the consortium.

Candidate sources, to confirm before drafting: FIPS 140-3 and ISO/IEC 19790, and the CMVP's handling of FIPS 140-2 certificates; PCI PTS HSM; Common Criteria and EUCC, with the EN 419221-5 protection profile for trust service modules; the CA/Browser Forum Baseline Requirements and Code Signing Baseline Requirements on key protection; NIST SP 800-208 on stateful hash-based signatures, which must be generated and used in hardware; CNSA 2.0 on firmware and software signing; OASIS PKCS #11 and KMIP, and their post-quantum mechanisms; ANSI X9.24, X9.143 and ISO 20038 for payment key blocks; and the published documentation of cloud HSM and key management services.

## Proposed chapters

### 1. Scope and readers
- On-premises HSMs: general-purpose, payment and signing HSMs.
- Cloud HSM and key management services, as services a customer does not run.
- Key management systems built on HSMs.
- Out of scope for a first version: software-only key vaults with no hardware root, unless a member offers an example.

### 2. CBOM profiles in brief
- The same short primer as the other domain documents.

### 3. What is different about HSMs and key management
- Key hierarchies, and why their order decides the order of a migration.
- Validation and re-validation: what a firmware change costs, and running outside the validated mode.
- Interfaces that applications use (PKCS #11, KMIP, vendor host commands) against interfaces that operators use (management consoles, custodian smart cards, key ceremonies).
- Stateful hash-based signatures (LMS, XMSS) for code and firmware signing: keys that must not be copied, and signature state that must not be reused.
- Moving keys between vendors: key block formats and export rules.

### 4. HSMs in the methodology's terms
- An HSM model and firmware release: a product record, under HSM Product.
- An HSM partition or cluster as configured by its owner: a deployment record that cites the product record.
- A cloud HSM or key management service: a service record, under Service Disclosure, with the key custody depth of the SaaS document.
- A key hierarchy: storage interfaces linked by `protectedBy`, up to the store the hardware protects.

### 5. Interfaces and their cryptography
- PKCS #11, KMIP, vendor host command sets, management consoles, custodian smart cards, cluster synchronisation between HSMs, backup and key export, and remote key loading (TR-34).

### 6. Use cases
- HSM procurement: whether a vendor's disclosure is complete enough to compare models and firmware releases.
- Firmware and validation planning: whether a needed algorithm arrives by firmware, when it is validated, and what re-validation costs.
- Key hierarchy migration: which keys must be re-wrapped or re-issued, and in which order.
- Code and firmware signing: whether a signing HSM supports LMS, XMSS or ML-DSA, and how it manages signature state.
- Moving to another vendor or to a cloud service: whether keys can be exported in a format the target accepts.
- Reliance on a cloud key management service: what the customer can learn, and what it must ask the provider.

### 7. Records across the life of an HSM
- Vendor release and validation, procurement, installation and key ceremonies, firmware updates and re-validation, backup and cluster changes, decommissioning and key destruction.

### 8. Profiles
- HSM Product (drafted): extends PQC Migration Extended; adds the payment HSM approval and key block formats, and makes certification impact and key store references mandatory.
- HSM Key Hierarchy (drafted): a depth of HSM Product; adds `protectedBy` and `keyBlockFormats` on every key store.
- HSM Deployment (proposed): the owner's record of partitions, enabled mechanisms and loaded key types, citing the product record.
- Key management service (proposed): Service Disclosure with the SaaS key custody depth, for cloud HSM and key management services.

### 9. Policies
- Validated-mode readiness: whether every interface the owner uses has its needed algorithms available in a validated mode.
- Hierarchy order: which stores must move first when the wrapping algorithm of one level is deprecated.

### 10. Worked examples
- Drafted: an illustrative payment HSM that conforms to both HSM profiles (`drafts/hsm-product/`).
- Proposed: SoftHSM or another open-source PKCS #11 implementation, written from its public source as a product record.
- Proposed: a cloud key management service, written from its public documentation as a service record, as the financial services document does for a payment cryptography service.

### 11. Standards, validation and regulation
- For each: which evidence questions a CBOM answers, added to the regulatory sufficiency register.

### 12. Positions and open work
- Positions the document would propose, for example that a key hierarchy is recorded as linked key stores, and that the payment HSM approval is a device approval separate from module validation.

## Decisions needed before drafting
1. Ownership: which PKI Consortium group, or which member organisations, would co-own the document.
2. Scope: whether cloud key management services belong here or stay in the SaaS document, which already has a key custody depth.
3. Scope: whether software key vaults without a hardware root are included.
4. Which open-source product to build the first real example on.
