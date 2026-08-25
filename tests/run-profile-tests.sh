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

# expect_output_fixed <label> <literal-needle> <cbom> <profile>
# Qualified group member ids such as pqc-migration#G1.2[key-establishment]
# contain [ and ].
expect_output_fixed() {
  local label=$1 needle=$2 cbom=$3 prof=$4
  validate "$cbom" "$prof"
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
expect_output "failure is product rule P2" "interface-disclosure#P2" \
              "$M/cbom-fail.cyclonedx.json" "$BASE"

# ------------------------------------------------- baseline product rules ---
# v0.6 added two product rules and revised a third. P3 and P4 are what make the
# document usable as an inventory record at all: without them a CBOM need not
# say what it describes, nor whether its interface list is the whole list.
echo
echo "Baseline product rules"
expect_output "P3 identifies the subject" "pkg:generic/nginx@1.27.0" \
              "$M/cbom-pass.cyclonedx.json" "$BASE"
expect_output "P4 states completeness"   "all-external" \
              "$M/cbom-pass.cyclonedx.json" "$BASE"

"$PY" - "$M/cbom-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
# Strip the subject identifier, leaving a name and a version behind.
bom["metadata"]["component"].pop("purl", None)
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-unidentified.json"), "w"))

bom = json.load(open(sys.argv[1], encoding="utf-8"))
bom["metadata"]["component"]["properties"] = [
    p for p in bom["metadata"]["component"].get("properties", [])
    if p.get("name") != "pkic:profile:coverage"]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-nocoverage.json"), "w"))

# A subject with no administrative surface: no management interface, and a
# stated reason. It must conform, where before v0.6 it could not.
bom = json.load(open(sys.argv[1], encoding="utf-8"))
bom["components"] = [c for c in bom["components"]
                     if c.get("bom-ref") != "crypto:protocol:mgmt-ssh"]
bom["metadata"]["component"].setdefault("properties", []).append(
    {"name": "pkic:profile:managementInterfaceAbsence", "value": "no-configuration-surface"})
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-noadmin.json"), "w"))

# The same document without the reason: silence is not a stated absence.
bom["metadata"]["component"]["properties"] = [
    p for p in bom["metadata"]["component"]["properties"]
    if p.get("name") != "pkic:profile:managementInterfaceAbsence"]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-noadmin-silent.json"), "w"))
PY
expect_exit   "a document that does not say what it describes fails" 1 \
              "$TMP/cbom-unidentified.json" "$BASE"
expect_output "and a name and version are not an identifier" "not a stable identifier" \
              "$TMP/cbom-unidentified.json" "$BASE"
expect_exit   "a document with no completeness statement fails" 1 \
              "$TMP/cbom-nocoverage.json" "$BASE"

# The revised P2. A structural rule is satisfied by presence or by a stated
# absence; silence is neither. Before v0.6 the first of these failed while
# hiding nothing.
expect_exit   "no management interface, absence stated, conforms" 0 \
              "$TMP/cbom-noadmin.json" "$BASE"
expect_output "and the report says how it was satisfied" "none declared, stated as" \
              "$TMP/cbom-noadmin.json" "$BASE"
expect_exit   "no management interface and no reason does not conform" 1 \
              "$TMP/cbom-noadmin-silent.json" "$BASE"
expect_output "and says the absence was never explained" "no declared reason for the absence" \
              "$TMP/cbom-noadmin-silent.json" "$BASE"

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
expect_output "conditional I5 fires"  "pqc-migration#I5" \
              "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output_fixed "conditional blocker fires within a purpose entry" \
              "pqc-migration#G1.2[key-establishment]" \
              "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "tightened I9 fires" "interface-disclosure#I9" \
              "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"

# --------------------------------------------------- capability per purpose ---
# Q27: readiness was one value per interface, which cannot express the ordinary
# position of key agreement done and identity proof not yet. It is now a group
# keyed by cryptographic purpose. Coverage is the whole vocabulary rather than
# only the purposes in scope, which is what stops a staged profile becoming a
# permanent floor.
echo
echo "Capability per cryptographic purpose"
expect_output_fixed "status is stated per purpose" \
              "pqc-migration#G1.1[entity-authentication]" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "one interface holds two different statuses" "= 'committed'" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "the blocker is evaluated inside the entry" \
              "pqc-migration#G1.2[entity-authentication]" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "an available purpose needs no blocker" "not applicable (capabilityStatus='available')" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "a missing in-scope purpose is named" "purpose[entity-authentication]" \
              "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"
expect_output "a missing out-of-scope purpose still fails" "no entry for this purpose (status only)" \
              "$M/cbom-pqc-fail.cyclonedx.json" "$PQC"

# Out-of-scope purposes owe a status, not the full attribute set. Strip every
# out-of-scope entry from the conforming document and it must stop conforming;
# that obligation is the ratchet, so it is worth asserting rather than assuming.
"$PY" - "$M/cbom-pqc-pass.cyclonedx.json" "$TMP" <<'PY'
import json, sys, os
bom = json.load(open(sys.argv[1], encoding="utf-8"))
deferred = ("data-integrity", "non-repudiation", "key-protection", "key-derivation")
for c in bom.get("components", []):
    c["properties"] = [p for p in c.get("properties", [])
                       if not any(":%s:" % d in p.get("name", "") for d in deferred)]
json.dump(bom, open(os.path.join(sys.argv[2], "cbom-no-deferred.json"), "w"))
PY
expect_exit   "dropping the deferred purposes breaks conformance" 1 \
              "$TMP/cbom-no-deferred.json" "$PQC"
expect_output "and the baseline is unaffected by any of it" "CONFORMS" \
              "$TMP/cbom-no-deferred.json" "$BASE"

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
expect_output "the failure is I8" "interface-disclosure#I8" \
              "$TMP/cbom-intended.json" "$PQC"
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
expect_output "the failure is I9" "interface-disclosure#I9" \
              "$TMP/cbom-no-marker.json" "$BASE"
expect_output "reported as undeclared, not withheld" "no disclosure marker" \
              "$TMP/cbom-no-marker.json" "$BASE"

# -------------------------------------------------- profile well-formedness ---
# The second conformance target: a profile checked against the methodology.
# Requirements C1 to C17 are stated in the Conformance section.
echo
echo "Profile well-formedness (C1-C17)"
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
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-c7-widening-stages.rules.json"

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
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-relax-mincount.rules.json"
expect_output "and the rejection names the count it lowered" "relaxes 'minCount' (2 -> 1)" \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-relax-mincount.rules.json"
expect_exit   "replacing an identifier form with a presence check is rejected" 3 \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-relax-identifier.rules.json"
expect_output "and the rejection says an obligation may not be dropped" \
              "may not remove one" \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-relax-identifier.rules.json"
expect_check_output "C7 reports the same relaxation" "[FAIL] C7" \
                    "$FIX/profile-relax-mincount.rules.json"

# The counterpart. A check that rejects relaxations is only worth having if it
# still admits the tightenings the mechanism exists for, so assert both.
expect_check_exit "raising the same minimum is accepted"   0 \
                  "$FIX/profile-tighten-constraint.rules.json"
expect_output "the tightening is recorded as a composition note" \
              "minCount tightened, 2 -> 3" \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-tighten-constraint.rules.json"
expect_exit   "and the tightened rule actually bites"      1 \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-tighten-constraint.rules.json"

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
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-c17-unknown-constraint.rules.json"
expect_check_exit   "a vocabulary reference that resolves to nothing is rejected" 1 \
                    "$FIX/profile-c17-unresolved-vocabulary.rules.json"
expect_check_output "C17 is the failing requirement" "[FAIL] C17" \
                    "$FIX/profile-c17-unresolved-vocabulary.rules.json"
expect_exit   "and the validator refuses that profile too" 3 \
              "$M/cbom-pass.cyclonedx.json" "$FIX/profile-c17-unresolved-vocabulary.rules.json"

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
              "$M/cbom-pass.cyclonedx.json" "$TMP/profile-no-constraint.rules.json"
expect_output "and it says the rule can neither pass nor fail" "neither pass nor fail" \
              "$M/cbom-pass.cyclonedx.json" "$TMP/profile-no-constraint.rules.json"

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
              "$M/cbom-pqc-pass.cyclonedx.json" "$L3"
expect_output "and the tightening reaches every entry in the group" \
              "roadmapRef" "$M/cbom-pqc-pass.cyclonedx.json" "$L3"
# The group shell is inherited, not restated, so its coverage still comes from
# the parent. That is the property restating the group would have destroyed.
expect_output_fixed "the group's own coverage is still the parent's" \
              "pqc-migration#G1.1[non-repudiation]" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$L3"

# A guard says when a rule applies. Removing one makes a rule apply always and is
# a tightening; adding or narrowing one is a relaxation that is nearly invisible
# on the page, because the rule is still listed and still reported.
expect_exit   "adding a guard where the base has none is rejected" 3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-guard-added.rules.json"
expect_output "and it says the rule would apply less often" "apply less often" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-guard-added.rules.json"
expect_exit   "narrowing an inherited guard is rejected"     3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-guard-changed.rules.json"
expect_output "and it offers the two legitimate alternatives" "remove the guard" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-guard-changed.rules.json"

# Coverage may be widened and never narrowed: narrowing it is how a staged
# profile becomes the permanent floor decision 0010 exists to prevent.
expect_exit   "narrowing an inherited group's coverage is rejected" 3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-coverage-narrowed.rules.json"
expect_output "and it says a producer would owe fewer answers" "answer for fewer keys" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-q49-coverage-narrowed.rules.json"

# ------------------------------------------------------------ rule numbering ---
# Decision 0011. A rule id is local to the profile that declares it, and the
# citable form is '<profileTag>#<ruleId>'. The point of the scheme is that three
# profiles in one chain can each number from I1 and a reader can still tell the
# three apart, so that is what these assert.
echo
echo "Rule numbering across a family"
L3="$FIX/profile-l3-settlement.rules.json"

expect_output_fixed "the report qualifies an inherited rule id" "interface-disclosure#I1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "a derived profile numbers its own rules from I1" "pqc-migration#I1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "and its product rules from P1, beside the base's P1" "pqc-migration#P1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "the base's own P1 is still there and distinct" "interface-disclosure#P1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output_fixed "a group rule takes the G letter" "pqc-migration#G1.1[encryption]" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
expect_output "the chain is printed above the report" "interface-disclosure -> pqc-migration" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"
# A tightened rule keeps the id, and the tag, of the profile that introduced it.
# That is what lets a stored claim citing it stay meaningful further down.
expect_output_fixed "a tightened rule keeps its introducer's id" \
              "override interface-disclosure#I9" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$PQC"

# Three levels. The fixture declares its own P1 and its own I1, both of which
# are local ids that BOTH ancestors already use.
expect_check_exit "a third-level profile is well-formed" 0 "$L3"
expect_check_output "C15 prints the whole chain" \
                    "interface-disclosure -> pqc-migration -> sector-settlement" "$L3"
expect_output_fixed "the third level numbers from I1 as well" "sector-settlement#I1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$L3"
expect_output_fixed "and all three I1 rules appear in one report" "pqc-migration#I1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$L3"
expect_output_fixed "the failure names the profile that imposed it" \
              "sector-settlement#I1" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$L3"

# Monotonicity holds transitively: a third-level profile may not relax a rule
# the base introduced, even though it is the grandparent rather than the parent.
expect_exit   "relaxing a grandparent rule is rejected" 3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-l3-relaxes-grandparent.rules.json"
expect_output "and the rejection names monotonicity" "monotonic" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-l3-relaxes-grandparent.rules.json"
expect_output_fixed "and names the grandparent's rule, two levels up" \
              "interface-disclosure#I9" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-l3-relaxes-grandparent.rules.json"

# The tag is the one identifier that has to be unique along a chain. It is what
# replaced the old rule-id collision check, so it is checked in both tools.
expect_exit   "a tag an ancestor already uses is rejected" 3 \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-l3-tag-collision.rules.json"
expect_output "and says why a tag must be unique" "unique along the chain" \
              "$M/cbom-pqc-pass.cyclonedx.json" "$FIX/profile-l3-tag-collision.rules.json"
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

"$PY" "$M/validate_cbom.py" "$M/cbom-pqc-pass.cyclonedx.json" \
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
sys.exit(0 if want==got else 1)" "$CLAIM" "$M/cbom-pqc-pass.cyclonedx.json"; then
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
OUT="$("$PY" "$M/validate_cbom.py" "$M/cbom-pqc-pass.cyclonedx.json" "$CLAIM" \
       --verify-claim --profiles-dir "$M" 2>&1)"; RC=$?
if [ "$RC" -eq 0 ] && printf '%s' "$OUT" | grep -q "VERIFIED"; then
  ok "a claim verifies against the document it names"
else
  bad "a claim verifies against the document it names" "expected exit 0 and VERIFIED, got exit $RC"
fi

# Point the same claim at a different document and it must not verify. Exit 5,
# because this is a finding about the claim and not a verdict on the document.
OUT="$("$PY" "$M/validate_cbom.py" "$M/cbom-pqc-fail.cyclonedx.json" "$CLAIM" \
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
OUT="$("$PY" "$M/validate_cbom.py" "$M/cbom-pqc-pass.cyclonedx.json" "$TMP/claim-tampered.json" \
       --verify-claim --profiles-dir "$M" 2>&1)"; RC=$?
if [ "$RC" -eq 5 ] && printf '%s' "$OUT" | grep -q "re-evaluation says"; then
  ok "a verdict that no longer holds is caught"
else
  bad "a verdict that no longer holds is caught" "expected exit 5 and a re-evaluation mismatch, got exit $RC"
fi

# A refused evaluation appears in the claim as refused, carrying no rule results.
# Merging refusal into failure is what T1 forbids, and a claim is where that
# merge would do the most damage.
"$PY" - "$M/cbom-pass.cyclonedx.json" "$TMP" <<'PY'
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
