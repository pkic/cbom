"""One-off conversion of a publication from .docx to the Markdown source.

Runs pandoc, extracts the images into src/media/<short>/, and writes each
table's column widths from the original into the Markdown separator row, so
that the widths are kept in the source and can be edited there.

Usage: python3 publications/convert.py ORIGINAL.docx src/NAME.md SHORT
"""
import html, re, subprocess, sys, zipfile, os

docx, out, short = os.path.abspath(sys.argv[1]), os.path.basename(sys.argv[2]), sys.argv[3]
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(here, "src"))

md = subprocess.run(
    ["pandoc", "-f", "docx+styles", docx, "-t", "markdown-smart-simple_tables-multiline_tables-grid_tables",
     "--wrap=none"], check=True, capture_output=True, text=True).stdout

# Images: extract with unzip-equivalent and point the Markdown at them.
z = zipfile.ZipFile(docx)
os.makedirs(f"media/{short}", exist_ok=True)
for n in z.namelist():
    if n.startswith("word/media/"):
        with open(f"media/{short}/{os.path.basename(n)}", "wb") as f:
            f.write(z.read(n))
md = re.sub(r"\]\((?:[^)]*/)?media/(image\d+\.\w+)\)", rf"](media/{short}/\1)", md)

# Inline code: the originals use the "Code Char" character style for
# technical terms. pandoc marks these as spans; turn them into backticks.
def inline(m):
    t = re.sub(r"\\(.)", r"\1", m.group(1))
    return "``" + t + "``" if "`" in t else "`" + t + "`"
md, n_inline = re.subn(r'\[((?:[^\[\]\\]|\\.)*)\]\{custom-style="Code Char"\}', inline, md)
md = re.sub(r'\[((?:[^\[\]\\]|\\.)*)\]\{custom-style="Hyperlink"\}', r"\1", md)

# Code paragraphs: take the exact text from the original, so that spacing
# and line breaks survive, and write it as a fenced code block.
x = z.read("word/document.xml").decode("utf8")
blocks = []
for p in re.findall(r'<w:p><w:pPr><w:pStyle w:val="Code"/>.*?</w:p>', x, re.S):
    p = re.sub(r"<w:br/>", "\n", p)
    p = re.sub(r"<w:tab/>", "\t", p)
    blocks.append(html.unescape(re.sub(r"<[^>]+>", "", p)))
divs = list(re.finditer(r'::: \{custom-style="Code"\}\n.*?\n:::', md, re.S))
if len(divs) != len(blocks):
    print(f"warning: {len(divs)} code blocks in Markdown, {len(blocks)} in original")
for d, b in reversed(list(zip(divs, blocks))):
    md = md[:d.start()] + "```\n" + b + "\n```" + md[d.end():]
# List items: pandoc wraps each item in a "List Paragraph" div. Remove the
# wrapper; the list itself carries the style at build time.
def unwrap(m):
    ind, body = m.group(1), m.group(2)
    lines = body.rstrip("\n").split("\n")
    return lines[0] + ("\n" + "\n".join(lines[1:]) if len(lines) > 1 else "")
md = re.sub(r'::: \{custom-style="List Paragraph"\}\n( *)((?:.*\n)*?)\1:::', unwrap, md)
left = re.findall(r'custom-style="([^"]+)"', md)
if left:
    print("styles left in the Markdown:", sorted(set(left)))

# Table widths from the original, in document order.
x = z.read("word/document.xml").decode("utf8")
widths = [[int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"', g)]
          for g in re.findall(r"<w:tblGrid>(.*?)</w:tblGrid>", x, re.S)]
lines = md.split("\n")
t = 0
for i, line in enumerate(lines):
    if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", line.strip()):
        cols = line.strip().strip("|").split("|")
        w = widths[t] if t < len(widths) else []
        t += 1
        if len(w) != len(cols):
            print(f"table {t}: {len(cols)} columns in Markdown, {len(w)} widths in original; left as is")
            continue
        dashes = [max(3, round(100 * v / sum(w))) for v in w]
        lines[i] = "|" + "|".join("-" * d for d in dashes) + "|"
md = "\n".join(lines)
if t != len(widths):
    print(f"warning: {t} tables in Markdown, {len(widths)} in original")
open(out, "w").write(md)
print(f"wrote src/{out}: {n_inline} inline code terms, {len(blocks)} code blocks, {t} tables, {len(os.listdir('media/' + short))} images")
