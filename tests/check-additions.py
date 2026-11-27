#!/usr/bin/env python3
"""Checks for the evaluator facilities added for Release 1.

Each check builds what it needs from a published example, so a change to the validator that
breaks one of these facilities fails here rather than passing silently:

  references inside a record   refersToLocal (system-disclosure I3)
  values from a declared list  inSubjectList (fixture on the substation record)
  coverage of cited records    coversCitedInterfaces (system-disclosure P2)
  grace periods                graceUntil, judged against --as-of
  members added to a group     addMembers and forKeys (pqc-migration-extended G1.5, G1.6)
  purposes taken in depth      a derived profile may not drop one
  cited verdicts               --cited-profile
  the claim format             'evaluated', claim format 0.2
  what terminates an interface terminatedBy (interface-disclosure I14, MUST in deployment-disclosure v0.3)
  certification impact         change-core and pqc-migration I17 and I18 (R2-23)
  key stores in a cited record keysStoredIn by BOM-Link (pqc-migration-extended I8, R2-27)

Usage:  python3 tests/check-additions.py
Exit:   0 every check as expected, 1 otherwise
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
EX = os.path.join(M, "examples")
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

P = "pkic:profile:"
SAS = "cbom-ot-sas-system-configured.cdx.json"
CITED = ["cbom-ot-protection-ied-product.cdx.json", "cbom-lib60870-2.4.1-product.cdx.json"]
bad = 0


def report(ok, label, detail=""):
    global bad
    bad += not ok
    print("  %s %s" % ("ok  " if ok else "FAIL", label))
    if not ok and detail:
        print("       %s" % (detail,))


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def evaluate(bom, profile_path, cited=(), as_of=None):
    reg = V.Registry()
    for c in cited:
        reg.add(os.path.join(EX, c))
    prof = V.load_profile(profile_path)[0]
    verdict, rep = V.validate(bom, prof, reg, as_of)
    failed = [r["id"] for r in rep["product"] + rep["references"] if r["level"] == "MUST" and not r["ok"]]
    for i in rep["interfaces"]:
        failed += ["%s/%s" % (i["interfaceId"], r["id"]) for r in i["rows"]
                   if r["level"] == "MUST" and not r["ok"]]
    return verdict, failed, rep


def set_prop(bom, ref, name, value):
    for c in bom["inventories"][0]["components"]:
        if c.get("bom-ref") == ref:
            c["properties"] = [p for p in c["properties"] if p["name"] != P + name] + \
                              [{"name": P + name, "value": value}]


SYS = os.path.join(M, "profile-system-disclosure.rules.json")
sas = load(os.path.join(EX, SAS))

# references inside a record
b = copy.deepcopy(sas)
set_prop(b, "ied1:tls-mms", "keysProvidedBy", "sys:enrolment-servce")
v, f, _ = evaluate(b, SYS, CITED)
report(f == ["ied1:tls-mms/system-disclosure#I3"],
       "a key provider that names no element of the record fails system-disclosure I3", f)

# values from a declared list
LIST = os.path.join(FIX, "profile-in-subject-list.rules.json")
v, f, _ = evaluate(sas, LIST, CITED)
report(v == "conforms", "every zone is one the system declares", f)
b = copy.deepcopy(sas)
set_prop(b, "ied1:svc-goose", "zone", "station_bus")
v, f, _ = evaluate(b, LIST, CITED)
report(f == ["ied1:svc-goose/in-subject-list#I1"], "a zone the system does not declare fails", f)

# coverage of cited records
b = copy.deepcopy(sas)
b["inventories"][0]["components"] = [c for c in b["inventories"][0]["components"]
                                     if c.get("bom-ref") != "gw1:svc-101"]
v, f, _ = evaluate(b, SYS, CITED)
report(f == ["system-disclosure#P2"], "a cited interface left out of the system record fails P2", f)
v, f, rep = evaluate(b, SYS, [])
p2 = [r for r in rep["product"] if r["id"] == "system-disclosure#P2"][0]
report(p2["ok"] and "not evaluated" in p2["detail"],
       "without the cited records, P2 says it was not evaluated", p2["detail"])

# grace periods
GRACE = os.path.join(FIX, "profile-grace.rules.json")
prod = load(os.path.join(EX, "cbom-keycloak-product.cdx.json"))
v, f, rep = evaluate(prod, GRACE, [], "2026-11-18")
states = {r["state"] for i in rep["interfaces"] for r in i["rows"] if r["id"] == "grace#I1"}
report(v == "conforms" and states == {"grace"}, "before graceUntil, a failure is reported, not counted",
       (v, states))
v, f, _ = evaluate(prod, GRACE, [], "2027-06-01")
report(v == "does-not-conform" and all(x.endswith("grace#I1") for x in f) and f,
       "from graceUntil, the failure counts", f[:2])

# members added to an inherited group, for some keys only
v, f, rep = evaluate(prod, os.path.join(M, "profile-pqc-migration-extended.rules.json"))
keys = sorted({r["id"].split("[")[1].rstrip("]") for i in rep["interfaces"] for r in i["rows"]
               if r["id"].startswith("pqc-migration-extended#G1.5[")})
report(keys == ["entity-authentication", "non-repudiation"],
       "pqc-migration-extended G1.5 is asked for the signing purposes only", keys)

# purposes taken in depth
try:
    V.load_profile(os.path.join(FIX, "profile-drops-purpose.rules.json"))
    report(False, "a derived profile that drops a purpose taken in depth is refused")
except V.ProfileError as err:
    report("drops purpose" in str(err), "a derived profile that drops a purpose taken in depth is refused",
           str(err))

# cited verdicts and the claim format
out = subprocess.run([sys.executable, os.path.join(M, "validate_cbom.py"), os.path.join(EX, SAS), SYS,
                      "--with", os.path.join(EX, CITED[0]), "--with", os.path.join(EX, CITED[1]),
                      "--cited-profile", os.path.join(M, "profile-interface-disclosure.rules.json")],
                     capture_output=True, text=True).stdout
cited_lines = [l for l in out.splitlines() if l.startswith("CITED")]
report(len(cited_lines) == 2 and all("CONFORMS" in l for l in cited_lines),
       "--cited-profile reports each cited record's verdict beside the system record's", cited_lines)
claim = load(os.path.join(M, "claim-example.json"))
report(claim.get("claimFormatVersion") == "0.2" and all("evaluated" in e for e in claim["profiles"]),
       "the example claim uses claim format 0.2 and 'evaluated'")

# what terminates an interface
DEPL = os.path.join(M, "profile-deployment-disclosure.rules.json")
BASE = os.path.join(M, "profile-interface-disclosure.rules.json")
conf = load(os.path.join(EX, "cbom-keycloak-deployment-configured.cdx.json"))
_, failed, _ = evaluate(conf, DEPL, ["cbom-keycloak-product.cdx.json"])
report(not failed, "the configured Keycloak record states what terminates each interface", failed)
for c in conf["inventories"][0]["components"]:
    if c.get("bom-ref") == "service:svc-http":
        c["properties"] = [q for q in c["properties"] if q["name"] != P + "terminatedBy"]
_, failed, _ = evaluate(conf, DEPL, ["cbom-keycloak-product.cdx.json"])
report(failed == ["service:svc-http/interface-disclosure#I14"],
       "deployment-disclosure fails an interface that does not say what terminates it", failed)
_, failed, _ = evaluate(conf, BASE, ["cbom-keycloak-product.cdx.json"])
report("service:svc-http/interface-disclosure#I14" not in failed,
       "the baseline leaves terminatedBy optional", failed)
for c in conf["inventories"][0]["components"]:
    if c.get("bom-ref") == "service:svc-http":
        c["properties"].append({"name": P + "terminatedBy", "value": "crypto:protocol:no-such-ingress"})
_, failed, _ = evaluate(conf, DEPL, ["cbom-keycloak-product.cdx.json"])
report(failed == ["service:svc-http/interface-disclosure#I14"],
       "terminatedBy must name a component of the same record", failed)

# certification impact, shared by the change core and PQC Migration (R2-23)
CORE = os.path.join(M, "profile-change-core.rules.json")
PQC = os.path.join(M, "profile-pqc-migration.rules.json")
OT = os.path.join(M, "profile-pqc-migration-ot.rules.json")
ied = load(os.path.join(EX, "cbom-ot-protection-ied-product.cdx.json"))
core_rules = {r["id"]: r for r in load(CORE)["interfaceRules"]}
pqc_rules = {r["id"]: r for r in load(PQC)["interfaceRules"]}
report(all(core_rules[k] == pqc_rules[k] for k in ("I17", "I18")),
       "the change core and PQC Migration declare I17 and I18 identically")
_, failed, rep = evaluate(ied, OT)
rows = [r["id"] for i in rep["interfaces"] for r in i["rows"]]
report(not failed and "change-core#I17" in rows and "pqc-migration-ot#I1" not in rows,
       "the protection IED conforms to the substation profile, which reports change-core#I17", failed)
b = copy.deepcopy(ied)
for c in b["inventories"][0]["components"]:
    if c.get("bom-ref") == "tls-mms":
        c["properties"] = [q for q in c["properties"] if q["name"] != P + "certificationImpact"]
_, failed, _ = evaluate(b, OT)
report(failed == ["tls-mms/change-core#I17"],
       "the substation profile raises certificationImpact to MUST", failed)
_, failed, _ = evaluate(b, CORE)
report("tls-mms/change-core#I17" not in failed,
       "the change core asks for certificationImpact at SHOULD", failed)


def i8(rep, iface):
    for i in rep["interfaces"]:
        if i["interfaceId"] == iface:
            for r in i["rows"]:
                if r["id"] == "pqc-migration-extended#I8":
                    return r
    return None


# a key store in a record the document cites (R2-27)
EXT = os.path.join(M, "profile-pqc-migration-extended.rules.json")
kc = load(os.path.join(EX, "cbom-keycloak-product.cdx.json"))
ied_key = V.doc_key(ied)
b = copy.deepcopy(kc)
set_prop(b, "service:sto-realm-keys", "keysStoredIn", ied_key + "#sto-keys")
_, _, rep = evaluate(b, EXT, ["cbom-ot-protection-ied-product.cdx.json"])
r = i8(rep, "service:sto-realm-keys")
report(r is not None and not r["ok"],
       "keysStoredIn into a record the document does not cite fails", r)
b["externalReferences"] = (b.get("externalReferences") or []) + [
    {"type": "bom", "url": ied_key,
     "properties": [{"name": P + "context", "value": "cited-document"}]}]
_, _, rep = evaluate(b, EXT, ["cbom-ot-protection-ied-product.cdx.json"])
r = i8(rep, "service:sto-realm-keys")
report(r is not None and r["ok"], "keysStoredIn may name a key store in a cited record", r)
set_prop(b, "service:sto-realm-keys", "keysStoredIn", ied_key + "#no-such-store")
_, _, rep = evaluate(b, EXT, ["cbom-ot-protection-ied-product.cdx.json"])
r = i8(rep, "service:sto-realm-keys")
report(r is not None and not r["ok"], "the key store must exist in the cited record", r)

print("%s" % ("all additions behave as specified" if not bad else "%d check(s) failed" % bad))
sys.exit(1 if bad else 0)
