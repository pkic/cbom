#!/usr/bin/env python3
"""Check that the interface family's profiles really are one ladder.

The Maturity section says a producer may conform at the entry depth and climb,
and that conforming at a deeper depth implies conformance at every depth below
it. That implication is what makes the ladder worth publishing: without it, "we
conform to the entry profile" and "we conform to the baseline" are two unrelated
statements, and a buyer who asked for the second learns nothing from the first.

Monotonic extension gives that implication structurally, and the validator
enforces it wherever one profile declares `extends` another. The two profiles
here do not: the Interface Disclosure Baseline was published first and does not
name the entry profile as its base, because re-parenting it would move seven
rule ids to another profile tag and change every citation of them in the
documentation, the tests and any report already issued. Whether to pay that is
the group's call, recorded as Q51.

Until it is paid, the ladder is an assertion about two sibling profiles, and an
assertion in this repository gets a check. This script requires that:

  * every rule the shallower profile declares is declared by the deeper one,
    under the same id, for the same attribute, with an identical constraint and
    an obligation at least as strong;
  * the vocabularies and identifier schemes those shared rules resolve against
    are identical, since `enumRef` resolves per profile and two rules with the
    same text can mean different things;
  * the disclosure marker convention is identical, or markers recognised at one
    depth stop being recognised at the other;
  * the deeper profile's scope and carrier range do not widen the shallower
    one's, checked by calling the validator's own monotonicity functions for a
    parent and child on a pair that is not one yet;
  * every committed document that conforms to the deeper profile also conforms
    to the shallower one.

Identity is required of a shared constraint rather than tightening, which real
extension permits, because these are siblings: there is no `overrides` block to
declare a tightening in, so a difference here is drift rather than design. The
day the baseline extends the entry profile, C7 and the validator replace most of
this file, and it should be deleted rather than kept in parallel.

Usage:  python tests/check-family.py
Exit:   0 the ladder holds, 1 it does not, 2 something was unreadable
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")

# The family, shallowest first. This list is here and not in the profiles
# because a profile cannot name the profiles deeper than it: they do not exist
# when it is published, and adding them later would mean re-releasing it every
# time the family grows. Where the family belongs instead — the register that
# Governance describes — is Q50.
#
# The PQC migration profile is deliberately absent. It derives from the
# baseline, but it is not a deeper rung of this ladder: it declares orientation
# 'both' and serves a different decision, which makes it a branch. Depth asks
# more about the same decision; a branch changes the decision.
FAMILY = ["profile-interface-enumeration.rules.json",
          "profile-interface-disclosure.rules.json"]

DOCUMENTS = ["cbom-entry-fail.cyclonedx.json", "cbom-fail.cyclonedx.json",
             "cbom-disclosure.cyclonedx.json", "cbom-noadmin.cyclonedx.json",
             "cbom-pass.cyclonedx.json"]

LEVELS = {"MAY": 0, "SHOULD": 1, "MUST": 2}
SECTIONS = ("productRules", "interfaceRules", "groupRules")
VOCABULARY_REFS = ("enumRef", "keyVocabularyRef", "absenceEnumRef")


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_cbom", os.path.join(M, "validate_cbom.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rules_of(profile):
    out = {}
    for section in SECTIONS:
        for rule in profile.get(section, []):
            out[str(rule.get("id"))] = (section, rule)
    return out


def compare(shallow, deep, shallow_name, deep_name, problems):
    """Require the deeper profile to declare everything the shallower one does."""
    shallow_rules, deep_rules = rules_of(shallow), rules_of(deep)

    for rid, (section, rule) in sorted(shallow_rules.items()):
        if rid not in deep_rules:
            problems.append(
                "%s declares %s and %s does not; a deeper profile drops nothing, so "
                "either the rule moved id or the ladder is broken"
                % (shallow_name, rid, deep_name))
            continue
        deep_section, deep_rule = deep_rules[rid]
        if deep_section != section:
            problems.append("%s is a %s rule in %s and a %s rule in %s"
                            % (rid, section, shallow_name, deep_section, deep_name))
            continue
        if rule.get("attribute") != deep_rule.get("attribute"):
            problems.append("%s assesses %r in %s and %r in %s"
                            % (rid, rule.get("attribute"), shallow_name,
                               deep_rule.get("attribute"), deep_name))
        if rule.get("constraint") != deep_rule.get("constraint"):
            problems.append(
                "%s constrains %s in %s and %s in %s; a shared rule is identical at "
                "both depths, because a sibling profile has no overrides block to "
                "declare a tightening in"
                % (rid, json.dumps(rule.get("constraint"), sort_keys=True), shallow_name,
                   json.dumps(deep_rule.get("constraint"), sort_keys=True), deep_name))
        if LEVELS.get(deep_rule.get("level"), -1) < LEVELS.get(rule.get("level"), -1):
            problems.append("%s is %s in %s and %s in %s, which is a relaxation"
                            % (rid, rule.get("level"), shallow_name,
                               deep_rule.get("level"), deep_name))
        if bool(rule.get("withholdable")) is False and deep_rule.get("withholdable"):
            problems.append(
                "%s is not withholdable in %s and is withholdable in %s; permitting a "
                "producer to withhold what the shallower profile required is a relaxation"
                % (rid, shallow_name, deep_name))

        # A constraint can be identical and still mean something different, because
        # enumRef and schemeRef resolve against the profile that declares them.
        for key in VOCABULARY_REFS:
            ref = (rule.get("constraint") or {}).get(key)
            if ref and shallow.get(ref) != deep.get(ref):
                problems.append(
                    "%s resolves %s %r to %s in %s and %s in %s, so the same rule text "
                    "permits different values at each depth"
                    % (rid, key, ref, json.dumps(shallow.get(ref)), shallow_name,
                       json.dumps(deep.get(ref)), deep_name))
        if rule.get("schemeRef"):
            ref = rule["schemeRef"]
            a = (shallow.get("identifierSchemes") or {}).get(ref)
            b = (deep.get("identifierSchemes") or {}).get(ref)
            if a != b:
                problems.append("%s names the %r identifier scheme as %r in %s and %r in %s"
                                % (rid, ref, a, shallow_name, b, deep_name))

    a = {k: v for k, v in (shallow.get("disclosure") or {}).items()
         if not k.startswith("$")}
    b = {k: v for k, v in (deep.get("disclosure") or {}).items()
         if not k.startswith("$")}
    if a != b:
        problems.append(
            "the disclosure convention differs: %s in %s, %s in %s. A marker written "
            "for one depth would not be recognised at the other."
            % (json.dumps(a, sort_keys=True), shallow_name,
               json.dumps(b, sort_keys=True), deep_name))

    a_or = (shallow.get("scope") or {}).get("orientation")
    b_or = (deep.get("scope") or {}).get("orientation")
    if a_or != b_or:
        problems.append(
            "orientation is %r at %s and %r at %s; a profile reporting a different kind "
            "of fact is a branch of the family, not a greater depth of it"
            % (a_or, shallow_name, b_or, deep_name))

    added = sorted(set(deep_rules) - set(shallow_rules))
    return added


def main() -> int:
    failures = 0

    def ok(label):
        print("  ok   %s" % label)

    def bad(label, detail):
        nonlocal failures
        failures += 1
        print("  FAIL %s\n     %s" % (label, detail))

    try:
        v = load_validator()
        loaded = []
        for name in FAMILY:
            with open(os.path.join(M, name), encoding="utf-8") as fh:
                loaded.append((name, json.load(fh)))
    except (OSError, ValueError) as err:
        print("  FAIL the family could not be read\n     %s" % err)
        return 2

    for (shallow_name, shallow), (deep_name, deep) in zip(loaded, loaded[1:]):
        short_a = shallow.get("profileTag", shallow_name)
        short_b = deep.get("profileTag", deep_name)
        label = "%s contains %s" % (short_b, short_a)
        problems = []
        added = compare(shallow, deep, short_a, short_b, problems)

        # The same two checks the validator applies to a parent and a child, on a
        # pair that is not one yet. They raise rather than return.
        for check in (v.check_range_narrows, v.check_scope_narrows):
            try:
                check(shallow, deep)
            except v.ProfileError as err:
                problems.append(str(err))

        if problems:
            bad(label, "\n     ".join(problems))
        else:
            ok("%s (%d rule(s) shared, %d added at the deeper depth)"
               % (label, len(rules_of(shallow)), len(added)))

    # The implication, over every committed document: conformance at a depth
    # carries conformance at every depth below it.
    verdicts = {}
    for doc in DOCUMENTS:
        path = os.path.join(M, doc)
        if not os.path.exists(path):
            bad("every named document exists", "%s is not in docs/methodology/" % doc)
            continue
        with open(path, encoding="utf-8") as fh:
            bom = json.load(fh)
        for name, _prof in loaded:
            profile, _origin, _notes = v.load_profile(os.path.join(M, name))
            verdict, report = v.validate(bom, profile)
            failed = [r["id"] for r in report["product"]
                      if not r["ok"] and r["level"] == "MUST"]
            for iface in report["interfaces"]:
                failed += ["%s/%s" % (iface["interfaceId"], r["id"])
                           for r in iface["rows"]
                           if not r["ok"] and r["level"] == "MUST"]
            verdicts[(doc, name)] = (verdict, failed)

    problems, climbed = [], []
    for (shallow_name, shallow), (deep_name, deep) in zip(loaded, loaded[1:]):
        for doc in DOCUMENTS:
            deep_verdict, deep_failed = verdicts.get((doc, deep_name), (None, []))
            shallow_verdict, _ = verdicts.get((doc, shallow_name), (None, []))
            if deep_verdict == "conforms" and shallow_verdict != "conforms":
                problems.append(
                    "%s conforms to %s and does not conform to the shallower %s, so "
                    "conformance at depth does not carry downwards"
                    % (doc, deep.get("profileTag"), shallow.get("profileTag")))
            if shallow_verdict == "conforms" and deep_verdict != "conforms":
                climbed.append("%s conforms to %s, and %s stands between it and %s"
                               % (doc, shallow.get("profileTag"),
                                  ", ".join(deep_failed) or "nothing",
                                  deep.get("profileTag")))
    if problems:
        bad("conformance carries downwards", "\n     ".join(problems))
    else:
        ok("conformance carries downwards (%d document(s) at %d depth(s))"
           % (len(DOCUMENTS), len(loaded)))

    # Not a failure: the ladder is pointless unless some document sits between two
    # depths. A family where every document conforms everywhere is a family with
    # one rung, whatever it declares.
    if climbed:
        print("\n  Between depths (the reason the family has more than one):")
        for line in climbed:
            print("    - %s" % line)
    else:
        bad("some document sits between two depths",
            "every committed document conforms at every depth, so nothing "
            "demonstrates that the depths differ")

    print("\n  %s" % ("the family is one ladder" if not failures
                      else "%d problem(s) with the family" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
