#!/usr/bin/env python3
"""Draft evaluator for the Keycloak lifecycle example.

Evaluates a CycloneDX CBOM against the draft profiles in ../profiles. It reuses
docs/methodology/validate_cbom.py for constraint checks, guards and override
comparison, and adds what the drafts need and the published validator lacks:

  * the K7-K9 encoding: interfaces may be protocol components or services;
    algorithms come from cryptoRefArray or the dependency graph; the
    implementing library comes from dependencies[].provides
  * one stage per document: the stage is read from metadata.lifecycles
  * literal values with stage restrictions ('deployment-defined',
    'peer-defined' only at 'implemented')
  * scope.subjectTypes as a set, narrowed by a derived profile
  * reference rules (R): pointers to context the document does not carry
  * joins across documents: BOM-Links checked against the cited document's
    serial number, version and SHA-256, and implementationPurl inherited
    along correspondsTo

It is a test harness for the drafts, not a replacement for validate_cbom.py.

Usage:
    python3 evaluate_draft.py <cbom.json> <profile.rules.json> [--with other.json ...] [--json]
Exit: 0 conforms, 1 does not conform, 3 profile error
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "methodology"))
import validate_cbom as V  # noqa: E402

ProfileError = V.ProfileError
PROP = V.PROP
SECTIONS = ("productRules", "interfaceRules", "referenceRules")
PHASE_TO_STAGE = {"design": "intended", "pre-build": "implemented", "build": "implemented",
                  "post-build": "implemented", "operations": "configured",
                  "discovery": "observed"}
INHERITED_ACROSS_DOCUMENTS = ("implementationPurl",)


# --------------------------------------------------------------------------- #
# Composition                                                                 #
# --------------------------------------------------------------------------- #
def _literal_stages_tighten(old, new):
    for lit, stages in new.items():
        if lit not in old:
            return (False, "adds a stage restriction for %r, which the base accepts nowhere" % lit)
        if not set(stages) <= set(old[lit]):
            return (False, "accepts %r at more stages than the base" % lit)
    return (True, "%s -> %s" % (old, new))


def _subject_map_tightens(old, new):
    o, n = old.get("startsWith"), new.get("startsWith")
    if isinstance(o, dict) and isinstance(n, dict):
        ok = all(k in o and str(v).startswith(str(o[k])) for k, v in n.items())
        return (ok, "%s -> %s" % (o, n))
    return V._subject_tightens(old, new)


V.CONSTRAINT_COMPARATORS.update({
    "literals": V._subset_tightens,
    "literalStages": _literal_stages_tighten,
    "subjectIdentified": _subject_map_tightens,
    "citesDocuments": V._equal_only,
    "refersToCited": V._equal_only,
    "subjectDeclared": V._equal_only,
    "singleStage": V._equal_only,
})
ATTRIBUTE_KEYS = set(V.ATTRIBUTE_CONSTRAINTS) | {"literals", "literalStages", "refersToCited"}
PRODUCT_KEYS = set(V.PRODUCT_CONSTRAINTS) | {"subjectDeclared", "singleStage", "citesDocuments"}


def _as_list(v):
    if v is None:
        return None
    return list(v) if isinstance(v, (list, tuple)) else [v]


def subject_types(profile):
    sc = profile.get("scope") or {}
    return _as_list(sc.get("subjectTypes") or sc.get("subjectType")) or []


def check_scope_narrows(base, derived):
    b, d = base.get("scope") or {}, derived.get("scope") or {}
    for key, label in (("lifecycleStages", "lifecycle stage(s)"),):
        if b.get(key) and d.get(key):
            wide = [s for s in d[key] if s not in b[key]]
            if wide:
                raise ProfileError("derived profile accepts %s %s that the base rejects"
                                   % (label, ", ".join(wide)))
    bs, ds = subject_types(base), subject_types(derived)
    if bs and ds and not set(ds) <= set(bs):
        raise ProfileError("derived profile accepts subject type(s) %s that the base does not"
                           % ", ".join(sorted(set(ds) - set(bs))))


def load_profile(path):
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    tag = raw["profileTag"]
    for s in SECTIONS:
        for r in raw.get(s, []):
            r["_qid"] = "%s#%s" % (tag, r["id"])
    notes = []
    ext = raw.get("extends")
    if not ext:
        raw["_chain"] = [tag]
        V.apply_scope(raw)
        check_evaluable(raw)
        return raw, notes
    base, notes = load_profile(os.path.join(os.path.dirname(os.path.abspath(path)), ext["file"]))
    if base["profileId"] != ext["profileId"] or str(base["version"]) != str(ext["version"]):
        raise ProfileError("extends pins %s %s, found %s %s" % (ext["profileId"], ext["version"],
                                                               base["profileId"], base["version"]))
    if tag in base["_chain"]:
        raise ProfileError("profile tag %r already used in the family" % tag)
    check_scope_narrows(base, raw)
    merged = dict(base)
    merged.update({k: v for k, v in raw.items()
                   if k not in SECTIONS + ("overrides", "extends", "contextKinds")})
    kinds = dict(base.get("contextKinds", {}))
    for k, v in raw.get("contextKinds", {}).items():
        if k in kinds and kinds[k] != v:
            raise ProfileError("context kind %r is redefined; a derived profile adds kinds "
                               "and may not change one it inherited" % k)
        kinds[k] = v
    merged["contextKinds"] = kinds
    merged["_chain"] = base["_chain"] + [tag]
    seen = set()
    for s in SECTIONS:
        inherited = [copy.deepcopy(r) for r in base.get(s, [])]
        by_qid = {r["_qid"]: r for r in inherited}
        for ov in raw.get("overrides", []):
            if ov["id"] in by_qid:
                V.check_override_tightens(by_qid[ov["id"]], ov, notes, base, raw)
                by_qid[ov["id"]].update({k: v for k, v in ov.items() if k not in ("id", "note")})
                seen.add(ov["id"])
        merged[s] = inherited + raw.get(s, [])
    missing = [o["id"] for o in raw.get("overrides", []) if o["id"] not in seen]
    if missing:
        raise ProfileError("overrides reference unknown rule(s): %s" % ", ".join(missing))
    V.apply_scope(merged)
    check_evaluable(merged)
    return merged, notes


def check_evaluable(profile):
    problems = []
    for s, allowed in (("productRules", PRODUCT_KEYS), ("interfaceRules", ATTRIBUTE_KEYS)):
        for r in profile.get(s, []):
            for k in (r.get("constraint") or {"<none>": 1}):
                if k not in allowed:
                    problems.append("%s constrains %r, which this evaluator does not implement"
                                    % (r["_qid"], k))
            ref = (r.get("constraint") or {}).get("enumRef")
            if ref and not profile.get(ref):
                problems.append("%s references undeclared vocabulary %r" % (r["_qid"], ref))
    for r in profile.get("referenceRules", []):
        if r.get("context") not in profile.get("contextKinds", {}):
            problems.append("%s names context kind %r, which the profile does not define"
                            % (r["_qid"], r.get("context")))
    if problems:
        raise ProfileError("; ".join(problems))


# --------------------------------------------------------------------------- #
# Documents and joins                                                         #
# --------------------------------------------------------------------------- #
def doc_key(bom):
    serial = str(bom.get("serialNumber", ""))
    return "urn:cdx:%s/%s" % (serial.replace("urn:uuid:", ""), bom.get("version", 1))


def split_bomlink(url):
    if not str(url).startswith("urn:cdx:"):
        return None, None
    doc, _, ref = str(url).partition("#")
    return doc, (ref or None)


class Registry:
    """Documents the evaluator has been given, addressable by BOM-Link."""

    def __init__(self):
        self.docs = {}

    def add(self, path):
        data = open(path, "rb").read()
        bom = json.loads(data)
        self.docs[doc_key(bom)] = {"path": path, "bom": bom,
                                   "sha256": hashlib.sha256(data).hexdigest()}
        return bom

    def get(self, key):
        return self.docs.get(key)


def props(element):
    return V.split_properties(element)


def refs_of(element):
    return element.get("externalReferences", []) or []


def ref_props(ref):
    return {p.get("name", "")[len(PROP):]: p.get("value") for p in ref.get("properties", [])
            if p.get("name", "").startswith(PROP)}


def unique(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


def algos(refs, comps, prims):
    names = []
    for r in refs:
        c = comps.get(r)
        if not c:
            continue
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") == "algorithm" and \
                cp.get("algorithmProperties", {}).get("primitive") in prims:
            names.append(c.get("name"))
    return unique(names)


def auth_algos(refs, comps):
    names = []
    for r in refs:
        c = comps.get(r, {})
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") == "certificate":
            sig = cp.get("certificateProperties", {}).get("signatureAlgorithmRef")
            if sig in comps:
                names.append(comps[sig].get("name"))
    return unique(names + algos(refs, comps, V.SIG_PRIMS))


def collapse(v):
    if isinstance(v, list):
        if not v:
            return None
        return v[0] if len(v) == 1 else v
    return v


def key_wrapping(refs, comps):
    out = []
    for r in refs:
        c = comps.get(r, {})
        cp = c.get("cryptoProperties", {})
        if cp.get("assetType") != "related-crypto-material":
            continue
        sb = cp.get("relatedCryptoMaterialProperties", {}).get("securedBy") or {}
        if sb.get("mechanism") == "none":
            out.append("none")
        elif sb.get("algorithmRef") in comps:
            out.append(comps[sb["algorithmRef"]].get("name"))
    return collapse(unique(out))


def extract(bom, registry):
    comps = {c.get("bom-ref"): c for c in bom.get("components", [])}
    services = {s.get("bom-ref"): s for s in bom.get("services", [])}
    deps = {d["ref"]: d.get("dependsOn", []) for d in bom.get("dependencies", [])}
    provider = {}
    for d in bom.get("dependencies", []):
        for p in d.get("provides", []) or []:
            provider[p] = d["ref"]
    phases = [l.get("phase") for l in bom.get("metadata", {}).get("lifecycles", []) if l.get("phase")]
    stages = unique(PHASE_TO_STAGE.get(p) for p in phases)
    doc_stage = stages[0] if len(stages) == 1 else None

    subj = bom.get("metadata", {}).get("component", {})
    s_single, _m, s_markers, _g, _gm = props(subj)
    cited = []
    for r in refs_of(bom):
        rp = ref_props(r)
        if r.get("type") == "bom" and rp.get("context") == "cited-document":
            cited.append(r)
    product = {
        "attrs": s_single, "_disclosure": s_markers,
        "subjectType": s_single.get("subjectType"),
        "identifier": subj.get("purl") or s_single.get("subjectIdentifier"),
        "identifierFallback": "%s@%s" % (subj.get("name"), subj.get("version"))
                              if subj.get("name") and subj.get("version") else None,
        "providerCount": len([c for c in comps.values() if c.get("type") == "library" and c.get("purl")]),
        "phases": phases, "docStage": doc_stage, "cited": cited,
    }

    interfaces = []
    for ref, el in list(comps.items()) + list(services.items()):
        single, multi, markers, groups, gm = props(el)
        if "interfaceType" not in single:
            continue
        is_proto = el.get("cryptoProperties", {}).get("assetType") == "protocol"
        if is_proto:
            pp = el["cryptoProperties"].get("protocolProperties", {})
            arefs = list(pp.get("cryptoRefArray", []))
            protocol = (pp.get("type") or "").upper() or None
            version = pp.get("version")
        else:
            arefs = list(deps.get(ref, []))
            protocol, version = single.get("protocol"), single.get("protocolVersion")
        iface = {k: (collapse(multi[k]) if len(multi.get(k, [])) > 1 else v)
                 for k, v in single.items()}
        iface.update({
            "_element": el, "_disclosure": markers, "_groups": groups, "_groupMarkers": gm,
            "interfaceId": ref, "protocol": single.get("protocol") or protocol,
            "protocolVersion": single.get("protocolVersion") or version,
            "endpointRoles": [k.split(":")[-1] for k in single if k.startswith("endpointRole:")],
            "_stageOwn": single.get("lifecycleStage"),
            "lifecycleStage": single.get("lifecycleStage") or doc_stage,
            "_sources": {},
        })
        for attr, prims in (("keyExchange", V.KEX_PRIMS), ("encryption", V.ENC_PRIMS)):
            if attr in multi:
                iface[attr] = collapse(multi[attr])
            else:
                iface[attr] = collapse(algos(arefs, comps, prims))
        iface["authentication"] = collapse(multi["authentication"]) if "authentication" in multi \
            else collapse(auth_algos(arefs, comps))
        iface["keyWrapping"] = single.get("keyWrapping") or key_wrapping(arefs, comps)
        if "implementationPurl" not in single and ref in provider:
            lib = comps.get(provider[ref], {})
            if lib.get("purl"):
                iface["implementationPurl"] = lib["purl"]
                iface["_sources"]["implementationPurl"] = "provided by %s" % provider[ref]
        interfaces.append(iface)

    # Inherit implementation facts along correspondsTo, across documents.
    for iface in interfaces:
        for attr in INHERITED_ACROSS_DOCUMENTS:
            if V.present(iface.get(attr)) or attr in iface["_disclosure"]:
                continue
            value, path = follow(iface.get("correspondsTo"), attr, registry, set())
            if V.present(value):
                iface[attr] = value
                iface["_sources"][attr] = "inherited via " + " -> ".join(path)
    return product, interfaces


def follow(link, attr, registry, seen):
    """Resolve attr along a chain of correspondsTo BOM-Links."""
    doc, ref = split_bomlink(link)
    if not doc or not ref or link in seen:
        return None, []
    seen.add(link)
    entry = registry.get(doc)
    if not entry:
        return None, []
    _p, ifaces = extract(entry["bom"], Registry())
    for i in ifaces:
        if i["interfaceId"] == ref:
            if V.present(i.get(attr)):
                return i[attr], [os.path.basename(entry["path"]) + "#" + ref]
            value, path = follow(i.get("correspondsTo"), attr, registry, seen)
            return value, ([os.path.basename(entry["path"]) + "#" + ref] + path) if value else []
    return None, []


# --------------------------------------------------------------------------- #
# Rules                                                                       #
# --------------------------------------------------------------------------- #
def check_value(iface, value, constraint, profile, rule, registry, product):
    lits = constraint.get("literals")
    if lits is not None:
        vals = _as_list(value)
        used = [v for v in vals if v in lits]
        if used and len(vals) > 1:
            return False, "the literal %r stands alone and cannot be listed with values" % used[0]
        if used:
            allowed = (constraint.get("literalStages") or {}).get(used[0])
            stage = iface.get("lifecycleStage")
            if allowed and stage not in allowed:
                return False, ("= %r, accepted only at %s; at %r the producer holds the answer"
                               % (used[0], ", ".join(allowed), stage))
            return True, "= %r" % used[0]
        rest = {k: v for k, v in constraint.items() if k not in ("literals", "literalStages")}
        return V.check_attr(value, rest, profile)
    if "refersToCited" in constraint:
        spec = constraint["refersToCited"]
        if value in spec.get("literals", []):
            return True, "= %r" % value
        doc, ref = split_bomlink(value)
        if not doc or not ref:
            return False, "= %r, not a BOM-Link to an interface" % value
        cited = [split_bomlink(r.get("url"))[0] for r in product["cited"]]
        if doc not in cited:
            return False, "points into %s, which the document does not cite (P1)" % doc
        entry = registry.get(doc)
        if not entry:
            return True, "-> %s (cited document not supplied, not resolved)" % value
        _p, ifs = extract(entry["bom"], Registry())
        if ref not in [i["interfaceId"] for i in ifs]:
            return False, "-> %s, which is not an interface in %s" % (ref, os.path.basename(entry["path"]))
        return True, "-> %s#%s" % (os.path.basename(entry["path"]), ref)
    if rule.get("list") and "enumRef" in constraint:
        vocab = profile.get(constraint["enumRef"], [])
        bad = [v for v in _as_list(value) if v not in vocab]
        return (not bad, "= %r" % (value,) if not bad else "%r not in vocabulary" % bad)
    return V.check_attr(value, constraint, profile)


def check_interface_rule(iface, rule, profile, registry, product):
    applies, why = V.condition_holds(rule, iface)
    if not applies:
        return True, "n/a", "not applicable (%s)" % why
    attr = rule["attribute"]
    value = iface.get(attr)
    if V.present(value):
        ok, detail = check_value(iface, value, rule["constraint"], profile, rule, registry, product)
        src = iface["_sources"].get(attr)
        return ok, "value", detail + (" [%s]" % src if src else "")
    marker = iface["_disclosure"].get(attr)
    if marker == "withheld":
        return (bool(rule.get("withholdable")), "withheld",
                "withheld by producer (%s)" % ("permitted" if rule.get("withholdable") else "not permitted here"))
    if marker == "unknown":
        return False, "unknown", "declared unknown to producer"
    return False, "undeclared", "absent, with no disclosure marker"


def check_product_rule(rule, product, interfaces, profile, registry):
    c = rule["constraint"]
    if "subjectDeclared" in c:
        st, allowed = product["subjectType"], subject_types(profile)
        if not st:
            return False, "the document does not declare its subject type"
        return (st in allowed, "= %r%s" % (st, "" if st in allowed else
                                           ", outside this profile's subject types (%s)" % ", ".join(allowed)))
    if "singleStage" in c:
        phases, st = product["phases"], product["docStage"]
        if not phases:
            return False, "no metadata.lifecycles phase, so the document's stage is undeclared"
        if not st:
            return False, "metadata.lifecycles names %s, which map to more than one stage" % phases
        clash = [i["interfaceId"] for i in interfaces if i["_stageOwn"] and i["_stageOwn"] != st]
        if clash:
            return False, "document stage %r, but %d interface(s) report another: %s" % (
                st, len(clash), ", ".join(clash[:4]) + (" ..." if len(clash) > 4 else ""))
        return True, "= %r (from phase %s)" % (st, phases[0])
    if "subjectIdentified" in c:
        spec = c["subjectIdentified"].get("startsWith")
        if isinstance(spec, dict):
            prefix = spec.get(product["subjectType"])
            val = product["identifier"]
            if not prefix:
                return False, "no identifier form is defined for subject type %r" % product["subjectType"]
            if not V.present(val):
                return False, "the document does not identify its subject"
            return (str(val).startswith(prefix), "= %r (%s expected for a %s)"
                    % (val, prefix, product["subjectType"]))
    if "citesDocuments" in c:
        spec = c["citesDocuments"]
        rows, ok = [], True
        if len(product["cited"]) < spec.get("min", 1):
            return False, "%d cited document(s), at least %d required" % (len(product["cited"]), spec.get("min", 1))
        for r in product["cited"]:
            url = r.get("url")
            doc, _ref = split_bomlink(url)
            hashes = {h.get("alg"): h.get("content") for h in r.get("hashes", [])}
            if not doc:
                ok = False
                rows.append("%s is not a BOM-Link" % url)
                continue
            if spec.get("hashRequired") and "SHA-256" not in hashes:
                ok = False
                rows.append("%s carries no SHA-256" % url)
                continue
            entry = registry.get(doc)
            if not entry:
                rows.append("%s (not supplied, not resolved)" % url)
            elif entry["sha256"] != hashes.get("SHA-256"):
                ok = False
                rows.append("%s: hash does not match %s; the cited revision has changed"
                            % (url, os.path.basename(entry["path"])))
            else:
                rows.append("%s = %s, hash matches" % (url, os.path.basename(entry["path"])))
        return ok, "; ".join(rows)
    return V.check_product(product, interfaces, c, profile)


def reference_applies(rule, product, iface=None):
    cond = rule.get("requiredWhen") or {}
    if "subjectType" in cond and product["subjectType"] != cond["subjectType"]:
        return False, "subjectType=%r" % product["subjectType"]
    if "documentStage" in cond and product["docStage"] != cond["documentStage"]:
        return False, "document stage=%r" % product["docStage"]
    if "anyAttributeEquals" in cond:
        spec = cond["anyAttributeEquals"]
        hit = [a for a in spec["attributes"] if iface and iface.get(a) == spec["value"]]
        if not hit:
            return False, "no attribute is %r" % spec["value"]
    return True, None


def check_reference(rule, profile, element_refs, markers, absence):
    kind = profile["contextKinds"][rule["context"]]
    vocab = profile.get("accessProtocolVocabulary", [])
    found = [r for r in element_refs if ref_props(r).get("context") == rule["context"]]
    if not found:
        if markers.get(rule["context"]) == "withheld":
            return bool(rule.get("withholdable")), "withheld", "withheld by producer (%s)" % (
                "permitted" if rule.get("withholdable") else "not permitted here")
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
        hashes = r.get("hashes") or []
        proto = rp.get("accessProtocol")
        if r.get("type") not in kind["carrier"]:
            problems.append("type %r is not a carrier for %s (%s)" % (r.get("type"), rule["context"],
                                                                     ", ".join(kind["carrier"])))
        is_endpoint = bool(proto) and proto != "vex-document"
        if kind["form"] == "document" and is_endpoint:
            problems.append("%s must be a fixed document, not an endpoint" % rule["context"])
        if is_endpoint and proto not in vocab:
            problems.append("access protocol %r is not in the vocabulary" % proto)
        need_hash = rule.get("hashRequired") is True or \
            (rule.get("hashRequired") == "when-document" and not is_endpoint)
        if need_hash and not hashes:
            problems.append("%s needs a hash, because it is a fixed document" % r.get("url"))
        details.append("%s%s" % (r.get("url"), " (%s)" % proto if proto else ""))
    if problems:
        return False, "value", "; ".join(problems)
    return True, "value", "; ".join(details)


def validate(bom, profile, registry):
    product, interfaces = extract(bom, registry)
    report = {"product": [], "interfaces": [], "references": []}
    for r in profile.get("productRules", []):
        ok, detail = check_product_rule(r, product, interfaces, profile, registry)
        report["product"].append({"id": r["_qid"], "level": r["level"], "ok": ok, "detail": detail,
                                  "attribute": r.get("description", "")})
    absence = product["attrs"]
    for r in profile.get("referenceRules", []):
        if r["at"] != "document":
            continue
        applies, why = reference_applies(r, product)
        if not applies:
            report["references"].append({"id": r["_qid"], "level": r["level"], "ok": True, "state": "n/a",
                                         "attribute": r["context"], "detail": "not applicable (%s)" % why})
            continue
        ok, state, detail = check_reference(r, profile, refs_of(bom), product["_disclosure"], absence)
        report["references"].append({"id": r["_qid"], "level": r["level"], "ok": ok, "state": state,
                                     "attribute": r["context"], "detail": detail})
    for iface in interfaces:
        rows = []
        for r in profile.get("interfaceRules", []):
            ok, state, detail = check_interface_rule(iface, r, profile, registry, product)
            rows.append({"id": r["_qid"], "level": r["level"], "attribute": r["attribute"],
                         "ok": ok, "state": state, "detail": detail})
        for r in profile.get("referenceRules", []):
            if r["at"] != "interface":
                continue
            applies, why = reference_applies(r, product, iface)
            if not applies:
                rows.append({"id": r["_qid"], "level": r["level"], "attribute": r["context"], "ok": True,
                             "state": "n/a", "detail": "not applicable (%s)" % why})
                continue
            ok, state, detail = check_reference(r, profile, refs_of(iface["_element"]),
                                                iface["_disclosure"], {})
            rows.append({"id": r["_qid"], "level": r["level"], "attribute": r["context"],
                         "ok": ok, "state": state, "detail": detail})
        report["interfaces"].append({"interfaceId": iface["interfaceId"],
                                     "interfaceType": iface.get("interfaceType"),
                                     "conforms": all(x["ok"] for x in rows if x["level"] == "MUST"),
                                     "rows": rows})
    must_ok = all(x["ok"] for x in report["product"] + report["references"] if x["level"] == "MUST") \
        and all(i["conforms"] for i in report["interfaces"])
    return ("conforms" if must_ok else "does-not-conform"), report


def failed_musts(report):
    out = ["%s" % x["id"] for x in report["product"] + report["references"]
           if x["level"] == "MUST" and not x["ok"]]
    for i in report["interfaces"]:
        out += ["%s/%s" % (i["interfaceId"], x["id"]) for x in i["rows"]
                if x["level"] == "MUST" and not x["ok"]]
    return out


def print_report(path, profile, verdict, report, verbose=True):
    print("CBOM    : %s" % os.path.basename(path))
    print("PROFILE : %s v%s (%s)" % (profile["profileId"], profile["version"], " -> ".join(profile["_chain"])))
    mark = lambda r: "PASS" if r["ok"] and r.get("state") != "n/a" else ("-- " if r.get("state") == "n/a" else
                                                                          ("FAIL" if r["level"] == "MUST" else ("WARN" if r["level"] == "SHOULD" else "info")))
    print("-" * 78)
    for r in report["product"] + report["references"]:
        print("  [%s] %-28s %-6s %s" % (mark(r), r["id"], r["level"], r["detail"]))
    for i in report["interfaces"]:
        bad = [r for r in i["rows"] if not r["ok"] or (verbose and r["state"] != "n/a")]
        print("INTERFACE %s (%s) => %s" % (i["interfaceId"], i["interfaceType"],
                                            "ok" if i["conforms"] else "FAILS"))
        for r in i["rows"]:
            if not verbose and r["ok"]:
                continue
            if r["state"] == "n/a":
                continue
            print("  [%s] %-28s %-6s %-20s %s" % (mark(r), r["id"], r["level"], r["attribute"], r["detail"]))
    print("=" * 78)
    fm = failed_musts(report)
    print("VERDICT : %s%s" % ("CONFORMS" if verdict == "conforms" else "DOES NOT CONFORM",
                             "" if not fm else "  (failed MUST: %s)" % ", ".join(fm)))


def main(argv):
    args, withs, i = [], [], 1
    while i < len(argv):
        if argv[i] == "--with":
            withs.append(argv[i + 1])
            i += 2
            continue
        if not argv[i].startswith("--"):
            args.append(argv[i])
        i += 1
    if len(args) != 2:
        print(__doc__)
        return 2
    reg = Registry()
    for w in withs:
        reg.add(w)
    bom = reg.add(args[0])
    try:
        profile, _notes = load_profile(args[1])
    except ProfileError as err:
        print("PROFILE ERROR: %s" % err, file=sys.stderr)
        return 3
    verdict, report = validate(bom, profile, reg)
    if "--json" in argv:
        print(json.dumps({"verdict": verdict, "failed": failed_musts(report)}, indent=2))
    else:
        print_report(args[0], profile, verdict, report, verbose="--quiet" not in argv)
    return 0 if verdict == "conforms" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
