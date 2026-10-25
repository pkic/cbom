#!/usr/bin/env python3
"""Validate example CBOMs against the CycloneDX schema their specVersion names.

CycloneDX 2.0 documents are checked against the pinned 2.0 schema in
tests/schemas/cyclonedx-2.0. CycloneDX 1.x documents are checked against the
schema shipped with cyclonedx-python-lib when it is installed, and skipped with
a message otherwise. Needs jsonschema 4.18 or later for the 2.0 schema (draft
2020-12); skips with a message on older versions.

Usage:  python3 tests/check-cyclonedx.py [file ...]   (default: every example)
Exit:   0 all valid or skipped, 1 something did not validate
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS = os.path.join(ROOT, "tests", "schemas", "cyclonedx-2.0")
DEFAULT = sorted(glob.glob(os.path.join(ROOT, "docs", "methodology", "examples", "*.cdx.json")) +
                 glob.glob(os.path.join(ROOT, "docs", "methodology", "examples", "*", "*.cdx.json")))


def validator_20():
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError:
        return None
    reg = Registry()
    base = "https://cyclonedx.org/schema/"
    for name in ("cryptography-defs.schema.json", "behavior-taxonomy.schema.json", "spdx.schema.json"):
        with open(os.path.join(SCHEMAS, name), encoding="utf-8") as fh:
            reg = reg.with_resource(base + name, Resource.from_contents(json.load(fh)))
    with open(os.path.join(SCHEMAS, "cyclonedx-2.0-bundled.schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    return Draft202012Validator(schema, registry=reg)


def validator_1x(version):
    try:
        from cyclonedx.schema import SchemaVersion
        from cyclonedx.validation.json import JsonValidator
    except ImportError:
        return None
    try:
        return JsonValidator(SchemaVersion.from_version(version))
    except Exception:
        return None


def main(argv):
    files = argv[1:] or DEFAULT
    v20 = validator_20()
    bad = skipped = 0
    for path in files:
        doc = json.load(open(path, encoding="utf-8"))
        version = str(doc.get("specVersion"))
        name = os.path.relpath(path, ROOT)
        if version.startswith("2."):
            if v20 is None:
                print("  SKIP %s (needs jsonschema >= 4.18 with referencing)" % name)
                skipped += 1
                continue
            errors = sorted(v20.iter_errors(doc), key=lambda e: list(e.absolute_path))
            if errors:
                bad += 1
                print("  FAIL %s: %d error(s)" % (name, len(errors)))
                for e in errors[:5]:
                    print("       at /%s: %s" % ("/".join(map(str, e.absolute_path)), e.message[:200]))
            else:
                print("  ok   %s valid CycloneDX %s" % (name, version))
        else:
            v = validator_1x(version)
            if v is None:
                print("  SKIP %s (CycloneDX %s needs cyclonedx-python-lib)" % (name, version))
                skipped += 1
                continue
            err = v.validate_str(json.dumps(doc))
            if err:
                bad += 1
                print("  FAIL %s: %s" % (name, str(err)[:300]))
            else:
                print("  ok   %s valid CycloneDX %s" % (name, version))
    print("%d file(s), %d invalid, %d skipped" % (len(files), bad, skipped))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
