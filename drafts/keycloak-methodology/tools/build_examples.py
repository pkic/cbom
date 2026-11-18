#!/usr/bin/env python3
"""Write the Keycloak lifecycle example documents.

The product document is derived from the pqc-migration worked example
(drafts/pqc-migration-depths/examples/cbom-keycloak-pqc-pass.cyclonedx.json), so it
keeps every migration attribute. The deployment documents describe an illustrative
operator, Example Org, running the 26.7.3 image. Documents that cite another are
written after it, because the citation carries the cited file's SHA-256.

Usage: python3 build_examples.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "examples")
SRC = os.path.join(HERE, "..", "..", "pqc-migration-depths", "examples",
                   "cbom-keycloak-pqc-pass.cyclonedx.json")
P = "pkic:profile:"

SERIAL = {
    "product": "6b3c1d2e-7a41-4c1e-9f0a-26730000c001",
    "configured": "8b1f0c2a-3d4e-4f50-8a61-7263740c0f01",
    "observed": "8b1f0c2a-3d4e-4f50-8a61-7263740b5e01",
    "intended": "6b3c1d2e-7a41-4c1e-9f0a-27000000d001",
    "sbom": "6b3c1d2e-7a41-4c1e-9f0a-26730000b000",
}
DEPLOYMENT_ID = "tag:example.org,2026:deployment/sso-prod"


def link(kind, ref=None, version=1):
    return "urn:cdx:%s/%d%s" % (SERIAL[kind], version, "#" + ref if ref else "")


def prop(name, value):
    return {"name": P + name, "value": value}


def illustrative_hash(text):
    return hashlib.sha256(("illustrative:" + text).encode()).hexdigest()


def write(name, bom):
    # A top-level '$comment' makes a document invalid against the CycloneDX 1.7
    # schema (additionalProperties is false). The explanation goes in a
    # metadata property instead, which the schema allows and evaluators ignore.
    bom = copy.deepcopy(bom)
    note = bom.pop("$comment", None)
    if note:
        md = bom.setdefault("metadata", {})
        md["properties"] = [p for p in md.get("properties", []) if p["name"] != "pkic:example:comment"]
        md["properties"].append({"name": "pkic:example:comment", "value": note})
        bom = {k: bom[k] for k in ("bomFormat", "specVersion", "serialNumber", "version", "metadata")
               if k in bom} | {k: v for k, v in bom.items()
                               if k not in ("bomFormat", "specVersion", "serialNumber", "version", "metadata")}
    path = os.path.join(OUT, name)
    data = (json.dumps(bom, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def ctx(kind, url, rtype, comment, protocol=None, sha256=None):
    ref = {"type": rtype, "url": url, "comment": comment,
           "properties": [prop("context", kind)]}
    if protocol:
        ref["properties"].append(prop("accessProtocol", protocol))
    if sha256:
        ref["hashes"] = [{"alg": "SHA-256", "content": sha256}]
    return ref


def set_props(el, updates, drop=()):
    keep = [p for p in el.get("properties", [])
            if p["name"][len(P):] not in updates and p["name"][len(P):] not in drop]
    for k, v in updates.items():
        for item in (v if isinstance(v, list) else [v]):
            keep.append(prop(k, item))
    el["properties"] = keep


# --------------------------------------------------------------------------- #
# Stage 2: implemented. The vendor's build record of the image.               #
# --------------------------------------------------------------------------- #
def product():
    bom = json.load(open(SRC, encoding="utf-8"))
    bom["serialNumber"] = "urn:uuid:" + SERIAL["product"]
    bom["version"] = 1
    bom["$comment"] = (
        "EXAMPLE CBOM, lifecycle stage 'implemented'. The build record of the Keycloak 26.7.3 container "
        "image at its defaults, as the vendor or a downstream builder would write it. Derived from the "
        "pqc-migration worked example, with three changes. (1) One stage for the whole document, carried "
        "natively in metadata.lifecycles (phase 'build'); no interface carries its own stage. (2) No "
        "deployment facts: the example's assumed RSA-2048 server certificate is gone. The server "
        "certificate is 'deployment-defined', and each such interface points to the guide where the "
        "operator sets it (R5). On connections Keycloak opens to a database, directory, identity provider "
        "or mail server, the group, the cipher and the server certificate are decided with the peer and "
        "are 'peer-defined'. What Keycloak offers is still stated, in the shared TLS configuration "
        "component and the migration attributes. (3) Context the document points to but does not carry: "
        "the companion SBOM, the advisory sources, the security contact, and a statement that the "
        "upstream project publishes no VEX. Intended to conform to interface-disclosure v0.9 (draft).")
    md = bom["metadata"]
    md["timestamp"] = "2026-10-25T09:00:00Z"
    md["lifecycles"] = [{"phase": "build"}]
    comp = md["component"]
    comp["description"] = ("Keycloak 26.7.3 container image at its defaults. Build record: what the image "
                           "does before anyone deploys it.")
    set_props(comp, {"subjectType": "product",
                     "contextAbsent:vulnerability-statements": "not-published"})
    bom["externalReferences"] = [
        ctx("sbom", link("sbom"), "bom",
            "Companion SBOM of the same image. Illustrative BOM-Link and hash.",
            sha256=illustrative_hash("keycloak-26.7.3-sbom")),
        ctx("advisories", "https://github.com/keycloak/keycloak/security/advisories", "advisories",
            "Keycloak security advisories (GitHub Security Advisories).", protocol="web-page"),
        ctx("advisories", "https://api.osv.dev/v1/query", "advisories",
            "OSV API. Query with the package URLs in this document, for example "
            "pkg:maven/org.keycloak/keycloak-services@26.7.3. OSV aggregates the GitHub advisories.",
            protocol="osv-api"),
        ctx("security-contact", "https://github.com/keycloak/keycloak/security/policy", "security-contact",
            "Keycloak security policy: how to report a vulnerability.", protocol="web-page"),
    ]

    guidance = {
        "crypto:protocol:tls-https": "https://www.keycloak.org/server/enabletls",
        "crypto:protocol:tls-mgmt": "https://www.keycloak.org/server/management-interface",
    }
    peer = ("crypto:protocol:int-db", "crypto:protocol:int-ldap", "crypto:protocol:int-broker",
            "crypto:protocol:int-smtp")
    default_state = {
        "crypto:protocol:tls-https": "enabled", "crypto:protocol:tls-mgmt": "disabled",
        "crypto:protocol:int-db": "enabled", "crypto:protocol:int-ldap": "disabled",
        "crypto:protocol:int-broker": "disabled", "crypto:protocol:int-smtp": "disabled",
        "crypto:protocol:int-cache": "enabled", "service:svc-oidc": "enabled",
        "service:svc-saml": "enabled", "service:svc-http": "disabled",
        "service:mgmt-admin": "enabled", "service:svc-broker-tokens": "disabled",
        "service:sto-realm-keys": "enabled",
    }
    for el in bom["components"] + bom["services"]:
        ref = el["bom-ref"]
        if ref not in default_state:
            continue
        set_props(el, {"defaultState": default_state[ref]}, drop=("lifecycleStage",))
        if ref in guidance:
            pp = el["cryptoProperties"]["protocolProperties"]
            pp["cryptoRefArray"] = [r for r in pp["cryptoRefArray"] if r != "crypto:algo:rsa-2048"]
            set_props(el, {"authentication": "deployment-defined"})
            el["externalReferences"] = [ctx("configuration-guidance", guidance[ref], "documentation",
                                            "Where the operator sets the server certificate and key.",
                                            protocol="web-page")]
        if ref in peer:
            el["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = []
            set_props(el, {"keyExchange": "peer-defined", "encryption": "peer-defined",
                           "authentication": "peer-defined"})
        if ref == "service:svc-broker-tokens":
            set_props(el, {"authentication": "peer-defined"})
    for d in bom["dependencies"]:
        if d["ref"] == "service:svc-broker-tokens":
            d["dependsOn"] = [x for x in d["dependsOn"] if x != "crypto:algo:rs256"]
    return bom


# --------------------------------------------------------------------------- #
# Shared helpers for the operator's documents                                 #
# --------------------------------------------------------------------------- #
ALGOS = {
    "x25519mlkem768": ("X25519MLKEM768", "kem"),
    "x25519": ("X25519", "key-agree"), "secp256r1": ("secp256r1", "key-agree"),
    "secp384r1": ("secp384r1", "key-agree"), "secp521r1": ("secp521r1", "key-agree"),
    "x448": ("X448", "key-agree"), "ffdhe2048": ("ffdhe2048", "key-agree"),
    "aes-256-gcm": ("AES-256-GCM", "ae"), "aes-128-gcm": ("AES-128-GCM", "ae"),
    "chacha20-poly1305": ("ChaCha20-Poly1305", "ae"),
    "ecdsa-p256": ("ECDSA-P256-SHA256", "signature"), "rsa-2048": ("RSA-2048", "signature"),
    "es256": ("ES256", "signature"), "rs256": ("RS256", "signature"),
    "rsa-sha256": ("RSA-SHA256", "signature"),
}
JDK_GROUPS = ["x25519", "secp256r1", "secp384r1", "secp521r1", "x448", "ffdhe2048"]
TLS13_SUITES = ["aes-256-gcm", "aes-128-gcm", "chacha20-poly1305"]


def algo_components(keys):
    out = []
    for k in keys:
        name, prim = ALGOS[k]
        out.append({"type": "cryptographic-asset", "bom-ref": "crypto:algo:" + k, "name": name,
                    "cryptoProperties": {"assetType": "algorithm",
                                         "algorithmProperties": {"primitive": prim}}})
    return out


def tls(ref, name, itype, version, algos, roles, corresponds, extra=None, refs=None):
    el = {"type": "cryptographic-asset", "bom-ref": ref, "name": name,
          "cryptoProperties": {"assetType": "protocol", "protocolProperties": {
              "type": "tls", "version": version,
              "cryptoRefArray": ["crypto:algo:" + a for a in algos]}},
          "properties": [prop("interfaceType", itype)] +
                        [prop("endpointRole:" + r, v) for r, v in roles.items()] +
                        [prop("correspondsTo", corresponds)]}
    for k, v in (extra or {}).items():
        for item in (v if isinstance(v, list) else [v]):
            el["properties"].append(prop(k, item))
    if refs:
        el["externalReferences"] = refs
    return el


def service(ref, name, itype, protocol, version, roles, corresponds, extra=None, refs=None):
    el = {"bom-ref": ref, "name": name,
          "properties": [prop("interfaceType", itype)] +
                        ([prop("protocol", protocol), prop("protocolVersion", version)] if protocol else []) +
                        [prop("endpointRole:" + r, v) for r, v in roles.items()] +
                        [prop("correspondsTo", corresponds)]}
    for k, v in (extra or {}).items():
        for item in (v if isinstance(v, list) else [v]):
            el["properties"].append(prop(k, item))
    if refs:
        el["externalReferences"] = refs
    return el


def operator_doc(stage, serial, comment, timestamp, tools, coverage):
    phase = {"configured": "operations", "observed": "discovery"}[stage]
    return {
        "bomFormat": "CycloneDX", "specVersion": "1.7", "serialNumber": "urn:uuid:" + serial,
        "version": 1, "$comment": comment,
        "metadata": {
            "timestamp": timestamp, "lifecycles": [{"phase": phase}],
            "tools": {"components": tools},
            "supplier": {"name": "Example Org (illustrative operator)"},
            "component": {
                "type": "application", "bom-ref": "deployment:sso-prod",
                "name": "sso.example.org identity service (production)",
                "description": "Keycloak 26.7.3 on Kubernetes, two replicas, behind a TLS-terminating ingress.",
                "properties": [prop("subjectType", "deployment"),
                               prop("subjectIdentifier", DEPLOYMENT_ID),
                               prop("coverage", coverage)]}},
        "externalReferences": [], "components": [], "services": [], "dependencies": [],
    }


def cite(kind, sha, comment):
    return ctx("cited-document", link(kind), "bom", comment, sha256=sha)


def finish(bom, ifaces, libs_provide):
    refs = [i["bom-ref"] for i in ifaces]
    bom["dependencies"].insert(0, {"ref": "deployment:sso-prod", "dependsOn": refs})
    for lib, provided in libs_provide.items():
        bom["dependencies"].append({"ref": lib, "provides": provided})
    bom["compositions"] = [{"aggregate": "complete" if bom["metadata"]["component"]["properties"][2]["value"] == "all"
                            else "incomplete", "assemblies": refs}]
    return bom


# --------------------------------------------------------------------------- #
# Stage 3: configured. What the operator's deployment permits.                #
# --------------------------------------------------------------------------- #
def configured(product_sha):
    bom = operator_doc(
        "configured", SERIAL["configured"],
        "EXAMPLE CBOM, lifecycle stage 'configured'. Example Org's deployment of the Keycloak 26.7.3 "
        "image, read from its configuration repository, realm exports and JVM settings. Illustrative: "
        "the operator, hostnames and configuration values are invented. TLS is terminated at the ingress "
        "(nginx with OpenSSL 3.5) and Keycloak runs with http-enabled=true and proxy-headers=xforwarded. "
        "So the product's TLS listener is not configured, the plaintext listener carries tokens on the "
        "hop from the ingress, and the management port inherits plain HTTP. No mail server is configured. "
        "Values are permitted sets where the outcome is negotiated. Each interface states the product "
        "interface it realises (correspondsTo), which is also how it inherits the implementing library. "
        "The ingress has no product CBOM, so its library is stated here. Intended to conform to "
        "deployment-disclosure v0.1 (draft).",
        "2026-10-24T16:00:00Z",
        [{"type": "application", "name": "Example Org configuration export", "version": "1.0",
          "description": "Reads keycloak.conf, realm exports, java.security and the ingress manifest"}],
        "all")
    bom["externalReferences"] = [
        cite("product", product_sha, "The product CBOM of the image this deployment runs."),
        ctx("configuration-source", "https://git.example.org/platform/sso-config/-/commit/4f2a9c1e7b",
            "vcs", "Revision of the configuration repository this record was read from."),
        ctx("data-register", "https://grc.example.org/registers/data/sso-prod", "risk-assessment",
            "Data classification and confidentiality lifetime per interface. Not reproduced here."),
        ctx("issuer-policy", "https://pki.example.org/cps", "documentation",
            "Certification practice statement of the internal CA that issues the ingress, database and "
            "directory certificates.", protocol="web-page"),
    ]
    bom["components"] = [{"type": "library", "bom-ref": "lib:openssl", "name": "OpenSSL (ingress controller)",
                          "version": "3.5.4", "purl": "pkg:generic/openssl@3.5.4"}]
    bom["components"] += algo_components(["x25519mlkem768"] + JDK_GROUPS + TLS13_SUITES +
                                         ["ecdsa-p256", "rsa-2048", "es256", "rs256", "rsa-sha256"])
    bom["components"].append({"type": "cryptographic-asset", "bom-ref": "crypto:key:realm-keys",
                              "name": "Realm keys (ES256 active, RSA-2048 retained, HMAC, AES)",
                              "cryptoProperties": {"assetType": "related-crypto-material",
                                                   "relatedCryptoMaterialProperties": {
                                                       "type": "private-key", "state": "active",
                                                       "algorithmRef": "crypto:algo:es256",
                                                       "securedBy": {"mechanism": "none"}}}})
    P_ = lambda r: link("product", r)
    ifaces = [
        tls("crypto:protocol:ing-tls", "TLS at the ingress (sso.example.org:443)", "service", "1.3",
            ["x25519mlkem768", "x25519", "aes-256-gcm", "aes-128-gcm", "chacha20-poly1305", "ecdsa-p256"],
            {"client": "endpoint:browser-or-relying-party", "server": "endpoint:ingress"},
            "no-product-document",
            {"integrationConstraints": "ssl_ecdh_curve X25519MLKEM768:X25519; certificate ECDSA P-256 from the internal CA"}),
        tls("crypto:protocol:int-db", "TLS to PostgreSQL (sslmode=verify-full)", "interconnect", "1.3",
            JDK_GROUPS + TLS13_SUITES + ["rsa-2048"],
            {"client": "endpoint:keycloak", "server": "endpoint:database"}, P_("crypto:protocol:int-db"),
            {"integrationConstraints": "Groups and suites are the JVM defaults (jdk.tls.namedGroups not set). "
                                       "Server certificate RSA-2048 from the internal CA."}),
        tls("crypto:protocol:int-ldap", "LDAPS to the corporate directory", "interconnect", "1.2",
            JDK_GROUPS + ["aes-256-gcm", "aes-128-gcm", "rsa-2048"],
            {"client": "endpoint:keycloak", "server": "endpoint:directory"}, P_("crypto:protocol:int-ldap"),
            {"integrationConstraints": "The directory accepts TLS 1.2 only."}),
        tls("crypto:protocol:int-broker", "TLS to the corporate external identity provider", "interconnect", "1.3",
            JDK_GROUPS + TLS13_SUITES + ["rsa-2048"],
            {"client": "endpoint:keycloak", "server": "endpoint:external-identity-provider"},
            P_("crypto:protocol:int-broker")),
        tls("crypto:protocol:int-cache", "Mutual TLS between the two Keycloak replicas", "peer", "1.3",
            JDK_GROUPS + TLS13_SUITES + ["rsa-2048"],
            {"initiator": "endpoint:keycloak-node", "responder": "endpoint:keycloak-node"},
            P_("crypto:protocol:int-cache"),
            {"integrationConstraints": "Product-generated RSA-2048 key, rotated every 30 days (cannot be changed by configuration)."}),
        service("service:svc-http", "HTTP from the ingress to Keycloak (port 8080)", "service", "HTTP", "1.1",
                {"client": "endpoint:ingress", "server": "endpoint:keycloak"}, P_("service:svc-http"),
                {"keyExchange": "none", "encryption": "none", "authentication": "none",
                 "integrationConstraints": "http-enabled=true. Carries tokens and credentials in clear inside the cluster."}),
        service("service:mgmt-health", "Health and metrics (port 9000, plain HTTP)", "management", "HTTP", "1.1",
                {"client": "endpoint:monitoring", "server": "endpoint:keycloak"}, P_("crypto:protocol:tls-mgmt"),
                {"keyExchange": "none", "encryption": "none", "authentication": "none",
                 "integrationConstraints": "health-enabled=true. The management interface inherits the main "
                                           "server's scheme, which is HTTP here."}),
        service("service:svc-oidc", "OIDC token issuance, realm 'corp'", "service", "OIDC", "1.0",
                {"issuer": "endpoint:keycloak", "relying-party": "endpoint:client-application"},
                P_("service:svc-oidc"),
                {"keyExchange": "none", "encryption": "none",
                 "integrationConstraints": "Realm defaultSignatureAlgorithm=ES256. Client 'legacy-portal' overrides it to RS256."}),
        service("service:svc-saml", "SAML 2.0 assertions, realm 'corp'", "service", "SAML", "2.0",
                {"identity-provider": "endpoint:keycloak", "service-provider": "endpoint:client-application"},
                P_("service:svc-saml"), {"keyExchange": "none", "encryption": "none"}),
        service("service:mgmt-admin", "Admin REST API (master realm tokens)", "management",
                "Admin REST (OAuth 2.0 bearer)", "1.0",
                {"administrator": "endpoint:admin-client", "server": "endpoint:keycloak"},
                P_("service:mgmt-admin"), {"keyExchange": "none", "encryption": "none"}),
        service("service:svc-broker-tokens", "Brokered token verification (corporate identity provider)",
                "interconnect", "OIDC", "1.0",
                {"relying-party": "endpoint:keycloak", "issuer": "endpoint:external-identity-provider"},
                P_("service:svc-broker-tokens"), {"keyExchange": "none", "encryption": "none"}),
        service("service:sto-realm-keys", "Realm key persistence (PostgreSQL)", "storage", None, None,
                {}, P_("service:sto-realm-keys"), {"encryption": "none"}),
    ]
    for el in ifaces:
        if "cryptoProperties" in el:
            bom["components"].append(el)
        else:
            bom["services"].append(el)
    deps = {"service:svc-oidc": ["crypto:algo:es256", "crypto:key:realm-keys"],
            "service:svc-saml": ["crypto:algo:rsa-sha256"],
            "service:mgmt-admin": ["crypto:algo:rs256"],
            "service:svc-broker-tokens": ["crypto:algo:rs256"],
            "service:sto-realm-keys": ["crypto:key:realm-keys"]}
    bom["dependencies"] = [{"ref": k, "dependsOn": v} for k, v in deps.items()]
    return finish(bom, ifaces, {"lib:openssl": ["crypto:protocol:ing-tls"]})


# --------------------------------------------------------------------------- #
# Stage 4: observed. What the deployment was seen to do.                      #
# --------------------------------------------------------------------------- #
def observed(product_sha, configured_sha, configured_hash_override=None):
    bom = operator_doc(
        "observed", SERIAL["observed"],
        "EXAMPLE CBOM, lifecycle stage 'observed'. What Example Org's deployment was seen to do between "
        "18 and 25 October 2026. Illustrative values. Each interface names the methods its values came from: "
        "a passive sensor sees the group in a TLS 1.3 ServerHello but not the server certificate; only an "
        "active probe sees a TLS 1.3 server certificate; pg_stat_ssl reports version and cipher and not the "
        "group; a JWKS shows which signing keys are published. Two findings the configured record cannot "
        "show: 29% of ingress sessions still negotiate X25519 alone, and tokens for one client are still "
        "signed RS256. The brokering interfaces were not observed (the sensor does not cover egress), so "
        "coverage is partial. Each interface points to the configured interface it was compared with, and "
        "through it to the product. Intended to conform to deployment-disclosure v0.1 (draft).",
        "2026-10-25T08:00:00Z",
        [{"type": "application", "name": "testssl.sh", "version": "3.2"},
         {"type": "application", "name": "Zeek", "version": "7.0"},
         {"type": "application", "name": "Example Org JWKS reader", "version": "0.3"}],
        "partial")
    bom["externalReferences"] = [
        cite("configured", configured_hash_override or configured_sha,
             "The configured record this observation was compared with."),
        cite("product", product_sha, "The product CBOM of the image."),
        ctx("data-register", "https://grc.example.org/registers/data/sso-prod", "risk-assessment",
            "Data classification and confidentiality lifetime per interface. Not reproduced here."),
    ]
    bom["components"] = algo_components(["x25519mlkem768", "x25519", "secp384r1", "aes-256-gcm",
                                         "aes-128-gcm", "ecdsa-p256", "rsa-2048", "es256", "rs256",
                                         "rsa-sha256"])
    bom["components"].append({"type": "cryptographic-asset", "bom-ref": "crypto:key:realm-keys",
                              "name": "Realm key rows in the database (read in clear)",
                              "cryptoProperties": {"assetType": "related-crypto-material",
                                                   "relatedCryptoMaterialProperties": {
                                                       "type": "private-key", "state": "active",
                                                       "securedBy": {"mechanism": "none"}}}})
    C_ = lambda r: link("configured", r)
    window = "2026-10-18T00:00:00Z/2026-10-25T00:00:00Z"
    ev = lambda name: [ctx("observation-evidence", "https://evidence.example.org/sso-prod/2026-10-25/" + name,
                           "evidence", "Evidence extract. Illustrative hash.",
                           sha256=illustrative_hash(name))]
    obs = lambda methods, extra=None: dict({"observationMethod": methods, "observedAt": window}, **(extra or {}))
    ifaces = [
        tls("crypto:protocol:ing-tls", "TLS at the ingress (sso.example.org:443)", "service", "1.3",
            ["x25519mlkem768", "x25519", "aes-256-gcm", "aes-128-gcm", "ecdsa-p256"],
            {"client": "endpoint:browser-or-relying-party", "server": "endpoint:ingress"},
            C_("crypto:protocol:ing-tls"),
            obs(["passive-sensor", "active-probe"],
                {"observationSummary": "Groups negotiated: X25519MLKEM768 71%, X25519 29% of 1.2 million sessions."}),
            ev("ing-tls-zeek-summary.json")),
        tls("crypto:protocol:int-db", "TLS to PostgreSQL", "interconnect", "1.3",
            ["x25519", "aes-256-gcm", "rsa-2048"],
            {"client": "endpoint:keycloak", "server": "endpoint:database"}, C_("crypto:protocol:int-db"),
            obs(["platform-query", "passive-sensor", "active-probe"],
                {"observationSummary": "Version and cipher from pg_stat_ssl; group from the ServerHello; "
                                       "certificate from testssl.sh --starttls postgres."}),
            ev("int-db.json")),
        tls("crypto:protocol:int-ldap", "LDAPS to the corporate directory", "interconnect", "1.2",
            ["secp384r1", "aes-256-gcm", "rsa-2048"],
            {"client": "endpoint:keycloak", "server": "endpoint:directory"}, C_("crypto:protocol:int-ldap"),
            obs(["passive-sensor"]), ev("int-ldap.json")),
        tls("crypto:protocol:int-cache", "Mutual TLS between the two Keycloak replicas", "peer", "1.3",
            ["x25519", "aes-256-gcm", "rsa-2048"],
            {"initiator": "endpoint:keycloak-node", "responder": "endpoint:keycloak-node"},
            C_("crypto:protocol:int-cache"), obs(["active-probe"])),
        service("service:svc-http", "HTTP from the ingress to Keycloak (port 8080)", "service", "HTTP", "1.1",
                {"client": "endpoint:ingress", "server": "endpoint:keycloak"}, C_("service:svc-http"),
                obs(["passive-sensor"], {"keyExchange": "none", "encryption": "none", "authentication": "none"})),
        service("service:mgmt-health", "Health and metrics (port 9000)", "management", "HTTP", "1.1",
                {"client": "endpoint:monitoring", "server": "endpoint:keycloak"}, C_("service:mgmt-health"),
                obs(["active-probe"], {"keyExchange": "none", "encryption": "none", "authentication": "none"})),
        service("service:svc-oidc", "OIDC token issuance, realm 'corp'", "service", "OIDC", "1.0",
                {"issuer": "endpoint:keycloak", "relying-party": "endpoint:client-application"},
                C_("service:svc-oidc"),
                obs(["endpoint-query"], {"keyExchange": "none", "encryption": "none",
                                         "observationSummary": "The JWKS publishes an ES256 and an RS256 key. "
                                                               "Tokens for 'legacy-portal' are RS256."}),
                ev("jwks-corp.json")),
        service("service:svc-saml", "SAML 2.0 assertions, realm 'corp'", "service", "SAML", "2.0",
                {"identity-provider": "endpoint:keycloak", "service-provider": "endpoint:client-application"},
                C_("service:svc-saml"), obs(["endpoint-query"], {"keyExchange": "none", "encryption": "none"})),
        service("service:mgmt-admin", "Admin REST API (master realm tokens)", "management",
                "Admin REST (OAuth 2.0 bearer)", "1.0",
                {"administrator": "endpoint:admin-client", "server": "endpoint:keycloak"},
                C_("service:mgmt-admin"), obs(["endpoint-query"], {"keyExchange": "none", "encryption": "none"})),
        service("service:sto-realm-keys", "Realm key persistence (PostgreSQL)", "storage", None, None,
                {}, C_("service:sto-realm-keys"),
                obs(["inspection"], {"encryption": "none",
                                     "observationSummary": "Private keys read in clear from the component configuration table."})),
    ]
    # Evidence for the cluster transport is held back: it carries node addresses.
    ifaces[3]["properties"].append(prop("disclosure:context:observation-evidence", "withheld"))
    for el in ifaces:
        (bom["components"] if "cryptoProperties" in el else bom["services"]).append(el)
    deps = {"service:svc-oidc": ["crypto:algo:es256", "crypto:algo:rs256"],
            "service:svc-saml": ["crypto:algo:rsa-sha256"],
            "service:mgmt-admin": ["crypto:algo:rs256"],
            "service:sto-realm-keys": ["crypto:key:realm-keys"]}
    bom["dependencies"] = [{"ref": k, "dependsOn": v} for k, v in deps.items()]
    return finish(bom, ifaces, {})


# --------------------------------------------------------------------------- #
# Stage 1: intended. Kept only to show that v0.9 no longer accepts it.        #
# --------------------------------------------------------------------------- #
def intended(prod):
    bom = copy.deepcopy(prod)
    bom["serialNumber"] = "urn:uuid:" + SERIAL["intended"]
    bom["$comment"] = ("NON-CONFORMING EXAMPLE, lifecycle stage 'intended'. What a vendor design record for "
                       "Keycloak 27.0 would contain: the 26.7.3 record with ML-DSA-65 token signing (epic "
                       "#43690). Fails interface-disclosure#I8 under v0.9 on every interface, because "
                       "'intended' is no longer accepted. It also fails I3-I5 wherever it repeats "
                       "'deployment-defined' or 'peer-defined', which are accepted only at 'implemented'. The same fact is already recorded in the product "
                       "record as capabilityStatus 'committed' with a roadmapRef. The image tag does not "
                       "exist yet, so the subject identifier resolves to nothing.")
    bom["metadata"]["lifecycles"] = [{"phase": "design"}]
    comp = bom["metadata"]["component"]
    comp["version"] = "27.0"
    comp["purl"] = "pkg:oci/keycloak?repository_url=quay.io/keycloak/keycloak&tag=27.0"
    bom["components"] += algo_components([])
    bom["components"].append({"type": "cryptographic-asset", "bom-ref": "crypto:algo:ml-dsa-65",
                              "name": "ML-DSA-65", "cryptoProperties": {"assetType": "algorithm",
                                                                        "algorithmProperties": {"primitive": "signature"}}})
    for d in bom["dependencies"]:
        if d["ref"] == "service:svc-oidc":
            d["dependsOn"] = [x if x != "crypto:algo:rs256" else "crypto:algo:ml-dsa-65" for x in d["dependsOn"]]
    return bom


def main():
    os.makedirs(OUT, exist_ok=True)
    expected = {}
    prod = product()
    sha_p = write("kc-product-implemented.cdx.json", prod)

    f = copy.deepcopy(prod)
    f["serialNumber"] = "urn:uuid:6b3c1d2e-7a41-4c1e-9f0a-26730000c0f5"
    f["$comment"] = ("NON-CONFORMING EXAMPLE. Identical to kc-product-implemented except that the HTTPS "
                     "listener states its certificate is deployment-defined without pointing to where the "
                     "operator sets it. Fails interface-disclosure#R5 on that interface only.")
    for c in f["components"]:
        if c["bom-ref"] == "crypto:protocol:tls-https":
            c.pop("externalReferences")
    write("kc-product-implemented-fail-R5.cdx.json", f)

    write("kc-product-intended-fail-I8.cdx.json", intended(prod))

    conf = configured(sha_p)
    sha_c = write("kc-deployment-configured.cdx.json", conf)

    f = copy.deepcopy(conf)
    f["serialNumber"] = "urn:uuid:8b1f0c2a-3d4e-4f50-8a61-7263740c0ff5"
    f["$comment"] = ("NON-CONFORMING EXAMPLE. Identical to kc-deployment-configured except that the database "
                     "connection still says 'peer-defined', as the product record does. At 'configured' the "
                     "operator holds the answer. Fails interface-disclosure#I3, I4 and I5 on that interface.")
    for c in f["components"]:
        if c["bom-ref"] == "crypto:protocol:int-db":
            c["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = []
            for a in ("keyExchange", "encryption", "authentication"):
                c["properties"].append(prop(a, "peer-defined"))
    write("kc-deployment-configured-fail-literal.cdx.json", f)

    obs = observed(sha_p, sha_c)
    write("kc-deployment-observed.cdx.json", obs)

    f = copy.deepcopy(obs)
    f["serialNumber"] = "urn:uuid:8b1f0c2a-3d4e-4f50-8a61-7263740b5ef5"
    f["$comment"] = ("NON-CONFORMING EXAMPLE. Identical to kc-deployment-observed except that the database "
                     "connection was observed through pg_stat_ssl alone, which does not report the group. "
                     "keyExchange is declared unknown. Fails interface-disclosure#I3 on that interface: an "
                     "observed record built from one source has gaps, and the profile asks the operator to "
                     "combine sources rather than accept the gap.")
    for c in f["components"]:
        if c["bom-ref"] == "crypto:protocol:int-db":
            c["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = ["crypto:algo:aes-256-gcm",
                                                                             "crypto:algo:rsa-2048"]
            c["properties"] = [p for p in c["properties"] if not p["name"].endswith(("observationMethod",
                                                                                      "observationSummary"))]
            c["properties"] += [prop("observationMethod", "platform-query"),
                                prop("observationMethod", "active-probe"),
                                prop("disclosure:keyExchange", "unknown")]
    write("kc-deployment-observed-fail-unknown.cdx.json", f)

    f = observed(sha_p, sha_c, configured_hash_override=illustrative_hash("configured-revision-before-edit"))
    f["serialNumber"] = "urn:uuid:8b1f0c2a-3d4e-4f50-8a61-7263740b5ef6"
    f["$comment"] = ("NON-CONFORMING EXAMPLE. Identical to kc-deployment-observed except that the hash it "
                     "records for the configured record does not match that record. This is what a consumer "
                     "sees when the configured record is revised after the observation cited it. Fails "
                     "deployment-disclosure#P1.")
    write("kc-deployment-observed-fail-P1.cdx.json", f)
    print("written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
