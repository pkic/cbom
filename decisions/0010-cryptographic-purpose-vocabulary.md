# 0010. Capability is stated per cryptographic purpose, from a fixed vocabulary

- **Status:** Proposed
- **Date:** 2026-08-21
- **Aspect:** 3.10 — Forward-looking / roadmap information (with consequences for 3.3 and 3.7)
- **Topic / issue:** #10, and #1 for the attribute-model half
- **Deciders:** not yet taken; settles Q27, raised from a discussion of staged PQC profiles
- **Decision rule applied:** lazy consensus (pending)

<!--
Implemented in the worked example, like 0008 and 0009, so the group is asked to ratify or reverse a
position that exists in the drafting rather than to decide in the abstract. Two points are still
left open rather than decided here, so the record can be accepted in part.
-->

## Context
> **Numbering.** Rule ids in this record predate decision 0011, which renumbered the family. `M1` to `M9` are now `pqc-migration#I1` to `#I9`; the capability group `M10` and its members are `pqc-migration#G1` and `G1.1` to `G1.3`; the rules recorded here as `M11` and `M12` were replaced before release and have no successor.


Q27 asks whether readiness is stated once per interface or separately for each job cryptography
does, and gives its own answer to why it matters: post-quantum key agreement can be deployed now
while post-quantum identity proof waits on certificate and PKI changes, so "keys done, identity
not yet" is the common position and one status per interface cannot express it.

The worked example already can't. Rule M10 constrains `capabilityStatus` to a single value from a
vocabulary, and the PQC Migration section states `available` for key exchange and `committed` for
authentication on one interface, with `blockedBy: certification` for the authentication case only.
That is a compound value the rule shape rejects, and M11's guard —
`requiredWhen: {attribute: capabilityStatus, notEquals: available}` — cannot evaluate against it at
all. The rules file records the gap as an exclusion pointing at this question.

A second requirement arrived from a separate direction. A sector body wanting to stage a migration
profile — harvest-now-decrypt-later first, authentication later, key protection after that — needs
to bound what a profile covers without writing the attribute set three times. Both needs are met
by the same change: make the forward-looking attributes per purpose, and let a profile declare
which purposes it requires in depth.

## Options considered

- **Option A — one status per interface**, as today. The supplier states the least advanced
  position, which governs (trade-off: Q27's own objection. A supplier forced into one answer gives
  the less advanced one, and a buyer concludes nothing can proceed when half of it can).
- **Option B — one status per algorithm.** Maximum resolution (trade-off: an algorithm is an
  implementation detail of a purpose, and a planner does not act per algorithm. It also breaks when
  one algorithm serves two purposes, which is common).
- **Option C — one status per cryptographic purpose**, from a vocabulary fixed by the methodology
  and extensible by sector profiles (trade-off: a new vocabulary to agree, and a repeated-group rule
  shape the validator does not have).

## Decision

Proposed: Option C.

### Purpose, not operation, and not role

Two naming collisions have to be avoided, and the second is the substantive one.

`endpointRoles` is rule I6 and already means *which party you are* — client, server. Decision 0005
requires an established name to keep its meaning, so the new concept is **`cryptographicPurpose`**
and not a second sense of "role".

The deeper collision is with CycloneDX. The example CBOMs already carry
`cryptoFunctions: ["sign", "verify"]`, `["encrypt", "decrypt"]`, `["keygen", "keyagreement"]`. Those
are **operations**: what an algorithm does. A purpose is what the system uses it for, and only the
purpose has a migration timetable. A TLS certificate signature and a firmware signature are both
`sign`/`verify`; one migrates when the PKI does, the other must still verify in twenty years and
migrates when the last verifier in the field is upgraded. Same operation, different decade,
different action. A vocabulary of operations would restate `cryptoFunctions` and answer no planning
question, and the mapping should say so, because the question will be asked.

### The test for inclusion

A purpose belongs in the base vocabulary when all four hold. The test exists so that additions can
be argued on their merits rather than by accretion.

1. **Declarable at the boundary.** A producer treating the subject as a black box can state it.
2. **Independently migratable.** It can be `available` while another purpose on the same interface
   is blocked. This is Q27's criterion and the one that earns a purpose its own entry.
3. **Actionable.** A planner does something different depending on its status.
4. **Not an ingredient.** It is not an algorithm appearing inside another purpose.

### The vocabulary

| Purpose | The question it answers | Why it is separate |
|---|---|---|
| `key-establishment` | Can this interface agree a quantum-safe session key? | The urgent one: harvest-now-decrypt-later. Covers agreement, KEM and key transport, which answer one planner question |
| `encryption` | What protects the data once a key exists? | Quantum impact is mild, so its timetable differs sharply from key establishment. Separating them stops the urgent half hiding inside a "confidentiality" status that is mostly fine |
| `entity-authentication` | How do the parties prove who they are, now? | The long pole: needs certificate profiles, PKI and root rollover. Invisible if merged with the two above |
| `data-integrity` | What protects a message from modification? | Symmetric, and essentially unaffected. Merging it with entity authentication averages "no action" with a multi-year programme |
| `non-repudiation` | What signs artifacts that must verify years later — code, firmware, documents, timestamps? | Governed by the verifier population rather than the signer. The action is re-signing and fleet upgrade, not certificate rotation |
| `key-protection` | Where do keys live, and what confines them? | Gates the others: an HSM that cannot do ML-DSA turns an authentication update into a hardware refresh. Partly present already as `providerLocation` |
| `key-derivation` | How are keys derived from other keys or secrets? | Own lifecycle, and a live agility and audit question |

Seven entries. An eighth, `randomness`, is **left open** — see below.

Deliberately excluded, with the test that excludes them: **certificate and trust-path validation**
(OCSP, CRL, path building) fails test 2, since it migrates when entity authentication does;
**hashing** fails test 4, being an ingredient of signature, KDF and MAC rather than a purpose;
**key escrow and recovery** is real but sector-shaped and belongs in an extension.

### Rule shape

`capabilityStatus`, `blockedBy` and `roadmapRef` move from single-valued interface attributes to a
repeated group keyed by purpose:

```json
"capabilityByPurpose": [
  { "purpose": "key-establishment",   "capabilityStatus": "available" },
  { "purpose": "entity-authentication", "capabilityStatus": "committed",
    "blockedBy": "certification", "roadmapRef": "https://example.test/pqc-roadmap#auth" }
]
```

M11's conditional guard then applies within a group member rather than across the interface, which
is what makes it evaluable again.

### Scope, and what staging costs

A profile declares the purposes it requires in depth:

```json
"scope": { "cryptographicPurposes": ["key-establishment", "encryption"], ... }
```

Rules are written once and quantified over the declared purposes, so a harvest-now-decrypt-later
profile and a profile that adds authentication have identical rule text and differ by one line.
Adding a purpose is adding rules, which monotonic extension permits, so conformance to the later
stage still implies conformance to the earlier one.

**Purposes outside the declared set still require a status.** In-scope purposes require the full
attribute set; out-of-scope purposes require `capabilityStatus`, and `blockedBy` where the status is
not `available`. That is one enumerated value per purpose, which is close to the cheapest obligation
a profile can impose, and it is what stops a staged profile becoming a permanent floor: a supplier
cannot conform to a stage-1 profile while behaving as though authentication does not exist, and a
buyer sees the long-lead blockers in the first document rather than the third.

## Rationale

The asymmetry Q27 describes is not a detail of one profile; it is the shape of the migration. Key
agreement is urgent because confidentiality is retroactively vulnerable, and authentication is slow
because it depends on infrastructure the vendor does not control. A model that cannot hold both
positions at once will report the pessimistic one, and a planner reading it defers work that could
have started.

Purpose is the right granularity because it is where the timetables actually differ. Per interface
is too coarse, as Q27 says. Per algorithm is too fine and models the wrong thing: a planner does not
schedule work per algorithm, and an algorithm can serve two purposes with different statuses.

Requiring a status for out-of-scope purposes is the part worth defending, because it looks like
scope creep and is the opposite. Without it, staging is a way to avoid questions; with it, staging
is a way to sequence *depth of answer* while the shape of the problem stays fully visible. It also
supplies the group with the evidence for when to publish the next stage, since the aggregate of
out-of-scope statuses across suppliers is a readiness signal nothing else produces.

## Consequences

Implemented. What it took:

- `cryptographicPurposeVocabulary` with the seven purposes, declared like every other vocabulary
  in the file, and `scope.cryptographicPurposes` naming the three this profile takes in depth.
- M10, M11 and M12 replaced by one group rule M10 with members M10.1 to M10.3. This is new
  validator capability rather than configuration: `check_rule` evaluated one attribute against one
  value, and a group needs coverage per key, member evaluation inside an entry, and a
  `requiredWhen` guard that resolves against the entry rather than the interface.
- **C13**, holding a group rule to two things that would otherwise pass silently: a group keyed by
  a vocabulary that does not exist requires an entry for no keys, and a group covering only the
  purposes in scope lets a profile defer a question and never ask it again.
- Group members counted as rules by C3 to C6 and by C12, since they are rules and are usually the
  forward-looking ones.
- Carriage in CycloneDX as `pkic:profile:capabilityByPurpose:<purpose>:<attribute>`, following the
  `endpointRole:<role>` convention. Three segments after the prefix marks a group entry, so the
  adapter needs no profile knowledge. The SPDX column stays unresolved with the rest of the
  per-interface rows (Q48).
- Migration profile v0.3 → **v0.4**, a **tightening**: a document carrying one status per interface
  does not conform to v0.4. Both example documents reissued, the worked interface on the PQC
  Migration page rewritten as the demonstration, and the deferring exclusion replaced with the
  narrower one that survives — per-*algorithm* status is still excluded, now for a stated reason
  rather than pending this question.
- Two fixtures, and six tests covering the group, including one that strips the deferred purposes
  from a conforming document and asserts it stops conforming. That obligation is the ratchet, so
  it is asserted rather than assumed. The suite runs 114 tests and passes.

Two points are **left open for the group rather than decided here**:

**Whether `randomness` is a purpose.** It passes tests 1, 3 and 4: a producer can state its DRBG and
entropy source, an auditor acts on the answer, and it is not an ingredient of another purpose. It
arguably fails test 2, since it does not migrate on a post-quantum timetable, though ML-KEM and
ML-DSA carry their own entropy requirements. Including it makes the vocabulary answer a question
regulators ask; excluding it keeps the vocabulary purely migration-shaped. This is a judgement about
what the methodology is for, which is the group's to make.

**How a sector profile widens the vocabulary.** Q35 asks whether a profile may *narrow* an inherited
list of permitted values. A sector adding `attestation`, `tokenization`, `secret-sharing`,
`password-verification` or `privacy` would *widen* one, which Q35 does not discuss and which is
arguably a relaxation: a document could then claim a purpose the base profile has no rule for. The
mirror case has been added to Q35.

## Links

- Q27, which this settles, and Q35, which gains the widening case.
- Decision 0005 for the naming conventions, and 0007 for the status-and-blocker shape this extends.
- `docs/methodology/pqc-migration.html`, rules M10 to M12, and the deferring exclusion in
  `profile-pqc-migration.rules.json`.
