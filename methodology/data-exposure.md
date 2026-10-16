---
title: Data Exposure
sideMenu: true
weight: 18
aliases:
- /cbom/methodology/data-exposure.html
linkTitle: Data Exposure
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

An adversary who records encrypted traffic today can decrypt it once a cryptographically relevant quantum computer exists. This is the harvest-now-decrypt-later threat. The exposure it creates is not visible in the cryptography a CBOM currently discloses. It also depends on how long the data must remain confidential, and on whether the traffic can be captured at all. Assessing the exposure needs further facts, and those facts belong partly to the supplier and partly to the operator.

Illustrative. The attributes proposed here are a draft for working group discussion. They are not part of the example profiles. They depend on a decision about scope: which kind of CBOM the attributes belong in. That decision is recorded as an open question.

## What makes this threat different

Most cryptographic risk is prospective: it affects traffic sent in the future. A weakness discovered in an algorithm affects the traffic protected by that algorithm from that point forward. The remedy is to stop using the algorithm. The harvest-now-decrypt-later threat is retrospective: it affects traffic already sent. Traffic captured and stored today is decrypted years later, when the capability arrives. Here the capability means a cryptographically relevant quantum computer. No action taken at that point can restore the confidentiality of data that has already been recorded.

As a result, the decision to migrate has to be taken before the capability exists. The time in which that decision still makes a difference is running out. Meanwhile, the estimate of when the capability will arrive remains uncertain. An organization that waits for confirmation will already have lost the confidentiality of the traffic it was protecting.

The threat therefore does not affect all data equally. Data that ceases to be sensitive within a year is largely unaffected, because a recording made today has little value by the time it can be read. Data that must remain confidential for decades is exposed now, regardless of the algorithm protecting it, if that algorithm is one a quantum computer will break.

## Why the cryptography alone does not answer the question

Consider two interfaces on two products. Both terminate TLS 1.3, both negotiate X25519 for key exchange and AES-256-GCM for encryption, and both authenticate with an RSA-2048 certificate. For every attribute that the baseline profile (the Interface Disclosure Baseline) requires, the two interfaces are identical. Yet their exposure to this threat is very different.

{{< figure src="../assets/figures/methodology-data-exposure-1.svg" alt="Two panels showing interfaces with identical cryptography. The left carries a public status page over the internet with a confidentiality lifetime under one year and low exposure. The right carries clinical records over the internet with a lifetime over fifteen years and high exposure" >}}

*Every attribute the baseline profile requires is identical across the two interfaces. What separates them is a property of the data, which no current profile records.*

## The three quantities

The assessment comes down to comparing three periods of time. This formulation is due to Mosca. Two of the periods describe the organization. The third describes the outside world.

| Quantity | Meaning | Known by |
| --- | --- | --- |
| **Confidentiality lifetime** | How long the data carried must remain confidential after it is transmitted | The data owner, which is the operator and not the vendor |
| **Migration time** | How long it takes to move the interface to quantum-safe cryptography | Derived from what the vendor's product can support and from the operator's capacity to make the change. The migration profile records the vendor's part |
| **Time to capability** | How long until a cryptographically relevant quantum computer exists | Nobody. It is an estimate that changes with published research and national guidance |

Suppose the confidentiality lifetime plus the migration time is greater than the time to capability. Then data being transmitted now will be readable before it stops being sensitive. The organization is already exposed, and the exposure grows with every day the interface continues to operate.

The methodology supplies the migration time through the migration profile. That profile records what is needed to reach a quantum-safe capability and what is blocking it. The methodology supplies nothing for the confidentiality lifetime. The proposals on this page are intended to fill that gap.

## Two kinds of data, with different owners

Which party can state these facts depends on the kind of data an interface carries. Different interfaces carry different kinds of data, so the answer differs from one interface to another.

**Conveyed payload** is whatever the customer chooses to send. A vendor shipping a device does not know what that will be. The same product may carry public information at one site and long-lived personal records at another. If the vendor is required to classify the payload, the vendor will either refuse or guess. A guess is worse than a refusal, because consumers will rely on it.

**Intrinsic data** is what an interface must carry to function, and the vendor knows precisely what it is because the vendor designed the interface. A management interface carries administrative credentials. A key management interface carries key material. An update channel carries a signed image and the signature verifying it. An enrolment interface carries device identity and private key material.

| Interface | What it necessarily carries | Stated by |
| --- | --- | --- |
| Management or control | Administrative credentials, configuration secrets | The vendor |
| Key management | Key material, wrapped or in the clear | The vendor |
| Firmware or software update | Signed images, and the verifying signature | The vendor |
| Enrolment or provisioning | Device identity, private key material | The vendor |
| Application data plane | Whatever the customer sends | The operator |

### The intrinsic case carries the worse exposure

Of the two kinds of data, intrinsic data carries the greater exposure. This is the kind the vendor can describe.

Take a management session protected by a classical key exchange, carrying a device credential. An adversary records the session now and decrypts it in 2035. If that credential is a certificate with a twenty-year validity, or a key held in hardware that cannot be rotated in the field, the adversary does not obtain stale information. It obtains a working secret. The confidentiality lifetime of that payload equals the lifetime of the credential, and the vendor knows that lifetime because the vendor chose it.

Ordinary business information loses sensitivity as it ages, which is what makes short confidentiality lifetimes tolerable. Credentials and key material do not lose sensitivity in this way, and may still be live when the recording is read. A model that accepts only facts stated by the operator leaves out intrinsic data. Intrinsic data is the half of the problem where the consequences are most serious.

## Where each fact belongs

[Lifecycle Data](../lifecycle/) separates a **product CBOM**, describing what a vendor ships, from a **service or deployment CBOM**, describing what an operator runs in a particular configuration. The proposal is that intrinsic data is declared in the product CBOM and conveyed payload in the service or deployment CBOM. Each fact is then stated by the party that is able to state it. The methodology applies this same test everywhere: a fact is recorded by the party that knows it.

This point is open and is recorded as Q36. An earlier draft of this page placed all facts about data at deployment scope, meaning in the deployment CBOM, on the grounds that a vendor cannot know them. That is right for payload and wrong for intrinsic data. The working group needs to decide where the boundary between the two kinds of data falls. Some interfaces are close to that boundary. For example, a database connection carries payload in general, but carries credentials when the session is established. The options are set out in `design-note-data-and-hndl.md`.

## Proposed attributes

The attributes in the table are candidates for a deployment-scope profile, that is, a profile that applies to the deployment CBOM. Their names follow the conventions in [Method](../method/). Each attribute records a fact that the operator can state. None of them records a judgement about the result of the assessment.

| Attribute | What it records | Notes |
| --- | --- | --- |
| `confidentialityLifetime` | How long the data carried must remain confidential | Recorded in bands: under 1 year, 1 to 5 years, 5 to 15 years, over 15 years, indefinite. A band is a fixed range of time. Bands can be compared between organizations. Specific durations and classification labels cannot. The assessment depends on this attribute |
| `exposure` | Where the traffic runs | From a controlled vocabulary: `public-internet`, `partner-network`, `private-network`, `physical-local`. The value determines whether large-scale interception of the traffic is plausible |
| `dataClassification` | The operator's own classification of the data | Optional. The value names the classification scheme it is drawn from. Classification labels are not comparable between organizations or jurisdictions. This attribute is therefore useful within one organization, but its values cannot be combined across suppliers |
| `retentionAtRest` | Whether ciphertext is stored, and for how long | The threat applies to stored ciphertext as much as to captured traffic. A backup or archive interface may carry the higher exposure. It is also easier to overlook, because it is not a network connection |

`confidentialityLifetime` is the most valuable of the four attributes. If the working group adopts only one attribute from this list, it should be `confidentialityLifetime`. It supplies the quantity that the comparison needs. The other attributes add detail to that quantity but do not supply it.

### Why bands are used instead of dates

A date suggests more precision than the answer has. An operator asked how long clinical records must stay confidential will reasonably say decades. A profile that demands a date will get either an invented date or an empty field. Bands can also be counted across interfaces. A migration programme wants to know how many interfaces fall in the longest band. That question can be answered across suppliers only if every supplier uses the same bands.

## What stays outside the CBOM

The date at which a cryptographically relevant quantum computer is expected is not a fact about any product, and no CBOM should record it. It is an estimate that changes with published research and with national guidance. A document that included the estimate would look authoritative, but the estimate in it would be wrong within a year.

[Policy Evaluation](../policy-evaluation/) describes how such an estimate is handled. The estimate is an input to an external policy that carries its own version number. Applying the policy produces an urgency ranking. The ranking is a derived judgement. It is calculated when someone asks for it, and it records the policy version and the date the policy was applied. The methodology already handles post-quantum posture in the same way. The mechanism therefore already exists, and nothing new is needed.

| Held in | What it carries |
| --- | --- |
| Deployment CBOM | Algorithms in use and supported, confidentiality lifetime, exposure, retention |
| External policy | The estimated arrival of the capability, and the thresholds that define urgency |
| The evaluation | An urgency ranking across interfaces, dated, citing the policy version |

## Storage as well as transit

Discussion of this threat usually assumes that traffic is captured on the network, and that case is easier to see. Stored ciphertext is exposed in the same way, and an adversary can reach it more easily. An adversary that obtains a backup already has the recording, without needing to intercept anything. The model already covers storage interfaces. The `storage` value in the interface type vocabulary exists for them. A deployment profile addressing this threat should require them to be declared, and the `retentionAtRest` attribute is where the duration is recorded.

## Open points

-   Where the boundary falls between intrinsic data, declared in the product CBOM, and conveyed payload, declared at deployment scope (Q36). The other proposals on this page depend on this decision.
-   Where the band boundaries fall. The values above follow the periods that appear in published migration guidance, and the group may prefer others.
-   Whether `dataClassification` should be included. Its values cannot be combined across organizations, and the classification schemes it draws on are not public.
-   Whether storage interfaces need attributes of their own beyond retention.
-   Whether a deployment-scope profile should be written as an extension of the interface disclosure baseline or as an independent profile. The composition rules in [Profile](../profile/) permit either.

The cryptography an interface uses is not sufficient to assess this threat. The missing information is a property of the data. Which party can state it depends on the kind of data. The vendor knows what an interface must carry in order to function. Only the operator knows what is sent across it. Each fact should be recorded at the scope where it is known, and the threat estimate should be left to external policy. Every fact in the document can then be verified by the party that stated it.

[← Formats](../formats/) [Next: Versioning →](../versioning/)
