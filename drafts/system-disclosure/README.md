# Draft: the generic system overlay, `system-disclosure`

The rules every system overlay shares, whatever the sector. Proposed for the Operation group
document. Draft only: none of these files is part of Release 1.

Run `python3 build.py` in this folder to regenerate the profile.

| Rule | Attribute | Level | From |
| --- | --- | --- | --- |
| P1 | cite every product record by BOM-Link and digest | MUST | OT S1 |
| I1 | `correspondsTo`: the product interface this interface realises | MUST | OT S1 |
| I2 | `designUse`: `in-use`, `disabled` or `not-connected` | MUST | OT S2 |
| I3 | `keysProvidedBy` on each interface in use: a system component, or `product` or `none` | MUST | OT S4 |

The profile extends the interface disclosure baseline v0.10, narrowed to the subject type `system`
and the stage `configured`. Two sector overlays extend it:

| Overlay | Folder | Adds |
| --- | --- | --- |
| `ot-system` v0.2-draft | `drafts/ot-system/` | zones, conduits and the IEC 62443-3-3 level claimed |
| `telecom-service-assurance` v0.1-draft | `drafts/telecom-service-assurance/` | the services each interface carries, and the operator boundary |

## Why S4 moved as well

The working group decided that S1 and S2 move here when a second sector writes an overlay. The
telecom overlay needs S4 too: N32 and SBI certificates come from the operator's PKI, and the SEPP's
key-encryption key from its HSM. A rule both sectors need has one home, so S4 moved with them. This
goes beyond the decision as recorded, and is registered for the working group to confirm.

## Verdicts

The profile is well formed under `check_profile.py`, with one SHOULD warning: no mapping and no
non-conforming example of its own (C9). Its examples are the sector overlays' records:

| Record | system-disclosure |
| --- | --- |
| substation system, configured | conforms |
| substation system, fail-keyprovider | fails I3 on `ied1:svc-goose` |
| roaming interconnect, system | conforms |
