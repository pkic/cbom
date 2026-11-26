#!/usr/bin/env python3
"""Build the financial services worked example: AWS Payment Cryptography as a service record.

Writes examples/cbom-aws-payment-cryptography-service.cdx.json.

The record is written by the working group from the provider's public
documentation, read on 26 November 2026. It has not been reviewed by the
provider. Every value comes from a documentation page named in SOURCES. A fact
the pages do not state is marked 'unknown' with a disclosure marker, never
guessed. Checking the record against Service Disclosure then shows which facts
a customer can learn from the public documentation, and which only the
provider can supply.

Usage: python3 drafts/fs-payment-cryptography-service/build.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "examples", "cbom-aws-payment-cryptography-service.cdx.json")
DOCS = "https://docs.aws.amazon.com/payment-cryptography/latest/userguide/"

SOURCES = {
    "data-protection": DOCS + "data-protection.html",
    "infrastructure": DOCS + "infrastructure-security.html",
    "import-export": DOCS + "keys-importexport.html",
    "foundations": DOCS + "cryptographic-details.foundations.html",
    "key-attributes": DOCS + "keys-validattributes.html",
    "terminology": DOCS + "terminology.html",
}


def prop(name, value):
    return {"name": "pkic:profile:" + name, "value": value}


def unknown(attr):
    return {"name": "pkic:profile:disclosure:" + attr, "value": "unknown"}


def iface(ref, name, props, note=None):
    c = {"type": "service", "bom-ref": ref, "name": name, "properties": props}
    if note:
        c["description"] = note
    return c


API_TLS = iface(
    "service:api-tls", "TLS on the control plane and data plane API endpoints",
    [prop("interfaceType", "service"),
     prop("protocol", "TLS"),
     prop("protocolVersion", "1.2, 1.3"),
     prop("endpointRole:client", "endpoint:customer-application"),
     prop("endpointRole:server", "endpoint:aws-api-endpoint"),
     prop("correspondsTo", "no-product-document"),
     unknown("keyExchange"),
     unknown("encryption"),
     unknown("authentication"),
     unknown("implementationPurl"),
     prop("integrationConstraints",
          "Clients must support TLS 1.2 or later (infrastructure security page). The data protection page "
          "states that endpoints support TLS 1.0 to 1.3, and that the service requires the versions and "
          "cipher suites PCI defines as strong cryptography. Hybrid post-quantum key exchange with ML-KEM "
          "is offered, and the client decides whether to use it. The groups, cipher suites and server "
          "certificate algorithm are not stated, so the key exchange is marked unknown.")],
    "Carries every API call. The pages read do not name the TLS groups, cipher suites or certificate algorithm.")

def api(ref, name, itype, what):
    return iface(ref, name,
        [prop("interfaceType", itype),
         prop("protocol", "HTTPS API"),
         unknown("protocolVersion"),
         prop("endpointRole:client", "endpoint:customer-application"),
         prop("endpointRole:server", "endpoint:aws-api-endpoint"),
         prop("correspondsTo", "no-product-document"),
         prop("keyExchange", "none"),
         prop("encryption", "none"),
         unknown("authentication"),
         unknown("implementationPurl"),
         prop("integrationConstraints",
              "Carried over service:api-tls. Every call must be signed (data protection page); the signing "
              "algorithm is not stated on the pages read.")],
        what)

CONTROL = api("service:mgmt-control-plane", "Control plane API: create, import, export and delete keys",
              "management", "Key management operations, including import and export of keys.")
DATA = api("service:svc-data-plane", "Data plane API: payment operations", "service",
           "Payment operations such as PIN translation, card verification values and EMV cryptograms.")

KEK_TR34 = iface(
    "service:kt-kek-tr34", "Import and export of key-encryption keys with TR-34",
    [prop("interfaceType", "interconnect"),
     prop("protocol", "TR-34"),
     unknown("protocolVersion"),
     prop("endpointRole:initiator", "endpoint:key-distribution-host"),
     prop("endpointRole:responder", "endpoint:key-receiving-device"),
     prop("correspondsTo", "no-product-document"),
     prop("keyExchange", "RSA-2048, RSA-3072, RSA-4096"),
     unknown("encryption"),
     unknown("authentication"),
     unknown("implementationPurl"),
     prop("integrationConstraints",
          "The import and export page lists TR-34 with RSA 2048, 3072 and 4096 bit keys for exchanging "
          "key-encryption keys, and RSA wrap where a partner does not support TR-34. Every working key "
          "later exchanged under a key-encryption key inherits the exposure of this interface.")])

KEK_ECDH = iface(
    "service:kt-kek-ecdh", "Import and export of key-encryption keys with ECDH",
    [prop("interfaceType", "interconnect"),
     prop("protocol", "ECDH key agreement"),
     unknown("protocolVersion"),
     prop("endpointRole:initiator", "endpoint:partner-hsm"),
     prop("endpointRole:responder", "endpoint:aws-payment-cryptography"),
     prop("correspondsTo", "no-product-document"),
     prop("keyExchange", "ECDH-P-256, ECDH-P-384, ECDH-P-521"),
     unknown("encryption"),
     unknown("authentication"),
     unknown("implementationPurl"),
     prop("integrationConstraints",
          "NIST curves P-256, P-384 and P-521; the shared secret is derived with the key derivation "
          "function of NIST SP 800-56A or ANSI X9.63 (import and export page; AWS blog). ECDH is the only "
          "method listed for exchanging AES-256 key-encryption keys.")])

WORKING = iface(
    "service:kt-working-keys", "Import and export of working keys in key blocks",
    [prop("interfaceType", "interconnect"),
     prop("protocol", "ANSI X9.143 key block"),
     unknown("protocolVersion"),
     prop("endpointRole:initiator", "endpoint:partner-hsm"),
     prop("endpointRole:responder", "endpoint:aws-payment-cryptography"),
     prop("correspondsTo", "no-product-document"),
     prop("keyExchange", "none"),
     prop("encryption", "TDEA-2KEY, TDEA-3KEY, AES-128, AES-192, AES-256"),
     prop("authentication", "none"),
     unknown("implementationPurl"),
     prop("integrationConstraints",
          "Working keys are exchanged as TR-31 or ANSI X9.143 key blocks under a key-encryption key that "
          "was exchanged first. The key block binds each key to its usage. Triple DES is still accepted, "
          "for compatibility with counterparties.")])

STORE = iface(
    "service:sto-payment-keys", "Storage of payment keys in the service's HSMs",
    [prop("interfaceType", "storage"),
     prop("correspondsTo", "no-product-document"),
     prop("encryption", "AES-256"),
     prop("keyWrapping", "AES-256"),
     unknown("implementationPurl"),
     prop("keyCustodySupported", "provider-managed"),
     prop("keyCustody", "provider-managed"),
     prop("storageRegion", "the AWS Region in which each key was created"),
     prop("integrationConstraints",
          "Keys are held in TR-31 key blocks protected by AES-256 main keys in the service's HSMs, which "
          "meet the PCI PTS HSM requirements (foundations page). A key exists in a single AWS Region "
          "(terminology page). A customer can import its own keys, but the service always holds them "
          "under its own main keys, so custody is provider-managed.")])

INTERFACES = [API_TLS, CONTROL, DATA, KEK_TR34, KEK_ECDH, WORKING, STORE]

bom = {
    "specFormat": "CycloneDX",
    "specVersion": "2.0",
    "$comment": ("Worked example for the financial services domain draft (chapter 11). AWS Payment Cryptography "
                 "as a service record, written by the PKI Consortium CBOM Profiles Working Group from the "
                 "provider's public documentation, read on 26 November 2026. Not reviewed by the provider. "
                 "Facts the documentation does not state are marked unknown. Built by "
                 "drafts/fs-payment-cryptography-service/build.py."),
    "serialNumber": "urn:uuid:5e1c0a77-0000-4000-8000-0000000f5001",
    "version": 1,
    "metadata": {
        "timestamp": "2026-11-26T12:00:00Z",
        "lifecycles": [{"phase": "operations"}],
        "tools": {"components": [{"type": "application", "name": "Manual reading of public documentation",
                                  "version": "1.0",
                                  "description": "Pages listed in the externalReferences of type documentation"}]},
        "supplier": {"name": "Amazon Web Services (provider of the service described)"},
    },
    "inventories": [{
        "bom-ref": "inventory:subject",
        "subject": {
            "type": "application",
            "bom-ref": "service:aws-payment-cryptography",
            "name": "AWS Payment Cryptography",
            "description": "Managed payment HSM service: payment key management and payment cryptographic operations.",
            "properties": [
                prop("subjectType", "service"),
                prop("coverage", "all-external"),
                prop("serviceRegions", "every AWS Region where the service is offered; the list is not reproduced"),
                prop("regenerationTrigger", "interface-change"),
            ],
            "identifiers": [{"party": "party:document-author", "identities": [{
                "scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."},
                "value": "tag:pkic.org,2026:example/aws-payment-cryptography"}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}],
                         "organization": {"name": "PKI Consortium CBOM Profiles Working Group"}}],
        },
        "components": INTERFACES,
    }],
    "dependencies": [{"ref": "service:aws-payment-cryptography",
                      "dependsOn": [i["bom-ref"] for i in INTERFACES]}],
    "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}],
    "externalReferences": (
        [{"type": "documentation", "url": u, "comment": "Source: AWS Payment Cryptography user guide (%s)." % k}
         for k, u in SOURCES.items()]
        + [{"type": "release-notes", "url": "https://aws.amazon.com/about-aws/whats-new/",
            "comment": "Where AWS announces changes to its services.",
            "properties": [{"name": "pkic:profile:context", "value": "change-notice"}]},
           {"type": "advisories", "url": "https://aws.amazon.com/security/security-bulletins/",
            "comment": "Where AWS publishes security bulletins.",
            "properties": [{"name": "pkic:profile:context", "value": "vulnerability-statements"}]}]),
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(bom, f, indent=2)
    f.write("\n")
print("wrote", os.path.relpath(OUT))
