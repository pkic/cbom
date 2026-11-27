#!/usr/bin/env python3
"""Deployment and system records built on the PQC migration product examples.

The product records come from tools/build_pqc_examples.py; run that first. This script writes:

1. bastion.example.org, an SSH bastion running OpenSSH 10.0p2, as configured by its operator.
   The operator allows only the two hybrid post-quantum key exchanges, so a client that cannot
   do them cannot connect.
2. The same bastion as observed by an active scan a week later. The scan finds that a change
   has put curve25519-sha256 back in the list: the drift between the two records is the
   finding the pair exists to show.
3. vpn.example.org, a remote-access VPN on the fictional ExampleGate 4.3.0, as configured, with
   ML-KEM-768 as an additional IKEv2 key exchange.
4. A remote administration access system: the reference design that joins the VPN gateway and
   the bastion, as the integrator delivers it. It cites both product records and lists every
   interface of each, with its usage and the component that provides its keys.

All names, addresses and repositories are invented (example.org, example.com). Each record has
failure variants that break one thing; tests/check-examples.py holds the expected verdicts.

Usage: python3 tools/build_pqc_deployment_examples.py
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_pqc_examples as B  # noqa: E402

OUT, CONTEXT, P, props = B.OUT, B.CONTEXT, B.P, B.props
STAMP_CONF = "2026-11-20T10:00:00Z"
STAMP_OBS = "2026-11-27T08:30:00Z"
OPERATOR = {"name": "Example Org platform team (fictional)", "url": [{"name": "website", "url": "https://example.org"}]}
INTEGRATOR = {"name": "Example Integrator (fictional)", "url": [{"name": "website", "url": "https://integrator.example"}]}
SERIAL = {"bastion-conf": "ba571000-0000-4000-8000-c00000000001",
          "bastion-obs": "ba571000-0000-4000-8000-0b0000000001",
          "vpn-conf": "a7900000-0000-4000-8000-c00000000001",
          "sys": "5a5a0000-0000-4000-8000-c00000000001"}


def digest(name):
    with open(os.path.join(OUT, name), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def serial_of(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        bom = json.load(fh)
    return bom["serialNumber"][len("urn:uuid:"):], bom["version"]


def link(name, ref):
    serial, version = serial_of(name)
    return "urn:cdx:%s/%d#%s" % (serial, version, ref)


def cite(name, comment):
    serial, version = serial_of(name)
    return {"type": "bom", "url": "urn:cdx:%s/%d" % (serial, version), "comment": comment,
            "properties": props([("context", "cited-document")]),
            "hashes": [{"alg": "SHA-256", "content": digest(name)}]}


def tag_subject(kind, ref, name, description, tag, subject_type, owner, coverage="all", extra=()):
    return {"type": kind, "bom-ref": ref, "name": name, "description": description,
            "properties": props([("subjectType", subject_type), ("coverage", coverage)] + list(extra)),
            "identifiers": [{"party": "party:document-author", "identities": [
                {"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."}, "value": tag}]}],
            "parties": [{"bom-ref": "party:document-author", "roles": [{"role": "author"}], "organization": owner}]}


def iface(ref, name, kind, pairs, refs=None, endpoints=None):
    c = {"type": "service", "bom-ref": ref, "name": name, "properties": props([("interfaceType", kind)] + pairs)}
    if endpoints:
        c["endpoints"] = endpoints
    if refs:
        c["externalReferences"] = refs
    return c


def doc(serial, comment, stamp, phase, owner, subj, comps, refs):
    return {"specFormat": "CycloneDX", "specVersion": "2.0", "$comment": comment,
            "serialNumber": "urn:uuid:" + serial, "version": 1,
            "metadata": {"timestamp": stamp, "lifecycles": [{"phase": phase}],
                         "supplier": {"name": owner["name"], "url": [owner["url"][0]["url"]]}},
            "inventories": [{"bom-ref": "inventory:subject", "subject": subj, "components": comps}],
            "dependencies": [{"ref": subj["bom-ref"], "dependsOn": [c["bom-ref"] for c in comps]}],
            "compositions": [{"kind": "components", "aggregate": "complete", "targets": ["inventory:subject"]}],
            "externalReferences": refs}


# ------------------------------------------------------------- the bastion ---
SSH = B.SSH_FILE
BASTION_KEX = ["mlkem768x25519-sha256", "sntrup761x25519-sha512"]
BASTION_CIPHERS = ["chacha20-poly1305@openssh.com", "aes256-gcm@openssh.com"]
CONF_REPO = "https://git.example.org/platform/bastion-config/-/commit/9c1d4e7a2b"


def bastion_interfaces(observed):
    kex = BASTION_KEX + (["curve25519-sha256"] if observed else [])
    obs = ([("observationMethod", "active-probe"), ("observedAt", STAMP_OBS)] if observed else [])
    evidence = ([{"type": "evidence", "url": "https://grc.example.org/scans/bastion-2026-11-27.json",
                  "comment": "The scan output: examples/context/bastion-ssh-scan-2026-11-27.json.",
                  "properties": props([("context", "observation-evidence")]),
                  "hashes": [{"alg": "SHA-256", "content": evidence_digest()}]}]
                if observed else None)
    transport = [
        ("protocol", "SSH"), ("protocolVersion", "2.0"),
        ("endpointRole:client", "endpoint:admin-workstation"), ("endpointRole:server", "endpoint:bastion"),
        ("keyExchange", kex), ("encryption", BASTION_CIPHERS), ("authentication", "ssh-ed25519"),
        ("correspondsTo", link(SSH, "ssh-transport")),
        # Administrators' workstations are not in any record this operator holds.
        ("connectsTo", "peer-not-recorded"),
        ("keysStoredIn", "sto-hostkeys"), ("terminatedBy", "workload")]
    transport += ([("integrationConstraints", "KexAlgorithms allows only the two hybrid post-quantum methods. "
                                              "A client older than OpenSSH 9.0 cannot connect.")]
                  if not observed else [])
    return [
        iface("ssh-transport", "SSH on bastion.example.org:22", "service", transport + obs,
              refs=evidence, endpoints=["ssh://bastion.example.org:22"]),
        iface("ssh-userauth", "Administrator public key authentication", "service", [
            ("protocol", "SSH user authentication (RFC 4252)"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:admin-workstation"), ("endpointRole:server", "endpoint:bastion"),
            ("keyExchange", "none"), ("encryption", "none"),
            ("authentication", ["sk-ssh-ed25519@openssh.com", "ssh-ed25519"]),
            ("correspondsTo", link(SSH, "ssh-userauth")),
            ("connectsTo", "peer-not-recorded"),
            ("keysStoredIn", "out-of-band"), ("terminatedBy", "workload")] + obs, refs=evidence),
        iface("sto-hostkeys", "Host key file (/etc/ssh/ssh_host_ed25519_key)", "storage", [
            ("encryption", "none"), ("keyWrapping", "none"),
            ("correspondsTo", link(SSH, "sto-hostkeys")),
            ("integrationConstraints", "Only the Ed25519 host key is configured; the other default types were "
                                       "removed after installation.")] + obs, refs=evidence),
    ]


def evidence_doc():
    return {"$comment": "EXAMPLE scan output for bastion.example.org, abridged. Fictional.",
            "target": "bastion.example.org:22", "scanned": STAMP_OBS, "tool": "ssh-audit",
            "banner": "SSH-2.0-OpenSSH_10.0",
            "kex": BASTION_KEX + ["curve25519-sha256"],
            "hostKeys": ["ssh-ed25519"], "ciphers": BASTION_CIPHERS,
            "note": "curve25519-sha256 is offered although the configured record does not allow it."}


_EVIDENCE = {}


def evidence_digest():
    return _EVIDENCE["digest"]


def bastion(observed):
    subj = tag_subject("application", "deployment:bastion", "bastion.example.org SSH bastion (production)",
                       "OpenSSH 10.0p2 on a hardened Linux virtual machine. The only route for administrators "
                       "into the production network.", "tag:example.org,2026:deployment/bastion",
                       "deployment", OPERATOR,
                       # sshd is configured through a file deployed from the configuration repository.
                       extra=[("absent:management-interface", "configured-out-of-band")])
    refs = [cite(SSH, "The product record of the OpenSSH release this host runs.")]
    if observed:
        refs.append(cite("cbom-bastion-deployment-configured.cdx.json",
                         "The configured record this observation was compared with."))
        refs.append({"type": "vcs", "url": CONF_REPO, "comment": "The configuration revision in force when the "
                                                                "scan ran, according to the deployment log.",
                     "properties": props([("context", "configuration-source")])})
        comment = ("EXAMPLE CBOM, lifecycle stage 'observed'. FICTIONAL deployment. bastion.example.org as an "
                   "active scan saw it on 27 November 2026. The scan finds curve25519-sha256 offered, which the "
                   "configured record does not allow. Compare the two records: the difference is configuration "
                   "drift, and it re-opens a classical key exchange.")
        refs.append({"type": "risk-assessment", "url": "https://grc.example.org/registers/data/bastion",
                     "comment": "What the administrators' sessions carry and how long it must stay confidential.",
                     "properties": props([("context", "data-register")])})
        return doc(SERIAL["bastion-obs"], comment, STAMP_OBS, "discovery", OPERATOR, subj,
                   bastion_interfaces(True), refs)
    refs += [{"type": "vcs", "url": CONF_REPO, "comment": "Revision of the configuration repository this record "
                                                         "was read from.",
              "properties": props([("context", "configuration-source")])},
             {"type": "risk-assessment", "url": "https://grc.example.org/registers/data/bastion",
              "comment": "What the administrators' sessions carry and how long it must stay confidential.",
              "properties": props([("context", "data-register")])}]
    comment = ("EXAMPLE CBOM, lifecycle stage 'configured'. FICTIONAL deployment. bastion.example.org runs "
               "OpenSSH 10.0p2 and allows only hybrid post-quantum key exchange. Each interface points to the "
               "product interface it realises, so the product's capability and this host's choice can be read "
               "side by side.")
    return doc(SERIAL["bastion-conf"], comment, STAMP_CONF, "operations", OPERATOR, subj,
               bastion_interfaces(False), refs)


# ----------------------------------------------------------------- the VPN ---
G43 = B.G43
CA = "https://pki.example.org/cps"


def vpn_interfaces():
    return [
        iface("ike", "IKEv2 on vpn.example.org", "service", [
            ("protocol", "IKEv2"), ("protocolVersion", "2"),
            ("endpointRole:initiator", "endpoint:remote-client"), ("endpointRole:responder", "endpoint:vpn-gateway"),
            ("keyExchange", ["ECP-256 (group 19)", "ML-KEM-768 (additional key exchange, RFC 9370)"]),
            ("encryption", "AES-256-GCM"), ("authentication", "ECDSA-P256-SHA256"),
            ("correspondsTo", link(G43, "ike")),
            ("connectsTo", "peer-not-recorded"),
            ("integrationConstraints", "ML-KEM-768 is required: the proposal has no classical-only fallback. "
                                       "Clients older than the 2026 client release cannot connect."),
            ("keysStoredIn", "sto-hsm"), ("terminatedBy", "workload")],
            endpoints=["udp://vpn.example.org:500", "udp://vpn.example.org:4500"]),
        iface("esp", "ESP tunnels", "service", [
            ("protocol", "ESP"), ("protocolVersion", "RFC 4303"),
            ("endpointRole:initiator", "endpoint:remote-client"), ("endpointRole:responder", "endpoint:vpn-gateway"),
            ("keyExchange", "none"), ("encryption", "AES-256-GCM"), ("authentication", "none"),
            ("correspondsTo", link(G43, "esp")),
            ("connectsTo", "peer-not-recorded"),
            ("keysStoredIn", "sto-hsm"), ("terminatedBy", "workload")]),
        iface("mgmt-https", "Management interface on the management network", "management", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:administrator", "endpoint:bastion"), ("endpointRole:server", "endpoint:vpn-gateway"),
            ("keyExchange", "X25519MLKEM768"), ("encryption", "AES-256-GCM"),
            ("authentication", "ECDSA-P256-SHA256"),
            ("correspondsTo", link(G43, "mgmt-https")),
            # Reached only from the bastion, whose own record describes that end.
            ("connectsTo", link("cbom-bastion-deployment-configured.cdx.json", "ssh-transport")),
            ("keysStoredIn", "sto-hsm"), ("terminatedBy", "workload")],
            endpoints=["https://vpn-mgmt.example.org/"]),
        iface("sto-hsm", "Embedded HSM key store", "storage", [
            ("encryption", "AES-256-GCM"), ("keyWrapping", "AES-256-KWP"),
            ("correspondsTo", link(G43, "sto-hsm"))]),
    ]


def vpn():
    subj = tag_subject("device", "deployment:vpn", "vpn.example.org remote-access VPN (production)",
                       "A pair of ExampleGate 4.3.0 appliances in an active-standby cluster.",
                       "tag:example.org,2026:deployment/vpn", "deployment", OPERATOR)
    refs = [cite(G43, "The product record of the gateway release this cluster runs."),
            cite("cbom-bastion-deployment-configured.cdx.json",
                 "The bastion's configured record: the far end of the management interface."),
            {"type": "vcs", "url": "https://git.example.org/network/vpn-config/-/commit/77e0b13f5c",
             "comment": "Revision of the configuration repository this record was read from.",
             "properties": props([("context", "configuration-source")])},
            {"type": "documentation", "url": CA, "comment": "Certification practice statement of the internal CA "
                                                            "that issues the gateway and client certificates.",
             "properties": props([("context", "certificate-policy"), ("accessProtocol", "web-page")])},
            {"type": "risk-assessment", "url": "https://grc.example.org/registers/data/vpn",
             "comment": "What the tunnels carry and how long it must stay confidential.",
             "properties": props([("context", "data-register")])}]
    comment = ("EXAMPLE CBOM, lifecycle stage 'configured'. FICTIONAL deployment. vpn.example.org runs the "
               "fictional ExampleGate 4.3.0 with ML-KEM-768 required in IKEv2. Its product record says ML-KEM "
               "runs outside the FIPS 140-3 validated boundary, so an operator bound to validated cryptography "
               "would find a conflict by joining the two records.")
    return doc(SERIAL["vpn-conf"], comment, STAMP_CONF, "operations", OPERATOR, subj, vpn_interfaces(), refs)


# -------------------------------------------------------------- the system ---
def system_interfaces():
    def gw(ref, name, kind, pairs, provider, usage="in-use"):
        base = [("correspondsTo", link(G43, ref)), ("designUse", usage)]
        if provider:
            base.append(("keysProvidedBy", provider))
        return iface("gw:" + ref, name, kind, pairs + base)

    def bh(ref, name, kind, pairs, provider, usage="in-use"):
        base = [("correspondsTo", link(SSH, ref)), ("designUse", usage)]
        if provider:
            base.append(("keysProvidedBy", provider))
        return iface("bastion:" + ref, name, kind, pairs + base)

    return [
        gw("ike", "Gateway IKEv2 for administrators", "service", [
            ("protocol", "IKEv2"), ("protocolVersion", "2"),
            ("endpointRole:initiator", "endpoint:admin-workstation"), ("endpointRole:responder", "endpoint:gateway"),
            ("keyExchange", ["ECP-256 (group 19)", "ML-KEM-768 (additional key exchange, RFC 9370)"]),
            ("encryption", "AES-256-GCM"), ("authentication", "ECDSA-P256-SHA256")], "sys:enterprise-ca"),
        gw("esp", "Gateway ESP tunnels", "service", [
            ("protocol", "ESP"), ("protocolVersion", "RFC 4303"),
            ("endpointRole:initiator", "endpoint:admin-workstation"), ("endpointRole:responder", "endpoint:gateway"),
            ("keyExchange", "none"), ("encryption", "AES-256-GCM"), ("authentication", "none")], "product"),
        gw("mgmt-https", "Gateway management interface", "management", [
            ("protocol", "TLS"), ("protocolVersion", "1.3"),
            ("endpointRole:administrator", "endpoint:bastion"), ("endpointRole:server", "endpoint:gateway"),
            ("keyExchange", "X25519MLKEM768"), ("encryption", "AES-256-GCM"),
            ("authentication", "ECDSA-P256-SHA256")], "sys:enterprise-ca"),
        gw("sto-hsm", "Gateway HSM key store", "storage", [
            ("encryption", "AES-256-GCM"), ("keyWrapping", "AES-256-KWP")], "product"),
        bh("ssh-transport", "Bastion SSH", "service", [
            ("protocol", "SSH"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:admin-workstation"), ("endpointRole:server", "endpoint:bastion"),
            ("keyExchange", BASTION_KEX), ("encryption", BASTION_CIPHERS), ("authentication", "ssh-ed25519")],
           "product"),
        bh("ssh-userauth", "Bastion administrator authentication", "service", [
            ("protocol", "SSH user authentication (RFC 4252)"), ("protocolVersion", "2.0"),
            ("endpointRole:client", "endpoint:admin-workstation"), ("endpointRole:server", "endpoint:bastion"),
            ("keyExchange", "none"), ("encryption", "none"),
            ("authentication", "sk-ssh-ed25519@openssh.com")], "sys:admin-security-keys"),
        bh("sto-hostkeys", "Bastion host key file", "storage", [
            ("encryption", "none"), ("keyWrapping", "none")], "product"),
        {"type": "service", "bom-ref": "sys:enterprise-ca", "name": "Enterprise certificate authority",
         "description": "Issues the gateway's IKE and management certificates and the administrators' client "
                        "certificates. ECDSA P-256 today; the gateway cannot authenticate with ML-DSA until the CA "
                        "issues ML-DSA certificates."},
        {"type": "device", "bom-ref": "sys:admin-security-keys", "name": "Administrators' FIDO2 security keys",
         "description": "Hold the administrators' sk-ssh-ed25519 keys. No post-quantum signature exists for them."},
    ]


def system():
    subj = tag_subject("platform", "system:remote-admin-access", "Remote administration access, reference design",
                       "Administrators reach production through an IPsec VPN gateway and then an SSH bastion. "
                       "Delivered by an integrator as a reference design. Fictional.",
                       "tag:integrator.example,2026:system/remote-admin-access", "system", INTEGRATOR)
    refs = [cite(G43, "The VPN gateway's product record (fictional ExampleGate 4.3.0)."),
            cite(SSH, "The bastion's product record (OpenSSH 10.0p2).")]
    comment = ("EXAMPLE CBOM, lifecycle stage 'configured'. FICTIONAL system. A remote administration access "
               "design joining two cited product records: an IPsec VPN gateway and an SSH bastion. Every interface "
               "of both products is listed, with the component that provides its keys. Two interfaces depend on "
               "components outside the products: the enterprise CA and the administrators' FIDO2 keys. Neither "
               "can move to post-quantum signatures yet, and that is what holds back entity authentication for "
               "the whole design.")
    return doc(SERIAL["sys"], comment, STAMP_CONF, "operations", INTEGRATOR, subj, system_interfaces(), refs)


# ------------------------------------------------------------- variants ---
def drop(ref, *names):
    return B.drop(ref, *names)


def unlink(ref, purl):
    """Drop the correspondsTo link of one interface. The implementing library was inherited through
    it, so the variant states it directly; otherwise the variant would also fail interface-disclosure I9."""
    def edit(bom):
        B.drop(ref, "correspondsTo")(bom)
        B._components(bom)[ref]["properties"].append({"name": P + "implementingLibrary", "value": purl})
    return edit


def stale_citation(serial_prefix):
    """Replace the digest of one citation, as if the cited record changed after it was cited."""
    def edit(bom):
        for r in bom["externalReferences"]:
            if r["type"] == "bom" and r["url"].startswith("urn:cdx:" + serial_prefix):
                r["hashes"][0]["content"] = "0" * 64
    return edit


def unhashed_citation(serial_prefix):
    """Cite one record by BOM-Link only, without the digest that fixes the revision."""
    def edit(bom):
        for r in bom["externalReferences"]:
            if r["type"] == "bom" and r["url"].startswith("urn:cdx:" + serial_prefix):
                r.pop("hashes", None)
    return edit


def drop_reference(context):
    def edit(bom):
        bom["externalReferences"] = [r for r in bom["externalReferences"]
                                     if {"name": P + "context", "value": context} not in r.get("properties", [])]
    return edit


def remove_component(ref):
    return B.remove_component(ref)


BC = "cbom-bastion-deployment-configured.cdx.json"
BO = "cbom-bastion-deployment-observed.cdx.json"
VC = "cbom-vpn-deployment-configured.cdx.json"
SY = "cbom-remote-admin-system-configured.cdx.json"
VARIANTS = [
    (BC, "fail-I1", "ssh-userauth does not say which product interface it realises",
     unlink("ssh-userauth", B.SSH_PURL)),
    (BC, "fail-R1", "the record does not name the configuration revision it was read from",
     drop_reference("configuration-source")),
    (BC, "fail-I14", "ssh-transport does not say what terminates it", drop("ssh-transport", "terminatedBy")),
    (BO, "fail-I2", "ssh-transport does not say how it was observed", drop("ssh-transport", "observationMethod")),
    (BO, "fail-I3", "ssh-transport does not say when it was observed", drop("ssh-transport", "observedAt")),
    (VC, "fail-P1", "the citation of the product record carries a digest that no longer matches it",
     stale_citation(B.GATE_SERIAL["4.3.0"][0][:8])),
    (SY, "fail-P1", "the bastion's product record is cited without a digest",
     unhashed_citation(B.SSH["product"][:8])),
    (SY, "fail-P2", "the bastion's host key store is left out of the design",
     remove_component("bastion:sto-hostkeys")),
    (SY, "fail-I1", "the gateway's ESP interface does not say which product interface it realises",
     unlink("gw:esp", "pkg:generic/example-networks/egcm@2.1")),
    (SY, "fail-I2", "the bastion's user authentication gives 'unused', which is not a usage value",
     B.set_value("bastion:ssh-userauth", "designUse", "unused")),
    (SY, "fail-I3", "the gateway's IKEv2 interface is in use but does not say what provides its keys",
     drop("gw:ike", "keysProvidedBy")),
]


def write_variants():
    for i, (base, suffix, what, edit) in enumerate(VARIANTS, 1):
        with open(os.path.join(OUT, base), encoding="utf-8") as fh:
            bom = copy.deepcopy(json.load(fh))
        edit(bom)
        bom["serialNumber"] = bom["serialNumber"][:-4] + "f%03d" % i
        bom["$comment"] = ("NON-CONFORMING EXAMPLE, derived from %s. It breaks one thing: %s. Everything else is "
                           "unchanged." % (base, what))
        B.write(B.variant_name(base, suffix), bom)


def main():
    if not os.path.exists(os.path.join(OUT, SSH)):
        sys.exit("run tools/build_pqc_examples.py first")
    _EVIDENCE["digest"] = B.write("bastion-ssh-scan-2026-11-27.json", evidence_doc(), CONTEXT)
    # Order matters: the observed record and the VPN record cite the bastion's configured record
    # by digest, and the system record cites the product records.
    B.write(BC, bastion(False))
    B.write(BO, bastion(True))
    B.write(VC, vpn())
    B.write(SY, system())
    write_variants()
    print("written to", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
