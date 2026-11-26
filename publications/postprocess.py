"""Applies the house layout to a .docx that pandoc has built.

pandoc writes its own paragraph styles (BodyText, FirstParagraph, Compact)
and its own table style. This script maps them onto the styles that the
publications use: Normal paragraphs, ListParagraph for list items, and
TableGrid tables with a shaded header row that repeats on each page.
Column widths come from the Markdown separator rows.

Usage: python3 publications/postprocess.py FILE.docx
"""
import re, sys, zipfile, shutil, tempfile

TEXT_WIDTH = 9360  # twentieths of a point: page width less both margins

def fix_tables(x):
    def one(m):
        t = m.group(0)
        grid = [float(v) for v in re.findall(r'<w:gridCol w:w="([\d.]+)"', t)]
        if not grid:
            ncols = len(re.findall(r"<w:tc>", re.search(r"<w:tr[ >].*?</w:tr>", t, re.S).group(0)))
            grid = [1.0] * ncols
        dxa = [round(TEXT_WIDTH * g / sum(grid)) for g in grid]
        t = re.sub(r"<w:tblPr>.*?</w:tblPr>",
                   '<w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
                   '<w:tblLayout w:type="fixed"/><w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" '
                   'w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>', t, count=1, flags=re.S)
        t = re.sub(r"<w:tblGrid>.*?</w:tblGrid>",
                   "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{d}"/>' for d in dxa) + "</w:tblGrid>", t, count=1, flags=re.S)
        rows = re.findall(r"<w:tr[ >].*?</w:tr>", t, re.S)
        for ri, row in enumerate(rows):
            header = "cnfStyle" in row and ri == 0
            new = re.sub(r"<w:trPr>.*?</w:trPr>", "<w:trPr><w:tblHeader/></w:trPr>" if header else "", row, flags=re.S)
            ci = iter(range(10**6))
            def cell(cm):
                i = next(ci)
                w = dxa[i] if i < len(dxa) else dxa[-1]
                shd = '<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>' if header else ""
                return f'<w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shd}</w:tcPr>'
            new = re.sub(r"<w:tcPr>.*?</w:tcPr>", cell, new, flags=re.S)
            t = t.replace(row, new, 1)
        return t
    return re.sub(r"<w:tbl>.*?</w:tbl>", one, x, flags=re.S)

def fix_code(x):
    # Code blocks: pandoc's SourceCode paragraph becomes the Code style,
    # with plain runs inside, as in the originals.
    def block(m):
        p = m.group(0).replace('<w:pStyle w:val="SourceCode" />', '<w:pStyle w:val="Code"/>')
        return re.sub(r'<w:rPr><w:rStyle w:val="VerbatimChar" ?/></w:rPr>', "", p)
    x = re.sub(r'<w:p>(?:(?!</w:p>).)*?<w:pStyle w:val="SourceCode" ?/>.*?</w:p>', block, x, flags=re.S)
    # Inline code: VerbatimChar becomes the Code Char style.
    return re.sub(r'<w:rStyle w:val="VerbatimChar" ?/>', '<w:rStyle w:val="CodeChar"/>', x)

def fix_paragraphs(x):
    x = re.sub(r'<w:pStyle w:val="(?:BodyText|FirstParagraph|Compact)" ?/>', "", x)
    x = re.sub(r'<w:jc w:val="left" ?/>', "", x)
    # List items: give them the ListParagraph style, as in the originals.
    x = re.sub(r"<w:pPr>(<w:numPr>)", r'<w:pPr><w:pStyle w:val="ListParagraph"/>\1', x)
    return x

path = sys.argv[1]
z = zipfile.ZipFile(path)
x = z.read("word/document.xml").decode("utf8")
x = fix_paragraphs(fix_code(fix_tables(x)))
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
    for item in z.infolist():
        data = x.encode("utf8") if item.filename == "word/document.xml" else z.read(item.filename)
        out.writestr(item, data)
z.close()
shutil.move(tmp, path)
