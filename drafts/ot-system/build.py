#!/usr/bin/env python3
"""Build the OT system overlay, ot-system, and its first worked example.

Writes, in this folder:
  profile-ot-system.rules.json                          the overlay (OT domain document, 8.3), v0.2-draft
  examples/cbom-sas-reference-system-configured.cdx.json   the reference substation as delivered
  examples/cbom-sas-reference-system-fail-conduit.cdx.json one path between zones without its conduit
  examples/cbom-sas-reference-system-fail-keyprovider.cdx.json  GOOSE in use, key provider not named

The overlay extends the generic system overlay, system-disclosure, which extends the interface
disclosure baseline v0.10. The system record cites two product records by BOM-Link and digest: the
protection IED and lib60870, which the substation gateway embeds. Each interface is joined to the
product interface it realises.

Draft only. Nothing in docs/methodology/ is changed. Values are illustrative.

Usage: python3 drafts/ot-system/build.py
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
LIB60870 = os.path.join(ROOT, "drafts", "ot-lib60870", "examples", "cbom-lib60870-2.4.1-product.cdx.json")
SERIAL = "5a5e0001-2b3c-4d5e-8f90-616850000002"
SUBJECT_TAG = "tag:integrator.example,2026:system/sas-110kv-reference"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# --------------------------------------------------------------------------- #
# The overlay                                                                 #
# --------------------------------------------------------------------------- #
def profile():
    return {
        "$comment": "DRAFT. The OT system overlay, proposed in the operational technology domain document, 8.3, "
                    "where its rules are S1 to S5. One overlay for every OT sector; the reference substation is its "
                    "first worked example. S1, S2 and S4 are not specific to OT and now sit in the generic overlay "
                    "system-disclosure, published in Release 1, which this profile extends. Each rule here names the "
                    "S-rule it implements.",
        "profileId": "pkic.example.ot-system",
        "profileTag": "ot-system",
        "title": "OT System Overlay (draft)",
        "version": "0.2-draft",
        "conformanceKeywords": "BCP 14 (MUST/SHOULD/MAY)",
        "extends": {"profileId": "pkic.example.system-disclosure", "version": "0.1",
                    "file": "../../docs/methodology/profile-system-disclosure.rules.json"},
        "objective": {
            "$comment": "C1. The consumer is the asset owner, or an assessor acting for one, receiving a system "
                        "from an integrator. The generic overlay answers what the design uses and who provides its "
                        "keys; this profile adds where each interface sits and which conduit it crosses.",
            "consumer": "An asset owner, or an assessor acting for one, accepting an OT system from its integrator.",
            "decision": "For each interface the design uses: which zone it sits in and which conduit it crosses, "
                        "so that a migration of one component can be planned with the zones and conduits it "
                        "affects.",
            "decisionOptions": ["accept the system as delivered",
                                "accept it and record the migration dependencies in the register",
                                "require the integrator to change the design before acceptance"]},
        "scope": {
            "$comment": "As the generic overlay: one system design, as its integrator delivers it.",
            "subjectTypes": ["system"], "orientation": "inventory",
            "relationshipTypes": ["interface"], "lifecycleStages": ["configured"]},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "zonePathVocabulary": ["within-zone", "crosses-zones"],
        "securityLevelVocabulary": ["SL-C 1", "SL-C 2", "SL-C 3", "SL-C 4"],
        "productRules": [
            {"id": "P1", "description": "S3. System names its zones", "level": "MUST",
             "constraint": {"productAttribute": "zones"}, "withholdable": False,
             "note": "The zones of the design, in the sense of IEC 62443-3-2. Each interface names one of them "
                     "(I1)."},
            {"id": "P2", "description": "S5. System states the IEC 62443-3-3 capability security level its "
                                        "integrator claims for it as delivered",
             "level": "SHOULD", "constraint": {"productAttribute": "claimedLevel62443",
                                               "enumRef": "securityLevelVocabulary"},
             "withholdable": True,
             "note": "S5. A claim the record reports, not a judgement it makes: the capability security level "
                     "(SL-C) the integrator states for the system as delivered. SHOULD, because many systems in "
                     "service were never assessed against IEC 62443-3-3, and a MUST would exclude them."}],
        "interfaceRules": [
            {"id": "I1", "attribute": "zone", "level": "MUST", "constraint": {"inSubjectList": "zones"},
             "withholdable": False,
             "note": "S3. The zone the interface sits in, one of the zones the system names (P1)."},
            {"id": "I2", "attribute": "zonePath", "level": "MUST",
             "constraint": {"enumRef": "zonePathVocabulary"}, "withholdable": False,
             "requiredWhen": {"attribute": "usage", "equals": "in-use"},
             "note": "S3. Whether the connection on this interface stays in its zone or crosses into another."},
            {"id": "I3", "attribute": "conduitRef", "level": "MUST",
             "constraint": {"refersToLocal": {}},
             "withholdable": True,
             "requiredWhen": {"attribute": "zonePath", "equals": "crosses-zones"},
             "note": "S3. The conduit the path crosses, as the bom-ref of the system component that implements "
                     "it: a firewall, a VPN router or a gateway. A conduit is an interface of that device, not an "
                     "object of its own. Withholdable, because a public record may not show the network design."}],
        "exclusions": [
            {"item": "Latency budgets, compensating controls and site variations",
             "reason": "They belong in the asset owner's register, which describes sites, not the design."},
            {"item": "A timing class for each interface", "reason": "An integration constraint of the product."}],
        "changelog": [
            {"version": "0.1-draft", "date": "2026-11-17",
             "summary": "First draft, built on the reference substation.", "changes": []},
            {"version": "0.2-draft", "date": "2026-11-17",
             "summary": "Extends the generic overlay system-disclosure. S1, S2 and S4 moved there.",
             "changes": []}],
        "artifacts": {"conformingExample": "examples/cbom-sas-reference-system-configured.cdx.json",
                      "nonConformingExample": "examples/cbom-sas-reference-system-fail-conduit.cdx.json"},
    }


# --------------------------------------------------------------------------- #
# The system record                                                           #
# --------------------------------------------------------------------------- #
DROP = ["protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported", "certification",
        "updateAuthoritySupported", "verifierReplaceable", "keyReplaceable", "negotiationControl",
        "integrationConstraints", "defaultState", "capabilityByPurpose", "enablementMethod",
        "minimumProductVersion", "coexistence", "updateMechanism", "updateAuthority"]

# What the design does with each interface of the protection IED (bay 1).
# usage, zone, zonePath, conduitRef, keyProvider
DESIGN = {
    "svc-goose": ("in-use", "station-bus", "within-zone", None, "sys:station-server-gdoi"),
    "svc-sv": ("not-connected", "station-bus", None, None, None),
    "tls-mms": ("in-use", "station-bus", "within-zone", None, "sys:enrolment-service"),
    "svc-mms": ("in-use", "station-bus", "within-zone", None, "sys:enrolment-service"),
    "int-gdoi": ("in-use", "station-bus", "within-zone", None, "sys:station-server-gdoi"),
    "mgmt-enrol": ("in-use", "station-bus", "crosses-zones", "sys:substation-gateway", "sys:enrolment-service"),
    "upd-fw": ("disabled", "station-bus", None, None, None),
    "mgmt-eng": ("in-use", "station-bus", "crosses-zones", "sys:substation-gateway", "sys:enrolment-service"),
    "peer-ptp": ("in-use", "station-bus", "within-zone", None, "none"),
    "sto-keys": ("in-use", "station-bus", "within-zone", None, "product"),
}

# The substation gateway's link to the control centre. The gateway's supplier has published no record;
# the integrator knows it embeds lib60870 v2.4.1 and joins to that record. Values are what the design
# configures: the control centre's front end accepts only the cipher suite IEC 62351-4:2018 makes
# mandatory, TLS_RSA_WITH_AES_128_CBC_SHA256 (illustrative).
# usage, zone, zonePath, conduitRef, keyProvider, configured values
GATEWAY = {
    "tls-104": ("in-use", "station-bus", "crosses-zones", "sys:substation-gateway", "sys:enrolment-service",
                [("protocolVersion", "1.2"), ("keyExchange", "RSA"), ("encryption", "AES-128-CBC"),
                 ("authentication", "RSA-2048")]),
    "svc-104": ("disabled", "station-bus", None, None, None, []),
    "svc-101": ("not-connected", "station-bus", None, None, None, []),
}

SYSTEM_COMPONENTS = [
    ("sys:station-server-gdoi", "Station server: GDOI group key server (IEC 62351-9)", "station-bus"),
    ("sys:enrolment-service", "Certificate enrolment service and issuing CA, control centre", "control-centre"),
    ("sys:substation-gateway", "Substation gateway and firewall: the conduit between the station bus and the "
                               "control centre. Embeds lib60870 v2.4.1 for IEC 60870-5-104", "station-bus"),
]


def strip(props):
    return [p for p in props if not any(p["name"].startswith(P + d) for d in DROP)]


def system_record(ied, ied_bytes, gw, gw_bytes):
    serial = ied["serialNumber"].split(":")[-1]
    gw_serial = gw["serialNumber"].split(":")[-1]
    ifaces = []
    for c in ied["inventories"][0]["components"]:
        if c.get("type") != "service":
            continue
        usage, zone, path, conduit, keys = DESIGN[c["bom-ref"]]
        i = copy.deepcopy(c)
        i["bom-ref"] = "ied1:" + c["bom-ref"]
        i["name"] = "Protection IED, bay 1: " + c["name"]
        add = [("correspondsTo", "urn:cdx:%s/1#%s" % (serial, c["bom-ref"])), ("usage", usage), ("zone", zone)]
        add += [(k, v) for k, v in (("zonePath", path), ("conduitRef", conduit), ("keyProvider", keys)) if v]
        i["properties"] = strip(i["properties"]) + [{"name": P + k, "value": v} for k, v in add]
        ifaces.append(i)
    for c in gw["inventories"][0]["components"]:
        if c.get("type") != "service":
            continue
        usage, zone, path, conduit, keys, values = GATEWAY[c["bom-ref"]]
        i = copy.deepcopy(c)
        i.pop("externalReferences", None)
        i["bom-ref"] = "gw1:" + c["bom-ref"]
        i["name"] = "Substation gateway: " + c["name"]
        set_ = dict(values)
        props = []
        for p in strip(i["properties"]):
            k = p["name"][len(P):]
            if k in set_:
                p = {"name": p["name"], "value": set_.pop(k)}
            elif k == "endpointRole:server":
                p = {"name": p["name"], "value": "endpoint:substation-gateway"}
            elif k == "endpointRole:client":
                p = {"name": p["name"], "value": "endpoint:control-centre-front-end"}
            props.append(p)
        add = [("correspondsTo", "urn:cdx:%s/1#%s" % (gw_serial, c["bom-ref"])), ("usage", usage), ("zone", zone)]
        add += [(k, v) for k, v in (("zonePath", path), ("conduitRef", conduit), ("keyProvider", keys)) if v]
        i["properties"] = props + [{"name": P + k, "value": v} for k, v in add]
        ifaces.append(i)
    others = [{"type": "device", "bom-ref": ref, "name": name,
               "properties": [{"name": P + "zone", "value": zone},
                              {"name": P + "correspondsTo", "value": "no-product-document"}]}
              for ref, name, zone in SYSTEM_COMPONENTS]
    comps = ifaces + others
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE for ot-system v0.2-draft. The reference substation automation system as its "
                    "integrator delivers it, stage 'configured'. Lists every interface of the two product records it "
                    "cites, the protection IED and lib60870 (embedded in the substation gateway), each joined to the "
                    "product interface it realises, with the zone it sits in, the conduit it crosses and the "
                    "component that provides its keys. The key server, the enrolment service and the gateway itself "
                    "have no product record. Illustrative values.",
        "serialNumber": "urn:uuid:" + SERIAL, "version": 1,
        "metadata": {"timestamp": "2026-11-17T09:00:00Z", "lifecycles": [{"phase": "operations"}],
                     "supplier": {"name": "Example Integrator (illustrative)"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": {
            "type": "platform", "bom-ref": "system:sas-110kv-reference",
            "name": "110 kV substation automation system, reference design (illustrative)",
            "properties": [{"name": P + "subjectType", "value": "system"},
                           {"name": P + "coverage", "value": "partial"},
                           {"name": P + "zones", "value": "station-bus"},
                           {"name": P + "zones", "value": "control-centre"},
                           {"name": P + "claimedLevel62443", "value": "SL-C 2"}],
            "identifiers": [{"party": "party:document-author", "identities": [
                {"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."}, "value": SUBJECT_TAG}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "Example Integrator (illustrative)"}}]},
            "components": comps}],
        "dependencies": [{"ref": "system:sas-110kv-reference", "dependsOn": [k["bom-ref"] for k in comps]}],
        "externalReferences": [{"type": "bom", "url": "urn:cdx:%s/1" % serial,
                                "comment": "The protection IED's product record.",
                                "properties": [{"name": P + "context", "value": "cited-document"}],
                                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(ied_bytes).hexdigest()}]},
                               {"type": "bom", "url": "urn:cdx:%s/1" % gw_serial,
                                "comment": "The lib60870 product record. The gateway embeds lib60870 v2.4.1.",
                                "properties": [{"name": P + "context", "value": "cited-document"}],
                                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(gw_bytes).hexdigest()}]}]}


def variant(rec, ref, drop, comment):
    v = copy.deepcopy(rec)
    v["serialNumber"] = v["serialNumber"][:-1] + {"conduitRef": "3", "keyProvider": "4"}[drop]
    v["$comment"] = comment
    for c in v["inventories"][0]["components"]:
        if c["bom-ref"] == ref:
            c["properties"] = [p for p in c["properties"] if p["name"] != P + drop]
    return v


def main():
    """Write the overlay and its one non-conforming example. The conforming system record is the
    worked example of system-disclosure, built by tools/build_ot_system_example.py."""
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "profile-ot-system.rules.json"), "wb") as fh:
        fh.write(dump(profile()))
    with open(os.path.join(METH, "examples", "cbom-ot-sas-system-configured.cdx.json"), encoding="utf-8") as fh:
        rec = json.load(fh)
    v = variant(rec, "ied1:mgmt-enrol", "conduitRef",
                "DRAFT NON-CONFORMING EXAMPLE for ot-system. The published substation system record with conduitRef "
                "removed from the enrolment interface, whose path crosses from the station bus to the control centre. "
                "Fails ot-system#I3 (S3).")
    with open(os.path.join(OUT, "cbom-sas-reference-system-fail-conduit.cdx.json"), "wb") as fh:
        fh.write(dump(v))
    print("written to", HERE)


if __name__ == "__main__":
    main()
