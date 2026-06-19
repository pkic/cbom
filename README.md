# CBOM Profiles Working Group

This repository is the working home of the **PKI Consortium CBOM Profiles Working Group**.
Its purpose is to develop a single deliverable: a **specification for how to create a CBOM
profile** — a vendor-neutral, format-independent methodology that any sector or organisation
can follow, and that maps cleanly onto both CycloneDX and SPDX.

The justification for the work and the aspects to be specified are set out in the scoping
document, *Defining CBOM Profiles* (v0.1). This README is the entry point for contributing.

---

## New here? Read this first

**You do not need to be a software developer, and you do not need to install anything.**
Almost everything a working-group member does happens in the browser, on the GitHub website,
using buttons on the page. The command-line scripts in this repository are only for the one
person who sets it up at the start — see [For maintainers](#for-maintainers-setting-up-the-repository)
right at the end. If you can use a web forum, you can take part fully.

A "repository" (or "repo") is just this shared workspace: a set of files plus the
conversations and decisions attached to them. GitHub gives us a few different places to work,
and the rest of this page explains what each one is for.

---

## A quick tour of the tools we use

GitHub has several features with overlapping-sounding names. Here is what each means **for us**,
in plain terms:

- **Issues** — A numbered to-do item for a *specific question we need to settle*. Each of the
  thirteen aspects of the methodology has one. An issue can be assigned to an owner, labelled,
  discussed in its comments, and "closed" when it's resolved. Think of it as a tracked task.
- **Discussions** — A forum for *open-ended conversation* that isn't yet a single decision —
  strategy, framing, "what do people think about…". Discussions are threaded like a message
  board and don't get "closed"; they just run their course. Use these to think out loud.
- **Comments** — Anyone can reply to an issue or discussion by typing in the box at the bottom
  and clicking the green button. This is how you say your piece.
- **Reactions** — The small 👍 / 👎 / 🎉 emoji buttons on any post or comment. We use them as a
  quick temperature check, *not* as a vote that decides anything.
- **Labels** — Coloured tags on issues (for example `status:deliberating`, `aspect:attribute-model`).
  They let us filter and see at a glance what an item is and where it's up to. Maintainers
  usually manage these; you don't have to.
- **Pull request (PR)** — A *proposed change to the actual specification text*, shown so others
  can review it before it becomes official. You don't need to create these to participate; and
  when the time comes, GitHub lets you propose an edit straight from the browser (it builds the
  pull request for you).
- **Project board** — A single Kanban-style page showing all thirteen issues as cards in
  columns (deliberating, converging, decided), so anyone can see the state of the whole effort
  at a glance.
- **Decision records** — Short plain-text files in the [`/decisions`](./decisions) folder that
  capture *what we decided and why*, once a topic is settled. This is our permanent memory.

> **About Markdown.** The files here (including this one) are written in *Markdown* — ordinary
> text with a few simple formatting marks like `#` for a heading or `-` for a bullet. You do
> **not** need to learn it to comment or take part; the comment box even has formatting buttons.

---

## How we work

We keep three things deliberately separate, because the most common failure on GitHub is a
decision getting lost inside a long comment thread that nobody can find later:

| | Where it lives | What it is |
|---|---|---|
| **Deliberation** | a Discussion or an Issue | the open argument — options, trade-offs, questions |
| **Decision** | a record in [`/decisions`](./decisions) | the agreed outcome, with the reasoning |
| **Artifact** | the spec text, changed via a pull request | the words that actually ship |

A topic moves through four stages, shown by its `status:` label:

**Raised → Deliberating → Converging → Decided**

Open exploration starts as a **Discussion**. Once a topic narrows to a concrete choice, it
becomes (or is captured as) an **Issue**, which can then be closed and linked to the change
that implements it. The full lifecycle, the decision rule (we use *lazy consensus* — silence
means assent after a notice period), and who does what are all explained in plain language in
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

> **Format note (for editors).** The working draft of the specification is kept in Markdown so
> that changes can be reviewed line-by-line. Word and PDF versions are generated only for
> publication. This mirrors how CycloneDX and SPDX run their specifications.

---

## What you'll actually do — common tasks

All of these are done in the browser at github.com, signed in with your GitHub account. No
software to install.

**Catch up on a topic.** Open the **Issues** tab (for the thirteen aspects) or the
**Discussions** tab (for open-ended threads), click the one you care about, and read from the
top. The first post states the question; the comments are the conversation so far.

**Weigh in.** Scroll to the bottom of any issue or discussion, type in the comment box, and
click the green **Comment** button. To signal quick agreement without writing, click a
reaction emoji on the relevant post.

**Raise a new topic.** Decide which fits:
- a *specific question to settle* → **Issues** tab → **New issue** → choose the
  "Aspect topic" template, which prompts you for the right details.
- an *open-ended conversation* → **Discussions** tab → **New discussion**.
If you're not sure, start a Discussion; it can become an Issue later. Before opening one, glance
at the table below so you don't start a second thread on something already being tracked.

**See what's been decided.** Open the [`/decisions`](./decisions) folder. Each file is one
decision, written in short sections (context, options, decision, rationale). The
[decisions index](./decisions/README.md) lists them.

**Edit the specification (optional, later).** When there's draft text to improve, open the file
under `spec/`, click the pencil ✏️ icon, make your change, and click **Propose changes** —
GitHub turns it into a pull request for others to review. You never touch a command line.

---

## The thirteen aspects

These are the building blocks of the methodology, taken from Section 3 of the scoping document.
Each has **one** canonical issue tracking it — please don't open a second thread for the same
aspect. The issue number, current status, and owner are filled in as they're assigned (a
maintainer running the setup script populates these).

| § | Aspect | Tracking issue | Status | Owner |
|---|---|---|---|---|
| 3.1 | Profile objective & scope | #4 | Deliberating | _unassigned_ |
| 3.2 | Profile identity & metadata | #5 | Deliberating | _unassigned_ |
| 3.3 | Format-independent attribute model | #1 | Deliberating | _unassigned_ |
| 3.4 | Obligation levels & conformance semantics | #6 | Deliberating | _unassigned_ |
| 3.5 | Conformance & validation | #7 | Deliberating | _unassigned_ |
| 3.6 | Mapping to serialization formats (CycloneDX, SPDX) | #2 | Deliberating | _unassigned_ |
| 3.7 | Vocabularies & normalisation | #3 | Deliberating | _unassigned_ |
| 3.8 | Relationship to SBOM / HBOM & layering | #8 | Deliberating | _unassigned_ |
| 3.9 | Extensibility & profile composition | #9 | Deliberating | _unassigned_ |
| 3.10 | Forward-looking / roadmap information | #10 | Deliberating | _unassigned_ |
| 3.11 | Profile governance & lifecycle | #11 | Deliberating | _unassigned_ |
| 3.12 | Regulatory & policy alignment | #12 | Deliberating | _unassigned_ |
| 3.13 | Templates, worked examples & tooling | #13 | Deliberating | _unassigned_ |

To read the table: **§** is the section number in the scoping document; **Tracking issue** is
the GitHub issue where that aspect is discussed (click the number to jump to it); **Status**
shows how far along it is; **Owner** is the person shepherding it.

### Sequencing — what to tackle first

- **Start with 3.3 (the attribute model).** Most other aspects build on it, so settling it
  first avoids rework.
- **Treat 3.6 (format mapping) and 3.7 (normalisation) as cross-cutting.** Rather than
  re-arguing them inside every other topic, we discuss them in their own issues and *link* to
  those. (Typing an issue number like `#12` in a comment automatically creates a link.)
- **3.10 (roadmap) mainly concerns migration-oriented profiles.** Topics that touch it carry an
  `orientation:` label so the connection stays visible.

The **Project board** shows all thirteen at once, so you can see what's stuck, converging, or
decided without opening each one.

---

## Repository layout

A map of what's in here. As a participating member you'll mostly use the GitHub *tabs*
(Issues, Discussions) rather than these files directly — but here's what each is:

```
.
├── README.md                       # you are here — the start-here guide
├── CONTRIBUTING.md                 # how a topic moves from raised to decided (plain language)
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── aspect-topic.md          # the form you fill in when raising a topic
│   │   └── config.yml               # points the "new issue" page at Discussions too
│   └── CODEOWNERS                   # who gets asked to review changes to each spec section
├── decisions/
│   ├── README.md                    # index of decisions taken
│   └── 0000-template.md             # the blank form for recording a new decision
├── labels/
│   ├── labels.yml                   # the list of labels (for setup)
│   └── create-labels.sh             # one-time script that creates the labels
├── docs/
│   └── tracking-issues.md           # the pre-written text of the thirteen issues
└── spec/                            # (to be created) the methodology draft, in Markdown
```

---

## For maintainers: setting up the repository

**Skip this section unless you are the person doing the initial setup.** These steps use the
[GitHub CLI](https://cli.github.com/) (`gh`) from a command line and only need to be run once,
to populate an empty repository. Ordinary members never need them.

1. **Enable Discussions:** on GitHub, go to **Settings → General → Features** and tick
   **Discussions**.
2. **Create the labels:** `bash labels/create-labels.sh` (or `REPO=owner/name bash labels/create-labels.sh`).
3. **Create the thirteen issues:** `REPO=owner/name bash create-issues.sh` — this also wires up
   the cross-references between them. Run with `DRY_RUN=1` first to preview.
4. **Seed the discussion topics:** `REPO=owner/name bash seed-discussions.sh`.
5. **Update the table above** with the issue numbers the scripts report, and assign owners.

Each script checks that `gh` is installed and that you're signed in, and supports `DRY_RUN=1`
to show what it would do without changing anything.

---

### Where to get help

If anything here is unclear, open a Discussion in the **General** category and ask — that's
exactly what it's for. No question is too basic.
