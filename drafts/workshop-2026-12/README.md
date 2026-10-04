# Workshop: "Your supplier sent a CBOM. Now what?"

Facilitator guide for the two-hour working-group workshop at the PKI Consortium conference,
December 2026. Format D from the options discussed in October: a tabletop exercise. Draft for the
working group.

| File | For | Contents |
|---|---|---|
| `README.md` | Facilitators | Purpose, room, running order, script, capture, preparation |
| `scenario.md` | Every participant | The company, the task, the three supplier CBOMs, the plan sheet |
| `cards.md` | Printing | Role cards, inject cards, gap card, wall layout |
| `answer-key.md` | Facilitators only | The gaps teams should find, and where each lands in the methodology |

## Purpose

Participants act as the migration team of a grid operator that has to plan its post-quantum
migration. Three suppliers have sent CBOMs of very different depth. Teams build a plan and log every
question the documents cannot answer. Then the whole room maps those gaps onto profile requirements.

The value of profiles is discovered, not explained. Teams reach for capability, blockers and
enablement on their own, because the plan cannot be written without them.

**Participants leave with:**

- The difference between an inventory ("what is used") and what a plan needs ("what could be used,
  what blocks it, what changing it costs").
- Why a buyer has to name a profile when asking for a CBOM, and what each kind of profile adds.
- The four use-case groups, met through their own gaps rather than through a slide.
- A way into the working group.

**The working group leaves with:**

- A wall of gaps from practitioners, mapped to existing, draft and missing requirements.
- Temperature readings on two or three open questions.
- Names of people willing to continue.

## Audience and room

- **Expected:** PKI and security practitioners, vendors, operators, some regulators. Most have not
  written a profile. No laptops needed. Everything is on paper.
- **Teams:** five or six people at a table, up to six tables (about 36 people). Each team needs one
  set of handouts and one stack of blank gap cards.
- **Scaling:**
  - Above 40 people, add tables and give two people the same role.
  - Below 15, run one team in plenary, with the facilitators playing the missing roles.
- **Facilitators:** one lead, plus one floater for every two tables. Floaters deliver the inject
  cards, keep teams on the plan and not on algorithm detail, and help place cards on the wall.
- **Wall:** one large wall or two flipchart stands, laid out as in `cards.md`. Painter's tape for
  the grid, and markers.

## Running order

| Time | Segment | Who | Notes |
|---|---|---|---|
| 0:00–0:05 | Welcome and why | Lead | Two sentences on the working group. The question of the day: "Could you plan your migration from what your suppliers send you?" |
| 0:05–0:15 | Briefing | Lead | Walk through `scenario.md`: the company, the board's request, the three documents, the plan sheet. Hand out role cards. Teams pick a migration lead |
| 0:15–1:15 | Tabletop | Teams | Build the plan, one system at a time. Every unanswerable question goes on a gap card. Four inject cards arrive at 0:30, 0:45, 0:55 and 1:05 |
| 1:15–1:45 | Mapping wall | Everyone | Each team places its gap cards. The lead walks the wall column by column and reveals where each gap lands (`answer-key.md`) |
| 1:45–1:55 | Debrief and temperature poll | Lead | Three teams each report one decision they could not make, and why. Then a three-question poll on an open link |
| 1:55–2:00 | Close | Lead | What happens to the wall, how to join, the next meeting date |

## Script

### 0:00 Welcome (5 min)

> We are the PKI Consortium CBOM Profiles Working Group. We do not write a new format. We write
> profiles: the rules that say which cryptographic facts a CBOM must carry for a particular decision.
> Today you will find out for yourselves why that matters. You are the migration team of a grid
> operator. Your suppliers have sent you CBOMs. Your board wants a plan.

No slides on the methodology. One slide with the question of the day, one with the running order.

### 0:05 Briefing (10 min)

- Read the first page of `scenario.md` aloud. Spend under two minutes on the company.
- Show the three documents side by side on screen. Say only that they differ in depth, not how.
  Teams find out.
- Explain the plan sheet. There are six actions per system: enable now, software update, replace,
  shield, accept and revisit, escalate to the supplier.
- Explain gap cards. One question per card. Say which document it concerns, who could answer it,
  and whether it blocks a decision. Ask for at least five cards per team.
- Hand out role cards. Each role has a private worry that surfaces during the hour.

### 0:15 Tabletop (60 min)

**Suggested pace:**

| Minutes | System |
|---|---|
| 0:15–0:35 | Identity: Keycloak, document A |
| 0:35–0:50 | Customer portal edge: nginx, document B |
| 0:50–1:10 | Substations: protection relay, document C |
| 1:10–1:15 | Priorities across the three |

**Injects:** floaters deliver the four cards to every table at the same time.

| Time | Inject | Pulls in |
|---|---|---|
| 0:30 | **Advisory**: an OpenSSL key-exchange flaw | Disclosure: the implementing library, and withholding |
| 0:45 | **Regulator**: data that must stay confidential beyond 2035 | Operation: facts only the operator knows |
| 0:55 | **Supplier slip**: the JOSE signature standard is late | Change planning: blockers make a plan robust |
| 1:05 | **Auditor**: prove these are the documents the suppliers issued | Assurance: provenance and freshness |

**Floater prompts, if a team stalls or drifts:**

- "Which action are you choosing for this interface? What would you need to know to choose
  another?"
- "Is that a question for the supplier, for you, or for a standards body? Write it on a card."
- If a team debates algorithm strength: "The plan does not need the security proof. What does it
  need?"
- If a team has no cards after 20 minutes: "What did document B not tell you that document A did?"

### 1:15 Mapping wall (30 min)

- **Teams place their cards (10 min).** Columns are the four use-case groups. Rows say whether a
  profile already requires the fact, a draft profile requires it, or no profile does yet. A fifth
  bin holds questions that are not CBOM questions, such as budget and staffing. Teams guess the
  placement. Duplicates go on top of each other, because a tall stack is a finding.
- **The lead walks the wall (20 min).**
  - Column by column, move misplaced cards using `answer-key.md`.
  - At each column, name the group in one sentence and the profile or draft that covers the row.
  - Point out the tallest stacks.
  - End on the "no profile yet" row, which is the working group's to-do list.

### 1:45 Debrief and poll (10 min)

- Ask three teams for one decision they could not make, and the gap that stopped them.
- Run the poll on an open Formbricks link, shown as a QR code. State plainly that it is a
  temperature reading for the working group, not a vote. The questions are in `cards.md`.

### 1:55 Close (5 min)

- The wall will be transcribed into a GitHub issue and into the decision backlog within a week.
- How to join: the mailing list, the meetings page, and that GitHub is optional.
- Collect names and emails of people who want to continue on a sign-up sheet.

## Capture

During the session:

- Photograph the wall twice: before the walk, and after the cards are moved.
- Collect every gap card.

After the session:

- Transcribe the cards into one issue, "Workshop gaps, December 2026". Record team, document,
  question, final placement and stack size.
- Add each gap in the "no profile yet" row to `drafts/decision-backlog/` as input to its cluster.
  Add any gap that names a new consumer and decision to the use-case register as *proposed*.
- Record the poll in `docs/_data/polls.yml` as an `open` poll with its result.
- Write a one-paragraph summary for the meeting page.

## Preparation

| By | Task | Owner |
|---|---|---|
| End of October | Agree the format and this draft at a working-group meeting | Chair |
| Mid-November | Close the "to verify" items in the Keycloak example, since document A quotes it. Settle the illustrative relay values against the substation draft | Example owners |
| Mid-November | Dry run with working-group members as players, timed. Adjust the injects and the pace | Lead facilitator |
| Late November | Print handouts (one `scenario.md` per person, one card set per table), wall headers and the sign-up sheet. Create the open poll in Formbricks and its QR code | Facilitators |
| Week before | Brief the floaters on `answer-key.md` | Lead facilitator |

**Materials per table:**

- six scenario packs;
- one set of role cards;
- four inject cards in sealed envelopes, marked with times;
- thirty blank gap cards;
- markers.

**For the room:** wall headers, tape, a projector for the three documents, the poll QR code, and
the sign-up sheet.

## Risks

| Risk | Mitigation |
|---|---|
| Teams dive into algorithm strength | Floater prompt: what does the plan need, not the proof |
| The tabletop overruns into the wall | The lead calls time at 1:15 regardless. Unfinished systems still produce cards |
| One expert dominates a table | Role cards spread the questions. The migration lead role goes to someone else |
| The answer key reads as "the working group already solved this" | Lead the walk with the "no profile yet" row as the point of the day, not a footnote |
| Draft attributes change before December | Document A quotes the draft profiles. Recheck at the dry run |
| Poll read as a decision | Say so twice, and record it in `polls.yml` as advisory |
