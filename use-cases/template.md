---
title: Worked Use Case Template
sideMenu: true
weight: 11
aliases:
- /cbom/use-cases/template.html
linkTitle: Template
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A blank worked use case, with the same sections as a completed one. Each section below says what belongs in it, why that part has to come before the next one, and how to tell when it is finished. Copy this page, work down it, and delete the instructions as you replace them. The [PQC migration](../pqc-migration/) page is the same shape filled in, and is worth reading alongside this one. How a use case is proposed, and what each status means, is on [Proposing a use case](../proposing/).

This page is scaffolding, not a deliverable. It states no requirement and constrains no profile. If you are looking for what a profile must satisfy, that is [Conformance](../../methodology/conformance/).

## Starting one

There are five mechanical steps. None of them involve writing prose.

1.  Copy this file to `docs/use-cases/<short-name>.html`. The short name becomes part of the URL and is awkward to change later, so pick the consumer's word for the thing rather than the working group's.
2.  Change the front matter `nav:` value to `uc-<short-name>`.
3.  Add one line to its group in `docs/_data/usecases_nav.yml` (Disclosure or Change planning), with the same id. If it fits neither group, raise that before writing anything else.
4.  In the [register](../), set its status to *draft worked example* and link the page in the last column. On its group page, point its entry to the page and add a row to the table of worked examples.
5.  Fix the previous and next links in the footer of this page and of its new neighbours. The footer links on use-case pages are written by hand. `tools/renumber-pagenav.py` manages the footer links on the methodology pages and will not change these.

Then work down the eight sections. They are in dependency order, so work through them in order. Section three cannot be done without section one, and section four cannot be reviewed without section six.

## 1 · The decision being supported

Name the consumer, the actions it is choosing between, and the questions it has to answer to choose. Name all three, not just the consumer. A consumer with no actions to choose between is only an audience. A profile written for an audience has no clear point at which to stop asking for more facts.

The test is whether a reader could disagree with you. "A security team wants visibility of its cryptography" is not a decision and cannot be argued with. "A fleet operator is choosing, per device model, between update in place, replace, and accept with a compensating control" can be: someone can say that a fourth option exists, or that two of these are really one.

to fill in

**The consumer.** Who reads the CBOM and acts on it. Name a role, not an organisation.

**The actions.** There should be two or more. They exclude each other, and each has a different cost. If you can think of only one, the use case is a reporting requirement rather than a decision. That is a different need, and usually a cheaper one to serve.

**The questions.** Three to five of them. Each one has to be answerable from a document, or it belongs to a different process.

**Why the existing profiles do not already answer them.** If the interface disclosure baseline answers them all, stop here and say so on the overview page. That is a good outcome, not a failed one.

## 2 · The constraint the producer is under

Describe what the party filling in the document can actually observe. This section keeps the profile satisfiable, meaning that a producer is able to conform to it. Skipping it is the most common way to end up with a profile that nobody can conform to.

The PQC migration profile has one constraint, the black box. The vendor will not expose internals, so every attribute must be declarable at the boundary, from outside the product. Your use case may have other constraints. A producer may not know how its product is deployed. It may know at manufacture and not afterwards. It may be a different party from the one the consumer is asking.

to fill in

**Who produces the document**, and whether that is the same party the consumer is in a relationship with.

**What they can observe**, and at what moment. Design time, build time, ship time and run time give different answers, and [capture phase](../../methodology/lifecycle/) is how the document says which one it is.

**What they will not disclose** even though they know it. Say whether the profile should let them declare such a fact as [withheld](../../methodology/confidentiality/), or require them to disclose it.

**A diagram, if the constraint is structural.** The migration page includes a diagram of its black box, because the shape of that constraint explains why the profile has the shape it does.

## 3 · From questions to attributes

Take each question from section one and turn it into one fact that can be declared at the boundary. Work in that direction. If you start from the fields a format happens to offer, you get a profile with no stated purpose, and nobody can argue about whether it asks for the right things.

Record the questions that cannot be turned into attributes. A question that cannot be turned into a declarable fact shows a limit of what a CBOM can carry. That is more useful written down than dropped.

to fill in

A two-column table: *what the consumer needs to know* against *the attribute that supplies it*. One row per question, and more than one row per question where the answer needs several facts.

For each attribute, say whether it already exists in the baseline, exists under a different name, or is new to this profile. Reusing a name means inheriting its meaning. [Method](../../methodology/method/) has the naming conventions, and they are not optional.

Then the questions that did not survive, with the reason each one failed. The usual reasons are that the producer cannot observe it, or that it is a judgement rather than a fact.

## 4 · The profile definition

The rules. State which profile this one extends, then list what it adds and what it tightens. Do not restate inherited rules as though they were yours. The base profile stays authoritative for them, and repeating them means one requirement has to be maintained in two places.

Rules are numbered in this profile's own sequence, starting from `P1` for product rules, `I1` for per-interface rules and `G1` for group rules. They are cited against this profile's tag. A tightened rule keeps the id of the profile that introduced it. [Profile](../../methodology/profile/) has the scheme and [Objects](../../methodology/objects/) has the identity rules.

to fill in

**The relationship to the base.** One table with three rows: inherited unchanged, tightened, added.

**Product-level rules**, **per-interface rules** and **group rules**, each with a conformance level and a note saying what the rule is for. The note is what a reviewer argues with.

**Every tightening, with its justification.** A tightening removes an option the base profile deliberately offered, so each one needs a reason. Extension is monotonic: a profile may add rules and tighten them, but may never relax them.

**Conditional rules.** A rule that applies only under a stated condition, with the condition written as something checkable rather than as advice.

Write the rules file at the same time as this table, not afterwards. Two statements of the same rules drift apart within a week, and the file is the one a tool reads.

## 5 · A worked interface

One real interface with every required attribute filled in, so the rules can be read against something concrete. Reviewers use this section most. It often shows problems that the rule table hides: an attribute with no sensible value, two attributes that cannot both be true, a MUST that the producer has no way to satisfy.

to fill in

One interface, named and typed, with each attribute the profile requires and a plain-language column saying what the value tells the consumer.

At least one attribute where the honest answer is `unknown` or withheld, if the profile permits either. A worked example in which everything is known does not test the case the profile has to survive.

## 6 · What the profile deliberately excludes

List each exclusion with its reason. Without this section, the profile cannot be reviewed. A reader cannot tell an exclusion that was argued for apart from an attribute that nobody thought of.

Two exclusions are likely to apply to any profile and are worth stating even when they feel obvious. Verdicts and scores belong in a [policy](../../methodology/policy-evaluation/) rather than a profile, because the criteria change and the document does not. Internal implementation detail is out of scope wherever the producer is a vendor. Asking for it produces a profile that nobody satisfies.

to fill in

Each excluded attribute or class of attribute, with the reason. "Not needed for this decision" is a reason. "We could not agree" is also a reason, and should be recorded as an open question rather than presented as a choice.

Anything a reader of the base profile would expect to see here and will not find.

## 7 · Expressing it in a CBOM

Show how the attributes are encoded in each format, and which of them have no native field. The attribute list is independent of any format by design. This section maps that list onto CycloneDX and SPDX. [Formats](../../methodology/formats/) has the encoding conventions.

to fill in

Which attributes map to native fields, and which are carried as properties under the `pkic:profile:` namespace.

Anything structural that the mapping makes awkward. The usual problem is an attribute that holds a list where the baseline holds a single value. The usual failure is a consumer that cannot tell an empty list from an absent one, or either of them from a withheld one.

What the four disclosure outcomes mean here, and specifically what a producer should record when it does not know rather than guessing.

## 8 · Recorded decisions and open questions

Record what was settled while writing the use case, and what was not. A decision taken during the work and not written down will be reopened, usually by the person who took it.

to fill in

**Decision records** for any choice made against a more obvious alternative. One file in `decisions/` each, with the options, the rationale and what reversing it would involve, plus a row in the decisions README. Summarise them here and link to them. The record is authoritative, not the summary.

**Open questions** added to `open-questions.md`, each mapped to one of the thirteen topics, each with its options and their trade-offs. Cite them by number here.

## Before it counts as developed

The overview page lists a use case as developed only when three things exist. A reader can check all three without taking anyone's word for it.

-   A rules file that passes requirements C1 to C17 of [Conformance](../../methodology/conformance/). Run `check_profile.py` against it.
-   One document that conforms to the profile, and one that does not. The second is the one that matters. If no document has ever failed a profile, nobody has shown that the profile constrains anything.
-   A test in `tests/run-profile-tests.sh` that asserts both outcomes, including the exit status.

Until then, the page is a draft. Draft is an acceptable status. Label the page as a draft rather than avoiding that status. A draft that names its consumer and its decision is already more useful to the working group than a finished profile whose purpose has to be worked out from its rules.

The pattern to take from this template: name the consumer and the decision, derive the questions that decision raises, and turn each question into an attribute that can be declared at the boundary. The rest of this template is record-keeping that supports those three steps.

[← Proposing a Use Case](../proposing/)
