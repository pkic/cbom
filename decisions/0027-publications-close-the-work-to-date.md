# 0027. The publications close the work to date, and the repository is aligned to them

- **Status:** Proposed
- **Date:** 2026-11-16
- **Aspect:** 3.11 — Governing a profile over time
- **Topic / issue:** Release 1: the publications, the website and the examples
- **Deciders:** chair's call, for review by the working group
- **Decision rule applied:** owner call, provisional

## Context

The publications draw a line under the work carried out so far. They record the methodology,
the profiles and the positions as they stand. When they are issued, they move to a separate part
of the PKIC platform and are governed there in a different way. The repository does not edit them
after that.

The repository holds the methodology pages, the rules files, the examples, the policies and
results, the tools and the tests. It continues to evolve after the publications are issued. At the
line, it has to say what the publications say.

An inventory on 16 November 2026 found that the repository does not yet agree with itself, let
alone with the publications:

- **Profile versions** are typed by hand in more than 30 pages, examples and scripts. Two stale
  versions were found: the data-exposure page and two example comments cited Deployment
  Disclosure v0.1.
- **The baseline's rule table** is restated in five places besides its rules file.
- **Result counts**, such as "156 findings" and "29%", are quoted in six pages, and nothing checks
  them against the result files.
- **Positions** are written in the methodology pages, the open-questions register and the decision
  records, in different wordings.
- **Versioning** is described twice: `versioning.html` and `versioning-and-legacy-cboms.md`.

## Options considered

- **Option A — issue the publications and leave the repository as it is.** Trade-off: no work now,
  and the repository starts its next phase already contradicting the record it came from.
- **Option B — align the repository to the publications at the line, then keep one source for each
  kind of content inside the repository.** Trade-off: an alignment pass now, and tooling to keep
  the repository consistent afterwards.
- **Option C — keep the publications and the repository in step permanently.** Trade-off: the
  publications are governed elsewhere, so the repository cannot change them, and every repository
  change would wait on another process.

## Decision

Option B.

**At the line (Release 1).**

1. Every decision taken up to the line is closed. Each decision record changes from Proposed to
   Accepted on the date the publications are issued. A record the publications reject is marked
   Deprecated instead.
2. The open-questions register is closed and kept as history. A question raised after the line
   starts a new register.
3. The methodology pages, rules files, examples, policies, results and tests are aligned with the
   publications. Where the repository and a publication differ, the repository changes. A
   difference that shows the publication is wrong is corrected in the publication before it is
   issued.
4. The repository is tagged `release-1`. The tag is the state that matches the publications.

**After the line.**

The repository is the source of its own content. Each kind of content has exactly one source
inside it, and any other copy is either generated from that source or checked against it by a
test. A copy that is neither is removed.

| Content | Source in the repository | Copies allowed |
|---|---|---|
| Methodology text and positions | The methodology pages | None. A page that needs another page's position links to it. |
| Why a position was taken | The decision records | None. Pages do not cite record numbers. |
| Questions not yet decided | The new register | None. |
| Profile identifier, version, rule ids, levels, withholdability, vocabularies | The rules files (`*.rules.json`) | Generated data for the website. Pages show versions and rule tables from it. |
| Example records and what each one shows | `tools/build_keycloak_examples.py` and `tools/keycloak/source-product-1.7.json` | The example descriptions in `files.html`, checked by a test. |
| Policy results and the counts quoted from them | The result files in `examples/results/` | Quoted counts, checked by a test. |
| Defined terms | `terms.html` | None. Other pages link to the entry. |
| Protocol names | `terms.html`, until a rules file carries the list | None. |
| References | `docs/_data/references.yml` | None. |
| Carrier pin (format and commit) | `tests/schemas/cyclonedx-2.0/` | Quoted in pages, checked by a test. |

A page that describes something the publications state may say which publication and release it
started from. The publications are not changed by later repository work, and the repository does
not copy later changes back into them.

Three repository documents change status:

- `mapping-cyclonedx-spdx.md` stays as the format mapping. Its rule descriptions are generated from
  the rules files.
- `profile-interface-disclosure.md` is retired. Content that is not in the rules file moves to
  `profile.html`.
- `versioning-and-legacy-cboms.md` is merged into `versioning.html`.

## Rationale

The publications are a record of the work, governed elsewhere, so the repository can neither edit
them nor depend on them for its next phase. What the repository can do is start that phase in
agreement with them, and stay consistent with itself afterwards. Facts that a validator reads are
already held in machine-readable files, and any typed copy of them can only drift. A test that
compares a typed copy with its source catches the drift at the next change rather than at the next
review.

## Consequences

- An alignment pass compares each publication section with the pages, rules files and examples
  that describe the same thing, and records every difference and its resolution.
- Before the tag, the working tree is cleaned: outstanding changes committed, finished drafts
  folded into the pages or archived, untracked folders kept or moved out, and the stale `.preview/`
  copy removed.
- Website data files are generated from the rules files. Pages show versions and rule tables from
  that data.
- New tests fail when a page cites a profile version that differs from the rules file, cites a
  `tag#id` that no rules file declares, names an example file that does not exist, quotes a result
  count that differs from the result file, quotes a different carrier pin, or cites a decision or
  question number.
- Record 0025 set a baseline of profiles and examples on 25 October 2026. Release 1 is a different
  thing and is named so that the two are not confused.

## Links

- Record 0025, the October 2026 baseline of profiles and examples.
- Record 0021, one word, one meaning.
