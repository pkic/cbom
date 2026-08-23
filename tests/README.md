# tests/

Automated checks for the methodology's example profiles, CBOMs and validator.

## Running them

```bash
bash tests/run-profile-tests.sh
```

Python 3 is the only requirement. Set `PYTHON` to use a specific interpreter:

```bash
PYTHON=python3.12 bash tests/run-profile-tests.sh
```

Exit status is 0 when every test passes. CI runs the same script on any change
under `docs/methodology/`, so a broken example fails visibly rather than sitting
on the published site.

## What is covered

Two of the three conformance targets in the Conformance section are covered
here. A **CBOM document** is checked against a profile by `validate_cbom.py`,
and a **profile** is checked against the methodology by `check_profile.py`. The
third target, an evaluation tool checked against the methodology's semantics, is
what this suite is an early form of.

| Area | Checks |
|---|---|
| Artifacts | Every JSON artifact parses; both Python tools are syntactically valid. |
| Baseline profile | The conforming CBOM is accepted and its withheld `implementationPurl` is reported as `HELD`; the non-conforming one is rejected on product rule P2. |
| Carrier version bands | 1.6 and 1.8 copies are accepted and flagged legacy and newer; a 1.5 copy is refused with exit 4, a REFUSED verdict, no rule results, and a JSON report marking it unassessed. Four bands need four inputs, which is why a 1.8 copy is generated. |
| Derived PQC profile | The conforming CBOM is accepted and the base profile resolves; the non-conforming one trips both conditional rules and the tightened inherited rule. |
| Composition | The document that fails the derived profile still conforms to the base, which is the tightening doing its work. A fixture with a relaxing override is rejected with exit code 3. |
| Withholdable MUST | A withheld marker satisfies baseline rule I9; the same document with the marker stripped does not, and is reported as undeclared rather than withheld. This is the only combination in which the disclosure model changes a verdict, and before profile v0.3 no rule exercised it. |
| Capability per cryptographic purpose | The conforming migration document states a different status for key establishment and for entity authentication on one interface, which is the position a single per-interface status could not express. The conditional blocker resolves inside a purpose entry. A missing entry is reported against the purpose it is missing for, whether that purpose is in scope or deferred, and stripping the deferred purposes from a conforming document breaks conformance — that obligation is the ratchet, so it is asserted rather than assumed. |
| Accepted lifecycle stages | The conforming migration document, with one interface moved to the `intended` stage, fails rule I8 against the migration profile and is reported as a stage the profile does not accept. The same document still conforms to the baseline, which accepts all four stages, so the narrowing belongs to the derived profile rather than to the vocabulary. |
| Profile well-formedness | Both example profiles satisfy C1 to C14, including under `--strict`. One fixture per MUST requirement confirms that each is enforced and that the right requirement is the one reported. |
| SHOULD handling | A profile failing only SHOULD requirements still passes, and `--strict` promotes those failures. |

## Exit codes

`validate_cbom.py`:

| Code | Meaning |
|---|---|
| 0 | Conforms |
| 1 | Does not conform |
| 2 | Usage error |
| 3 | Profile error, such as an override that relaxes an inherited rule |
| 4 | Refused: the carrier version is below the profile's minimum, so nothing was assessed |

The distinction between 1 and 3 matters to these tests: a CBOM failing a profile
is a normal result, while an invalid profile is a defect in the profile itself.
The distinction between 1 and 4 matters more, because the Conformance section
makes it a MUST and the suite previously asserted the wrong one: a refused
document was never assessed, and may be perfectly adequate.

`check_profile.py`:

| Code | Meaning |
|---|---|
| 0 | Well-formed |
| 1 | Not well-formed, or a SHOULD failed under `--strict` |
| 2 | Usage error, or the file could not be read or parsed |

## Fixtures

Every fixture is deliberately defective and none should be copied as a model for
a real profile.

| Fixture | Fails | Why it exists |
|---|---|---|
| `profile-invalid-relaxing.rules.json` | C7, and exit 3 from the validator | Extends the baseline and lowers an inherited rule from MUST to SHOULD, which monotonic extension forbids. |
| `profile-c1-no-objective.rules.json` | C1 | States no consumer and no decision, so there is no standard against which to judge whether it asks for the right things. |
| `profile-c2-no-applies-to.rules.json` | C2 | Declares no carrier acceptance range, leaving the format gate with no basis. |
| `profile-c3-names-instance.rules.json` | C3 | Requires an interface of type `nginx-https` and constrains `interfaceId`. Reproduces the defect corrected by decision 0001. |
| `profile-c4-no-withholdable.rules.json` | C4 | A rule that does not say whether withholding satisfies it, so the answer would depend on the validator's default. |
| `profile-c5-naming.rules.json` | C5 | Uses the rejected `Current` suffix, and a `Supported` attribute that is not list-valued. |
| `profile-c6-judgement.rules.json` | C6 | Requires `pqcPosture`, a derived judgement. Reproduces the attribute removed by decision 0002. |
| `profile-c7-diverging-block.rules.json` | C7 | Extends the baseline and restates `disclosure` with a different marker prefix. Nothing is relaxed and no rule changes, but the base's prefix is overridden silently and every marker would stop being recognised. |
| `profile-c7-widening-stages.rules.json` | C7, and exit 3 from the validator | Extends the migration profile and accepts the `intended` stage that its base rejects. Widening the accepted stages is a relaxation: a document reporting only intentions would conform here while failing the base. |
| `profile-c1-no-decision-options.rules.json` | C1 | States a consumer and a decision, but the decision is "to understand our cryptographic position" and no options are listed. The failure the action-choice test in Method step 1 exists to catch. |
| `profile-c11-no-scope.rules.json` | C11 | Declares no `scope`, so it says neither what kind of subject it describes nor which lifecycle stages it accepts, and a document reporting nothing but intentions would conform. |
| `profile-c12-capability-unpaired.rules.json` | C12 | Orientation `both`, requiring `keyExchangeSupported` and not `keyExchange`, so a consumer sees what an interface could negotiate and never what it does. |
| `profile-c12-inventory-capability.rules.json` | C12 | Orientation `inventory` while requiring `capabilityStatus`, so statements about a future state arrive under a label that promises present state. |
| `profile-c13-uncovered-purposes.rules.json` | C13 | A group rule covering only the purposes in scope, so a supplier conforms while saying nothing at all about the four the profile deferred. The floor a staged profile is meant not to become. |
| `profile-c13-unkeyed-group.rules.json` | C13 | A group keyed by a vocabulary the profile does not declare. It requires an entry for no keys, so every document passes it and the rule reads as satisfied — silent success rather than a loud failure. |
| `profile-should-gaps.rules.json` | C8, C9, C10 only | Satisfies every MUST and no SHOULD. Also the template the others mutate. |

Every fixture fails exactly one MUST requirement, so a test can assert which
requirement was reported rather than only that something failed. Keeping that
property is the reason each fixture carries a `scope` object and a set of
`decisionOptions` it does not otherwise need: without them it would fail C11 and
C1 as well as the requirement it exists to exercise.

## Adding a test

Two helpers are available in the script. `expect_exit` takes a label, an
expected exit code, a CBOM and a profile. `expect_output` takes a label, a
string the output must contain, a CBOM and a profile. Both print a line to the
summary and set the overall exit status.
