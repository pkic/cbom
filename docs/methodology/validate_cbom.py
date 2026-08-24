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

Usage:
    python validate_cbom.py <cbom.json> <profile.rules.json> [--json]

Exit codes:
    0  conforms
    1  does not conform
    2  usage error
    3  profile error, such as an override that relaxes an inherited rule
    4  refused: not assessed, as distinct from assessed and found short
"""
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
                check_override_tightens(target, ov, notes)
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

    # Group rules are concatenated rather than overridden. A derived profile may
    # add a group; tightening one member of an inherited group is not yet
    # expressible, and inventing a syntax for it before anyone needs it would be
    # guessing. The gap is recorded rather than hidden.
    inherited_groups = [dict(g) for g in base.get("groupRules", [])]
    seen_groups = {g["_qid"] for g in inherited_groups}
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


def check_override_tightens(base_rule, ov, notes):
    """Reject an override that relaxes an inherited rule."""
    rid = base_rule.get("_qid", base_rule["id"])
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
    return (True, "ok")


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
    return (True, "ok")


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

    bom = json.load(open(args[0], encoding="utf-8"))
    try:
        profile, origin, notes = load_profile(args[1])
    except ProfileError as err:
        print("PROFILE ERROR: %s" % err, file=sys.stderr)
        return 3
    verdict, report = validate(bom, profile)

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
