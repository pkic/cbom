---
title: Versioning
sideMenu: true
weight: 19
aliases:
- /cbom/methodology/versioning.html
linkTitle: Versioning
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

"An older CBOM" can mean three different things, because three items each carry their own version and change independently: the document format (for example CycloneDX 1.7), the profile, and the CBOM's content. A conformance claim must state all three versions, or nobody can repeat the check and get the same result.

## Three version axes

| Axis | Example | Changes when |
| --- | --- | --- |
| **Carrier format** | CycloneDX `specVersion` 1.6 → 1.7 | the SBOM/CBOM standard is revised |
| **Profile** | `interface-disclosure` v0.6 → v0.7 | the requirements change |
| **Content revision** | a product's CBOM `version` over time | the product or a re-scan changes |

The carrier format is the document format in which a CBOM is written. The three axes vary independently. For example, a newly generated CBOM (a new content revision) may still be serialized in CycloneDX 1.6 (an older carrier) and evaluated against profile v0.7 (newer rules). A common error is to treat the three axes as one.

The values for two of these axes are now recorded as data in the bill of materials, rather than left to local convention. The 2026 minimum elements guidance adds the elements SBOM Data Format Name and SBOM Data Format Version, which record the carrier version. It also adds SBOM Version, which records the content revision. Its Frequency element expects a new bill of materials for each build or release. Content revisions are therefore produced as a matter of course rather than on request. A producer that meets the minimum elements guidance supplies the two values a validator needs to place a document on both axes. See [References](../../references/).

## Carrier version bands

The profile declares the range of carrier versions it accepts, so that the validator handles older CBOMs by a stated rule. The rules file specifies `"appliesTo": { "cyclonedx": { "min": "1.6", "tested": "1.7" } }`. The validator then places each CBOM in one of four bands (ranges of carrier versions), and each band receives its own treatment:

{{< figure src="../assets/figures/methodology-versioning-1.svg" alt="A horizontal band of four carrier version ranges: below 1.6 refused, 1.6 accepted as legacy with a warning, 1.7 the accepted target, and above 1.7 accepted for review" >}}

*A declared range does two things. It provides a migration window, so that existing 1.6 CBOMs are not invalidated when 1.7 is published. It also sets a defined lower bound. Below that bound, evaluation could produce an incorrect verdict (pass or fail result).*

The validator reports the band in which the CBOM falls. To observe all four bands, evaluate the example CBOM, which is at 1.7, and copies of it at 1.8, 1.6 and 1.5. Each band needs its own input. 1.7 is the tested version, 1.8 is newer than tested, 1.6 falls in the legacy window, and 1.5 is below the minimum and is refused.

## A major carrier revision: CycloneDX 2.0

CycloneDX 2.0 is in development, with Ecma ratification expected around the end of 2026. The observations below were made against the development branch `2.0-dev-safety` (20 September 2026) and should be revisited against the released schema.

The *newer* band assumes that the adapter (the part of the validator that reads a carrier format) can still read the fields that a newer version shares with the tested version. That assumption holds between minor versions. It does not hold for 2.0: a CycloneDX 1.7 worked example fails the 2.0 schema with 19 errors. Until an adapter for 2.0 exists, a change of major version should be treated as *unsupported*.

| CycloneDX 1.7 | CycloneDX 2.0 |
| --- | --- |
| `bomFormat` | `specFormat` |
| `services[]` | `components[]` with `type: "service"` |
| `purl` on a component | `identifiers[]`, each claimed by a declared party |
| `supplier`, `manufacturer` on a component | `parties[]`, each with a role |
| `cryptoRefArray`, `algorithmRef` and the certificate references | `relatedCryptographicAssets[]` |
| `curve` (deprecated in 1.7) | `ellipticCurve`, enumerated |

Applying these six changes made the example valid against the 2.0 schema without altering any profile attribute. The upgrade is therefore mechanical. CycloneDX 2.0 has the following consequences for the profiles:

-   **Paths change, attributes do not.** The profile attributes stay the same, but the locations of their values in the document change. Rules that read a Package URL, a supplier or a service need new paths.
-   **New native fields for some profile attributes.** `certifications` on any component can carry module validation and product certification. `agility` partly covers enablement and negotiation. `rotation` and `renewal` describe how keys and certificates are replaced. The capability-by-purpose group still has no native field in CycloneDX 2.0.
-   **Migration management maps to a risk register.** The new `risks` array carries status, owner, response and target date. These values are judgements, not product facts. They belong in an operator's CBOM rather than a supplier's conformance claim (decisions 0002 and 0007).
-   **Perspectives** mark JSONPath expressions as required, recommended or optional. They cannot express conditions or vocabularies. Perspectives could therefore accompany a profile, but could not replace it.
-   **Terminology.** CycloneDX 2.0 uses "profile" and "interface" for other concepts. Say "PKIC CBOM profile" where both appear.
-   **The edge gap remains.** CycloneDX 2.0 adds a blueprint model with flows and boundaries. That model describes a deployed system for threat analysis. It does not describe a product's cryptographic interface, so it does not close the gap.

Proposed position, pending working-group review: CycloneDX 1.7 remains the tested carrier. CycloneDX 2.0 will be added once it is ratified and an adapter for it exists.

## Supporting recommendations

-   **Normalize at the adapter.** Prefer CycloneDX 1.7 Cryptography Registry identifiers where they are present. CycloneDX 1.6 CBOMs use free-text algorithm names. For those, apply a versioned name map before the rules are evaluated.
-   **Upgrade rather than reject.** Convert a legacy but supported CBOM mechanically (raise the version, attach registry identifiers, record provenance) rather than rejecting it. The conversion re-encodes existing facts and adds no new ones. This is consistent with the expectation in the minimum elements guidance that organizations accommodate updates to bill-of-materials data, including corrections.
-   **Pin the profile version** in every conformance claim. When a rule is tightened, enforce the tightening only after a dated grace window. During that window the validator emits a warning, so that the warning comes before the result changes to a failure.
-   **Deprecate, rather than delete, vocabulary.** If `interfaceType` values change, retain recognition of the former values (mapped to their replacements) for at least one profile major version.
-   **Track freshness and supersedence** (whether a newer revision has replaced a CBOM), so that an older content revision is not treated as incorrect without cause.

The full treatment is provided in [versioning-and-legacy-cboms.md](https://github.com/pkic/cbom/blob/main/docs/methodology/versioning-and-legacy-cboms.md), and the acceptance range is enforced by the format gate in `validate_cbom.py`; see [Files](../files/).

[← Data Exposure](../data-exposure/) [Next: Governance →](../governance/)
