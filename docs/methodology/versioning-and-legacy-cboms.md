# Handling older CBOM files

> **Status:** Illustrative design note for the PKIC CBOM Profiles Working Group.
> Descriptive; not normative. Uses the Keycloak 26.7.3 worked example and the consolidated
> baseline of 25 October 2026 (decision 0025).

The term "older CBOM files" is ambiguous until the versions it may refer to are
separated. Three items each carry a version, and each changes independently.

## 1. Three version axes

| Axis | Example | Owner | Changes when |
|---|---|---|---|
| **Carrier format** | CycloneDX `specVersion` 1.7 → **2.0** | CycloneDX / Ecma (ECMA-424) | the SBOM/CBOM standard is revised |
| **PKIC CBOM profile** | `interface-disclosure` v0.8 → v0.9 | the profile author (PKIC or a sector) | the requirements change |
| **CBOM content revision** | a product's CBOM `version` / `serialNumber` over time | the CBOM producer | the product or a re-scan changes |

Conflating these axes is a common error. A CBOM may be current on one axis and older on
another. A newly generated CBOM (a new content revision) may still be serialized in
CycloneDX 1.7 (an older carrier) and evaluated against the baseline v0.9 (newer rules).

A conformance claim must reference all three. For example: "conforms to `interface-disclosure`
v0.9, evaluated against a CycloneDX 2.0 CBOM, content revision 1." A claim that omits any of the
three is not reproducible.

The current profile versions are:

| Profile | Version | Extends |
|---|---|---|
| `interface-enumeration` (entry depth) | 0.3 | – |
| `interface-disclosure` (the baseline) | 0.9 | – |
| `deployment-disclosure` | 0.1 | baseline 0.9 |
| `pqc-migration` | 0.8 | baseline 0.9 |
| `pqc-migration-extended` | 0.1 | pqc-migration 0.8 |
| `procurement` | 0.1 | baseline 0.9 |

## 2. Carrier-format version: the acceptance range

**Recommendation: accept a declared range rather than a single fixed version.** Each profile
declares the carrier versions it accepts, so that older CBOMs are handled explicitly. Every
profile in the family declares:

```json
"appliesTo": { "cyclonedx": { "min": "1.6", "tested": "2.0" } }
```

The validator (`validate_cbom.py`, `check_format`) applies a four-band policy:

| CBOM `specVersion` | Band | Behaviour |
|---|---|---|
| below `min` (for example 1.5) | **refused** | Refuse, exit code 4. The adapter may be unable to read the model, so it must not evaluate it. The producer is advised to upgrade the CBOM. |
| `min` ≤ v < `tested` (1.6, 1.7) | **legacy** | Accept with a warning. Evaluate normally, and record that the profile was tested against a newer carrier. |
| v == `tested` (2.0) | **target** | Accept. |
| above `tested` (for example 2.1) | **newer** | Accept with a note. A reviewer should assess whether new fields affect the result. |

Four inputs show the four bands:

- `examples/cbom-keycloak-product.cdx.json`, at 2.0: target;
- `examples/legacy/cbom-keycloak-product-1.7.cdx.json`, at 1.7: legacy;
- a copy of the 2.0 record marked 2.1: newer;
- a copy of the legacy record marked 1.5: refused.

A declared range is preferred to a single fixed version. The tools that produce CBOMs today emit
CycloneDX 1.x, so refusing 1.x would leave no real input. A range provides a migration window. An
unrestricted range is not appropriate either. Below `min`, the cryptographic object model may
differ enough that evaluation could produce an incorrect verdict, which is less acceptable than
an explicit refusal.

This amends decision 0006 in value, not in mechanism. The range was `min 1.6, tested 1.7`; it is
now `min 1.6, tested 2.0`.

## 3. How a CycloneDX 1.7 document is read

**The adapter reads both generations.** CycloneDX 2.0 moved several facts. The validator reads
each fact from wherever the document's generation keeps it, and produces the same abstract
record from both. The rules are written once and see only that record.

| Fact | CycloneDX 2.0 | CycloneDX 1.6 / 1.7 |
|---|---|---|
| The subject | `inventories[0].subject` | `metadata.component` |
| Services | components with `type: "service"` | `services[]` |
| Package URLs | `identifiers[]` asserted by a party | `purl` |
| Algorithms in use | `relatedCryptographicAssets` | `cryptoRefArray`, `algorithmRef`, `signatureAlgorithmRef` |
| Module validation | `certifications[]` on the library | property and `certification-report` reference |
| Deployment identifier | identity with custom scheme `tag-uri` | property `pkic:profile:subjectIdentifier` |

**The band changes the report, not the verdict.** The Keycloak product record is published twice
with the same facts. `examples/legacy/cbom-keycloak-product-1.7.cdx.json` conforms to the same
five profiles as the 2.0 record: interface-enumeration v0.3, the baseline v0.9, pqc-migration
v0.8, pqc-migration-extended v0.1 and procurement v0.1. Its report opens with:

```
FORMAT  [warn] CycloneDX 1.7 accepted, profile tested against 2.0 (legacy -- warn)
```

A conformance claim for it records `carrierBand: legacy`. The test suite checks that the two
records receive the same verdicts.

A legacy document can still fail on its content. `examples/legacy/cbom-keycloak-scanner-output.cdx.json`
is untargeted scanner output in CycloneDX 1.7. The validator reads it in the legacy band and finds
that it fails the entry profile on P1, P3, P4, P5 and P6: it declares no interface, identifies no
subject, states no coverage, declares no subject type and states no lifecycle stage.

## 4. Normalization

CycloneDX 1.7 introduced the Cryptography Registry, an authoritative, machine-readable list of
algorithm families with stable identifiers. It addresses the situation in which one producer
records `AES-256-GCM` and another records `aes_256_gcm`, which prevents automated comparison.
CycloneDX 2.0 also replaces the free-text `curve` with the enumerated `ellipticCurve`, such as
`other/Curve25519` for X25519.

Implications for older CBOMs:

- **2.0 and 1.7 CBOMs** can anchor each algorithm to a registry identifier, so normalization is
  intrinsic.
- **1.6 CBOMs** carry free-text algorithm names. To compare them reliably, apply a
  name-normalization map in the adapter (canonicalizing `AES256`, `AES-256-GCM`, and
  `AES_256_GCM` to a single registry identifier) before the rules are evaluated. Maintain that
  map under version control alongside the profile.

This is the syntactic normalization identified in the GSMA telecommunications CBOM draft:
normalization is performed at the adapter boundary, so that the rules operate only on canonical
identifiers.

## 5. Upgrade in preference to rejection

For a legacy but supported CBOM, a one-way mechanical upgrade is preferable to rejection.
`cdx17_to_20.py` converts a CycloneDX 1.6 or 1.7 CBOM to 2.0:

```
python3 cdx17_to_20.py <in-1.x.json> <out-2.0.json>
```

Its docstring lists every conversion. The main ones are:

| CycloneDX 1.x | CycloneDX 2.0 |
|---|---|
| `bomFormat` | `specFormat` |
| `metadata.component` | `inventories[0].subject` |
| `components[]`, `services[]` | `inventories[0].components[]` (a service becomes type `service`) |
| `purl` | `identifiers[]` asserted by a party |
| `supplier`, `manufacturer` on a component | `parties[]` with a role |
| `cryptoRefArray`, `algorithmRef`, `signatureAlgorithmRef`, `subjectPublicKeyRef` | `relatedCryptographicAssets` |
| `securedBy.algorithmRef` (string) | `securedBy.algorithmRef` (array) |
| `curve` | `ellipticCurve` |
| `certificationLevel`; `moduleValidationScheme` with a `certification-report` | `certifications[]` |
| `service.data`, `trustZone` and the other service-only fields | dropped |
| `compositions[].assemblies` | `compositions[].targets`, kind `components` |
| `pkic:profile:subjectIdentifier` | identifier with custom scheme `tag-uri` |
| property `pkic:example:comment` | top-level `$comment` |

Properties named `pkic:profile:*` carry over unchanged. `dependencies[].provides`, the protocol
type enumeration and the cipher-suite structure are unchanged.

Upgrading is a data transformation, not a re-attestation. It must not add cryptographic facts that
were not present in the original; it only re-encodes existing facts. Any value that cannot be
resolved remains flagged. The repository's example generator, `tools/build_keycloak_examples.py`,
writes each Keycloak document in 1.7 form and converts it with `cdx17_to_20.py`, so the converter
runs on every published example.

## 6. CycloneDX 2.0 as the target, and re-pinning

CycloneDX 2.0 is the target carrier. It is not yet released. The profiles are pinned to
`CycloneDX/specification` branch `2.0-dev`, commit `76f185c` (23 October 2026), and the pinned
schema is in `tests/schemas/cyclonedx-2.0/` in the repository. Ecma is expected to ratify the
release in December 2026.

**What changes for the profiles.**

- **Paths, not attributes.** The validator reads the subject, services, package URLs and in-use
  algorithms from their 2.0 locations. Attribute names, levels and vocabularies do not change.
- **New native homes.** A `certifications` array on any component (standard, identifier, issuer,
  dates and URL) carries module validation on the implementing library and product certification
  on the subject, including schemes that the algorithm-level `certificationLevel` enumeration did
  not list. `rotation` on keys and `renewal` on certificates describe how those are replaced; no
  rule reads them yet. The profile's capability-by-purpose group still has no native home.
- **Supported and in-use algorithms.** `cipherSuites` still list the supported set.
  `cryptoRefArray` is removed, so the in-use reading moved to `relatedCryptographicAssets`.
- **Risks are ignored.** CycloneDX 2.0 adds a root `risks` array. A risk can reference a
  cryptographic asset and carries a status and an owner; each response carries a strategy,
  controls, a status, an owner and a target date. These are judgements, not product facts.
  Decision 0002 places judgements in policy. Decision 0007 states forward-looking capability as a
  status and a blocker rather than a date. The validator ignores `risks` for conformance, and a
  supplier's product record should not contain them.
- **Perspectives.** CycloneDX 2.0 adds perspectives: JSONPath expressions, each marked required,
  recommended, optional or informative. A perspective cannot express conditions, vocabularies,
  groups or withholding, so it does not replace a profile's rules file. Each PKIC CBOM profile
  publishes a perspective generated from its rules (`perspectives/`), as an informative companion.
- **Terminology.** CycloneDX 2.0 uses "profile" for reusable data and threat characterizations,
  and its blueprint model defines an "interface" with types such as `rest` and `cli`. Neither is
  the concept used here. Documents that discuss both say "PKIC CBOM profile" and "cryptographic
  interface".
- **The edge gap remains.** The blueprint model has zones, boundaries and flows with a source
  and a destination, but it models a deployed system for threat analysis. Its protocols are free
  text and its encryption is a boolean. It does not represent a product's cryptographic
  interface.

**Re-pinning to the released 2.0.** When Ecma ratifies the release, the working group:

1. replaces the files in `tests/schemas/cyclonedx-2.0/` with the released schema;
2. compares the release with commit `76f185c`, and revises the converter, the validator's 2.0
   reading and the mapping wherever a field the profiles use has moved;
3. regenerates the examples with `tools/build_keycloak_examples.py`, the perspectives with
   `tools/build_perspectives.py` and the demonstration reports with `tools/build_demo_reports.py`;
4. runs the test suite, which validates every example against the schema and checks every
   expected verdict.

The carrier range keeps `tested` at 2.0, so the acceptance rule does not change. Conformance
claims and policy results bind a document by digest. Where a regenerated example changes, its
digest changes, and the claims and results that cite it are issued again. A document that a
producer wrote against the pinned commit also says `specVersion` 2.0. If a field moved before
the release, such a document may not validate against the released schema, and the producer
should regenerate it.

## 7. Profile-version change (the second axis)

When a profile is tightened, existing CBOMs do not become incorrect; they were evaluated against
the profile in force at the time. An example is v0.9 of the baseline, which stopped accepting
`intended` (decision 0025). The Keycloak 27.0 design record,
`examples/cbom-keycloak-product-intended.cdx.json`, fails baseline I8 and still conforms to the
entry profile, which accepts `intended`. This is handled as any policy change:

- **Evaluate against a stated profile version.** An older CBOM must not be re-interpreted under
  newer, stricter rules without notice. The profile version is pinned in the conformance claim.
- **Use grace windows rather than immediate cutoffs.** A newly raised requirement should emit a
  warning, rather than a failure, for the now-deprecated but formerly permitted state until a
  published date. After that date the result becomes a failure. The cutoff is encoded in the rule,
  so that the change is automatic and auditable.
- **Deprecate, rather than delete, vocabulary.** If `interfaceType` values change, retain
  recognition of the former values (mapped to their replacements) for at least one profile
  major version.

## 8. Content-revision change (staleness)

The CBOM's own `version`, `serialNumber`, and `timestamp` sequence constitutes the audit trail
on which the PQC progress-tracking use case relies. Two controls apply:

- **Freshness policy:** a consumer may require the CBOM `timestamp` to be within a defined
  interval of the artifact it describes, and otherwise emit a warning. A syntactically valid
  CBOM may still be stale.
- **Supersedence:** a newer content revision for the same subject supersedes older ones. The
  history is retained, and the latest revision is evaluated.

Content revisions also matter across documents. A deployment record cites the records it builds
on by serial number, version and SHA-256 hash. If a cited record changes, the citation no longer
matches. `examples/cbom-keycloak-deployment-observed-fail-P1.cdx.json` cites a configured record
that has since changed. When the evaluator is given the current configured record (`--with`), the
hash does not match and the observed record fails `deployment-disclosure#P1`.

## 9. Summary of recommendations

Version handling should be explicit and machine-checkable on all three axes:

1. Profiles declare an `appliesTo` carrier range, and validators enforce the minimum, tested,
   and newer bands. The family's range is `min 1.6`, `tested 2.0`.
2. A CycloneDX 1.6 or 1.7 document is read as legacy and receives the same verdicts as the
   same facts in 2.0.
3. Algorithm identity is normalized at the adapter (registry identifiers in 2.0 and 1.7; a
   versioned name map for 1.6).
4. Legacy CBOMs are upgraded mechanically with `cdx17_to_20.py` rather than rejected, and the
   upgrade adds no facts.
5. The profiles stay pinned to CycloneDX 2.0 commit `76f185c` until the release, and are then
   re-pinned by replacing the schema and regenerating the examples.
6. The profile version is pinned in every conformance claim, and rules are tightened behind
   dated grace windows.
7. Content-revision freshness and supersedence are tracked, so that an older revision is not
   treated as incorrect without cause.
