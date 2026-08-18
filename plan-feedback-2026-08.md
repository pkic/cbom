# Resolution plan: member feedback, August 2026

Working note for the PKI Consortium CBOM Profiles Working Group.
Written 9 August 2026 in response to five items of feedback on the current proposal.

## Summary

Five items were raised. Two of them turn out to be the same underlying problem, and one has a
much more concrete answer than it first appears.

| # | Feedback | Proposed treatment | Size |
|---|---|---|---|
| 1 | Harvest-now-decrypt-later, and linking data to interfaces | New section, plus attributes on a deployment-scope profile | Large |
| 2 | Identifying the same asset across different tools | New challenge, plus expansion of Inventory | Medium |
| 3 | Link to the PQC Maturity Model | New section | Medium |
| 4 | Building an end-to-end deployment picture by linking CBOMs | New subsection in Inventory, plus a stated scope boundary | Medium |
| 5 | Long-term governance of profiles and mappings | Expansion of Governance | Medium |

**Items 2 and 4 are the same problem.** An end-to-end picture cannot be assembled without stable
identity for the things being linked, and the methodology currently has none. Worse, it has
deliberately excluded one: `interfaceId` is explicitly a producer-chosen label that no profile may
constrain, which is correct for product independence and means nothing connects an interface
record across two documents, two tools, or two revisions of the same document. They should be
worked together.

**Item 3 is a dependency, not an alignment exercise.** PQCMM Level 4 requires "CBOM support" and
does not define what a CBOM must contain. A profile is that definition. Without one, every
assessor decides for itself what Level 4 means, which is the ambiguity PQCMM was created to
remove for the phrase "quantum-ready". The certification programme is targeted for the end of
2026, so there is a window in which this work is useful to them and after which their
interpretation will have settled without us.

---

## 1. Harvest now, decrypt later

### What the feedback asks for

A better way to link data to the interfaces that carry it, so that harvest-now-decrypt-later risk
can be understood. A new section. Data sensitivity is suggested as a candidate attribute.

### Why the methodology cannot answer it today

The profile describes the cryptography at an interface. It says nothing about what travels over
that interface. Two interfaces both using X25519 are identical in every attribute the baseline
records, and their harvest-now-decrypt-later exposure can differ by decades: one carries a public
status page, the other carries medical records that must stay confidential until 2070.

The threat is not determined by the algorithm alone. It is determined by three quantities, which
is the formulation Mosca gives: how long the data must stay confidential, how long migration
takes, and how long until a cryptographically relevant quantum computer exists. If the first two
added together exceed the third, the data is already exposed. The methodology currently supplies
none of the first quantity.

### The design problem to resolve first

Data sensitivity is not a product attribute and cannot be one. A vendor shipping a black box does
not know what its customers will send through it, and the same product carries public data at one
site and state secrets at another. Requiring a vendor to declare data sensitivity produces either
a refusal or a guess.

The methodology already has the distinction that resolves this. The Lifecycle Data section
separates a **product CBOM**, describing what a vendor ships, from a **service or deployment
CBOM**, describing what an operator runs. Data attributes belong to the second and must be
excluded from the first. Stating that clearly is most of the work.

### Proposed attributes

For a deployment-scope profile only. Names follow the existing conventions.

| Attribute | Purpose | Notes |
|---|---|---|
| `confidentialityLifetime` | How long the data carried must remain confidential | The input the threat model needs. Bands rather than dates: under 1 year, 1 to 5, 5 to 15, over 15, indefinite. Bands are comparable across organisations in a way that classification labels are not |
| `exposure` | Where the traffic runs | `public-internet`, `partner-network`, `private-network`, `physical-local`. Determines whether interception at scale is plausible, and so whether harvesting is a practical concern |
| `dataClassification` | The operator's own classification | Optional, and must name the scheme it comes from. Classification labels are not comparable between organisations or jurisdictions, so this supports internal use and not aggregation |
| `retentionAtRest` | Whether ciphertext is stored, and for how long | Harvesting applies to stored ciphertext as much as to captured traffic. A storage interface may be the higher risk |

`confidentialityLifetime` is the one that matters most. If the group adopts only one attribute
from this list, it should be that one.

### What stays outside the CBOM

The date at which a cryptographically relevant quantum computer is expected is an estimate that
changes with published research and national guidance. It is not a fact about any product, and it
does not belong in any CBOM. Under decision 0002 it is external policy input, and the resulting
urgency ranking is a derived judgement computed at the time of asking, carrying the policy version
and the date applied. This is the same treatment the methodology already gives post-quantum
posture, so no new machinery is needed.

### Steps

1. Draft the section. Working title "Data exposure and the harvest-now-decrypt-later threat".
   Cover the threat, the three-quantity formulation, why the answer is not visible in the
   cryptography alone, and why the data attributes sit at deployment scope.
2. Add the attributes to the Terms section and record the product-scope exclusion in the baseline
   profile's `exclusions` list, so a reader of the baseline sees why they are absent.
3. Produce a third worked profile at deployment scope, or extend the migration profile with a
   deployment variant. This is the larger part of the work and could follow the section.
4. Add a diagram contrasting two interfaces with identical cryptography and opposite exposure.
5. Record a decision on data attributes being deployment-scope only.
6. Add open questions on the band boundaries, on whether `dataClassification` earns its place
   given it cannot be aggregated, and on whether storage interfaces need their own treatment.

### Placement

After Lifecycle Data, which is where the product and service distinction is established, and
before Model. It is motivating material rather than applied material, and a policy reader will
want it early.

---

## 2. Identifying the same asset across different tools

### What the feedback asks for

Add the difficulty of uniquely identifying assets, such as components and keys, when they are
reported by different tools. A suggestion of where it belongs.

### The problem

An inventory is assembled from a vendor CBOM, a build-time scan and a runtime discovery tool.
Each names things differently, and for some asset classes there is no agreed name at all.

| Asset class | Identity today | Assessment |
|---|---|---|
| Software components | Package URL, and formerly CPE | Workable. The methodology already requires `pkg:` form for the implementing library |
| Certificates | SHA-256 fingerprint of the DER encoding, or issuer and serial | Workable, though tools disagree on which to use |
| Keys | No agreed identifier | The hard case. A public key can be thumbprinted, a private key in a hardware module has only a local label or handle, and the same key material existing in a module and in a backup is genuinely ambiguous |
| Algorithms | Registry identifiers, several competing | Already recorded as open question Q20 |
| Interfaces | `interfaceId`, producer-chosen and unconstrained by design | Undefined across documents. See item 4 |

Correlation has to hold across tools, and also across time: an inventory that cannot tell whether
today's record is the same interface as last quarter's cannot track progress, which is one of the
stated use cases.

### Where to add it

Three places, in order of importance.

1. **Challenges.** A new numbered challenge, with a short subsection. This is where the existing
   limitations are catalogued and where a reader will look for it. Mark it as a current
   observation, consistent with how the rest of that section is framed.
2. **Inventory.** Expand the normalisation and correlation step. The first diagram already shows
   several sources feeding a normalisation stage, and that stage is where this problem lives. It
   is currently drawn as a box with no discussion of what it has to do.
3. **Formats.** A paragraph noting that the mapping normalises identity as well as encoding, and
   that identity normalisation is the harder of the two.

There is also a constructive answer worth stating: a profile can require a particular identifier
form, which is what baseline rule I9 already does by requiring a `pkg:` Package URL. Generalising
that, identity requirements are a profile concern, and a profile intended to feed an inventory
should say which identifier form it requires for each asset class. That turns the problem from an
unsolvable general one into a per-profile decision.

### Steps

1. Draft the challenge entry and subsection.
2. Expand the Inventory normalisation discussion, with a table of asset classes and their
   identifier options.
3. Add the paragraph to Formats.
4. Add open questions on key identity and on whether the methodology should require an identifier
   scheme per asset class.
5. Coordinate with item 4, which depends on the interface row of that table.

---

## 3. Relationship to the PQC Maturity Model

### What was found

The PQCMM is a PKI Consortium PQC Working Group framework, currently at version 1.0.1. It is
product and service centric, which is unusual for a maturity model and matches the subject of the
CBOM interface model exactly. It defines six cumulative levels, and the two in the middle are the
relevant ones:

- **Level 3 (Advanced)** requires a cryptographic inventory, SBOM support and cryptographic
  agility.
- **Level 4 (Managed)** requires **CBOM support**, hybrid cryptography and zero-legacy capability.

A certification programme is planned, with third-party assessors validating vendor evidence, and
is targeted for announcement at the PQC Conference in Amsterdam on 1 to 3 December 2026.

### Why this is a dependency rather than an alignment exercise

PQCMM Level 4 requires CBOM support and does not define what a CBOM must contain. That is
precisely the gap this working group exists to fill. Until it is filled, each assessor decides for
itself what CBOM support means, and vendors will produce whatever satisfies the assessor in front
of them. That is the same ambiguity PQCMM was created to remove from the phrase "quantum-ready",
and it reappears one level down.

The complement is clean, and the methodology has already provided for it. The Policy Evaluation
section states that derived judgements, naming cryptographic maturity as an example, are computed
by external versioned policy from the facts a CBOM discloses. PQCMM is exactly that external
policy. Nothing needs to change architecturally; the relationship needs to be described.

| | PQCMM | CBOM profiles |
|---|---|---|
| Question answered | How ready is this product, on a scale of 0 to 5 | Does this document disclose what the purpose requires |
| Result | A graded level, cumulative | A binary verdict, per profile |
| Subject | A product or service as shipped | One revision of one document |
| Assessed by | Self-assessment or an accredited assessor | A validator, mechanically |
| Relationship | Consumes the facts | Supplies the facts |

The migration profile's attributes read like the evidence a Level 3 or 4 assessment needs:
supported algorithm sets, how a capability is enabled, whether hybrid operation is possible,
minimum product version, and what is blocking a capability that is not yet available.

### Points requiring care

The two efforts treat external schemes differently. PQCMM references schemes such as CycloneDX and
Package URL by name and takes whichever version is current, deliberately, so that the model does
not age. This methodology pins carrier versions with a declared acceptance range, because a
validator has to know what it can parse. Both positions are right for their purpose. The
interaction should be stated so that neither is read as contradicting the other.

### Steps

1. Create the new section. Suggested title "Related work", housing the PQCMM relationship first
   and leaving room for the PQC Capabilities Matrix and the PKI Maturity Model, which are adjacent
   and will otherwise generate the same question again.
2. Describe the complement, using the table above, and state explicitly that PQCMM is an instance
   of the external policy the Policy Evaluation section describes.
3. Map the migration profile's attributes to the evidence Levels 3 and 4 appear to require. This
   needs the detailed level criteria read properly, not the summary.
4. Add PQCMM to the reference register, under a category for related consortium work.
5. **Approach the PQC Working Group.** This is the step with a deadline. If Level 4 conformance
   could cite a CBOM profile, both efforts benefit, and the certification programme is being
   designed now.
6. Add an open question on whether the working group should offer a profile as the definition of
   CBOM support for Level 4, which is a commitment rather than a drafting choice.

---

## 4. Building an end-to-end deployment picture

### What the feedback asks for

A response to the question of how CBOMs are linked to show end-to-end posture across a deployment.

### The response

A CBOM describes one subject's boundary. It does not know what is on the other side of any of its
interfaces, and it cannot: the same product is deployed into different topologies at every site.
End-to-end posture is therefore not a property any CBOM can carry, and assembling it requires
three things the methodology has not defined.

1. **Stable identity for the things being linked.** This is item 2. The interface case is the
   sharp one, because `interfaceId` is deliberately unconstrained so that profiles stay product
   independent. Correct for its purpose, and it means nothing connects an interface in one
   document to an interface in another.
2. **A topology record.** Something must state that this product's interface connects to that
   product's interface. That is deployment knowledge, held by the operator, not by any vendor. It
   belongs in the inventory layer, and putting it in a product CBOM would break instance
   independence.
3. **A composition rule.** Given a path, how is posture computed along it. The Model section
   already establishes the substance: relationships overlap rather than partition a path, posture
   is set by the weaker end, and a signature relationship can span an entire path while transport
   protection is renegotiated at every hop. So the weakest-link rule is right for transport and
   wrong for anything spanning the path, and the section already has the worked examples to show
   why.

End-to-end posture is an **inventory function**, not a CBOM function. CBOMs supply per-node
facts; the inventory supplies the topology; the composition is computed and dated, like any other
derived judgement.

### Steps

1. Add a subsection to Inventory, "End-to-end posture", with a diagram showing several CBOMs
   feeding an inventory that holds the topology, and posture computed over a path.
2. State the scope boundary explicitly: a product CBOM does not and should not carry topology, and
   say why, referring to instance independence and decision 0001.
3. Define the minimum linkage a service-scope CBOM may carry, since a service CBOM legitimately
   describes instances. This is the same deployment-scope profile that item 1 needs, which is an
   argument for doing items 1 and 4 together.
4. Add a worked example following one transaction across several hops, reusing the Model section's
   existing multi-hop diagram.
5. State the composition rules, distinguishing per-hop protection from relationships that span the
   path.
6. Add an open question on whether the methodology should define a topology record at all, or
   scope it out and leave it to inventory tooling.

---

## 5. Long-term governance of profiles and mappings

### What the feedback asks for

A perspective on how profiles and mappings are governed over the long term.

### What exists and what is missing

The Governance section covers the CBOM lifecycle, signing, provenance, the relationship between a
CBOM and an SBOM, and change control. It treats CBOMs thoroughly and profiles barely at all. The
gaps are all about what happens after publication, and several already exist as scattered open
questions.

| Gap | Existing item |
|---|---|
| Who may publish under a consortium name, and who maintains the register | Q03 |
| Whether a profile is signed, and by whom | Q29 |
| Who tracks the carrier formats as they change | Q18 |
| Whether a carrier release obliges a profile version | Q04 |
| How long a supplier has when a profile is tightened | Q15 |
| Ownership and succession when a profile's author stops maintaining it | not recorded |
| How a profile is deprecated or withdrawn | not recorded |
| Archive obligations, since a claim can outlive the profile it cites | not recorded |

The last three are the substance of the feedback and are genuinely absent.

The archive point deserves emphasis. A conformance claim cites a profile version so that the
result can be reproduced. An auditor examining a claim in 2035 needs the text of the profile as it
stood when the claim was made. If profile versions are not archived and served indefinitely, every
claim becomes unverifiable the moment the profile moves on, and the reproducibility the whole
conformance model rests on is lost. This is an obligation on whoever publishes a profile, and
nothing currently states it.

Mappings need separate treatment from profiles. A profile changes when the group decides to change
it. A mapping changes because something outside the group changed, on a schedule the group does
not control. That makes mapping maintenance a standing obligation rather than an occasional
decision, which is the substance of Q18.

### Proposed structure

A new part of the Governance section, "Stewardship of profiles and mappings", covering:

- **Ownership.** Who maintains a profile after publication, and what happens on abandonment.
  A tiered model is worth considering: the working group owns the baseline, sector bodies own
  their derived profiles, and the consortium maintains the register and the archive.
- **Review cadence.** A stated review period, and a trigger on each carrier format release.
- **Deprecation and withdrawal.** How a profile is retired, what happens to claims citing it, and
  the minimum notice.
- **Archive.** Every published version retained and served indefinitely, addressed by version, so
  that claims stay reproducible.
- **Mapping maintenance.** Named responsibility for tracking each carrier format, and how a
  superseded limitation is recorded.
- **Succession.** What happens when a working group closes or a sector body withdraws.

PQCMM publishes a version history and describes itself as actively maintained with community
editing. Whatever this group decides should not contradict how a sibling effort in the same
consortium operates.

### Steps

1. Draft the stewardship section.
2. Pull Q03, Q04, Q15, Q18 and Q29 together under it, so the register points at one place.
3. Add open questions on ownership and succession, on deprecation, and on the archive obligation.
4. Record a decision on the archive obligation if the group accepts it, since conformance
   reproducibility depends on it and it is currently an unstated assumption.

---

## Sequencing

**First, because they unblock others.** Item 2, asset identity, since item 4 depends on it.
Item 3, the PQCMM relationship, because the certification programme is being designed now and
the window closes.

**Second.** Item 5, stewardship, which is mostly consolidation of material and questions that
already exist. Item 4, end-to-end posture, once identity is settled.

**Third, and largest.** Item 1, harvest now decrypt later. The section can be drafted early, but
the deployment-scope profile it implies is a substantial piece of work and overlaps with item 4.
Items 1 and 4 both need a deployment-scope profile and should share one.

## Consequences for the site

Two new tabs are requested and a third is implied, taking the navigation from eighteen entries to
twenty or twenty-one. The tab bar is already past the point where it guides a reader, which is why
reading paths were added to the Overview. Before adding more, the navigation should be grouped,
either into labelled bands or into a small number of top-level groups with the sections beneath
them. Adding two more flat tabs will make it worse.

## What the working group needs to decide

1. Whether data attributes are accepted as deployment scope only, and excluded from product CBOMs.
2. Whether to approach the PQC Working Group about profiles defining CBOM support for PQCMM
   Level 4. This is a commitment between working groups, not a drafting decision.
3. Whether the methodology defines a topology record for end-to-end posture, or scopes it out.
4. Whether identity requirements per asset class belong in profiles.
5. The stewardship model: who owns a profile after publication, and who holds the archive.
6. How the navigation is restructured before two more tabs are added.

## Effect on the release

Item 3 is small enough to sit in the August release and is the most time-sensitive. Items 2 and 5
are consolidation and could make it. Items 1 and 4 are new material with a new profile behind
them, and would push the release. This strengthens the case for the scoped release described as
N03 in the open questions register, with the conceptual core published in August and this
material following.

## Sources

- [PQC Maturity Model (PQCMM), PKI Consortium](https://pkic.org/wg/pqc/pqcmm/)
- [Defining 'Quantum-Ready' for the Supply Chain: Introducing the PQC Maturity Model (PQCMM)](https://pkic.org/2026/06/14/defining-quantum-ready-for-the-supply-chain-introducing-the-pqc-maturity-model-pqcmm/)
- [PQC Capabilities Matrix (PQCCM)](https://pkic.org/wg/pqc/pqccm/)
- [PKI Maturity Model Working Group](https://pkic.org/wg/pkimm/)
