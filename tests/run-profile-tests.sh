#!/usr/bin/env bash
# Profile and validator tests for the CBOM Profiles methodology.
#
# Checks that the published example artifacts still behave as the documentation
# says they do. Run locally with:
#
#     bash tests/run-profile-tests.sh
#
# CI runs the same script on any change under docs/methodology/.
# Exit status is 0 when every test passes, 1 otherwise.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
M="$ROOT/docs/methodology"
FIX="$ROOT/tests/fixtures"
PY="${PYTHON:-python3}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

BASE="$M/profile-interface-disclosure.rules.json"
PQC="$M/profile-pqc-migration.rules.json"
EXT="$M/profile-pqc-migration-extended.rules.json"
DEPL="$M/profile-deployment-disclosure.rules.json"
PROC="$M/profile-procurement.rules.json"

# The worked example is Keycloak 26.7.3. Examples are CycloneDX 2.0 unless they
# sit under examples/legacy, which holds CycloneDX 1.7 documents.
EX="$M/examples"
PROD="$EX/cbom-keycloak-product.cdx.json"
LEGACY="$EX/legacy/cbom-keycloak-product-1.7.cdx.json"
FAILP2="$EX/cbom-keycloak-product-fail-P2.cdx.json"
STATES="$EX/cbom-keycloak-product-disclosure-states.cdx.json"
PQCFAIL="$EX/cbom-keycloak-product-fail-pqc-I12.cdx.json"
SCANNER="$EX/legacy/cbom-keycloak-scanner-output.cdx.json"
INTENDED="$EX/cbom-keycloak-product-intended.cdx.json"
CONF="$EX/cbom-keycloak-deployment-configured.cdx.json"
OBS="$EX/cbom-keycloak-deployment-observed.cdx.json"

passed=0
failed=0

ok()   { printf '  ok   %s\n' "$1"; passed=$((passed + 1)); }
bad()  { printf '  FAIL %s\n     %s\n' "$1" "$2"; failed=$((failed + 1)); }

# validate <cbom> <profile> -> writes output to $OUT, sets $RC
validate() {
  OUT="$("$PY" "$M/validate_cbom.py" "$@" 2>&1)"
  RC=$?
}

# expect_exit <label> <expected-rc> <cbom> <profile>
expect_exit() {
  local label=$1 want=$2 cbom=$3 prof=$4
  shift 4
  validate "$cbom" "$prof" "$@"
  if [ "$RC" -eq "$want" ]; then
    ok "$label"
  else
    bad "$label" "expected exit $want, got $RC$(printf '\n     %s' "$(echo "$OUT" | tail -3)")"
  fi
}

# expect_output <label> <needle> <cbom> <profile>
expect_output() {
  local label=$1 needle=$2 cbom=$3 prof=$4
  shift 4
  validate "$cbom" "$prof" "$@"
  if printf '%s' "$OUT" | grep -q -- "$needle"; then
    ok "$label"
  else
    bad "$label" "output did not contain: $needle"
  fi
}

# expect_output_fixed <label> <literal-needle> <cbom> <profile>
# Qualified group member ids such as pqc-migration#G1.2[key-establishment]
# contain [ and ].
expect_output_fixed() {
  local label=$1 needle=$2 cbom=$3 prof=$4
  shift 4
  validate "$cbom" "$prof" "$@"
  if printf '%s' "$OUT" | grep -qF -- "$needle"; then
    ok "$label"
  else
    bad "$label" "output did not contain: $needle"
  fi
}

# checkprof <args...> -> writes output to $OUT, sets $RC
checkprof() {
  OUT="$("$PY" "$M/check_profile.py" "$@" 2>&1)"
  RC=$?
}

# expect_check_exit <label> <expected-rc> <args...>
expect_check_exit() {
  local label=$1 want=$2
  shift 2
  checkprof "$@"
  if [ "$RC" -eq "$want" ]; then
    ok "$label"
  else
    bad "$label" "expected exit $want, got $RC$(printf '\n     %s' "$(echo "$OUT" | tail -3)")"
  fi
}

# expect_check_output <label> <literal-needle> <args...>
# Uses a fixed-string match: the needles here contain [ and ].
expect_check_output() {
  local label=$1 needle=$2
  shift 2
  checkprof "$@"
  if printf '%s' "$OUT" | grep -qF -- "$needle"; then
    ok "$label"
  else
    bad "$label" "output did not contain: $needle"
  fi
}

echo
echo "CBOM profile tests"
echo "=================="

# --------------------------------------------------------------- artifacts ---
echo
echo "Artifacts parse"
for f in "$M"/*.json "$EX"/context/*.json "$EX"/*.json "$EX"/legacy/*.json "$EX"/results/*.json "$M"/policies/*.json "$M"/perspectives/*.json "$FIX"/*.json; do
  if "$PY" -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    ok "valid JSON: $(basename "$f")"
  else
    bad "valid JSON: $(basename "$f")" "does not parse"
  fi
done

# A fixture extending a profile pins its base by exact version, which is the
# behaviour being tested. Bumping a profile version therefore invalidates every
# fixture pinning it, and without this check the breakage surfaces downstream as
# a missing word in some unrelated assertion.
if OUT="$("$PY" "$ROOT/tests/check-fixture-pins.py" "$M" "$FIX" 2>&1)"; then
  ok "fixtures pin the current base versions"
else
  bad "fixtures pin the current base versions" "re-pin these, then re-run:"
  printf '%s\n' "$OUT"
fi

for script in validate_cbom.py check_profile.py evaluate_policy.py compare_stages.py cdx17_to_20.py; do
  if "$PY" -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$M/$script" 2>/dev/null; then
    ok "$script parses"
  else
    bad "$script parses" "syntax error"
  fi
done

# ------------------------------------------------------- baseline profile ---
echo
echo "Baseline profile"
expect_exit   "the Keycloak product record conforms"       0 "$PROD" "$BASE"
expect_output "verdict reads CONFORMS"             "CONFORMS" "$PROD" "$BASE"
expect_output "the stage is read from metadata.lifecycles" "lifecycle phase 'build'" "$PROD" "$BASE"
expect_output "the subject type is declared"   "= 'product'" "$PROD" "$BASE"
expect_exit   "non-conforming CBOM is rejected"            1 "$FAILP2" "$BASE"
expect_output "failure is product rule P2" "interface-disclosure#P2" "$FAILP2" "$BASE"
expect_output "an interface the product does not fix is 'deployment-defined'" "= 'deployment-defined'" \
              "$PROD" "$BASE"
expect_output "an outcome the peer decides is 'peer-defined'" "= 'peer-defined'" "$PROD" "$BASE"
expect_output "the implementing library is inherited through provides" "provided by lib:openjdk" \
              "$PROD" "$BASE"

# ------------------------------------------------- baseline product rules ---
echo
echo "Baseline product rules"
expect_output "P3 identifies the subject by package URL" "pkg:oci/keycloak" "$PROD" "$BASE"
expect_output "P4 states completeness"   "all-external" "$PROD" "$BASE"

"$PY" - "$PROD" "$TMP" <<'PY'
import json, sys, os
src = sys.argv[1]
def load():
    return json.load(open(src, encoding="utf-8"))
def subject(bom):
    return bom["inventories"][0]["subject"]
def entries(bom):
    return bom["inventories"][0]["components"]
def save(bom, name):
    json.dump(bom, open(os.path.join(sys.argv[2], name), "w"))

bom = load()
subject(bom).pop("identifiers", None)
save(bom, "cbom-unidentified.json")

bom = load()
s = subject(bom)
s["properties"] = [p for p in s["properties"] if p["name"] != "pkic:profile:coverage"]
bom.pop("compositions", None)
save(bom, "cbom-nocoverage.json")

bom = load()
s = subject(bom)
s["properties"] = [p for p in s["properties"] if p["name"] != "pkic:profile:subjectType"]
save(bom, "cbom-nosubjecttype.json")

bom = load()
bom["metadata"].pop("lifecycles", None)
save(bom, "cbom-nostage.json")

# One interface reporting a different stage from the document.
bom = load()
for c in entries(bom):
    if c.get("bom-ref") == "service:svc-oidc":
        c["properties"].append({"name": "pkic:profile:lifecycleStage", "value": "observed"})
save(bom, "cbom-mixedstage.json")

# A subject with no administrative surface: no management interface, and a
# stated reason. Synthetic: Keycloak has one, so this is a test document only.
bom = load()
bom["inventories"][0]["components"] = [c for c in entries(bom)
    if c.get("bom-ref") not in ("service:mgmt-admin", "crypto:protocol:tls-mgmt")]
subject(bom)["properties"].append(
    {"name": "pkic:profile:managementInterfaceAbsence", "value": "no-configuration-surface"})
save(bom, "cbom-noadmin.json")
subject(bom)["properties"] = [p for p in subject(bom)["properties"]
    if p["name"] != "pkic:profile:managementInterfaceAbsence"]
save(bom, "cbom-noadmin-silent.json")

# 'not-reached' is an observer's reason, accepted only on an observed record.
bom = load()
bom["inventories"][0]["components"] = [c for c in entries(bom)
    if c.get("bom-ref") not in ("service:mgmt-admin", "crypto:protocol:tls-mgmt")]
subject(bom)["properties"].append(
    {"name": "pkic:profile:managementInterfaceAbsence", "value": "not-reached"})
save(bom, "cbom-notreached-at-build.json")
PY
expect_exit   "a document that does not say what it describes fails" 1 \
              "$TMP/cbom-unidentified.json" "$BASE"
expect_output "and a name and version are not an identifier" "not a stable identifier" \
              "$TMP/cbom-unidentified.json" "$BASE"
expect_exit   "a document with no completeness statement fails" 1 \
              "$TMP/cbom-nocoverage.json" "$BASE"
expect_exit   "a document that does not declare its subject type fails" 1 \
              "$TMP/cbom-nosubjecttype.json" "$BASE"
expect_output "and the failure is P5" "interface-disclosure#P5" "$TMP/cbom-nosubjecttype.json" "$BASE"
expect_exit   "a document with no lifecycle stage fails" 1 "$TMP/cbom-nostage.json" "$BASE"
expect_output "and the failure is P6" "interface-disclosure#P6" "$TMP/cbom-nostage.json" "$BASE"
expect_exit   "one interface reporting another stage fails" 1 "$TMP/cbom-mixedstage.json" "$BASE"
expect_output "and the report names it" "report another: service:svc-oidc" \
              "$TMP/cbom-mixedstage.json" "$BASE"

# The revised P2. A structural rule is satisfied by presence or by a stated
# absence; silence is neither.
expect_exit   "no management interface, absence stated, conforms" 0 \
              "$TMP/cbom-noadmin.json" "$BASE"
expect_output "and the report says how it was satisfied" "none declared, stated as" \
              "$TMP/cbom-noadmin.json" "$BASE"
expect_exit   "no management interface and no reason does not conform" 1 \
              "$TMP/cbom-noadmin-silent.json" "$BASE"
expect_output "and says the absence was never explained" "no declared reason for the absence" \
              "$TMP/cbom-noadmin-silent.json" "$BASE"
expect_exit   "'not-reached' is refused on a build record" 1 \
              "$TMP/cbom-notreached-at-build.json" "$BASE"
expect_output "because it is accepted only at observed" "accepted only at observed" \
              "$TMP/cbom-notreached-at-build.json" "$BASE"

# ------------------------------------------------------------ carrier bands ---
echo
echo "Carrier version bands"
# CycloneDX 2.0 is the target. 1.6 and 1.7 are read as legacy, through the 1.x
# adapter; a version above the target is accepted with a note; below 1.6 the
# evaluation is refused.
"$PY" - "$LEGACY" "$PROD" "$TMP" <<'PY'
import json, sys, os
legacy = json.load(open(sys.argv[1], encoding="utf-8"))
for v in ("1.6", "1.5"):
    legacy["specVersion"] = v
    json.dump(legacy, open(os.path.join(sys.argv[3], "cbom-%s.json" % v), "w"))
target = json.load(open(sys.argv[2], encoding="utf-8"))
target["specVersion"] = "2.1"
json.dump(target, open(os.path.join(sys.argv[3], "cbom-2.1.json"), "w"))
PY
expect_output "CycloneDX 2.0 is the target"  "(target)" "$PROD" "$BASE"
expect_exit   "a CycloneDX 1.7 record still evaluates"  0 "$LEGACY" "$BASE"
expect_output "and is flagged legacy"         "legacy" "$LEGACY" "$BASE"
expect_exit   "legacy 1.6 still evaluates"         0 "$TMP/cbom-1.6.json" "$BASE"
expect_output "legacy 1.6 is flagged"        "legacy" "$TMP/cbom-1.6.json" "$BASE"
expect_exit   "newer 2.1 still evaluates"          0 "$TMP/cbom-2.1.json" "$BASE"
expect_output "newer 2.1 is flagged"          "newer" "$TMP/cbom-2.1.json" "$BASE"

# Refusal is not failure. The Conformance section makes this a MUST.
expect_exit   "unsupported 1.5 is refused"         4 "$TMP/cbom-1.5.json" "$BASE"
expect_output "refusal explains why"  "older than min" "$TMP/cbom-1.5.json" "$BASE"
expect_output "the verdict reads REFUSED"    "REFUSED" "$TMP/cbom-1.5.json" "$BASE"
expect_output "refusal is not called a failure" "not a failure" \
              "$TMP/cbom-1.5.json" "$BASE"
validate "$TMP/cbom-1.5.json" "$BASE"
if printf '%s' "$OUT" | grep -q 'PRODUCT-LEVEL RULES\|INTERFACE '; then
  bad "no rules are evaluated on refusal" "the report contains rule results"
else
  ok "no rules are evaluated on refusal"
fi
OUT="$("$PY" "$M/validate_cbom.py" "$TMP/cbom-1.5.json" "$BASE" --json 2>&1)"; RC=$?
if [ "$RC" -eq 4 ] && printf '%s' "$OUT" | grep -q '"verdict": "refused"' \
   && printf '%s' "$OUT" | grep -q '"assessed": false'; then
  ok "JSON reports refusal distinctly"
else
  bad "JSON reports refusal distinctly" "expected exit 4, verdict refused, assessed false"
fi

# ------------------------------------------------------ derived PQC profile ---
echo
echo "PQC migration profile (derived)"
expect_exit   "the product record conforms"         0 "$PROD" "$PQC"
expect_output "base profile is resolved"     "extends" "$PROD" "$PQC"
expect_output "inapplicable conditional is skipped" "not applicable" "$PROD" "$PQC"
expect_output "module validation is inherited from the library" "inherited from lib:openjdk" \
              "$PROD" "$PQC"
expect_output "TLS capability is read from cipherSuites" "cipherSuites.tlsGroups" "$PROD" "$PQC"
expect_exit   "non-conforming CBOM is rejected"     1 "$PQCFAIL" "$PQC"
expect_output "the failure is I12"  "pqc-migration#I12" "$PQCFAIL" "$PQC"
expect_output "tightened I9: withholding the library fails here" "interface-disclosure#I9" \
              "$STATES" "$PQC"
expect_exit   "a deployment record is not a product record" 1 "$CONF" "$PQC"
expect_output "and the failure is P5" "outside the subject types this profile accepts" "$CONF" "$PQC"

# --------------------------------------------------- capability per purpose ---
echo
echo "Capability per cryptographic purpose"
expect_output_fixed "status is stated per purpose" \
              "pqc-migration#G1.1[entity-authentication]" "$PROD" "$PQC"
expect_output "one interface holds two different statuses" "= 'committed'" "$PROD" "$PQC"
expect_output_fixed "the blocker is evaluated inside the entry" \
              "pqc-migration#G1.2[entity-authentication]" "$PROD" "$PQC"
expect_output "an available purpose needs no blocker" "not applicable (capabilityStatus='available')" \
              "$PROD" "$PQC"

"$PY" - "$PROD" "$TMP" <<'PY'
import json, sys, os
def load():
    return json.load(open(sys.argv[1], encoding="utf-8"))
def everything(bom):
    return bom["inventories"][0]["components"]
def drop(bom, needle):
    for c in everything(bom):
        c["properties"] = [p for p in c.get("properties", []) if needle not in p.get("name", "")]
bom = load()
drop(bom, ":entity-authentication:")
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-entity-auth.json"), "w"))
bom = load()
for d in ("data-integrity", "non-repudiation", "key-protection", "key-derivation"):
    drop(bom, ":%s:" % d)
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-deferred.json"), "w"))
# The blocker for one purpose, stated once on the library, removed.
bom = load()
for c in everything(bom):
    if c.get("bom-ref") == "lib:openjdk":
        c["properties"] = [p for p in c["properties"]
                           if p["name"] != "pkic:profile:capabilityByPurpose:key-establishment:blockedBy"]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-blocker.json"), "w"))
PY
expect_output_fixed "a missing in-scope purpose is named" "purpose[entity-authentication]" \
              "$TMP/cbom-no-entity-auth.json" "$PQC"
expect_exit   "dropping the deferred purposes breaks conformance" 1 "$TMP/cbom-no-deferred.json" "$PQC"
expect_output "a missing out-of-scope purpose still fails" "no entry for this purpose (status only)" \
              "$TMP/cbom-no-deferred.json" "$PQC"
expect_output "and the baseline is unaffected by any of it" "CONFORMS" "$TMP/cbom-no-deferred.json" "$BASE"
expect_output_fixed "a blocker removed from the library fails on every interface it provides" \
              "tls-https/pqc-migration#G1.2[key-establishment]" "$TMP/cbom-no-blocker.json" "$PQC"

# ------------------------------------------------- accepted lifecycle stages ---
echo
echo "Accepted lifecycle stages"
expect_exit   "a design record fails the baseline"   1 "$INTENDED" "$BASE"
expect_output "the failure is I8" "interface-disclosure#I8" "$INTENDED" "$BASE"
expect_output "the report says the stage is out of scope" "outside the stages this profile accepts" \
              "$INTENDED" "$BASE"
expect_output "and repeating a build-time literal at design fails too" "accepted only at implemented" \
              "$INTENDED" "$BASE"
expect_exit   "the entry profile accepts the same record" 0 "$INTENDED" "$M/profile-interface-enumeration.rules.json"

# ------------------------------------------------------------- composition ---
echo
echo "Composition semantics"
expect_exit   "derived-failing CBOM conforms to the base" 0 "$PQCFAIL" "$BASE"
expect_exit   "relaxing override is rejected"      3 \
              "$PROD" "$FIX/profile-invalid-relaxing.rules.json"
expect_output "rejection names monotonicity" "monotonic" \
              "$PROD" "$FIX/profile-invalid-relaxing.rules.json"

# ---------------------------------------------- withholdable MUST (v0.3) ---
echo
echo "Withholdable MUST"
"$PY" - "$PROD" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
# The OIDC interface withholds its implementing library: the providing link is
# removed and a 'withheld' marker stated.
for d in bom["dependencies"]:
    if "provides" in d:
        d["provides"] = [x for x in d["provides"] if x != "service:svc-oidc"]
for c in bom["inventories"][0]["components"]:
    if c.get("bom-ref") == "service:svc-oidc":
        c["properties"].append({"name": "pkic:profile:disclosure:implementationPurl", "value": "withheld"})
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-withheld.json"), "w"))
for c in bom["inventories"][0]["components"]:
    c["properties"] = [p for p in c.get("properties", [])
                       if p.get("name") != "pkic:profile:disclosure:implementationPurl"]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-marker.json"), "w"))
PY
expect_exit   "a withheld marker satisfies the MUST"       0 "$TMP/cbom-withheld.json" "$BASE"
expect_output "withheld purl reported HELD"            "HELD" "$TMP/cbom-withheld.json" "$BASE"
expect_exit   "silent omission of the same attribute does not" 1 "$TMP/cbom-no-marker.json" "$BASE"
expect_output "the failure is I9" "interface-disclosure#I9" "$TMP/cbom-no-marker.json" "$BASE"
expect_output "reported as undeclared, not withheld" "no disclosure marker" \
              "$TMP/cbom-no-marker.json" "$BASE"

# ------------------------------------------- the four disclosure outcomes ---
echo
echo "Four disclosure outcomes in one document"
expect_exit   "the disclosure document is rejected"        1 "$STATES" "$BASE"
expect_output "withheld is reported HELD, and permitted" "HELD" "$STATES" "$BASE"
expect_output "unknown is reported UNKN, distinctly"    "UNKN" "$STATES" "$BASE"
expect_output "undeclared is reported as such"  "no disclosure marker" "$STATES" "$BASE"
expect_output "the failures are I5 and I4" \
              "int-cache/interface-disclosure#I5, service:svc-saml/interface-disclosure#I4" "$STATES" "$BASE"
expect_output "the interface that withholds still conforms" "service:svc-oidc  (type=service)  ==>  conforms" \
              "$STATES" "$BASE"

# ------------------------------------------------- entry profile and family ---
# The shallowest profile of the interface family. Its reason to exist is that a
# producer who cannot yet satisfy the disclosure baseline is not producing
# nothing, so the case that matters is cbom-fail: the document named for the
# verdict the baseline gives it, conforming here. See decision 0019.
echo
echo "Entry profile and the family ladder"
ENTRY="$M/profile-interface-enumeration.rules.json"
expect_check_exit "entry profile is well-formed"           0 "$ENTRY"
expect_check_exit "and under --strict"                     0 "$ENTRY" --strict
expect_check_output "it declares no forward-looking rules" "orientation 'inventory'" "$ENTRY"
expect_exit   "the baseline's failing document conforms here" 0 "$FAILP2" "$ENTRY"
expect_exit   "so does the one failing on disclosure states" 0 "$STATES" "$ENTRY"
expect_exit   "and the product record that conforms to the baseline" 0 "$PROD" "$ENTRY"
expect_exit   "an observation with a gap lands here" 0 \
              "$EX/cbom-keycloak-deployment-observed-fail-unknown.cdx.json" "$ENTRY" --with "$PROD" --with "$CONF"
expect_exit   "the untargeted scanner output does not"       1 "$SCANNER" "$ENTRY"
expect_output "it declares no interface" "interface-enumeration#P1" "$SCANNER" "$ENTRY"
expect_output "it fails on subject identity" "interface-enumeration#P3" "$SCANNER" "$ENTRY"
expect_output "on completeness" "interface-enumeration#P4" "$SCANNER" "$ENTRY"
expect_output "and on subject type and stage" "interface-enumeration#P6" "$SCANNER" "$ENTRY"
# Rule ids are local to the profile that declares them, so the same rule carries
# the same number at both depths and is cited against a different tag. Decision
# 0011 is what makes that legible rather than ambiguous.
expect_output "a shared rule is cited against this profile's tag" "interface-enumeration#I1" \
              "$PROD" "$ENTRY"
expect_output "and against the baseline's from the baseline" "interface-disclosure#I1" \
              "$PROD" "$BASE"

# The ladder itself: the deeper profile contains the shallower one, and
# conformance carries downwards. The baseline does not declare 'extends' on the
# entry profile, so nothing structural enforces this yet (Q51).
OUT="$("$PY" "$ROOT/tests/check-family.py" 2>&1)"; RC=$?
printf '%s\n' "$OUT" | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then
  passed=$((passed + 1))
else
  failed=$((failed + 1))
fi

# -------------------------------------------------- profile well-formedness ---
# The second conformance target: a profile checked against the methodology.
# Requirements C1 to C17 are stated in the Conformance section.
echo
echo "Profile well-formedness (C1-C18)"
expect_check_output "baseline verdict reads WELL-FORMED" "VERDICT : WELL-FORMED" "$BASE"
for prof in "$M"/profile-*.rules.json; do
  expect_check_exit "$(basename "$prof") is well-formed under --strict" 0 "$prof" --strict
done
expect_check_output "C18 checks the reference rules" "[PASS] C18" "$BASE"

# One fixture per MUST requirement, each failing exactly that requirement.
echo
echo "Each MUST requirement is enforced"
expect_check_exit   "C1 missing objective is rejected"   1 "$FIX/profile-c1-no-objective.rules.json"
expect_check_output "C1 is the failing requirement" "[FAIL] C1" "$FIX/profile-c1-no-objective.rules.json"
expect_check_exit   "C2 missing appliesTo is rejected"   1 "$FIX/profile-c2-no-applies-to.rules.json"
expect_check_output "C2 is the failing requirement" "[FAIL] C2" "$FIX/profile-c2-no-applies-to.rules.json"
expect_check_exit   "C3 instance-naming rule is rejected" 1 "$FIX/profile-c3-names-instance.rules.json"
expect_check_output "C3 is the failing requirement" "[FAIL] C3" "$FIX/profile-c3-names-instance.rules.json"
expect_check_output "C3 names the offending type" "nginx-https" "$FIX/profile-c3-names-instance.rules.json"
expect_check_exit   "C4 unstated withholdability is rejected" 1 "$FIX/profile-c4-no-withholdable.rules.json"
expect_check_output "C4 is the failing requirement" "[FAIL] C4" "$FIX/profile-c4-no-withholdable.rules.json"
expect_check_exit   "C5 naming violations are rejected"  1 "$FIX/profile-c5-naming.rules.json"
expect_check_output "C5 is the failing requirement" "[FAIL] C5" "$FIX/profile-c5-naming.rules.json"
expect_check_output "C5 catches the Current suffix" "Current" "$FIX/profile-c5-naming.rules.json"
expect_check_exit   "C6 derived judgement is rejected"   1 "$FIX/profile-c6-judgement.rules.json"
expect_check_output "C6 is the failing requirement" "[FAIL] C6" "$FIX/profile-c6-judgement.rules.json"
expect_check_exit   "C7 relaxing override is rejected"   1 "$FIX/profile-invalid-relaxing.rules.json"
expect_check_output "C7 is the failing requirement" "[FAIL] C7" "$FIX/profile-invalid-relaxing.rules.json"
expect_check_output "C7 explains monotonicity" "monotonic" "$FIX/profile-invalid-relaxing.rules.json"
expect_check_exit   "C7 diverging inherited block is rejected" 1 "$FIX/profile-c7-diverging-block.rules.json"
expect_check_output "C7 names the diverging block" "disclosure" "$FIX/profile-c7-diverging-block.rules.json"
expect_check_exit   "C7 widened lifecycle stages are rejected" 1 "$FIX/profile-c7-widening-stages.rules.json"
expect_check_output "C7 explains the widening" "monotonic" "$FIX/profile-c7-widening-stages.rules.json"
expect_check_exit   "C1 an unactionable decision is rejected" 1 "$FIX/profile-c1-no-decision-options.rules.json"
expect_check_output "C1 is the failing requirement" "[FAIL] C1" "$FIX/profile-c1-no-decision-options.rules.json"
expect_check_output "C1 asks for the actions" "decisionOptions" "$FIX/profile-c1-no-decision-options.rules.json"
expect_check_exit   "C13 a group covering only the in-scope purposes is rejected" 1 \
                    "$FIX/profile-c13-uncovered-purposes.rules.json"
expect_check_output "C13 is the failing requirement" "[FAIL] C13" \
                    "$FIX/profile-c13-uncovered-purposes.rules.json"
expect_check_output "C13 says why it is a floor" "floor rather than a stage" \
                    "$FIX/profile-c13-uncovered-purposes.rules.json"
expect_check_exit   "C13 a group keyed by nothing is rejected" 1 \
                    "$FIX/profile-c13-unkeyed-group.rules.json"
expect_check_output "C13 says the rule would require no entries" "would require no entries" \
                    "$FIX/profile-c13-unkeyed-group.rules.json"
expect_check_exit   "C11 missing scope is rejected"      1 "$FIX/profile-c11-no-scope.rules.json"
expect_check_output "C11 is the failing requirement" "[FAIL] C11" "$FIX/profile-c11-no-scope.rules.json"
expect_check_exit   "C12 capability without present state is rejected" 1 \
                    "$FIX/profile-c12-capability-unpaired.rules.json"
expect_check_output "C12 is the failing requirement" "[FAIL] C12" \
                    "$FIX/profile-c12-capability-unpaired.rules.json"
expect_check_output "C12 names the missing counterpart" "expected keyExchange" \
                    "$FIX/profile-c12-capability-unpaired.rules.json"
expect_check_exit   "C12 an inventory profile requiring capability is rejected" 1 \
                    "$FIX/profile-c12-inventory-capability.rules.json"
expect_check_output "C12 is the failing requirement" "[FAIL] C12" \
                    "$FIX/profile-c12-inventory-capability.rules.json"

# The migration profile satisfies C12 only through inheritance: it declares the
# capability attributes itself and takes every present-state attribute from the
# baseline it extends. That is the normal case, not an edge one, so it is worth
# asserting rather than assuming.
expect_check_output "the migration profile is oriented 'both'" "orientation 'both'" "$PQC"
expect_check_output "the baseline is oriented 'inventory'" "orientation 'inventory'" "$BASE"

# A widened stage set is rejected before any document is evaluated, in the same
# way a relaxing override is: the profile is invalid, not the document.
expect_exit   "widening is a profile error, not a verdict" 3 \
              "$PROD" "$FIX/profile-c7-widening-stages.rules.json"

# SHOULD failures are reported without affecting the verdict, unless --strict.
echo
echo "SHOULD requirements and --strict"
expect_check_exit   "SHOULD gaps alone still pass"       0 "$FIX/profile-should-gaps.rules.json"
expect_check_output "the warnings are reported" "warn" "$FIX/profile-should-gaps.rules.json"
expect_check_exit   "--strict promotes them to failures" 1 "$FIX/profile-should-gaps.rules.json" --strict

# --------------------------------------------------- constraint monotonicity ---
# Decision 0013. Extension is monotonic: conformance to a derived profile has to
# imply conformance to its base. Until this check existed only 'level' and
# 'withholdable' were compared, so an override could lower a minimum count or
# replace an identifier-form requirement with a bare presence check and still be
# accepted — while the report said no override relaxed anything.
echo
echo "Constraint monotonicity"
expect_exit   "lowering an inherited minimum is rejected" 3 \
              "$PROD" "$FIX/profile-relax-mincount.rules.json"
expect_output "and the rejection names the count it lowered" "relaxes 'minCount' (2 -> 1)" \
              "$PROD" "$FIX/profile-relax-mincount.rules.json"
expect_exit   "replacing an identifier form with a presence check is rejected" 3 \
              "$PROD" "$FIX/profile-relax-identifier.rules.json"
expect_output "and the rejection says an obligation may not be dropped" \
              "may not remove one" \
              "$PROD" "$FIX/profile-relax-identifier.rules.json"
expect_check_output "C7 reports the same relaxation" "[FAIL] C7" \
                    "$FIX/profile-relax-mincount.rules.json"

# The counterpart. A check that rejects relaxations is only worth having if it
# still admits the tightenings the mechanism exists for, so assert both.
expect_check_exit "raising the same minimum is accepted"   0 \
                  "$FIX/profile-tighten-constraint.rules.json"
expect_output "the tightening is recorded as a composition note" \
              "minCount tightened, 2 -> 3" \
              "$PROD" "$FIX/profile-tighten-constraint.rules.json"
expect_exit   "and the tightened rule actually bites"      1 \
              "$PROD" "$FIX/profile-tighten-constraint.rules.json"

# ------------------------------------------------------- rules that can fail ---
# C17. A rule that cannot fail is worse than a missing rule, because the report
# says it passed. Both fixtures were accepted before decision 0013: one reported
# 'ok' against every value, the other failed every value without saying why.
echo
echo "Rules that can pass and fail"
expect_check_exit   "an unimplemented constraint key is rejected" 1 \
                    "$FIX/profile-c17-unknown-constraint.rules.json"
expect_check_output "C17 is the failing requirement" "[FAIL] C17" \
                    "$FIX/profile-c17-unknown-constraint.rules.json"
expect_check_output "C17 says what the rule would do" "reports 'ok' against every value" \
                    "$FIX/profile-c17-unknown-constraint.rules.json"
expect_exit   "and the validator refuses the profile rather than issuing a verdict" 3 \
              "$PROD" "$FIX/profile-c17-unknown-constraint.rules.json"
expect_check_exit   "a vocabulary reference that resolves to nothing is rejected" 1 \
                    "$FIX/profile-c17-unresolved-vocabulary.rules.json"
expect_check_output "C17 is the failing requirement" "[FAIL] C17" \
                    "$FIX/profile-c17-unresolved-vocabulary.rules.json"
expect_exit   "and the validator refuses that profile too" 3 \
              "$PROD" "$FIX/profile-c17-unresolved-vocabulary.rules.json"

# A rule with no constraint used to raise an exception part-way through an
# evaluation, so the two tools disagreed and the validator broke its own exit
# contract. It is now a profile error like any other.
"$PY" - "$M/profile-interface-disclosure.rules.json" "$TMP" <<'PY'
import json, sys, os
prof = json.load(open(sys.argv[1], encoding="utf-8"))
prof["interfaceRules"][0].pop("constraint", None)
json.dump(prof, open(os.path.join(sys.argv[2], "profile-no-constraint.rules.json"), "w"))
PY
expect_exit   "a rule with no constraint is a profile error, not a traceback" 3 \
              "$PROD" "$TMP/profile-no-constraint.rules.json"
expect_output "and it says the rule can neither pass nor fail" "neither pass nor fail" \
              "$PROD" "$TMP/profile-no-constraint.rules.json"

# ------------------------------------------- tightening an inherited group ---
# Decision 0014, settling Q49. A derived profile may tighten one member of a
# group it inherited, and may widen that group's coverage. Without this the only
# ways to ask for more depth were to restate the group, which silently replaces
# the base's coverage, or to add a parallel group, which asks a producer for the
# same fact twice under two names.
echo
echo "Tightening an inherited group"
L3="$FIX/profile-l3-settlement.rules.json"

expect_output "a member of an inherited group can be tightened" \
              "override pqc-migration#G1.3: level raised MAY -> MUST" \
              "$PROD" "$L3"
expect_output "and the tightening reaches every entry in the group" \
              "roadmapRef" "$PROD" "$L3"
# The group shell is inherited, not restated, so its coverage still comes from
# the parent. That is the property restating the group would have destroyed.
expect_output_fixed "the group's own coverage is still the parent's" \
              "pqc-migration#G1.1[non-repudiation]" \
              "$PROD" "$L3"

# A guard says when a rule applies. Removing one makes a rule apply always and is
# a tightening; adding or narrowing one is a relaxation that is nearly invisible
# on the page, because the rule is still listed and still reported.
expect_exit   "adding a guard where the base has none is rejected" 3 \
              "$PROD" "$FIX/profile-q49-guard-added.rules.json"
expect_output "and it says the rule would apply less often" "apply less often" \
              "$PROD" "$FIX/profile-q49-guard-added.rules.json"
expect_exit   "narrowing an inherited guard is rejected"     3 \
              "$PROD" "$FIX/profile-q49-guard-changed.rules.json"
expect_output "and it offers the two legitimate alternatives" "remove the guard" \
              "$PROD" "$FIX/profile-q49-guard-changed.rules.json"

# Coverage may be widened and never narrowed: narrowing it is how a staged
# profile becomes the permanent floor decision 0010 exists to prevent.
expect_exit   "narrowing an inherited group's coverage is rejected" 3 \
              "$PROD" "$FIX/profile-q49-coverage-narrowed.rules.json"
expect_output "and it says a producer would owe fewer answers" "answer for fewer keys" \
              "$PROD" "$FIX/profile-q49-coverage-narrowed.rules.json"

# ------------------------------------------------------------ rule numbering ---
# Decision 0011. A rule id is local to the profile that declares it, and the
# citable form is '<profileTag>#<ruleId>'. The point of the scheme is that three
# profiles in one chain can each number from I1 and a reader can still tell the
# three apart, so that is what these assert.
echo
echo "Rule numbering across a family"
L3="$FIX/profile-l3-settlement.rules.json"

expect_output_fixed "the report qualifies an inherited rule id" "interface-disclosure#I1" \
              "$PROD" "$PQC"
expect_output_fixed "a derived profile numbers its own rules from I1" "pqc-migration#I1" \
              "$PROD" "$PQC"
expect_output_fixed "and its product rules from P1, beside the base's P1" "pqc-migration#P1" \
              "$PROD" "$PQC"
expect_output_fixed "the base's own P1 is still there and distinct" "interface-disclosure#P1" \
              "$PROD" "$PQC"
expect_output_fixed "a group rule takes the G letter" "pqc-migration#G1.1[encryption]" \
              "$PROD" "$PQC"
expect_output "the chain is printed above the report" "interface-disclosure -> pqc-migration" \
              "$PROD" "$PQC"
# A tightened rule keeps the id, and the tag, of the profile that introduced it.
# That is what lets a stored claim citing it stay meaningful further down.
expect_output_fixed "a tightened rule keeps its introducer's id" \
              "override interface-disclosure#I9" \
              "$PROD" "$PQC"

# Three levels. The fixture declares its own P1 and its own I1, both of which
# are local ids that BOTH ancestors already use.
expect_check_exit "a third-level profile is well-formed" 0 "$L3"
expect_check_output "C15 prints the whole chain" \
                    "interface-disclosure -> pqc-migration -> sector-settlement" "$L3"
expect_output_fixed "the third level numbers from I1 as well" "sector-settlement#I1" \
              "$PROD" "$L3"
expect_output_fixed "and all three I1 rules appear in one report" "pqc-migration#I1" \
              "$PROD" "$L3"
expect_output_fixed "the failure names the profile that imposed it" \
              "sector-settlement#I1" \
              "$PROD" "$L3"

# Monotonicity holds transitively: a third-level profile may not relax a rule
# the base introduced, even though it is the grandparent rather than the parent.
expect_exit   "relaxing a grandparent rule is rejected" 3 \
              "$PROD" "$FIX/profile-l3-relaxes-grandparent.rules.json"
expect_output "and the rejection names monotonicity" "monotonic" \
              "$PROD" "$FIX/profile-l3-relaxes-grandparent.rules.json"
expect_output_fixed "and names the grandparent's rule, two levels up" \
              "interface-disclosure#I9" \
              "$PROD" "$FIX/profile-l3-relaxes-grandparent.rules.json"

# The tag is the one identifier that has to be unique along a chain. It is what
# replaced the old rule-id collision check, so it is checked in both tools.
expect_exit   "a tag an ancestor already uses is rejected" 3 \
              "$PROD" "$FIX/profile-l3-tag-collision.rules.json"
expect_output "and says why a tag must be unique" "unique along the chain" \
              "$PROD" "$FIX/profile-l3-tag-collision.rules.json"
expect_check_exit   "C15 rejects the same profile" 1 "$FIX/profile-l3-tag-collision.rules.json"
expect_check_output "C15 is the failing requirement" "[FAIL] C15" \
                    "$FIX/profile-l3-tag-collision.rules.json"

# The letter is fixed by the section a rule sits in, because that is the fact a
# reader wants from it: once per product, once per interface, once per entry.
expect_check_exit   "C16 rejects a letter that contradicts its section" 1 \
                    "$FIX/profile-c16-wrong-letter.rules.json"
expect_check_output "C16 is the failing requirement" "[FAIL] C16" \
                    "$FIX/profile-c16-wrong-letter.rules.json"
expect_check_output "C16 says which letter the section takes" "so it takes the letter P" \
                    "$FIX/profile-c16-wrong-letter.rules.json"
expect_check_output "C17 passes on both example profiles" "[PASS] C17" "$BASE"
expect_check_output "C17 passes on the derived profile too" "[PASS] C17" "$PQC"

# ------------------------------------------------------- conformance claims ---
# Decision 0015, settling Q24. A claim is the artifact that crosses an
# organisational boundary. It is bound to one document by digest, names every
# profile with its chain, and can be re-checked by whoever receives it.
echo
echo "Conformance claims"
CLAIM="$TMP/claim.json"

"$PY" "$M/validate_cbom.py" "$PROD" \
      "$M/profile-interface-disclosure.rules.json" "$M/profile-pqc-migration.rules.json" \
      --claim > "$CLAIM" 2>/dev/null
RC=$?
if [ "$RC" -eq 0 ] && "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if len(d['profiles'])==2 else 1)" "$CLAIM"; then
  ok "a claim covers several profiles at once"
else
  bad "a claim covers several profiles at once" "expected exit 0 and two profile entries, got exit $RC"
fi

# The digest is what binds a claim to a document. Without it a claim is about
# whatever document someone later puts beside it.
if "$PY" -c "
import json,sys,hashlib
c=json.load(open(sys.argv[1]))
want=c['document']['digest']['value']
got=hashlib.sha256(open(sys.argv[2],'rb').read()).hexdigest()
sys.exit(0 if want==got else 1)" "$CLAIM" "$PROD"; then
  ok "the claim's digest is the document's digest"
else
  bad "the claim's digest is the document's digest" "digest does not match"
fi

for field in claimFormat notAsserted evaluableFromCarrier; do
  if "$PY" -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if sys.argv[2] in d else 1)" "$CLAIM" "$field"; then
    ok "the claim carries '$field'"
  else
    bad "the claim carries '$field'" "field absent"
  fi
done

# A claim that cannot be re-checked is a press release.
OUT="$("$PY" "$M/validate_cbom.py" "$PROD" "$CLAIM" \
       --verify-claim --profiles-dir "$M" 2>&1)"; RC=$?
if [ "$RC" -eq 0 ] && printf '%s' "$OUT" | grep -q "VERIFIED"; then
  ok "a claim verifies against the document it names"
else
  bad "a claim verifies against the document it names" "expected exit 0 and VERIFIED, got exit $RC"
fi

# Point the same claim at a different document and it must not verify. Exit 5,
# because this is a finding about the claim and not a verdict on the document.
OUT="$("$PY" "$M/validate_cbom.py" "$PQCFAIL" "$CLAIM" \
       --verify-claim --profiles-dir "$M" 2>&1)"; RC=$?
if [ "$RC" -eq 5 ] && printf '%s' "$OUT" | grep -q "digest mismatch"; then
  ok "the same claim does not verify against a different document"
else
  bad "the same claim does not verify against a different document" "expected exit 5 and a digest mismatch, got exit $RC"
fi

# A tampered verdict is caught by re-evaluation rather than by trusting the issuer.
"$PY" - "$CLAIM" "$TMP" <<'PY'
import json, sys, os
c = json.load(open(sys.argv[1], encoding="utf-8"))
c["profiles"][0]["verdict"] = "does-not-conform"
json.dump(c, open(os.path.join(sys.argv[2], "claim-tampered.json"), "w"))
PY
OUT="$("$PY" "$M/validate_cbom.py" "$PROD" "$TMP/claim-tampered.json" \
       --verify-claim --profiles-dir "$M" 2>&1)"; RC=$?
if [ "$RC" -eq 5 ] && printf '%s' "$OUT" | grep -q "re-evaluation says"; then
  ok "a verdict that no longer holds is caught"
else
  bad "a verdict that no longer holds is caught" "expected exit 5 and a re-evaluation mismatch, got exit $RC"
fi

# A refused evaluation appears in the claim as refused, carrying no rule results.
# Merging refusal into failure is what T1 forbids, and a claim is where that
# merge would do the most damage.
"$PY" - "$LEGACY" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
bom["specVersion"] = "1.5"
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-1.5-claim.json"), "w"))
PY
"$PY" "$M/validate_cbom.py" "$TMP/cbom-1.5-claim.json" "$M/profile-interface-disclosure.rules.json" \
      --claim > "$TMP/claim-refused.json" 2>/dev/null
RC=$?
if [ "$RC" -eq 4 ] && "$PY" -c "
import json,sys
e=json.load(open(sys.argv[1]))['profiles'][0]
sys.exit(0 if e['verdict']=='refused' and e['assessed'] is False and 'rules' not in e else 1)" "$TMP/claim-refused.json"; then
  ok "a refused evaluation is refused in the claim, with no rule results"
else
  bad "a refused evaluation is refused in the claim, with no rule results" "expected exit 4 and a refused entry carrying no rules, got exit $RC"
fi

# ----------------------------------------------------- deployment records ---
# The operator's records of the same Keycloak: what the deployment permits
# (configured) and what it was seen to do (observed). Each cites the documents
# it builds on by BOM-Link and hash, and joins each interface to the one it
# realises. Supplying the cited documents lets the validator check the hashes
# and follow the join.
echo
echo "Deployment records and joins"
expect_exit   "the configured record conforms"  0 "$CONF" "$DEPL" --with "$PROD"
expect_output "the citation is checked by hash" "hash matches" "$CONF" "$DEPL" --with "$PROD"
expect_output "the deployment is identified by a tag URI" "tag:example.org,2026:deployment/sso-prod" \
              "$CONF" "$DEPL" --with "$PROD"
expect_output "each interface names the one it realises" "-> cbom-keycloak-product.cdx.json#" \
              "$CONF" "$DEPL" --with "$PROD"
expect_output "the library is inherited across the join" "inherited via cbom-keycloak-product.cdx.json" \
              "$CONF" "$DEPL" --with "$PROD"
expect_exit   "without the cited document it still conforms" 0 "$CONF" "$DEPL"
expect_output "and says what was not resolved" "not supplied" "$CONF" "$DEPL"
expect_exit   "a build-time literal at configured fails" 1 \
              "$EX/cbom-keycloak-deployment-configured-fail-literal.cdx.json" "$DEPL" --with "$PROD"
expect_output "because the operator holds the answer" "the producer holds the answer" \
              "$EX/cbom-keycloak-deployment-configured-fail-literal.cdx.json" "$DEPL" --with "$PROD"
expect_exit   "the observed record conforms" 0 "$OBS" "$DEPL" --with "$PROD" --with "$CONF"
expect_output "the library is followed through two hops" \
              "inherited via cbom-keycloak-deployment-configured.cdx.json#crypto:protocol:int-db -> cbom-keycloak-product.cdx.json" \
              "$OBS" "$DEPL" --with "$PROD" --with "$CONF"
expect_output "observation methods are recorded" "observationMethod" "$OBS" "$DEPL" --with "$PROD" --with "$CONF"
expect_exit   "an unknown observed value fails the deployment profile" 1 \
              "$EX/cbom-keycloak-deployment-observed-fail-unknown.cdx.json" "$DEPL" --with "$PROD" --with "$CONF"
expect_exit   "a cited record that has changed is caught" 1 \
              "$EX/cbom-keycloak-deployment-observed-fail-P1.cdx.json" "$DEPL" --with "$PROD" --with "$CONF"
expect_output "and the report says the revision changed" "the cited revision has changed" \
              "$EX/cbom-keycloak-deployment-observed-fail-P1.cdx.json" "$DEPL" --with "$PROD" --with "$CONF"
expect_output "an outside observer satisfies P2 with 'not-reached'" "stated as 'not-reached'" \
              "$EX/cbom-keycloak-deployment-observed-outside.cdx.json" "$DEPL" --with "$PROD"
"$PY" - "$OBS" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
# An inside observer whose scan did not reach the management interfaces.
bom["inventories"][0]["components"] = [c for c in bom["inventories"][0]["components"]
    if c.get("bom-ref") not in ("service:mgmt-health", "service:mgmt-admin")]
json.dump(bom, open(os.path.join(sys.argv[2], "obs-nomgmt.json"), "w"))
PY
expect_exit   "an inside observer that missed the management port still conforms" 0 \
              "$TMP/obs-nomgmt.json" "$DEPL" --with "$PROD" --with "$CONF"
expect_output "because the configured record it cites declares one" "declared in a cited record" \
              "$TMP/obs-nomgmt.json" "$DEPL" --with "$PROD" --with "$CONF"

# ---------------------------------------------------------- reference rules ---
echo
echo "Reference rules"
expect_output "the companion SBOM is pointed to" "interface-disclosure#R1" "$PROD" "$BASE"
expect_output "a stated absence of VEX satisfies R2" "stated absent: 'not-published'" "$STATES" "$BASE"
expect_output "a VEX document is pointed to by BOM-Link and hash" "(vex-document)" "$PROD" "$BASE"
expect_output "and the hash is checked when the VEX is supplied" "hash matches keycloak-26.7.3-vex.cdx.json" \
              "$PROD" "$BASE" --with "$EX/context/keycloak-26.7.3-vex.cdx.json"
expect_output "so is the companion SBOM's" "hash matches keycloak-26.7.3-sbom.cdx.json" \
              "$PROD" "$BASE" --with "$EX/context/keycloak-26.7.3-sbom.cdx.json"
expect_output "the roadmap is pointed to under pqc-migration#R2" "keycloak-pqc-roadmap.json" "$PROD" "$PQC"
expect_output "an advisory API names its protocol" "(osv-api)" "$PROD" "$BASE"
expect_exit   "deployment-defined without a pointer to the guide fails" 1 \
              "$EX/cbom-keycloak-product-fail-R5.cdx.json" "$BASE"
expect_output "and the failure is R5" "tls-https/interface-disclosure#R5" \
              "$EX/cbom-keycloak-product-fail-R5.cdx.json" "$BASE"
expect_output "R5 does not apply where the product fixes the value" "no attribute is 'deployment-defined'" \
              "$PROD" "$BASE"

# ------------------------------------------------------ examples and carriers ---
echo
echo "Every example gets its expected verdicts"
OUT="$("$PY" "$ROOT/tests/check-examples.py" 2>&1)"; RC=$?
printf '%s\n' "$OUT" | tail -3 | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then passed=$((passed + 1)); else printf '%s\n' "$OUT" | grep FAIL -A2; failed=$((failed + 1)); fi

echo
echo "Context documents the product record points to"
OUT="$("$PY" "$ROOT/tests/check-context.py" 2>&1)"; RC=$?
printf '%s\n' "$OUT" | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then passed=$((passed + 1)); else failed=$((failed + 1)); fi

echo
echo "CycloneDX schema validity"
OUT="$("$PY" "$ROOT/tests/check-cyclonedx.py" "$EX"/*.cdx.json "$EX"/legacy/*.cdx.json "$EX"/context/*.cdx.json "$M"/perspectives/*.cdx.json 2>&1)"; RC=$?
printf '%s\n' "$OUT" | tail -1 | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then passed=$((passed + 1)); else printf '%s\n' "$OUT" | grep FAIL -A3; failed=$((failed + 1)); fi

# --------------------------------------------------------------- policies ---
echo
echo "Policies"
for spec in "result-readiness-gap-sso-prod.json:policy-readiness-gap.policy.json:cbom-keycloak-product.cdx.json cbom-keycloak-deployment-configured.cdx.json cbom-keycloak-deployment-observed.cdx.json" \
            "result-algorithm-transition-keycloak-product.json:policy-algorithm-transition.policy.json:cbom-keycloak-product.cdx.json" \
            "result-algorithm-transition-sso-prod-observed.json:policy-algorithm-transition.policy.json:cbom-keycloak-deployment-observed.cdx.json"; do
  result=${spec%%:*}; rest=${spec#*:}; policy=${rest%%:*}; docs=${rest#*:}
  args=""
  for d in $docs; do args="$args $EX/$d"; done
  "$PY" "$M/evaluate_policy.py" "$M/policies/$policy" $args --date 2026-10-25 --out "$TMP/$result" >/dev/null 2>&1
  if cmp -s "$TMP/$result" "$EX/results/$result"; then
    ok "$result reproduces from its policy and CBOMs"
  else
    bad "$result reproduces from its policy and CBOMs" "regenerate with tools/build_keycloak_examples.py"
  fi
done
if "$PY" -c "
import json,sys
r=json.load(open(sys.argv[1]))
c={(f['interface']['configured'] or f['interface']['implemented'],f['purpose']):f['class'] for f in r['findings']}
want={('crypto:protocol:ing-tls','key-establishment'):'enabled-not-negotiated',
      ('service:svc-http','key-establishment'):'unprotected',
      ('service:svc-oidc','entity-authentication'):'not-capable',
      ('crypto:protocol:tls-https','key-establishment'):'not-deployed'}
sys.exit(0 if all(c.get(k)==v for k,v in want.items()) else 1)" "$EX/results/result-readiness-gap-sso-prod.json"; then
  ok "the readiness gap places the ingress, the plaintext hop, token signing and the unused listener"
else
  bad "the readiness gap places the ingress, the plaintext hop, token signing and the unused listener" "unexpected classes"
fi
if "$PY" -c "
import json,sys
r=json.load(open(sys.argv[1]))
ok=[d['digest']['alg']=='SHA-256' and len(d['digest']['value'])==64 for d in r['documents']]
sys.exit(0 if ok and all(ok) and r['policy']['version'] and r['evaluationDate'] else 1)" "$EX/results/result-readiness-gap-sso-prod.json"; then
  ok "a result names the policy version, the date, and every CBOM by digest"
else
  bad "a result names the policy version, the date, and every CBOM by digest" "missing fields"
fi

# ------------------------------------------------------- demonstration page ---
# The site's interactive page is a second implementation of the evaluation
# semantics, and it told readers its results matched the reference tool's while
# nothing checked that. See decision 0018.
echo
echo "Demonstration page"
OUT="$("$PY" "$ROOT/tests/check-demo.py" 2>&1)"; RC=$?
printf '%s\n' "$OUT" | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then
  passed=$((passed + 1))
else
  failed=$((failed + 1))
fi

# --------------------------------------------------------- published schemas ---
echo
echo "Published schemas"
OUT="$("$PY" "$ROOT/tests/check-schemas.py" 2>&1)"; RC=$?
printf '%s\n' "$OUT" | sed 's/^/  /'
if [ "$RC" -eq 0 ]; then
  passed=$((passed + 1))
else
  failed=$((failed + 1))
fi

# ------------------------------------------------------------------ summary ---
echo
echo "=================="
printf '%d passed, %d failed\n\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
