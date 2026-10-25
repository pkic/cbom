#!/usr/bin/env python3
"""Generate docs/methodology/demo-reports.json, which the demonstration page renders.

The page used to carry its own JavaScript evaluator, a second implementation of
the evaluation semantics that had to be kept in step with validate_cbom.py by a
test. It now renders reports that validate_cbom.py produced, so the two cannot
disagree. tests/check-demo.py regenerates the reports and fails if the committed
file differs (decision 0018).

Usage: python3 tools/build_demo_reports.py [--check]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
OUT = os.path.join(M, "demo-reports.json")
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

P = "examples/cbom-keycloak-product.cdx.json"
C = "examples/cbom-keycloak-deployment-configured.cdx.json"
CASES = [
    ("product", "Product record", P, "interface-disclosure", [],
     "The vendor's build record of the Keycloak 26.7.3 image. Thirteen interfaces, one stage "
     "(implemented), and the context it points to without carrying it."),
    ("missing-management", "Missing management interface", "examples/cbom-keycloak-product-fail-P2.cdx.json",
     "interface-disclosure", [],
     "The same record with both management interfaces left out and no reason given. Every interface "
     "it does declare is complete, and it still fails: the omission is at the level of the set."),
    ("disclosure-states", "Disclosure states", "examples/cbom-keycloak-product-disclosure-states.cdx.json",
     "interface-disclosure", [],
     "One record exercising the four outcomes: a value, a withheld value (permitted for the library), "
     "an unknown value and an undeclared one (neither satisfies a MUST rule)."),
    ("missing-guide", "Missing pointer", "examples/cbom-keycloak-product-fail-R5.cdx.json",
     "interface-disclosure", [],
     "The HTTPS listener says the operator decides its certificate, and does not point to where the "
     "operator sets it. A reference rule fails."),
    ("design", "Design record", "examples/cbom-keycloak-product-intended.cdx.json",
     "interface-disclosure", [],
     "A design record for Keycloak 27.0 with ML-DSA token signing. The baseline does not accept the "
     "stage 'intended'; the entry profile does."),
    ("configured", "Deployment, configured", C, "deployment-disclosure", [P],
     "An illustrative operator's deployment, read from its configuration. It cites the product record by "
     "hash and joins each interface to the product interface it realises."),
    ("observed", "Deployment, observed", "examples/cbom-keycloak-deployment-observed.cdx.json",
     "deployment-disclosure", [P, C],
     "The same deployment observed over a week. Each value names the methods it came from. The "
     "implementing library is followed through two joins."),
    ("observed-gap", "Observation with a gap", "examples/cbom-keycloak-deployment-observed-fail-unknown.cdx.json",
     "deployment-disclosure", [P, C],
     "The database connection was observed through one source that cannot see the group. The value is "
     "declared unknown, which fails the deployment profile."),
    ("observed-gap-entry", "Observation with a gap, entry depth",
     "examples/cbom-keycloak-deployment-observed-fail-unknown.cdx.json", "interface-enumeration", [P, C],
     "The same record against the entry profile, which asks for no algorithms. It conforms: a record "
     "with gaps lands one depth down."),
    ("migration", "Migration depth", P, "pqc-migration", [],
     "The product record against the PQC migration profile: capability per purpose, inherited from the "
     "library that provides each interface."),
    ("legacy", "CycloneDX 1.7 record", "examples/legacy/cbom-keycloak-product-1.7.cdx.json",
     "interface-disclosure", [],
     "The product record in the CycloneDX 1.7 form today's tools emit. It is read as legacy and gets the "
     "same verdict."),
]


def clean(row):
    return {k: row.get(k) for k in ("id", "level", "attribute", "description", "state", "ok", "detail")
            if row.get(k) is not None}


def build():
    reports = []
    for cid, label, doc, tag, withs, about in CASES:
        reg = V.Registry()
        for w in withs:
            reg.add(os.path.join(M, w))
        bom = reg.add(os.path.join(M, doc))
        profile, _o, _n = V.load_profile(os.path.join(M, "profile-%s.rules.json" % tag))
        verdict, report = V.validate(bom, profile, reg)
        reports.append({
            "id": cid, "label": label, "about": about, "document": doc, "with": withs,
            "profile": {"profileId": profile["profileId"], "version": profile["version"],
                        "title": profile.get("title"), "chain": profile.get("_chain", [])},
            "verdict": verdict,
            "carrier": {"status": report["format"]["status"], "detail": report["format"]["detail"]},
            "product": [clean(r) for r in report["product"]],
            "references": [clean(r) for r in report["references"]],
            "interfaces": [{"interfaceId": i["interfaceId"], "interfaceType": i["interfaceType"],
                            "conforms": i["conforms"],
                            "rows": [clean(r) for r in i["rows"] if r.get("state") != "n/a"]}
                           for i in report["interfaces"]],
        })
    return {"$comment": "Generated by tools/build_demo_reports.py with validate_cbom.py. Do not edit.",
            "reports": reports}


def main(argv):
    data = json.dumps(build(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as fh:
            return 0 if fh.read() == data else 1
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(data)
    print("written", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
