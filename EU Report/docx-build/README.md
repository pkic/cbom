# Word build

The markdown is the master. This turns it into the .docx.

```bash
./build.sh
```

It reads `../Cryptographic-Transparency-in-the-Supply-Chain.md` (the file `publish.py`
writes) and `../figures/`, and writes `../Cryptographic-Transparency-in-the-Supply-Chain.docx`.

Needs `pandoc`, `python3`, `zip` and `unzip`.

## What each piece does

**`mkpandoc.py`** turns the published markdown into pandoc input. It lifts the title
block into YAML metadata, sets the version row, drops the markdown contents list
(Word gets a real field instead), and gives every figure `{width=16cm}`, which is the
text column.

**`reference.docx`** carries the page setup and styles: A4, 2.5 cm margins, Cambria
body over Calibri headings, chapter headings starting a new page, 9 pt table text,
and a centred page-number footer that is suppressed on the title page.

**`fixtables.py`** sizes the table columns. Pandoc emits no widths, and Word's autofit
gives a six-column table a ten-character "Recommendation" column. This measures the
text in each column, classifies each one as either a label column that must not wrap
or a prose column that may, guarantees the label columns their width, and shares what
is left among the rest. It also drops inline code from 11 pt to 8.5 pt, so `Consolas`
in a table matches the Cambria around it.

**`fixtoc.py`** inserts a real `TOC \o "1-2" \h \z \u` field before "How to read this
report". Word shows placeholder text until someone right-clicks and chooses Update
Field; after that it is a live, clickable contents list with page numbers.

## Checking a build

```bash
soffice --headless --convert-to pdf ../Cryptographic-Transparency-in-the-Supply-Chain.docx
```

LibreOffice substitutes Caladea for Cambria and Carlito for Calibri. Both are
metric-compatible, so the pagination matches what Word will show.
