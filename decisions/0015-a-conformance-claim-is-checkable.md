# 0015. A conformance claim is bound to a document, lists each profile separately, and can be re-checked

- **Status:** Proposed
- **Date:** 2026-08-24
- **Aspect:** 3.5 — Conformance & validation (with consequences for 3.9)
- **Topic / issue:** #7, and #9 for the several-profiles half
- **Deciders:** not yet taken; settles Q24
- **Decision rule applied:** lazy consensus (pending)

## Context

Everything in this methodology is machine-checkable except the one artifact that crosses an
organisational boundary. A profile is a rules file a validator reads. A CBOM is a document a
validator evaluates. A **claim** — the thing a supplier actually hands a buyer — was four lines of
prose in a `<pre>` block on the Profile page.

That is the wrong way round. The producer and the consumer are in different organisations, months
apart, and the consumer was not present when the evaluation ran. Every other artifact is checked by
someone who has the inputs in front of them; the claim is the only one read by someone who does not.

Q24 asked how a claim describes conformance to several profiles at once. Answering it turned up
three further gaps that matter more:

**A claim was not bound to a document.** "Conforms to pkic.example.pqc-migration v0.6" is a
statement about some CBOM. Put it beside a different CBOM and nothing contradicts it. A claim that
cannot be falsified by the wrong document is not evidence.

**A verdict alone loses the disclosure state.** "Conforms" with `implementationPurl` withheld and
"conforms" with it supplied are materially different answers to the question the baseline exists to
serve, and the profile permits both. A claim reporting only the verdict throws away the distinction
the four-outcome model was built to preserve.

**A claim carried no statement of what it does not assert.** The Conformance section has that list.
A consumer reading a claim in nine months will not have read the Conformance section, and the word
"conforms" invites more inference than it can carry.

## Options considered

- **Option A — leave the claim as prose**, and rely on the report for detail (trade-off: the report
  is generated where the evaluation ran and is not what gets forwarded. Prose is what gets
  forwarded, and prose cannot be checked).
- **Option B — a claim is the report.** Ship the full JSON report as the claim (trade-off: large,
  carries per-rule detail a producer may not wish to forward, and still says nothing about which
  document it describes).
- **Option C — a claim is a distinct, minimal, checkable artifact**: bound to a document by digest,
  one entry per profile with the whole chain, disclosure states summarised rather than enumerated,
  and the non-assertions carried inside it.

## Decision

Proposed: Option C, plus a verifier.

**One claim, one document, bound by digest.** `sha-256` over the CBOM as it was evaluated. The
filename is a convenience; the digest is the identity.

**Several profiles are listed, not combined.** This is Q24's answer. Each entry carries its own
verdict, because a document can conform to one profile and fail another, and a single overall answer
would have to choose which question it was answering. Each entry carries the full inheritance chain
with pinned versions, so a reader can resolve exactly what was applied without looking it up.

**Disclosure states travel with the verdict.** Per profile: how many rules were assessed, and which
were failed, withheld, unknown or undeclared. Summarised by reference, not by re-stating every rule.

**A refused evaluation appears as refused, carrying no rule results.** T1 forbids merging refusal
with non-conformance, and a claim is where that merge would do the most damage — a buyer's
procurement filter reads the claim, not the report. Reporting "0 failed" about a document nobody
assessed is exactly that merge.

**The non-assertions are carried inside the claim**, not referenced.

**`--verify-claim` re-runs it.** A consumer holding the claim and the document can establish, without
trusting the issuer, that this is the document evaluated and that the profiles still produce the
recorded verdicts. Mismatch exits **5** — a new code, because it is a finding about the claim and
not a verdict on the document.

## Rationale

The verifier is what makes the rest worth having. Every field above could be written by hand into a
plausible-looking JSON document, and a consumer with no way to re-run the evaluation is back to
trusting the issuer — which is the position the whole methodology exists to improve on. With the
verifier, a claim is a falsifiable statement: wrong document, wrong version, or a verdict that no
longer holds, and it says which.

What the verifier deliberately cannot establish is that the disclosed values are true. A producer
who states `TLS 1.3` for an interface running `TLS 1.2` produces a claim that verifies perfectly.
That is in `notAsserted` and always will be — attestation is a different problem, and pretending
otherwise here would be the most damaging thing this format could do.

Listing profiles rather than combining them is the conservative reading of Q24, and it is also the
honest one. A combined verdict would need a rule for what "conforms to A and B" means when the two
disagree, and every such rule loses information a reader needs.

The exit code deserves its own line. Mismatch is not `1`: a claim failing to verify says nothing
about whether the document conforms. Someone holding a bad claim and a good document should evaluate
the document, and an exit code that told them "does not conform" would send them the wrong way.

## Consequences

- `validate_cbom.py` gains `--claim` (accepting several profiles), `--verify-claim`,
  `--profiles-dir`, and exit code 5. `build_claim`, `verify_claim`, `chain_of`, `rule_states`,
  `digest_of` and `find_profile` are new.
- `find_profile` locates a rules file by reading candidates and comparing the declared `profileId`,
  rather than by guessing a filename convention the methodology does not impose. A claim cites a
  profile by identity; where the file sits is the verifier's problem.
- `claim.schema.json` is published, and encodes two consistency rules a schema can enforce: a
  refused entry carries no rule results and asserts `assessed: false`, and an entry claiming
  conformance may not also list a failed MUST.
- `claim-example.json` is committed as a worked example, over both profiles at once.
- Twelve new tests, including that the same claim does not verify against a different document, and
  that a tampered verdict is caught by re-evaluation.
- The Profile page's prose claim block is replaced by the real thing.

## Links

- Q24, which this settles.
- Decision 0003, whose four disclosure outcomes are what `rules` preserves; 0011, which made a
  profile citable as a tag plus version; 0016, which bounds what an SPDX-only claim may assert.
- Conformance requirement T1, and the "what a conformance verdict does not assert" table, which is
  the source of `notAsserted`.
