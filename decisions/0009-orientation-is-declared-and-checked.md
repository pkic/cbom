# 0009. A profile declares its orientation, and the declaration constrains its rules

- **Status:** Proposed
- **Date:** 2026-08-21
- **Aspect:** 3.1 — Profile objective & scope (with consequences for 3.3 and 3.7)
- **Topic / issue:** #4, and #1 for the attribute-model half
- **Deciders:** not yet taken; raised from a second member submission on the profile preamble
- **Decision rule applied:** lazy consensus (pending)

## Context

Decision 0008 rejected `orientation` on the grounds that no consumer acts on it: a profile
already states its consumer and decision, and a label saying `inventory` or `migration` adds
nothing a reader could not infer. That reasoning was sound for the proposal as it stood, which
was a bare classification.

A second submission put it differently. Orientation should be declared, but "it should not
silently change the meaning of shared attributes. Present-state attributes remain present-state
attributes; migration profiles add capability, dependency, and roadmap facts using distinct
names." On that reading orientation is not a label but a guard, and the thing it guards against
is reachable today.

Decision 0005 and requirement C5 police the *names*: a bare name denotes present state, a
`Supported` suffix denotes declared capability, and the `Current` suffix is rejected. Nothing
polices whether a profile requiring the capability form also requires the present-state form.
The migration example requires `protocolVersionsSupported`, `keyExchangeSupported` and
`authenticationSupported` in rules M1 to M3 (now `pqc-migration#I1` to `#I3`; see decision 0011), and obtains their present-state counterparts only
by inheriting I2, I3 and I5 from the baseline. A migration profile written standalone, or
extending something else, could require capability alone and pass every requirement from C1 to
C11. A consumer reading `keyExchangeSupported: [ML-KEM, X25519]` would have no way to tell what
the interface negotiates today, and would in practice read the capability as present state.

## Options considered

- **Option A — leave orientation out, as 0008 decided.** The naming conventions already
  distinguish the two senses (trade-off: they distinguish the names, not the obligations, and
  the gap above stays open. Nothing stops capability arriving instead of present state).
- **Option B — declare orientation as a classification.** A profile states `inventory`,
  `migration` or `both` (trade-off: this is the version 0008 rejected. Nothing checks it, so it
  drifts from the rules while still being read as authoritative, which is worse than absent).
- **Option C — declare it, and make the declaration constrain the rules.** Each value carries an
  obligation the checker enforces against the resolved profile (trade-off: a twelfth requirement,
  and a profile author has one more thing to get right).

## Decision

Proposed: Option C. `scope.orientation` takes one of `inventory`, `migration`, `both`, and a new
**C12 (MUST)** holds the rules to it.

| Value | Obligation |
|---|---|
| `inventory` | Requires no forward-looking attribute — no `*Supported`, and none of `capabilityStatus`, `blockedBy`, `roadmapRef`. |
| `migration` | May require them, and must require at least one, or it is an inventory profile mislabelled. |
| `both` | May require them, **and** every capability attribute it requires must have its present-state counterpart required as well. |

The `both` row is the submission's requirement made mechanical. C12 is evaluated against the
resolved profile, so inheritance satisfies it: the migration example declares `both`, requires
six forward-looking attributes, and takes the three present-state counterparts from the baseline.

The four values are those the working group already uses to classify its own aspects in
`_data/aspects.yml`, less `n-a`. A profile that reports neither present state nor capability is
not a profile.

## Rationale

The distinction between what an interface does and what it could do is the one most likely to be
lost in transmission, because the two are reported in the same document, about the same
interface, using names that differ by one suffix. A buyer who reads a capability set as a present
state concludes that an interface is already quantum-safe when the vendor has claimed only that
it could be configured that way. Nothing in the methodology prevented a profile from making that
misreading the only available reading.

Orientation was rejected in 0008 because it did no work. Option C gives it work, and the work is
exactly the guarantee the submission asked for. A declaration that constrains nothing was the
right thing to reject; the error was treating the proposal as only that.

Declaring `migration` rather than `both` for the migration example was considered and is wrong:
that profile reports present state as well, and `migration` would understate what it requires.
The value describes what the profile obliges, not what motivated it.

## Consequences

Implemented in the worked example.

- Baseline v0.4 → **v0.5**, declaring `inventory`. Migration v0.2 → **v0.3**, declaring `both`
  and re-pinning its base. Both changes editorial: no document verdict changes, because the
  constraint falls on the profile rather than on the document.
- `check_profile.py` gains C12 and `validate_cbom.py` the orientation vocabulary and the
  present-state pairing helper. Two fixtures, one for each failure mode: capability without its
  counterpart under `both`, and an `inventory` profile requiring `capabilityStatus`.
- The C5 fixture gained a present-state rule it does not otherwise need, so that it still
  isolates C5 rather than failing C12 as well. That it needed `keyExchange` rather than the
  `keyExchangeCurrent` it already had is a small demonstration of why the `Current` suffix was
  rejected in 0005.
- `tests/check-fixture-pins.py` was added after the version bump broke three fixtures pinning the
  old base. It reports a stale pin directly rather than letting it surface as a missing word in
  an unrelated assertion.
- Decision 0008 is annotated rather than edited: the clause rejecting orientation stands as a
  record of what was decided and why it was revisited.

Reversing this means removing a MUST requirement, which no document depends on, so the cost is
lower than 0008's: two profile versions and the tooling, with no effect on any CBOM already
produced.

## Links

- Second member submission on the profile preamble, August 2026.
- Decision 0008, which rejected orientation, and decision 0005, which fixed the naming
  conventions this builds on.
- Conformance requirement C12; `docs/methodology/check_profile.py`.
- `review-2026-08-structured-preamble.md` for the first submission and its disposition.
