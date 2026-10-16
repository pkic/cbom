---
build:
  render: never
---

# Publishing CBOM working material through PKIC

PKIC defines the publishing capabilities shared by its working groups. This repository supplies content in that format, following the PKIMM and PQCCM content repositories. It does not supply a PKIC application, theme, renderer, or importer.

## Proposed content structure

- `_index.md`: entry point for the working material.
- `methodology/` and `use-cases/`: Markdown documents; `_index.md` identifies each section.
- `references.md`, `tooling.md`, `meetings.md`, `presentations.md`, `issues.md`, and `contributing.md`: editorial pages.
- `assets/figures/`: standalone SVG figures with descriptive alternative text in the Markdown. Existing figures are preserved as vectors; future Mermaid diagrams use fenced `mermaid` blocks.
- `docs/methodology/` and `docs/assets/presentations/`: existing example artifacts and presentation downloads. These remain the authoritative files; the native pages link to them rather than copying them.

PKIC mounts this repository as a pinned content submodule under `content/wg/cbom/profiles`, using its ordinary Markdown renderer, site shell, navigation, image and download handling, search, and preview. The WG landing page and charter remain in the PKIC site repository. Updating content requires a reviewed source commit and a submodule update, as for the other content repositories. No CBOM-specific script runs during publication.

Repository notes and internal plans are not public content. Root-level nonpublication Markdown declares `build.render: never`. PKIC's existing `ignoreFiles` configuration excludes `docs`, `doc`, `drafts`, `decisions`, `tools`, and `tests` from document discovery. Files linked as downloads remain available through the ordinary content-asset mechanism.

## Review and cutover

This is a proposed source reorganization. The existing Jekyll site under `docs/` is retained during review so published external links, the conformance example, and the interactive registers continue to work. It is not a second renderer embedded into PKIC. The initial native content is a one-time conversion of source revision `acee89668382c1acb3a847e2e2f0e49625f12b50`; no conversion tool or synchronization job is part of either repository.

Before accepting the cutover, review the Markdown against the existing source and approve which format becomes the editorial source of truth. Do not maintain parallel versions indefinitely. Once PKIC publication is accepted, retire the old editorial pages through a coordinated source-site redirect change. Confirm anchors and downloads before redirecting; the PKIC site cannot install redirects on `pkic.github.io`.

## Shared capabilities and remaining gaps

Native pages retain the complete static registers and link to their original interactive versions. PKIC's existing site search and browser find can locate entries. The source site's facet filters and regrouping are not provided by the current shared content renderer. If these are required inside PKIC, implement one shared authored-register capability for every working group, with a common content contract and presentation. Do not add CBOM filter scripts, endpoint families, or D1 tables.

The conformance page explains all four examples and carrier-version bands, links the committed inputs and validator, and links the existing standalone interactive example. PKIC does not execute the source site's arbitrary inline JavaScript. A future interactive example mechanism must be a shared platform capability with an explicit content contract, rather than an extracted CBOM script.

The current figures are SVG, not D3 or Mermaid. Mermaid is already supported by PKIC. D3 is a JavaScript library, not a document format that PKIC automatically renders; any D3-based feature must use a common platform mechanism rather than a group-specific code loader.

No active survey or published poll exists in this source revision. Future response collection should use PKIC forms after defining the form, identity/access rules, and result visibility. Personal voting links must not be placed in public content.

The content remains illustrative working material, not an adopted deliverable. Tool listings retain their evidence and nonendorsement statements.
