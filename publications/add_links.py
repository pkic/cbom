"""Turns file and folder names in the publications into links.

A name written as inline code, such as `validate_cbom.py`, is linked when it
matches exactly one file or folder in the repository. Each name is linked at
its first mention in each chapter (each heading of level 1 or 2). Command
lines, code blocks, names that are already links, and names that match no
file or more than one file are left as text and listed in the report.

Usage: python3 publications/add_links.py src/FILE.md [...]
"""
import os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP = {".git", ".preview", "_originals_2026-11-11", "publications", "_to_delete",
        "EU Report", "Claude outputs", "__pycache__", "node_modules", "_site"}
PREFER = ["docs/methodology/examples/", "docs/", "tools/", "tests/", "schemas/", "drafts/", ""]

files, dirs = [], []
for d, ds, fs in os.walk(ROOT):
    ds[:] = [x for x in ds if x not in SKIP and not x.startswith("_build")]
    rel = os.path.relpath(d, ROOT).replace(os.sep, "/")
    rel = "" if rel == "." else rel + "/"
    dirs += [rel + x + "/" for x in ds]
    files += [rel + f for f in fs]

def resolve(term):
    t = term.strip()
    if re.match(r"^(python3?|bash|sh|\./)\s", t) or " " in t:
        return None, "command or phrase"
    if t.startswith("…"):
        suffix = t[1:]
        cands = [f for f in files if f.endswith(suffix)]
    elif t.endswith("/"):
        cands = [d for d in dirs if d == t or d.endswith("/" + t)]
    elif "/" in t:
        cands = [f for f in files if f == t or f.endswith("/" + t)]
    else:
        cands = [f for f in files if f.rsplit("/", 1)[-1] == t]
    if not cands:
        return None, "no match"
    for root in PREFER:
        pick = [c for c in cands if c.startswith(root)]
        if pick:
            if len(pick) == 1:
                return pick[0], None
            return None, "ambiguous: " + ", ".join(pick[:4])
    return None, "no match"

HEADING = re.compile(r"^(#{1,2} |[^\n]+\n[=-]{3,}$)")
def is_heading(lines, i):
    return lines[i].startswith(("# ", "## ")) or (
        i + 1 < len(lines) and lines[i].strip() and re.fullmatch(r"[=-]{3,}", lines[i + 1].strip())
        and not lines[i].startswith("|"))

report = {}
for path in sys.argv[1:]:
    lines = open(path).read().split("\n")
    seen, in_code, linked = set(), False, 0
    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if is_heading(lines, i):
            seen = set()
            continue
        def sub(m):
            global linked_count
            term = m.group(1)
            if not re.search(r"\.(json|py|sh|md|yml|yaml)$|/$", term.strip()):
                return m.group(0)
            target, why = resolve(term)
            if not target:
                report.setdefault(why if not why.startswith("ambiguous") else "ambiguous", set()).add(
                    (os.path.basename(path), term, why))
                return m.group(0)
            if term in seen:
                return m.group(0)
            seen.add(term)
            nonlocal_count[0] += 1
            return f"[`{term}`](../../{target})"
        nonlocal_count = [0]
        # Skip code that is already inside a link: `[`x`](...)`.
        lines[i] = re.sub(r"(?<!\[)`([^`]+)`(?!\]\()", sub, line)
        linked += nonlocal_count[0]
    open(path, "w").write("\n".join(lines))
    print(f"{os.path.basename(path)}: {linked} links added")
for why, items in sorted(report.items()):
    if why == "command or phrase":
        continue
    print(f"\nLeft as text ({why}):")
    for f, term, detail in sorted(items):
        print(f"  {f}: {term}" + (f"  [{detail}]" if detail != why else ""))
