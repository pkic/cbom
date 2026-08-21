# Design note: multi-party trust, and what payment rails actually need

Working note for the PKIC CBOM Profiles Working Group.
Written 21 August 2026, in response to member feedback on financial-sector systems.

## The feedback

> FSI/payment-rail systems (RTGS, SWIFT, LYNX/RTR-class settlement) carry multi-party certificate
> trust patterns closer to Q08's "group cryptography" question than to the two-party model the
> baseline assumes today. This is a dependency between Q08 and Q25, not a separate ask.

The conclusion is right: the baseline cannot describe these systems, and a finance profile is
blocked until it can. The attribution to Q08 is, I think, wrong, and getting it wrong matters,
because Q08 is the most expensive open question in the register and folding this into it would
block a cheap fix behind an expensive one.

## Shared key against shared trust anchor

Q08 asks how to describe cryptography **shared among many parties**, and the Model records the
same case as a known limitation. Its defining property is stated there precisely: a group
relationship "does not decompose into pairwise edges without losing the shared key and the
membership over which it applies". Broadcast, multicast and group messaging have that property. n
parties hold one key at one time, and any pairwise description of the system is false.

Closed-membership financial messaging generally does not. What those systems share is a **trust
anchor** and an administered membership: a scheme operator decides who may participate and issues
or anchors their credentials, each participant holds its own keys, and the traffic runs pairwise
between counterparties or hub-and-spoke through a central operator. Each leg decomposes into a
pairwise relationship and nothing is lost by describing it that way — which is the test Q08 sets,
and this case passes it.

So generalising the relationship to n endpoints, which is what Q08's Option B would do, would not
help. The two systems look alike from a distance because both involve many parties. They differ
in what is shared, and it is the sharing of a *key* that breaks the model, not the sharing of a
*trust anchor*.

## What is actually missing

Two things, of very different cost.

**A trust domain.** The baseline records `authentication`, the signature algorithm an interface
uses. Nothing records that the trust anchor is a scheme's rather than a public CA's, or that
membership in that scheme is administered and closed. For a settlement participant that fact
carries most of the security argument, and for a supervisor it is the thing being supervised. Two
interfaces with identical `authentication` values sit in entirely different risk positions
depending on who may hold a credential the interface will accept. This is a gap in the attribute
model, not in the relationship model, and no question in the register covers it. Filed as **Q47**.

**A verifier population.** Here the feedback is onto something the register does miss. A signed
settlement message is signed once and verified by every member that receives it. The Model's
taxonomy has a row for signing — two parties, not simultaneous, one-to-one, "parties never
interact; the verifier sets the ceiling" — and a row for broadcast — n parties, simultaneous,
one-to-many, not represented in v1. One signer to many verifiers is *n parties, not simultaneous,
one-to-many*, and the taxonomy has no such row. It is a one-to-many relationship, which is why it
reads as Q08, but it needs no shared key and no membership state at the cryptographic layer, so it
is far cheaper to model than the broadcast case. Filed as **Q46**.

The register's own framing invited the confusion: Q08 asks about cryptography "shared among many
parties", which is broad enough to swallow both. Q08 has been restated to say explicitly that it
is about a shared key, and to point at Q46 for the other half.

## The dependency on Q25

There is a dependency, and it runs the opposite way to how the feedback frames it.

Q25 asks where a sector profile sits, and its Option A — sector profiles build on the general
baseline — is the option that preserves portability, so that a supplier meeting a finance profile
also meets the baseline and the document stays useful to a buyer in another sector.

A finance profile cannot be built on the baseline today, because the baseline has no attribute in
which to say that an interface trusts a scheme's anchor under administered membership. Option A is
therefore conditional on Q47, and on Q46 for any profile that needs to describe the verification
fan-out. That conditionality is now recorded in Q25.

Note what this does *not* depend on. Nothing in the above requires Q08 to be settled. A finance
profile can be written while shared-key group cryptography remains out of scope, provided the
group agrees that these systems do not need it.

## What would settle this

The distinction above rests on a general reading of closed-membership scheme PKI rather than on
the internals of any particular rail. The question to put to a member who works on one:

> Do any of these systems use a key **shared among more than two participants at once** — a group
> key for a settlement window, a shared session key across a membership, anything requiring
> rekeying on join or leave — as opposed to per-participant keys under a common trust anchor?

If the answer is no, Q46 and Q47 are the whole of it, and Q08 stays out of scope with a clearer
boundary than it had. If the answer is yes for any rail, that is a direct argument for Q08's
Option B and changes the priority of the most expensive question in the register.
