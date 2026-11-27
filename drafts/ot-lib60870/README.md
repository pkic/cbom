# Draft OT example: lib60870 v2.4.1

The control-centre link of the reference substation, written for the operational technology domain
document (chapter 12). The subject is [lib60870](https://github.com/mz-automation/lib60870) v2.4.1
(15 July 2026), the open-source (GPLv3) IEC 60870-5-101 and IEC 60870-5-104 library from MZ
Automation, built with Mbed TLS 3.6. The working group wrote the record from the project's public
source at the `v2.4.1` tag. The library was not built or run, and the maintainers have not reviewed
the record.

## Files

| File | What it is |
| --- | --- |
| `build.py` | Writes both documents |
| `examples/cbom-lib60870-2.4.1-product.cdx.json` | Product record, stage `implemented`, three interfaces |
| `examples/lib60870-2.4.1-sbom.cdx.json` | Companion SBOM, cited by BOM-Link and SHA-256 |

## Interfaces

| Interface | Protocol | Cryptography |
| --- | --- | --- |
| `tls-104` | TLS 1.2 and 1.3 (IEC 62351-3) | Through Mbed TLS. Key exchange and encryption peer-defined, authentication deployment-defined |
| `svc-104` | IEC 60870-5-104 | None in the library |
| `svc-101` | IEC 60870-5-101, serial | None in the library |

## Verdicts

Run from `docs/methodology/`, with `--with ../../drafts/ot-lib60870/examples/lib60870-2.4.1-sbom.cdx.json`:

| Profile | Verdict |
| --- | --- |
| `profile-interface-enumeration.rules.json` | conforms |
| `profile-interface-disclosure.rules.json` | conforms |
| `profile-change-core.rules.json` | does not conform: no capability, enablement, transition mode or update mechanism |
| `profile-pqc-migration-ot.rules.json` | does not conform: the change core's failures, plus I1 (`certificationImpact`) |

The same pattern as libIEC61850. Both documents validate against the pinned CycloneDX 2.0 schema.

## Findings

- The default cipher suites include `TLS_RSA_WITH_AES_128_CBC_SHA256`: RSA key transport, with no forward
  secrecy, which IEC 62351-4:2018 makes mandatory. A record captured today is open to later decryption
  if that suite is negotiated. This is the strongest harvest-now-decrypt-later finding in the OT examples.
- The README names only Mbed TLS 2.28, whose support ended at the end of 2024. The code has integrated 3.6
  since v2.4.0. A build that follows the README, or uses CMake with both versions present, gets 2.28.
- Application-layer authentication (IEC 60870-5-7, IEC 62351-5) is a commercial add-on. Without it, IEC 104
  outside TLS and IEC 101 have no cryptography at all.
- The library's own Mbed TLS 3.6 configuration file appears not to be used by the build: it contains an
  `#error` line, and Mbed TLS resolves the configuration file name to its own default first. If so, the
  Mbed TLS defaults apply, with TLS 1.3 enabled.

## Values to confirm

- The named groups in `keyExchangeSupported`, and TLS 1.3 support, follow from the Mbed TLS 3.6 default
  configuration. Confirm both against a build.
- Mbed TLS is identified as `mbedtls-3.6.8`, the current 3.6 release. The project does not pin a patch release.
- `protocolVersion` for IEC 104 and IEC 101 is the edition year of the standard (2006, 2003).
