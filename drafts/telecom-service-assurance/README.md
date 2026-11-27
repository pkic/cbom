# Draft: the telecom service-assurance profile, `telecom-service-assurance`

The second sector system profile, after `ot-system`. Service assurance asks which services depend on
which interfaces, so that a weakness or a migration at one interface can be traced to the services
and commitments it affects (telecom CBOM document, 3.2.4: "component-to-service dependency
mapping"). Draft only: none of these files is part of Release 1.

Run `python3 build.py` in this folder to regenerate every file.

## Files

| File | What it is |
| --- | --- |
| `profile-telecom-service-assurance.rules.json` | The profile, v0.1-draft. Extends System Disclosure v0.1, published in Release 1 |
| `examples/cbom-sepp-product.cdx.json` | An illustrative SEPP 5.1.0, stage `implemented`, five interfaces. Not a real product |
| `examples/sepp-5.1.0-sbom.cdx.json` | Its companion SBOM |
| `examples/cbom-roaming-interconnect-system.cdx.json` | An operator's roaming interconnect, stage `configured`, joined to the SEPP record |
| `examples/cbom-roaming-interconnect-fail-service.cdx.json` | N32-f in use, with the services it carries left out |
| `examples/cbom-roaming-interconnect-fail-proxy.cdx.json` | N32-c crosses the operator boundary, with the component that terminates it left out |

## Rules

System Disclosure supplies the citations, the join to product interfaces, `designUse` and `keysProvidedBy`.
This profile adds:

| Rule | Attribute | Level |
| --- | --- | --- |
| P1 | `services`: the services the system delivers, as the operator's service model names them | MUST |
| I1 | `carriesService` on each interface in use: the services that depend on it, or `none` | MUST, withholdable |
| I2 | `operatorBoundary` on each interface in use: `intra-operator` or `inter-operator` | MUST |
| I3 | `proxiedBy` where the connection crosses the operator boundary: the SEPP, a security gateway or the interconnect provider | MUST, withholdable |

Service levels, availability targets, customers and a criticality rating stay in the operator's
service model, which the record joins by service name.

## The example

The SEPP is the network function at N32, the interface between roaming partners. It has five
interfaces: N32-c (TLS 1.3), N32-f (PRINS, with JWE keys derived from the N32-c session), the
service-based interface to the operator's own network functions (TLS 1.3 with OAuth 2.0), management
(NETCONF over SSH) and key storage. It is built on OpenSSL 3.5.4, OpenSSH 9.9p1 and an illustrative
JOSE library.

The roaming interconnect delivers three services: inbound roaming, outbound roaming and roaming for
mission-critical users. All five SEPP interfaces are in use. N32-c, N32-f and the service-based
interface carry all three services. Two interfaces cross the operator boundary: N32-c, terminated by
the SEPP, and N32-f, relayed by the interconnect provider. N32 and SBI certificates come from the
operator's PKI, and the key-encryption key from the operator's HSM.

## Verdicts

From `docs/methodology/`, with `--with ../../drafts/telecom-service-assurance/examples/cbom-sepp-product.cdx.json`
(the SEPP record with `--with .../sepp-5.1.0-sbom.cdx.json`):

| Document | Baseline v0.10 | system-disclosure | telecom-service-assurance |
| --- | --- | --- | --- |
| SEPP product record | conforms | not applicable (product) | not applicable |
| roaming interconnect | conforms | conforms | conforms |
| fail-service | conforms | conforms | fails I1 on `sepp:n32f` |
| fail-proxy | conforms | conforms | fails I3 on `sepp:n32c` |

The SEPP record fails the change core, as the OT records do: it states no capability per purpose or
update mechanism. The profile is well formed under `check_profile.py`, with one SHOULD warning: it
has no CycloneDX and SPDX mapping yet (C9). All five documents are valid CycloneDX 2.0. The published
test suite passes: 362 passed, 0 failed.

## What the example showed

- The question the telecom document poses for the SEPP can now be asked of the record: every
  service the interconnect delivers depends on N32-c, which uses X25519 alone. The libraries already
  support hybrid key exchange (X25519MLKEM768 in OpenSSL 3.5, mlkem768x25519-sha256 in OpenSSH 9.9);
  the SEPP leaves it out because the 3GPP profile for N32-c does not name it, and enabling it needs
  the roaming partner too. That is a configuration change agreed with each partner, not a software
  release.
- S4, the key provider, is needed in telecom as well as in OT, so it moved to System Disclosure
  with S1 and S2.
- The operator boundary has the same shape as the OT zones and conduits: an attribute that says
  whether a connection crosses a boundary, and a pointer to the component that guards it. The two
  stay separate, because IEC 62443 zones and 3GPP security domains are not the same idea.
  Release 1 keeps such boundaries as sector rules (Publication 3, 13.2).
- A service model and a CBOM join on service names. I1 checks that the names on interfaces
  match the names the system declares, with `inSubjectList`.

## Values

The SEPP, its JOSE library and every configured value are illustrative. OpenSSL 3.5.4 and OpenSSH
9.9p1 are real releases, and their post-quantum defaults are as stated. OpenSSL 3.5.4 has since had
security fixes (3.5.5 onwards); a real record would name the current patch release.
