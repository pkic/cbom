#!/usr/bin/env python3
"""Integrity checks for the site data files that carry meetings and presentations.

Jekyll will happily build a page with a download link to a file that is not
there, a presentation attached to a meeting that does not exist, or a deck with
neither a file nor a URL. None of those fail the build; all of them are visible
to a visitor. This checks them before they ship.

    python3 tests/check-site-data.py

Exit status is 0 when every check passes and 1 otherwise. Placeholder entries
marked `example: true` are reported as a reminder but are not failures — the
site is expected to ship with them until real meetings exist.
"""

import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "_data")
DECKS = os.path.join(ROOT, "docs", "assets", "presentations")

passed = 0
failures = []
notes = []


def ok(label):
    global passed
    passed += 1
    print("    ok   %s" % label)


def bad(label, detail):
    failures.append((label, detail))
    print("    FAIL %s\n         %s" % (label, detail))


def note(text):
    notes.append(text)


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.0f %s" % (n, unit) if unit == "B" else "%.1f %s" % (n, unit)
        n /= 1024.0


def load(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


try:
    import yaml
except ImportError:
    print("Site data checks")
    print("    skipped — PyYAML is not installed (pip install pyyaml)")
    sys.exit(0)


print("Site data: meetings and presentations")

meetings_doc = load("meetings.yml")
decks_doc = load("presentations.yml")
meetings = meetings_doc.get("meetings") or []
decks = decks_doc.get("presentations") or []

# ---------------------------------------------------------------- meetings ---

numbers = [m.get("number") for m in meetings]
if len(numbers) == len(set(numbers)) and all(isinstance(n, int) for n in numbers):
    ok("meeting numbers are unique integers")
else:
    bad("meeting numbers are unique integers", "found %r" % (numbers,))

for m in meetings:
    label = "meeting #%s" % m.get("number")
    missing = [k for k in ("number", "date", "title") if not m.get(k)]
    if missing:
        bad(label, "missing required field(s): %s" % ", ".join(missing))
        continue

    date = m["date"]
    if not isinstance(date, datetime.date):
        bad(label, "date %r is not a YYYY-MM-DD date (quote it and it becomes a string)" % date)
        continue

    upcoming = date >= datetime.date.today()

    if m.get("time") and not re.match(r"^\d{2}:\d{2}$", str(m["time"])):
        bad(label, "time %r is not HH:MM — quote it, or YAML reads 15:00 as a number" % m["time"])

    if upcoming:
        if not m.get("agenda"):
            note("%s is upcoming and has no agenda yet" % label)
        if m.get("recording"):
            bad(label, "is in the future but carries a recording link")
        if m.get("recording_members_only"):
            bad(label, "is in the future but is marked recording_members_only")
    else:
        if m.get("join"):
            note("%s is past but still carries a join link — remove it" % label)
        if not (m.get("recording") or m.get("no_recording") or m.get("recording_members_only")):
            note("%s is past with no recording; the page says 'Recording to follow'" % label)
        if m.get("recording") and m.get("no_recording"):
            bad(label, "has both a recording and no_recording: true")
        if m.get("recording_members_only") and m.get("recording"):
            bad(label, "is marked recording_members_only but carries a public recording link")
        if m.get("recording_members_only") and m.get("no_recording"):
            bad(label, "has both recording_members_only and no_recording: true")

    if m.get("example"):
        note("%s is a placeholder (example: true)" % label)

ok("%d meeting entr%s checked" % (len(meetings), "y" if len(meetings) == 1 else "ies"))

# ----------------------------------------------------------- presentations ---

ids = [p.get("id") for p in decks]
if len(ids) == len(set(ids)) and all(ids):
    ok("presentation ids are unique and present")
else:
    bad("presentation ids are unique and present", "found %r" % (ids,))

known = set(n for n in numbers if isinstance(n, int))

for p in decks:
    label = "presentation %s" % p.get("id", "(no id)")
    missing = [k for k in ("id", "title", "date", "presenter") if not p.get(k)]
    if missing:
        bad(label, "missing required field(s): %s" % ", ".join(missing))

    has_file, has_url = bool(p.get("file")), bool(p.get("url"))
    if has_file and has_url:
        bad(label, "has both file: and url: — an entry needs exactly one")
    elif not has_file and not has_url:
        bad(label, "has neither file: nor url: — nothing to download")

    if has_file:
        path = os.path.join(DECKS, p["file"])
        if not os.path.isfile(path):
            bad(label, "file: %s is not in docs/assets/presentations/" % p["file"])
        else:
            actual = human(os.path.getsize(path))
            if not p.get("filesize"):
                note("%s has no filesize:; the file is %s" % (label, actual))
            elif p["filesize"].replace(" ", "").lower() != actual.replace(" ", "").lower():
                note("%s says filesize: %s but the file is %s" % (label, p["filesize"], actual))

    if "size" in p:
        bad(label, "uses size: — rename it to filesize:, because `size` is a reserved "
                   "Liquid property and the page would render the field count instead")

    if p.get("meeting") is not None and p["meeting"] not in known:
        bad(label, "meeting: %r does not match any meeting number" % p["meeting"])

    if not isinstance(p.get("date"), datetime.date):
        bad(label, "date %r is not a YYYY-MM-DD date" % p.get("date"))

    if p.get("example"):
        note("%s is a placeholder (example: true)" % label)

ok("%d presentation entr%s checked" % (len(decks), "y" if len(decks) == 1 else "ies"))

# --------------------------------------------------------------- orphans -----

referenced = set(p.get("file") for p in decks if p.get("file"))
if os.path.isdir(DECKS):
    on_disk = set(
        f for f in os.listdir(DECKS)
        if not f.startswith(".") and os.path.isfile(os.path.join(DECKS, f))
    )
    orphans = sorted(on_disk - referenced)
    if orphans:
        note("in docs/assets/presentations/ but listed by no entry: %s" % ", ".join(orphans))
    else:
        ok("every committed deck is listed")

# ----------------------------------------------------------------- report ----

if notes:
    print("\n  Notes (not failures):")
    for n in notes:
        print("    - %s" % n)

print("\n%d passed, %d failed" % (passed, len(failures)))
sys.exit(1 if failures else 0)
