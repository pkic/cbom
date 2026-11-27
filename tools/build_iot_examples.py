#!/usr/bin/env python3
"""Write the IoT device estate worked example.

Two illustrative LoRaWAN soil sensors, described by their manufacturer against iot-device, which
extends the change core. S1 can never be updated: no update mechanism, a factory-injected root key
that cannot be replaced, and a radio frame too small for any post-quantum key exchange or signature.
S2 can be updated over the air and keeps its keys in a secure element. Read together, the two show
the profile separating the four actions: replace S1, update S2. One non-conforming variant of S1
leaves out the resource bound.

Values are illustrative. The LoRaWAN facts (AES-128, a 242-byte maximum application payload at the
highest data rate in EU868) follow the LoRaWAN 1.0.4 specification and regional parameters.

Usage: python3 tools/build_iot_examples.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "docs", "methodology", "examples")
CONTEXT = os.path.join(OUT, "context")
P = "pkic:profile:"
STAMP = "2026-11-18T09:00:00Z"
AUTHOR = {"name": "Example Sensors (illustrative manufacturer)"}


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


def ident(purl):
    return [{"party": "party:document-author", "identities": [{"scheme": "purl", "value": purl}]}]


def capability(rows):
    out = []
    for purpose, status, blocker in rows:
        out.append(("capabilityByPurpose:%s:capabilityStatus" % purpose, status))
        if blocker:
            out.append(("capabilityByPurpose:%s:blockedBy" % purpose, blocker))
    return out


def iface(ref, name, kind, pairs):
    return {"type": "service", "bom-ref": ref, "name": name,
            "properties": props([("interfaceType", kind)] + pairs + [("defaultState", "enabled")])}


FRAME = ("integrationConstraints", "The largest application payload is 242 bytes (EU868, highest data rate) and "
         "51 bytes at the lowest. An ML-KEM-768 ciphertext is 1,088 bytes and an ML-DSA-44 signature 2,420 bytes, "
         "so neither fits a frame.")


def radio(provider_location):
    return iface("radio-lorawan", "LoRaWAN radio link (uplink and downlink)", "interconnect", [
        ("protocol", "LoRaWAN"), ("protocolVersion", "1.0.4"),
        ("endpointRole:client", "endpoint:sensor"), ("endpointRole:server", "endpoint:network-server"),
        ("keyExchange", "none"), ("encryption", "AES-128-CTR"), ("authentication", "AES-128-CMAC"),
        ("protocolVersionsSupported", "1.0.4"), ("keyExchangeSupported", "none"),
        ("authenticationSupported", "AES-128-CMAC"),
        ("algorithmSelection", "None: the algorithms are fixed by the LoRaWAN specification"), FRAME,
        ("keysStoredIn", "sto-keys"), ("terminationOptions", "device"),
        ("executionEnvironment", provider_location)])


# --- S1: no update path -----------------------------------------------------------------------
S1 = {"serial": "10700001-5e45-4e01-9a01-000000000001", "sbom": "10700001-5e45-4e01-9a01-0000000000b1",
      "purl": "pkg:generic/example-sensors/soil-sensor-s1@1.3.0",
      "fw": "pkg:generic/example-sensors/s1-firmware@1.3.0"}
S1_CAP = [("key-establishment", "not-planned", "hardware"), ("encryption", "available", None),
          ("entity-authentication", "not-planned", "hardware"), ("data-integrity", "available", None),
          ("non-repudiation", "not-planned", "product"), ("key-protection", "not-planned", "hardware"),
          ("key-derivation", "available", None)]

# --- S2: updatable over the air -----------------------------------------------------------------
S2 = {"serial": "10700002-5e45-4e01-9a01-000000000001", "sbom": "10700002-5e45-4e01-9a01-0000000000b1",
      "purl": "pkg:generic/example-sensors/soil-sensor-s2@2.0.1",
      "fw": "pkg:generic/example-sensors/s2-firmware@2.0.1"}
S2_CAP = [("key-establishment", "not-planned", "standard"), ("encryption", "available", None),
          ("entity-authentication", "planned", "standard"), ("data-integrity", "available", None),
          ("non-repudiation", "planned", "standard"), ("key-protection", "available", None),
          ("key-derivation", "available", None)]


def library(ref, name, version, purl, cap, enablement, transitionMode, extra=()):
    return {"type": "library", "bom-ref": ref, "name": name, "version": version,
            "properties": props([("enablementMethod", enablement), ("transitionMode", transitionMode)] + list(extra)
                                + capability(cap)),
            "identifiers": ident(purl)}


def subject(model, version, purl, description, extra):
    return {"type": "device", "bom-ref": "dev:sensor", "name": model, "version": version,
            "description": description, "properties": extra, "identifiers": ident(purl),
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}], "organization": AUTHOR}]}


def record(m, model, version, description, subject_props, components, provides, comment, sbom_hash):
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0", "$comment": comment,
        "serialNumber": "urn:uuid:" + m["serial"], "version": 1,
        "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}], "supplier": AUTHOR},
        "inventories": [{"bom-ref": "inventory:subject",
                         "subject": subject(model, version, m["purl"], description, props(subject_props)),
                         "components": components}],
        "dependencies": [{"ref": "dev:sensor", "dependsOn": [c["bom-ref"] for c in components]}] +
                        [{"ref": k, "provides": v} for k, v in provides.items()],
        "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
        "externalReferences": [
            {"type": "bom", "url": "urn:cdx:%s/1" % m["sbom"], "comment": "Companion SBOM of the same firmware.",
             "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": sbom_hash}]},
            {"type": "advisories", "url": "https://psirt.example.com/sensors/advisories",
             "comment": "The manufacturer's security advisories (illustrative).",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://psirt.example.com/contact",
             "comment": "The manufacturer's security contact (illustrative).",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])}]}


def sbom(m, model, version, libs):
    return {"specFormat": "CycloneDX", "specVersion": "2.0",
            "$comment": "EXAMPLE SBOM for the illustrative %s. Lists only the libraries the CBOM names, so its "
                        "composition is incomplete." % model,
            "serialNumber": "urn:uuid:" + m["sbom"], "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}], "supplier": AUTHOR},
            "inventories": [{"bom-ref": "inventory:subject",
                             "subject": subject(model, version, m["purl"], "", []),
                             "components": [{"type": "library", "bom-ref": c["bom-ref"], "name": c["name"],
                                             "version": c["version"], "identifiers": c["identifiers"]}
                                            for c in libs]}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def s1():
    libs = [library("lib:s1-firmware", "S1 firmware and LoRaWAN stack (illustrative)", "1.3.0", S1["fw"], S1_CAP,
                    "not-available", "switch-over")]
    comps = libs + [
        radio("mcu-internal"),
        iface("sto-keys", "LoRaWAN root key (AppKey) and device identity", "storage", [
            ("encryption", "none"), ("keyWrapping", "none"),
            ("algorithmSelection", "Not applicable"),
            ("integrationConstraints", "The root key is written at manufacture into the microcontroller's internal "
                                       "flash, with read-out protection set."),
            ("keyReplaceable", "not-replaceable"), ("keyProvisioning", "factory-injected")])]
    subject_props = [("coverage", "all"), ("subjectType", "product"),
                     ("absent:management-interface", "no-configuration-surface"),
                     ("updateMechanism", "none"), ("updateSupportStatus", "never-offered"),
                     ("resourceLimits", "flash=16384 ram=4096 frame=242"),
                     ("absent:support-lifecycle", "not-published"), ("absent:roadmap", "not-published"),
                     ("absent:vulnerability-statements", "not-published")]
    return libs, comps, subject_props, {"lib:s1-firmware": ["radio-lorawan", "sto-keys"]}


def s2():
    libs = [library("lib:s2-firmware", "S2 firmware and LoRaWAN stack (illustrative)", "2.0.1", S2["fw"], S2_CAP,
                    "software-update", "side-by-side", [("availableFromVersion", "unreleased")])]
    comps = libs + [
        radio("secure-element"),
        iface("upd-fuota", "Firmware update over the air (LoRaWAN FUOTA)", "management", [
            ("protocol", "LoRaWAN FUOTA"), ("protocolVersion", "1.0.0"),
            ("endpointRole:client", "endpoint:sensor"), ("endpointRole:server", "endpoint:fuota-server"),
            ("keyExchange", "none"), ("encryption", "AES-128-CTR"), ("authentication", "ECDSA-P-256-SHA-256"),
            ("protocolVersionsSupported", "1.0.0"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", "ECDSA-P-256-SHA-256"),
            ("algorithmSelection", "The firmware signature algorithm is fixed by the bootloader"),
            ("integrationConstraints", "Images arrive in fragments over multicast and are verified as a whole by "
                                       "the bootloader, so a larger post-quantum signature costs flash, not frames."),
            ("updateMechanism", "remote-managed"), ("updateAuthority", "platform"),
            ("updateAuthoritySupported", ["platform", "vendor"]),
            ("keysStoredIn", "sto-keys"), ("terminationOptions", "device"),
            ("executionEnvironment", "secure-element")]),
        iface("sto-keys", "LoRaWAN root key and firmware verification key, in a secure element", "storage", [
            ("encryption", "AES-128-CCM"), ("keyWrapping", "AES-128-KW"),
            ("algorithmSelection", "Not applicable"),
            ("integrationConstraints", "The secure element holds the root key and the firmware verification key, "
                                       "which a signed update can replace."),
            ("keyReplaceable", "software-update"), ("keyProvisioning", "provisioned-at-onboarding")])]
    subject_props = [("coverage", "all"), ("subjectType", "product"),
                     ("updateMechanism", "remote-managed"), ("updateSupportStatus", "supported"),
                     ("resourceLimits", "flash=262144 ram=65536 frame=242"),
                     ("absent:support-lifecycle", "not-published"), ("absent:roadmap", "not-published"),
                     ("absent:vulnerability-statements", "not-published")]
    return libs, comps, subject_props, {"lib:s2-firmware": ["radio-lorawan", "upd-fuota", "sto-keys"]}


def build(m, model, version, description, parts, stem, comment):
    libs, comps, subject_props, provides = parts
    h = write(os.path.join(CONTEXT, "%s-sbom.cdx.json" % stem), sbom(m, model, version, libs))
    rec = record(m, model, version, description, subject_props, comps, provides, comment, h)
    write(os.path.join(OUT, "cbom-%s-product.cdx.json" % stem), rec)
    return rec


def main():
    os.makedirs(CONTEXT, exist_ok=True)
    r1 = build(S1, "Soil sensor S1 (illustrative)", "1.3.0",
               "A battery-powered soil sensor reaching a gateway over LoRaWAN. No update mechanism and a "
               "factory-injected root key. Values are illustrative.", s1(), "iot-sensor-s1",
               "EXAMPLE CBOM, lifecycle stage 'implemented'. An illustrative LoRaWAN soil sensor that can never be "
               "updated, described by its manufacturer against iot-device v0.1. Read with the S2 record: the operator "
               "replaces S1 and updates S2.")
    build(S2, "Soil sensor S2 (illustrative)", "2.0.1",
          "A battery-powered soil sensor reaching a gateway over LoRaWAN, with firmware update over the air and "
          "keys in a secure element. Values are illustrative.", s2(), "iot-sensor-s2",
          "EXAMPLE CBOM, lifecycle stage 'implemented'. An illustrative LoRaWAN soil sensor that can be updated "
          "over the air, described by its manufacturer against iot-device v0.1. Read with the S1 record.")
    v = copy.deepcopy(r1)
    v["serialNumber"] = "urn:uuid:10700001-5e45-4e01-9a01-0000000000f1"
    v["$comment"] = ("NON-CONFORMING EXAMPLE. The S1 record with resourceLimits left out. Fails iot-device#P1 only: "
                     "the operator cannot tell a permanent 'no' from one a firmware release could change.")
    subj = v["inventories"][0]["subject"]
    subj["properties"] = [p for p in subj["properties"] if p["name"] != P + "resourceLimits"]
    write(os.path.join(OUT, "cbom-iot-sensor-s1-product-fail-P1.cdx.json"), v)
    print("written to", OUT)


if __name__ == "__main__":
    main()
