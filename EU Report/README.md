# EU Report — working folder

## Files

| File | What it is |
|---|---|
| `EU Report.md` | **The working draft. This is the only file anyone edits.** Carries owner lines, page caps, drafting notes, verification markers and internal `DR-`, `VL` and `P-` citations. |
| `Cryptographic-Transparency-in-the-Supply-Chain.md` | The submittable copy. **Generated — never edit it.** Overwritten on every build. |
| `publish-report.txt` | What the last build stripped, and anything still blocking submission, with line numbers. |
| `EU Report.pre-review-backup.md` | The draft as it stood before the September 2026 review. Keep until the review is signed off, then delete. |
| `review-2026-09-18.md` | The review that produced the current round of changes, with sources and an outstanding worklist. |
| `publish.py`, `publish.sh`, `toclib.py` | The publication build. |

## Building the submittable copy

```
bash publish.sh "v0.9 — draft for Commission review"
```

The version label is optional and lands in the title block; omitted, it becomes
`Draft for review — <today>`.

The build exits **non-zero** if anything remains that must not ship. Read
`publish-report.txt`, fix the working draft, run it again. It never edits the working draft.

## What the build does

1. Stamps the version label into the title block.
2. Removes the *Editorial conventions* and *Resolved drafting questions* sections.
3. Removes blockquotes marked `Verify`, `Drafting note`, `Open:`, `Decision needed in` and
   `Internal.`
4. Removes owner and status lines, register footers, and build-script references.
5. Removes internal `DR-`, `VL`, `P-` and `pkic-feedback` citations, but only where they sit in a
   parenthetical. **This is why every internal tag must be written as a trailing parenthetical** —
   `... routed to the working group (P-11).` and not `... is routed as P-11.` The second form
   leaves a broken sentence, so the build refuses it rather than mangling the prose.
6. Regenerates the table of contents.
7. Checks the result and lists anything left.

`LYR-`, `LSN-`, `GAP-` and `RDY-` tags are reader-facing and survive publication. The front
matter explains them.

## Next steps after a clean build

The markdown copy is not the final deliverable. Word or PDF is, for a government-facing output,
and pagination and numbering come from that conversion rather than from markdown. The outstanding
items are listed at the end of `review-2026-09-18.md`.
