#!/usr/bin/env python3
"""
Illustrative CBOM profile validator.

Demonstrates the conformance-checklist direction of a profile that is
product-independent, version-aware, and composable:

  * FORMAT check    -- is this CBOM in a carrier format/version the profile
                       accepts? ('appliesTo'). Refused below 'min', flagged
                       'legacy' between 'min' and 'tested', accepted at 'tested'.
  * COMPOSITION     -- a profile may 'extend' another. The base is resolved,
                       'overrides' are applied, and any override that RELAXES an
                       inherited rule is rejected. Extension is monotonic, so
                       conforming to a derived profile implies conforming to its
                       base.
  * SCOPE           -- 'scope.lifecycleStages' says which stages of reported
                       data the profile accepts, in the same sense as
                       'appliesTo' for carrier versions. It narrows the
                       lifecycleStage rule, so an interface reporting a stage
                       outside the set fails that rule. A derived profile may
                       narrow the set and may not widen it.
  * PRODUCT rules   -- constrain the SET of interfaces and product-level
                       attributes, naming no specific interface.
  * INTERFACE rules -- applied to every declared cryptographic interface, with
                       support for conditional rules ('requiredWhen') and
                       list-valued attributes ('list': true).
  * GROUP rules     -- a repeated group keyed by a controlled vocabulary, so an
                       interface can state one answer per cryptographic purpose
                       rather than one answer overall. Member rules are
                       evaluated inside an entry, so a 'requiredWhen' guard
                       refers to that entry. 'coverage' says whether an entry is
                       required for every value in the vocabulary or only for
                       those the profile's scope declares.

Disclosure states. An attribute is reported as one of:
  value      -- supplied and checked against the constraint
  withheld   -- declared withheld; satisfies a rule marked 'withholdable'
  unknown    -- declared unknown to the producer; never satisfies MUST
  undeclared -- neither a value nor a marker
  n/a        -- a conditional rule whose condition does not hold

Verdicts. The Conformance section defines three, and requires that refusal and
non-conformance be reported distinctly (T1, and "MUST NOT be merged"). They are
distinct here in the verdict, in the exit code, and in the JSON report:

  conforms          every MUST rule is satisfied at an accepted carrier version
  does not conform  the document was assessed and at least one MUST rule failed
  refused           the carrier version is below the profile's declared minimum,
                    so no assessment was performed. This says nothing about the
                    document, which may be entirely adequate. Treating it as a
                    failure penalises a producer for the age of a format rather
                    than for the content of its disclosure.

Conformance claims. A claim is the artifact that crosses an organisational
boundary: a producer hands it to a consumer, who was not present when the
evaluation ran. It names every profile evaluated with its whole chain and
version, binds itself to one document by digest, records the disclosure state of
what was assessed, and carries the list of what a verdict does not assert. A
claim that cannot be re-checked is a press release, so '--verify-claim' re-runs
the evaluation and reports where the claim and the document disagree. See
decision 0015.

Usage:
    python validate_cbom.py <cbom.json> <profile.rules.json> [--json]
    python validate_cbom.py <cbom.json> <profile.rules.json>... --claim
    python validate_cbom.py <cbom.json> <claim.json> --verify-claim [--profiles-dir DIR]

Exit codes:
    0  conforms
    1  does not conform
    2  usage error
    3  profile error, such as an override that relaxes an inherited rule
    4  refused: not assessed, as distinct from assessed and found short
    5  a claim does not match the document or the profiles it names
"""
import datetime
import hashlib
import json
import os
import sys


class ProfileError(Exception):
    """The profile itself is invalid, as distinct from a CBOM failing it."""

# Reader-side sets, deliberately lenient. The CycloneDX value for an
# authenticated cipher is "ae"; "aead" is accepted because documents in the
# wild carry it, and refusing to read a document over a spelling would report
# a missing algorithm rather than a malformed one. The mapping documents "ae"
# as the value a producer should write.
ENC_PRIMS = {"ae", "aead", "block-cipher", "stream-cipher"}
KEX_PRIMS = {"key-agree", "key-agreement", "kem"}
SIG_PRIMS = {"signature"}

LEVEL_ORDER = {"MAY": 0, "SHOULD": 1, "MUST": 2}
PROP = "pkic:profile:"

# The three verdicts, their exit codes, and how they are printed. Refusal has
# its own code because a caller that cannot distinguish it from failure will
# reject a producer for the age of a carrier format, which is the outcome the
# Conformance section forbids.
EXIT_FOR = {"conforms": 0, "does-not-conform": 1, "refused": 4}
EXIT_CLAIM_MISMATCH = 5
VERDICT_LABEL = {"conforms": "CONFORMS", "does-not-conform": "DOES NOT CONFORM",
                 "refused": "REFUSED"}

# Methodology-level vocabularies, fixed here rather than declared per profile so
# that two profiles cannot mean different things by the same word. Both are used
# by check_profile.py when it checks C11.
SUBJECT_TYPES = ("product", "service", "component", "estate-subset")
LIFECYCLE_STAGES = ("intended", "implemented", "configured", "observed")
STAGE_ATTRIBUTE = "lifecycleStage"

# Orientation. The same four values the working group already uses to classify
# its own aspects in _data/aspects.yml, less 'n-a': a profile that is neither
# about present state nor about migration is not a profile.
ORIENTATIONS = ("inventory", "migration", "both")

# Forward-looking attributes: those describing what an interface could do or
# will do, as against what it does. The 'Supported' suffix is the general form
# fixed by decision 0005; these three are named because they describe a future
# state without having a present-state counterpart to be suffixed from.
CAPABILITY_SUFFIX = "Supported"
ROADMAP_ATTRIBUTES = ("capabilityStatus", "blockedBy", "roadmapRef")


def is_forward_looking(attribute):
    return bool(attribute) and (attribute.endswith(CAPABILITY_SUFFIX)
                                or attribute in ROADMAP_ATTRIBUTES)


def present_state_counterparts(attribute):
    """The present-state names a capability attribute could be suffixed from.

    'keyExchangeSupported' -> ('keyExchange',). A capability attribute is a set
    and so is plural, while its present-state counterpart holds one value and is
    singular, so 'protocolVersionsSupported' -> ('protocolVersions',
    'protocolVersion'). Both are offered rather than guessed at, because a stem
    ending in 's' is not always a plural.

    Empty for a roadmap attribute, which describes a future state with no
    present-state equivalent, and for an attribute that is already present
    state."""
    if not attribute or not attribute.endswith(CAPABILITY_SUFFIX) \
            or len(attribute) == len(CAPABILITY_SUFFIX):
        return ()
    stem = attribute[:-len(CAPABILITY_SUFFIX)]
    return (stem, stem[:-1]) if stem.endswith("s") else (stem,)


def ver_tuple(s):
    return tuple(int(x) for x in str(s).split(".") if x.isdigit())


# --------------------------------------------------------------------------- #
# Profile loading and composition                                             #
# --------------------------------------------------------------------------- #
# Every constraint kind the evaluator can actually apply. A key outside these
# sets is a typo or an invention, and a rule carrying one constrains nothing
# while reporting 'ok' against every value — silent success, which is the
# failure mode this methodology is least able to tolerate. C13 already rejects
# it for group keys; C17 rejects it everywhere else. See decision 0013.
ATTRIBUTE_CONSTRAINTS = ("present", "minCount", "enum", "enumFull", "enumRef",
                         "startsWith")
PRODUCT_CONSTRAINTS = ("minInterfaces", "minInterfacesOfType", "minProviders",
                       "subjectIdentified", "productAttribute", "enumRef",
                       "orDeclaredAbsent", "absenceEnumRef")
# Keys naming a vocabulary the profile must declare. An unresolvable reference
# is the mirror defect: instead of passing everything it fails everything, and
# the report says only that the value was not accepted.
VOCABULARY_REFS = ("enumRef", "absenceEnumRef", "keyVocabularyRef")


def constraint_kinds(rule, section):
    allowed = PRODUCT_CONSTRAINTS if section == "productRules" else ATTRIBUTE_CONSTRAINTS
    return allowed


def check_evaluable(profile):
    """Every rule must be capable of failing a document and of passing one.

    Run on the resolved profile, so an inherited vocabulary counts as declared.
    Three defects are caught here, and all three are silent without it: a rule
    with no constraint (which used to raise an exception mid-evaluation rather
    than refusing the profile), a constraint key the evaluator does not
    implement, and a reference to a vocabulary that does not exist."""
    problems = []

    def check_one(rule, section, label):
        constraint = rule.get("constraint")
        if not isinstance(constraint, dict) or not constraint:
            problems.append("%s has no constraint, so it can neither pass nor fail a document"
                            % label)
            return
        allowed = constraint_kinds(rule, section)
        for key in constraint:
            if key not in allowed:
                problems.append(
                    "%s constrains %r, which the evaluator does not implement; the rule "
                    "would report 'ok' against every value" % (label, key))
        for key in VOCABULARY_REFS:
            ref = constraint.get(key)
            if ref and not profile.get(ref):
                problems.append(
                    "%s references the vocabulary %r, which the profile does not declare; "
                    "the rule would fail every value without saying why" % (label, ref))

    for section in ("productRules", "interfaceRules"):
        for rule in profile.get(section, []):
            check_one(rule, section, rule.get("_qid", rule.get("id", "?")))
    for group in profile.get("groupRules", []):
        ref = group.get("keyVocabularyRef")
        if ref and not profile.get(ref):
            problems.append("%s is keyed by the vocabulary %r, which the profile does not "
                            "declare; the group would require no entries"
                            % (group.get("_qid", group.get("id", "?")), ref))
        for member in group.get("members", []):
            check_one(member, "groupRules", member.get("_qid", member.get("id", "?")))

    if problems:
        raise ProfileError("; ".join(problems))
    return profile


def profile_tag(profile):
    """The short handle a rule id is cited against.

    A rule id is local to the profile that declared it, so 'I3' on its own does
    not name a rule: the citable form is '<profileTag>#<ruleId>'. The tag
    defaults to the last dotted segment of the profileId, which is already the
    part a reader says aloud. See decision 0011."""
    tag = profile.get("profileTag")
    if not tag:
        tag = str(profile.get("profileId", "")).split(".")[-1]
    return tag


def stamp_qids(profile, tag):
    """Attach the qualified id to every rule this profile declares."""
    for section in ("productRules", "interfaceRules"):
        for rule in profile.get(section, []):
            rule["_qid"] = "%s#%s" % (tag, rule["id"])
    for group in profile.get("groupRules", []):
        group["_qid"] = "%s#%s" % (tag, group["id"])
        for member in group.get("members", []):
            member["_qid"] = "%s#%s" % (tag, member["id"])


def all_qids(profile):
    out = [r["_qid"] for r in profile.get("productRules", [])
           + profile.get("interfaceRules", [])]
    for group in profile.get("groupRules", []):
        out.append(group["_qid"])
        out += [m["_qid"] for m in group.get("members", [])]
    return out


def origin_map(profile):
    """Map every qualified rule id to the profile that imposed it.

    A rule keeps the id of the profile that introduced it however far down the
    chain it is later tightened, so the origin names the introducer first and
    then the tighteners in the order they applied."""
    introduced = profile.get("_introducedBy", {})
    tightened = profile.get("_tightenedBy", {})
    out = {}
    for qid, who in introduced.items():
        tags = tightened.get(qid)
        out[qid] = ("%s (tightened by %s)" % (who, ", ".join(tags))) if tags else who
    return out


def load_profile(path):
    """Load a profile, resolving 'extends' and applying 'overrides'.

    Returns (profile, origin, notes) where origin maps a qualified rule id to
    the profileId that imposed it, and notes records composition events."""
    with open(path, encoding="utf-8") as fh:
        prof = json.load(fh)
    notes = []

    tag = profile_tag(prof)
    stamp_qids(prof, tag)

    ext = prof.get("extends")
    if not ext:
        prof["profileTag"] = tag
        prof["_chain"] = [tag]
        prof["_introducedBy"] = {q: prof["profileId"] for q in all_qids(prof)}
        prof["_tightenedBy"] = {}
        apply_scope(prof)
        check_evaluable(prof)
        return prof, origin_map(prof), notes

    base_file = ext.get("file")
    if not base_file:
        raise ProfileError("extends: no 'file' hint, cannot resolve base profile")
    base_path = os.path.join(os.path.dirname(os.path.abspath(path)), base_file)
    base, _base_origin, base_notes = load_profile(base_path)
    notes += base_notes

    if base.get("profileId") != ext.get("profileId"):
        raise ProfileError("extends: resolved base %r does not match declared %r"
                         % (base.get("profileId"), ext.get("profileId")))
    if str(base.get("version")) != str(ext.get("version")):
        raise ProfileError("extends: base is version %s, profile pins %s"
                         % (base.get("version"), ext.get("version")))

    # Rule ids are local to the profile that declares them, so nothing stops a
    # derived profile from calling its first interface rule I1 as well. What
    # must be unique along the chain is the tag, because that is what makes a
    # citation unambiguous. This is the check that replaces the old rule-id
    # collision error, and it is the reason the scheme survives three levels.
    if tag in base.get("_chain", []):
        raise ProfileError(
            "profile tag %r is already used in this family (%s); the tag is the "
            "handle every rule this profile introduces is cited against, so it "
            "must be unique along the chain" % (tag, " -> ".join(base["_chain"])))

    merged = dict(base)
    merged.update({k: v for k, v in prof.items()
                   if k not in ("productRules", "interfaceRules", "groupRules",
                                "overrides", "extends")})
    merged["profileId"] = prof["profileId"]
    merged["profileTag"] = tag
    merged["title"] = prof.get("title", base.get("title"))
    merged["version"] = prof.get("version")
    merged["extends"] = ext
    merged["_chain"] = list(base.get("_chain", [])) + [tag]
    merged["_introducedBy"] = dict(base.get("_introducedBy", {}))
    merged["_tightenedBy"] = {k: list(v) for k, v in base.get("_tightenedBy", {}).items()}

    check_range_narrows(base, prof)
    check_scope_narrows(base, prof)

    for section in ("productRules", "interfaceRules"):
        inherited = [dict(r) for r in base.get(section, [])]
        by_qid = {r["_qid"]: r for r in inherited}
        for ov in prof.get("overrides", []):
            if "#" not in str(ov.get("id", "")):
                raise ProfileError(
                    "override %r is not qualified: an override names the rule it "
                    "tightens as '<profileTag>#<ruleId>', because a bare id is "
                    "local to the profile that declared it" % ov.get("id"))
            if ov["id"] in by_qid:
                target = by_qid[ov["id"]]
                check_override_tightens(target, ov, notes, base, prof)
                # The id is not copied: a tightened rule keeps the id, and the
                # tag, of the profile that introduced it. That is what lets a
                # claim citing it stay meaningful three levels down.
                target.update({k: v for k, v in ov.items()
                               if k not in ("note", "id")})
                merged["_tightenedBy"].setdefault(ov["id"], []).append(tag)
        added = prof.get(section, [])
        for r in added:
            if r["_qid"] in by_qid:
                raise ProfileError("rule id %s is declared twice in %s" % (r["id"], tag))
            by_qid[r["_qid"]] = r
            merged["_introducedBy"][r["_qid"]] = prof["profileId"]
        merged[section] = inherited + added

    # A derived profile may add a group, and may tighten one member of a group it
    # inherited, or widen that group's coverage. Settling Q49: without member
    # overrides the only ways to ask for more depth were to restate the group,
    # which silently replaces the base's coverage, or to add a parallel group,
    # which asks a producer for the same fact twice under two names.
    inherited_groups = []
    for g in base.get("groupRules", []):
        g = dict(g)
        g["members"] = [dict(m) for m in g.get("members", [])]
        inherited_groups.append(g)
    seen_groups = {g["_qid"] for g in inherited_groups}
    group_by_qid = {g["_qid"]: g for g in inherited_groups}
    member_by_qid = {m["_qid"]: (g, m)
                     for g in inherited_groups for m in g.get("members", [])}

    for ov in prof.get("overrides", []):
        oid = ov.get("id")
        if oid in group_by_qid:
            check_coverage_tightens(oid, group_by_qid[oid], ov, notes)
            group_by_qid[oid].update({k: v for k, v in ov.items()
                                      if k not in ("note", "id", "members")})
            merged["_tightenedBy"].setdefault(oid, []).append(tag)
        elif oid in member_by_qid:
            _group, target = member_by_qid[oid]
            check_override_tightens(target, ov, notes, base, prof)
            target.update({k: v for k, v in ov.items() if k not in ("note", "id")})
            merged["_tightenedBy"].setdefault(oid, []).append(tag)

    for g in prof.get("groupRules", []):
        if g["_qid"] in seen_groups:
            raise ProfileError("group rule id %s is declared twice in %s" % (g["id"], tag))
        seen_groups.add(g["_qid"])
        merged["_introducedBy"][g["_qid"]] = prof["profileId"]
        for m in g.get("members", []):
            merged["_introducedBy"][m["_qid"]] = prof["profileId"]
    merged["groupRules"] = inherited_groups + list(prof.get("groupRules", []))

    unmatched = [o["id"] for o in prof.get("overrides", [])
                 if o["id"] not in merged["_introducedBy"]]
    if unmatched:
        raise ProfileError("overrides reference unknown rule(s): %s" % ", ".join(unmatched))

    apply_scope(merged)
    check_evaluable(merged)
    return merged, origin_map(merged), notes


def apply_scope(profile):
    """Narrow the lifecycle-stage rule to the stages the profile's scope accepts.

    'scope.lifecycleStages' is an acceptance constraint in the same sense as
    'appliesTo': it says which reported data the profile is prepared to evaluate.
    Rather than adding a parallel check, it is applied by narrowing the enum on
    whichever rule constrains lifecycleStage, so a stage outside the set fails
    that rule and is reported against it. The full vocabulary is kept as
    'enumFull' so the failure can say the stage is real but out of scope, rather
    than implying the producer wrote something meaningless.

    Applied to the resolved profile, so a derived profile's narrower set wins.
    Mutates in place and is idempotent."""
    stages = (profile.get("scope") or {}).get("lifecycleStages")
    if not stages:
        return profile
    for rule in profile.get("interfaceRules", []):
        if rule.get("attribute") != STAGE_ATTRIBUTE:
            continue
        constraint = dict(rule.get("constraint") or {})
        if "enum" not in constraint:
            continue
        constraint.setdefault("enumFull", list(constraint["enum"]))
        constraint["enum"] = [s for s in constraint["enumFull"] if s in stages]
        rule["constraint"] = constraint
    return profile


# An override's constraint has to impose at least everything the base's did.
# Each comparator answers one question: is the new value at least as demanding
# as the old one? Anything this table cannot answer is refused rather than
# assumed, which is what makes the guarantee hold for constraints a later
# version invents.
def _num_tightens(old, new):
    return (new >= old, "%s -> %s" % (old, new))


def _subset_tightens(old, new):
    o, n = set(old or []), set(new or [])
    return (n <= o, "%d value(s) -> %d" % (len(o), len(n)))


def _prefix_tightens(old, new):
    return (str(new).startswith(str(old)), "%r -> %r" % (old, new))


def _present_tightens(old, new):
    # Requiring presence is stricter than requiring absence-or-anything.
    return ((not old) or bool(new), "%s -> %s" % (old, new))


def _min_of_type_tightens(old, new):
    if old.get("interfaceType") != new.get("interfaceType"):
        return (False, "constrains a different interface type")
    return (new.get("min", 0) >= old.get("min", 0),
            "min %s -> %s" % (old.get("min"), new.get("min")))


def _subject_tightens(old, new):
    return _prefix_tightens(old.get("startsWith", ""), new.get("startsWith", ""))


def _equal_only(old, new):
    return (old == new, "%r -> %r" % (old, new))


CONSTRAINT_COMPARATORS = {
    "present": _present_tightens,
    "minCount": _num_tightens,
    "minInterfaces": _num_tightens,
    "minProviders": _num_tightens,
    "minInterfacesOfType": _min_of_type_tightens,
    "subjectIdentified": _subject_tightens,
    "enum": _subset_tightens,
    "startsWith": _prefix_tightens,
    "productAttribute": _equal_only,
}
# Removing one of these removes an escape hatch, which is a tightening. Adding
# one where the base had none is a relaxation, and is caught by the general rule.
RELEASABLE_KEYS = ("orDeclaredAbsent", "absenceEnumRef")


def check_constraint_tightens(rid, base_rule, ov, base, derived, notes):
    """Reject an override whose constraint imposes less than the base's.

    Until this existed, only 'level' and 'withholdable' were compared, so a
    derived profile could lower a minimum count or replace an identifier-form
    requirement with a bare presence check and still be accepted. Monotonic
    extension is the guarantee the whole composition model rests on — conformance
    to the derived profile implies conformance to the base — and it was being
    enforced for two fields out of the set that determines a verdict."""
    if "constraint" not in ov:
        return
    old = base_rule.get("constraint") or {}
    new = ov["constraint"] or {}
    if not new:
        raise ProfileError("override on %s supplies an empty constraint, which imposes "
                           "nothing where the base imposed something" % rid)

    for key in old:
        if key in ("enumFull",) or key in RELEASABLE_KEYS:
            continue
        if key not in new:
            raise ProfileError(
                "override on %s drops the base's %r constraint; extension is monotonic, "
                "so an override may add obligations and may not remove one" % (rid, key))
    for key in RELEASABLE_KEYS:
        if key in old and key not in new:
            notes.append("%s: %s removed, so the rule is satisfied by presence alone" % (rid, key))

    for key, value in new.items():
        if key == "enumFull":
            continue
        if key not in old:
            if key in RELEASABLE_KEYS:
                raise ProfileError(
                    "override on %s adds %r, which lets the rule be satisfied without the "
                    "thing the base required; extension is monotonic" % (rid, key))
            notes.append("%s: constraint %r added" % (rid, key))
            continue
        if key == "enumRef":
            # Vocabularies are inherited, so both sides resolve against the
            # profile that declared them rather than against the merged result.
            ok, how = _subset_tightens(base.get(old[key], []),
                                       derived.get(value, base.get(value, [])))
            if not ok:
                raise ProfileError(
                    "override on %s repoints %r from %r to %r, which admits values the base "
                    "does not; extension is monotonic" % (rid, key, old[key], value))
            if how.split(" -> ")[0] != how.split(" -> ")[-1]:
                notes.append("%s: vocabulary narrowed, %s" % (rid, how))
            continue
        comparator = CONSTRAINT_COMPARATORS.get(key)
        if comparator is None:
            raise ProfileError(
                "override on %s changes %r, which cannot be shown to tighten the base; "
                "an override is refused rather than assumed monotonic" % (rid, key))
        ok, how = comparator(old[key], value)
        if not ok:
            raise ProfileError(
                "override on %s relaxes %r (%s); extension is monotonic" % (rid, key, how))
        if old[key] != value:
            notes.append("%s: %s tightened, %s" % (rid, key, how))


# A group's coverage says which keys must have an entry. Widening it obliges a
# producer to answer for more keys, so it is a tightening; narrowing it is how a
# staged profile would quietly become a permanent floor, which is the thing
# decision 0010 exists to prevent.
COVERAGE_STRENGTH = {"in-scope": 0, "all-purposes": 1, "all": 1}


def check_guard_tightens(rid, base_rule, ov, notes):
    """A 'requiredWhen' guard may be removed, and may not be added or changed.

    The guard says when a rule applies. Removing it makes the rule apply always,
    which is strictly more demanding. Adding one where the base had none makes it
    apply less often, which is a relaxation wearing the clothes of a refinement:
    the rule is still listed, still reported, and quietly stops firing. Changing
    an existing guard is refused rather than compared, because whether one
    condition is broader than another depends on values the profile does not
    hold."""
    if "requiredWhen" not in ov:
        return
    old, new = base_rule.get("requiredWhen"), ov["requiredWhen"]
    if new in (None, {}):
        if old:
            notes.append("%s: guard removed, the rule now applies always" % rid)
        return
    if not old:
        raise ProfileError(
            "override on %s adds a 'requiredWhen' guard where the base has none, so the "
            "rule would apply less often than in the base; extension is monotonic" % rid)
    if old != new:
        raise ProfileError(
            "override on %s changes the 'requiredWhen' guard, which cannot be shown to "
            "widen the base's; remove the guard to apply the rule always, or add a new "
            "rule under this profile's own id" % rid)


def check_coverage_tightens(rid, base_group, ov, notes):
    """A group's coverage may be widened, never narrowed."""
    if "coverage" not in ov:
        return
    old, new = base_group.get("coverage"), ov["coverage"]
    if old == new:
        return
    o, n = COVERAGE_STRENGTH.get(old), COVERAGE_STRENGTH.get(new)
    if o is None or n is None:
        raise ProfileError("override on %s sets coverage %r, which is not a known coverage"
                           % (rid, new))
    if n < o:
        raise ProfileError(
            "override on %s narrows coverage from %r to %r, so a producer would owe an "
            "answer for fewer keys; extension is monotonic" % (rid, old, new))
    notes.append("%s: coverage widened, %s -> %s" % (rid, old, new))


def check_override_tightens(base_rule, ov, notes, base=None, derived=None):
    """Reject an override that relaxes an inherited rule."""
    rid = base_rule.get("_qid", base_rule["id"])
    if "attribute" in ov and ov["attribute"] != base_rule.get("attribute"):
        raise ProfileError(
            "override on %s renames the attribute from %r to %r; that is a different rule, "
            "which a derived profile adds under its own id rather than overriding"
            % (rid, base_rule.get("attribute"), ov["attribute"]))
    check_guard_tightens(rid, base_rule, ov, notes)
    check_constraint_tightens(rid, base_rule, ov, base or {}, derived or {}, notes)
    if "level" in ov:
        old, new = base_rule.get("level", "MAY"), ov["level"]
        if LEVEL_ORDER.get(new, 0) < LEVEL_ORDER.get(old, 0):
            raise ProfileError(
                "override on %s relaxes the level from %s to %s; extension is monotonic"
                % (rid, old, new))
        if LEVEL_ORDER.get(new, 0) > LEVEL_ORDER.get(old, 0):
            notes.append("%s: level raised %s -> %s" % (rid, old, new))
    if "withholdable" in ov:
        if ov["withholdable"] and not base_rule.get("withholdable"):
            raise ProfileError(
                "override on %s makes a non-withholdable attribute withholdable; "
                "extension is monotonic" % rid)
        if base_rule.get("withholdable") and not ov["withholdable"]:
            notes.append("%s: withholdability removed" % rid)


def check_range_narrows(base, derived):
    """A derived profile may narrow the carrier acceptance range, never widen it."""
    b = base.get("appliesTo", {}).get("cyclonedx")
    d = derived.get("appliesTo", {}).get("cyclonedx")
    if not b or not d:
        return
    if ver_tuple(d["min"]) < ver_tuple(b["min"]):
        raise ProfileError(
            "derived profile accepts CycloneDX %s, below the base minimum %s"
            % (d["min"], b["min"]))


def check_scope_narrows(base, derived):
    """A derived profile may narrow the accepted lifecycle stages, never widen them.

    Accepting a stage the base rejects would let a document conform to the
    derived profile while failing the base, which is exactly what monotonic
    extension exists to prevent. A different subjectType is rejected for a
    related reason: the inherited rules were written about a different kind of
    subject, so the result is an independent profile rather than an extension."""
    b = base.get("scope") or {}
    d = derived.get("scope") or {}
    if not d:
        return

    b_stages, d_stages = b.get("lifecycleStages"), d.get("lifecycleStages")
    if b_stages and d_stages:
        widened = [s for s in d_stages if s not in b_stages]
        if widened:
            raise ProfileError(
                "derived profile accepts lifecycle stage(s) %s that the base rejects; "
                "extension is monotonic" % ", ".join(sorted(widened)))

    if b.get("subjectType") and d.get("subjectType") \
            and b["subjectType"] != d["subjectType"]:
        raise ProfileError(
            "derived profile describes a %r where the base describes a %r; "
            "a profile with a different subject is an independent profile, "
            "not an extension" % (d["subjectType"], b["subjectType"]))


# --------------------------------------------------------------------------- #
# Carrier format / version handling                                           #
# --------------------------------------------------------------------------- #
def check_format(bom, profile):
    fmt = bom.get("bomFormat")
    spec = bom.get("specVersion")
    applies = profile.get("appliesTo", {})

    if fmt != "CycloneDX" or "cyclonedx" not in applies:
        return {"ok": False, "status": "unsupported-format",
                "detail": "bomFormat=%r not supported by this profile" % fmt}

    rng = applies["cyclonedx"]
    v, vmin, vtested = ver_tuple(spec), ver_tuple(rng["min"]), ver_tuple(rng["tested"])
    if v < vmin:
        return {"ok": False, "status": "unsupported-version",
                "detail": "CycloneDX %s is older than min supported %s -- refuse; "
                          "upgrade the CBOM first" % (spec, rng["min"])}
    if v < vtested:
        return {"ok": True, "status": "legacy",
                "detail": "CycloneDX %s accepted, profile tested against %s (legacy -- warn)"
                          % (spec, rng["tested"])}
    if v > vtested:
        return {"ok": True, "status": "newer",
                "detail": "CycloneDX %s is newer than tested %s -- accepted, review advised"
                          % (spec, rng["tested"])}
    return {"ok": True, "status": "target", "detail": "CycloneDX %s (target)" % spec}


# --------------------------------------------------------------------------- #
# Format adapter: CycloneDX -> abstract attributes                            #
# --------------------------------------------------------------------------- #
def split_properties(component):
    """Return (single, multi, markers) from a component's properties.

    CycloneDX permits a property name to repeat, which is how list-valued
    attributes are carried. 'single' keeps the last value seen; 'multi' keeps
    every value in order."""
    single, multi, markers = {}, {}, {}
    groups, group_markers = {}, {}
    for p in component.get("properties", []):
        name, value = p.get("name", ""), p.get("value")
        if not name.startswith(PROP):
            continue
        rest = name[len(PROP):]

        # A group entry is written <group>:<key>:<attribute>, following the
        # endpointRole:<role> convention already in use. Three segments is what
        # distinguishes it, so the adapter needs no knowledge of which profile
        # declares which groups.
        withheld = rest.startswith("disclosure:")
        if withheld:
            rest = rest[len("disclosure:"):]
        parts = rest.split(":")

        if len(parts) == 3:
            group, key, attr = parts
            target = group_markers if withheld else groups
            target.setdefault(group, {}).setdefault(key, {})[attr] = value
            continue
        if withheld:
            markers[parts[-1]] = value
            continue
        single[rest] = value
        multi.setdefault(rest, []).append(value)
    return single, multi, markers, groups, group_markers


def extract_product(bom):
    comp = bom.get("metadata", {}).get("component", {})
    single, _multi, markers, _groups, _gm = split_properties(comp)
    providers = [c for c in bom.get("components", [])
                 if c.get("type") == "library" and c.get("purl")]
    return {"attrs": single, "_disclosure": markers, "providerCount": len(providers),
            # The subject's own identifier. A CBOM that does not say which version
            # of what it describes cannot be matched to a deployment, compared
            # with last quarter's, or joined to an SBOM.
            "identifier": comp.get("purl"),
            "identifierFallback": "%s@%s" % (comp.get("name"), comp.get("version"))
                                  if comp.get("name") and comp.get("version") else None}


def extract_interfaces(bom):
    comps = {c.get("bom-ref"): c for c in bom.get("components", [])}
    interfaces = []
    for c in bom.get("components", []):
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") != "protocol":
            continue
        single, multi, markers, groups, group_markers = split_properties(c)
        proto = cp.get("protocolProperties", {})
        refs = list(proto.get("cryptoRefArray", []))
        for s in proto.get("cipherSuites", []):
            refs += s.get("algorithms", [])
        roles = [k.split(":")[-1] for k in single if k.startswith("endpointRole:")]

        iface = {
            "_disclosure": markers,
            "_groups": groups,
            "_groupMarkers": group_markers,
            "interfaceId": single.get("interfaceId") or c.get("bom-ref"),
            "interfaceType": single.get("interfaceType"),
            "protocol": (proto.get("type") or "").upper() or None,
            "protocolVersion": proto.get("version"),
            "keyExchange": algo_name(refs, comps, KEX_PRIMS),
            "encryption": algo_name(refs, comps, ENC_PRIMS),
            "authentication": auth(refs, comps),
            "endpointRoles": roles,
            "lifecycleStage": single.get("lifecycleStage"),
            "implementationPurl": single.get("implementationPurl"),
        }
        # Attributes added by derived profiles, carried wholly as properties.
        for key in ("enablementMethod", "minimumProductVersion", "providerLocation",
                    "coexistence", "negotiationControl", "integrationConstraints",
                    "capabilityStatus", "blockedBy", "roadmapRef"):
            iface[key] = single.get(key)
        for key in ("protocolVersionsSupported", "keyExchangeSupported",
                    "authenticationSupported"):
            iface[key] = multi.get(key)
        interfaces.append(iface)
    return interfaces


def algo_name(refs, comps, prims):
    for ref in refs:
        c = comps.get(ref)
        if not c:
            continue
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") != "algorithm":
            continue
        if cp.get("algorithmProperties", {}).get("primitive") in prims:
            return c.get("name")
    return None


def auth(refs, comps):
    for ref in refs:
        c = comps.get(ref)
        if not c:
            continue
        if c.get("cryptoProperties", {}).get("assetType") == "certificate":
            sig = c["cryptoProperties"]["certificateProperties"].get("signatureAlgorithmRef")
            if sig and sig in comps:
                return comps[sig].get("name")
    return algo_name(refs, comps, SIG_PRIMS)


# --------------------------------------------------------------------------- #
# Constraint checks                                                           #
# --------------------------------------------------------------------------- #
def present(v):
    return v not in (None, "", [], {})


def check_attr(value, constraint, profile):
    if "present" in constraint:
        p = present(value)
        return (p == constraint["present"], "present" if p else "absent")
    if "minCount" in constraint:
        n = len(value or [])
        return (n >= constraint["minCount"], "count=%d (min %d)" % (n, constraint["minCount"]))
    if not present(value):
        return (False, "absent")
    if "enum" in constraint:
        if value in constraint["enum"]:
            return (True, "= %r" % (value,))
        # A value the methodology defines but this profile's scope excludes is a
        # different failure from a value that means nothing, and a producer
        # reading the report needs to be able to tell them apart.
        if value in constraint.get("enumFull", []):
            return (False, "= %r, outside the stages this profile accepts (%s)"
                    % (value, ", ".join(constraint["enum"])))
        return (False, "= %r" % (value,))
    if "enumRef" in constraint:
        return (value in profile.get(constraint["enumRef"], []), "= %r" % (value,))
    if "startsWith" in constraint:
        return (str(value).startswith(constraint["startsWith"]), "= %r" % (value,))
    # Unreachable: check_evaluable refuses a profile whose constraint the
    # evaluator does not implement. Kept loud rather than returning a pass,
    # because this returning True is what made a typo'd key look satisfied.
    raise ProfileError("no evaluable constraint in %r" % (constraint,))


def condition_holds(rule, iface):
    """Evaluate a 'requiredWhen' guard. Absent guard means always applicable."""
    cond = rule.get("requiredWhen")
    if not cond:
        return True, None
    actual = iface.get(cond["attribute"])
    if "equals" in cond:
        return actual == cond["equals"], "%s=%r" % (cond["attribute"], actual)
    if "notEquals" in cond:
        return actual != cond["notEquals"], "%s=%r" % (cond["attribute"], actual)
    return True, None


def check_rule(iface, rule, profile):
    """Evaluate one interface rule. Returns (ok, state, detail)."""
    applies, why = condition_holds(rule, iface)
    if not applies:
        return (True, "n/a", "not applicable (%s)" % why)

    attr = rule["attribute"]
    value = iface.get(attr)
    if present(value):
        ok, detail = check_attr(value, rule["constraint"], profile)
        if rule.get("list"):
            detail = "%s %s" % (detail, list(value)[:3])
        return (ok, "value", detail)

    marker = iface.get("_disclosure", {}).get(attr)
    if marker == "withheld":
        if rule.get("withholdable"):
            return (True, "withheld", "withheld by producer (permitted)")
        return (False, "withheld", "withheld by producer (not permitted here)")
    if marker == "unknown":
        return (False, "unknown", "declared unknown to producer")
    return (False, "undeclared", "absent, with no disclosure marker")


def required_keys(rule, profile):
    """The keys a group rule requires an entry for.

    'all-purposes' means every value in the referenced vocabulary, not only the
    ones the profile takes in scope. That is deliberate and is what stops a
    staged profile becoming a permanent floor: a profile may require depth for
    key establishment alone and still oblige a producer to say where
    authentication stands. 'in-scope' restricts the requirement to the scope
    member of the same name."""
    vocab = profile.get(rule.get("keyVocabularyRef"), [])
    if rule.get("coverage") == "in-scope":
        scope_key = rule.get("scopeRef") or "cryptographicPurposes"
        declared = (profile.get("scope") or {}).get(scope_key) or []
        return [k for k in vocab if k in declared]
    return list(vocab)


def in_scope_keys(rule, profile):
    scope_key = rule.get("scopeRef") or "cryptographicPurposes"
    return set((profile.get("scope") or {}).get(scope_key) or [])


def check_group_rule(iface, rule, profile):
    """Evaluate a repeated group keyed by a controlled vocabulary.

    Returns a list of report rows. A missing entry is reported against the group
    rule and named by its key, because "no status for entity-authentication" is
    what a reader needs, not "G1 failed". Member rules are evaluated inside the
    entry, so a 'requiredWhen' guard refers to the entry's own attributes rather
    than to the interface: the blocker for one purpose depends on the status of
    that purpose and on nothing else. That was the defect in the per-interface
    shape, where the guard had no single value to test."""
    rows = []
    group = rule["group"]
    entries = (iface.get("_groups") or {}).get(group, {})
    entry_markers = (iface.get("_groupMarkers") or {}).get(group, {})
    scoped = in_scope_keys(rule, profile)

    for key in required_keys(rule, profile):
        depth = "in scope" if (not scoped or key in scoped) else "status only"
        values = entries.get(key)
        if not values:
            rows.append({"id": rule["_qid"], "level": rule["level"],
                         "attribute": "%s[%s]" % (rule["keyedBy"], key),
                         "ok": False, "state": "undeclared",
                         "detail": "no entry for this %s (%s)" % (rule["keyedBy"], depth)})
            continue

        entry = dict(values)
        entry["_disclosure"] = entry_markers.get(key, {})
        for member in rule.get("members", []):
            # Outside the profile's declared scope a purpose owes a status and,
            # where the status is not already available, a blocker. The optional
            # members are the depth that scope buys.
            if scoped and key not in scoped and member.get("level") == "MAY":
                continue
            ok, state, detail = check_rule(entry, member, profile)
            rows.append({"id": "%s[%s]" % (member["_qid"], key), "level": member["level"],
                         "attribute": member["attribute"], "ok": ok,
                         "state": state, "detail": detail})
    return rows


KIND_ORDER = {"P": 0, "I": 1, "G": 2}


def rule_sort_key(row, chain=()):
    """Order rows for reading: base profile first, then by kind and number.

    Ids are qualified now, so a plain alphabetic sort would interleave two
    profiles' rules by tag rather than by where they came from. A reader works
    outward from the base, so the chain position leads, then the kind letter,
    then the number. Member ids like 'pqc-migration#G1.2[key-establishment]'
    sort under their group."""
    ident = str(row.get("id", ""))
    tag, _, local = ident.rpartition("#")
    try:
        depth = list(chain).index(tag)
    except ValueError:
        depth = len(chain)
    kind = KIND_ORDER.get(local[:1], len(KIND_ORDER))
    digits = local[1:].split("[")[0]
    parts = [int(p) for p in digits.split(".") if p.isdigit()]
    return (depth, kind, parts or [0], ident)


def check_product(product, interfaces, constraint, profile):
    if "minInterfaces" in constraint:
        n = len(interfaces)
        return (n >= constraint["minInterfaces"], "%d interface(s) declared" % n)
    if "subjectIdentified" in constraint:
        spec = constraint["subjectIdentified"]
        value = product.get("identifier")
        if present(value):
            prefix = spec.get("startsWith")
            if prefix and not str(value).startswith(prefix):
                return (False, "subject identified as %r, which is not a %s identifier"
                        % (value, prefix))
            return (True, "= %r" % (value,))
        if product.get("identifierFallback"):
            return (False, "subject named as %r but carries no identifier in the "
                    "required form; a name and a version are not a stable identifier"
                    % product["identifierFallback"])
        return (False, "the document does not say what it describes")

    if "minInterfacesOfType" in constraint:
        spec = constraint["minInterfacesOfType"]
        n = sum(1 for i in interfaces if i.get("interfaceType") == spec["interfaceType"])
        if n >= spec["min"]:
            return (True, "%d of type '%s' (min %d)"
                    % (n, spec["interfaceType"], spec["min"]))

        # A structural rule is satisfied by presence or by an explicit statement
        # of absence; silence is neither. A product with no administrative
        # surface at all — a library, a token, an embedded component — hides
        # nothing by having no management interface, and should be able to say
        # so rather than fail. This is the disclosure model applied to structure.
        absent = constraint.get("orDeclaredAbsent")
        if absent:
            reason = product.get("attrs", {}).get(absent)
            if present(reason):
                vocab = profile.get(constraint.get("absenceEnumRef"), [])
                if vocab and reason not in vocab:
                    return (False, "declared absent as %r, which is not a permitted reason"
                            % (reason,))
                return (True, "none declared, stated as %r" % (reason,))
            marker = product.get("_disclosure", {}).get(absent)
            if marker:
                return (False, "no interface of type '%s', and its absence is declared %s "
                        "rather than explained" % (spec["interfaceType"], marker))
            return (False, "%d of type '%s' (min %d), and no declared reason for the "
                    "absence" % (n, spec["interfaceType"], spec["min"]))
        return (False, "%d of type '%s' (min %d)" % (n, spec["interfaceType"], spec["min"]))
    if "minProviders" in constraint:
        n = product.get("providerCount", 0)
        return (n >= constraint["minProviders"],
                "%d provider component(s) with a purl" % n)
    if "productAttribute" in constraint:
        value = product.get("attrs", {}).get(constraint["productAttribute"])
        if not present(value):
            marker = product.get("_disclosure", {}).get(constraint["productAttribute"])
            if marker:
                return (False, "declared %s" % marker)
            return (False, "%s absent" % constraint["productAttribute"])
        if "enumRef" in constraint:
            return (value in profile.get(constraint["enumRef"], []), "= %r" % (value,))
        return (True, "= %r" % (value,))
    raise ProfileError("no evaluable constraint in %r" % (constraint,))


# --------------------------------------------------------------------------- #
def validate(bom, profile):
    """Evaluate a CBOM against a profile.

    Returns (verdict, report) where verdict is one of the three the Conformance
    section defines: 'conforms', 'does-not-conform', or 'refused'.

    Refusal is not a failure and the two must not be merged. A refused document
    may be entirely adequate; the profile is simply unable to express its rules
    against that carrier version, so no assessment is performed and the report
    carries no rule results to summarise. Returning a bare boolean here is what
    collapsed the two, because there is no false that means 'not assessed'."""
    fmt = check_format(bom, profile)
    report = {"format": fmt, "product": [], "interfaces": []}
    if not fmt["ok"]:
        return "refused", report

    product = extract_product(bom)
    interfaces = extract_interfaces(bom)

    chain = profile.get("_chain", [])

    for rule in profile.get("productRules", []):
        ok, detail = check_product(product, interfaces, rule["constraint"], profile)
        row = dict(rule, id=rule.get("_qid", rule["id"]), ok=ok, detail=detail)
        row.pop("_qid", None)
        report["product"].append(row)

    for iface in interfaces:
        rows = []
        for rule in profile.get("interfaceRules", []):
            ok, state, detail = check_rule(iface, rule, profile)
            rows.append({"id": rule["_qid"], "level": rule["level"],
                         "attribute": rule["attribute"], "ok": ok,
                         "state": state, "detail": detail})
        for grule in profile.get("groupRules", []):
            rows.extend(check_group_rule(iface, grule, profile))
        rows.sort(key=lambda r: rule_sort_key(r, chain))
        iface_ok = all(r["ok"] for r in rows if r["level"] == "MUST")
        report["interfaces"].append({
            "interfaceId": iface["interfaceId"],
            "interfaceType": iface.get("interfaceType"),
            "conforms": iface_ok, "rows": rows,
        })

    product_ok = all(r["ok"] for r in report["product"] if r["level"] == "MUST")
    ifaces_ok = all(i["conforms"] for i in report["interfaces"])
    return ("conforms" if product_ok and ifaces_ok else "does-not-conform"), report


CLAIM_FORMAT = "pkic.cbom.conformance-claim"
CLAIM_FORMAT_VERSION = "0.1"

# What a verdict does not assert. The Conformance section carries this list, and
# a consumer reading a claim months later will not have read the Conformance
# section. Restating it inside the claim is the difference between a consumer
# who knows what they are holding and one who infers more from the word
# "conforms" than the word can carry.
NOT_ASSERTED = [
    "that the disclosed values are true; a profile constrains what is stated, not whether it is so",
    "that the document is complete, beyond whatever completeness rule the profile carries",
    "that every relevant interface was declared",
    "that the cryptography is adequate, now or later; that judgement belongs to versioned policy",
    "anything about a withheld value beyond the fact that withholding was permitted here",
]


# Q48. Which kinds of rule a carrier can carry enough structure to evaluate.
# CycloneDX gives one component per interface, so all three kinds are evaluable.
# In the current SPDX arrangement an SPDX document satisfies a profile by
# referencing a CycloneDX CBOM as an external artifact, which gives the SPDX side
# one element for the whole product: the attribute rules are evaluable through
# the reference and the product-level rules are not, because there is nothing on
# the SPDX side to count. A claim says so rather than leaving a consumer to
# assume a verdict covers more than it does. See decision 0016.
CARRIER_CAPABILITY = {
    "cyclonedx": {"productRules": True, "interfaceRules": True, "groupRules": True},
    "spdx": {"productRules": False, "interfaceRules": True, "groupRules": True},
}


def carrier_capability(carrier_format):
    return CARRIER_CAPABILITY.get(str(carrier_format).lower(),
                                  {"productRules": False, "interfaceRules": False,
                                   "groupRules": False})


def digest_of(path):
    with open(path, "rb") as fh:
        return {"alg": "sha-256", "value": hashlib.sha256(fh.read()).hexdigest()}


def chain_of(profile):
    """The whole inheritance chain, each link with the version that was pinned.

    A claim naming only the profile evaluated is not reproducible: the derived
    profile pins a base version, and a reader has to be able to resolve exactly
    what was applied without going and looking it up."""
    links = []
    prof = profile
    ext = prof.get("extends")
    if ext:
        links.append({"profileId": ext.get("profileId"), "version": str(ext.get("version"))})
    links.append({"profileId": prof.get("profileId"), "version": str(prof.get("version")),
                  "profileTag": profile_tag(prof)})
    return links


def rule_states(report):
    """Summarise what was assessed, by disclosure state rather than by count alone.

    'Conforms' with the implementing library withheld and 'conforms' with it
    supplied are materially different answers to the question a consumer asked.
    A claim that reports only the verdict throws that away, so the states travel
    with it."""
    buckets = {"failed": [], "withheld": [], "unknown": [], "undeclared": []}
    total = 0
    for row in report.get("product", []):
        total += 1
        if not row.get("ok") and row.get("level") == "MUST":
            buckets["failed"].append(row["id"])
    for iface in report.get("interfaces", []):
        for row in iface.get("rows", []):
            total += 1
            ref = "%s/%s" % (iface["interfaceId"], row["id"])
            if not row.get("ok") and row.get("level") == "MUST":
                buckets["failed"].append(ref)
            state = row.get("state")
            if state in ("withheld", "unknown", "undeclared"):
                buckets[state].append(ref)
    return dict(buckets, assessed=total)


def build_claim(bom_path, bom, evaluations, issued=None):
    """Assemble a claim over one document and one or more profiles.

    Several profiles in one claim is the case Q24 asked about. They are listed
    rather than combined: each carries its own verdict, because a document can
    conform to one profile and not another and a single overall answer would
    have to choose which question it was answering."""
    product = extract_product(bom)
    capability = carrier_capability("cyclonedx")
    not_asserted = list(NOT_ASSERTED)
    for kind, evaluable in sorted(capability.items()):
        if not evaluable:
            not_asserted.append(
                "anything a %s constrains; this carrier does not carry the structure to "
                "evaluate them, so they were not assessed" % kind)
    entries = []
    for profile, verdict, report in evaluations:
        entry = {
            "profileId": profile.get("profileId"),
            "profileTag": profile_tag(profile),
            "version": str(profile.get("version")),
            "chain": chain_of(profile),
            "assessed": verdict != "refused",
            "verdict": verdict,
            "carrierBand": report["format"]["status"],
        }
        # A refused evaluation carries no rule results to summarise, and saying
        # "0 failed" about a document nobody assessed is the merge of refusal
        # and failure the Conformance section forbids.
        if verdict != "refused":
            entry["rules"] = rule_states(report)
        else:
            entry["refusedBecause"] = report["format"]["detail"]
        entries.append(entry)

    return {
        "claimFormat": CLAIM_FORMAT,
        "claimFormatVersion": CLAIM_FORMAT_VERSION,
        "issued": issued or datetime.datetime.now(datetime.timezone.utc)
                              .replace(microsecond=0).isoformat(),
        "subject": {"identifier": product.get("identifier"),
                    "identifierFallback": product.get("identifierFallback")},
        "document": {
            "file": os.path.basename(bom_path),
            "digest": digest_of(bom_path),
            "carrier": {"format": "cyclonedx", "version": str(bom.get("specVersion"))},
        },
        "profiles": entries,
        "evaluableFromCarrier": capability,
        "assertedBy": {"tool": "validate_cbom.py", "claimFormat": CLAIM_FORMAT},
        "notAsserted": not_asserted,
    }


def verify_claim(claim, bom_path, bom, search_dirs):
    """Re-run everything the claim asserts and report where it disagrees.

    This is what separates a claim from an assertion. A consumer holding a claim
    and the document it names can establish, without trusting the issuer, that
    the document is the one evaluated and that the profiles still produce the
    verdicts recorded. What it cannot establish is that the disclosed values are
    true, which is in 'notAsserted' and always will be."""
    problems = []
    if claim.get("claimFormat") != CLAIM_FORMAT:
        problems.append("not a %s document" % CLAIM_FORMAT)
        return problems

    want = (claim.get("document") or {}).get("digest") or {}
    got = digest_of(bom_path)
    if want.get("value") != got["value"]:
        problems.append(
            "digest mismatch: the claim is about a document with %s %s..., this document is %s..."
            % (want.get("alg"), str(want.get("value"))[:16], got["value"][:16]))
        # Everything below would compare a claim against a document it was never
        # about, so the mismatch is reported alone rather than with its symptoms.
        return problems

    carrier = ((claim.get("document") or {}).get("carrier") or {}).get("version")
    if carrier and str(carrier) != str(bom.get("specVersion")):
        problems.append("carrier version mismatch: claim says %s, document says %s"
                        % (carrier, bom.get("specVersion")))

    for entry in claim.get("profiles", []):
        pid, tag = entry.get("profileId"), entry.get("profileTag")
        path = find_profile(search_dirs, pid, tag)
        if not path:
            problems.append(
                "%s: no rules file declaring %s was found in %s, so the claim could not be "
                "re-checked. This is a gap in the verifier's inputs rather than a defect in "
                "the claim; point it at the profile with --profiles-dir."
                % (tag or pid, pid, ", ".join(search_dirs)))
            continue
        try:
            profile, _origin, _notes = load_profile(path)
        except ProfileError as err:
            problems.append("%s: profile no longer loads (%s)" % (tag or pid, err))
            continue
        if str(profile.get("version")) != str(entry.get("version")):
            problems.append("%s: claim cites v%s, the file here is v%s"
                            % (tag or pid, entry.get("version"), profile.get("version")))
            continue
        try:
            verdict, _report = validate(bom, profile)
        except ProfileError as err:
            problems.append("%s: could not re-evaluate (%s)" % (tag or pid, err))
            continue
        if verdict != entry.get("verdict"):
            problems.append("%s: claim says %r, re-evaluation says %r"
                            % (tag or pid, entry.get("verdict"), verdict))
    return problems


def find_profile(search_dirs, profile_id, tag):
    """Locate the rules file declaring a profileId.

    Found by reading candidates and comparing the declared profileId, rather than
    by guessing at a filename convention the methodology does not impose. A claim
    cites a profile by identity; where the file sits is the verifier's problem,
    not the claim's."""
    for base_dir in search_dirs:
        if not os.path.isdir(base_dir):
            continue
        for name in sorted(os.listdir(base_dir)):
            if not name.endswith(".rules.json"):
                continue
            path = os.path.join(base_dir, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    candidate = json.load(fh)
            except (OSError, ValueError):
                continue
            if candidate.get("profileId") == profile_id:
                return path
    return None


def icon_for(row):
    if row["ok"]:
        return {"withheld": "HELD", "n/a": " -- "}.get(row.get("state"), "PASS")
    if row["level"] == "MUST":
        return "UNKN" if row.get("state") == "unknown" else "FAIL"
    return "warn"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    as_json = "--json" in argv
    as_claim = "--claim" in argv
    verifying = "--verify-claim" in argv

    bom = json.load(open(args[0], encoding="utf-8"))

    # --- verify a claim against this document -------------------------------
    if verifying:
        claim_path = args[1]
        with open(claim_path, encoding="utf-8") as fh:
            claim = json.load(fh)
        # A claim names profiles by identity, so the verifier has to be told
        # where to look. The document's own directory first, because a producer
        # who ships a CBOM and a claim together usually ships the profile too.
        dirs = [os.path.dirname(os.path.abspath(args[0])) or ".",
                os.path.dirname(os.path.abspath(claim_path)) or ".", os.getcwd()]
        for i, a in enumerate(argv):
            if a == "--profiles-dir" and i + 1 < len(argv):
                dirs.insert(0, argv[i + 1])
            elif a.startswith("--profiles-dir="):
                dirs.insert(0, a.split("=", 1)[1])
        seen, search_dirs = set(), []
        for d in dirs:
            if d not in seen:
                seen.add(d)
                search_dirs.append(d)
        problems = verify_claim(claim, args[0], bom, search_dirs)
        if as_json:
            print(json.dumps({"verified": not problems, "problems": problems}, indent=2))
        else:
            print("CLAIM   : %s" % claim_path)
            print("CBOM    : %s" % args[0])
            print("=" * 70)
            if problems:
                print("MISMATCH")
                for pr in problems:
                    print("  - %s" % pr)
                print("=" * 70)
                print("The claim does not describe this document, or no longer holds against")
                print("the profiles it names. That is a finding about the claim, not a verdict")
                print("on the document: evaluate the document directly to get one.")
            else:
                n = len(claim.get("profiles", []))
                print("VERIFIED  the document matches the claim's digest, and re-evaluating")
                print("          %d profile(s) reproduces every verdict the claim records." % n)
                print("          What is still not asserted is listed in the claim itself.")
        return EXIT_CLAIM_MISMATCH if problems else 0

    # --- evaluate against one or more profiles ------------------------------
    profile_paths = args[1:] if as_claim else args[1:2]
    evaluations = []
    for path in profile_paths:
        try:
            prof, orig, nts = load_profile(path)
            vd, rp = validate(bom, prof)
        except ProfileError as err:
            print("PROFILE ERROR: %s" % err, file=sys.stderr)
            return 3
        evaluations.append((prof, vd, rp))

    if as_claim:
        claim = build_claim(args[0], bom, evaluations)
        print(json.dumps(claim, indent=2))
        # A document that fails one profile and is refused by another has failed:
        # refusal says nothing happened, and something did.
        verdicts = [v for _p, v, _r in evaluations]
        if "does-not-conform" in verdicts:
            return EXIT_FOR["does-not-conform"]
        if "refused" in verdicts:
            return EXIT_FOR["refused"]
        return EXIT_FOR["conforms"]

    profile, origin, notes = evaluations[0][0], None, None
    try:
        profile, origin, notes = load_profile(args[1])
    except ProfileError as err:
        print("PROFILE ERROR: %s" % err, file=sys.stderr)
        return 3
    verdict, report = evaluations[0][1], evaluations[0][2]

    if as_json:
        print(json.dumps({"verdict": verdict,
                          "conforms": verdict == "conforms",
                          "assessed": verdict != "refused",
                          "profile": profile.get("profileId"),
                          "profileTag": profile_tag(profile),
                          "chain": profile.get("_chain", []),
                          "report": report, "origin": origin}, indent=2))
        return EXIT_FOR[verdict]

    print("Profile : %s v%s  (tag: %s)"
          % (profile["title"], profile["version"], profile_tag(profile)))
    if profile.get("extends"):
        e = profile["extends"]
        print("          extends %s v%s" % (e["profileId"], e["version"]))
        print("          chain   %s" % " -> ".join(profile.get("_chain", [])))
        for n in notes:
            print("          override %s" % n)
    print("CBOM    : %s" % args[0])
    print("=" * 70)
    f = report["format"]
    warn = f["status"] in ("legacy", "newer")
    gate = "warn" if warn else ("PASS" if f["ok"] else "STOP")
    print("FORMAT  [%s] %s" % (gate, f["detail"]))
    if verdict == "refused":
        print("=" * 70)
        print("VERDICT : REFUSED  (%s)" % f["detail"])
        print("          No assessment was performed, so this is not a failure. "
              "The document may")
        print("          be adequate; the profile cannot express its rules "
              "against this carrier")
        print("          version. Upgrade the CBOM and evaluate again.")
        return EXIT_FOR[verdict]

    print("=" * 70)
    print("PRODUCT-LEVEL RULES")
    pidw = max([len(r["id"]) for r in report["product"]] + [4])
    for r in report["product"]:
        print("  [%s] %-*s %-6s %s" % ("PASS" if r["ok"] else "FAIL",
                                       pidw, r["id"], r["level"], r["description"]))
        print("         -> %s   [%s]" % (r["detail"], origin.get(r["id"], "?")))
    for iface in report["interfaces"]:
        print("-" * 70)
        print("INTERFACE  %s  (type=%s)  ==>  %s"
              % (iface["interfaceId"], iface["interfaceType"],
                 "conforms" if iface["conforms"] else "FAILS"))
        # Ids are qualified and group member ids carry their key, so the column
        # is sized per interface rather than fixed:
        # 'pqc-migration#G1.2[entity-authentication]' should not push every other
        # row out of alignment.
        idw = max([len(r["id"]) for r in iface["rows"]] + [4])
        attrw = max([len(r["attribute"]) for r in iface["rows"]] + [18])
        for r in iface["rows"]:
            print("  [%s] %-*s %-6s %-*s %s" % (icon_for(r), idw, r["id"], r["level"],
                                                attrw, r["attribute"], r["detail"]))
    print("=" * 70)
    fails = [r["id"] for r in report["product"] if not r["ok"] and r["level"] == "MUST"]
    for i in report["interfaces"]:
        for r in i["rows"]:
            if not r["ok"] and r["level"] == "MUST":
                fails.append("%s/%s" % (i["interfaceId"], r["id"]))
    tail = ("  (failed MUST: %s)" % ", ".join(fails)) if fails else ""
    print("VERDICT : %s%s  [carrier: %s]"
          % (VERDICT_LABEL[verdict], tail, report["format"]["status"]))
    return EXIT_FOR[verdict]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
