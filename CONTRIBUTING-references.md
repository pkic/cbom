# Contributing to the CBOM reference register

The register lives in **`docs/_data/references.yml`**. That file is the source of
truth; the published page is generated from it. You never need to touch HTML or
templates to add a reference.

## Adding a reference

1. Open `docs/_data/references.yml`.
2. Append an entry to the `references:` list, in the block for its category.
3. Open a pull request using the **Add a reference** template.

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

## Field reference

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Stable citation key (`F1`, `M3`, `E5`, `U7`, `A1`, `N1`). **Never reuse or renumber** — other documents cite these. Prefix by section: `F` formats, `M` methodology, `E` Europe, `U` United States, `A` Asia-Pacific, `N` other national. |
| `doc` | yes | Document or standard number, e.g. `BSI TR-03183-2 v2.1.0`. Include the version — half the errors in the old reference list were stale versions. |
| `title` | yes | Full published title. |
| `org` | yes | Publishing body. |
| `date` | no | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Use the publication date, not the date you found it. |
| `category` | yes | `formats`, `methodology` or `policy`. |
| `jurisdiction` | yes | Must exist in `labels.jurisdiction` in `docs/_config.yml`. Adding a new one? Add the label too. |
| `status` | yes | `current`, `draft`, `superseded` or `gap`. |
| `url` | no | Canonical link. Prefer the publisher's own URL over a mirror or a vendor blog. |
| `tags` | no | Free-text list. `inventory` is worth applying consistently — see below. |
| `notes` | no | One to three sentences. Say why it matters *for CBOM work*, not what the document is about in general. |
| `verify` | no | `true` if you could not confirm a detail against the primary source. Renders a visible badge. Better an honest flag than a confident error. |

## House rules

- **State the status honestly.** NIST IR 8547 is a draft; marking it `current` would
  imply a mandate that does not exist. If something is directional rather than
  binding, say so in `notes`.
- **Flag what you could not verify** with `verify: true` rather than asserting it.
- **Watch for supersession.** When a document is replaced, set the old entry to
  `superseded` and note what replaced it — do not delete it. Existing documents cite
  these keys.
- **Tag inventory mandates.** Where a document requires a cryptographic inventory,
  tag it `inventory` and note in `notes` whether it specifies a *format*. Nearly all
  of them do not. That pattern is the working group's central argument, and the tag is
  what makes it demonstrable rather than assertable.

## Previewing locally

```bash
cd docs
bundle exec jekyll serve   # or: docker run --rm -v "$PWD":/srv/jekyll -p 4000:4000 jekyll/jekyll jekyll serve
```

Or simply open the pull request — GitHub Pages builds a preview on the branch.
