---
title: Method
sideMenu: true
weight: 16
aliases:
- /cbom/methodology/method.html
linkTitle: Method
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The procedure for writing a profile has twelve steps. A sector body adopting this methodology follows them in order. The earlier sections define what a profile is and the terms it uses. The worked use cases show the procedure applied.

This procedure is derived from how the worked example in this documentation was actually built. It is a proposal for the working group to accept, amend or reject, and is not yet an agreed position.

## The shape of the work

The twelve steps are grouped into five stages. The order of the stages matters, because each stage sets limits on the next one. The most common way to produce an unusable profile is to start in the middle, by choosing attributes before the scope has been set.

{{< figure src="../assets/figures/methodology-method-1.svg" alt="Five stages: Scope, Content, Rules, Realisation, Proof, with a feedback loop from Proof back to Content" >}}

*The five stages of defining a profile. Returning from stage 5 to stage 2 is normal. A profile has not been checked until it has been run against a real document.*

## Stage 1 — Scope

### Step 1. Name the consumer and the decision

Write down who will read a CBOM evaluated against this profile, and what they will do differently depending on what it says. You need both. If you name a consumer but no decision, the profile collects data that nobody acts on. If you name a decision but no consumer, nobody is accountable for satisfying the profile.

To test the decision, state it as a sentence that contains a choice. "Whether to schedule this system for upgrade, replacement, or no action" passes the test. "To understand our cryptographic position" fails it. A profile written from that second sentence keeps growing until it demands everything.

Record the choices explicitly in `objective.decisionOptions`. Do not leave them implied in the sentence. At least two options are required. Because the options are recorded as data, `check_profile.py` can enforce the test under rule C1. If the author cannot list a second option, the profile does not yet have a real decision.

### Step 2. Establish the subject and its boundary

Decide what the profile describes: a `product`, a deployed `service`, a `component`, or a bounded part of an estate (`estate-subset`). Then decide where the boundary sits. The boundary is the limit of what the producer can reasonably declare. If the consumer cannot inspect the product, the profile can only ask for what can be observed or asserted at the product's interfaces. A profile for an operator's own service can ask for more.

The boundary limits what the profile can feasibly ask for. Setting it early avoids work on attributes that no producer will supply. To test the boundary, ask this of each item you intend to request: could the producer answer without disclosing something it has a legitimate reason to protect? See the black-box discussion in [PQC Migration](../../use-cases/pqc-migration/) for a worked instance.

Four further decisions belong in stage 1 and not later, because each one limits what the profile can ask for. All four are recorded in the `scope` object that rule C11 requires.

-   **Relationship types.** Decide which relationship types the rules will constrain, using the vocabulary in [Model](../model/).
-   **Cryptographic purposes.** Decide which cryptographic purposes the profile requires in full detail. A profile may address key establishment now and entity authentication later. If the profile declares its set of purposes here, the rules can be written once and applied to every purpose in the declared set. Otherwise they have to be rewritten for each stage.
-   **Lifecycle stages.** Decide which lifecycle stages the profile will accept. A procurement or migration profile has no use for cryptography that the producer reports only as `intended`. A disclosure baseline should record whatever the producer can report, and leave it to profiles derived from the baseline to narrow the accepted stages. This decision is an acceptance constraint. If an interface reports a stage that the profile does not accept, the interface fails the rule that constrains the stage.
-   **Orientation.** State the profile's orientation: `inventory` if it reports what interfaces do, `migration` if it reports what they could do, `both` if it reports both. The orientation limits the rules the profile may contain. Under C12, an inventory profile may not require any forward-looking attribute. A profile that declares `both` must require the present-state attribute behind every capability attribute it asks for. As a result, a producer can never report capability in place of present state.

### Also in stage 1: decide whether you are extending

Before deriving questions, establish whether an existing profile already covers part of the ground. If one does, the new profile can extend it, inheriting its rules and stating only additions and tightenings. If the new profile would need to relax any requirement of the candidate base profile, it is an independent profile and should be written as one. Make this choice once, at the start, because it determines what the remaining steps produce. An extension states only its differences from the base profile. An independent profile states all of its requirements in full.

The rules governing extension, including why relaxation is excluded, are in [Profile](../profile/).

## Stage 2 — Content

### Step 3. Derive the questions

From the decision, enumerate the questions the consumer must answer to make it. Keep them as questions, phrased in the consumer's own language. Do not convert them to attributes yet. This step is the one most often skipped. Profiles written without it tend to copy the fields that a format happens to offer.

Expect between three and a dozen. If the list runs much longer, the decision in step 1 was probably too broad and should be split into separate profiles.

### Step 4. Convert each question into a declarable attribute

Work through the questions and, for each, identify what would have to be disclosed to answer it. One question may need several attributes, and several questions may share one. Every attribute must have two properties. First, the producer must be able to declare it at the boundary set in step 2. Second, a declared value must be capable, in principle, of being wrong. If no value could ever be wrong, conformance to the attribute would mean nothing.

Express attributes in format-independent terms. Use the vocabulary in [the model](../model/), so that an attribute belongs clearly to a relationship, an endpoint, or an asset. Attributes that turn out to belong to none of those are usually judgements, which step 5 handles.

#### Naming conventions

Profiles written under this methodology are meant to be read together, and a reader should not have to work out that two names mean the same thing. Four conventions apply.

| Convention | Form | Example |
| --- | --- | --- |
| Present state carries the bare name | `attribute` | `keyExchange` is what the interface uses now |
| Declared capability takes a `Supported` suffix | `attributeSupported` | `keyExchangeSupported` is everything it could use |
| Sets are plural, single values are singular | `attributesSupported` | `protocolVersionsSupported` holds several; `protocolVersion` holds one |
| Names describe what is disclosed, not what it implies | — | `keyExchangeSupported`, never `pqcReady` |

The fourth convention applies step 5 to names. Step 5 removes judgements from the attribute list. A name that describes a conclusion, such as `pqcReady`, brings that judgement back into the profile even when the values under it are facts.

Where an existing profile has already published an attribute, later profiles reuse the name and its meaning without redefining it. If a later profile changes the name or the meaning, the two profiles can no longer be used together. The author who introduces the difference does not always notice it.

### Step 5. Separate facts from judgements

Review the attribute list and remove anything that is a conclusion drawn against criteria that change over time. Post-quantum posture and cryptographic maturity are the two clearest cases. These conclusions belong in an external, versioned policy. The policy reads the facts that the profile collects and produces a dated verdict, meaning an assessment that holds as of a stated date. The reasoning is set out in [Policy Evaluation](../policy-evaluation/).

To test an attribute, ask whether the same disclosed values could give a different answer next year without any change to the product. If they could, the attribute is a judgement. Keep the facts that feed the judgement, and remove the judgement itself.

## Stage 3 — Rules

### Step 6. Assign conformance levels and disclosure treatment

Give every attribute a level using BCP 14 keywords. Then decide, for each attribute, what happens when its value is absent. Under the disclosure model, every attribute has one of four outcomes: value, withheld, unknown or undeclared. A value can be missing because the producer does not know it, or because the producer has deliberately withheld it. The profile must say which attributes a producer may withhold while the document still conforms. A procurement profile may permit none. A supply-chain disclosure profile will permit several.

For each attribute, ask what a consumer should conclude if the value is missing. If its absence changes nothing, the attribute does not need to be mandatory, and it may not need to be in the profile at all.

### Step 7. Add the structural rules

Per-attribute rules detect values that are stated wrongly. They do not detect things that are left out, because a rule about interfaces cannot check an interface that was never declared. Structural rules constrain the whole set of declared items. They state how many of a thing must be present, and of which kinds.

Structural rules are how a profile requires that a management interface exists at all, or that the producer states whether its list is complete. Structural rules never depend on a particular product, because they constrain kinds and counts and never name an instance.

Structural rules belong in the earliest version of a profile, and in the shallowest profile of a family. A family is a series of profiles, each asking for more than the one before. It costs a producer little to declare that an interface exists. Describing the interface in detail is what costs effort. Some profiles defer the structural rules to a deeper profile so that they look less demanding. Such a profile lets a supplier conform while leaving out an entire interface. The worked example is built around this failure. A deeper profile adds detail. The structural rules, which set what the answer must contain, are settled at the start.

### Step 8. State the exclusions

Write down what the profile deliberately does not ask for, and why. The list of exclusions answers in advance the reasonable objection that something obvious was forgotten. It records the boundary decision from step 2 in a form a reader can check. It also means that any later expansion of the profile has to be a deliberate decision.

## Stage 4 — Realisation

### Step 9. Define the format mapping

For each format the profile must support, state where each attribute is located in that format. Formats allow the same information to be encoded in more than one valid way. The mapping therefore fixes one canonical location, so that consumers read each attribute from one place. Record the normalization of names and encodings that the mapping assumes. The conventions and the reasoning are in [Formats](../formats/).

The profile itself stays format-independent. Adding support for a further format adds a mapping and changes no requirement.

### Step 10. Declare the carrier acceptance range (the accepted format versions)

The carrier is the format, and the format version, in which a CBOM is written. State which format versions the profile accepts. Give a minimum version and a tested version, so that documents in older versions are handled deliberately and not by accident. [Versioning](../versioning/) describes the bands into which format versions are sorted, and the reasoning behind them.

### Step 11. Record the decisions and their revival triggers

Where one option was chosen over a defensible alternative, record the decision together with the condition that should cause it to be revisited. That condition is the revival trigger. Without a trigger, a decision tends either to be re-argued from scratch or never to be re-examined. The working group's decision-record template applies, and [Governance](../governance/) covers how profiles evolve after publication.

## Stage 5 — Proof

### Step 12. Build the examples and run them

Produce at least two documents: one that conforms and one that fails for a specific, stated reason. Implement the rules in machine-readable form and run a validator over both. A profile has not been tested until its rules have been run. The failures this step finds are usually in the attribute definitions, not in the tooling.

Expect to return to stage 2. An attribute that reads well in prose can turn out to be ambiguous when a validator has to decide whether a document satisfies it. This happens most often with conditional attributes and with attributes whose value is a list.

## Releasing a profile as a family of depths

A profile that asks for everything a mature producer could supply will not be met by any producer at the start. A profile set at what producers can supply today will still be set at that level in three years. The usual answer is to publish a family of profiles ordered by depth, with each depth asking for more than the one before (see [Maturity](../maturity/)). Two rules keep this approach honest.

**Every depth supports a decision of its own.** A depth is a profile, so rule C1 applies to it. Each depth names a consumer and a decision, and states the options that the consumer chooses between. It is tempting to build the first depth from the attributes that are cheapest to produce. A supplier could be certified against such a depth, but a consumer could not use it to make any decision. The first depth should therefore be the smallest set of questions that answers a real decision, and not the set of easiest questions.

**What a depth defers, it still asks about.** A depth may leave the detail of a subject to a deeper profile, but it does not leave out the subject itself. For example, a profile that requires full detail for key establishment can require a one-word status for entity authentication, and it should. The status costs the producer a single enumerated value. It tells the consumer where the work with the longest lead time stands. It also gives the next depth a starting point to improve on. Without the status, the deferred subject is simply absent from the document, and the first depth becomes a permanent floor. SBOM minimum elements fell into this pattern, as described in [Challenges](../challenges/).

A separate question is who sets the date after which a depth is no longer acceptable. A profile should not set that date. A profile cannot know a given consumer's risk position. A standards body that sets commercial deadlines for parties it has no relationship with also tends to be ignored. The profile gives each depth a name and makes it checkable. A contract between the parties sets when a particular depth is required.

## When a profile is finished

The criteria for a first release, as opposed to a perfect one:

-   The consumer and the decision are stated, and the decision contains a choice.
-   Every attribute traces back to a question, and every question to the decision.
-   No attribute encodes a judgement that policy should make.
-   No rule names a product, a vendor, or an interface instance.
-   For every attribute, the profile defines what absence means, including whether the attribute may be withheld.
-   Structural rules exist, so that missing items can be detected.
-   Exclusions are written down with reasons.
-   A mapping exists for at least one format, with a stated acceptance range.
-   A conforming and a non-conforming example exist, and a validator agrees with both.

## Ways this goes wrong

Six failure modes, each observed while building the worked example in this documentation.

| Failure | How it shows up | Remedy |
| --- | --- | --- |
| Starting from the format | The attribute list resembles the fields CycloneDX offers, and no attribute traces to a question. | Return to step 1 and derive the questions before looking at any schema. |
| No named decision | The profile grows during review because every suggestion seems reasonable and nothing rules anything out. | State the decision as a choice. Suggestions that do not affect it are out of scope. |
| Encoding a judgement | An attribute such as a readiness rating, whose correct value changes when guidance changes. | Keep the inputs and move the conclusion to an external policy. |
| Naming an instance | A rule requires a particular identifier value, so the profile only applies to one product. | Constrain kinds and counts. The baseline profile in this documentation was corrected for exactly this. |
| A depth that becomes a permanent floor | A profile addresses part of the problem and says nothing about the rest, so a supplier conforms while a whole subject is absent from the document and no later profile has a baseline to improve on. | Require a statement of position for what the profile defers, even where it requires no detail. One enumerated value costs a producer almost nothing. Without it, the depth becomes a permanent floor that later profiles do not build on. |
| Treating absence as one thing | A consumer cannot distinguish a producer that lacks the data from one withholding it. | Apply the four disclosure outcomes, and decide for each attribute whether a producer may withhold it. |

## Worked application

The [PQC Migration](../../use-cases/pqc-migration/) section applies this procedure end to end for a product treated as a black box, and is the reference example. The [Profile](../profile/) section describes the resulting baseline profile in its finished form, and the [Demo](../demo/) section runs stage 5 in the browser.

The procedure exists to keep two properties true of whatever it produces: that every requirement can be traced to a decision somebody is making, and that no requirement names the product it was first written for.

[← Starting from a Use Case](../use-cases/) [Next: Formats →](../formats/)
