#!/usr/bin/env python3
"""Build the service disclosure profiles and the service examples: Keycloak run as a managed service.

Writes, in docs/methodology/:
  profile-service-disclosure.rules.json             the service disclosure profile
  profile-service-disclosure-restricted.rules.json  its restricted pair
  examples/cbom-keycloak-service-restricted.cdx.json  coverage 'all'
  examples/cbom-keycloak-service-public.cdx.json      coverage 'all-external', internal links left out
  examples/cbom-keycloak-service-fail-custody.cdx.json  storage interface without keyCustodySupported

The service records are built from the configured deployment record. Values are illustrative.

Usage: python3 tools/build_service_examples.py
"""
import copy, json, os, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
METH = os.path.join(HERE, "..", "docs", "methodology")
EX = os.path.join(METH, "examples")

def load(p):
    with open(p) as f:
        return json.load(f)

def save(name, obj):
    with open(os.path.join(METH, name), "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")

# 1. Service disclosure profile --------------------------------------------------------
svc = {
  "$comment": "Illustrative machine-readable CBOM profile for a managed service, written by its provider. It extends the Interface Disclosure Baseline, narrowed to the subject type 'service' and the stages 'configured' and 'observed'. A service record cites the product records of the software it runs and joins each interface to the product interface it realises, as a deployment record does. It adds what a customer of a service needs and a deployment record does not carry: the regions covered, key custody on stores of customer data, and where the provider announces changes. The worked example is Keycloak 26.7.3 run as a managed identity service by an illustrative provider.",
  "profileId": "pkic.example.service-disclosure",
  "profileTag": "service-disclosure",
  "title": "Service Disclosure (Example)",
  "version": "0.1",
  "objective": {
    "consumer": "A customer, or an assessor acting for one, that relies on a service it does not run",
    "decision": "Whether to rely on the service, and what to require of the provider in the contract",
    "decisionOptions": ["rely on the service as offered", "rely on it with contractual requirements",
                        "do not rely on it"]},
  "scope": {
    "$comment": "Narrows the base to running services, as configured or observed by the provider.",
    "subjectTypes": ["service"], "orientation": "both",
    "relationshipTypes": ["interface"], "lifecycleStages": ["configured", "observed"]},
  "extends": {"profileId": "pkic.example.interface-disclosure", "version": "0.10",
              "file": "profile-interface-disclosure.rules.json"},
  "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
  "overrides": [{"id": "interface-disclosure#I14", "level": "SHOULD",
                 "note": "Raised from MAY: a customer needs to know whether the provider's ingress or the application holds the TLS keys of each customer-facing interface."}],
  "storageAbsenceVocabulary": ["stores-no-customer-data"],
  "keyCustodyVocabulary": ["provider-managed", "customer-managed", "external"],
  "regenerationTriggerVocabulary": ["schedule", "interface-change", "schedule-and-interface-change"],
  "productRules": [
    {"id": "P1", "description": "Service names the regions the record describes", "level": "MUST",
     "constraint": {"productAttribute": "serviceRegions"}, "withholdable": False,
     "note": "Part of the coverage statement. Where the cryptography differs between regions, the provider writes one record per group of regions."},
    {"id": "P2", "description": "Service declares at least one storage interface for customer data, or states why it has none",
     "level": "MUST", "constraint": {"minInterfacesOfType": {"interfaceType": "storage", "min": 1},
     "orDeclaredAbsent": "storageInterfaceAbsence", "absenceEnumRef": "storageAbsenceVocabulary"},
     "withholdable": False, "note": "For most customers the store matters more than the session."},
    {"id": "P3", "description": "Service cites the records it builds on, each by BOM-Link and hash", "level": "MUST",
     "constraint": {"citesDocuments": {"min": 1, "hashRequired": True}}, "withholdable": False,
     "note": "The product records of the software it runs, and the records of the services beneath it."},
    {"id": "P4", "description": "Service states what makes the provider produce a new record", "level": "MUST",
     "constraint": {"productAttribute": "regenerationTrigger", "enumRef": "regenerationTriggerVocabulary"},
     "withholdable": False, "note": "With the document timestamp and the change-notice pointer, a customer's policy can judge whether the record it holds is current."}],
  "interfaceRules": [
    {"id": "I1", "attribute": "keyCustodySupported", "level": "MUST", "constraint": {"enumRef": "keyCustodyVocabulary"},
     "list": True, "withholdable": False, "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
     "note": "The key-custody models a tenant can choose for this store."},
    {"id": "I3", "attribute": "keyCustody", "level": "MUST", "constraint": {"enumRef": "keyCustodyVocabulary"},
     "withholdable": False, "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
     "note": "The custody model a new tenant gets unless it chooses another. The present-state attribute behind keyCustodySupported (C12). A tenant's own choice is stated in its tenant record."},
    {"id": "I2", "attribute": "storageRegion", "level": "SHOULD", "constraint": {"present": True},
     "withholdable": False, "requiredWhen": {"attribute": "interfaceType", "equals": "storage"},
     "note": "The regions where this store holds customer data."}],
  "referenceRules": [
    {"id": "R1", "context": "change-notice", "at": "document", "level": "MUST", "hashRequired": False,
     "withholdable": False, "note": "Where the provider announces changes to the service. The context kind is defined in the baseline. A service changes without a version number, so a customer needs this, with the document timestamp and the regeneration trigger (P4), to judge whether the record it holds is current."}],
  "exclusions": [
    {"item": "A maximum age for the record", "reason": "Freshness is a policy matter (Release 1). The record supplies what a policy needs."},
    {"item": "The customer's choice of key custody", "reason": "A tenant fact. It belongs in the tenant record, which cites this one."}],
  "artifacts": {"mapping": "mapping-cyclonedx-spdx.md",
                "conformingExample": "examples/cbom-keycloak-service-restricted.cdx.json",
                "nonConformingExample": "examples/cbom-keycloak-service-fail-custody.cdx.json"},
  "changelog": [{"version": "0.1", "date": "2026-11-18", "summary": "Initial version, built on Keycloak run as a managed service.",
                 "changes": [{"kind": "editorial", "summary": "Raised interface-disclosure#I14 'terminatedBy' to SHOULD (19 November 2026). No verdict changes."}]}]
}
save("profile-service-disclosure.rules.json", svc)

# 3. Restricted pair ------------------------------------------------------------------
rst = {
  "$comment": "Illustrative profile for the restricted variant of a service record: the one a provider gives a customer under a confidentiality agreement. It extends Service Disclosure with two tightenings: coverage of every interface, and the implementing library on every interface without withholding. The public variant may leave internal links out and withhold the library.",
  "profileId": "pkic.example.service-disclosure-restricted",
  "profileTag": "service-disclosure-restricted",
  "title": "Service Disclosure, Restricted (Example)",
  "version": "0.1",
  "objective": {"consumer": "A customer under a confidentiality agreement with the provider",
                "decision": "Whether the provider's internal cryptography is acceptable for the data the customer will place in the service",
                "decisionOptions": ["accept", "accept with conditions", "reject"]},
  "scope": {"subjectTypes": ["service"], "orientation": "both", "relationshipTypes": ["interface"],
            "lifecycleStages": ["configured", "observed"]},
  "extends": {"profileId": "pkic.example.service-disclosure", "version": "0.1",
              "file": "profile-service-disclosure.rules.json"},
  "appliesTo": {"cyclonedx": {"min": "1.6", "tested": "2.0"}},
  "overrides": [{"id": "interface-disclosure#I9", "level": "MUST", "withholdable": False,
                 "note": "Tightened: a customer under agreement must be able to match every interface to library advisories."}],
  "restrictedCoverageVocabulary": ["all"],
  "productRules": [
    {"id": "P1", "description": "Service states coverage of all interfaces", "level": "MUST",
     "constraint": {"productAttribute": "coverage", "enumRef": "restrictedCoverageVocabulary"}, "withholdable": False,
     "note": "The public variant may declare all-external and leave internal links out. The restricted variant may not."}],
  "interfaceRules": [],
  "exclusions": [{"item": "Further rules on internal interfaces", "reason": "The base profile's rules already apply to every interface the restricted variant declares."}],
  "artifacts": {"mapping": "mapping-cyclonedx-spdx.md",
                "conformingExample": "examples/cbom-keycloak-service-restricted.cdx.json",
                "nonConformingExample": "examples/cbom-keycloak-service-public.cdx.json"},
  "changelog": [{"version": "0.1", "date": "2026-11-18", "summary": "Initial version, built on Keycloak run as a managed service.", "changes": []}]
}
save("profile-service-disclosure-restricted.rules.json", rst)

# 4. Service records, built from the configured deployment record ----------------------
dep = load(os.path.join(EX, "cbom-keycloak-deployment-configured.cdx.json"))

def prop(obj, name, value):
    props = obj.setdefault("properties", [])
    props[:] = [p for p in props if p["name"] != "pkic:profile:" + name]
    props.append({"name": "pkic:profile:" + name, "value": value})

def build(serial_suffix, coverage, keep_internal, with_custody):
    d = copy.deepcopy(dep)
    d["serialNumber"] = "urn:uuid:5e1c0a77-0000-4000-8000-%012d" % serial_suffix
    d["version"] = 1
    d["$comment"] = ("Illustrative service record. Keycloak 26.7.3 run as a managed identity service "
                     "by an illustrative provider. Built from the configured deployment record by tools/build_service_examples.py. "
                     "Values are illustrative.")
    d["metadata"]["timestamp"] = "2026-11-18T09:00:00Z"
    d["metadata"]["supplier"] = {"name": "Example Cloud (illustrative provider)"}
    subj = d["inventories"][0]["subject"]
    subj["bom-ref"] = "service:managed-identity-eu"
    subj["name"] = "Example Cloud managed identity (EU regions)"
    subj["description"] = "Keycloak 26.7.3 run for many tenants in two EU regions, behind a TLS-terminating ingress."
    subj["identifiers"][0]["identities"][0]["value"] = "tag:example.org,2026:service/managed-identity-eu"
    subj["parties"][0]["organization"]["name"] = "Example Cloud (illustrative provider)"
    prop(subj, "subjectType", "service")
    prop(subj, "coverage", coverage)
    prop(subj, "serviceRegions", "eu-west, eu-central")
    prop(subj, "regenerationTrigger", "interface-change")
    comps = d["inventories"][0]["components"]
    internal = {"crypto:protocol:int-db", "crypto:protocol:int-ldap", "crypto:protocol:int-cache",
                "service:mgmt-health"}
    if not keep_internal:
        drop = set(internal)
        d["inventories"][0]["components"] = [c for c in comps if c.get("bom-ref") not in drop]
        d["dependencies"] = [x for x in d.get("dependencies", []) if x.get("ref") not in drop]
        for x in d["dependencies"]:
            if "dependsOn" in x:
                x["dependsOn"] = [r for r in x["dependsOn"] if r not in drop]
    for c in d["inventories"][0]["components"]:
        if c.get("bom-ref") == "service:sto-realm-keys":
            if with_custody:
                prop(c, "keyCustodySupported", "provider-managed")
                prop(c, "keyCustody", "provider-managed")
            prop(c, "storageRegion", "eu-west, eu-central")
    d["externalReferences"] = list(d.get("externalReferences", [])) + [{
        "type": "release-notes", "url": "https://status.example.org/managed-identity/changes",
        "comment": "Where the provider announces changes to the service.",
        "properties": [{"name": "pkic:profile:context", "value": "change-notice"}]}]
    return d

VARIANTS = [
    ("cbom-keycloak-service-restricted.cdx.json", (1, "all", True, True),
     "The restricted variant, given to customers under agreement: coverage 'all'."),
    ("cbom-keycloak-service-public.cdx.json", (2, "all-external", False, True),
     "The public variant: coverage 'all-external', with the database, directory, cache and health links "
     "left out. Conforms to service-disclosure and fails the restricted profile's coverage rule (P1)."),
    ("cbom-keycloak-service-fail-custody.cdx.json", (3, "all", True, False),
     "NON-CONFORMING. The restricted variant with keyCustodySupported and keyCustody removed from the "
     "realm-key store. Fails service-disclosure I1 and I3."),
]
for name, args, note in VARIANTS:
    d = build(*args)
    d["$comment"] = d["$comment"] + " " + note
    save(os.path.join("examples", name), d)
print("written")
