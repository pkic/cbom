# Draft: Thales Luna T7 from its FIPS 140-3 security policy

The first real example of the draft HSM Product and HSM Key Hierarchy profiles, and of the HSMs and key
management domain document (chapter 10.2). Draft only: it is not part of Release 1. The working group wrote
the record from public sources, read on 26 November 2026, and the vendor has not reviewed it:

- the CMVP certificate [#5450](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/5450):
  FIPS 140-3, overall level 3, validated 29 July 2026, sunset 28 July 2031;
- the module's [non-proprietary security policy](https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp5450.pdf),
  document 002-500027-001, revision G, 14 April 2026.

Run `python3 build.py` in this folder to regenerate the record. Each value names, in the interface's
constraints, the section or table of the security policy it comes from. A fact the security policy does
not state is marked `unknown` with a disclosure marker. No value is guessed.

## What the record covers

The record describes the validated module: the PCIe card, part numbers 872-500025-001 (Luna T7) and
875-500025-002 (Luna T7U), with firmware 7.15.1. The Luna Network HSM appliance and the services built on
the module have interfaces outside the module boundary, such as SSH to the appliance and the client's
network link. They belong in their own records, which would cite this one.

| Interface | Type | What the security policy states |
| --- | --- | --- |
| `service:svc-icd` | service | ICD commands over PCIe in plaintext; ML-KEM, ML-DSA and LMS services in the approved mode, with RSA, ECDSA and AES |
| `service:mgmt-icd` | management | Key generation, import, export, wrapping and zeroisation; roles authenticate with a password or PED keys |
| `service:mgmt-ped` | management | PED tunnel with KAS-ECC; remote PED protected with KTS-RSA and KTS-HMAC; local PED in plaintext over serial |
| `service:mgmt-firmware-load` | management | New firmware accepted only after an RSA 4096 signature with SHA2-384 is verified |
| `service:int-cloning` | interconnect | Cloning tunnel with KAS-RSA between RSA-4096 keys; objects wrapped with AES-KWP under a derived key |
| `service:int-wrapped-export` | interconnect | Export, import, backup and restore with AES-KW, AES-KWP or RSA-OAEP |
| `service:sto-mtk` | storage | The master tamper key, AES-256, in battery-backed NVRAM, derived from an internal split and the SRV on the purple PED key: `hardware-root` |
| `service:sto-partition-keys` | storage | Partition keys, including LMS, ML-DSA and ML-KEM private keys, in flash under the MTK: `protectedBy` `service:sto-mtk` |

## Result

Against HSM Key Hierarchy v0.2 the record does not conform: 251 checks pass, 37 are unknown, 15 MUST checks
fail and 2 SHOULD checks fail. The record is valid CycloneDX 2.0. The failures are what a security policy
cannot supply:

- **P3, identification.** The module has part numbers and a certificate, but no package URL (question
  register R2-33).
- **R1 and R2, SBOM and vulnerability statements.** The security policy points to neither, and only the
  vendor can say whether they are published.
- **G1, twelve times.** On the PED, firmware load, cloning and export interfaces, the security policy lists
  only classical asymmetric algorithms and states no plan, so the post-quantum status for key
  establishment, authentication and non-repudiation is unknown (R2-34).
- **P1 and P2 (SHOULD).** The firmware has no package URL, and a general-purpose HSM has no PCI PTS HSM
  approval reference. P2 should apply only when `hsmApproval` is not `none`.

The unknowns are the protocol versions of the vendor's own protocols, the implementation's package URL, how
a new algorithm is enabled, and whether old and new algorithms can run together.

## What the security policy supplies well

- The validated firmware and hardware versions, and the certificate.
- The approved algorithms, with their algorithm certificates, including ML-KEM, ML-DSA and LMS.
- The ports and the data each carries.
- The key table, from which the key hierarchy follows: the MTK protects the partition keys, and the MTK is
  derived from a split held on a PED key.
- The firmware verifier, which decides whether the module can later accept firmware signed with a new
  algorithm.

## What it does not say

- Anything about plans or roadmaps.
- How LMS signature state is protected against reuse after a restore or a cloning. The security policy
  lists LMS key generation, signing and verification, but not state handling, which supports the signature
  state attribute proposed in chapter 8.1 of the domain document.
- The PKCS #11 mechanisms the host library offers.
- Whether the firmware verification key can be replaced.

The security policy also states, in section 2.1, that without the configuration of section 11.1.2 the
module uses non-approved cryptography, and in section 4.4 that it has no non-approved mode. The record
follows section 11.1.2: the approved mode must be set with HSM policy 12, so `defaultState` is `disabled`.

## Open work

1. Ask the vendor to review the record and supply the unknown facts.
2. Write a record of the Luna Network HSM appliance that cites this one.
3. Make hsm-product P2 conditional on `hsmApproval` not being `none`.
4. Settle R2-33 and R2-34.
