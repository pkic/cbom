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

| Area | Checks |
|---|---|
| Artifacts | Every JSON artifact parses; the validator is syntactically valid Python. |
| Baseline profile | The conforming CBOM is accepted and its withheld `implementationPurl` is reported as `HELD`; the non-conforming one is rejected on product rule P2. |
| Carrier version bands | A 1.6 copy is accepted and flagged legacy; a 1.5 copy is refused with an explanation. |
| Derived PQC profile | The conforming CBOM is accepted and the base profile resolves; the non-conforming one trips both conditional rules and the tightened inherited rule. |
| Composition | The document that fails the derived profile still conforms to the base, which is the tightening doing its work. A fixture with a relaxing override is rejected with exit code 3. |

## Exit codes from the validator

| Code | Meaning |
|---|---|
| 0 | Conforms |
| 1 | Does not conform |
| 2 | Usage error |
| 3 | Profile error, such as an override that relaxes an inherited rule |

The distinction between 1 and 3 matters to these tests: a CBOM failing a profile
is a normal result, while an invalid profile is a defect in the profile itself.

## Fixtures

`fixtures/profile-invalid-relaxing.rules.json` is deliberately invalid. It
extends the baseline and attempts to lower an inherited rule from MUST to
SHOULD, which monotonic extension forbids. It exists so that the guard against
relaxation is itself tested, and should not be used as a model for a real
profile.

## Adding a test

Two helpers are available in the script. `expect_exit` takes a label, an
expected exit code, a CBOM and a profile. `expect_output` takes a label, a
string the output must contain, a CBOM and a profile. Both print a line to the
summary and set the overall exit status.
