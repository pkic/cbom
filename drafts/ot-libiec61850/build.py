#!/usr/bin/env python3
"""Draft OT example: libIEC61850 v1.6.2, an open-source IEC 61850 stack, as a product record.

The first OT example with real values. The working group writes the record from public
sources: the project README, CHANGELOG and source at the v1.6 branch (hal/tls/mbedtls3/
tls_mbedtls.c, hal/inc/tls_config.h, src/r_session/r_session.c), built with Mbed TLS 3.6.
Values the source does not fix are stated as literals (peer-defined, deployment-defined)
with a pointer to where the application decides them.

Usage: python3 drafts/ot-libiec61850/build.py
Then:  cd docs/methodology && python3 validate_cbom.py ../../drafts/ot-libiec61850/examples/<file> <profile>
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "examples")
P = "pkic:profile:"
STAMP = "2026-11-17T09:00:00Z"
AUTHOR = {"name": "PKI Consortium CBOM Profiles Working Group (worked example)",
          "url": [{"name": "website", "url": "https://pkic.org"}]}
SERIAL = {"product": "61850a1e-0b6c-4f2e-9d1a-161850000001",
          "sbom": "61850a1e-0b6c-4f2e-9d1a-1618500000b0"}
SUBJECT_PURL = "pkg:github/mz-automation/libiec61850@v1.6.2"
MBEDTLS_PURL = "pkg:github/mbed-tls/mbedtls@v3.6.0"
SRC = "https://github.com/mz-automation/libiec61850/blob/v1.6/"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write(name, obj):
    data = dump(obj)
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def props(pairs):
    out = []
    for k, v in pairs:
        for one in (v if isinstance(v, list) else [v]):
            out.append({"name": P + k, "value": one})
    return out


def ident(purl):
    return [{"party": "party:document-author", "identities": [{"scheme": "purl", "value": purl}]}]


def subject(extra):
    return {"type": "library", "bom-ref": "lib:libiec61850", "name": "libIEC61850", "version": "1.6.2",
            "licenses": [{"license": {"id": "GPL-3.0-only"}}],
            "description": "Open-source IEC 61850 client and server library (MMS, GOOSE, SV, R-GOOSE/R-SV), "
                           "built with Mbed TLS 3.6. Described from its public source by the working group, "
                           "not by its maintainers.",
            "properties": extra, "identifiers": ident(SUBJECT_PURL),
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}], "organization": AUTHOR},
                        {"bom-ref": "party:maintainer", "roles": [{"role": "supplier"}],
                         "organization": {"name": "MZ Automation GmbH"}}]}


def guidance(url, comment):
    return [{"type": "documentation", "url": url, "comment": comment,
             "properties": props([("context", "configuration-guidance"), ("accessProtocol", "web-page")])}]


def iface(ref, name, kind, pairs, state="enabled", refs=None):
    c = {"type": "service", "bom-ref": ref, "name": name,
         "properties": props([("interfaceType", kind)] + pairs + [("defaultState", state)])}
    if refs:
        c["externalReferences"] = refs
    return c


# Mbed TLS 3.6 default named groups. libIEC61850 configures none of its own
# (tls_mbedtls.c), so these apply. To be confirmed against the compiled configuration.
GROUPS = ["X25519", "ECDH-P256", "ECDH-P384", "X448", "ECDH-P521", "ECDH-brainpoolP256r1",
          "ECDH-brainpoolP384r1", "ECDH-brainpoolP512r1", "FFDHE-2048", "FFDHE-3072", "FFDHE-4096",
          "FFDHE-6144", "FFDHE-8192"]

NONE3 = [("keyExchange", "none"), ("encryption", "none"), ("authentication", "none"),
         ("implementationPurl", SUBJECT_PURL), ("keyStoreRef", "none")]


def interfaces():
    return [
        iface("tls-mms", "TLS for MMS (IEC 62351-3/4)", "service", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:embedding-application"), ("endpointRole:server", "endpoint:peer"),
            ("keyExchange", "peer-defined"), ("encryption", "peer-defined"), ("authentication", "deployment-defined"),
            ("protocolVersionsSupported", ["1.2", "1.3"]), ("keyExchangeSupported", GROUPS),
            ("negotiationControl", "Cipher suites through TLSConfiguration_addCipherSuite; minimum and maximum version "
                                   "through TLSConfiguration_setMinTlsVersion and _setMaxTlsVersion. The library has "
                                   "no function for named groups or signature schemes."),
            ("integrationConstraints", "Default maximum certificate size 8192 bytes "
                                       "(TLSConfiguration_setMaxCertificateSize)."),
            ("integrationConstraints", "Default minimum key length 1024 bits (TLSConfiguration_setMinimumKeyLength)."),
            ("integrationConstraints", "TLS 1.2 renegotiation enabled, legacy renegotiation allowed; TLS 1.3 needs "
                                       "Mbed TLS 3.6, and only Mbed TLS 2.28 and 3.6 are integrated."),
            ("keyStoreRef", "out-of-band")],
            refs=guidance(SRC + "hal/inc/tls_config.h",
                          "Where the application sets its certificate, key, CA certificates, cipher suites and "
                          "TLS versions.")),
        iface("svc-mms", "MMS without TLS (IEC 61850-8-1)", "service", [
            ("protocol", "MMS"), ("protocolVersion", "2003"),
            ("endpointRole:client", "endpoint:embedding-application"), ("endpointRole:server", "endpoint:peer"),
            ] + NONE3 + [
            ("integrationConstraints", "Optional ACSE password authentication, sent in clear unless carried in tls-mms. "
                                       "IEC 62351-8 roles need an application callback: the library provides the "
                                       "access-control hook, not the token check.")]),
        iface("svc-goose", "GOOSE (IEC 61850-8-1, layer 2)", "service", [
            ("protocol", "GOOSE"), ("protocolVersion", "2.1"),
            ("endpointRole:publisher", "endpoint:embedding-application"), ("endpointRole:subscriber", "endpoint:peer"),
            ] + NONE3 + [
            ("integrationConstraints", "No IEC 62351-6 protection for layer-2 GOOSE in the library.")]),
        iface("svc-sv", "Sampled values (IEC 61850-9-2, layer 2)", "service", [
            ("protocol", "SV"), ("protocolVersion", "2.1"),
            ("endpointRole:publisher", "endpoint:embedding-application"), ("endpointRole:subscriber", "endpoint:peer"),
            ] + NONE3 + [
            ("integrationConstraints", "No IEC 62351-6 protection for layer-2 sampled values in the library.")]),
        iface("svc-rsession", "R-GOOSE and R-SV session protocol (IEC 61850-8-1 Amd 1, beta)", "service", [
            ("protocol", "R-GOOSE"), ("protocolVersion", "2"),
            ("endpointRole:publisher", "endpoint:embedding-application"), ("endpointRole:subscriber", "endpoint:peer"),
            ("keyExchange", "none"), ("encryption", "deployment-defined"), ("authentication", "deployment-defined"),
            ("authenticationSupported", ["HMAC-SHA256-128", "HMAC-SHA256-256"]),
            ("integrationConstraints", "Beta, off by default (CONFIG_IEC61850_R_GOOSE). Keys are provisioned by the "
                                       "application through RSession_addKey; the library has no group key "
                                       "distribution (IEC 62351-9). Encryption only in session protocol version 2."),
            ("keyStoreRef", "out-of-band")], state="disabled",
            refs=guidance("https://github.com/mz-automation/libiec61850/tree/v1.6/src/r_session",
                          "Where the application adds keys and chooses the signature and encryption algorithms.")),
    ]


def product(sbom_hash):
    bom = {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "DRAFT EXAMPLE CBOM, lifecycle stage 'implemented'. libIEC61850 v1.6.2 built with Mbed TLS 3.6, "
                    "described by the working group from the project's public source. Real values; not reviewed "
                    "by the maintainers.",
        "serialNumber": "urn:uuid:" + SERIAL["product"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                     "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": subject(props([
            ("coverage", "all"), ("subjectType", "product"),
            ("managementInterfaceAbsence", "not-applicable-to-subject"),
            ("contextAbsent:vulnerability-statements", "not-published")])),
            "components": [{"type": "library", "bom-ref": "lib:mbedtls", "name": "Mbed TLS", "version": "3.6.0",
                            "identifiers": ident(MBEDTLS_PURL)}] + interfaces()}],
        "dependencies": [{"ref": "lib:libiec61850", "dependsOn": ["lib:mbedtls"]},
                         {"ref": "lib:mbedtls", "provides": ["tls-mms", "svc-rsession"]},
                         ],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % SERIAL["sbom"],
             "comment": "Companion SBOM: examples/libiec61850-1.6.2-sbom.cdx.json.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://github.com/mz-automation/libiec61850/security/advisories",
             "comment": "GitHub security advisories for libIEC61850.",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://github.com/mz-automation/libiec61850/security/policy",
             "comment": "The project's security policy.",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])}]}
    # svc-mms, svc-goose and svc-sv are implemented by the subject's own code, so they name
    # the subject's purl directly: the subject is not a component and cannot 'provide'.
    return bom


def sbom():
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "DRAFT EXAMPLE SBOM for libIEC61850 v1.6.2 built with Mbed TLS 3.6. Lists only the two "
                        "libraries the CBOM names, so its composition is incomplete.",
            "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subject([]), "components": [
                {"type": "library", "bom-ref": "lib:mbedtls", "name": "Mbed TLS", "version": "3.6.0",
                 "identifiers": ident(MBEDTLS_PURL)}]}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def main():
    os.makedirs(OUT, exist_ok=True)
    h = write("libiec61850-1.6.2-sbom.cdx.json", sbom())
    write("cbom-libiec61850-1.6.2-product.cdx.json", product(h))
    print("written to", OUT)


if __name__ == "__main__":
    main()
