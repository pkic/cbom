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
| `issues.md` | The methodology aspects. |
| `contributing.md` | How to take part. |
| `_data/references.yml` | Reference sources, with category, status and jurisdiction. |
| `_data/aspects.yml` | The methodology aspects. |
| `_layouts/`, `_includes/` | Page shells and the shared header and footer. |
| `assets/css/style.css` | The design system: palette, typography, components. |
| `assets/js/references.js` | Filtering for the reference register. |

To add a reference or an aspect, edit the relevant file in `_data/`. Adding a new value for a
category, status or jurisdiction also needs a display label adding under `labels:` in
`_config.yml`.

## 2. The methodology documentation (static HTML)

`methodology/` holds the working draft of the methodology, explained against a worked example:
an nginx web server, its CBOM in CycloneDX 1.7, evaluated against a small product-independent
profile. These are plain HTML files with no front matter, so Jekyll copies them through
untouched and they are served at `/cbom/methodology/`.

| File | Section |
|---|---|
| `index.html` | Overview |
| `challenges.html` | Challenges with SBOMs and current CBOMs |
| `inventory.html` | Inventory and CBOMs |
| `lifecycle.html` | Lifecycle data across development and deployment |
| `model.html` | The cryptographic relationship model |
| `profile.html` | The profile: rules, dual use, conformance |
| `policy-evaluation.html` | Policy evaluation: facts against derived judgements |
| `use-cases.html` | Use cases for profiles |
| `formats.html` | CycloneDX and SPDX mapping |
| `versioning.html` | Handling older CBOM files |
| `governance.html` | Governance: lifecycle, signing, provenance |
| `files.html` | Files and how to run them |
| `demo.html` | Interactive conformance evaluation |
| `references.html` | References |

Machine-readable artifacts in the same folder:

| File | Purpose |
|---|---|
| `profile-interface-disclosure.md` | The profile specification, including the relationship taxonomy. |
| `profile-interface-disclosure.rules.json` | The same profile as machine-readable rules. |
| `mapping-cyclonedx-spdx.md` | Requirement-to-format mapping for both formats. |
| `cbom-pass.cyclonedx.json` | Conforming example CBOM. |
| `cbom-fail.cyclonedx.json` | Non-conforming example; omits the management interface. |
| `validate_cbom.py` | Version-aware validator. |
| `versioning-and-legacy-cboms.md` | Design note on handling older CBOM files. |

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
`references.md`, `issues.md` and `contributing.md` served as raw Markdown and break the data
register and the templates. A `.nojekyll` was added here by mistake once and removed.

**Keep `methodology/` free of front matter.** The files are deliberately plain HTML. Adding
front matter would pull them into the Jekyll build and apply the site layout on top of their
own, producing two headers.

**Links are relative.** Nothing in `methodology/` hard-codes the baseurl, so `../` reaches the
site root and the section works unchanged if the folder is moved or served elsewhere.

**Styling is shared by convention, not by import.** `methodology/styles.css` is a separate
stylesheet that mirrors the palette, typography and header treatment of `assets/css/style.css`.
A change to the design system needs applying in both.

## Known gaps

- The reference list in `methodology/references.html` duplicates, and will drift from, the
  register in `_data/references.yml`. Folding the former into the latter and linking to
  `/references/` would remove the duplication.
- Diagrams in the methodology sections use hard-coded colours rather than the CSS variables,
  so a palette change does not reach them.

## Status

The methodology documentation is an illustrative working draft, not an adopted deliverable of
the working group. Field names are aligned to CycloneDX 1.7 / ECMA-424 (2nd Edition) and should
be checked against the current specifications before operational use.
