# Draft: AWS Payment Cryptography as a service record

The worked example of the financial services domain document (chapter 11). Draft only: it is not part
of Release 1. The working group wrote the record from the provider's public documentation, read on
26 November 2026. The provider has not reviewed it.

Run `python3 build.py` in this folder to regenerate the record. The pages the record was written from
are listed in `SOURCES` in the script, and in the record's external references.

## How the record was written

Every value comes from a documentation page. A fact the pages do not state is marked `unknown` with a
disclosure marker. No value is guessed. The record therefore shows what a customer can learn about the
service from public documentation alone.

| Interface | Type | What the documentation states |
| --- | --- | --- |
| `service:api-tls` | service | TLS 1.2 or later required; hybrid post-quantum key exchange with ML-KEM offered and chosen by the client |
| `service:mgmt-control-plane` | management | Key creation, import, export and deletion; every call signed |
| `service:svc-data-plane` | service | Payment operations; every call signed |
| `service:kt-kek-tr34` | interconnect | Key-encryption keys exchanged with TR-34, RSA 2048, 3072 or 4096 |
| `service:kt-kek-ecdh` | interconnect | Key-encryption keys agreed with ECDH on P-256, P-384 or P-521, with the KDF of SP 800-56A or X9.63 |
| `service:kt-working-keys` | interconnect | Working keys in TR-31 or X9.143 key blocks, under Triple DES or AES |
| `service:sto-payment-keys` | storage | Key blocks protected by AES-256 main keys in PCI PTS HSMs; each key in one region; custody provider-managed |

## Verdict

From `docs/methodology/`:

```
python3 validate_cbom.py ../../drafts/fs-payment-cryptography-service/examples/cbom-aws-payment-cryptography-service.cdx.json profile-service-disclosure.rules.json
```

The record does not conform to Service Disclosure. It passes 52 rule checks. Of the rest, 21 are
facts marked `unknown` and one is a rule the record cannot meet:

| What is missing | Rule | Interfaces | Who can supply it |
| --- | --- | --- | --- |
| Implementing library or module | baseline I9 | all 7 | The provider |
| Authentication algorithm (server certificate, request signing, TR-34 and ECDH signatures) | baseline I5 | 5 | The provider |
| Protocol version (HTTP API, TR-34, ECDH scheme, X9.143) | baseline I2 | 5 | The provider |
| Encryption algorithm (TLS cipher suites, TR-34 and ECDH wrapping) | baseline I4 | 3 | The provider |
| TLS key exchange groups | baseline I3 | 1 | The provider, or an observation of the endpoint |
| A cited record of what the service builds on | service-disclosure P3 | document | Nobody: no product records are published for the HSMs the service runs on |

The record is valid CycloneDX 2.0 (`tests/check-cyclonedx.py`).

## What the example showed

- A customer can learn the shape of the service from public documentation: its interfaces, the key
  types, the key exchange methods and how keys are stored. It cannot learn the implementing modules,
  the authentication algorithms or the exact protocol versions. Those 21 facts are what a customer
  would ask the provider for, and they are the content of the review request to the provider.
- The quantum-exposed interfaces are the two that carry key-encryption keys (TR-34 and ECDH). Every
  working key exchanged later inherits their exposure. The API is already offered with hybrid
  post-quantum TLS, so the key exchange interfaces, not the API, are where the migration work lies.
- Service Disclosure P3 assumes that a service can cite the product records of what it runs. A
  provider that runs its own platform on hardware whose vendor publishes no records cannot meet P3
  honestly. Question register item R2-29 proposes that P3 accept a declared absence with a reason,
  in the same way as P2.
