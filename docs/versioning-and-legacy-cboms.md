# Handling older CBOM files

> **Status:** Illustrative design note for the PKIC CBOM Profiles Working Group.
> Practitioner-oriented; not normative. Uses the nginx interface-disclosure example.

"Older CBOM files" is ambiguous until you separate the versions that actually move. Three
independent things carry a version, and each ages differently.

## 1. Three version axes

| Axis | Example | Who owns it | Moves when |
|---|---|---|---|
| **Carrier format** | CycloneDX `specVersion` 1.6 → **1.7** | CycloneDX / Ecma (ECMA-424) | the SBOM/CBOM standard revises |
| **Profile** | `interface-disclosure` v0.1 → v0.2 | the profile author (PKIC / a sector) | the *requirements* change |
| **CBOM content revision** | a product's CBOM `version` / `serialNumber` over time | the CBOM producer | the product or a re-scan changes |

Conflating these is the usual mistake. A CBOM can be *current* on one axis and *old* on
another: a freshly generated CBOM (new content revision) may still be serialized in
CycloneDX 1.6 (old carrier), and evaluated against profile v0.2 (new rules).

**A conformance claim must cite all three:** *"conforms to `interface-disclosure` v0.1,
evaluated against a CycloneDX 1.7 CBOM, content revision 3."* Anything less is not reproducible.

## 2. Carrier-format version (the CycloneDX 1.6 → 1.7 case)

This is the axis this update touches. The example now targets **CycloneDX 1.7**.

**Recommendation: accept a declared range, don't hard-pin.** The profile declares which
carrier versions it accepts, so old CBOMs are handled deliberately rather than by accident.
In the rules file:

```json
"appliesTo": { "cyclonedx": { "min": "1.6", "tested": "1.7" } }
```

The validator (`validate_cbom.py`, `check_format`) then applies a three-band policy:

| CBOM `specVersion` | Band | Behaviour |
|---|---|---|
| below `min` (e.g. 1.5) | **unsupported** | **refuse** — do not pretend to evaluate a model the adapter cannot read. Tell the producer to upgrade. |
| `min` ≤ v < `tested` (e.g. 1.6) | **legacy** | **accept + warn** — evaluate normally, flag that the profile was authored against a newer carrier. |
| v == `tested` (1.7) | **target** | accept silently. |
| above `tested` | **newer** | accept + note; a human should review whether new fields change anything. |

You can see all four bands by running the validator against 1.7, a 1.6 copy, and a 1.5 copy.

**Why a range and not "latest only":** rejecting every 1.6 CBOM the day 1.7 ships would
invalidate a whole supply chain's existing artifacts overnight. A range gives a migration
window. **Why not "anything goes":** below `min` the crypto object model may differ enough
that silent evaluation would give a false verdict — worse than an honest refusal.

**Adapters read the common subset.** The format adapter deliberately reads fields shared by
1.6 and 1.7 (protocol type/version, cipher suites, referenced algorithms, certificate
signature ref). That is what makes a 1.6 CBOM validate against a 1.7-targeted profile at all.
Where 1.7 adds capability (below), prefer it when present and fall back otherwise.

## 3. Normalization: what CycloneDX 1.7 buys you

1.7 introduced the **Cryptography Registry** — an authoritative, machine-readable list of
algorithm families with stable identifiers. It exists precisely to fix the "one vendor writes
`AES256`, another writes `AES_256_CBC`" problem that breaks automated comparison.

Implication for older CBOMs:

- **1.7 CBOMs** can anchor each algorithm to a registry identifier — normalization is intrinsic.
- **1.6 (and older) CBOMs** carry free-text algorithm names. To compare them reliably, apply a
  **name-normalization map** in the adapter (canonicalize `AES256`, `AES-256-GCM`,
  `AES_256_GCM` → one registry id) *before* the rules run. Keep that map versioned alongside
  the profile.

This is the "syntactic normalization" the GSMA telecom CBOM draft calls for, made concrete:
normalize at the adapter boundary, so the rules only ever see canonical identifiers.

## 4. Prefer upgrade over rejection

For a legacy-but-supported CBOM, offer a **one-way mechanical upgrade** rather than bouncing it:

1. bump `specVersion` to the target,
2. attach registry identifiers where the name map resolves them,
3. record provenance (a note that the CBOM was machine-upgraded, from what version, by what tool).

Upgrading is a data transform, not a re-attestation — it must never *add* cryptographic facts
that weren't in the original, only re-encode existing ones. Anything unresolved stays flagged.

## 5. Profile-version ageing (the other axis)

When a profile tightens (say v0.2 adds a rule requiring `pqcPosture` ∈ {`hybrid`,`pqc`} for
`service` interfaces), existing CBOMs don't become "wrong" — they were evaluated against the
profile *in force at the time*. Handle it like any policy change:

- **Evaluate against a stated profile version.** Never silently re-interpret an old CBOM under
  new, stricter rules; pin the profile version in the conformance claim.
- **Grace windows over hard cutoffs.** A newly raised bar should emit `warn` (not `fail`) for the
  now-deprecated-but-formerly-allowed state until a published date, then flip to `fail`. Encode
  the cutoff in the rule so the change is automatic and auditable.
- **Deprecate, don't delete, vocabulary.** If `interfaceType` values change, keep old values
  recognized (mapped to their replacement) for at least one profile major version.

## 6. Content-revision ageing (staleness)

The CBOM's own `version`/`serialNumber`/`timestamp` sequence is the audit trail the PQC
progress-tracking use case relies on. Two cheap guards:

- **Freshness policy:** a consumer may require the CBOM `timestamp` to be within N days of the
  artifact it describes, else warn — a syntactically perfect CBOM can still be stale.
- **Supersedence:** a newer content revision for the same product supersedes older ones; keep
  the history, evaluate the latest.

## 7. Summary recommendation

Make version handling explicit and machine-checkable, on all three axes:

1. Profiles declare an `appliesTo` carrier range; validators enforce the min/tested/newer bands.
2. Normalize algorithm identity at the adapter (registry ids in 1.7; a versioned name map for 1.6).
3. Upgrade legacy CBOMs mechanically instead of rejecting them, preserving provenance.
4. Pin profile version in every conformance claim; tighten rules behind dated grace windows.
5. Track content-revision freshness and supersedence so "old" never silently means "wrong."
