# Draft: telecom network function profiles

One draft profile for the telecom domain document, and its examples. Draft only: none of these
files is part of Release 1.

Run `python3 build.py` in this folder to regenerate every file.

## Profiles

| File | Telecom document | Extends | Adds |
| --- | --- | --- | --- |
| `profile-telecom-network-function.rules.json` | 8.1 | Interface Disclosure Baseline v0.10 | `referencePoint` on every interface (I1); `referenceSpecification` where it implements one (I2) |

The rule on what terminates each interface was first drafted here as `telecom-nf-deployment`. On 19 November 2026 it moved into Release 1: the baseline defines `terminatedBy` (I14) at MAY, and Deployment Disclosure v0.3 requires it. The draft profile was removed.

## The examples

The Open5GS SEPP record is written by the working group from the public source at the v2.8.0 tag:
`lib/sbi/nghttp2-server.c`, `lib/sbi/client.c`, `lib/sbi/context.c`, `src/sepp/context.c`,
`src/sepp/n32c-build.c` and `configs/open5gs/sepp1.yaml.in`. It is not written by the Open5GS
maintainers. The library versions are those of an Ubuntu 24.04 build and are marked to confirm.

What the source shows:

- N32-c and N32-f both use TLS. PRINS is not implemented: the SEPP advertises TLS as its only
  security capability.
- The TLS server context sets the group list to P-256 only. The server negotiates ECDHE on P-256
  whatever the client offers, and there is no setting to change it. The client side uses libcurl
  with OpenSSL's default groups.
- The server allows TLS 1.0 to 1.3 in code; OpenSSL 3 refuses 1.0 and 1.1 at its default security
  level. Client certificate verification is off unless `verify_client` is set.
- The shipped configuration runs the SBI over HTTP without TLS.

The deployment record is illustrative: an operator runs the SEPP in Kubernetes with a service mesh.
N32 is terminated by the SEPP. The SBI runs as plain HTTP inside the pod, and the mesh sidecar
terminates mutual TLS with its own CA's RSA-2048 certificates.

## Verdicts

From `docs/methodology/`:

| Document | Profile | Verdict |
| --- | --- | --- |
| `cbom-open5gs-sepp-2.8.0-product` | baseline; telecom-network-function, `--with examples/context/open5gs-sepp-2.8.0-sbom.cdx.json` | conforms |
| `cbom-open5gs-sepp-fail-referencepoint` | telecom-network-function | fails I1 on `n32c` |
| `cbom-open5gs-sepp-deployment-configured` | deployment-disclosure v0.3, `--with examples/cbom-open5gs-sepp-2.8.0-product.cdx.json` | conforms |
| `cbom-open5gs-sepp-deployment-fail-termination` | deployment-disclosure v0.3 | fails `interface-disclosure#I14` on `dep:sbi` |

## What the examples showed

- Post-quantum key exchange on N32 is blocked in the product itself: the group list is fixed in
  code. Linking OpenSSL 3.5 would not change it. This is the case the change core's blocker
  `product` describes.
- Behind a mesh, the SBI's cryptography is the mesh's, not the SEPP's. Without `terminatedBy`, the
  deployment record would show plain HTTP on the SBI and nothing about the mutual TLS that protects
  it, or show the mesh's TLS as if the SEPP did it.
