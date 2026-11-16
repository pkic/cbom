#!/usr/bin/env python3
"""Write the substation automation (OT) worked example.

One illustrative protection IED, described by its supplier against the component profile
pqc-migration-ot, which extends the change core. Two non-conforming variants show one failing
rule each. The values are illustrative: they are taken from the profiles in the published
IEC 62351 standards and stay illustrative until a supplier volunteers a real product.

Usage: python3 tools/build_ot_examples.py
Then:  python3 tests/check-cyclonedx.py && python3 tests/check-examples.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "methodology", "examples")
CONTEXT = os.path.join(OUT, "context")
SITE = "https://pkic.github.io/cbom/methodology/examples/"
P = "pkic:profile:"
STAMP = "2026-11-16T09:00:00Z"
AUTHOR = {"name": "PKI Consortium CBOM Profiles Working Group (worked example)",
          "url": [{"name": "website", "url": "https://pkic.org"}]}
SERIAL = {"product": "0d7a5e10-62f3-4b51-9e3a-61850000c001",
          "sbom": "0d7a5e10-62f3-4b51-9e3a-61850000b000"}
SUBJECT_PURL = "pkg:generic/example-grid/protection-ied@4.2.0"
FW_PURL = "pkg:generic/example-grid/ied-firmware@4.2.0"
CRYPTO_PURL = "pkg:generic/example-grid/ied-crypto-library@3.1.0"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write(path, obj):
    data = dump(obj)
    with open(path, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def props(pairs):
    out = []
    for k, v in pairs:
        for one in (v if isinstance(v, list) else [v]):
            out.append({"name": P + k, "value": one})
    return out


def party(ref, role, org):
    return {"bom-ref": ref, "roles": [{"role": role}], "organization": org}


def ident(purl):
    return [{"party": "party:document-author", "identities": [{"scheme": "purl", "value": purl}]}]


def subject(extra):
    return {"type": "device", "bom-ref": "dev:protection-ied", "name": "Protection IED (illustrative)",
            "version": "4.2.0",
            "description": "A generic line-protection IED at firmware 4.2.0, as its supplier would describe it. "
                           "Ten interfaces, described from the outside. Values are illustrative.",
            "properties": extra, "identifiers": ident(SUBJECT_PURL),
            "parties": [party("party:document-author", "author", AUTHOR),
                        party("party:dev:protection-ied:supplier", "supplier",
                              {"name": "Example Grid Equipment (illustrative)"})]}


# Capability per purpose, stated once on each library and inherited by the interfaces it
# provides (decision 0022, K9). The protection traffic is already symmetric; every asymmetric
# purpose is blocked by the IEC 62351 profiles, which list no post-quantum algorithms.
CAPABILITY = [
    ("key-establishment", "planned", "standard"),
    ("encryption", "available", None),
    ("entity-authentication", "planned", "standard"),
    ("data-integrity", "available", None),
    ("non-repudiation", "not-planned", "product"),
    ("key-protection", "under-evaluation", "hardware"),
    ("key-derivation", "available", None),
]


def capability():
    out = []
    for purpose, status, blocker in CAPABILITY:
        out.append(("capabilityByPurpose:%s:capabilityStatus" % purpose, status))
        if blocker:
            out.append(("capabilityByPurpose:%s:blockedBy" % purpose, blocker))
    return out


def library(ref, name, purl, extra):
    return {"type": "library", "bom-ref": ref, "name": name,
            "properties": props([("enablementMethod", "software-update"), ("minimumProductVersion", "unreleased"),
                                 ("coexistence", "simultaneous")] + extra + capability()),
            "externalReferences": [{"type": "bom", "url": "urn:cdx:%s/1#%s" % (SERIAL["sbom"], ref),
                                    "comment": "This library's entry in the companion SBOM."}],
            "identifiers": ident(purl)}


def iface(ref, name, kind, pairs):
    return {"type": "service", "bom-ref": ref, "name": name,
            "properties": props([("interfaceType", kind)] + pairs + [("defaultState", "enabled")])}


TLS = [("keyExchange", "ECDH-P256"), ("encryption", "AES-128-GCM"), ("authentication", "ECDSA-P256-SHA256"),
       ("protocolVersionsSupported", ["1.2", "1.3"]), ("keyExchangeSupported", ["ECDH-P256", "ECDH-P384"]),
       ("authenticationSupported", ["ECDSA-P256-SHA256", "ECDSA-P384-SHA384"])]


def interfaces():
    return [
        iface("svc-goose", "GOOSE protection messages (IEC 62351-6)", "service", [
            ("protocol", "GOOSE"), ("protocolVersion", "2.1"),
            ("endpointRole:publisher", "endpoint:ied"), ("endpointRole:subscriber", "endpoint:bay-peers"),
            ("keyExchange", "none"), ("encryption", "none"), ("authentication", "HMAC-SHA256"),
            ("protocolVersionsSupported", "2.1"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", ["HMAC-SHA256", "AES-GMAC"]),
            ("negotiationControl", "Not applicable: one-way multicast"),
            ("integrationConstraints", "Layer-2 multicast with a 3 ms transfer time for trip messages "
                                       "(IEC 61850-5 P2/P3). A per-message signature does not fit: ML-DSA-44 "
                                       "signatures are 2,420 bytes. Already symmetric."),
            ("keyStoreRef", "int-gdoi"), ("certificationImpact", "not-applicable")]),
        iface("svc-sv", "Sampled values (IEC 62351-6)", "service", [
            ("protocol", "SV"), ("protocolVersion", "2.1"),
            ("endpointRole:publisher", "endpoint:merging-unit"), ("endpointRole:subscriber", "endpoint:ied"),
            ("keyExchange", "none"), ("encryption", "none"), ("authentication", "HMAC-SHA256"),
            ("protocolVersionsSupported", "2.1"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", ["HMAC-SHA256", "AES-GMAC"]),
            ("negotiationControl", "Not applicable: one-way multicast"),
            ("integrationConstraints", "Layer-2 multicast within the sampling interval. Already symmetric."),
            ("keyStoreRef", "int-gdoi"), ("certificationImpact", "not-applicable")]),
        iface("tls-mms", "TLS for MMS (IEC 62351-3)", "service", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:station-server"), ("endpointRole:server", "endpoint:ied")] + TLS + [
            ("negotiationControl", "Groups and signature schemes limited to those IEC 62351-3:2023 profiles"),
            ("integrationConstraints", "Conformance to IEC 62351-3 permits only the groups and signature schemes it "
                                       "lists, and it lists no post-quantum ones."),
            ("keyStoreRef", "sto-keys"), ("certificationImpact", "recertification"),
            ("certificationScheme", "IEC 62443-4-2 (ISASecure CSA)")]),
        iface("svc-mms", "MMS with role-based access tokens (IEC 62351-4, -8)", "service", [
            ("protocol", "MMS"), ("protocolVersion", "2003"),
            ("endpointRole:client", "endpoint:station-server"), ("endpointRole:server", "endpoint:ied"),
            ("keyExchange", "none"), ("encryption", "none"), ("authentication", "ECDSA-P256-SHA256"),
            ("protocolVersionsSupported", "2003"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", "ECDSA-P256-SHA256"),
            ("negotiationControl", "Token signature algorithm set by the access token issuer"),
            ("integrationConstraints", "Carried over tls-mms. The token signature is what grants authority."),
            ("keyStoreRef", "sto-keys"), ("certificationImpact", "retest"),
            ("certificationScheme", "IEC 61850 conformance testing")]),
        iface("int-gdoi", "GDOI group key distribution (IEC 62351-9)", "interconnect", [
            ("protocol", "GDOI"), ("protocolVersion", "1"),
            ("endpointRole:group-member", "endpoint:ied"), ("endpointRole:key-server", "endpoint:station-server"),
            ("keyExchange", "MODP-2048"), ("encryption", "AES-128-CBC"), ("authentication", "RSA-2048"),
            ("protocolVersionsSupported", "1"), ("keyExchangeSupported", ["MODP-2048", "ECDH-P256"]),
            ("authenticationSupported", ["RSA-2048", "ECDSA-P256-SHA256"]),
            ("negotiationControl", "Set by the key server's group policy"),
            ("integrationConstraints", "The key plane for GOOSE and SV. GDOI over IKEv1 phase 1 (RFC 8052). Its "
                                       "successor G-IKEv2 (RFC 9838) is not profiled by IEC 62351-9:2023, which "
                                       "provides no post-quantum measures."),
            ("certificationImpact", "recertification"), ("certificationScheme", "IEC 62443-4-2 (ISASecure CSA)")]),
        iface("mgmt-enrol", "Certificate enrolment (EST, IEC 62351-9)", "management", [
            ("protocol", "EST"), ("protocolVersion", "1"),
            ("endpointRole:client", "endpoint:ied"), ("endpointRole:server", "endpoint:enrolment-service")] + [
            ("keyExchange", "ECDH-P256"), ("encryption", "AES-128-GCM"), ("authentication", "ECDSA-P256-SHA256"),
            ("protocolVersionsSupported", "1"), ("keyExchangeSupported", ["ECDH-P256", "ECDH-P384"]),
            ("authenticationSupported", ["ECDSA-P256-SHA256", "ECDSA-P384-SHA384"]),
            ("negotiationControl", "Certificate profile set by the enrolment service"),
            ("integrationConstraints", "Device identity certificates with long validity."),
            ("updateMechanism", "none"), ("certificationImpact", "retest"),
            ("certificationScheme", "IEC 61850 conformance testing")]),
        iface("upd-fw", "Firmware update", "management", [
            ("protocol", "TLS"), ("protocolVersion", "1.2"),
            ("endpointRole:client", "endpoint:engineering-workstation"), ("endpointRole:server", "endpoint:ied")] + TLS + [
            ("negotiationControl", "Firmware signature algorithm fixed by the bootloader"),
            ("integrationConstraints", "Firmware images are signed ECDSA-P256-SHA256 and verified by the bootloader."),
            ("updateMechanism", "local-network"), ("updateAuthority", "operator"),
            ("updateAuthoritySupported", ["operator", "installer"]),
            ("verifierReplaceable", "via-bootloader-update"), ("certificationImpact", "recertification"),
            ("certificationScheme", "IEC 62443-4-2 (ISASecure CSA)")]),
        iface("mgmt-eng", "Engineering configuration download", "management", [
            ("protocol", "TLS"), ("protocolVersion", "1.2"),
            ("endpointRole:client", "endpoint:engineering-workstation"), ("endpointRole:server", "endpoint:ied")] + TLS + [
            ("negotiationControl", "Inherits the device TLS settings"),
            ("integrationConstraints", "Protected by TLS and access control. The configuration file itself is not signed."),
            ("updateMechanism", "none"), ("certificationImpact", "retest"),
            ("certificationScheme", "IEC 61850 conformance testing")]),
        iface("peer-ptp", "Time synchronisation (IEEE 1588)", "peer", [
            ("protocol", "PTP"), ("protocolVersion", "2.1"),
            ("endpointRole:client", "endpoint:ied"), ("endpointRole:server", "endpoint:grandmaster-clock"),
            ("keyExchange", "none"), ("encryption", "none"), ("authentication", "none"),
            ("protocolVersionsSupported", "2.1"), ("keyExchangeSupported", "none"), ("authenticationSupported", "none"),
            ("negotiationControl", "Not applicable"),
            ("integrationConstraints", "No cryptography.")]),
        iface("sto-keys", "Device private key and trust anchors", "storage", [
            ("encryption", "none"), ("keyWrapping", "none"),
            ("negotiationControl", "Not applicable"),
            ("integrationConstraints", "Whether a secure element holds the device key is under evaluation."),
            ("keyReplaceable", "software-update"), ("certificationImpact", "recertification"),
            ("certificationScheme", "IEC 62443-4-2 (ISASecure CSA)")]),
    ]


PROVIDES = {"lib:ied-firmware": ["svc-goose", "svc-sv", "svc-mms", "int-gdoi", "upd-fw", "peer-ptp", "sto-keys"],
            "lib:ied-crypto": ["tls-mms", "mgmt-enrol", "mgmt-eng"]}


def product(sbom_hash):
    libs = [library("lib:ied-firmware", "IED firmware (illustrative)", FW_PURL, []),
            library("lib:ied-crypto", "Embedded TLS and certificate library (illustrative)", CRYPTO_PURL, [])]
    comps = libs + interfaces()
    bom = {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "EXAMPLE CBOM, lifecycle stage 'implemented'. A generic protection IED described by its supplier "
                    "against pqc-migration-ot v0.1, which extends the change core v0.1. Illustrative values, taken from the "
                    "profiles in the published IEC 62351 standards. Conforms to interface-enumeration v0.3, "
                    "interface-disclosure v0.9, change-core v0.1 and pqc-migration-ot v0.1.",
        "serialNumber": "urn:uuid:" + SERIAL["product"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                     "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": subject(props([
            ("coverage", "all"), ("subjectType", "product"), ("updateMechanism", "local-network"),
            ("contextAbsent:support-lifecycle", "not-published"), ("contextAbsent:roadmap", "not-published"),
            ("contextAbsent:vulnerability-statements", "not-published")])), "components": comps}],
        "dependencies": [{"ref": "dev:protection-ied", "dependsOn": [c["bom-ref"] for c in comps]}] +
                        [{"ref": k, "provides": v} for k, v in PROVIDES.items()],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % SERIAL["sbom"],
             "comment": "Companion SBOM of the same firmware: examples/context/ot-protection-ied-sbom.cdx.json.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://psirt.example.com/advisories",
             "comment": "The supplier's security advisories (illustrative).",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://psirt.example.com/",
             "comment": "The supplier's product security contact (illustrative).",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])}]}
    return bom


def sbom():
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "EXAMPLE SBOM. The companion SBOM of the illustrative protection IED firmware, referenced by the "
                        "product record under interface-disclosure#R1 by BOM-Link and SHA-256. It lists only the two "
                        "libraries the record names, so its composition is declared incomplete.",
            "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subject([]), "components": [
                {"type": "library", "bom-ref": "lib:ied-firmware", "name": "IED firmware (illustrative)",
                 "version": "4.2.0", "identifiers": ident(FW_PURL)},
                {"type": "library", "bom-ref": "lib:ied-crypto",
                 "name": "Embedded TLS and certificate library (illustrative)", "version": "3.1.0",
                 "identifiers": ident(CRYPTO_PURL)}]}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def drop(bom, ref, attr):
    for c in bom["inventories"][0]["components"]:
        if c.get("bom-ref") == ref:
            c["properties"] = [p for p in c["properties"] if p["name"] != P + attr]


def variant(bom, serial_tail, comment):
    v = copy.deepcopy(bom)
    v["serialNumber"] = "urn:uuid:0d7a5e10-62f3-4b51-9e3a-6185000%s" % serial_tail
    v["$comment"] = comment
    return v


def main():
    os.makedirs(CONTEXT, exist_ok=True)
    h = write(os.path.join(CONTEXT, "ot-protection-ied-sbom.cdx.json"), sbom())
    prod = product(h)
    write(os.path.join(OUT, "cbom-ot-protection-ied-product.cdx.json"), prod)

    v = variant(prod, "0c013", "NON-CONFORMING EXAMPLE. The protection IED record with updateMechanism left out "
                "on the enrolment interface. Fails change-core#I13 only.")
    drop(v, "mgmt-enrol", "updateMechanism")
    write(os.path.join(OUT, "cbom-ot-protection-ied-product-fail-core-I13.cdx.json"), v)

    v = variant(prod, "0c004", "NON-CONFORMING EXAMPLE. The protection IED record with verifierReplaceable left out "
                "on the firmware update interface. Fails pqc-migration-ot#I4 only: the operator cannot tell whether "
                "the device can be updated or has to be replaced.")
    drop(v, "upd-fw", "verifierReplaceable")
    write(os.path.join(OUT, "cbom-ot-protection-ied-product-fail-ot-I4.cdx.json"), v)
    print("written to", OUT)


if __name__ == "__main__":
    main()
