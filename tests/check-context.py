#!/usr/bin/env python3
"""Check that the Keycloak product record and the context it points to agree.

The product record points to four context documents under examples/context/:
the companion SBOM, a VEX document, configuration guidance and a post-quantum
roadmap. Conformance checks only that the pointers exist and are well formed;
this check makes sure the example set is internally consistent, so that a reader
following a pointer finds what the record says is there.

  * every hashed pointer resolves to a committed file whose SHA-256 matches
  * every VEX statement names an SBOM component, and that component carries the
    package URL the product record names for the same library
  * every library's BOM-Link into the SBOM resolves
  * every 'deployment-defined' value has a guidance entry, and every guidance
    entry names a real interface
  * every roadmap item agrees with the record's capability status and blocker

Usage:  python3 tests/check-context.py
Exit:   0 consistent, 1 otherwise
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
EX = os.path.join(M, "examples")
SITE = "https://pkic.github.io/cbom/methodology/examples/"
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

failures = 0


def ok(label):
    print("  ok   %s" % label)


def bad(label, detail):
    global failures
    failures += 1
    print("  FAIL %s\n     %s" % (label, detail))


def main():
    reg = V.Registry()
    for name in os.listdir(os.path.join(EX, "context")):
        if name.endswith(".cdx.json"):
            reg.add(os.path.join(EX, "context", name))
    prod_path = os.path.join(EX, "cbom-keycloak-product.cdx.json")
    prod = reg.add(prod_path)
    subject, entries, _n = V.document_parts(prod)
    product_refs = {e.get("bom-ref"): e for e in entries}
    interfaces = {i["interfaceId"]: i for i in V.extract_interfaces(prod)}

    # Hashed pointers resolve and match.
    pointers = list(V.refs_of(prod))
    for e in entries:
        pointers += V.refs_of(e)
    checked = 0
    for r in pointers:
        want = {h.get("alg"): h.get("content") for h in r.get("hashes", []) or []}.get("SHA-256")
        url = r.get("url", "")
        path = None
        doc, _ref = V.split_bomlink(url)
        if doc and reg.get(doc):
            path = reg.get(doc)["path"]
        elif url.startswith(SITE):
            path = os.path.join(EX, url[len(SITE):])
        if not want or not path:
            continue
        checked += 1
        if not os.path.exists(path):
            bad("a hashed pointer resolves", "%s -> %s does not exist" % (url, path))
            continue
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if got != want:
            bad("a hashed pointer matches its file", "%s: hash does not match %s" % (url, os.path.relpath(path, ROOT)))
    ok("%d hashed pointer(s) resolve to committed files with matching SHA-256" % checked) if not failures else None

    sbom = next(e["bom"] for e in reg.docs.values() if e["path"].endswith("sbom.cdx.json"))
    _s, sbom_entries, _n = V.document_parts(sbom)
    sbom_refs = {e.get("bom-ref"): e for e in sbom_entries}

    # Library BOM-Links into the SBOM.
    for e in entries:
        if e.get("type") != "library":
            continue
        for r in V.refs_of(e):
            doc, ref = V.split_bomlink(r.get("url"))
            if r.get("type") == "bom" and ref and ref not in sbom_refs:
                bad("every library's SBOM link resolves", "%s -> %s" % (e["bom-ref"], ref))
            elif ref and V.purl_of(sbom_refs[ref]) != V.purl_of(e):
                bad("the SBOM entry carries the record's package URL", "%s" % ref)
    ok("every library in the record points to an SBOM entry with the same package URL")

    # VEX statements join to the SBOM, and through it to I9.
    vex = next(e["bom"] for e in reg.docs.values() if e["path"].endswith("vex.cdx.json"))
    implementations = {i.get("implementationPurl") for i in interfaces.values()}
    for v in vex.get("vulnerabilities", []):
        for a in v.get("affects", []):
            doc, ref = V.split_bomlink(a.get("ref"))
            target = sbom_refs.get(ref)
            if not target:
                bad("every VEX statement names an SBOM component", "%s -> %s" % (v["id"], a.get("ref")))
            elif V.purl_of(target) not in implementations:
                bad("the affected component implements a declared interface",
                    "%s: %s is no interface's implementationPurl" % (v["id"], V.purl_of(target)))
    ok("%d VEX statement(s) join to SBOM components that implement declared interfaces"
       % len(vex.get("vulnerabilities", [])))

    # Configuration guidance.
    guidance = json.load(open(os.path.join(EX, "context", "keycloak-configuration-guidance.json")))
    covered = set()
    for g in guidance["entries"]:
        _doc, ref = V.split_bomlink(g["interface"])
        if ref not in product_refs:
            bad("every guidance entry names a real interface", g["interface"])
        covered.add((ref, g["attribute"]))
    for iid, i in interfaces.items():
        for attr in ("keyExchange", "encryption", "authentication"):
            if i.get(attr) == "deployment-defined" and (iid, attr) not in covered:
                bad("every deployment-defined value has guidance", "%s %s" % (iid, attr))
    ok("every 'deployment-defined' value has a guidance entry naming a real interface")

    # Roadmap agrees with the capability group.
    roadmap = json.load(open(os.path.join(EX, "context", "keycloak-pqc-roadmap.json")))
    for item in roadmap["items"]:
        for link in item["interfaces"]:
            _doc, ref = V.split_bomlink(link)
            entry = (interfaces.get(ref, {}).get("_groups") or {}).get("capabilityByPurpose", {}).get(item["purpose"], {})
            if entry.get("capabilityStatus") != item["capabilityStatus"] or \
                    entry.get("blockedBy") != item["blockedBy"]:
                bad("the roadmap agrees with the record",
                    "%s on %s: roadmap says %s/%s, record says %s/%s"
                    % (item["id"], ref, item["capabilityStatus"], item["blockedBy"],
                       entry.get("capabilityStatus"), entry.get("blockedBy")))
    ok("%d roadmap item(s) agree with the record's capability status and blocker" % len(roadmap["items"]))

    print("  %s" % ("the context set is consistent" if not failures else "%d problem(s)" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
