---
title: Conformance
sideMenu: true
weight: 10
aliases:
- /cbom/methodology/conformance.html
linkTitle: Conformance
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

Conformance is the relation between a document and the rules it is checked against. The [Profile](../profile/) section gives the rules of one example profile. Conformance covers what can be assessed, who may claim conformance, how a claim is written down, and what a claim does not cover.

Illustrative. This clause is a draft for working group discussion. Several points marked below remain open, and are recorded in the open questions register.

## Requirement keywords

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in capitals. The same keywords in lower case carry their ordinary English meaning and impose no requirement.

## What can be assessed

Three different things can be assessed, and each is assessed against its own criteria. A claim that does not say which of the three it means is ambiguous. Saying that something "is conformant", without naming what was assessed, is not a conformance claim under this methodology.

| Target | Assessed against | Assessed by | Result |
| --- | --- | --- | --- |
| **A CBOM document**
a specific revision of a specific document | A specific version of a specific profile | A validator, mechanically | Conforms · Does not conform · Refused |
| **A profile**
the rules document itself | This methodology | Review, with mechanical checks on the rules file | Well-formed · Not well-formed |
| **An evaluation tool**
a validator implementation | This methodology's evaluation semantics | A conformance test suite | Conforms · Does not conform |

The three assessments depend on each other, and the dependency runs in one direction only. A verdict is the result of assessing a document against a profile. A verdict is meaningful only if the tool that produced it conforms to this methodology, and only if the profile used is well-formed. A document assessed by a non-conforming tool therefore has no established verdict. A verdict against a profile that is not well-formed establishes nothing either, because the rules used to measure the document were not valid rules.

## 1\. A CBOM document conforming to a profile

A CBOM document conforms to a profile version when all of the following hold.

-   The carrier format is the standard the CBOM is written in, such as CycloneDX. The document's carrier format and version fall within the range of versions the profile declares that it accepts. See [Versioning](../versioning/).
-   Every product-level rule at MUST level is satisfied.
-   Every declared interface satisfies every per-interface rule at MUST level.
-   Where a rule is satisfied by a disclosure marker rather than by a value, the profile marks that rule as withholdable. A withholdable rule is one the producer may satisfy by declaring the value withheld instead of disclosing it.

Rules at SHOULD and MAY level are evaluated and reported, but they do not decide the verdict. If an author wants a requirement to decide the verdict, the author states it at MUST level. A consumer may sometimes treat a SHOULD rule as binding anyway. That consumer has misread the profile. If the author meant MUST, the fix is for the author to raise the rule to MUST level.

### Verdict vocabulary

| Verdict | Meaning | What it says about the document |
| --- | --- | --- |
| **Conforms** | Every MUST rule is satisfied, at a carrier version within the acceptance range. | The document discloses at least what the profile requires. |
| **Does not conform** | At least one MUST rule is not satisfied. | The document was assessed and found short. The report identifies each failing rule. |
| **Refused** | The carrier version falls below the profile's declared minimum. | Nothing. No assessment was performed, because the profile cannot express its rules against that carrier version. |

Refusal and non-conformance are reported separately and MUST NOT be merged. A refused document may be perfectly adequate. The profile is simply unable to say so, because it cannot express its rules against that version of the carrier format. Treating a refusal as a failure penalises a producer because its document uses an older format version, not because of what the document discloses.

### Effect of the disclosure states

Every attribute is assessed according to which of the four outcomes applies to it. The states are defined in the [Profile](../profile/) section and are summarised here for their effect on a verdict.

| Outcome | Against a MUST rule | Against a SHOULD or MAY rule |
| --- | --- | --- |
| **value** | Satisfied if the value meets the constraint | Reported; satisfied if the value meets the constraint |
| **withheld** | Satisfied only where the rule is marked withholdable; otherwise not satisfied | Reported as withheld |
| **unknown** | Not satisfied, and reported as unknown rather than as absent | Reported; does not affect the verdict |
| **undeclared** | Not satisfied | Reported; does not affect the verdict |

A document can therefore conform while withholding some values. A consumer who reads only the verdict will not know that values were withheld. For this reason a conformance report states the disclosure state of every rule it assessed. A consumer who acts on the verdict alone ignores the part of the result that is most likely to matter commercially. The clearest example is a public variant and a restricted variant of the same document. Both variants conform, but only one of them answers the consumer's question. See [Confidentiality](../confidentiality/).

### Conformance to more than one profile

A document evaluated against several profiles receives one verdict per profile. A verdict against one profile implies nothing about conformance to any other profile. There is one exception. Where one profile extends another, conformance to the derived profile also implies conformance to the base profile version that the derived profile pins, meaning names by identifier and version. This holds because extension is monotonic: a derived profile cannot relax an inherited rule. See the composition rules in [Profile](../profile/).

### Scope of a verdict

A verdict applies to one revision of one document, assessed at a point in time. It does not extend to later revisions, to other documents describing the same product, or to the product itself. A product does not conform to a profile; a document describing it does.

## 2\. A profile conforming to this methodology

A profile is well-formed under this methodology when it satisfies the following. Each requirement restates, as a requirement, an output that the procedure in [Method](../method/) produces.

| # | Requirement | Level |
| --- | --- | --- |
| C1 | The profile states the consumer it serves, the decision it supports, and the options the consumer chooses between. | **MUST** |
| C2 | The profile carries an identifier and a version, and declares an acceptance range for every carrier format it supports. | **MUST** |
| C3 | No rule refers to a named product, vendor, or interface instance. | **MUST** |
| C4 | Every rule carries a stable identifier, an obligation level, and a statement of whether withholding satisfies it. | **MUST** |
| C5 | Attribute names follow the methodology's naming conventions, and any attribute already defined elsewhere in the methodology is used with its established meaning. | **MUST** |
| C6 | No rule requires a derived judgement whose criteria are external to the document and subject to change. See [Policy Evaluation](../policy-evaluation/). | **MUST** |
| C7 | Where the profile extends another, it pins the base by identifier and version, and no override relaxes an inherited rule. | **MUST** |
| C8 | The profile states what it deliberately excludes, and why. | SHOULD |
| C9 | The profile is accompanied by a mapping to at least one carrier format, and by at least one document that conforms and one that does not. | SHOULD |
| C10 | The profile carries a changelog classifying each change as tightening, relaxing, or editorial. | SHOULD |
| C11 | The profile declares its scope: the type of subject it describes, its orientation, the relationship types its rules constrain, and the lifecycle stages of reported data it accepts. | **MUST** |
| C12 | The rules the profile imposes are consistent with the orientation it declares. | **MUST** |
| C14 | Identifier schemes are declared for every asset class the rules constrain, and no scheme is declared that no rule applies. | **MUST** |
| C15 | The profile carries a tag, and no profile it inherits from already uses that tag. | **MUST** |
| C16 | Rule identifiers are local to the profile, and each carries the letter of the section it sits in. | **MUST** |
| C17 | Every rule can pass a document and can fail one: it has a constraint, the constraint is one the evaluator implements, and any vocabulary it names is declared. | **MUST** |
| C13 | Every group rule is keyed to a declared vocabulary, and a profile that declares a subset of that vocabulary in scope still requires an answer for the rest. | **MUST** |

C3, C6 and C7 are the requirements that review most often has to enforce. Each can be broken by a rules file that still loads and runs without errors. For example, a profile that names a particular instance still evaluates documents without error. However, it evaluates them for that one deployment rather than for the product.

### The scope declaration

C11 requires the scope to be declared as one object, rather than as separate fields scattered through the profile. The reason is that the subject type, the relationship types and the accepted lifecycle stages together describe a single boundary. Step 2 of [Method](../method/) decides all of them at once.

| Member | Values | What it settles |
| --- | --- | --- |
| `subjectType` | `product`, `service`, `component`, `estate-subset` | Whether the profile applies to the thing a consumer is holding. A profile for a product a consumer cannot inspect can ask for less than one for a service the consumer operates. |
| `relationshipTypes` | the relationship types named in [Model](../model/); today only `interface` | Which kinds of cryptographic relationship the rules constrain. The profile declares these types, and the checker compares the declaration with the rules instead of trusting it. A scope statement that no longer matches the rules still reads as authoritative, so it is worse than no statement at all. |
| `orientation` | `inventory`, `migration`, `both` | Whether the profile reports what an interface does, what it could do, or both. The value is more than a label, because C12 requires the rules to be consistent with it. It uses the same vocabulary the working group uses for its own aspects, except for `n-a`. |
| `lifecycleStages` | a subset of `intended`, `implemented`, `configured`, `observed` | Which stages of reported data the profile will accept, in the same sense that `appliesTo` settles which carrier versions it will accept. An interface reporting a stage outside the set fails the rule that constrains the stage. |

Of the four members, `lifecycleStages` is the one that changes verdicts. Without it, a document could report every interface at the `intended` stage and still conform. Such a document would describe cryptography the producer plans to build, not cryptography that exists.

Reporting planned cryptography is acceptable for a disclosure baseline, so the example baseline profile accepts all four stages. It is not acceptable for a procurement or migration profile. The example migration profile therefore accepts only the three stages that describe cryptography that exists. A derived profile may narrow the set of accepted stages. It may not widen the set, for the same reason that it may not relax a rule.

### Orientation, and why it is checked rather than taken on trust

A document can describe both the present state of an interface and its declared capability. Both appear in the same document, about the same interface, under attribute names that differ only by a suffix. `keyExchange` is the key exchange an interface negotiates today. `keyExchangeSupported` is every key exchange it could negotiate.

The naming conventions in [Method](../method/) keep the two names apart. They do not keep the two *obligations* apart. A profile could require only the capability attribute. A consumer would then hold a set of supported algorithms with no way to tell which one is in use, and would be likely to misread the document.

C12 closes that gap by setting an obligation for each orientation.

| Orientation | The profile's rules must |
| --- | --- |
| `inventory` | Require no forward-looking attribute: nothing with a `Supported` suffix, and none of `capabilityStatus`, `blockedBy` or `roadmapRef`. |
| `migration` | Require at least one, or the profile reports present state only and is an inventory profile under another name. |
| `both` | Require, for every capability attribute, the present-state attribute it is a capability for. |

C12 is assessed against the resolved profile, which is the profile together with the rules it inherits from its base. A rule inherited from a base can therefore satisfy C12. This is the normal case, not a loophole. The example migration profile declares the three capability attributes itself, and inherits their present-state counterparts from the baseline it extends. A profile that declared `both` but required only capability attributes would fail C12. That is the case the requirement exists to catch.

### Group rules, and why coverage is checked

A rule normally constrains one attribute of one interface. A **group rule** is different. It constrains a repeated group of entries, keyed by a controlled vocabulary, so that an interface gives one answer per key instead of one answer overall. The migration example uses a group rule for capability. An interface states its status separately for each cryptographic purpose, because key agreement and identity proof migrate on different timetables. A single status would have to report the worse of the two.

Two properties of a group rule are checked. Without these checks, each property has a failure mode that would go unnoticed, because the rule looks ordinary in the file and the report shows it passing.

The first failure mode is a group rule keyed to a vocabulary that the profile never declares. Such a rule requires an entry for no keys at all. Every document therefore satisfies it, and the report shows it as passing. C13 rejects the profile instead of issuing that verdict.

The second failure mode is a group rule whose `keyCoverage` is set to `in-scope` while the vocabulary it is keyed to contains more keys than the profile takes in scope. That setting lets a profile defer part of the problem and never return to it. A family of depths is meant to control how much *detail* an answer carries at each depth. It is not meant to remove the question. A purpose that the profile has deferred still requires a status. It also requires a blocker wherever that status is not `available`. Without that requirement, a supplier could conform while acting as though a whole class of cryptography did not exist. Each depth would then become a permanent floor instead of a step towards the next depth. C13 makes this difference checkable.

### Identifier schemes

When an inventory is built from CBOMs supplied by several suppliers, the consumer has to work out which records describe the same thing. Identity cannot be settled in general, because some classes of asset have no agreed identifier at all. It can be settled one profile at a time, and that is the means this methodology has available. A profile names the identifier form it requires for each class of asset that its rules constrain. A consumer then knows which naming scheme the document uses.

C14 does not check that a value really belongs to a registry. The checker does not hold a copy of the registry, so any such check would be a guess. Instead, C14 checks that the declaration and the rules agree in both directions. Every scheme a rule references must be declared, and every declared scheme must be referenced by some rule. A declared scheme that no rule applies can drift away from what the profile actually does, while still reading as authoritative. Which registry algorithm names should come from is open question [Q20](../../issues/), and it is not settled. This methodology does settle that a profile has to state which registry it means.

### C15 and C16: identifiers that can be cited

A rule identifier is local to the profile that declares it. A rule is therefore cited as `<profileTag>#<ruleId>`, and three profiles in one family may each declare their own `I1`. This approach moves the uniqueness requirement off the rule identifiers and onto the tag. No author can coordinate rule identifiers across a whole family, but an author picks a tag only once. C15 checks that the tag is unique. Without C15, a citation could resolve to two different rules, and a stored conformance claim would no longer identify which rule it refers to. With C15, a base profile can add a rule without first checking which identifiers its derived profiles already use.

C16 fixes the meaning of the letter in a rule identifier, so that the author does not choose it. `P` means the rule is evaluated once per product, `I` once per declared interface, and `G` once per entry in a group. The tag already says which profile a rule belongs to, so the letter can tell the reader how often the rule is evaluated. C16 does not require the numbers to run without gaps. A released identifier is never reused, so gaps are expected. A checker that demanded a contiguous sequence would forbid exactly what the no-reuse rule exists to allow. See [decision 0011](https://github.com/pkic/cbom/blob/main/decisions/0011-rule-numbering-across-a-family.md).

### The claim: the artifact read without the inputs

Two of the conformance targets are checked by someone who holds the inputs: a document against a profile, and a profile against the methodology. The **claim** is a separate artifact. It is the only one read by someone who does not hold the inputs. That reader is typically a buyer in a different organisation, reading the claim months later.

A claim is a machine-readable document. It is bound to one CBOM by digest. It lists every profile that was evaluated, each with its own verdict and its whole pinned chain of base profiles. It also carries the disclosure states and the non-assertions inside itself, rather than pointing to them elsewhere. The non-assertions are the statements of what a verdict does not establish.

The non-assertions matter most. Every point in the table at the end of this page about what a verdict does not establish is repeated inside every claim. The reason is that the person reading a claim will not have read this page, and the word “conforms” invites more inference than it supports.

A claim can be re-checked. Running `--verify-claim` confirms the digest and re-runs each profile the claim names. Re-checking cannot establish that the disclosed values are true, and no future version of the check will be able to. A producer who misstates a protocol version still produces a claim that verifies correctly. See [decision 0015](https://github.com/pkic/cbom/blob/main/decisions/0015-a-conformance-claim-is-checkable.md), and [0016](https://github.com/pkic/cbom/blob/main/decisions/0016-what-an-spdx-only-claim-asserts.md) for what an SPDX-only claim may assert.

### C17: rules that cannot fail

A rule that cannot fail is worse than a missing rule. The report says the rule passed, and a reader cannot tell that it could never have failed. There are three ways to write such a rule, and until recently all three passed review.

-   Give the rule no constraint at all.
-   Misspell the constraint key, so the evaluator recognises nothing and reports `ok` against every value.
-   Point the rule at a vocabulary that does not exist. This is the mirror image of the second case. The rule fails every value, and the report says only that the value was not accepted.

C13 already rejected the third case for group keys. C17 covers the remaining cases. The validator refuses a profile that breaks C17, instead of issuing a verdict against it.

C17 applies the principle behind C13 more widely: every rule in a profile must be capable of failing a document. C17 is written as a requirement, rather than left to review, because none of the three defects is visible when you read the file. Each defect produces a rule that looks ordinary.

C1 to C7 and C11 to C17 are checked mechanically by `check_profile.py`, which takes a rules file and reports on each requirement in turn. C8 to C10 are checked where the profile declares the material, and are reported as warnings that do not affect the result unless `--strict` is given.

All three example profiles pass: the entry profile of the interface family, the disclosure baseline and the migration profile. The test suite also carries one deliberately defective profile for each MUST requirement, so that the checks themselves are tested.

The tool does not replace review. C3 in particular is enforced through indirect structural checks. A rule that names a specific instance in a way the checker does not model would therefore still pass.

## 3\. An evaluation tool conforming to this methodology

Two tools given the same document, the same profile, and the same resolution of any extended base should return the same verdict. The requirements below are what that expectation rests on.

| # | Requirement | Level |
| --- | --- | --- |
| T1 | Determine the carrier band, meaning which of the profile's version ranges the carrier version falls in, before evaluating content, and refuse a document below the declared minimum without issuing a conformance verdict. | **MUST** |
| T2 | Report the four disclosure outcomes distinctly, and not collapse withheld, unknown and undeclared into a single absent state. | **MUST** |
| T3 | Resolve an extended base and reject, before evaluating any document, a profile containing an override that relaxes an inherited rule. | **MUST** |
| T4 | Report, for every rule assessed, its identifier, the profile that imposed it, its obligation level, and the outcome. | **MUST** |
| T5 | Distinguish, in whatever channel the caller consumes, between a conformance failure and an invalid profile. | **MUST** |
| T6 | Evaluate rules at SHOULD and MAY level and report them without allowing them to determine the verdict. | **MUST** |
| T7 | Produce identical output for identical inputs, with no dependence on ordering within the document. | SHOULD |
| T8 | Apply the profile's accepted lifecycle stages, and reject, before evaluating any document, a derived profile that accepts a stage its base rejects. | **MUST** |
| T9 | Distinguish, when a stage is rejected, a stage the methodology defines that this profile does not accept from a value that is not a stage at all. | SHOULD |

The reference validator signals T5 through its exit code: 0 for conforms, 1 for does not conform, 2 for a usage error, 3 for a profile error such as a relaxing override, and 4 for a refusal.

Exit code 4 exists because of T1. A caller that cannot tell a refusal from a failure will reject a producer because of the age of its carrier format.

Until August 2026 the validator printed `DOES NOT CONFORM` and exited 1 on a refusal. It merged the two results that must not be merged. The test suite asserted that exit code, so the test held the defect in place instead of catching it.

The methodology requires only that the distinction between the two results reaches the caller. The particular codes are an implementation choice, and another tool may signal it differently.

This site runs two tools, so the expectation that two tools return the same verdict can be tested. `validate_cbom.py` is the reference implementation. The [Demo](../demo/) page is a second one: a static page cannot run Python, so the evaluation is written again in JavaScript.

The demo previously carried its own copy of the rules as well. The page stated that its results matched the reference tool, but nothing checked either the copied rules or the results. The demo now fetches the rules from the published rules file, so the rules are stated in one place only. The evaluation logic is still a second implementation. For that reason `tests/check-demo.py` runs the page's own functions over the four example documents. It requires the same verdict, the same outcome for every rule, the same disclosure state for every value, and the same carrier band.

The demo and the reference tool had diverged once before this check existed. A published page that silently disagrees with the specification is worse than no page at all. Before the check, the statement that two tools return the same verdict had no evidence behind it. See [decision 0018](https://github.com/pkic/cbom/blob/main/decisions/0018-the-demonstration-is-checked-against-the-tool.md).

## Making and recording a claim

A conformance claim is a statement by an identified party that a named document revision was assessed against a named profile version and produced a stated verdict.

### What a claim cites

A claim names three things: the profile and its version, the carrier format and its version, and the content revision of the document that was assessed. A claim missing any of the three cannot be reproduced, and a claim that cannot be reproduced cannot be audited. Where a derived profile was used, the claim also names the base and the version it pins.

```
Conforms to:
  pkic.example.pqc-migration v0.6
    extending pkic.example.interface-disclosure v0.7
Carrier: CycloneDX 1.7
Content revision: 3
Assessed by: Example Ltd (self-declared)
Assessed on: 2026-08-09
Tool: validate_cbom.py 0.2
```

### Who may claim

A claim is made by the party that performed the evaluation, and identifies that party. A producer evaluating its own document makes a self-declared claim, which is permitted and is labelled as such. A claim made by a party other than the producer is an attested claim, and carries whatever additional weight the relying party assigns to the attesting party.

Open point. Whether self-declaration is sufficient for a given purpose, or whether some profiles should require attestation by an independent party, is not settled. It may reasonably differ between a procurement profile and an internal reporting profile. Recorded as Q14.

### Validity over time

A claim is fixed to the revision it assessed and does not roll forward. A new content revision needs a new evaluation. So does a new profile version, and where that version tightened a rule, a document that conformed before may no longer conform. The changelog is what tells a producer whether re-evaluation is likely to be needed, and that is why the methodology asks for every change to be classified.

Open point. Whether a tightening obliges a grace window before a consumer may reject documents produced against the previous version, and whether that window belongs to the profile or to the agreement between the parties, is not settled. Recorded as Q15.

## What a conformance verdict does not assert

The verdict is a statement about disclosure only. It does not make the following claims, although it is often mistaken for them.

| A verdict of "conforms" does not assert | Because |
| --- | --- |
| That the disclosed values are accurate | Accuracy is a property of the producing process. Signing establishes origin, and the lifecycle stage records how the data was obtained. Neither is checked by the profile. |
| That the disclosed values are current | A CBOM revision is a point-in-time record. A configured or observed value may have changed since capture. |
| That the cryptography described is adequate | Adequacy is a derived judgement made by external versioned policy, deliberately kept out of the document. See [Policy Evaluation](../policy-evaluation/). |
| That the document is complete | A profile is a minimum reporting requirement. Cryptography outside the profile's scope may exist and is not required to be disclosed. |
| That every relevant interface was declared | Product rules constrain the set of declared interfaces by kind and count. An undeclared interface that no product rule requires is invisible to the evaluation. |
| That the cryptography described is free of known vulnerabilities | A third party asserts a weakness about a component. Whether the weakness affects this product is a judgement the producer publishes separately, as a VEX statement. A profile requires the facts that let a consumer join the weakness to the VEX statement. It does not require a verdict on vulnerability. See [Vulnerabilities](../vulnerabilities/). |
| That the product is suitable for a given purpose | Suitability is the consumer's decision. The profile exists to supply the facts that decision needs. |

The rows on completeness and on undeclared interfaces are the ones most likely to cause trouble in procurement. Both allow a document to conform while leaving out something the buyer assumed was covered. The remedy is in the profile author's hands: write product rules strong enough that the omission fails the evaluation. This is a drafting question, and the conformance semantics do not need to change to deal with it.

In short. Conformance under this methodology is a relation between one revision of one document and one version of one profile. It is established mechanically and reproducibly, and what it says is that the document discloses at least what the profile requires. Whether the disclosure is accurate, and whether the cryptography it describes is adequate, are separate questions. [Governance](../governance/) and [Policy Evaluation](../policy-evaluation/) deal with those.

[← Profile](../profile/) [Next: Maturity →](../maturity/)
