# docs/

The published site for the PKI Consortium CBOM Profiles Working Group, served by GitHub Pages
at <https://pkic.github.io/cbom/>. This file is excluded from the build and is here for
contributors.

The folder holds two things that are built differently.

## 1. The working group site (Jekyll)

Data-driven pages built by Jekyll from Markdown and Liquid templates.

| Path | Purpose |
|---|---|
| `_config.yml` | Site settings. `baseurl` must stay `/cbom` so `relative_url` resolves correctly. |
| `index.md` | Overview and landing page. |
| `references.md` | The reference register, rendered from `_data/references.yml`. |
| `tooling.md` | The tooling registry, rendered from `_data/tooling.yml`. |
| `issues.md` | The methodology aspects. |
| `meetings.md` | Meetings, rendered from `_data/meetings.yml`. |
| `presentations.md` | Presentations, rendered from `_data/presentations.yml`. |
| `contributing.md` | How to take part. |
| `_data/references.yml` | Reference sources, with category, status and jurisdiction. |
| `_data/tooling.yml` | Tools that work with CBOMs, with what they do and where they say so. |
| `_data/aspects.yml` | The methodology aspects. |
| `_data/meetings.yml` | Meetings, their agendas and their recordings. |
| `_data/presentations.yml` | Presentations, and where each deck is held. |
| `_layouts/`, `_includes/` | Page shells and the shared header and footer. |
| `assets/css/style.css` | The design system: palette, typography, components. |
| `assets/js/references.js` | Filtering for the reference register. |
| `assets/js/tooling.js` | Filtering and grouping for the tooling registry. |
| `assets/js/presentations.js` | Search and grouping for the presentations page. |
| `assets/presentations/` | Presentation files served at `/cbom/assets/presentations/`. |

To add a reference or an aspect, edit the relevant file in `_data/`. Adding a new value for a
category, status or jurisdiction also needs a display label adding under `labels:` in
`_config.yml`.

Meetings and presentations work the same way and are documented in
[CONTRIBUTING-meetings.md](../CONTRIBUTING-meetings.md). Two things about them are worth knowing
here. A meeting is Upcoming or Previous according to its `date`, worked out **at build time**, so
the split only moves when the site is rebuilt — in practice the push that adds the recording. And
a presentation's file size field is called `filesize`, not `size`, because `size` is a reserved
Liquid property that would render the number of fields on any entry lacking the key.

`python3 tests/check-site-data.py` checks both files: that a download link points at a file that
is actually committed, that a presentation's `meeting:` matches a real meeting, and that an entry
has exactly one of `file:` and `url:`. Jekyll fails on none of these — it builds the broken link
and serves it.

The tooling registry is documented in [CONTRIBUTING-tooling.md](../CONTRIBUTING-tooling.md). Its
admission rule is that a tool's maintainer states CBOM support in their own material, and each
entry links to that statement. The same checker validates it: every value in `functions`,
`methods`, `licensing` and `status` must have a label in `_config.yml`, or the page renders a blank
where the label should be.

## 2. The methodology documentation (static HTML)

`methodology/` holds the working draft of the methodology, explained against a worked example:
an nginx web server, its CBOM in CycloneDX 1.7, evaluated against a small product-independent
profile. The pages are hand-written HTML served at `/cbom/methodology/`. Each carries a two-line
front matter block so that Jekyll processes it, which is what allows the shared navigation
include to work. No layout is applied, so each page still controls its own markup.

### Previewing locally

Because of that front matter and the navigation include, opening a page straight from the
filesystem shows the front matter as text and no navigation. Two ways to see the real thing:

| | Command | Covers |
|---|---|---|
| **Full site** | `bundle install` then `bundle exec jekyll serve --source docs` | Everything, at the versions GitHub Pages builds with. Use this before publishing. |
| **Methodology pages only** | `python3 tools/preview.py` | The twenty HTML sections, served on `localhost:8000`. No Ruby, no install. Skips the Markdown pages and layouts. |

`tools/preview.py` does only what Jekyll does to these particular pages — strips the front
matter and expands the one navigation include — and warns rather than guessing if a page grows
Liquid it does not handle. Re-run it after editing; it does not watch for changes.

### Navigation

The section navigation lives in one place and is rendered into every page.

| Path | Purpose |
|---|---|
| `_data/methodology_nav.yml` | The list of sections, in groups, in reading order. The single source of truth. |
| `_includes/methodology-nav.html` | Renders the list. Marks the current page from its `nav:` front matter value. |
| `methodology/styles.css` | Styling, under "section navigation". A left rail at 1100px and above, a grouped block above the content below that. |

**Adding a section** means: create the page with `nav: <id>` in its front matter, wrap its body in
`<div class="shell">` with `{% include methodology-nav.html %}` before `<main>`, add one line to
`_data/methodology_nav.yml`, then run `python3 tools/renumber-pagenav.py` from the repository
root. The same applies to reordering: the sidebar comes from the data file, but the previous and
next links at the foot of each page are written into the pages themselves, and the script is what
keeps the two in step.

The order in `_data/methodology_nav.yml` is a *reading* order, aimed at someone meeting the
material for the first time. It is deliberately not the clause order of the numbered draft, where
Scope, Terms and Conformance appear early because a normative document has to be self-contained.
Both orders are maintained; neither is derived from the other.

Until August 2026 the navigation was copied into every page, so adding one section meant editing
twenty files and was done with a script each time. That is why the include exists.

| File | Section |
|---|---|
| `introduction.html` | Introduction: the problem, one worked document, and what a profile does |
| `index.html` | Overview: the map, the reading routes, and the contents |
| `challenges.html` | Challenges with SBOMs and current CBOMs |
| `inventory.html` | Inventory and CBOMs |
| `lifecycle.html` | Lifecycle data across development and deployment |
| `data-exposure.html` | Data exposure and the harvest-now-decrypt-later threat |
| `model.html` | The cryptographic relationship model |
| `profile.html` | The profile: rules, dual use, conformance |
| `conformance.html` | What conformance means, and what a verdict does not assert |
| `policy-evaluation.html` | Policy evaluation: facts against derived judgements |
| `method.html` | How to define a CBOM profile (the procedure) |
| `use-cases.html` | Use cases for profiles |
| `pqc-migration.html` | PQC migration: worked use case to profile definition |
| `formats.html` | CycloneDX and SPDX mapping |
| `versioning.html` | Handling older CBOM files |
| `governance.html` | Governance: lifecycle, signing, provenance, stewardship |
| `related-work.html` | Relationship to the PQC Maturity Model and other efforts |
| `files.html` | Files and how to run them |
| `demo.html` | Interactive conformance evaluation |
| `terms.html` | Terms and definitions (Reference group) |

Machine-readable artifacts in the same folder:

| File | Purpose |
|---|---|
| `profile-interface-disclosure.md` | The profile specification, including the relationship taxonomy. |
| `profile-interface-disclosure.rules.json` | The same profile as machine-readable rules. |
| `mapping-cyclonedx-spdx.md` | Requirement-to-format mapping for both formats. |
| `cbom-pass.cyclonedx.json` | Conforming example CBOM. |
| `cbom-fail.cyclonedx.json` | Non-conforming example; omits the management interface. |
| `profile-pqc-migration.rules.json` | The PQC migration profile, derived from the baseline via `extends`. |
| `cbom-pqc-pass.cyclonedx.json` | Conforming example for the migration profile. |
| `cbom-pqc-fail.cyclonedx.json` | Non-conforming example exercising conditional rules and the tightening. |
| `validate_cbom.py` | Version-aware validator, with profile composition. Checks a document against a profile. |
| `check_profile.py` | Well-formedness checker. Checks a profile against requirements C1 to C17 of the Conformance section. |
| `versioning-and-legacy-cboms.md` | Design note on handling older CBOM files. |

Both tools are exercised by `tests/run-profile-tests.sh` in the repository root, which CI runs on
any change under `docs/methodology/`.

Running the validator:

```bash
cd docs/methodology
python3 validate_cbom.py cbom-pass.cyclonedx.json profile-interface-disclosure.rules.json
python3 validate_cbom.py cbom-fail.cyclonedx.json profile-interface-disclosure.rules.json
```

The first conforms. The second fails product rule P2, because it declares no management
interface. Exit status is 0 for conformance and 1 otherwise, so the validator can be used
directly as a CI gate.

## Building locally

```bash
cd docs
bundle exec jekyll serve --baseurl /cbom
```

## Conventions worth keeping

**Do not add a `.nojekyll` file.** It disables Jekyll processing, which would leave `index.md`,
`references.md`, `issues.md`, `meetings.md`, `presentations.md` and `contributing.md` served as
raw Markdown and break the data registers and the templates. A `.nojekyll` was added here by mistake once and removed.

**Do not set a default layout for HTML pages.** The `methodology/` pages carry front matter so
that Jekyll processes them and the navigation include works, but they specify no `layout:` and
`_config.yml` has no `defaults:` block. If one were added that applied a layout to HTML files,
every methodology page would be wrapped in the site shell on top of its own markup and would
render two headers. An earlier version of this file advised keeping the folder free of front
matter for exactly that reason; the risk is real, and it comes from a default layout rather than
from front matter itself.

**Links are relative.** Nothing in `methodology/` hard-codes the baseurl, so `../` reaches the
site root and the section works unchanged if the folder is moved or served elsewhere.

**Styling is shared by convention, not by import.** `methodology/styles.css` is a separate
stylesheet that mirrors the palette, typography and header treatment of `assets/css/style.css`.
A change to the design system needs applying in both.

## Known gaps

- Diagrams in the methodology sections use hard-coded colours rather than the CSS variables,
  so a palette change does not reach them.
- The previous and next links at the foot of each page are per-page and hand-maintained. They
  duplicate the order held in `_data/methodology_nav.yml` and can drift from it. Rendering them
  from the same data would remove the duplication.
- The section navigation has not been checked in a browser since it changed from a flat tab bar
  to a grouped rail. The layout switches at 1100px and both states need looking at.

## Status

The methodology documentation is an illustrative working draft, not an adopted deliverable of
the working group. Field names are aligned to CycloneDX 1.7 / ECMA-424 (2nd Edition) and should
be checked against the current specifications before operational use.
