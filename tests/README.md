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
| Carrier version bands | A 1.6 copy is accepted and flagged legacy; a 1.5 copy is refused with an explanation. |
| Derived PQC profile | The conforming CBOM is accepted and the base profile resolves; the non-conforming one trips both conditional rules and the tightened inherited rule. |
| Composition | The document that fails the derived profile still conforms to the base, which is the tightening doing its work. A fixture with a relaxing override is rejected with exit code 3. |
| Profile well-formedness | Both example profiles satisfy C1 to C10, including under `--strict`. One fixture per MUST requirement confirms that each is enforced and that the right requirement is the one reported. |
| SHOULD handling | A profile failing only SHOULD requirements still passes, and `--strict` promotes those failures. |

## Exit codes

`validate_cbom.py`:

| Code | Meaning |
|---|---|
| 0 | Conforms |
| 1 | Does not conform |
| 2 | Usage error |
| 3 | Profile error, such as an override that relaxes an inherited rule |

The distinction between 1 and 3 matters to these tests: a CBOM failing a profile
is a normal result, while an invalid profile is a defect in the profile itself.

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
| `profile-should-gaps.rules.json` | C8, C9, C10 only | Satisfies every MUST and no SHOULD. Also the template the others mutate. |

Each of the C1 to C6 fixtures fails exactly one MUST requirement, so a test can
assert which requirement was reported rather than only that something failed.
The relaxing fixture also fails C1, which is why its test asserts on C7
specifically.

## Adding a test

Two helpers are available in the script. `expect_exit` takes a label, an
expected exit code, a CBOM and a profile. `expect_output` takes a label, a
string the output must contain, a CBOM and a profile. Both print a line to the
summary and set the overall exit status.
