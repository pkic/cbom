#!/usr/bin/env python3
"""Write docs/methodology/examples/README.md, the catalogue of example CBOMs.

The catalogue is generated from the test cases in tests/check-examples.py and
tests/check-draft-examples.py, so every verdict it lists is one the test suite checks. It
cannot claim a conformance that the tests do not confirm.

Usage:  python3 tools/build_examples_catalogue.py           write the catalogue
        python3 tools/build_examples_catalogue.py --check   exit 1 if the catalogue is out of date
"""
import collections
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
EX = os.path.join(M, "examples")
TARGET = os.path.join(EX, "README.md")
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

P = "pkic:profile:"


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tests", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def facts(path):
    bom = json.load(open(path, encoding="utf-8"))
    # CycloneDX 2.0 carries the subject in an inventory; 1.7 in metadata.component.
    subj = bom["inventories"][0]["subject"] if "inventories" in bom else bom["metadata"].get("component", {})
    kind = next((p["value"] for p in subj.get("properties", []) if p["name"] == P + "subjectType"), "")
    phases = [p.get("phase") for p in bom.get("metadata", {}).get("lifecycles", [])]
    stage = ", ".join(sorted({V.PHASE_TO_STAGE.get(p, p) for p in phases if p}))
    name = "%s %s" % (subj.get("name", ""), subj.get("version", "")) if subj.get("version") else subj.get("name", "")
    fictional = "FICTIONAL" in bom.get("$comment", "") or "(fictional)" in json.dumps(subj.get("parties", []))
    return name.strip() + (" (fictional)" if fictional else ""), kind, stage


def rule_names(rules):
    """'ssh-transport/pqc-migration#I4' -> 'pqc-migration#I4'; distinct, in order."""
    out = []
    for r in rules:
        short = r.split("/")[-1]
        if short not in out:
            out.append(short)
    return out


def link(rel, base_dir):
    return "[`%s`](%s)" % (os.path.basename(rel), os.path.relpath(rel, base_dir).replace(os.sep, "/"))


def add(entries, tag, cited):
    """One entry per profile. A record tested with and without its cited records keeps the
    longer description, which names what to supply."""
    for i, e in enumerate(entries):
        if e == tag or e.startswith(tag + " ("):
            if len(tag + cited) > len(e):
                entries[i] = tag + cited
            return
    entries.append(tag + cited)


def published():
    ce = load("check-examples")
    conforms = collections.OrderedDict()
    fails = collections.OrderedDict()
    for doc, tag, withs, expected in ce.CASES:
        if expected is None:
            continue
        cited = " (given %s)" % ", ".join("`%s`" % w for w in withs) if withs else ""
        if not expected:
            add(conforms.setdefault(doc, []), tag, cited)
        else:
            fails.setdefault(doc, {"fails": [], "against": []})
            add(fails[doc]["against"], tag, cited)
            for r in rule_names(expected):
                if r not in fails[doc]["fails"]:
                    fails[doc]["fails"].append(r)
    return conforms, fails


def drafts():
    cd = load("check-draft-examples")
    rows = []
    for doc, prof, withs, expected in cd.CASES:
        tag = os.path.basename(prof).replace("profile-", "").replace(".rules.json", "")
        if os.path.dirname(prof).startswith(os.path.join(ROOT, "drafts")):
            tag += " (draft)"
        if isinstance(expected, tuple):
            verdict = "does not conform: gap analysis, %d failing MUST checks" % expected[1]
        elif expected:
            verdict = "fails " + ", ".join("`%s`" % r for r in rule_names(expected))
        else:
            verdict = "conforms"
        rows.append((doc, tag, verdict))
    return rows


def render():
    conforms, fails = published()
    out = ["# Example CBOMs", "",
           "This folder holds the methodology's example CBOMs. Every record is CycloneDX 2.0 unless it sits in "
           "`legacy/`, which holds CycloneDX 1.7 documents. The companion SBOMs, VEX documents and guidance that "
           "the records cite are in `context/`. The results of evaluating policies against the records are in "
           "`results/`.", "",
           "There are two kinds of example. A conforming record shows what a complete answer looks like for one "
           "kind of subject. A failure variant is a copy of a conforming record with one thing broken, so that "
           "it fails exactly one rule. You can use the failure variants to check that a validator reports the "
           "rule you expect.", "",
           "To browse the examples as readable pages, with each failure variant's fix explained, open the "
           "[examples gallery](https://pkic.github.io/cbom/methodology/examples.html).", "",
           "Every verdict below is checked by the test suite (`bash tests/run-profile-tests.sh`). This file is "
           "generated by `python3 tools/build_examples_catalogue.py` from the test cases. Do not edit it by "
           "hand: change the tests and run the script again.", "",
           "To check a record yourself:", "",
           "```bash",
           "python3 docs/methodology/validate_cbom.py \\",
           "    docs/methodology/examples/cbom-openssh-10.0p2-product.cdx.json \\",
           "    docs/methodology/profile-pqc-migration.rules.json",
           "```", "",
           "Add `--with <file>` for each record that the example cites, where a case below lists one.", "",
           "## Conforming records", "",
           "| Example | Subject | Subject type | Stage | Conforms to |",
           "|---|---|---|---|---|"]
    for doc, tags in conforms.items():
        if doc in fails:
            continue
        name, kind, stage = facts(os.path.join(EX, doc))
        out.append("| %s | %s | %s | %s | %s |" % (link(os.path.join(EX, doc), EX), name, kind, stage,
                                                 "<br>".join(tags)))
    out += ["", "## Failure variants", "",
            "Each variant names the rule it isolates. It also conforms to the profiles in the last column, which "
            "shows that nothing else in it is broken.", "",
            "| Example | Fails | Evaluated against | Still conforms to |", "|---|---|---|---|"]
    for doc, f in fails.items():
        still = "<br>".join(conforms.get(doc, [])) or "—"
        out.append("| %s | %s | %s | %s |" % (link(os.path.join(EX, doc), EX),
                                            ", ".join("`%s`" % r for r in f["fails"]),
                                            "<br>".join(f["against"]), still))
    out += ["", "## Draft application-domain examples", "",
            "These records belong to application-domain documents that are still drafts. They sit under "
            "`drafts/`, next to the draft profiles they are written for, and `tests/check-draft-examples.py` "
            "checks them. A record marked as a gap analysis describes a real product from its public "
            "documentation. It is meant not to conform: the failing checks show what the public documentation "
            "does not say.", "",
            "| Example | Profile | Verdict |", "|---|---|---|"]
    for doc, tag, verdict in drafts():
        out.append("| %s | %s | %s |" % (link(doc, EX), tag, verdict))
    return "\n".join(out) + "\n"


def main():
    text = render()
    if "--check" in sys.argv:
        current = open(TARGET, encoding="utf-8").read() if os.path.exists(TARGET) else ""
        if current != text:
            print("docs/methodology/examples/README.md is out of date: run python3 tools/build_examples_catalogue.py")
            return 1
        print("the examples catalogue is up to date")
        return 0
    with open(TARGET, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("written", os.path.relpath(TARGET, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
