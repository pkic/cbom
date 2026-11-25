"""Table-of-contents generation, shared by the working draft and the publication build."""
import re

TOC_START = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"

SKIP = ("Editorial conventions", "How to read this report", "Contents")


def slug(text):
    t = text.lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"\s+", "-", t).strip("-")


def headings(body):
    """Chapter (#) and section (##) headings, minus the title and internal sections."""
    out = []
    first_h1_seen = False
    in_fence = False
    for line in body.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,2})\s+(.*?)\s*$", line)
        if not m:
            continue
        level, text = len(m.group(1)), m.group(2)
        if level == 1 and not first_h1_seen:
            first_h1_seen = True          # the report title
            continue
        if text in SKIP:
            continue
        out.append((level, text))
    return out


def render(body, title="Contents"):
    lines = ["## " + title, ""]
    for level, text in headings(body):
        indent = "" if level == 1 else "  "
        lines.append("%s- [%s](#%s)" % (indent, text, slug(text)))
    return "\n".join(lines)


def strip(body):
    """Remove the TOC block and its markers entirely."""
    if TOC_START in body and TOC_END in body:
        pre, rest = body.split(TOC_START, 1)
        _, post = rest.split(TOC_END, 1)
        return pre + post.lstrip("\n")
    return body.replace(TOC_START, "")


def inject(body, title="Contents", markers=True):
    """Replace the TOC block (or the bare marker) with a freshly generated TOC.

    markers=False emits the contents without the HTML comment markers, for output
    that will not be regenerated in place.
    """
    rendered = render(strip(body), title)
    toc = (TOC_START + "\n\n" + rendered + "\n\n" + TOC_END) if markers else rendered
    if TOC_START in body and TOC_END in body:
        pre, rest = body.split(TOC_START, 1)
        _, post = rest.split(TOC_END, 1)
        return pre + toc + post
    if TOC_START in body:
        return body.replace(TOC_START, toc, 1)
    return body
