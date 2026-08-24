#!/usr/bin/env python3
"""Rewrite the previous/next links at the foot of every methodology page.

The reading order lives in docs/_data/methodology_nav.yml. Before this script
existed the footer links were maintained by hand, which meant reordering a
section silently left them pointing at the old neighbours. Run this after any
change to the order in that file.

No third-party dependencies: the nav file is a fixed shape and is parsed with
a small reader rather than PyYAML, so the script runs anywhere Python does.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAV = ROOT / "docs" / "_data" / "methodology_nav.yml"
PAGES = ROOT / "docs" / "methodology"

ITEM = re.compile(
    r"^\s*-\s*\{\s*id:\s*(?P<id>[\w-]+)\s*,"
    r"\s*title:\s*(?P<title>.+?)\s*,"
    r"\s*url:\s*(?P<url>\S+?)\s*\}\s*$"
)
BLOCK = re.compile(r'(<div class="pagenav">)(.*?)(</div>)', re.DOTALL)


def read_order() -> list[tuple[str, str, str]]:
    order = []
    for line in NAV.read_text(encoding="utf-8").splitlines():
        m = ITEM.match(line)
        if m:
            order.append((m["id"], m["title"], m["url"]))
    return order


def links(order):
    """Yield (page_path, previous_html, next_html) for each local page."""
    for i, (_id, _title, url) in enumerate(order):
        if not url.endswith(".html"):
            continue  # the reference register lives outside this directory
        prev_html = "<span></span>"
        if i > 0:
            _pid, ptitle, purl = order[i - 1]
            prev_html = f'<a href="{purl}">← {ptitle}</a>'
        next_html = "<span></span>"
        if i + 1 < len(order):
            _nid, ntitle, nurl = order[i + 1]
            label = "the reference register" if not nurl.endswith(".html") else ntitle
            next_html = f'<a class="next" href="{nurl}">Next: {label} →</a>'
        yield PAGES / url, prev_html, next_html


def main() -> int:
    order = read_order()
    if not order:
        print(f"no nav items parsed from {NAV}", file=sys.stderr)
        return 1

    changed, untouched, missing = [], [], []
    for path, prev_html, next_html in links(order):
        if not path.exists():
            missing.append(path.name)
            continue
        text = path.read_text(encoding="utf-8")
        replacement = f"\\1\n    {prev_html}\n    {next_html}\n  \\3"
        new, n = BLOCK.subn(replacement, text, count=1)
        if n == 0:
            missing.append(f"{path.name} (no pagenav block)")
        elif new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(path.name)
        else:
            untouched.append(path.name)

    print(f"{len(changed)} rewritten, {len(untouched)} already correct")
    for name in changed:
        print(f"  updated  {name}")
    for name in missing:
        print(f"  MISSING  {name}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
