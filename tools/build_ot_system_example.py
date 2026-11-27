#!/usr/bin/env python3
"""Build the reference substation's system record, the worked example of system-disclosure.

Writes, in docs/methodology/examples/:
  cbom-ot-sas-system-configured.cdx.json        the reference substation as its integrator delivers it
  cbom-ot-sas-system-fail-keyprovider.cdx.json  GOOSE in use, the component providing its keys not named

The system record cites two product records by BOM-Link and digest: the protection IED and
lib60870, which the substation gateway embeds. It lists every interface of both, each joined to
the product interface it realises, with its usage, the component that provides its keys, and the
zone and conduit facts the OT overlay asks for (operational technology domain document, 8.3).
Values are illustrative.

Usage: python3 tools/build_ot_system_example.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
METH = os.path.join(ROOT, "docs", "methodology")
OUT = os.path.join(METH, "examples")
P = "pkic:profile:"
IED = os.path.join(METH, "examples", "cbom-ot-protection-ied-product.cdx.json")
LIB60870 = os.path.join(METH, "examples", "cbom-lib60870-2.4.1-product.cdx.json")
SERIAL = "5a5e0001-2b3c-4d5e-8f90-616850000002"
SUBJECT_TAG = "tag:integrator.example,2026:system/sas-110kv-reference"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# --------------------------------------------------------------------------- #
# The system record                                                           #
# --------------------------------------------------------------------------- #
DROP = ["protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported", "certification",
        "updateAuthoritySupported", "verifierReplaceable", "keyReplaceable", "algorithmSelection",
        "integrationConstraints", "defaultState", "capabilityByPurpose", "enablementMethod",
        "availableFromVersion", "transitionMode", "updateMechanism", "updateAuthority"]

# What the design does with each interface of the protection IED (bay 1).
# usage, zone, zonePath, crossesConduit, keysProvidedBy
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
# usage, zone, zonePath, crossesConduit, keysProvidedBy, configured values
GATEWAY = {
    "tls-104": ("in-use", "station-bus", "crosses-zones", "sys:substation-gateway", "sys:enrolment-service",
                [("protocolVersion", "1.2"), ("keyExchange", "RSA-PKCS1-1.5"), ("encryption", "AES-128-CBC"),
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
    ied_refs = {c["bom-ref"] for c in ied["inventories"][0]["components"]}
    ifaces = []
    for c in ied["inventories"][0]["components"]:
        if c.get("type") != "service":
            continue
        usage, zone, path, conduit, keys = DESIGN[c["bom-ref"]]
        i = copy.deepcopy(c)
        i["bom-ref"] = "ied1:" + c["bom-ref"]
        i["name"] = "Protection IED, bay 1: " + c["name"]
        add = [("correspondsTo", "urn:cdx:%s/1#%s" % (serial, c["bom-ref"])), ("designUse", usage), ("zone", zone)]
        add += [(k, v) for k, v in (("zonePath", path), ("crossesConduit", conduit), ("keysProvidedBy", keys)) if v]
        props = strip(i["properties"])
        for p in props:
            # A key store named by the product's own bom-ref is renamed to this record's copy,
            # so that the reference resolves inside the system record.
            if p["name"] == P + "keysStoredIn" and p["value"] in ied_refs:
                p["value"] = "ied1:" + p["value"]
        i["properties"] = props + [{"name": P + k, "value": v} for k, v in add]
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
        add = [("correspondsTo", "urn:cdx:%s/1#%s" % (gw_serial, c["bom-ref"])), ("designUse", usage), ("zone", zone)]
        add += [(k, v) for k, v in (("zonePath", path), ("crossesConduit", conduit), ("keysProvidedBy", keys)) if v]
        i["properties"] = props + [{"name": P + k, "value": v} for k, v in add]
        ifaces.append(i)
    others = [{"type": "device", "bom-ref": ref, "name": name,
               "properties": [{"name": P + "zone", "value": zone},
                              {"name": P + "correspondsTo", "value": "no-product-document"}]}
              for ref, name, zone in SYSTEM_COMPONENTS]
    comps = ifaces + others
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "EXAMPLE system record for system-disclosure v0.1, and for the OT overlay ot-system. The reference substation automation system as its "
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
                           {"name": P + "claimedSecurityLevel", "value": "sl-c-2"}],
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
    v["serialNumber"] = v["serialNumber"][:-1] + {"crossesConduit": "3", "keysProvidedBy": "4"}[drop]
    v["$comment"] = comment
    for c in v["inventories"][0]["components"]:
        if c["bom-ref"] == ref:
            c["properties"] = [p for p in c["properties"] if p["name"] != P + drop]
    return v


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(IED, "rb") as fh:
        raw = fh.read()
    with open(LIB60870, "rb") as fh:
        gw_raw = fh.read()
    rec = system_record(json.loads(raw), raw, json.loads(gw_raw), gw_raw)
    files = {
        "cbom-ot-sas-system-configured.cdx.json": rec,
        "cbom-ot-sas-system-fail-keyprovider.cdx.json": variant(
            rec, "ied1:svc-goose", "keysProvidedBy",
            "NON-CONFORMING EXAMPLE for system-disclosure. The conforming record with keysProvidedBy removed from "
            "the GOOSE interface, which is in use. Fails system-disclosure#I3."),
    }
    for name, obj in files.items():
        with open(os.path.join(OUT, name), "wb") as fh:
            fh.write(dump(obj))
    print("written to", OUT)


if __name__ == "__main__":
    main()
