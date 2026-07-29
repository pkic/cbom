# CBOM Profiles — documentation site

A self-contained, static, multi-page documentation site for the PKIC CBOM Profiles
Working Group's worked example (an nginx web server, CycloneDX 1.7). Light theme,
no build step, no external dependencies. Served by GitHub Pages from this `docs/` folder.

## Pages

| File | Tab |
|---|---|
| `index.html` | Overview |
| `challenges.html` | Challenges (SBOM & current CBOM limitations) |
| `inventory.html` | Inventory and CBOMs |
| `lifecycle.html` | Lifecycle Data (dev & deployment phases) |
| `ontology.html` | Ontology (node · edge · asset) |
| `profile.html` | Profile (rules, dual use, conformance) |
| `policy-evaluation.html` | Policy Evaluation (facts vs derived evaluations) |
| `use-cases.html` | Use Cases |
| `formats.html` | Formats (CycloneDX & SPDX mapping) |
| `versioning.html` | Versioning (older CBOM files) |
| `governance.html` | Governance (lifecycle, signing, provenance) |
| `files.html` | Files & how to run |
| `demo.html` | Interactive conformance evaluation |
| `references.html` | References |

Shared styling is in `styles.css`. `.nojekyll` disables Jekyll processing so the
files are served exactly as written.

## Publishing on GitHub Pages

In *Settings → Pages*, set the source to *Deploy from a branch*, branch = your default
branch, folder = `/docs`. The entry point is `index.html`. All links between pages are
relative, so the site works under a `/<repo>/` base path.

## Artifacts

The machine-readable artifacts referenced by the Files page live alongside the HTML:
`profile-interface-disclosure.md`, `profile-interface-disclosure.rules.json`,
`mapping-cyclonedx-spdx.md`, `cbom-pass.cyclonedx.json`, `cbom-fail.cyclonedx.json`,
`validate_cbom.py`, `versioning-and-legacy-cboms.md`.

## Status

Illustrative early-concept material. Not a normative PKIC or GSMA deliverable. CycloneDX
field names are aligned to v1.7 / ECMA-424 (2nd Edition) but should be validated against
the live schema before real use.
