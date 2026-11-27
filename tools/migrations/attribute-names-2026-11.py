#!/usr/bin/env python3
"""Apply the attribute renames agreed from drafts/attribute-naming-review.md (27 November 2026).

Run once, then run the builders, which regenerate every example, report and page from the renamed
sources. Kept in the repository as a record of exactly what was renamed, and so that a branch
created before the rename can be brought up to date by running it again.

What it changes:
  1. Attribute names, vocabulary names and context kinds, as whole tokens.
  2. Vocabulary values that changed with an attribute, only where the value belongs to that attribute.

What it leaves alone, because it is history: decisions/, plan and review documents at the root,
'Claude outputs', the EU Report, published slides and posts, profile changelogs, the CycloneDX test
schemas, and the naming review itself.

Usage: python3 tools/migrations/attribute-names-2026-11.py [--dry-run]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = "pkic:profile:"

# Identifier renames, applied as whole tokens in every file in scope. Longer names first.
TOKENS = [
    ("$commentProviderLocation", "$commentExecutionEnvironment"),
    ("providerLocationVocabulary", "executionEnvironmentVocabulary"),
    ("coexistenceVocabulary", "transitionModeVocabulary"),
    ("externalDependencyVocabulary", "trustServiceDependencyVocabulary"),
    ("keyManagementFunctionVocabulary", "managesKeysVocabulary"),
    ("cryptoTerminationPointVocabulary", "terminationOptionsVocabulary"),
    ("cryptoTerminationPoint", "terminationOptions"),
    ("negotiationControl", "algorithmSelection"),
    ("providerLocation", "executionEnvironment"),
    ("implementationPurl", "implementingLibrary"),
    ("externalDependencies", "trustServiceDependencies"),
    ("minimumProductVersion", "availableFromVersion"),
    ("certificationScheme", "impactedCertification"),
    ("keyManagementFunction", "managesKeys"),
    ("resourceBound", "resourceLimits"),
    ("claimedLevel62443", "claimedSecurityLevel"),
    ("regenerationTrigger", "recordRefreshTrigger"),
    ("referenceSpecification", "governingSpecification"),
    ("boundaryProxy", "proxiedBy"),
    ("keyStoreRef", "keysStoredIn"),
    ("keyProvider", "keysProvidedBy"),
    ("conduitRef", "crossesConduit"),
    ("peerInterface", "connectsTo"),
    ("externalKeyService", "keysHeldBy"),
    ("managementInterfaceAbsence", "absent:management-interface"),
    ("storageInterfaceAbsence", "absent:storage-interface"),
    ("hsmApprovalRef", "productCertificationRef"),
    ("hsmApproval", "productCertificationScheme"),
    ("keyBlockFormat", "keyBlockFormats"),
    ("design-intent", "threat-model"),
    ("issuer-policy", "certificate-policy"),
]
# 'contextAbsent:<kind>' becomes 'absent:<kind>'.
PREFIXES = [("contextAbsent:", "absent:")]
# Ordinary English words: renamed only where they are plainly the attribute (code, quoted strings,
# property names), never in running prose. Prose is reviewed by hand.
CODE_ONLY = [("coexistence", "transitionMode")]
# 'usage' is an ordinary word in code and prose, so only its quoted and code-marked forms are renamed.
QUOTED = [('"usage"', '"designUse"'), ("'usage'", "'designUse'"), ("`usage`", "`designUse`"),
          ("<code>usage</code>", "<code>designUse</code>"), (P + "usage", P + "designUse"),
          ("usageVocabulary", "designUseVocabulary"), ("$commentUsage", "$commentDesignUse")]
# 'boundary' is renamed only in the telecom service assurance files, where it is the attribute.
TELECOM_ONLY = [("boundary", "operatorBoundary")]

# Values that changed with their attribute (new attribute name -> old value -> new value).
VALUES = {
    "transitionMode": {"simultaneous": "side-by-side", "exclusive": "switch-over"},
    "managesKeys": {"keys-and-certificates": "yes", "none": "no"},
    "verifierReplaceable": {"yes": "in-field", "via-bootloader-update": "bootloader-update", "no": "not-replaceable"},
    "blockedBy": {"provider": "crypto-library"},
    "claimedSecurityLevel": {"SL-C 1": "sl-c-1", "SL-C 2": "sl-c-2", "SL-C 3": "sl-c-3", "SL-C 4": "sl-c-4"},
    "keyBlockFormats": {"x9.143": "x9-143"},
    "keyBlockFormatsSupported": {"x9.143": "x9-143"},
}
VOCABULARIES = {"transitionModeVocabulary": "transitionMode", "managesKeysVocabulary": "managesKeys",
                "verifierReplaceableVocabulary": "verifierReplaceable", "blockedByVocabulary": "blockedBy",
                "securityLevelVocabulary": "claimedSecurityLevel", "keyBlockFormatVocabulary": "keyBlockFormats"}

INCLUDE_DIRS = ["docs", "drafts", "tools", "tests", "publications/src", "publications/templates", "regulation"]
INCLUDE_FILES = ["open-questions.md", "questions-after-release-1.md", "README.md", "CONTRIBUTING.md"]
EXCLUDE = ["tests/schemas", "drafts/attribute-naming-review.md", "tools/migrations", "docs/assets",
           "drafts/decision-backlog", "drafts/keycloak-methodology", "/_build/", "__pycache__", "/gallery/"]
EXTS = (".json", ".md", ".html", ".py", ".sh", ".yml", ".yaml", ".js", ".txt")


def tok(word):
    return re.compile(r"(?<![A-Za-z0-9_$-])" + re.escape(word) + r"(?![A-Za-z0-9_-])")


TOKEN_RE = [(tok(a), b) for a, b in TOKENS]


def code_only(text, old, new, ext):
    if ext in (".json", ".py", ".js", ".sh", ".yml", ".yaml"):
        return tok(old).sub(new, text)
    # Markdown and HTML: only inside backticks, <code>, quotes, or as a property name.
    pats = [r"`%s`" % old, r"<code>%s</code>" % old, r'"%s"' % old, r"'%s'" % old, P + old]
    for p in pats:
        text = text.replace(p, p.replace(old, new))
    return text


def map_values_json(obj):
    """Rename values that belong to a renamed attribute, wherever the attribute is named next to them."""
    if isinstance(obj, dict):
        name = obj.get("name")
        if isinstance(name, str) and name.startswith(P) and "value" in obj:
            attr = name[len(P):].split(":")[-1]
            m = VALUES.get(attr)
            if m and obj["value"] in m:
                obj["value"] = m[obj["value"]]
        attr = obj.get("attribute")
        if attr in VALUES:
            m = VALUES[attr]
            for k in ("equals", "notEquals"):
                if obj.get(k) in m:
                    obj[k] = m[obj[k]]
            if isinstance(obj.get("in"), list):
                obj["in"] = [m.get(v, v) for v in obj["in"]]
        for k, v in list(obj.items()):
            if k in VOCABULARIES and isinstance(v, list):
                m = VALUES[VOCABULARIES[k]]
                obj[k] = [m.get(x, x) for x in v]
            elif k in VALUES and isinstance(v, (str, list)) and k != "attribute":
                m = VALUES[k]
                obj[k] = m.get(v, v) if isinstance(v, str) else [m.get(x, x) if isinstance(x, str) else x for x in v]
            elif k != "changelog":
                map_values_json(v)
    elif isinstance(obj, list):
        for v in obj:
            map_values_json(v)


def map_values_py(text):
    for attr, m in VALUES.items():
        for old, new in m.items():
            o, n = re.escape(old), new
            text = re.sub(r'(\(\s*"%s"\s*,\s*)"%s"' % (attr, o), r'\1"%s"' % n, text)
            text = re.sub(r'("%s"\s*:\s*)"%s"' % (attr, o), r'\1"%s"' % n, text)
    return text


def map_values_text(text):
    """For JSON that cannot be rewritten without reformatting: rename values in name/value pairs."""
    for attr, m in VALUES.items():
        for old, new in m.items():
            text = re.sub(r'("name"\s*:\s*"%s(?:[^"]*:)?%s"\s*,\s*"value"\s*:\s*)"%s"' % (re.escape(P), attr, re.escape(old)),
                          r'\1"%s"' % new, text)
    return text


def roundtrips(text):
    try:
        obj = json.loads(text)
    except ValueError:
        return False
    compact = "\n" not in text.strip()
    return text == (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact
                    else json.dumps(obj, indent=2, ensure_ascii=False)) + "\n"


def transform(path, text):
    ext = os.path.splitext(path)[1]
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    clean = ext == ".json" and roundtrips(text)
    is_profile_json = clean and os.path.basename(path).endswith(".rules.json")
    changelog = None
    if is_profile_json:
        obj = json.loads(text)
        changelog = obj.pop("changelog", None)
        text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    for rx, new in TOKEN_RE:
        text = rx.sub(new, text)
    for old, new in PREFIXES:
        text = text.replace(old, new)
    for old, new in QUOTED:
        text = text.replace(old, new)
    for old, new in CODE_ONLY:
        text = code_only(text, old, new, ext)
    if "telecom-service-assurance" in rel or "domain-telecommunications" in rel:
        for old, new in TELECOM_ONLY:
            text = code_only(text, old, new, ext)
    if ext == ".json" and not clean:
        return map_values_text(text)
    if ext == ".json":
        try:
            obj = json.loads(text)
        except ValueError:
            return text
        map_values_json(obj)
        if is_profile_json and changelog is not None:
            obj["changelog"] = changelog
        compact = "\n" not in text.strip()
        text = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact
                else json.dumps(obj, indent=2, ensure_ascii=False)) + "\n"
    elif ext == ".py":
        text = map_values_py(text)
    return text


def files():
    for d in INCLUDE_DIRS:
        for root, dirs, names in os.walk(os.path.join(ROOT, d)):
            for n in names:
                p = os.path.join(root, n)
                rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
                if n.endswith(EXTS) and not any(x in "/" + rel for x in EXCLUDE):
                    yield p
    for n in INCLUDE_FILES:
        if os.path.exists(os.path.join(ROOT, n)):
            yield os.path.join(ROOT, n)


def main():
    dry = "--dry-run" in sys.argv
    changed = 0
    for p in files():
        with open(p, encoding="utf-8") as fh:
            old = fh.read()
        try:
            new = transform(p, old)
        except Exception as e:  # noqa: BLE001
            print("skipped %s: %s" % (os.path.relpath(p, ROOT), e))
            continue
        if new != old:
            changed += 1
            if dry:
                print("would change", os.path.relpath(p, ROOT))
            else:
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)
    print("%d file(s) %s" % (changed, "would change" if dry else "changed"))


if __name__ == "__main__":
    main()
