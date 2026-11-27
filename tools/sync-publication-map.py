#!/usr/bin/env python3
"""Keep the methodology pages in step with the Release 1 publications.

docs/_data/methodology_pubmap.yml says which chapter of which publication each
methodology page explains. This script writes, from that file:

  * on every mapped page, the breadcrumb (for example "PUBLICATION 2 · PROFILES AND CONFORMANCE")
    and a banner after the page title that names the chapter and links to the
    publication, which is the authoritative text;
  * on the Overview (index.html), the map from publications and chapters to pages,
    between the markers <!-- pubmap:start --> and <!-- pubmap:end -->.

It also checks that every page in the section navigation is mapped, so that a new
page cannot be added without saying which chapter it explains.

No third-party dependencies: the data file holds one JSON object per line.

Usage:  python3 tools/sync-publication-map.py           rewrite the pages
        python3 tools/sync-publication-map.py --check   exit 1 if any page is out of step
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "_data" / "methodology_pubmap.yml"
NAV = ROOT / "docs" / "_data" / "methodology_nav.yml"
PAGES = ROOT / "docs" / "methodology"
DOWNLOADS = "../assets/publications/"
UNMAPPED = {"index"}  # the Overview introduces the section and belongs to no chapter

CRUMB = re.compile(r'<div class="crumb">.*?</div>', re.S)
BANNER = re.compile(r'\n?\s*<div class="pubref">.*?</div>\s*<!-- /pubref -->', re.S)
H1_END = re.compile(r"</h1>")
MAP = re.compile(r"(<!-- pubmap:start -->).*?(<!-- pubmap:end -->)", re.S)


def read_data():
    pubs, pages, section = {}, [], None
    for line in DATA.read_text(encoding="utf-8").splitlines():
        if line.startswith("publications:"):
            section = "pubs"
        elif line.startswith("pages:"):
            section = "pages"
        elif line.startswith("- {"):
            obj = json.loads(line[2:])
            if section == "pubs":
                pubs[obj["pub"]] = obj
            else:
                pages.append(obj)
    return pubs, pages


def nav_pages():
    """id -> url for every local page in the section navigation."""
    out = {}
    for m in re.finditer(r"\{\s*id:\s*([\w-]+)\s*,\s*title:\s*.+?,\s*url:\s*(\S+?)\s*\}", NAV.read_text(encoding="utf-8")):
        if m.group(2).endswith(".html") and "/" not in m.group(2):
            out[m.group(1)] = m.group(2)
    return out


def where(p):
    """'Chapter 9', 'Sections 4.1–4.2 of chapter 4', 'Annex D' and so on."""
    unit = "annex" if not p["ch"].isdigit() else "chapter"
    if p["sections"]:
        label = "Section" + ("s" if "–" in p["sections"] or "," in p["sections"] else "")
        return "%s %s of %s %s" % (label, p["sections"], unit, p["ch"])
    return "%s %s" % (unit.capitalize(), p["ch"])


def crumb(p, pub):
    return '<div class="crumb">PUBLICATION %d · %s</div>' % (p["pub"], html.escape(pub["title"].upper()))


def banner(p, pub):
    return ('\n  <div class="pubref"><span class="pubref-where">%s</span> '
            "This page explains %s, <em>%s</em>, of <em>%s</em>, with diagrams, worked examples and checks "
            "you can run. The publication is the authoritative text: where the two differ, the publication "
            'applies. <a href="%s%s" download>Download Publication %d (Word)</a></div><!-- /pubref -->'
            % (html.escape(where(p)), html.escape(where(p)[0].lower() + where(p)[1:]),
               html.escape(p["chapter"]), html.escape(pub["title"]), DOWNLOADS, pub["file"], p["pub"]))


def overview_map(pubs, pages, urls):
    out = ["<!-- pubmap:start -->"]
    for n in sorted(pubs):
        pub = pubs[n]
        out.append('  <div class="pubmap">')
        out.append('    <div class="pubmap-head"><div><span class="pubmap-num">Publication %d</span><h3>%s</h3>'
                   '<p>%s</p></div><a class="pubmap-dl" href="%s%s" download>Download (Word)</a></div>'
                   % (n, html.escape(pub["title"]), html.escape(pub["covers"]), DOWNLOADS, pub["file"]))
        out.append('    <div class="cards">')
        for p in pages:
            if p["pub"] != n:
                continue
            num = ("§ " + p["sections"]) if p["sections"] else ("Chapter " + p["ch"])
            if not p["ch"].isdigit() and not p["sections"]:
                num = "Annex " + p["ch"]
            title = nav_titles().get(p["id"], p["id"])
            out.append('      <a class="card" href="%s"><div class="num">%s</div><h3>%s</h3><p>%s</p></a>'
                       % (urls[p["id"]], html.escape(num), html.escape(title), html.escape(p["summary"])))
        out.append("    </div>")
        out.append("  </div>")
    out.append("  <!-- pubmap:end -->")
    return "\n".join(out)


def nav_titles():
    out = {}
    for m in re.finditer(r"\{\s*id:\s*([\w-]+)\s*,\s*title:\s*(.+?)\s*,\s*url:", NAV.read_text(encoding="utf-8")):
        out[m.group(1)] = re.sub(r"^[0-9A-Z]+ · ", "", m.group(2))
    return out


def main():
    check = "--check" in sys.argv
    pubs, pages = read_data()
    urls = nav_pages()
    problems, changed = [], []
    mapped = {p["id"] for p in pages}
    for pid in urls:
        if pid not in mapped and pid not in UNMAPPED:
            problems.append("%s is in the navigation but not in methodology_pubmap.yml" % pid)
    for p in pages:
        if p["id"] not in urls:
            problems.append("%s is in methodology_pubmap.yml but not in the navigation" % p["id"])
            continue
        path = PAGES / urls[p["id"]]
        old = path.read_text(encoding="utf-8")
        new = BANNER.sub("", old)
        if not CRUMB.search(new) or not H1_END.search(new):
            problems.append("%s has no breadcrumb or no <h1>" % path.name)
            continue
        new = CRUMB.sub(crumb(p, pubs[p["pub"]]), new, count=1)
        new = H1_END.sub("</h1>" + banner(p, pubs[p["pub"]]), new, count=1)
        if new != old:
            changed.append(path)
            if not check:
                path.write_text(new, encoding="utf-8", newline="\n")
    index = PAGES / "index.html"
    old = index.read_text(encoding="utf-8")
    if not MAP.search(old):
        problems.append("index.html has no <!-- pubmap:start --> ... <!-- pubmap:end --> block")
    else:
        new = MAP.sub(lambda m: overview_map(pubs, pages, urls), old, count=1)
        if new != old:
            changed.append(index)
            if not check:
                index.write_text(new, encoding="utf-8", newline="\n")
    for pr in problems:
        print("  problem: " + pr)
    if check:
        for c in changed:
            print("  out of step: %s (run python3 tools/sync-publication-map.py)" % c.name)
        print("%d page(s) mapped, %d out of step, %d problem(s)" % (len(pages), len(changed), len(problems)))
        return 1 if changed or problems else 0
    print("%d page(s) rewritten, %d problem(s)" % (len(changed), len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
