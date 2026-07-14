---
layout: default
title: Contributing
permalink: /contributing/
eyebrow: CBOM Reference Register
heading: Contributing
lede: The register lives in one YAML file. Adding a reference means adding a block and opening a pull request — no HTML, no templates.
---

## The one file that matters

Everything on the [References]({{ '/references/' | relative_url }}) page is generated
from **`docs/_data/references.yml`**. That file is the single source of truth. You never
touch HTML or the templates to add or correct a reference.

<div class="callout">
  <strong>In three steps:</strong>
  <ol>
    <li>Open <code>docs/_data/references.yml</code>.</li>
    <li>Append an entry to the <code>references:</code> list, in the block for its category.</li>
    <li>Open a pull request using the <em>Add a reference</em> template.</li>
  </ol>
</div>

## A worked example

```yaml
  - id: A8
    doc: BSSN Regulation No. X
    title: National cryptographic transition guidance
    org: BSSN (Indonesia)
    date: 2026-03
    category: policy
    jurisdiction: indonesia
    status: current
    url: https://example.gov.id/...
    tags: [inventory, pqc]
    notes: >-
      One to three sentences on why this matters for CBOM work — what it requires,
      and whether it names a format.
```

If you introduce a new `jurisdiction` (as above with `indonesia`), add a matching label
under `labels.jurisdiction` in `docs/_config.yml` so it renders with a readable name.

## Field reference

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Stable citation key (`F1`, `M3`, `E5`, `U7`, `A1`, `N1`). **Never reuse or renumber** — other documents cite these. Prefix by section: `F` formats, `M` methodology, `E` Europe, `U` United States, `A` Asia-Pacific, `N` other national. |
| `doc` | yes | Document or standard number, e.g. `BSI TR-03183-2 v2.1.0`. Include the version — most errors in reference lists are stale versions. |
| `title` | yes | Full published title. |
| `org` | yes | Publishing body. |
| `date` | no | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Publication date, not the date you found it. |
| `category` | yes | `formats`, `methodology` or `policy`. |
| `jurisdiction` | yes | Must exist in `labels.jurisdiction` in `docs/_config.yml`. New one? Add the label too. |
| `status` | yes | `current`, `draft`, `superseded` or `gap`. |
| `url` | no | Canonical link. Prefer the publisher's own URL over a mirror or vendor blog. |
| `tags` | no | Free-text list. Apply `inventory` consistently — see the house rules. |
| `notes` | no | One to three sentences on why it matters *for CBOM work*, not what the document says in general. |
| `verify` | no | `true` if you could not confirm a detail against the primary source. Renders a visible badge. |

## House rules

<div class="rules">
  <div class="rule">
    <h3>State status honestly</h3>
    <p>NIST IR 8547 is a draft; marking it <code>current</code> would imply a mandate that
       does not exist. If something is directional rather than binding, say so in
       <code>notes</code>.</p>
  </div>
  <div class="rule">
    <h3>Flag what you can't verify</h3>
    <p>Set <code>verify: true</code> rather than asserting a detail you couldn't confirm.
       An honest flag beats a confident error.</p>
  </div>
  <div class="rule">
    <h3>Supersede, don't delete</h3>
    <p>When a document is replaced, set the old entry to <code>superseded</code> and note
       what replaced it. Existing documents cite these keys.</p>
  </div>
  <div class="rule">
    <h3>Tag inventory mandates</h3>
    <p>Where a document requires a cryptographic inventory, tag it <code>inventory</code>
       and note whether it specifies a <em>format</em>. Nearly none do — that pattern is
       the working group's central argument.</p>
  </div>
</div>

## Previewing locally

```bash
cd docs
bundle exec jekyll serve
# or, without a local Ruby toolchain:
docker run --rm -v "$PWD":/srv/jekyll -p 4000:4000 jekyll/jekyll jekyll serve
```

Or simply open the pull request — GitHub Pages builds a preview from the branch.

<p class="post-links">
  <a class="btn btn-ghost" href="https://github.com/pkic/cbom/blob/main/docs/_data/references.yml">Open references.yml on GitHub &#8599;</a>
  <a class="btn btn-ghost" href="{{ '/references/' | relative_url }}">Back to the references</a>
</p>
