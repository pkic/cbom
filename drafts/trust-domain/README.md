# Draft attribute: `trustDomain`

**Status:** draft, for working group review. Settles Q47 provisionally (chair's call, 11 November 2026).

## The question it answers

Whose credentials does this interface accept?

The baseline records the signature algorithm an interface uses for authentication. It does not
record whose trust anchor the interface accepts, or whether the parties holding credentials under
that anchor are open or admitted by someone. Two interfaces can declare identical algorithms and
carry very different risk:

- one accepts any certificate issued by a publicly trusted certificate authority;
- the other accepts only members that a scheme operator has admitted.

In closed-membership systems, such as settlement, payment rails and consortium PKIs, that
difference carries most of the security argument, and it is what a supervisor supervises. A CBOM
without it describes the cryptography accurately and the trust position not at all.

## Definition

`trustDomain` states the kind of trust anchor under which an interface accepts the other party's
credentials.

It is an attribute of the interface, not of the endpoint. One server often accepts different
anchors on different interfaces, for example a public certificate authority on its customer-facing
listener and a scheme anchor on its settlement link.

## Values

| Value | Meaning |
| --- | --- |
| `public` | The interface accepts credentials issued under a publicly trusted certificate authority. Anyone who can obtain such a credential can connect. |
| `private` | The interface accepts credentials issued under the organisation's own certificate authority. The organisation controls who holds them. |
| `scheme-administered` | The interface accepts credentials only from members that a scheme operator has admitted, for example the participants of a payment or settlement scheme. |

The list is fixed, so that CBOMs from different suppliers can be compared. A sector profile that
needs another value proposes it to the working group.

## Pointer to the anchor

`trustAnchorRef` is optional. It names the anchor itself, for example by the fingerprint of the
root certificate or by the scheme's identifier. A reference rule checks the pointer, not its target.

## Stage

In a product CBOM, the vendor states what the interface accepts by default, or `deployment-defined`
when the operator chooses the anchor. In a deployment CBOM, the operator states the anchor as
configured.

## Withholding

The identity of a trust anchor can be sensitive. A supplier may mark `trustAnchorRef` as `withheld`
under the three-state disclosure model in decision 0003. `trustDomain` itself reveals little, and a
profile that asks for it should normally not allow it to be withheld.

## Which profiles ask for it

- **Baseline:** optional (MAY).
- **Sector profiles,** such as a finance or payment profile, may make it a MUST. This gives such a
  profile (Q25) a place for the fact without inventing a sector attribute.

## Relation to other attributes

- **`verifierPopulation` (Q46)** says who must be able to verify a signature. An interface whose
  trust domain is `scheme-administered` usually has `scheme-members` as its verifier population.
- **`authentication`** records the algorithm. `trustDomain` records whose credentials pass it.

## Still to do

- Done: the Terms section.
- Add it as an optional attribute to the baseline rules file, with an example that carries it.
- Map it to CycloneDX 2.0 and SPDX.
