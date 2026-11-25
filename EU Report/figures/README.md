# Figures

Eleven figures for *Cryptographic Transparency in the Supply Chain*. Figures 1 to 6 are in the
report. Figures 7 to 11 are drafted and not yet wired in.

| File | Goes in | Carries |
|---|---|---|
| `fig-1-migration-chain` | §3.1, ahead of the identifier table | The chain of six dependent stages, the three tracks converging on it, the seven constraints, and where EU instruments land |
| `fig-2-cryptographic-relationship` | §10.5, inside the WR1 worked case | One connection containing three relationships, none of which is in either endpoint's inventory |
| `fig-3-timeline` | §5.5 | Every EU and US date that bounds the recommendations, and the window that closes around March 2027 |
| `fig-4-hsm-interfaces` | §10.5, ahead of the WR4 table | A module whose validated boundary encloses its post-quantum algorithms but not the five classical interfaces crossing it |
| `fig-5-derived-artefact` | §10.7 | The supplier and operator artefacts, the derivedFrom link, the four statement kinds, and what the pair makes checkable |
| `fig-6-format-asymmetry` | §4.4 | One format has the vocabulary, the other has the object model, and six attributes fall outside both |
| `fig-7-supply-chain-opacity` | §2.1 | Visibility runs one tier; exposure runs the whole chain |
| `fig-8-consumption-gap` | §6.1 | What regulation achieved in SBOM adoption, and what it did not |
| `fig-9-two-axes` | §8.5 | Lifecycle stage and classical retirement state are independent axes |
| `fig-10-baseline-and-families` | §11.1 | One baseline, four families, sector profiles that extend rather than fork |

Each exists as `.svg` (source) and `.png` (what the markdown references).

A third pointer sits in §2.3, where the term *cryptographic relationship* is introduced, sending the
reader forward to Figure 2.

## Captions as inserted

**Figure 1.** The migration chain, its parallel tracks, and the constraints that bound both. The
table below carries the same structure with the identifiers used throughout this report.

**Figure 2.** One mutually authenticated connection, decomposed. Both inventories are complete and
correct, and neither contains any of the three relationships.

**Figure 3.** The dates that bound the recommendations in chapter 12. The scale is not linear, and
the 2026 and 2027 standards dates are committee expectations rather than commitments.

**Figure 4.** The same module, drawn by interface. The validated boundary encloses the algorithms
the module offers. It does not enclose the cryptography that protects the module.

**Figure 5.** The artefact pair. The second references the first rather than rewriting it, and the
link is what makes the cross-artefact checks possible.

**Figure 6.** The asymmetry stated once. One format has the vocabulary, the other has the object
model, and six attributes fall outside both.

## What was deliberately not drawn

A diagram earns its place when it saves a reader from assembling a mechanism out of prose. These
were considered and rejected:

- **The §8.1 two-step mechanism** (standardise, then automate). It is two steps and a list of four
  gates. A sentence says it faster.
- **The §7.8 gap cross-tabulation.** Figure 1 already marks where instruments land, and a second
  view of the same distribution would restate it.
- **The §12.3 sequencing.** The recommendations table carries preconditions and indicative dates in
  columns, which is the right form for something a reader will scan rather than trace.
- **The orientation and subject-scope model.** Genuinely orthogonal dimensions, but §10.2.1's table
  already sets them out and a matrix would add a picture without adding an insight.

## Which file to use

The markdown references the **PNG**, because pandoc's SVG handling into .docx is unreliable. Both
PNGs render at roughly 400 dpi across a 160 mm text column, which is enough for print.

Keep the **SVG** as the source. It is the better file for a PDF-only route, it stays sharp at any
size, and it is the one to edit. Regenerate the PNG after any edit:

```bash
node shot.js fig-1-migration-chain.svg fig-2-cryptographic-relationship.svg
```

`shot.js` is not included here; it is six lines of Playwright that opens the SVG in Chromium at
`deviceScaleFactor: 3` and screenshots it. Any SVG rasteriser does the same job:
`rsvg-convert -z 3 in.svg -o out.png`.

## Design notes, so a later edit stays consistent

- **Print first.** Ink is `#1a1a1a`, secondary text `#5a5a55` and `#6b6b6b`, panel fill `#f2f2ef`.
  Nothing relies on a screen background, and nothing inherits a page foreground.
- **One accent only,** `#1f5fa9`, and it means one thing in each figure: in Figure 1 it marks where
  EU instruments land; in Figure 2 it marks the post-quantum half of the connection. It survives
  greyscale printing as a mid tone.
- **Dashing carries meaning as well as colour,** so the figures still read when printed mono. In
  Figure 1, solid outlines are the core chain and dashed outlines are the tracks running on their
  own timelines.
- **Arrows are labelled.** "blocked until", "gates entry", "converge at deployment". An unlabelled
  arrow only says "related somehow".
- **Text is sized for the column.** Figure 1 is 866 units wide and Figure 2 is 840; body labels sit
  at 14 to 19 units, which lands between 8.5 and 11 pt at a 160 mm column. If you widen a figure,
  scale the type with it.
- Each `<svg>` carries `role="img"` and an `aria-label` stating the same claim as the caption, for
  anyone reading the report with a screen reader.

## If the figures change

Figure 1 states positions as at September 2026 in its footer, and two cells will age: "substantially
complete" against algorithm standardisation, and "TLS done, others not" against protocol profiling.
Re-check both against §3.2 before publication.


## Figures 7 to 10 — drafted, not yet placed

**Figure 7 (§2.1).** Visibility runs one tier down the chain. Exposure runs the whole length of it.
Each of the four answers is correct about itself, and none of them answers the buyer's question.

**Figure 8 (§6.1).** Regulation solved the production of software bills of materials and did not
solve their use. The two figures are ENISA's, measured ahead of the Cyber Resilience Act.

**Figure 9 (§8.5).** The lifecycle stage and the classical retirement state are independent. A
scheme that records only the horizontal axis counts the dot as finished.

**Figure 10 (§11.1).** One baseline carrying the shared vocabulary, four families for four
decisions, and sector profiles that extend a family instead of forking from the baseline.

Figure 8 is the only one of the four that encodes a quantity. It uses a unit pictogram rather than a
chart, because two ratios do not need axes, and the hatched units are the group each figure is
about. Figure 9 is a position on a grid rather than a plot; there is no scale on either axis and
none is implied.


**Figure 11 (§7.8 or §8.2).** All twenty-five gaps at once, grouped by the six categories of
chapter 7 and shaded by how far a profile goes with each. The point is the pattern: a profile is
strong where the problem is incommensurability and weak where the problem is absence.

The four treatment levels are a reading of §8.2's third column, not a scheme the report states.
Every chip carries its identifier and its name, so colour never carries the meaning alone, and the
four fills differ in lightness as well as hue for mono printing and colour vision deficiency.
