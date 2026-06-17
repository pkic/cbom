# CBOM Profiles Working Group

This repository is the working home of the **PKI Consortium CBOM Profiles Working Group**.
Its purpose is to develop a single deliverable: a **specification for how to create a CBOM
profile** — a vendor-neutral, format-independent methodology that any sector or organisation
can follow, and that maps cleanly onto both CycloneDX and SPDX.

The justification for the work and the aspects to be specified are set out in the scoping
document, *Defining CBOM Profiles* (v0.1). This README is the entry point for contributing
to it.

---

## How we work (the short version)

We keep three things deliberately separate:

| | Where it lives | Purpose |
|---|---|---|
| **Deliberation** | a Discussion or Issue per topic | the open argument — options, trade-offs, questions |
| **Decision** | a record in [`/decisions`](./decisions) | the recorded outcome, with rationale |
| **Artifact** | the spec text, via pull request | the words that ship |

A topic moves **Raised → Deliberating → Converging → Decided**. The full lifecycle, the
decision rule, and roles are in [`CONTRIBUTING.md`](./CONTRIBUTING.md).

Open exploration happens in **Discussions**. Once a topic narrows to a concrete choice, it
becomes an **Issue** (assignable, closeable, links to the PR that lands the change). Every
topic uses the [aspect topic template](./.github/ISSUE_TEMPLATE/aspect-topic.md) so all
thirteen are argued on the same terms.

> **Format note.** The working draft of the specification is maintained in **Markdown** so it
> diffs and reviews line-by-line on GitHub. Word/PDF are generated for publication only. This
> is the same convention CycloneDX and SPDX follow.

---

## The thirteen aspects

Each aspect from Section 3 of the scoping document has **one** canonical tracking item. Fill
in the issue number and owner as they are created; do not open parallel threads for the same
aspect.

| § | Aspect | Tracking issue | Status | Owner |
|---|---|---|---|---|
| 3.1 | Profile objective & scope | `#4` | _tbd_ | _tbd_ |
| 3.2 | Profile identity & metadata | `#5` | _tbd_ | _tbd_ |
| 3.3 | Format-independent attribute model | `#1` | _tbd_ | _tbd_ |
| 3.4 | Obligation levels & conformance semantics | `#6` | _tbd_ | _tbd_ |
| 3.5 | Conformance & validation | `#7` | _tbd_ | _tbd_ |
| 3.6 | Mapping to serialization formats (CycloneDX, SPDX) | `#2` | _tbd_ | _tbd_ |
| 3.7 | Vocabularies & normalisation | `#3` | _tbd_ | _tbd_ |
| 3.8 | Relationship to SBOM / HBOM & layering | `#8` | _tbd_ | _tbd_ |
| 3.9 | Extensibility & profile composition | `#9` | _tbd_ | _tbd_ |
| 3.10 | Forward-looking / roadmap information | `#10` | _tbd_ | _tbd_ |
| 3.11 | Profile governance & lifecycle | `#11` | _tbd_ | _tbd_ |
| 3.12 | Regulatory & policy alignment | `#12` | _tbd_ | _tbd_ |
| 3.13 | Templates, worked examples & tooling | `#13` | _tbd_ | _tbd_ |

### Sequencing

- **Start with 3.3 (attribute model).** Most other aspects select from or constrain it; settling
  it first prevents rework.
- **Treat 3.6 (format mapping) and 3.7 (normalisation) as cross-cutting.** Open them as issues
  that the per-aspect threads *reference* (GitHub auto-links the mentions) rather than
  re-debating mapping or vocabulary inside each topic.
- **3.10 (roadmap) applies mainly to migration-oriented profiles.** Tag topics with
  `orientation:*` so this dependency stays visible.

A **Project board** across all thirteen issues gives the at-a-glance view of what is stuck,
converging, or decided.

---

## Repository layout

```
.
├── README.md                       # you are here — start-here index
├── CONTRIBUTING.md                 # how a topic moves from raised to decided
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── aspect-topic.md          # the standard topic template
│   │   └── config.yml               # routes open-ended threads to Discussions
│   └── CODEOWNERS                   # aspect owners (review routing)
├── decisions/
│   ├── README.md                    # index of decision records
│   └── 0000-template.md             # decision-record template (copy to start one)
├── labels/
│   ├── labels.yml                   # the label scheme
│   └── create-labels.sh             # applies the scheme via the gh CLI
└── spec/                            # (to be created) the methodology draft, in Markdown
```
