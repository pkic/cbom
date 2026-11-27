#!/usr/bin/env python3
"""Build the telecom service-assurance overlay and its first worked example.

Writes, in this folder:
  profile-telecom-service-assurance.rules.json            the overlay
  examples/cbom-sepp-product.cdx.json                      an illustrative SEPP, stage 'implemented'
  examples/sepp-5.1.0-sbom.cdx.json                        its companion SBOM
  examples/cbom-roaming-interconnect-system.cdx.json       the operator's roaming interconnect, 'configured'
  examples/cbom-roaming-interconnect-fail-service.cdx.json   N32-f in use, the services it carries not named
  examples/cbom-roaming-interconnect-fail-proxy.cdx.json     N32-c crosses the operator operatorBoundary, proxy not named

Service assurance asks which services depend on which interfaces, so that a weakness or a
migration at one interface can be traced to the services and commitments it affects (telecom
CBOM document, 3.2.4). The overlay extends the generic system overlay, system-disclosure, which
supplies the citations, the join to product interfaces, usage and the key provider. It adds the
services the system delivers, the services each interface carries, and the operator operatorBoundary.

Draft only. Nothing in docs/methodology/ is changed. Values are illustrative; the SEPP is not a
real product.

Usage: python3 drafts/telecom-service-assurance/build.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "examples")
P = "pkic:profile:"
STAMP = "2026-11-17T09:00:00Z"
SERIAL = {"sepp": "5e990001-3c4d-4e5f-9a01-329020000001", "sbom": "5e990001-3c4d-4e5f-9a01-3290200000b0",
          "system": "5e990001-3c4d-4e5f-9a01-329020000010"}
SEPP_PURL = "pkg:generic/example-telco/sepp@5.1.0"
OPENSSL_PURL = "pkg:github/openssl/openssl@openssl-3.5.4"
JOSE_PURL = "pkg:generic/example-telco/jose-library@2.0.0"
OPENSSH_PURL = "pkg:github/openssh/openssh-portable@V_9_9_P1"
SUBJECT_TAG = "tag:operator.example,2026:system/roaming-interconnect-reference"
SERVICES = ["inbound-roaming", "outbound-roaming", "mission-critical-roaming"]


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def props(pairs):
    out = []
    for k, v in pairs:
        for one in (v if isinstance(v, list) else [v]):
            out.append({"name": P + k, "value": one})
    return out


def ident(purl):
    return [{"party": "party:document-author", "identities": [{"scheme": "purl", "value": purl}]}]


# --------------------------------------------------------------------------- #
# The overlay                                                                 #
# --------------------------------------------------------------------------- #
def profile():
    return {
        "$comment": "DRAFT. The telecom service-assurance overlay. Extends the generic system overlay "
                    "system-disclosure, which supplies the citations, the join to product interfaces, usage and "
                    "the key provider. Adds the component-to-service dependency mapping the telecom CBOM document "
                    "asks for (3.2.4), and the operator operatorBoundary.",
        "profileId": "pkic.example.telecom-service-assurance",
        "profileTag": "telecom-service-assurance",
        "title": "Telecom Service Assurance Overlay (draft)",
        "version": "0.1-draft",
        "conformanceKeywords": "BCP 14 (MUST/SHOULD/MAY)",
        "extends": {"profileId": "pkic.example.system-disclosure", "version": "0.1",
                    "file": "../../docs/methodology/profile-system-disclosure.rules.json"},
        "objective": {
            "$comment": "C1. The consumer is the operator's service assurance team, or a customer of a critical "
                        "service such as a public safety authority. The decision is the one the telecom document "
                        "names: how a weakness or a change at one component affects the services built on it.",
            "consumer": "An operator's service assurance team, or a customer of a critical communications service "
                        "acting through the operator.",
            "decision": "For each interface the system uses: which services depend on it and whether it crosses "
                        "the operator operatorBoundary, so that a weakness or a migration at that interface can be traced "
                        "to the services, and the partners, it affects.",
            "decisionOptions": ["record the dependencies and take no further action",
                                "raise the priority of a migration that affects a critical service",
                                "agree a change with the roaming partner or interconnect provider first"]},
        "scope": {
            "$comment": "As the generic overlay: one system design, as the operator's architects deliver it.",
            "subjectTypes": ["system"], "orientation": "inventory",
            "relationshipTypes": ["interface"], "lifecycleStages": ["configured"]},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "boundaryVocabulary": ["intra-operator", "inter-operator"],
        "$commentBoundary": "'inter-operator': the connection leaves the operator's network, to a roaming partner, "
                            "an interconnect provider (IPX) or another network, the operatorBoundary 3GPP TS 33.210 draws "
                            "between security domains.",
        "productRules": [
            {"id": "P1", "description": "System names the services it delivers", "level": "MUST",
             "constraint": {"productAttribute": "services"}, "withholdable": False,
             "note": "The services, as the operator's service model names them. Each interface in use names the "
                     "ones it carries (I1). Commitments, availability targets and customers stay in the service "
                     "model: the record holds the names it joins on."}],
        "interfaceRules": [
            {"id": "I1", "attribute": "carriesService", "level": "MUST",
             "constraint": {"inSubjectList": "services", "literals": ["none"]}, "withholdable": True, "list": True,
             "requiredWhen": {"attribute": "designUse", "equals": "in-use"},
             "note": "The services that depend on this interface, by the names the system gives them (P1). A "
                     "list, because an interconnect usually carries several. 'none' for an interface no service "
                     "depends on directly, such as management. This is the component-to-service dependency "
                     "mapping. Withholdable, because a public record may not show which services depend on what."},
            {"id": "I2", "attribute": "operatorBoundary", "level": "MUST",
             "constraint": {"enumRef": "boundaryVocabulary"}, "withholdable": False,
             "requiredWhen": {"attribute": "designUse", "equals": "in-use"},
             "note": "Whether the connection stays in the operator's network or crosses to another. A change on "
                     "an inter-operator interface needs the other party to change too."},
            {"id": "I3", "attribute": "proxiedBy", "level": "MUST", "constraint": {"refersToLocal": {}},
             "withholdable": True,
             "requiredWhen": {"attribute": "operatorBoundary", "equals": "inter-operator"},
             "note": "The component that terminates the operatorBoundary, by its bom-ref: the SEPP for N32, a security "
                     "gateway for Za, or the interconnect provider where it relays the traffic."}],
        "exclusions": [
            {"item": "Service levels, availability targets and the customers of each service",
             "reason": "They belong in the operator's service model, which the record joins by service name."},
            {"item": "A criticality rating for each service",
             "reason": "A judgement the operator's policy makes from the service model, not a fact of the design."}],
        "changelog": [{"version": "0.1-draft", "date": "2026-11-17",
                       "summary": "First draft, built on a roaming interconnect.", "changes": []}],
        "artifacts": {"conformingExample": "examples/cbom-roaming-interconnect-system.cdx.json",
                      "nonConformingExample": "examples/cbom-roaming-interconnect-fail-service.cdx.json"},
    }


# --------------------------------------------------------------------------- #
# The SEPP product record (illustrative)                                      #
# --------------------------------------------------------------------------- #
def iface(ref, name, kind, pairs):
    return {"type": "service", "bom-ref": ref, "name": name,
            "properties": props([("interfaceType", kind)] + pairs + [("defaultState", "enabled")])}


TLS_GROUPS = ["X25519MLKEM768", "X25519", "ECDH-P256", "ECDH-P384"]


def sepp_interfaces():
    return [
        iface("n32c", "N32-c: control plane between SEPPs (TLS)", "interconnect", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:sepp"), ("endpointRole:server", "endpoint:peer-sepp"),
            ("keyExchange", "X25519"), ("encryption", "AES-256-GCM"), ("authentication", "ECDSA-P256-SHA256"),
            ("protocolVersionsSupported", ["1.2", "1.3"]), ("keyExchangeSupported", TLS_GROUPS),
            ("authenticationSupported", ["ECDSA-P256-SHA256", "ECDSA-P384-SHA384", "RSA-PSS-2048-SHA256"]),
            ("algorithmSelection", "Groups, signature schemes and cipher suites set per roaming partner"),
            ("integrationConstraints", "OpenSSL 3.5 offers X25519MLKEM768 by default. The SEPP sets its own "
                                       "group list and leaves the hybrid group out unless the operator enables "
                                       "it per roaming partner, because the 3GPP TLS profile for N32-c does not "
                                       "name it. Both SEPPs must support it."),
            ("keysStoredIn", "sto-keys")]),
        iface("n32f", "N32-f: forwarded messages, application-layer protection (PRINS)", "interconnect", [
            ("protocol", "PRINS"), ("protocolVersion", "17"),
            ("endpointRole:sender", "endpoint:sepp"), ("endpointRole:receiver", "endpoint:peer-sepp"),
            ("keyExchange", "none"), ("encryption", "AES-128-GCM"), ("authentication", "ECDSA-P256-SHA256"),
            ("algorithmSelection", "Cipher suites for JWE and JWS agreed over N32-c"),
            ("integrationConstraints", "The JWE keys are derived from the N32-c TLS session; an interconnect "
                                       "provider that modifies a message signs its change with JWS."),
            ("keysStoredIn", "n32c")]),
        iface("sbi", "Service-based interface to the operator's network functions (TLS, OAuth 2.0)", "service", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:nf-consumer"), ("endpointRole:server", "endpoint:sepp"),
            ("keyExchange", "X25519"), ("encryption", "AES-256-GCM"), ("authentication", "ECDSA-P256-SHA256"),
            ("protocolVersionsSupported", ["1.2", "1.3"]), ("keyExchangeSupported", TLS_GROUPS),
            ("integrationConstraints", "Access tokens are JWTs signed ES256 by the operator's NRF."),
            ("keysStoredIn", "sto-keys")]),
        iface("mgmt", "Management (NETCONF over SSH)", "management", [
            ("protocol", "SSH"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:oam"), ("endpointRole:server", "endpoint:sepp"),
            ("keyExchange", "X25519"), ("encryption", "AES-256-GCM"), ("authentication", "Ed25519"),
            ("keyExchangeSupported", ["mlkem768x25519-sha256", "sntrup761x25519-sha512", "X25519", "ECDH-P256"]),
            ("integrationConstraints", "The SEPP restricts SSH key exchange to X25519 and ECDH-P256 unless the "
                                       "operator enables the hybrid methods OpenSSH 9.9 provides."),
            ("keysStoredIn", "sto-keys")]),
        iface("sto-keys", "Private keys and trust anchors", "storage", [
            ("encryption", "AES-256-GCM"), ("keyWrapping", "AES-256-KW"),
            ("integrationConstraints", "The key-encryption key can be held in an external HSM over PKCS#11.")]),
    ]


LIBS = [("lib:openssl", "OpenSSL", "3.5.4", OPENSSL_PURL),
        ("lib:jose", "JOSE library (illustrative)", "2.0.0", JOSE_PURL),
        ("lib:openssh", "OpenSSH", "9.9p1", OPENSSH_PURL)]


def sepp_subject(extra):
    return {"type": "application", "bom-ref": "app:sepp", "name": "SEPP (illustrative)", "version": "5.1.0",
            "description": "A cloud-native SEPP at release 5.1.0, as its supplier would describe it. Five "
                           "interfaces. Values are illustrative.",
            "properties": extra, "identifiers": ident(SEPP_PURL),
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "Example Telco Vendor (illustrative)"}}]}


def libs():
    return [{"type": "library", "bom-ref": r, "name": n, "version": v, "identifiers": ident(p)} for r, n, v, p in LIBS]


def sepp_sbom():
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "DRAFT EXAMPLE SBOM for the illustrative SEPP 5.1.0. Lists only the three libraries the "
                        "CBOM names, so its composition is incomplete.",
            "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": "Example Telco Vendor (illustrative)"}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": sepp_subject([]), "components": libs()}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def sepp(sbom_hash):
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE CBOM, lifecycle stage 'implemented'. An illustrative Security Edge Protection "
                    "Proxy (SEPP), the network function at the N32 interface between roaming partners. Not a real "
                    "product.",
        "serialNumber": "urn:uuid:" + SERIAL["sepp"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                     "supplier": {"name": "Example Telco Vendor (illustrative)"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": sepp_subject(props([
            ("coverage", "all"), ("subjectType", "product"),
            ("absent:vulnerability-statements", "not-published")])),
            "components": libs() + sepp_interfaces()}],
        "dependencies": [{"ref": "app:sepp", "dependsOn": ["lib:openssl", "lib:jose", "lib:openssh"]},
                         {"ref": "lib:openssl", "provides": ["n32c", "sbi", "sto-keys"]},
                         {"ref": "lib:jose", "provides": ["n32f"]},
                         {"ref": "lib:openssh", "provides": ["mgmt"]}],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % SERIAL["sbom"],
             "comment": "Companion SBOM: examples/sepp-5.1.0-sbom.cdx.json.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://psirt.example.com/sepp/advisories",
             "comment": "The supplier's security advisories (illustrative).",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://psirt.example.com/contact",
             "comment": "The supplier's security contact (illustrative).",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])}]}


# --------------------------------------------------------------------------- #
# The system record                                                           #
# --------------------------------------------------------------------------- #
DROP = ["protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported", "algorithmSelection",
        "integrationConstraints", "defaultState"]
ALL = SERVICES
# usage, carriesService, operatorBoundary, proxiedBy, keysProvidedBy
DESIGN = {
    "n32c": ("in-use", ALL, "inter-operator", "sys:sepp", "sys:operator-pki"),
    "n32f": ("in-use", ALL, "inter-operator", "sys:ipx-provider", "product"),
    "sbi": ("in-use", ALL, "intra-operator", None, "sys:operator-pki"),
    "mgmt": ("in-use", "none", "intra-operator", None, "product"),
    "sto-keys": ("in-use", "none", "intra-operator", None, "sys:operator-hsm"),
}
SYSTEM_COMPONENTS = [
    ("sys:sepp", "SEPP, both sites: the product cited, deployed in a redundant pair"),
    ("sys:operator-pki", "Operator PKI: issues the N32 and SBI certificates"),
    ("sys:operator-hsm", "Operator HSM: holds the SEPP's key-encryption key"),
    ("sys:ipx-provider", "Interconnect provider (IPX): relays N32-f to roaming partners"),
]


def system(sepp_doc, sepp_bytes):
    serial = sepp_doc["serialNumber"].split(":")[-1]
    sepp_refs = {c["bom-ref"] for c in sepp_doc["inventories"][0]["components"]}
    ifaces = []
    for c in sepp_doc["inventories"][0]["components"]:
        if c.get("type") != "service":
            continue
        usage, svc, operatorBoundary, proxy, keys = DESIGN[c["bom-ref"]]
        i = copy.deepcopy(c)
        i["bom-ref"] = "sepp:" + c["bom-ref"]
        i["name"] = "SEPP: " + c["name"]
        i["properties"] = [p for p in i["properties"] if not any(p["name"].startswith(P + d) for d in DROP)]
        for p in i["properties"]:
            # A key store named by the product's own bom-ref is renamed to this record's copy.
            if p["name"] == P + "keysStoredIn" and p["value"] in sepp_refs:
                p["value"] = "sepp:" + p["value"]
        add = [("correspondsTo", "urn:cdx:%s/1#%s" % (serial, c["bom-ref"])), ("designUse", usage),
               ("carriesService", svc), ("operatorBoundary", operatorBoundary), ("keysProvidedBy", keys)]
        if proxy:
            add.append(("proxiedBy", proxy))
        i["properties"] += props(add)
        ifaces.append(i)
    others = [{"type": "device", "bom-ref": ref, "name": name,
               "properties": props([("correspondsTo", "no-product-document")])} for ref, name in SYSTEM_COMPONENTS]
    comps = ifaces + others
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE for telecom-service-assurance v0.1-draft. An operator's roaming interconnect as "
                    "its architects deliver it, stage 'configured'. Lists every interface of the SEPP, each joined "
                    "to the product interface it realises, with the services it carries, whether it crosses the "
                    "operator operatorBoundary and the component that provides its keys. Illustrative values.",
        "serialNumber": "urn:uuid:" + SERIAL["system"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "operations"}],
                     "supplier": {"name": "Example Operator (illustrative)"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": {
            "type": "platform", "bom-ref": "system:roaming-interconnect",
            "name": "Roaming interconnect, reference design (illustrative)",
            "properties": props([("subjectType", "system"), ("coverage", "partial"), ("services", SERVICES)]),
            "identifiers": [{"party": "party:document-author", "identities": [
                {"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."}, "value": SUBJECT_TAG}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "Example Operator (illustrative)"}}]},
            "components": comps}],
        "dependencies": [{"ref": "system:roaming-interconnect", "dependsOn": [k["bom-ref"] for k in comps]}],
        "externalReferences": [{"type": "bom", "url": "urn:cdx:%s/1" % serial,
                                "comment": "The SEPP's product record.",
                                "properties": props([("context", "cited-document")]),
                                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(sepp_bytes).hexdigest()}]}]}


def variant(rec, ref, drop, digit, comment):
    v = copy.deepcopy(rec)
    v["serialNumber"] = v["serialNumber"][:-1] + digit
    v["$comment"] = comment
    for c in v["inventories"][0]["components"]:
        if c["bom-ref"] == ref:
            c["properties"] = [p for p in c["properties"] if p["name"] != P + drop]
    return v


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "profile-telecom-service-assurance.rules.json"), "wb") as fh:
        fh.write(dump(profile()))
    sb = dump(sepp_sbom())
    with open(os.path.join(OUT, "sepp-5.1.0-sbom.cdx.json"), "wb") as fh:
        fh.write(sb)
    raw = dump(sepp(hashlib.sha256(sb).hexdigest()))
    with open(os.path.join(OUT, "cbom-sepp-product.cdx.json"), "wb") as fh:
        fh.write(raw)
    rec = system(json.loads(raw), raw)
    files = {
        "cbom-roaming-interconnect-system.cdx.json": rec,
        "cbom-roaming-interconnect-fail-service.cdx.json": variant(
            rec, "sepp:n32f", "carriesService", "1",
            "DRAFT NON-CONFORMING EXAMPLE for telecom-service-assurance. The conforming record with carriesService "
            "removed from N32-f, which is in use. Fails telecom-service-assurance#I1."),
        "cbom-roaming-interconnect-fail-proxy.cdx.json": variant(
            rec, "sepp:n32c", "proxiedBy", "2",
            "DRAFT NON-CONFORMING EXAMPLE for telecom-service-assurance. The conforming record with proxiedBy "
            "removed from N32-c, which crosses the operator operatorBoundary. Fails telecom-service-assurance#I3."),
    }
    for name, obj in files.items():
        with open(os.path.join(OUT, name), "wb") as fh:
            fh.write(dump(obj))
    print("written to", HERE)


if __name__ == "__main__":
    main()
