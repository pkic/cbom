# Cryptographic Transparency in the Supply Chain

**A CBOM profile approach to post-quantum migration readiness**

*Working draft — not agreed text*
*Audience: European Commission and Member State policy stakeholders*

---

## Editorial conventions

- **Format-independence.** The methodology is defined independently of CycloneDX or SPDX
  throughout. Format-specific detail belongs in Annex B, not in the body.
- **Precedent.** Cite the **PKIC CBOM Profiles Working Group charter** as the motivating
  precedent for the profile-first, format-independent method. Do not cite the PQC Maturity
  Model — it is a separate effort.
- **Obligation language.** BCP 14 keywords, capitalised, only where an obligation is meant.
- **Length.** Body targets 40 pages as a guide. Chapters 6 and 7 cap at six pages each; chapter
  3 is uncapped (DR-05, DR-10). Detail that does not fit goes to the register or an annex.
- **Decisions.** Recorded in `decisions.md` as `DR-nn`. Cite the record rather than restating
  the rationale.
- **Numbering.** Report divisions are cited as "chapter n" / "§n.n". PKIC methodology
  aspects are cited as "aspect 3.n". The two numbering schemes are unrelated.
- **Item IDs.** `LYR-*`, `LSN-*`, `GAP-*` and `RDY-*` are defined once in `register.md`. Chapters
  reference them; they do not redefine them.
- **Verification markers.** `> **Verify:**` flags a claim to be checked against current
  releases or instrument text. None should survive to v1.0.


---

# 1  Executive summary

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text

European policy already expects organisations to hold a cryptographic inventory. The coordinated
post-quantum roadmap goes further and recommends a standardised format, naming a cryptography
bill of materials as the example. What no instrument states is **which attributes, at what
obligation level, for which decision** — and without that, a supplier cannot know what a
conforming answer looks like, and each supervisory authority will reasonably arrive at its own.
Divergence is the default outcome rather than a risk.

This report proposes filling that space with **CBOM profiles**: defined attribute sets, with
obligation levels, each serving a named decision. It uses a supply-chain post-quantum migration
profile as the worked example, and it is addressed to the Commission because the space is at
Union level and the alternative is being filled nationally already.

**Migration is a coordination problem, not an engineering one.** It proceeds as a chain of
dependent stages — algorithm standardisation, protocol profiling, library implementation,
product adoption, deployment, and finally decommissioning the classical algorithms — alongside
parallel tracks for public-key infrastructure, hardware, and certification, and under
constraints of legacy, budget, expertise and performance. Each stage is owned by a different
party, blocked by the stage below it, and invisible to the parties depending on it. That
invisibility is the specific thing a profile addresses.

**The relevant experiment has already been run.** ENISA measured SBOM adoption ahead of the
Cyber Resilience Act and found that regulation drove investment decisively, that generation is
largely solved, and that consumption is not: most organisations rarely or never receive
artefacts from suppliers, most report a substantial gap between producing and using them, and
ENISA's own conclusion is that they serve compliance rather than security. **An artefact
produced under an obligation and then not read is the default outcome, not the failure case.**
Any cryptographic transparency measure that does not design against this will reproduce it, and
faster — cryptographic attributes are harder to normalise than component names, and reading them
requires scarcer expertise.

**What a profile does, and does not do.** It makes the same question reach every supplier in the
same terms, and — because question and answer are both machine-readable — makes asking,
checking, and monitoring machine operations rather than expert ones. That is what converts a
documentation improvement into something that mitigates the expertise shortage running through
every stage of the chain, and it is the operational substance of cryptographic agility. It does
not verify that any declaration is true, create visibility that does not exist, shrink a
signature, resolve doubt about new algorithms, or shorten a capital cycle. Chapter 8 accounts
for all twenty-five identified gaps on both sides of that line.

**Recommendations.** Nine, each answering a stated readiness criterion, and none requiring new
legislation. In summary: establish a reference EU baseline profile, defined independently of
serialisation format so the Union need not pick a winner between formats moving at different
speeds, with four profile families above it grouped by the decision each serves — procurement,
vulnerability response, migration, and compliance — and procurement built first as a pathfinder; fund consumer-side validation tooling as part of the deliverable rather than assuming
the market supplies it; publish model procurement clauses citing a named profile and version;
identify a custodian; and raise, where the standards models are made, the absence of any standard
means of expressing cryptography applied *between* two parties. That last gap is the one this
report cannot solve and does not claim to.

**A note on precedent and on pace.** The mechanism is not novel in Europe: Germany's BSI already
defines required SBOM content and binds it to a format through a published taxonomy. And two
cautions bear on timing — protocol profiling is still in motion for several families, and
certification throughput is structurally limited, so an obligation that outruns the stages it
depends on produces declarations and queues rather than migration. Neither is an argument for
delay; both are arguments for sequencing.

**Finally, the durable case is not post-quantum.** Algorithms standardised today will be
deprecated; parameters will change; hybrid modes will be retired. The chain will be walked
again. The question is whether Europe emerges from this transition able to do the next one —
which requires knowing what cryptography is in use, checking a proposed change against policy,
and confirming it took effect, repeatedly and at scale. The post-quantum transition is the
occasion for building that capability, not the reason for it.


---

# 2  Cryptographic opacity across the supply chain

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text

A European operator of critical infrastructure, asked today which of its systems are protected
against an adversary recording traffic now to decrypt later, cannot answer. Not because the
question is hard, and not through negligence — but because the answer is distributed across
suppliers it has never contracted with, in a form nobody has agreed how to write down.

That is the subject of this report. It is stated here before any bill-of-materials vocabulary
appears, because the vocabulary is the proposed remedy and the problem is prior to it.

## 2.1  Exposure is set by parties the buyer cannot see

Harvest-now-decrypt-later gives ordinary supply-chain opacity a deadline. Traffic captured today
under classical cryptography is decryptable whenever a sufficiently capable quantum computer
arrives; the value of the protection therefore depends on how long the data stays sensitive, not
on when the machine appears. For anything with a long confidentiality life — health records,
legal and financial archives, state communications, industrial designs — the exposure is already
incurred.

What determines that exposure is not the operator's own cryptography. It is the weakest link in
a chain the operator can see perhaps one tier into. The buyer contracts with a primary supplier;
the cryptography is frequently in a library or hardware module two or three tiers further down,
integrated by parties whose names never appear in the contract. And once a product is deployed,
its cryptographic posture is fixed for a service life measured in years and, for
hardware-anchored elements, in decades.

## 2.2  The question that cannot be asked

Suppose the operator asks. Today the same enquiry, sent to five suppliers, returns five
incommensurable answers: a spreadsheet, a security questionnaire response, a PDF datasheet, a
statement that the matter is confidential, and silence.

None is unreasonable in isolation. There is no agreed form for the question, so each supplier
answers the question they understood; there is no agreed vocabulary, so the same algorithm
appears under three names; there is no agreed scope, so one supplier answers for the product and
another for the library inside it; and there is no obligation, so a supplier for whom the honest
answer is unflattering may reasonably decline.

The operator's cost is not that any single answer is wrong. It is that the answers cannot be
compared, aggregated, or checked — so the effort of collecting them produces no position on
which action can be taken. Multiply by a supplier base in the hundreds and the exercise stops
being worth running, which is why, in the adjacent domain of software transparency, most
organisations that receive such artefacts do not use them (§6.1).

## 2.3  The cryptography that matters is between the parties

A more fundamental difficulty sits underneath the practical ones, and it recurs throughout this
report.

Cryptographic inventories describe what a component *has*: the algorithms it implements, the
libraries it links, the certificates it holds. But cryptography secures a *connection*, and a
connection has two ends. Whether traffic between two components is protected against a future
quantum adversary depends on what both ends support, what was negotiated between them, and what
configuration was in force at the time — none of which is a property of either component alone.

This report calls that locus a **cryptographic relationship**, and the participants in it
**endpoints**. The terms are used consistently from here on. A relationship is not a
cryptographic asset: it is where cryptography is applied, between parties, and it appears in
neither party's inventory.

The consequence for supply chain is direct. Even if every supplier produced a perfect inventory
of its own component, the buyer would still not know whether the connections between those
components were secure. And the ordinary state of the internet in 2026 illustrates the problem
rather than the exception: a connection may carry post-quantum key establishment while its
certificate authentication remains classical (§7.1) — one relationship, two different answers,
recorded in neither endpoint.

Section 7.1 records this as the structural gap in current standards; §12.2 recommends it be
raised where the models are made. It is named here because everything that follows depends on
the distinction.

## 2.4  Why transparency is the precondition

Nothing above is an argument for a particular artefact, format, or instrument. It is an argument
that the migration described in the next chapter cannot be planned, sequenced, or evidenced
while the information required to do so is unaskable.

Migration planning needs to know which systems are exposed and in what order to address them.
Procurement needs to avoid acquiring, today, the constraint that blocks the migration in 2030.
Supervision needs to distinguish progress from assertion. Each of those is a different question,
and each is unanswerable for the same reason.


---

# 3  What PQC migration actually involves

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text · **Register: `LYR-*`**

> **Drafting note.** This chapter carries the report's central structural claim: migration is a
> chain of dependent stages, each owned by a different party, and no party can see the progress
> of the parties it depends on. Chapters 7, 8 and 11 all consume it. The page cap has been lifted
> (DR-10) — this chapter carries the structural argument the rest of the report consumes.

Post-quantum migration is routinely described as replacing one set of algorithms with another.
That description is accurate and almost entirely unhelpful, because it locates the work in a
single place. In practice the work is distributed across at least a dozen organisations that
have no contractual relationship with one another, and it proceeds in a fixed order that no
individual participant controls.

This chapter sets out that order. It distinguishes a **core chain**, in which each stage is
blocked until the stage before it completes; two **parallel tracks** that run on their own
timelines and converge at deployment; and **cross-cutting constraints** that bound what is
achievable at every stage. The purpose is not to be exhaustive about the engineering. It is to
establish, before any bill-of-materials vocabulary appears, that the binding difficulty is
coordination between parties rather than cryptography.

## 3.1  The shape of the problem

| Track | ID | Stage | Owned by | Blocked until |
|---|---|---|---|---|
| Core chain | LYR-C-01 | Algorithm standardisation | standards bodies | — |
| | LYR-C-02 | Protocol profiling | IETF, sector bodies | LYR-C-01 |
| | LYR-C-03 | Library implementation | implementers | LYR-C-02 |
| | LYR-C-04 | Adoption in products and components | suppliers | LYR-C-03 |
| | LYR-C-05 | System deployment, preserving availability and interoperability | integrators, operators | LYR-C-04 |
| | LYR-C-06 | Decommissioning classical algorithms and retiring hybrids | operators | LYR-C-05 |
| Parallel | LYR-T-01 | PKI and trust infrastructure | CAs, trust store operators, relying parties | LYR-C-02 |
| | LYR-T-02 | Hardware and roots of trust | silicon and module vendors | LYR-C-01 |
| | LYR-T-03 | Validation and certification | schemes, labs, sponsors | LYR-C-03 |
| Constraint | LYR-X-01 | Legacy estate within budget and lifecycle limits | operators | — |
| | LYR-X-02 | Expertise and capacity | all parties | — |
| | LYR-X-03 | Performance and resource cost | all parties | — |
| | LYR-X-04 | Confidence in the new algorithms | all parties | — |
| | LYR-X-05 | Operational risk and change tolerance | operators | — |
| | LYR-X-06 | Incentive and threat-timeline uncertainty | all parties | — |
| | LYR-X-07 | Regulatory divergence and sovereignty | suppliers, operators | — |

The tracks are not a second-order detail. A product can hold a validated PQC library, speak a
profiled PQC protocol, and still be unable to establish a single post-quantum session because
no certificate authority will issue it a suitable certificate, or because the root of trust in
the device it must authenticate to is fixed in silicon. Treating PKI and hardware as stages
inside the chain rather than as tracks converging on it produces a diagram that is tidy and
wrong.

## 3.2  The core chain

### LYR-C-01  Algorithm standardisation

The most visible stage and the only one that is substantially complete. Standardisation
establishes the primitives, their parameter sets, and the security levels they claim. It does
not say how they are used.

This stage is where public attention has concentrated, which has had an unhelpful side effect:
its completion is widely read as migration being underway, when it is the precondition for
work that has barely started at the stages below.

### LYR-C-02  Protocol profiling

Primitives are not deployed; protocols are. Between a standardised algorithm and a working
connection sits the question of how the algorithm is carried — negotiation, identifiers,
message sizes, fallback behaviour, and whether classical and post-quantum algorithms are
combined and how. This is decided in the IETF for general-purpose protocols and in sector
bodies for sector-specific ones, and it is decided protocol by protocol.

Two features of this stage matter for the rest of the report. It is **plural**: there is no
single completion date, because TLS, IPsec, code signing, secure messaging, and each sector
protocol proceed independently. And it is **the last stage at which design choices are cheap** —
a decision taken here propagates into every library, product and deployment above.

The per-protocol position as of mid-2026 makes the plurality concrete, and the report should
show it at this granularity rather than asserting it (VL §3b): IPsec/IKEv2 integration is
mature with finalised RFCs; hybrid key agreement for TLS is IESG-approved and awaiting RFC
publication; PQ-only key agreement for TLS remains in working group last call; PQ certificate
authentication for TLS likewise; JOSE and COSE are at active draft; parts of X.509 and CMS are
published. One protocol family being finished says nothing about the next.

> **Verify (pass 3):** re-check each row against the datatracker immediately before
> publication. This is the stage most likely to move.

### LYR-C-03  Library implementation

Implementations of the profiled protocols, in the libraries that products actually consume.
Correctness is necessary but not sufficient: implementations must also be maintained,
packaged, and made available on the platforms and language runtimes suppliers use, including
the constrained and embedded environments common in critical infrastructure.

Availability at this stage is uneven in a way that is easy to miss from the outside. A library
may support an algorithm in its development branch, in its stable release, or in the version
that a supplier's platform actually ships — three quite different things.

### LYR-C-04  Adoption in products and components

The stage at which the supply chain becomes the constraint. A supplier must take an available
library, integrate it, expose the necessary configuration, test interoperability, and ship it.
Then their customer must do the same, and so on up the chain — frequently through three or
four tiers, each of which is blocked by the tier below.

This is also the first stage at which the visibility problem becomes acute. A buyer can
observe that a product has shipped; they cannot observe whether the cryptography inside it is
post-quantum capable, at which version, on which interfaces, and under which configurations.
Nor can they observe where their supplier sits in their own dependency chain. Almost every
commercial gap in chapter 7 lands here.

### LYR-C-05  System deployment, preserving availability

Deployment into running systems that cannot stop. This stage introduces requirements the
stages below do not have: staged rollout with rollback, interoperability across mixed-version
estates during the transition, and negotiation behaviour that degrades safely when the two
endpoints of a connection are at different points in their own migrations.

Two problems that are specific to this stage:

- **The cryptography that matters sits between components.** A connection is established
  between two parties, and neither party's inventory describes it. What each supplier can tell
  you is what their component supports; whether the connection is post-quantum depends on both
  ends and the configuration in force. This is the structural gap introduced in §2.1 and
  recorded as GAP-STD-03.
- **Capability is not configuration.** A deployed system may be entirely PQC-capable and
  running classical cryptography, and may revert across a configuration change or a failover.

### LYR-C-06  Decommissioning classical algorithms

Migration is not complete when post-quantum cryptography is switched on. It is complete when
classical algorithms are switched off, hybrid modes are retired, and the fallback paths that
made the transition survivable are removed. Until then, an attacker able to force
downgrade — or simply able to capture traffic on a connection that has quietly reverted — is in
the same position as before.

Naming this as a stage is deliberate. Without it, every party in the chain can declare success
at the midpoint, and the harvest-now-decrypt-later exposure that motivated the work persists
behind a completed migration programme. Backward-compatibility obligations make this the stage
most likely to be indefinitely deferred (GAP-LIFE-03).

## 3.3  The parallel tracks

### LYR-T-01  PKI and trust infrastructure

Authentication depends on certificates, and certificates depend on issuance, chains, trust
stores, and roots. A post-quantum handshake requires a certificate the relying party will
accept, issued under a chain it trusts, from a root already distributed to it. Root
distribution and rollover run on multi-year cycles that are not synchronised with any product
release schedule, and the constraints propagate: certificate sizes, chain construction,
issuance policy, and revocation all interact with the protocol choices made at LYR-C-02.

The current position illustrates the point better than any argument could. Hybrid post-quantum
key agreement is widely deployed in browsers and servers, while no post-quantum root has entered
the major trust stores and the CA/Browser Forum has no merged requirement permitting ML-DSA in
publicly trusted certificates (VL §3b). The result is a **split state inside a single
connection**: the session key is post-quantum, and the certificate that authenticated it is
not.

That asymmetry is worth dwelling on, because it is the clearest available demonstration of two
claims this report makes elsewhere. "PQC enabled" is not one state — a single cryptographic
relationship can be post-quantum on key establishment and classical on authentication, which is
precisely why the migration profile carries a retirement state per relationship (DR-09). And
the asymmetry sits on the *connection*, not in either endpoint's inventory, which is the
structural gap of §2.1.

Size drives the timeline. Replacing the authentication data in a typical handshake with
post-quantum signatures takes it from roughly 1.2 kB to roughly 14.7 kB, while certificate
validity periods are being cut in stages toward 47 days — more frequent issuance, each carrying
the larger payload (VL §3b). LYR-T-01 and LYR-X-03 bind together here exactly as the structure
predicts. And because roots commonly carry 20–30 year validity, roots issued today on classical
algorithms will sit in trust stores well into the post-quantum era: a parallel track bounded by
LYR-X-01.

For a policy audience this track deserves explicit treatment, because it is infrastructure in
the ordinary sense — shared, slow to change, and belonging to no single market participant.

### LYR-T-02  Hardware and roots of trust

Silicon, secure elements, hardware security modules, trusted platform modules and smartcards.
Three properties distinguish this track: lead times measured in years rather than releases;
migration by replacement rather than update; and, in many cases, a root of trust that is fixed
at manufacture and cannot be changed at all.

The figures bear this out (VL §3c): HSMs in financial, CA and government use run on ten- to
twenty-year replacement cycles, and TPMs are typically soldered in and cannot be replaced
independently of the board. An organisation that deployed a classical-only module recently
chooses between a firmware upgrade where one exists, a disruptive hardware replacement, or
deferred protection. Note also the interaction with the certification track: capability shipping
in a product is not the same as adoptability in a regulated sector, and as of early 2026 no HSM
vendor had completed a Level 3 validation covering post-quantum algorithms.

Splitting hardware out of LYR-C-04 rather than treating it as a kind of product is what makes
the interaction with LYR-X-01 visible. Where cryptography is hardware-anchored, migration is a
capital refresh, and the decision that determined it was taken at procurement, years before
anyone was asked about post-quantum readiness.

### LYR-T-03  Validation and certification

FIPS and CMVP validation, Common Criteria evaluation, and national schemes. In regulated
sectors an unvalidated implementation is not adoptable regardless of its correctness, so this
track functions as a gate between LYR-C-03 and LYR-C-04 for a substantial share of the market.

It is also a queue with finite capacity, and the evidence is that this is structural rather
than a passing backlog: validation has been running well over a year from submission to active
certificate, with the average lengthening rather than shortening (VL §2). It is therefore a rate
limiter independent of any technical readiness. Any policy instrument that accelerates demand at LYR-C-04 without
regard to capacity here produces a backlog rather than a migration.

> **Verify (pass 3):** LYR-T-02 remains unsourced — hardware lead times and root-of-trust
> update paths have not been checked. LYR-T-01 and LYR-T-03 are sourced (VL §2, §3b).

## 3.4  The cross-cutting constraints

Seven constraints bound what is achievable at every stage above. They are not a list of
excuses: each one determines the pace at which a stage can actually move, and instruments that
assume migration is primarily a technical decision will misjudge that pace. Register §D.3 records
the admission test used, and the candidates that failed it.

### LYR-X-01  Legacy within budget and lifecycle limits

Presenting legacy management as a final step would imply it is dealt with last. The opposite is
true: it bounds every stage above, and the decisions that created it were taken at procurement,
sometimes a decade earlier. Long service lives, capital depreciation cycles, end-of-support
products that will never receive an update, and equipment that cannot be taken out of service
all constrain the pace at which LYR-C-05 and LYR-C-06 can proceed.

The budget point is not incidental. Migration competes for capital with every other programme,
and — see LYR-X-06 — the case for it is made against a threat with no fixed date.

### LYR-X-02  Expertise and capacity

The binding constraint at more stages than any other, and the one most often mistaken for a
technical problem. The people who can profile an algorithm into a protocol, review an
implementation for side channels, and write a defensible cryptographic requirement into a
tender are substantially the same small population.

It manifests differently at each stage. At LYR-C-02, working group participation bounds how
many protocol families can be profiled in parallel. At LYR-C-03, the scarce capability is
*review* rather than authorship: implementations that look correct are not hard to produce,
while constant-time, side-channel-resistant, correctly parameterised implementations reviewed
by someone competent to judge them are. At LYR-C-04, a buyer who cannot specify the requirement
cannot evaluate the answer, so capacity gates the demand signal itself. On the tracks, it is
issuance policy design and evaluation lab throughput.

One consequence is that concentration is a capacity phenomenon: where few implementations are
trusted, everyone queues behind the same ones, and a defect or delay propagates market-wide.

A concrete illustration, and worth using because it is unusually clean: a cryptography
workstream inside one of the two major BOM standards reported in 2026 that the work it could not
progress was not difficult — it lacked a single contributor with the knowledge and the time to
do it (VL §2). Standards capacity is measured in people, not in intent.

> This report treats capacity as a single constraint with per-stage manifestations. A fuller
> treatment is out of scope — see register §D.3.

### LYR-X-03  Performance and resource cost

Post-quantum key and signature sizes are materially larger than their classical equivalents,
and this propagates. It shapes protocol design at LYR-C-02, implementation choices at LYR-C-03,
and imposes hard limits at LYR-C-05 on constrained devices, high-volume interfaces, and links
where message size interacts with fragmentation or latency budgets. Some deployments cannot
absorb the overhead at any level of funding, which distinguishes this constraint from LYR-X-01.

### LYR-X-04  Confidence in the new algorithms

Hybrid modes exist because confidence in the new algorithms, while high, is not the confidence
that comes from decades of concentrated cryptanalysis. That uncertainty slows commitment
independently at three stages: what to profile at LYR-C-02, what to ship at LYR-C-04, and — most
consequentially — whether to retire the classical half at LYR-C-06. It is the main reason
LYR-C-06 slips, and it is a constraint that resolves with time rather than with money or policy.

### LYR-X-05  Operational risk and change tolerance

Distinct from budget. Critical infrastructure operates with rare change windows, mandatory
availability targets, and a low appetite for experimentation at the handshake layer. A change
that is affordable and technically ready may still wait for a window, and a failed
cryptographic change fails closed — the connection does not degrade, it stops. This bounds
LYR-C-05 and LYR-C-06 regardless of funding or expertise.

### LYR-X-06  Incentive and threat-timeline uncertainty

There is no fixed date. Migration therefore competes for capital and attention against
programmes that have deadlines, and it does so with a benefit that is contingent, deferred, and
invisible if the work succeeds. This explains hesitancy at LYR-C-04 and delay at LYR-C-05 and
LYR-C-06 more fundamentally than any technical gap does — and it is the constraint that
regulation exists to address, which makes it the most policy-relevant item in this section.

### LYR-X-07  Regulatory divergence and sovereignty

National parameter preferences, sovereign certification requirements, and export control regimes
mean a supplier may face several incompatible answers to the same question. Divergence
multiplies the cost of every other constraint: capacity is spent several times over, and
performance and certification budgets are duplicated per jurisdiction. It binds at LYR-C-02,
LYR-C-04, and on both the PKI and certification tracks.

For this report's audience the point is direct: divergence is not only a constraint the
Commission observes, it is one the Commission is positioned to reduce.

## 3.5  Why the structure matters for this report

Three consequences, each load-bearing later.

**Readiness is not uniform.** Stating that the supply chain is unready is not useful; the
question is where. Chapter 7 tags every gap against the stage or track at which it bites, and
the distribution is markedly uneven. That cross-tab (§7.8) is a sharper finding for a policy
audience than a flat list of shortcomings.

**Waiting is rational.** Most EU instruments address LYR-C-04 and above, while LYR-C-02 is
still in motion for several protocol families and LYR-T-03 has finite throughput. A supplier
that commits early to a configuration may have to withdraw it. This explains supplier
hesitancy without ascribing bad faith to it, and it sets up the phasing argument in §11.8.

**The constraints are what a profile is measured against.** A profile does not shrink a
signature, resolve cryptanalytic doubt, create a change window, or lengthen a capital cycle.
What it does is make the questions machine-askable and machine-checkable, which lowers the cost
of operating under several of these constraints without removing any of them. Chapter 8 sets
out that mechanism (§8.1) and scores each constraint against it (§8.4), including the one it
does nothing for.

**Progress is invisible across the boundaries.** Each party depends on stages it does not own
and cannot observe. There is no mechanism by which a buyer learns where their supplier's
suppliers are, and no comparable form in which a supplier could tell them even if willing.
This is the specific absence that a CBOM profile addresses, and it is the transition into
chapter 4.

## 3.6  Migration is not a single event

Brief, but state it. Parameter sets will change; hybrid modes will be retired; algorithms
standardised today will be deprecated in time. The chain above will be walked again.

There is a sharper version of this point, and it distinguishes cryptography from software.
Cryptographic posture decays **without anything changing in the estate**: an intermediate
authority is revoked, a certificate expires, a key outlives its cryptoperiod, or a national
authority deprecates an algorithm. A software vulnerability requires a code change to come into
existence. A cryptographic one can arrive by announcement. An organisation can therefore be
compliant on Monday and not on Tuesday having deployed nothing — which is an argument for
continuous inventory rather than periodic audit. That is
the case for building durable capability — inventory, agility, and a repeatable way to ask the
supply chain a question — rather than running a one-off programme with an end date.

---

## Resolved drafting questions

1. **Data-at-rest re-encryption** — sub-stage of LYR-C-05, not a separate stage (DR-07). Give it
   a paragraph within C-05: backups, archives and stored keys are central to
   harvest-now-decrypt-later, and re-encryption is bounded by LYR-X-05 as much as by budget.
2. **Interoperability testing** — remains within LYR-C-05 (DR-07), despite its plug-test
   resemblance to LYR-T-03.
3. **Depth per stage** — cap lifted (DR-10). LYR-C-04 and LYR-C-05 still take the larger share.
4. **Maturity claims** — the register's `Position today` column needs an owner or is deleted
   before v1.0 (DR-07). It does not ship empty.

*Register: `../register.md` §D. Layer tags on gaps are maintained there.*


---

# 4  What a CBOM profile is

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text · **Target: under 3pp**

Enough to follow chapters 6 to 12 without reading a specification. If this chapter grows beyond
three pages, the report has become one.

## 4.1  From inventory to profile

A **cryptographic bill of materials** is a structured, machine-readable inventory of the
cryptography associated with a product or system: the algorithms and parameters in use, the
protocols composing them, the keys and certificates supporting them, the libraries or hardware
implementing them, and the configurations determining how each is actually used. It is modelled
on the software bill of materials, deliberately, so that cryptographic information travels the
supply-chain channels and tooling that already exist for software rather than requiring parallel
ones.

An inventory alone does not settle what a given exchange should contain. Reporting every
cryptographic call in a large product can produce thousands of entries and bury the handful that
bear on any particular decision, while omitting the one attribute that decision actually needs.

A **profile** resolves that. It is a defined subset of attributes, each with an obligation level,
serving a named decision — stated precisely enough that two parties can produce and check
conforming artefacts without further negotiation.

## 4.2  Four properties that matter for policy

**It serves a decision, not an obligation.** A profile begins by naming the question it answers.
This is the discipline that separates an artefact somebody uses from an artefact somebody files
(§6.1).

**It is machine-readable, and therefore automatable.** The profile is a specification a machine
can enforce, not a document a person must interpret. Generation in a build pipeline, validation
at a deployment gate, comparison between releases, re-checking one artefact against another
jurisdiction's profile — all machine operations. This is the property that does the work in
chapter 8, and it is also the substance of cryptographic agility: knowing what you have,
checking a change against policy, and confirming it took effect.

**It runs in both directions.** A profile is a *production recipe* — how to generate a conforming
artefact — and a *conformance checklist* — how to verify one received. Both matter here: the
first is what suppliers do, the second is what procurement and supervision do. A specification
written only for producers is how the consumption gap opens.

**One artefact can satisfy several profiles.** A single CBOM may conform to a procurement
profile, a migration profile and a regulatory-reporting profile at once, each consumer reading
the subset its profile defines. This is the direct answer to duplicated supplier effort across
jurisdictions and use cases, and it turns divergence from a duplication problem into a mapping
problem.

## 4.3  Two declarations that come before the attributes

A profile is underspecified without two statements about itself, and both matter to a consumer
trying to judge what they are reading.

A related distinction runs underneath both, and it is why `lifecycleStage` exists. A built
artefact states a **capability ceiling** — what the software can do. The deployment states a
**configured floor** — what it is permitted to do here. A strong implementation can be rendered
weak by a permissive configuration, and neither number is derivable from the other.

**Orientation.** A profile declares itself `inventory` (present state), `migration` (adds
forward-looking capability, dependency and roadmap facts), or `both`. Orientation *classifies*
a profile; it does not reinterpret anything. An attribute shared with another profile keeps its
meaning, and forward-looking facts are carried under distinct attribute names rather than by
reading an existing present-state field differently. Without that rule, a consumer aggregating
artefacts from many suppliers cannot tell deployed reality from vendor intent, because the two
arrive in the same field.

One consequence is worth stating early: because scope determines what can be asserted, a
profile's obligations differ by scope rather than requiring a separate profile per kind of
subject. A supplier's product artefact and an operator's deployed-service artefact conform to
the same profile, with different mandatory sets (§10.7.1).

**Subject scope.** A profile declares what kind of thing it describes — a component, a product,
a deployed service, or a bounded estate. This is not labelling. It determines what evidence the
producer can have and what they have authority to disclose. A vendor asserting a product CBOM
speaks from build-time evidence about something it controls entirely; an operator asserting a
deployed-service CBOM speaks from runtime evidence about a boundary containing components it
did not build and may not be free to describe. Two CBOMs that appear to disagree may not be in
conflict at all — one describes what a product can do, the other what a deployment does.

## 4.4  Format-independence

A profile defines *what* must be captured. It does not define *how* the result is serialised.
The same content is then mapped onto the formats in use — currently CycloneDX and SPDX, which
sit at markedly different stages of cryptographic maturity (§7.1).

For a technical audience this is good practice. For a policy audience it is more than that: it
means content can be specified without selecting a format winner, and without the specification
becoming obsolete when the formats move. Where a format cannot carry an attribute, the gap is
documented and raised with the specification body rather than silently dropped.

## 4.5  What a profile is not

It is not a format, a competing standard, or a tool. It is not an attestation: a conforming
artefact is internally consistent and checkable against policy, but nothing in it verifies that
the supplier's declarations are true.

**Nor is it a statement of exploitability.** A CBOM records that an algorithm is present; it
does not say whether that algorithm is reachable, negotiable, or actually relied on in a given
deployment — which is usually the question a defender or a supervisor is really asking. That
judgement belongs in a separate assertion artefact referencing the CBOM, with its own author,
date and scope, in the way exploitability statements sit alongside software inventories rather
than inside them (DR-11, §9.3). The distinction matters because inventory alone generates
volume rather than action, which is exactly how the software case failed (LSN-10). And it is not a substitute for the instruments that create
an obligation to produce one — chapter 8 is explicit about the difference between what a
specification can do and what requires a market or a regulator.


---

# 5  Policy anchoring

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text

This report describes a gap inside existing European policy, not a case for new policy. The
instruments below already establish that cryptographic inventory is expected. What none of them
establishes is what such an inventory must contain.

## 5.1  The instruments

| Instrument | Relevance to cryptographic inventory | Names CBOM? |
|---|---|---|
| Cyber Resilience Act (2024/2847) | Binding. SBOM-based supply-chain transparency for products with digital elements; general expectation of appropriate cryptographic protection | No |
| NIS2 Directive, implementing regulation, and ENISA technical implementation guidance | Binding directive; guidance recommends organisations inventory cryptographic assets | No |
| Commission Recommendation (EU) 2024/1101 | Recommendation. Establishes the coordinated PQC transition and the workstream that produced the roadmap | No |
| NIS Cooperation Group coordinated PQC roadmap (June 2025) | Recommendation with strong political backing. Milestones at end-2026, 2030 and 2035; recommends a standardised format for cryptographic inventories | **Yes — by name** |
| COM(2026) 13 — proposed NIS2 amendment | Proposal. Would require Member States to adopt PQC transition policies aligned to the roadmap milestones | No, but names PQC |
| BSI TR-03183 (national) | Non-binding national guideline in three parts; Part 2 specifies SBOM format and content. No CBOM part | Part 2 is SBOM |

> **Verify (pass 5):** article references against the source texts; the adoption status of
> COM(2026) 13; whether the NIS CG technical recommendations have been published; and whether
> any harmonised standard under M/606 has been cited in the Official Journal.

## 5.2  Three qualifications

**The roadmap does name CBOM.** An earlier draft of this report recorded the reference as
indirect. It is not: the coordinated roadmap recommends a standardised format for cryptographic
inventories and names CBOM as the example (VL C-01). The report's argument is correspondingly
narrower, and better for it — see §5.3.

**BSI disclaims its own standing.** TR-03183 is explicit that it is not binding, cannot confer a
presumption of conformity, and is expected to be replaced by harmonised European standards once
those exist (VL §3c). It is a national interim, not a parallel regime — but see §5.4, because it
is also the most useful precedent in this table.

**A proposal is not law.** COM(2026) 13 would make PQC transition planning a named component of
national cybersecurity strategy rather than something reached by interpretation. If adopted it
materially strengthens the supervisory route in §11.3. Its status must be re-checked before
publication.

## 5.3  The gap

Cryptographic inventory is a recurring expectation across these instruments. In one case a
format family is named. In none is it specified **which attributes, at what obligation level,
for which decision**.

That distinction is the whole of the space this report addresses. "Maintain a cryptographic
inventory in a standardised format" leaves a supplier unable to know what a conforming answer
looks like, and leaves each supervisory authority to determine it independently — which is why
divergence between Member States is the default outcome rather than a risk (GAP-POL-02).

It is worth being precise about what is *not* being claimed. The instruments are not deficient
for failing to specify attribute sets; that is not what directives and recommendations do. The
observation is simply that the specification layer beneath them is empty, and that something has
to occupy it before the expectations above can be met consistently.

## 5.4  A precedent already exists

The mechanism this report proposes is not novel in Europe. BSI TR-03183-2 defines required SBOM
content, names the accepted format versions, and binds its additional fields to a format through
a published property taxonomy (VL §3c).

That is a European technical authority doing profile-shaped work today, for software. What this
report proposes is the same mechanism applied to cryptography, at Union rather than national
level. The precedent matters for two reasons: it demonstrates the approach is workable rather
than theoretical, and it suggests that in the absence of a Union-level answer, national answers
will arrive anyway — which is the divergence problem beginning rather than a hypothetical.


---

# 6  Lessons from SBOM adoption

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text · **Cap: 6pp (DR-05)**
**Register: `LSN-*`**

This chapter is not background. It is the evidence base for the claim that the difficulties
ahead are predictable, and it has an unusual advantage: the experiment has already been run,
in this jurisdiction, under a comparable instrument, and the Commission's own agency has
measured the result.

ENISA surveyed SBOM adoption at the end of 2025 and published the analysis in June 2026. Its
findings are the spine of this chapter, and they should be read as a forecast of CBOM adoption
rather than a report on a neighbouring topic.

## 6.1  What the evidence shows

**Regulation moved adoption; nothing else did** (LSN-P-04). The survey is unambiguous that the
Cyber Resilience Act is the accelerator: roughly four in ten organisations reported that it
significantly increased their investment in tooling and automation, with a further group
reporting moderate influence. Voluntary advocacy had produced a decade of slower progress. This
finding underwrites chapter 11 entirely — the question is not whether an instrument is needed,
but which one.

**Generation is close to solved; consumption is not** (LSN-01, LSN-07). Most organisations now
produce SBOMs, frequently automated per release and integrated into build pipelines. Receiving
and using them is a different picture: only a small minority always receive SBOMs from
suppliers as part of procurement, while a large share receive them rarely or never. Most
organisations report a moderate or significant gap between generating artefacts and actually
using them, and a substantial minority do not know whether their organisation consumes them at
all.

ENISA's own summary is that SBOMs are used <cite index="102-1">"mainly for compliance purposes"</cite> rather than for active security work.

That sentence is the single most important line in this report's evidence base. An artefact
produced to satisfy an obligation, and then not read, is the default outcome — not the failure
case. Any CBOM instrument that does not design against it will reproduce it.

**Maturity is thin** (LSN-01). Although a large majority have begun, only about one in ten
report a mature, highly automated implementation. Most remain in pilots or limited deployment.
The distance between having started and being able to act is the whole of the problem.

**Expertise is the binding constraint on adoption** (LSN-07, and LYR-X-02). Research into
stakeholder groups found lack of knowledge or expertise to be the leading reason organisations
fail to adopt, cited by around seven in ten. This is the same constraint chapter 3 identifies
running through the migration chain, measured independently in the adjacent domain.

**Format fragmentation persists under a regulation that names formats** (LSN-05). A significant
minority of organisations remain on proprietary formats despite both the CRA guidance ecosystem
and BSI TR-03183 naming CycloneDX and SPDX. Naming a format does not settle the format
question; it narrows it.

**Completeness is not achievable by effort alone** (LSN-03). Even organisations with mature
development practice produce incomplete artefacts, because upstream open-source projects do not
produce them for their own software. The incompleteness is inherited, not chosen — and an
incomplete inventory can mislead as effectively as no inventory.

## 6.2  What this predicts for CBOM

Each finding maps to a design consequence. The register carries the full set (`LSN-01`…`LSN-10`);
these are the ones that change how a profile is specified.

| Observed | Consequence for a CBOM profile |
|---|---|
| Artefacts produced for compliance, not read (LSN-01) | Define profiles by the **decision** they serve, not by the obligation that prompts them (aspect 3.1) |
| Consumption lags production badly (LSN-07) | Consumer-side validation is a first-class deliverable, not a downstream concern (aspect 3.5) |
| Expertise is the top barrier | The profile must reduce the expertise needed to *ask*, not only to answer (§8.1) |
| Incompleteness inherited from upstream (LSN-03) | Scope and completeness statements, so an incomplete artefact is visibly incomplete (aspect 3.1) |
| Minimum-element floors too low to act on (LSN-02) | Obligation levels set per use case, against a decision (aspect 3.4) |
| Identity unresolvable across tools (LSN-04) | Normalised vocabularies and stable identifiers (aspect 3.7) |
| Format fragmentation persists (LSN-05) | Content defined once, independently of serialisation, then mapped (aspect 3.6) |
| Build-time snapshot drifts from deployment (LSN-06) | `lifecycleStage` — intended / implemented / configured / observed (aspect 3.3) |
| Disclosure resistance (LSN-08) | Bounded disclosure as an explicit purpose of obligation levels (aspect 3.4) |
| No agreed exchange channel (LSN-09) | Delivery, governance and versioning specified (aspect 3.11) |
| Output unusable without VEX (LSN-10) | Layering onto SBOM, HBOM and adjacent artefacts (aspect 3.8) |

## 6.3  What worked, and transfers

Three assets carry over, and they are why the CBOM case is credible at all rather than merely
plausible.

**Generation in the build pipeline** (LSN-P-01). The survey shows per-release generation
substantially automated. Cryptographic inventory can ride the same pipeline at low marginal
cost, and the organisational argument for doing so has already been won.

**Shared identity conventions** (LSN-P-02) — package identifiers and the practice of pinning
versions — are directly reusable for library-level cryptographic provenance.

**An existing tooling ecosystem** (LSN-P-03). CBOM inherits generators, parsers, storage and
pipeline integration rather than rebuilding them. This is the concrete reason for aligning CBOM
with the SBOM model rather than establishing a parallel one.

And a fourth, more consequential than the rest: **regulation works** (LSN-P-04), as above.

## 6.4  The transferable conclusion

SBOM's difficulties were **specification and incentive** problems far more than technical ones.
Nobody failed to produce artefacts. They produced artefacts that were incomplete, inconsistently
identified, formatted several ways, and — decisively — not consumed, because nothing specified
what a consumer should expect or gave them the means to check it.

A CBOM effort that repeats the specification error will fail the same way, faster, for two
reasons. Cryptographic attributes are harder to normalise than component names: a library
version is a string, while an algorithm in use is a function of implementation, configuration
and the party at the other end of the connection. And the consumption gap will be wider, because
reading a cryptographic inventory requires expertise that is scarcer than the expertise to read
a dependency list.

That is the case for defining the profile before mandating the artefact. It is also the case for
treating consumer tooling as part of the deliverable rather than as something the market will
supply once demand exists — the SBOM evidence is that it does not.

---

*Register: `../register.md` §A. Add or reword lessons there, not here.*


---

# 7  Why the supply chain is not ready

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text · **Cap: 6pp (DR-05)**
**Register: `GAP-*`, `RDY-*`**

> **Sourcing convention.** Sixteen of the twenty-five gaps below carry a source; nine are
> working group observation, and are written as such. Where this chapter says *we observe*, no
> public study was located and the claim rests on practitioner experience. That distinction is
> maintained deliberately: a report that presents observation as finding invites the reader to
> discount both.

The instruments in chapter 5 assume a supply chain capable of answering a cryptographic
question. This chapter sets out why it is not, organised by the kind of obstacle rather than by
who is at fault. Most of what follows is nobody's failure — it is the ordinary condition of a
market midway through a transition whose lower layers only recently settled.

## 7.1  Standards gaps

**Format asymmetry, not absence** (GAP-STD-01). Both major BOM formats are moving, at markedly
different stages. One carries a cryptographic object model ratified as an international
standard; the other's cryptography workstream took its first structural decisions in 2026 and
describes itself as at the beginning (VL §2). The consequence for policy is not that
cryptographic inventory is unexpressible — it is that content specified in one format is not
reliably recoverable from the other, so any instrument naming a single format picks a winner,
and any instrument naming both must say what it expects of each.

**Registry coverage** (GAP-STD-02). Algorithm registries are recent, and we observe that
sector-specific primitives — air-interface algorithms, national schemes, mission-critical voice
— are unevenly represented. A profile author encountering an absent algorithm has no normalised
term to reference.

**No expression for cryptographic relationships** (GAP-STD-03). The structural gap, and the one
that matters most for supply chain. Current models describe cryptographic assets as things a
component *has*. The cryptography that determines security in a multi-party chain is applied
*between* components, and belongs to neither inventory. Section 2.1 introduces the terms;
§7.8 records that this gap bites at deployment while originating in protocol profiling; §12.1
escalates it, because no profile resolves it.

The current state of the public web is the cleanest available illustration. A connection may
carry post-quantum key establishment and classical certificate authentication simultaneously
(VL §3b). Neither endpoint's inventory records that combination, because the combination is a
property of the connection.

**Roadmap commitments** (GAP-STD-04) have no agreed representation, so forward-looking supplier
statements arrive as prose and cannot be compared or tracked across releases.

**No conformance path** (GAP-STD-05), in two distinct senses. There is no CBOM conformance
suite or reference implementation — working group observation. And the validation machinery
that does exist is capacity-constrained: certification has been running twelve to eighteen
months from submission to certificate, described as structural rather than a passing backlog,
with the average lengthening (VL §2). An instrument that increases demand here without regard
to throughput produces a queue, not a migration.

**Fragmented PKI inventory models** (GAP-STD-06) and **protocol profiling still landing**
(GAP-STD-07). On the latter, the position is uneven by family rather than uniformly immature:
IPsec integration is mature with finalised RFCs, TLS hybrid key agreement was approved and
awaiting publication in mid-2026, TLS post-quantum certificate authentication remained in
working group last call, and JOSE and COSE are at active draft (VL §3b). One family finishing
says nothing about the next.

## 7.2  Discovery and tooling

A built artefact states a capability ceiling; the running configuration states the floor, and
the second is where security actually sits. Scanners address the ceiling: they find what code
*contains*, not what a system *does* (GAP-TOOL-01). A library present
in a binary may be unused; an algorithm compiled in may be disabled by configuration; a
configuration in force may revert on failover. We observe that the gap between compiled
capability and effective runtime posture is the single most common source of inventory error.

Firmware, hardware modules, trusted execution environments and sealed appliances resist
source-level analysis entirely (GAP-TOOL-02), and the position is worse than opacity alone
suggests: post-quantum support in embedded roots of trust depends on manufacturers shipping
updated firmware, which is outside the operator's control (VL §3c).

Consequently most cryptographic inventories are **declarations rather than measurements**
(GAP-TOOL-03) — a fact that should be visible in the artefact rather than assumed away.

The false-positive problem (GAP-TOOL-04) has a specific cause worth naming, because it is
fixable. Tools treat an algorithm identifier as a universal risk indicator: a scanner
encountering MD5 or SHA-1 raises a high-severity finding regardless of what the algorithm is
doing. But cryptographic weakness is a property of the **role**, not the primitive. MD5 used for
a digital signature is broken, because an adversary can construct collisions and forge an
identity. The same MD5 used to generate an HTTP ETag or index a hash table is harmless — a
collision costs a cache miss, and there is no adversary in the model at all.

An inventory that records the algorithm but not its role therefore cannot distinguish a genuine
exposure from a benign legacy use, and the consumer receives volume rather than signal. This is
the cryptographic form of the problem VEX was created to solve in software (LSN-10), and §8.2
records what a profile can do about it.

## 7.3  Commercial and contractual

No standard procurement language exists for requiring cryptographic transparency at a defined
content and version (GAP-COM-01), and no obligation to supply one exists in any instrument
surveyed in chapter 5 (GAP-COM-02). Suppliers who do disclose do so voluntarily, which selects
for those with least to disclose.

Disclosure resistance is real and partly legitimate (GAP-COM-03): open-ended cryptographic
detail exposes implementation choices with competitive value, and the SBOM era produced the
same objection in the same form (LSN-08). We observe that visibility in practice stops at the
first tier (GAP-COM-04) — flow-down obligations to sub-suppliers are rare and rarely enforced,
so a buyer's view ends precisely where the cryptographic dependency usually begins.

Finally, a category no instrument reaches: products already deployed and out of support will
never receive a bill of materials of any kind (GAP-COM-05). Whatever is agreed applies
prospectively.

## 7.4  Organisational capability

Cryptography sits outside most configuration and asset-management functions, and few
organisations have anyone accountable for cryptographic inventory as such (GAP-ORG-01,
GAP-ORG-02 — both working group observation). The data required sits with engineering and
procurement; the expertise to interpret it sits in security (GAP-ORG-03). This is not a
transparency problem and no artefact fixes it, but it determines whether a supplied artefact is
read.

## 7.5  Product lifecycle

Service lives in critical sectors are measured in decades: hardware security modules in
financial, certificate authority and government use run on ten- to twenty-year replacement
cycles, and roots of trust commonly carry twenty- to thirty-year validity, so roots issued today
on classical algorithms will remain in trust stores well into the post-quantum era (GAP-LIFE-01,
VL §3b/§3c).

Hardware-anchored cryptography cannot move on a software cadence (GAP-LIFE-02): trusted platform
modules are typically soldered to boards and cannot be replaced independently, and an
organisation with a recently purchased classical-only module chooses between a firmware upgrade
where one exists, disruptive replacement, or deferred protection (VL §3c).

Compounding both: cryptographic posture degrades out of band. A revoked intermediate, an
expired certificate, a key past its cryptoperiod, or an algorithm deprecated by a national
authority all change an estate's position without anything in the estate changing. Point-in-time
inventory is structurally mismatched to a risk that moves on its own.

And backward-compatibility obligations sustain deprecated algorithms indefinitely (GAP-LIFE-03).
This is why decommissioning is treated as a distinct stage in chapter 3: without it, the
transition can be declared complete while the exposure that motivated it remains.

## 7.6  Policy asymmetry

Instruments recommend cryptographic inventory and, in the case of the coordinated roadmap, name
a format family — but none specifies which attributes, at what obligation level, for which
decision (GAP-POL-01, VL C-01). That unoccupied space is the subject of this report.

Its consequence is that divergence between Member States is the **default outcome, not a risk**
(GAP-POL-02): absent a common definition, each supervisory authority reasonably arrives at its
own, and suppliers face several incompatible answers to one question. And it makes waiting
rational for suppliers (GAP-POL-03), since any early commitment may prove to be the wrong shape
— particularly while the protocol layer they depend on is still moving (§7.1).

## 7.7  What readiness would look like

Nine criteria, stated so that chapter 12 maps onto them one for one.

| ID | Criterion |
|---|---|
| RDY-01 | A named, versioned, publicly available profile for each recurring decision |
| RDY-02 | Content defined independently of format, with mappings maintained for both |
| RDY-03 | Normalised vocabularies covering the algorithms actually deployed |
| RDY-04 | Declared and observed states distinguishable within the artefact |
| RDY-05 | Machine-checkable conformance, with tooling available to consumers and not only producers |
| RDY-06 | A defined exchange channel and a supply obligation carried in procurement |
| RDY-07 | Forward-looking commitments expressed comparably |
| RDY-08 | An identified custodian with a change process |
| RDY-09 | A standard means of expressing cryptography applied between two parties |

Note what is absent. No criterion addresses service lives, capital cycles, or organisational
accountability, because no achievable specification would satisfy one. Those gaps are stated
here and answered, so far as they can be, elsewhere (§8.6).

## 7.8  Readiness by migration layer

Tagging each gap against the stage or track where it bites (register §D) gives a sharper answer
than "the supply chain is not ready".

**Core chain**

| Stage | Gaps biting here |
|---|---|
| LYR-C-01 Algorithm standardisation | — |
| LYR-C-02 Protocol profiling | GAP-STD-07, GAP-POL-03 |
| LYR-C-03 Library implementation | — |
| LYR-C-04 Adoption in products | GAP-STD-01/02/04, GAP-TOOL-01/04, GAP-COM-01/02/03/04, GAP-POL-01/02/03 |
| LYR-C-05 System deployment | GAP-STD-01, GAP-STD-03, GAP-TOOL-01, GAP-TOOL-03, GAP-POL-01 |
| LYR-C-06 Decommissioning | GAP-LIFE-03 |

**Parallel tracks and constraints**

| Track | Gaps biting here |
|---|---|
| LYR-T-01 PKI and trust | GAP-STD-06 |
| LYR-T-02 Hardware | GAP-TOOL-02, GAP-LIFE-02 |
| LYR-T-03 Validation and certification | GAP-STD-05 |
| LYR-X-01 Legacy and budget | GAP-COM-05, GAP-LIFE-01, GAP-LIFE-02 |
| LYR-X-02 Expertise and capacity | GAP-ORG-01/02/03 |

Three findings follow, and they are the substance of this chapter.

**The gaps cluster where the supply chain itself operates.** Thirteen of twenty-five bite at
LYR-C-04, the stage owned by suppliers and their customers. Almost none bite at the stages
furthest along technically. Readiness is not a uniform deficit to be closed by more standards
work at the bottom of the chain.

**Where instruments land is where the gaps are.** EU instruments predominantly address LYR-C-04
and above. That is fortunate in one sense — the policy attention is aimed at the right stage —
and hazardous in another: the stage is dense with gaps precisely because it depends on
everything below it, and several of those dependencies are still moving.

**Two gaps bite far from where they must be fixed.** GAP-STD-03 hurts at deployment but
originates in protocol modelling; GAP-COM-05 hurts as legacy cost but originates at
procurement, years earlier. Recommendations aimed at where a gap hurts will miss both.

---

*Register: `../register.md` §B, §C and §D. Add or reword gaps there, not here.*


---

# 8  What a CBOM profile fixes — and what it does not

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text · **Cap: 6pp (DR-05)**

Chapter 7 sets out twenty-five gaps between the supply chain as it is and a supply chain that
could answer a cryptographic question. This chapter answers them one at a time. It is
deliberately structured so that the answer *no* appears as often as it honestly should: a
report that claims a bill of materials solves a market coordination problem will be discounted
by the reader it is written for, and rightly.

`bash check-coverage.sh` fails if any gap in the register is missing from §8.2.

## 8.1  The mechanism: standardisation enables automation

Before the accounting, state how a profile acts at all. It is not that writing requirements
down makes them true. The mechanism is two-step, and the second step carries the value:

1. **Standardisation.** The profile fixes what is asked, in what vocabulary, at what obligation
   level — so the same question reaches every supplier, and the same answer means the same
   thing to every consumer.
2. **Automation.** Because question and answer are both machine-readable and defined against a
   published schema, asking, answering, checking and monitoring become machine operations.
   Generation in the build pipeline, validation at a deployment gate, comparison between
   releases, re-checking an unchanged artefact against another jurisdiction's profile.

The second step converts a documentation improvement into a constraint mitigation. Scarce
expertise (LYR-X-02) is spent once, on defining the profile, then executed repeatedly at no
marginal expert cost. Change risk (LYR-X-05) falls when posture is verified before deployment
rather than discovered after it. Divergence (LYR-X-07) costs less when one artefact is
re-validated by machine rather than re-answered by hand.

**Automation is also the substance of cryptographic agility.** Agility is usually described as
a property of a system — the ability to replace an algorithm without redesign. Operationally it
is a property of a *process*: knowing what you have, checking a candidate change against
policy, and confirming the change took effect, repeatedly and at estate scale. Each of those is
a machine operation over a conforming artefact. A profile is therefore not only a transparency
mechanism; it is a precondition for agility, and agility is what makes the chain in chapter 3
walkable a second and third time (§3.6). Carry this thread into §8.3 and §12.

One workflow is worth naming because it is where the two steps compound: tooling reads the
inventory, follows its locators to the current exploitability assertions, and resolves those
*before* surfacing anything to a person. Without that chain a consumer receives every present
algorithm as a finding; with it, they receive the ones that matter. This is a second demand on
consumer-side tooling beyond validation, and it bears on RDY-05.

Two qualifications, stated here rather than buried. Automation requires **consumer-side
tooling**, which is exactly where SBOM adoption fell short (LSN-07): a machine-readable
artefact nobody can machine-read is a document with extra steps. And automation amplifies
whatever the profile specifies — a poorly chosen attribute set is enforced faster, not better.

## 8.2  Gap by gap

Three columns, and the third is not a disclaimer. It marks the boundary between what a
specification can do and what requires a market, a regulator, or a decade.

### Standards gaps

| Gap | What a profile does | What it does not do |
|---|---|---|
| GAP-STD-01 Format asymmetry | Content defined once, independently of serialisation, then mapped. A consumer asks for the same information whichever format arrives | Does not close the model gap in either format, and cannot express what the target format has no room for |
| GAP-STD-02 Thin registry coverage | Forces the vocabulary question at authoring time: a profile that references an absent algorithm exposes the absence rather than hiding it behind free text | Does not populate the registry. The profile author must contribute upstream or carry a provisional local term |
| GAP-STD-03 No relationship expression | Names the relationship as the unit of interest and can require both endpoints and the connection between them to be described within its own scope | Does not fix the underlying model. This is the one gap the report escalates rather than solves (§12.1) |
| GAP-STD-04 Roadmap commitments unstructured | Makes forward-looking commitments comparable across suppliers and trackable across releases | Does not make them contractual, and cannot distinguish an intention from a plan |
| GAP-STD-05 No conformance path | The profile *is* the conformance definition — validation rules stated once, executable by either party | Does not build the validator, and does nothing for certification-scheme throughput (LYR-T-03) |
| GAP-STD-06 Fragmented PKI inventory models | A profile can require certificate and trust-anchor attributes consistently even where the underlying models differ | Does not unify the models, and inherits whatever the formats can carry |
| GAP-STD-07 Protocol profiling still landing | Can record *which* protocol profile a product implements, at which draft or RFC — making a moving target legible rather than resolved | Does not accelerate the IETF |

### Discovery and tooling

| Gap | What a profile does | What it does not do |
|---|---|---|
| GAP-TOOL-01 Scanners miss configuration | `lifecycleStage` separates *implemented* from *configured* and *observed*, so a scanner result is not silently read as deployed reality | Does not measure the running estate |
| GAP-TOOL-02 Opaque firmware and modules | Requires the supplier to declare what cannot be externally observed — moving the burden to the only party who knows | Does not make the module inspectable, and a declaration is not evidence |
| GAP-TOOL-03 Observed state unmeasurable at scale | Makes the declaration/observation distinction explicit and checkable, so the limits of an inventory are visible in the artefact | Does not make observation feasible |
| GAP-TOOL-04 False positives unusable as evidence | **Requires the operational role of each algorithm to be declared** — signature, key exchange, bulk encryption, integrity, or explicitly non-security use. A consumer can then separate a broken signature algorithm from the same primitive generating a cache key. Obligation levels and declared scope further bound what must be reported | Does not improve scanner *detection*; it supplies the context a scanner cannot infer, and depends on the producer declaring the role honestly |

### Commercial and contractual

| Gap | What a profile does | What it does not do |
|---|---|---|
| GAP-COM-01 No standard procurement language | Gives a contracting authority a citable object: a named profile at a stated version, referenced in a clause | Does not write the clause, nor oblige anyone to adopt it |
| GAP-COM-02 No obligation to supply | Makes an obligation cheap to state and cheap to verify, which is what makes one adoptable | Creates no obligation. This is chapter 11's work, not the profile's |
| GAP-COM-03 Disclosure resistance | Bounds what must be shared and caps scope creep — the supplier's protection as much as the buyer's floor | Does not remove the negotiation over where the bound sits |
| GAP-COM-04 Tier-2 opacity | Scope and completeness statements make the boundary explicit, so an incomplete answer is visibly incomplete rather than silently so | Does not create visibility that is not there |
| GAP-COM-05 Legacy products never get a CBOM | Nothing at the artefact level; at most, an operator-authored inventory entry recording the absence | Does not retrofit anything. Prospective only |

### Organisational, lifecycle, policy

| Gap | What a profile does | What it does not do |
|---|---|---|
| GAP-ORG-01 Cryptography outside asset management | A defined artefact with a defined consumer gives the data somewhere to live | Does not assign the function or fund it |
| GAP-ORG-02 No named owner for cryptographic inventory | Names roles — producer, consumer, validator — which is weak evidence of who should own it | Does not create the owner |
| GAP-ORG-03 Data sits away from the skills | Reduces the expertise needed to *ask*, which is the half that sits with procurement | Does not move the data or the people |
| GAP-LIFE-01 Decade-long service lives | Nothing | Nothing |
| GAP-LIFE-02 Hardware cannot move on a software cadence | Makes hardware-anchored cryptography visible at procurement, when the commitment is made | Does not change the cadence |
| GAP-LIFE-03 Backward compatibility sustains deprecated algorithms | Makes retirement reportable as a distinct state (§8.5), so deferral is visible rather than assumed | Does not remove the compatibility obligation |
| GAP-POL-01 Instruments name a format, not the content | Occupies exactly the unoccupied space: which attributes, at what obligation level, for which decision | Does not verify that any answer is true |
| GAP-POL-02 Member State divergence is the default | One artefact satisfying several profiles; divergence becomes a mapping problem rather than a duplication problem | Does not harmonise the underlying law |
| GAP-POL-03 Suppliers rationally wait | A published profile is a stable target, which is what waiting is waiting for | Does not settle the protocol layer they are actually waiting on (LYR-C-02) |

Read the third column as a whole and a pattern emerges. A profile is strong where the problem
is **incommensurability** — different parties answering different questions in different words.
It is weak or useless where the problem is **absence**: absent visibility, absent obligation,
absent budget, absent hardware. That distinction is the honest summary of this chapter, and it
predicts where the recommendations in chapter 12 have to come from something other than a
specification.

## 8.3  Compounding effects

Four effects that do not belong to any single gap.

**Procurement leverage.** Cryptographic posture is set at purchase and lived with for the
service life of the equipment. A profile makes the question askable at the one moment when the
buyer has leverage and the cost of a different answer is lowest. The market states this itself:
hardware bought in 2026 determines whether an organisation migrates through its existing
infrastructure or replaces it under time pressure (VL §3c).

**Quality gates across the lifecycle.** A conformance definition that executes is a gate, and
the same definition can sit at every point where cryptographic posture is decided: a commit or
build check that a new dependency introduces nothing outside policy; a release gate that the
artefact accompanying a build conforms; a deployment admission check that a candidate workload
meets the posture required for its environment; and a procurement evaluation gate before
anything is bought at all.

Two things follow. The producer is checking against the same definition the consumer will apply,
so failures surface where they are cheapest to fix rather than at the customer. And the profile
becomes part of the development lifecycle rather than a reporting obligation bolted onto the end
of it — which is the structural answer to the compliance-not-security failure in §6.1.

**Delta as evidence.** Successive conforming artefacts make migration progress a difference
between two machine-readable documents rather than a narrative assertion. This is what turns
progress reporting (§11.5) from a survey into a measurement.

**One artefact, several consumers.** The same CBOM serves procurement, supervision, incident
response and internal planning, each reading the subset its profile defines.

**Agility as a repeatable capability.** The three operations agility requires — inventory,
policy check, confirmation of effect — are the same operations a conforming artefact supports.
An organisation that can execute them for the post-quantum transition can execute them for the
next one, which is the difference between a migration programme and a capability.

## 8.4  Preconditions

None of the above is a property of the profile. Each requires something the profile cannot
provide:

- **Consumer-side tooling.** Without a validator in the hands of the party doing the asking,
  automation does not happen and the artefact is a PDF with better syntax. SBOM's central
  failure (LSN-07).
- **An obligation to supply.** Voluntary transparency selects for suppliers who already had
  little to hide.
- **A maintained profile.** An unversioned or abandoned profile is worse than none: it is cited
  in contracts and then drifts from what it was meant to capture.

State these as preconditions in the report, not as caveats. They are what chapter 11 is for.

## 8.5  Making completion reportable

If a migration profile can express *classical retired* as a state distinct from *PQC enabled*,
LYR-C-06 becomes reportable and the midpoint-victory problem acquires a mechanism rather than a
warning.

**Resolved (DR-09).** The migration profile carries a classical-retirement state per
cryptographic relationship — *classical present / classical disabled / classical removed* —
orthogonal to `lifecycleStage`. It is an attribute of this profile; the general v1 attribute
model is not reopened. Shown in the worked example (chapter 10) and Annex A.

The case for it is not theoretical. The current deployed position of most of the public web is
a connection whose key establishment is post-quantum and whose certificate authentication is
not (VL §3b). A profile that cannot express the difference cannot describe 2026.

## 8.6  What a profile does not touch

Load-bearing, and the credibility of §8.1 depends on it being unflinching.

**Gaps.** `GAP-LIFE-01` and the `GAP-ORG-*` set are not specification problems. Service lives,
capital cycles, and whether an organisation has anyone accountable for cryptography are
addressed by budgets, mandates and time. Say so, and say what would address them.

**Constraints.** Of the seven cross-cutting constraints in chapter 3:

| Constraint | Effect | Via |
|---|---|---|
| LYR-X-02 Expertise and capacity | **Multiplier** — expertise spent once, executed repeatedly by tooling. A buyer without in-house cryptographers still asks a competent question. The clearest case for EU-level action: the Commission can amortise scarce expertise across a market | automation |
| LYR-X-07 Regulatory divergence | **Reduces** — one artefact machine-validated against several profiles, not re-answered per jurisdiction | automation |
| LYR-X-06 Incentive uncertainty | **Partial** — structured data makes an obligation cheap to verify, and so enforceable rather than declaratory | standardisation |
| LYR-X-05 Operational risk | **Partial** — posture verifiable at a pre-deployment gate rather than discovered in production; does not create the change window | automation |
| LYR-X-04 Algorithm confidence | **Partial** — does not resolve the doubt, but agility lowers the cost of being wrong, which is the practical form the constraint takes. Automation is what makes agility operational at scale | standardisation + automation |
| LYR-X-01 Legacy and budget | **Partial**, prospective only — visibility at procurement, before the debt is incurred; and inventory maintenance across a large estate becomes affordable | automation |
| LYR-X-03 Performance | **None** — no artefact shrinks a signature | — |

Two counter-arguments to state rather than bury. The people who would write the profiles are
drawn from the same scarce population as everyone else at LYR-X-02: the multiplier holds
because the work is done **once** and reused, not because it is free. And six of seven
constraints now read as partial or better, which is a stronger claim than an earlier draft
made. It rests entirely on the automation step happening, which is a precondition (§8.4) and
not a property of the profile.

---

*Register: `../register.md` §B and §D.*


---

# 9  The methodology applied

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text

The profile in chapter 10 was not assembled by intuition. It follows a published methodology for
defining CBOM profiles — a vendor-neutral, format-independent method that any sector or
authority can apply, developed by the PKI Consortium's CBOM Profiles Working Group and cited
here as the motivating precedent for the profile-first approach.

This chapter walks its thirteen aspects and records what each demanded of a supply-chain PQC
migration profile. It serves two purposes for a policy reader: it shows the worked example is
reproducible rather than bespoke, and it shows what an EU baseline profile would require
somebody to decide.

Aspects are numbered as the methodology numbers them (aspect 3.1 to aspect 3.13). Those numbers
are unrelated to this report's own sections.

## 9.1  Purpose of the profile

**Aspect 3.1 — Objective and scope.** The methodology requires a profile to name the decision it
serves before any attribute is chosen. Here: *can this product be deployed in a post-quantum
migration programme, and what will it take* (§10.1). This is the discipline that answers the
central SBOM failure — artefacts produced against an obligation rather than a decision end up
unread (§6.1).

This aspect is also, at the time of writing, under active consultation within the working
group — practitioners are being asked which decisions a CBOM actually needs to support, and
where inventory exercises have failed, before options are drafted. That sequencing is
deliberate and worth noting: the aspect that determines what every profile is *for* is being
grounded in practice rather than authored from first principles.

Scope also fixes the boundary of the supply chain the artefact speaks for. The profile requires
a scope statement per artefact precisely because a supplier cannot answer for tiers they do not
contract with (§10.5, R2).

**Aspect 3.2 — Identity and metadata.** Ordinarily a housekeeping aspect; here it is load-bearing,
because procurement clauses cite profiles by name and version (§11.4). That imposes requirements
internal use does not: stable naming, a resolvable reference, and a stated position on how long
a conformance claim against a superseded version remains valid.

**Aspect 3.11 — Governance and lifecycle.** Who maintains the profile and what happens to
existing claims when it changes. For a sector profile this is an internal question; for an EU
baseline it is §11.7, and the report leaves the choice open by design.

## 9.2  What the profile says

**Aspect 3.3 — Attribute model.** The most consequential aspect, and where this profile departs
from the obvious approach. The methodology's model describes cryptographic assets; this profile
organises around **cryptographic relationships** and the **endpoints** participating in them
(§10.3), because in a supply chain the cryptography that determines security is applied between
components rather than held by one.

Two attributes sit on the model and both were decisions rather than defaults. `lifecycleStage`
separates *intended / implemented / configured / observed*, so a supplier's declaration is not
silently read as deployed reality. The classical-retirement state is orthogonal to it, and is
what makes completion reportable (DR-09).

The methodology does not currently provide a first-class expression for relationships; this
profile works within what the formats offer and records the loss. That record is the evidence
behind RDY-09.

**Aspect 3.4 — Obligation levels.** BCP 14 keywords, and the aspect where the supplier's
interest and the buyer's coincide more than is usually acknowledged. Obligation levels set a
floor that prevents underreporting *and* a ceiling that bounds disclosure. Bounded disclosure is
a purpose here, not a side effect (§10.7).

**Aspect 3.7 — Vocabularies and normalisation.** Where a registry term exists, the profile
requires it. Where it does not — and sector-specific primitives are unevenly covered
(GAP-STD-02) — the profile requires a provisional term plus an upstream contribution, rather
than permitting free text. The methodology should say which of those an author must do; it is
routed as P-11.

**Aspect 3.10 — Forward-looking information.** Roadmap commitments are carried, marked as
forward-looking, and never merged with current state. A current-state query must not return
them (Annex A, rule C5). This is the aspect that makes vendor commitments comparable and
trackable rather than prose in a tender response.

## 9.3  How it is carried and checked

**Aspect 3.5 — Conformance and validation.** The profile is the conformance definition, and it
executes: structural checks are mechanical, policy checks belong to the consumer, and the
outcome set is pass / fail / **out of scope** (§10.6). That third outcome is a methodology
finding as much as a profile one — treating unknown as pass is how a transparency regime becomes
theatre.

The unresolved question is whether the consumer policy check belongs inside the profile at all
or whether the profile should only define what such a check can address. Left open in Annex A.

**Aspect 3.6 — Mapping to serialisation formats.** The profile is defined without naming a field
in any format; the binding is Annex B. This is what allows the Union to specify content without
selecting a format winner (§11.1) — a political advantage of format-independence that the
methodology's own rationale does not currently claim (pkic-feedback §C).

Where a format cannot carry an attribute, the methodology's instruction is to document the gap
and raise it upstream. What a conforming producer does *in the meantime* is unspecified, and is
routed as P-12.

**Aspect 3.8 — Relationship to SBOM, HBOM and exploitability assertions.** Cryptographic
inventory is not free-standing: an algorithm is implemented by a component, which runs in an
environment. The profile links endpoints to components (Annex A, E3) and records execution
environment (E4), which is what makes the hardware-anchoring attribute derivable. Practically,
the SBOM obligations already in the CRA are the delivery channel through which cryptographic
content would travel.

The aspect also has to settle a question the methodology currently passes over: **where
exploitability lives.** The software domain answered it by splitting — an inventory says a
vulnerable component is present, and a separate exploitability statement says whether it is
actually exploitable in this product. That split was not tidiness. It was the response to
inventory alone producing more findings than any defender could act on (LSN-10).

The cryptographic case has the same shape and a sharper version of the problem. That a product
implements a weakened algorithm says nothing about whether it is reachable, whether it can be
negotiated down to, whether the affected mode is enabled, or whether the data it protects
matters. A profile that tried to answer those inside the inventory would be answering them on
behalf of a party — the operator — who holds the relevant facts and whom the supplier cannot
speak for.

**This report's position is that exploitability sits alongside** (DR-11): a separate assertion
artefact referencing a CBOM, carrying its own author, date and scope.

The operational argument is the most direct. A CBOM is signed at build by the release pipeline.
Embedding a vulnerability list means re-authoring and re-signing that artefact every time an
assessment changes — destroying the release-time provenance that made it worth signing. Three
further reasons. Inventory changes when the product changes, while exploitability changes when
cryptanalysis, configuration or deployment context changes — often with no new release. The
author frequently differs, and may be an operator, a CERT or a supervisory body rather than the
supplier. And an assertion may be superseded or contested while the inventory it references
remains correct.

The boundary against `lifecycleStage` needs stating, because the two will otherwise drift
together. `lifecycleStage` records the basis of an assertion *about the inventory* — intended,
implemented, configured, observed. An exploitability assertion is a judgement about
*consequence*, given that inventory. The first is a property of the record; the second is an
opinion about the world, and opinions require an author and a date. What remains open, and is
routed as P-18, is whether an existing VEX-shaped artefact can carry cryptographic
exploitability or whether a distinct one is needed.

**Aspect 3.9 — Extensibility and composition.** A single artefact satisfying several profiles is
the direct answer to duplicated supplier effort (§10.9), and baseline-plus-sector is the shape
policy adoption needs (§11.6).

Composition also runs in a second direction the methodology treats less explicitly: artefacts
composing with each other. A derived CBOM references an upstream one rather than replacing it
(DR-12), which makes the pair jointly checkable in ways neither is alone (§10.7.2). The
methodology should say whether artefact-to-artefact derivation is in scope for this aspect or
belongs with layering under aspect 3.8. The open methodology question — whether an extending profile may
narrow obligations or only add them — is routed as P-08.

## 9.4  Policy fit

**Aspect 3.12 — Regulatory and policy alignment.** The mapping is bidirectional and that is the
point. Instruments recommend cryptographic inventory without specifying content (§5); a profile
supplies the content; and a single artefact can then satisfy several instruments, which is what
makes divergence a mapping problem rather than a duplication problem.

**Aspect 3.13 — Templates and worked examples.** Chapter 10 and Annex A are this aspect
discharged. The methodology's own position — that a profile is not usable until somebody has
worked an example through it — was borne out here: three of the decisions recorded above only
became visible when the example was written.

## 9.5  What the application returned to the methodology

Applying a methodology tests it. Twenty findings from this work are routed back to the working
group's tracking aspects in a separate file, ranging from the modelling gap at aspect 3.3 to a
suggestion that the methodology's rationale rest on cryptographic agility rather than
transparency, since agility survives the end of the post-quantum transition and transparency is
only the means to it.

That two-way traffic is worth stating in a report addressed to policymakers. A methodology that
no one has applied is a proposal; one that has been applied, and amended in consequence, is
infrastructure.


---

# 10  Worked example: a supply-chain PQC migration profile

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text
**Scope fixed by DR-02:** migration profile only, with a closing note on composition.

Everything before this chapter is argument. This chapter is the thing itself: what a supplier
would actually be asked to produce, and what a buyer would actually be able to check. A reader
who takes nothing else from the report should be able to describe the artefact after reading it.

The example is written **format-independently**, as the methodology requires. Nothing here
names a field in CycloneDX or SPDX; that binding is Annex B, and keeping it separate is the
point — the same content survives a change of serialisation.

## 10.1  The decision the profile serves

> *Can this product be deployed in a post-quantum migration programme, and what will it take?*

Asked by a buyer — an operator, integrator or contracting authority — of a supplier, at
procurement and again at each release. Everything in the profile earns its place by bearing on
that question. Attributes that would be interesting but do not change the answer are excluded,
which is what makes the profile a profile rather than an inventory.

**Consumers.** Procurement evaluation; migration planning; supervisory reporting under §11.3
and §11.5. **Producer.** The supplier of the product, drawing on their own suppliers' artefacts
where the dependency is cryptographic.

## 10.2  Profile identity

Because procurement clauses cite profiles (§11.4), identity has to survive contractual
reference:

| | |
|---|---|
| Name | Supply-chain PQC migration profile |
| Version | Semantic; a conformance claim names the exact version |
| **Orientation** | `migration` — present state plus forward-looking capability and roadmap facts, the latter under distinct attribute names |
| **Subject scope** | `product` — the supplier's own product, from build-time evidence |
| Custodian | *tbd* — see §11.7 |
| Status of superseded versions | Must be defined: how long a claim against version *n−1* remains valid |
| Scope statement | Mandatory, per artefact — see §10.4 |

### 10.2.1  Why the two declarations matter here

Orientation is `migration`, and that classification changes nothing about how a shared attribute
is read. An algorithm attribute means *in use* in this profile exactly as it does in an
inventory profile; the forward-looking material is carried under separate names (R10). The rule
is what makes the artefact aggregable: an operator collecting from forty suppliers, some using
inventory profiles and some migration profiles, must be able to query deployed state without
branching on each producer's intent.

Subject scope is `product`, and it bounds what the supplier can honestly assert:

| Subject scope | Typical producer | Evidence basis | Change cadence | Disclosure limit |
|---|---|---|---|---|
| Component | Vendor or upstream supplier | Build-time; source and dependency analysis | Per component release | Narrow; may be commercially sensitive in isolation |
| **Product** | **Vendor** | **Build-time and test: what it implements and can support** | **Per product release** | **Bounded by IP; producer controls the whole subject** |
| Deployed service | Operator or integrator | Runtime and configuration, over a boundary the producer controls | Per configuration change, failover or certificate renewal | May lack authority to disclose third-party internals inside the boundary |
| Bounded estate | Operator | Aggregated; mixed freshness and provenance | Continuous; never uniformly current | Aggregate exposure; the boundary definition is itself sensitive |

The cadence column explains why these cannot be one artefact: the rows change on different
clocks, and binding them forces re-issue on the fastest.

A consumer that does not know the subject scope cannot weigh what it is reading — and two
CBOMs that appear to disagree may not conflict at all, if one describes what a product can do
and the other what a deployment actually does. This is also why §11.5 progress reporting needs
the declaration: aggregating product-scope and estate-scope artefacts without distinguishing
them produces a number that means nothing.

## 10.3  The unit of description

The profile describes **cryptographic relationships** — the loci where cryptography is applied
between two parties — and the **endpoints** that participate in them. This is deliberate and it
is the report's structural claim made operational (§2.1, GAP-STD-03).

A product's answer to "are you post-quantum ready" is not a property of the product. It is a set
of statements about each interface the product exposes or consumes, each of which has another
party at the far end. A profile organised around assets alone cannot express that; one organised
around relationships can, at the cost of requiring the supplier to enumerate their interfaces.

Since no current format carries relationships as first-class objects, the profile expresses them
within what the formats do offer, and records the loss. That record is the evidence behind
RDY-09 (§12.2).

## 10.4  Attributes

The full table is Annex A. The shape, and the four attributes that carry the argument:

**Per artefact**

| Attribute | Obligation | Notes |
|---|---|---|
| Profile name and version claimed | MUST | |
| Product and version identified | MUST | |
| **Scope statement** | MUST | What was examined, what was not, and how far down the supply chain the answer extends. An incomplete answer must be visibly incomplete (LSN-03) |
| Completeness basis | SHOULD | How the artefact was produced: build-time generation, scan, supplier declaration, manual |

**Per cryptographic relationship**

| Attribute | Obligation | Notes |
|---|---|---|
| Relationship identifier and the two endpoints | MUST | |
| Purpose | MUST | Key establishment, authentication, integrity, confidentiality at rest |
| Algorithms and parameters | MUST | Normalised vocabulary where one exists; provisional term plus upstream contribution where not (RDY-03) |
| **`lifecycleStage`** | MUST | *intended / implemented / configured / observed*. A supplier ordinarily declares *implemented*; an operator may record *observed* against the same relationship |
| **Classical retirement state** | MUST | *classical present / classical disabled / classical removed*. Orthogonal to `lifecycleStage` (DR-09) — this is what makes completion reportable |
| Negotiation and fallback behaviour | SHOULD | What happens when the far endpoint is at a different point in its migration |
| Hardware anchoring | MUST where applicable | Whether the cryptography is fixed in hardware, and therefore whether migration is an update or a refresh |
| **Roadmap commitment** | MAY | Forward-looking, and marked as such. Never merged with current state (RDY-07) |

Four attributes do the work: the scope statement makes incompleteness visible; `lifecycleStage`
separates capability from configuration; the retirement state makes completion reportable; and
hardware anchoring is the single field that most changes a migration plan's cost.

## 10.5  Worked relationships

### R1 — one connection, three relationships

A TLS interface the product exposes to a client, with mutual authentication. The first thing to
notice is that it is not one relationship but **three**: the connection itself, and two
trust-anchor relationships — each party's reliance on the authority that vouches for the other.
None of the three is a cryptographic asset, and a model built only on assets cannot hold any of
them.

That decomposition is what makes the next observation expressible. Key establishment on the
connection uses a hybrid mechanism combining a classical and a post-quantum component;
authentication on both trust-anchor relationships is classical, because no post-quantum root is
available in the relevant trust stores (VL §3b).

| | |
|---|---|
| Purpose | key establishment · authentication |
| Key establishment | hybrid, PQ component present, `lifecycleStage: implemented` |
| Authentication | classical, `lifecycleStage: implemented` |
| Classical retirement | **classical present** — on both, for different reasons |
| Fallback | negotiates to classical-only key establishment if the peer does not offer the hybrid group |

The two trust-anchor relationships carry their own rows, and both sit at *classical present*
for a reason external to the supplier: it is LYR-T-01, and no supplier action resolves it.

This is why the profile exists. A product-level flag would record the whole thing as "PQC
supported" — true, and misleading. The buyer needs to see that key establishment is protected
against harvest-now-decrypt-later while authentication is not, and that the second is not the
supplier's to fix.

It is also the clearest available demonstration of GAP-STD-03. Three relationships, two of them
trust-anchor relationships that belong to neither party's inventory, and the security of the
whole determined by their combination.

### R2 — a relationship spanning two suppliers

An interface between this product and a component supplied by a third party, where the buyer
contracts only with the first supplier.

The supplier can state what their side supports, the configuration they ship, and which
component they integrate. They cannot state the far side's posture, because they do not own it.
The profile requires them to say so — the scope statement records the boundary — rather than
leaving a silence the buyer may read as an assurance.

This is GAP-COM-04 handled honestly: the profile does not create tier-2 visibility, but it makes
the absence of visibility explicit and locatable.

### R3 — a hardware-anchored relationship

Signing performed in a hardware module. Algorithms are classical; the module has no post-quantum
firmware path available, so migration requires replacement rather than update (VL §3c).

The hardware-anchoring attribute changes the buyer's plan from a software upgrade line item to a
capital refresh with a procurement lead time — which is exactly the visibility that would have
prevented the debt had it been available at the original purchase (§8.3).

## 10.6  A conformance check

Conformance is a machine operation over the artefact (§8.1). Two checks, deliberately different
in kind:

**Structural.** Every mandatory attribute present; vocabularies drawn from the registry;
`lifecycleStage` and retirement state populated for every relationship. Pass or fail, no
judgement.

**Policy.** Evaluated by the *consumer* against their own requirement — for example: every
relationship whose purpose is key establishment must have a post-quantum component at
`lifecycleStage: configured` or better.

Against R1–R3 that policy check fails: R1 passes on key establishment, R3 fails on both, and R2
returns *out of scope* rather than pass or fail — a third outcome the check must support, since
treating unknown as pass is how transparency regimes become theatre.

**And the distinction that matters:** the artefact can report *PQC enabled* on R1's key
establishment while its classical retirement state remains *classical present*. Migration
complete is a different query from PQC enabled, and only a profile carrying both can answer it
(§8.5, LYR-C-06).

## 10.7  The derived artefact: after the operator installs it

Everything above describes what the supplier produces. The buyer then installs the product,
configures it, and connects it to their own PKI and key storage — and at that point a second
artefact exists. Getting its relationship to the first right matters more than it first appears.

**It references the supplier's artefact; it does not replace it** (DR-12). The operator's CBOM
carries a `derivedFrom` pointer — identity, digest, and the profile the upstream artefact
claimed — and declares its own subject scope (`deployed service`), author and date. Rewriting
the supplier's artefact would break the signature applied at release and destroy the chain back
to the build. It would also merge two sets of claims, from different evidence and different
authors, into a document where neither can be attributed.

The clocks differ too. The supplier's artefact changes at release; the operator's changes at
every configuration change, failover, certificate renewal and trust-store update. Binding them
into one document means re-issuing on the faster clock.

**Four kinds of statement, all of which must be expressible:**

| Kind | Example | Why it is explicit |
|---|---|---|
| Confirmed | Supplier implements hybrid key exchange; the operator has enabled it | The ordinary case |
| **Suppressed** | Supplier implements a legacy suite; the operator has disabled it | Absence is ambiguous — omitting it is indistinguishable from not having looked. A disabled capability is a positive fact |
| **Additive** | The operator's own trust anchors, issued certificates, HSM binding, an external TLS terminator | The supplier never described these, and they are frequently where the operator's real exposure sits |
| Divergent | Observation contradicts the supplier's declaration | A finding, not an error. Recorded as a conflict rather than silently overwritten |

The additive category is the one most easily missed. Installing a product does not merely
*narrow* the supplier's cryptography — the operator supplies their own: which authority issues
its certificates, which roots it trusts, where its private keys live, what terminates its
transport security. In the model used here those are new relationships and endpoints, not
annotations on existing ones. A derived artefact that only narrows the supplier's list loses
the operator's entire trust configuration.

This is also why the two artefacts are not the same shape. The supplier describes endpoints and
what they can do. The operator largely describes **relationships** — what was negotiated, with
whom, under which trust anchors — because that is what configuration determines.

### 10.7.1  Why this needs no second profile

A consumer must be able to tell at a glance whether an artefact states capability or deployed
posture. That is already achieved by the **declared subject scope** (§10.2.1), which sits in the
header before any attribute is read.

What varies between the two is not the attribute model but what each subject can honestly
assert, so **obligation levels are conditional on declared scope**:

| Attribute | `product` | `deployed service` |
|---|---|---|
| Implemented capability | MUST | SHOULD — inherited by reference |
| Configured state | — not knowable | MUST |
| Observed state | — | SHOULD where measurable |
| Suppression records | — | MUST |
| Operator-supplied trust anchors and key storage | — | MUST |
| Roadmap commitment | MAY | — not the operator's to state |
| `derivedFrom` | — | MUST |

One profile, one vocabulary, one attribute model. Forking into separate capability and runtime
profiles would duplicate most of the attribute set and then drift from it, and it would turn the
queries in §10.6 and §11.5 into joins across two schemas.

### 10.7.2  What the pair makes checkable

Having two linked artefacts enables a class of check neither supports alone:

- Every relationship in the derived artefact resolves to one upstream, or is flagged additive.
- No algorithm reported as *configured* that the upstream artefact does not list as
  *implemented*.
- Suppression records reference a capability that still exists upstream — which catches
  suppressions that have drifted after a product upgrade.
- The `derivedFrom` digest matches the artefact actually held, catching derivation from a
  superseded release.

The second is the interesting one, because a mismatch is often not an error. It usually means a
reverse proxy, sidecar or platform component is performing cryptography nobody attributed —
precisely the kind of supply-chain finding the report describes as currently invisible
(GAP-COM-04).

### 10.7.3  One limit

A supplier can *declare* what the configured state will be — a documented default or a
recommended hardening profile. An operator can *derive* it from the running system. Both are
`lifecycleStage: configured`, and they are not worth the same. The stage and the basis of the
assertion are orthogonal, and the flat v1 tag does not carry the second.

The interim used here is that a derived artefact states its evidence basis once, at artefact
level (A7). That is sufficient where a whole artefact was produced the same way, and it avoids
reopening the attribute model. The general problem is routed to the methodology (DR-12).

## 10.8  What the artefact does not contain

Stated in the report, because a supplier reading it needs to know the bound and a regulator needs
to know the limit:

- **No key material, and no configuration secrets.** Ever.
- **No implementation detail beyond what the decision requires** — bounded disclosure is a
  purpose of the obligation levels, not an oversight (GAP-COM-03).
- **No assertion about parties beyond the scope statement.**
- **No verification that the declarations are true.** The profile makes a claim checkable for
  internal consistency and against policy; it does not attest it (§8.2).
- **No exploitability judgement.** That a weakened algorithm is present says nothing about
  whether it is reachable, negotiable, or protecting anything that matters. That assessment
  depends on facts the operator holds and the supplier cannot speak for, and it belongs in a
  separate assertion artefact referencing this one (DR-11, §9.3). The artefact does carry a
  typed locator to where such assertions are published, so a consumer's tooling can follow it
  rather than having to discover it.

## 10.9  How a procurement profile would compose

Briefly, per DR-02. A procurement profile serving a different decision — *should we buy this* —
would share most of the attribute set and diverge in two ways: it would raise the roadmap
commitment from MAY to MUST, since forward commitments are what is being negotiated, and it
would relax the observed `lifecycleStage`, which does not exist before deployment.

One artefact could satisfy both simultaneously. That is the multi-profile property (§4), and it
is the direct answer to duplicated supplier effort across jurisdictions and use cases.


---

# 11  How the EU could use CBOM profiles

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text

Six options, ordered from lightest to heaviest instrument, because that ordering is the actual
decision in front of the Commission. Each is tagged with the stage or track it targets, since
§3.5 establishes that an obligation landing on a stage whose inputs have not settled produces
declarations rather than migration.

Two framing points before the options.

**Nothing here requires new legislation.** Every option sits inside an instrument that exists,
or in procurement practice that needs none. The report's claim is that the gap is a missing
*specification*, not a missing law.

**The mechanism already has a European precedent.** BSI's TR-03183 defines required SBOM content
and binds it to a format through a published property taxonomy, naming accepted format versions
(VL §3c). Everything below applies that same mechanism to cryptography, at Union rather than
national level. This is worth leading with: it answers the "is this realistic" objection before
it is raised, and the existence proof is European.

## 11.1  A reference EU baseline profile

*Targets LYR-C-04 · closes GAP-POL-01, GAP-POL-02 · RDY-01*

A named, versioned, publicly available profile stating the minimum cryptographic transparency
expected of products with digital elements — defined once at Union level rather than arrived at
separately by each supervisory authority.

The gap it fills is narrow and specific. The coordinated roadmap already recommends a
standardised format and names CBOM (VL C-01). What no instrument states is **which attributes,
at what obligation level, for which decision**. Without that, "use a standardised format" leaves
each Member State to determine what a conforming artefact contains, and divergence is the
default outcome rather than a risk (GAP-POL-02).

There is also evidence that Member States will coordinate here if given something to coordinate
on: Germany, France and the Netherlands have issued a joint position on post-quantum migration,
and BSI's national framing of cryptographic procedures under NIS2 follows an
*inventory → assess → implement* sequence in which the first step is precisely what a profile
would specify. A baseline gives that existing coordination a common object.

A baseline profile is also the answer to the capacity constraint that runs through this report.
Defining it consumes scarce cryptographic expertise once; every subsequent use is a machine
operation (§8.1). No other actor in the European market is positioned to amortise that cost
across all of it.

## 11.2  CRA technical documentation

*Targets LYR-C-04 · RDY-06*

Profile conformance as an accepted means of evidencing the cryptographic aspects of technical
documentation for products with digital elements.

The timing argument matters here more than anywhere. The CRA applies fully from December 2027;
its harmonised standards are being drafted under mandate M/606; as of August 2026 none had been
cited in the Official Journal, so the presumption of conformity was not yet available for any
product category, and the drafting deadlines had already slipped by two months (VL §3).

Read that two ways, and the report should say both. It is a caution — the machinery supporting
an instrument at LYR-C-04 is itself still in motion, which is the pattern §3.5 describes. And it
is an opportunity: cryptographic content is being specified *now*, and a profile-shaped
contribution is more useful before the standards land than after.

> **Verify (pass 5):** whether any harmonised standard has since been cited, and whether
> cryptographic transparency appears in the horizontal series.

## 11.3  NIS2 supervision

*Targets LYR-C-04, LYR-C-05 · RDY-04*

Profile-conformant artefacts as structured evidence of the cryptographic inventory that the
technical implementation guidance already recommends.

This route is materially less speculative than it was. A proposed amendment published in
February 2026 would require Member States to adopt PQC transition policies aligned to the
roadmap milestones, naming PQC in the directive's own text rather than leaving it to
interpretation (VL C-02). If adopted, national strategies acquire a named obligation, and the
question of what evidences progress follows immediately.

The supervisory case rests on automation. Machine-checkable conformance is what makes
supervision affordable at market scale — for the supervised entity and the supervisor alike. An
obligation assessable only by expert reading is bounded by the scarcest resource in the chain
(LYR-X-02) and will be applied thinly, or not at all.

One caution from chapter 6, which should temper any enthusiasm here: an artefact produced for
supervision and then not read is the *default* outcome, not the failure case. Supervisory demand
without consumer-side tooling reproduces the SBOM result exactly.

> **Verify (pass 5):** adoption status of the proposed amendment. A proposal is not law.

## 11.4  Public procurement

*Targets LYR-C-04 · closes GAP-COM-01, GAP-COM-02 · RDY-06*

Model clauses citing a named profile at a stated version, with a defined exchange channel and
delivery points across the product lifecycle.

The fastest lever available, and the only one requiring no instrument at all. It is also the
point of maximum leverage: cryptographic posture is set at purchase and lived with for the
service life of the equipment. Hardware bought today determines whether an organisation migrates
through its existing infrastructure or replaces it under time pressure (VL §3c) — and that
determination is made by a contracting authority that frequently has no cryptographer.

That is the capacity argument at its clearest. A published profile lets an authority without
in-house expertise state a defensible requirement and evaluate the response with tooling. The
expertise is spent once, centrally; it is executed thousands of times, locally.

## 11.5  PQC roadmap progress reporting

*Targets LYR-C-05, LYR-C-06 · RDY-07*

Member State reporting against the roadmap milestones built on comparable structured data rather
than narrative returns.

The mechanism is delta-as-evidence (§8.3): successive conforming artefacts make progress the
difference between two machine-readable documents. This turns reporting from a survey into a
measurement.

It also depends on something only this profile provides. Progress toward 2030 and 2035 is not
measured by post-quantum capability being present — it is measured by classical cryptography
being gone. A reporting scheme that cannot distinguish *PQC enabled* from *migration complete*
will record the midpoint as the end (§8.5, LYR-C-06).

## 11.6  Sector profiles composing on the baseline

*Targets LYR-C-04 · RDY-02*

Two axes of specialisation sit above a baseline, and conflating them causes trouble.

**By decision type.** Profiles group according to what the consumer is deciding, which yields
four families: procurement and vendor evaluation; vulnerability response; PQC migration; and
compliance and audit. This follows from the use-case-led position — profiles serving the same
class of decision share most of their attribute set and should be authored together rather than
discovered to overlap afterwards.

**By sector.** Telecommunications, finance, energy and health each have cryptographic specifics
the baseline should not carry. Composition lets a sector extend the baseline rather than fork
it, so a supplier serving several sectors produces one artefact rather than several.

The two compose: a telecommunications procurement profile is the procurement family extended
with sector specifics, not a separate thing. What must be settled centrally before any of this
splits is the shared attribute vocabulary, the use-case template, and the orientation and
subject-scope rules — otherwise four families produce four vocabularies and the multi-profile
property is lost.

Sector work is already under way — telecommunications most visibly — which makes this urgent
rather than theoretical. Sector profiles defined before a baseline exists will diverge, and
reconciling them afterwards is considerably harder than composing onto a baseline from the
start. The methodology question of whether extension may narrow obligations or only add them is
routed to the working group (P-08).

## 11.7  Custodianship

*RDY-08*

Who maintains the baseline, at what cadence, and what happens to a conformance claim when it
changes.

**This report does not recommend an option** (DR-01). Custodianship is a question of EU
institutional design, and the choice is the Commission's. The omission is deliberate and stated
so that it does not read as evasion.

| Option | Strengths | Weaknesses |
|---|---|---|
| ENISA | Institutional weight; NIS2 and CRA proximity; already the author of the adjacent SBOM evidence base | Capacity; change cadence slower than the specification churn |
| CEN-CENELEC workstream | Direct route to a harmonised standard and the presumption of conformity | Timeline; governance overhead; already carrying M/606 |
| Reference an external methodology, instantiate for the EU | Speed; avoids duplicating methodology work already under way | Dependence on external governance; less institutional weight |

Whichever is chosen, the requirement is the same: a defined change process and a versioning
policy. An unversioned or abandoned profile is worse than none — it gets cited in contracts and
then drifts from what it was meant to capture (§8.4).

## 11.8  Phasing against the chain

Phasing should follow the migration chain, not the legislative calendar.

**Sequence.** Voluntary reference → procurement clause → supervisory evidence. Each step
requires the previous one to have produced something readable, and each requires a custodian.

**Two cautions on pace**, both from chapter 3 and both sourced.

Protocol profiling is still in motion for several families (LYR-C-02, VL §3b). A requirement
that fixes on a particular configuration before the layer beneath it settles will need
withdrawing, and withdrawal is expensive in credibility. This is also, precisely, why suppliers
wait (GAP-POL-03): an early commitment may prove to be the wrong shape.

Certification throughput is finite and structural, not a passing backlog (LYR-T-03, VL §2). An
instrument that accelerates demand at LYR-C-04 without regard to validation capacity produces a
queue rather than a migration.

Neither is an argument for delay. Both are arguments for sequencing obligations against the
stage they depend on — which is what the layer tags on each option above are for.


---

# 12  Recommendations

**Owner:** _tbd_ · **Status:** first draft — prose, not agreed text
**Must address every `RDY-*`** — `bash check-coverage.sh` enforces it.

Nine recommendations, one per readiness criterion in §7.7. Each names an addressee, the stage
or track it targets, and what must be true before it can be acted on. Three constraints from
earlier chapters shape the set and should be visible in it:

- **Aim at where a gap must be fixed, not where it hurts** (§7.8). Two gaps originate far from
  the point of pain, and a recommendation aimed at the symptom will miss both.
- **Do not accelerate demand at a stage whose inputs have not settled** (§3.5, §11.8). An
  obligation landing on LYR-C-04 while LYR-C-02 is still moving produces declarations, not
  migration.
- **An unread artefact is the default outcome** (§6.1). Every recommendation that creates supply
  must be paired with one that creates the means to consume.

## 12.1  The recommendations

| RDY | Recommendation | Addressee | Targets | Precondition |
|---|---|---|---|---|
| RDY-01 | Establish a **reference EU baseline CBOM profile** — named, versioned, publicly available — defining the minimum cryptographic transparency expected of products with digital elements, following the mechanism BSI already uses for SBOM (§11.1). Above it, four profile families grouped by consumer decision: procurement and vendor evaluation, vulnerability response, PQC migration, and compliance and audit. **Build procurement first, as a pathfinder** | Commission, with ENISA | LYR-C-04 | A custodian (RDY-08); shared vocabulary settled centrally |
| RDY-02 | Require the baseline to be **defined independently of serialisation** and mapped to both major formats, with unmappable attributes documented and raised with the specification bodies | Commission; profile custodian | LYR-C-04, LYR-C-05 | None — actionable now |
| RDY-03 | Support **normalised vocabularies covering the algorithms actually deployed in Europe**, including sector-specific and national primitives absent from current registries, through contribution rather than a parallel European registry | Member States, sector bodies, suppliers | LYR-C-01, LYR-C-04 | Identification of the missing set |
| RDY-04 | Require any profile used as regulatory evidence to **distinguish declared from observed state**, so the limits of an inventory are visible in the artefact rather than assumed | Commission; supervisory authorities | LYR-C-04, LYR-C-05 | RDY-01 |
| RDY-05 | Treat **consumer-side validation tooling as part of the deliverable**, not a market by-product. Build on existing open tooling rather than commissioning greenfield: CBOM generators and viewers are already published under open licences, including through the Linux Foundation's post-quantum alliance. The missing piece is a *profile-aware validator*, not a generator | Commission, ENISA | LYR-C-04 | RDY-01, RDY-02 |
| RDY-06 | Publish **model procurement clauses** citing a named profile at a stated version, and a defined exchange channel. The fastest available lever: no new legislation required | Commission; Member State contracting authorities | LYR-C-04 | RDY-01 |
| RDY-07 | Require **forward-looking cryptographic commitments to be expressed comparably**, distinct from current-state inventory, so a roadmap can be compared across suppliers and tracked across releases | Commission; profile custodian | LYR-C-04, LYR-C-06 | RDY-01 |
| RDY-08 | **Identify a custodian** with a defined change process and versioning policy. Options and trade-offs are at §11.7; the choice is the Commission's and this report does not make it (DR-01) | Commission | all | None — actionable now |
| RDY-09 | **Raise the absence of a standard expression for cryptography applied between two parties** with the relevant specification bodies, as a named modelling gap, using the supply-chain case as the motivating example (§12.2) | Commission, ENISA, Member States, PKIC and other methodology bodies | LYR-C-02 *(gap bites at C-05)* | None — actionable now |

Four are actionable immediately; the remainder depend on RDY-01 or RDY-08, which is the
sequencing argument in miniature.

## 12.2  The one gap that must be escalated, not solved

GAP-STD-03 is the only item in this report that no profile can address. Current models describe
cryptographic assets as properties of components; the cryptography that determines security in a
multi-party supply chain is applied between components and belongs to neither inventory.

The evidence is not hypothetical. A connection carrying post-quantum key establishment and
classical certificate authentication is the ordinary state of the public web in 2026 (VL §3b),
and no endpoint inventory records that combination, because the combination is a property of the
connection.

**An interim approach already exists, and the recommendation should carry it.** The modelling
options have been worked through in the methodology community: four candidate treatments were
evaluated — relationship as an asset, as a pair of endpoints, as a first-class attributed edge,
and by binding the protocol to the locus — and the conclusion was that the endpoint-pair and
protocol-binding treatments compose adequately for a first version, with the first-class edge
parked behind a named revival trigger: a consumer needing per-connection readiness or trust
posture that sits on no single endpoint.

That trigger is now met. The worked example in §10.5 is exactly the case described — a
connection whose post-quantum readiness cannot be read off either endpoint, and two trust-anchor
relationships belonging to neither.

The recommendation is therefore not "someone should look at this". It is: the analysis exists,
the interim composition is workable and in use here, and the condition for revisiting the
first-class model has been reached. Raising it where the models are made — the format bodies,
the protocol bodies, and the methodology work mapping between them — is a low-cost ask: it
opens a modelling question, it does not create an instrument.

## 12.3  Sequencing

Phasing follows the chain, not the legislative calendar (§11.8).

**Now.** RDY-08 (custodian), RDY-02 (format-independent definition), RDY-09 (escalate the
modelling gap). None requires an instrument, and all three unblock what follows.

Settle the shared attribute vocabulary, use-case template, and orientation and subject-scope
rules at the same time. These are cheap while one profile exists and expensive once four do.

**Next, with the baseline.** RDY-01, then RDY-04, RDY-05, RDY-07 as properties of it. Take
the procurement family first: it needs no instrument, it is where cryptographic posture is
actually set, and it exercises the whole method — orientation, subject scope, obligation levels,
conformance — against a decision with an unambiguous consumer. The other three families follow
against a proven template rather than in parallel against an unproven one. RDY-05
deserves emphasis: publishing a profile without a validator repeats the SBOM consumption failure
at the point where it is cheapest to avoid.

**Then, as demand.** RDY-06 in procurement, which is the first point where an obligation
attaches. RDY-03 runs alongside throughout.

**Caution on pace.** Two of the constraints in chapter 3 bear directly on how fast this can be
pushed. Protocol profiling is still in motion for several families (LYR-C-02), so a requirement
that fixes on a particular configuration too early will need withdrawing. And certification
throughput is finite and structural (LYR-T-03) — an instrument that accelerates demand at
LYR-C-04 without regard to it produces a queue rather than a migration. Neither is an argument
for delay; both are arguments for sequencing obligations against the stage they depend on.

## 12.4  What this report does not recommend

Stated so the omissions read as deliberate.

- **No new legislation.** Every recommendation above sits within instruments that exist or in
  procurement practice that requires none.
- **No selection of a serialisation format.** RDY-02 is specifically designed so the Union need
  not pick a winner between formats moving at different speeds.
- **No custodian.** See DR-01 and §11.7.
- **No recommendation on the constraints a profile cannot touch.** Service lives, capital
  cycles, performance overhead and organisational accountability are real limits on the pace of
  migration (§8.6). They are outside what cryptographic transparency can address, and this
  report does not pretend otherwise.

## 12.5  Closing

The transition described in chapter 3 will be walked more than once. Algorithms standardised
today will be deprecated; parameters will change; hybrid modes will be retired. The durable
question is not whether Europe completes this migration, but whether it emerges from it able to
do the next one — which requires knowing what cryptography is in use, being able to check a
proposed change against policy, and confirming that the change took effect, repeatedly and at
scale.

That capability is what a profile, and the automation it enables, is for. The post-quantum
transition is the occasion for building it, not the reason.


---

# Annex A  Profile definition table

**Owner:** _tbd_ · **Status:** first draft · Supports chapter 10.

The supply-chain PQC migration profile in the form a producer would work from. Obligation levels
per BCP 14, and **conditional on declared subject scope** (DR-12) — see §A.3b for the attributes
where the `product` and `deployed service` cases differ. Format binding is Annex B; nothing here
names a field in any serialisation.

## A.1  Artefact level

| # | Attribute | Obligation | Values | Notes |
|---|---|---|---|---|
| A1 | Profile name | MUST | string | Enables contractual citation (§11.4) |
| A2 | Profile version claimed | MUST | semantic version | A claim names the exact version |
| A3 | Product identity | MUST | name + version | |
| A4 | Producer identity | MUST | organisation | |
| A5 | Artefact timestamp | MUST | date-time | |
| A6 | Scope statement | MUST | prose + structured bounds | What was examined, what was not, how far down the chain (LSN-03, GAP-COM-04) |
| A9 | Declared orientation | MUST | inventory / migration / both | Classifies the profile. MUST NOT alter the meaning of any attribute shared with another orientation |
| A10 | Declared subject scope | MUST | component / product / deployed service / bounded estate | Determines evidence basis and disclosure authority (§10.2.1) |
| A11 | Boundary definition | MUST where A10 = bounded estate | structured | An estate artefact is an aggregate of mixed freshness; the boundary is stated, not inferred |
| A12 | `derivedFrom` | MUST where A10 = deployed service or bounded estate | upstream identity + digest + profile claimed | The derived artefact references, never rewrites (DR-12) |
| A13 | Evidence basis, artefact level | MUST where A12 present | declared / config-derived / runtime-measured | Interim for the stage-versus-basis gap (§10.7.3) |
| A7 | Completeness basis | SHOULD | build-generated / scanned / declared / manual | How the artefact was produced |
| A8 | Supersedes | MAY | artefact reference | Enables delta-as-evidence (§8.3) |

## A.2  Endpoint level

| # | Attribute | Obligation | Values | Notes |
|---|---|---|---|---|
| E1 | Endpoint identifier | MUST | string | Referenced by relationships |
| E2 | Endpoint role | MUST | exposed / consumed / internal | |
| E3 | Implementing component | SHOULD | component reference | Links to the SBOM (aspect 3.8) |
| E4 | Execution environment | SHOULD | software / HSM / TEE / TPM / other hardware | Feeds R7 |

## A.3  Relationship level

The unit of description (§10.3).

| # | Attribute | Obligation | Values | Notes |
|---|---|---|---|---|
| R1 | Relationship identifier | MUST | string | |
| R2 | Endpoints | MUST | 2 × endpoint reference | One may be out of scope; say so rather than omitting |
| R3 | Purpose | MUST | key establishment / authentication / integrity / confidentiality at rest | Multiple permitted |
| R3a | Operational role | MUST | digital signature / key exchange / bulk encryption / integrity under adversary / key derivation / **non-security use** | Weakness is a property of the role, not the primitive: MD5 in a signature is broken, MD5 in a cache key is not. Without this a consumer cannot separate genuine exposure from benign legacy use (§7.2, §8.2) |
| R3b | Non-security justification | MUST where R3a = non-security use | prose | Prevents the value being used to suppress findings silently. The claim is stated and attributable, not assumed |
| R4 | Algorithms and parameters | MUST | normalised term + parameters | Registry term where one exists; provisional term + upstream contribution where not (RDY-03) |
| R5 | `lifecycleStage` | MUST | intended / implemented / configured / observed | Supplier ordinarily declares *implemented*; operator may record *observed* |
| R6 | Classical retirement state | MUST | classical present / classical disabled / classical removed | Orthogonal to R5 (DR-09). Makes LYR-C-06 reportable |
| R7 | Hardware anchoring | MUST where E4 is not software | fixed / firmware-updatable / replaceable | Determines whether migration is update or refresh |
| R8 | Negotiation and fallback | SHOULD | prose + structured downgrade path | Behaviour when the far endpoint differs |
| R9 | Protocol profile implemented | SHOULD | specification + version/draft | Makes a moving target legible (GAP-STD-07) |
| R10 | Roadmap commitment | MAY | target state + date, marked forward-looking | Never merged with current state (RDY-07) |
| R11 | Out-of-scope declaration | MUST where applicable | reason | Prevents silence being read as assurance |
| R12 | Statement kind | MUST in derived artefacts | confirmed / suppressed / additive / divergent | Suppression and additive are mandatory, not optional — absence is otherwise ambiguous (DR-12) |
| R13 | Upstream relationship reference | MUST where R12 ≠ additive | relationship reference | Enables the cross-artefact checks C9–C12 |

## A.3b  Obligation by subject scope

Where the two differ. Attributes not listed carry the same obligation in both.

| Attribute | `product` | `deployed service` |
|---|---|---|
| R4 algorithms, as implemented capability | MUST | SHOULD — inherited by reference |
| R5 `lifecycleStage` = configured | — not knowable | MUST |
| R5 `lifecycleStage` = observed | — | SHOULD where measurable |
| R12 suppression records | — | MUST |
| Operator-supplied trust anchors and key storage (E1–E4, R1–R4) | — | MUST |
| R10 roadmap commitment | MAY | — not the operator's to state |
| A12 `derivedFrom` | — | MUST |

## A.4  Conformance rules

| # | Rule | Kind |
|---|---|---|
| C1 | All MUST attributes present | structural |
| C2 | R4 terms resolve to the registry, or carry a provisional marker | structural |
| C3 | R5 and R6 populated for every relationship | structural |
| C4 | Every endpoint referenced by an R2 is defined, or declared out of scope | structural |
| C5 | R10 values are never returned by a current-state query | structural |
| C6 | Consumer policy evaluation | policy — defined by the consumer, not the profile |
| C7 | A2 orientation is declared, and no attribute is used with a meaning contingent on it | structural |
| C7a | R3a present on every relationship; R3b present wherever R3a is `non-security use` | structural |
| C8 | A10 subject scope is declared; where it is `bounded estate`, A11 is present | structural |
| C9 | Every relationship resolves upstream via R13, or carries R12 = additive | cross-artefact |
| C10 | No relationship at `lifecycleStage: configured` whose algorithm the upstream artefact does not list as implemented | cross-artefact |
| C11 | Every R12 = suppressed references a capability still present upstream | cross-artefact |
| C12 | A12 digest matches the upstream artefact actually held | cross-artefact |

C10 failing is frequently not an error: it usually means a proxy, sidecar or platform component
is performing cryptography nobody attributed. Treat it as a finding to investigate (GAP-COM-04).

Outcomes are **pass / fail / out of scope**. Treating out of scope as pass is the failure mode
§10.6 warns against.

**Not in this table.** Exploitability judgements are excluded by DR-11 — they belong in a
separate assertion artefact referencing an artefact conforming to this profile, with its own
author, date and scope. Nothing here should be extended to carry them.

> **Open:** whether C6 belongs in the profile at all, or whether the profile should only define
> what a policy check *can* address. Resolve with aspect 3.5.


---

# Annex B  Format mapping

**Owner:** _tbd_ · **Status:** stub

Attribute-by-attribute mapping to CycloneDX and SPDX. Unmappable attributes are marked and the
gap recorded — that record is the evidence for GAP-STD-01.

| Attribute | CycloneDX | SPDX | Gap |
|---|---|---|---|
| _tbd_ | _tbd_ | _tbd_ | _tbd_ |

> **Verify:** every field name against the current specification releases. Do not draft this
> annex from memory.


---

# Annex C  Glossary

**Owner:** _tbd_ · **Status:** first draft

Terms as used in this report. Where a term is contested or used differently elsewhere, that is
noted — precision here prevents argument later.

## Core terms

**Cryptographic bill of materials (CBOM).** A structured, machine-readable inventory of the
cryptography associated with a product or system: algorithms and parameters, protocols, keys and
certificates, implementing libraries or hardware, and the configurations governing their use.

**Profile.** A defined subset of CBOM attributes, each with an obligation level, serving a named
decision — specified precisely enough that two parties can produce and check conforming
artefacts without further negotiation. Both a production recipe and a conformance checklist.

**Cryptographic relationship.** The locus at which cryptography is applied *between* two
parties. A relationship is not a cryptographic asset: it is a property of the connection, and
appears in neither participant's inventory. The report's structural claim rests on this
distinction (§2.3).

*Terms considered and rejected: "interface" over-fits to two-party communications and carries
protocol-specific baggage; "cryptographic context" collides with cipher context and runtime
state.*

**Endpoint.** A participant in a cryptographic relationship. The node to the relationship's edge.

**`lifecycleStage`.** An attribute value tag recording the basis of an assertion: *intended*,
*implemented*, *configured*, *observed*. Separates what a supplier declares from what an operator
can confirm.

**Classical retirement state.** *Classical present / classical disabled / classical removed*,
per relationship. Orthogonal to `lifecycleStage`. Distinguishes *PQC enabled* from *migration
complete* (DR-09).

**Profile family.** A group of profiles serving the same class of consumer decision —
procurement and vendor evaluation, vulnerability response, PQC migration, or compliance and
audit. Distinct from a *sector* profile, which extends a baseline with domain specifics; the two
compose (§11.6).

**Orientation.** A profile's declared classification as `inventory`, `migration`, or `both`.
Orientation says what kinds of fact a profile carries; it does not change the meaning of any
attribute shared with another orientation.

**Subject scope.** The declared kind of thing a CBOM describes — component, product, deployed
service, or bounded estate. Determines the producer's evidence basis and disclosure authority,
and therefore how a consumer should weigh the assertion.

**Bounded estate.** A defined collection of deployed systems within a stated organisational or
network boundary, treated as a single CBOM subject. Always an aggregate of mixed freshness and
provenance.

**Derived CBOM.** An artefact produced by an operator after installing and configuring a
product, referencing the supplier's artefact by identity and digest rather than replacing it.
Carries its own author, subject scope, date and evidence basis (DR-12).

**Statement kind.** In a derived artefact: *confirmed*, *suppressed*, *additive*, or
*divergent*. Suppression and additive records are mandatory, because absence is otherwise
ambiguous.

**Operational role.** What a cryptographic algorithm is doing — digital signature, key
exchange, bulk encryption, integrity under an adversary, key derivation, or a declared
non-security use. Weakness attaches to the role rather than the primitive: MD5 in a signature
is broken, MD5 generating a cache key is not.

**Capability ceiling / configured floor.** What a built artefact *can* do, against what a
deployment is configured to permit. Neither is derivable from the other, which is why
`lifecycleStage` distinguishes *implemented* from *configured*.

**Evidence basis.** How an assertion was established — declared, config-derived, or
runtime-measured. Orthogonal to `lifecycleStage`, which records *what point* a value describes
rather than *how it was known*. Carried at artefact level in this profile as an interim.

**Exploitability assertion.** A statement about whether a cryptographic weakness is reachable
and consequential in a given context. Distinct from the inventory, carried alongside it with its
own author, date and scope (DR-11). The software-domain analogue is VEX.

**Obligation level.** MUST / SHOULD / MAY per BCP 14. Sets both a floor preventing underreporting
and a ceiling bounding disclosure.

**Conformance.** Structural checks (mechanical, defined by the profile) and policy checks
(defined by the consumer). Outcomes are pass, fail, or **out of scope** — the third is not a
variety of pass.

## Adjacent artefacts

**SBOM.** Software bill of materials — inventory of components, libraries and dependencies. The
model on which CBOM is based and the channel through which it travels.

**HBOM.** Hardware bill of materials — hardware components and provenance. Relevant where
cryptography is hardware-anchored.

**VEX.** Vulnerability exploitability exchange — the software-domain artefact stating whether a
present vulnerability is actually exploitable in a product. Cited as an SBOM-era lesson
(LSN-10): inventory output was largely unusable without it, and as the precedent for keeping
cryptographic exploitability alongside the CBOM rather than inside it (DR-11).

**purl.** Package URL — a shared identifier convention for software packages.

## Cryptography and migration

**PQC.** Post-quantum cryptography — algorithms designed to resist both classical and quantum
attack.

**CRQC.** Cryptographically relevant quantum computer — one capable of breaking public-key
algorithms based on factoring or discrete logarithms within practically meaningful timescales.

**HNDL.** Harvest now, decrypt later — capturing encrypted traffic today to decrypt once a CRQC
exists. What gives migration a deadline set by data sensitivity lifetime rather than by hardware.

**Hybrid.** A mechanism combining a classical and a post-quantum component such that the result
holds if either remains secure. Also written PQ/T (post-quantum / traditional).

**Cryptographic agility.** Usually described as a system property — the ability to replace an
algorithm without redesign. This report treats it operationally as a *process* property:
inventory, policy check, confirmation of effect, repeatedly and at scale (§8.1).

## Report constructs

These are this report's own scaffolding, defined in `register.md` and not standard terminology.

**`LYR-C-*` / `LYR-T-*` / `LYR-X-*`.** Migration layers: the core chain of dependent stages, the
parallel tracks converging at deployment, and the cross-cutting constraints (chapter 3).

**`LSN-*`.** Lessons observed in SBOM adoption (chapter 6).

**`GAP-*`.** Readiness gaps (chapter 7). Tagged with the layer where the gap *bites*; origin
noted where the point of correction differs.

**`RDY-*`.** Readiness criteria (§7.7), each answered by a recommendation (chapter 12).

**`DR-*`.** Decision records (`decisions.md`). **`VL`.** Verification log.

## A note on German usage

Where a German version is produced: BSI has no official term for CBOM. Recommended usage is
**CBOM (kryptografische Stückliste)** on first use, consistent with BSI and NIS Cooperation Group
conventions, and CBOM thereafter.


---

# Annex D  References

**Owner:** _tbd_ · **Status:** first draft — **every entry requires verification**

> **Verify (pass 5):** this annex is assembled from working notes and secondary summaries.
> Before publication every entry must be checked against the primary document: exact title,
> publishing body, date, version, and a resolvable identifier. See `verification-log.md` §5 —
> commentary was sufficient to establish what to check and is not sufficient to cite.

## D.1  European instruments and guidance

- Regulation (EU) 2024/2847 — Cyber Resilience Act
- Directive (EU) 2022/2555 — NIS2, with its implementing regulation
- ENISA — technical implementation guidance supporting NIS2
- Commission Recommendation (EU) 2024/1101 — coordinated implementation roadmap for the
  transition to post-quantum cryptography
- NIS Cooperation Group — *A Coordinated Implementation Roadmap for the Transition to
  Post-Quantum Cryptography*, June 2025
- COM(2026) 13 — proposed amendment to NIS2 *(proposal; status to be confirmed)*
- Standardisation request M/606 to CEN, CENELEC and ETSI in support of the CRA
- ENISA — *SBOM Adoption State of Play — 2026*, June 2026

- Joint Germany–France–Netherlands position on post-quantum migration *(supports §11.1)*

## D.2  National guidance

- BSI TR-03183 — Cyber Resilience Requirements for Manufacturers and Products, Parts 1–3;
  Part 2 (SBOM) at v2.1.0
- BSI — CycloneDX property taxonomy for TR-03183-2
- BSI TR-02102-1 — cryptographic mechanisms: recommendations and key lengths, 2026 edition
- BSI — PQC migration guidance
- BSI — framework for cryptographic procedures under NIS2, structured as
  *Inventarisieren → Bewerten → Umsetzen* (inventory → assess → implement)
- TNO — Dutch quantum risk methodology
- CERT-In — technical guidelines on SBOM, QBOM, CBOM, AIBOM and HBOM *(status to be confirmed)*

## D.3  Standards and specifications

- ECMA-424 — CycloneDX bill of materials standard, 2nd Edition
- CycloneDX Cryptography Registry
- SPDX specification, 3.0.1; SPDX cryptography workstream materials
- NIST FIPS 203, 204, 205 — ML-KEM, ML-DSA, SLH-DSA
- IETF: RFC 9794 (PQ/T terminology); RFC 9958 (post-quantum cryptography for engineers); RFCs
  covering X.509 and CMS uses; TLS, JOSE/COSE and IPsec work in progress
- BCP 14 (RFC 2119, RFC 8174)
- OpenVEX — vulnerability exploitability exchange specification
- CSAF 2.0 — Common Security Advisory Framework, OASIS
- OWASP CycloneDX — authoritative guide to CBOM
- NIST IR 8547 — transition to post-quantum cryptography standards

*Per-document status as at mid-2026 is recorded in `verification-log.md` §3b; drafts move, and
citations must state the exact revision relied on.*

## D.4  Methodology

- PKI Consortium, CBOM Profiles Working Group — charter and methodology for defining CBOM
  profiles. **The motivating precedent for the profile-first, format-independent approach used
  in this report.** Cite this, not the PQC Maturity Model, which is a separate effort.

## D.4b  United States

- Executive Order 14412 — securing the nation against advanced cryptographic attacks (June 2026),
  and the companion OMB memorandum
- OMB M-23-02 — migrating to post-quantum cryptography

## D.4c  Tooling

- IBM CBOMkit — open-source CBOM generation, scanning and viewing tools
- Linux Foundation Post-Quantum Cryptography Alliance — open PQC projects and CBOM tooling
  (pqca.org) *(supports RDY-05)*

## D.5  Sector work

- GSMA — CBOM in telecommunications *(referenced as the sector-profile example in §11.6)*

## D.6  Supporting research

- Research on SBOM adoption barriers by business stakeholder group *(Kloeg et al.)*
- Studies on post-quantum authentication in TLS certificate hierarchies

## Citation convention

Primary instruments and specifications only. Vendor and consultancy commentary was used during
verification to establish what to check; it does not appear here. Where a claim in the body
rests on practitioner observation rather than a source, the body says so — it is not
back-filled with a citation that does not support it.


---

