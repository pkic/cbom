"""One-off conversion of a publication from .docx to the Markdown source.

Runs pandoc, extracts the images into src/media/<short>/, and writes each
table's column widths from the original into the Markdown separator row, so
that the widths are kept in the source and can be edited there.

Usage: python3 publications/convert.py ORIGINAL.docx src/NAME.md SHORT
"""
import re, subprocess, sys, zipfile, os

docx, out, short = os.path.abspath(sys.argv[1]), os.path.basename(sys.argv[2]), sys.argv[3]
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(here, "src"))

md = subprocess.run(
    ["pandoc", docx, "-t", "markdown-smart-simple_tables-multiline_tables-grid_tables",
     "--wrap=none"], check=True, capture_output=True, text=True).stdout

# Images: extract with unzip-equivalent and point the Markdown at them.
z = zipfile.ZipFile(docx)
os.makedirs(f"media/{short}", exist_ok=True)
for n in z.namelist():
    if n.startswith("word/media/"):
        with open(f"media/{short}/{os.path.basename(n)}", "wb") as f:
            f.write(z.read(n))
md = re.sub(r"\]\((?:[^)]*/)?media/(image\d+\.\w+)\)", rf"](media/{short}/\1)", md)

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
print(f"wrote src/{out}: {t} tables, {len(os.listdir('media/' + short))} images")
