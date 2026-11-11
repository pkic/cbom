# Draft attribute: `verifierPopulation`

**Status:** draft, for working group review. Settles Q46 provisionally (chair's call, 11 November 2026).

## The question it answers

Who must be able to verify this signature?

A signed message is often verified by many parties, not one. A settlement instruction is verified
by every member of a payment scheme. A software release is verified by every customer. In both
cases the weakest verifier sets the limit on what the signer can use. The signer cannot move to a
post-quantum signature until the whole population can verify it.

A migration planner needs to know this, because it decides whether a change can be made by the
supplier alone or needs coordination across a scheme or a customer base. The model's taxonomy has
no row for one signer with many verifiers who do not verify at the same time, so today the case is
neither described nor recorded as a limitation.

## Definition

`verifierPopulation` names the set of parties that must be able to verify signatures produced on
an interface.

The relationship stays between two parties: the signer and a verifier. The attribute adds a fact
about how many verifiers stand behind that second party. It does not change the definition of a
relationship, which is binding under N02.

It applies only where the interface's cryptographic purpose is `entity-authentication`,
`data-integrity` or `non-repudiation`.

## Values

| Value | Meaning |
| --- | --- |
| `counterparty` | One known party verifies. This is the usual case, for example a TLS server certificate checked by a connecting client. |
| `scheme-members` | Every member of a defined membership verifies, for example the participants of a payment or settlement scheme, or the members of a consortium PKI. |
| `public` | Anyone may verify, for example the customers of a signed software release. |

The list is fixed, so that CBOMs from different suppliers can be compared.

## Pointer to the rules that set the minimum

`verifierPopulationRef` is optional. It points to the document that sets what the verifiers must
support, such as a scheme rulebook or a published verification policy. It works the same way as the
existing roadmap pointer: the CBOM records where the rules are, and does not copy them. A reference
rule checks the pointer, not its target.

## Withholding

A supplier may mark either attribute `withheld` or `unknown`, under the three-state disclosure
model in decision 0003. A profile that asks for the attribute states whether withholding is
permitted.

## Which profiles ask for it

- **`pqc-migration-extended`:** SHOULD. The value `scheme-members` or `public` tells the planner
  that a change of signature algorithm needs coordination beyond the supplier.
- **Baseline and `pqc-migration`:** not required.
- **Sector profiles,** such as a finance profile, may make it a MUST.

## Relation to other questions

- **Q08** (a key shared among many parties) stays out of scope. This attribute needs no shared key
  and no change to the model, which is why it costs much less.
- **Q47** (an interface that trusts a closed, administered membership) is separate. The value
  `scheme-members` gives it a natural starting point.

## Still to do

- Done: the Model section's taxonomy and known-limitations text, and the Terms section.
- Add the SHOULD rule to `profile-pqc-migration-extended.rules.json`, with one example that carries
  the attribute and one that fails it.
- Map it to CycloneDX 2.0 and SPDX.
