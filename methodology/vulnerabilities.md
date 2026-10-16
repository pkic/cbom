---
title: Vulnerabilities
sideMenu: true
weight: 14
aliases:
- /cbom/methodology/vulnerabilities.html
linkTitle: Vulnerabilities
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A CBOM says what cryptography a product uses. Whether any of that cryptography is broken is a separate question. A different party answers it, at a different time, and the answer does not belong in the CBOM. Instead, the CBOM and the answer are linked. A profile has to require the facts that let a responder holding a CBOM match it to a security advisory. A reader must also know what a passing result does not say about safety.

## Three statements, written by three different parties

Three kinds of document describe cryptographic weakness. They are often confused with each other, because they travel together and can even share a file. The table sets out who writes each one, what it says, and when it changes.

| Statement | Written by | Says | Is revised when | Identified by |
| --- | --- | --- | --- | --- |
| **CBOM** | Whoever produces the product | This product uses these algorithms at these interfaces, and these libraries implement them | The product changes, or someone observes it more accurately | The subject it describes, plus a revision number |
| **Advisory** | A third party: a maintainer, a body that issues vulnerability identifiers, a research team | This component, in these versions, has this weakness | Knowledge changes. More versions turn out to be affected, or the analysis is corrected | A vulnerability identifier and a component identifier |
| **VEX statement** | Whoever produces the product, or someone acting on their behalf | This product is affected by that advisory, or is not, and why | Either of the two above changes, or an investigation finishes | A vulnerability identifier and a product identifier, together |

The producer writes two of the three: the CBOM and the VEX statement. This is why people tend to merge those two. They should stay separate, because they change on different schedules.

A CBOM revision records facts about a product at a moment in time, and those facts do not change until the product does. A VEX statement is a judgement about that product, made against knowledge held elsewhere. That judgement can change several times while the product stays the same. If the two are merged, the producer has to republish the whole CBOM every time a vulnerability feed is updated. If the producer does not republish, it is left holding a document that looks authoritative but is out of date in exactly the part a reader relies on most.

## Why a verdict does not belong in the document

The [Policy Evaluation](../policy-evaluation/) section already settles the general form of this. A CBOM records facts. Any judgement drawn from those facts is produced separately, by a versioned policy, at the moment someone asks. Post-quantum posture was the case that forced the rule, and the `pqcPosture` attribute was removed from the baseline because of it.

Vulnerability status is the same kind of thing and goes wrong in the same way. Saying "this interface is not affected" is a conclusion. It draws on facts the producer holds, on knowledge the producer does not own, and on criteria other people revise. Put that conclusion inside the document and it goes stale without anyone noticing. A signed and dated CBOM that says a product is unaffected is worse than one that says nothing at all, because people will believe it.

The methodology therefore applies decision 0002 to vulnerability status. **A profile does not require a vulnerability verdict, and does not permit one as an attribute.** It requires the facts from which a verdict can be worked out. This is written up as [decision 0020](https://github.com/pkic/cbom/blob/main/decisions/0020-cbom-joined-to-vulnerability-statements.md).

## Two kinds of cryptographic weakness

Joining a CBOM to an advisory works well for one kind of weakness and hardly at all for the other. An implementation defect has an advisory and an identifier to join on. An algorithm or parameter weakness usually has neither. The methodology therefore has to state clearly which kind of weakness is which.

An **implementation defect** is a bug in code that performs cryptography. Examples are a buffer overrun in a TLS extension parser, a timing side channel in an RSA decryption path, and a padding oracle. A defect like this has a version range, a patch, and an identifier in a feed. It is discovered on a particular date. The day before, the same code was running and the weakness was not yet known.

An **algorithm or parameter weakness** is not a bug at all. It is a property of a choice: SHA-1 used for signatures, RSA at 1024 bits, a static Diffie-Hellman group, or any classical key exchange once you assume an adversary with a quantum computer. The code may be flawless. There is no patch, because nothing is broken in the way a patch fixes. The remedy is to use something else, and that means changing a configuration, a protocol negotiation, or the product itself.

|  | Implementation defect | Algorithm or parameter weakness |
| --- | --- | --- |
| **Identified by** | A CVE or equivalent, against a range of component versions | Usually nothing. Guidance deprecates an algorithm, but nobody issues an identifier against a product for still using it |
| **Communicated by** | An advisory, then a VEX statement for each product | Guidance documents and national profiles, addressed to the industry rather than to any one product |
| **Remedy** | Update the component | Change the algorithm, which may mean a configuration change, a software update or new hardware |
| **Found by** | Matching the implementing library against a feed | Comparing the disclosed algorithms with current guidance, which is a [policy evaluation](../policy-evaluation/) |
| **What the CBOM does** | Narrows the search: it says which interfaces use the affected library, and what each of those interfaces is for | It is the only evidence there is |

The last row shows the main difference between the two cases. That difference determines where the working group should spend its effort.

For implementation defects, the machinery already exists and works. There are feeds, identifiers and VEX formats. A CBOM does not replace any of that. It makes the results more precise.

For algorithm weakness there is no machinery at all. No feed announces that a product signs with SHA-1. No patch arrives. A scanner that cannot tell which interface uses which algorithm cannot tell an operator what to change. A CBOM profile exists for this case. It addresses the case through disclosure rules combined with an external policy, not through anything resembling a vulnerability record.

The line between the two is not perfectly clean, and pretending otherwise would mislead. Some protocol-level weaknesses do get identifiers, because there is a specific implementation path to name. The attacks on export-grade ciphersuites and on weak Diffie-Hellman groups were issued CVEs for that reason. What never gets an identifier is the plain case: current, correct, fully patched code using an algorithm that guidance now says to stop using.

## What the CBOM contributes that an SBOM does not

Suppose an advisory is published against a cryptographic library. An SBOM answers one question. Is that library in this product, at a version in the affected range? That tells a responder whether to care. It does not tell them what to do.

A CBOM that conforms to the [interface disclosure baseline](../profile/) answers the next few questions, because its rules describe interfaces rather than components. Rule `I9` names the library implementing each interface. `I7` says what kind of interface it is. `I6` says who sits at each end. `I1` and `I2` give the protocol and its version.

Put together, a responder learns which interfaces use the affected library, whether the management interface is one of them, and whether the product initiates or accepts connections at each. Compare the two answers. "OpenSSL 3.0.7 is present somewhere in this product" has to be triaged by a person. "Three interfaces use it, one of them is the administrative login, and the product accepts connections on all three" can be acted on straight away.

Product rule `P2` matters more here than anywhere else, for a reason that has nothing to do with cryptography. The management interface is the one a responder most needs to find, and it is the one most often left out of a disclosure. A profile that only checks the interfaces a producer chose to declare can never catch that omission. This is why the baseline insists that a management interface is either declared, or that its absence is stated.

## What makes the join possible

None of the above works unless a machine can put the two documents together without a person in the middle. Three things make that possible, and the methodology already requires all three for other reasons.

-   **An identifier in a scheme the feeds also use.** Rule `I9` requires the implementing library as a Package URL, and the profile fixes that scheme rather than letting each document choose. Two disclosures about the same library can then be matched. A product name and a marketing version cannot be matched against anything. The [Formats](../formats/) section notes that provider identity is the one requirement SPDX carries natively today, through `packageUrl`, for this same reason.
-   **A lifecycle stage, so the responder knows what was described.** Rule `I8` says whether the reported state is `intended`, `implemented`, `configured` or `observed`. During an incident the responder needs the running deployment. A document describing what was built answers a different question, and may name a library the deployment never loads. A profile written for this use case should accept `configured` and `observed` and reject the other two. That is a narrowing of `scope.lifecycleStages`, and it needs no new machinery.
-   **A link from the statement to a particular revision of the document.** A [conformance claim](../conformance/) already binds a document by its digest. The same mechanism lets a VEX statement record which CBOM revision its analysis was performed against. That is what keeps the analysis checkable after the product is patched and a new CBOM is issued.

## Where the join breaks down

This use case depends almost entirely on one attribute, and that attribute is the only one the baseline lets a producer withhold. Rule `I9` is a MUST, but it carries `withholdable: true`. This means the producer may supply a `withheld` marker instead of a Package URL. The marker states that the value exists but is not disclosed. A document that does this still conforms.

For procurement, and for supply-chain disclosure generally, that is a defensible trade-off, and the working group made it deliberately. The library and its version are what a supplier is least willing to publish, as [Confidentiality](../confidentiality/) explains. If the baseline had demanded them, suppliers would have refused it outright rather than negotiated over it.

For incident response, the same trade-off defeats the purpose. A withheld `I9` leaves the responder with an interface that cannot be matched against any feed, and no other disclosure makes up for it. This has two consequences, and both are difficult to accept.

-   A profile written for vulnerability response has to remove the permission to withhold `I9`. Removing it makes the rule stricter. A profile that extends the baseline is allowed to do this, and the validator already enforces it. The [PQC migration](../../use-cases/pqc-migration/) profile does exactly this to `I9`, for a migration reason rather than an incident one.
-   Once that permission is removed, only a restricted variant of a document can conform to the profile, in the sense of "restricted" that [Confidentiality](../confidentiality/) uses. As a result, the consumer under the most time pressure is the one a public document serves least well. Worse, the responder who most needs the data is often the one with no agreement in place at all: a downstream operator reading a vendor's published CBOM in the middle of an incident. This is recorded as Q57.

## Carrying both in one document

CycloneDX allows a BOM to carry a `vulnerabilities` array, and a VEX document in that format can either stand alone or sit in the same file as the inventory it refers to. The question is not theoretical. A producer can hand over a single file holding both a CBOM and a set of vulnerability assertions, and a consumer can evaluate that file against a profile.

The methodology's position is that the two are **joined, not merged**. The rule concerns what a conformance verdict (the pass or fail result of checking a document against a profile) means. It does not restrict what a file may contain.

-   A profile neither requires nor forbids an embedded vulnerability array. A profile sets the minimum a document must disclose, not a maximum. Forbidding the array would set a maximum.
-   A profile's rules do not examine that array, and a conformance verdict says nothing about it. If a document containing vulnerability assertions passes, that means its cryptographic disclosure met the profile. It does not mean the assertions are true, current, complete, or that anyone has assessed them.
-   A consumer must not read an empty vulnerability array, or a missing one, as a statement that there are no vulnerabilities. A missing vulnerability statement means only that no statement was made. This is the same principle the [disclosure states](../terms/) apply at attribute level, where `undeclared` does not mean `none`.

The formats also differ here, in the same way that decision 0016 dealt with for conformance claims. CycloneDX can carry both in one file. SPDX 3.0.1 expresses vulnerability assessment through its own security relationships, and a CBOM referenced from an SPDX SBOM sits in a separate document altogether. A statement such as "the CBOM and the VEX are in one artifact" is therefore true in one format and false in the other. A profile must not be written in a way that depends on which format is used. This is recorded as Q58.

## Algorithm weakness has no identifier

A responder dealing with an implementation defect can cite CVE-XXXX-NNNNN in a ticket. They can suppress it with a justification, track it to closure, and show later what was decided and why. None of that is available for "this interface signs with SHA-1". There is no identifier to cite, so the finding cannot be suppressed with a reason, cannot be deduplicated across reports, and cannot be compared between tools. Two scanners will report the same problem in two ways that do not line up.

Three existing schemes are sometimes pressed into this role. None of them fits.

-   **CWE** classifies the type of weakness. CWE-327 covers a broken or risky algorithm, CWE-326 inadequate encryption strength, CWE-328 a weak hash. These are categories rather than instances. Every SHA-1 signature in an estate is CWE-328, so there is nothing there to track to closure.
-   **A clause in a guidance document**, such as a section of a national technical guideline, identifies the criterion rather than the occurrence. It also changes whenever the guidance is revised, which is exactly the instability the methodology keeps out of documents.
-   **A CVE raised against the product** is a category error, and the feeds are right to resist it. Using a deprecated algorithm in a supported configuration is not a defect in the product's code.

What the methodology offers instead is the [policy evaluation](../policy-evaluation/): a versioned, dated policy applied to disclosed facts, producing a finding that carries both the policy version and the date it was run. That is reproducible and auditable. It is still not citable the way a CVE is, because the finding is identified by the policy and the facts it was applied to, rather than by a name in a register that other people recognise. Whether that gap ought to be filled, and by whom, is Q59.

## What each kind looks like in practice

Both examples use the nginx subject that runs through this documentation.

### An advisory against a library

An advisory is published against the OpenSSL version the subject's CBOM names at `I9`. The SBOM confirms the package is present. The CBOM goes further and says three interfaces use it: the HTTPS service interface, a TLS interface to an upstream application server, and the management interface.

Rule `I6` says the product accepts connections on the first and initiates them on the second. So if the defect can only be triggered by a malicious server, the upstream interface is the exposure and the public one is not.

The producer then publishes a VEX statement. The statement is either `affected`, with a remediation, or `not_affected`, with a justification: the vulnerable code is not present, or is not in the execute path, or cannot be reached by an adversary, or is mitigated already. That justification vocabulary exists for the same reason the methodology's disclosure markers do. A negative statement is only useful if it carries its reason. None of this analysis is written into the CBOM.

### Guidance deprecates an algorithm

Guidance withdraws SHA-1 for signature generation. No advisory is published. No CVE is issued. No feed fires, and no scanner reports anything, because nothing about the product has changed.

The CBOM's `authentication` and certificate signature facts are the only record of which interfaces are affected. Running a policy evaluation across the estate's CBOMs is the only thing that produces a list. The remedy turns out to be a configuration change at one interface and a product replacement at another, and which it is can be read from the facts the CBOM discloses.

This is the case the methodology is built for, and it is the case the vulnerability ecosystem does not address.

## What a conforming CBOM does not assert

The [Conformance](../conformance/) section covers this in general terms. Vulnerabilities need separate treatment, because reading a passing result as a statement about vulnerabilities is the most common way a conformance verdict is misread.

A document that conforms to a profile does not assert that the cryptography it describes is safe, current, unaffected by any advisory, or adequate for any purpose. It asserts that the required facts were disclosed in the required form, and nothing more. A profile sets a minimum standard for reporting. Whether the disclosed facts are good news is a judgement. Someone else makes that judgement, separately, against criteria that will probably have changed by the time anyone asks again.

## What is not settled

-   **Q57.** Must a vulnerability-response profile remove the permission to withhold `I9`? If it must, is the consequence acceptable: that the most urgent consumer can only be served by a restricted variant, and that a public CBOM cannot support incident response at all?
-   **Q58.** May a conforming document carry vulnerability assertions in the same file, and does a verdict say anything about them? The draft answers yes to the first and no to the second. The difference between CycloneDX and SPDX 3.0.1 means the answer cannot be written as a constraint on the file.
-   **Q59.** Is an identifier scheme needed for algorithm-class weakness, so that a finding derived from a CBOM can be cited, tracked and suppressed the way a CVE can?
-   **Q60.** When a product is patched and a new CBOM revision is published, does anyone have to re-issue the VEX statements bound to the previous revision's digest, and whose job is that?

In short. A CBOM states cryptographic facts. An advisory states a weakness in a component. A VEX statement says whether this product is affected by it. The producer writes the first and the third, and they must stay separate, because one changes when the product changes and the other when knowledge changes. A profile requires the facts that make the join possible: a library identifier in a scheme the feeds use, a lifecycle stage saying what was described, and a digest the statement can be bound to. It requires no verdict, which is decision 0002 applied to a second kind of judgement. For implementation defects the CBOM makes existing machinery more precise. For algorithm weakness there is no machinery, no identifier and no patch, and the CBOM is the only evidence there is.

[← Policy Evaluation](../policy-evaluation/) [Next: Starting from a Use Case →](../use-cases/)
