"""Compares two .docx files paragraph by paragraph.

Used during the move from Word to Markdown sources: the original .docx and
the .docx rebuilt from Markdown must carry the same text, styles, tables,
images and links.

Usage: python3 publications/compare.py ORIGINAL.docx REBUILT.docx
"""
import difflib, html, re, sys, zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()

def load(path):
    z = zipfile.ZipFile(path)
    x = z.read("word/document.xml").decode("utf8")
    rels = z.read("word/_rels/document.xml.rels").decode("utf8")
    body = x[x.index("<w:body>"):]
    paras = []
    for m in re.finditer(r"<w:p[ >].*?</w:p>", body, re.S):
        p = m.group(0)
        text = re.sub(r"<[^>]+>", "", re.sub(r"<w:tab/>", " ", p))
        text = html.unescape(text)
        text = norm(text)
        style = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        style = style.group(1) if style else ""
        if style.startswith("Heading"):
            kind = style
        elif "<w:numPr>" in p or style in ("ListParagraph", "Compact") and "<w:numPr>" in p:
            kind = "list"
        else:
            kind = "body"
        if text:
            paras.append((kind, text))
    links = sorted(set(re.findall(r'Target="(https?://[^"]+)"', rels)))
    return {
        "paras": paras,
        "tables": len(re.findall(r"<w:tbl>", body)),
        "rows": len(re.findall(r"<w:tr[ >]", body)),
        "images": len(re.findall(r"<a:blip ", body)),
        "links": links,
        "code": [norm(html.unescape(re.sub(r"<[^>]+>", "", r))) for r in re.findall(r'<w:r>(?:(?!</w:r>).)*?<w:rStyle w:val="CodeChar" ?/>.*?</w:r>', body, re.S)],
        "codeblocks": [html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<w:br ?/>", "\n", p))) for p in re.findall(r'<w:p>(?:(?!</w:p>).)*?<w:pStyle w:val="Code" ?/>.*?</w:p>', body, re.S)],
        "bold": len(re.findall(r"<w:b(?: w:val=\"(?:true|1|on)\")? ?/>", body)),
        "italic": len(re.findall(r"<w:i(?: w:val=\"(?:true|1|on)\")? ?/>", body)),
    }

a, b = load(sys.argv[1]), load(sys.argv[2])
ta = [t for _, t in a["paras"]]
tb = [t for _, t in b["paras"]]
sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
print(f"paragraphs  {len(ta):5} {len(tb):5}  text match {sm.ratio():.4f}")
for k in ("tables", "rows", "images", "bold", "italic"):
    print(f"{k:11} {a[k]:5} {b[k]:5}")
print(f"links       {len(a['links']):5} {len(b['links']):5}")
ca, cb = "".join(a["code"]).replace(" ", ""), "".join(b["code"]).replace(" ", "")
print(f"code text   {len(ca):5} {len(cb):5}  {'same' if ca == cb else 'DIFFERENT'}")
print(f"codeblocks  {len(a['codeblocks']):5} {len(b['codeblocks']):5}  {'same' if a['codeblocks'] == b['codeblocks'] else 'DIFFERENT'}")
if a["links"] != b["links"]:
    print("  links only in original:", sorted(set(a["links"]) - set(b["links"])))
    print("  links only in rebuilt: ", sorted(set(b["links"]) - set(a["links"])))
kinds = lambda d: [k for k, _ in d["paras"]]
ka, kb = kinds(a), kinds(b)
same_kind = sum(1 for (x, y) in zip(ka, kb) if x == y) if ta == tb else None
if same_kind is not None:
    print(f"kind match  {same_kind}/{len(ka)}")
    for (x, t), (y, _) in zip(a["paras"], b["paras"]):
        if x != y:
            print(f"  kind {x} -> {y}: {t[:70]}")
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal":
        print(f"--- {tag}")
        for t in ta[i1:i2]: print("  - " + t[:160])
        for t in tb[j1:j2]: print("  + " + t[:160])
