---
title: Introduction
sideMenu: true
weight: 1
aliases:
- /cbom/methodology/introduction.html
linkTitle: Introduction
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

No prior knowledge of bills of materials is assumed. A buyer asks a question about one product. The product's CBOM cannot answer it. A profile changes that, by stating which facts the CBOM must contain. Every other section expands on a step in this example.

## The problem, in one example

A vendor supplies an nginx web server and, with it, a CBOM. From that document you learn that the product uses AES-256-GCM, X25519 and RSA-2048, that it holds a server certificate for `example.com`, and that OpenSSL 3.4.0 implements the cryptography. Every statement in it is true.

```
Document A, as supplied
────────────────────────────────────────────────────────────
subject       nginx 1.27.0
interfaces    1 declared

  [1]  HTTPS service interface
       protocol          TLS 1.3
       key exchange      X25519
       encryption        AES-256-GCM
       authentication    RSA-2048
       certificate       example.com
       implemented by    OpenSSL 3.4.0

not declared  the interface an administrator logs in to
              (on this product, SSH via OpenSSH)
```

Three months later a weakness is published against a key exchange that SSH uses. The question that lands on your desk is whether this product is affected, and if it is, which of the several hundred instances you operate.

Document A cannot answer. It describes the interface that serves web traffic and says nothing about the interface an administrator connects to. The vendor was not careless. It described the HTTPS service interface accurately and in full. Nothing required it to declare the management interface as well.

A CBOM format defines what a document *may* record. It does not define what a document *must* record. A vendor that answers a request for a CBOM with Document A has complied with the format and left the buyer no better off.

Document A is not an unusual document. It is the ordinary result of asking a supplier for a CBOM without saying what the CBOM is for.

## Why asking for everything does not work

The obvious remedy is to ask for everything, and it makes matters worse. A large product performs thousands of cryptographic operations. A document listing all of them buries the two or three facts that any particular decision depends on. Covering everything does not make a document useful, and in practice no supplier would produce such a document.

There is no absolute standard of completeness for a CBOM. Completeness is relative to a purpose. The question "does this document contain everything?" therefore has no answer. The question "does it contain what this decision needs?" does have one. That second question can be answered only if the decision has first been written down in a form that a machine, and not only a person, can check.

## What a profile is

A profile is a short list of rules stating which attributes a CBOM must carry to support one stated decision, for one stated reader. It is a minimum reporting requirement. It is not a schema, and it is not a format.

### The example used throughout: the Interface Disclosure Baseline

Every profile begins by naming who reads the document and what they are deciding. Without a named reader and a named decision, there is no principled point at which to stop adding rules.

|  | The Interface Disclosure Baseline, v0.7 |
| --- | --- |
| **Reader** | An operator or purchaser holding a product it did not build and cannot inspect, keeping a cryptographic inventory across an estate. |
| **Decision** | When a weakness is published against an algorithm, a protocol version or a library, which of the deployed interfaces are affected. And, set beside the record from last quarter, what has changed. |
| **Actions** | Record the interfaces and take no further action. Act on an affected interface by reconfiguring, upgrading or isolating it. Ask the producer for a fuller disclosure. Reject the submission as insufficient to inventory. |

Naming the four actions is what allows the rest of the profile to be justified or challenged. A reader with only one available action is not making a decision. A profile written for such a reader has no test for whether it asks for the right things.

The baseline has thirteen rules, of two kinds.

### Product rules: constraints on the set of interfaces

| # | The document must | Level | Because |
| --- | --- | --- | --- |
| P1 | declare at least one cryptographic interface | MUST | A CBOM describing no interface answers nothing. |
| P2 | declare at least one management interface, or state that there is none | MUST | This is the rule Document A fails. A hardware token with no configuration surface hides nothing by not having one. A statement that there is no management interface therefore satisfies the rule. Saying nothing does not. |
| P3 | identify the subject it describes | MUST | An unidentified record cannot be matched to a deployment, or compared with the same product's record from last quarter. |
| P4 | state how complete its list of interfaces is | MUST | Otherwise a missing interface is uninterpretable. It could mean the interface does not exist, or that the producer chose not to list it. |

These four rules catch omissions, which no rule about a single attribute can do. A document can describe its service interface impeccably, pass every attribute rule, and still fail P2.

### Interface rules: constraints on each one

These apply uniformly to every interface the document declares, however many that is.

| # | Attribute | Level | What it answers |
| --- | --- | --- | --- |
| I1 | `protocol` | MUST | TLS, SSH, IPsec, and similar |
| I2 | `protocolVersion` | MUST | Which version, since an advisory usually names one |
| I3 | `keyExchange` | MUST | How the session key is agreed |
| I4 | `encryption` | MUST | What protects the traffic once the key is agreed |
| I5 | `authentication` | MUST | How each end proves who it is |
| I6 | `endpointRoles` | MUST | Who is at each end, so the interface can be located in a topology |
| I7 | `interfaceType` | MUST | One of five values, among them service, management and interconnect. P2 is checked against this |
| I8 | `lifecycleStage` | MUST | Whether the value was intended, implemented, configured or observed, which is how much weight the reader should give it |
| I9 | `implementationPurl` | MUST | Which library implements it, so an advisory against that library can be matched. This is the only rule in the profile that a producer may answer by withholding the value |

Thirteen rules is the entire profile. It is short on purpose. It names the minimum needed to support one decision and then stops. Because the profile is short, a vendor can satisfy it and a buyer can insist on it.

### What the profile does not say

No rule asks whether the cryptography is any good. Whether a product is post-quantum ready is not a fact about the product. It is a judgement made against criteria that change over time, and it is kept outside the document, in versioned [policy](../policy-evaluation/). The CBOM carries the facts. The policy reaches the verdict. The verdict is dated so that a reader can tell which criteria produced it.

## Evaluating two documents against the profile

Document A is the one above. Document B is the same product described by a supplier who declared both interfaces, the HTTPS service interface and the SSH management interface.

| Rule | Document A | Document B |
| --- | --- | --- |
| P1  at least one cryptographic interface | passes | passes |
| P2  a management interface, or a statement that there is none | FAILS | passes |
| P3  the subject is identified | passes | passes |
| P4  the interface list states its completeness | passes | passes |
| I1 to I9  on every declared interface | passes (1 interface) | passes (2 interfaces) |
| **Verdict** | **does not conform** | **conforms** |

Document A contains no false statement, and every attribute it does carry is correct. It fails because conformance is measured against what a decision needs, not against whether the statements are true. A profile exists to catch exactly this failure: an accurate document that omits the one thing its reader needs. No check based on the format alone can find it.

The [Demo](../demo/) runs both of these in the browser, along with a third: a library with no administrative surface at all, which satisfies P2 by saying so.

## The four disclosure outcomes

One refinement recurs throughout the methodology. In Document B the management interface does not name its implementing library. It carries a marker saying the value is withheld, and rule I9 accepts that, because I9 is the one rule in this profile marked withholdable.

The marker matters to the reader of the document. A withheld value is a position the producer has taken, and the reader can challenge it in a negotiation. An absent value could mean anything. For this reason the methodology distinguishes four outcomes for any attribute. The CBOM formats distinguish only two: present and absent.

| Outcome | What it says about the producer | Satisfies a MUST rule? |
| --- | --- | --- |
| **value** | It knows the value and has published it | Yes |
| **withheld** | It knows the value and has decided not to publish it | Only where the rule is marked withholdable |
| **unknown** | It does not know the value | No, but it is reported separately from an attribute that is simply missing |
| **undeclared** | Nothing was said, and the reader cannot tell which of the other three applies | No |

The first three can be acted on. The fourth can only be guessed at. A buyer who cannot tell a deliberate omission from an oversight has no basis for asking the supplier to fix it.

## Where to go next

Everything above can be understood without the rest of the documentation. The other sections expand on it.

### [Demo](../demo/)

*interactive*

Review the example documents and open the interactive source demo to see each rule resolve, including the four disclosure outcomes.

### [Overview](../)

*map*

What each section covers, and three suggested routes through the material depending on why you are here.

### [Challenges](../challenges/)

*background*

Why CBOMs behave the way Document A did, and what SBOM adoption already established about it.

### [Method](../method/)

*procedure*

The twelve steps for defining a profile, if you are here to write one rather than to read one.

[Terms](../terms/) is a glossary and sits in the Reference group. Use it to look up an unfamiliar word. It is not intended to be read first.

This documentation works a single example, an nginx web server expressed in CycloneDX 1.7, all the way through. The material is illustrative and demonstrates the methodology; it is not a normative deliverable of the PKIC CBOM Profiles Working Group.

[Next: Overview →](../)
