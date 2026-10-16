---
title: IoT Device Estate
sideMenu: true
weight: 6
aliases:
- /cbom/use-cases/iot.html
linkTitle: IoT Device Estate
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

This use case follows the shape of the [template](../template/). It is developed as far as it can be without decisions from the working group. The sections that could be argued from the methodology are written. The sections that need a decision are marked and left open. Nothing here is a profile yet, and no rules file exists.

Draft for discussion. The attribute names below are proposals made on this page, not established terms, and the profile has not been written, validated or tested. See [what this page needs next](#what-this-page-needs-next).

## Choosing the decision

The term "IoT" on its own does not identify a consumer or a decision. It identifies a class of subject: devices that are numerous, constrained, deployed somewhere nobody visits, and expected to keep working for a decade or more. Several different consumers make several different decisions about that class, and they need different profiles.

So the first piece of work is choosing which decision to develop. Three candidate decisions are plausible. They are three separate decisions, not three descriptions of the same decision.

| Candidate | Consumer and decision | Why it might be the one |
| --- | --- | --- |
| **Fleet remediation**
proposed | An operator of a deployed estate deciding, per device model, whether to update it, replace it, put something in front of it, or accept it | The device constraints described above matter most for this decision, and no existing profile serves it. The migration profile assumes that an interface can negotiate its algorithms and that the device has an update path. A large part of an IoT estate has neither. |
| Device procurement and certification | A buyer or certification body checking a device against a scheme before it is bought or placed on the market | It is close to the [procurement](../disclosure/#procurement-and-tender-conformance) and [compliance](../assurance/#regulatory-and-compliance-reporting) entries already in the catalogue. A more detailed version of one of those profiles (a "depth", in the methodology's terms) may serve it. In that case it would not need a profile of its own. |
| Manufacturer support planning | A manufacturer deciding which of its shipped models to carry forward and which to end | The producer and the consumer are the same party. That is different from every other use case here. Because the manufacturer would be producing the document for itself, this use case probably needs no disclosure profile at all. |

The rest of this page develops fleet remediation. The other two candidates are recorded to show that fleet remediation was chosen deliberately from several options.

## 1 · The decision being supported

An operator runs an estate of devices it did not build, cannot inspect, and in most cases cannot reach without sending somebody. Cryptography on some of those devices will have to change. For each device model in the estate the operator is choosing between four actions. The four actions differ in cost by orders of magnitude.

-   **Update in place.** New firmware carries the new algorithms. This is the cheapest action, and it is available for only a minority of the estate.
-   **Replace.** This happens on a schedule. The cost is the unit cost multiplied by the number deployed, plus the cost of reaching each device physically.
-   **Put something in front of it.** Terminate the protected session at a gateway that can carry the new algorithms, and leave the device alone. This is cheap where the topology allows it, and impossible where the device talks directly to the outside.
-   **Accept and document.** The device outlives the exposure, or the data it carries does not warrant the spend. This is a legitimate answer, but it has to be defensible.

The operator chooses between the four actions by answering five questions.

-   Can this model carry the algorithms at all, or do its memory, compute and message-size limits rule them out whatever firmware it runs?
-   Is there a mechanism to get new firmware onto it, who is able to trigger that, and for how long will it still be offered?
-   Is the key material replaceable, or was it fixed at manufacture?
-   Does the cryptography for this interface terminate on the device, or somewhere the operator controls?
-   How long will this model stay in the field, and does that outlast the exposure?

Only the third question (replaceable keys) and the fourth (where the cryptography terminates) are close to anything the interface disclosure baseline asks. The baseline is the base profile that other disclosure profiles extend. The first question asks for a fact about the device rather than about an interface, which is unusual. The second question asks for a fact about a process, which is even more unusual. The second question is the one most likely to be disputed.

## 2 · The constraint the producer is under

The black-box constraint applies, as it does to every profile whose producer is a vendor. Under that constraint the vendor will not expose the product's internals, so every attribute must be declarable at the product's boundary. Four further constraints apply here. Because of these four constraints, IoT fleet remediation is a separate use case, not a sector-specific version of PQC migration.

### The producer knows the model, not the deployment

A device manufacturer knows what it shipped. It usually does not know how any particular unit was configured, what it was connected to, or whether it is still switched on. The CBOM therefore describes a device model, while the operator's decision is made about individual deployed units of that model. The operator has to add everything that varies per instance from its own inventory. The CBOM does not carry it.

{{< figure src="../assets/figures/use-cases-iot-1.svg" alt="A device model on the left is the subject of the CBOM; many deployed instances in the middle are what the operator decides about; a gateway sits between the instances and the outside" >}}

*The subject of the document and the subject of the decision are not the same object. A profile for this use case has to be explicit about which one each rule is about, and has to accept that the operator supplies the rest.*

### Some limits are set by physics, not by design choices

Elsewhere in this methodology, a statement that an interface cannot do something describes what has been built. A different implementation could change the answer. On a constrained device, the same statement is often about available flash, available RAM, or a frame size fixed by a radio standard. No firmware release changes those. This is the only use case here in which a capability answer of "no" can be permanent. If a profile cannot distinguish a permanent "no" from a temporary one, it effectively tells an operator to wait for an update that will never come.

### The party who can update may be neither the vendor nor the operator

Firmware often reaches a device through a third party: a connectivity provider, a platform operator, an installer with physical access. The operator making the decision may have no relationship with that party. A profile that records only whether an update exists, and not who can cause it to happen, leaves the operator unable to tell an action it can actually take from one that exists only in theory.

### Field life outlasts the support commitment, and sometimes the vendor

A device installed today may still be running in fifteen years. The commitment to ship firmware for it will not last that long, and neither, in some cases, will the company that made it. This is the same problem as the long-term stewardship question that the working group already tracks. In this use case the problem appears on the device side rather than on the profile side.

## 3 · From questions to attributes

Each question from section one is turned into facts that a manufacturer could declare about a model. The Status column says whether each attribute already exists. The balance between existing and new attributes decides how much of this is a new profile. It also decides how much is a tightening of an existing profile, meaning stricter requirements on attributes that profile already has.

| What the consumer needs to know | Proposed attribute | Status |
| --- | --- | --- |
| What is this interface and what does it speak? | `interfaceType`, `protocol`, `protocolVersionsSupported` | Baseline. The value set for `interfaceType` probably needs extending; see below. |
| What is it doing now, and what else could it do? | `keyExchange`, `authentication`, and their `Supported` counterparts | Baseline and migration profile. |
| Could any firmware carry the new algorithms, given what the hardware is? | `resourceBound` | New. The hard limits that bound what this model could ever negotiate: usable flash and RAM headroom, and the maximum frame or message size the link imposes. |
| Is there a way to get new firmware onto it? | `updateMechanism` | New. `none` · `physical-access` · `local-network` · `remote-managed`. |
| Who can trigger that? | `updateAuthority` | New. `operator` · `vendor` · `platform` · `installer`. This attribute separates an available action from a theoretical one. |
| Will firmware still be offered? | `updateSupportStatus` | New. A commitment class rather than a date, following decision 0007: `supported` · `limited` · `ended` · `never-offered`. |
| Can the keys be replaced? | `keyProvisioning`, `keyReplaceable` | New. Where key material came from, and whether anything short of replacing the device can change it. Factory-injected material that cannot be rotated is the case that turns an update decision into a replacement decision. |
| Where do key operations execute? | `providerLocation` | Migration profile, but the value set is wrong here: `software`, `hsm`, `tee` and `unspecified` do not cover a secure element, an MCU's internal flash, or one-time-programmable fuses. |
| Does the cryptography terminate on the device? | `cryptoTerminationPoint` | New. `device` · `gateway` · `both`. The compensating-control option depends on this attribute. It is also the one most likely to be contested, because it is arguably a deployment fact rather than a product fact. |
| What breaks if we do change it? | `integrationConstraints` | Migration profile. It matters more here than elsewhere, because a post-quantum handshake may not fit within the device's resources or the link's message size. |
| How much should we trust this record? | `lifecycleStage` | Baseline. |

### Interface types a device has that a server does not

The baseline's product rule P2 requires a management interface or a statement of why there is none. That rule was written for products that are administered. Many devices are not administered at all. The escape clause in P2 (stating why there is no management interface) covers them. A profile for this use case should still say so explicitly, so that each producer does not have to work it out alone. Four kinds of interface recur on devices and have no obvious place in the current value set for `interfaceType`: a provisioning or onboarding interface used once and never again, a firmware update channel, a radio link with cryptography fixed by its own standard, and a telemetry uplink that is one-way.

### Questions that may not survive

Two of the five questions from section one may not be answerable by a document at all. That result is a finding about what a CBOM can carry, not a gap to be filled.

**How long the model will stay in the field** is a fact about the operator's estate, not about the product. The manufacturer can state how long it will support the model, which is `updateSupportStatus`. How long the operator will keep running it is the operator's own planning input.

**Whether a gateway can carry the cryptography instead** is a fact about a deployment. `cryptoTerminationPoint` is an attempt to get at the part of it that is a product fact: whether the device's design permits termination elsewhere. Whether it has been deployed that way is not something the document can say.

## 4 · The profile definition

One structural question has to be answered before any rule can be written: which profile does this one extend? This profile is not a deeper version of PQC migration. It supports a different decision, with a different set of actions. It adds attributes that the migration profile has no use for. It also ignores several attributes that the migration profile requires. In the terms used under composition in [Profile](../../methodology/profile/), it is a branch rather than a depth. A branch extends the interface disclosure baseline directly. A depth would extend the migration profile. The question is carried as [Q64](https://github.com/pkic/cbom/blob/main/open-questions.md) because the alternative also has a fair case. The same person often plans both an estate of gateways and an estate of sensors, and two unrelated profiles make that work harder. Draft decision 0023 proposes an answer. Under it, this profile and the migration profile would both extend a shared change core, a common base for change-planning profiles. This profile would remain a branch, but the two profiles would no longer be unrelated.

to fill in

**The relationship to the base**, once Q64 is settled: one table with three rows for inherited, tightened and added.

**Product-level rules.** At least one is needed that the baseline does not have. A device with no update path at all is the most consequential fact in this use case. A rule that is checked only per interface would let it go unstated, because the lack of an update path is a fact about the whole product.

**Per-interface rules** for the attributes in section three, each with a conformance level and a note saying what a consumer does with it.

**Tightenings**, with a justification each. One candidate is already visible: if `resourceBound` is required at MUST then `integrationConstraints`, which the migration profile leaves at SHOULD, is arguably the attribute that explains the resource bound, and should be raised to MUST with it.

**Conditional rules.** Two are implied by section three: `updateAuthority` and `updateSupportStatus` only mean anything where `updateMechanism` is not `none`. A guard is the condition that decides whether a conditional rule applies. A derived profile may remove a guard, but may never add or narrow one.

## 5 · A worked interface

The worked example should be one real interface on one real device model, filled in completely. The most useful candidate is the least convenient one: a battery-powered sensor reaching a gateway over a constrained radio link, where the honest answer to several attributes is that the model cannot do it and never will.

to fill in

| Attribute | Value | What it tells the consumer |
| --- | --- | --- |
| `interfaceId` | … | … |
| `interfaceType` | … | … |
| `protocol` · `protocolVersionsSupported` | … | … |
| `keyExchange` · `keyExchangeSupported` | … | … |
| `authentication` · `authenticationSupported` | … | … |
| `resourceBound` | … | … |
| `updateMechanism` · `updateAuthority` · `updateSupportStatus` | … | … |
| `keyProvisioning` · `keyReplaceable` | … | … |
| `providerLocation` | … | … |
| `cryptoTerminationPoint` | … | … |
| `integrationConstraints` | … | … |
| `lifecycleStage` | … | … |

Then the same interface on a device that *can* be updated, so the two can be read against each other. Read together, the two examples should show that the profile can separate the four actions, not just describe them.

## 6 · What the profile deliberately excludes

Three exclusions can be argued now. A fourth is open.

**No device verdict.** Whether a device model is quantum-safe, or safe at all, is a judgement against criteria that change while the device sits in a field. The profile states facts, and an external [policy](../../methodology/policy-evaluation/) reaches a dated verdict. This matters more here than elsewhere because the device will outlive several revisions of the criteria.

**Nothing per instance.** No serial numbers, no locations, no deployment configuration. The producer does not know them. A profile that asks for them cannot be satisfied by the party that has to fill it in. The operator links the document to the matching entries in its own inventory. [Objects](../../methodology/objects/) sets out why the subject of a document and the subject of a decision are separate objects.

**No firmware component inventory.** What libraries the firmware is built from is an SBOM question. The two questions do overlap. The boundary between a CBOM and an SBOM is the one drawn in [Model](../../methodology/model/). Restating that boundary here would put the same requirement in two places.

to fill in

**Whether the physical attack surface is in scope.** Debug ports, unlocked bootloaders and readable flash decide whether key material can be extracted, which bears directly on whether replacing the device is necessary. It is also a security posture question rather than a cryptographic disclosure question, and admitting it would widen this profile considerably. Whichever way it goes, the group should argue it explicitly.

## 7 · Expressing it in a CBOM

to fill in

Which of the new attributes map to native CycloneDX and SPDX fields and which become properties under the `pkic:profile:` namespace. Most of them will be properties. `resourceBound` is a structure rather than a value and needs the most care.

How the subject is identified, given that it is a model. This is the part to settle first. If a document's subject could be either a model or a unit, it cannot be linked reliably to an estate inventory. Everything the consumer does with the document depends on that link.

What a producer records when it does not know. `unknown` has to be available on the update attributes in particular, because a manufacturer may really not know who can push firmware to a unit it sold through a channel.

## 8 · Recorded decisions and open questions

No decision records yet. Four questions are carried in the [open questions register](https://github.com/pkic/cbom/blob/main/open-questions.md). These four questions have to be answered before the rules can be written.

| # | Question | Topic |
| --- | --- | --- |
| Q62 | Is the subject of a CBOM a device model or a deployed device, and does the methodology need to say which? | 3.3 |
| Q63 | Does the methodology need a way to say that a limit is permanent rather than a current state? | 3.3 |
| Q64 | Is an IoT profile a branch from the baseline or a depth of the migration family? | 3.9 |
| Q65 | May a profile require a fact about a process, such as who can push firmware, rather than about a product? | 3.4 |

## What this page needs next

These are in order, because each step depends on the one before it.

1.  Confirm the consumer and the decision, or pick one of the two alternatives instead.
2.  Settle Q64, which decides what the profile extends and therefore what it may tighten.
3.  Settle Q62, which decides what the subject is and therefore what the product rules can say.
4.  Write the rule tables in section four and the rules file together, then run `check_profile.py` against it for C1 to C17.
5.  Fill in section five with two interfaces, one that can be updated and one that cannot.
6.  Add a conforming and a non-conforming document, and a test in `tests/run-profile-tests.sh` that asserts both.

Until step six, the overview page lists this as a draft. Draft is the correct status for this use case. The page exists to give the working group a draft to debate. A draft that names its consumer and its constraints gives the group something concrete to debate. An empty slot in a table does not.

This use case adds three things to the methodology, whatever is decided about the profile. It is the first use case where a capability answer of "no" can be permanent. It is the first where the party who can act is neither the producer nor the consumer. It is the first where the subject of the document is a class (a device model) and the subject of the decision is a member of that class (a deployed unit). Each of these is a general problem. The IoT sector happens to expose it first.

[← PQC Migration](../pqc-migration/) [Next: Substation Automation (OT) →](../substation/)
