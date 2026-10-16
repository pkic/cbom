---
title: Maturity
sideMenu: true
weight: 11
aliases:
- /cbom/methodology/maturity.html
linkTitle: Maturity
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A profile sets one requirement, and a document either meets it or does not. That works for a conformance decision, but it makes adoption hard. Suppose a producer can list its interfaces this quarter, but cannot say which algorithms each one uses until it has changed its build tooling. Against a single demanding profile, that producer conforms to nothing. The answer is to publish a **family** of profiles, each asking for more detail than the one before. The methodology calls each step a depth. The first depth is within reach of most producers, the last is demanding, and a consumer can see which depth a supplier has met.

## Depth uses existing mechanisms

A family of profiles of increasing depth needs no new mechanism. Everything it needs has already been decided, and is already checked. [Profile](../profile/#composition-how-profiles-relate-to-each-other) defines extension, in which one profile is derived from another. It also defines the two kinds of extension, depth and coverage. Extension is monotonic. A derived profile may add rules and tighten the rules it inherits, but it may never relax them. As a result, a document that conforms to the derived profile also conforms to the base profile. A rule id belongs to the profile that declares it, and is cited together with that profile's tag. The same rule therefore keeps its number as a family grows. A derived profile may also sharpen an inherited group of rules in place.

A depth is therefore not a new kind of object. **A depth is a profile.** Depth adds no new field, no new artifact type and no new kind of verdict (the conformance result a validator returns). A conformance claim is the statement that a document meets a profile. A claim already names each profile it covers by identity and version, so it already states which depth was met. A conformance report already lists the rules that were assessed to reach that result. The mechanism is therefore complete. Three things are still needed. The family's shallowest profile has to exist. Producers have to be able to reach it. It has to be published as part of a family, and not as a baseline that competes with the existing one.

What depth adds is a set of working rules. Set the entry depth where a producer starting today can reach it. Order the family so that each depth contains the one below it. Require the consumer to name the depth it is asking for.

## Why these are not called maturity levels

This documentation already uses "maturity level" for something that a profile deliberately is not. [Related Work](../related-work/) describes how this methodology relates to the consortium's [PQC Maturity Model](https://pkic.org/wg/pqc/pqcmm/) (PQCMM). Both have the same subject: a product assessed from the outside. A PQCMM level is a *judgement*. An external, versioned policy derives it from the facts that a document discloses. [Policy Evaluation](../policy-evaluation/) states that such judgements are computed at the time of evaluation and are not recorded as attributes. The reason is that the criteria change over time while the product stays the same.

A profile is the other half of that arrangement. It defines the facts that the judgement reads. If both were called "maturity level", the documentation would use the phrase with two meanings, and profiles exclude one of those meanings, the judgement, on principle. This project has already had to resolve one clash of terminology. It is cheaper to settle the term now, before anyone cites the numbering.

The normative term is **depth**. A family of profiles is ordered by depth, and its shallowest member is the **entry profile**. The page keeps "Maturity" in its title because that is the word readers look for. The obvious alternative words already have other meanings in this documentation:

| Word | Already means |
| --- | --- |
| `level` | How binding one rule is: MUST, SHOULD or MAY. It is a field in every rules file. |
| `stage` | `lifecycleStage`: where the reported fact came from — intended, implemented, configured or observed. |
| `band` | The ranges of carrier (document format) versions that a profile accepts, described in [Versioning](../versioning/): target, legacy, newer, refused. |
| tier | Position in a supply chain, and a pattern of profile ownership in [Governance](../governance/). |
| maturity level | A judgement derived from disclosed facts by external policy, which a profile is not. |

## The family as it stands

The family currently has two profiles at different depths and one branch. A branch is a derived profile that serves a different decision, as explained in the next section. One test document conforms to the shallower profile but not to the deeper one.

| Profile | Asks for | Rules | Position |
| --- | --- | --- | --- |
| [Interface Enumeration](../../docs/methodology/profile-interface-enumeration.rules.json) v0.1 | What the product is, which interfaces it exposes, what each speaks and at which version, how the report was taken, and whether the list is the whole list. | P1, P3, P4, I1, I2, I7, I8 | The entry profile. No profile in the family is shallower. |
| [Interface Disclosure Baseline](https://github.com/pkic/cbom/blob/main/docs/methodology/profile-interface-disclosure.md) v0.7 | Everything above, and the algorithms for each cryptographic job, the endpoint roles, the implementing library, and a management interface or a stated reason there is none. | adds P2, I3, I4, I5, I6, I9 | One depth deeper than the entry profile. It adds six rules and shares seven rules unchanged. |
| [PQC Migration](../../use-cases/pqc-migration/) v0.6 | Per-interface capability by cryptographic purpose, what enabling it requires, and what is blocking it. | adds a group rule and its members | A **branch**, not a greater depth. See below. |

The entry profile declares each shared rule under the same id that the baseline uses for it. The gaps in the entry profile's numbering (no P2, no I3 to I6, no I9) therefore mark exactly the rules that the next depth adds. Reusing ids in this way is unambiguous because each id is cited together with a profile tag. The same rule appears in a report as `interface-enumeration#I1` at one depth and `interface-disclosure#I1` at the other, so a reader can see which profile's requirements were applied.

A document that was already in the repository shows that the entry depth is worth having. `cbom-fail` is named for the verdict the baseline gives it. It omits the management interface, so it fails product rule P2 of the baseline. It does conform to the entry profile. A producer in that position is still producing a usable document, but before the entry profile existed there was no profile for that document to conform to. At the other end, `cbom-entry-fail` conforms to neither profile. It is roughly what a scanner produces with no profile in mind. It records a TLS asset that the scanner found, and nothing about what the interface is for. The entry depth is set between these two documents. It asks for more than untargeted scanner output, and for less than the full disclosure that the baseline requires.

## Depth and branch are different relations

Depth and branch both use monotonic extension, and the extension mechanism treats them the same way. However, a family is planned and read differently depending on which of the two relations links its profiles.

**Depth** asks for more information to support the same decision. The entry profile and the baseline serve one consumer with one question: which interfaces does a published weakness reach? The two profiles differ in how much they demand before that question can be answered. Both declare orientation `inventory`. A producer moves between them by disclosing more about the same interfaces.

**A branch** serves a different decision. The migration profile is derived from the baseline, but its consumer is planning a migration, not maintaining an inventory. The migration profile therefore declares orientation `both` and asks for statements about a future state. A producer cannot reach it by disclosing more of the same facts, so a supplier at the entry depth is not two steps away from it. Suppose a branch were presented as a rung, meaning one step in the sequence of depths. Producers would then be told to work in the wrong order. Buyers would be told that a single number ranks suppliers who are in fact answering different questions.

To tell a depth from a branch, compare the derived profile with its base. If the derived profile's `objective` states the same decision and its `scope.orientation` is the same, it is a depth. If either differs, it is a branch.

This test does not identify a third relation. Two profiles can state the same decision and the same orientation and differ only in their intended audience. For example, a profile can have the same rules as another, except that the producer may no longer withhold values for the contested rules, because the recipient is bound by an agreement. [Confidentiality](../confidentiality/) explains why such a profile is published as a pair with its counterpart at the same depth, and not as the next depth up. A producer reaches it by signing an agreement, not by learning something new about its own product. Presenting it as a higher rung would place a producer that *will not tell you* on the same scale as a producer that *cannot tell you*.

A fourth relation is not a relation between profiles. An **overlay** is a profile for a document that references other documents instead of describing a subject directly. An example is an integrator's system document that cites each supplier's component CBOM by digest. It states which of each supplier's interfaces are used and how the parts connect. An overlay is neither a deeper profile nor a branch, because it does not extend the component profile. It constrains a different document, whose facts are added on top of the facts in the component documents. The substation and service-assurance entries in the [use cases](../../use-cases/) both need one. How an overlay's obligations relate to those of the documents it cites is not settled, and is recorded as Q68.

## What makes a family a ladder

A ladder is a family in which each depth contains the one below it. Publishing profiles in a sequence does not by itself make them a ladder. A family claims that a document conforming at one depth also conforms at every shallower depth. That claim holds only under the conditions in the following table.

| Condition | Why, and what goes wrong without it |
| --- | --- |
| A deeper profile drops no rule | Otherwise a document can conform to the deeper profile and fail the shallower one. Calling that profile "deeper" would then be misleading. |
| A shared rule is identical, or tightened through an `overrides` block | If two rules share an id but have different constraints, they are really two different rules. A citation of that id no longer identifies a single requirement. |
| The vocabularies a shared rule resolves against are identical | `enumRef` resolves against the profile that declares it, so the same rule text can permit different values at two depths. The difference cannot be seen by reading the rule. It is the most likely way for the profiles in a family to drift apart. |
| The disclosure marker convention is identical | If the convention differs, a marker written for one depth would not be recognised at the other. A producer's "withheld" marker would then be read as if the producer had said nothing. |
| Scope and carrier range do not widen | This follows the same rules as monotonic extension. If the deeper profile accepts a lifecycle stage or a carrier version that the shallower profile rejects, a document can conform to the deeper profile while failing the shallower one. |
| Orientation is the same | If the orientation differs, the derived profile is a branch, and the family cannot claim to be a ladder. |

When one profile declares `extends` on another, the validator already enforces most of these conditions. It refuses a profile that relaxes its base before it evaluates any document. The two profiles in this family are *siblings*, which means that neither extends the other. The baseline was published first and does not name the entry profile as its base. Re-parenting the baseline, so that it extends the entry profile, would move seven rule ids to another profile tag. That would change every citation of those ids in this documentation, in the test suite, and in any report already issued. The working group must decide whether that cost is worth paying. Until it decides, the claim that the two profiles form a ladder is an assertion about two independent profiles. Every assertion in this repository has a check, and the check for this one is `tests/check-family.py`. It requires every condition in the table of conditions. It also requires that every committed document that conforms to the baseline also conforms to the entry profile. Finally, it reports the documents that sit between the two depths. If every document conformed to every profile, the family would in effect have only one rung, whatever it declares.

## What a depth must not become

**A permanent floor.** The obvious objection to an entry profile is that suppliers will treat its floor as the most they need to supply, and stop there. Nothing in the profile itself can prevent that, and preventing it is not the profile's job. A profile states a requirement. The consumer decides which requirement to ask for. The control therefore lies in what the buyer asks for. A buyer names the profile and version it requires, and a date by which the deeper profile is required. This is the same question as the grace-window question in [Versioning](../versioning/). A conformance claim names the profile it met, so a statement that a document "conforms" always shows which depth was reached. A family makes the depth visible in this way. A single baseline profile does not.

**A floor set too high.** If the entry depth asks for too much, its floor is one that most producers cannot reach. A family of depths exists to correct that failure. This methodology was itself in that state. The shallowest profile available required nine facts about every declared interface, including the implementing library, and four facts about the product. A producer who could supply the first four of the nine facts had no way to show this, and no verdict to point to.

**A relabelling of obligation levels.** A depth is not the same as renaming the SHOULD rules of one profile. SHOULD rules and depths do different jobs. A validator reports a SHOULD rule, but the rule does not decide the verdict. A document that satisfies only the MUST rules still conforms, and nothing in the result says the other rules were expected. The requirements of a shallower profile are MUST rules, and a document that fails them does not conform. Changing a SHOULD to a MUST inside one profile changes the verdict on documents already published, even though the documents have not changed. Version discipline exists to control that kind of change. Adding a depth does not change earlier verdicts, because the deeper profile is a new profile with its own version.

**An enumeration of what comes later.** A shallower profile cannot list what deeper profiles will require, because those profiles do not exist when it is published. If the entry profile had to name them, it would have to be re-released every time the family grew. That would reverse the direction of extension, because the base profile would then depend on the profiles derived from it. The family is therefore recorded in the register described in [Governance](../governance/), not in the rules files. Each profile still states, in its `exclusions`, what *it* defers and why. That is the part of the information that a profile can carry on its own.

This creates a problem. A rules file has a single `exclusions` list. The list is used for what is excluded permanently, such as key material at every depth of every profile, and derived judgements, which are excluded on principle. The same list is also used for what is only not asked for at this depth. These are different statements to a consumer, but no field distinguishes them in a form a tool can read. The entry profile marks each of its own exclusions as "deferred, not excluded" or "permanently excluded" in prose. A reader can follow that, but a tool cannot.

## Moving to a deeper profile, and asking for one

When a family is built this way, a producer's work list is generated by the validator and does not have to be negotiated. A producer that conforms at the entry depth runs the deeper profile against the same document. The rule ids that fail are the gap between the two depths. Each item in the gap is named, and the items can be counted:

```
cbom-fail.cyclonedx.json conforms to interface-enumeration,
  and interface-disclosure#P2 stands between it and interface-disclosure
```

This line is real output from the test suite. The test suite reports the gap in the same way for the test document that exercises the disclosure states. That document falls short of the baseline only because the algorithms for one interface are missing.

The same pattern already appears inside a single profile, at the level of cryptographic purposes. The migration profile requires full detail for three cryptographic purposes, and still requires a status for all seven. As a result, a supplier cannot conform while ignoring entity authentication. A buyer also sees the blockers that take longest to resolve in the first document, not the third. A family ordered by depth applies the same idea at the level of whole profiles. The shallow depth is cheap to reach. It states openly what it does not cover, so the subjects it does not cover remain visible.

## What is not settled

| Question | What turns on it |
| --- | --- |
| Where a family is recorded, if not in its profiles | A consumer holding an entry-profile claim cannot see from the artifact that deeper profiles exist. Recorded as Q50. |
| Whether the baseline is re-parented to extend the entry profile | Re-parenting would make the validator enforce the ladder through extension, and most of the family test would no longer be needed. It moves seven rule ids to another tag and changes every citation of them. Recorded as Q51. |
| Whether a rules file should distinguish a deferral from a permanent exclusion | One field currently carries both. Recorded as Q52. |
| Whether depths are numbered, and whether a consortium profile may be published as an entry depth at all | A number invites the ranking of suppliers that this page argues against. A name is harder to demand in a contract. Recorded as Q53. |

A depth is a profile. A family is a set of profiles ordered so that each contains the one below it. Maturity, in this methodology, is the decision to publish the family with an entry depth low enough for producers to reach. The mechanism is the monotonic extension already defined in [Profile](../profile/). Depth adds two obligations: to check that the order really holds, and to name the depth when asking for one.

[← Conformance](../conformance/) [Next: Confidentiality →](../confidentiality/)
