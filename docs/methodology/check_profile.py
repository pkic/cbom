#!/usr/bin/env python3
"""
Profile well-formedness checker.

Checks a machine-readable profile against requirements C1 to C10 of the
Conformance section, which state what makes a profile well-formed under this
methodology. This is the second of the three conformance targets: a CBOM
document is checked against a profile by validate_cbom.py, and a profile is
checked against the methodology here.

C1  MUST    states the consumer it serves and the decision it supports
C2  MUST    carries an identifier and version, and a carrier acceptance range
C3  MUST    no rule refers to a named product, vendor, or interface instance
C4  MUST    every rule has an identifier, a level, and a withholdability statement
C5  MUST    attribute names follow the naming conventions
C6  MUST    no rule requires a derived judgement
C7  MUST    extension pins the base and relaxes nothing
C8  SHOULD  states what it deliberately excludes, and why
C9  SHOULD  is accompanied by a mapping and by conforming and non-conforming examples
C10 SHOULD  carries a changelog classifying each change

Rules are checked as DECLARED in the file under test. A derived profile is not
re-checked against its base's rules, because the base is checkable on its own;
C7 confirms that the base resolves and that no override relaxes it.

Usage:
    python check_profile.py <profile.rules.json> [--strict] [--json]

    --strict   treat SHOULD failures as failures
    --json     emit the findings as JSON

Exit codes:
    0  well-formed
    1  not well-formed (a MUST failed, or a SHOULD failed under --strict)
    2  usage error, or the file could not be read or parsed
"""
import json
import os
import re
import sys

try:
    from validate_cbom import load_profile, ProfileError
except ImportError:  # allow running from another directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from validate_cbom import load_profile, ProfileError

LEVELS = ("MUST", "SHOULD", "MAY")
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")

# C6. Substrings that indicate a name is asserting a conclusion rather than
# disclosing a fact. The criteria behind each of these change over time, so the
# judgement belongs to external policy and not to the document. See decision 0002.
JUDGEMENT_TOKENS = (
    "pqc", "posture", "ready", "readiness", "compliant", "compliance",
    "secure", "security", "safe", "maturity", "score", "rating", "grade",
    "risk", "approved", "acceptable",
)


class Findings:
    """Collects one result per requirement."""

    def __init__(self):
        self.rows = []

    def add(self, cid, level, ok, detail):
        self.rows.append({"id": cid, "level": level, "ok": ok, "detail": detail})

    def failed_must(self):
        return [r for r in self.rows if r["level"] == "MUST" and not r["ok"]]

    def failed_should(self):
        return [r for r in self.rows if r["level"] == "SHOULD" and not r["ok"]]


def declared_rules(prof):
    """Every rule the file declares itself, product and interface alike."""
    return list(prof.get("productRules", [])) + list(prof.get("interfaceRules", []))


def vocabularies(prof):
    """Every value appearing in any declared *Vocabulary list."""
    values = set()
    for key, val in prof.items():
        if key.endswith("Vocabulary") and isinstance(val, list):
            values.update(v for v in val if isinstance(v, str))
    return values


# --------------------------------------------------------------------------- #
# The checks                                                                   #
# --------------------------------------------------------------------------- #
def c1_objective(prof, f):
    obj = prof.get("objective")
    if not isinstance(obj, dict):
        f.add("C1", "MUST", False, "no 'objective' object")
        return
    missing = [k for k in ("consumer", "decision") if not str(obj.get(k, "")).strip()]
    if missing:
        f.add("C1", "MUST", False, "objective is missing: %s" % ", ".join(missing))
    else:
        f.add("C1", "MUST", True, "consumer and decision both stated")


def c2_identity(prof, f):
    problems = []
    if not str(prof.get("profileId", "")).strip():
        problems.append("no profileId")
    if not str(prof.get("version", "")).strip():
        problems.append("no version")
    applies = prof.get("appliesTo") or {}
    carriers = [k for k in applies if k != "$comment"]
    if not carriers:
        problems.append("no carrier declared in appliesTo")
    for c in carriers:
        rng = applies[c]
        if not isinstance(rng, dict) or "min" not in rng or "tested" not in rng:
            problems.append("appliesTo.%s lacks min and tested" % c)
    if problems:
        f.add("C2", "MUST", False, "; ".join(problems))
    else:
        f.add("C2", "MUST", True,
              "%s v%s, carriers: %s" % (prof["profileId"], prof["version"],
                                        ", ".join(sorted(carriers))))


def c3_no_instances(prof, vocab_source, f):
    """No rule may name a product, a vendor, or an interface instance.

    'vocab_source' is the profile with its base resolved where there is one,
    because a derived profile inherits its vocabularies and does not restate
    them. Checking a derived profile against its own declarations alone would
    reject a sector profile that requires an interface type the base defines."""
    problems = []
    vocab = vocabularies(vocab_source)
    iface_types = set(vocab_source.get("interfaceTypeVocabulary", []))

    for r in declared_rules(prof):
        rid = r.get("id", "?")

        # The instance label is chosen by the producer and is never constrained.
        if r.get("attribute") == "interfaceId":
            problems.append("%s constrains interfaceId, which is an instance label" % rid)

        # A conditional guard must reference a controlled value.
        cond = r.get("requiredWhen") or {}
        for key in ("equals", "notEquals"):
            if key in cond:
                val = cond[key]
                if isinstance(val, str) and val not in vocab:
                    problems.append(
                        "%s requiredWhen %s %r is not a value in any declared vocabulary"
                        % (rid, key, val))

        # A structural rule must require a controlled interface type.
        spec = (r.get("constraint") or {}).get("minInterfacesOfType")
        if isinstance(spec, dict):
            t = spec.get("interfaceType")
            if t not in iface_types:
                problems.append(
                    "%s requires interfaceType %r, which is not in interfaceTypeVocabulary"
                    % (rid, t))

    if problems:
        f.add("C3", "MUST", False, "; ".join(problems))
    else:
        f.add("C3", "MUST", True, "no rule names an instance")


def c4_rule_shape(prof, f):
    problems = []
    seen = {}
    for r in declared_rules(prof):
        rid = r.get("id")
        if not rid:
            problems.append("a rule has no id")
            continue
        if rid in seen:
            problems.append("duplicate rule id %s" % rid)
        seen[rid] = r
        if r.get("level") not in LEVELS:
            problems.append("%s has level %r, expected one of %s"
                            % (rid, r.get("level"), "/".join(LEVELS)))
        if not r.get("constraint"):
            problems.append("%s has no constraint" % rid)

        # Withholdability is stated for every rule that assesses a disclosed
        # attribute. Structural rules that only count interfaces are exempt,
        # because there is no attribute for a producer to withhold.
        assesses_attribute = ("attribute" in r
                              or "productAttribute" in (r.get("constraint") or {}))
        if assesses_attribute and not isinstance(r.get("withholdable"), bool):
            problems.append("%s does not state 'withholdable'" % rid)

    if problems:
        f.add("C4", "MUST", False, "; ".join(problems))
    else:
        f.add("C4", "MUST", True, "%d rule(s) well-shaped" % len(seen))


def c5_naming(prof, f):
    problems = []
    for r in prof.get("interfaceRules", []):
        rid, attr = r.get("id", "?"), r.get("attribute")
        if not attr:
            continue
        if not CAMEL.match(attr):
            problems.append("%s: %r is not lowerCamelCase" % (rid, attr))
        if attr.endswith("Current"):
            problems.append("%s: %r uses the rejected 'Current' suffix; "
                            "a bare name already denotes present state" % (rid, attr))
        if attr.endswith("Supported") and not r.get("list"):
            problems.append("%s: %r declares a capability and so is a set; "
                            "the rule needs 'list': true" % (rid, attr))
    if problems:
        f.add("C5", "MUST", False, "; ".join(problems))
    else:
        f.add("C5", "MUST", True, "attribute names follow the conventions")


def c6_no_judgements(prof, f):
    problems = []
    for r in declared_rules(prof):
        attr = r.get("attribute") or (r.get("constraint") or {}).get("productAttribute")
        if not attr:
            continue
        low = attr.lower()
        hits = [t for t in JUDGEMENT_TOKENS if t in low]
        if hits:
            problems.append("%s: %r suggests a derived judgement (%s); "
                            "record the facts and let external policy judge"
                            % (r.get("id", "?"), attr, ", ".join(hits)))
    if problems:
        f.add("C6", "MUST", False, "; ".join(problems))
    else:
        f.add("C6", "MUST", True, "no attribute asserts a conclusion")


def c7_extension(path, prof, f):
    ext = prof.get("extends")
    if not ext:
        f.add("C7", "MUST", True, "not an extension")
        return
    missing = [k for k in ("profileId", "version") if not str(ext.get(k, "")).strip()]
    if missing:
        f.add("C7", "MUST", False, "extends is missing: %s" % ", ".join(missing))
        return
    try:
        load_profile(path)
    except ProfileError as err:
        f.add("C7", "MUST", False, str(err))
        return
    except (OSError, KeyError) as err:
        f.add("C7", "MUST", False, "base could not be resolved: %s" % err)
        return
    f.add("C7", "MUST", True,
          "pins %s v%s; base resolves and no override relaxes it"
          % (ext["profileId"], ext["version"]))


def c8_exclusions(prof, f):
    ex = prof.get("exclusions")
    if not isinstance(ex, list) or not ex:
        f.add("C8", "SHOULD", False, "no 'exclusions' recorded")
        return
    unexplained = [e.get("item", "?") for e in ex
                   if isinstance(e, dict) and not str(e.get("reason", "")).strip()]
    if unexplained:
        f.add("C8", "SHOULD", False,
              "exclusion(s) with no reason: %s" % ", ".join(unexplained))
    else:
        f.add("C8", "SHOULD", True, "%d exclusion(s), each with a reason" % len(ex))


def c9_artifacts(path, prof, f):
    art = prof.get("artifacts")
    if not isinstance(art, dict):
        f.add("C9", "SHOULD", False, "no 'artifacts' declared")
        return
    here = os.path.dirname(os.path.abspath(path))
    wanted = ("mapping", "conformingExample", "nonConformingExample")
    problems = []
    for key in wanted:
        names = art.get(key)
        if not names:
            problems.append("no %s" % key)
            continue
        for name in (names if isinstance(names, list) else [names]):
            if not os.path.exists(os.path.join(here, name)):
                problems.append("%s: %s not found" % (key, name))
    if problems:
        f.add("C9", "SHOULD", False, "; ".join(problems))
    else:
        f.add("C9", "SHOULD", True, "mapping and both example documents present")


def c10_changelog(path, prof, f):
    log = prof.get("changelog")
    if isinstance(log, list) and log:
        kinds = {"tightening", "relaxing", "editorial"}
        bad = []
        for entry in log:
            for ch in entry.get("changes", []):
                if ch.get("kind") not in kinds:
                    bad.append("%s: %r" % (entry.get("version", "?"), ch.get("kind")))
        if bad:
            f.add("C10", "SHOULD", False,
                  "change(s) not classified as tightening/relaxing/editorial: %s"
                  % ", ".join(bad))
        else:
            f.add("C10", "SHOULD", True, "%d version(s) recorded" % len(log))
        return
    ref = prof.get("changelogRef")
    if ref and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(path)), ref)):
        f.add("C10", "SHOULD", True, "changelog held in %s" % ref)
        return
    f.add("C10", "SHOULD", False, "no changelog and no changelogRef")


# --------------------------------------------------------------------------- #
def check(path):
    with open(path, encoding="utf-8") as fh:
        prof = json.load(fh)

    # Vocabularies are inherited rather than restated, so resolve the base where
    # there is one. A failure to resolve is not swallowed: C7 reports it.
    vocab_source = prof
    if prof.get("extends"):
        try:
            vocab_source = load_profile(path)[0]
        except (ProfileError, OSError, KeyError):
            pass

    f = Findings()
    c1_objective(prof, f)
    c2_identity(prof, f)
    c3_no_instances(prof, vocab_source, f)
    c4_rule_shape(prof, f)
    c5_naming(prof, f)
    c6_no_judgements(prof, f)
    c7_extension(path, prof, f)
    c8_exclusions(prof, f)
    c9_artifacts(path, prof, f)
    c10_changelog(path, prof, f)
    return prof, f


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    strict = "--strict" in argv
    as_json = "--json" in argv

    try:
        prof, f = check(args[0])
    except (OSError, ValueError) as err:
        print("CANNOT READ PROFILE: %s" % err, file=sys.stderr)
        return 2

    bad = f.failed_must() + (f.failed_should() if strict else [])

    if as_json:
        print(json.dumps({"profileId": prof.get("profileId"),
                          "version": prof.get("version"),
                          "wellFormed": not bad,
                          "strict": strict,
                          "findings": f.rows}, indent=2))
        return 1 if bad else 0

    print("Profile : %s v%s" % (prof.get("title", "?"), prof.get("version", "?")))
    print("File    : %s" % args[0])
    print("=" * 74)
    for r in f.rows:
        mark = "PASS" if r["ok"] else ("FAIL" if r["level"] == "MUST" else "warn")
        print("  [%s] %-4s %-6s %s" % (mark, r["id"], r["level"], r["detail"]))
    print("=" * 74)
    if f.failed_must():
        print("VERDICT : NOT WELL-FORMED  (failed %s)"
              % ", ".join(r["id"] for r in f.failed_must()))
    elif f.failed_should() and strict:
        print("VERDICT : NOT WELL-FORMED under --strict  (failed %s)"
              % ", ".join(r["id"] for r in f.failed_should()))
    elif f.failed_should():
        print("VERDICT : WELL-FORMED  (with %d SHOULD warning(s))" % len(f.failed_should()))
    else:
        print("VERDICT : WELL-FORMED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
