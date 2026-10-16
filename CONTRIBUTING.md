# Contributing

This guide describes how work moves through the CBOM Profiles Working Group. The goal is that
anyone — a long-standing member or someone arriving six weeks late — can see what has been
decided, what is still open, and how to weigh in.

## The lifecycle of a topic

Every aspect of the methodology, and every sub-question within it, moves through four states.
The state is shown by a `status:` label.

1. **Raised** — A topic is opened. Open-ended exploration starts as a **Discussion**; a topic
   that is already a concrete choice starts as an **Issue**. Either way, use the
   [aspect topic template](./.github/ISSUE_TEMPLATE/aspect-topic.md) so the objective,
   background, options, and open questions are stated up front. Apply the `aspect:*` label and,
   if relevant, an `orientation:*` label.

2. **Deliberating** (`status:deliberating`) — The argument is open. Options are added and
   challenged; questions are surfaced. Reactions (👍/👎) are *signal*, not the decision
   mechanism. Keep one canonical thread per topic — link related threads rather than forking
   the discussion.

3. **Converging** (`status:converging`) — Options have narrowed. A maintainer or the aspect
   owner posts a **proposed decision** in the thread and gives notice (e.g. "decision in 7
   days unless objections"). If the topic began as a Discussion, promote it to an Issue now so
   it can be closed and linked to a PR.

4. **Decided** (`status:decided`) — The decision rule (below) has been satisfied. A
   **decision record** is committed to [`/decisions`](./decisions) and linked from the issue.
   The issue is closed when the corresponding spec change merges. If a topic is parked, use
   `status:deferred` or `status:blocked` and say why.

## The decision rule

Default: **lazy consensus.** A proposed decision that draws no sustained objection within the
notice period (default 7 calendar days) is adopted. "Sustained objection" means a substantive
concern, not a preference — the objector is expected to propose an alternative.

If consensus cannot be reached, escalate in this order:

1. The **aspect owner** makes a call and records the dissent in the decision record.
2. Failing that, the topic goes to the next working-group **call** for a decision, with the
   outcome recorded in committed meeting notes and the decision record.

Record *who decided and why*, including any minority position. The audit trail matters more
than unanimity.

## Roles

- **Aspect owners** — listed in [`.github/CODEOWNERS`](./.github/CODEOWNERS). An owner shepherds
  their aspect from raised to decided, keeps its thread canonical, and drafts its spec section.
  Owners are not sole deciders; they drive the process.
- **Maintainers** — manage labels, the board, releases, and the decision cadence. They can
  invoke the decision rule.
- **Contributors** — anyone participating. No special status is needed to raise a topic, argue
  a position, or open a PR.

## Decisions are records, not threads

When a topic is decided, copy [`decisions/0000-template.md`](./decisions/0000-template.md) to
`decisions/NNNN-short-title.md`, fill it in, and link it from the issue. This is the single
source of truth for *what was decided and why* — the thread is the evidence behind it, not the
record of it.

## The specification evolves by pull request

The methodology draft lives in `spec/` as **Markdown**. Wording is discussed at line level in
PR review, which keeps the argument about *text* attached to the *text*. A PR that implements a
decision should link the decision record. Word/PDF are generated for publication; do not edit
binary formats in the repo.

## Connecting async and sync

Working-group calls are part of the process, not a side channel. Commit meeting notes to the
repo (e.g. `meetings/YYYY-MM-DD.md`) and link the issues discussed, so a decision taken on a
call is traceable from its issue and vice versa.
