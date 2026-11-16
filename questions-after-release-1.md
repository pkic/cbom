# Carried past Release 1

Items that are not closed by the Release 1 publications and are carried into the next phase of
work. This file starts the register that replaces `open-questions.md` after the line (record 0027).
`open-questions.md` is kept as history. Every item here was recorded on 16 November 2026, during
the closing pass over Publications 1 to 4.

Each item says where it came from, what is already settled about it, and what is left.

## Methodology

**R2-01 — An attribute for the vendor's intrinsic data.**
From: Data Exposure; Publication 2, 11.6. Settled: the vendor states the data an interface exists to
carry for the product's own operation (credentials, keys, tokens, configuration); the operator states
the conveyed payload in its own register. Left: the attribute itself, for example how long a
credential stays valid, and the profile that requires it.

**R2-02 — Grace periods in the rules-file format and the validator.**
From: Q15. Settled: a tightened rule takes effect after a grace period the profile recommends, and a
contract may set a different one. Left: a field in the rules-file format and support in
`validate_cbom.py`, which today report a tightened rule as a failure at once.

**R2-03 — The claim format's `assessed` field.**
From: the verb convention (a tool evaluates, a rule checks, a claim is verified). Left: renaming the
field to `evaluated`, which changes the claim format version.

## Profiles and tooling

**R2-04 — `verifierPopulation` and `trustDomain` in PQC Migration Extended.**
From: Publication 2, 7.4 (provisionally decided at SHOULD, on the `entity-authentication` and
`non-repudiation` purposes). Left: the validator and `check_profile.py` must let a derived profile
add members to an inherited group before the rules can be written.

**R2-05 — Two checker gaps in PQC Migration Extended.**
From: the profile's pending-tooling notes. Left: a `refersTo` constraint for I8, and reading
`cryptographicPurposes` in the scope-narrowing check.

## Use cases

**R2-06 — The substation system overlay.**
From: record 0024. Settled: the overlay's rules (S1 to S5) and a `system` subject type accepted only
by the overlay. Left: the rules file, the subject type in the validator, and reporting of cited
verdicts beside the overlay's own (Q68).

**R2-07 — The rest of the substation worked example.**
From: record 0024. Left: records for the bay controller, station gateway, station server and WAN
router, and the system document; review by a protection IED supplier and a transmission or
distribution operator.

**R2-08 — `usage` as a general facility.**
From: record 0024. Settled: `usage` stays in the substation overlay. Left: whether other derived
documents need it.

**R2-09 — The IoT device estate profile.**
From: the IoT use case. Settled: the subject is a device model (Q62); a hard limit is recorded in
`resourceBound` (Q63); the profile extends the change core (Q64); who can install firmware is
`updateAuthority` (Q65). Left: the rules file; whether `resourceBound` is MUST, and with it
`integrationConstraints`; `updateSupportStatus`, `keyProvisioning` and `cryptoTerminationPoint`;
values of `providerLocation` that fit devices; whether the physical attack surface is in scope; the
worked interface.

**R2-10 — A transparency-service annex for shared CBOMs.**
From: the Assurance use case. Settled: a digest is SHA-256 over the published file, byte for byte.
Left: whether an informative annex describes transparency services.
