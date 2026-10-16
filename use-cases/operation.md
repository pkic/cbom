---
title: Operation
sideMenu: true
weight: 8
aliases:
- /cbom/use-cases/operation.html
linkTitle: Operation
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

Use cases in which the CBOM is produced by the operator of a system rather than by the supplier of a product. The subject is a deployed system, a service or an estate, and what is reported is mostly configured or observed. An operator can state facts no supplier knows: what data crosses an interface and how long it must stay confidential, what was actually negotiated, which instances are still running, and what has changed since the last report.

Proposed in October 2026 as an amendment to draft decision 0023, which defined the first two groups. Not yet settled.

## What the group shares

The Disclosure and Change planning groups are each defined by the facts their profiles ask for. The Operation group is defined by who produces the document: the operator of the system. The operator can see the whole deployed system. A supplier cannot see how its product is deployed, so supplier profiles only ask for facts that can be known from the product itself. That limit does not apply to an operator, so a profile in this group can ask for more. It can require the deployment facts that the interface disclosure baseline excludes because a vendor cannot know them: the payload an interface carries, its confidentiality lifetime, the number of instances, and the configuration as observed rather than as declared.

An operator document usually draws on supplier documents rather than repeating them. It cites the supplier CBOM for each product it runs and adds what only the operator knows. A document that cites other documents and adds to them is an overlay, as defined in [Maturity](../../methodology/maturity/). The substation system document has the same relation to its component documents.

A use case belongs in this group when the operator produces the document. An operator describing what it runs may also be planning a change. A profile in this group can therefore extend either the interface disclosure baseline or the change core, which is the shared base of the change-planning profiles. Each use case decides which of the two to extend.

## Questions this group owns

| Question | Why it belongs to this group |
| --- | --- |
| Q36, Q45 | Where vendor-stated data facts end and operator-stated ones begin, and how the operator's half is linked to the supplier's document |
| Q37 | The confidentiality-lifetime bands an operator would report against |
| Q67 | Whether an estate is a subject a profile can declare, with its own completeness statement |
| Q68 | What an overlay's verdict says about the supplier documents it cites |

## Worked examples

None yet. A natural first example would reuse work already done. It would be an operator document for a Keycloak deployment. The document would cite the supplier's Keycloak CBOM from the [PQC migration](../pqc-migration/) example and add the instance count, the realm data each token interface carries, and the TLS groups actually negotiated with the directory and the database.

## The use cases in this group

### Managed and cloud service disclosure

A customer relies on a service it does not operate: an identity provider, a key management service, a payment gateway, a managed network. It has to decide whether to rely on it, and what to require of the provider. Here the producer is the operator of the service, not a vendor shipping a product. The operator knows the service's configuration and deployment, which a vendor cannot see.

A profile can therefore ask more of the operator than of a vendor. That is why this use case sits in this group. The operator can report the lifecycle stage `configured` or `observed`. It can also state facts that the product profiles leave out because they depend on the deployment. **Proposed.** So far only the consumer and the decision are named.

### Stored data and archive protection

A data owner decides which stores and archives to re-encrypt or re-wrap, and in what order. The order follows from how long the data has to stay confidential, set against the key establishment and key wrapping that protect it today. This is where harvest-now-decrypt-later exposure is most direct.

The producer is the operator, not a vendor, because only the operator knows what a store holds and for how long. The use case depends on how data is modelled alongside cryptography. That is still an open design note. **Proposed.**

### Harvest-now-decrypt-later exposure

A security function decides which of its systems are exposed to traffic recorded today and decrypted later, and which to migrate first on that ground. Exposure depends on two facts a supplier cannot state: what data crosses an interface, and how long that data has to stay confidential. Combined with the key establishment the interface uses today, these two facts give the window during which recorded traffic remains worth decrypting.

Some of these facts are known to the supplier, however. Credentials on a management interface and key material on a key-management interface follow from the interface's design, and they often have the longest lifetimes. Q36 asks where the supplier's facts end and the operator's begin. **Proposed.** Depends on Q36, Q37 and Q45.

### Migration progress over time

A migration programme lead, or a regulator receiving its reports, decides whether a migration is on track: how much has moved since the last report, how much remains, and why the numbers changed. The facts needed are two operator documents about the same estate at different dates, and the reason for each difference between them: an interface migrated, a product replaced, an instance retired, or an earlier finding that turned out to be a false positive.

Comparing two documents is covered by [Versioning](../../methodology/versioning/). This use case adds the reason for each change. Without the reason, a reader cannot tell whether a count fell because work was done or because a scanner stopped looking. Raised in member feedback on the Inventory chapter: "How much more do we have to do to be PQC ready?" **Proposed.**

### The operator's migration register

An operator records, for each finding in its estate, the decision it took: the response, who owns it, the target date and the status. These are judgements and plans. Decisions 0002 and 0007 keep them out of a supplier's CBOM, because a supplier document records facts about a product and a date there is a promise the supplier may not control.

They belong in the operator's own document about its own estate. Documents of that kind are what this group covers. CycloneDX 2.0 gives them a native home in its root `risks` list, with an owner, a response strategy, a target date and a status for each risk. **Proposed.**

[← Substation Automation (OT)](../substation/) [Next: Assurance →](../assurance/)
