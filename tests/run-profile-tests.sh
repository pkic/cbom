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

passed=0
failed=0

ok()   { printf '  ok   %s\n' "$1"; passed=$((passed + 1)); }
bad()  { printf '  FAIL %s\n     %s\n' "$1" "$2"; failed=$((failed + 1)); }

# validate <cbom> <profile> -> writes output to $OUT, sets $RC
validate() {
  OUT="$("$PY" "$M/validate_cbom.py" "$1" "$2" 2>&1)"
  RC=$?
}

# expect_exit <label> <expected-rc> <cbom> <profile>
expect_exit() {
  local label=$1 want=$2 cbom=$3 prof=$4
  validate "$cbom" "$prof"
  if [ "$RC" -eq "$want" ]; then
    ok "$label"
  else
    bad "$label" "expected exit $want, got $RC$(printf '\n     %s' "$(echo "$OUT" | tail -3)")"
  fi
}

# expect_output <label> <needle> <cbom> <profile>
expect_output() {
  local label=$1 needle=$2 cbom=$3 prof=$4
  validate "$cbom" "$prof"
  if printf '%s' "$OUT" | grep -q -- "$needle"; then
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
for f in "$M"/*.json "$FIX"/*.json; do
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

for script in validate_cbom.py check_profile.py; do
  if "$PY" -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$M/$script" 2>/dev/null; then
    ok "$script parses"
  else
    bad "$script parses" "syntax error"
  fi
done

# ------------------------------------------------------- baseline profile ---
echo
echo "Baseline profile"
expect_exit   "conforming CBOM is accepted"        0 "$M/cbom-pass.cyclonedx.json" "$BASE"
expect_output "verdict reads CONFORMS"     "CONFORMS" "$M/cbom-pass.cyclonedx.json" "$BASE"
expect_output "withheld purl reported HELD"    "HELD" "$M/cbom-pass.cyclonedx.json" "$BASE"
expect_exit   "non-conforming CBOM is rejected"    1 "$M/cbom-fail.cyclonedx.json" "$BASE"
expect_output "failure is product rule P2"       "P2" "$M/cbom-fail.cyclonedx.json" "$BASE"

# ------------------------------------------------------------ carrier bands ---
echo
echo "Carrier version bands"
# Four bands, so four inputs. Three copies only reach target, legacy and
# refuse; 'newer' needs a carrier above the profile's tested version, and both
# versioning documents used to claim four bands from three copies.
"$PY" - "$M/cbom-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
for v in ("1.8", "1.6", "1.5"):
    bom["specVersion"] = v
    json.dump(bom, open(os.path.join(sys.argv[2], "cbom-%s.json" % v), "w"))
PY
expect_exit   "legacy 1.6 still evaluates"         0 "$TMP/cbom-1.6.json" "$BASE"
expect_output "legacy 1.6 is flagged"        "legacy" "$TMP/cbom-1.6.json" "$BASE"
expect_exit   "newer 1.8 still evaluates"          0 "$TMP/cbom-1.8.json" "$BASE"
expect_output "newer 1.8 is flagged"          "newer" "$TMP/cbom-1.8.json" "$BASE"

# Refusal is not failure. The Conformance section makes this a MUST — "Refusal
# and non-conformance are reported distinctly and MUST NOT be merged", and T1
# requires refusing without issuing a conformance verdict. Until this was fixed
# the validator printed DOES NOT CONFORM and exited 1 for a refused document,
# and the test below asserted that exit code, so the suite pinned the defect.
expect_exit   "unsupported 1.5 is refused"         4 "$TMP/cbom-1.5.json" "$BASE"
expect_output "refusal explains why"  "older than min" "$TMP/cbom-1.5.json" "$BASE"
expect_output "the verdict reads REFUSED"    "REFUSED" "$TMP/cbom-1.5.json" "$BASE"
expect_output "refusal is not called a failure" "not a failure" \
              "$TMP/cbom-1.5.json" "$BASE"
# A refused document is not assessed, so no rule result may be reported for it.
validate "$TMP/cbom-1.5.json" "$BASE"
if printf '%s' "$OUT" | grep -q 'PRODUCT-LEVEL RULES\|INTERFACE '; then
  bad "no rules are evaluated on refusal" "the report contains rule results"
else
  ok "no rules are evaluated on refusal"
fi
# The distinction has to survive into the machine-readable report, since that is
# what a pipeline reads.
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
expect_exit   "conforming CBOM is accepted"        0 "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "base profile is resolved"     "extends" "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "inapplicable conditional is skipped" "not applicable" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_exit   "non-conforming CBOM is rejected"    1 "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "conditional M5 fires"             "M5" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "conditional M11 fires"           "M11" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "tightened I9 fires"               "I9" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"

# ------------------------------------------------- accepted lifecycle stages ---
# scope.lifecycleStages says which stages of reported data a profile will accept.
# The baseline accepts all four; the migration profile narrows to the three that
# describe something that exists, because a migration plan built on cryptography
# a producer merely intends to implement is a plan built on an intention.
echo
echo "Accepted lifecycle stages"
"$PY" - "$M/cbom-pqc-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
# Move one interface from 'implemented' to 'intended', changing nothing else.
for c in bom.get("components", []):
    for p in c.get("properties", []):
        if p.get("name") == "pkic:profile:lifecycleStage":
            p["value"] = "intended"
            break
    else:
        continue
    break
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-intended.json"), "w"))
PY
expect_exit   "the same document conforms with an accepted stage" 0 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_exit   "an unaccepted stage fails the migration profile"   1 \
              "$TMP/cbom-intended.json" "$PQC"
expect_output "the failure is I8"                "I8" "$TMP/cbom-intended.json" "$PQC"
expect_output "the report says the stage is out of scope" "outside the stages this profile accepts" \
              "$TMP/cbom-intended.json" "$PQC"
# The stage is a real one, so the baseline, which accepts all four, still passes
# it. The narrowing belongs to the derived profile and not to the vocabulary.
expect_exit   "the baseline still accepts the same document"      0 \
              "$TMP/cbom-intended.json" "$BASE"

# ------------------------------------------------------------- composition ---
echo
echo "Composition semantics"
# The same document that fails the derived profile conforms to the base, because
# the base permits a withheld implementationPurl and the derived profile does not.
expect_exit   "derived-failing CBOM conforms to the base" 0 \
              "$M/cbom-pqc-fail.cyclonedx.json" "$BASE"
expect_exit   "relaxing override is rejected"      3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-invalid-relaxing.rules.json"
expect_output "rejection names monotonicity" "monotonic" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-invalid-relaxing.rules.json"

# ---------------------------------------------- withholdable MUST (v0.3) ---
# Withholding can only change an outcome on a MUST rule. Baseline v0.3 raised I9
# to MUST while keeping it withholdable, which is the combination the disclosure
# model exists for. Before v0.3 no rule combined the two.
echo
echo "Withholdable MUST"
"$PY" - "$M/cbom-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
# Strip the withheld marker, leaving implementationPurl with neither a value nor
# a marker on the management interface: undeclared rather than withheld.
for c in bom.get("components", []):
    c["properties"] = [p for p in c.get("properties", [])
                       if p.get("name") != "pkic:profile:disclosure:implementationPurl"]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-marker.json"), "w"))
PY
expect_exit   "a withheld marker satisfies the MUST"       0 "$M/cbom-pass.cyclonedx.json" "$BASE"
expect_exit   "silent omission of the same attribute does not" 1 "$TMP/cbom-no-marker.json" "$BASE"
expect_output "the failure is I9"                       "I9" "$TMP/cbom-no-marker.json" "$BASE"
expect_output "reported as undeclared, not withheld" "no disclosure marker" \
              "$TMP/cbom-no-marker.json" "$BASE"

# -------------------------------------------------- profile well-formedness ---
# The second conformance target: a profile checked against the methodology.
# Requirements C1 to C12 are stated in the Conformance section.
echo
echo "Profile well-formedness (C1-C12)"
expect_check_exit "baseline profile is well-formed"        0 "$BASE"
expect_check_exit "derived profile is well-formed"         0 "$PQC"
expect_check_output "baseline verdict reads WELL-FORMED" "VERDICT : WELL-FORMED" "$BASE"
expect_check_exit "both are well-formed under --strict"    0 "$BASE" --strict
expect_check_exit "derived is well-formed under --strict"  0 "$PQC" --strict

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
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-c7-widening-stages.rules.json"

# SHOULD failures are reported without affecting the verdict, unless --strict.
echo
echo "SHOULD requirements and --strict"
expect_check_exit   "SHOULD gaps alone still pass"       0 "$FIX/profile-should-gaps.rules.json"
expect_check_output "the warnings are reported" "warn" "$FIX/profile-should-gaps.rules.json"
expect_check_exit   "--strict promotes them to failures" 1 "$FIX/profile-should-gaps.rules.json" --strict

# ------------------------------------------------------------------ summary ---
echo
echo "=================="
printf '%d passed, %d failed\n\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
