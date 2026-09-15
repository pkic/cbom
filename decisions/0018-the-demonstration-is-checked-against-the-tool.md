# 0018. The demonstration loads the published rules and is checked against the reference tool

- **Status:** Proposed
- **Date:** 2026-09-12
- **Aspect:** 3.13 — Examples and tooling (with consequences for 3.5)
- **Topic / issue:** #13
- **Deciders:** not yet taken; settles Q30
- **Decision rule applied:** lazy consensus (pending)

## Context

The Conformance section opens its third part with a claim about tools: two tools given the same
document, the same profile and the same resolution of any extended base return the same verdict.
The site runs two tools. `validate_cbom.py` is the reference. The Demo page evaluates a document
in the browser, because a static site cannot run Python, and it told readers that what it showed
"corresponds to that performed by `validate_cbom.py`".

Nothing checked that. The page carried its own transcription of the rules and its own
implementation of the evaluation, and both were asserted to match rather than shown to. The two
had already diverged once: when the baseline was tightened, the page's copy had to be edited by
hand, and had the edit been missed nothing would have caught it. The failure mode is quiet. A
transcription that is merely out of date still renders a complete, plausible page, and a reader
has no way to tell that the profile it names is not the profile it applies.

Two further gaps turned up while settling this, both of the same kind — something described but
not evaluable:

**Two of the four example documents did not exist.** The page described four, and the repository
held two. The disclosure-states example and the no-management-interface example were arrays of
interface records written into the page, so the only two cases that exercise the four-outcome
model and the stated-absence rule were the two that no tool could evaluate.

**The interface records on the page were a third copy.** They were transcribed from the CBOMs the
adapter reads, and nothing held them to what it extracts.

## Options considered

- **Option A — have the page load the shared rules file** (trade-off: removes the rules copy and
  nothing else, since the evaluation logic is still written twice; adds a fetch, which fails when
  the file is opened from disk rather than served).
- **Option B — state on the page that the reference tool is authoritative** (trade-off: cheap and
  honest, and leaves a published page that can still be wrong. An advisory note does not help a
  reader who has no way to see the disagreement).
- **Option C — test the two against each other** (trade-off: the only option that would have
  caught the divergence that already happened, and the only one that addresses the logic rather
  than the data; costs a test that needs a JavaScript runtime).
- **Option D — remove the demonstration** (trade-off: the duplication goes and so does the thing
  that makes the conformance model legible to a reader who will not run a validator).

## Decision

A and C together, and neither alone.

The page fetches `profile-interface-disclosure.rules.json` at load and holds no transcription of
the rules: not the rule set, not the vocabularies, not the carrier range, not the profile version,
which it now prints from the file. When the fetch fails it says so and evaluates nothing, rather
than falling back to a copy.

The evaluation logic remains a second implementation, which loading a file cannot fix, so it is
tested. `tests/check-demo.py` runs the page's own functions under Node, over the four example
documents, and requires the same verdict, the same outcome for every rule, the same disclosure
state for every value, and the same carrier band as `validate_cbom.py`. It also requires that the
interface records the page displays are what the reference adapter extracts from the document each
one names, and that no copy of the rules has come back. It skips itself with a message where Node
is absent, and CI installs Node so that the check is not skipped there.

The two missing documents are now committed as `cbom-disclosure.cyclonedx.json` and
`cbom-noadmin.cyclonedx.json`, evaluable by the reference tool and covered by the suite.

## Rationale

The two halves of the problem are not the same problem and do not have the same fix. Duplicated
*data* should be deleted, because a single copy cannot disagree with itself; that is Option A, and
it is the stronger of the two moves where it applies. Duplicated *logic* cannot be deleted here —
the constraint is that a static page cannot run the reference tool — so the only remaining question
is whether the divergence is visible, which is Option C.

Option B was the position this repository was already in, and the divergence happened anyway. An
honest note about a risk is not a control on it.

Option D would have been defensible. It was rejected because the demonstration carries the part of
the methodology that prose carries worst: that withheld, unknown and undeclared are three
different answers, and that a refusal is not a failure. A reader sees four outcomes on one
interface in one screen. What was wrong was the unchecked claim, not the page.

The cost is a runtime fetch, which a browser blocks for a page opened from the filesystem. That is
a real regression for anyone reading the HTML locally, and it is accepted with the failure made
loud: the page names the file, says why nothing is shown, and gives the command that serves the
site. A silently stale copy is the worse failure, because the reader cannot see it.

## Consequences

- The Demo page is inert without its rules file. A build that fails to publish the rules file
  publishes a visibly broken demonstration rather than a plausible wrong one.
- The Conformance section's two-tools expectation is now exercised on every change, and the demo
  is the second implementation it is exercised against. A future tool requirement could generalise
  this — that a second implementation published alongside a profile is tested against the reference
  — and is deliberately not proposed here: one instance is not evidence for a requirement.
- The test suite depends on Node for one check, and skips that check rather than failing where Node
  is absent. CI installs it. A contributor's green run is therefore not quite the same suite as
  CI's, which is stated in `tests/README.md`.
- Four example documents exist where two did. `cbom-disclosure` is the only document in the
  repository that exercises all four disclosure outcomes at once, which is what T2 forbids
  collapsing.
- Reversing this means restoring a transcription of the rules to the page and deleting the test,
  which puts the page back in the state that produced the divergence. It does not mean deleting the
  two documents: those stand on their own.

## Links

- Settles Q30 in [`../open-questions.md`](../open-questions.md).
- Implemented in `docs/methodology/demo.html`, `docs/methodology/cbom-disclosure.cyclonedx.json`,
  `docs/methodology/cbom-noadmin.cyclonedx.json`, `tests/check-demo.py`,
  `tests/run-profile-tests.sh` and `.github/workflows/profile-tests.yml`.
- Related: [0003](./0003-three-state-disclosure-model.md), which the disclosure document exercises;
  [0013](./0013-monotonicity-covers-constraints.md), whose principle that a rule must be able to
  fail is why this test was checked against deliberate divergences before being trusted;
  [0017](./0017-published-schemas.md), on what a published artifact is for.
