#!/usr/bin/env python3
"""
Profile well-formedness checker.

Checks a machine-readable profile against requirements C1 to C16 of the
Conformance section, which state what makes a profile well-formed under this
methodology. This is the second of the three conformance targets: a CBOM
document is checked against a profile by validate_cbom.py, and a profile is
checked against the methodology here.

C1  MUST    states the consumer, the decision, and the options it chooses between
C2  MUST    carries an identifier and version, and a carrier acceptance range
C3  MUST    no rule refers to a named product, vendor, or interface instance
C4  MUST    every rule has an identifier, a level, and a withholdability statement
C5  MUST    attribute names follow the naming conventions
C6  MUST    no rule requires a derived judgement
C7  MUST    extension pins the base and relaxes nothing
C8  SHOULD  states what it deliberately excludes, and why
C9  SHOULD  is accompanied by a mapping and by conforming and non-conforming examples
C10 SHOULD  carries a changelog classifying each change
C11 MUST    declares its scope: subject, relationship types, lifecycle stages
C12 MUST    its rules are consistent with its declared orientation
C13 MUST    group rules are keyed to a real vocabulary and cover it
C14 MUST    identifier schemes are declared and match what the rules reference
C15 MUST    carries a profile tag, unique along its inheritance chain
C16 MUST    rule ids are local and carry the kind letter of the section they sit in

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
    from validate_cbom import (load_profile, ProfileError, profile_tag,
                               SUBJECT_TYPES, LIFECYCLE_STAGES, ORIENTATIONS,
                               is_forward_looking, present_state_counterparts)
except ImportError:  # allow running from another directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from validate_cbom import (load_profile, ProfileError, profile_tag,
                               SUBJECT_TYPES, LIFECYCLE_STAGES, ORIENTATIONS,
                               is_forward_looking, present_state_counterparts)

LEVELS = ("MUST", "SHOULD", "MAY")
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")

# C15/C16. A rule id is local to the profile that declares it and is cited as
# '<profileTag>#<ruleId>'. The tag is the half that must be unique along the
# chain; the id only has to be unique within its own file. See decision 0011.
TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RULE_ID = re.compile(r"^[A-Z][0-9]+$")
MEMBER_ID = re.compile(r"^[A-Z][0-9]+\.[0-9]+$")
KIND_LETTER = {"productRules": "P", "interfaceRules": "I", "groupRules": "G"}

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
    """Every rule the file declares itself, product and interface alike.

    Group members count: they are rules, and C3 to C6 apply to them exactly as
    to any other. The group shell is excluded because it constrains coverage
    rather than an attribute, and C13 checks it instead."""
    rules = list(prof.get("productRules", [])) + list(prof.get("interfaceRules", []))
    for g in prof.get("groupRules", []):
        rules.extend(g.get("members", []))
    return rules


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
    problems = []
    missing = [k for k in ("consumer", "decision") if not str(obj.get(k, "")).strip()]
    if missing:
        problems.append("objective is missing: %s" % ", ".join(missing))

    # The action-choice test from Method step 1, made mechanical. A decision the
    # consumer cannot answer in more than one way is not a decision, and a
    # profile written from one has no principled place to stop.
    options = obj.get("decisionOptions")
    if not isinstance(options, list):
        problems.append("no 'decisionOptions'; state the actions the consumer "
                        "chooses between, so the decision is one that can be acted on")
    else:
        stated = [o for o in options if isinstance(o, str) and o.strip()]
        if len(stated) < 2:
            problems.append("decisionOptions lists %d option(s); a decision has at "
                            "least two, or the consumer is not deciding anything"
                            % len(stated))

    if problems:
        f.add("C1", "MUST", False, "; ".join(problems))
    else:
        f.add("C1", "MUST", True, "consumer, decision, and %d decision option(s) stated"
              % len(obj["decisionOptions"]))


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

    # A restated inherited block silently overrides the base's value, so a later
    # change to the base would not reach this profile and would raise no error.
    # 'appliesTo' is exempt: narrowing the carrier range is a real choice, and
    # check_range_narrows already rejects a range that widens the base's.
    diverged = []
    try:
        base_path = os.path.join(os.path.dirname(os.path.abspath(path)), ext["file"])
        base = load_profile(base_path)[0]
    except (ProfileError, OSError, KeyError):
        base = None
    if base:
        # Vocabularies are deliberately not checked here: narrowing an inherited
        # vocabulary is a tightening and a derived profile may legitimately do
        # it. Only the blocks that carry no requirement of their own are checked,
        # because for those a divergence can only be a mistake.
        for key in ("disclosure", "conformanceKeywords"):
            if key in prof and prof[key] != base.get(key):
                diverged.append(key)
    if diverged:
        f.add("C7", "MUST", False,
              "restates inherited block(s) with a different value: %s. "
              "The base's value is overridden silently, so a change to the base "
              "would not reach this profile" % ", ".join(diverged))
        return

    f.add("C7", "MUST", True,
          "pins %s v%s; base resolves, no override relaxes it, no inherited block diverges"
          % (ext["profileId"], ext["version"]))


def evidenced_relationship_types(prof):
    """The relationship kinds the profile's rules actually constrain.

    The scope declaration is checked against this rather than trusted, because a
    scope statement maintained by hand drifts from the rules it claims to
    describe, and a stale one is worse than none: it reads as authoritative.

    Only 'interface' can be evidenced today, because it is the only refined
    relationship type the model names. The set grows as the model does."""
    kinds = set()
    if prof.get("interfaceRules"):
        kinds.add("interface")
    for r in prof.get("productRules", []):
        c = r.get("constraint") or {}
        if "minInterfaces" in c or "minInterfacesOfType" in c:
            kinds.add("interface")
    return kinds


def c11_scope(prof, scope_source, evidence_reliable, f):
    """C11. The profile declares what it describes and what it will accept.

    'scope_source' is the profile with its base resolved where there is one, so
    a derived profile that does not restate the scope inherits it rather than
    failing. Where it does restate it, the resolved value is the derived
    profile's own, and validate_cbom rejects a restatement that widens the
    base."""
    scope = scope_source.get("scope")
    if not isinstance(scope, dict):
        f.add("C11", "MUST", False,
              "no 'scope' object; a profile states the subject it describes and "
              "the lifecycle stages it accepts")
        return

    problems = []

    subject = scope.get("subjectType")
    if not subject:
        problems.append("no subjectType")
    elif subject not in SUBJECT_TYPES:
        problems.append("subjectType %r is not one of %s"
                        % (subject, "/".join(SUBJECT_TYPES)))

    orientation = scope.get("orientation")
    if not orientation:
        problems.append("no orientation; state whether the profile reports present "
                        "state, migration capability, or both")
    elif orientation not in ORIENTATIONS:
        problems.append("orientation %r is not one of %s"
                        % (orientation, "/".join(ORIENTATIONS)))

    stages = scope.get("lifecycleStages")
    if not isinstance(stages, list) or not stages:
        problems.append("no lifecycleStages; state which stages of reported data "
                        "the profile accepts")
    else:
        unknown = [s for s in stages if s not in LIFECYCLE_STAGES]
        if unknown:
            problems.append("lifecycleStages contains %s, not in %s"
                            % (", ".join(repr(s) for s in unknown),
                               "/".join(LIFECYCLE_STAGES)))

    declared = scope.get("relationshipTypes")
    if not isinstance(declared, list) or not declared:
        problems.append("no relationshipTypes")
    elif not evidence_reliable:
        # The base did not resolve, so the inherited rules are not visible and
        # the declaration cannot be checked against them. C7 reports the
        # resolution failure; repeating it here would be noise.
        pass
    else:
        evidenced = evidenced_relationship_types(scope_source)
        undeclared = evidenced - set(declared)
        unevidenced = set(declared) - evidenced
        if undeclared:
            problems.append("rules constrain %s, which scope does not declare"
                            % ", ".join(sorted(undeclared)))
        if unevidenced:
            problems.append("scope declares %s, which no rule constrains"
                            % ", ".join(sorted(unevidenced)))

    if problems:
        f.add("C11", "MUST", False, "; ".join(problems))
    else:
        f.add("C11", "MUST", True,
              "%s, %s; accepts %s" % (subject, orientation, ", ".join(stages)))


def c12_orientation(prof, resolved, evidence_reliable, f):
    """C12. The rules a profile imposes match the orientation it declares.

    Orientation exists to stop a shared attribute changing sense between profile
    kinds. Declaring it is not enough on its own: the value has to constrain
    something, or it becomes a label that drifts away from the rules while
    still being read as authoritative.

    Checked against the resolved profile, so an inherited rule counts. That is
    the normal case rather than an edge one: the migration example declares the
    capability attributes itself and inherits every present-state attribute from
    the baseline it extends."""
    scope = resolved.get("scope") or {}
    orientation = scope.get("orientation")
    if orientation not in ORIENTATIONS:
        f.add("C12", "MUST", True, "no valid orientation to check against (see C11)")
        return
    if not evidence_reliable:
        f.add("C12", "MUST", True, "base did not resolve; not checked (see C7)")
        return

    rules = list(resolved.get("interfaceRules", [])) + list(resolved.get("productRules", []))
    # Group members are rules and are usually the forward-looking ones, so
    # orientation has to govern them or the check misses what it exists for.
    for g in resolved.get("groupRules", []):
        rules.extend(g.get("members", []))
    required = set()
    forward = []
    for r in rules:
        attr = r.get("attribute") or (r.get("constraint") or {}).get("productAttribute")
        if not attr:
            continue
        required.add(attr)
        if is_forward_looking(attr):
            forward.append((r.get("id", "?"), attr))

    problems = []

    if orientation == "inventory" and forward:
        problems.append(
            "declares orientation 'inventory' but requires forward-looking "
            "attribute(s) %s. An inventory profile reports what is; a profile "
            "reporting what could be is 'migration' or 'both'"
            % ", ".join("%s (%s)" % (rid, a) for rid, a in forward))

    if orientation == "both":
        # The guarantee that makes 'both' meaningful: capability never arrives
        # instead of present state, only alongside it.
        unpaired = []
        for rid, attr in forward:
            candidates = present_state_counterparts(attr)
            if candidates and not (set(candidates) & required):
                unpaired.append("%s (%s, expected %s alongside it)"
                                % (rid, attr, " or ".join(candidates)))
        if unpaired:
            problems.append(
                "declares orientation 'both' but requires capability without "
                "the present state it is a capability for: %s. A consumer "
                "reading only the capability cannot tell what the interface "
                "does today" % "; ".join(unpaired))

    if orientation == "migration" and not forward:
        problems.append(
            "declares orientation 'migration' but requires no forward-looking "
            "attribute, so it reports present state only and is 'inventory'")

    if problems:
        f.add("C12", "MUST", False, "; ".join(problems))
    else:
        f.add("C12", "MUST", True,
              "orientation '%s' matches the rules: %d forward-looking attribute(s)"
              % (orientation, len(forward)))


def c13_group_rules(prof, resolved, evidence_reliable, f):
    """C13. A group rule is well-formed, and a declared scope for it is honoured.

    Two failures are worth catching separately. A group rule keyed by a
    vocabulary that does not exist evaluates against nothing and silently
    requires no entries at all, which reads as conformance. And a profile whose
    status rule covers only the purposes it took in scope has built a floor: a
    supplier can conform while saying nothing at all about the purposes the
    profile deferred, which is the outcome staging exists to avoid."""
    groups = resolved.get("groupRules") or []
    scope = resolved.get("scope") or {}

    if not groups:
        if scope.get("cryptographicPurposes"):
            f.add("C13", "MUST", False,
                  "scope declares cryptographicPurposes but no group rule is keyed "
                  "by them, so the declaration constrains nothing")
        else:
            f.add("C13", "MUST", True, "no group rules")
        return
    if not evidence_reliable:
        f.add("C13", "MUST", True, "base did not resolve; not checked (see C7)")
        return

    problems = []
    for g in groups:
        gid = g.get("id", "?")
        for key in ("group", "keyedBy", "keyVocabularyRef", "level"):
            if not g.get(key):
                problems.append("%s has no '%s'" % (gid, key))
        if not g.get("members"):
            problems.append("%s declares no members, so it requires an entry with "
                            "nothing in it" % gid)

        ref = g.get("keyVocabularyRef")
        vocab = resolved.get(ref) if ref else None
        if ref and not isinstance(vocab, list):
            problems.append("%s is keyed by %r, which is not a declared vocabulary; "
                            "the rule would require no entries" % (gid, ref))
            continue

        coverage = g.get("coverage")
        if coverage not in ("all-purposes", "in-scope"):
            problems.append("%s has coverage %r, expected all-purposes or in-scope"
                            % (gid, coverage))

        declared = scope.get("cryptographicPurposes")
        if declared:
            unknown = [p for p in declared if vocab and p not in vocab]
            if unknown:
                problems.append("scope.cryptographicPurposes contains %s, absent from %s"
                                % (", ".join(repr(u) for u in unknown), ref))
            if coverage == "in-scope" and len(declared) < len(vocab or []):
                problems.append(
                    "%s covers only the %d purpose(s) in scope while the vocabulary "
                    "has %d. A purpose the profile defers still owes a status, or the "
                    "profile is a floor rather than a stage" % (gid, len(declared), len(vocab or [])))

    if problems:
        f.add("C13", "MUST", False, "; ".join(problems))
    else:
        f.add("C13", "MUST", True,
              "%d group rule(s), keyed and covered" % len(groups))


def c14_identifier_schemes(prof, resolved, f):
    """C14. Identifier schemes are declared, and the declaration matches the rules.

    Q38's lever. Identity cannot be settled in general, because some asset classes
    have no agreed identifier; it can be settled per profile, by naming the form
    required for each class. The check is deliberately not that a value belongs to
    a registry — the checker does not hold the registry and would be guessing.
    What it checks is that the declaration and the rules agree, in both
    directions, because a scheme nobody references and a reference to a scheme
    nobody declared are the two ways this drifts."""
    declared = resolved.get("identifierSchemes")
    referenced = {}
    for r in declared_rules(resolved):
        ref = r.get("schemeRef")
        if ref:
            referenced.setdefault(ref, []).append(r.get("id", "?"))

    if not referenced and not declared:
        f.add("C14", "MUST", True, "no identifier schemes declared or referenced")
        return
    if not isinstance(declared, dict):
        f.add("C14", "MUST", False,
              "rule(s) %s name an identifier scheme, but the profile declares none"
              % ", ".join(sorted(sum(referenced.values(), []))))
        return

    problems = []
    for ref, rules in sorted(referenced.items()):
        if not str(declared.get(ref, "")).strip():
            problems.append("%s reference scheme %r, which is not declared"
                            % (", ".join(rules), ref))
    unused = [k for k in declared if k not in referenced and not k.startswith("$")]
    if unused:
        problems.append("scheme(s) declared for %s, which no rule references; a scheme "
                        "nobody applies drifts from the rules while reading as authoritative"
                        % ", ".join(sorted(unused)))

    if problems:
        f.add("C14", "MUST", False, "; ".join(problems))
    else:
        f.add("C14", "MUST", True,
              "%d scheme(s) declared and referenced: %s"
              % (len(referenced), ", ".join("%s=%s" % (k, declared[k])
                                            for k in sorted(referenced))))


def c15_profile_tag(path, prof, f):
    """The profile carries a tag, and no ancestor already uses it.

    Rule ids are local, so 'I9' names a rule only once a reader knows which
    profile declared it. The tag is that handle. It is the one identifier that
    has to be unique along a chain, and moving the uniqueness requirement here
    from the rule ids is what lets a derived profile number from I1 and lets a
    family go three levels deep without a reservation scheme. See decision 0011."""
    tag = prof.get("profileTag")
    if tag is None:
        derived = profile_tag(prof)
        f.add("C15", "MUST", False,
              "no profileTag; every rule this profile declares would have to be cited "
              "as %r, inferred from the profileId rather than stated" % ("%s#..." % derived))
        return
    if not TAG.match(str(tag)):
        f.add("C15", "MUST", False,
              "profileTag %r is not a lowercase kebab-case token; it appears in every "
              "citation of every rule, so it has to be typeable and stable" % tag)
        return
    ext = prof.get("extends")
    if not ext:
        f.add("C15", "MUST", True, "tag %r, base of its family" % tag)
        return

    # The base is resolved here rather than the composed profile, because a
    # colliding tag is exactly what stops the composed profile from resolving.
    # Reading the answer off the failure would report this as C7's problem and
    # leave C15 saying nothing about the one thing it is for.
    try:
        base_path = os.path.join(os.path.dirname(os.path.abspath(path)), ext["file"])
        chain = list(load_profile(base_path)[0].get("_chain", []))
    except (ProfileError, OSError, KeyError) as err:
        f.add("C15", "MUST", True,
              "tag %r is well-formed; uniqueness along the chain was not checked "
              "because the base did not resolve (%s)" % (tag, err))
        return
    if tag in chain:
        f.add("C15", "MUST", False,
              "profileTag %r is already used by an ancestor; the chain above this "
              "profile is %s, and a repeated tag makes every citation in it ambiguous"
              % (tag, " -> ".join(chain)))
        return
    f.add("C15", "MUST", True,
          "tag %r, unique in chain %s" % (tag, " -> ".join(chain + [tag])))


def c16_rule_ids(prof, f):
    """Rule ids are local, and the letter says which kind of rule it is.

    Because an id is always cited against a tag, the letter is free to carry the
    thing a reader actually wants from it: whether the rule is evaluated once
    per product, once per interface, or once per entry in a group. So the letter
    is fixed by the section the rule sits in rather than chosen by the author.

    Ids are not required to be contiguous. Decision 0011 says a released id is
    never reused, which means gaps are correct and a checker that demanded a
    dense sequence would forbid the thing the rule exists to allow."""
    problems = []
    for section, letter in KIND_LETTER.items():
        for rule in prof.get(section, []):
            rid = str(rule.get("id", ""))
            if "#" in rid:
                problems.append(
                    "%s declares its id qualified; a profile writes its own ids bare "
                    "and readers qualify them with the tag" % rid)
                continue
            if not RULE_ID.match(rid):
                problems.append("%r is not of the form <letter><number>" % rid)
                continue
            if rid[0] != letter:
                problems.append(
                    "%s sits in %s, so it takes the letter %s; %s is the letter for %s"
                    % (rid, section, letter, rid[0],
                       {v: k for k, v in KIND_LETTER.items()}.get(rid[0], "no section")))
            if section == "groupRules":
                for member in rule.get("members", []):
                    mid = str(member.get("id", ""))
                    if not MEMBER_ID.match(mid) or not mid.startswith(rid + "."):
                        problems.append(
                            "group member id %r should be %s.<number>" % (mid, rid))

    for ov in prof.get("overrides", []):
        oid = str(ov.get("id", ""))
        if "#" not in oid:
            problems.append(
                "override on %r is not qualified; an override names the rule it tightens "
                "as <profileTag>#<ruleId>, because the target belongs to another profile"
                % oid)

    if problems:
        f.add("C16", "MUST", False, "; ".join(problems))
        return
    counted = sum(len(prof.get(s, [])) for s in KIND_LETTER)
    f.add("C16", "MUST", True,
          "%d declared rule id(s) well-formed and local" % counted)


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
    resolved = True
    if prof.get("extends"):
        resolved = False
        try:
            vocab_source = load_profile(path)[0]
            resolved = True
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
    c11_scope(prof, vocab_source, resolved, f)
    c12_orientation(prof, vocab_source, resolved, f)
    c13_group_rules(prof, vocab_source, resolved, f)
    c14_identifier_schemes(prof, vocab_source, f)
    c15_profile_tag(path, prof, f)
    c16_rule_ids(prof, f)
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
