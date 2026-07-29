#!/usr/bin/env python3
"""
Illustrative CBOM profile validator (product-independent, version-aware).

Demonstrates the "conformance checklist" direction of a CBOM profile that is
product- and instance-independent:

  * FORMAT check    -- is this CBOM in a carrier format/version the profile
                       accepts? (see 'appliesTo' in the rules file). Older CBOMs
                       are handled deliberately: refused below 'min', flagged
                       'legacy' between 'min' and 'tested', accepted at 'tested'.
  * PRODUCT rules   -- constrain the SET of interfaces (cardinality, e.g. "at
                       least one management interface"), naming no specific one.
  * INTERFACE rules -- apply uniformly to EVERY declared cryptographic interface.

Design point (matches the working-group methodology):
  * The RULES are format-independent and protocol-neutral.
  * The FORMAT ADAPTER (extract_interfaces) is the only format-specific part, and
    it reads fields common to CycloneDX 1.6 and 1.7 so older CBOMs still validate.

Usage:
    python validate_cbom.py <cbom.json> <profile.rules.json> [--json]
Exit code: 0 = conforms, 1 = does not conform, 2 = usage/error.
"""
import json
import sys

ENC_PRIMS = {"ae", "aead", "block-cipher", "stream-cipher"}
KEX_PRIMS = {"key-agree", "key-agreement", "kem"}
SIG_PRIMS = {"signature"}


def ver_tuple(s):
    return tuple(int(x) for x in str(s).split(".") if x.isdigit())


# --------------------------------------------------------------------------- #
# Carrier-format / version handling                                           #
# --------------------------------------------------------------------------- #
def check_format(bom, profile):
    """Decide whether this CBOM's carrier format/version is acceptable.
    Returns dict: {ok, status, detail}. status in
    {target, legacy, newer, unsupported-version, unsupported-format}."""
    fmt = bom.get("bomFormat")
    spec = bom.get("specVersion")
    applies = profile.get("appliesTo", {})

    if fmt != "CycloneDX" or "cyclonedx" not in applies:
        return {"ok": False, "status": "unsupported-format",
                "detail": "bomFormat=%r not supported by this profile" % fmt}

    rng = applies["cyclonedx"]
    v, vmin, vtested = ver_tuple(spec), ver_tuple(rng["min"]), ver_tuple(rng["tested"])
    if v < vmin:
        return {"ok": False, "status": "unsupported-version",
                "detail": "CycloneDX %s is older than min supported %s -- refuse; upgrade the CBOM first"
                          % (spec, rng["min"])}
    if v < vtested:
        return {"ok": True, "status": "legacy",
                "detail": "CycloneDX %s accepted, but profile was tested against %s (legacy -- warn)"
                          % (spec, rng["tested"])}
    if v > vtested:
        return {"ok": True, "status": "newer",
                "detail": "CycloneDX %s is newer than tested %s -- accepted, review advised"
                          % (spec, rng["tested"])}
    return {"ok": True, "status": "target", "detail": "CycloneDX %s (target)" % spec}


# --------------------------------------------------------------------------- #
# Format adapter: CycloneDX 1.6/1.7 CBOM -> list of abstract interfaces         #
# --------------------------------------------------------------------------- #
def extract_interfaces(bom):
    comps = {c.get("bom-ref"): c for c in bom.get("components", [])}
    interfaces = []
    for c in bom.get("components", []):
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") != "protocol":
            continue
        props = {p["name"]: p["value"] for p in c.get("properties", [])}
        proto = cp.get("protocolProperties", {})
        refs = list(proto.get("cryptoRefArray", []))
        for s in proto.get("cipherSuites", []):
            refs += s.get("algorithms", [])
        roles = [k.split(":")[-1] for k in props
                 if k.startswith("pkic:profile:endpointRole:")]
        interfaces.append({
            "interfaceId": props.get("pkic:profile:interfaceId") or c.get("bom-ref"),
            "interfaceType": props.get("pkic:profile:interfaceType"),
            "protocol": (proto.get("type") or "").upper() or None,
            "protocolVersion": proto.get("version"),
            "keyExchange": algo_name(refs, comps, KEX_PRIMS),
            "encryption": algo_name(refs, comps, ENC_PRIMS),
            "authentication": auth(refs, comps),
            "endpointRoles": roles,
            "lifecycleStage": props.get("pkic:profile:lifecycleStage"),
            "implementationPurl": props.get("pkic:profile:implementationPurl"),
        })
    return interfaces


def algo_name(refs, comps, prims):
    for ref in refs:
        c = comps.get(ref)
        if not c:
            continue
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") != "algorithm":
            continue
        if cp.get("algorithmProperties", {}).get("primitive") in prims:
            return c.get("name")
    return None


def auth(refs, comps):
    for ref in refs:
        c = comps.get(ref)
        if not c:
            continue
        if c.get("cryptoProperties", {}).get("assetType") == "certificate":
            props = c["cryptoProperties"]["certificateProperties"]
            sig = props.get("signatureAlgorithmRef")
            if sig and sig in comps:
                return comps[sig].get("name")
    return algo_name(refs, comps, SIG_PRIMS)


# --------------------------------------------------------------------------- #
# Constraint checks                                                           #
# --------------------------------------------------------------------------- #
def present(v):
    return v not in (None, "", [], {})


def check_attr(value, constraint, profile):
    if "present" in constraint:
        p = present(value)
        return (p == constraint["present"], "present" if p else "absent")
    if "minCount" in constraint:
        n = len(value or [])
        return (n >= constraint["minCount"], "count=%d (min %d)" % (n, constraint["minCount"]))
    if not present(value):
        return (False, "absent")
    if "enum" in constraint:
        return (value in constraint["enum"], "= %r" % (value,))
    if "enumRef" in constraint:
        return (value in profile.get(constraint["enumRef"], []), "= %r" % (value,))
    if "startsWith" in constraint:
        return (str(value).startswith(constraint["startsWith"]), "= %r" % (value,))
    return (True, "ok")


def check_product(interfaces, constraint):
    if "minInterfaces" in constraint:
        n = len(interfaces)
        return (n >= constraint["minInterfaces"], "%d interface(s) declared" % n)
    if "minInterfacesOfType" in constraint:
        spec = constraint["minInterfacesOfType"]
        n = sum(1 for i in interfaces if i.get("interfaceType") == spec["interfaceType"])
        return (n >= spec["min"],
                "%d of type '%s' (min %d)" % (n, spec["interfaceType"], spec["min"]))
    return (True, "ok")


# --------------------------------------------------------------------------- #
def validate(bom, profile):
    fmt = check_format(bom, profile)
    report = {"format": fmt, "product": [], "interfaces": []}

    # If the carrier format/version is unsupported, refuse without pretending
    # to evaluate content it may not fully understand.
    if not fmt["ok"]:
        return False, report

    interfaces = extract_interfaces(bom)
    for rule in profile.get("productRules", []):
        ok, detail = check_product(interfaces, rule["constraint"])
        report["product"].append(dict(rule, ok=ok, detail=detail))

    for iface in interfaces:
        rows = []
        for rule in profile.get("interfaceRules", []):
            ok, detail = check_attr(iface.get(rule["attribute"]),
                                    rule["constraint"], profile)
            rows.append({"id": rule["id"], "level": rule["level"],
                         "attribute": rule["attribute"], "ok": ok, "detail": detail})
        iface_ok = all(r["ok"] for r in rows if r["level"] == "MUST")
        report["interfaces"].append({
            "interfaceId": iface["interfaceId"],
            "interfaceType": iface.get("interfaceType"),
            "conforms": iface_ok, "rows": rows,
        })

    product_ok = all(r["ok"] for r in report["product"] if r["level"] == "MUST")
    ifaces_ok = all(i["conforms"] for i in report["interfaces"])
    return (product_ok and ifaces_ok), report


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    as_json = "--json" in argv
    bom = json.load(open(argv[1], encoding="utf-8"))
    profile = json.load(open(argv[2], encoding="utf-8"))
    conforms, report = validate(bom, profile)

    if as_json:
        print(json.dumps({"conforms": conforms, "report": report}, indent=2))
        return 0 if conforms else 1

    print("Profile : %s v%s" % (profile["title"], profile["version"]))
    print("CBOM    : %s" % argv[1])
    print("=" * 64)
    f = report["format"]
    icon = "PASS" if f["ok"] else "FAIL"
    warn = f["status"] in ("legacy", "newer")
    print("FORMAT  [%s] %s" % ("warn" if warn else icon, f["detail"]))
    if not f["ok"]:
        print("=" * 64)
        print("VERDICT : DOES NOT CONFORM  (carrier format/version not accepted)")
        return 1
    print("=" * 64)
    print("PRODUCT-LEVEL RULES")
    for r in report["product"]:
        icon = "PASS" if r["ok"] else "FAIL"
        print("  [%s] %-3s %-5s %s" % (icon, r["id"], r["level"], r["description"]))
        print("         -> %s" % r["detail"])
    for iface in report["interfaces"]:
        print("-" * 64)
        status = "conforms" if iface["conforms"] else "FAILS"
        print("INTERFACE  %s  (type=%s)  ==>  %s"
              % (iface["interfaceId"], iface["interfaceType"], status))
        for r in iface["rows"]:
            icon = "PASS" if r["ok"] else ("FAIL" if r["level"] == "MUST" else "warn")
            print("  [%s] %-4s %-6s %-18s %s"
                  % (icon, r["id"], r["level"], r["attribute"], r["detail"]))
    print("=" * 64)
    fails = [r["id"] for r in report["product"] if not r["ok"] and r["level"] == "MUST"]
    for i in report["interfaces"]:
        for r in i["rows"]:
            if not r["ok"] and r["level"] == "MUST":
                fails.append("%s/%s" % (i["interfaceId"], r["id"]))
    verdict = "CONFORMS" if conforms else "DOES NOT CONFORM"
    tail = ("  (failed MUST: %s)" % ", ".join(fails)) if fails else ""
    note = "  [carrier: %s]" % report["format"]["status"]
    print("VERDICT : %s%s%s" % (verdict, tail, note))
    return 0 if conforms else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
