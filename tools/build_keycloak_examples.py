#!/usr/bin/env python3
"""Write the Keycloak example CBOMs published with the methodology.

Every example is generated here, so the documents that cite each other stay
consistent: a citation carries the cited file's SHA-256, so a cited document is
written before the one that cites it.

The product record is derived from tools/keycloak/source-product-1.7.json, the
hand-maintained source of the Keycloak 26.7.3 facts (sources in its comment and
in docs/methodology/files.html). The deployment records describe an
illustrative operator, Example Org. Documents are built in CycloneDX 1.7 form
and converted to CycloneDX 2.0 with docs/methodology/cdx17_to_20.py; the 2.0
documents are the published examples, and one product record is also kept in
1.7 form to show how a legacy document is read.

Usage: python3 tools/build_keycloak_examples.py
Then:  python3 tests/check-cyclonedx.py && bash tests/run-profile-tests.sh
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "methodology", "examples")
SRC = os.path.join(HERE, "keycloak", "source-product-1.7.json")
sys.path.insert(0, os.path.join(ROOT, "docs", "methodology"))
import cdx17_to_20  # noqa: E402
P = "pkic:profile:"

SERIAL = {
    "product": "6b3c1d2e-7a41-4c1e-9f0a-26730000c001",
    "configured": "8b1f0c2a-3d4e-4f50-8a61-7263740c0f01",
    "observed": "8b1f0c2a-3d4e-4f50-8a61-7263740b5e01",
    "intended": "6b3c1d2e-7a41-4c1e-9f0a-27000000d001",
    "sbom": "6b3c1d2e-7a41-4c1e-9f0a-26730000b000",
    "legacy": "6b3c1d2e-7a41-4c1e-9f0a-26730000c017",
    "vex": "6b3c1d2e-7a41-4c1e-9f0a-26730000e001",
}
SITE = "https://pkic.github.io/cbom/methodology/examples/"
CONTEXT = os.path.join(OUT, "context")
PRODUCT_PURL = "pkg:oci/keycloak?repository_url=quay.io/keycloak/keycloak&tag=26.7.3"
DEPLOYMENT_ID = "tag:example.org,2026:deployment/sso-prod"


def link(kind, ref=None, version=1):
    return "urn:cdx:%s/%d%s" % (SERIAL[kind], version, "#" + ref if ref else "")


def prop(name, value):
    return {"name": P + name, "value": value}


def illustrative_hash(text):
    return hashlib.sha256(("illustrative:" + text).encode()).hexdigest()


def write(name, bom, legacy=False):
    """Write one example. CycloneDX 2.0 unless 'legacy' is set."""
    if not legacy:
        doc = cdx17_to_20.convert(bom)
        data = (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        with open(os.path.join(OUT, name), "wb") as fh:
            fh.write(data)
        return hashlib.sha256(data).hexdigest()
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
# Context the product record points to and does not carry                     #
# --------------------------------------------------------------------------- #
def write_context(name, doc, convert=False):
    os.makedirs(CONTEXT, exist_ok=True)
    if convert:
        doc = cdx17_to_20.convert(doc)
    data = (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with open(os.path.join(CONTEXT, name), "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def sbom():
    """The companion SBOM of the image: an illustrative subset of its components.

    The library components carry the same bom-ref as in the product record, so
    the record can point at each library's SBOM entry by BOM-Link."""
    lib = lambda ref, name, purl, version=None: dict(
        {"type": "library", "bom-ref": ref, "name": name, "purl": purl},
        **({"version": version} if version else {}))
    return {
        "bomFormat": "CycloneDX", "specVersion": "1.7",
        "serialNumber": "urn:uuid:" + SERIAL["sbom"], "version": 1,
        "metadata": {
            "timestamp": "2026-10-25T09:00:00Z", "lifecycles": [{"phase": "build"}],
            "supplier": {"name": "PKI Consortium CBOM Profiles Working Group (worked example)",
                         "url": ["https://pkic.org"]},
            "component": {"type": "container", "bom-ref": "app:keycloak", "name": "Keycloak",
                          "version": "26.7.3", "purl": PRODUCT_PURL,
                          "supplier": {"name": "Keycloak project", "url": ["https://www.keycloak.org"]}},
            "properties": [{"name": "pkic:example:comment", "value":
                "EXAMPLE SBOM. The companion SBOM of the Keycloak 26.7.3 container image, referenced by the "
                "product record under interface-disclosure#R1 by BOM-Link and SHA-256. It lists an "
                "illustrative subset of the image's components, so its composition is declared "
                "incomplete. Versions are given only where the product record states them; a real SBOM "
                "from the build pipeline lists every component with its exact version. The library "
                "components keep the bom-ref they have in the product record, so the record can point at "
                "each one's SBOM entry."}]},
        "components": [
            lib("lib:keycloak-services", "Keycloak services", "pkg:maven/org.keycloak/keycloak-services@26.7.3", "26.7.3"),
            lib("lib:keycloak-model-jpa", "Keycloak JPA model", "pkg:maven/org.keycloak/keycloak-model-jpa@26.7.3", "26.7.3"),
            lib("lib:quarkus-vertx-http", "Quarkus HTTP (Vert.x)", "pkg:maven/io.quarkus/quarkus-vertx-http"),
            lib("lib:openjdk", "OpenJDK 21 (java-21-openjdk-headless, UBI 9)",
                "pkg:rpm/redhat/java-21-openjdk-headless?arch=x86_64&distro=rhel-9"),
            lib("lib:postgresql-jdbc", "PostgreSQL JDBC driver", "pkg:maven/org.postgresql/postgresql"),
            lib("lib:infinispan-core", "Infinispan core (distributed caches)", "pkg:maven/org.infinispan/infinispan-core"),
            lib("lib:jgroups", "JGroups (cluster transport)", "pkg:maven/org.jgroups/jgroups"),
        ],
        "dependencies": [
            {"ref": "app:keycloak", "dependsOn": ["lib:keycloak-services", "lib:keycloak-model-jpa",
                                                  "lib:quarkus-vertx-http", "lib:openjdk"]},
            {"ref": "lib:keycloak-model-jpa", "dependsOn": ["lib:postgresql-jdbc"]},
            {"ref": "lib:keycloak-services", "dependsOn": ["lib:infinispan-core"]},
            {"ref": "lib:infinispan-core", "dependsOn": ["lib:jgroups"]},
        ],
        "compositions": [{"aggregate": "incomplete", "assemblies": []}],
    }


def vex():
    """A supplier's vulnerability statements about the image, in CycloneDX 2.0.

    The identifiers are illustrative. They are not CVEs and describe no real
    vulnerability: the document shows the form a statement takes and how it
    joins to the SBOM, not the security state of Keycloak."""
    sbom_ref = lambda r: link("sbom", r)
    src = {"name": "PKIC CBOM Profiles WG worked example (illustrative identifiers)",
           "url": "https://pkic.github.io/cbom/methodology/vulnerabilities.html"}
    return {
        "specFormat": "CycloneDX", "specVersion": "2.0",
        "serialNumber": "urn:uuid:" + SERIAL["vex"], "version": 1,
        "$comment": ("EXAMPLE VEX, CycloneDX 2.0. Vulnerability statements about the Keycloak 26.7.3 image, "
                     "in the form a supplier publishes them. The product record points here under "
                     "interface-disclosure#R2 by BOM-Link and SHA-256. ILLUSTRATIVE: the identifiers are not "
                     "CVEs and describe no real vulnerability, and the upstream Keycloak project publishes no "
                     "VEX. Each statement names the affected component by a BOM-Link into the companion SBOM, "
                     "and the SBOM entry carries the package URL that the product record's I9 also names. "
                     "That shared identifier is the join. The VEX is revised when knowledge changes; the "
                     "CBOM is revised when the product changes (decision 0020)."),
        "metadata": {"timestamp": "2026-10-25T09:00:00Z",
                     "supplier": {"name": "PKI Consortium CBOM Profiles Working Group (worked example)"}},
        "vulnerabilities": [
            {"bom-ref": "vex:example-0001", "id": "PKIC-EXAMPLE-2026-0001", "source": src,
             "description": "Illustrative: a token signature verification flaw in the server's JOSE handling.",
             "analysis": {"state": "resolved",
                          "detail": "Fixed before 26.7.3. Listed so that a consumer holding an older record "
                                    "can see the version boundary."},
             "affects": [{"ref": sbom_ref("lib:keycloak-services"),
                          "versions": [{"version": "26.7.3", "status": "unaffected"},
                                       {"range": "vers:maven/<26.7.3", "status": "affected"}]}]},
            {"bom-ref": "vex:example-0002", "id": "PKIC-EXAMPLE-2026-0002", "source": src,
             "description": "Illustrative: a timing side channel in RSA PKCS#1 v1.5 decryption in the Java runtime.",
             "analysis": {"state": "not_affected", "justification": "requires_configuration",
                          "detail": "Exploitation needs RSA key transport cipher suites. The image's TLS "
                                    "configuration offers TLS 1.3 suites only, which use no RSA key transport "
                                    "(see the shared TLS configuration in the product record)."},
             "affects": [{"ref": sbom_ref("lib:openjdk"), "versions": [{"version": "21", "status": "affected"}]}]},
            {"bom-ref": "vex:example-0003", "id": "PKIC-EXAMPLE-2026-0003", "source": src,
             "description": "Illustrative: a request smuggling flaw in the HTTP server layer.",
             "analysis": {"state": "in_triage",
                          "detail": "Under analysis. The plaintext listener is off by default; deployments "
                                    "behind a proxy with it enabled are the exposed case."},
             "affects": [{"ref": sbom_ref("lib:quarkus-vertx-http")}]},
        ],
    }


def configuration_guidance():
    """Where an operator sets each value the product leaves open."""
    p = lambda r: link("product", r)
    return {
        "guidanceFormat": "pkic.example.configuration-guidance", "version": "0.1",
        "$comment": ("EXAMPLE. Configuration guidance for the Keycloak 26.7.3 image, as a supplier could "
                     "publish it beside its product record. The record points here under "
                     "interface-disclosure#R5 from every interface whose certificate is 'deployment-defined', "
                     "and from the record as a whole. Each entry names the interface by a BOM-Link into the "
                     "product record, the attribute the operator decides, the setting that decides it, and the "
                     "supplier's documentation. The option names are Keycloak's; the format is an "
                     "illustration, not a standard. The CBOM does not carry this content: it changes when the "
                     "documentation changes, not when the product does."),
        "subject": PRODUCT_PURL,
        "entries": [
            {"interface": p("crypto:protocol:tls-https"), "attribute": "authentication",
             "decidedBy": "operator",
             "settings": [{"kind": "server-option", "name": "https-certificate-file"},
                          {"kind": "server-option", "name": "https-certificate-key-file"}],
             "note": "The server certificate and key are operator-supplied files. Their algorithm is the "
                     "interface's authentication value at 'configured'.",
             "documentation": "https://www.keycloak.org/server/enabletls"},
            {"interface": p("crypto:protocol:tls-https"), "attribute": "keyExchange",
             "decidedBy": "operator",
             "settings": [{"kind": "jvm-property", "name": "jdk.tls.namedGroups"}],
             "note": "The product default is the JDK's group order. A hybrid ML-KEM group can be enabled "
                     "here only once the JDK in the image supports one.",
             "documentation": "https://www.keycloak.org/server/enabletls"},
            {"interface": p("crypto:protocol:tls-mgmt"), "attribute": "authentication",
             "decidedBy": "operator",
             "settings": [{"kind": "server-option", "name": "http-management-scheme"}],
             "note": "Defaults to 'inherited': the management listener uses the main server's scheme and "
                     "certificate. With HTTP on the main server it is plain HTTP.",
             "documentation": "https://www.keycloak.org/server/management-interface"},
            {"interface": p("service:svc-http"), "attribute": "defaultState",
             "decidedBy": "operator",
             "settings": [{"kind": "server-option", "name": "http-enabled"},
                          {"kind": "server-option", "name": "proxy-headers"}],
             "note": "Off by default. Enabled behind a TLS-terminating proxy, it carries tokens in clear on "
                     "the proxy hop.",
             "documentation": "https://www.keycloak.org/server/reverseproxy"},
            {"interface": p("crypto:protocol:int-db"), "attribute": "authentication",
             "decidedBy": "peer",
             "settings": [{"kind": "server-option", "name": "db-url"}],
             "note": "The database server's certificate decides the value; set sslmode=verify-full in the "
                     "JDBC URL so the driver verifies it.",
             "documentation": "https://www.keycloak.org/server/db"},
            {"interface": p("crypto:protocol:int-cache"), "attribute": "authentication",
             "decidedBy": "product",
             "settings": [{"kind": "server-option", "name": "cache-embedded-mtls-enabled"}],
             "note": "The product generates and rotates the RSA-2048 key; the operator can switch mutual TLS "
                     "off, not change the key type.",
             "documentation": "https://www.keycloak.org/server/caching"},
            {"interface": p("service:svc-oidc"), "attribute": "authentication",
             "decidedBy": "operator",
             "settings": [{"kind": "realm-attribute", "name": "defaultSignatureAlgorithm"},
                          {"kind": "client-attribute", "name": "access.token.signed.response.alg"}],
             "note": "The realm default is RS256. A client can override it.",
             "documentation": "https://www.keycloak.org/docs/latest/server_admin/#realm_keys"},
        ],
    }


def roadmap():
    """The supplier's own statement of planned post-quantum availability."""
    p = lambda r: link("product", r)
    return {
        "roadmapFormat": "pkic.example.roadmap", "version": "0.1", "asOf": "2026-10-25",
        "$comment": ("EXAMPLE. A post-quantum roadmap for the Keycloak image, as a supplier could publish "
                     "it. The product record points here under pqc-migration#R2. The record itself states "
                     "each purpose's capability as a status and a blocker, never a date (decision 0007); a "
                     "roadmap is where a supplier may name a target release, and the record points to it "
                     "without evaluating it. Each item agrees with the record's capabilityByPurpose entries. "
                     "Target releases and tracking links are those in the public sources; the format is an "
                     "illustration, not a standard, and the document is not a statement by the Keycloak "
                     "project."),
        "subject": PRODUCT_PURL,
        "items": [
            {"id": "ml-dsa-token-signing", "purpose": "entity-authentication",
             "interfaces": [p("service:svc-oidc"), p("service:mgmt-admin"), p("service:svc-broker-tokens")],
             "algorithms": ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
             "capabilityStatus": "committed", "blockedBy": "standard", "targetRelease": "27.0",
             "dependsOn": [{"what": "ML-DSA in JOSE, including the AKP JWK key type",
                            "status": "Internet-Draft",
                            "ref": "https://datatracker.ietf.org/doc/draft-ietf-cose-dilithium/"}],
             "tracking": "https://github.com/keycloak/keycloak/issues/43690",
             "note": "ML-DSA-65 signed tokens exceed the 4 KB browser cookie limit; relying parties must "
                     "accept the AKP key type."},
            {"id": "hybrid-key-exchange-tls", "purpose": "key-establishment",
             "interfaces": [p("crypto:protocol:tls-https"), p("crypto:protocol:tls-mgmt"),
                            p("crypto:protocol:int-db"), p("crypto:protocol:int-ldap"),
                            p("crypto:protocol:int-broker"), p("crypto:protocol:int-smtp"),
                            p("crypto:protocol:int-cache")],
             "algorithms": ["X25519MLKEM768"],
             "capabilityStatus": "planned", "blockedBy": "provider", "targetRelease": None,
             "dependsOn": [{"what": "A Java runtime with hybrid ML-KEM TLS groups (JEP 527)",
                            "status": "in JDK 27", "ref": "https://openjdk.org/jeps/527"}],
             "note": "Available when the image ships a JDK that offers the hybrid groups; no Keycloak release "
                     "is named."},
            {"id": "saml-ml-dsa", "purpose": "entity-authentication",
             "interfaces": [p("service:svc-saml")], "algorithms": [],
             "capabilityStatus": "under-evaluation", "blockedBy": "standard", "targetRelease": None,
             "dependsOn": [{"what": "ML-DSA identifiers for XML Signature", "status": "not standardised"}]},
            {"id": "realm-key-encryption", "purpose": "key-protection",
             "interfaces": [p("service:sto-realm-keys")], "algorithms": [],
             "capabilityStatus": "not-planned", "blockedBy": "product", "targetRelease": None,
             "tracking": "https://github.com/keycloak/keycloak/issues/39933",
             "note": "Realm key material is stored in the database in plaintext; the request to encrypt it "
                     "has no milestone."},
        ],
    }


def context_artifacts():
    """Write the context documents and return their SHA-256 digests."""
    return {"sbom": write_context("keycloak-26.7.3-sbom.cdx.json", sbom(), convert=True),
            "vex": write_context("keycloak-26.7.3-vex.cdx.json", vex()),
            "guidance": write_context("keycloak-configuration-guidance.json", configuration_guidance()),
            "roadmap": write_context("keycloak-pqc-roadmap.json", roadmap())}


# --------------------------------------------------------------------------- #
# Stage 2: implemented. The vendor's build record of the image.               #
# --------------------------------------------------------------------------- #
def product(hashes):
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
        "the companion SBOM, an illustrative VEX document, the advisory sources, the security contact, "
        "configuration guidance and a post-quantum roadmap, each a file under examples/context/. Conforms to interface-enumeration v0.3, interface-disclosure "
        "v0.9, pqc-migration v0.8, pqc-migration-extended v0.1 and procurement v0.1.")
    md = bom["metadata"]
    md["timestamp"] = "2026-10-25T09:00:00Z"
    md["lifecycles"] = [{"phase": "build"}]
    comp = md["component"]
    comp["description"] = ("Keycloak 26.7.3 container image at its defaults. Build record: what the image "
                           "does before anyone deploys it.")
    set_props(comp, {"subjectType": "product",
                     "contextAbsent:support-lifecycle": "not-published"})
    bom["externalReferences"] = [
        ctx("sbom", link("sbom"), "bom",
            "Companion SBOM of the same image: examples/context/keycloak-26.7.3-sbom.cdx.json.",
            sha256=hashes["sbom"]),
        ctx("vulnerability-statements", link("vex"), "vulnerability-assertion",
            "The supplier's VEX: examples/context/keycloak-26.7.3-vex.cdx.json. Illustrative: the upstream "
            "project publishes no VEX, and the identifiers in it are not CVEs.", protocol="vex-document",
            sha256=hashes["vex"]),
        ctx("advisories", "https://github.com/keycloak/keycloak/security/advisories", "advisories",
            "Keycloak security advisories (GitHub Security Advisories).", protocol="web-page"),
        ctx("advisories", "https://api.osv.dev/v1/query", "advisories",
            "OSV API. Query with the package URLs in this document, for example "
            "pkg:maven/org.keycloak/keycloak-services@26.7.3. OSV aggregates the GitHub advisories.",
            protocol="osv-api"),
        ctx("security-contact", "https://github.com/keycloak/keycloak/security/policy", "security-contact",
            "Keycloak security policy: how to report a vulnerability.", protocol="web-page"),
        ctx("configuration-guidance", SITE + "context/keycloak-configuration-guidance.json", "configuration",
            "Where the operator sets each value this record leaves open, interface by interface.",
            sha256=hashes["guidance"]),
        ctx("roadmap", SITE + "context/keycloak-pqc-roadmap.json", "documentation",
            "The supplier's post-quantum roadmap. Target releases live there, not in this record.",
            sha256=hashes["roadmap"]),
    ]
    # Each library points at its entry in the companion SBOM.
    for c in bom["components"]:
        if c.get("type") == "library":
            c["externalReferences"] = [{"type": "bom", "url": link("sbom", c["bom-ref"]),
                                        "comment": "This library's entry in the companion SBOM."}]

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
            el["externalReferences"] = [
                ctx("configuration-guidance", guidance[ref], "documentation",
                    "Where the operator sets the server certificate and key.", protocol="web-page"),
                ctx("configuration-guidance", SITE + "context/keycloak-configuration-guidance.json",
                    "configuration", "The same setting in the supplier's machine-readable guidance.",
                    sha256=hashes["guidance"])]
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
        "The ingress has no product CBOM, so its library is stated here. Conforms to "
        "deployment-disclosure v0.1.",
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
        "through it to the product. Conforms to deployment-disclosure v0.1.",
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


def variant(bom, serial_suffix, comment):
    v = copy.deepcopy(bom)
    v["serialNumber"] = v["serialNumber"][:-4] + serial_suffix
    v["$comment"] = comment
    return v


def element(bom, ref):
    for el in bom.get("components", []) + bom.get("services", []):
        if el.get("bom-ref") == ref:
            return el
    raise KeyError(ref)


def drop_props(el, *names):
    el["properties"] = [p for p in el.get("properties", []) if p["name"][len(P):] not in names]


def remove_elements(bom, refs):
    bom["components"] = [c for c in bom["components"] if c.get("bom-ref") not in refs]
    bom["services"] = [c for c in bom.get("services", []) if c.get("bom-ref") not in refs]
    for d in bom.get("dependencies", []):
        for key in ("dependsOn", "provides"):
            if key in d:
                d[key] = [x for x in d[key] if x not in refs]
    for c in bom.get("compositions", []):
        c["assemblies"] = [x for x in c.get("assemblies", []) if x not in refs]
    for el in bom["components"] + bom.get("services", []):
        drop = [p for p in el.get("properties", []) if p["name"] == P + "keyStoreRef" and p["value"] in refs]
        el["properties"] = [p for p in el.get("properties", []) if p not in drop]


def scanner_output():
    """What a network scanner typically emits: assets, no profile facts."""
    return {
        "bomFormat": "CycloneDX", "specVersion": "1.7",
        "serialNumber": "urn:uuid:6b3c1d2e-7a41-4c1e-9f0a-2673000005c0", "version": 1,
        "metadata": {"timestamp": "2026-10-25T07:00:00Z",
                     "tools": {"components": [{"type": "application", "name": "generic TLS scanner", "version": "1.0"}]},
                     "component": {"type": "application", "name": "sso.example.org", "version": "unknown"},
                     "properties": [{"name": "pkic:example:comment", "value":
                         "NON-CONFORMING EXAMPLE, CycloneDX 1.7. Untargeted scanner output for the same host: two "
                         "TLS endpoints and their algorithms, with no profile facts. It declares no interface "
                         "(nothing carries interfaceType), does not identify its subject, states no coverage, no "
                         "subject type and no lifecycle stage. It fails the entry profile on P1, P3, P4, P5 and P6. "
                         "Every fact in it is useful, and none of it is yet an inventory record."}]},
        "components": algo_components(["x25519", "aes-256-gcm", "ecdsa-p256"]) + [
            {"type": "cryptographic-asset", "bom-ref": "crypto:protocol:443", "name": "TLS on port 443",
             "cryptoProperties": {"assetType": "protocol", "protocolProperties": {
                 "type": "tls", "version": "1.3",
                 "cryptoRefArray": ["crypto:algo:x25519", "crypto:algo:aes-256-gcm", "crypto:algo:ecdsa-p256"]}}},
            {"type": "cryptographic-asset", "bom-ref": "crypto:protocol:9000", "name": "HTTP on port 9000",
             "cryptoProperties": {"assetType": "protocol", "protocolProperties": {"type": "other"}}}],
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    hashes = context_artifacts()
    prod = product(hashes)
    sha_p = write("cbom-keycloak-product.cdx.json", prod)

    legacy = copy.deepcopy(prod)
    legacy["serialNumber"] = "urn:uuid:" + SERIAL["legacy"]
    legacy["$comment"] = ("LEGACY EXAMPLE, CycloneDX 1.7. The Keycloak product record in the form today's "
                          "tools emit. Same facts as cbom-keycloak-product.cdx.json (CycloneDX 2.0). It is "
                          "evaluated and flagged legacy, and gets the same verdicts.")
    write("legacy/cbom-keycloak-product-1.7.cdx.json", legacy, legacy=True)

    v = variant(prod, "c0f5", "NON-CONFORMING EXAMPLE. The product record, except that the HTTPS listener "
                "states its certificate is deployment-defined without pointing to where the operator sets "
                "it. Fails interface-disclosure#R5 on that interface only.")
    element(v, "crypto:protocol:tls-https").pop("externalReferences")
    write("cbom-keycloak-product-fail-R5.cdx.json", v)

    v = variant(prod, "c0f2", "NON-CONFORMING EXAMPLE. The product record with both management interfaces "
                "(the Admin REST API and the management listener) left out and no reason stated. Every "
                "interface it does declare is complete. Fails interface-disclosure#P2: the interface most "
                "often omitted is the one the rule exists to catch.")
    remove_elements(v, {"service:mgmt-admin", "crypto:protocol:tls-mgmt"})
    write("cbom-keycloak-product-fail-P2.cdx.json", v)

    v = variant(prod, "c0d5", "NON-CONFORMING EXAMPLE. The product record exercising the four disclosure "
                "outcomes. Most values are supplied. The OIDC interface withholds its implementing library, "
                "which the baseline permits (I9 is withholdable). It states that no VEX is published, which "
                "satisfies R2 as a stated absence. The cluster transport declares its "
                "authentication unknown, and the SAML interface leaves its encryption undeclared; "
                "neither satisfies a MUST rule. Fails interface-disclosure#I5 and #I4, and conforms to the "
                "entry profile, which asks for neither.")
    for d in v["dependencies"]:
        if "provides" in d:
            d["provides"] = [x for x in d["provides"] if x != "service:svc-oidc"]
    element(v, "service:svc-oidc")["properties"].append(prop("disclosure:implementationPurl", "withheld"))
    cache = element(v, "crypto:protocol:int-cache")
    cache["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = [
        r for r in cache["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] if r != "crypto:algo:rsa-2048"]
    cache["properties"].append(prop("disclosure:authentication", "unknown"))
    drop_props(element(v, "service:svc-saml"), "encryption")
    # It also states, instead of pointing to a VEX, that none is published: a stated absence
    # satisfies interface-disclosure#R2, which is the true position of the upstream project.
    v["externalReferences"] = [r for r in v["externalReferences"]
                               if not any(p["value"] == "vulnerability-statements" for p in r.get("properties", []))]
    v["metadata"]["component"]["properties"].append(prop("contextAbsent:vulnerability-statements", "not-published"))
    write("cbom-keycloak-product-disclosure-states.cdx.json", v)

    v = variant(prod, "c0e1", "NON-CONFORMING EXAMPLE. The product record with the storage interface's "
                "key-wrapping capability left out. Fails pqc-migration#I12 only: the migration profile asks "
                "what protection a key store could offer, not only what it offers today.")
    drop_props(element(v, "service:sto-realm-keys"), "keyWrappingSupported")
    write("cbom-keycloak-product-fail-pqc-I12.cdx.json", v)

    v = variant(prod, "c0e3", "NON-CONFORMING EXAMPLE. The product record with the key types the Admin "
                "REST API can generate left out. Fails pqc-migration-extended#I3 only: the operator cannot "
                "tell whether the key management surface can create an ML-DSA key.")
    drop_props(element(v, "service:mgmt-admin"), "keyTypesSupported")
    write("cbom-keycloak-product-fail-ext-I3.cdx.json", v)

    v = variant(prod, "c0b5", "NON-CONFORMING EXAMPLE. The product record with the storage interface left "
                "out and no reason stated. Fails procurement#P5 only: a tender response describes the paths "
                "traffic crosses and stays silent about where keys are kept.")
    remove_elements(v, {"service:sto-realm-keys"})
    write("cbom-keycloak-product-fail-procurement-P5.cdx.json", v)

    write("cbom-keycloak-product-intended.cdx.json", intended(prod))

    write("legacy/cbom-keycloak-scanner-output.cdx.json", scanner_output(), legacy=True)

    conf = configured(sha_p)
    sha_c = write("cbom-keycloak-deployment-configured.cdx.json", conf)

    v = variant(conf, "0ff5", "NON-CONFORMING EXAMPLE. The configured record, except that the database "
                "connection still says 'peer-defined', as the product record does. At 'configured' the "
                "operator holds the answer. Fails interface-disclosure#I3, I4 and I5 on that interface.")
    db = element(v, "crypto:protocol:int-db")
    db["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = []
    for a in ("keyExchange", "encryption", "authentication"):
        db["properties"].append(prop(a, "peer-defined"))
    write("cbom-keycloak-deployment-configured-fail-literal.cdx.json", v)

    obs = observed(sha_p, sha_c)
    write("cbom-keycloak-deployment-observed.cdx.json", obs)

    v = variant(obs, "5ef5", "NON-CONFORMING EXAMPLE. The observed record, except that the database "
                "connection was observed through pg_stat_ssl alone, which does not report the group. "
                "keyExchange is declared unknown. Fails interface-disclosure#I3 on that interface, and "
                "conforms to the entry profile: a record with gaps lands one depth down.")
    db = element(v, "crypto:protocol:int-db")
    db["cryptoProperties"]["protocolProperties"]["cryptoRefArray"] = ["crypto:algo:aes-256-gcm", "crypto:algo:rsa-2048"]
    drop_props(db, "observationMethod", "observationSummary")
    db["properties"] += [prop("observationMethod", "platform-query"), prop("observationMethod", "active-probe"),
                         prop("disclosure:keyExchange", "unknown")]
    write("cbom-keycloak-deployment-observed-fail-unknown.cdx.json", v)

    v = observed(sha_p, sha_c, configured_hash_override=illustrative_hash("configured-revision-before-edit"))
    v["serialNumber"] = v["serialNumber"][:-4] + "5ef6"
    v["$comment"] = ("NON-CONFORMING EXAMPLE. The observed record, except that the hash it records for the "
                     "configured record does not match that record. This is what a consumer sees when the "
                     "configured record is revised after the observation cited it. Fails "
                     "deployment-disclosure#P1.")
    write("cbom-keycloak-deployment-observed-fail-P1.cdx.json", v)

    v = variant(obs, "5ef7", "NON-CONFORMING EXAMPLE. An observation from outside the deployment, by an "
                "assessor who could not reach the management interfaces and has no configured record to "
                "cite. The management interfaces are absent, stated as 'not-reached', with coverage "
                "'partial': P2 passes through its second route. The assessor cannot see which library "
                "terminates TLS at the ingress, and there is no product record to inherit it from, so the "
                "ingress fails interface-disclosure#I9. The record conforms to the entry profile. An "
                "outside observation is an enumeration-depth record unless the observer can name the "
                "libraries.")
    remove_elements(v, {"service:mgmt-health", "service:mgmt-admin"})
    v["externalReferences"] = [r for r in v["externalReferences"] if r.get("url", "").find(SERIAL["configured"]) < 0]
    for el in v["components"] + v["services"]:
        for p in el.get("properties", []):
            if p["name"] == P + "correspondsTo" and SERIAL["configured"] in p["value"]:
                p["value"] = "no-product-document" if "ing-tls" in p["value"] else \
                    link("product", {"service:svc-http": "service:svc-http", "service:svc-oidc": "service:svc-oidc",
                                     "service:svc-saml": "service:svc-saml", "crypto:protocol:int-db": "crypto:protocol:int-db",
                                     "crypto:protocol:int-ldap": "crypto:protocol:int-ldap",
                                     "crypto:protocol:int-cache": "crypto:protocol:int-cache",
                                     "service:sto-realm-keys": "service:sto-realm-keys"}[el["bom-ref"]])
    v["metadata"]["component"]["properties"].append(prop("managementInterfaceAbsence", "not-reached"))
    write("cbom-keycloak-deployment-observed-outside.cdx.json", v)
    results()
    print("written to", os.path.abspath(OUT))


EVALUATION_DATE = "2026-10-25"


def results():
    """Policy results over the examples, at a fixed evaluation date so they reproduce."""
    import evaluate_policy
    pol = os.path.join(ROOT, "docs", "methodology", "policies")
    res = os.path.join(OUT, "results")
    os.makedirs(res, exist_ok=True)
    ex = lambda n: os.path.join(OUT, n)
    runs = {
        "result-readiness-gap-sso-prod.json": (
            "policy-readiness-gap.policy.json",
            ["cbom-keycloak-product.cdx.json", "cbom-keycloak-deployment-configured.cdx.json",
             "cbom-keycloak-deployment-observed.cdx.json"]),
        "result-algorithm-transition-keycloak-product.json": (
            "policy-algorithm-transition.policy.json", ["cbom-keycloak-product.cdx.json"]),
        "result-algorithm-transition-sso-prod-observed.json": (
            "policy-algorithm-transition.policy.json",
            ["cbom-keycloak-deployment-observed.cdx.json"]),
    }
    for name, (policy, docs) in runs.items():
        result = evaluate_policy.evaluate(os.path.join(pol, policy), [ex(d) for d in docs], EVALUATION_DATE)
        with open(os.path.join(res, name), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
