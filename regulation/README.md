# Regulatory sufficiency register

This register records, for each regulation or policy, whether a CBOM that
conforms to a named profile gives a reader enough data to show that the
regulation is met. Publication 3, section 16.4, describes the method. This
folder holds the data, which changes whenever an instrument changes, so it is
kept outside the release as a living register.

## Files

| Path | Contents |
|---|---|
| `catalogue/*.yaml` | One file for each instrument: its source, and one entry for each question a reader must answer to show compliance |
| `coverage.md` | The coverage matrix, generated from the catalogue. Do not edit it by hand |
| `../tools/build_regulatory_coverage.py` | Writes `coverage.md` |
| `../tests/check-regulation.py` | Checks the catalogue against the profiles, and checks that `coverage.md` is up to date |

To regenerate the matrix after editing the catalogue:

```
python3 tools/build_regulatory_coverage.py
```

## How an instrument is recorded

An instrument is broken down into **evidence questions**. An evidence question
is something a reader must be able to answer to show that one clause is met,
for example "Which key-establishment algorithms does each interface use?" A
clause that asks for several things becomes several questions.

Each question is then mapped to the profile rules that supply the data, and is
tested at three levels:

| Level | The question it answers |
|---|---|
| `expressible` | Can the methodology's model express the facts the question needs? |
| `required` | Does a named profile require those facts? |
| `evaluable` | Can a policy compute the answer from those facts without a person's judgement? |

Each level is answered `yes`, `partly` or `no`. Keeping the levels apart stops
a gap in one profile's obligations from being reported as a gap in the model.

Each question then gets one verdict:

| Verdict | Meaning |
|---|---|
| `sufficient` | A CBOM that conforms to the entry profile named in the entry answers the question |
| `deeper-profile` | The model has the facts, but only a deeper or more specific profile requires them. A reader must ask for that profile by name |
| `partial` | The CBOM supplies part of the answer. The rest must come from the operator, for example how long data must stay confidential, or which systems are high risk |
| `judgement` | The CBOM supplies the facts, but the answer is a judgement, such as whether a mechanism is "state of the art". The judgement belongs in a versioned policy, not in the CBOM (decision 0002) |
| `out-of-scope` | The question is about an organisation or a process, not about the cryptography of a product, service or system. No CBOM can answer it |
| `open` | The source text that defines the question has not been published yet |

A question with a gap names it under `gap`. A gap is either a candidate
attribute for the methodology, or a plain statement of why the question stays
outside a CBOM.

## How the sources were checked

Every question records how its clause was checked:

| Value | Meaning |
|---|---|
| `primary` | Checked against the official text of the instrument |
| `eu-report` | Checked in the verification passes of the working group's report to the European Commission |
| `secondary` | Checked against a secondary source only. To be confirmed against the official text before the register is cited |

The register paraphrases the instruments in its own words. It is not legal
advice, and it does not interpret what an instrument requires of any
particular organisation.
