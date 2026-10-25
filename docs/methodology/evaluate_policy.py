#!/usr/bin/env python3
"""Evaluate CBOMs against an example policy and write a policy result.

A CBOM records facts. A judgement about those facts, such as whether an
interface meets a post-quantum target or whether an algorithm is past its
transition date, is computed here at evaluation time from a versioned policy
(decision 0002). The result names the policy and its version, the date the
policy was applied, and every CBOM it read, each by SHA-256 digest. The result
points to the CBOMs; a CBOM never points to a result.

Two evaluation methods are implemented, selected by the policy's 'method':

  algorithm-transition  classify each disclosed algorithm against a dated
                        schedule (example: NIST IR 8547 initial public draft)
  readiness-gap         join a product record, a configured record and an
                        observation along correspondsTo, and place each
                        interface and purpose in one gap class

Usage:
    python3 evaluate_policy.py <policy.json> <cbom.json> [<cbom.json> ...]
                               [--date YYYY-MM-DD] [--out result.json]
Exit: 0 evaluated, 2 usage error
"""
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate_cbom as V  # noqa: E402

RESULT_FORMAT = "pkic.cbom.policy-result"
RESULT_FORMAT_VERSION = "0.1"
LITERALS = {"none": "not-applicable", "deployment-defined": "not-fixed-by-product",
            "peer-defined": "decided-by-peer"}
NOT_ASSERTED = [
    "that the disclosed values are true; the policy was applied to what the CBOMs state",
    "anything about interfaces or algorithms the CBOMs do not disclose",
    "that the policy is right; it is an example, and its source should be checked",
    "anything after the evaluation date; the same facts give a different result under a later date or policy version",
]


def norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def classifier(policy):
    table = {}
    for entry in policy.get("classification", []):
        for n in entry.get("names", []):
            table[norm(n)] = entry
    return lambda name: table.get(norm(name))


def as_list(v):
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def doc_record(path, bom):
    data = open(path, "rb").read()
    product = V.extract_product(bom)
    return {"file": os.path.basename(path), "serialNumber": bom.get("serialNumber"),
            "version": bom.get("version"), "subject": product.get("identifier"),
            "subjectType": product.get("subjectType"), "stage": product.get("docStage"),
            "digest": {"alg": "SHA-256", "value": hashlib.sha256(data).hexdigest()}}


# --------------------------------------------------------------------------- #
# algorithm-transition                                                        #
# --------------------------------------------------------------------------- #
def schedule_for(policy, cls):
    for rule in policy.get("schedule", []):
        w = rule.get("when", {})
        if "quantumVulnerable" in w and w["quantumVulnerable"] != cls.get("quantumVulnerable"):
            continue
        s = cls.get("securityStrength")
        if "securityStrength" in w and s != w["securityStrength"]:
            continue
        if "securityStrengthBelow" in w and not (s is not None and s < w["securityStrengthBelow"]):
            continue
        if "securityStrengthAtLeast" in w and not (s is not None and s >= w["securityStrengthAtLeast"]):
            continue
        return rule
    return None


def status_on(rule, date):
    if rule.get("status"):
        return rule["status"], None
    nxt = None
    status = "acceptable"
    for key, label in (("deprecatedAfter", "deprecated"), ("disallowedAfter", "disallowed")):
        after = rule.get(key)
        if not after:
            continue
        if date > after:
            status = label
        elif nxt is None:
            nxt = {"status": label, "after": after}
    return status, nxt


def algorithm_transition(policy, docs, date, registry):
    classify = classifier(policy)
    findings = []
    for path, bom in docs:
        for iface in V.extract_interfaces(bom, registry):
            for attr in policy["inputs"]["attributes"]:
                for value in as_list(iface.get(attr)):
                    finding = {"document": os.path.basename(path), "interface": iface["interfaceId"],
                               "attribute": attr, "value": value}
                    if value in LITERALS:
                        finding["status"] = LITERALS[value]
                    else:
                        cls = classify(value)
                        if not cls:
                            finding["status"] = "unclassified"
                        else:
                            rule = schedule_for(policy, cls)
                            status, nxt = status_on(rule or {}, date)
                            finding.update({"family": cls.get("family"),
                                            "securityStrength": cls.get("securityStrength"),
                                            "quantumVulnerable": cls.get("quantumVulnerable"),
                                            "status": status})
                            if nxt:
                                finding["nextTransition"] = nxt
                    findings.append(finding)
    summary = {}
    for f in findings:
        summary[f["status"]] = summary.get(f["status"], 0) + 1
    return findings, summary


# --------------------------------------------------------------------------- #
# readiness-gap                                                               #
# --------------------------------------------------------------------------- #
def meets(policy_target, name, classify):
    cls = classify(name)
    if not cls:
        return False
    if "quantumVulnerable" in policy_target and cls.get("quantumVulnerable") != policy_target["quantumVulnerable"]:
        return False
    fams = policy_target.get("familyIn")
    return not fams or cls.get("family") in fams


def readiness_gap(policy, docs, date, registry):
    classify = classifier(policy)
    by_stage = {}
    for path, bom in docs:
        stage = V.extract_product(bom).get("docStage")
        by_stage[stage] = (path, bom, {i["interfaceId"]: i for i in V.extract_interfaces(bom, registry)})

    def target_of(iface):
        _doc, ref = V.split_bomlink(iface.get("correspondsTo"))
        return ref

    prod = by_stage.get("implemented", (None, None, {}))[2]
    conf = by_stage.get("configured", (None, None, {}))[2]
    obs = by_stage.get("observed", (None, None, {}))[2]
    rows, seen_conf, seen_prod = [], set(), set()
    for oid, o in obs.items():
        c = conf.get(target_of(o)) if target_of(o) in conf else None
        p = prod.get(target_of(c)) if c is not None and target_of(c) in prod else \
            (prod.get(target_of(o)) if target_of(o) in prod else None)
        rows.append((p, c, o))
        if c is not None:
            seen_conf.add(c["interfaceId"])
        if p is not None:
            seen_prod.add(p["interfaceId"])
    for cid, c in conf.items():
        if cid in seen_conf:
            continue
        p = prod.get(target_of(c)) if target_of(c) in prod else None
        rows.append((p, c, None))
        if p is not None:
            seen_prod.add(p["interfaceId"])
    for pid, p in prod.items():
        if pid not in seen_prod:
            rows.append((p, None, None))

    findings = []
    for p, c, o in rows:
        name = (p or c or o)["interfaceId"]
        for purpose, spec in policy["purposes"].items():
            attr, cap_attr, target = spec["attribute"], spec["capabilityAttribute"], spec["target"]
            vp = as_list(p.get(attr)) if p else []
            vc = as_list(c.get(attr)) if c else []
            vo = as_list(o.get(attr)) if o else []
            capability = as_list(p.get(cap_attr)) + vp if p else []
            entry = ((p or {}).get("_groups") or {}).get("capabilityByPurpose", {}).get(purpose, {})
            finding = {"interface": {"implemented": p["interfaceId"] if p else None,
                                     "configured": c["interfaceId"] if c else None,
                                     "observed": o["interfaceId"] if o else None},
                       "purpose": purpose,
                       "evidence": {"implemented": vp or None, "capability": capability or None,
                                    "configured": vc or None, "observed": vo or None}}
            latest = vo if o else vc
            latest_iface = o or c
            ok = lambda vals: [v for v in vals if meets(target, v, classify)]
            stages_present = [v for v in (vp, vc, vo) if v]
            if (conf or obs) and not (c or o):
                cls = "not-deployed"
            elif latest_iface is not None and all(as_list(latest_iface.get(a)) == ["none"]
                                                  for a in ("keyExchange", "encryption", "authentication")):
                cls = "unprotected"
            elif stages_present and all(v == ["none"] for v in stages_present):
                cls = "not-applicable"
            elif latest and latest != ["none"] and all(meets(target, v, classify) for v in latest):
                cls = "target-met"
                if not o:
                    finding["note"] = "configured, not observed"
            elif c and ok(vc) and o and not all(meets(target, v, classify) for v in vo):
                cls = "enabled-not-negotiated"
            elif ok(capability) or entry.get("capabilityStatus") == "available":
                cls = "capable-not-enabled" if (c or o) else "capable"
            elif p is None:
                cls = "unknown"
                finding["note"] = "no product record to say what the product can do"
            else:
                cls = "not-capable"
            if cls in ("not-capable", "capable", "capable-not-enabled") and entry:
                finding["productCapability"] = {k: entry[k] for k in
                                                ("capabilityStatus", "blockedBy", "roadmapRef") if k in entry}
            finding["class"] = cls
            findings.append(finding)
    summary = {}
    for f in findings:
        summary[f["class"]] = summary.get(f["class"], 0) + 1
    return findings, summary


METHODS = {"algorithm-transition": algorithm_transition, "readiness-gap": readiness_gap}


def evaluate(policy_path, cbom_paths, date):
    policy = json.load(open(policy_path, encoding="utf-8"))
    method = METHODS.get(policy.get("method"))
    if not method:
        raise SystemExit("unknown policy method %r" % policy.get("method"))
    registry = V.Registry()
    docs = []
    for p in cbom_paths:
        docs.append((p, registry.add(p)))
    findings, summary = method(policy, docs, date, registry)
    pdata = open(policy_path, "rb").read()
    return {
        "resultFormat": RESULT_FORMAT, "resultFormatVersion": RESULT_FORMAT_VERSION,
        "policy": {"policyId": policy.get("policyId"), "version": policy.get("version"),
                   "file": os.path.basename(policy_path),
                   "digest": {"alg": "SHA-256", "value": hashlib.sha256(pdata).hexdigest()}},
        "evaluationDate": date,
        "documents": [doc_record(p, b) for p, b in docs],
        "summary": summary,
        "findings": findings,
        "notAsserted": NOT_ASSERTED,
    }


def main(argv):
    args, date, out, i = [], datetime.date.today().isoformat(), None, 1
    while i < len(argv):
        if argv[i] == "--date":
            date, i = argv[i + 1], i + 2
            continue
        if argv[i] == "--out":
            out, i = argv[i + 1], i + 2
            continue
        args.append(argv[i])
        i += 1
    if len(args) < 2:
        print(__doc__)
        return 2
    result = evaluate(args[0], args[1:], date)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
