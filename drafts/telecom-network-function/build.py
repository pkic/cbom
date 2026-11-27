#!/usr/bin/env python3
"""Build the telecom network function profiles and their worked examples.

Writes, in this folder:
  profile-telecom-network-function.rules.json        network function product profile, v0.1-draft
  examples/cbom-open5gs-sepp-2.8.0-product.cdx.json  the Open5GS SEPP at v2.8.0, stage 'implemented'
  examples/context/open5gs-sepp-2.8.0-sbom.cdx.json  its companion SBOM
  examples/cbom-open5gs-sepp-fail-referencepoint.cdx.json   N32-c without its reference point
  examples/cbom-open5gs-sepp-deployment-configured.cdx.json an operator's deployment behind a service mesh
  examples/cbom-open5gs-sepp-deployment-fail-termination.cdx.json  the SBI without the component that terminates TLS

The SEPP record is written by the working group from the public source at the v2.8.0 tag
(lib/sbi/nghttp2-server.c, lib/sbi/client.c, lib/sbi/context.c, src/sepp/context.c,
src/sepp/n32c-build.c, configs/open5gs/sepp1.yaml.in). It is not written by the Open5GS
maintainers. The library versions are those of an Ubuntu 24.04 build and are marked to confirm.
The deployment record is illustrative.

Draft only. Nothing in docs/methodology/ is changed. The deployment records are evaluated
against Deployment Disclosure v0.3, which requires terminatedBy (interface-disclosure#I14);
the draft deployment profile that first carried the rule was removed on 19 November 2026.

Usage: python3 drafts/telecom-network-function/build.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "examples")
P = "pkic:profile:"
STAMP = "2026-11-18T09:00:00Z"
SERIAL = {"sepp": "5e990002-0000-4000-8000-000000000001", "sbom": "5e990002-0000-4000-8000-0000000000b0",
          "fail": "5e990002-0000-4000-8000-000000000002", "dep": "5e990002-0000-4000-8000-000000000010",
          "depfail": "5e990002-0000-4000-8000-000000000011"}
SEPP_PURL = "pkg:github/open5gs/open5gs@v2.8.0"
OPENSSL_PURL = "pkg:deb/ubuntu/openssl@3.0.13-0ubuntu3?distro=ubuntu-24.04"
NGHTTP2_PURL = "pkg:deb/ubuntu/nghttp2@1.59.0-1build4?distro=ubuntu-24.04"
CURL_PURL = "pkg:deb/ubuntu/curl@8.5.0-2ubuntu10?distro=ubuntu-24.04"
METH = "../../docs/methodology/"
TO_CONFIRM = " Library version from an Ubuntu 24.04 build; to confirm."

REFERENCE_POINTS = ["n32-c", "n32-f", "sbi", "n2", "n3", "n4", "n9", "nds-ip", "o-ran-m-plane",
                    "o-ran-fronthaul", "e2", "a1", "o1", "o2", "ota", "rsp", "not-a-reference-point"]


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write(rel, obj):
    data = dump(obj)
    with open(os.path.join(HERE, rel), "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def props(pairs):
    out = []
    for k, v in pairs:
        for one in (v if isinstance(v, list) else [v]):
            out.append({"name": P + k, "value": one})
    return out


def ident(purl):
    return [{"party": "party:document-author", "identities": [{"scheme": "purl", "value": purl}]}]


# --------------------------------------------------------------------------- #
# Profiles                                                                    #
# --------------------------------------------------------------------------- #
def nf_profile():
    return {
        "$comment": "DRAFT. A product profile for a telecom network function release. It extends the Interface "
                    "Disclosure Baseline with the reference point each interface implements and the specification "
                    "that profiles its security, so that an operator can compare vendors reference point by "
                    "reference point. A planning depth on the change core can follow.",
        "profileId": "pkic.example.telecom-network-function",
        "profileTag": "telecom-network-function",
        "title": "Telecom Network Function (Example, draft)",
        "version": "0.1-draft",
        "objective": {
            "consumer": "An operator's procurement or security team comparing network functions from several vendors",
            "decision": "Whether a network function release implements each reference point as its specification profiles it",
            "decisionOptions": ["accept the release", "accept with conditions", "reject the release"]},
        "scope": {"subjectTypes": ["product"], "orientation": "inventory", "relationshipTypes": ["interface"],
                  "lifecycleStages": ["implemented"]},
        "extends": {"profileId": "pkic.example.interface-disclosure", "version": "0.10",
                    "file": METH + "profile-interface-disclosure.rules.json"},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "referencePointVocabulary": REFERENCE_POINTS,
        "productRules": [],
        "interfaceRules": [
            {"id": "I1", "attribute": "referencePoint", "level": "MUST", "constraint": {"enumRef": "referencePointVocabulary"},
             "withholdable": False,
             "note": "The 3GPP, O-RAN or GSMA reference point the interface implements, or 'not-a-reference-point' "
                     "for an interface no specification names, such as a key store."},
            {"id": "I2", "attribute": "governingSpecification", "level": "MUST", "constraint": {"present": True},
             "withholdable": False,
             "requiredWhen": {"attribute": "referencePoint", "notEquals": "not-a-reference-point"},
             "note": "The specification and clause that profile the interface's security, such as 'TS 33.501 13.1'."}],
        "referenceRules": [],
        "exclusions": [
            {"item": "Whether the implementation meets the specification",
             "reason": "A judgement for SCAS testing or a policy. The record states the values; the specification states what is allowed."},
            {"item": "Capability, blocker and roadmap per purpose",
             "reason": "Change planning. A depth on the change core can add them."}],
        "artifacts": {"conformingExample": "examples/cbom-open5gs-sepp-2.8.0-product.cdx.json",
                      "nonConformingExample": "examples/cbom-open5gs-sepp-fail-referencepoint.cdx.json"},
        "changelog": [{"version": "0.1-draft", "date": "2026-11-18",
                       "summary": "First draft, built on the Open5GS SEPP.", "changes": []}]}


def dep_profile():
    return {
        "$comment": "DRAFT. A deployment profile for a network function the operator runs on its own platform. It "
                    "extends Deployment Disclosure with one rule: each interface that realises a product interface "
                    "names what terminates its cryptography. Where a service mesh terminates TLS for the workload, "
                    "the record names the mesh's interface, which is a component of the same record. The rule is "
                    "not specific to telecom, and could move to Deployment Disclosure once a second sector uses it.",
        "profileId": "pkic.example.telecom-nf-deployment",
        "profileTag": "telecom-nf-deployment",
        "title": "Telecom Network Function Deployment (Example, draft)",
        "version": "0.1-draft",
        "objective": {
            "consumer": "An operator's security operations team",
            "decision": "Which weakness affects each deployed interface, and which component has to change to remove it",
            "decisionOptions": ["change the workload", "change the platform", "accept"]},
        "scope": {"subjectTypes": ["deployment"], "orientation": "inventory", "relationshipTypes": ["interface"],
                  "lifecycleStages": ["configured", "observed"]},
        "extends": {"profileId": "pkic.example.deployment-disclosure", "version": "0.2",
                    "file": METH + "profile-deployment-disclosure.rules.json"},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "productRules": [],
        "interfaceRules": [
            {"id": "I1", "attribute": "terminatedBy", "level": "MUST",
             "constraint": {"refersToLocal": {"literals": ["workload", "platform"]}}, "withholdable": False,
             "requiredWhen": {"attribute": "interfaceType", "notEquals": "storage"},
             "note": "'workload' where the network function terminates the cryptography itself; the bom-ref of "
                     "the platform interface that terminates it for the workload, such as a service mesh sidecar "
                     "or an ingress; or 'platform' on that platform interface itself."}],
        "referenceRules": [],
        "exclusions": [
            {"item": "The platform's own product records",
             "reason": "The mesh or ingress is described by its own records. This profile names it, and the record "
                       "states its interface only as far as the deployment configures it."}],
        "artifacts": {"conformingExample": "examples/cbom-open5gs-sepp-deployment-configured.cdx.json",
                      "nonConformingExample": "examples/cbom-open5gs-sepp-deployment-fail-termination.cdx.json"},
        "changelog": [{"version": "0.1-draft", "date": "2026-11-18",
                       "summary": "First draft, built on the Open5GS SEPP behind a service mesh.", "changes": []}]}


# --------------------------------------------------------------------------- #
# The Open5GS SEPP product record                                            #
# --------------------------------------------------------------------------- #
GUIDANCE = [{"type": "documentation", "url": "https://open5gs.org/open5gs/docs/",
             "comment": "Where the operator sets the certificate and key: the 'tls' section of sepp.yaml.",
             "properties": props([("context", "configuration-guidance"), ("accessProtocol", "web-page")])}]


def iface(ref, name, kind, pairs, state="enabled"):
    c = {"type": "service", "bom-ref": ref, "name": name,
         "properties": props([("interfaceType", kind)] + pairs + [("defaultState", state)])}
    if any(k == "authentication" and v == "deployment-defined" for k, v in pairs):
        c["externalReferences"] = copy.deepcopy(GUIDANCE)
    return c


SERVER_TLS = ("The server context (lib/sbi/nghttp2-server.c) allows TLS 1.0 to 1.3 and sets the group list to P-256 "
              "only, so the server negotiates ECDHE on P-256 whatever the client offers. OpenSSL 3 refuses TLS 1.0 "
              "and 1.1 at its default security level. TLS 1.2 suites are ECDHE-ECDSA and ECDHE-RSA with AES-GCM or "
              "ChaCha20-Poly1305, and DHE-RSA with AES-GCM; TLS 1.3 suites are the OpenSSL defaults, with server "
              "preference. The client side (lib/sbi/client.c) uses libcurl with OpenSSL and its default groups. "
              "There is no setting for the group list.")


def sepp_interfaces():
    tls = [("protocol", "TLS"), ("protocolVersion", "1.3"),
           ("keyExchange", "ECDH-P256"), ("encryption", "AES-256-GCM"), ("authentication", "deployment-defined"),
           ("protocolVersionsSupported", ["1.2", "1.3"]),
           ("keyExchangeSupported", ["ECDH-P256"]),
           ("authenticationSupported", ["ECDSA", "RSA"])]
    return [
        iface("n32c", "N32-c: N32 handshake between SEPPs (HTTPS)", "interconnect", tls + [
            ("endpointRole:client", "endpoint:sepp"), ("endpointRole:server", "endpoint:peer-sepp"),
            ("algorithmSelection", "Certificate and key from the 'tls' section of sepp.yaml; client "
                                   "certificate verification is off unless 'verify_client' is set"),
            ("integrationConstraints", SERVER_TLS + " The SEPP advertises TLS as its only N32-f security capability."
                                       + TO_CONFIRM),
            ("referencePoint", "n32-c"), ("governingSpecification", "TS 33.501 13.1 and 13.5; TS 29.573"),
            ("keysStoredIn", "sto-keys")]),
        iface("n32f", "N32-f: forwarded messages between SEPPs (HTTPS)", "interconnect", tls + [
            ("endpointRole:client", "endpoint:sepp"), ("endpointRole:server", "endpoint:peer-sepp"),
            ("algorithmSelection", "A separate listener and certificate may be set in the 'n32f' section"),
            ("integrationConstraints", "PRINS is not implemented: N32-f is protected by TLS only. " + SERVER_TLS
                                       + TO_CONFIRM),
            ("referencePoint", "n32-f"), ("governingSpecification", "TS 33.501 13.1 and 13.5"),
            ("keysStoredIn", "sto-keys")]),
        iface("sbi", "Service-based interface to the operator's network functions", "service", tls + [
            ("endpointRole:client", "endpoint:nf-consumer"), ("endpointRole:server", "endpoint:sepp"),
            ("algorithmSelection", "The scheme is set per server in the 'sbi' section: 'http' or 'https'"),
            ("integrationConstraints", "The shipped configuration uses HTTP without TLS on the SBI. With 'https', "
                                       "the same TLS context as N32 applies. " + SERVER_TLS + TO_CONFIRM),
            ("referencePoint", "sbi"), ("governingSpecification", "TS 33.501 13.1"),
            ("keysStoredIn", "sto-keys")], state="disabled"),
        iface("sto-keys", "Private keys, certificates and CA certificates (PEM files)", "storage", [
            ("encryption", "none"), ("keyWrapping", "none"),
            ("integrationConstraints", "Read from the file paths in sepp.yaml at start-up. Protection of the "
                                       "files is left to the platform."),
            ("referencePoint", "not-a-reference-point")]),
    ]


LIBS = [("lib:openssl", "OpenSSL", "3.0.13", OPENSSL_PURL),
        ("lib:nghttp2", "nghttp2", "1.59.0", NGHTTP2_PURL),
        ("lib:curl", "libcurl", "8.5.0", CURL_PURL)]


def subject(extra):
    return {"type": "application", "bom-ref": "app:open5gs-sepp", "name": "Open5GS SEPP", "version": "2.8.0",
            "description": "The SEPP of Open5GS v2.8.0 (open5gs-seppd). Record written by the PKIC CBOM Profiles "
                           "working group from the public source, not by the Open5GS maintainers.",
            "properties": extra, "identifiers": ident(SEPP_PURL),
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "PKIC CBOM Profiles Working Group"}}]}


def libs():
    return [{"type": "library", "bom-ref": r, "name": n, "version": v, "identifiers": ident(p)} for r, n, v, p in LIBS]


def sbom():
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "DRAFT EXAMPLE SBOM for the Open5GS SEPP v2.8.0. Lists only the libraries the CBOM names, so "
                        "its composition is incomplete. Versions from an Ubuntu 24.04 build; to confirm.",
            "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": "Open5GS"}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subject([]), "components": libs()}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def sepp(sbom_hash, serial=SERIAL["sepp"]):
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE CBOM, lifecycle stage 'implemented'. The Open5GS SEPP at v2.8.0, written from "
                    "its public source by the PKIC CBOM Profiles working group. Library versions to confirm.",
        "serialNumber": "urn:uuid:" + serial, "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}], "supplier": {"name": "Open5GS"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": subject(props([
            ("coverage", "all"), ("subjectType", "product"),
            ("absent:management-interface", "configured-out-of-band"),
            ("absent:vulnerability-statements", "not-published")])),
            "components": libs() + sepp_interfaces()}],
        "dependencies": [{"ref": "app:open5gs-sepp", "dependsOn": ["lib:openssl", "lib:nghttp2", "lib:curl"]},
                         {"ref": "lib:openssl", "provides": ["n32c", "n32f", "sbi", "sto-keys"]}],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % SERIAL["sbom"],
             "comment": "Companion SBOM: examples/context/open5gs-sepp-2.8.0-sbom.cdx.json.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://github.com/open5gs/open5gs/security/advisories",
             "comment": "The project's published security advisories.",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "configuration", "url": "https://open5gs.org/open5gs/docs/",
             "comment": "The project's documentation, including the TLS settings in sepp.yaml.",
             "properties": props([("context", "configuration-guidance")])},
            {"type": "vcs", "url": "https://github.com/open5gs/open5gs/tree/v2.8.0",
             "comment": "The source the record was written from."}]}


# --------------------------------------------------------------------------- #
# The deployment record (illustrative)                                       #
# --------------------------------------------------------------------------- #
SEPP_DOC = "urn:cdx:%s/1" % SERIAL["sepp"]


def deployment(product_hash, drop_termination=False, serial=SERIAL["dep"]):
    def d_iface(ref, name, kind, pairs, corresponds, terminated):
        p = [("lifecycleStage", "configured"), ("correspondsTo", corresponds)] + pairs
        if terminated is not None:
            p.append(("terminatedBy", terminated))
        return {"type": "service", "bom-ref": ref, "name": name, "properties": props([("interfaceType", kind)] + p)}

    n32 = [("protocol", "TLS"), ("protocolVersion", "1.3"), ("keyExchange", "ECDH-P256"),
           ("encryption", "AES-256-GCM"), ("authentication", "ECDSA-P256-SHA256")]
    comps = [
        d_iface("dep:n32c", "N32-c to roaming partners", "interconnect", n32 + [
            ("endpointRole:client", "endpoint:sepp"), ("endpointRole:server", "endpoint:peer-sepp"),
            ("keysStoredIn", "dep:sto-keys")], SEPP_DOC + "#n32c", "workload"),
        d_iface("dep:n32f", "N32-f to roaming partners", "interconnect", n32 + [
            ("endpointRole:client", "endpoint:sepp"), ("endpointRole:server", "endpoint:peer-sepp"),
            ("keysStoredIn", "dep:sto-keys")], SEPP_DOC + "#n32f", "workload"),
        d_iface("dep:sbi", "SBI inside the pod: plain HTTP to the sidecar", "service", [
            ("protocol", "HTTP"), ("protocolVersion", "2"), ("keyExchange", "none"), ("encryption", "none"),
            ("authentication", "none"),
            ("endpointRole:client", "endpoint:mesh-sidecar"), ("endpointRole:server", "endpoint:sepp"),
            ("integrationConstraints", "The SEPP runs with scheme 'http' on the SBI. The sidecar terminates mutual "
                                       "TLS and forwards over the pod's loopback interface.")],
            SEPP_DOC + "#sbi", None if drop_termination else "mesh:sbi-mtls"),
        d_iface("mesh:sbi-mtls", "Service mesh sidecar: mutual TLS on the SBI", "service", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"), ("keyExchange", "X25519"),
            ("encryption", "AES-128-GCM"), ("authentication", "RSA-2048-PKCS1-SHA256"),
            ("endpointRole:client", "endpoint:nf-consumer-sidecar"), ("endpointRole:server", "endpoint:mesh-sidecar"),
            ("integrationConstraints", "Workload certificates issued by the mesh's own CA with its default RSA-2048 "
                                       "keys, rotated daily. The operator's SBA certificate profile (TS 33.310) is "
                                       "not applied to them. Values illustrative.")],
            "no-product-document", "platform"),
        d_iface("dep:sto-keys", "Kubernetes secret holding the N32 key and certificates", "storage", [
            ("encryption", "AES-256-GCM"), ("keyWrapping", "none"),
            ("integrationConstraints", "Mounted into the pod as files. Encrypted at rest by the cluster's secret "
                                       "encryption.")], SEPP_DOC + "#sto-keys", None),
    ]
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE CBOM, lifecycle stage 'configured'. An illustrative operator's deployment of the "
                    "Open5GS SEPP v2.8.0 in a Kubernetes cluster with a service mesh. N32 is terminated by the SEPP; "
                    "the SBI is terminated by the mesh sidecar." +
                    (" NON-CONFORMING: the SBI does not name what terminates it." if drop_termination else ""),
        "serialNumber": "urn:uuid:" + serial, "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "operations"}],
                     "supplier": {"name": "Example Mobile Operator (illustrative)"}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": {
            "type": "application", "bom-ref": "deployment:sepp-roaming", "name": "SEPP for roaming, production cluster",
            "properties": props([("subjectType", "deployment"), ("coverage", "all"),
                                 ("absent:management-interface", "configured-out-of-band")]),
            "identifiers": [{"party": "party:document-author", "identities": [
                {"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."},
                 "value": "tag:operator.example,2026:deployment/sepp-roaming"}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "Example Mobile Operator (illustrative)"}}]},
            "components": libs() + [{"type": "library", "bom-ref": "lib:envoy", "name": "Envoy (the mesh sidecar)",
                                     "description": "Version as shipped with the operator's mesh release. Illustrative.",
                                     "identifiers": ident("pkg:github/envoyproxy/envoy")}] + comps}],
        "dependencies": [{"ref": "lib:openssl", "provides": ["dep:n32c", "dep:n32f", "dep:sto-keys"]},
                         {"ref": "lib:envoy", "provides": ["mesh:sbi-mtls"]}],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": SEPP_DOC, "comment": "The product CBOM of the SEPP this deployment runs.",
             "properties": props([("context", "cited-document")]),
             "hashes": [{"alg": "SHA-256", "content": product_hash}]},
            {"type": "vcs", "url": "https://git.operator.example/core/sepp-deploy/-/commit/7d1e0b2",
             "comment": "Revision of the deployment repository this record was read from.",
             "properties": props([("context", "configuration-source")])}]}


def main():
    write("profile-telecom-network-function.rules.json", nf_profile())
    h_sbom = write("examples/context/open5gs-sepp-2.8.0-sbom.cdx.json", sbom())
    h_sepp = write("examples/cbom-open5gs-sepp-2.8.0-product.cdx.json", sepp(h_sbom))
    bad = sepp(h_sbom, SERIAL["fail"])
    bad["$comment"] += " NON-CONFORMING: N32-c does not state its reference point."
    for c in bad["inventories"][0]["components"]:
        if c["bom-ref"] == "n32c":
            c["properties"] = [p for p in c["properties"] if p["name"] not in (P + "referencePoint", P + "governingSpecification")]
    write("examples/cbom-open5gs-sepp-fail-referencepoint.cdx.json", bad)
    write("examples/cbom-open5gs-sepp-deployment-configured.cdx.json", deployment(h_sepp))
    write("examples/cbom-open5gs-sepp-deployment-fail-termination.cdx.json",
          deployment(h_sepp, drop_termination=True, serial=SERIAL["depfail"]))
    print("written")


if __name__ == "__main__":
    main()
