#!/usr/bin/env python3
"""Check every Keycloak lifecycle example against its expected verdict.

Each non-conforming example is meant to fail exactly the rules listed here, so a
change to a profile or to the evaluator that alters any verdict is caught.
Usage: python3 check_examples.py    Exit: 0 all as expected, 1 otherwise
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluate_draft as E  # noqa: E402

EX = os.path.join(HERE, "..", "examples")
PR = os.path.join(HERE, "..", "profiles")
BASE = os.path.join(PR, "profile-interface-disclosure-0.9.rules.json")
DEPL = os.path.join(PR, "profile-deployment-disclosure-0.1.rules.json")
OLD = os.path.join(HERE, "..", "..", "pqc-migration-depths", "examples", "cbom-keycloak-pqc-pass.cyclonedx.json")
P, C = "kc-product-implemented.cdx.json", "kc-deployment-configured.cdx.json"

CASES = [
    # (document, profile, documents supplied for joins, expected failed MUST rules)
    (P, BASE, [], []),
    ("kc-product-implemented-fail-R5.cdx.json", BASE, [],
     ["crypto:protocol:tls-https/interface-disclosure#R5"]),
    ("kc-product-intended-fail-I8.cdx.json", BASE, [],
     ["%s/interface-disclosure#I8" % i for i in (
         "crypto:protocol:tls-https", "crypto:protocol:tls-mgmt", "crypto:protocol:int-db",
         "crypto:protocol:int-ldap", "crypto:protocol:int-broker", "crypto:protocol:int-smtp",
         "crypto:protocol:int-cache", "service:svc-oidc", "service:svc-saml", "service:svc-http",
         "service:mgmt-admin", "service:svc-broker-tokens", "service:sto-realm-keys")] +
     ["crypto:protocol:tls-https/interface-disclosure#I5", "crypto:protocol:tls-mgmt/interface-disclosure#I5",
      "service:svc-broker-tokens/interface-disclosure#I5"] +
     ["crypto:protocol:%s/interface-disclosure#%s" % (i, r)
      for i in ("int-db", "int-ldap", "int-broker", "int-smtp") for r in ("I3", "I4", "I5")]),
    (C, DEPL, [P], []),
    ("kc-deployment-configured-fail-literal.cdx.json", DEPL, [P],
     ["crypto:protocol:int-db/interface-disclosure#I3", "crypto:protocol:int-db/interface-disclosure#I4",
      "crypto:protocol:int-db/interface-disclosure#I5"]),
    ("kc-deployment-observed.cdx.json", DEPL, [P, C], []),
    ("kc-deployment-observed-fail-unknown.cdx.json", DEPL, [P, C],
     ["crypto:protocol:int-db/interface-disclosure#I3"]),
    ("kc-deployment-observed-fail-P1.cdx.json", DEPL, [P, C], ["deployment-disclosure#P1"]),
    # The pqc-migration worked example as it stands, against the revised baseline.
    (OLD, BASE, [], ["interface-disclosure#P3", "interface-disclosure#P5", "interface-disclosure#P6"]),
]


def main():
    bad = 0
    for doc, prof, withs, expected in CASES:
        reg = E.Registry()
        for w in withs:
            reg.add(os.path.join(EX, w))
        path = doc if os.path.isabs(doc) else os.path.join(EX, doc)
        bom = reg.add(path)
        profile, _ = E.load_profile(prof)
        verdict, report = E.validate(bom, profile, reg)
        got = E.failed_musts(report)
        ok = sorted(got) == sorted(expected) and (verdict == "conforms") == (not expected)
        bad += not ok
        print("%s  %-48s %-22s %s" % ("ok  " if ok else "FAIL", os.path.basename(path)[:48],
                                      profile["profileTag"], verdict))
        if not ok:
            print("      expected %s\n      got      %s" % (expected, got))
    print("%d case(s), %d unexpected" % (len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
