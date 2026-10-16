---
title: Profile
sideMenu: true
weight: 9
aliases:
- /cbom/methodology/profile.html
linkTitle: Profile
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

This profile is product-independent. Its rules are structural: they say which categories of interface must exist, and what each one must disclose. Written that way, they apply to any product. No rule names a specific product or a specific interface instance.

A profile must not bind a rule to a specific product or interface. An earlier draft incorrectly required `interfaceId` to equal `"nginx-https"`. Rules instead constrain the set of interfaces and the attributes of each interface.

## Two directions of use

The profile contains one attribute table. Two different parties use that same table for two different purposes.

{{< figure src="../assets/figures/methodology-profile-1.svg" alt="A central Profile box holding one attribute table, with an arrow from a producer labelled specification and an arrow to a consumer labelled checklist" >}}

*The profile serves as a specification for the party that generates the CBOM and as a conformance checklist for the party that consumes it.*

## Three kinds of rule

{{< figure src="../assets/figures/methodology-profile-2.svg" alt="A product outline for nginx 1.27.0 containing two interface cards, an HTTPS service interface and an SSH management interface, each giving its protocol, library and endpoint roles" >}}

*Product rule P2 requires at least one `management` interface. Omitting the management interface, as the non-conforming CBOM does, fails rule P2 even when the service interface is fully described.*

### Product-level rules (constraints on the set of interfaces)

| # | Requirement | Level | Constraint |
| --- | --- | --- | --- |
| P1 | Declare at least one cryptographic interface | MUST | `minInterfaces: 1` |
| P2 | Declare at least one `management` interface, **or state why there is none** | MUST | `minInterfacesOfType: {management, 1}`, `orDeclaredAbsent` |
| P3 | Identify the subject the document describes | MUST | `subjectIdentified: {startsWith: pkg:}` |
| P4 | State how complete the declared interface set is | MUST | `productAttribute: coverage` |

P1 and P2 catch omissions. Per-attribute rules cannot catch them, because those rules only check the interfaces a document actually declares. For example, a document may describe its service interface accurately and say nothing about how the product is administered. That document passes every interface rule, but it fails P2. A producer satisfies P2 in one of two ways: by declaring a management interface, or by stating that the subject has none. Some subjects, such as a library or a hardware token with no configuration surface, have no management interface. Stating that absence hides nothing. What P2 rules out is saying nothing at all about management. P2 therefore applies the [disclosure model](#disclosure-states) (the rules for how a producer accounts for information it does not supply) to the structure of the document rather than to a single attribute.

P3 and P4 make the document usable as a record of a specific product, not only as a description. Without P3, a CBOM does not have to say which product, or which version of it, the document describes. The CBOM then cannot be matched to a deployment or compared with the same product's CBOM from last quarter. Without P4, a reader cannot interpret a missing interface. The interface might not exist, or the producer might have chosen not to list it, and those two situations are entirely different. The Conformance section identifies these two gaps as the non-assertions (things a CBOM leaves unstated) most likely to cause difficulty in procurement. P3 and P4 are the rules that address them.

### Per-interface rules (applied to every interface)

Attribute names follow the conventions in [Method](../method/). A bare name describes the interface's present state, so `keyExchange` is the key exchange the interface uses now. A profile that needs to record what an interface is declared to support adds the `Supported` suffix to the name. The [PQC Migration](../../use-cases/pqc-migration/) profile does this.

| # | Attribute | Level | Notes |
| --- | --- | --- | --- |
| I1 | `protocol` | MUST | TLS, SSH, IPsec, and similar |
| I2 | `protocolVersion` | MUST |  |
| I3 | `keyExchange` | MUST | registry algorithm identifier |
| I4 | `encryption` | MUST | bulk or AEAD algorithm |
| I5 | `authentication` | MUST | certificate signature (TLS) or host key (SSH) |
| I6 | `endpointRoles` | MUST | at least two endpoints |
| I7 | `interfaceType` | MUST | from the controlled vocabulary |
| I8 | `lifecycleStage` | MUST | see [Lifecycle Data](../lifecycle/) |
| I9 | `implementationPurl` | MUST | Package URL of the implementing library. Withholdable, which means the producer may decline to publish the value. A `withheld` marker satisfies the rule, but silent omission does not. I9 is the only rule in this table where the disclosure state decides whether the rule passes. |

A CBOM conforms if and only if the carrier format (the document format, such as CycloneDX) is accepted, every product-level MUST rule holds, and every declared interface satisfies every per-interface MUST rule. `interfaceId` is an instance label chosen by the producer and is not constrained by the profile. The full statement of what conformance means, including what a passing verdict (the pass or fail result of an evaluation) does not assert, is in [Conformance](../conformance/).

Derived evaluations such as post-quantum posture are deliberately not profile attributes. They are computed by an external policy from the disclosed facts, because the criteria on which they depend change over time. See [Policy Evaluation](../policy-evaluation/).

### Group rules (one answer per key, within an interface)

Product rules and per-interface rules each produce a single answer. A product rule answers about the set of interfaces. A per-interface rule answers about one attribute of one interface. Some questions do not have a single answer.

For example, consider whether an interface can be made quantum-safe. A producer may have finished the work on the interface's key agreement, while its identity proof is still waiting on a certificate authority. That producer has two answers, not one. If the profile forces a single answer, the CBOM reports the worse of the two. A planner reading it then concludes that no part of the work can proceed, when in fact half of it can.

A **group rule** constrains a repeated group of entries. Each entry is identified by a key taken from a controlled vocabulary, and an interface carries one entry per key. The group rule contains member rules, which are evaluated inside each entry. A conditional guard in a member rule (a condition that says when the rule applies) therefore refers to that entry, not to the interface as a whole.

The [PQC Migration](../../use-cases/pqc-migration/) profile uses a group rule, keyed by [cryptographic purpose](../model/). Rule `pqc-migration#G1` requires an entry per purpose, and its member `G1.2` requires a blocker wherever *that purpose's* status is not `available`.

A group rule also declares its **key coverage** (`keyCoverage`). Key coverage is the set of vocabulary values for which an interface must carry an entry. It may be every value in the vocabulary, or only the values that the profile's scope declares.

The choice of key coverage matters most for a profile that addresses only part of a problem. It decides whether that profile can serve as one depth in a family of profiles, or becomes a permanent floor for the purposes it covers. With full key coverage, the profile still requires a status for each purpose it defers, so a consumer learns where each deferred purpose stands. With key coverage limited to the purposes in scope, the deferred purposes disappear from the document entirely. A later profile then has no baseline (no recorded starting point) to improve on. [C13](../conformance/) checks which key coverage a profile uses. The check is needed because a profile written with either setting loads and runs without error.

## Disclosure states

An attribute with no value may be missing for several different reasons, and the profile keeps those reasons apart. Following the 2026 SBOM minimum elements, a producer states whether the information is unknown to it or is being withheld.

| Outcome | Meaning | Effect on a MUST rule |
| --- | --- | --- |
| `value` | A value was supplied and checked against the constraint. | Passes if valid. |
| `withheld` | The producer holds the information and declines to publish it. | Passes only where the rule is marked withholdable. |
| `unknown` | The producer does not have the information. | Fails, but is reported as unknown rather than absent. |
| `undeclared` | Neither a value nor a marker was supplied. | Fails. |

An unknown value does not satisfy a MUST rule, because the requirement has not been met. It is still reported separately from an undeclared one. An `unknown` marker records a limit of the producer's process. An undeclared attribute records that the producer never addressed the question.

In this profile only I9 is withholdable. I9 is withholdable because a producer can decline to publish a library version and still meet the purpose of the disclosure. A procurement profile might permit no withholding at all.

The choice of which rules are withholdable also decides a larger question. It decides whether a public document can conform to the profile, or whether only a document released under an agreement can conform. [Confidentiality](../confidentiality/) covers that question. One kind of consumer, the vulnerability responder, cannot accept a withheld I9 at all. Incident response depends entirely on matching a library against a vulnerability feed. If I9 is withheld, the responder has no library to match. For that reason, [Vulnerabilities](../vulnerabilities/) treats the withholding of I9 as the open question that blocks that use case. See [Challenges](../challenges/) and [Demo](../demo/).

## Composition: how profiles relate to each other

People mean two different things when they talk about combining profiles. Keeping the two apart matters, because they carry different guarantees.

{{< figure src="../assets/figures/methodology-profile-3.svg" alt="Independent evaluation produces separate verdicts; extension produces a derived profile whose conformance implies the base" >}}

*Independent evaluation answers several questions about one document. Extension builds one profile out of another, and carries a guarantee that independent evaluation does not.*

### Independent evaluation

A CBOM may be evaluated against any number of profiles, each producing its own verdict. The profiles need not know of each other and are not combined. This is how one document serves several purposes. A vendor publishes the CBOM once. A procurement team, a migration planner and a vulnerability responder then each apply the profile that matches the decision they have to make.

Independent evaluation depends on two conditions. First, attribute names are global across the methodology, so a name means the same thing in every profile that uses it. That is why the naming conventions and the attribute table in [Terms](../terms/) apply to all profiles rather than to each one in isolation. Second, a verdict is always reported per profile, so conformance to one says nothing about another.

### Extension

A profile may declare that it extends another. It then inherits every rule of the base and states only what it adds or changes. A sector baseline built on a general one, and the [PQC migration](../../use-cases/pqc-migration/) profile built on the interface disclosure baseline, are both of this kind.

Extension is **monotonic**. A derived profile may add rules and tighten inherited ones. It may not relax them. This restriction guarantees the property that makes extension useful: a document that conforms to the derived profile also conforms to the base. Without the restriction, a claim of conformance to a sector profile "based on" the baseline would tell a consumer nothing at all about the baseline, and the word "based" would mislead the consumer.

| Operation on an inherited rule | Permitted | Why |
| --- | --- | --- |
| Raise the level, SHOULD to MUST | yes | Tightening. Anything satisfying the derived rule satisfies the base rule. |
| Narrow a constraint, such as restricting an enumeration to a subset or raising a minimum count | yes | Tightening. Each kind of constraint is compared with the same kind of constraint in the base. An override (a derived profile's change to an inherited rule) that carries a constraint the comparison does not recognise is refused rather than assumed safe. |
| Add a constraint the base did not carry, such as requiring an identifier form where the base required only presence | yes | Tightening. Recorded as a composition note, so a reader of a report can see what the derived profile added. |
| Drop a constraint the base carried, or replace an identifier-form requirement with a bare presence check | no | Relaxation. This is the relaxation most easily written by accident, because the rule still appears to be present in the file. |
| Make a withholdable attribute non-withholdable | yes | Tightening. |
| Add a new attribute or structural rule | yes | Extension proper. |
| Lower the level, MUST to SHOULD | no | Relaxing. Breaks the implication that derived conformance means base conformance. |
| Widen a constraint or remove a rule | no | Relaxing, on the same grounds. |
| Make a non-withholdable attribute withholdable | no | Relaxing. |
| Redefine what an inherited attribute means | no | Names are global. A profile needing different semantics needs a different attribute. |

A profile that genuinely needs to relax a base requirement is not an extension of that base. It is an independent profile, and it should be written and claimed as one. The methodology treats this as a firm rule, not as an inconvenience to work around. Holding to the rule keeps conformance claims meaningful.

### Two things extension is used for

Extension expresses two different intentions. If the two are confused, it becomes hard to discuss what a derived profile is for.

**Depth.** The derived profile asks for more detail about the same subject matter. The migration profile relates to the baseline in this way. It covers the same interfaces and describes them more fully.

**Coverage.** The derived profile brings more subject matter into scope, at the same level of detail. A profile covering key establishment, later extended by one that adds entity authentication, is of this kind. Here the rules often do not change at all. They are written once and applied to whichever purposes the scope declares. The two profiles then differ only by one line in their scope declaration, not by a second set of rules.

Both kinds of extension are monotonic and both are permitted. The distinction matters when a family of related profiles is planned, because depth and coverage are added at different times. Depth is added when producers are able to supply the extra detail. Coverage is added when consumers need the extra subject matter. Stating which of the two a derived profile adds avoids a later argument about why the profile exists.

**An unsettled case.** The table above covers narrowing an inherited list of permitted values, which is a tightening. It does not cover *widening* one. Suppose a sector profile adds a cryptographic purpose the base does not define, such as attestation, tokenization or credential verification. That widens an inherited vocabulary, and a document could then claim a purpose the base profile has no rule for, which looks like a relaxation. Whether the mechanism permits this, and under what constraint, is recorded as Q35 and is unresolved. Q35 should be settled before a sector body adopts the purpose vocabulary, because a mechanism that permitted only narrowing would block that adoption outright.

### Pinning, ranges and identifiers

-   **The base version is pinned.** A derived profile names the base profile and the exact version it extends. A later release of the base has no effect until the derived profile's author re-pins and re-checks, which follows the general treatment of profile versions in [Versioning](../versioning/).
-   **The carrier acceptance range may narrow, never widen.** The carrier acceptance range is the range of document format versions a profile accepts. A derived profile cannot accept a format version the base excludes, since the base's adapter may be unable to read it.
-   **Inherited rules keep the identifiers the base gave them.** A report can then trace any failure to the profile that imposed it. See *Rule identifiers* for how identifiers are allocated.
-   **An inherited group can be tightened without restating it.** A derived profile may tighten one *member* of a group it inherited, naming that member by its qualified id (`pqc-migration#G1.3`), and may widen the group's `keyCoverage`. Members it does not name are inherited unchanged, and so is the key vocabulary. Restating the whole group would discard both the unchanged members and the key vocabulary. A restated group would also silently replace the base's coverage. Coverage may be widened and never narrowed. See [decision 0014](https://github.com/pkic/cbom/blob/main/decisions/0014-tightening-an-inherited-group.md).
-   **A guard may be removed, but not added or changed.** A `requiredWhen` guard says when a rule applies. Removing it makes the rule apply always, which is a tightening. Adding one where the base has none makes the rule fire less often, and narrowing an existing guard does the same. This is the relaxation that is hardest to spot by reading, because the rule stays listed and stays in every report, but quietly stops applying. Adding a guard and narrowing a guard are both refused.
-   **Single inheritance only, for now.** A profile extends at most one base. Multiple inheritance raises conflicts between bases that would need resolution rules, and no case requiring it has arisen.

### Rule identifiers

A rule identifier is local to the profile that declares it. The citable form is the profile's tag (its short name) followed by the identifier, for example `interface-disclosure#I9`. No shorter form names a rule. Three profiles in one family may each declare an `I1`, and in the worked example three of them do.

The letter in an identifier shows how often the rule is evaluated. It is fixed by the section the rule sits in rather than chosen by the author. `P` means once per product, `I` once per declared interface, and `G` once per entry in a group, with members numbered under their group as `G1.2`. Numbering restarts at 1 in every profile, at every level of a family.

This scheme has two consequences.

-   **A rule keeps the identifier of the profile that introduced it**, however far down the family it is later tightened. The migration profile makes the baseline's `implementationPurl` rule non-withholdable, but that rule is still `interface-disclosure#I9`. The tightening is recorded against `interface-disclosure#I9`, and a report names both the rule and the profile that tightened it.
-   **The tag is the only thing that has to be unique** along a chain of profiles. Because only the tag must be unique, a base profile can add a rule without first checking which identifiers its derived profiles already use. For the same reason, a family can go three levels deep with no reserved ranges of numbers and no registry. A tag that an ancestor already uses is rejected before any document is evaluated.

Identifiers are not reused. Once a version is released, an identifier retired in a later version stays retired, and the numbering carries a gap. The reason is that a conformance report or a stored claim may cite that identifier against a document evaluated under the earlier version. Reusing it would make the old report silently wrong, rather than merely out of date.

Identifiers do not appear in CBOM documents at all. They appear in conformance reports and in claims, which is why they have to be stable and why they have to say which profile they came from. See [decision 0011](https://github.com/pkic/cbom/blob/main/decisions/0011-rule-numbering-across-a-family.md).

### Expressing a conformance claim

A conformance claim is the artifact that passes from one organisation to another. A producer hands the claim to a consumer who was not present when the evaluation ran, and who may read it months later. The claim is a machine-readable document with [its own schema](../../docs/methodology/claim.schema.json). The shape below is illustrative. [claim-example.json](../../docs/methodology/claim-example.json) is a real claim, covering both example profiles at once.

Four properties make a claim checkable. A claim is **bound to one document by digest** (a hash of the document), so the claim no longer matches if it is placed beside a different CBOM. It **lists every profile separately**, with its own verdict and its whole pinned chain, because a document can conform to one profile and fail another. It carries the **disclosure states** alongside the verdict, because “conforms” with the implementing library withheld is a different answer from “conforms” with it supplied. And the claim itself lists **what it does not assert**, rather than referring to another document for that list. See [decision 0015](https://github.com/pkic/cbom/blob/main/decisions/0015-a-conformance-claim-is-checkable.md).

```
Conforms to:
  pkic.example.pqc-migration v0.6            (tag: pqc-migration)
    extending pkic.example.interface-disclosure v0.7   (tag: interface-disclosure)
  pkic.example.interface-disclosure v0.7     (independently evaluated)
Carrier: CycloneDX 1.7
Content revision: 3
```

The tags have a function in the claim. A report attached to the claim cites rules as `pqc-migration#I4`, and a reader needs the claim to say which profile that tag belongs to.

**A claim is useful only if a consumer can re-check it.** A consumer holding the claim and the document runs `validate_cbom.py <cbom> <claim> --verify-claim`. The command confirms the digest, re-runs every profile the claim names, and reports where the claim and the new results disagree. A mismatch exits with `5` rather than `1`, because a mismatch is a finding about the claim, not a verdict on the document. Someone holding a bad claim and a good document should evaluate the document. An exit code meaning “does not conform” would wrongly point them at the document.

Verification cannot establish that the disclosed values are true. A producer who states `TLS 1.3` for an interface actually running `TLS 1.2` produces a claim that verifies perfectly. The claim's own `notAsserted` list states this limitation, and the list will always include it. Proving that values are true is attestation, which is a different problem. If the claim format implied that it provided attestation, that would be the most damaging error it could make.

### Machine-readable form

A derived rules file declares its base and lists only its additions and its tightenings.

```
{
  "profileId": "pkic.example.pqc-migration",
  "profileTag": "pqc-migration",
  "version": "0.6",
  "extends": { "profileId": "pkic.example.interface-disclosure", "version": "0.7" },
  "overrides": [
    { "id": "interface-disclosure#I9", "level": "MUST", "withholdable": false }
  ],
  "interfaceRules": [ ... numbered from I1 in this profile's own space ... ]
}
```

The override names its target in full. A bare `I9` would be this profile's own ninth interface rule, which is a different rule, so the validator rejects an unqualified override rather than guessing.

A validator loading such a file resolves the base, applies the overrides, and rejects any override that relaxes an inherited rule. That check is worth implementing early, because a relaxing override is easy to write by accident and its effect on a conformance claim is not obvious from reading the file.

**What “relaxes” means for a constraint.** Comparing obligation levels is easy. Comparing constraints is harder, and it decides whether the guarantee that derived conformance implies base conformance actually holds. Each kind of constraint is therefore compared on its own terms. A minimum may rise and not fall. A list of permitted values may shrink and not grow. A required prefix may lengthen and not shorten. An override may add an obligation the base did not carry, but may not drop one it did. Changing which attribute a rule is about is not an override at all. It is a different rule, and a derived profile adds it under its own id.

The most important rule covers a constraint that the comparison does not recognise. An override carrying such a constraint is *refused*, rather than assumed to be monotonic. A checker that passes what it cannot assess produces the same green report as a checker that has actually checked. Wrongly passing an override in this way is a worse failure than wrongly refusing it. See [decision 0013](https://github.com/pkic/cbom/blob/main/decisions/0013-monotonicity-covers-constraints.md).

## Conformance pipeline

The validator takes a CBOM and applies four stages in sequence: the format gate, the product rules, the interface rules and the verdict. The content stages are evaluated only if the format stage accepts the CBOM.

{{< figure src="../assets/figures/methodology-profile-4.svg" alt="Five boxes chained by arrows: a CycloneDX 1.7 CBOM, a format gate checking the version band, product rules P1 to P4, interface rules I1 to I9, and a verdict" >}}

*The pipeline is shown interactively in the [Demo](../demo/) section, and the version bands are described in the [Versioning](../versioning/) section.*

[← Objects](../objects/) [Next: Conformance →](../conformance/)
