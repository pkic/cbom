---
layout: default
title: Contributing
permalink: /contributing/
eyebrow: CBOM Profiles · Working Group
heading: Contributing
lede: You don't need to be a developer, and you don't need to install anything. If you can use a web forum, you can take part fully.
---

There are three ways to contribute, in rough order of how often you'll do them. All happen in
the browser at github.com, signed in with a GitHub account.

<div class="card-grid contrib-grid">
  <div class="feature-card">
    <span class="card-kicker">Most common</span>
    <h3>Weigh in on an aspect</h3>
    <p>Open the <a href="{{ '/issues/' | relative_url }}">Issues</a> page, pick a topic, read
       from the top, and add your view in the comment box. A reaction emoji is a quick
       temperature check.</p>
    <a class="card-cta" href="{{ site.repo.issues }}">Go to issues &#8599;</a>
  </div>
  <div class="feature-card">
    <span class="card-kicker">Open-ended</span>
    <h3>Start a discussion</h3>
    <p>For a topic that hasn't narrowed to a single decision yet, open a
       <a href="{{ site.repo.discussions }}">Discussion</a>. It can be promoted to an aspect
       issue once it's ready to converge.</p>
    <a class="card-cta" href="{{ site.repo.discussions }}">Go to discussions &#8599;</a>
  </div>
  <div class="feature-card">
    <span class="card-kicker">Structured</span>
    <h3>Add a reference</h3>
    <p>Keep the <a href="{{ '/references/' | relative_url }}">register</a> current by adding a
       single YAML entry and opening a pull request — the guide below covers it.</p>
    <a class="card-cta" href="#adding-a-reference">Jump to the guide &#8595;</a>
  </div>
</div>

## Raising a new topic

Decide which fits:

- A **specific question to settle** → the [Issues]({{ site.repo.issues }}) tab → **New issue**
  → the *Aspect topic* template, which prompts you for the right details.
- An **open-ended conversation** → the [Discussions]({{ site.repo.discussions }}) tab →
  **New discussion**.

If you're not sure, start a Discussion — it can become an Issue later. Before opening one,
check the [Issues page]({{ '/issues/' | relative_url }}) so you don't start a second thread on
an aspect already being tracked.

## Adding a reference

Everything on the [References]({{ '/references/' | relative_url }}) page is generated from
**`docs/_data/references.yml`**. That file is the single source of truth — you never touch HTML
or the templates.

<div class="callout">
  <strong>In three steps:</strong>
  <ol>
    <li>Open <code>docs/_data/references.yml</code>.</li>
    <li>Append an entry to the <code>references:</code> list, in the block for its category.</li>
    <li>Open a pull request using the <em>Add a reference</em> template.</li>
  </ol>
</div>

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

If you introduce a new `jurisdiction`, add a matching label under `labels.jurisdiction` in
`docs/_config.yml` so it renders with a readable name.

### Field reference

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Stable citation key (`F1`, `M3`, `E5`, `U7`, `A1`, `N1`). **Never reuse or renumber** — other documents cite these. Prefix by section: `F` formats, `M` methodology, `E` Europe, `U` United States, `A` Asia-Pacific, `N` other national. |
| `doc` | yes | Document or standard number, e.g. `BSI TR-03183-2 v2.1.0`. Include the version. |
| `title` | yes | Full published title. |
| `org` | yes | Publishing body. |
| `date` | no | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Publication date, not the date you found it. |
| `category` | yes | `formats`, `methodology` or `policy`. |
| `jurisdiction` | yes | Must exist in `labels.jurisdiction` in `docs/_config.yml`. |
| `status` | yes | `current`, `draft`, `superseded` or `gap`. |
| `url` | no | Canonical link. Prefer the publisher's own URL. |
| `tags` | no | Free-text list. Apply `inventory` consistently. |
| `notes` | no | One to three sentences on why it matters *for CBOM work*. |
| `verify` | no | `true` if you could not confirm a detail against the primary source. Renders a badge. |

### House rules

<div class="rules">
  <div class="rule">
    <h3>State status honestly</h3>
    <p>NIST IR 8547 is a draft; marking it <code>current</code> would imply a mandate that
       does not exist. Say so in <code>notes</code>.</p>
  </div>
  <div class="rule">
    <h3>Flag what you can't verify</h3>
    <p>Set <code>verify: true</code> rather than asserting a detail you couldn't confirm.</p>
  </div>
  <div class="rule">
    <h3>Supersede, don't delete</h3>
    <p>When a document is replaced, set the old entry to <code>superseded</code> and note what
       replaced it. Existing documents cite these keys.</p>
  </div>
  <div class="rule">
    <h3>Tag inventory mandates</h3>
    <p>Where a document requires a cryptographic inventory, tag it <code>inventory</code> and
       note whether it specifies a <em>format</em> — that pattern is the central argument.</p>
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
  <a class="btn btn-ghost" href="{{ site.repo.url }}/blob/main/docs/_data/references.yml">Open references.yml on GitHub &#8599;</a>
  <a class="btn btn-ghost" href="{{ '/issues/' | relative_url }}">See the open aspects</a>
</p>
