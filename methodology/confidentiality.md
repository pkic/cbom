---
title: Confidentiality
sideMenu: true
weight: 12
aliases:
- /cbom/methodology/confidentiality.html
linkTitle: Confidentiality
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A CBOM says where a product's cryptography is and what it is made of. That information is useful to an operator, and for the same reasons it is useful to an attacker. It can also be commercially sensitive. Most producers will therefore have two documents about one product: one they publish, and one they release only under an agreement. The questions are how the two documents relate, how a profile reflects the difference, and what a consumer can tell from the document it holds.

## Two documents, one product

A CBOM can exist in two **variants**. The variants are distinguished by who may hold them rather than by what they contain.

| Variant | Who receives it | What governs what it contains |
| --- | --- | --- |
| **Public variant** | Anyone who asks. The audience is unbounded, cannot be enumerated afterwards, and the release cannot be revoked. | The producer's disclosure policy. There is no counterparty to negotiate with. The minimum content (the floor) is set by whichever profile the producer wants to be able to claim conformance to in public. |
| **Restricted variant** | A named recipient on stated terms: a customer under a non-disclosure agreement, an auditor, a regulator, a supply-chain partner. | The agreement, and the profile the recipient asked for. Because the producer knows who holds the document and on what basis, it can agree to a higher floor, meaning a more demanding profile. |

There can be more than two variants. In principle there could be any number of levels. In practice there are a small number of tiers, because every additional tier is another document that has to stay consistent with the others. Both variants are extracts, in the sense [Inventory](../inventory/) uses. The inventory is the asset, and a CBOM is a scoped, filtered, redacted snapshot taken from it for a particular consumer. The two variants come from the same extraction, run at two redaction settings. The difference between the variants should be introduced at that step and nowhere else. A public variant produced by editing a restricted one by hand is a third document with no source in the inventory.

## Other meanings of confidentiality and disclosure

The word "confidentiality" already has another use in this documentation. The two uses are easy to confuse, because both concern secrecy and both affect what is disclosed.

| Term | Already means |
| --- | --- |
| confidentiality lifetime | How long the data crossing an interface must stay secret. It is a property of the *traffic*, proposed as `confidentialityLifetime` in [Data Exposure](../data-exposure/). It determines how urgent the harvest-now-decrypt-later threat is. |
| disclosure | What a producer tells a consumer about the product: the four [disclosure states](../profile/#disclosure-states), and the Interface Disclosure Baseline named after them. |
| confidentiality, here | The protection of the CBOM *document*: who may hold it, and what it therefore may contain. |

The normative terms on this page are **variant**, for one of the documents, and **audience**, for the parties who may hold it. The title "Confidentiality" is kept because that is the word readers look for.

## Redaction is declared, never performed silently

This principle is settled, and everything else on this page depends on it. Decision 0003 established that an attribute with no value carries a marker saying *why* it has none. [Profile](../profile/#disclosure-states) sets out the four possible outcomes. For a pair of variants, the principle has one important consequence: **a public variant is not a smaller document. It is the same document with values replaced by markers.**

| Two ways to redact | What the recipient sees |
| --- | --- |
| **By deletion.** The attribute is simply not there. | `undeclared`. The attribute fails the rule, and its absence indicates that the document was not built against the profile. The recipient cannot tell whether the attribute is missing because of a policy decision, a limitation in the producer's tooling, or an oversight. |
| **By marker.** The attribute carries `withheld`. | The recipient learns that the fact exists, that the producer holds it, and that the producer is not releasing it on these terms. Where the profile permits withholding, the marker satisfies the rule. The document can therefore conform while redacting. |

This approach has a cost, which the methodology accepts deliberately. A marker confirms that the information exists. For example, a producer withholding `implementationPurl` has confirmed that it knows which library implements the interface. The methodology treats that confirmation as information the consumer is entitled to. It tells a buyer that there is a conversation to open with the supplier, rather than a gap to write off. The alternative is to leave the attribute out with no marker, and a document that does so does not conform.

## A profile sets a floor and cannot set a maximum

No type of rule in this methodology fails a document because it contains *more*: more attributes, more interfaces, or more detail than the rule asked for. Every count in the constraint vocabulary is a minimum (`minCount`, `minInterfaces`, `minInterfacesOfType`, `minProviders`). There is no maximum of any kind. A profile therefore cannot say "do not disclose X". This is deliberate, for three reasons.

-   **It would break monotonicity.** Monotonicity is the property that a document conforming to a derived profile also conforms to its base. It holds because extending a profile can add or tighten rules but never relax them. A rule that sets a maximum could not be tightened by a deeper profile. A document could then satisfy the derived profile while failing the base, because it contained something extra. Conformance would stop being monotone in the document as well as in the profile.
-   **It is outside the methodology's scope.** A profile is a minimum reporting requirement. What a producer may not say is a matter for its own policy and for the contract it is disclosing under. A reporting standard that told producers what to conceal would be a different instrument.
-   **It would be unenforceable by the party that wants it.** The consumer holds the document and runs the evaluation. A producer cannot rely on a consumer's validator to protect the producer's secrets.

Confidentiality is therefore controlled where the document is produced, in the *select · filter · redact* step described in [Inventory](../inventory/). The profile is the acceptance test applied when the document is released. A profile can still express its side of the decision. It cannot say "this must not be disclosed". It can say "this rule may be satisfied by a marker".

## Reflecting the difference in a profile

Each rule has a `withholdable` setting. When it is true, the rule accepts a `withheld` marker in place of a value. The negotiation over confidentiality is settled through this setting. Decision 0003 states this directly: deciding withholdability for each rule is a substantive negotiation between producers and consumers rather than a formatting detail. One rule set can therefore produce two profiles:

-   a profile whose sensitive rules are `withholdable` is one that a lawfully redacted **public** variant can satisfy;
-   a profile that permits no withholding on those rules is one that only a **restricted** variant can satisfy.

Removing withholdability from a rule is a tightening, and the validator already treats it as one. The validator refuses an override that makes a non-withholdable attribute withholdable, because that would relax the rule. It accepts and records the reverse. **The restricted profile is therefore a derived profile of the public one**, and the pair needs no new machinery at all. Conformance to the restricted profile carries conformance to the public one. A consumer gains two things from this. A supplier's restricted disclosure is never *less* acceptable than its public one. A consumer holding a conformance claim against the restricted profile also does not have to re-evaluate the document against the public profile to know where it stands.

The migration profile already uses this pattern. It tightens the baseline profile's `implementationPurl` rule in exactly this way:

```
{
  "id": "interface-disclosure#I9",
  "level": "MUST",
  "withholdable": false,
  "note": "Tightened by removing withholdability. The base already requires
           implementationPurl at MUST and accepts a 'withheld' marker in place
           of a value. Migration sequencing depends on knowing which library
           implements an interface, so this profile removes that option and
           requires the value itself. Level is restated as MUST for readability
           and is unchanged from the base."
}
```

That is the block as it stands in `profile-pqc-migration.rules.json`, with the note wrapped to fit.

The migration profile removes withholdability for a migration reason, not because of who will receive the document. The mechanism does not distinguish between the two reasons. That makes it convenient for building a restricted profile.

### The restricted profile derives from the public one

The *public* profile is the base, and the *restricted* profile derives from it. Documents get smaller as the audience widens. Profiles get larger as the audience narrows. A reader may expect the confidential profile to be the complete one, with the public profile as a cut-down version of it. That reader has the direction of derivation reversed. Such a reader would write an extension that adds withholdability. Adding withholdability is a relaxation, and the validator refuses it before it evaluates any document.

## Audience is a third relation, beside depth and branch

A derived profile can relate to its base in more than one way. [Maturity](../maturity/) gives a practical test. If the derived profile's `objective` states the same decision and its `scope.orientation` is the same, it is a greater *depth*: it asks for more about the same decision. If either differs, it is a *branch*: it answers a different question. A restricted variant profile has the same consumer, the same decision and the same orientation, so it passes the test for depth. It is nevertheless not a depth. Audience is a third kind of relation.

| Relation | What differs | What moves a producer | What a buyer should read into it |
| --- | --- | --- | --- |
| **Depth** | How much is asked about the same decision. | Engineering: instrumenting a build, extending a scanner, learning something about its own product it did not previously record. | How far the supplier's own visibility reaches. |
| **Branch** | The decision itself, and usually the orientation. | Answering a different question. | Nothing that allows comparison. Two suppliers on different branches cannot be ranked against each other. |
| **Audience** | Who may hold the document. | A signature on an agreement. No engineering change is involved, and none is implied. | What the supplier will say *to this recipient*, which is not the same as what the supplier knows. |

Audience must be kept separate from depth, for a reason the methodology has already settled elsewhere. *Cannot tell you* and *will not tell you* are different findings. For a single rule, the disclosure states keep them apart. `unknown` and `withheld` are reported separately and listed separately in a conformance claim, because an unknown value points at the producing process and a withheld one points at a policy. Suppose a profile family presents an audience step as the next level of depth. It merges the two findings again, this time across a whole profile. It would rank a supplier that is contractually barred from naming a library below a supplier whose scanner cannot see hardware cryptography, or the reverse. The ranking would depend only on how the levels were ordered. Both conditions may also be true of the same supplier, for different rules, in the same document.

This affects how the pair of profiles is published and requested. An audience step is published as a *pair at one depth*, not as the level above. A consumer's requirement names two things separately: which profile it requires, and on what terms it will receive the document.

## What a profile cannot yet say

Nothing in a rules file records which audience its withholding permissions were set for. Suppose two profiles have an identical rule set, but one was drafted as a public floor and the other as a restricted floor. As artifacts, the two are indistinguishable. Today a public profile and a restricted profile are told apart only by their titles and their descriptive text.

The obvious fix is to declare the audience in the profile. However, the declaration cannot go in the `disclosure` block. C7 requires an inherited block to be identical along a chain of derived profiles. The stated reasoning is that `disclosure` and `conformanceKeywords` carry no requirement of their own, so any difference between a base and a derived profile can only be a mistake. A test fixture covers this case. A derived restricted profile that declared a different audience in that block would therefore fail C7. The failure would be correct by the letter of the check but wrong by its intent. `scope` is the more plausible place for the declaration. Scope already narrows along a chain, and C11 already checks it. The audience a profile is written for is also part of the boundary that scope draws.

The mechanisms described in the earlier sections work with the tooling as it stands. The audience declaration discussed in this section does not: no schema, checker or validator has a concept of audience. The distinction is kept sharp deliberately, because the value of the existing mechanism is that tooling already checks it. Recorded as Q54.

## What the document says about itself

A recipient should not have to guess which variant it holds. Today it may have no way to find out. A public variant in which the producer happened to redact nothing looks exactly like a restricted one. Two documents with the same subject and different digests give no explanation of why they differ. Declaring the variant at product level would close this gap. The variant would be a fact about the document, of the same kind as P3's subject identity and P4's completeness statement. It could be expressed with the product-rule machinery that already exists.

A related defect should be handled separately. P4 requires a completeness statement from a three-value vocabulary: `all-external`, `all`, `partial`. The value `partial` has two meanings. It can mean "we did not enumerate everything", and it can mean "we are not telling you about everything". The first is a matter of ignorance and the second is a matter of policy. The four disclosure states exist to keep these apart for individual attributes. The completeness vocabulary merges them again for the document's structure as a whole. A buyer reading `partial` cannot tell whether to press the supplier about its tooling or to open a commercial conversation. Decision 0003 was taken to avoid exactly this loss of information. Recorded as Q55.

## Withholding structure

Markers apply to attributes. If an interface is left out for confidentiality, there is no attribute on which to place a marker. Yet structure, meaning which interfaces a document lists, is where the two variants most often differ. It is easier to argue that a management interface should not be advertised than that a protocol version should not be.

Today a producer has an honest option in two of the following situations and no honest option in the third.

| Situation | What the producer can do |
| --- | --- |
| An interface may be named but its detail may not | Declare the interface and withhold the attributes the profile permits withholding. The preferred shape: the count stays honest and the recipient sees what exists. |
| An interface may not be named at all, and no product rule requires its kind | Omit it and state `coverage: partial`. The document conforms, but the reason for the omission is lost (see "What the document says about itself"). |
| An interface may not be named at all, and a product rule requires its kind | No honest option. P2 is satisfied either by declaring a management interface or by stating an absence from `no-configuration-surface`, `configured-out-of-band`, `not-applicable-to-subject`. None of those means "exists, and is not disclosed". The producer must disclose the interface, state something untrue, or fail the rule. |

The last row shows a gap in how the disclosure model's own reasoning has been applied. P2 was revised in baseline v0.6 so that a subject with nothing to hide could say so rather than fail. The reasoning was that a rule which a legitimate subject cannot satisfy honestly is wrong, not strict. The same reasoning applies to a subject that has something it is not permitted to say. However, allowing a structural rule to be satisfied by a declared withholding has a cost. `minInterfaces` and `minInterfacesOfType` would become lower bounds on the *declared* set of interfaces rather than on the product. That is a weaker statement than they make today. The change would also give a producer a way to satisfy a structural rule without declaring anything. Recorded as Q56.

## What the two variants owe each other

The following obligations fall on the producer. No artifact in this repository can check them, and a consumer holding only one variant cannot test them. They are written down for that reason.

| Obligation | Why |
| --- | --- |
| One subject, one revision | Both carry the same subject identifier and the same content revision. They describe one product at one moment. A variant is not a new observation of the product. If the two documents disagree about the product, the difference is not a redaction. |
| A redaction and nothing else | Every value the public variant carries is the value the restricted one carries. Redaction replaces a value with a marker. It does not change a value, and it does not add one. If values differ, the two documents are separate accounts of the same product rather than variants. The public one circulates freely, and nobody has checked it against the restricted one. |
| One source | Both are extracted from the inventory at two redaction settings. Neither is produced by editing the other. Two separate pipelines drift apart over time. The drift appears as a breach of the previous obligation, usually months later, when an auditor holds both variants. |
| Both signed | Signing both lets a recipient holding both establish that they agree and that both come from the producer. It also means that a restricted variant which leaks can be attributed to its producer. See [Governance](../governance/). |
| A variant is not a version | [Versioning](../versioning/) tracks three axes: carrier format, profile, and content revision. Audience is not one of them. Distinguishing variants by revision number makes a public document issued on Tuesday look like a correction of the restricted one issued on Monday. |

## What a claim already reveals

A conformance claim binds to one document by digest and lists, for each profile evaluated, the rules whose values were `withheld`, `unknown` and `undeclared`. Two claims for the same subject with different digests and different withheld lists therefore *are* the two variants. No new field and no new vocabulary are needed to tell them apart. The difference between the two withheld lists is the redaction, named rule by rule.

A claim does not record the audience the document was prepared for. It also gives no indication that a fuller variant exists. Suppose a buyer compares two suppliers on the verdict alone, and one supplier provided a public document while the other provided a restricted one. The buyer finds the two equal. [Conformance](../conformance/) already warns that a consumer acting on the verdict alone discards the part of the result most likely to matter commercially. The variant pair is the clearest example of that warning. Both documents conform and neither producer has done anything wrong, but only one of them has answered the buyer's question.

## What confidentiality is not a reason for

**Dropping the marker.** Silent redaction produces `undeclared`. That fails the rule, and it tells the recipient that the document was not built against the profile. A producer that will neither disclose a value nor admit to holding it has chosen the one option that costs it conformance.

**Publishing nothing.** "We cannot publish our library versions" is an argument about one rule, not about the document. The entry profile in [Maturity](../maturity/) exists so that there is a bar low enough to be reachable, and the interfaces a product exposes, the protocols they speak and the versions of those protocols are not usually the sensitive part.

**A floor set to nothing.** If every contested rule in the public profile is withholdable, a conforming public variant answers no question. The public profile then exists in name only. The test is the same one that every profile already has to pass. State the consumer's decision and the options it chooses between. Then check that a conforming document still discriminates between those options, even when it uses every withholding the profile permits.

**Excluding secrets.** Key material, private keys and seeds are outside every profile at every depth and in every variant. That exclusion is permanent and is not a confidentiality decision. It is also not the purpose of a restricted variant. A restricted variant contains the library versions, not the keys.

## One document is not the exposure

The argument against publishing a CBOM is rarely about one CBOM. A single product's document describes what its datasheet and its release notes largely describe already. The exposure comes from combining documents. A profile exists to make documents correlatable through shared identifier schemes. When the documents for a whole estate are correlated in this way, the result is a list of targets ordered by weakness. That combined artifact is the inventory. This is why [Inventory](../inventory/) treats the inventory as the asset and the CBOM as an extract from it. It is also why a distributed inventory is a confidentiality arrangement as much as an organisational one.

The second exposure comes from comparing documents over time rather than combining them. Two public variants of consecutive releases disclose what changed between them. A producer that publishes a CBOM on every release therefore announces its own cryptographic fixes, whether or not it intends to. This includes fixes it has not otherwise announced, and the announcement comes before its customers have deployed them.

A profile cannot address either exposure. It cannot make a disclosed fact less true, and each fact involved is harmless on its own. Both exposures are questions of distribution and retention. They belong with the registry access control and the immutable-revision arrangement in [Governance](../governance/). They are recorded here because they are the reason producers give for refusing to publish at all. A methodology that only ever argues for more disclosure will not be believed on this point.

## What is not settled

| Question | What turns on it |
| --- | --- |
| Whether a profile declares the audience its withholding permissions assume | Two profiles with identical rules and opposite intentions are indistinguishable as artifacts, and the `disclosure` block cannot carry it without breaking C7's reasoning. Recorded as Q54. |
| Whether a document declares which variant it is, and whether the completeness vocabulary separates ignorance from policy | A recipient cannot always tell which document it holds, and `partial` carries two opposite meanings. Recorded as Q55. |
| Whether a structural rule can be satisfied by a declared withholding | A product whose management interface is confidential has no honest way to conform. The change would weaken what an interface count asserts. Recorded as Q56. |
| Whether a withheld answer must say why | Already recorded as Q12. A stated reason turns a refusal into a starting point for the buyer: a contractual bar, a commercial sensitivity and a security concern about naming an exact version call for three different responses from the buyer. |

In summary, a public and a restricted variant are one document redacted in two ways. The redaction is declared with markers rather than performed silently. A profile reflects the difference through which rules are withholdable. That makes the restricted profile a derived profile of the public one, and no new machinery is needed. What is missing is labelling. Nothing yet records which audience a profile was drafted for, or which variant a document is. A profile family must also not present an audience step as a level of depth. *Cannot tell you* and *will not tell you* are different answers, and the methodology keeps them apart everywhere else.

[← Maturity](../maturity/) [Next: Policy Evaluation →](../policy-evaluation/)
