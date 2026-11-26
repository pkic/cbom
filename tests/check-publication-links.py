"""Checks the links in the Markdown sources of the publications.

Every relative link must point to a file or folder that exists in the
repository. The build rewrites these links to the release tag, so a link
that resolves here also resolves at the tag, provided the tag is set on the
commit that is checked.

With --online, every external link is also requested, and a link that does
not answer with a success status is reported. The online check needs
network access and runs in the GitHub workflow.

Usage: python3 tests/check-publication-links.py [--online]
"""
import glob, os, re, sys, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "publications", "src")
LINK = re.compile(r"(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

failures, external, checked = [], set(), 0
for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
    name = os.path.basename(path)
    in_code = False
    for n, line in enumerate(open(path, encoding="utf8"), 1):
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        for target in LINK.findall(line):
            if target.startswith("#") or target.startswith("mailto:"):
                continue
            if re.match(r"^[a-z][a-z0-9+.-]*:", target):
                external.add(target)
                continue
            checked += 1
            full = os.path.normpath(os.path.join(SRC, target))
            if not full.startswith(ROOT + os.sep):
                failures.append(f"{name}:{n}: {target} points outside the repository")
            elif not os.path.exists(full):
                failures.append(f"{name}:{n}: {target} does not exist")
            elif target.endswith("/") != os.path.isdir(full):
                failures.append(f"{name}:{n}: {target} is a {'folder' if os.path.isdir(full) else 'file'}; "
                                f"write folders with a trailing / and files without one")

if "--online" in sys.argv:
    for url in sorted(external):
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "pkic-cbom-link-check"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status >= 400:
                    failures.append(f"{url}: HTTP {r.status}")
        except Exception as e:
            failures.append(f"{url}: {e}")

for f in failures:
    print("FAIL " + f)
print(f"{checked} repository links and {len(external)} external links in "
      f"{len(glob.glob(os.path.join(SRC, '*.md')))} publications"
      + ("" if "--online" in sys.argv else " (external links not requested; use --online)")
      + f": {len(failures)} problems")
sys.exit(1 if failures else 0)
