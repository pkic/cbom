#!/usr/bin/env python3
"""Build the example for the draft HSM profiles: an illustrative payment HSM.

Writes, in examples/:
  cbom-example-payment-hsm-product.cdx.json       conforms to hsm-key-hierarchy (and so to hsm-product)
  cbom-example-payment-hsm-product-fail-I1.cdx.json  the management interface omits its key block formats

The HSM, its vendor and every value are illustrative. They are chosen to be
realistic for a payment HSM, not taken from any real product.

Usage: python3 drafts/hsm-product/build.py
"""
import copy, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "examples")
PURPOSES = ["key-establishment", "encryption", "entity-authentication", "data-integrity",
            "non-repudiation", "key-protection", "key-derivation"]


def props(*pairs):
    out = []
    for name, value in pairs:
        for v in (value if isinstance(value, list) else [value]):
            out.append({"name": "pkic:profile:" + name, "value": v})
    return out


def capability(status_by_purpose):
    """G1: one entry per cryptographic purpose."""
    pairs = []
    for p in PURPOSES:
        status, blocker = status_by_purpose.get(p, ("available", None))
        pairs.append(("capabilityByPurpose:%s:capabilityStatus" % p, status))
        if status == "available":
            pairs.append(("capabilityByPurpose:%s:validatedModeAvailability" % p, "in-validated-mode"))
        else:
            pairs.append(("capabilityByPurpose:%s:blockedBy" % p, blocker))
    return pairs


# Facts shared by every interface: one firmware, one validated module.
COMMON = [
    ("enablementMethod", "software-update"),
    ("availableFromVersion", "5.0"),
    ("executionEnvironment", "hsm"),
    ("transitionMode", "side-by-side"),
    ("moduleValidationScheme", "fips-140-3"),
    ("moduleValidationRef", "illustrative: FIPS 140-3 certificate #0000"),
    ("certificationImpact", "recertification"),
    ("impactedCertification", "FIPS 140-3 and PCI PTS HSM"),
    ("trustServiceDependencies", "none"),
    ("defaultState", "enabled"),
]
PQC_PLAN = {"key-establishment": ("committed", "product"),
            "entity-authentication": ("planned", "certification"),
            "non-repudiation": ("planned", "certification")}

HOST = {"type": "service", "bom-ref": "service:svc-host-commands",
        "name": "Host command interface (mutually authenticated TLS)",
        "properties": props(
            ("interfaceType", "service"), ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:client", "endpoint:payment-application"), ("endpointRole:server", "endpoint:hsm"),
            ("keyExchange", "ECDHE-secp384r1"), ("encryption", "AES-256-GCM"),
            ("authentication", "ECDSA-P-384-SHA-384"),
            ("protocolVersionsSupported", ["1.2", "1.3"]),
            ("keyExchangeSupported", ["ECDHE-secp256r1", "ECDHE-secp384r1"]),
            ("authenticationSupported", ["ECDSA-P-256-SHA-256", "ECDSA-P-384-SHA-384", "RSA-PSS-SHA-256"]),
            ("algorithmSelection", "Client certificates and groups are set in the HSM's security settings"),
            ("integrationConstraints", "Hybrid ML-KEM key exchange is committed for firmware 5.0; ML-DSA client certificates wait for FIPS 140-3 validation of the new firmware"),
            ("keysStoredIn", "service:sto-key-db"),
            *COMMON, *capability(PQC_PLAN))}

MGMT = {"type": "service", "bom-ref": "service:mgmt-console",
        "name": "Management console and key custodian smart cards",
        "properties": props(
            ("interfaceType", "management"), ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:administrator", "endpoint:security-officer"), ("endpointRole:server", "endpoint:hsm"),
            ("keyExchange", "ECDHE-secp384r1"), ("encryption", "AES-256-GCM"),
            ("authentication", "ECDSA-P-384-SHA-384"),
            ("protocolVersionsSupported", ["1.3"]),
            ("keyExchangeSupported", ["ECDHE-secp384r1"]),
            ("authenticationSupported", ["ECDSA-P-384-SHA-384"]),
            ("algorithmSelection", "Fixed by the firmware"),
            ("integrationConstraints", "Key ceremonies need a quorum of custodian smart cards"),
            ("managesKeys", "yes"),
            ("keyOperations", ["generate", "import", "export", "wrap", "unwrap", "derive", "delete", "zeroize"]),
            ("keyTypesSupported", ["TDEA-3KEY", "AES-128", "AES-256", "RSA-2048", "RSA-4096", "ECDSA-P256", "ECDSA-P384"]),
            ("keyTypes", ["TDEA-3KEY", "AES-128", "AES-256", "RSA-2048", "ECDSA-P384"]),
            ("keyStoreFormatsSupported", ["token-native", "other"]),
            ("keyStoreFormats", ["token-native"]),
            ("keyStoreLocation", "hsm"),
            ("keyBlockFormatsSupported", ["x9-143", "tr-31", "iso-20038"]),
            ("keyBlockFormats", ["x9-143", "tr-31"]),
            *COMMON, *capability(PQC_PLAN))}

RKL = {"type": "service", "bom-ref": "service:int-rkl-tr34",
       "name": "Remote key loading to terminals (TR-34)",
       "properties": props(
           ("interfaceType", "interconnect"), ("protocol", "TR-34"), ("protocolVersion", "2019"),
           ("endpointRole:initiator", "endpoint:hsm"), ("endpointRole:responder", "endpoint:terminal"),
           ("keyExchange", "RSA-2048"), ("encryption", "AES-128"),
           ("authentication", "RSA-PKCS1-1.5-SHA-256"),
           ("protocolVersionsSupported", ["2019"]),
           ("keyExchangeSupported", ["RSA-2048", "RSA-3072"]),
           ("authenticationSupported", ["RSA-PKCS1-1.5-SHA-256"]),
           ("algorithmSelection", "Set per terminal estate by the acquirer"),
           ("integrationConstraints", "No post-quantum key transport is standardised for TR-34 yet"),
           ("keysStoredIn", "service:sto-key-db"),
           *COMMON, *capability({"key-establishment": ("not-planned", "standard"),
                                 "entity-authentication": ("not-planned", "standard"),
                                 "non-repudiation": ("planned", "certification")}))}

def store(ref, name, block_format, protected_by, note):
    return {"type": "service", "bom-ref": ref, "name": name,
            "properties": props(
                ("interfaceType", "storage"), ("encryption", "AES-256"), ("keyWrapping", "AES-256"),
                ("keyWrappingSupported", ["AES-256"]),
                ("algorithmSelection", "Not applicable"), ("integrationConstraints", note),
                ("keysStoredIn", "service:mgmt-console"),
                ("protectedBy", protected_by), ("keyBlockFormats", block_format),
                *COMMON, *capability({"non-repudiation": ("planned", "certification")}))}

LMK = store("service:sto-lmk", "Local master key store (inside the tamper-responsive boundary)",
            "proprietary", "hardware-root",
            "The local master key never leaves the HSM. It is protected by the tamper-responsive hardware.")
KEYDB = store("service:sto-key-db", "Working key database on the host, under the local master key",
              "x9-143", "service:sto-lmk",
              "Working keys and zone master keys are kept on the host in X9.143 key blocks, wrapped under the local master key.")

INTERFACES = [HOST, MGMT, RKL, LMK, KEYDB]

def product(interfaces, serial):
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "$comment": "Illustrative example for the draft HSM Product and HSM Key Hierarchy profiles. The HSM, its vendor and every value are invented. Built by drafts/hsm-product/build.py.",
        "serialNumber": serial, "version": 1,
        "metadata": {"timestamp": "2026-11-26T12:00:00Z", "lifecycles": [{"phase": "build"}],
                     "tools": {"components": [{"type": "application", "name": "PKIC CBOM Profiles WG worked-example builder", "version": "0.1"}]},
                     "supplier": {"name": "Example HSM Vendor (illustrative)"}},
        "inventories": [{
            "bom-ref": "inventory:subject",
            "subject": {
                "type": "device", "bom-ref": "device:example-payment-hsm", "name": "Example Payment HSM 9000",
                "version": "4.2.0",
                "description": "Illustrative payment HSM, firmware 4.2.0, as shipped.",
                "properties": props(("subjectType", "product"), ("coverage", "all"),
                                    ("productCertificationScheme", "pci-pts-hsm"),
                                    ("productCertificationRef", "illustrative: PCI PTS HSM approval 0-00000"),
                                    ("absent:support-lifecycle", "not-published")),
                "identifiers": [{"party": "party:document-author", "identities": [
                    {"scheme": "purl", "value": "pkg:generic/example-hsm-vendor/payment-hsm-9000@4.2.0"}]}],
                "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                             "organization": {"name": "Example HSM Vendor (illustrative)"}}]},
            "components": [{"type": "library", "bom-ref": "lib:hsm-firmware", "name": "Payment HSM 9000 cryptographic firmware",
                            "version": "4.2.0",
                            "identifiers": [{"party": "party:document-author", "identities": [
                                {"scheme": "purl", "value": "pkg:generic/example-hsm-vendor/payment-hsm-9000-firmware@4.2.0"}]}]}]
                          + interfaces}],
        "dependencies": [{"ref": "device:example-payment-hsm", "dependsOn": [i["bom-ref"] for i in interfaces]},
                         {"ref": "lib:hsm-firmware", "provides": [i["bom-ref"] for i in interfaces]}],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:7e5a0000-0000-4000-8000-00000000a001/1",
             "comment": "Illustrative SBOM of the same firmware release.",
             "properties": [{"name": "pkic:profile:context", "value": "sbom"}],
             "hashes": [{"alg": "SHA-256", "content": "0" * 64}]},
            {"type": "vulnerability-assertion", "url": "https://hsm.example.com/.well-known/csaf/provider-metadata.json",
             "comment": "Illustrative: the vendor's CSAF provider, where it publishes statements about whether its products are affected by vulnerabilities.",
             "properties": [{"name": "pkic:profile:context", "value": "vulnerability-statements"},
                            {"name": "pkic:profile:accessProtocol", "value": "csaf-provider"}]},
            {"type": "documentation", "url": "https://hsm.example.com/roadmap/post-quantum",
             "comment": "Illustrative: the vendor's post-quantum roadmap.",
             "properties": [{"name": "pkic:profile:context", "value": "roadmap"}]}]}

os.makedirs(EX, exist_ok=True)
good = product(INTERFACES, "urn:uuid:7e5a0000-0000-4000-8000-00000000a000")
bad_mgmt = copy.deepcopy(MGMT)
bad_mgmt["properties"] = [p for p in bad_mgmt["properties"] if p["name"] != "pkic:profile:keyBlockFormatsSupported"]
bad = product([HOST, bad_mgmt, RKL, LMK, KEYDB], "urn:uuid:7e5a0000-0000-4000-8000-00000000a0f1")
bad["$comment"] += " Non-conforming variant: the management interface omits keyBlockFormatsSupported (hsm-product I1)."
for name, doc in (("cbom-example-payment-hsm-product.cdx.json", good),
                  ("cbom-example-payment-hsm-product-fail-I1.cdx.json", bad)):
    with open(os.path.join(EX, name), "w") as f:
        json.dump(doc, f, indent=2); f.write("\n")
    print("wrote examples/" + name)
