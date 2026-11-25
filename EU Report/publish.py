#!/usr/bin/env python3
"""Emit the submittable copy of the report from the working draft.

Usage:  bash publish.sh ["version label"]

The working draft is the only file anyone edits. This script strips the drafting
scaffolding, regenerates the table of contents, and refuses to produce output that
still contains anything which must not ship.
"""
import os, re, sys, datetime

SRC = "EU Report.md"
OUT = "Cryptographic-Transparency-in-the-Supply-Chain.md"
REPORT = "publish-report.txt"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toclib


# ---------------------------------------------------------------- section removal
def drop_section(body, heading, stop=("\n---\n",)):
    """Remove a '## heading' section up to the next horizontal rule."""
    i = body.find(heading)
    if i < 0:
        return body, False
    ends = [body.find(s, i + len(heading)) for s in stop]
    ends = [e for e in ends if e >= 0]
    if not ends:
        return body, False
    j = min(ends)
    return body[:i] + body[j + 5:], True


def drop_blockquotes(body, markers):
    """Remove whole blockquotes whose first line contains any marker."""
    lines = body.split("\n")
    out, i, n = [], 0, 0
    while i < len(lines):
        if lines[i].startswith(">") and any(m in lines[i] for m in markers):
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ">"):
                i += 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            n += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), n


def drop_lines(body, patterns):
    lines = body.split("\n")
    out, n = [], 0
    for line in lines:
        if any(re.search(p, line) for p in patterns):
            n += 1
            continue
        out.append(line)
    return "\n".join(out), n


def collapse_blanks(body):
    return re.sub(r"\n{4,}", "\n\n\n", body)


# ---------------------------------------------------------------- internal citations
# Safe, mechanical: parentheticals that contain nothing but internal tags.
# LSN-P-nn is a report tag that survives publication, so P-nn is matched only when it is
# not preceded by "LSN-".
INTERNAL = (r"(?:DR-\d+"
            r"|VL(?:\s*§\s*[0-9a-zA-Z./§\s]+?|\s+C-\d+)"
            r"|pkic-feedback\s*§\s*[0-9a-zA-Z.]+"
            r"|(?<!LSN-)P-\d+)")
SAFE_SUBS = [
    # "(DR-09)" / "(VL §3b)" / "(DR-11, VL §2)" -> removed, with the preceding space
    (re.compile(r"\s*\((?:%s)(?:\s*[,;]\s*(?:%s))*\)" % (INTERNAL, INTERNAL)), ""),
    # "(DR-11, §9.3)" -> "(§9.3)"   /  "(§7.2, VL §3c)" -> "(§7.2)"
    (re.compile(r"\((?:%s)\s*,\s*" % INTERNAL), "("),
    (re.compile(r",\s*(?:%s)\)" % INTERNAL), ")"),
    # "**Resolved (DR-09).**" handled by the first rule, leaving "**Resolved.**"
]

# Anything still matching this after the safe pass needs a human sentence rewrite.
RESIDUAL = re.compile(INTERNAL)

FORBIDDEN = [
    (r"\*\*Owner:\*\*", "owner/status line"),
    (r"\*\*Verify", "verification marker"),
    (r"Cap:\s*\d+pp", "page cap"),
    (r"Cap lifted", "page cap note"),
    (r"\*\*Drafting note", "drafting note"),
    (r"_tbd_", "tbd placeholder"),
    (r"check-coverage\.sh", "build script reference"),
    (r"\.\./register\.md", "register path"),
    (r"decisions\.md", "decisions path"),
    (r"pkic-feedback", "feedback path"),
    (r"verification-log", "verification log path"),
    (r"Removed by the publication build", "internal marker"),
]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "Draft for review — %s" % datetime.date.today().isoformat()
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    raw = open(SRC, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    body = raw.replace("\r\n", "\n")
    log = []

    # 1. version label in the title block
    body, n = re.subn(r"\| \*\*Version\*\* \| [^|]*\|",
                      "| **Version** | %s |" % label, body, count=1)
    log.append("version label set (%d)" % n)

    # 2. internal sections
    for heading in ("## Editorial conventions", "## Resolved drafting questions"):
        body, hit = drop_section(body, heading)
        log.append("%s: %s" % (heading, "removed" if hit else "NOT FOUND"))

    # 3. blockquotes
    body, n = drop_blockquotes(body, ("**Verify", "**Drafting note", "**Open:",
                                      "Decision needed in", "Removed by the publication build",
                                      "**Internal."))
    log.append("blockquotes removed: %d" % n)

    # 4. scaffolding lines
    body, n = drop_lines(body, [
        r"^\*\*Owner:\*\*",
        r"^\*Register: `\.\./register\.md`",
        r"^`bash check-coverage\.sh` fails",
        r"check-coverage\.sh",
    ])
    log.append("scaffolding lines removed: %d" % n)

    # 5. internal citations, safe pass
    total = 0
    for rx, repl in SAFE_SUBS:
        body, n = rx.subn(repl, body)
        total += n
    log.append("internal citations removed: %d" % total)

    # 6. tidy and regenerate the contents
    body = collapse_blanks(body)
    body = toclib.inject(body, markers=False)
    log.append("contents regenerated")

    # 7. enforcement
    problems = []
    lines = body.split("\n")
    for i, line in enumerate(lines, 1):
        for pat, what in FORBIDDEN:
            if re.search(pat, line):
                problems.append((i, what, line.strip()[:110]))
    residual = [(i, "internal tag needing a sentence rewrite", line.strip()[:110])
                for i, line in enumerate(lines, 1) if RESIDUAL.search(line)]

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("publish.py run %s\n\n" % datetime.datetime.now().isoformat(timespec="seconds"))
        for entry in log:
            fh.write("  %s\n" % entry)
        fh.write("\nMUST FIX (%d)\n" % len(problems))
        for i, what, text in problems:
            fh.write("  line %5d  %-28s %s\n" % (i, what, text))
        fh.write("\nNEEDS A SENTENCE REWRITE (%d)\n" % len(residual))
        for i, what, text in residual:
            fh.write("  line %5d  %s\n" % (i, text))

    out = body.replace("\n", "\r\n") if crlf else body
    open(OUT, "wb").write(out.encode("utf-8"))

    print("wrote %s (%d lines)" % (OUT, len(lines)))
    print("wrote %s" % REPORT)
    for entry in log:
        print("  %s" % entry)
    if problems or residual:
        print("\nNOT READY TO SUBMIT")
        print("  must fix:            %d" % len(problems))
        print("  sentence rewrites:   %d" % len(residual))
        print("  see %s for line numbers" % REPORT)
        return 1
    print("\nclean — no drafting scaffolding remains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
