# Open questions register

Working note for the PKI Consortium CBOM Profiles Working Group.
Compiled 7 August 2026. Rewritten 9 August 2026 for a general reader.

## What this document is for

The working group is writing a methodology for defining CBOM profiles. While drafting it, a
number of questions came up that the group has not settled. They were recorded wherever they
arose, which left them scattered across six sections and two working notes.

This register collects them in one place so that a meeting agenda can be set from a single list.
Each question is mapped to one of the thirteen topics the group already tracks as GitHub issues,
so an item can be posted to the issue that covers it.

Forty-eight questions sit under those thirteen topics. Four more do not fit any of them, which
is itself worth knowing, and they are listed at the end.

Q36 to Q44 were added on 9 August 2026 in response to member feedback, covering the
harvest-now-decrypt-later threat, asset identity, end-to-end posture, long-term stewardship, and
the relationship to the PQC Maturity Model. The resolution plan for that feedback is in
`plan-feedback-2026-08.md`. Q36 was then restated and Q45 added after review found that the
original treatment of data facts was wrong for one class of interface; the reasoning is in
`design-note-data-and-hndl.md`.

Q46 and Q47 were added on 21 August 2026, and Q08 restated, after member feedback on
financial-sector systems. The feedback attributed the gap to Q08; the reasoning for separating it
into two cheaper questions, and for leaving Q08 where it stands, is in
`design-note-multiparty-trust.md`.

Q48 was added on 21 August 2026 after a review found that the SPDX column of the format mapping
described a structure the linkage arrangement does not produce.

## Who this is written for

Both a technical reader and a policy reader. Several of these questions look like implementation
detail and are not: they decide what a supplier has to tell a buyer, what a buyer may rely on,
and what a regulator can ask for. Those consequences are the point, so each entry states them in
plain language first.

Every entry follows the same shape:

- **The question**, in one or two sentences without jargon.
- **Why it matters**, saying who is affected and what goes wrong while it is unsettled.
- **The options**, with the argument for each.
- **Where it stands**, describing what the current draft does.
- **What would have to change**, listing the documents and files affected. A policy reader can
  skip this part.

The register makes no recommendation. Where the draft has already taken a position it says so as
a fact, because the cost of reversing it is part of what the group is weighing.

## Terms used throughout

| Term | Meaning |
|---|---|
| CBOM | Cryptography Bill of Materials. A document listing the cryptography a product uses and where it uses it. |
| Profile | A list of the facts a CBOM has to contain for one purpose. A minimum reporting bar, not a full description. |
| Attribute | One fact a profile asks for, such as which key exchange algorithm an interface uses. |
| Interface | A point where a product applies cryptography with another party, such as a web connection or an administrative login. |
| Rule | One requirement in a profile, covering a single attribute or the set of interfaces as a whole. |
| MUST, SHOULD, MAY | How binding a rule is. Only MUST rules decide whether a document passes. The terms come from BCP 14, used across internet standards. |
| Conformance, verdict | Whether a document meets a profile. The result is conforms, does not conform, or refused. |
| Withheld, unknown, undeclared | Three reasons an attribute may carry no value: the supplier will not say, the supplier does not know, or the supplier never addressed it. A profile decides which of these it accepts. |
| Baseline profile, derived profile | A general profile, and a more demanding one built on top of it. A derived profile may add requirements and make existing ones stricter. It may never make them looser. |
| Tightening | A change that makes a profile stricter, so a document that passed before may now fail. |
| Carrier format | The file format a CBOM is written in. The examples use CycloneDX; SPDX is the other main option. |

**Status values.** `open`, `drafted`, `blocked`, `deferred`, `decided`. A `drafted` item has a
position written into the methodology and is waiting for the group to accept or reject it.
Nothing has been ratified.

Identifiers are stable. An item moved to a different topic keeps its number. When something is
settled, add a decision record under `decisions/` and mark the item `decided`. Items are not
deleted.

## Index

| Topic | Items |
|---|---|
| 3.1 What a profile is for, and its scope | Q01, Q02 |
| 3.2 Naming and versioning a profile | Q03, Q04 |
| 3.3 The list of attributes | Q05, Q06, Q07, Q08, Q09, Q34, Q36, Q37, Q45, Q46, Q47 |
| 3.4 How binding each rule is | Q10, Q11, Q12 |
| 3.5 Checking conformance | Q13, Q14, Q15, Q31, Q32 |
| 3.6 Writing a profile into a file format | Q16, Q17, Q18, Q48 |
| 3.7 Agreed names for algorithms and protocols | Q19, Q20, Q21, Q38, Q39 |
| 3.8 How a CBOM relates to an SBOM | Q22, Q40 |
| 3.9 Building one profile on another | Q23, Q24, Q25, Q33, Q35, Q49, Q50, Q51, Q52, Q53 |
| 3.10 Statements about the future | Q26, Q27, Q28 |
| 3.11 Governing a profile over time | Q29, Q41, Q42 |
| 3.12 Fitting regulation and policy | Q43, Q44 |
| 3.13 Examples and tooling | Q30 |
| No matching topic | N01, N02, N03, N04 |

---

# 3.1 What a profile is for, and its scope

Tracked as issue #4.

## Q01 — Is the PQC migration profile a real specification or a worked illustration?

**Status** open

**The question.** The group has produced a second profile covering post-quantum migration. Is it
something a supplier can be held to, or an example showing how a profile is built?

**Why it matters.** Buyers are asking suppliers for post-quantum readiness information now, and
there is no agreed form for the answer. If this profile is a specification, buyers and suppliers
can converge on it immediately. If it is an illustration, everyone keeps inventing their own
version, which is the fragmentation the methodology exists to prevent. But calling it a
specification too early locks in choices the group has not argued yet, and correcting them later
would break anyone who adopted it.

**Option A: treat it as a specification.** It is complete. It has machine-readable rules, a
passing and a failing example, and it satisfies the group's own quality checks. Suppliers asked
for this information have nothing else to point at, and the need is immediate.

**Option B: treat it as an illustration.** Three of its attributes are unresolved, covered by
Q05, Q06 and Q27. Publishing it as binding freezes those before they have been discussed, and
fixing them afterwards would make a stricter profile that existing documents fail.

**Where it stands.** The draft calls it illustrative while shipping it as a complete working
artifact. The two signals conflict, and readers will follow the artifact.

**What would have to change.** A specification would need an identifier outside the `example`
namespace, covered by Q03. Q05, Q06 and Q27 would become blocking. The August release scope
(N03) would have to say whether it is included.

## Q02 — Can a profile require a product to be built a certain way, or only require disclosure?

**Status** open

**The question.** The example profile says a product must declare an administrative interface.
That reads as a requirement about the product itself, not about the document describing it.

**Why it matters.** This is the difference between a reporting standard and a product standard.
A reporting standard says what you must tell people. A product standard says how you must build
things. Members will react differently to the two, and regulators citing the methodology need to
know which it is. There is also a practical problem: as written, the rule cannot tell a product
that genuinely has no administrative interface from one that has a hidden one it did not
disclose, and those are very different situations for a buyer.

**Option A: disclosure only.** A profile describes what a document must contain. Requiring a
product to have a particular interface belongs in a purchasing contract. The rule would be
restated as a condition: if such an interface exists, it must be declared. That wording is
unenforceable against a supplier who simply says none exists, and the rule format does not
currently support it.

**Option B: allow requirements about the set of interfaces.** Counting rules are the only way to
catch an incomplete disclosure, and incompleteness is what buyers worry about most. Without them
a supplier could describe one interface perfectly, omit five, and pass. The appearance of a
product requirement is an acceptable side effect.

**Where it stands.** Option B. The Conformance section is explicit that passing does not prove
every relevant interface was declared.

**What would have to change.** The rule format, the rule itself, both example documents, and one
row of the table in the Conformance section listing what a pass does not prove.

---

# 3.2 Naming and versioning a profile

Tracked as issue #5.

## Q03 — Who may publish a profile under a PKI Consortium name?

**Status** open

**The question.** The two examples are named `pkic.example.interface-disclosure` and
`pkic.example.pqc-migration`. The `pkic` part suggests consortium authority. Nothing says who is
allowed to use it.

**Why it matters.** When a supplier claims conformance, the profile name is what the buyer
checks. A name anyone can use tells a buyer nothing about whether the profile was reviewed. This
is the same problem trust marks have: the value is in who controls the mark.

**Option A: the consortium keeps a register.** The consortium allocates names when it adopts a
profile. A buyer seeing `pkic` knows the profile went through working group process. Someone has
to maintain the register, and a sector body wanting to move quickly has to wait for it.

**Option B: authors name profiles in a space they already control.** A company or sector body
uses its own domain name as a prefix, in the way software packages are named. This needs no
administration and makes the origin obvious. Nothing then distinguishes a carefully reviewed
profile from one written in an afternoon, so the burden of judging falls on the buyer.

**Option C: both.** Anyone may publish under their own name, and the consortium maintains a
published list of profiles it has reviewed.

**Where it stands.** No rule exists. The examples use `pkic.example` by habit.

**What would have to change.** The names in both rule files, one requirement in the Conformance
section, possibly a check in the profile checker, and Q01, since a profile intended as a
specification would need a name outside `example`.

## Q04 — Does a profile need a new version when a new file format release appears?

**Status** open

**The question.** A profile records which versions of the carrier file format it was tested
against. When a new release of that format appears and the profile is checked against it, no
requirement has changed. Does that still count as a new version of the profile?

**Why it matters.** It looks like housekeeping and is not. The profile sorts documents into
bands: fully supported, older but still accepted, and newer than anything tested. When the tested
version is raised, documents move between bands. A result that came with a caution attached can
lose the caution without anything about the document changing. A conformance claim is supposed to
be reproducible, so an auditor re-running a check months later should get the same answer with
the same caveats. That property breaks if the profile version does not capture the change.

**Option A: no new version.** Version numbers should signal changes to requirements. Incrementing
for maintenance trains readers to ignore version changes, which weakens the signal when a real
tightening happens.

**Option B: a new version.** Reproducibility is the reason claims cite a version at all. If two
checks under the same version can differ in the caveats they carry, the claim is not
reproducible.

**Option C: a third number.** Record maintenance in a separate component of the version, leaving
the main numbers for requirement changes.

**Where it stands.** The draft records this kind of change as editorial, implying Option A,
without stating a rule.

**What would have to change.** The changelog convention in both profiles, the Versioning section,
and the reproducibility statement in the Conformance section.

---

# 3.3 The list of attributes

Tracked as issue #1.

## Q05 — Can switching on a capability require more than one kind of change?

**Status** open

**The question.** The migration profile asks a supplier how a buyer turns a capability on. The
answer is one of: already on, a configuration change, a software update, a hardware change, a
licence, or not available. Only one may be given. Real capabilities often need two.

**Why it matters.** A buyer planning a migration across hundreds of systems is costing the work.
Firmware updates, configuration changes and hardware replacement have very different costs and
very different approval paths. If a supplier can only name the largest one, the buyer discovers
the rest during the rollout, which is where migration programmes stall.

**Option A: one answer.** The list runs roughly from cheapest to most expensive, so the biggest
step is the one that governs the plan. It keeps the rule simple and keeps a dependent rule simple
too: naming a minimum product version is required only when the answer is a software update.

**Option B: allow several.** A plan needs every step, and the omitted configuration change is
exactly what causes a rollout to stall. This makes the dependent rule more complex, and under the
group's naming convention a field holding several values takes a plural name, so the field would
have to be renamed.

**Option C: one governing answer plus an optional ordered list of steps.**

**Where it stands.** Option A.

**What would have to change.** The field name under the plural convention, the dependent rule,
the part of the validator that evaluates conditions, and both migration examples.

## Q06 — Should "what might break" be free text or a set of categories?

**Status** open

**The question.** The migration profile asks what is likely to break when a capability is turned
on. Today the answer is a sentence in free text.

**Why it matters.** The information is genuinely useful: larger post-quantum keys can exceed
network size limits, network equipment can reject unfamiliar algorithms, and hardware
acceleration can be lost. But an operator with several hundred interfaces cannot read several
hundred sentences and find the pattern. A buyer wanting to know how many systems share one
problem has no way to ask.

**Option A: free text.** It is what suppliers will actually write. A fixed set of categories that
does not match a supplier's real constraint produces either a wrong label or an empty field, and
an empty field is worse than an accurate sentence.

**Option B: categories.** A short list, covering network size limits, intermediate equipment,
performance and interoperability, would let a planner find every affected interface in one query.
Free text can sit alongside for detail.

**Option C: a category plus a description**, repeated as often as needed, so aggregation works
where the category fits and nothing is lost where it does not.

**Where it stands.** Option A, at SHOULD level, and a supplier may decline to answer.

**What would have to change.** One rule, possibly a new list of categories, and the field would
become multi-valued, which engages the plural naming convention.

## Q07 — Should the list of attributes be published as a document in its own right?

**Status** open

**The question.** The attribute definitions currently live inside the methodology, alongside the
procedure and the worked examples. Should they be separated out?

**Why it matters.** This one is mainly for policy readers. A regulator or sector body writing a
requirement wants to point at a definition of a term and cite it. Citing a definition that sits
inside a long methodology document means citing the whole thing, including material that changes
for unrelated reasons. A separate document could stabilise sooner and be referenced cleanly.

**Note.** This item may not be a live question. It appears as an example row in the decision
index, and may have been written to show the format. The group should confirm which, and close it
if it is a placeholder.

**Option A: separate document.** The definitions are the part other bodies will cite. Separating
them gives a stable reference with its own version.

**Option B: keep them in the methodology.** The definitions depend on the underlying model and
the naming conventions. Separating them invites citation without the context that makes them
precise, and one document with one version is easier to govern.

**Where it stands.** The definitions are spread across three sections, with the Terms section as
the collected reference. No separate document exists.

**What would have to change.** Whether the Terms section becomes a versioned document, and how
the rule files point at definitions.

## Q08 — How should the model describe cryptography under a key shared among many parties?

**Status** open

**The question.** The methodology describes cryptography as something applied between two
parties. Some systems apply it among many at once, under a shared key, with members joining and
leaving.

*Restated 21 August 2026.* This question was originally titled "shared among many parties", which
is broad enough to cover two different situations with very different costs. It covers only the
first of them:

- **A shared key.** n parties hold one key at one time. Splitting the group into pairs loses the
  key and the membership, so no pairwise description of the system is true. That is this question.
- **A shared trust anchor, or one signer and many verifiers.** Many parties, but each holding its
  own keys under a common anchor, or one signature verified by a population. These decompose into
  pairwise relationships without loss. Separated out as Q46 and Q47, and much cheaper to settle.

The distinction is set out in `design-note-multiparty-trust.md`. It matters because financial
messaging and settlement systems were raised as a case for this question and are, on the evidence
available, an instance of the second kind.

**Why it matters.** This affects which sectors the methodology can serve. Group cryptography is
normal in broadcast and multicast systems, group messaging, and some industrial, utility and
satellite networks. Splitting a group into pairs loses both the shared key and the membership,
so a CBOM built that way would misdescribe the system. If the group intends the methodology to
cover those sectors, the model has to say so.

**Option A: leave it out of scope.** Most subjects are covered by the two-party description, and
adding a group construct complicates the model for every reader to serve a minority. A sector
that needs it can extend the methodology.

**Option B: generalise now.** Describe cryptography as applied among a set of parties, with two
being the common case. This is a change to a core definition, so it is cheap now and expensive
once profiles and file mappings assume two parties.

**Option C: add a separate kind** for group cryptography, with its own attributes covering
membership and rekeying.

**Where it stands.** Option A, stated openly. The Model section describes the limitation and one
rule requires at least two parties.

**What would have to change.** The definitions in the Model and Terms sections, one rule, the
file mapping, and any claim that the methodology suits sectors where group cryptography is
routine.

**What would settle it.** Whether any sector the group intends to serve uses a key held by more
than two parties at once, as against per-participant keys under a common anchor. Broadcast and
multicast clearly do. Whether settlement and payment rails do is an open factual question and is
recorded under Q47.

## Q09 — Should the file formats gain a proper object for a cryptographic connection?

**Status** deferred

**The question.** Neither CycloneDX nor SPDX has a way to describe a connection where
cryptography is applied. Both describe components. The methodology works around this by
describing each connection as if it were a component.

**Why it matters.** This is the central gap between how the methodology thinks and what the file
formats can express. It is currently absorbed by the mapping, which keeps the workaround out of
sight. The alternative is to state the model properly and take the gap to the format bodies as a
proposal. That is slower and depends on organisations the group does not control.

**Option A: keep the workaround.** It works today in a shipping format, it is documented, and the
tools read it. Both formats are actively adding cryptographic modelling, so the workaround may be
superseded without the methodology changing at all. That is the benefit of keeping profiles
independent of any format.

**Option B: describe the connection properly in the model** and let each format mapping express
it however it can. This makes the model correct on its own terms and gives the group a concrete
proposal to put to the format bodies.

**Where it stands.** Option A. The model describes connections; the mapping represents them as
components. The mismatch is acknowledged in two sections.

**What would have to change.** The Model section, the mapping, and whether the group makes a
submission to CycloneDX or SPDX. Q17 asks the same question about a different gap.

## Q46 — How should a signature verified by a population, rather than by one counterparty, be described?

**Status** open. Added 21 August 2026 from member feedback on financial-sector systems.

**The question.** A signed message may be verified by many parties rather than one. A settlement
instruction signed by a participant and verified by every member of a scheme is the case that
raised it; a signed software release verified by every customer is the same shape.

**Why it matters.** The model's taxonomy sorts relationships by how many parties there are and
whether they exist at the same time. It has a row for signing, at two parties and not
simultaneous, and a row for broadcast, at n parties and simultaneous. One signer with many
verifiers is n parties and *not* simultaneous, and there is no such row. So the case is neither
represented nor recorded as unrepresented, which is worse than the broadcast limitation, which at
least is written down.

The practical consequence is that a profile cannot say who is entitled to verify. The signing row
already notes that "the verifier sets the ceiling": the weakest verifier that must be supported
fixes what the signer may use. When the verifier is a whole membership, that ceiling is a property
of the scheme rather than of either party, and nothing in the baseline expresses it.

**Option A: leave it out of scope alongside Q08.** Simple, and treats every one-to-many case the
same way (trade-off: this case needs no shared key and no membership state at the cryptographic
layer, so it is much cheaper than Q08. Blocking it behind Q08 blocks a cheap fix behind an
expensive one).

**Option B: add a verifier-population attribute** to the relationship, naming the population that
must be able to verify, without generalising the relationship to n endpoints. The relationship
stays pairwise in the model; what is added is a fact about the ceiling.

**Option C: generalise the relationship**, which is Q08's Option B, and treat this as an instance.

**Where it stands.** Nothing. The taxonomy row is missing and the Model's known-limitation
paragraph mentions only the shared-key case.

**What would have to change.** The taxonomy table in the Model section, one new attribute in the
attribute model, its format mapping, and the Terms section. Not the definition of a relationship,
which is what makes this cheaper than Q08.

## Q47 — Should a profile be able to state that an interface trusts an administered, closed membership?

**Status** open. Added 21 August 2026 from member feedback on financial-sector systems.

**The question.** The baseline records the signature algorithm an interface uses for
authentication. It does not record whose trust anchor the interface accepts, or whether the set of
parties holding a credential under that anchor is open or administered.

**Why it matters.** Two interfaces can declare identical algorithms and sit in entirely different
risk positions, because one accepts any credential under a public CA and the other accepts only
members admitted by a scheme operator. In closed-membership systems — settlement, payment rails,
and any consortium PKI — that difference carries most of the security argument, and it is the
thing a supervisor supervises. A CBOM that omits it describes the cryptography accurately and the
trust position not at all.

It also blocks Q25. A finance profile built on the general baseline has nowhere to put this fact,
so it would have to invent a sector attribute for it, which is what building on the baseline is
meant to avoid.

**Option A: leave it to sector profiles.** Each sector adds its own attribute (trade-off: the
same concept arrives under several names, and a document stops being readable outside its sector,
which is the fragmentation the methodology exists to prevent).

**Option B: add a trust-domain attribute to the general model**, naming the anchor and whether
membership is administered. General enough for consortium PKI, private CAs and scheme operators
alike.

**Option C: treat it as a property of the endpoint** rather than of the relationship, on the
grounds that it describes who a party will accept rather than what passes between them.

**Where it stands.** Nothing. Raised in `design-note-multiparty-trust.md`, which also records the
factual question that would settle Q08's boundary: whether any of these systems use a key shared
among more than two participants at once, as against per-participant keys under a common anchor.

**What would have to change.** The attribute model, its format mapping, the Terms section, and
the baseline profile if the attribute is required rather than optional. Possibly the endpoint
definition in the Model, under Option C.

## Q34 — Should the completeness statement move into the baseline profile?

**Status** settled by decision 0012, awaiting ratification

**The question.** One attribute records how complete a supplier's list of interfaces is: all of
them, all external ones, or only some. It currently sits in the migration profile.

**Why it matters.** Without it, a buyer cannot interpret a missing interface. Silence could mean
the interface does not exist, or that the supplier chose not to list it. Those are entirely
different, and the difference matters in any use of a CBOM, not only in migration planning. This
is the single attribute that turns an incomplete disclosure from invisible into visible.

**Option A: move it into the baseline.** The question it answers applies to every consumer. Its
position in the migration profile is an accident of the order the examples were written in.
Moving it would let the baseline say something about completeness and would close one of the gaps
the Conformance section currently has to disclose.

**Option B: leave it where it is.** The baseline is deliberately minimal, and anything added to
it is imposed on every profile built on top. A supplier who cannot honestly claim a complete list
may prefer to say nothing at all, so requiring the statement could reduce take-up.

**Where it stands.** Option B, though the choice was never argued. Moving it would make the
baseline stricter, so it would need a version increase and would affect every existing document.

**What would have to change.** Three rules, both baseline examples, the baseline changelog, and
one row of the Conformance table. This question is bound up with Q02: the completeness statement
is the disclosure-side answer to the same problem.

**Settled in the drafting, 21 August 2026, and awaiting ratification.** Yes. The coverage statement
moved from the migration profile into the baseline as P4 in v0.6. Silence about an interface is
uninterpretable in every use of a CBOM, not only in migration planning, and the Conformance
section already named this as one of the two non-assertions most likely to cause difficulty in
procurement. Recorded as decision 0012. Moving it forced the numbering question, Q33, which is
recorded as decision 0011.

## Q36 — Where does the boundary fall between vendor-stated and operator-stated data facts?

**Status** open

**The question.** To assess the harvest-now-decrypt-later threat, someone has to record how long
the data crossing an interface must stay confidential. Which party states it, and does the answer
differ by interface?

**Why it matters.** It decides who is asked, and an earlier draft got it half wrong. A vendor
cannot know what a customer will send through a data-plane interface. A vendor knows exactly what
a management interface carries, because the interface exists to carry administrative credentials,
and it knows how long those credentials stay valid because it chose their validity. The intrinsic
case carries the worse exposure: a credential harvested today and decrypted in 2035 may still be
live, whereas ordinary business information has usually decayed. Placing all data facts at
deployment scope discards the half of the problem with the more serious consequences.

**Option A: conveyed payload from the operator, intrinsic data from the vendor.** Each fact is
stated by the party competent to state it, which is the test the methodology applies throughout.
The vendor half stays product-independent and needs no new artifact. A boundary definition is
needed, and some interfaces sit near it: a database connection carries payload in general and
credentials at session establishment.

**Option B: deployment scope only.** One rule, easy to check, no boundary to define. It forbids a
vendor from stating something it knows and no operator can derive.

**Option C: operator states everything, taking intrinsic facts from vendor documentation.** One
authoring party. It requires every operator to derive the same facts independently from the same
documentation, which is the duplicated effort the methodology exists to remove.

**Where it stands.** The Data Exposure section now describes both kinds and proposes Option A
without asserting it. The baseline's exclusion has been narrowed to conveyed payload and records
the limit explicitly. The options are worked through in `design-note-data-and-hndl.md`.

**What would have to change.** The baseline's exclusions, the Data Exposure section, and the scope
of any deployment profile. If Option A is taken, a further question follows on how the operator
half is represented and linked, which is Q45.

## Q45 — How is the operator's half of the data record represented and linked?

**Status** open

**The question.** Assuming intrinsic data sits in the product CBOM, where do the operator's facts
about conveyed payload live, and how are they connected to the interfaces they describe?

**Why it matters.** The obvious answer, attributes on the interface in a deployment CBOM, has
three defects: it forces a CBOM revision when a data classification changes, which is not a
cryptographic event; it cannot express one interface carrying several flows with different
lifetimes; and it requires the operator to amend a document the vendor signed. The alternatives
each buy something and cost something, and the choice determines whether a second artifact class
has to be governed.

**Option A: attributes on the interface in a deployment CBOM.** Nothing new to define, and the
existing conformance machinery works unchanged. Carries the three defects above.

**Option B: a separate data document referencing the CBOM.** Clean ownership and independent
lifecycles, and it supports the many-to-many case. It needs a new artifact class to specify and
govern, it depends on interfaces having stable identity across documents which is unresolved in
Q38 and Q39, and it needs a conformance model that can express a requirement spanning two
documents, which the current one cannot.

**Option C: use the carrier format's existing service and data-flow model.** CycloneDX represents
services with endpoints, authentication requirements, trust boundary traversal, and data flows
carrying a classification and a direction. Nothing is invented, flow direction comes free, and
components can depend on services so linkage is expressible. Against it: the methodology maps an
interface to a component because there is no first-class object for a cryptographic relationship,
and cryptographic properties attach to components rather than services, so an interface would
become two linked objects. It also leans on one format's structure, which cuts against format
independence unless SPDX offers an equivalent.

**Option D: inventory only, not exchanged.** No linkage problem and no new artifact. It removes
the supply-chain case, so a vendor cannot state and a buyer cannot request the information in a
comparable form.

**Where it stands.** Nothing decided. Option A is what the draft attributes imply.

**What would have to change.** Depends on the answer. Two subsidiary questions would settle much
of it: whether SPDX offers an equivalent to the service and data-flow model, and whether the group
is willing to extend the conformance model to requirements that span documents.

## Q37 — Where do the confidentiality lifetime bands fall?

**Status** open

**The question.** Confidentiality lifetime is proposed in bands: under 1 year, 1 to 5, 5 to 15,
over 15, indefinite. Are those the right boundaries?

**Why it matters.** Bands are only useful if everybody uses the same ones. A migration programme
asks how many interfaces fall in the longest band, and that question is answerable across
suppliers only when the bands match. Choosing them badly means either that almost everything
lands in one band, which carries no information, or that organizations quietly use their own.

**Option A: as proposed.** The boundaries follow periods that appear in published migration
guidance and in records-retention regulation.

**Option B: fewer bands.** Three would be easier to answer and would still separate the cases
that matter.

**Option C: align to a published retention schedule** from a regulator, so the boundaries are
already familiar in the sectors that care most.

**Where it stands.** The five bands above are a drafting proposal.

**What would have to change.** One vocabulary in any deployment profile.

---

# 3.4 How binding each rule is

Tracked as issue #6.

## Q10 — Should suppliers be required to name the software library behind an interface?

**Status** open

**The question.** The baseline requires the implementing library to be identified, and allows a
supplier to say openly that it is withholding the answer. The migration profile removes that
option and requires the actual answer.

**Why it matters.** This is the only place the migration profile is stricter than the baseline,
and it is a commercial question as much as a technical one. A buyer planning a migration needs to
know which library is involved, because that determines whether a fix exists at all and who has
to produce it. A supplier may regard the library and version it embeds as competitively
sensitive, and is sometimes contractually barred from disclosing it. Ask vendor members directly
before deciding.

**Option A: keep the requirement.** Without it the profile cannot answer its own question. A
buyer told an interface is blocked on its provider, and not told which provider, has learned
nothing it can act on.

**Option B: allow it to be withheld.** A profile suppliers will not complete is worth less than a
weaker one they will. If the requirement causes suppliers to decline the profile entirely, the
buyer gets nothing. Note that the rules on building one profile on another do not allow this to
be relaxed within the migration profile. It would have to become a separate profile, checked on
its own, with no implied conformance to the baseline.

**Where it stands.** Option A.

**What would have to change.** The override in the migration profile, the failing example, a test
that depends on the same document passing one profile and failing the other, and the explanation
in two sections.

## Q11 — Should "we do not know" show up more prominently when a rule is only advisory?

**Status** open

**The question.** An attribute can be missing for three reasons: the supplier will not say, the
supplier does not know, or the supplier never addressed it. Against a binding rule these are
treated differently. Against an advisory rule they are reported and change nothing.

**Why it matters.** A supplier answering "we do not know" to many advisory questions is
describing a real limitation in its own visibility of its product. That is often the more serious
finding, and a buyer reading only the pass or fail result will not see it.

**Option A: reporting is enough.** A rule that changes the result is a binding rule wearing the
wrong label. If the group wants an answer to matter, it should make the rule binding. Adding a
second mechanism duplicates what the binding levels already express.

**Option B: summarise it.** The result could carry a count of unknowns, or a profile could set a
threshold above which a document is flagged as materially incomplete even though it passes. The
buyer gets a signal without changing what conformance means.

**Where it stands.** Option A. Advisory rules are evaluated and reported and never change the
result.

**What would have to change.** The result line in the validator, one tool requirement, and one
table in the Conformance section.

## Q12 — When a supplier withholds an answer, should it have to say why?

**Status** open

**The question.** A supplier can mark an answer as withheld. Nothing records the reason.

**Why it matters.** The reasons call for different responses. A contractual bar cannot be
negotiated. Commercial sensitivity often can, under an agreement. A security concern about naming
an exact version might be met by giving a range. A buyer receiving a bare marker cannot tell
which conversation to open, so it opens none. Recording the reason is what turns a refusal into a
starting point. Government guidance on bills of materials already expects an empty field to carry
a reason, so this option is closer to that baseline than the current draft is.

**Option A: the marker alone.** The three-way distinction already goes beyond what either file
format supports, and each addition raises the cost of producing a conforming document. The reason
can be given in the commercial exchange where it belongs.

**Option B: allow a profile to require a reason**, chosen from a short list. A procurement
profile would require it; a public disclosure baseline would not. The cost is one list and one
setting per rule.

**Where it stands.** Option A.

**What would have to change.** The disclosure settings in the rule format, the file mapping, part
of the validator, and one table in the Conformance section.

---

# 3.5 Checking conformance

Tracked as issue #7.

## Q13 — Is the drafted conformance section accepted?

**Status** drafted

**The question.** The methodology issued pass and fail judgements throughout without ever
defining what conformance meant. A section has now been written. Does the group accept it?

**Why it matters.** Before this, a claim that something "is conformant" could not be checked,
because it did not say conformant to what. The new section names three separate things that can
be assessed: a document against a profile, a profile against the methodology, and a checking tool
against the methodology. Only the first had been treated anywhere. It also sets out what a pass
does not prove, which is the part a buyer or regulator most needs to read.

**Option A: accept as written.** It mostly consolidates material that already existed, and the
additions follow from decisions the group has already taken.

**Option B: accept, but drop the requirements on checking tools.** Seven requirements describe
what a tool must do. That is a larger commitment than a methodology usually makes, and the group
may not want to be in the business of judging tools.

**Option C: revise first.** The section settles several things in passing that the group has not
discussed, including how documents written to older file formats are treated, and the position
that a product never conforms to a profile, only a document describing it does.

**Where it stands.** Written, cross-referenced from three other sections, and marked as a draft.

**What would have to change.** The section itself, seventeen numbered requirements, and the
checking tool that implements ten of them. See also Q31 and Q32.

## Q14 — Can a supplier certify its own conformance, or must someone else check it?

**Status** open

**The question.** A conformance claim says who did the checking. When that is the supplier
itself, the claim is self-declared. When it is another party, it is attested.

**Why it matters.** This is a familiar question from product safety and security certification,
where the two forms carry very different weight and very different cost. The checking itself is
mechanical, so anyone running it gets the same answer. What an independent party adds is scrutiny
of whether the document is true, which conformance checking does not examine at all. In
procurement and regulation, that gap is precisely where an inaccurate but conforming document
would do damage.

**Option A: self-declaration by default.** The check is mechanical and produces the same result
whoever runs it. Requiring independent attestation adds cost and delay without changing the
answer, and would suppress take-up when the ecosystem most needs volume.

**Option B: independent attestation for some purposes.** The mechanical result is only as good as
the document, and nothing in conformance checks whether the document is accurate. A buyer has no
way to detect an accurate-looking but false document.

**Option C: let each profile decide.** A public disclosure baseline accepts self-declaration; a
procurement profile requires attestation.

**Where it stands.** Self-declaration is permitted provided the claim says so, with stronger
requirements left to individual profiles. That is close to Option C without saying so.

**What would have to change.** The claim format, possibly a new setting in the rule format, and
the Governance section's treatment of signing.

## Q15 — When a profile gets stricter, how long do suppliers have to catch up?

**Status** open

**The question.** The baseline recently became stricter. A document that passed under the old
version fails under the new one. Nothing says how long a supplier has before a buyer may start
rejecting documents.

**Why it matters.** This is the transition-period question that appears in every regulation, and
getting it wrong in either direction causes real disruption. Too short, and conforming suppliers
are suddenly non-conforming through no fault of their own. Too long, or undefined, and a buyer
has no basis for insisting on the newer requirement at all. The methodology already recommends
a grace period. Nothing implements one, and nobody owns it.

**Option A: the profile sets it.** The profile carries a date for each tightening, and checking
tools report a warning rather than a failure until then. This makes the period uniform and
readable by machine, and a supplier can plan from the profile alone. It puts the profile's author
in the position of setting deadlines for parties it has no relationship with.

**Option B: the contract sets it.** A profile says what conformance requires; when a buyer starts
enforcing a version is a commercial matter. This keeps the profile purely technical, and means
every pair of parties negotiates separately, which is the overhead profiles exist to remove.

**Option C: the profile recommends a period and a contract may vary it.**

**Where it stands.** Neither. The recommendation exists as good practice, the example does not
use one, and the recent tightening was published without a transition period.

**What would have to change.** The rule format, the validator's result logic, the changelog
convention, and the Conformance section's statement on how long a claim stays valid.

## Q31 — Are the requirements on profiles and on checking tools accepted?

**Status** open

**The question.** The Conformance section lists ten requirements a profile must meet to be
well-formed, and seven a checking tool must meet. Does the group accept them?

**Why it matters.** Three of them restrict what a member organisation may publish and call a
profile. A profile may not name a specific product or interface. It may not ask for a judgement
whose criteria sit outside the document, such as a readiness score. And a profile built on
another may not weaken it. Each is defensible, and each will stop somebody publishing something
they wanted to publish.

**Option A: accept as written.** Each traces back to a decision already recorded, and seven of
them are now checked automatically, so an author gets the answer in seconds instead of in review.
Automatic enforcement is what makes them more than advice.

**Option B: accept the binding ones, soften the advisory ones.** Three ask for a statement of
exclusions, companion example documents and a changelog. These are editorial obligations that may
deter a sector body publishing something small.

**Option C: soften the rule against judgement attributes.** It is enforced by looking for
suspicious words in field names, which is crude and could catch a legitimate field.

**Where it stands.** All seventeen are written. Both example profiles satisfy them, so the group
is ratifying something already shown to be workable rather than deciding in the abstract.

**What would have to change.** The Conformance section, the checking tool, seven test fixtures,
and both example profiles, which were amended to meet five of the requirements.

## Q32 — The rule against naming specific products cannot be fully checked

**Status** open

**The question.** A profile may not name a specific product, supplier or interface. A tool cannot
reliably detect that, because it cannot tell a product name from any other text. Three indirect
checks catch the known mistakes. Something else would slip through.

**Why it matters.** This rule is the reason the methodology can claim its profiles work for any
product. It exists because an early draft accidentally tied a rule to one web server. The risk
now is false confidence: an author whose profile passes the check may believe the rule is
satisfied when it is not.

**Option A: keep it binding.** The indirect checks catch the realistic mistakes, and a rule that
is mostly enforced beats one that is only advice. The Conformance section already says the tool
narrows what review must catch without replacing it.

**Option B: make it advisory and enforce it by review.** A binding rule that a conforming tool
cannot fully check is misleading.

**Option C: keep it binding and tighten the checks**, by requiring every fixed text value in a
rule to come from a declared list. That would make naming a product structurally impossible, at
the cost of forbidding one-off lists.

**Where it stands.** Option A, with the limitation stated openly in the Conformance section.

**What would have to change.** The rule's status, one function in the checking tool, and one test
fixture.

---

# 3.6 Writing a profile into a file format

Tracked as issue #2.

## Q16 — The SPDX side of the work is untested

**Status** blocked

**The question.** The methodology claims profiles work with any file format. Every working
example uses CycloneDX. The SPDX half of the mapping has never been tried against a real
document.

**Why it matters.** Format independence is the central claim, and nothing currently demonstrates
it. A reviewer is entitled to discount it. Nothing here waits on a group decision. It waits on
expertise: producing an SPDX example from unverified knowledge would create something that looks
right and is wrong, which is worse than an acknowledged gap. It needs a member who works with
SPDX, or time budgeted to read the specification properly.

**Option A: produce a minimal SPDX example and adapter.** Even a partial one, letting the same
profile check an SPDX document, would substantiate the claim.

**Option B: state the limitation and proceed.** SPDX is adding cryptographic modelling, so
anything built against the current specification may be obsolete before the methodology is
published. Two sections already mark the position as an observation about today rather than a
permanent property.

**Where it stands.** Option B.

**What would have to change.** Whether a member with SPDX knowledge can be found, the mapping
document, and the credibility of the format-independence claim.

## Q48 — How are the product-level rules evaluated from the SPDX side?

**Status** settled by decision 0016, awaiting adoption

**The question.** In the current arrangement an SPDX document satisfies the profile by referencing
a CycloneDX CBOM as an external artifact. That gives the SPDX document one element for the whole
CBOM, not one per interface. The per-interface rules are reached through the linked document and
are fine. The product-level rules are not: P1 counts interfaces and P2 counts interfaces of a
particular type, and there is no set of SPDX elements to count.

**Why it matters.** Product rules are the ones that catch omission. P2 is what fails a vendor who
describes its service interface and says nothing about how the product is administered, which is
the failure the whole worked example is built around. If those rules cannot be evaluated from the
SPDX side, then an SPDX-only consumer gets the attribute checks and not the completeness check,
and the claim that one profile can be expressed in two formats holds for half the profile.

The mapping previously filled these rows in — an annotation per interface, a count of annotated
elements — describing a structure the linkage arrangement does not produce. They are now marked
unresolved, which is the honest state.

**Option A: one SPDX element per interface**, with the CBOM linked per interface rather than once.
Gives the product rules something to count (trade-off: multiplies the linkage, and it is not clear
which SPDX element class should stand for an interface).

**Option B: carry the interface classifiers as annotations on the single reference element**,
encoded so that several interfaces can be distinguished within it (trade-off: an encoding
convention invented by this group inside another format's extension point, which is the kind of
thing harmonisation is supposed to avoid).

**How it was settled.** Option C, as decision 0016, made machine-readable rather than left in
prose. A claim carries `evaluableFromCarrier`, saying which kinds of rule the carrier holds enough
structure to evaluate — for SPDX in the linkage arrangement, `productRules: false` — and each kind
that is not evaluable adds a line to the claim's `notAsserted` list. The bound is therefore visible
to whoever is holding the claim rather than to whoever reads the mapping document.

Options A and B were rejected for the same reason: both would have this group invent something
inside a format it does not own, producing documents only our tools can read. That is the
fragmentation the methodology exists to prevent, arriving under the banner of format independence.

The mapping document's rows stay marked unresolved, which is the honest state. If SPDX's
cryptographic modelling grows a structure carrying interfaces as distinct elements, this is
superseded and `CARRIER_CAPABILITY` is the one table that changes.

**What it leaves.** The claim "one profile, two formats" holds for the attribute rules and not for
the product rules, and now says so. Q16 to Q18 on the mapping generally are untouched.

## Q49 — Can a derived profile tighten one member of an inherited group rule?

**Status** settled by decision 0014, awaiting adoption

**The question.** A group rule constrains a repeated group keyed by a controlled vocabulary, and
its member rules are evaluated inside an entry. A derived profile may add a whole group and may
tighten an ordinary inherited rule. It cannot tighten one *member* of an inherited group: group
rules are concatenated rather than overridden, and an override naming a member is rejected.

**Why it matters.** It is the first thing a sector profile will want. The migration profile's
capability group requires a status for every cryptographic purpose and the full attribute set only
for the purposes in scope. A settlement or telecom profile deriving from it would ordinarily want
to raise one member — make `roadmapRef` a MUST rather than a MAY for the purposes it cares about,
or require a blocker where the base requires one only conditionally — and there is no way to say
so. The alternatives available today are both bad: restate the whole group, which silently
overrides the base's coverage and defeats the point of inheriting it, or add a second parallel
group, which asks a producer for the same fact twice under two names.

The gap is currently recorded only in a code comment, which is the wrong place for a limitation
that shapes what a derived profile can express.

**Option A: leave it.** A derived profile that needs a stricter member declares its own group
(trade-off: two groups over the same vocabulary, and a report that shows both. The coverage
guarantee the base group carries does not transfer, so the derived profile has to restate it).

**Option B: allow an override to name a member**, as `<profileTag>#G1.3`, tightened under the same
monotonicity rules as any other rule (trade-off: a member's `requiredWhen` guard refers to its
entry, so tightening a guard is a different operation from tightening a constraint and needs its
own comparison. Coverage stays with the base group, which is the property worth keeping).

**Option C: allow a derived profile to raise the coverage of an inherited group** without touching
its members — turning `in-scope` into `all`, or widening the purposes in scope (trade-off: solves
the case that motivated the group rule and not the case a sector profile actually raises, which is
depth per member rather than breadth).

**How it was settled.** Options B and C together, as decision 0014 — they are the two halves of
one question, depth per member and breadth across keys. A member is overridden by qualified id
(`pqc-migration#G1.3`) and compared exactly as any other rule. The group shell is overridden by its
own id, where the only field an override may change is `coverage`, which may be widened and never
narrowed. A `requiredWhen` guard may be removed, which makes a rule apply always; adding one where
the base has none is refused, and changing an existing one is refused rather than compared, because
whether one condition is broader than another depends on values the profile does not hold.

**What it leaves.** Nothing of this question. It removes one of Q25's blockers: a finance profile
can now sharpen the capability group rather than restate it and lose the base's coverage.

## Q17 — Should the group ask the format bodies to add a field for withheld information?

**Status** open

**The question.** Recording that information is withheld, rather than simply absent, is central
to the methodology. Neither file format has a field for it, so the methodology carries it in a
general-purpose field under its own naming convention.

**Why it matters.** The convention works, but it is private. A tool that does not know about it
sees an ordinary annotation, so documents are only portable among tools that do. Government
guidance already expects an empty field to carry a reason, so the need is not specific to this
group. A native field would make the distinction visible to every tool in the ecosystem.

**Option A: propose it upstream.** The group has a worked design and two implementations, which
is a stronger submission than most proposals arrive with.

**Option B: keep it as a mapping convention.** The value of the methodology is that profiles do
not depend on any format, and the mapping absorbs whatever a format lacks. Pursuing format
changes is slow and creates a dependency the group does not control.

**Where it stands.** Option B, documented in the mapping and in each profile.

**What would have to change.** Whether the group makes a submission. Q09 is the same question
about a different gap.

## Q18 — Who watches the file formats, and how are outdated criticisms retired?

**Status** open

**The question.** The methodology lists limitations in the current file formats. Both formats are
being actively developed and several of those limitations will stop being true. Nobody is
assigned to notice.

**Why it matters.** A standards document that criticises a format for something the format fixed
two releases ago loses credibility quickly, and the criticism is hard to retract once other
people are citing it.

**Option A: assign a maintainer.** A named member tracks both specifications and raises an issue
when something changes. Cheap, and it depends on one person staying involved.

**Option B: date each claim and review on a cycle.** Each limitation records the version it was
observed against, and the group reviews them whenever either format publishes. More durable, and
it creates a standing obligation.

**Option C: write each limitation as a statement about a named version**, so it never becomes
false, only historical.

**Where it stands.** The prose is careful to describe current observations, and a warning notice
says so, but there is no process and no version recorded against each claim.

**What would have to change.** Two sections, the mapping, and the supported format ranges in both
profiles if a release changes what the mapping can rely on.

---

# 3.7 Agreed names for algorithms and protocols

Tracked as issue #3.

## Q19 — Does the new reference category stay?

**Status** open

**The question.** The reference register had three categories. A fourth was added during drafting
to hold the protocol and algorithm specifications the worked example cites. Eight references use
it.

**Why it matters.** A minor question, recorded because the category was created during drafting
and not by the group. Register categories are how members navigate the material, and adding one
per need eventually stops the categorisation helping.

**Option A: keep it.** The worked example cites protocol and algorithm specifications and they do
not fit the existing categories. Without a home they sit miscategorised or go uncited, and an
uncited normative reference is a defect in a standards document.

**Option B: remove it and recategorise the eight entries.**

**Where it stands.** The category exists and eight references use it.

**What would have to change.** One configuration file, eight register entries, and the filters on
the references page.

## Q20 — Whose names for algorithms should a CBOM use?

**Status** open

**The question.** The same algorithm has different names depending on who is naming it. One
common key exchange method appears as `x25519` in the CycloneDX registry, `X25519` in the
internet standards registry, and `curve25519-sha256` in SSH, where the name also bundles in a
hash function. Nothing says which name a profile requires.

**Why it matters.** A buyer comparing disclosures from twelve suppliers needs the same thing to
be called the same thing. If suppliers use different registries, the comparison silently fails:
the buyer sees twelve different algorithms where there are four. This is the concrete form of the
normalisation problem the methodology exists to address.

**Option A: the file format's registry is authoritative.** A CBOM is written in a file format,
the mapping's job is normalisation, and producers already work in that format.

**Option B: the protocol's own registry is authoritative.** The value being described is a
protocol fact, and an operator comparing a CBOM against a live system configuration will see
protocol names. Translating loses that correspondence.

**Option C: the file format's name is canonical, with the protocol name recorded alongside.**

**Where it stands.** Option A. Producers are directed to prefer CycloneDX registry identifiers
where they exist.

**What would have to change.** The mapping, the discussion of normalisation in two sections, and
whether the group needs to publish a name translation table.

## Q21 — There is no agreed list of protocol names

**Status** open

**The question.** Every interface must state its protocol. The examples use `TLS`, `SSH` and
`IPsec`. Any text satisfies the rule.

**Why it matters.** The same problem as Q20, one level up. Suppliers will write `TLS`, `tls`,
`SSL/TLS` and `HTTPS` for the same thing, and `IPsec`, `IPSec`, `IKEv2` and `ESP` for overlapping
things at different layers. A buyer cannot group interfaces without a rule. The methodology
argues that protocol names need normalising and does not say to what.

**Option A: a short controlled list maintained by the group.** Immediate and under the group's
control. It is another list to maintain and will lag real protocols.

**Option B: point at an existing registry.** No maintenance burden, and no existing registry fits
well: the obvious internet one names services rather than cryptographic protocols, and the
CycloneDX list is short.

**Option C: require the name and version used by the protocol's own specification**, cited in the
reference register.

**Where it stands.** Nothing. The rule requires only that something be present, so any text
passes, and the examples follow a convention that is not written down anywhere.

**What would have to change.** One rule, possibly a new list of protocol names, and the
comparison use cases, which assume suppliers can be compared.

## Q38 — Should a profile be required to state an identifier scheme per asset class?

**Status** settled by decision 0012, awaiting ratification

**The question.** An inventory built from several tools has to decide which records describe the
same thing. Should a profile be obliged to say which identifier form it requires for each class
of asset it covers?

**Why it matters.** This is the lever the methodology actually has. Identity cannot be solved in
general, because some asset classes have no agreed identifier at all. It can be solved per
profile: baseline rule I9 already requires a Package URL for the implementing library, which
removes software components from the correlation problem for anyone using that profile. An
organization that specifies identifier forms for its suppliers has turned an open research
problem into a procurement requirement it can check mechanically.

**Option A: require it.** Any profile intended to feed an inventory states the identifier form
for each asset class. Profiles become longer and inventories become buildable.

**Option B: leave it to each profile author.** Some profiles are not intended to feed an
inventory, and requiring the statement everywhere imposes work with no benefit in those cases.

**Where it stands.** Nothing requires it. One rule happens to do it for one asset class.

**What would have to change.** Possibly a new well-formedness requirement in the Conformance
section, and the checker that enforces those requirements.


**Answered for the baseline, 21 August 2026, and awaiting ratification.** Yes, and the answer is
narrower than the question. A profile declares `identifierSchemes` naming the required form per
asset class, and C14 checks that the declaration and the rules agree in both directions. It does
not check that a value belongs to a registry: the checker does not hold the registry and would be
guessing, which is stated in the profile rather than glossed. The baseline previously constrained
the form of the least contested identifier — the implementing library, which had to be a purl — and
left the most contested free, so `protocol: "our secure channel"` conformed. Which registry
algorithm names should come from is still Q20. Recorded as decision 0012.

## Q39 — How are keys identified across tools?

**Status** open

**The question.** Software components have Package URL and certificates have fingerprints. Keys
have no agreed identifier.

**Why it matters.** Keys are where the correlation problem is genuinely unsolved rather than
merely unagreed. A public key can be thumbprinted. A private key held in a hardware module has
only a label local to that module. The same key material present in a module and in a backup
raises a question the methodology has not answered: whether those are one key or two. Until that
is settled, any inventory count of keys is approximate, and migration progress measured in keys
is not comparable between organizations.

**Option A: identify by the public component** where one exists, using a published thumbprint
method. Works for asymmetric keys and not for symmetric ones.

**Option B: identify by role and location** rather than by material, so a key is identified by
what it does and where it lives. Stable and it makes the same material in two places two keys.

**Option C: state that keys are out of scope for cross-tool correlation** and record why.

**Where it stands.** Nothing. The problem is now described in Challenges and not addressed.

**What would have to change.** The Model and Terms sections, and any profile requiring keys to be
declared.

---

# 3.8 How a CBOM relates to an SBOM

Tracked as issue #8.

## Q22 — Should the group recommend how a CBOM and an SBOM are linked?

**Status** open

**The question.** Cryptography lives inside software, so a CBOM is of limited use without a route
to the software it describes. There are four ways to arrange this: one combined document, a
standalone CBOM, a CBOM pointing at an SBOM, or an SBOM pointing at a CBOM. The methodology sets
out the arguments for each and recommends none.

**Why it matters.** The choice decides what gets signed, who is accountable for which document,
how often each is regenerated, and what a buyer has to fetch before it can act. Without a
recommendation, each organisation picks differently and the reconciliation problem the
methodology exists to solve reappears one level up. Adopters generally want to be told.

**Option A: recommend a default.** The Governance section already contains a defensible one: a
combined document where the software and cryptography are produced by the same team on the same
release cycle, and a linked pair where the cryptographic configuration changes independently of
any software release. Stating it as a recommendation would give adopters something to follow.

**Option B: no default.** The right arrangement genuinely depends on who produces the documents
and how often each changes. A default will be followed where it does not fit. Where a buyer
requires SPDX, only one arrangement currently works, so a default stated without that
qualification would mislead.

**Option C: recommend one per stage of the product lifecycle**, which is what the current text
does without calling itself a recommendation.

**Where it stands.** Structurally Option B, in substance Option C. A notice labelled "a
defensible default" states one, and nothing adopts it.

**What would have to change.** The Governance section, the mapping's treatment of external
references, and whether a profile can require a particular arrangement.

## Q40 — Should the methodology define a topology record?

**Status** open

**The question.** Showing the posture of a whole transaction path requires knowing which
interface connects to which. That is deployment knowledge and no CBOM can carry it. Does the
methodology define a way to record it, or state that it is out of scope?

**Why it matters.** Members have asked how CBOMs are linked to give an end-to-end picture, and at
present they cannot be. A path is only as protected as its weakest hop, so an organization that
has assessed every product individually may still have no idea whether any transaction is
protected. If the methodology stays silent, every organization builds its own linkage and
estate-wide comparison stays out of reach. If it defines one, the methodology extends beyond
describing documents into describing deployments, which is a larger commitment.

**Option A: define a minimal topology record.** Enough to say that one interface connects to
another, held in the inventory and expressible in a deployment CBOM. It would depend on
interfaces having stable identity, which is Q38 and Q39.

**Option B: state it as out of scope** and leave it to inventory tooling, with the reasoning
recorded so the question is not reopened repeatedly.

**Option C: describe the composition rules without defining the record.** State how posture
composes along a path, including that a signature spanning the path does not compose like
per-hop protection, and leave the representation to implementers.

**Where it stands.** Option C in substance. The Inventory section now describes what linking
requires and how posture composes, and defines no record.

**What would have to change.** The Inventory section, possibly the Model section, and any
deployment-scope profile.

---

# 3.9 Building one profile on another

Tracked as issue #9.

## Q23 — May a profile build on more than one other profile?

**Status** open

**The question.** A profile may currently build on one other, adding requirements and making
existing ones stricter. Building on two is undefined.

**Why it matters.** The case is not hypothetical. A telecommunications operator in the EU could
plausibly want a profile that satisfies both a general industry baseline and a European
regulatory profile. If that is not possible, sector and regulatory requirements have to be
combined by hand in every organisation, or one of them has to be abandoned.

**Option A: keep it to one.** Two parents create conflicts. If they set different strictness for
the same requirement, or different permitted values for the same field, something has to decide
which wins, and any answer will surprise somebody. One parent keeps the guarantee simple: meeting
the stricter profile automatically means meeting the one it builds on.

**Option B: allow two or more, taking the strictest of any conflict.** The result is then at
least as strict as every parent, so the guarantee still holds against all of them. Under the
numbering settled in decision 0011 the rule ids themselves compose without difficulty, because
each is local to its own profile; what has to hold is that no two profiles in the merged chains
share a tag, and nothing today registers tags across families.

**Option C: no combining, but allow a profile to declare that it is always checked alongside
named others**, each producing its own result. This is already possible; the option is to make it
explicit.

**Where it stands.** Option A, described as "single inheritance only, for now".

**What would have to change.** The rule format, the part of the validator that resolves parent
profiles, the composition section, and Q33 and Q24.

## Q24 — How does a claim describe conformance to several profiles at once?

**Status** settled by decision 0015, awaiting adoption

**The question.** A document can be checked against several profiles, each giving its own result.
The methodology shows an example of how to write that down. It does not set a rule.

**Why it matters.** Buyers and auditors read claims. Unanswered questions include whether a claim
may list only the profiles a document passed, and whether silence about a profile means it failed
or that it was never checked. Those read very differently to an auditor.

**Option A: list every profile checked, with its result.** Honest and complete. It means a claim
can carry failures, which suppliers will resist and which may discourage publishing claims at
all.

**Option B: a claim lists only what a document conforms to.** Cleaner as a published statement,
weaker as an audit record, because silence cannot be distinguished from not having checked.

**Option C: a claim covers a declared set**, listing everything checked and the result of each,
so that a profile's absence means it was not assessed.

**How it was settled.** Option C, as decision 0015, and the claim is now a machine-readable
document with a published schema. Every profile evaluated is listed with its own verdict, its whole
inheritance chain and the versions pinned; a profile's absence means it was not assessed. Verdicts
are not combined, because a document can conform to one profile and fail another and a single
overall answer would have to choose which question it was answering.

Answering it turned up three gaps that mattered more than the original question. A claim was not
bound to any particular document, so it could not be falsified by the wrong one — it now carries a
`sha-256` digest. A verdict alone lost the disclosure state, so `conforms` with the implementing
library withheld read the same as `conforms` with it supplied — the four outcomes now travel with
the verdict. And a claim carried no statement of what it does not assert, which is now inside the
claim rather than referenced from it.

`--verify-claim` re-runs the evaluation, so a consumer can establish without trusting the issuer
that this is the document evaluated and that the verdicts still hold. What it cannot establish is
that the disclosed values are true; that is in `notAsserted` and always will be.

**What it leaves.** Nothing of this question. Whether a claim should be signed, and by whom, is a
separate matter that nobody has raised yet.

## Q25 — How would a sector profile fit alongside these?

**Status** open

**The question.** A telecommunications or finance body writing its own profile would most likely
require particular interface types and restrict which algorithms are acceptable, while keeping
the same list of attributes. Where does such a profile sit?

**Why it matters.** This is the question most likely to be forced by an outside body adopting the
methodology, and the answer determines whether their profile is usable by anyone outside that
sector. If a sector profile builds on the general baseline, a supplier meeting it automatically
meets the baseline too, so a buyer in another sector can still use the document. If it stands
alone, that portability is lost.

**Option A: sector profiles build on the baseline.** They inherit the disclosure requirements and
add sector ones. Documents stay useful outside the sector.

**Option B: sector profiles build on the migration profile.** For post-quantum purposes the
migration attributes are what a regulator cares about, and building on the baseline would mean
restating them.

**Option C: sector profiles stand alone and are checked alongside.** Avoids the combining
question and loses the guarantee that makes building on another profile worthwhile.

**Where it stands.** Nothing. No sector profile exists.

**What would have to change.** Whether combining is allowed (Q23), and whether permitted value
lists can be narrowed (Q35). The numbering half is settled: decision 0011 makes a rule citable as
`<profileTag>#<ruleId>`, so a claim naming several profiles has to carry their tags for a report
attached to it to be readable.

**A dependency, added 21 August 2026.** Option A is the option that preserves portability, and it
is conditional on the attribute model being able to express what a sector needs. For finance it
cannot today: there is no attribute in which to say that an interface trusts a scheme's anchor
under administered, closed membership (Q47), nor to describe a signature verified by a membership
rather than by one counterparty (Q46). A finance profile built on the baseline before those are
settled would have to carry the facts in sector-specific attributes, which is the outcome Option A
exists to avoid. Note that this does *not* depend on Q08: see `design-note-multiparty-trust.md`.

## Q33 — How are requirement numbers allocated across a family of profiles?

**Status** settled by decision 0011, awaiting ratification

**The question.** The baseline numbered its requirements P1, P2 and I1 to I9. The migration
profile continued the P sequence at P3 and started a new letter at M1. A third profile had
nothing to follow.

**Why it mattered.** Requirement numbers appear in failure reports and in a supplier's
remediation work, so they are part of a profile's public interface. Two conventions were in use
within one family, and the base could not add a product rule at all while a derived profile held
an id in the base's space — a hard validator error rather than an untidiness.

**How it was settled.** A rule id is local to the profile that declares it, and the citable form
is `<profileTag>#<ruleId>`. Every profile numbers from 1 in each kind — `P` per product, `I` per
interface, `G` per group, members as `G1.2` — at every level of a family. The uniqueness
requirement moves off the ids, which an author cannot coordinate across a family, and onto the
tag, which an author chooses once: C15 rejects a tag an ancestor already uses, and C16 fixes the
letter to the section the rule sits in. A rule keeps the id of the profile that introduced it
however far down it is later tightened, so an override names its target in full.

Nothing had been released when this was settled, so the whole family was renumbered clean and no
id is retired. From here on a released id is never reused, and gaps in a sequence are correct.

**What it leaves.** Q24 depends on this: a claim naming several profiles at once has to carry the
tags, because a report attached to it cites rules by tag. Nothing in the scheme registers tags
across bodies, which is only a problem if two profiles from different families are ever composed —
and single inheritance means they cannot be today.

**What would have to change.** Both rule files, the override declarations, the origin tracking in
the validator, and any sector profile (Q25).

**Settled in the drafting, 21 August 2026, and awaiting ratification.** The base of a family keeps
the kind letters `P` and `I`; a derived profile numbers every rule it adds under one letter of its
own, whatever the kind. Retired ids are not reused, because a stored conformance claim may cite
one. This stopped being theoretical when the baseline needed a third product rule and found the
migration profile occupying `P3`: `load_profile` raises a collision error and refuses to evaluate
anything, so the base could not grow. Recorded as decision 0011.

## Q35 — May a profile narrow an inherited list of permitted values?

**Status** open

**The question.** When a profile builds on another it inherits shared settings. Restating one of
those settings quietly overrides the parent, so a later change to the parent never reaches the
child and nothing reports it. Restating some settings is now rejected. Lists of permitted values
are exempt.

**Why it matters.** This is the most likely way a sector body would express its constraints: take
the general list of acceptable algorithms and cut it down. If restating is forbidden, they need
another mechanism. If it is allowed, a list that is narrower today could become wider than the
parent's after the parent changes, which would silently break the guarantee that the stricter
profile is genuinely stricter.

**Option A: allow narrowing by restating.** Narrowing is a tightening, and tightening is
permitted. It is the obvious way to express a sector constraint.

**Option B: forbid restating and add an explicit narrowing mechanism**, checked against the
parent. Same expressiveness, without the silent-override hazard.

**A mirror case, added 21 August 2026.** This question is framed around narrowing, which is a
tightening and therefore permitted. Decision 0010 raises the opposite: a sector profile adding
`attestation`, `tokenization` or `password-verification` to the cryptographic purpose vocabulary
would *widen* an inherited list. That is arguably a relaxation, because a document could then claim
a purpose the base profile has no rule for, and a consumer holding the base profile would have no
way to evaluate it. Whichever mechanism is chosen has to answer for both directions, and an
extension point that permits only narrowing would block sector adoption of the purpose vocabulary
entirely.

**Option C: allow restating and check it**, rejecting any restatement that adds a value the
parent did not have.

**Where it stands.** Option A, by exemption, recorded as a drafting judgement rather than a
decision.

**What would have to change.** One check in the profile checker, the rule format, and Q25.

---

## Q50 — Where is a profile family recorded, if not in its profiles?

**Status** open. Added 12 September 2026 with decision 0019.

**The question.** A family of profiles ordered by depth is only useful if a consumer can see that
the deeper ones exist. A profile points down the family, to the base it extends, and nothing points
up. A consumer holding a claim of conformance to the entry profile cannot tell from the artifact
whether that is the whole family or the first of four.

**Why it matters.** The entry profile's whole purpose is to be a first step, and a first step that
nobody can see the second of is a destination. It also affects what a buyer can write into a
requirement: "the entry profile now, the next depth within eighteen months" requires the second one
to be nameable.

**Why not fix it in the profile.** A profile cannot list the profiles deeper than it. They do not
exist when it is published, and adding them later means re-releasing it every time the family grows,
which inverts the direction of extension: the base would depend on its derivatives.

**Option A: the register.** Governance already describes a register of published profiles. A family
is a fact about a set of profiles, which is what a register holds. A consumer resolves the family
from the profile id.

**Option B: a family identifier in each profile.** Each member declares `family: pkic.interface`
and its own depth within it, without naming the others. Cheap, visible in the artifact, and it
makes two claims comparable without a lookup — but a declared depth number is a rank, and ranks
invite the comparison this methodology avoids (see Q53).

**Option C: nothing.** The chain is discoverable by reading the profiles that extend, and a consumer
who wants the family asks the publisher.

**Where it stands.** Option A by inference, stated in the Maturity section. The register does not
exist yet, so today the family is recorded in `tests/check-family.py` and in prose, which is honest
and not sufficient.

**What would have to change.** The register's contents, which Q42 and Q41 also bear on, or the rule
format if Option B is taken.

## Q51 — Should the disclosure baseline be re-parented to extend the entry profile?

**Status** open. Added 12 September 2026 with decision 0019.

**The question.** The entry profile and the Interface Disclosure Baseline are siblings: the baseline
was published first and declares no `extends`. The ladder between them is therefore an assertion
checked by a test rather than a structural fact enforced by the validator.

**Why it matters.** Monotonic extension is the mechanism that guarantees conformance at a depth
carries conformance below it. Where it is declared, the validator refuses a relaxing profile before
evaluating any document. Where it is not, nothing stops the two drifting except a test this project
wrote itself, which is the weaker of the two arrangements.

**What it costs.** Seven rules would move to the entry profile and be inherited: P1, P3, P4, I1, I2,
I7 and I8. Under decision 0011 a rule id belongs to the profile that declares it, so every report
would cite them as `interface-enumeration#I1` rather than `interface-disclosure#I1`. That changes
every citation of those seven ids in the documentation, in the test suite, and in any report or
claim already issued. It is also a tightening of nothing and a relaxation of nothing: no document's
verdict changes.

**Option A: re-parent.** The baseline declares `extends` on the entry profile at a pinned version,
drops the seven rules, and bumps its version. The ladder becomes structural and most of
`tests/check-family.py` is deleted rather than kept in parallel.

**Option B: leave them as siblings** and keep the check. The citations stay where they are, and the
cost is a test that has to be maintained and a property that holds by assertion.

**Option C: re-parent and keep the ids** by having the entry profile declare its rules under
different numbers, so the baseline's citations are unaffected. This trades citation churn for two
numbers for one rule, which decision 0011 exists to avoid.

**Where it stands.** Option B, as the state that exists. The choice is the group's because it is
about published identifiers, not about drafting.

**What would have to change.** The baseline's version and rule set, the entry profile's status as a
base, every citation of the seven ids, and the family check.

## Q52 — Should a rules file distinguish a deferral from a permanent exclusion?

**Status** open. Added 12 September 2026 with decision 0019.

**The question.** A profile records what it deliberately leaves out in one `exclusions` list. Two
quite different statements go in it: that something is excluded on principle at every depth of every
profile — key material, derived judgements — and that something is simply not asked at this depth and
is required by the profile above.

**Why it matters.** To a consumer these mean opposite things. A permanent exclusion says do not
expect this from anyone. A deferral says expect this from the next depth, and ask for it if you need
it now. A tool reading the file cannot tell them apart, so neither can anything built on one.
The entry profile marks each of its own in prose, which a reader can follow and a checker cannot.

**Option A: a `kind` on each exclusion**, one of `permanent` or `deferred`, with a deferred entry
naming nothing about where it is satisfied — because a profile cannot name its descendants (Q50).
C8 would check the field is present and valid. Both existing profiles would need their exclusions
classified.

**Option B: leave it.** The distinction is a reading matter, and every exclusion already carries a
reason that says which it is in words.

**Option C: separate lists**, `exclusions` and `deferrals`, which is clearer to read and changes the
published schema more than Option A.

**Where it stands.** Option B, with the distinction made in the reasons and in the Maturity section.

**What would have to change.** The rule format and schema, C8, and the exclusions of all three
published profiles.

## Q53 — Are the depths of a family numbered, and may a consortium profile be an entry depth?

**Status** open. Added 12 September 2026 with decision 0019.

**The question.** Two questions that have to be answered together, because the answer to one makes
the other easier or harder. Are a family's depths given numbers, and may a profile published under a
PKI Consortium name be a deliberately shallow one?

**Why it matters.** A number is what a buyer can put in a contract and what a supplier can put on a
datasheet, which is most of why staged adoption works at all. A number is also a rank, and a rank
invites the comparison the methodology avoids elsewhere: two families numbered independently would
put unlike things at "level 2", and a branch would be mistaken for a rung. Meanwhile a shallow
profile published under a consortium name may be read as the consortium's view of what is
sufficient, which is the risk in publishing an entry depth at all — and not publishing one leaves
each buyer to write its own, which loses comparability.

**Option A: names, not numbers.** A depth is identified by the profile's own id and version, which
a claim already carries. Nothing is comparable across families, which is accurate.

**Option B: numbers within a named family.** `pkic.interface` depth 1 and depth 2, with the family
name mandatory so that a number never appears alone.

**Option C: no consortium entry profile.** The consortium publishes the full baseline only, and
sector bodies publish their own shallower profiles.

**Where it stands.** Option A, by default, since profiles are named and versioned and no numbering
has been introduced. The entry profile is published as an example, like everything else in
`docs/methodology/`, which defers rather than answers the second half.

**What would have to change.** Q03, on who may publish under a consortium name, and the register's
naming rules.

---

# 3.10 Statements about the future

Tracked as issue #10.

## Q26 — Should a CBOM say anything about what a product will support later?

**Status** open

**The question.** The migration profile asks suppliers what a product will support, what is
blocking it, and where to find the commitment. A bill of materials has always been a record of
what is true now.

**Why it matters.** This is the item most likely to divide the group, and it will not be settled
by better drafting. A signed bill of materials is valuable because its contents can be checked. A
statement about the future cannot be checked, and ages without any signal that it has aged. Mixing
the two means a reader of a signed document cannot tell which parts are attestable. Against that,
a buyer committing to a product for a decade is entitled to ask what it will support, and today
that information moves in unstructured correspondence, which is the fragmentation the methodology
exists to reduce.

**Option A: present state only.** Keep bills of materials verifiable. Roadmap information belongs
in commercial documents, where it already lives and where its status is understood.

**Option B: procurement profiles may ask.** Requiring it in a defined form, with a stated
blocker, is better than leaving it to correspondence.

**Option C: allow it, and let each profile decide.** A procurement or migration profile may ask;
a profile used to assure what is running must not, because a statement about the future says
nothing about the present. The methodology already records whether each fact is intended,
implemented, configured or observed, so the mechanism to distinguish them exists.

**Where it stands.** Option C in effect. The baseline records present state and lists
forward-looking information among the things it deliberately excludes. The migration profile adds
it. No general rule is stated.

**What would have to change.** Three rules in the migration profile, the baseline's exclusions,
one decision record, and possibly a statement in the Conformance section about what can be
verified.

## Q27 — Should readiness be stated once per interface, or separately for each job cryptography does?

**Status** settled by decision 0010, awaiting ratification

**The question.** The migration profile asks for one readiness status per interface. In practice
the two main jobs cryptography does at an interface, agreeing keys and proving identity, migrate
on very different timetables.

**Why it matters.** Post-quantum key agreement can be deployed now. Post-quantum identity proof
depends on certificate and PKI changes that are further out. The most common real position is
therefore "keys done, identity not yet", and a single status per interface cannot say that. A
supplier forced into one answer will give the less advanced one, and a buyer will conclude
nothing can proceed when half of it can.

**Option A: one per interface.** Simple rule, simple dependent rule, and operators plan at
interface level anyway. The supplier states the least advanced position, which governs.

**Option B: one per job.** Reflects how migration actually proceeds. It complicates the dependent
rule, since the blocker would also become per job.

**Answered in the drafting, 21 August 2026, and awaiting ratification.** Option B, with "job" fixed as a *cryptographic purpose* from
a vocabulary the methodology defines, and with a test for what belongs in that vocabulary so
additions can be argued rather than accumulated. Seven purposes are proposed; `randomness` is left
open as an eighth. The proposal also names the collision to avoid: `endpointRoles` already means
which party you are, and CycloneDX `cryptoFunctions` already names *operations*, which is a
different thing — `sign`/`verify` is one operation covering both a TLS certificate signature and a
firmware signature, which migrate a decade apart. Recorded as decision 0010 and implemented: the migration
profile is at v0.4 with a group rule keyed by purpose, and the worked interface now states
`available` for key establishment and `committed`, blocked on certification, for entity
authentication — the position that was not expressible before. Settling it also makes staged
profiles nearly free: a profile declares which purposes it requires in depth, the rules are
written once and quantified over them, and every purpose the profile defers still owes a
status, which is what keeps a stage from becoming a floor.

**Option C: one per interface, with an optional breakdown.**

**Where it stands.** Option A in the rules. The explanatory text describes Option B. The profile
records the per-job version as deferred rather than rejected.

**What would have to change.** Two rules, the conditional mechanism, both migration examples, and
the field naming convention if the jobs become separate fields.

## Q28 — What may the pointer to a supplier's commitment point at?

**Status** open

**The question.** Where a capability is not yet available, the profile asks for a reference to
whatever commitment the supplier is willing to make. What that reference may be is unspecified.

**Why it matters.** The methodology deliberately moved dates off the interface and into the
commitment they belong to, on the grounds that a date offered when the blocker is an unfinished
international standard is not a date anyone can keep. That reasoning only holds if the reference
can actually be followed. A pointer to a customer portal a buyer cannot access, or to a page with
no date on it, has lost the thing the indirection was for.

**Option A: leave it open.** It is an optional field and cannot cause a failure. Any pointer
beats none, and constraining the form would exclude the private references most likely to carry
real commitments.

**Option B: require a resolvable address and say who can access it**, using a short list such as
public, customer, or contractual.

**Option C: require the referenced document to carry a date.**

**Where it stands.** Option A.

**What would have to change.** One rule, and the reasoning in the decision record that moved
dates off the interface.

---

# 3.11 Governing a profile over time

Tracked as issue #11.

## Q29 — Should published profiles be signed?

**Status** open

**The question.** The methodology treats signing of CBOMs at length. It says nothing about
signing the profiles themselves.

**Why it matters.** A profile is the yardstick a conformance claim is measured against, and a
claim identifies the profile by name and version. If a profile can be altered without detection,
an auditor re-running a check cannot know it used the same yardstick, so the claim is not
reproducible. This matters more for a profile that builds on another, since it locates its parent
by a file reference.

**Option A: profiles are signed by whoever publishes them.** The argument that makes CBOM signing
expected applies more strongly here, since one profile governs many documents. It requires the
consortium or a sector body to hold and manage a signing key.

**Option B: identify profiles by a fingerprint instead.** A claim records a digest of the profile
alongside its version. This gives reproducibility without key management. It does not establish
who published the profile, only that two parties used the same file.

**Option C: both.** A signature for authenticity, a fingerprint in the claim for reproducibility.

**Where it stands.** Neither. Profiles are plain files, a parent profile is located by filename,
and a claim records only a name and version.

**What would have to change.** The claim format, possibly the rule format, how parent profiles
are resolved, and the Governance section.

## Q41 — Is there an obligation to archive published profile versions?

**Status** open

**The question.** A conformance claim cites a profile version so the result can be reproduced.
Does whoever publishes a profile have to keep every published version available indefinitely?

**Why it matters.** An auditor examining a claim years later needs the profile as it stood when
the claim was made, because a later version may require different things. Without indefinite
retention, every claim becomes unverifiable the moment the profile moves on, and the failure is
silent: the claim looks valid until somebody tries to check it. Reproducibility is the property
the whole conformance model rests on, and it currently depends on an assumption nobody has
written down.

**Option A: an obligation on the publisher.** Every published version retained and served
indefinitely, addressable by version, never altered in place. This matches how the methodology
already treats superseded CBOM revisions.

**Option B: an obligation on the party making the claim.** The claimant keeps a copy of the
profile it used, or records a fingerprint of it. Puts the burden on the party that benefits and
means there is no single authoritative copy.

**Option C: both.** The publisher archives, and a claim records a fingerprint so that the archived
copy can be shown to be the one used.

**Where it stands.** Nothing states it. The Governance section now describes the obligation and
flags that it is currently assumed.

**What would have to change.** The Governance section, the claim format, and whoever ends up
holding the archive, which is bound up with Q03.

## Q42 — Who owns a profile after publication, and what happens if they stop?

**Status** open

**The question.** A profile is published by a working group or a sector body. Who maintains it
afterwards, and what happens when that body closes or loses interest?

**Why it matters.** Profiles outlive the circumstances that produced them. A profile still in use
with nobody maintaining it becomes stale against the carrier formats, and there is no route to
correct it. Conformance claims against it continue to be made and mean progressively less.
Suppliers need to know whether a profile they have invested in will still be current in five
years.

**Option A: tiered ownership.** The working group owns the baseline, sector bodies own the
profiles they derive, and the consortium maintains the register and the archive. Clear, and it
requires the consortium to accept a standing obligation.

**Option B: ownership follows the publisher, with a dormancy process.** A profile with no
maintainer is marked dormant after a stated period, warning adopters without withdrawing it.

**Option C: transfer on abandonment.** An unmaintained profile reverts to the consortium, which
may continue or retire it.

**Where it stands.** Nothing. The Governance section now names the areas to be assigned without
assigning them.

**What would have to change.** The Governance section, and any register the consortium maintains.

---

# 3.12 Fitting regulation and policy

Tracked as issue #12.

## Q43 — Should a profile define what CBOM support means for PQCMM Level 4?

**Status** open

**The question.** The PKI Consortium PQC Maturity Model requires CBOM support at Level 4 and does
not define what a CBOM must contain. Should this working group offer a profile as that
definition?

**Why it matters.** Without a definition, each assessor decides for itself what CBOM support
means, and vendors produce whatever satisfies the assessor in front of them. That is the same
ambiguity the PQCMM exists to remove from the phrase "quantum-ready", reappearing one level down.
A certification programme with third-party assessors is planned for announcement in December
2026, so assessment practice will settle around then. Work done before that can shape what the
requirement means; work done afterwards will be reconciling with an interpretation already in
use.

This is a commitment between two working groups and not a drafting decision, so it needs a
deliberate answer rather than a default.

**Option A: offer a profile.** Both efforts benefit. The PQCMM gets a checkable criterion, and
the methodology gets an adopter with a certification programme behind it. It commits this group
to maintaining a profile on somebody else's timetable.

**Option B: describe the relationship and offer nothing.** The Related Work section explains how
the two fit together and leaves the PQC Working Group to decide what it needs. Lower commitment,
and the opportunity passes.

**Option C: offer the baseline as a floor**, leaving level-specific requirements to the PQCMM.

**Where it stands.** The relationship is now described in the Related Work section. No approach
has been made.

**What would have to change.** Depends on the answer. Offering a profile would likely require a
stable identifier outside the example namespace (Q03) and a decision on whether the migration
profile is normative (Q01).

## Q44 — Should a conforming CBOM be proposed as evidence in a PQCMM assessment?

**Status** open

**The question.** A PQCMM assessment rests on vendor evidence, reviewed by the vendor itself or
by an accredited assessor. Should a CBOM conforming to a named profile be proposed as an accepted
form of that evidence?

**Why it matters.** It is the difference between the two efforts referencing each other and
actually interoperating. Machine-checkable evidence would reduce assessor effort and make
assessments more consistent, which is what a certification programme needs. It also changes what
a conformance claim is worth commercially, which raises the attestation question in Q14: a claim
used as certification evidence may need a party other than the producer to have checked it.

**Option A: propose it.** The migration profile's attributes already read as the evidence Levels
2 to 4 require.

**Option B: do not.** Conformance says a document discloses what a profile requires; it says
nothing about whether the disclosure is true. Offering it as certification evidence may imply an
assurance the methodology explicitly disclaims.

**Where it stands.** The correspondence between attributes and level requirements is noted in the
Related Work section as an observation, not agreed with anyone.

**What would have to change.** Possibly the Conformance section's statement on what a verdict
does not assert, since certification evidence carries expectations that statement is written to
manage.

## Alignment with government guidance

The alignment with the 2026 government guidance on bills of materials was analysed separately and
shaped one decision, on distinguishing withheld information from missing information.

A further question has not been raised and probably should be: whether the methodology claims
conformance to that guidance or only notes that it aligns with it. Claiming conformance would
oblige the group to track a document it does not control, and to revise the methodology whenever
that document changes. Noting alignment costs nothing and gives an adopter no assurance.

Until the PQCMM questions above were added, this topic had no items at all, which suggested that
regulatory and policy alignment had not been examined rather than that it was settled. That
remains true of the government guidance question.

---

# 3.13 Examples and tooling

Tracked as issue #13.

## Q30 — The interactive demonstration contains its own copy of the rules

**Status** settled by decision 0018, awaiting adoption

**The question.** The website has an interactive page that checks a document against the baseline
in the browser. It contains its own copy of the rules and its own checking logic, because a
static website cannot run the reference tool. Nothing verifies that the two agree.

**Why it matters.** The page tells readers it performs the same check as the reference tool, and
nothing verifies that claim. The two have already drifted once: when the baseline was made
stricter, the demonstration's copy had to be edited separately, and nothing would have caught it
if the edit had been missed. A published page that quietly disagrees with the specification is
worse than no page.

**Option A: have the page load the shared rules file.** Removes half the duplication, leaving
only the checking logic. It costs a file fetch when the page loads.

**Option B: say on the page that the reference tool is authoritative.** Cheap and honest, and it
leaves a published page that can still be wrong.

**Option C: test the two against each other.** Compare the page's rules against the rules file
automatically, or run both over the example documents and compare results. This is the only
option that would have caught the drift that already happened.

**Where it stands.** A and C together, under decision 0018, on the grounds that the two halves of
the problem have different fixes. Duplicated data can be deleted, so it was: the page fetches the
rules file and holds no copy of the rule set, the vocabularies, the carrier range or the profile
version, and shows a visible failure rather than falling back to anything when the file cannot be
loaded. Duplicated logic cannot be deleted, because a static page cannot run the reference tool, so
it is tested: `tests/check-demo.py` runs the page's own functions under Node over the four example
documents and requires the same verdict, the same outcome for every rule, the same disclosure state
for every value and the same carrier band. B was the position the repository was already in, and the
drift happened anyway.

Settling it turned up two further gaps of the same kind. Two of the four example documents the page
described did not exist as documents, so the only two cases exercising the four-outcome model and
the stated-absence rule were the two no tool could evaluate; both are now committed. And the
interface records the page displays were a third copy, transcribed from those documents, which the
test now holds to what the reference adapter extracts.

**What changed.** The demonstration page, two new example CBOMs, a new check wired into the suite
and into CI, and a paragraph in the Conformance section, which now says where its two-tools
expectation is exercised. **What is left.** The check needs a JavaScript runtime and skips itself
where there is none, so a contributor's green run is not quite CI's. Whether a tool requirement
should generalise the position — that a second implementation published alongside a profile is
tested against the reference — is left open: one instance is not evidence for a requirement.

---

# Items with no matching topic

The thirteen topics describe the parts of a profile. Four questions sit outside that frame, which
suggests the topic list may be incomplete. The group may want to close that gap before the topic
numbering is cited by anyone outside it.

## N01 — Is the drafted procedure accepted as the methodology's method?

**Status** open

**The question.** The deliverable is a methodology for defining profiles. Until recently no
section described the procedure. One has now been written: twelve steps in five stages, with a
test for each step and a table of common mistakes. It was inferred from how the worked example
was built.

**Why it has no topic.** The thirteen topics describe what a profile contains. None covers the
procedure for producing one, which is what the deliverable is actually about.

**Option A: accept it as the method.** It is the spine of the document, and ten requirements in
the Conformance section restate its outputs as obligations, so the two are already coupled.
Without acceptance the methodology describes one example instead of setting out a method.

**Option B: accept it as guidance.** Presenting twelve steps as the way to build a profile may be
more prescriptive than the evidence supports, since it has been used on two profiles for one
subject.

**What would have to change.** The Method section, ten requirements, and whether the topic list
gains an entry for the method itself.

## N02 — Is the underlying model normative or explanatory?

**Status** open

**The question.** The methodology describes cryptography in terms of connections between parties,
the parties themselves, and the algorithms and keys involved. Everything else depends on those
definitions. They are presented as explanation and never declared binding.

**Why it has no topic.** The model sits underneath the attribute list and is not itself one of
the thirteen topics. Q08 and Q09 are filed under the attribute list for want of a better home.

**Option A: binding.** The definitions are the vocabulary every requirement is written in. A
profile using them differently would be incompatible while appearing to conform. If they are
binding they need a version and a conformance statement of their own.

**Option B: explanatory.** The operative definitions are the attributes and the requirements; the
model explains why they are what they are. Making it binding adds another artifact to govern for
little practical gain.

**What would have to change.** The status of two sections, whether Q08 and Q09 become blocking,
and possibly the topic list.

## N03 — What goes into the first release, and when?

**Status** open

**The question.** Members have been told that three sections are reviewed every two weeks and
that an initial document appears in August. There are nineteen sections.

**Why it has no topic.** Project scoping.

**Why it matters.** At three sections a fortnight the review alone runs to about twelve weeks, so
both commitments cannot hold. It is better to resolve that now than in September. The first
review batch closes on 14 August.

**Option A: release the conceptual core.** The ten sections covering the problem, the model, the
profile, conformance and the method, published as a numbered draft, with the applied and
operational sections following. This gives members a document with a beginning and an end in
August, and lets the later sections benefit from decisions taken in the meantime.

**Option B: release everything at once as a marked draft**, and run the review against a
published document. Faster, and members would be reviewing material that is already public.

**Option C: keep the full scope and move the date.**

**What would have to change.** The announced cadence, what members are asked to review next, and
whether the migration profile is in scope, which depends on Q01.

## N04 — A second worked example from a different sector

**Status** deferred

**The question.** The methodology claims profiles work for any product and demonstrates it on
one: a web server. A short second example from a different sector, using the same profile
unchanged, would show the claim holds.

**Why it has no topic.** Scoping. It is the most expensive item in the improvement plan and the
least urgent.

**Option A: produce one before the release.** A generalisation demonstrated once invites a
reviewer to discount it.

**Option B: defer.** It is expensive, and more convincing once the method and composition
questions have settled. A second example built on unsettled foundations would need reworking.

**What would have to change.** Release scope (N03) and reviewer confidence. Note that the rule
against naming specific products gives a mechanical argument for product independence that does
not depend on a second example.

---

# Where each item came from

| Source | Items |
|---|---|
| PQC Migration section | Q05, Q06, Q10, Q25, Q26, Q27, Q28 |
| Profile section and its rule files | Q02, Q03, Q04, Q11, Q12, Q15, Q17, Q23, Q24, Q33, Q34, Q35 |
| Model section | Q08, Q09, Q46, Q47, N02 |
| Formats section | Q20, Q21, Q48 |
| Governance section | Q14, Q22, Q29 |
| Challenges section | Q18 |
| Demo section | Q30 |
| Conformance section | Q13, Q31, Q32 |
| Improvement plan | Q01, Q16, Q19, N01, N03, N04 |
| Decision index | Q07 |
| Validator source, where the limitation was recorded as a comment | Q49 |
| Maturity section, drafted from a member's request for a reachable first profile | Q50, Q51, Q52, Q53 |
