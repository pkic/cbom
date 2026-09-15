#!/usr/bin/env python3
"""Check the site's interactive demonstration against the reference validator.

The Conformance section says that two tools given the same document, the same
profile and the same resolution of any extended base return the same verdict.
The site has two such tools. `validate_cbom.py` is the reference. `demo.html`
is a second implementation, because a static page cannot run Python, and it
tells readers its results correspond to the reference tool's. Nothing used to
verify that, and the two had already diverged once: when the baseline was
tightened, the page's own copy of the rules had to be edited separately.

The page no longer carries that copy — it fetches the published rules file — so
what is left to check is the part loading a file cannot fix: the evaluation
logic, and the interface records the page displays. This script runs the page's
own functions under Node, over the same four committed CBOMs, and requires:

  * the page holds no transcription of the rules, only the fetch;
  * every interface record it shows is what the reference adapter extracts from
    the CBOM it names;
  * for each document, the same verdict, and the same outcome and disclosure
    state for every rule;
  * the same carrier band for each version in the profile's acceptance range.

A disagreement is a real defect in one of the two, and which one it is has to be
judged case by case: the reference tool is authoritative about the methodology,
but a divergence has twice turned out to be the reference tool's own.

Skips with a message rather than failing when Node is not installed, so that a
contributor without it can still run the rest of the suite.

Usage:  python tests/check-demo.py
Exit:   0 they agree (or skipped), 1 a disagreement, 2 something was unreadable
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")
DEMO = os.path.join(M, "demo.html")
BASE = os.path.join(M, "profile-interface-disclosure.rules.json")

# The attributes the page displays and evaluates. 'nm' and 'via' are for the
# card at the top of the page and are not profile attributes, so they are not
# compared; everything else has to be what the adapter produced.
COMPARED = ("interfaceId", "interfaceType", "protocol", "protocolVersion",
            "keyExchange", "encryption", "authentication", "endpointRoles",
            "lifecycleStage", "implementationPurl", "_disclosure")

# Each band in the profile's acceptance range, and the version that lands in it.
BANDS = {"1.5": "refused", "1.6": "legacy", "1.7": "target", "1.8": "newer"}
REFERENCE_BAND = {"unsupported-version": "refused", "legacy": "legacy",
                  "target": "target", "newer": "newer"}

HARNESS = r"""
// Runs demo.html's own script in Node and reports what it decides.
//
// The page is written for a browser: it reaches for document and fetch, and it
// loads the rules over HTTP. Both are stubbed here — fetch reads from the
// methodology directory, and the document is a sink — so that the functions
// under test are the ones the published page runs, not a copy of them.
const fs = require("fs");
const path = require("path");
const [, , demoPath, methodologyDir] = process.argv;

const html = fs.readFileSync(demoPath, "utf8");
const blocks = html.match(/<script>[\s\S]*?<\/script>/g) || [];
const script = blocks.filter(b => b.includes("RULES_URL"));
if (script.length !== 1) {
  console.error("expected exactly one script block using RULES_URL, found " + script.length);
  process.exit(2);
}
const source = script[0].replace(/^<script>/, "").replace(/<\/script>$/, "");

function element() {
  return {innerHTML: "", textContent: "", className: "", style: {},
          classList: {add() {}, remove() {}}, children: [],
          addEventListener() {}};
}
const sink = {};
const document = {
  getElementById(id) { return (sink[id] = sink[id] || element()); },
  querySelectorAll() { return []; },
};
async function fetch(url) {
  const file = path.join(methodologyDir, url);
  if (!fs.existsSync(file)) return {ok: false, status: 404};
  const text = fs.readFileSync(file, "utf8");
  return {ok: true, status: 200, json: async () => JSON.parse(text)};
}

const run = new Function("document", "fetch", "module",
                         source + "\n;return module.exports;");
const demo = run(document, fetch, {exports: {}});

(async () => {
  await demo.READY;
  const profile = demo.profile();
  if (!profile) { console.error("the page did not load the rules file"); process.exit(2); }
  const tag = profile.profileTag;
  const qid = id => tag + "#" + id;

  const documents = {};
  for (const variant of Object.keys(demo.DOCUMENTS)) {
    const res = demo.validate(demo.CBOMS[variant], demo.PRODUCTS[variant]);
    documents[variant] = {
      file: demo.DOCUMENTS[variant],
      verdict: res.conforms ? "conforms" : "does-not-conform",
      product: res.product.map(r => ({id: qid(r.id), level: r.level, ok: r.ok})),
      interfaces: res.interfaces.map(i => ({
        interfaceId: i.iface.interfaceId,
        conforms: i.conforms,
        rows: i.rows.map(r => ({id: qid(r.id), level: r.level, attribute: r.attribute,
                                ok: r.ok, state: r.state})),
      })),
      // What the page displays for each interface, to be held against what the
      // reference adapter extracts from the document named above.
      shown: demo.CBOMS[variant].map(f => {
        const out = {};
        for (const k of Object.keys(f)) out[k] = f[k];
        return out;
      }),
      subject: demo.PRODUCTS[variant],
    };
  }

  const bands = {};
  for (const v of ["1.5", "1.6", "1.7", "1.8"]) {
    const b = demo.band(v);
    bands[v] = {band: b.k, evaluate: b.evaluate};
  }

  console.log(JSON.stringify({profileVersion: profile.version,
                              profileTag: tag, documents, bands}));
})().catch(err => { console.error(String(err && err.stack || err)); process.exit(2); });
"""


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_cbom", os.path.join(M, "validate_cbom.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_harness(node: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        harness = os.path.join(tmp, "harness.js")
        with open(harness, "w", encoding="utf-8") as fh:
            fh.write(HARNESS)
        proc = subprocess.run([node, harness, DEMO, M], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("the demonstration page could not be run:\n%s"
                           % (proc.stderr.strip() or proc.stdout.strip()))
    return json.loads(proc.stdout)


def main() -> int:
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        print("SKIP  Node is not installed; the demonstration page was not checked")
        print("      against validate_cbom.py. Install Node to enable it.")
        return 0

    failures = 0

    def ok(label):
        print("  ok   %s" % label)

    def bad(label, detail):
        nonlocal failures
        failures += 1
        print("  FAIL %s\n     %s" % (label, detail))

    # The page must not carry its own statement of the rules. This is what drifted
    # before, and it drifts silently: a transcription that is merely out of date
    # still renders a complete, plausible page.
    with open(DEMO, encoding="utf-8") as fh:
        demo_source = fh.read()
    copied = [key for key in ("productRules:", "interfaceRules:", "appliesTo:",
                              "coverageVocabulary:", "interfaceTypeVocabulary:")
              if re.search(r"\n\s*" + re.escape(key), demo_source)]
    if copied:
        bad("the page holds no copy of the rules",
            "demo.html declares %s, which belongs to the rules file. The page is "
            "meant to fetch it." % ", ".join(copied))
    else:
        ok("the page holds no copy of the rules")

    try:
        v = load_validator()
        result = run_harness(node)
    except Exception as err:                                  # noqa: BLE001
        print("  FAIL the demonstration page could not be evaluated\n     %s" % err)
        return 2

    profile, _origin, _notes = v.load_profile(BASE)

    if result["profileVersion"] == str(profile["version"]):
        ok("the page evaluates against profile v%s, the published version"
           % result["profileVersion"])
    else:
        bad("the page evaluates against the published profile version",
            "the page reports v%s, the rules file says v%s"
            % (result["profileVersion"], profile["version"]))

    for variant, shown in sorted(result["documents"].items()):
        path = os.path.join(M, shown["file"])
        if not os.path.exists(path):
            bad("%s names a committed document" % variant,
                "the page names %s, which is not in docs/methodology/" % shown["file"])
            continue
        with open(path, encoding="utf-8") as fh:
            bom = json.load(fh)

        # 1. What the page displays is what the adapter extracts.
        extracted = v.extract_interfaces(bom)
        product = v.extract_product(bom)
        problems = []
        if len(extracted) != len(shown["shown"]):
            problems.append("the page shows %d interface(s), the document has %d"
                            % (len(shown["shown"]), len(extracted)))
        for page_iface, real in zip(shown["shown"], extracted):
            for key in COMPARED:
                a, b = page_iface.get(key), real.get(key)
                if key == "_disclosure":
                    a, b = a or {}, b or {}
                if a != b:
                    problems.append("%s: %s is %r on the page, %r in %s"
                                    % (page_iface.get("interfaceId"), key, a, b, shown["file"]))
        if shown["subject"].get("identifier") != product.get("identifier"):
            problems.append("subject is %r on the page, %r in %s"
                            % (shown["subject"].get("identifier"),
                               product.get("identifier"), shown["file"]))
        if shown["subject"].get("attrs") != product.get("attrs"):
            problems.append("product attributes are %r on the page, %r in %s"
                            % (shown["subject"].get("attrs"), product.get("attrs"),
                               shown["file"]))
        if problems:
            bad("%s shows what %s contains" % (variant, shown["file"]),
                "\n     ".join(problems))
        else:
            ok("%s shows what %s contains" % (variant, shown["file"]))

        # 2. The same verdict, rule by rule.
        verdict, report = v.validate(bom, profile)
        if verdict != shown["verdict"]:
            bad("%s: same verdict as the reference tool" % variant,
                "the page says %s, validate_cbom.py says %s" % (shown["verdict"], verdict))
            continue

        reference = {r["id"]: (r["ok"], None) for r in report["product"]}
        for iface in report["interfaces"]:
            for row in iface["rows"]:
                reference[(iface["interfaceId"], row["id"])] = (row["ok"], row["state"])

        problems = []
        for row in shown["product"]:
            want = reference.get(row["id"])
            if want is None:
                problems.append("%s is evaluated by the page and not by the tool" % row["id"])
            elif want[0] != row["ok"]:
                problems.append("%s: page says %s, tool says %s"
                                % (row["id"], "pass" if row["ok"] else "fail",
                                   "pass" if want[0] else "fail"))
        for iface in shown["interfaces"]:
            for row in iface["rows"]:
                key = (iface["interfaceId"], row["id"])
                want = reference.get(key)
                if want is None:
                    problems.append("%s/%s is evaluated by the page and not by the tool"
                                    % key)
                    continue
                if want[0] != row["ok"]:
                    problems.append("%s/%s: page says %s, tool says %s"
                                    % (key + ("pass" if row["ok"] else "fail",
                                              "pass" if want[0] else "fail")))
                # T2: withheld, unknown and undeclared are three different
                # statements to a consumer, and a page that renders one as
                # another misleads even when the verdict agrees.
                if want[1] != row["state"]:
                    problems.append("%s/%s: page reports the value %s, tool reports it %s"
                                    % (key + (row["state"], want[1])))
        unseen = len(reference) - (len(shown["product"])
                                  + sum(len(i["rows"]) for i in shown["interfaces"]))
        if unseen:
            problems.append("the tool assesses %d rule(s) the page does not show" % unseen)
        if problems:
            bad("%s: same outcome for every rule" % variant, "\n     ".join(problems))
        else:
            ok("%s: same outcome for every rule (%d rules)"
               % (variant, len(reference)))

    # 3. The same carrier band in each direction from the tested version.
    problems = []
    with open(os.path.join(M, "cbom-pass.cyclonedx.json"), encoding="utf-8") as fh:
        carrier_bom = json.load(fh)
    for version, expected in sorted(BANDS.items()):
        carrier_bom["specVersion"] = version
        fmt = v.check_format(carrier_bom, profile)
        reference_band = REFERENCE_BAND.get(fmt["status"], fmt["status"])
        page = result["bands"][version]
        if page["band"] != reference_band:
            problems.append("CycloneDX %s: page says %s, tool says %s"
                            % (version, page["band"], reference_band))
        elif page["band"] != expected:
            problems.append("CycloneDX %s: both say %s, the test expected %s; the "
                            "profile's acceptance range has moved"
                            % (version, page["band"], expected))
        if page["evaluate"] != fmt["ok"]:
            problems.append("CycloneDX %s: the page does%s evaluate, the tool does%s"
                            % (version, "" if page["evaluate"] else " not",
                               "" if fmt["ok"] else " not"))
    if problems:
        bad("the same carrier band, and the same decision to evaluate",
            "\n     ".join(problems))
    else:
        ok("the same carrier band, and the same decision to evaluate (%d versions)"
           % len(BANDS))

    print("  %s" % ("the demonstration agrees with the reference tool" if not failures
                    else "%d disagreement(s) between the page and the reference tool"
                         % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
