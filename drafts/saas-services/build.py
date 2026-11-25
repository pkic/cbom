#!/usr/bin/env python3
"""Build the draft service profiles of the SaaS domain document and their examples.

Writes, in this folder:
  profile-service-key-custody.rules.json        key-custody depth (SaaS document 8.4), v0.1-draft
  profile-service-change-planning.rules.json    service change planning (8.5), v0.1-draft
  profile-tenant-disclosure.rules.json          the tenant record (8.6), v0.1-draft
  examples/cbom-keycloak-service-key-custody.cdx.json             conforms to the depth
  examples/cbom-keycloak-service-key-custody-fail-replica.cdx.json   no replicaProtection on the realm-key store
  examples/cbom-keycloak-service-change-planning.cdx.json         conforms to service change planning
  examples/cbom-keycloak-tenant-configured.cdx.json               one tenant of the managed service
  examples/cbom-keycloak-tenant-fail-custody.cdx.json             the tenant record without its custody choice

All records start from the published restricted service record,
docs/methodology/examples/cbom-keycloak-service-restricted.cdx.json. The change-planning record
takes its capability facts from the Keycloak product record, interface by interface. Values
are illustrative.

Draft only. Nothing in docs/methodology/ is changed.

Usage: python3 drafts/saas-services/build.py
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
EX = os.path.join(ROOT, "docs", "methodology", "examples")
METH = "../../docs/methodology/"
P = "pkic:profile:"
STAMP = "2026-11-18T09:00:00Z"


def load(name):
    with open(os.path.join(EX, name), "rb") as f:
        data = f.read()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def write(rel, obj):
    data = (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with open(os.path.join(HERE, rel), "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def setprop(obj, name, value):
    ps = obj.setdefault("properties", [])
    ps[:] = [p for p in ps if p["name"] != P + name]
    for v in (value if isinstance(value, list) else [value]):
        ps.append({"name": P + name, "value": v})


def delprop(obj, name):
    obj["properties"] = [p for p in obj.get("properties", []) if p["name"] != P + name]


def getprops(obj, prefix):
    return [p for p in obj.get("properties", []) if p["name"].startswith(P + prefix)]


def comp(doc, ref):
    for c in doc["inventories"][0]["components"]:
        if c.get("bom-ref") == ref:
            return c
    raise KeyError(ref)


def ifaces(doc):
    return [c for c in doc["inventories"][0]["components"] if getprops(c, "interfaceType")]


def carry_libraries(d, prod, ref_of):
    """Copy the product record's libraries into d, with 'provides' mapped onto d's interfaces.
    ref_of maps a product interface bom-ref to the bom-refs of d that realise it."""
    have = {c.get("bom-ref") for c in d["inventories"][0]["components"]}
    for c in prod["inventories"][0]["components"]:
        if c.get("type") == "library" and c["bom-ref"] not in have:
            d["inventories"][0]["components"].append(copy.deepcopy(c))
    for x in prod.get("dependencies", []):
        if x["ref"].startswith("lib:") and "provides" in x:
            mapped = [r for pr in x["provides"] for r in ref_of.get(pr, [])]
            if mapped:
                d.setdefault("dependencies", []).append({"ref": x["ref"], "provides": mapped})


def product_refs(d):
    out = {}
    for c in ifaces(d):
        corr = getprops(c, "correspondsTo")
        if corr and "#" in corr[0]["value"]:
            out.setdefault(corr[0]["value"].split("#", 1)[1], []).append(c["bom-ref"])
    return out


INGRESS_FACTS = [
    ("protocolVersionsSupported", ["1.2", "1.3"]),
    ("keyExchangeSupported", ["X25519MLKEM768", "X25519", "ECDH-P256"]),
    ("authenticationSupported", ["ECDSA-P256-SHA256", "RSA-PSS-2048-SHA256"]),
    ("enablementMethod", "already-enabled"), ("coexistence", "simultaneous"),
    ("capabilityByPurpose:key-establishment:capabilityStatus", "available"),
    ("capabilityByPurpose:encryption:capabilityStatus", "available"),
    ("capabilityByPurpose:entity-authentication:capabilityStatus", "under-evaluation"),
    ("capabilityByPurpose:entity-authentication:blockedBy", "standard"),
    ("capabilityByPurpose:data-integrity:capabilityStatus", "available"),
    ("capabilityByPurpose:non-repudiation:capabilityStatus", "not-planned"),
    ("capabilityByPurpose:non-repudiation:blockedBy", "product"),
    ("capabilityByPurpose:key-protection:capabilityStatus", "not-planned"),
    ("capabilityByPurpose:key-protection:blockedBy", "product"),
    ("capabilityByPurpose:key-derivation:capabilityStatus", "available")]


MODULE_VALIDATION = ["fips-140-2", "fips-140-3", "iso-19790", "national-crypto-approval", "none"]
CUSTODY = ["provider-managed", "customer-managed", "external"]


# --------------------------------------------------------------------------- #
# Profiles                                                                    #
# --------------------------------------------------------------------------- #
def key_custody_profile():
    return {
        "$comment": "DRAFT. A depth on Service Disclosure, Restricted, for a customer whose main concern is stored "
                    "data. On every storage interface it asks which key service holds the keys, whether backups and "
                    "replicas are protected as the live data is, and the key service's module validation. The "
                    "algorithms that wrap the data keys are already required by the baseline (keyWrapping).",
        "profileId": "pkic.example.service-key-custody",
        "profileTag": "service-key-custody",
        "title": "Service Key Custody (Example, draft)",
        "version": "0.1-draft",
        "objective": {
            "consumer": "A customer under agreement whose main concern is the data it stores in the service",
            "decision": "Which custody model to use for which data, and whether to place a data set in the service at all",
            "decisionOptions": ["place the data under the default custody", "place it under another custody model",
                                "do not place it in the service"]},
        "scope": {"subjectTypes": ["service"], "orientation": "both", "relationshipTypes": ["interface"],
                  "lifecycleStages": ["configured", "observed"]},
        "extends": {"profileId": "pkic.example.service-disclosure-restricted", "version": "0.1",
                    "file": METH + "profile-service-disclosure-restricted.rules.json"},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "replicaProtectionVocabulary": ["same-as-primary", "differs-from-primary", "no-replicas"],
        "moduleValidationSchemeVocabulary": MODULE_VALIDATION,
        "productRules": [],
        "interfaceRules": [
            {"id": "I1", "attribute": "keyStoreRef", "level": "MUST",
             "constraint": {"refersToLocal": {"literals": ["none", "out-of-band", "product-managed"],
                                              "orCited": True}}, "withholdable": False,
             "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
             "note": "The interface of the key service that holds the keys protecting this store: a component of "
                     "the same record, or a BOM-Link to one in a record this document cites. 'out-of-band' where "
                     "the keys are held outside any record, such as the tenant's own key service; 'none' where no "
                     "key service is involved. The literals are those of PQC Migration Extended I8 (R2-22)."},
            {"id": "I2", "attribute": "replicaProtection", "level": "MUST",
             "constraint": {"enumRef": "replicaProtectionVocabulary"}, "withholdable": False,
             "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
             "note": "Whether backups and copies replicated between regions use the same custody and wrapping as "
                     "the live data."},
            {"id": "I3", "attribute": "moduleValidationScheme", "level": "SHOULD",
             "constraint": {"enumRef": "moduleValidationSchemeVocabulary"}, "withholdable": True,
             "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
             "note": "The validation of the module that holds the keys, with the vocabulary of PQC Migration."}],
        "referenceRules": [],
        "exclusions": [
            {"item": "How long the stored data must stay confidential",
             "reason": "The customer's fact. It belongs in the customer's data register, linked from the tenant record."}],
        "artifacts": {"conformingExample": "examples/cbom-keycloak-service-key-custody.cdx.json",
                      "nonConformingExample": "examples/cbom-keycloak-service-key-custody-fail-replica.cdx.json"},
        "changelog": [{"version": "0.1-draft", "date": "2026-11-18",
                       "summary": "First draft, built on Keycloak run as a managed service.", "changes": []}]}


def change_planning_profile():
    return {
        "$comment": "DRAFT. Service change planning: the change core applied to a managed service, for customers "
                    "planning around the provider's post-quantum work. It narrows the change core to the subject "
                    "type 'service' and the stage 'configured', and asks the record to cite the records it builds "
                    "on. It adds no attribute: capability, blocker and roadmap per purpose apply to a service "
                    "endpoint as they do to a product interface.",
        "profileId": "pkic.example.service-change-planning",
        "profileTag": "service-change-planning",
        "title": "Service Change Planning (Example, draft)",
        "version": "0.1-draft",
        "objective": {
            "consumer": "A customer, or its migration lead, that relies on a service it does not run",
            "decision": "When the service can move to post-quantum cryptography, and what the customer must change itself",
            "decisionOptions": ["plan around the provider's roadmap", "ask the provider for a commitment",
                                "plan a move away from the service"]},
        "scope": {"subjectTypes": ["service"], "orientation": "migration", "relationshipTypes": ["interface"],
                  "lifecycleStages": ["configured"]},
        "extends": {"profileId": "pkic.example.change-core", "version": "0.2",
                    "file": METH + "profile-change-core.rules.json"},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "productRules": [
            {"id": "P1", "description": "Service cites the records it builds on, each by BOM-Link and hash", "level": "MUST",
             "constraint": {"citesDocuments": {"min": 1, "hashRequired": True}}, "withholdable": False,
             "note": "The provider's service record and the product records of the software it runs. A customer "
                     "reads the capability facts here beside the present state there."}],
        "interfaceRules": [],
        "referenceRules": [],
        "exclusions": [
            {"item": "The customer's own migration plan",
             "reason": "A customer fact. It belongs in the customer's migration register."}],
        "artifacts": {"conformingExample": "examples/cbom-keycloak-service-change-planning.cdx.json"},
        "changelog": [{"version": "0.1-draft", "date": "2026-11-18",
                       "summary": "First draft, built on Keycloak run as a managed service.", "changes": []}]}


def tenant_profile():
    return {
        "$comment": "DRAFT. The tenant record: a deployment record for one tenant of a managed service, citing the "
                    "service record. It extends Deployment Disclosure with the tenant's choice of key custody on "
                    "every storage interface and, for external keys, the key service that holds them.",
        "profileId": "pkic.example.tenant-disclosure",
        "profileTag": "tenant-disclosure",
        "title": "Tenant Disclosure (Example, draft)",
        "version": "0.1-draft",
        "objective": {
            "consumer": "A customer's security team, or an auditor acting for it",
            "decision": "Whether the tenant's settings protect each data set as the customer's policy requires",
            "decisionOptions": ["accept the settings", "change the settings", "move the data"]},
        "scope": {"subjectTypes": ["deployment"], "orientation": "inventory", "relationshipTypes": ["interface"],
                  "lifecycleStages": ["configured", "observed"]},
        "extends": {"profileId": "pkic.example.deployment-disclosure", "version": "0.3",
                    "file": METH + "profile-deployment-disclosure.rules.json"},
        "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
        "keyCustodyVocabulary": CUSTODY,
        "productRules": [],
        "interfaceRules": [
            {"id": "I1", "attribute": "keyCustody", "level": "MUST", "constraint": {"enumRef": "keyCustodyVocabulary"},
             "withholdable": False, "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
             "note": "The custody model the tenant chose for this store. It should be one the service record offers "
                     "(keyCustodySupported); the evaluator does not compare the two records."},
            {"id": "I2", "attribute": "externalKeyService", "level": "MUST",
             "constraint": {"refersToCited": {}}, "withholdable": False,
             "requiredWhen": {"attribute": "keyCustody", "equals": "external"},
             "note": "The interface of the tenant's own key service, in a record the tenant record cites."}],
        "referenceRules": [],
        "exclusions": [
            {"item": "What the data is and how long it must stay confidential",
             "reason": "The customer's data register holds it, linked by the context kind data-register."}],
        "artifacts": {"conformingExample": "examples/cbom-keycloak-tenant-configured.cdx.json",
                      "nonConformingExample": "examples/cbom-keycloak-tenant-fail-custody.cdx.json"},
        "changelog": [{"version": "0.1-draft", "date": "2026-11-18",
                       "summary": "First draft, built on one tenant of the Keycloak managed service.", "changes": []}]}


# --------------------------------------------------------------------------- #
# Records                                                                     #
# --------------------------------------------------------------------------- #
def key_custody_record(svc, serial, with_replica=True):
    d = copy.deepcopy(svc)
    d["serialNumber"] = "urn:uuid:" + serial
    d["metadata"]["timestamp"] = STAMP
    st = comp(d, "service:sto-realm-keys")
    setprop(st, "keyStoreRef", "service:mgmt-admin")
    if with_replica:
        setprop(st, "replicaProtection", "same-as-primary")
    setprop(st, "moduleValidationScheme", "none")
    setprop(st, "integrationConstraints",
            "Realm keys are held in the database without wrapping. The database is replicated between the two "
            "regions with the same storage encryption. No key service is in front of it.")
    d["$comment"] = ("DRAFT EXAMPLE. The restricted Keycloak service record with the key-custody depth's facts on "
                     "the realm-key store. Values are illustrative." +
                     ("" if with_replica else " NON-CONFORMING: replicaProtection removed from the realm-key store."))
    return d


def change_planning_record(svc, svc_hash, prod, prod_hash, serial):
    d = copy.deepcopy(svc)
    d["serialNumber"] = "urn:uuid:" + serial
    d["metadata"]["timestamp"] = STAMP
    d["$comment"] = ("DRAFT EXAMPLE. Keycloak run as a managed service, with the change core's capability facts. "
                     "Each interface takes them from the product interface it realises. Values are illustrative.")
    subj = d["inventories"][0]["subject"]
    setprop(subj, "updateMechanism", "provider-managed")
    prod_url = prod["serialNumber"].replace("urn:uuid:", "urn:cdx:") + "/%d" % prod["version"]
    carry = ("protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported", "enablementMethod",
             "minimumProductVersion", "coexistence", "negotiationControl", "capabilityByPurpose:")
    for c in ifaces(d):
        corr = getprops(c, "correspondsTo")
        if corr and "#" in corr[0]["value"]:
            src = comp(prod, corr[0]["value"].split("#", 1)[1])
            for p in src.get("properties", []):
                short = p["name"][len(P):]
                if short.startswith(carry) and not any(q["name"] == p["name"] and q["value"] == p["value"]
                                                       for q in c["properties"]):
                    c["properties"].append(dict(p))
            for rel in src.get("cryptoProperties", {}).get("protocolProperties", {}).get("relatedCryptographicAssets", []):
                if rel.get("type") == "protocol-configuration":
                    suites = comp(prod, rel["ref"])["cryptoProperties"]["protocolProperties"].get("cipherSuites", [])
                    groups = sorted({g for cs in suites for g in cs.get("tlsGroups", [])})
                    schemes = sorted({x for cs in suites for x in cs.get("tlsSignatureSchemes", [])})
                    if not getprops(c, "keyExchangeSupported"):
                        setprop(c, "keyExchangeSupported", groups)
                    if not getprops(c, "authenticationSupported"):
                        setprop(c, "authenticationSupported", schemes)
        if getprops(c, "interfaceType")[0]["value"] == "management":
            setprop(c, "updateMechanism", "provider-managed")
            setprop(c, "updateAuthority", "operator")
        if getprops(c, "interfaceType")[0]["value"] == "storage":
            setprop(c, "keyReplaceable", "in-field")
    # The libraries, and the per-purpose facts they carry, from the product record.
    carry_libraries(d, prod, product_refs(d))
    # The ingress is the provider's own; its facts are stated here.
    ing = comp(d, "crypto:protocol:ing-tls")
    for k, v in INGRESS_FACTS:
        setprop(ing, k, v)
    svc_url = svc["serialNumber"].replace("urn:uuid:", "urn:cdx:") + "/%d" % svc["version"]
    d["externalReferences"] = [e for e in d["externalReferences"] if not (
        e["type"] == "bom" and any(p["value"] == "cited-document" for p in e.get("properties", [])))]
    d["externalReferences"] += [
        {"type": "bom", "url": prod_url, "comment": "The Keycloak product record.",
         "properties": [{"name": P + "context", "value": "cited-document"}],
         "hashes": [{"alg": "SHA-256", "content": prod_hash}]},
        {"type": "bom", "url": svc_url, "comment": "The provider's restricted service record.",
         "properties": [{"name": P + "context", "value": "cited-document"}],
         "hashes": [{"alg": "SHA-256", "content": svc_hash}]}]
    return d


TENANT_KEEP = {"crypto:protocol:ing-tls", "service:svc-oidc", "service:svc-saml", "service:mgmt-admin",
               "service:sto-realm-keys"}


def tenant_record(svc, svc_hash, prod, serial, with_custody=True):
    d = copy.deepcopy(svc)
    d["serialNumber"] = "urn:uuid:" + serial
    d["metadata"]["timestamp"] = STAMP
    d["metadata"]["supplier"] = {"name": "Example Customer (illustrative tenant)"}
    svc_url = svc["serialNumber"].replace("urn:uuid:", "urn:cdx:") + "/%d" % svc["version"]
    inv = d["inventories"][0]
    drop = {c["bom-ref"] for c in ifaces(d) if c["bom-ref"] not in TENANT_KEEP}
    inv["components"] = [c for c in inv["components"] if c.get("bom-ref") not in drop]
    d["dependencies"] = [x for x in d.get("dependencies", []) if x.get("ref") not in drop]
    for x in d["dependencies"]:
        for k in ("dependsOn", "provides"):
            if k in x:
                x[k] = [r for r in x[k] if r not in drop]
    subj = inv["subject"]
    subj["bom-ref"] = "deployment:tenant-example-customer"
    subj["name"] = "Example Customer's tenant of the managed identity service"
    subj["description"] = "One tenant of Example Cloud managed identity (EU regions), as the tenant configured it."
    subj["identifiers"][0]["identities"][0]["value"] = "tag:customer.example,2026:deployment/identity-tenant"
    subj["parties"][0]["organization"]["name"] = "Example Customer (illustrative tenant)"
    for n in ("serviceRegions", "regenerationTrigger"):
        delprop(subj, n)
    setprop(subj, "subjectType", "deployment")
    setprop(subj, "coverage", "all-external")
    carry_libraries(d, prod, product_refs(d))
    for c in ifaces(d):
        setprop(c, "correspondsTo", svc_url + "#" + c["bom-ref"])
        for n in ("keyCustodySupported", "storageRegion"):
            delprop(c, n)
    st = comp(d, "service:sto-realm-keys")
    delprop(st, "keyCustody")
    if with_custody:
        setprop(st, "keyCustody", "provider-managed")
    d["externalReferences"] = [
        {"type": "bom", "url": svc_url, "comment": "The provider's restricted service record.",
         "properties": [{"name": P + "context", "value": "cited-document"}],
         "hashes": [{"alg": "SHA-256", "content": svc_hash}]},
        {"type": "configuration", "url": "https://console.example.org/tenants/example-customer/settings/2026-11-18",
         "comment": "Export of the tenant's settings this record was read from.",
         "properties": [{"name": P + "context", "value": "configuration-source"}]},
        {"type": "risk-assessment", "url": "https://grc.customer.example/registers/data/identity",
         "comment": "The customer's data register: what each store holds and how long it must stay confidential.",
         "properties": [{"name": P + "context", "value": "data-register"}]}]
    d["$comment"] = ("DRAFT EXAMPLE, lifecycle stage 'configured'. A tenant record for one customer of the managed "
                     "identity service. It cites the restricted service record. The only custody model the "
                     "service offers for realm keys is provider-managed, so that is the tenant's choice. Values "
                     "are illustrative." +
                     ("" if with_custody else " NON-CONFORMING: keyCustody removed from the realm-key store."))
    return d


def main():
    write("profile-service-key-custody.rules.json", key_custody_profile())
    write("profile-service-change-planning.rules.json", change_planning_profile())
    write("profile-tenant-disclosure.rules.json", tenant_profile())
    svc, svc_hash = load("cbom-keycloak-service-restricted.cdx.json")
    prod, prod_hash = load("cbom-keycloak-product.cdx.json")
    write("examples/cbom-keycloak-service-key-custody.cdx.json",
          key_custody_record(svc, "5e1c0a77-0000-4000-8000-000000000011"))
    write("examples/cbom-keycloak-service-key-custody-fail-replica.cdx.json",
          key_custody_record(svc, "5e1c0a77-0000-4000-8000-000000000012", with_replica=False))
    write("examples/cbom-keycloak-service-change-planning.cdx.json",
          change_planning_record(svc, svc_hash, prod, prod_hash, "5e1c0a77-0000-4000-8000-000000000021"))
    write("examples/cbom-keycloak-tenant-configured.cdx.json",
          tenant_record(svc, svc_hash, prod, "5e1c0a77-0000-4000-8000-000000000031"))
    write("examples/cbom-keycloak-tenant-fail-custody.cdx.json",
          tenant_record(svc, svc_hash, prod, "5e1c0a77-0000-4000-8000-000000000032", with_custody=False))
    print("written")


if __name__ == "__main__":
    main()
