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

if "$PY" -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$M/validate_cbom.py" 2>/dev/null; then
  ok "validator parses"
else
  bad "validator parses" "syntax error in validate_cbom.py"
fi

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
"$PY" - "$M/cbom-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
for v in ("1.6", "1.5"):
    bom["specVersion"] = v
    json.dump(bom, open(os.path.join(sys.argv[2], "cbom-%s.json" % v), "w"))
PY
expect_exit   "legacy 1.6 still evaluates"         0 "$TMP/cbom-1.6.json" "$BASE"
expect_output "legacy 1.6 is flagged"        "legacy" "$TMP/cbom-1.6.json" "$BASE"
expect_exit   "unsupported 1.5 is refused"         1 "$TMP/cbom-1.5.json" "$BASE"
expect_output "refusal explains why"  "older than min" "$TMP/cbom-1.5.json" "$BASE"

# ------------------------------------------------------ derived PQC profile ---
echo
echo "PQC migration profile (derived)"
expect_exit   "conforming CBOM is accepted"        0 "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "base profile is resolved"     "extends" "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "inapplicable conditional is skipped" -- "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_exit   "non-conforming CBOM is rejected"    1 "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "conditional M5 fires"             "M5" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "conditional M11 fires"           "M11" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "tightened I9 fires"               "I9" "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"

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

# ------------------------------------------------------------------ summary ---
echo
echo "=================="
printf '%d passed, %d failed\n\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
