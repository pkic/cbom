# Draft attribute: `updateAuthority`

**Status:** draft, for working group review. Settles Q65 provisionally (chair's call, 10 November 2026).

## The question it answers

Who can get new software or firmware onto this product?

An operator deciding whether to update, replace or isolate a device needs the answer. Without it,
the operator cannot tell an update they can actually carry out from one that only exists on paper.
Firmware often reaches a device through a third party, such as a connectivity provider, a platform
operator or an installer with physical access. The operator may have no relationship with that
party. The IoT use case (`docs/use-cases/iot.html`) raised the need.

## Definition

`updateAuthority` names the parties from which the product's update mechanism accepts new software
or firmware.

It describes the update mechanism declared in `updateMechanism`. When `updateMechanism` is `none`,
`updateAuthority` is not required.

## Values

A set of one or more of the following values:

| Value | Meaning |
| --- | --- |
| `operator` | The organisation that runs the product can install updates itself. |
| `vendor` | The manufacturer or supplier can install updates, for example by pushing them remotely. |
| `platform` | A third party, such as a connectivity provider or device-management platform, can install updates. |
| `installer` | A party with physical access to the device can install updates, for example through a local port. |

The list is fixed, so that CBOMs from different suppliers can be compared. A sector profile that
needs another value proposes it to the working group. It does not add it locally.

## Stage and naming

The answer can change between the product as built and the product as deployed. Many devices let
the operator change which parties may push updates. Following decision 0005:

- **`updateAuthoritySupported`** is the set of parties the product can be configured to accept.
  The vendor states it in the product CBOM.
- **`updateAuthority`** is the set of parties the product accepts now. In the product CBOM it is
  the default as shipped. In a deployment CBOM the operator states it as configured.

## Withholding

Who can push code to a device can be security-sensitive. A supplier may mark the attribute
`withheld` or `unknown`, under the three-state disclosure model in decision 0003. A profile that
depends on the attribute states whether withholding is permitted for it.

## Boundary

An attribute may name who can use a technical capability of the product. It may not record
commercial terms, such as support periods, service levels, prices or contract conditions.

`updateAuthority` passes this test: it describes which parties the mechanism accepts, which is a
property of the product. A support contract, or how quickly a platform operator will act, fails
it. Whether firmware will still be offered is covered separately by `updateSupportStatus`, which
states a commitment class rather than contract terms, following decision 0007.

## Related attributes

| Attribute | Question |
| --- | --- |
| `updateMechanism` | Is there a way to get new firmware onto it? (`none`, `physical-access`, `local-network`, `remote-managed`) |
| `updateAuthority` | Who can use that way? |
| `updateSupportStatus` | Will firmware still be offered? |
| `keyProvisioning`, `keyReplaceable` | Where the keys came from, and whether they can be replaced without replacing the device. |

## Still to do

- Add the definition and its values to the Terms section.
- Write the rule in the IoT profile, and decide whether it may be withheld there.
- Map it to CycloneDX 2.0 and SPDX (Publication 3).
- Add one conforming and one failing example to the IoT worked example.
