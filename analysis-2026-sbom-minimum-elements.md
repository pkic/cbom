# Analysis: 2026 Minimum Elements for a Software Bill of Materials

Working note for the PKIC CBOM Profiles Working Group.
Subject document: *2026 Minimum Elements for a Software Bill of Materials (SBOM)*, published
29 July 2026, TLP:CLEAR.
Source: https://media.defense.gov/2026/Jul/29/2003971159/-1/-1/1/CSI_2026_cisa_sbom_minimum_elements_508c.PDF

Authored by CISA with the NSA and FBI, and co-sealed by a large international group including
ASD's ACSC, the Canadian Cyber Centre, NÚKIB, ANSSI, BSI, CERT-In, ACN, METI, NCO, NIS/NCSC,
KISA, NCSC-NL, NCSC-NZ, NASK and NBU. It updates the 2021 NTIA minimum elements while keeping
their core principles.

The breadth of co-sealing matters for our purposes. The 2021 document was a US instrument. This
one carries the signatures of most of the European agencies our work already references, which
makes it a more usable anchor for a vendor-neutral profile methodology.

---

## 1. What the update contains

### 1.1 New elements

Ten elements are added:

| New element | Note |
|---|---|
| SBOM Author Signature | A digital signature attributable to the SBOM author. |
| SBOM Data Format Name | The data format used to represent the SBOM. |
| SBOM Data Format Version | The version of that data format. |
| SBOM Generation Context | The lifecycle phase and data available when the SBOM was generated. |
| SBOM Tool Name | The tool used to generate or amend the SBOM. |
| SBOM Tool Version | The version of that tool. |
| SBOM Version | Identifier for a change to the SBOM document itself. |
| Component Hash Value | Output of a cryptographic hash over the executable component artifact. |
| Component Hash Algorithm | The algorithm used to compute that hash. |
| Component License | Licence identifier(s) for the component. |

### 1.2 Major updates

SBOM Author, Component Identifiers, Component Producer, Component Version, Coverage,
Machine-Processable Data, and two renamed elements:

- **Known Unknowns** becomes **Explicitly Identifying Unknown Information**. The author must
  state whether missing information is unknown to the author, or known but deliberately
  withheld. The document treats this as a practice applied across the SBOM lifecycle rather
  than a data field.
- **Accommodation of Mistakes** becomes **Accommodation of Updates to SBOM Data**, covering
  corrections and other changes, with prompt correction expected of authors.

**Coverage** replaces the earlier depth requirement. An SBOM should include all components
that make up the target software, including transitive dependencies, and the document states
that there is no minimum depth. Multiple instances of a component with differing metadata are
listed separately.

### 1.3 Minor updates and removals

Minor updates to SBOM Timestamp (now aligned to RFC 9557), Component Name, Component Dependency
Relationship, Distribution and Delivery, and Frequency. The **Access Controls** element is
removed and its considerations folded into Distribution and Delivery.

### 1.4 Two passages that bear directly on our work

On formats, under Machine-Processable Data:

> "Minimum support for automation means supporting all data formats that are widely used, open
> source, and compatible with existing data formats. Supported data formats should be
> reassessed regularly."

SPDX and CycloneDX are both named as the formats in wide use.

On generation context:

> "The relative software lifecycle phase and data available at the time the SBOM author
> generated the SBOM."

with lifecycle references such as "before build", "build", and "after build" given as
acceptable values, and more specific identifiers permitted.

---

## 2. What this means for the CBOM profiles work

### 2.1 Positions it supports

Five of our existing positions now have authority behind them, which changes how we can argue
them rather than what we say.

**Multiple formats, not one target format.** We revised the challenges page recently to say
that harmonization is achieved through agreed encoding rather than by mandating a single
format. The guidance says the same thing, and goes further by requiring support for all widely
used formats and periodic reassessment of which those are. Our mapping approach is a
mechanism for meeting that requirement, and we should say so.

**Lifecycle stage on the artifact.** Our `lifecycleStage` attribute and the readiness-gap
argument correspond closely to SBOM Generation Context. The guidance confirms that the phase at
which the artifact was produced changes what the data means, and that this belongs in the
document. This is useful support for a part of our model that had no external anchor.

**Carrier format and version as recorded data.** SBOM Data Format Name and Version are now
minimum elements. Our validator already reads `bomFormat` and `specVersion` and applies an
acceptance range through `appliesTo`. The versioning page's carrier-format axis is now
consistent with a stated minimum element rather than a convention we invented.

**Signing and provenance.** The governance page treats signing and provenance as good practice.
SBOM Author Signature, SBOM Author, SBOM Tool Name and SBOM Tool Version are now minimum
elements. Provenance moves from advisable to expected.

**Content revision.** SBOM Version and the Frequency element, which expects a new SBOM for each
build or release, match the content-revision axis on our versioning page.

### 2.2 The material gap: unknown is not the same as withheld

This is the one substantive gap the update exposes in our example.

Our profile and validator are binary. An attribute is present and valid, or it is absent and
the rule fails. The guidance now requires the author to distinguish two cases that we collapse:

- information the author does not have; and
- information the author has but is withholding, for example for confidentiality.

These have different meanings for a consumer. An unknown value indicates a limit of the
producing process, and may be a reason to improve tooling or to treat the result with caution.
A withheld value indicates a policy decision, and the consumer knows the producer holds the
information and could disclose it under other terms. Reporting both as "absent" loses that
distinction and, in a procurement setting, misrepresents the supplier.

This interacts with our inventory page, which already discusses redaction when a CBOM is
extracted for an external consumer. Redaction is exactly the withheld case. We describe the
practice but provide no way to record it in the document.

### 2.3 A tension to address

The Coverage element states that there is no minimum depth and that all components, including
transitive dependencies, should be included. Our challenges page argues that exhaustive
coverage is not necessarily useful coverage, which a reader could take as the opposite position.

They are not in conflict, but we should say why. The guidance sets a floor for which
*components* appear and which *elements* each carries. A profile selects which *attributes* are
mandatory for a stated purpose, and does not licence omitting components. Our own example
already behaves this way: the profile judges the declared interfaces and says nothing about the
thousands of other entries a real CBOM would contain. Making the distinction explicit protects
the profiling argument from an easy objection.

### 2.4 Smaller observations

**Hash algorithm as cryptography.** Component Hash Algorithm is a cryptographic algorithm
recorded in the SBOM. It sits outside our interface model, which covers cryptography in use
between endpoints, but it is legitimately of interest to a cryptographic inventory: an estate
still hashing with a withdrawn algorithm is a finding, and the algorithm is now a minimum
element that a CBOM consumer can read from the SBOM beside it. This strengthens the
SBOM-alongside-CBOM argument on our formats and inventory pages.

**Component Identifiers.** The emphasis on machine-processable unique identifiers supports the
point in our inventory page about stable identifiers for correlating a CBOM with SBOM and HBOM
records.

**Distribution and Delivery.** Access control is now handled here rather than as a separate
element. Our governance page treats distribution, retention and access control together, which
remains consistent.

---

## 3. Recommended changes to our documents

Ordered by significance rather than by page.

### 3.1 Introduce a three-state attribute model (profile, rules, validator, demo)

Replace the present/absent binary with present, unknown, and withheld. Concretely:

- Extend the profile specification so that a MUST attribute is satisfied by a value, and a
  stated `unknown` or `withheld` marker is a distinct outcome rather than a plain failure.
- Decide the conformance treatment. A defensible default is that `unknown` fails a MUST rule
  but is reported distinctly from a missing attribute, while `withheld` is accepted only where
  the profile permits it for that attribute, since a procurement profile and a
  runtime-assurance profile will differ here.
- Extend `validate_cbom.py` to report three outcomes, and the demo page to display them.
- Record the marker convention in the mapping, since neither format has a native field for it.

This is the largest change and the one most worth doing, because it is the point where our
example would fail to meet the updated guidance.

### 3.2 Add the document to the references page

Add to the governmental section, noting the co-sealing agencies. It supersedes nothing we cite,
but it is now the most current statement of SBOM minimum elements and is jointly issued by
agencies we already reference separately, including BSI, ANSSI, NCSC-NL and CERT-In.

### 3.3 Challenges page

- Cite the Machine-Processable Data passage as support for the multi-format position we
  recently adopted, replacing our unsupported assertion with a referenced one.
- Add a short paragraph distinguishing component coverage from attribute selection, as in 2.3.
- Add the unknown-versus-withheld distinction as a challenge in its own right. It belongs
  beside the depth-of-disclosure item, which currently treats confidentiality without
  addressing how a withheld value is expressed.

### 3.4 Lifecycle page

- Relate `lifecycleStage` to SBOM Generation Context, giving the correspondence between our
  four values and the "before build", "build", "after build" references. Our model extends
  further into deployment and runtime, which the guidance permits through its allowance for
  more specific identifiers.
- Note that the guidance permits, and our model requires, a statement of the phase, so a
  producer following the minimum elements already has the information our profile needs.

### 3.5 Governance page

- Reframe signing and provenance from recommended practice to expected practice, citing SBOM
  Author Signature, SBOM Author, SBOM Tool Name and SBOM Tool Version.
- Note that the guidance references ENISA Agreed Cryptographic Mechanisms in connection with
  signatures, which supports the point already on that page about governing the signing
  algorithm itself.
- Add the correction obligation from Accommodation of Updates to SBOM Data, which sits with our
  immutability and supersedence discussion.

### 3.6 Versioning page

- Cite SBOM Data Format Name and Version in support of the carrier-format axis.
- Cite SBOM Version and Frequency in support of the content-revision axis.
- Relate Accommodation of Updates to SBOM Data to the upgrade-over-rejection recommendation.

### 3.7 Inventory page

- Connect the redaction discussion to the withheld marker, so the practice we describe has a
  representation in the document.
- Cite Component Identifiers in support of the stable-identifier recommendation.

### 3.8 Formats and mapping

- Record the marker convention for unknown and withheld values.
- Note that Component Hash Algorithm is cryptographic data available in the SBOM beside the
  CBOM, in the section on relating cryptography to its environment.

---

## 4. Suggested sequence

1. References page entry, since it is small and makes the rest citable.
2. Challenges, lifecycle, governance, versioning and inventory text changes, which are prose
   and cross-references only.
3. The three-state attribute model, which touches the profile specification, the rules file,
   the validator, both example CBOMs, the demo page and the mapping. This should be treated as
   a version increment of the example profile rather than an edit, and handled through the
   grace-window approach the versioning page already describes.

## 5. Points to confirm before publication

- Whether the working group wants `withheld` to be profile-permitted per attribute, as
  suggested in 3.1, or governed separately by policy.
- Whether our lifecycle vocabulary should be aligned to the guidance's terms or mapped to them.
  Mapping is the safer option, since our terms distinguish deployment and runtime, which
  "after build" merges.
- The document's exact page and clause references, which this note does not cite, since the
  text was extracted rather than read from the paginated original.
