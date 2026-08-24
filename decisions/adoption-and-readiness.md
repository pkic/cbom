# How adoption will work, and what makes an aspect ready for it

- **Status:** draft for discussion, not itself a decision
- **Date:** 2026-08-24
- **Prepared for:** the PKIC CBOM Profiles Working Group

## Where this sits

The methodology and its worked example are alpha. Decision records are written from choices taken
while building it, so that the reasoning behind a choice survives the choice — not because the
group has been asked to hold those positions yet. Thirteen records carry the status **Proposed**,
and that is the correct status for all of them today.

Adoption is not a milestone at the end. It happens per aspect, as each one stops moving. Some will
be ready long before others: 3.2 (identity and metadata) and 3.10 (forward-looking information) own
few open questions and their rules have been stable through several revisions, while 3.3 (the
attribute model) owns eleven and is still absorbing sector feedback. Waiting for all twelve would
mean adopting nothing until the last one settles, and adopting everything now would ratify
positions that are still being argued with by the code.

This note says how a batch will run when an aspect is ready, and — more usefully — what *ready*
means, so that "closer" is something the group can check rather than feel.

## What makes an aspect ready

An aspect is ready to be put to the group when all four hold. Each is checkable, and the ones that
fail say what is missing.

1. **No open question would change a rule.** Questions about scope, sequencing or presentation may
   remain. A question whose answer would add, remove or alter a requirement means the rules are
   still being designed.
2. **The worked example exercises it, and the suite covers it.** Every requirement belonging to the
   aspect is demonstrated by a conforming document and by one that fails it, so a member can
   disagree by running something rather than by reading.
3. **No open defect in the tools touches it.** A guarantee the tooling does not actually enforce is
   not a guarantee. Decision 0013 exists because monotonicity was stated, believed and unenforced
   for months.
4. **It has an owner.** Ratifying an aspect nobody owns leaves nobody to maintain what was
   ratified. This is the condition most likely to be the binding one — all twelve aspects are
   unassigned today.

An aspect meeting all four is ratifiable. One that does not is not, and the failing condition is
the work item.

## How a batch runs, when there is one

Lazy consensus needs three things that have to be stated together, or silence means nothing:

- **A set.** The specific records, named, with one line each on what ratifying commits the group to.
- **A window.** Long enough to read the material, short enough to remember. Two weeks for records
  with no live objection; longer where a record carries a point the group has not seen before.
- **A closing consequence.** What happens on the closing date, stated in advance.

Records are put in batches rather than all at once, because thirteen at a time produces either
thirteen silent assents — which is assent in name only — or one objection that stalls the lot.
Group by aspect readiness rather than by record number.

Any record carrying a point the group has not yet argued should have that point put as a question
rather than presented as settled. Known examples: whether `randomness` is a cryptographic purpose
(0010); how a sector profile *widens* an inherited vocabulary, the mirror of Q35 (0010); and the
revision to P2 in 0012, which is the only relaxing change in either profile's history and should
need an express yes rather than silence.

## Closing a batch

The window closing is the only moment at which lazy consensus produces anything, and it is the step
most easily left half-done — a record marked Accepted while the README still says Deliberating. The
result is a project whose own records disagree about what was decided, which is worse than not
having ratified at all. So the closing is a checklist, and it is one commit.

For each record in the batch with **no unresolved objection**:

1. `Status: Proposed` → `Status: Accepted`, and add `- **Ratified:** <date>, lazy consensus,
   <n>-day window opened <date>` under it. Keep `Deciders` as it stands: it records who drafted,
   not who assented.
2. Any question the record settles moves from *settled by decision NNNN, awaiting ratification* to
   *settled by decision NNNN*.
3. The aspect's row in the README moves `Deliberating` → `Converging`, or → `Decided` where the
   aspect owns no open question at all. Most will be Converging for a long time.
4. A comment on the aspect's tracking issue saying the record was ratified, with the date. The issue
   stays open while the aspect owns open questions.

For each record **with** an unresolved objection: it stays `Proposed`, and the objection is
summarised in the record itself under an `## Objections raised` heading, with who raised it and what
would resolve it. That heading is the useful artifact — a record that was contested and says why is
worth more than one ratified quietly.

Then one commit, naming the batch, the window and which records moved. Not several: the README table
and the record statuses have to change together or they will not change together. Finally, post the
outcome wherever the batch was announced.

## What this does not propose

No dates, and no batch is open. Nothing here starts a window. The four conditions above are the
gate, and the honest position today is that no aspect passes condition 4, and few pass condition 1 —
41 of 48 questions are open, which is what an alpha looks like.
