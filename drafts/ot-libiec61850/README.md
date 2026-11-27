# Draft OT example: libIEC61850 v1.6.2

The first OT example with real values, written for the operational technology domain document
(Working Draft 0.1, chapter 10). The subject is [libIEC61850](https://github.com/mz-automation/libiec61850)
v1.6.2, an open-source (GPLv3) IEC 61850 library, built with Mbed TLS 3.6. The working group wrote
the record from the project's public source at the `v1.6` branch. The maintainers have not reviewed it.

## Files

| File | What it is |
| --- | --- |
| `build.py` | Writes both documents |
| `examples/cbom-libiec61850-1.6.2-product.cdx.json` | Product record, stage `implemented`, five interfaces |
| `examples/libiec61850-1.6.2-sbom.cdx.json` | Companion SBOM, cited by BOM-Link and SHA-256 |

## Verdicts

Run from `docs/methodology/`, with `--with ../../drafts/ot-libiec61850/examples/libiec61850-1.6.2-sbom.cdx.json`:

| Profile | Verdict |
| --- | --- |
| `profile-interface-enumeration.rules.json` | conforms |
| `profile-interface-disclosure.rules.json` | conforms |
| `profile-change-core.rules.json` | does not conform: no capability, enablement, transition mode or update mechanism |
| `profile-pqc-migration-ot.rules.json` | does not conform: the change core's failures, plus I1 (`certificationImpact`) |

Both documents validate against the pinned CycloneDX 2.0 schema (`tests/check-cyclonedx.py`).

## Findings

- A record written from public source stops at the baseline. The change-core facts need the maintainer.
- MMS, GOOSE and SV state `keysStoredIn` as `none`: they use no key, and `pqc-migration-ot#I3` accepts the literal (R2-16).
- `R-GOOSE` is added to the list of protocol names after Release 1 (R2-17).

## Values to confirm

- The Mbed TLS 3.6 default named groups in `keyExchangeSupported` are taken from the library's
  defaults. Confirm them against the compiled configuration.
- Mbed TLS is identified as `v3.6.0`, the version the libIEC61850 README names.
