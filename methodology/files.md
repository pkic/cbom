---
title: Files
sideMenu: true
weight: 23
aliases:
- /cbom/methodology/files.html
linkTitle: Files
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The machine-readable files that make up the example: the profile rules file, the example CBOMs and the validator. The commands below reproduce every conformance result shown in this documentation.

## Artifacts

| File | Description |
| --- | --- |
| [profile-interface-enumeration.rules.json](../../docs/methodology/profile-interface-enumeration.rules.json) | The entry profile of the interface family: the shallowest set of rules that still produces a usable inventory record. See [Maturity](../maturity/) |
| [profile-interface-disclosure.md](https://github.com/pkic/cbom/blob/main/docs/methodology/profile-interface-disclosure.md) | Prose profile specification (product-level and per-interface rules) |
| [profile-interface-disclosure.rules.json](../../docs/methodology/profile-interface-disclosure.rules.json) | Machine-readable rules, including the `appliesTo` version range |
| [profile.schema.json](../../docs/methodology/profile.schema.json) | The schema for a rules file. A third party can use it to validate a profile without our checker. The schema does not replace requirements C1 to C17. A schema can check that `objective` has a `decision` string, but not whether the decision is one a consumer could act on |
| [claim.schema.json](../../docs/methodology/claim.schema.json) | The schema for a conformance claim. It includes the two consistency rules that a schema can enforce: a refused entry carries no rule results, and an entry that claims conformance may not list a failed MUST rule |
| [claim-example.json](../../docs/methodology/claim-example.json) | A worked example of a claim that covers both example profiles at once, bound to `cbom-pqc-pass` by digest |
| [mapping-cyclonedx-spdx.md](https://github.com/pkic/cbom/blob/main/docs/methodology/mapping-cyclonedx-spdx.md) | Complete requirement-to-format mapping |
| [cbom-pass.cyclonedx.json](../../docs/methodology/cbom-pass.cyclonedx.json) | Conforming example CBOM (CycloneDX 1.7) |
| [cbom-fail.cyclonedx.json](../../docs/methodology/cbom-fail.cyclonedx.json) | Non-conforming example. It omits the management interface |
| [cbom-disclosure.cyclonedx.json](../../docs/methodology/cbom-disclosure.cyclonedx.json) | Non-conforming example exercising all four disclosure outcomes on one interface: a withheld library (permitted), an encryption algorithm declared unknown, an undeclared authentication algorithm, and a key exchange disclosed normally |
| [cbom-noadmin.cyclonedx.json](../../docs/methodology/cbom-noadmin.cyclonedx.json) | Conforming example with no management interface at all: a library with no configuration surface, It satisfies product rule P2 by stating that there is no management interface, rather than by declaring one |
| [cbom-entry-fail.cyclonedx.json](../../docs/methodology/cbom-entry-fail.cyclonedx.json) | Roughly what a scanner produces when it is not working to any profile. It is valid CycloneDX, but it falls below even the entry profile. It identifies no subject, states no completeness, classifies no interface and says nothing about where the reading came from |
| [profile-pqc-migration.rules.json](../../docs/methodology/profile-pqc-migration.rules.json) | The PQC migration profile, derived from the baseline via `extends` |
| [cbom-pqc-pass.cyclonedx.json](../../docs/methodology/cbom-pqc-pass.cyclonedx.json) | Conforming example for the migration profile; three interfaces at different readiness stages |
| [cbom-pqc-fail.cyclonedx.json](../../docs/methodology/cbom-pqc-fail.cyclonedx.json) | Non-conforming example that exercises both conditional rules and the tightening of an inherited rule |
| [validate\_cbom.py](https://github.com/pkic/cbom/blob/main/docs/methodology/validate_cbom.py) | Version-aware validator with profile composition. Checks a document against a profile |
| [check\_profile.py](https://github.com/pkic/cbom/blob/main/docs/methodology/check_profile.py) | Well-formedness checker. Checks a profile against requirements C1 to C17 of [Conformance](../conformance/) |
| [versioning-and-legacy-cboms.md](https://github.com/pkic/cbom/blob/main/docs/methodology/versioning-and-legacy-cboms.md) | Treatment of older CBOM files |

## Running the validator

```
# conforms (CycloneDX 1.7)
python validate_cbom.py cbom-pass.cyclonedx.json profile-interface-disclosure.rules.json

# does not conform; fails product rule P2 (no management interface)
python validate_cbom.py cbom-fail.cyclonedx.json profile-interface-disclosure.rules.json

# the same document at the family's entry depth, which does not require a
# management interface: conforms. See Maturity.
python validate_cbom.py cbom-fail.cyclonedx.json profile-interface-enumeration.rules.json

# JSON output, for integration into a continuous-integration gate
python validate_cbom.py cbom-pass.cyclonedx.json profile-interface-disclosure.rules.json --json
```

## Reproducing the version bands

```
# four bands need four inputs: 1.7 is the tested version, and these are the rest
python - <<'PY'
import json
b = json.load(open("cbom-pass.cyclonedx.json"))
for v in ("1.8", "1.6", "1.5"):
    b["specVersion"] = v
    json.dump(b, open(f"cbom-{v}.json", "w"))
PY
python validate_cbom.py cbom-pass.cyclonedx.json profile-interface-disclosure.rules.json  # target:  exit 0
python validate_cbom.py cbom-1.8.json profile-interface-disclosure.rules.json   # newer:   accepted, review advised, exit 0
python validate_cbom.py cbom-1.6.json profile-interface-disclosure.rules.json   # legacy:  accepted with a warning,  exit 0
python validate_cbom.py cbom-1.5.json profile-interface-disclosure.rules.json   # refused: not assessed,            exit 4
```

The last of these commands is the most useful one to run. A refusal is not a failure. The document was never assessed, so the validator exits with 4 rather than 1 and reports no rule results for it. A pipeline that treats any non-zero exit code as a rejection will penalise a supplier for the age of its carrier format. The distinct exit code exists to prevent that.

## The derived profile

The PQC migration profile extends the baseline, so evaluating against it also evaluates every baseline rule. The validator resolves the base, applies the overrides, and rejects any override that would relax an inherited rule.

```
# conforms
python validate_cbom.py cbom-pqc-pass.cyclonedx.json profile-pqc-migration.rules.json

# does not conform: five failures, of three kinds
python validate_cbom.py cbom-pqc-fail.cyclonedx.json profile-pqc-migration.rules.json
```

Read the failing document alongside its verdict. Two failures come from conditional rules. In the first, an interface claims enablement by software update without naming the version (`pqc-migration#I5`). In the second, an interface declares a capability committed for key establishment without saying what blocks it (`pqc-migration#G1.2`). Two more failures come from the group rule. One is a purpose that the profile takes in scope but that has no entry at all. The other is a purpose that the profile defers, which also has no entry. A deferred purpose still requires a status. The last failure comes from the extension itself. The document's interconnect interface withholds `implementationPurl`, which the baseline permits. Evaluated against the baseline alone, the document conforms. It fails here only because the derived profile no longer allows that rule to be satisfied by withholding the value.

```
# the same document against the base profile, which permits the withheld value
python validate_cbom.py cbom-pqc-fail.cyclonedx.json profile-interface-disclosure.rules.json
```

## Checking a profile

A profile can itself be checked, against requirements C1 to C17 of [Conformance](../conformance/). C1 to C7 and C11 to C17 are MUST requirements and determine the result. C8 to C10 are reported as warnings unless `--strict` is given.

```
# all three example profiles are well-formed
python check_profile.py profile-interface-enumeration.rules.json
python check_profile.py profile-interface-disclosure.rules.json
python check_profile.py profile-pqc-migration.rules.json

# require the SHOULD material as well: exclusions, companion artifacts, changelog
python check_profile.py profile-interface-disclosure.rules.json --strict

# machine-readable findings
python check_profile.py profile-pqc-migration.rules.json --json
```

The test suite carries one deliberately defective profile per MUST requirement, so that each check is itself tested. See `tests/fixtures/` and `tests/README.md` in the repository.

The [Demo](../demo/) section performs the same evaluation in the browser for the baseline profile, over the four baseline documents above. It reads the rules file rather than a copy of it, and `tests/check-demo.py` requires its results to match this validator's, rule by rule, on all four. Standards, regulation and specifications cited across this documentation are listed in the [reference register](../../references/).

[← Related Work](../related-work/) [Next: the reference register →](../../references/)
