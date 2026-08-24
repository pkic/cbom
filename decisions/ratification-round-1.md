# Ratification round 1 — proposal for the working group

- **Status:** draft for discussion, not itself a decision
- **Date:** 2026-08-24
- **Prepared for:** the PKIC CBOM Profiles Working Group

## Why this exists

Thirteen decision records carry the status **Proposed**. None has been ratified. Every aspect in
the README's tracking table reads *Deliberating*, and every one is *unassigned*. The decision rule
is lazy consensus — silence is assent — but lazy consensus needs something a member could be silent
*about*: a stated set, a stated window, and a stated consequence when the window closes. None of
those has been set, so the records have accumulated rather than settled, and the worked example
implements thirteen positions the group has never been asked to hold.

That is the risk worth naming. The methodology pages, the two example profiles and both tools are
now internally consistent with all thirteen. A member reading them cannot tell which parts are
settled and which are one person's reasoning, because everything reads with the same confidence.

## Proposal: three batches, not one

Putting thirteen records to a group at once produces either thirteen silent assents, which is
assent in name only, or one objection that stalls the lot. Three batches, each with its own window,
gives a member a realistic amount to read and lets the uncontroversial half close.

### Batch A — foundations (six records, no live objection)

`0001` product- and instance-independence · `0002` facts not judgements · `0003` absence
distinguished from withholding · `0004` monotonic extension · `0005` attribute naming · `0006`
declared carrier versions.

These are the oldest, they are each already implemented and tested, and everything since depends on
them. Nothing later can be ratified while these are open. **Proposed window: two weeks.**

### Batch B — mechanism (four records, one open point each)

`0008` scope declaration · `0009` orientation · `0011` rule numbering · `0013` constraint
monotonicity and evaluability.

Each is machine-checked, so a member can test disagreement against the tools rather than argue it
in the abstract. Each carries one point the record itself leaves open, and those should be put
explicitly rather than buried:

- `0011` — nothing registers profile tags across families. Only bites if multiple inheritance
  arrives (Q23).
- `0013` — an override carrying a constraint kind the comparison does not recognise is **refused**.
  This is deliberate and it will eventually block someone.
- `0009` — whether orientation `both` should oblige the present-state counterpart of *every*
  capability attribute, or only of those a consumer would otherwise misread.
- `0008` — whether `intended` belongs in the accepted stage set of any published profile.

**Proposed window: three weeks.**

### Batch C — substance (three records, genuinely arguable)

`0007` status-and-blocker rather than a date · `0010` the cryptographic purpose vocabulary ·
`0012` what a disclosure baseline requires.

These are the ones a member is most likely to have a view on, because they determine what a
supplier has to write down. Two carry unsettled points that should be put as questions rather than
presented as settled:

- `0010` — is `randomness` a cryptographic purpose? The record declines to decide.
- `0010` — how does a sector profile *widen* an inherited vocabulary? The mirror of Q35, unresolved.
- `0012` — the revision to P2 is the only **relaxing** change in either profile's history.
  Relaxations are otherwise forbidden, so this one needs express assent rather than silence.
- `0012` — should `implementationPurl` stay withholdable, given the baseline's stated decision?

**Proposed window: four weeks, with the P2 relaxation requiring an explicit yes from at least two
members rather than silence.**

## What ratification should change

- The record's status moves `Proposed` → `Accepted`, with the date and the window that closed.
- The questions each record settles move from *awaiting ratification* to *settled*. Q27, Q33, Q34
  and Q38 are in that state today.
- The aspect's row in the README moves `Deliberating` → `Converging`, or `Decided` where the aspect
  has no open questions left. Aspects 3.2 and 3.10 are closest.
- An aspect gains an owner. Twelve unassigned aspects is the more serious of the two governance
  gaps, because ratification without an owner produces no one to maintain what was ratified.

## Closing a batch

The window closing is the only moment at which lazy consensus produces anything, and it is the
step most easily left half-done — a record marked Accepted while the README still says
Deliberating, or an issue commented on and never relabelled. The result is a project whose own
records disagree about what was decided, which is worse than not having ratified at all. So the
closing is a checklist, and it is one commit.

For each record in the batch with **no unresolved objection**:

1. `Status: Proposed` → `Status: Accepted`, and add `- **Ratified:** <date>, lazy consensus,
   <n>-day window opened <date>` under it. Keep `Deciders` as it stands: it records who drafted,
   not who assented.
2. Any question the record settles moves from *settled by decision NNNN, awaiting ratification* to
   *settled by decision NNNN*. Batch A settles none directly; batches B and C settle Q27, Q33, Q34
   and Q38.
3. The aspect's row in the README moves `Deliberating` → `Converging`. **Not** `Decided` — an
   aspect is Decided only when it owns no open questions, and none of the twelve does today.
4. A comment on the aspect's tracking issue saying the record was ratified, with the date. The
   issue stays open.

For each record **with** an unresolved objection: it stays `Proposed`, and the objection is
summarised in the record itself under a `## Objections raised` heading, with who raised it and
what would resolve it. That heading is the useful artifact — a record that was contested and says
why is worth more than one that was ratified quietly.

Then one commit, message naming the batch, the window and which records moved. Not several: the
README table and the record statuses have to change together or they will not change together.

Finally, post the outcome back to the Discussion. A ratification nobody is told about has the same
practical effect as none.

## What this does not propose

Nothing about the 41 open questions. Ratifying a decision does not close a question the decision
did not address, and the open-questions list is the honest record of how much is unsettled — 41 of
48. It should stay that way rather than being tidied to look further along than it is.
