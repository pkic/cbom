# Publications: Markdown sources

The Markdown files in `src/` are the source of the working group's publications.
The Word files in `docs/assets/publications/` are built from them. Edit the
Markdown, not the Word files: a change made only in Word is lost at the next build.

## Layout

| Path | Contents |
|---|---|
| `src/*.md` | One Markdown file per publication |
| `src/media/<short>/` | The images of each publication |
| `templates/reference.docx` | The Word template. Its styles, page size and margins are used for every publication |
| `links.lua` | Rewrites relative links to the tagged release on GitHub |
| `postprocess.py` | Applies the house layout to the Word file that pandoc builds |
| `build.sh` | Builds the Word files |
| `add_links.py` | Turns file and folder names written as inline code into links, at their first mention in each chapter |
| `convert.py`, `compare.py` | Tools for the one-off move from Word to Markdown |
| `_build/` | Local output and comparison files. Not committed |

## Building

From the repository root:

```
bash publications/build.sh
```

The build needs pandoc and Python 3. By default the links point to the tag
`release-1`. To build against another tag, set `CBOM_TAG`, for example
`CBOM_TAG=release-1-rc1 bash publications/build.sh`. To write the output
somewhere other than `docs/assets/publications/`, set `OUT`.

## Writing rules for the sources

- **Links to files in this repository** are written as relative paths from
  `src/`, for example `[validate_cbom.py](../../docs/methodology/validate_cbom.py)`.
  The build turns them into links to the tagged release, so a reader always sees
  the version that the publication describes. Write folders with a trailing `/`:
  the build then uses GitHub's folder view. Links to other sites are written in full.
- **Checking the links.** `tests/check-publication-links.py` checks that every
  relative link points to a file or folder that exists. It runs with the profile
  tests. In the GitHub workflow it also runs with `--online`, which requests every
  external link.
- **Code.** Technical terms use inline code (backticks), which the build turns into
  the `Code Char` style. Code blocks use three backticks and become the `Code` style.
- **Table column widths** are set by the number of dashes in each column of the
  separator row under the table header. The dashes in a row add up to about 100,
  so each count is a percentage of the text width.
- **Images** go in `src/media/<short>/`, with the size given after the image,
  for example `{width="6.0in"}`.
- **Straight quotation marks** are kept as they are. The build does not turn
  them into curly quotation marks, because the originals use straight ones.

## Move from Word to Markdown

Each publication is converted with `convert.py`, rebuilt, and checked with
`compare.py` against the original Word file. A publication is switched to its
Markdown source only when the comparison shows the same paragraphs, styles,
tables, images, emphasis and links.

| Document | Source | Status |
|---|---|---|
| Publication 1, Foundations | `src/publication-1-foundations.md` | Converted, checked |
| Publication 2, Profiles and conformance | `src/publication-2-profiles-and-conformance.md` | Converted, checked, 5 files linked |
| Publication 3, Applying the methodology | `src/publication-3-applying-the-methodology.md` | Converted, checked, 56 files linked |
| Application domain: Operational technology | `src/domain-operational-technology.md` | Converted, checked, 3 files linked |
| Application domain: SaaS and cloud services | `src/domain-saas-and-cloud-services.md` | Converted, checked, 2 files linked |
| Application domain: Telecommunications | `src/domain-telecommunications.md` | Converted, checked, 2 folders linked |

"Checked" means that `compare.py` found the same paragraphs, paragraph styles,
tables, table rows, images, bold and italic text, inline code and code blocks as
in the original Word file. Adding the links changed no text. The Word files in
`docs/assets/publications/` are still the originals until the first build
replaces them.
