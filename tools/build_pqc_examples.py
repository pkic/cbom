#!/usr/bin/env python3
"""PQC migration examples beyond Keycloak.

Two product records at lifecycle stage 'implemented', each written to conform to
interface-enumeration, interface-disclosure, pqc-migration, pqc-migration-extended and
procurement, and a set of failure variants derived from them. Each failure variant removes or
breaks one attribute, so that it fails exactly one MUST rule of one profile.

1. OpenSSH 10.0p2 (portable), the SSH server. Post-quantum key establishment is shipped and on
   by default: OpenSSH 10.0 made the hybrid mlkem768x25519-sha256 the default key agreement.
   Signatures are still classical. Written by the working group from the public release notes
   and manual pages. Not built or run: values that depend on the build are marked to confirm
   against 'sshd -T' on the target.
2. ExampleGate 4.2, an IPsec VPN gateway from a fictional supplier (Example Networks). It
   shows the opposite position: post-quantum key establishment arrives by a software update,
   its keys live in an embedded HSM, the cryptographic module is FIPS 140-3 validated, and the
   new algorithm is outside the validated boundary until the module is revalidated. Every
   identifier, version and certificate number in it is invented.

Writes to docs/methodology/examples/ and docs/methodology/examples/context/.

Usage: python3 tools/build_pqc_examples.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "methodology", "examples")
CONTEXT = os.path.join(OUT, "context")
P = "pkic:profile:"
STAMP = "2026-11-26T09:00:00Z"
AUTHOR = {"name": "PKI Consortium CBOM Profiles Working Group (worked example)",
          "url": [{"name": "website", "url": "https://pkic.org"}]}
PURPOSES = ["key-establishment", "encryption", "entity-authentication", "data-integrity",
            "non-repudiation", "key-protection", "key-derivation"]


# ------------------------------------------------------------------ helpers ---
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


def purpose(name, status, blocked=None, validated=None, roadmap=None, verifiers=None, trust=None):
    """One entry of the capabilityByPurpose group (pqc-migration G1)."""
    pre = "capabilityByPurpose:%s:" % name
    out = [(pre + "capabilityStatus", status)]
    if blocked:
        out.append((pre + "blockedBy", blocked))
    if validated:
        out.append((pre + "validatedModeAvailability", validated))
    if roadmap:
        out.append((pre + "roadmapRef", roadmap))
    if verifiers:
        out.append((pre + "verifierPopulation", verifiers))
    if trust:
        out.append((pre + "trustDomain", trust))
    return out


def guidance(url, comment):
    return [{"type": "documentation", "url": url, "comment": comment,
             "properties": props([("context", "configuration-guidance"), ("accessProtocol", "web-page")])}]


def iface(ref, name, kind, pairs, state="enabled", refs=None, endpoints=None):
    c = {"type": "service", "bom-ref": ref, "name": name,
         "properties": props([("interfaceType", kind)] + pairs + [("defaultState", state)])}
    if endpoints:
        c["endpoints"] = endpoints
    if refs:
        c["externalReferences"] = refs
    return c


def subject(kind, ref, name, version, licence, description, purl, supplier, extra):
    s = {"type": kind, "bom-ref": ref, "name": name, "version": version,
         "description": description, "properties": extra, "identifiers": ident(purl),
         "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}], "organization": AUTHOR},
                     {"bom-ref": "party:supplier", "roles": [{"role": "supplier"}], "organization": supplier}]}
    if licence:
        s["licenses"] = [{"license": {"id": licence}}]
    return s


def document(serial, comment, subj, components, dependencies, references):
    return {"specFormat": "CycloneDX", "specVersion": "2.0", "$comment": comment,
            "serialNumber": "urn:uuid:" + serial, "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subj, "components": components}],
            "dependencies": dependencies,
            "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
            "externalReferences": references}


def sbom(serial, comment, subj, libs):
    return {"specFormat": "CycloneDX", "specVersion": "2.0", "$comment": comment,
            "serialNumber": "urn:uuid:" + serial, "version": 1,
            "metadata": {"timestamp": STAMP, "lifecycles": [{"phase": "build"}],
                         "supplier": {"name": AUTHOR["name"], "url": ["https://pkic.org"]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subj, "components": libs}],
            "compositions": [{"kind": "components", "aggregate": "incomplete", "targets": ["inventory:subject"]}]}


def sbom_ref(serial, file, digest):
    return {"type": "bom", "url": "urn:cdx:%s/1" % serial, "comment": "Companion SBOM: examples/context/%s." % file,
            "properties": props([("context", "sbom")]), "hashes": [{"alg": "SHA-256", "content": digest}]}


# ------------------------------------------------------------------ OpenSSH ---
SSH = {"product": "0a55e100-0000-4000-8000-100000000001", "sbom": "0a55e100-0000-4000-8000-1000000000b0"}
# Portable 10.0 was released as 10.0p2 by mistake (it was meant to be 10.0p1), and no 10.0p1 was
# made. A generic purl avoids guessing which tag or tarball name a consumer will see.
SSH_PURL = "pkg:generic/openssh-portable@10.0p2"
SSH_VERSION = "10.0p2"
OPENSSL_PURL = "pkg:github/openssl/openssl@openssl-3.5.4"
MAN = "https://man.openbsd.org/sshd_config"

# sshd 10.0 default KexAlgorithms. The 10.0 release notes remove the diffie-hellman-group* and
# diffie-hellman-group-exchange-* methods from the server's default list. To confirm with 'sshd -T'.
SSH_KEX = ["mlkem768x25519-sha256", "sntrup761x25519-sha512", "sntrup761x25519-sha512@openssh.com",
           "curve25519-sha256", "curve25519-sha256@libssh.org", "ecdh-sha2-nistp256", "ecdh-sha2-nistp384",
           "ecdh-sha2-nistp521"]
# Host key and public key signature algorithms. DSA support was removed in OpenSSH 10.0.
SSH_SIG = ["ssh-ed25519", "ecdsa-sha2-nistp256", "ecdsa-sha2-nistp384", "ecdsa-sha2-nistp521",
           "sk-ssh-ed25519@openssh.com", "sk-ecdsa-sha2-nistp256@openssh.com", "rsa-sha2-512", "rsa-sha2-256"]

SSH_MIGRATION = ([("enablementMethod", "already-enabled"), ("executionEnvironment", "software"),
                  ("transitionMode", "side-by-side"), ("moduleValidationScheme", "none"),
                  ("certificationImpact", "not-applicable")]
                 + purpose("key-establishment", "available", validated="no-validated-mode")
                 + purpose("encryption", "available", validated="no-validated-mode")
                 + purpose("data-integrity", "available", validated="no-validated-mode")
                 + purpose("key-derivation", "available", validated="no-validated-mode")
                 # Host keys are checked by each client against its own known_hosts file, and user
                 # keys by the server against authorized_keys: one counterparty, no shared scheme.
                 + purpose("entity-authentication", "under-evaluation", blocked="standard",
                           verifiers="counterparty", trust="private")
                 + purpose("non-repudiation", "not-planned", blocked="product",
                           verifiers="counterparty", trust="private")
                 + purpose("key-protection", "not-planned", blocked="product"))


def ssh_interfaces():
    return [
        iface("ssh-transport", "SSH transport layer (sshd, port 22)", "service", [
            ("protocol", "SSH"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:ssh-client"), ("endpointRole:server", "endpoint:sshd"),
            # In SSH the client's preference order decides the key exchange and the cipher, among
            # those the server allows. The host key is generated or supplied by the operator.
            ("keyExchange", "peer-defined"), ("encryption", "peer-defined"),
            ("authentication", "deployment-defined"),
            ("implementingLibrary", SSH_PURL),
            ("protocolVersionsSupported", "2.0"), ("keyExchangeSupported", SSH_KEX),
            ("authenticationSupported", SSH_SIG),
            ("algorithmSelection", "KexAlgorithms, Ciphers, MACs and HostKeyAlgorithms in sshd_config."),
            ("integrationConstraints", "The client's preference decides the key exchange. OpenSSH clients from "
                                       "10.0 choose mlkem768x25519-sha256 by default, and sshd offers it from 9.9. "
                                       "A client older than 9.0 negotiates a classical key exchange."),
            ("integrationConstraints", "Finite-field Diffie-Hellman methods are no longer offered by default; "
                                       "an operator can add them back in KexAlgorithms for old clients."),
            ("integrationConstraints", "No post-quantum signature algorithm is available for host keys or user "
                                       "keys."),
            ("keysStoredIn", "sto-hostkeys"),
            ("trustServiceDependencies", "random-bit-generator"),
            ("terminatedBy", "workload")] + SSH_MIGRATION,
            refs=guidance(MAN, "Where the operator sets HostKey, KexAlgorithms, Ciphers, MACs and "
                               "HostKeyAlgorithms."),
            endpoints=["ssh://{host}:22"]),
        iface("ssh-userauth", "SSH public key user authentication", "service", [
            ("protocol", "SSH user authentication (RFC 4252)"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:ssh-client"), ("endpointRole:server", "endpoint:sshd"),
            # Carried inside the transport layer: no key exchange or encryption of its own.
            ("keyExchange", "none"), ("encryption", "none"), ("authentication", "peer-defined"),
            ("implementingLibrary", SSH_PURL),
            ("protocolVersionsSupported", "2.0"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", SSH_SIG),
            ("algorithmSelection", "PubkeyAcceptedAlgorithms and AuthorizedKeysFile in sshd_config."),
            ("integrationConstraints", "Carried over ssh-transport."),
            ("keysStoredIn", "out-of-band"),
            ("trustServiceDependencies", "none"),
            ("terminatedBy", "workload")] + SSH_MIGRATION),
        iface("sto-hostkeys", "Host private keys (/etc/ssh/ssh_host_*_key)", "storage", [
            ("encryption", "none"), ("keyWrapping", "none"), ("keyWrappingSupported", "none"),
            ("implementingLibrary", SSH_PURL),
            ("algorithmSelection", "Not applicable: nothing is negotiated at a file store."),
            ("integrationConstraints", "Host keys are unencrypted files readable only by root. 'ssh-keygen -A' "
                                       "generates any missing default host key type at installation."),
            ("keysStoredIn", "product-managed"),
            ("trustServiceDependencies", "none")] + SSH_MIGRATION,
            endpoints=["file:///etc/ssh/"]),
    ]


def ssh_subject(extra):
    return subject("application", "app:openssh", "OpenSSH (portable)", SSH_VERSION, "BSD-2-Clause",
                   "The OpenSSH server, sshd, from the portable release " + SSH_VERSION + ", linked to OpenSSL "
                   "libcrypto. Described from the release notes and manual pages by the working group, not by "
                   "the OpenSSH developers.",
                   SSH_PURL, {"name": "OpenSSH project", "url": [{"name": "website", "url": "https://www.openssh.com"}]},
                   extra)


def ssh_product(sbom_digest):
    extra = props([("coverage", "all-external"), ("subjectType", "product"),
                   ("absent:management-interface", "configured-out-of-band"),
                   ("productCertificationScheme", "none"),
                   ("absent:vulnerability-statements", "not-published"),
                   ("absent:support-lifecycle", "not-published"),
                   ("absent:roadmap", "not-published")])
    comps = [{"type": "library", "bom-ref": "lib:openssl", "name": "OpenSSL libcrypto", "version": "3.5.4",
              "identifiers": ident(OPENSSL_PURL)}] + ssh_interfaces()
    deps = [{"ref": "app:openssh", "dependsOn": ["lib:openssl", "ssh-transport", "ssh-userauth", "sto-hostkeys"]},
            {"ref": "ssh-userauth", "dependsOn": ["ssh-transport"]},
            {"ref": "ssh-transport", "dependsOn": ["sto-hostkeys"]}]
    refs = [sbom_ref(SSH["sbom"], "openssh-10.0p2-sbom.cdx.json", sbom_digest),
            {"type": "advisories", "url": "https://www.openssh.com/security.html",
             "comment": "OpenSSH security advisories.",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "security-contact", "url": "https://www.openssh.com/report.html",
             "comment": "How to report a security problem to the OpenSSH developers.",
             "properties": props([("context", "security-contact"), ("accessProtocol", "web-page")])},
            {"type": "release-notes", "url": "https://www.openssh.com/txt/release-10.0",
             "comment": "Release notes: the client uses mlkem768x25519-sha256 by default; DSA is removed; sshd drops "
                        "finite-field Diffie-Hellman from its default key exchange list."}]
    comment = ("EXAMPLE CBOM, lifecycle stage 'implemented'. OpenSSH " + SSH_VERSION + " (portable) server at "
               "its defaults: post-quantum hybrid key establishment shipped and enabled, signatures classical. "
               "Real values from public sources; not built, and not reviewed by the OpenSSH developers. The "
               "configuration is a file the operator edits, so the product declares its management interface "
               "absent as 'configured-out-of-band'.")
    return document(SSH["product"], comment, ssh_subject(extra), comps, deps, refs)


def ssh_sbom():
    return sbom(SSH["sbom"], "EXAMPLE SBOM for OpenSSH " + SSH_VERSION + ". Lists only the library the CBOM "
                "names, so its composition is incomplete.", ssh_subject([]),
                [{"type": "library", "bom-ref": "lib:openssl", "name": "OpenSSL libcrypto", "version": "3.5.4",
                  "identifiers": ident(OPENSSL_PURL)}])



# -------------------------------------------------------------- ExampleGate ---
# A fictional IPsec VPN gateway. Supplier, product, versions, URLs and certificate numbers are
# invented; example.com is reserved for documentation (RFC 2606).
GATE_SERIAL = {"4.2.0": ("e8a7e000-0000-4000-8000-420000000001", "e8a7e000-0000-4000-8000-4200000000b0"),
               "4.3.0": ("e8a7e000-0000-4000-8000-430000000001", "e8a7e000-0000-4000-8000-4300000000b0")}
GATE_DOCS = "https://docs.example.com/examplegate/"
MODULE_REF = ("FIPS 140-3 certificate EXAMPLE-0001 (fictional) for the ExampleGate Cryptographic Module 2.1, "
              "embedded HSM")
GATE_IKE_KEX = ["ECP-256 (group 19)", "ECP-384 (group 20)", "Curve25519 (group 31)", "MODP-2048 (group 14)",
                "MODP-3072 (group 15)"]
GATE_PQ_KEX = ["ML-KEM-768 (additional key exchange, RFC 9370)", "ML-KEM-1024 (additional key exchange, RFC 9370)"]
GATE_SIG = ["ECDSA-P256-SHA256", "ECDSA-P384-SHA384", "RSA-PSS-SHA256", "RSA-PKCS1-1.5-SHA256", "PSK"]
GATE_TLS_GROUPS = ["x25519", "secp256r1", "secp384r1"]
GATE_TLS_SIG = ["ecdsa_secp256r1_sha256", "ecdsa_secp384r1_sha384", "rsa_pss_rsae_sha256"]


def gate_module(version):
    """The embedded HSM that implements every interface. Migration facts sit here and each
    interface inherits them through 'provides', as the Keycloak example does with its JDK."""
    pq = version == "4.3.0"
    pairs = [("executionEnvironment", "hsm"), ("transitionMode", "side-by-side"),
             ("moduleValidationScheme", "fips-140-3"), ("moduleValidationRef", MODULE_REF)]
    if pq:
        pairs += [("enablementMethod", "configuration")]
        pairs += purpose("key-establishment", "available", validated="outside-validated-mode-only",
                         roadmap=GATE_DOCS + "pqc-roadmap")
    else:
        pairs += [("enablementMethod", "software-update"), ("availableFromVersion", "4.3.0")]
        pairs += purpose("key-establishment", "committed", blocked="product",
                         roadmap=GATE_DOCS + "pqc-roadmap")
    pairs += (purpose("encryption", "available", validated="in-validated-mode")
              + purpose("data-integrity", "available", validated="in-validated-mode")
              + purpose("key-derivation", "available", validated="in-validated-mode")
              # Keys at rest are wrapped with AES-256 inside the HSM: already quantum-resistant.
              + purpose("key-protection", "available", validated="in-validated-mode")
              + purpose("entity-authentication", "planned", blocked="standard", roadmap=GATE_DOCS + "pqc-roadmap",
                        verifiers="counterparty", trust="private")
              + purpose("non-repudiation", "not-planned", blocked="product", verifiers="counterparty",
                        trust="private"))
    return {"type": "library", "bom-ref": "lib:egcm", "name": "ExampleGate Cryptographic Module (embedded HSM)",
            "version": "2.1", "identifiers": ident("pkg:generic/example-networks/egcm@2.1"),
            "properties": props(pairs)}


def gate_interfaces(version):
    pq = version == "4.3.0"
    enable = [("enablementSetting", "crypto ike proposal <name> additional-key-exchange mlkem768")] if pq else []
    tls_enable = [("enablementSetting", "system tls groups x25519mlkem768,x25519,secp256r1")] if pq else []
    # Enabling ML-KEM changes what the validated module runs, so it costs a recertification in 4.3.0.
    # In 4.2.0 nothing changes yet.
    cert = ([("certificationImpact", "recertification"), ("impactedCertification", "FIPS 140-3")] if pq
            else [("certificationImpact", "none")])
    esp_enable = [("enablementSetting", "None of its own: ESP keys are derived in the IKE SA, so enabling ML-KEM "
                                        "on ike protects them.")] if pq else []
    return [
        iface("ike", "IKEv2 key exchange (UDP 500 and 4500)", "service", [
            ("protocol", "IKEv2"), ("protocolVersion", "2"),
            ("endpointRole:initiator", "endpoint:remote-peer"), ("endpointRole:responder", "endpoint:examplegate"),
            ("keyExchange", "deployment-defined"), ("encryption", "deployment-defined"),
            ("authentication", "deployment-defined"),
            ("protocolVersionsSupported", "2"),
            ("keyExchangeSupported", GATE_IKE_KEX + (GATE_PQ_KEX if pq else [])),
            ("authenticationSupported", GATE_SIG),
            ("algorithmSelection", "IKE proposals in the gateway configuration: one ordered list of transforms "
                                   "per tunnel."),
            ("integrationConstraints", "The peer must support RFC 9370 additional key exchanges for ML-KEM to be "
                                       "negotiated; otherwise the tunnel falls back to the classical group."
             if pq else "No post-quantum key exchange in this release. ML-KEM arrives in 4.3.0."),
            ("integrationConstraints", "Fragmentation (RFC 7383) is on by default, because ML-KEM key shares make "
                                       "IKE_INTERMEDIATE messages larger than a typical path MTU."
             if pq else "IKEv1 is not supported."),
            ("keysStoredIn", "sto-hsm"),
            ("trustServiceDependencies", ["certificate-authority", "revocation-responder", "time-source"]),
            ("terminatedBy", "workload")] + enable + cert,
            refs=guidance(GATE_DOCS + version + "/ike-proposals",
                          "Where the operator sets the IKE proposals, the tunnel certificates and pre-shared keys."),
            endpoints=["udp://{gateway}:500", "udp://{gateway}:4500"]),
        iface("esp", "ESP tunnel traffic", "service", [
            ("protocol", "ESP"), ("protocolVersion", "RFC 4303"),
            ("endpointRole:initiator", "endpoint:remote-peer"), ("endpointRole:responder", "endpoint:examplegate"),
            # Keys come from the IKE SA; ESP has no key exchange or peer authentication of its own.
            ("keyExchange", "none"), ("encryption", "deployment-defined"), ("authentication", "none"),
            ("protocolVersionsSupported", "RFC 4303"), ("keyExchangeSupported", "none"),
            ("authenticationSupported", "none"),
            ("algorithmSelection", "ESP proposals in the gateway configuration, per tunnel."),
            ("integrationConstraints", "Keyed by ike."),
            ("keysStoredIn", "sto-hsm"),
            ("trustServiceDependencies", "none"),
            ("terminatedBy", "workload")] + esp_enable + cert,
            refs=guidance(GATE_DOCS + version + "/esp-proposals", "Where the operator sets the ESP proposals.")),
        iface("mgmt-https", "Management web interface and REST API (HTTPS, port 443)", "management", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:administrator", "endpoint:admin-browser"), ("endpointRole:server", "endpoint:examplegate"),
            ("keyExchange", "deployment-defined"), ("encryption", "deployment-defined"),
            ("authentication", "deployment-defined"),
            ("protocolVersionsSupported", ["1.2", "1.3"]),
            ("keyExchangeSupported", GATE_TLS_GROUPS + (["X25519MLKEM768"] if pq else [])),
            ("authenticationSupported", GATE_TLS_SIG),
            ("algorithmSelection", "TLS versions, cipher suites and groups under 'system tls'."),
            ("integrationConstraints", "Administrators authenticate with a client certificate or with a password "
                                       "and a one-time code."),
            ("managesKeys", "yes"),
            ("keyOperations", ["generate", "import", "request-certificate", "rotate", "zeroize"]),
            ("keyTypesSupported", ["RSA-2048", "RSA-3072", "ECDSA-P256", "ECDSA-P384"]),
            ("keyTypes", "ECDSA-P256"),
            ("keyStoreFormatsSupported", ["pkcs12", "pem", "token-native"]),
            ("keyStoreFormats", "token-native"),
            ("keyStoreLocation", "hsm"),
            ("trustServiceDependencies", ["certificate-authority", "revocation-responder", "time-source"]),
            ("terminatedBy", "workload")] + tls_enable + cert,
            refs=guidance(GATE_DOCS + version + "/management-tls",
                          "Where the operator sets the management certificate and the TLS settings."),
            endpoints=["https://{gateway}/"]),
        iface("sto-hsm", "Key store in the embedded HSM", "storage", [
            ("encryption", "AES-256-GCM"), ("keyWrapping", "AES-256-KWP"),
            ("keyWrappingSupported", ["AES-256-KWP"]),
            ("algorithmSelection", "Not applicable: nothing is negotiated at the key store."),
            ("integrationConstraints", "Private keys are generated in the HSM and cannot be exported in the clear. "
                                       "A backup leaves the HSM wrapped under a key-encryption key held on a "
                                       "smart card."),
            ("keysStoredIn", "product-managed"),
            # AES-256 key wrapping needs no change for post-quantum security.
            ("enablementMethod", "already-enabled"),
            ("certificationImpact", "none"),
            ("trustServiceDependencies", "none")]),
    ]


def gate_subject(version, extra):
    return subject("device", "dev:examplegate", "ExampleGate", version, None,
                   "ExampleGate %s, an IPsec VPN gateway appliance from Example Networks. Fictional: written by the "
                   "working group to show a validated module and a post-quantum update." % version,
                   "pkg:generic/example-networks/examplegate@" + version,
                   {"name": "Example Networks (fictional)", "url": [{"name": "website", "url": "https://example.com"}]},
                   extra)


def gate_product(version, sbom_digest):
    serial, sbom_serial = GATE_SERIAL[version]
    extra = props([("coverage", "all"), ("subjectType", "product"), ("productCertificationScheme", "common-criteria")])
    comps = [gate_module(version)] + gate_interfaces(version)
    deps = [{"ref": "dev:examplegate", "dependsOn": ["lib:egcm", "ike", "esp", "mgmt-https", "sto-hsm"]},
            {"ref": "lib:egcm", "provides": ["ike", "esp", "mgmt-https", "sto-hsm"]},
            {"ref": "esp", "dependsOn": ["ike"]}]
    refs = [sbom_ref(sbom_serial, "examplegate-%s-sbom.cdx.json" % version, sbom_digest),
            {"type": "vulnerability-assertion", "url": "https://example.com/.well-known/csaf/provider-metadata.json",
             "comment": "The supplier's CSAF provider, which publishes VEX documents for each release (fictional).",
             "properties": props([("context", "vulnerability-statements"), ("accessProtocol", "csaf-provider")])},
            {"type": "advisories", "url": "https://example.com/security/advisories",
             "properties": props([("context", "advisories"), ("accessProtocol", "web-page")])},
            {"type": "rfc-9116", "url": "https://example.com/.well-known/security.txt",
             "properties": props([("context", "security-contact"), ("accessProtocol", "other")])},
            {"type": "support", "url": "https://example.com/examplegate/support-lifecycle",
             "comment": "End-of-sale and end-of-support dates for each release.",
             "properties": props([("context", "support-lifecycle"), ("accessProtocol", "web-page")])},
            {"type": "documentation", "url": GATE_DOCS + "pqc-roadmap",
             "comment": "Post-quantum roadmap: ML-KEM for IKEv2 and management TLS in 4.3.0; module revalidation; "
                        "ML-DSA authentication once IKEv2 signatures are standardised.",
             "properties": props([("context", "roadmap"), ("accessProtocol", "web-page")])}]
    if version == "4.3.0":
        comment = ("EXAMPLE CBOM, lifecycle stage 'implemented'. FICTIONAL product. ExampleGate 4.3.0: ML-KEM is "
                   "in the release and is switched on by configuration. It runs in the embedded HSM but outside "
                   "the module's FIPS 140-3 validated boundary until the module is revalidated, so the record "
                   "answers 'outside-validated-mode-only' for key establishment and 'recertification' for the "
                   "certification impact. Compare with the 4.2.0 record.")
    else:
        comment = ("EXAMPLE CBOM, lifecycle stage 'implemented'. FICTIONAL product. ExampleGate 4.2.0: no "
                   "post-quantum key establishment. The supplier has committed to ML-KEM in 4.3.0, so the record "
                   "answers 'software-update' with a minimum product version. Everything the gateway does runs in "
                   "a FIPS 140-3 validated embedded HSM.")
    return document(serial, comment, gate_subject(version, extra), comps, deps, refs)


def gate_sbom(version):
    return sbom(GATE_SERIAL[version][1], "EXAMPLE SBOM for the fictional ExampleGate %s. Lists only the module the "
                "CBOM names, so its composition is incomplete." % version, gate_subject(version, []),
                [{"type": "library", "bom-ref": "lib:egcm", "name": "ExampleGate Cryptographic Module",
                  "version": "2.1", "identifiers": ident("pkg:generic/example-networks/egcm@2.1")}])



# --------------------------------------------------------- failure variants ---
def _components(bom):
    return {c["bom-ref"]: c for c in bom["inventories"][0]["components"]}


def drop(ref, *names):
    """Remove every property of one component whose name is, or starts with, one of names."""
    def edit(bom):
        c = _components(bom)[ref]
        c["properties"] = [p for p in c["properties"]
                           if not any(p["name"] == P + n or p["name"].startswith(P + n + ":") for n in names)]
    return edit


def set_value(ref, name, value):
    def edit(bom):
        props_ = bom["inventories"][0]["subject"]["properties"] if ref is None else _components(bom)[ref]["properties"]
        for p in props_:
            if p["name"] == P + name:
                p["value"] = value
    return edit


def remove_component(ref):
    def edit(bom):
        inv = bom["inventories"][0]
        inv["components"] = [c for c in inv["components"] if c["bom-ref"] != ref]
        for d in bom["dependencies"]:
            d["dependsOn"] = [r for r in d.get("dependsOn", []) if r != ref]
            if d.get("provides"):
                d["provides"] = [r for r in d["provides"] if r != ref]
        for c in inv["components"]:
            for p in c.get("properties", []):
                if p["name"] == P + "keysStoredIn" and p["value"] == ref:
                    p["value"] = "out-of-band"
    return edit


# (base file, variant suffix, what the variant breaks, edit). Each fails exactly one MUST rule
# of one profile; tests/check-examples.py holds the expected verdicts.
SSH_FILE = "cbom-openssh-10.0p2-product.cdx.json"
G42 = "cbom-examplegate-4.2.0-product.cdx.json"
G43 = "cbom-examplegate-4.3.0-product.cdx.json"
VARIANTS = [
    (SSH_FILE, "fail-pqc-I1", "ssh-transport states no supported protocol versions",
     drop("ssh-transport", "protocolVersionsSupported")),
    (SSH_FILE, "fail-pqc-I2", "ssh-transport states no supported key exchange algorithms",
     drop("ssh-transport", "keyExchangeSupported")),
    (SSH_FILE, "fail-pqc-I3", "ssh-userauth states no supported authentication algorithms",
     drop("ssh-userauth", "authenticationSupported")),
    (SSH_FILE, "fail-pqc-I4", "ssh-transport does not say how post-quantum algorithms are enabled",
     drop("ssh-transport", "enablementMethod")),
    (SSH_FILE, "fail-pqc-I6", "ssh-transport does not say where its cryptography runs",
     drop("ssh-transport", "executionEnvironment")),
    (SSH_FILE, "fail-pqc-I7", "ssh-transport answers transitionMode with 'hybrid', which is not in the vocabulary",
     set_value("ssh-transport", "transitionMode", "hybrid")),
    (SSH_FILE, "fail-pqc-I10", "ssh-transport does not state a module validation scheme",
     drop("ssh-transport", "moduleValidationScheme")),
    (SSH_FILE, "fail-pqc-G1", "sto-hostkeys gives no status for the key-protection purpose",
     drop("sto-hostkeys", "capabilityByPurpose:key-protection")),
    (SSH_FILE, "fail-ext-P1", "the host key store is left out, and no reason is given",
     remove_component("sto-hostkeys")),
    (SSH_FILE, "fail-ext-I9", "ssh-userauth does not state its external dependencies",
     drop("ssh-userauth", "trustServiceDependencies")),
    (SSH_FILE, "fail-procurement-P2", "the coverage is 'partial', which a tender response may not answer",
     set_value(None, "coverage", "partial")),
    (G42, "fail-pqc-I5", "the update path names no minimum product version",
     drop("lib:egcm", "availableFromVersion")),
    (G43, "fail-pqc-I11", "a FIPS 140-3 module is claimed with no certificate reference",
     drop("lib:egcm", "moduleValidationRef")),
    (G43, "fail-ext-I1", "mgmt-https does not say whether it manages keys",
     drop("mgmt-https", "managesKeys")),
    (G43, "fail-ext-I2", "mgmt-https manages keys but lists no key operations",
     drop("mgmt-https", "keyOperations")),
    (G43, "fail-ext-I4", "mgmt-https lists the key types it supports but not the ones it uses",
     drop("mgmt-https", "keyTypes")),
    (G43, "fail-ext-I7", "mgmt-https manages keys but does not say where they are stored",
     drop("mgmt-https", "keyStoreLocation")),
]


def variant_name(base, suffix):
    return base.replace(".cdx.json", "-%s.cdx.json" % suffix)


def write_variants():
    for i, (base, suffix, what, edit) in enumerate(VARIANTS, 1):
        bom = json.load(open(os.path.join(OUT, base), encoding="utf-8"))
        bom = copy.deepcopy(bom)
        edit(bom)
        # A variant is a different document, so it gets its own serial number.
        bom["serialNumber"] = bom["serialNumber"][:-4] + "f%03d" % i
        bom["$comment"] = ("NON-CONFORMING EXAMPLE, derived from %s. It breaks one thing: %s. "
                           "Everything else is unchanged." % (base, what))
        write(variant_name(base, suffix), bom)


# ------------------------------------------------------------------- main ---
def main():
    os.makedirs(CONTEXT, exist_ok=True)
    h = write("openssh-10.0p2-sbom.cdx.json", ssh_sbom(), CONTEXT)
    write("cbom-openssh-10.0p2-product.cdx.json", ssh_product(h))
    for version in ("4.2.0", "4.3.0"):
        h = write("examplegate-%s-sbom.cdx.json" % version, gate_sbom(version), CONTEXT)
        write("cbom-examplegate-%s-product.cdx.json" % version, gate_product(version, h))
    write_variants()
    print("written to", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
