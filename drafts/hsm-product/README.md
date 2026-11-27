# Draft: HSM profiles

Two draft profiles for hardware security modules, and their examples. They are the profiles of the
HSMs and key management domain document (outline: `drafts/domain-outlines/hsm-and-key-management.md`).
The financial services draft (9.1) relies on them, and so would every other sector that uses HSMs.
Draft only: neither is part of Release 1.

Run `python3 build.py` in this folder to regenerate the examples.

## Profiles

| File | Extends | Adds |
| --- | --- | --- |
| `profile-hsm-product.rules.json` | PQC Migration Extended v0.3 | P1 `productCertificationScheme` (`pci-pts-hsm` or `none`), P2 `productCertificationRef` (SHOULD); on management interfaces that handle keys, I1 `keyBlockFormatsSupported` and I2 `keyBlockFormats` (SHOULD), from `x9-143`, `tr-31`, `iso-20038`, `proprietary`, `none`. Raises four inherited rules to MUST: `certificationImpact` and `impactedCertification` (pqc-migration I17, I18), `keyStoreFormatsSupported` and `keysStoredIn` (pqc-migration-extended I5, I8) |
| `profile-hsm-key-hierarchy.rules.json` | HSM Product v0.1 | On every storage interface: I3 `protectedBy`, the store whose key protects this one, or `hardware-root`, or `software-root` for a vault without a hardware module; I4 `keyBlockFormats`, the format of the key blocks in the store |

Two facts needed their own attributes rather than an inherited one:

- **The payment HSM approval.** PCI PTS HSM is a device approval, not a module validation, so the
  module validation vocabulary does not hold it. A derived profile may not widen an inherited
  vocabulary (Publication 2, position 31), so the approval is a new product attribute.
- **Key block formats.** The key store formats of PQC Migration Extended describe files such as
  PKCS #12 and JKS. Payment key blocks bind each key to its permitted usage, and an HSM must agree a
  format with each counterparty, so they are a separate attribute.

## Verdicts

From `docs/methodology/`:

| Document | Profile | Verdict |
| --- | --- | --- |
| `cbom-example-payment-hsm-product` | hsm-product | conforms |
| `cbom-example-payment-hsm-product` | hsm-key-hierarchy | conforms |
| `cbom-example-payment-hsm-product-fail-I1` | hsm-product | fails I1: the management interface omits its key block formats |

Both profiles are well-formed under `check_profile.py`. Both examples are valid CycloneDX 2.0.

## The example

An illustrative payment HSM, "Example Payment HSM 9000", firmware 4.2.0. The vendor and every value are
invented, chosen to be realistic for a payment HSM:

- a host command interface over mutually authenticated TLS 1.3, with hybrid ML-KEM key exchange
  committed for firmware 5.0;
- a management console with custodian smart cards, which generates, imports, exports, wraps and
  derives keys, in X9.143, TR-31 and ISO 20038 key blocks;
- remote key loading to terminals with TR-34 and RSA-2048, for which no post-quantum key transport is
  standardised yet (`blockedBy` `standard`);
- a local master key store, protected by the tamper-responsive hardware (`protectedBy`
  `hardware-root`);
- a working key database on the host, in X9.143 key blocks under the local master key (`protectedBy`
  `service:sto-lmk`).

## Open work

- `protectedBy` is checked as a reference to a local storage interface. Nothing yet checks that
  following it from every store reaches `hardware-root` without a cycle. That needs a new constraint
  in the validator.
- The validator counts a cryptographic provider only when its component type is `library`. An HSM's
  provider is its firmware, so the example declares it as a library. Whether `firmware` should count
  is a question for the question register.
- Write the deployment side: a bank's record of its HSM partitions, citing this product record, with
  the keys it has loaded at each level.
