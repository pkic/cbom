#!/usr/bin/env python3
"""Draft OT example: lib60870 v2.4.1, an open-source IEC 60870-5-101/104 stack, as a product record.

The control-centre link of the reference substation. The working group writes the record from
public sources: the project README, CHANGELOG, Makefile and source at the v2.4.1 tag
(lib60870-C/src/hal/tls/mbedtls3/tls_mbedtls.c, lib60870-C/src/hal/inc/tls_config.h), built
with Mbed TLS 3.6. The library was not built or run: values that depend on the compiled
configuration are taken from the Mbed TLS 3.6 defaults and marked to confirm.

Writes docs/methodology/examples/cbom-lib60870-2.4.1-product.cdx.json and its companion SBOM,
docs/methodology/examples/context/lib60870-2.4.1-sbom.cdx.json.

Usage: python3 tools/build_lib60870_example.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "methodology", "examples")
CONTEXT = os.path.join(OUT, "context")
P = "pkic:profile:"
STAMP = "2026-11-17T09:00:00Z"
AUTHOR = {"name": "PKI Consortium CBOM Profiles Working Group (worked example)",
          "url": [{"name": "website", "url": "https://pkic.org"}]}
SERIAL = {"product": "60870a1e-0b6c-4f2e-9d1a-160870000001",
          "sbom": "60870a1e-0b6c-4f2e-9d1a-1608700000b0"}
SUBJECT_PURL = "pkg:github/mz-automation/lib60870@v2.4.1"
MBEDTLS_VERSION = "3.6.8"
MBEDTLS_PURL = "pkg:github/mbed-tls/mbedtls@mbedtls-3.6.8"
SRC = "https://github.com/mz-automation/lib60870/blob/v2.4.1/lib60870-C/"


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write(name, obj, where=None):
    data = dump(obj)
    with open(os.path.join(where or OUT, name), "wb") as fh:
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
    return {"type": "library", "bom-ref": "lib:lib60870", "name": "lib60870", "version": "2.4.1",
            "licenses": [{"license": {"id": "GPL-3.0-only"}}],
            "description": "Open-source IEC 60870-5-101 and IEC 60870-5-104 library (lib60870-C), with TLS "
                           "after IEC 62351-3, built with Mbed TLS 3.6. Described from its public source by the "
                           "working group, not by its maintainers.",
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


# Mbed TLS 3.6 default named groups for TLS 1.3 and ECDHE. lib60870 configures none of its own
# (tls_mbedtls.c), and its own mbedtls_config.h for 3.6 is not used by the build (it holds an
# #error line), so the Mbed TLS defaults apply. To be confirmed against the compiled configuration.
GROUPS = ["x25519", "ECDH-P-256", "ECDH-P-384", "x448", "ECDH-P-521", "ECDH-brainpoolP256r1",
          "ECDH-brainpoolP384r1", "ECDH-brainpoolP512r1", "FFDHE-ffdhe2048", "FFDHE-ffdhe3072", "FFDHE-ffdhe4096",
          "FFDHE-ffdhe6144", "FFDHE-ffdhe8192"]

NONE3 = [("keyExchange", "none"), ("encryption", "none"), ("authentication", "none"),
         ("implementingLibrary", SUBJECT_PURL), ("keysStoredIn", "none")]

SECURE_AUTH = ("integrationConstraints", "Secure authentication (IEC 60870-5-7:2013, the application-layer "
               "authentication of IEC 62351-5) is a commercial add-on. The open-source library holds only the "
               "integration code for it.")


def interfaces():
    return [
        iface("tls-104", "TLS for IEC 60870-5-104 (IEC 62351-3)", "service", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:peer"), ("endpointRole:server", "endpoint:embedding-application"),
            ("keyExchange", "peer-defined"), ("encryption", "peer-defined"), ("authentication", "deployment-defined"),
            ("protocolVersionsSupported", ["1.2", "1.3"]), ("keyExchangeSupported", ["RSA-PKCS1-1.5"] + GROUPS),
            ("algorithmSelection", "Cipher suites through TLSConfiguration_addCipherSuite and "
                                   "_clearCipherSuiteList; minimum and maximum version through "
                                   "TLSConfiguration_setMinTlsVersion and _setMaxTlsVersion. The library has no "
                                   "function for named groups or signature schemes."),
            ("integrationConstraints", "Default cipher suites include TLS_RSA_WITH_AES_128_CBC_SHA256, RSA key "
                                       "transport without forward secrecy, which IEC 62351-4:2018 makes mandatory."),
            ("integrationConstraints", "Default minimum TLS version 1.2, no maximum set."),
            ("integrationConstraints", "Default maximum certificate size 8192 bytes "
                                       "(TLSConfiguration_setMaxCertificateSize)."),
            ("integrationConstraints", "Default minimum key length 1024 bits (TLSConfiguration_setMinimumKeyLength)."),
            ("integrationConstraints", "TLS 1.2 renegotiation enabled, legacy renegotiation allowed; session "
                                       "resumption on, with a 6-hour interval."),
            ("integrationConstraints", "Integrated with Mbed TLS 2.28 and 3.6. The README names only 2.28, whose "
                                       "support ended at the end of 2024. The CMake build takes 2.28 when both are "
                                       "present; the Makefile takes 3.6."),
            ("keysStoredIn", "out-of-band")],
            refs=guidance(SRC + "src/hal/inc/tls_config.h",
                          "Where the application sets its certificate, key, CA certificates, CRLs, cipher suites "
                          "and TLS versions.")),
        iface("svc-104", "IEC 60870-5-104 without TLS", "service", [
            ("protocol", "IEC 60870-5-104"), ("protocolVersion", "2006"),
            ("endpointRole:client", "endpoint:peer"), ("endpointRole:server", "endpoint:embedding-application"),
            ] + NONE3 + [SECURE_AUTH]),
        iface("svc-101", "IEC 60870-5-101, serial", "service", [
            ("protocol", "IEC 60870-5-101"), ("protocolVersion", "2003"),
            ("endpointRole:client", "endpoint:peer"), ("endpointRole:server", "endpoint:embedding-application"),
            ] + NONE3 + [SECURE_AUTH]),
    ]


def product(sbom_hash):
    bom = {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "EXAMPLE CBOM, lifecycle stage 'implemented'. lib60870 v2.4.1 built with Mbed TLS 3.6, "
                    "described by the working group from the project's public source. Real values; not built, and "
                    "not reviewed by the maintainers.",
        "serialNumber": "urn:uuid:" + SERIAL["product"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                     "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
        "inventories": [{"bom-ref": "inventory:subject", "subject": subject(props([
            ("coverage", "all"), ("subjectType", "product"),
            ("absent:management-interface", "not-applicable-to-subject"),
            ("absent:vulnerability-statements", "not-published")])),
            "components": [{"type": "library", "bom-ref": "lib:mbedtls", "name": "Mbed TLS",
                            "version": MBEDTLS_VERSION, "identifiers": ident(MBEDTLS_PURL)}] + interfaces()}],
        "dependencies": [{"ref": "lib:lib60870", "dependsOn": ["lib:mbedtls"]},
                         {"ref": "lib:mbedtls", "provides": ["tls-104"]}],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % SERIAL["sbom"],
             "comment": "Companion SBOM: examples/context/lib60870-2.4.1-sbom.cdx.json.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://github.com/mz-automation/lib60870/security/advisories",
             "comment": "GitHub security advisories for lib60870.",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://github.com/mz-automation/lib60870/security/policy",
             "comment": "The project's security policy.",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])}]}
    # svc-104 and svc-101 are implemented by the subject's own code, so they name the subject's
    # purl directly: the subject is not a component and cannot 'provide'.
    return bom


def sbom():
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "EXAMPLE SBOM for lib60870 v2.4.1 built with Mbed TLS 3.6. Lists only the two "
                        "libraries the CBOM names, so its composition is incomplete.",
            "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subject([]), "components": [
                {"type": "library", "bom-ref": "lib:mbedtls", "name": "Mbed TLS", "version": MBEDTLS_VERSION,
                 "identifiers": ident(MBEDTLS_PURL)}]}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def main():
    os.makedirs(OUT, exist_ok=True)
    h = write("lib60870-2.4.1-sbom.cdx.json", sbom(), CONTEXT)
    write("cbom-lib60870-2.4.1-product.cdx.json", product(h))
    print("written to", OUT)


if __name__ == "__main__":
    main()
