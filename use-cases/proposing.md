---
title: Proposing a Use Case
sideMenu: true
weight: 10
aliases:
- /cbom/use-cases/proposing.html
linkTitle: Proposing a Use Case
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

How a use case enters this section, how it is developed into a worked example, and what each status means. Read this before copying the [template](../template/).

## When a use case is worth proposing

A use case is worth proposing when a consumer and a decision can be named, and the facts that decision needs are not already required by the interface disclosure baseline. A use case is not a sector, a product, or a field that a format happens to offer. A profile written by starting from a format's fields has no stated purpose. There is then no basis for arguing whether it asks for the right things.

1.  Open a topic on the [aspect issues](https://github.com/pkic/cbom/issues) stating the consumer, the actions being chosen between, and the questions that decision raises.
2.  Add it to the register on the [overview](../) and to its group page as *proposed*. If it fits none of the groups, raise that first. It may need a new group, or it may not be a use case at all.
3.  Copy the [template](../template/) and work down it. Open a pull request even if the page is only half filled in. The blank sections show the working group what it still has to answer.

A use case may turn out to be served by an existing profile, by a depth of an existing profile family, or by the change core alone. A depth is a version of a profile that asks for more or fewer of the same facts. Any of these is a better outcome than a new profile. Argue for the use case on that basis.

## Status

| Status | What it requires |
| --- | --- |
| **Proposed** | A consumer and a decision are named. Nothing more has been written. This status invites others to develop the use case. It does not commit the working group to writing a profile for it. |
| **Described** | The consumer, the decision, the constraint the producer is under and what the profile would need are written on the group page. |
| **Draft worked example** | A page in the eight-part shape below exists. Some of its rules, documents or verdicts are not yet settled. The page says which ones. |
| **Worked example** | A rules file that passes requirements C1 to C17 of [Conformance](../../methodology/conformance/), at least one document that conforms to it and one that does not, and verdicts checked with the validator. |

## The shape of a worked example

Every worked example follows the same eight parts, in the same order, because each part is the input to the next. The eight parts are the twelve steps of [Method](../../methodology/method/), grouped to suit a reader rather than someone carrying out the steps. The [template](../template/) is the same shape as a blank.

1.  **The decision being supported.** Who the consumer is, what actions it is choosing between, and the questions it has to answer to choose. Stating the actions makes the rest checkable. A decision that can only be answered one way is not a real decision. A profile written from such a decision has no principled point at which to stop adding requirements.
2.  **The constraint the producer is under.** What the party filling the document in can actually observe. An operator of its own service can be asked for more than a vendor shipping a product it cannot inspect. A profile that ignores this difference asks for facts the producer cannot supply, so no document can satisfy it.
3.  **From questions to attributes.** Each question is turned into one fact that can be declared at the boundary. Some questions cannot be turned into such a fact. They matter as much as the ones that can, so they are recorded rather than dropped.
4.  **The profile definition.** The product-level, per-interface and group rules, with their conformance levels; any rule inherited from a base profile that this one tightens; and any rule that applies only under a stated condition.
5.  **A worked interface.** One real interface with every required attribute filled in, so the rules can be read against something concrete rather than in the abstract.
6.  **What the profile deliberately excludes.** Each exclusion with its reason. Without this list, the profile cannot be reviewed. A reader cannot tell an attribute that was deliberately excluded from one that nobody thought of.
7.  **Expressing it in a CBOM.** How the attributes land in CycloneDX and SPDX, and which of them the formats have no native field for.
8.  **Recorded decisions and open questions.** What was settled while writing it, and what the working group has not settled.

## Why worked examples are kept out of the methodology

-   **The number of worked examples keeps growing, and the specification should not grow with it.** If each worked example were part of the methodology, the length of the deliverable would depend on how many use cases exist.
-   **They have different readers.** Someone assessing the methodology needs one example. Someone with a migration to plan needs the worked example for their own case in full.
-   **They are governed differently.** A profile is versioned and stewarded on its own schedule, as [Governance](../../methodology/governance/) sets out.

[← Substation Automation (OT)](../substation/) [Next: Template →](../template/)
