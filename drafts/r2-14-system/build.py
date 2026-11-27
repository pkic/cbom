#!/usr/bin/env python3
"""Draft for R2-14: the subject type 'system' in the interface disclosure baseline.

Writes the baseline as v0.10-draft, with 'service' (R2-11) and 'system' (R2-14) added to
its subject types and an identifier form for each, and a system record for the reference
substation that cites the published protection IED product record.

A system record describes one system design as the integrator delivers it. It is written
at the stage 'configured', like a deployment record: each interface it lists realises a
product interface, named in 'correspondsTo', and states the values the design configures.
It differs from a deployment record in its subject: one design, built at many sites,
rather than one site.

Usage: python3 drafts/r2-14-system/build.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
METH = os.path.join(ROOT, "docs", "methodology")
OUT = os.path.join(HERE, "examples")
P = "pkic:profile:"
IED = os.path.join(METH, "examples", "cbom-ot-protection-ied-product.cdx.json")
SERIAL = "5a5e0001-2b3c-4d5e-8f90-616850000001"
SUBJECT_TAG = "tag:integrator.example,2026:system/sas-110kv-reference"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def baseline():
    with open(os.path.join(METH, "profile-interface-disclosure.rules.json"), encoding="utf-8") as fh:
        b = json.load(fh)
    b["$comment"] = ("DRAFT for R2-11 and R2-14. The interface disclosure baseline v0.9 with the subject "
                     "types 'service' and 'system' added to its scope, and a tag-URI identifier form for each. "
                     "No other change.")
    b["version"] = "0.10-draft"
    b["scope"]["subjectTypes"] = ["product", "deployment", "service", "system"]
    for r in b["productRules"]:
        if r["id"] == "P3":
            r["constraint"]["subjectIdentified"]["startsWith"].update({"service": "tag:", "system": "tag:"})
    b["identifierSchemes"]["subject"].update({"service": "tag-uri", "system": "tag-uri"})
    b["changelog"].append({"version": "0.10-draft", "date": "2026-11-17", "changes": [
        {"kind": "relaxing", "summary": "Accepts the subject types 'service' (R2-11) and 'system' (R2-14), each "
         "identified by a tag URI. No rule changes for product or deployment records."}]})
    return b


def strip(props, drop):
    return [p for p in props if not any(p["name"].startswith(P + d) for d in drop)]


def system_record(ied, ied_bytes):
    serial = ied["serialNumber"].split(":")[-1]
    keep = []
    # Capability, certification and update-path facts belong to the product record; the
    # system record states what the design configures, and joins to the rest.
    drop = ["protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported",
            "certification", "updateAuthoritySupported", "verifierReplaceable", "keyReplaceable",
            "algorithmSelection", "integrationConstraints", "defaultState", "capabilityByPurpose",
            "enablementMethod", "availableFromVersion", "transitionMode", "updateMechanism", "updateAuthority"]
    usage = {"peer-ptp": "in-use", "mgmt-eng": "in-use"}
    for c in ied["inventories"][0]["components"]:
        if c.get("type") != "service":
            continue
        i = copy.deepcopy(c)
        i["bom-ref"] = "ied1:" + c["bom-ref"]
        i["name"] = "Protection IED, bay 1: " + c["name"]
        i["properties"] = strip(i["properties"], drop) + [
            {"name": P + "correspondsTo", "value": "urn:cdx:%s/1#%s" % (serial, c["bom-ref"])},
            {"name": P + "designUse", "value": usage.get(c["bom-ref"], "in-use")}]
        keep.append(i)
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE system record for R2-14. The reference substation automation system as its "
                    "integrator delivers it, stage 'configured'. Lists the interfaces of the one component record "
                    "published so far, the protection IED, each joined to the product interface it realises. "
                    "Illustrative values.",
        "serialNumber": "urn:uuid:" + SERIAL, "version": 1,
        "metadata": {"timestamp": "2026-11-17T09:00:00Z", "lifecycles": [{"phase": "operations"}],
                     "supplier": {"name": "Example Integrator (illustrative)"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": {
            "type": "platform", "bom-ref": "system:sas-110kv-reference",
            "name": "110 kV substation automation system, reference design (illustrative)",
            "properties": [{"name": P + "subjectType", "value": "system"},
                           {"name": P + "coverage", "value": "partial"}],
            "identifiers": [{"party": "party:document-author", "identities": [
                {"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."}, "value": SUBJECT_TAG}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "Example Integrator (illustrative)"}}]},
            "components": keep}],
        "dependencies": [{"ref": "system:sas-110kv-reference", "dependsOn": [k["bom-ref"] for k in keep]}],
        "externalReferences": [{"type": "bom", "url": "urn:cdx:%s/1" % serial,
                                "comment": "The protection IED's product record.",
                                "properties": [{"name": P + "context", "value": "cited-document"}],
                                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(ied_bytes).hexdigest()}]}]}


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "profile-interface-disclosure.rules.json"), "wb") as fh:
        fh.write(dump(baseline()))
    with open(IED, "rb") as fh:
        raw = fh.read()
    with open(os.path.join(OUT, "cbom-sas-reference-system-configured.cdx.json"), "wb") as fh:
        fh.write(dump(system_record(json.loads(raw), raw)))
    print("written to", HERE)


if __name__ == "__main__":
    main()
