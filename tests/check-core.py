#!/usr/bin/env python3
"""The change core and pqc-migration state their shared rules identically.

The change core is published as a sibling of pqc-migration rather than as its base, so that no
rule id moves (decision 0023). Nothing structural then keeps the two in step. This check requires
that every rule the core shares with pqc-migration, under the same id, is identical in both files,
that every vocabulary a shared rule resolves against is identical, and that both pin the same base.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")


def load(name):
    with open(os.path.join(M, name), encoding="utf-8") as fh:
        return json.load(fh)


core, pqc = load("profile-change-core.rules.json"), load("profile-pqc-migration.rules.json")
bad = []
print("Change core and pqc-migration")


def rules(p):
    out = {}
    for k in ("productRules", "interfaceRules", "referenceRules"):
        for r in p.get(k, []):
            out[r["id"]] = r
    for g in p.get("groupRules", []):
        out[g["id"]] = {k: v for k, v in g.items() if k != "members"}
        for m in g.get("members", []):
            out[m["id"]] = m
    return out


rc, rp = rules(core), rules(pqc)
shared = sorted(set(rc) & set(rp))
for rid in shared:
    if rc[rid] != rp[rid]:
        bad.append("rule %s differs between the two files" % rid)
    for key in ("enumRef", "keyVocabularyRef"):
        ref = rc[rid].get("constraint", {}).get(key) if key == "enumRef" else rc[rid].get(key)
        if ref and core.get(ref) != pqc.get(ref):
            bad.append("vocabulary %s, used by %s, differs" % (ref, rid))
if core.get("extends") != pqc.get("extends"):
    bad.append("the two profiles pin different bases")
if core.get("overrides") != pqc.get("overrides"):
    bad.append("the two profiles override the base differently")
for b in bad:
    print("  FAIL ", b)
if not bad:
    print("  ok    %d shared rule(s) identical: %s" % (len(shared), ", ".join(shared)))
sys.exit(1 if bad else 0)
