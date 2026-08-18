# Design note: modelling data alongside cryptography

Working note for the PKI Consortium CBOM Profiles Working Group.
Written 9 August 2026, in response to the observation that a bill of materials sometimes does
know what data an interface carries.

## The observation that reframes this

The Data Exposure section as drafted says that facts about data belong to a deployment-scope
document, because a vendor does not know what its customers will send through a product. That is
true of payload and false of a whole class of interfaces.

Some interfaces carry data whose nature follows from the interface's function, and the vendor
knows exactly what it is because the vendor designed it.

| Interface | What it necessarily carries | Who knows |
|---|---|---|
| Management or control | Administrative credentials, configuration secrets | The vendor. The interface exists to carry them |
| Key management | Key material, wrapped or in the clear | The vendor |
| Firmware or software update | Signed images, and the signature verifying them | The vendor |
| Enrolment or provisioning | Device identity, private key material, certificate requests | The vendor |
| Authentication | Passwords, tokens, assertions | The vendor |
| Application data plane | Whatever the customer sends | Only the operator |

The last row is the case the current draft assumed was the only case.

### Why the intrinsic case matters more, not less

The harvest-now-decrypt-later exposure of intrinsic data is often worse than that of payload, and
the reason is worth stating plainly.

Consider a management session protected by a classical key exchange, carrying a device credential.
An adversary records the session today and decrypts it in 2035. If the credential is a device
certificate with a twenty-year validity, or a key burned into hardware that cannot be rotated in
the field, the adversary does not obtain stale information. It obtains a working secret. The
confidentiality lifetime of that payload equals the lifetime of the credential, and the vendor
knows that lifetime because the vendor chose it.

This inverts the usual framing. The data the vendor cannot know about is ordinary business
information whose sensitivity decays. The data the vendor does know about is often credentials and
keys, whose value does not decay and may outlast the recording. Excluding vendor knowledge from
the model discards the worse half of the problem.

## Two questions that were being asked as one

The draft conflated a question about knowledge with a question about representation. Separating
them makes the options tractable.

1. **Scope.** Which party is competent to state each fact, and therefore which facts may appear in
   a vendor-authored document.
2. **Representation.** Which document carries the facts, and how the documents are linked.

The scope question has to be answered first, because it constrains the representation options but
not the reverse.

---

## Part 1: options for scope

### S1. Payload only, operator only

The current draft. All facts about data are operator-stated and excluded from a product CBOM.

**For.** One rule, easy to state and to check. No risk of a vendor guessing.

**Against.** Discards the intrinsic case, which is the higher-risk half. A vendor that knows its
management interface carries a twenty-year credential is forbidden from saying so, and no operator
can supply that fact because it is a property of the product's design.

### S2. Split by knowledge: intrinsic data from the vendor, payload from the operator

A product CBOM declares what an interface necessarily carries, as a property of the interface's
function. A deployment record supplies the sensitivity of whatever else flows across it.

**For.** Each fact is stated by the party that can state it, which is the test the methodology
already applies elsewhere. Captures the credential and key-material cases. The vendor half stays
product-independent, so it fits the existing profile model without a new artifact. It also gives
a consumer something useful before any deployment record exists, which matters because the
deployment record is the part least likely to be produced.

**Against.** Two mechanisms to specify and two documents to consult. The boundary needs a
definition, and some interfaces sit near it: a database connection carries payload from the
vendor's point of view and credentials at session establishment. A vendor may under-declare, since
declaring that an interface carries long-lived credentials invites questions.

### S3. Everything from the operator, including the intrinsic case

The operator states both, taking the intrinsic facts from the vendor's documentation.

**For.** One authoring party and one document. No boundary to define.

**Against.** Requires every operator to derive the same facts independently from the same
documentation, which is the duplicated effort the methodology exists to remove. The facts are
identical across every deployment of the product, so stating them once at the vendor is strictly
more efficient.

---

## Part 2: options for representation

These assume S2 has been chosen, since it is the option that creates a representation question.
The vendor half is straightforward in every case; the variation is in how the operator half is
carried and linked.

### R1. Attributes on the interface, in a deployment-scope CBOM

The operator produces a CBOM for its deployment, with data attributes on each interface.

**For.** No new artifact class. The existing profile machinery works unchanged: rules,
conformance, the validator, the checker. One document to fetch.

**Against.** It forces a CBOM revision whenever a data classification changes, which is a
non-cryptographic event, so the document's revision history stops corresponding to cryptographic
change. It cannot express one interface carrying several data flows with different lifetimes,
which is common. And it requires the operator to author or amend a document the vendor produced,
which raises the question of who signs the result and what the vendor's signature then covers.

### R2. A separate data bill of materials, referencing the CBOM

The proposal in the question. A distinct document describes data flows and points at the interfaces
in a CBOM.

**For.** Ownership is clean: the vendor signs the CBOM, the operator signs the data document, and
neither is altered by the other. The two have independent lifecycles, so reclassifying data does
not disturb the cryptographic record. It supports many-to-many, which R1 cannot: one interface
carrying several flows, and one flow crossing several interfaces along a path. The layering pattern
already exists in the methodology for the CBOM and SBOM relationship, and the four arrangements
described in the Governance section apply unchanged. Most organizations already hold a data
inventory for data-protection purposes, so this connects to an existing asset instead of
duplicating it.

**Against, and these are substantial.** It is a new artifact class to specify, version, govern,
sign and archive, and nothing standardises it, so the group would be defining a format. Linkage
depends on interfaces having stable identity across documents, which is unresolved and recorded as
Q38 and Q39: the interface identifier is deliberately unconstrained, so there is currently nothing
to point at. Most seriously, the conformance model cannot express a requirement that spans two
documents. Every rule in the schema is evaluated against one document, so a requirement such as
"every interface in the CBOM has a data record" is not expressible, and adding cross-document
rules is a change to the conformance model rather than a new rule type.

### R3. Use the carrier format's existing service and data-flow model

CycloneDX represents **services** with endpoint identifiers, authentication requirements, trust
boundary traversal, and data flows carrying a classification and a direction. Version 1.5
introduced a richer data-flow element with source and destination. This is close to what the
methodology means by an interface, and it already carries the data half.

**For.** Nothing is invented. The facts land in fields the format defines, so any CycloneDX tool
can read them and the methodology's normalisation work is reduced to choosing the canonical
location. Flow direction comes free, and direction matters here: an inbound credential and an
outbound telemetry stream have different exposure. Trust boundary traversal overlaps with the
`exposure` attribute proposed in the draft, so one of them is redundant. Components can depend on
services in the dependency graph, so linkage between the cryptographic and data views is
expressible without a new identifier scheme.

**Against.** The methodology currently maps an interface to a *component* with an asset type of
protocol, because CycloneDX has no first-class object for a cryptographic relationship. Cryptographic
properties attach to components, not to services. Adopting services for the data half means an
interface is represented by two linked objects, which complicates the mapping and the adapter, and
makes the format-independent model harder to state cleanly. It also binds the data half to one
carrier format's structure, which cuts against format independence unless SPDX offers an
equivalent, and that has not been checked. This option is worth taking seriously and needs
somebody to read the specification properly before it is chosen.

### R4. Inventory only, with no exchangeable artifact

The join between cryptography and data happens inside the inventory and is never exchanged.

**For.** No new artifact, no linkage problem, and the Inventory section already discusses
non-cryptographic context data. Fastest to adopt, since organizations are doing it already.

**Against.** It removes the supply-chain case entirely. A vendor cannot tell a customer that a
management interface carries long-lived credentials, and a buyer cannot ask for it in a
comparable form. Every organization models it differently, so nothing aggregates. It also
contradicts S2, since the vendor's knowledge has nowhere to go.

### R5. Reference existing data-protection records instead of describing data

The document points at records the organization already maintains: a record of processing, a data
classification register, a retention schedule.

**For.** Reuses artifacts that already exist and are legally required in several jurisdictions. A
retention schedule already contains the confidentiality lifetime, stated by the party accountable
for it.

**Against.** Those records are internal, rarely machine-readable, and almost never granular to an
interface. They are organised by processing activity or record class, and mapping either onto an
interface is manual work with no obvious rule. Useful as a source for the values, not as a
substitute for recording them.

---

## Where this leaves the question

The scope question looks settled by the argument rather than by preference. S2 captures a class of
high-risk, vendor-knowable facts that S1 discards, and does so more efficiently than S3. The
counter-argument to watch is under-declaration, which is a disclosure-incentive problem the
withheld marker already exists to handle.

The representation question is genuinely open, and the two strongest options pull in opposite
directions. R2 is right about ownership and lifecycle and wrong about cost: it needs a new artifact
class, and it needs a cross-document conformance capability the model does not have. R3 needs
nothing invented and buys real capability, and it compromises format independence and complicates
the mapping.

A combination is available and is worth putting to the group: adopt **S2** for scope; carry the
vendor half as interface attributes in the product CBOM, which needs nothing new; and decide
between **R2** and **R3** for the operator half on the basis of whether the group is prepared to
define an artifact or prepared to lean on one format's structure.

Two questions would settle it. Does SPDX offer an equivalent to the service and data-flow model,
which determines whether R3 costs format independence or not. And is the group willing to extend
the conformance model to cross-document requirements, without which R2 produces documents whose
relationship nothing can check.

## Consequences for what is already drafted

- The Data Exposure section states the scope rule as settled. It is not, and the intrinsic case is
  missing entirely. The section needs the distinction added and the rule softened to a proposal.
- The baseline profile's exclusion list says data properties are excluded because the vendor cannot
  know them. Under S2 that reason is wrong for intrinsic data and the exclusion needs narrowing to
  payload.
- The `exposure` attribute proposed in the draft overlaps with the trust-boundary concept in the
  carrier format. One of the two should go.
- Q36 in the open questions register asks whether data facts are deployment scope only. The
  question needs restating: the answer is no, and the real question is where the boundary falls.

## Incidental findings

Reading the carrier format's object model for this question surfaced two things that bear on other
open questions, and both deserve checking before more is built.

**Completeness may already exist.** CycloneDX **compositions** describe constituent parts and
their completeness, with an aggregate of complete, incomplete, incomplete first-party only,
incomplete third-party only, or unknown. That is close to the `coverage` attribute carried as
product rule P3 in the migration profile, and to the question in Q34 about whether coverage belongs
in the baseline. If the native construct is adequate, the attribute should map onto it instead of
being invented.

**Conformance declarations may already exist.** CycloneDX **definitions** express standards,
requirements and levels in machine-readable form, and **declarations** express conformance to them
with attestations, claims, evidence, conformance and confidence, and signatories. The methodology
has been defining a profile format and a conformance claim format independently. Whether these
constructs are a better carrier for both is a substantial question, and it bears on Q07, on the
claim format in Q24, and on how PQCMM levels might be expressed. **Citations**, which record who
contributed which piece of information and when, are also relevant to the multi-source correlation
problem.

None of this has been verified at field level. It should be, by somebody reading the specification
rather than its overview.

## Sources

- [CycloneDX Specification Overview](https://cyclonedx.org/specification/overview) — services and
  data flow, compositions, definitions and declarations, citations. Version 1.7, ECMA-424.
- [CycloneDX specification repository](https://github.com/CycloneDX/specification) — schema
  definitions, including the data classification and flow direction values.
