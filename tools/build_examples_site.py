#!/usr/bin/env python3
"""Generate the data behind the examples gallery (docs/methodology/examples.html) and the record
viewer (docs/methodology/example.html).

Writes docs/methodology/gallery/index.json, which lists every example by story, and one file per
example under docs/methodology/gallery/, which holds what the viewer shows: the subject, each
interface with its attributes, the capability-by-purpose grid, the validator's report for each
profile the example is tested against, and, for a failure variant, the difference from the record
it was derived from and how to fix it.

Everything comes from the test cases in tests/check-examples.py and tests/check-draft-examples.py
and from validate_cbom.py itself, so the pages show only verdicts the test suite confirms.

Usage:  python3 tools/build_examples_site.py           write the data
        python3 tools/build_examples_site.py --check   exit 1 if the committed data is out of date
"""
import collections
import glob
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
EX = os.path.join(M, "examples")
OUT = os.path.join(M, "gallery")
REPO = "https://github.com/pkic/cbom/blob/main/"
P = "pkic:profile:"
sys.path.insert(0, M)
import validate_cbom as V  # noqa: E402

PURPOSES = ["key-establishment", "encryption", "entity-authentication", "data-integrity",
            "non-repudiation", "key-protection", "key-derivation"]

# Stories, in the order the gallery shows them. The first pattern that matches a file decides its
# story. 'domain' feeds the gallery's filter.
STORIES = [
    ("openssh", "OpenSSH: post-quantum key exchange shipped, deployed, then drifted", "Generic",
     "The OpenSSH 10.0p2 product record shows hybrid ML-KEM key exchange on by default and signatures "
     "still classical. An operator then configures a bastion to allow only post-quantum key exchange, and "
     "a scan a week later finds a classical method back in the list.",
     [r"openssh", r"bastion"]),
    ("examplegate", "ExampleGate: post-quantum by software update (fictional)", "Generic",
     "One VPN gateway in two releases. In 4.2.0 post-quantum key exchange is promised for the next "
     "release. In 4.3.0 it is there, switched on by configuration, but outside the FIPS 140-3 validated "
     "boundary. The operator's record then requires it.",
     [r"examplegate", r"vpn-deployment"]),
    ("remote-admin", "Remote administration: a system that waits on its CA", "Generic",
     "An integrator's design joining the VPN gateway and the SSH bastion. Every interface names what "
     "provides its keys, which shows that the enterprise CA and the administrators' security keys hold "
     "back post-quantum authentication for the whole design.",
     [r"remote-admin"]),
    ("keycloak", "Keycloak: one product at every stage", "Generic",
     "The methodology's main worked example. The same identity server as built, as intended, as "
     "configured, as observed, and as a managed service, with the database at the far end of one "
     "connection.",
     [r"keycloak", r"postgres"]),
    ("substation", "Substation automation", "Operational technology",
     "A protection IED, the IEC 60870-5-104 library a gateway embeds, and the substation system an "
     "integrator delivers from them.",
     [r"ot-", r"lib60870", r"libiec61850", r"sas-reference"]),
    ("iot", "Soil sensors", "IoT",
     "Two field sensors. One can never be updated; the other can.",
     [r"iot-sensor"]),
    ("hsm", "Hardware security modules", "HSMs and key management",
     "A payment HSM written against the draft HSM profiles, and a real HSM described from its public "
     "documentation.",
     [r"hsm", r"luna"]),
    ("payments", "Managed payment cryptography", "Financial services",
     "A managed payment HSM service, described from its public documentation.",
     [r"payment-cryptography"]),
    ("telecom", "5G roaming interconnect", "Telecommunications",
     "A SEPP network function as a product and as deployed, and the roaming interconnect a service "
     "assurance record describes.",
     [r"sepp", r"roaming"]),
]

DOMAIN_OF_DRAFT = {"saas-services": "SaaS and cloud services"}


def load_tests(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tests", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def ident(path):
    r = rel(path)
    if r.startswith("docs/methodology/examples/"):
        r = r[len("docs/methodology/examples/"):]
    return re.sub(r"[^A-Za-z0-9.-]+", "--", r.replace(".cdx.json", ""))


def raw_link(path):
    r = rel(path)
    if r.startswith("docs/methodology/"):
        return r[len("docs/methodology/"):]
    return REPO + r


# ---------------------------------------------------------------- cases ---
def collect():
    """Every (document, profile path, cited paths, expected) the two test files check."""
    out = []
    ce = load_tests("check-examples")
    for doc, tag, withs, expected in ce.CASES:
        out.append((os.path.join(EX, doc), os.path.join(M, "profile-%s.rules.json" % tag),
                    [os.path.join(EX, w) for w in withs], expected))
    cd = load_tests("check-draft-examples")
    for doc, prof, withs, expected in cd.CASES:
        out.append((doc, prof, list(withs), expected))
    return out


# --------------------------------------------------------------- profiles ---
_PROFILES = {}


def profile(path):
    if path not in _PROFILES:
        _PROFILES[path] = V.load_profile(path)[0]
    return _PROFILES[path]


def rule_index():
    """'pqc-migration#I4' -> description and vocabulary, from every profile file in the repository."""
    idx = {}
    files = glob.glob(os.path.join(M, "profile-*.rules.json")) + glob.glob(os.path.join(ROOT, "drafts", "*",
                                                                                         "profile-*.rules.json"))
    for f in files:
        p = json.load(open(f, encoding="utf-8"))
        tag = p.get("profileTag")
        for sec in ("productRules", "interfaceRules", "referenceRules", "groupRules"):
            for r in p.get(sec, []) or []:
                if not isinstance(r, dict) or not r.get("id"):
                    continue
                vocab = None
                ref = (r.get("constraint") or {}).get("enumRef")
                if ref and isinstance(p.get(ref), list):
                    vocab = p[ref]
                text = r.get("description") or (
                    "Every interface it applies to states %s" % r["attribute"] if r.get("attribute") else
                    "Points to %s" % r["context"] if r.get("context") else r["id"])
                idx.setdefault("%s#%s" % (tag, r["id"]), {"text": text, "attribute": r.get("attribute"),
                                                          "level": r.get("level"), "vocabulary": vocab,
                                                          "note": r.get("note", "")})
    return idx


# ----------------------------------------------------------------- records ---
def subject_of(bom):
    if "inventories" in bom:
        return bom["inventories"][0]["subject"], bom["inventories"][0].get("components", [])
    return bom["metadata"].get("component", {}), bom.get("components", [])


def pmap(props_):
    out = collections.OrderedDict()
    for p in props_ or []:
        if p.get("name", "").startswith(P):
            out.setdefault(p["name"][len(P):], []).append(p.get("value"))
    return out


def stage_of(bom):
    phases = [l.get("phase") for l in bom.get("metadata", {}).get("lifecycles", [])]
    return ", ".join(sorted({V.PHASE_TO_STAGE.get(p, p) for p in phases if p})) or "unstated"


def interfaces(bom):
    subj, comps = subject_of(bom)
    provided = {}
    for d in bom.get("dependencies", []) or []:
        for r in d.get("provides", []) or []:
            provided.setdefault(r, []).append(d["ref"])
    byref = {c.get("bom-ref"): c for c in comps}
    out = []
    for c in comps:
        own = pmap(c.get("properties"))
        if "interfaceType" not in own:
            continue
        attrs = [{"name": k, "values": v} for k, v in own.items() if not k.startswith("capabilityByPurpose:")]
        grid = {}
        sources = [(None, own)] + [(src, pmap(byref.get(src, {}).get("properties"))) for src in provided.get(
            c["bom-ref"], [])]
        for src, pm in sources:
            for k, v in pm.items():
                if k.startswith("capabilityByPurpose:"):
                    _, purpose, field = k.split(":", 2)
                    cell = grid.setdefault(purpose, {})
                    cell.setdefault(field, v[0])
                    if src:
                        cell.setdefault("from", src)
                elif src and k not in own:
                    attrs.append({"name": k, "values": v, "from": src})
        out.append({"ref": c["bom-ref"], "name": c.get("name", c["bom-ref"]), "type": own["interfaceType"][0],
                    "attributes": attrs, "purposes": grid, "endpoints": c.get("endpoints", [])})
    return out


def components(bom):
    """Components that are not interfaces: libraries, key providers, certificate authorities."""
    _, comps = subject_of(bom)
    out = []
    for c in comps:
        if "interfaceType" in pmap(c.get("properties")) or c.get("type") == "cryptographic-asset":
            continue
        out.append({"ref": c.get("bom-ref"), "type": c.get("type"), "name": c.get("name", ""),
                    "version": c.get("version", ""), "description": c.get("description", "")})
    return out


def references(bom):
    out = []
    for r in bom.get("externalReferences", []) or []:
        pm = pmap(r.get("properties"))
        out.append({"context": (pm.get("context") or [r.get("type")])[0], "type": r.get("type"),
                    "url": r.get("url"), "comment": r.get("comment", ""), "hashed": bool(r.get("hashes"))})
    return out


# ------------------------------------------------------------------ reports ---
STATE = {"value": "pass", "withheld": "held", "unknown": "unkn", "undeclared": "none", "open": "open"}


def compact(report):
    def row(r):
        if r.get("detail", "").startswith("not applicable"):
            st = "na"
        elif r["ok"]:
            st = STATE.get(r.get("state"), "pass") if r.get("state") in ("withheld", "unknown", "open") else "pass"
        else:
            st = "fail" if r["level"] == "MUST" else "warn"
        label = r.get("description") or r.get("attribute") or ""
        return [st, r["level"], r["id"], label, (r.get("detail") or "")[:400]]
    def rows(rs):
        # Rows that do not apply are counted, not listed: they carry no information beyond the guard.
        out = [row(r) for r in rs]
        return [r for r in out if r[0] != "na"], sum(1 for r in out if r[0] == "na")

    ifaces = []
    for i in report["interfaces"]:
        kept, na = rows(i["rows"])
        ifaces.append({"id": i["interfaceId"], "type": i["interfaceType"], "conforms": i["conforms"],
                       "rows": kept, "notApplicable": na})
    return {"product": rows(report["product"])[0], "references": rows(report["references"])[0],
            "interfaces": ifaces}


def evaluate(doc, prof, withs):
    reg = V.Registry()
    for w in withs:
        reg.add(w)
    bom = reg.add(doc)
    verdict, report = V.validate(bom, profile(prof), reg)
    failing = [r["id"] for r in report["product"] + report["references"] if r["level"] == "MUST" and not r["ok"]]
    for i in report["interfaces"]:
        failing += ["%s/%s" % (i["interfaceId"], r["id"]) for r in i["rows"] if r["level"] == "MUST" and not r["ok"]]
    return verdict, failing, compact(report)


# -------------------------------------------------------------------- diffs ---
def flatten(bom):
    """Comparable facts: one entry per property of the subject, of each component, and per reference."""
    subj, comps = subject_of(bom)
    out = {}
    for k, v in pmap(subj.get("properties")).items():
        out[("subject", k)] = v
    for c in comps:
        out[(c.get("bom-ref"), "(component)")] = [c.get("name", "")]
        for k, v in pmap(c.get("properties")).items():
            out[(c.get("bom-ref"), k)] = v
    for r in bom.get("externalReferences", []) or []:
        ctx = (pmap(r.get("properties")).get("context") or [r.get("type")])[0]
        key = ("document", "%s %s" % (ctx, r.get("url")))
        out[key] = ["digest " + h["content"][:12] + "…" for h in r.get("hashes", [])] or ["no digest"]
    return out


def diff(base, variant):
    a, b = flatten(base), flatten(variant)
    out = []
    for key in list(a) + [k for k in b if k not in a]:
        if a.get(key) != b.get(key):
            out.append({"where": key[0], "attribute": key[1], "before": a.get(key), "after": b.get(key)})
    return out


def fix_text(change, rules):
    where, attr = change["where"], change["attribute"]
    vocab = next((r["vocabulary"] for r in rules if r.get("attribute") == attr and r.get("vocabulary")), None)
    choose = " Use one of: %s." % ", ".join(vocab) if vocab else ""
    if attr == "(component)" and change["after"] is None:
        return "Declare %s again, or state why the subject has none." % where
    if where == "document":
        if change["after"] is None:
            return "Point to the %s again." % attr.split(" ")[0]
        return "Cite the record with the digest of the revision you actually used, and include the digest."
    if change["after"] is None:
        return "State %s on %s.%s" % (attr, where, choose)
    if change["before"] is None:
        return "Remove %s from %s." % (attr, where)
    return "Replace %s on %s with a valid value.%s" % (attr, where, choose)


# --------------------------------------------------------------------- build ---
def story_of(path):
    name = os.path.basename(path)
    for sid, *_rest, patterns in STORIES:
        if any(re.search(p, name) for p in patterns):
            return sid
    return "other"


def domain_of(path, story):
    r = rel(path)
    for key, dom in DOMAIN_OF_DRAFT.items():
        if "/" + key + "/" in "/" + r:
            return dom
    return next((s[2] for s in STORIES if s[0] == story), "Generic")


# Variants whose name does not start with their base's name.
BASES = {"cbom-keycloak-service-fail-custody.cdx.json": "cbom-keycloak-service-restricted.cdx.json",
         "cbom-open5gs-sepp-fail-referencepoint.cdx.json": "cbom-open5gs-sepp-2.8.0-product.cdx.json",
         "cbom-roaming-interconnect-fail-proxy.cdx.json": "cbom-roaming-interconnect-system.cdx.json",
         "cbom-roaming-interconnect-fail-service.cdx.json": "cbom-roaming-interconnect-system.cdx.json"}


def base_of(path, known):
    name = os.path.basename(path)
    if name in BASES:
        return next((k for k in known if os.path.basename(k) == BASES[name]), None)
    if "-fail-" not in name:
        return None
    cand = os.path.join(os.path.dirname(path), name.split("-fail-")[0] + ".cdx.json")
    if cand in known:
        return cand
    # Some draft variants are derived from a published record.
    stem = name.split("-fail-")[0]
    for k in known:
        if os.path.basename(k) == stem + "-configured.cdx.json" or os.path.basename(k) == stem + ".cdx.json":
            return k
    return None


def build():
    rules = rule_index()
    cases = collect()
    docs = collections.OrderedDict()
    for doc, prof, withs, expected in cases:
        if expected is None:
            continue
        docs.setdefault(doc, []).append((prof, withs, expected))
    records, index = {}, []
    for doc, runs in docs.items():
        bom = json.load(open(doc, encoding="utf-8"))
        subj, _ = subject_of(bom)
        sp = pmap(subj.get("properties"))
        story = story_of(doc)
        # One evaluation per profile: the one with the most cited records supplied.
        best = {}
        for prof, withs, expected in runs:
            if prof not in best or len(withs) > len(best[prof][0]):
                best[prof] = (withs, expected)
        profiles = []
        for prof, (withs, expected) in best.items():
            verdict, failing, report = evaluate(doc, prof, withs)
            tag = profile(prof).get("profileTag")
            draft = rel(prof).startswith("drafts/")
            profiles.append({"tag": tag, "title": profile(prof).get("title", tag),
                             "version": profile(prof).get("version"), "draft": draft,
                             "verdict": verdict, "failing": failing,
                             "gapAnalysis": isinstance(expected, tuple),
                             "with": [os.path.basename(w) for w in withs], "report": report})
        comment = bom.get("$comment", "")
        fictional = "FICTIONAL" in comment or "fictional" in json.dumps(subj.get("parties", [])).lower() or \
                    "illustrative" in (subj.get("name", "") + comment[:200]).lower()
        rec = {"id": ident(doc), "file": os.path.basename(doc), "raw": raw_link(doc), "story": story,
               "domain": domain_of(doc, story), "draft": rel(doc).startswith("drafts/"),
               "name": subj.get("name", ""), "version": subj.get("version", ""),
               "description": subj.get("description", ""), "comment": comment,
               "subjectType": (sp.get("subjectType") or [""])[0], "stage": stage_of(bom),
               "coverage": (sp.get("coverage") or [""])[0], "fictional": fictional,
               "subjectFacts": [{"name": k, "values": v} for k, v in sp.items()
                                if k not in ("subjectType", "coverage")],
               "identifier": next((i.get("value") for idn in subj.get("identifiers", [])
                                   for i in idn.get("identities", [])), ""),
               "interfaces": interfaces(bom), "references": references(bom), "profiles": profiles,
               "serial": bom.get("serialNumber", ""), "components": components(bom)}
        records[doc] = rec
    for doc, rec in records.items():
        base = base_of(doc, records)
        rec["variant"] = None
        if base:
            changes = diff(json.load(open(base, encoding="utf-8")), json.load(open(doc, encoding="utf-8")))
            broken = sorted({f.split("/")[-1] for p in rec["profiles"] for f in p["failing"]})
            brk = [dict(id=b, **rules.get(b, {"text": b})) for b in broken]
            m = re.search(r"It breaks one thing: (.*?)\. Everything else", rec["comment"])
            rec["variant"] = {"base": records[base]["id"], "baseName": records[base]["file"],
                              "what": m.group(1) if m else "", "changes": changes, "rules": brk,
                              "fix": [fix_text(c, brk) for c in changes]}
        index.append({k: rec[k] for k in ("id", "file", "raw", "story", "domain", "draft", "name", "version",
                                         "subjectType", "stage", "fictional")} | {
            "variant": bool(rec["variant"]), "base": rec["variant"]["base"] if rec["variant"] else None,
            "breaks": rec["variant"]["what"] if rec["variant"] else "",
            "profiles": [{"tag": p["tag"], "verdict": p["verdict"], "draft": p["draft"],
                          "failing": sorted({f.split("/")[-1] for f in p["failing"]}),
                          "gapAnalysis": p["gapAnalysis"]} for p in rec["profiles"]]})
    # A BOM-Link names a record by serial number; this lets the viewer turn one into a link.
    serials = {}
    for rec in records.values():
        if rec["serial"] and not rec["variant"]:
            serials.setdefault(rec["serial"][len("urn:uuid:"):], rec["id"])
    stories = [{"id": s[0], "title": s[1], "domain": s[2], "blurb": s[3]} for s in STORIES]
    if any(i["story"] == "other" for i in index):
        stories.append({"id": "other", "title": "Other examples", "domain": "Generic", "blurb": ""})
    return {"stories": stories, "examples": index, "serials": serials}, records


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n"


def outputs():
    idx, records = build()
    files = {os.path.join(OUT, "index.json"): dump(idx)}
    for rec in records.values():
        files[os.path.join(OUT, rec["id"] + ".json")] = dump(rec)
    return files


def main():
    files = outputs()
    if "--check" in sys.argv:
        stale = [f for f, text in files.items()
                 if not os.path.exists(f) or open(f, encoding="utf-8").read() != text]
        extra = [f for f in glob.glob(os.path.join(OUT, "*.json")) if f not in files]
        if stale or extra:
            print("the gallery data is out of date (%d stale, %d extra): run python3 tools/build_examples_site.py"
                  % (len(stale), len(extra)))
            return 1
        print("the gallery data is up to date (%d files)" % len(files))
        return 0
    os.makedirs(OUT, exist_ok=True)
    for f, text in files.items():
        with open(f, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    print("written %d files to %s (%d KB)" % (len(files), rel(OUT),
                                              sum(len(t.encode()) for t in files.values()) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
