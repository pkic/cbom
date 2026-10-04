# Poll: format of the December workshop

The first working-group poll, run with the "Open WG poll" workflow. The issue below is the poll:
its title and body become the poll's title and description, so the body is written for members
who will read it on the voting page and never open GitHub.

## 1. Open this issue

**Title**

```
Poll: how should we use the two-hour workshop at the PKI Consortium conference?
```

**Body**

```markdown
The working group has a two-hour workshop at the PKI Consortium conference in Amsterdam in
December. This poll chooses its format. Pick the one you would most like to run.

The audience is mixed: PKI and security practitioners, vendors, operators and some regulators.
Most have not written a CBOM profile. Each format is a full two hours.

**A. Hands-on lab: "One CBOM, three readers."** Participants run the browser demo against the
Keycloak CBOM under three profiles and fix a document until it conforms. They leave knowing what a
profile does, having seen it work. Risk: it needs laptops, and it needs validator features that
are not built yet.

**B. Design studio: "Write a profile in an afternoon."** Tables each take a proposed use case (OT,
PKI estate, code signing, data exposure) from decision to questions to required facts, on cards.
Each table reports back. They leave with draft use cases for our register, and we gain
contributors. Risk: quality varies by table.

**C. Structured debate with live polling.** Four open questions from our decision backlog, each
with a short case for each side, a few minutes from the floor and a live temperature poll. They
leave seeing the questions as real. Risk: conference votes are not working-group votes and must
be treated as advisory.

**D. Tabletop exercise: "Your supplier sent a CBOM. Now what?"** Teams play the migration team
of a fictional grid operator. They plan from three supplier CBOMs of very different depth, log
every question the documents cannot answer, and map those gaps onto profile requirements on a
wall. They discover why profiles matter instead of being told. No laptops. Risk: it needs the
most preparation. A full draft pack exists: https://github.com/pkic/cbom/tree/main/drafts/workshop-2026-12

**Hybrid.** A 15-minute live demo by a presenter, the tabletop from D (shortened), and a short
live poll at the end. Less hands-on time than D, and it still needs the validator features for the
demo.

The result goes to the next meeting. The chosen format gets a timed dry run with working-group
members in mid-November.
```

## 2. Run the workflow

Actions → **Open WG poll** → Run workflow:

| Input | Value |
|---|---|
| `issue` | the number of the issue above |
| `options` | `A: hands-on lab \| B: design studio \| C: debate with live polling \| D: tabletop exercise \| Hybrid: demo, tabletop and poll \| Abstain` |
| `days` | `14` |
| `multi_select` | `false` |
| `publish_results` | `false` for a first trial. The result is reported at the meeting and recorded in `polls.yml` |

The poll service comments on the issue with the voting link. Send that link to the mailing list
(cbom@lists.pkic.org) with the closing date, for members who do not follow GitHub.

## 3. Record it

`docs/_data/polls.yml` carries the entry `workshop-format`, unpublished. Once the poll is open:

- If the voting link is one public link, set `access: open`, add `url:` with the link, and set
  `published: true`.
- If the service issues personal links, keep `access: single-use`, add no `url`, and set
  `published: true`.
- Set `issue:` to the issue number and correct `opens` and `closes` to the dates the service
  reports.

After it closes, add `result` with the counts and a one-sentence outcome, as for any poll.

## Why one question

The workflow asks one question per issue. That suits a first trial: one decision, one set of
options, nothing to misread. The follow-up questions can each be a short poll of their own once
this has shown how the service behaves. They are how many attendees to plan for, whether laptops
can be assumed, and who facilitates.
