# Handling older CBOM files

> **Status:** Illustrative design note for the PKIC CBOM Profiles Working Group.
> Descriptive; not normative. Uses the nginx interface-disclosure example.

The term "older CBOM files" is ambiguous until the versions it may refer to are
separated. Three items each carry a version, and each changes independently.

## 1. Three version axes

| Axis | Example | Owner | Changes when |
|---|---|---|---|
| **Carrier format** | CycloneDX `specVersion` 1.6 → **1.7** | CycloneDX / Ecma (ECMA-424) | the SBOM/CBOM standard is revised |
| **Profile** | `interface-disclosure` v0.2 → v0.3 | the profile author (PKIC or a sector) | the requirements change |
| **CBOM content revision** | a product's CBOM `version` / `serialNumber` over time | the CBOM producer | the product or a re-scan changes |

Conflating these axes is a common error. A CBOM may be current on one axis and older on
another: a newly generated CBOM (a new content revision) may still be serialized in
CycloneDX 1.6 (an older carrier) and evaluated against profile v0.3 (newer rules).

A conformance claim must reference all three: for example, "conforms to `interface-disclosure`
v0.3, evaluated against a CycloneDX 1.7 CBOM, content revision 3." A claim that omits any of
the three is not reproducible.

## 2. Carrier-format version (the CycloneDX 1.6 to 1.7 case)

This is the axis addressed by the present update; the example now targets CycloneDX 1.7.

**Recommendation: accept a declared range rather than a single fixed version.** The profile
declares the carrier versions it accepts, so that older CBOMs are handled explicitly. In the
rules file:

```json
"appliesTo": { "cyclonedx": { "min": "1.6", "tested": "1.7" } }
```

The validator (`validate_cbom.py`, `check_format`) applies a four-band policy:

| CBOM `specVersion` | Band | Behaviour |
|---|---|---|
| below `min` (for example 1.5) | **unsupported** | Refuse. The adapter may be unable to read the model, so it must not evaluate it. The producer is advised to upgrade the CBOM. |
| `min` ≤ v < `tested` (for example 1.6) | **legacy** | Accept with a warning. Evaluate normally, and record that the profile was authored against a newer carrier. |
| v == `tested` (1.7) | **target** | Accept. |
| above `tested` | **newer** | Accept with a note; a reviewer should assess whether new fields affect the result. |

The four bands can be observed by evaluating the CBOM at 1.7 and at 1.8, 1.6 and 1.5 copies. Three copies reach only three bands; `newer` needs a carrier above the tested version.

A declared range is preferred to a single fixed version because rejecting every 1.6 CBOM on the
day 1.7 is published would invalidate a supply chain's existing artifacts; a range provides a
migration window. An unrestricted range is not appropriate because, below `min`, the
cryptographic object model may differ sufficiently that evaluation could produce an incorrect
verdict, which is less acceptable than an explicit refusal.

**Adapters read the common subset.** The format adapter reads fields shared by 1.6 and 1.7
(protocol type and version, cipher suites, referenced algorithms, and the certificate signature
reference). This is what allows a 1.6 CBOM to be evaluated against a 1.7-targeted profile.
Where 1.7 adds capability, as described below, it is preferred when present, with a fallback
otherwise.

## 3. Normalization provided by CycloneDX 1.7

Version 1.7 introduces the Cryptography Registry, an authoritative, machine-readable list of
algorithm families with stable identifiers. It addresses the situation in which one producer
records `AES256` and another records `AES_256_CBC`, which prevents automated comparison.

Implications for older CBOMs:

- **1.7 CBOMs** can anchor each algorithm to a registry identifier; normalization is intrinsic.
- **1.6 and earlier CBOMs** carry free-text algorithm names. To compare them reliably, apply a
  name-normalization map in the adapter (canonicalizing `AES256`, `AES-256-GCM`, and
  `AES_256_GCM` to a single registry identifier) before the rules are evaluated. Maintain that
  map under version control alongside the profile.

This is the syntactic normalization identified in the GSMA telecommunications CBOM draft:
normalization is performed at the adapter boundary, so that the rules operate only on canonical
identifiers.

## 4. Upgrade in preference to rejection

For a legacy but supported CBOM, a one-way mechanical upgrade is preferable to rejection:

1. raise `specVersion` to the target;
2. attach registry identifiers where the name map resolves them;
3. record provenance (a note that the CBOM was upgraded by a tool, from which version).

Upgrading is a data transformation, not a re-attestation; it must not add cryptographic facts
that were not present in the original, but only re-encode existing facts. Any value that cannot
be resolved remains flagged.

## 5. A major carrier revision: CycloneDX 2.0

CycloneDX 2.0 is in development, with Ecma ratification expected around the end of 2026. The
observations below were made against the development branch `2.0-dev-safety` (commit
`78f96fe`, 20 September 2026). Field names may still change, and this section should be
revisited against the released schema.

**The four-band policy assumes the common subset still reads.** A `newer` CBOM is accepted
with a note because the adapter can still read the fields shared with the tested version. That
assumption holds for 1.6 to 1.7. It does not hold for 2.0. A CycloneDX 1.7 worked example fails
validation against the 2.0 schema with 19 errors, and a 2.0 document cannot be read by a 1.7
adapter. Until an adapter for 2.0 exists, a validator should treat a change of major version as
**unsupported** rather than **newer**.

**The changes are structural, and the mechanical upgrade is small.** Six changes made the
example valid 2.0 without altering any profile attribute:

| CycloneDX 1.7 | CycloneDX 2.0 |
|---|---|
| `bomFormat` | `specFormat` |
| `services[]` | `components[]` with `type: "service"` |
| `purl` on a component | `identifiers[]`, each claimed by a declared party |
| `supplier`, `manufacturer` on a component | `parties[]`, each with a role |
| `cryptoRefArray`, `algorithmRef`, `signatureAlgorithmRef`, `subjectPublicKeyRef` | `relatedCryptographicAssets[]` |
| `curve` (free text, deprecated in 1.7) | `ellipticCurve` (enumerated, for example `other/Curve25519`) |

`dependencies[].provides`, the protocol type enumeration and the cipher-suite structure are
unchanged. The upgrade therefore follows section 4: it re-encodes existing facts and adds none.

**What changes for the profiles.**

- **Paths, not attributes.** Rules that read a Package URL, a supplier or a service need new
  paths. Attribute names, levels and vocabularies do not change.
- **New native homes.** A `certifications` array on any component (standard, identifier, level,
  issuer, dates and URL) can carry module validation and product certification, including schemes
  that the algorithm-level `certificationLevel` enumeration does not list. An `agility` object
  (configuration source, whether the configuration is negotiated, and the change mechanism)
  partly covers enablement and negotiation. `rotation` on keys and `renewal` on certificates
  describe how those are replaced. The profile's capability-by-purpose group still has no native
  home.
- **Supported and in-use algorithms.** The mapping currently reads `cipherSuites` as supported
  and `cryptoRefArray` as in use. `cryptoRefArray` is removed, so the in-use reading moves to
  `relatedCryptographicAssets`.
- **Migration management is a risk register.** CycloneDX 2.0 adds a root `risks` array. A risk
  can reference a cryptographic asset and carries a status and an owner; each response carries a
  strategy, controls, a status, an owner and a target date. These are judgements, not product
  facts. Decision 0002 places judgements in policy, and decision 0007 states forward-looking
  capability as a status and a blocker rather than a date. They belong in an operator's CBOM for
  its own estate, not in a supplier's conformance claim.
- **Perspectives.** CycloneDX 2.0 adds perspectives: JSONPath expressions, each marked required,
  recommended, optional or informative. A perspective cannot express conditions, vocabularies,
  groups or withholding, so it does not replace a profile's rules file. It could accompany one,
  so that generic tooling can check which fields a profile expects.
- **Terminology.** CycloneDX 2.0 uses "profile" for reusable data and threat characterizations,
  and its blueprint model defines an "interface" with types such as `rest` and `cli`. Neither is
  the concept used here. Documents that discuss both should say "PKIC CBOM profile".
- **The edge gap remains.** The blueprint model has zones, boundaries and flows with a source
  and a destination, but it models a deployed system for threat analysis. Its protocols are free
  text and its encryption is a boolean. It does not represent a product's cryptographic
  interface.

**Position pending working-group review:** CycloneDX 1.7 remains the tested carrier for the
current profiles; 2.0 is added to the mapping and to `appliesTo` once it is ratified and an
adapter exists.

## 6. Profile-version change (the second axis)

When a profile is tightened (for example, v0.3 raises `implementationPurl` from SHOULD to MUST,
keeping it withholdable), existing CBOMs do not become incorrect; they were
evaluated against the profile in force at the time. This is handled as any policy change:

- **Evaluate against a stated profile version.** An older CBOM must not be re-interpreted under
  newer, stricter rules without notice; the profile version is pinned in the conformance claim.
- **Use grace windows rather than immediate cutoffs.** A newly raised requirement should emit a
  warning, rather than a failure, for the now-deprecated but formerly permitted state until a
  published date, after which the result becomes a failure. The cutoff is encoded in the rule,
  so that the change is automatic and auditable.
- **Deprecate, rather than delete, vocabulary.** If `interfaceType` values change, retain
  recognition of the former values (mapped to their replacements) for at least one profile
  major version.

## 7. Content-revision change (staleness)

The CBOM's own `version`, `serialNumber`, and `timestamp` sequence constitutes the audit trail
on which the PQC progress-tracking use case relies. Two controls apply:

- **Freshness policy:** a consumer may require the CBOM `timestamp` to be within a defined
  interval of the artifact it describes, and otherwise emit a warning; a syntactically valid
  CBOM may still be stale.
- **Supersedence:** a newer content revision for the same product supersedes older ones. The
  history is retained, and the latest revision is evaluated.

## 8. Summary of recommendations

Version handling should be explicit and machine-checkable on all three axes:

1. Profiles declare an `appliesTo` carrier range, and validators enforce the minimum, tested,
   and newer bands.
2. Algorithm identity is normalized at the adapter (registry identifiers in 1.7; a versioned
   name map for 1.6).
3. Legacy CBOMs are upgraded mechanically rather than rejected, with provenance preserved.
4. The profile version is pinned in every conformance claim, and rules are tightened behind
   dated grace windows.
5. Content-revision freshness and supersedence are tracked, so that an older revision is not
   treated as incorrect without cause.
6. A change of carrier major version, such as CycloneDX 2.0, is treated as unsupported until an
   adapter for it exists; the upgrade from 1.7 is mechanical and re-encodes existing facts only.
