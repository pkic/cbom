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
                       refers to that entry. 'keyCoverage' says whether an
                       entry is required for every key in the vocabulary or only
                       for those the profile's scope declares.

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

Carriers: CycloneDX 2.0 is the target (pinned 2.0-dev schema); CycloneDX 1.6 and
1.7 are read as legacy. A deployment record cites the documents it builds on;
'--with' supplies them, so citations are checked by hash and implementation facts
are followed along correspondsTo. Without them, inherited facts are reported as
unresolved rather than failed.

Usage:
    python validate_cbom.py <cbom.json> <profile.rules.json> [--with <cited.json>]... [--json]
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
SUBJECT_TYPES = ("product", "deployment", "service", "component", "system", "estate-subset")
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
                         "startsWith", "literals", "literalStages", "refersToCited")
PRODUCT_CONSTRAINTS = ("minInterfaces", "minInterfacesOfType", "minProviders",
                       "subjectIdentified", "productAttribute", "enumRef",
                       "orDeclaredAbsent", "absenceEnumRef", "absenceConditions",
                       "orCitedDeclares", "subjectDeclared", "singleStage", "citesDocuments")
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

    for rule in profile.get("referenceRules", []):
        label = rule.get("_qid", rule.get("id", "?"))
        if rule.get("context") not in (profile.get("contextKinds") or {}):
            problems.append("%s names the context kind %r, which the profile does not define"
                            % (label, rule.get("context")))
        if rule.get("at") not in ("document", "interface"):
            problems.append("%s sits at %r; a reference rule sits on the document or on an "
                            "interface" % (label, rule.get("at")))
        ref = rule.get("orDeclaredAbsent")
        if ref and not profile.get(ref):
            problems.append("%s references the vocabulary %r, which the profile does not declare"
                            % (label, ref))

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
    for section in ("productRules", "interfaceRules", "referenceRules"):
        for rule in profile.get(section, []):
            rule["_qid"] = "%s#%s" % (tag, rule["id"])
    for group in profile.get("groupRules", []):
        group["_qid"] = "%s#%s" % (tag, group["id"])
        for member in group.get("members", []):
            member["_qid"] = "%s#%s" % (tag, member["id"])


def all_qids(profile):
    out = [r["_qid"] for r in profile.get("productRules", [])
           + profile.get("interfaceRules", []) + profile.get("referenceRules", [])]
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
                                "referenceRules", "overrides", "extends", "contextKinds")})
    # Context kinds accumulate along the chain. A derived profile may add a kind
    # and may not redefine one it inherited, because the reference rules of the
    # base were written against the inherited definition.
    kinds = dict(base.get("contextKinds") or {})
    for name, definition in (prof.get("contextKinds") or {}).items():
        if name in kinds and kinds[name] != definition:
            raise ProfileError("context kind %r is redefined by %s; a derived profile may add "
                               "kinds and may not change one it inherited" % (name, tag))
        kinds[name] = definition
    if kinds:
        merged["contextKinds"] = kinds
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

    for section in ("productRules", "interfaceRules", "referenceRules"):
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
    # inherited, or widen that group's keyCoverage. Settling Q49: without member
    # overrides the only ways to ask for more depth were to restate the group,
    # which silently replaces the base's keyCoverage, or to add a parallel group,
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
            check_key_coverage_tightens(oid, group_by_qid[oid], ov, notes)
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


def _literal_stages_tighten(old, new):
    for lit, stages in (new or {}).items():
        if lit not in (old or {}):
            return (False, "restricts %r, which the base accepts at every stage" % lit)
        if not set(stages) <= set(old[lit]):
            return (False, "accepts %r at more stages than the base" % lit)
    return (True, "%s -> %s" % (old, new))


def _subject_form_tightens(old, new):
    o, n = old.get("startsWith"), new.get("startsWith")
    if isinstance(o, dict) or isinstance(n, dict):
        if not (isinstance(o, dict) and isinstance(n, dict)):
            return (False, "changes between one identifier form and one per subject type")
        ok = all(k in o and str(v).startswith(str(o[k])) for k, v in n.items())
        return (ok, "%s -> %s" % (o, n))
    return _prefix_tightens(o or "", n or "")


CONSTRAINT_COMPARATORS = {
    "present": _present_tightens,
    "minCount": _num_tightens,
    "minInterfaces": _num_tightens,
    "minProviders": _num_tightens,
    "minInterfacesOfType": _min_of_type_tightens,
    "subjectIdentified": _subject_form_tightens,
    "literals": _subset_tightens,
    "literalStages": _literal_stages_tighten,
    "absenceConditions": _equal_only,
    "subjectDeclared": _equal_only,
    "singleStage": _equal_only,
    "citesDocuments": _equal_only,
    "refersToCited": _equal_only,
    "enum": _subset_tightens,
    "startsWith": _prefix_tightens,
    "productAttribute": _equal_only,
}
# Removing one of these removes an escape hatch, which is a tightening. Adding
# one where the base had none is a relaxation, and is caught by the general rule.
RELEASABLE_KEYS = ("orDeclaredAbsent", "absenceEnumRef", "orCitedDeclares")


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


# A group's keyCoverage says which keys of its vocabulary must have an entry.
# Widening it obliges a producer to answer for more keys, so it is a tightening;
# narrowing it is how a staged profile would quietly become a permanent floor,
# which is the thing decision 0010 exists to prevent.
#
# Named keyCoverage rather than coverage because a document already carries a
# product attribute called 'coverage', saying how complete its interface list
# is. Two unrelated things in one rules file under one word is how a reader ends
# up checking the wrong one. See decision 0021.
KEY_COVERAGE_STRENGTH = {"in-scope": 0, "all-purposes": 1}


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


def check_key_coverage_tightens(rid, base_group, ov, notes):
    """A group's keyCoverage may be widened, never narrowed."""
    if "keyCoverage" not in ov:
        return
    old, new = base_group.get("keyCoverage"), ov["keyCoverage"]
    if old == new:
        return
    o, n = KEY_COVERAGE_STRENGTH.get(old), KEY_COVERAGE_STRENGTH.get(new)
    if o is None or n is None:
        raise ProfileError("override on %s sets keyCoverage %r, which is not a known value"
                           % (rid, new))
    if n < o:
        raise ProfileError(
            "override on %s narrows keyCoverage from %r to %r, so a producer would owe "
            "an answer for fewer keys; extension is monotonic" % (rid, old, new))
    notes.append("%s: keyCoverage widened, %s -> %s" % (rid, old, new))


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

    bs, ds = subject_types(base), subject_types(derived)
    if bs and ds and not set(ds) <= set(bs):
        raise ProfileError(
            "derived profile describes %s where the base describes %s; a profile with a "
            "different subject is an independent profile, not an extension"
            % (", ".join(sorted(set(ds) - set(bs))), ", ".join(bs)))


def subject_types(profile):
    """The subject types a profile's scope accepts, as a list.

    'subjectTypes' is a set, narrowed by a derived profile like lifecycleStages.
    The older single 'subjectType' is read as a set of one."""
    scope = profile.get("scope") or {}
    value = scope.get("subjectTypes") or scope.get("subjectType")
    if value is None:
        return []
    return list(value) if isinstance(value, (list, tuple)) else [value]


# --------------------------------------------------------------------------- #
# Carrier format / version handling                                           #
# --------------------------------------------------------------------------- #
def check_format(bom, profile):
    fmt = bom.get("bomFormat") or bom.get("specFormat")
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
# Two carrier generations are read. CycloneDX 2.0 is the target: the subject is
# inventories[0].subject, services are components of type 'service', package
# URLs are identifiers asserted by a party, in-use algorithms are
# relatedCryptographicAssets, and module validation is certifications[].
# CycloneDX 1.6 and 1.7 are read as legacy: the subject is metadata.component,
# services are a separate list, and the same facts sit in purl, cryptoRefArray,
# algorithmRef and a certification-report reference. Both produce the same
# abstract record, so every rule is written once.
PHASE_TO_STAGE = {"design": "intended", "pre-build": "implemented", "build": "implemented",
                  "post-build": "implemented", "operations": "configured",
                  "discovery": "observed"}

# Attributes that describe the implementation rather than the boundary. An
# interface inherits them from the library that provides it (decision 0022, K9).
INHERITABLE = ("moduleValidationScheme", "moduleValidationRef", "providerLocation",
               "enablementMethod", "minimumProductVersion", "coexistence")
# The only facts that follow a correspondsTo join from one document to another.
# Present-state facts never do: each stage reports its own.
INHERITED_ACROSS_DOCUMENTS = ("implementationPurl",)

VALIDATION_STANDARDS = {"fips 140-3": "fips-140-3", "fips 140-2": "fips-140-2",
                        "iso/iec 19790": "iso-19790", "cavp": "cavp"}
# CycloneDX 2.0 certifications[].standard is free text; these names are read
# as the values of the extended depth's productCertificationVocabulary.
PRODUCT_CERTIFICATIONS = {"common criteria": "common-criteria",
                          "common criteria (iso/iec 15408)": "common-criteria",
                          "iso/iec 15408": "common-criteria", "eucc": "eucc"}
EXECUTION_TO_LOCATION = {"software-plain-ram": "software", "software-encrypted-ram": "software",
                         "software-tee": "tee", "hardware": "hsm"}


def split_properties(component):
    """Return (single, multi, markers, groups, group_markers) from a component's properties.

    CycloneDX permits a property name to repeat, which is how list-valued
    attributes are carried. 'single' keeps the last value seen; 'multi' keeps
    every value in order."""
    single, multi, markers = {}, {}, {}
    groups, group_markers = {}, {}
    for p in component.get("properties", []) or []:
        name, value = p.get("name", ""), p.get("value")
        if not name.startswith(PROP):
            continue
        rest = name[len(PROP):]
        # A group entry is written <group>:<key>:<attribute>, following the
        # endpointRole:<role> convention. Three segments is what distinguishes it.
        withheld = rest.startswith("disclosure:")
        if withheld:
            rest = rest[len("disclosure:"):]
        parts = rest.split(":")
        if len(parts) == 3 and parts[0] != "context":
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


def is_v2(bom):
    return str(bom.get("specVersion", "")).startswith("2.")


def _flatten(items):
    out = []
    for c in items or []:
        if not isinstance(c, dict) or "ref" in c and len(c) <= 2:
            continue
        out.append(c)
        out += _flatten(c.get("components"))
    return out


def document_parts(bom):
    """(subject, entries, inventory count) for either carrier generation."""
    if is_v2(bom):
        inventories = bom.get("inventories") or []
        first = inventories[0] if inventories else {}
        return first.get("subject") or {}, _flatten(first.get("components")), len(inventories)
    entries = _flatten(bom.get("components"))
    services = []
    for s in _flatten(bom.get("services")):
        s = dict(s)
        s["type"] = "service"
        services.append(s)
    return bom.get("metadata", {}).get("component", {}), entries + services, 1


def identities(el):
    """Every (scheme, value) the element is identified by."""
    out = []
    if el.get("purl"):
        out.append(("purl", el["purl"]))
    for ident in el.get("identifiers", []) or []:
        for i in ident.get("identities", []) or []:
            scheme = i.get("scheme")
            name = scheme if isinstance(scheme, str) else (scheme or {}).get("name")
            out.append((name, i.get("value")))
    return out


def purl_of(el):
    for scheme, value in identities(el):
        if scheme == "purl":
            return value
    return None


def refs_of(element):
    return element.get("externalReferences", []) or []


def ref_props(ref):
    return {p.get("name", "")[len(PROP):]: p.get("value") for p in ref.get("properties", []) or []
            if p.get("name", "").startswith(PROP)}


def doc_key(bom):
    serial = str(bom.get("serialNumber", ""))
    return "urn:cdx:%s/%s" % (serial.replace("urn:uuid:", ""), bom.get("version", 1))


def split_bomlink(url):
    if not str(url).startswith("urn:cdx:"):
        return None, None
    doc, _, ref = str(url).partition("#")
    return doc, (ref or None)


class Registry:
    """Documents an evaluation has been given, addressable by BOM-Link.

    A deployment record cites the product record it builds on by BOM-Link and
    hash. When the cited document is supplied (--with), the citation is checked
    and implementation facts are followed across the join; when it is not, the
    citation is checked for form only and the report says it was not resolved."""

    def __init__(self):
        self.docs = {}

    def add(self, path):
        with open(path, "rb") as fh:
            data = fh.read()
        bom = json.loads(data)
        self.docs[doc_key(bom)] = {"path": path, "bom": bom,
                                   "sha256": hashlib.sha256(data).hexdigest()}
        return bom

    def get(self, key):
        return self.docs.get(key)


def _unique(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


def _collapse(v):
    if isinstance(v, list):
        if not v:
            return None
        return v[0] if len(v) == 1 else v
    return v


def _related_refs(props_obj):
    """Targets of relatedCryptographicAssets (2.0) or cryptoRefArray (1.x)."""
    refs = list(props_obj.get("cryptoRefArray", []) or [])
    for r in props_obj.get("relatedCryptographicAssets", []) or []:
        if isinstance(r, dict) and r.get("ref"):
            refs.append(r["ref"])
    return refs


def _asset_type(el):
    return (el or {}).get("cryptoProperties", {}).get("assetType")


def _algorithms(refs, comps, prims):
    names = []
    for r in refs:
        c = comps.get(r)
        if _asset_type(c) == "algorithm" and \
                c["cryptoProperties"].get("algorithmProperties", {}).get("primitive") in prims:
            names.append(c.get("name"))
    return _unique(names)


def _signature_algorithms(refs, comps):
    names = []
    for r in refs:
        c = comps.get(r, {})
        if _asset_type(c) == "certificate":
            cert = c["cryptoProperties"].get("certificateProperties", {})
            sigs = [cert.get("signatureAlgorithmRef")] + _related_refs(cert)
            names += [comps[s].get("name") for s in sigs if s in comps and _asset_type(comps[s]) == "algorithm"]
    return _unique(names + _algorithms(refs, comps, SIG_PRIMS))


def _material(refs, comps):
    return [comps[r] for r in refs if _asset_type(comps.get(r)) == "related-crypto-material"]


def _material_algorithm(m, comps):
    rm = m["cryptoProperties"].get("relatedCryptoMaterialProperties", {})
    targets = ([rm["algorithmRef"]] if rm.get("algorithmRef") else []) + _related_refs(rm)
    for t in targets:
        if _asset_type(comps.get(t)) == "algorithm":
            return comps[t].get("name")
    return None


def _key_wrapping(materials, comps):
    out = []
    for m in materials:
        sb = m["cryptoProperties"].get("relatedCryptoMaterialProperties", {}).get("securedBy") or {}
        if str(sb.get("mechanism", "")).lower() == "none":
            out.append("none")
            continue
        refs = sb.get("algorithmRef")
        for r in ([refs] if isinstance(refs, str) else (refs or [])):
            if r in comps:
                out.append(comps[r].get("name"))
    return _collapse(_unique(out))


def _supported_from_suites(pp, comps):
    """TLS groups and signature schemes a protocol component or its shared configurations offer."""
    suites = list(pp.get("cipherSuites", []) or [])
    for r in pp.get("relatedCryptographicAssets", []) or []:
        target = comps.get(r.get("ref")) if isinstance(r, dict) else None
        if _asset_type(target) == "protocol" and target is not None:
            suites += target["cryptoProperties"].get("protocolProperties", {}).get("cipherSuites", []) or []
    groups, schemes = [], []
    for s in suites:
        groups += s.get("tlsGroups", []) or []
        schemes += s.get("tlsSignatureSchemes", []) or []
    return _unique(groups), _unique(schemes)


def _validation_from_certifications(el):
    for cert in el.get("certifications", []) or []:
        std = str(cert.get("standard", "")).strip()
        scheme = VALIDATION_STANDARDS.get(std.lower(), std)
        return scheme, cert.get("url") or cert.get("identifier")
    return None, None


def _library_facts(lib):
    """Implementation facts stated once on a library (K9)."""
    single, multi, markers, groups, gm = split_properties(lib)
    facts = {k: single[k] for k in INHERITABLE if k in single}
    scheme, ref = _validation_from_certifications(lib)
    if scheme and "moduleValidationScheme" not in facts:
        facts["moduleValidationScheme"] = scheme
    if ref and "moduleValidationRef" not in facts:
        facts["moduleValidationRef"] = ref
    for r in refs_of(lib):
        if r.get("type") == "certification-report" and "moduleValidationRef" not in facts:
            facts["moduleValidationRef"] = r.get("url")
    return facts, groups, gm


def _coverage(bom, subject_attrs):
    if subject_attrs.get("coverage"):
        return subject_attrs["coverage"]
    for comp in bom.get("compositions", []) or []:
        agg = comp.get("aggregate")
        if agg == "complete":
            return "all"
        if agg and agg.startswith("incomplete"):
            return "partial"
    return None


def extract_product(bom, registry=None):
    subject, entries, inventories = document_parts(bom)
    single, _multi, markers, _g, _gm = split_properties(subject)
    attrs = dict(single)
    cov = _coverage(bom, single)
    if cov:
        attrs["coverage"] = cov
    if "productCertificationScheme" not in attrs and subject.get("certifications"):
        std = str(subject["certifications"][0].get("standard", "")).strip().lower()
        attrs["productCertificationScheme"] = PRODUCT_CERTIFICATIONS.get(std, std)
    ident = purl_of(subject)
    if not ident:
        for scheme, value in identities(subject):
            if scheme == "tag-uri":
                ident = value
        ident = ident or single.get("subjectIdentifier")
    phases = [l.get("phase") for l in bom.get("metadata", {}).get("lifecycles", []) or []
              if isinstance(l, dict) and l.get("phase")]
    stages = _unique(PHASE_TO_STAGE.get(p) for p in phases)
    cited = [r for r in refs_of(bom)
             if r.get("type") == "bom" and ref_props(r).get("context") == "cited-document"]
    return {"attrs": attrs, "_disclosure": markers,
            "subjectType": single.get("subjectType"),
            "providerCount": len([c for c in entries if c.get("type") == "library" and purl_of(c)]),
            # The subject's own identifier. A CBOM that does not say which version
            # of what it describes cannot be matched to a deployment, compared
            # with last quarter's, or joined to an SBOM.
            "identifier": ident,
            "identifierFallback": "%s@%s" % (subject.get("name"), subject.get("version"))
                                  if subject.get("name") and subject.get("version") else None,
            "phases": phases, "docStage": stages[0] if len(stages) == 1 else None,
            "cited": cited, "inventories": inventories}


def extract_interfaces(bom, registry=None):
    subject, entries, _n = document_parts(bom)
    product = extract_product(bom)
    comps = {c.get("bom-ref"): c for c in entries}
    deps = {d.get("ref"): d.get("dependsOn", []) or [] for d in bom.get("dependencies", []) or []}
    provider = {}
    for d in bom.get("dependencies", []) or []:
        for p in d.get("provides", []) or []:
            provider[p] = d.get("ref")

    interfaces = []
    for el in entries:
        single, multi, markers, groups, group_markers = split_properties(el)
        if "interfaceType" not in single:
            continue
        ref = el.get("bom-ref")
        pp = el.get("cryptoProperties", {}).get("protocolProperties") \
            if _asset_type(el) == "protocol" else None
        if pp is not None:
            arefs = _related_refs(pp)
            protocol = (pp.get("type") or "").upper() or None
            version = pp.get("version")
        else:
            arefs = list(deps.get(ref, []))
            protocol, version = None, None
        iface = {k: (_collapse(multi[k]) if len(multi.get(k, [])) > 1 else v) for k, v in single.items()}
        iface.update({
            "_element": el, "_disclosure": markers, "_sources": {},
            "_groups": {}, "_groupMarkers": {},
            "interfaceId": single.get("interfaceId") or ref,
            "protocol": single.get("protocol") or protocol,
            "protocolVersion": single.get("protocolVersion") or version,
            "endpointRoles": [k.split(":")[-1] for k in single if k.startswith("endpointRole:")],
            "_stageOwn": single.get("lifecycleStage"),
            "lifecycleStage": single.get("lifecycleStage") or product["docStage"],
        })
        for attr, prims in (("keyExchange", KEX_PRIMS), ("encryption", ENC_PRIMS)):
            iface[attr] = _collapse(multi[attr]) if attr in multi else _collapse(_algorithms(arefs, comps, prims))
        iface["authentication"] = _collapse(multi["authentication"]) if "authentication" in multi \
            else _collapse(_signature_algorithms(arefs, comps))
        mats = _material(arefs, comps)
        if "keyWrapping" not in single:
            iface["keyWrapping"] = _key_wrapping(mats, comps)
        if "keyTypes" not in multi and mats:
            iface["keyTypes"] = _unique(_material_algorithm(m, comps) for m in mats) or None
        if "keyStoreFormats" not in multi and mats:
            fmts = _unique(str(m["cryptoProperties"].get("relatedCryptoMaterialProperties", {})
                               .get("format", "")).lower() for m in mats)
            iface["keyStoreFormats"] = fmts or None
        if pp is not None:
            g, s = _supported_from_suites(pp, comps)
            if "keyExchangeSupported" not in multi and g:
                iface["keyExchangeSupported"] = g
                iface["_sources"]["keyExchangeSupported"] = "cipherSuites.tlsGroups"
            if "authenticationSupported" not in multi and s:
                iface["authenticationSupported"] = s
                iface["_sources"]["authenticationSupported"] = "cipherSuites.tlsSignatureSchemes"
        for k in ("protocolVersionsSupported", "keyExchangeSupported", "authenticationSupported",
                  "keyOperations", "keyTypesSupported", "keyStoreFormatsSupported", "keyStoreFormats",
                  "keyTypes", "externalDependencies", "keyWrappingSupported", "observationMethod"):
            if k in multi:
                iface[k] = list(multi[k])
        if "providerLocation" not in single:
            envs = _unique(EXECUTION_TO_LOCATION.get(comps[r]["cryptoProperties"]
                                                     .get("algorithmProperties", {}).get("executionEnvironment"))
                           for r in arefs if _asset_type(comps.get(r)) == "algorithm")
            if len(envs) == 1:
                iface["providerLocation"] = envs[0]
                iface["_sources"]["providerLocation"] = "algorithm executionEnvironment"
        # K9: inherit implementation facts from the providing library.
        lib = comps.get(provider.get(ref))
        lib_groups, lib_gm = {}, {}
        if lib is not None:
            if "implementationPurl" not in single and purl_of(lib):
                iface["implementationPurl"] = purl_of(lib)
                iface["_sources"]["implementationPurl"] = "provided by %s" % lib.get("bom-ref")
            facts, lib_groups, lib_gm = _library_facts(lib)
            for k, v in facts.items():
                if not present(iface.get(k)) and k not in markers:
                    iface[k] = v
                    iface["_sources"][k] = "inherited from %s" % lib.get("bom-ref")
        for name in set(lib_groups) | set(groups):
            merged = dict(lib_groups.get(name, {}))
            merged.update(groups.get(name, {}))
            iface["_groups"][name] = merged
            gm = dict(lib_gm.get(name, {}))
            gm.update(group_markers.get(name, {}))
            iface["_groupMarkers"][name] = gm
        interfaces.append(iface)

    for iface in interfaces:
        iface["_unresolved"] = {}
        link = iface.get("correspondsTo")
        doc, ref = split_bomlink(link)
        if not doc or not ref:
            continue
        for attr in INHERITED_ACROSS_DOCUMENTS:
            if present(iface.get(attr)) or attr in iface["_disclosure"]:
                continue
            value, path = follow_correspondence(link, attr, registry, set()) if registry else (None, [])
            if present(value):
                iface[attr] = value
                iface["_sources"][attr] = "inherited via " + " -> ".join(path)
            elif not registry or not registry.get(doc):
                # The fact lives in a document this one cites, and the evaluator
                # was not given it. That is a gap in the evaluator's inputs, not
                # in the document, so it is reported and does not fail the rule.
                iface["_unresolved"][attr] = link
    return interfaces


def follow_correspondence(link, attr, registry, seen):
    """Resolve an implementation fact along a chain of correspondsTo BOM-Links."""
    doc, ref = split_bomlink(link)
    if not doc or not ref or link in seen:
        return None, []
    seen.add(link)
    entry = registry.get(doc)
    if not entry:
        return None, []
    here = os.path.basename(entry["path"]) + "#" + ref
    for i in extract_interfaces(entry["bom"]):
        if i["interfaceId"] == ref:
            if present(i.get(attr)):
                return i[attr], [here]
            value, path = follow_correspondence(i.get("correspondsTo"), attr, registry, seen)
            return (value, [here] + path) if present(value) else (None, [])
    return None, []


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
    """Evaluate a 'requiredWhen' guard. Absent guard means always applicable.

    A guard on an attribute the document does not state does not hold. Without
    this, a rule guarded on another rule's attribute failed alongside it: an
    omitted moduleValidationScheme failed I10 and also I11, which asks for the
    reference only when the scheme is not 'none'. One omission is reported once."""
    cond = rule.get("requiredWhen")
    if not cond:
        return True, None
    actual = iface.get(cond["attribute"])
    if not present(actual):
        return False, "%s not stated" % cond["attribute"]
    if "equals" in cond:
        return actual == cond["equals"], "%s=%r" % (cond["attribute"], actual)
    if "notEquals" in cond:
        return actual != cond["notEquals"], "%s=%r" % (cond["attribute"], actual)
    if "in" in cond:
        return actual in cond["in"], "%s=%r" % (cond["attribute"], actual)
    return True, None


def _as_list(v):
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def check_value(iface, value, rule, profile):
    """Check a supplied value, including literals and joins, against a rule."""
    constraint = rule["constraint"]
    lits = constraint.get("literals")
    if lits is not None:
        values = _as_list(value)
        used = [v for v in values if v in lits]
        if used and len(values) > 1:
            return False, "the literal %r stands alone and cannot be listed with values" % used[0]
        if used:
            allowed = (constraint.get("literalStages") or {}).get(used[0])
            stage = iface.get("lifecycleStage")
            if allowed and stage not in allowed:
                return False, ("= %r, accepted only at %s; at %r the producer holds the answer"
                               % (used[0], ", ".join(allowed), stage))
            return True, "= %r" % used[0]
        constraint = {k: v for k, v in constraint.items() if k not in ("literals", "literalStages")}
    if "refersToCited" in constraint:
        spec = constraint["refersToCited"]
        if value in spec.get("literals", []):
            return True, "= %r" % value
        doc, ref = split_bomlink(value)
        if not doc or not ref:
            return False, "= %r, not a BOM-Link to an interface" % (value,)
        ctx = iface.get("_context") or {}
        cited = [split_bomlink(r.get("url"))[0] for r in ctx.get("cited", [])]
        if doc not in cited:
            return False, "points into %s, which the document does not cite" % doc
        registry = ctx.get("registry")
        entry = registry.get(doc) if registry else None
        if not entry:
            return True, "-> %s (cited document not supplied, so not resolved)" % value
        if ref not in [i["interfaceId"] for i in extract_interfaces(entry["bom"])]:
            return False, "-> %s, which is not an interface in %s" % (ref, os.path.basename(entry["path"]))
        return True, "-> %s#%s" % (os.path.basename(entry["path"]), ref)
    if rule.get("list") and "enumRef" in constraint:
        vocab = profile.get(constraint["enumRef"], [])
        bad = [v for v in _as_list(value) if v not in vocab]
        return (not bad, ("= %r" % (value,)) if not bad else "%r not in the vocabulary" % bad)
    return check_attr(value, constraint, profile)


def check_rule(iface, rule, profile):
    """Evaluate one interface rule. Returns (ok, state, detail)."""
    applies, why = condition_holds(rule, iface)
    if not applies:
        return (True, "n/a", "not applicable (%s)" % why)

    attr = rule["attribute"]
    value = iface.get(attr)
    if present(value):
        ok, detail = check_value(iface, value, rule, profile)
        if rule.get("list") and isinstance(value, (list, tuple)):
            detail = "%s %s" % (detail, list(value)[:3])
        src = (iface.get("_sources") or {}).get(attr)
        if src:
            detail = "%s [%s]" % (detail, src)
        return (ok, "value", detail)

    unresolved = (iface.get("_unresolved") or {}).get(attr)
    if unresolved:
        return (True, "unresolved", "inherited from %s, which was not supplied; evaluate with "
                "--with <cited document> to resolve it" % unresolved)
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
    if rule.get("keyCoverage") == "in-scope":
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


KIND_ORDER = {"P": 0, "I": 1, "G": 2, "R": 3}


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


def _cited_interfaces_of_type(product, interface_type):
    """Interfaces of a type declared in the configured records this one cites, where supplied."""
    registry = product.get("_registry")
    found = []
    for r in product.get("cited", []):
        doc, _ref = split_bomlink(r.get("url"))
        entry = registry.get(doc) if (registry and doc) else None
        if entry and extract_product(entry["bom"]).get("docStage") == "configured":
            found += ["%s#%s" % (os.path.basename(entry["path"]), i["interfaceId"])
                      for i in extract_interfaces(entry["bom"]) if i.get("interfaceType") == interface_type]
    return found


def check_product(product, interfaces, constraint, profile):
    if "subjectDeclared" in constraint:
        declared, allowed = product.get("subjectType"), subject_types(profile)
        if not declared:
            return (False, "the document does not declare the type of subject it describes")
        if allowed and declared not in allowed:
            return (False, "= %r, outside the subject types this profile accepts (%s)"
                    % (declared, ", ".join(allowed)))
        return (True, "= %r" % declared)
    if "singleStage" in constraint:
        phases, stage = product.get("phases") or [], product.get("docStage")
        if not phases:
            return (False, "no metadata.lifecycles phase, so the document's stage is undeclared")
        if not stage:
            return (False, "metadata.lifecycles names %s, which map to more than one stage" % phases)
        clash = [i["interfaceId"] for i in interfaces if i.get("_stageOwn") and i["_stageOwn"] != stage]
        if clash:
            return (False, "the document's stage is %r, and %d interface(s) report another: %s"
                    % (stage, len(clash), ", ".join(clash[:4]) + (" ..." if len(clash) > 4 else "")))
        if product.get("inventories", 1) > 1:
            return (False, "the document carries %d inventories; one document describes one subject"
                    % product["inventories"])
        return (True, "= %r (lifecycle phase %r)" % (stage, phases[0]))
    if "minInterfaces" in constraint:
        n = len(interfaces)
        return (n >= constraint["minInterfaces"], "%d interface(s) declared" % n)
    if "subjectIdentified" in constraint:
        spec = constraint["subjectIdentified"]
        prefix = spec.get("startsWith")
        if isinstance(prefix, dict):
            prefix = prefix.get(product.get("subjectType") or "")
            if not prefix:
                return (False, "no identifier form is defined for a subject of type %r"
                        % product.get("subjectType"))
        value = product.get("identifier")
        if present(value):
            if prefix and not str(value).startswith(prefix):
                return (False, "subject identified as %r, which is not a %s identifier"
                        % (value, prefix))
            return (True, "= %r" % (value,))
        if product.get("identifierFallback"):
            return (False, "subject named as %r but carries no identifier in the "
                    "required form; a name and a version are not a stable identifier"
                    % product["identifierFallback"])
        return (False, "the document does not say what it describes")
    if "citesDocuments" in constraint:
        spec = constraint["citesDocuments"]
        cited = product.get("cited", [])
        if len(cited) < spec.get("min", 1):
            return (False, "%d cited document(s), at least %d required" % (len(cited), spec.get("min", 1)))
        registry, notes, ok = product.get("_registry"), [], True
        for r in cited:
            url = r.get("url")
            doc, _ref = split_bomlink(url)
            hashes = {h.get("alg"): h.get("content") for h in r.get("hashes", []) or []}
            if not doc:
                ok = False
                notes.append("%s is not a BOM-Link" % url)
                continue
            if spec.get("hashRequired") and "SHA-256" not in hashes:
                ok = False
                notes.append("%s carries no SHA-256" % url)
                continue
            entry = registry.get(doc) if registry else None
            if not entry:
                notes.append("%s (not supplied, so not resolved)" % url)
            elif entry["sha256"] != hashes.get("SHA-256"):
                ok = False
                notes.append("%s: the hash does not match %s, so the cited revision has changed"
                             % (url, os.path.basename(entry["path"])))
            else:
                notes.append("%s = %s, hash matches" % (url, os.path.basename(entry["path"])))
        return (ok, "; ".join(notes))

    if "minInterfacesOfType" in constraint:
        spec = constraint["minInterfacesOfType"]
        n = sum(1 for i in interfaces if i.get("interfaceType") == spec["interfaceType"])
        if n >= spec["min"]:
            return (True, "%d of type '%s' (min %d)"
                    % (n, spec["interfaceType"], spec["min"]))

        # At 'observed', an interface the observer could not reach may still be
        # declared by the configured record the observation cites. The omission
        # stays visible through the join, as an interface with no observed
        # counterpart, so nothing is hidden by accepting it here.
        if constraint.get("orCitedDeclares") and product.get("docStage") == "observed":
            found = _cited_interfaces_of_type(product, spec["interfaceType"])
            if found:
                return (True, "none observed; declared in a cited record: %s" % ", ".join(found[:3]))

        # A structural rule is satisfied by presence or by an explicit statement
        # of absence; silence is neither. This is the disclosure model applied
        # to structure.
        absent = constraint.get("orDeclaredAbsent")
        if absent:
            reason = product.get("attrs", {}).get(absent)
            if present(reason):
                vocab = profile.get(constraint.get("absenceEnumRef"), [])
                if vocab and reason not in vocab:
                    return (False, "declared absent as %r, which is not a permitted reason"
                            % (reason,))
                cond = (constraint.get("absenceConditions") or {}).get(reason)
                if cond:
                    if "documentStage" in cond and product.get("docStage") not in cond["documentStage"]:
                        return (False, "declared absent as %r, which is accepted only at %s"
                                % (reason, ", ".join(cond["documentStage"])))
                    cov = product.get("attrs", {}).get("coverage")
                    if "coverage" in cond and cov not in cond["coverage"]:
                        return (False, "declared absent as %r, which is accepted only with coverage %s"
                                % (reason, " or ".join(cond["coverage"])))
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


def reference_applies(rule, product, iface=None):
    cond = rule.get("requiredWhen") or {}
    if "subjectType" in cond and product.get("subjectType") != cond["subjectType"]:
        return False, "subjectType=%r" % product.get("subjectType")
    if "documentStage" in cond and product.get("docStage") != cond["documentStage"]:
        return False, "document stage=%r" % product.get("docStage")
    if "anyAttributeEquals" in cond:
        spec = cond["anyAttributeEquals"]
        if not iface or not [a for a in spec["attributes"] if iface.get(a) == spec["value"]]:
            return False, "no attribute is %r" % spec["value"]
    return True, None


def check_reference(rule, profile, element_refs, markers, absence):
    """Evaluate a reference rule: a pointer to context the document does not carry.

    Checks that the pointer exists and is well formed: a carrier type the kind
    allows, a hash where the target is a fixed document, an access protocol
    where it is an endpoint. Never evaluates what the pointer points to."""
    kind = profile["contextKinds"][rule["context"]]
    vocab = profile.get("accessProtocolVocabulary", [])
    found = [r for r in element_refs if ref_props(r).get("context") == rule["context"]]
    if not found:
        marker = markers.get(rule["context"])
        if marker == "withheld":
            return (bool(rule.get("withholdable")), "withheld", "withheld by producer (%s)"
                    % ("permitted" if rule.get("withholdable") else "not permitted here"))
        reason = absence.get("contextAbsent:" + rule["context"])
        if reason:
            allowed = profile.get(rule.get("orDeclaredAbsent") or "", [])
            if rule.get("orDeclaredAbsent") and reason in allowed:
                return True, "absent", "stated absent: %r" % reason
            return False, "absent", "stated absent as %r, which this rule does not accept" % reason
        return False, "undeclared", "no pointer to %s, and no statement of absence" % rule["context"]
    problems, details = [], []
    for r in found:
        rp = ref_props(r)
        proto = rp.get("accessProtocol")
        if r.get("type") not in kind.get("carrier", []):
            problems.append("type %r is not a carrier for %s (%s)"
                            % (r.get("type"), rule["context"], ", ".join(kind.get("carrier", []))))
        endpoint = bool(proto) and proto != "vex-document"
        if kind.get("form") == "document" and endpoint:
            problems.append("%s must be a fixed document, not an endpoint" % rule["context"])
        if endpoint and vocab and proto not in vocab:
            problems.append("access protocol %r is not in the vocabulary" % proto)
        need_hash = rule.get("hashRequired") is True or \
            (rule.get("hashRequired") == "when-document" and not endpoint)
        if need_hash and not r.get("hashes"):
            problems.append("%s needs a hash, because it is a fixed document" % r.get("url"))
        details.append("%s%s" % (r.get("url"), " (%s)" % proto if proto else ""))
    if problems:
        return False, "value", "; ".join(problems)
    return True, "value", "; ".join(details)


# --------------------------------------------------------------------------- #
def validate(bom, profile, registry=None):
    """Evaluate a CBOM against a profile.

    Returns (verdict, report) where verdict is one of the three the Conformance
    section defines: 'conforms', 'does-not-conform', or 'refused'.

    Refusal is not a failure and the two must not be merged. A refused document
    may be entirely adequate; the profile is simply unable to express its rules
    against that carrier version, so no assessment is performed and the report
    carries no rule results to summarise.

    'registry' holds the documents this one cites, where the caller has them.
    Without it, citations are checked for form and joins are not followed."""
    fmt = check_format(bom, profile)
    report = {"format": fmt, "product": [], "references": [], "interfaces": []}
    if not fmt["ok"]:
        return "refused", report

    product = extract_product(bom)
    product["_registry"] = registry
    interfaces = extract_interfaces(bom, registry)
    for iface in interfaces:
        iface["_context"] = {"cited": product.get("cited", []), "registry": registry}

    chain = profile.get("_chain", [])

    for rule in profile.get("productRules", []):
        ok, detail = check_product(product, interfaces, rule["constraint"], profile)
        row = dict(rule, id=rule.get("_qid", rule["id"]), ok=ok, detail=detail)
        row.pop("_qid", None)
        report["product"].append(row)

    absence = product.get("attrs", {})
    for rule in profile.get("referenceRules", []):
        if rule.get("at") != "document":
            continue
        applies, why = reference_applies(rule, product)
        if not applies:
            ok, state, detail = True, "n/a", "not applicable (%s)" % why
        else:
            ok, state, detail = check_reference(rule, profile, refs_of(bom),
                                                product.get("_disclosure", {}), absence)
        report["references"].append({"id": rule["_qid"], "level": rule["level"],
                                     "attribute": rule["context"], "ok": ok,
                                     "state": state, "detail": detail})

    for iface in interfaces:
        rows = []
        for rule in profile.get("interfaceRules", []):
            ok, state, detail = check_rule(iface, rule, profile)
            rows.append({"id": rule["_qid"], "level": rule["level"],
                         "attribute": rule["attribute"], "ok": ok,
                         "state": state, "detail": detail})
        for grule in profile.get("groupRules", []):
            rows.extend(check_group_rule(iface, grule, profile))
        for rule in profile.get("referenceRules", []):
            if rule.get("at") != "interface":
                continue
            applies, why = reference_applies(rule, product, iface)
            if not applies:
                ok, state, detail = True, "n/a", "not applicable (%s)" % why
            else:
                ok, state, detail = check_reference(rule, profile, refs_of(iface["_element"]),
                                                    iface.get("_disclosure", {}), {})
            rows.append({"id": rule["_qid"], "level": rule["level"], "attribute": rule["context"],
                         "ok": ok, "state": state, "detail": detail})
        rows.sort(key=lambda r: rule_sort_key(r, chain))
        iface_ok = all(r["ok"] for r in rows if r["level"] == "MUST")
        report["interfaces"].append({
            "interfaceId": iface["interfaceId"],
            "interfaceType": iface.get("interfaceType"),
            "conforms": iface_ok, "rows": rows,
        })

    product_ok = all(r["ok"] for r in report["product"] + report["references"]
                     if r["level"] == "MUST")
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
    "anything inherited from a cited document the evaluator was not given; those rules are listed as unresolved",
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
    buckets = {"failed": [], "withheld": [], "unknown": [], "undeclared": [], "unresolved": []}
    total = 0
    for row in report.get("product", []) + report.get("references", []):
        total += 1
        if not row.get("ok") and row.get("level") == "MUST":
            buckets["failed"].append(row["id"])
        if row.get("state") in ("withheld", "unknown", "undeclared"):
            buckets[row["state"]].append(row["id"])
    for iface in report.get("interfaces", []):
        for row in iface.get("rows", []):
            total += 1
            ref = "%s/%s" % (iface["interfaceId"], row["id"])
            if not row.get("ok") and row.get("level") == "MUST":
                buckets["failed"].append(ref)
            state = row.get("state")
            if state in ("withheld", "unknown", "undeclared", "unresolved"):
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
        return {"withheld": "HELD", "n/a": " -- ", "unresolved": "OPEN"}.get(row.get("state"), "PASS")
    if row["level"] == "MUST":
        return "UNKN" if row.get("state") == "unknown" else "FAIL"
    return "warn"


def main(argv):
    # '--with <document>' supplies a document this one cites, so the citation's
    # hash is checked and joins across documents are followed. It may repeat.
    withs, rest, i = [], [], 1
    while i < len(argv):
        if argv[i] == "--with" and i + 1 < len(argv):
            withs.append(argv[i + 1])
            i += 2
            continue
        if argv[i].startswith("--with="):
            withs.append(argv[i].split("=", 1)[1])
        else:
            rest.append(argv[i])
        i += 1
    argv = [argv[0]] + rest
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    as_json = "--json" in argv
    as_claim = "--claim" in argv
    verifying = "--verify-claim" in argv

    registry = Registry()
    for w in withs:
        registry.add(w)
    bom = registry.add(args[0])

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
            vd, rp = validate(bom, prof, registry)
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
    if report.get("references"):
        print("-" * 70)
        print("REFERENCE RULES (context the document points to and does not carry)")
        ridw = max([len(r["id"]) for r in report["references"]] + [4])
        for r in report["references"]:
            print("  [%s] %-*s %-6s %-24s %s" % (icon_for(r), ridw, r["id"], r["level"],
                                                 r["attribute"], r["detail"]))
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
    fails = [r["id"] for r in report["product"] + report.get("references", [])
             if not r["ok"] and r["level"] == "MUST"]
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
