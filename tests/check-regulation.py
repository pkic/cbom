"""Checks the regulatory sufficiency catalogue in regulation/catalogue/.

- Every entry has the required fields, and uses the defined values for
  verdict, levels and checked.
- Every rule an entry cites exists in the profile it names. The rule must be
  defined in that profile's own rules file, not inherited from its base.
- The verdict agrees with the levels: "sufficient" and "deeper-profile" need
  the facts to be expressible and required; "out-of-scope" and "open" stand
  alone; "partial" names a gap.
- regulation/coverage.md is up to date with the catalogue.

Usage: python3 tests/check-regulation.py
"""
import glob, json, os, subprocess, sys
try:
    import yaml
except ImportError:
    print("skipped: PyYAML is not installed")
    sys.exit(0)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VERDICTS = {"sufficient", "deeper-profile", "partial", "judgement", "out-of-scope", "open"}
LEVELS = {"yes", "partly", "no"}
CHECKED = {"primary", "eu-report", "secondary"}

rules = {}
for path in glob.glob(os.path.join(ROOT, "docs", "methodology", "profile-*.rules.json")):
    d = json.load(open(path, encoding="utf8"))
    ids = set()
    for k, v in d.items():
        if k.endswith("Rules") and isinstance(v, list):
            ids |= {r["id"] for r in v}
    rules[d["profileId"]] = ids

fails, n = [], 0
seen = set()
for path in sorted(glob.glob(os.path.join(ROOT, "regulation", "catalogue", "*.yaml"))):
    name = os.path.basename(path)
    d = yaml.safe_load(open(path, encoding="utf8"))
    ins = d.get("instrument", {})
    for f in ("id", "title", "jurisdiction", "kind", "published", "appliesTo", "summary"):
        if f not in ins:
            fails.append(f"{name}: instrument has no {f}")
    if ins.get("id") and ins["id"] + ".yaml" != name:
        fails.append(f"{name}: file name does not match instrument id {ins.get('id')}")
    for q in d.get("questions", []):
        n += 1
        qid = q.get("id", "?")
        where = f"{name} {qid}"
        if qid in seen:
            fails.append(f"{where}: duplicate question id")
        seen.add(qid)
        for f in ("clause", "checked", "question", "levels", "verdict", "rationale"):
            if f not in q:
                fails.append(f"{where}: no {f}")
        v, lv = q.get("verdict"), q.get("levels") or {}
        if v not in VERDICTS:
            fails.append(f"{where}: verdict {v!r} is not one of {sorted(VERDICTS)}")
        if q.get("checked") not in CHECKED:
            fails.append(f"{where}: checked {q.get('checked')!r} is not one of {sorted(CHECKED)}")
        for k in ("expressible", "required", "evaluable"):
            if lv.get(k) not in LEVELS:
                fails.append(f"{where}: level {k} is {lv.get(k)!r}, not one of yes, partly, no")
        for e in q.get("evidence") or []:
            p = e.get("profile")
            if p not in rules:
                fails.append(f"{where}: profile {p} does not exist")
                continue
            for r in e.get("rules", []):
                if r not in rules[p]:
                    fails.append(f"{where}: rule {r} is not defined in {p}")
        if v in ("sufficient", "deeper-profile"):
            if lv.get("expressible") != "yes" or lv.get("required") != "yes":
                fails.append(f"{where}: {v} needs expressible and required to be yes")
            if not q.get("evidence"):
                fails.append(f"{where}: {v} needs evidence")
        if v == "partial" and not q.get("gap"):
            fails.append(f"{where}: a partial verdict must name its gap")
        if v in ("out-of-scope", "open") and q.get("evidence"):
            fails.append(f"{where}: {v} should cite no evidence")

rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_regulatory_coverage.py"), "--check"]).returncode
if rc != 0:
    fails.append("regulation/coverage.md is out of date: run python3 tools/build_regulatory_coverage.py")

for f in fails:
    print("FAIL " + f)
print(f"{n} evidence questions checked: {len(fails)} problems")
sys.exit(1 if fails else 0)
