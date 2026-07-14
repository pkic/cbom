---
name: Add or amend a reference
about: Add a document to the CBOM reference register, or correct an existing entry
labels: references
---

## What is changing

<!-- New entry, or an amendment to an existing one? Give the id(s). -->

## Checklist

- [ ] Entry added to / amended in `docs/_data/references.yml` (not the rendered page)
- [ ] `id` is new and not a reuse of a retired key — or, for an amendment, unchanged
- [ ] `doc` includes the version or edition
- [ ] `status` reflects reality (a draft is `draft`, not `current`)
- [ ] Anything I could not confirm against the primary source is marked `verify: true`
- [ ] If this supersedes an existing entry, the old one is set to `superseded` rather than deleted
- [ ] If the document mandates a cryptographic inventory, it is tagged `inventory` and the notes say whether it names a format

## Source

<!-- Link to the primary source. Publisher URL, not a vendor summary. -->
