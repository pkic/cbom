# Draft: the OT system overlay, `ot-system`

The overlay proposed in the operational technology domain document (8.3), with the reference
substation as its first worked example. Draft only: none of these files is part of Release 1. Version 0.2-draft extends the generic system
overlay, `system-disclosure`.

Run `python3 build.py` in this folder to regenerate every file.

## Files

| File | What it is |
| --- | --- |
| `profile-ot-system.rules.json` | The overlay, v0.2-draft. Extends the generic overlay `system-disclosure` (`drafts/system-disclosure/`) |
| `examples/cbom-sas-reference-system-configured.cdx.json` | The reference substation as its integrator delivers it. Lists every interface of the two product records it cites: the protection IED and lib60870, which the substation gateway embeds |
| `examples/cbom-sas-reference-system-fail-conduit.cdx.json` | The same record with `crossesConduit` removed from the enrolment interface, whose path leaves the station bus |
| `examples/cbom-sas-reference-system-fail-keyprovider.cdx.json` | The same record with `keysProvidedBy` removed from the GOOSE interface, which is in use |

## Rules

The domain document numbers the rules S1 to S5. S1, S2 and S4 are not specific to OT and now sit in
the generic overlay. The rules files follow the methodology's numbering (requirement C16), and each
rule names the S-rule it implements.

| Domain document | Rules file | Attribute | Level |
| --- | --- | --- | --- |
| S1 | system-disclosure P1, I1 | citations with digest; `correspondsTo` | MUST |
| S2 | system-disclosure I2 | `designUse`: `in-use`, `disabled` or `not-connected` | MUST |
| S3 | ot-system P1, I1, I2, I3 | `zones` on the system; `zone` and `zonePath` on each interface; `crossesConduit` where the path crosses zones | MUST |
| S4 | system-disclosure I3 | `keysProvidedBy` on each interface in use: a system component, or `product` or `none` | MUST |
| S5 | ot-system P2 | `claimedSecurityLevel`: `sl-c-1` to `sl-c-4` | SHOULD |

## The record

Thirteen interfaces: ten from the protection IED and three from lib60870 in the substation gateway.
Nine are in use. Sampled values and IEC 101 are `not-connected`; firmware update and IEC 104 without
TLS are `disabled`. Three paths cross from the station bus to the control centre through the gateway:
certificate enrolment, remote engineering and IEC 104 over TLS.

The IEC 104 link uses the one cipher suite the control centre's front end accepts,
`TLS_RSA_WITH_AES_128_CBC_SHA256`: RSA key transport, with no forward secrecy (illustrative). Its
implementing library, Mbed TLS 3.6.8, is inherited from the lib60870 record through `correspondsTo`.

## Verdicts

From `docs/methodology/`, with `--with examples/cbom-ot-protection-ied-product.cdx.json --with
../../drafts/ot-lib60870/examples/cbom-lib60870-2.4.1-product.cdx.json`:

| Document | Baseline v0.10 | system-disclosure | ot-system |
| --- | --- | --- | --- |
| configured | conforms | conforms | conforms |
| fail-conduit | conforms | conforms | fails ot-system#I3 (S3) on `ied1:mgmt-enrol` |
| fail-keyprovider | conforms | fails I3 (S4) on `ied1:svc-goose` | fails system-disclosure#I3 |

The overlay is well formed under `check_profile.py`, with one SHOULD warning: it has no CycloneDX and
SPDX mapping yet (C9). All three records are valid CycloneDX 2.0. The published test suite passes:
337 passed, 0 failed.

## What the example showed

- The overlays need no change to the validator. Every rule uses a constraint the evaluator already
  has, and each conditional rule needs only one condition.
- S4 asks every interface in use where its keys or trust come from, with the literals `product` and
  `none` for the two cases where no other component is involved.
- `securityLevel` was refused by requirement C6, which rejects names that suggest a judgement. The
  attribute is `claimedSecurityLevel`: the record reports the integrator's claim and makes no judgement.
- The evaluator checks `designUse` on each interface listed. It does not check that every interface of
  every cited product is listed, which S2 asks. Registered as R2-18.
- The gateway's supplier has published no record, so the integrator joins the gateway's interfaces to
  the record of the library it embeds. The join gives the implementing library but skips the device:
  the gateway's own update path and key storage stay unknown.
- `crossesConduit` and `keysProvidedBy` name components of the system record by `bom-ref`. The evaluator
  does not check that they resolve.
