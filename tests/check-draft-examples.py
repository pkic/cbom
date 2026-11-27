#!/usr/bin/env python3
"""Check the example CBOMs under drafts/ against their draft profiles.

The examples under drafts/ belong to application-domain work that is not yet published. The
methodology examples are pinned by tests/check-examples.py; these were not checked at all, so a
change to a published base profile could silently move a draft verdict. Each case pins either the
exact failing MUST rules (a conforming example, or a failure variant that isolates one rule) or,
for a record written as a gap analysis of a real product, the number of failing MUST checks.

Usage:  python3 tests/check-draft-examples.py
Exit:   0 every verdict as expected, 1 otherwise
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
D = os.path.join(ROOT, "drafts")
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402


def m(name):
    return os.path.join(M, "profile-%s.rules.json" % name)


def ex(name):
    return os.path.join(M, "examples", name)


def dr(path):
    return os.path.join(D, path)


HSM = dr("hsm-product/profile-hsm-product.rules.json")
HSMK = dr("hsm-product/profile-hsm-key-hierarchy.rules.json")
OTS = dr("ot-system/profile-ot-system.rules.json")
R214 = dr("r2-14-system/profile-interface-disclosure.rules.json")
SCP = dr("saas-services/profile-service-change-planning.rules.json")
SKC = dr("saas-services/profile-service-key-custody.rules.json")
TEN = dr("saas-services/profile-tenant-disclosure.rules.json")
TNF = dr("telecom-network-function/profile-telecom-network-function.rules.json")
TSA = dr("telecom-service-assurance/profile-telecom-service-assurance.rules.json")
NF = "telecom-network-function/examples/"
SA = "telecom-service-assurance/examples/"
SAAS = "saas-services/examples/"
SEPP = dr(NF + "cbom-open5gs-sepp-2.8.0-product.cdx.json")
IED_LIB = [ex("cbom-ot-protection-ied-product.cdx.json"), ex("cbom-lib60870-2.4.1-product.cdx.json")]

# (example, profile, cited documents, expected). Expected is a list of failing MUST rule ids, or
# ("count", n) for a gap analysis that is meant not to conform.
CASES = [
    # HSMs and key management
    (dr("hsm-product/examples/cbom-example-payment-hsm-product.cdx.json"), HSM, [], []),
    (dr("hsm-product/examples/cbom-example-payment-hsm-product.cdx.json"), HSMK, [], []),
    (dr("hsm-product/examples/cbom-example-payment-hsm-product-fail-I1.cdx.json"), HSM, [],
     ["service:mgmt-console/hsm-product#I1"]),
    # A real HSM written as a gap analysis from public documentation.
    (dr("hsm-luna-t7/examples/cbom-thales-luna-t7-fw-7.15.1.cdx.json"), HSMK, [], ("count", 52)),
    # Financial services: a managed payment HSM service, also a gap analysis.
    (dr("fs-payment-cryptography-service/examples/cbom-aws-payment-cryptography-service.cdx.json"),
     m("service-disclosure"), [], ("count", 22)),
    # Operational technology
    (dr("ot-libiec61850/examples/cbom-libiec61850-1.6.2-product.cdx.json"), m("interface-enumeration"), [], []),
    (dr("ot-libiec61850/examples/cbom-libiec61850-1.6.2-product.cdx.json"), m("interface-disclosure"), [], []),
    (ex("cbom-ot-sas-system-configured.cdx.json"), OTS, IED_LIB, []),
    (dr("ot-system/examples/cbom-sas-reference-system-fail-conduit.cdx.json"), OTS, IED_LIB,
     ["ied1:mgmt-enrol/ot-system#I3"]),
    (dr("r2-14-system/examples/cbom-sas-reference-system-configured.cdx.json"), R214, [], []),
    # SaaS and cloud services
    (dr(SAAS + "cbom-keycloak-service-change-planning.cdx.json"), SCP, [], []),
    (dr(SAAS + "cbom-keycloak-service-key-custody.cdx.json"), SKC, [], []),
    (dr(SAAS + "cbom-keycloak-service-key-custody-fail-replica.cdx.json"), SKC, [],
     ["service:sto-realm-keys/service-key-custody#I2"]),
    (dr(SAAS + "cbom-keycloak-tenant-configured.cdx.json"), TEN, [], []),
    (dr(SAAS + "cbom-keycloak-tenant-fail-custody.cdx.json"), TEN, [],
     ["service:sto-realm-keys/tenant-disclosure#I1"]),
    # Telecommunications
    (SEPP, TNF, [], []),
    (dr(NF + "cbom-open5gs-sepp-fail-referencepoint.cdx.json"), TNF, [], ["n32c/telecom-network-function#I1"]),
    (dr(NF + "cbom-open5gs-sepp-deployment-configured.cdx.json"), m("deployment-disclosure"), [SEPP], []),
    (dr(NF + "cbom-open5gs-sepp-deployment-fail-termination.cdx.json"), m("deployment-disclosure"), [SEPP],
     ["dep:sbi/interface-disclosure#I14"]),
    (dr(SA + "cbom-roaming-interconnect-system.cdx.json"), TSA, [], []),
    (dr(SA + "cbom-roaming-interconnect-fail-proxy.cdx.json"), TSA, [], ["sepp:n32c/telecom-service-assurance#I3"]),
    (dr(SA + "cbom-roaming-interconnect-fail-service.cdx.json"), TSA, [],
     ["sepp:n32f/telecom-service-assurance#I1"]),
]


def failing(bom, profile, reg):
    verdict, report = V.validate(bom, profile, reg)
    got = [r["id"] for r in report["product"] + report["references"] if r["level"] == "MUST" and not r["ok"]]
    for i in report["interfaces"]:
        got += ["%s/%s" % (i["interfaceId"], r["id"]) for r in i["rows"] if r["level"] == "MUST" and not r["ok"]]
    return verdict, got


def main():
    profiles = {}
    bad = 0
    for doc, prof, withs, expected in CASES:
        if prof not in profiles:
            profiles[prof] = V.load_profile(prof)[0]
        reg = V.Registry()
        for w in withs:
            reg.add(w)
        bom = reg.add(doc)
        verdict, got = failing(bom, profiles[prof], reg)
        if isinstance(expected, tuple):
            ok = verdict == "does-not-conform" and len(got) == expected[1]
            want = "does not conform, with %d failing MUST checks" % expected[1]
        else:
            ok = sorted(got) == sorted(expected) and (verdict == "conforms") == (not expected)
            want = expected
        bad += not ok
        label = "%s against %s%s" % (os.path.relpath(doc, ROOT), os.path.basename(prof),
                                     " (with %d cited)" % len(withs) if withs else "")
        print("  %s %s: %s" % ("ok  " if ok else "FAIL", label, verdict))
        if not ok:
            print("       expected %s\n       got      %s (%d)" % (want, got, len(got)))
    print("%d case(s), %d unexpected" % (len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
