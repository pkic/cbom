#!/usr/bin/env python3
"""Validate the published artifacts against the published schemas.

The schemas say what shape a rules file and a claim have. They deliberately do
not say whether a profile is well-formed under the methodology, which is C1 to
C17 and belongs to check_profile.py: a schema can see that 'objective' is an
object with a 'decision' string, and cannot see whether the decision is one a
consumer could act on. Both checks are worth having, and neither substitutes for
the other.

Skips with a message rather than failing when 'jsonschema' is not installed, so
that a contributor without it can still run the rest of the suite.

Usage:  python tests/check-schemas.py
Exit:   0 all valid (or skipped), 1 something did not validate
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
FIX = os.path.join(ROOT, "tests", "fixtures")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    try:
        import jsonschema
    except ImportError:
        print("SKIP  jsonschema is not installed; schema checks not run")
        print("      pip install jsonschema  to enable them")
        return 0

    failures = 0
    profile_schema = load(os.path.join(M, "profile.schema.json"))
    claim_schema = load(os.path.join(M, "claim.schema.json"))
    for name, schema in (("profile.schema.json", profile_schema),
                         ("claim.schema.json", claim_schema)):
        try:
            jsonschema.Draft7Validator.check_schema(schema)
            print("  ok   %s is a valid schema" % name)
        except jsonschema.SchemaError as err:
            print("  FAIL %s is not a valid schema\n     %s" % (name, err))
            failures += 1

    def check(path, schema, label, expect_valid=True):
        nonlocal failures
        errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(load(path)),
                        key=lambda e: list(e.path))
        ok = (not errors) if expect_valid else bool(errors)
        if ok:
            print("  ok   %s" % label)
        else:
            failures += 1
            print("  FAIL %s" % label)
            for e in errors[:3]:
                print("     %s %s" % (list(e.path), e.message[:160]))

    # The published profiles and the third-level fixture must validate.
    for f in ("profile-interface-enumeration.rules.json",
              "profile-interface-disclosure.rules.json",
              "profile-pqc-migration.rules.json"):
        check(os.path.join(M, f), profile_schema, "%s validates" % f)
    check(os.path.join(FIX, "profile-l3-settlement.rules.json"), profile_schema,
          "a third-level profile validates")

    # And the schema has to be able to reject: a constraint key the evaluator
    # does not implement is caught structurally as well as by C17, because a
    # third party validating a profile may not have our checker.
    check(os.path.join(FIX, "profile-c17-unknown-constraint.rules.json"), profile_schema,
          "an unimplemented constraint key is rejected by the schema too", expect_valid=False)

    check(os.path.join(M, "claim-example.json"), claim_schema, "the example claim validates")

    print("  %s" % ("all schema checks passed" if not failures
                    else "%d schema check(s) failed" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
