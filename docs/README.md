# docs/

The published site for the PKI Consortium CBOM Profiles Working Group, served by GitHub Pages
at <https://pkic.github.io/cbom/>. This file is excluded from the build and is here for
contributors.

The folder holds two things that are built differently: the Jekyll site, and two sections of
hand-written HTML.

## 1. The working group site (Jekyll)

Data-driven pages built by Jekyll from Markdown and Liquid templates.

| Path | Purpose |
|---|---|
| `_config.yml` | Site settings. `baseurl` must stay `/cbom` so `relative_url` resolves correctly. |
| `index.md` | Overview and landing page. |
| `references.md` | The reference register, rendered from `_data/references.yml`. |
| `tooling.md` | The tooling registry, rendered from `_data/tooling.yml`. |
| `issues.md` | The methodology aspects. |
| `meetings.md` | Meetings and polls, rendered from `_data/meetings.yml` and `_data/polls.yml`. |
| `presentations.md` | Presentations, rendered from `_data/presentations.yml`. |
| `contributing.md` | How to take part. |
| `_data/references.yml` | Reference sources, with category, status and jurisdiction. |
| `_data/tooling.yml` | Tools that work with CBOMs, with what they do and where they say so. |
| `_data/aspects.yml` | The methodology aspects. |
| `_data/meetings.yml` | Meetings, their agendas and their recordings. |
| `_data/polls.yml` | Polls: what was asked, when voting closes, and the result. Votes are collected in Formbricks. |
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

Two sections are hand-written HTML rather than Markdown:

| Path | Served at | Holds |
|---|---|---|
| `methodology/` | `/cbom/methodology/` | The working draft of the methodology, explained against one worked example: Keycloak 26.7.3, described by a vendor's product record and an operator's deployment records in CycloneDX 2.0, evaluated against a family of product-independent profiles. |
| `use-cases/` | `/cbom/use-cases/` | The register of use cases, in four groups (disclosure, change planning, operation and assurance). Three are worked examples with published profiles, all applied to Keycloak 26.7.3: PQC migration, procurement and deployment disclosure. IoT device estates and substation automation are drafts. |

Each page carries a two-line front matter block so that Jekyll processes it, which is what allows
the shared navigation include to work. No layout is applied, so each page still controls its own
markup.

The two sections are separate because the methodology is the deliverable and a worked use case is
an instance of applying it: instances multiply with the number of sectors that want one, and the
length of the deliverable should not. The argument is set out on `use-cases/index.html`. The
methodology keeps the general part in `methodology/use-cases.html`: why the use case comes first,
and why one document can serve several profiles only up to a limit. That page lists no use cases.
It keeps anchors for the entries it once listed, and links each one to its page in `use-cases/`.
It is a different page from the section index and is easy to confuse with it.

`use-cases/` has no stylesheet of its own and links `../methodology/styles.css`, which is the
design system for both. `methodology/pqc-migration.html` is a redirect stub: that page moved to
`use-cases/` and the old URL was already published and cited outside the repository.

### Previewing locally

Because of that front matter and the navigation include, opening a page straight from the
filesystem shows the front matter as text and no navigation. Two ways to see the real thing:

| | Command | Covers |
|---|---|---|
| **Full site** | `bundle install` then `bundle exec jekyll serve --source docs` | Everything, at the versions GitHub Pages builds with. Use this before publishing. |
| **The HTML sections only** | `python3 tools/preview.py` | Both sections, served on `localhost:8000/methodology/introduction.html`. No Ruby, no install. Skips the Markdown pages and layouts. |

`tools/preview.py` does only what Jekyll does to these particular pages — strips the front matter
and expands the one navigation include each calls — and warns rather than guessing if a page grows
Liquid it does not handle. It writes each section under its own directory name so the links between
them resolve as they do on the published site, and it copies a redirect stub through untouched.
Re-run it after editing; it does not watch for changes. Adding a third section means adding a line
to `SECTIONS` in that file.

### Navigation

The section navigation lives in one place and is rendered into every page.

| Path | Purpose |
|---|---|
| `_data/methodology_nav.yml` | The methodology's sections, in groups, in reading order. The single source of truth. |
| `_data/usecases_nav.yml` | The same for the Use Cases section. Its ids are prefixed `uc-` so the two rails cannot mark each other's pages current. |
| `_includes/methodology-nav.html` | Renders the methodology's list. Marks the current page from its `nav:` front matter value. |
| `_includes/usecases-nav.html` | The same for the Use Cases section. A copy against a different data file rather than one parameterised include. |
| `methodology/styles.css` | Styling for both, under "section navigation". A left rail at 1100px and above, a grouped block above the content below that. |

**Adding a methodology section** means: create the page with `nav: <id>` in its front matter, wrap
its body in `<div class="shell">` with `{% include methodology-nav.html %}` before `<main>`, add one
line to `_data/methodology_nav.yml`, then run `python3 tools/renumber-pagenav.py` from the repository
root. The same applies to reordering: the sidebar comes from the data file, but the previous and
next links at the foot of each page are written into the pages themselves, and the script is what
keeps the two in step.

**Adding a worked use case** means the same, against `_data/usecases_nav.yml` and
`{% include usecases-nav.html %}`, plus a row in the table on `use-cases/index.html`. Do not run
`renumber-pagenav.py` for it: that script manages the methodology's order only, and this section's
footer links are written by hand because it has few enough pages for that to be safe.

Each rail carries a pointer to the other section, as its own group at the end of the list. In
`methodology_nav.yml` that entry is last on purpose: `renumber-pagenav.py` skips entries whose url
is not a local `.html` page, and the page before a skipped entry keeps the neighbour it had, so a
cross-section pointer placed mid-order would give its predecessor a footer link into the other
section.

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
| `objects.html` | The objects the methodology defines, who creates each one and how it is identified |
| `profile.html` | The profile: rules, dual use, conformance |
| `conformance.html` | What conformance means, and what a verdict does not assert |
| `maturity.html` | Profile maturity: a family of profiles ordered by depth, and the entry profile |
| `confidentiality.html` | Public and restricted variants of a CBOM, and how withholding is marked |
| `policy-evaluation.html` | Policy evaluation: facts against derived judgements |
| `method.html` | How to define a CBOM profile (the procedure) |
| `use-cases.html` | Starting from a use case: why every profile begins with a consumer and a decision. Lists no use cases |
| `vulnerabilities.html` | How cryptographic weakness is communicated alongside a CBOM rather than inside one |
| `context.html` | Context pointers: what a CBOM points to and does not carry, and how reference rules check the pointer |
| `pqc-migration.html` | Redirect stub. The page is now `use-cases/pqc-migration.html` |
| `formats.html` | CycloneDX and SPDX mapping |
| `versioning.html` | Handling older CBOM files |
| `governance.html` | Governance: lifecycle, signing, provenance, stewardship |
| `related-work.html` | Relationship to the PQC Maturity Model and other efforts |
| `files.html` | Files and how to run them |
| `demo.html` | Interactive conformance evaluation |
| `terms.html` | Terms and definitions (Reference group) |

The Use Cases section, for comparison, has eleven files:

| File | Section |
|---|---|
| `use-cases/index.html` | Overview: the groups, the register of all use cases with their status, and why use cases are not in the methodology |
| `use-cases/disclosure.html` | Disclosure group: profiles that choose among the baseline's facts |
| `use-cases/procurement.html` | Procurement: the procurement profile v0.1 applied to the Keycloak product record (worked example) |
| `use-cases/change-planning.html` | Change planning group: profiles that add capability facts, and the proposed change core |
| `use-cases/pqc-migration.html` | PQC migration: one use case from the consumer's decision to two profile depths (worked example) |
| `use-cases/iot.html` | IoT device estate (draft worked example) |
| `use-cases/substation.html` | Substation automation, OT (draft worked example) |
| `use-cases/operation.html` | Operation group: documents written by the operator, with the deployment disclosure profile v0.1 (worked example) |
| `use-cases/assurance.html` | Assurance group: a reader relies on the document as evidence |
| `use-cases/proposing.html` | How a use case is proposed, and what each status means |
| `use-cases/template.html` | Template for a worked use case |

The machine-readable artifacts for the PQC migration profile stay in `methodology/` with the other
profiles and documents, because `tests/run-profile-tests.sh` and `files.html` path them there and
splitting the artifacts would make the suite harder to read than the page being one directory away.

Machine-readable artifacts in the same folder (the full list, with expected verdicts, is on
`files.html`):

| Path | Purpose |
|---|---|
| `profile-*.rules.json` | Six profiles: interface-enumeration (entry), interface-disclosure (the baseline), deployment-disclosure, pqc-migration, pqc-migration-extended, procurement. |
| `profile-interface-disclosure.md` | The baseline's specification, including the relationship taxonomy. |
| `mapping-cyclonedx-spdx.md` | Where each rule's facts sit in CycloneDX 2.0, CycloneDX 1.6/1.7 (legacy) and SPDX. |
| `examples/` | The Keycloak example CBOMs in CycloneDX 2.0. `examples/legacy/` holds CycloneDX 1.7 documents; `examples/results/` holds policy results. |
| `policies/` | Two example policies: the readiness gap and an algorithm transition. |
| `perspectives/` | One CycloneDX 2.0 perspective per profile, generated from its rules. Informative only. |
| `validate_cbom.py` | Validator. Reads CycloneDX 2.0 and 1.x; `--with` supplies documents a record cites. |
| `check_profile.py` | Well-formedness checker for profiles (requirements C1 to C18). |
| `evaluate_policy.py` | Applies a policy to CBOMs and writes a result that names every CBOM by digest. |
| `compare_stages.py` | Lays a product record, a configured record and an observation side by side. |
| `cdx17_to_20.py` | Converts a CycloneDX 1.6/1.7 CBOM to 2.0. |
| `profile.schema.json`, `claim.schema.json`, `policy.schema.json`, `policy-result.schema.json` | Published schemas. |
| `claim-example.json` | A worked claim over three profiles, bound to a document by digest. |
| `demo-reports.json` | Reports the demonstration page renders, generated by `tools/build_demo_reports.py`. |
| `versioning-and-legacy-cboms.md` | Design note on handling older CBOM files. |

The examples, perspectives and demo reports are generated by scripts in `tools/`. All of it is
exercised by `tests/run-profile-tests.sh` in the repository root, which CI runs on any change
under `docs/methodology/`.

Running the validator:

```bash
cd docs/methodology
python3 validate_cbom.py examples/cbom-keycloak-product.cdx.json profile-interface-disclosure.rules.json
python3 validate_cbom.py examples/cbom-keycloak-product-fail-P2.cdx.json profile-interface-disclosure.rules.json
python3 validate_cbom.py examples/cbom-keycloak-deployment-configured.cdx.json \
    profile-deployment-disclosure.rules.json --with examples/cbom-keycloak-product.cdx.json
```

The first conforms. The second fails product rule P2, because it declares no management
interface. The third conforms, and checks its citation of the product record by hash. Exit status
is 0 for conformance and 1 for non-conformance. Other codes mark a usage error (2), a profile error
(3), a refusal because the carrier version is below the profile's minimum (4) and a claim mismatch
(5). A CI gate must not treat a refusal as a failure, because a refused document was never assessed.

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

**Links are relative.** Nothing in either HTML section hard-codes the baseurl, so `../` reaches the
site root and a section works unchanged if the folder is moved or served elsewhere. Links between the
two sections assume they stay siblings under `docs/`, which is the one relative assumption that
crosses a directory: `../use-cases/…` from the methodology, `../methodology/…` back.

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
the working group. Field names target CycloneDX 2.0, pinned to the 2.0-dev schema of 23 October 2026 until the
release (decision 0025); CycloneDX 1.6 and 1.7 are read as legacy. Check them against the current
specifications before operational use.
