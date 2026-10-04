# Review: how the website presents use cases

Working note, 4 October 2026. Reviews the Use Cases section and the methodology's Use Cases page
as merged in #65. The first set of changes is made on the branch `use-case-section-intro`. The
rest is listed under "Phase 2".

## Verdict

The section is right in substance and hard to read. Four things cause most of the difficulty:

- **The overview page does six jobs.** A visitor reads about 1,600 words before reaching the list
  of use cases. In order, the page explains the eight-part shape, the grouping theory, the status
  definitions (twice), the register, the "applying a profile" entries, why worked examples are
  kept out of the methodology, and how to propose one.
- **Working-group vocabulary reaches the reader before the content does.** The first screen uses
  "baseline", "orientation `inventory`", "change core", "C1 to C17", "Q64", "Q66" and "draft
  decision 0023". These are the right terms for a working-group member reviewing a draft. They
  mean nothing to someone arriving to see what a CBOM profile is for.
- **The split from the methodology is still blurred.** The methodology's Use Cases page sits under
  "Start here" and lists all sixteen entries. The "one document, many consumers" point is made
  three times: on the methodology page, the overview and the group pages. The overview also
  carries a section explaining why it is not in the methodology.
- **Pages that claim one shape have four.** The overview says every worked page follows the same
  eight parts, in the same order. Only IoT does:

  | Page | Structure |
  |---|---|
  | PQC migration | Its own headings, unnumbered |
  | IoT | The eight numbered parts, after a preamble that is now out of date |
  | Substation | Eight parts with different titles, plus "Choice of case" and "Sources" |
  | Procurement | A demonstration of reuse, in five unrelated sections |

## Findings

### 1. The overview page

| Problem | Effect | Change |
|---|---|---|
| The register is the fourth section | Readers who want to know "what use cases are there" scroll past theory | Register second, straight after a short introduction |
| The eight-part shape opens the page | It is guidance for authors, not for readers | Move it to a "Proposing a use case" page |
| Status definitions appear twice, with "developed" defined both times | Repetition, and two slightly different wordings | One definition, on the proposing page; one line under the register |
| The state column mixes status and blockers ("Described. Blocked on Q57") | Open questions read as status | Status only. Blockers go on the group page entry |
| The tag "1 developed · 3 drafted · 11 described or placeholder" | Precise and unreadable | Remove. The register shows it |
| "Why the methodology keeps only the argument" | A governance rationale shown to every visitor | Move to the proposing page, shortened |
| Closing banner "One document, many consumers" | Third copy of the same point | Remove. The methodology page owns it |

### 2. Terms used for the same thing

The pages use "purpose", "use case", "catalogue entry", "worked use case" and "worked example"
interchangeably. They also use "described", "placeholder", "drafted" and "developed" without a
reader-facing explanation.

**Proposed terms, used everywhere:**

| Term | Meaning |
|---|---|
| **Use case** | A consumer and the decision it has to make |
| **Profile** | The rules that say which facts a CBOM must carry for that decision |
| **Worked example** | A use case taken through to a profile, applied to a real product, with a conforming and a non-conforming document |

"Purpose" and "catalogue entry" are retired from the use-case pages.

**Status, four values:**

| Status | Meaning |
|---|---|
| Worked example | A profile that passes C1 to C17, plus conforming and non-conforming documents |
| Draft worked example | Written in the worked-example shape, but rules or verdicts are not yet settled |
| Described | Consumer, decision and what the profile would need are written |
| Proposed | Consumer and decision named, nothing more |

### 3. Numbers

Catalogue numbers 1 to 16 were kept as identifiers when entries moved. In the register they now
read as a sequence with a gap: 5 moved to "Applying a profile". They carry no meaning for a
reader. The anchors (`#procurement`, `#iot`) are the real identifiers and are what other pages
link to.

**Change:**

- Drop the numbers from the register and the group pages.
- Keep them only in the redirect list on the methodology page, so that anyone holding an old
  reference ("purpose 9") can find the entry.

### 4. Names

- **The OT use case is not findable by the word "OT".** List it as "Substation automation (OT)" in
  the register and on its group page.
- **"PQC migration" appears under three names:** "PQC migration readiness and planning" (the
  catalogue heading), "PQC Migration" (navigation) and "PQC migration" (register). Use "PQC
  migration" everywhere.
- **"Disclosure" and "Change planning" are working-group terms.** They are kept, because draft 0023
  defines them. Each is introduced on the overview by what it means to a reader: *know what a
  product uses* and *decide how to change it*. Renaming "change planning" to "migration planning"
  would read better. It is an open choice for the group, not made here.

### 5. Methodology and use cases: where each thing lives

| Content | Today | Should be |
|---|---|---|
| What a use case is, and why a profile starts from one | Methodology page | Methodology page (kept) |
| One document serving several profiles, and the limit | Methodology page, overview banner, group pages | Methodology page only. Group pages state their own consequence in one sentence |
| Selecting facts versus adding facts | Methodology "Two kinds of profile", overview, group pages | Methodology states the distinction. The section uses it to group |
| List of all use cases | Methodology redirect list, overview register | Overview register only. Methodology keeps a small redirect line for old anchors |
| Eight-part shape of a worked example | Overview | Proposing page |
| Why worked examples are not in the methodology | Overview | Proposing page, short |
| The nginx example | Methodology throughout | Methodology (kept). It illustrates concepts. Keycloak is the worked example. Both sections say so |

**The methodology's page moves and is renamed.** It sits under "Start here" next to the
Introduction and Demo, which presents it as an entry point. It is now a concept page. Retitle it
"Starting from a Use Case" and move it to "Applying it", before Method. That is where the procedure
that begins with a use case is described.

### 6. Version mismatch between the two sections

The methodology describes the published profiles: baseline v0.7 and PQC migration v0.6, with the
nginx and gateway examples. The use-case pages describe the draft 0022 profiles: baseline v0.8,
PQC migration v0.7 and the extended depth, with Keycloak. A reader moving between sections sees
two "current" migration profiles and is not told why.

**Change:**

- The overview states it in one sentence.
- Each draft worked example says it in its status line.
- The mismatch ends when 0022 is promoted. That is a separate change, listed in
  `drafts/pqc-migration-depths/README.md`.

### 7. Worked example pages (Phase 2)

- **Give every worked example the same opening block, "At a glance":** consumer; decision; subject
  type; group; product used; profiles and versions; example documents; status.
- **Use the eight numbered parts on every page, with the template's titles.** PQC migration keeps
  its content but gains the numbering. Substation drops "Choice of case" into part 1. Procurement
  is rewritten into the eight parts, most of which are short because the profile only tightens.
- **Collect working-group material at the end, under "Status for the working group".** That means
  draft decision numbers, Q-numbers, `drafts/` paths, evaluator gaps and to-verify lists. It stays
  visible, but it no longer interrupts the reading.
- **IoT's preamble "Why IoT is not yet a use case" is out of date.** It says every other entry
  names a consumer and a decision and IoT does not. That reads oddly now that the page develops
  one. Retitle it "Choosing the decision" (done on the branch).

### 8. Group pages (Phase 2)

- **Turn each use case into a uniform entry.** Use labelled lines (consumer, decision, subject,
  what the profile needs, status, open issues) instead of two to three paragraphs of free prose.
  Keep the prose as a short note under them.
- **Fold the emphasis tables into those entries.** The ●/○ tables compare different columns on
  the two pages and are the least-read content in the section. "What the profile needs" is the
  same information, stated per use case.
- **Move the profile tree on the change-planning page into a diagram.** It is shown as
  preformatted text today, and the existing site diagrams show the same kind of relation as SVG.

## Changes made on `use-case-section-intro`

| File | Change |
|---|---|
| `docs/use-cases/index.html` | Rewritten. A short introduction, three kinds of page, the two groups in reader terms, the register with plain status values and a "who decides what" column, "not use cases", how the section relates to the methodology, and the version note. About 700 words, down from about 1,600 |
| `docs/use-cases/proposing.html` | New. The eight-part shape, the status definitions, how to propose a use case, and why worked examples are kept out of the methodology |
| `docs/use-cases/disclosure.html`, `change-planning.html` | Catalogue numbers removed from headings. The banner about numbers removed. The OT name added |
| `docs/use-cases/iot.html` | The out-of-date preamble retitled and its first sentence corrected |
| `docs/methodology/use-cases.html` | Rewritten as "Starting from a use case": what a use case is, why it comes first, one document and several profiles with the limit, and where the use cases are. The full list is replaced by a one-line redirect for the old anchors |
| `docs/_data/methodology_nav.yml` | The page moves from "Start here" to "Applying it", before Method, retitled. The pointer to the other section reads "Use cases". Footers regenerated with `tools/renumber-pagenav.py` |
| `docs/_data/usecases_nav.yml` | "Writing one" holds "Proposing a use case" and "Template" |
| `docs/use-cases/template.html` | Links to the proposing page for the shape and states |

## Proposed overview text

The text as committed, for review outside the HTML:

> **Use cases**
>
> A CBOM profile is written for someone who has a decision to make. A use case names that person
> and that decision: a buyer comparing tenders, a responder tracing an advisory, a grid operator
> planning a migration. This section collects the use cases the working group has identified, and
> takes the most developed of them through to a profile, a real product and documents that can be
> checked.
>
> **Two groups**
>
> Use cases fall into two groups. The difference matters most to whoever has to produce the CBOM.
>
> *Disclosure: know what a product uses.* The profile chooses which facts a CBOM must carry from
> the set every CBOM already describes: interfaces, protocols, algorithms and the libraries that
> implement them. One CBOM from a supplier can answer every profile in this group.
>
> *Change planning: decide how to change it.* The profile adds facts a basic CBOM does not have:
> what each interface could support, what is blocking it, and what changing it costs. A supplier
> has to produce a richer CBOM. That CBOM then answers the disclosure profiles as well.

## Phase 2, in order

1. "At a glance" blocks and the uniform eight parts on the four worked examples.
2. Uniform entries on the group pages, replacing the emphasis tables.
3. Promote the 0022 drafts, which removes the version note.
4. Decide whether "change planning" becomes "migration planning".
