#!/usr/bin/env python3
"""Build a product record of the Thales Luna T7 cryptographic module from its FIPS 140-3 security policy.

Writes examples/cbom-thales-luna-t7-fw-7.15.1.cdx.json.

The record is the first real example of the draft HSM Product and HSM Key
Hierarchy profiles (HSMs and key management domain document, chapter 10). The
working group wrote it from public sources only, read on 26 November 2026:
the CMVP certificate #5450 and the module's FIPS 140-3 non-proprietary
security policy (document 002-500027-001, revision G, 14 April 2026). The
vendor has not reviewed it. Every value cites the section or table it comes
from. A fact the security policy does not state is marked 'unknown' with a
disclosure marker, and no value is guessed.

The record describes the validated module (the PCIe card and its firmware),
not the Luna Network HSM appliance or the services built on the module. Their
management interfaces, such as SSH to the appliance, are outside the module
boundary and belong in their own records, which would cite this one.

Usage: python3 drafts/hsm-luna-t7/build.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "examples")
PURPOSES = ["key-establishment", "encryption", "entity-authentication", "data-integrity",
            "non-repudiation", "key-protection", "key-derivation"]
CERT = "https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/5450"
SP = ("https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/"
      "documents/security-policies/140sp5450.pdf")


def props(*pairs):
    out = []
    for name, value in pairs:
        for v in (value if isinstance(value, list) else [value]):
            out.append({"name": "pkic:profile:" + name, "value": v})
    return out


def unknown(*attrs):
    return [{"name": "pkic:profile:disclosure:" + a, "value": "unknown"} for a in attrs]


SYMMETRIC = ["encryption", "data-integrity", "key-protection", "key-derivation"]


def capability(pqc_purposes):
    """G1. Symmetric purposes are served by AES-256, HMAC and approved KDFs in the validated mode, which
    need no post-quantum replacement. Asymmetric purposes for which the module offers an approved
    post-quantum algorithm on this interface are 'available' in the validated mode. For the remaining
    asymmetric purposes the security policy states no capability and no plan, so the status is marked
    unknown and the entry is missing; G1 fails on them, which is what a reader of a security policy
    alone cannot learn."""
    pairs, unk = [], []
    for p in PURPOSES:
        if p in SYMMETRIC or p in pqc_purposes:
            pairs.append(("capabilityByPurpose:%s:capabilityStatus" % p, "available"))
            pairs.append(("capabilityByPurpose:%s:validatedModeAvailability" % p, "in-validated-mode"))
        else:
            unk.append("capabilityByPurpose:%s:capabilityStatus" % p)
    return pairs, unk


# Facts shared by every interface: one firmware release under one certificate.
COMMON = [
    ("executionEnvironment", "hsm"),
    ("availableFromVersion", "7.15.1"),
    ("moduleValidationScheme", "fips-140-3"),
    ("moduleValidationRef", "CMVP certificate #5450 (FIPS 140-3, overall level 3, validated 29 July 2026)"),
    ("certificationImpact", "recertification"),
    ("impactedCertification", "FIPS 140-3"),
    ("trustServiceDependencies", "none"),
    ("defaultState", "disabled"),
]
COMMON_UNKNOWN = ["enablementMethod", "transitionMode", "implementingLibrary", "protocolVersionsSupported"]
CONSTRAINT_MODE = ("The approved mode must be set by the Security Officer with HSM policy 12 "
                   "(security policy, section 11.1.2); the module is valid only when configured that way. ")


def iface(ref, name, itype, specific, pqc, unknowns=(), note=None):
    cap, cap_unknown = capability(pqc)
    c = {"type": "service", "bom-ref": ref, "name": name,
         "properties": props(("interfaceType", itype), *specific, *COMMON, *cap)
                       + unknown(*COMMON_UNKNOWN, *unknowns, *cap_unknown)}
    if note:
        c["description"] = note
    return c


ALL_PQC = ["key-establishment", "entity-authentication", "non-repudiation"]

ICD = iface(
    "service:svc-icd", "Cryptographic services for host applications over PCIe (ICD commands)", "service",
    [("protocol", "Luna ICD command interface"),
     ("endpointRole:client", "endpoint:host-application"), ("endpointRole:server", "endpoint:luna-t7"),
     ("keyExchange", "none"), ("encryption", "none"), ("authentication", "password"),
     ("keyExchangeSupported", "none"), ("authenticationSupported", ["password", "ped-key"]),
     ("keyTypesSupported", ["AES-128", "AES-192", "AES-256", "TDEA-3KEY", "RSA-2048", "RSA-3072", "RSA-4096",
                            "ECDSA-P256", "ECDSA-P384", "ECDSA-P521", "ML-KEM", "ML-DSA", "LMS"]),
     ("algorithmSelection", "The application chooses the mechanism in each command"),
     ("integrationConstraints", CONSTRAINT_MODE +
      "ICD input and output are plaintext over the PCIe bus (table 18). The user password is entered "
      "encrypted under the module's RSA-4096 PEC key (tables 18, 20, 21). Approved services include ML-KEM "
      "key generation, encapsulation and decapsulation, ML-DSA and LMS key generation, signing and "
      "verification (tables 4, 5 and 13; algorithm certificates A7879 and A7880). Parameter sets are not "
      "restated here."),
     ("keysStoredIn", "service:sto-partition-keys")],
    ALL_PQC, ["protocolVersion"],
    "The command interface that applications reach, normally through the vendor's PKCS #11 library on the host. "
    "The library is outside the module boundary, so its mechanism list is not part of this record.")

ADMIN = iface(
    "service:mgmt-icd", "Administration by the Security Officer and Crypto Officer (ICD commands)", "management",
    [("protocol", "Luna ICD command interface"),
     ("endpointRole:administrator", "endpoint:security-officer"), ("endpointRole:server", "endpoint:luna-t7"),
     ("keyExchange", "none"), ("encryption", "none"), ("authentication", "password"),
     ("keyExchangeSupported", "none"), ("authenticationSupported", ["password", "ped-key"]),
     ("algorithmSelection", "Fixed by the firmware; HSM policies set by the Security Officer"),
     ("integrationConstraints", CONSTRAINT_MODE +
      "Roles authenticate with a password or with PED keys (section 11.1.2, tables 13 and 18)."),
     ("managesKeys", "yes"),
     ("keyOperations", ["generate", "import", "export", "wrap", "unwrap", "derive", "delete", "zeroize"]),
     ("keyTypesSupported", ["AES-128", "AES-192", "AES-256", "TDEA-3KEY", "RSA-2048", "RSA-3072", "RSA-4096",
                            "ECDSA-P256", "ECDSA-P384", "ECDSA-P521", "ML-KEM", "ML-DSA", "LMS"]),
     ("keyStoreFormatsSupported", ["token-native"]),
     ("keyStoreLocation", "hsm"),
     ("keyBlockFormatsSupported", ["proprietary"]),
     ("keysStoredIn", "service:sto-partition-keys")],
    ALL_PQC, ["protocolVersion", "keyTypes", "keyStoreFormats", "keyBlockFormats"],
    "Key generation, import, export, wrapping and zeroisation, and HSM policy changes. Which key types and "
    "formats an owner actually uses is a deployment fact, so it is marked unknown here.")

PED = iface(
    "service:mgmt-ped", "PIN entry device for role authentication and the master key split", "management",
    [("protocol", "Luna PED (local serial or remote PED)"),
     ("endpointRole:administrator", "endpoint:ped-key-holder"), ("endpointRole:server", "endpoint:luna-t7"),
     ("keyExchange", "ECDH"), ("encryption", "AES-256"), ("authentication", "HMAC"),
     ("keyExchangeSupported", ["ECDH", "RSA"]), ("authenticationSupported", "HMAC"),
     ("managesKeys", "no"),
     ("algorithmSelection", "Fixed by the firmware"),
     ("integrationConstraints",
      "The PED tunnel is established with KAS-ECC (table 13). Remote PED traffic is protected with KTS-RSA "
      "and KTS-HMAC; a locally connected PED (TPED) passes data in plaintext over the serial port (table 18). "
      "The SRV, from which the master key is derived together with an internal split, is held on the purple "
      "PED key (section 7.7.1, table 21). The curve and the RSA key size of the remote path are not restated.")],
    [], ["protocolVersion"],
    "The serial PED port carries authentication data only (table 10).")

FIRMWARE = iface(
    "service:mgmt-firmware-load", "Firmware load and its signature check", "management",
    [("protocol", "Luna firmware update"),
     ("endpointRole:administrator", "endpoint:security-officer"), ("endpointRole:server", "endpoint:luna-t7"),
     ("keyExchange", "none"), ("encryption", "none"), ("authentication", "RSA-4096-SHA-384"),
     ("keyExchangeSupported", "none"), ("authenticationSupported", "RSA-4096-SHA-384"),
     ("managesKeys", "no"),
     ("algorithmSelection", "Fixed by the firmware"),
     ("integrationConstraints",
      "A firmware load test verifies an RSA 4096 signature with SHA2-384 before the new firmware is accepted "
      "(table 23). The bootloader checks its own integrity with a SHA-1 error detection code, and the "
      "firmware with a SHA2-256 known-answer test (table 22, section 5.1). Whether the verification key "
      "can itself be replaced is not stated.")],
    [], ["protocolVersion"],
    "The verifier of firmware updates. It decides whether the module can later accept firmware signed with a "
    "new algorithm (question register R2-30).")

CLONING = iface(
    "service:int-cloning", "Cloning of keys between Luna modules", "interconnect",
    [("protocol", "Luna cloning protocol"),
     ("endpointRole:initiator", "endpoint:luna-t7"), ("endpointRole:responder", "endpoint:luna-t7-peer"),
     ("keyExchange", "RSA-4096"), ("encryption", "AES-256-KWP"), ("authentication", "RSA-4096"),
     ("keyExchangeSupported", "RSA-4096"), ("authenticationSupported", "RSA-4096"),
     ("algorithmSelection", "Fixed by the firmware"),
     ("integrationConstraints",
      "The cloning tunnel is established with KAS-RSA between the modules' RSA-4096 TUK keys, whose "
      "certificates (TWC) are signed by the module's HOK (tables 13, 20, 21). Objects are wrapped with AES "
      "KWP under a cloning key encryption vector derived with a two-step KDF of SP 800-56C and SP 800-108 "
      "(section 2.10.2). Only modules in the same domain can clone. No post-quantum key establishment is "
      "listed for this interface."),
     ("keysStoredIn", "service:sto-partition-keys")],
    [], ["protocolVersion"])

EXPORT = iface(
    "service:int-wrapped-export", "Key export, import, backup and restore under a wrapping key", "interconnect",
    [("protocol", "Luna wrapped key transfer"),
     ("endpointRole:initiator", "endpoint:luna-t7"), ("endpointRole:responder", "endpoint:key-recipient"),
     ("keyExchange", "RSA-OAEP"), ("encryption", "AES-256-KWP"), ("authentication", "none"),
     ("keyExchangeSupported", ["RSA-OAEP", "none"]), ("authenticationSupported", "none"),
     ("algorithmSelection", "The application chooses the wrapping mechanism"),
     ("integrationConstraints",
      "Key export and import, and partition backup and restore, use KTS-AES (table 13). Approved key "
      "transport is AES-KW and AES-KWP (SP 800-38F), RSA-OAEP (SP 800-56B rev 2, 128-bit strength), and "
      "AES-CBC with HMAC-SHA2-256 (section 2.10.3). Wrapped keys pass through the WICD path (table 18). "
      "ML-KEM is an approved service of the module, but its use for key transport on this interface is not "
      "stated."),
     ("keysStoredIn", "service:sto-partition-keys")],
    [], ["protocolVersion"])


# A key store is protected with AES-256 only (tables 20 and 21). It has no asymmetric use, so every
# purpose is recorded as available, as in the illustrative payment HSM.
STORE_PURPOSES = ["key-establishment", "entity-authentication", "non-repudiation"]


def store(ref, name, encryption, wrapping, protected_by, note):
    return iface(ref, name, "storage",
        [("encryption", encryption), ("keyWrapping", wrapping), ("keyWrappingSupported", [wrapping]),
         ("algorithmSelection", "Not applicable"), ("integrationConstraints", note),
         ("keysStoredIn", "service:mgmt-icd"),
         ("protectedBy", protected_by), ("keyBlockFormats", "proprietary")],
        STORE_PURPOSES, [])


MTK = store("service:sto-mtk", "Master tamper key in battery-backed NVRAM", "none", "none", "hardware-root",
            "The MTK, an AES-256 key, is held in battery-backed NVRAM inside the tamper-responsive boundary and is "
            "zeroised on tamper or decommission (tables 17, 19, 20, 21). It is derived from an internal split and "
            "the SRV held on the purple PED key (section 7.7.1).")
PARTITION = store("service:sto-partition-keys", "Partition keys in flash, encrypted under the master tamper key",
                  "AES-256", "AES-256", "service:sto-mtk",
                  "Partition symmetric, RSA, ECDSA, DSA, LMS, ML-DSA and ML-KEM private keys are stored encrypted in "
                  "flash and in RAM, under the MTK (section 7.7.1, tables 20 and 21). The wrapping mode is not "
                  "restated.")

INTERFACES = [ICD, ADMIN, PED, FIRMWARE, CLONING, EXPORT, MTK, PARTITION]

record = {
    "specFormat": "CycloneDX", "specVersion": "2.0",
    "$comment": ("Product record of the Thales Luna T7 cryptographic module, firmware 7.15.1, written by the PKIC CBOM "
                 "Profiles Working Group from the CMVP certificate #5450 and the module's FIPS 140-3 security policy, "
                 "read on 26 November 2026. Not reviewed by the vendor. Facts the security policy does not state are "
                 "marked unknown. Built by drafts/hsm-luna-t7/build.py."),
    "serialNumber": "urn:uuid:7e5a0000-0000-4000-8000-00000000b000", "version": 1,
    "metadata": {"timestamp": "2026-11-26T12:00:00Z", "lifecycles": [{"phase": "build"}],
                 "tools": {"components": [{"type": "application", "name": "Manual reading of public documentation",
                                           "version": "1",
                                           "description": "The CMVP certificate and security policy listed in externalReferences"}]},
                 "supplier": {"name": "Thales Trusted Cyber Technologies"}},
    "inventories": [{
        "bom-ref": "inventory:subject",
        "subject": {
            "type": "device", "bom-ref": "device:luna-t7", "name": "Luna T7 cryptographic module",
            "version": "7.15.1",
            "description": ("Half-height PCIe cryptographic module, part 872-500025-001 (Luna T7) and 875-500025-002 "
                            "(Luna T7U), firmware 7.15.1, bootloader 2.0.1 and 2.0.2 (security policy, table 2). "
                            "It is built into the Luna PCIe HSM, Luna Network HSM, Luna as a Service and CipherTrust "
                            "Manager offerings."),
            "properties": props(("subjectType", "product"), ("coverage", "all"),
                                ("productCertificationScheme", "none"),
                                ("productCertificationScheme", "none"),
                                ("absent:support-lifecycle", "not-published"))
                          + unknown("correspondsTo"),
            "identifiers": [{"party": "party:vendor", "identities": [
                {"scheme": "mpn", "value": "872-500025-001"}, {"scheme": "mpn", "value": "875-500025-002"}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "PKIC CBOM Profiles Working Group (from public sources)"}},
                        {"bom-ref": "party:vendor", "roles": [{"role": "manufacturer"}],
                         "organization": {"name": "Thales Trusted Cyber Technologies"}}]},
        "components": [{"type": "library", "bom-ref": "lib:luna-t7-firmware", "name": "Luna T7 firmware",
                        "version": "7.15.1"}] + INTERFACES}],
    "dependencies": [{"ref": "device:luna-t7", "dependsOn": [i["bom-ref"] for i in INTERFACES]},
                     {"ref": "lib:luna-t7-firmware", "provides": [i["bom-ref"] for i in INTERFACES]}],
    "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
    "externalReferences": [
        {"type": "certification-report", "url": CERT,
         "comment": "CMVP certificate #5450: FIPS 140-3, overall level 3, validated 29 July 2026, sunset 28 July 2031."},
        {"type": "documentation", "url": SP,
         "comment": "FIPS 140-3 non-proprietary security policy, document 002-500027-001, revision G, 14 April 2026.",
         "properties": [{"name": "pkic:profile:context", "value": "security-policy"}]}]}

os.makedirs(EX, exist_ok=True)
out = os.path.join(EX, "cbom-thales-luna-t7-fw-7.15.1.cdx.json")
with open(out, "w") as f:
    json.dump(record, f, indent=2); f.write("\n")
print("wrote examples/" + os.path.basename(out))
