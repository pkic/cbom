#!/usr/bin/env python3
"""Check every published example CBOM against its expected verdicts.

Each example is evaluated against the profiles it is meant to show something
about, with the documents it cites supplied, and must fail exactly the rules
listed here. A non-conforming example is meant to isolate one rule, so a change
to a profile or to the validator that moves any verdict is caught here.

Usage:  python3 tests/check-examples.py
Exit:   0 every verdict as expected, 1 otherwise
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
EX = os.path.join(M, "examples")
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

ENUM, BASE, DEPL = "interface-enumeration", "interface-disclosure", "deployment-disclosure"
PQC, EXT, PROC = "pqc-migration", "pqc-migration-extended", "procurement"
CORE, OT = "change-core", "pqc-migration-ot"
SYS, SVC, SVCR = "system-disclosure", "service-disclosure", "service-disclosure-restricted"
IOT = "iot-device"
LIB = "cbom-lib60870-2.4.1-product.cdx.json"
SAS = "cbom-ot-sas-system-configured.cdx.json"
IED = "cbom-ot-protection-ied-product.cdx.json"
PRODUCT = "cbom-keycloak-product.cdx.json"
CONF = "cbom-keycloak-deployment-configured.cdx.json"
OBS = "cbom-keycloak-deployment-observed.cdx.json"
TLS_ETC = ("crypto:protocol:int-db", "crypto:protocol:int-ldap", "crypto:protocol:int-broker",
           "crypto:protocol:int-smtp")
ALL13 = ("crypto:protocol:tls-https", "crypto:protocol:tls-mgmt") + TLS_ETC + (
    "crypto:protocol:int-cache", "service:svc-oidc", "service:svc-saml", "service:svc-http",
    "service:mgmt-admin", "service:svc-broker-tokens", "service:sto-realm-keys")

INTENDED = (["%s/%s#I8" % (i, BASE) for i in ALL13] +
            ["%s/%s#%s" % (i, BASE, r) for i in TLS_ETC for r in ("I3", "I4", "I5")] +
            ["crypto:protocol:tls-https/%s#I5" % BASE, "crypto:protocol:tls-mgmt/%s#I5" % BASE,
             "service:svc-broker-tokens/%s#I5" % BASE])

# (example, profile, cited documents supplied, expected failed MUST rules)
CASES = [
    (PRODUCT, ENUM, [], []),
    (PRODUCT, BASE, [], []),
    (PRODUCT, PQC, [], []),
    (PRODUCT, EXT, [], []),
    (PRODUCT, PROC, [], []),
    ("legacy/cbom-keycloak-product-1.7.cdx.json", BASE, [], []),
    ("legacy/cbom-keycloak-product-1.7.cdx.json", EXT, [], []),
    ("legacy/cbom-keycloak-product-1.7.cdx.json", PROC, [], []),
    ("cbom-keycloak-product-fail-R5.cdx.json", BASE, [], ["crypto:protocol:tls-https/%s#R5" % BASE]),
    ("cbom-keycloak-product-fail-P2.cdx.json", BASE, [], ["%s#P2" % BASE]),
    ("cbom-keycloak-product-fail-P2.cdx.json", ENUM, [], []),
    ("cbom-keycloak-product-disclosure-states.cdx.json", BASE, [],
     ["crypto:protocol:int-cache/%s#I5" % BASE, "service:svc-saml/%s#I4" % BASE]),
    ("cbom-keycloak-product-disclosure-states.cdx.json", ENUM, [], []),
    ("cbom-keycloak-product-fail-pqc-I12.cdx.json", PQC, [], ["service:sto-realm-keys/%s#I12" % PQC]),
    ("cbom-keycloak-product-fail-pqc-I12.cdx.json", BASE, [], []),
    ("cbom-keycloak-product-fail-ext-I3.cdx.json", EXT, [], ["service:mgmt-admin/%s#I3" % EXT]),
    ("cbom-keycloak-product-fail-ext-I3.cdx.json", PQC, [], []),
    ("cbom-keycloak-product-fail-procurement-P1.cdx.json", PROC, [], ["%s#P1" % PROC]),
    ("cbom-keycloak-product-intended.cdx.json", BASE, [], INTENDED),
    ("cbom-keycloak-product-intended.cdx.json", ENUM, [], []),
    ("legacy/cbom-keycloak-scanner-output.cdx.json", ENUM, [],
     ["%s#%s" % (ENUM, r) for r in ("P1", "P3", "P4", "P5", "P6")]),
    (CONF, DEPL, [PRODUCT], []),
    (CONF, DEPL, [], []),
    ("cbom-keycloak-deployment-configured-fail-literal.cdx.json", DEPL, [PRODUCT],
     ["crypto:protocol:int-db/%s#%s" % (BASE, r) for r in ("I3", "I4", "I5")]),
    (OBS, DEPL, [PRODUCT, CONF], []),
    ("cbom-keycloak-deployment-observed-fail-unknown.cdx.json", DEPL, [PRODUCT, CONF],
     ["crypto:protocol:int-db/%s#I3" % BASE]),
    ("cbom-keycloak-deployment-observed-fail-unknown.cdx.json", ENUM, [PRODUCT, CONF], []),
    ("cbom-keycloak-deployment-observed-fail-P1.cdx.json", DEPL, [PRODUCT, CONF], ["%s#P1" % DEPL]),
    ("cbom-keycloak-deployment-observed-outside.cdx.json", DEPL, [PRODUCT],
     ["crypto:protocol:ing-tls/%s#I9" % BASE]),
    ("cbom-keycloak-deployment-observed-outside.cdx.json", ENUM, [PRODUCT], []),
    # The far end of the database connection, recorded by the team that runs it. Its
    # peerInterface (I4) resolves into the Keycloak configured record when that is supplied.
    ("cbom-postgres-deployment-configured.cdx.json", DEPL, [CONF], []),
    ("cbom-postgres-deployment-configured.cdx.json", DEPL, [], []),
    # The substation automation (OT) worked example: one protection IED, described by its
    # supplier against the component profile, which extends the change core.
    (IED, ENUM, [], []),
    (IED, BASE, [], []),
    (IED, CORE, [], []),
    (IED, OT, [], []),
    ("cbom-ot-protection-ied-product-fail-core-I13.cdx.json", CORE, [], ["mgmt-enrol/%s#I13" % CORE]),
    ("cbom-ot-protection-ied-product-fail-core-I13.cdx.json", BASE, [], []),
    ("cbom-ot-protection-ied-product-fail-ot-I4.cdx.json", OT, [], ["upd-fw/%s#I4" % OT]),
    ("cbom-ot-protection-ied-product-fail-ot-I4.cdx.json", CORE, [], []),
    # lib60870, the open-source IEC 60870-5-101/104 library the substation gateway embeds, written
    # from its public source. It meets the baseline and not the change core.
    (LIB, ENUM, [], []),
    (LIB, BASE, [], []),
    # The reference substation as its integrator delivers it: a system record citing the IED and
    # lib60870. Without the cited records, coverage (P2) cannot be evaluated and passes as such.
    (SAS, SYS, [IED, LIB], []),
    (SAS, SYS, [], []),
    (SAS, BASE, [IED, LIB], []),
    ("cbom-ot-sas-system-fail-keyprovider.cdx.json", SYS, [IED, LIB],
     ["ied1:svc-goose/%s#I3" % SYS]),
    ("cbom-ot-sas-system-fail-keyprovider.cdx.json", BASE, [IED, LIB], []),
    # Keycloak run as a managed service: the restricted and public variants, and a store
    # without its key-custody statements.
    ("cbom-keycloak-service-restricted.cdx.json", SVC, [CONF, PRODUCT], []),
    ("cbom-keycloak-service-restricted.cdx.json", SVCR, [CONF, PRODUCT], []),
    ("cbom-keycloak-service-public.cdx.json", SVC, [CONF, PRODUCT], []),
    ("cbom-keycloak-service-public.cdx.json", SVCR, [CONF, PRODUCT], ["%s#P1" % SVCR]),
    ("cbom-keycloak-service-fail-custody.cdx.json", SVC, [CONF, PRODUCT],
     ["service:sto-realm-keys/%s#%s" % (SVC, r) for r in ("I1", "I3")]),
    # Two LoRaWAN soil sensors against the IoT device estate profile, which extends the change
    # core: S1 can never be updated, S2 can. The variant without a resource bound fails P1 only.
    ("cbom-iot-sensor-s1-product.cdx.json", BASE, [], []),
    ("cbom-iot-sensor-s1-product.cdx.json", CORE, [], []),
    ("cbom-iot-sensor-s1-product.cdx.json", IOT, [], []),
    ("cbom-iot-sensor-s2-product.cdx.json", IOT, [], []),
    ("cbom-iot-sensor-s1-product-fail-P1.cdx.json", IOT, [], ["%s#P1" % IOT]),
    ("cbom-iot-sensor-s1-product-fail-P1.cdx.json", CORE, [], []),
    # A product profile refuses to treat a deployment record as a product record.
    (CONF, PQC, [PRODUCT], None),
    (PRODUCT, DEPL, [], None),
]


def main():
    profiles = {}
    bad = 0
    for doc, tag, withs, expected in CASES:
        if tag not in profiles:
            profiles[tag] = V.load_profile(os.path.join(M, "profile-%s.rules.json" % tag))[0]
        reg = V.Registry()
        for w in withs:
            reg.add(os.path.join(EX, w))
        bom = reg.add(os.path.join(EX, doc))
        verdict, report = V.validate(bom, profiles[tag], reg)
        got = [r["id"] for r in report["product"] + report["references"]
               if r["level"] == "MUST" and not r["ok"]]
        for i in report["interfaces"]:
            got += ["%s/%s" % (i["interfaceId"], r["id"]) for r in i["rows"]
                    if r["level"] == "MUST" and not r["ok"]]
        if expected is None:
            ok = verdict == "does-not-conform" and "%s#P5" % BASE in got
            want = "does not conform, with interface-disclosure#P5 (subject type outside scope)"
        else:
            ok = sorted(got) == sorted(expected) and (verdict == "conforms") == (not expected)
            want = expected
        bad += not ok
        label = "%s against %s%s" % (doc, tag, " (with %s)" % ", ".join(withs) if withs else "")
        print("  %s %s: %s" % ("ok  " if ok else "FAIL", label, verdict))
        if not ok:
            print("       expected %s\n       got      %s" % (want, got))
    print("%d case(s), %d unexpected" % (len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
