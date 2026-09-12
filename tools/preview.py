#!/usr/bin/env python3
"""Preview the hand-written documentation sections without installing Jekyll.

Two sections of the site are hand-written HTML rather than Markdown: the
methodology under docs/methodology/, and the worked use cases under
docs/use-cases/. Each page carries a two-line front matter block and exactly
one Liquid tag, the navigation include for its own section. Opening them
straight from the filesystem therefore shows the front matter as text and no
navigation, which is why this exists.

This script does the two things Jekyll does to those pages — strip the front
matter, expand the navigation include from the section's data file — writes the
result to .preview/ under the same directory names, and serves it. Keeping the
directory names is what makes the cross-section links (../methodology/… and
../use-cases/…) resolve in the preview as they do on the published site.

It is NOT a Jekyll substitute: it does not render the Markdown pages (index.md,
issues.md, contributing.md, references.md), does not apply layouts, and does not
resolve relative_url. For those, and before publishing anything, use Jekyll:

    bundle install
    bundle exec jekyll serve --source docs

If a page ever grows a second kind of Liquid tag, this script says so rather
than rendering it wrongly.

    python3 tools/preview.py              # build and serve on :8000
    python3 tools/preview.py --port 4000
    python3 tools/preview.py --no-serve   # build only
"""

from __future__ import annotations

import argparse
import functools
import http.server
import re
import shutil
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# One entry per hand-written section: its directory under docs/, the data file
# holding its navigation, the include tag its pages call, and the aria-label the
# real include renders. Adding a section means adding a line here.
SECTIONS = (
    ("methodology", "methodology_nav.yml", "{% include methodology-nav.html %}", "Methodology sections"),
    ("use-cases", "usecases_nav.yml", "{% include usecases-nav.html %}", "Use case sections"),
)
LANDING = "methodology/introduction.html"

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAV_ID = re.compile(r"^nav:\s*([\w-]+)", re.MULTILINE)
GROUP = re.compile(r"^-\s*group:\s*(.+?)\s*$")
ITEM = re.compile(
    r"^\s*-\s*\{\s*id:\s*(?P<id>[\w-]+)\s*,"
    r"\s*title:\s*(?P<title>.+?)\s*,"
    r"\s*url:\s*(?P<url>\S+?)\s*\}\s*$"
)
LIQUID = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.DOTALL)
# A redirect stub left behind at a published URL whose page has moved. It has no
# front matter and no navigation, deliberately, and is copied through.
REDIRECT = re.compile(r'<meta\s+http-equiv="refresh"', re.IGNORECASE)


def read_nav(nav: Path) -> list[tuple[str, list[tuple[str, str, str]]]]:
    """Return [(group title, [(id, title, url), ...]), ...] from a data file."""
    groups: list[tuple[str, list]] = []
    for line in nav.read_text(encoding="utf-8").splitlines():
        g = GROUP.match(line)
        if g:
            groups.append((g.group(1), []))
            continue
        m = ITEM.match(line)
        if m and groups:
            groups[-1][1].append((m["id"], m["title"], m["url"]))
    return groups


def render_nav(groups, current: str | None, label: str) -> str:
    """Reproduce a section's navigation include for one page."""
    out = [f'<aside class="sidenav" aria-label="{label}">']
    for name, items in groups:
        out.append(f'  <div class="sidenav-group">{name}</div>')
        out.append("  <ul>")
        for item_id, title, url in items:
            active = ' class="active" aria-current="page"' if item_id == current else ""
            out.append(f'    <li><a href="{url}"{active}>{title}</a></li>')
        out.append("  </ul>")
    out.append("</aside>")
    return "\n".join(out)


def build_section(name: str, nav_file: str, include: str, label: str,
                  out_dir: Path, warnings: list[str]) -> tuple[int, int]:
    src = DOCS / name
    groups = read_nav(DOCS / "_data" / nav_file)
    if not groups:
        warnings.append(f"{nav_file}: no navigation entries parsed")
        return 0, 0

    # Overwrite in place rather than clearing the directory first. Deleting is
    # not available on every filesystem this repository gets mounted on, and a
    # rebuild that dies halfway through the delete leaves no output at all.
    # Anything left over from a previous build is reported instead of removed.
    before = {p.name for p in out_dir.iterdir()} if out_dir.exists() else set()
    out_dir.mkdir(parents=True, exist_ok=True)

    pages, assets, written = 0, 0, set()
    for path in sorted(src.iterdir()):
        if path.is_dir():
            continue
        if path.suffix != ".html":
            shutil.copy2(path, out_dir / path.name)  # styles.css, the JSON, the scripts
            written.add(path.name)
            assets += 1
            continue

        text = path.read_text(encoding="utf-8")
        if REDIRECT.search(text):
            shutil.copy2(path, out_dir / path.name)
            written.add(path.name)
            assets += 1
            continue

        fm = FRONT_MATTER.match(text)
        current = None
        if fm:
            found = NAV_ID.search(fm.group(1))
            current = found.group(1) if found else None
            text = text[fm.end():]
        else:
            warnings.append(f"{name}/{path.name}: no front matter, so no page is marked current")

        if include in text:
            text = text.replace(include, render_nav(groups, current, label))
        else:
            warnings.append(f"{name}/{path.name}: no navigation include")

        leftover = {t.strip() for t in LIQUID.findall(text)}
        if leftover:
            warnings.append(
                f"{name}/{path.name}: Liquid this script does not handle, shown raw: "
                + ", ".join(sorted(leftover)[:3])
            )

        (out_dir / path.name).write_text(text, encoding="utf-8")
        written.add(path.name)
        pages += 1

    stale = sorted(before - written)
    if stale:
        warnings.append(f"{name}/: {len(stale)} file(s) left from a previous build and no longer "
                        f"produced: {', '.join(stale)}")
    return pages, assets


def build(out_dir: Path) -> int:
    warnings: list[str] = []
    total_pages = total_assets = 0
    for name, nav_file, include, label in SECTIONS:
        pages, assets = build_section(name, nav_file, include, label, out_dir / name, warnings)
        total_pages += pages
        total_assets += assets
        print(f"  {name}/: {pages} pages, {assets} assets")

    if not total_pages:
        print("error: no pages were built", file=sys.stderr)
        for w in warnings:
            print(f"  warning: {w}", file=sys.stderr)
        return 1

    print(f"built {total_pages} pages and {total_assets} assets into "
          f"{out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}/")
    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)
    return 0


def serve(out_dir: Path, port: int) -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out_dir))
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
            print(f"\n  http://localhost:{port}/{LANDING}")
            print("  Ctrl-C to stop. Re-run this script after editing a page.\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    except OSError as e:
        print(f"error: could not listen on port {port}: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / ".preview"), help="build directory (default: .preview)")
    ap.add_argument("--port", type=int, default=8000, help="port to serve on (default: 8000)")
    ap.add_argument("--no-serve", action="store_true", help="build and exit")
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    rc = build(out_dir)
    if rc or args.no_serve:
        return rc
    return serve(out_dir, args.port)


if __name__ == "__main__":
    raise SystemExit(main())
