# 0025. A consistent baseline: every pending choice instantiated, built on Keycloak

- **Status:** Proposed
- **Date:** 2026-10-25
- **Aspect:** all; principally 3.1, 3.2, 3.3, 3.4, 3.5, 3.9 and 3.13
- **Topic / issue:** baseline consolidation
- **Deciders:** chair's call, for review by the working group
- **Decision rule applied:** owner call, provisional

## Context

Open decisions were holding up a consistent set of artefacts. Profiles, examples, tools and site
pages each reflected a different stage of the discussion. The PQC migration depths, the
procurement profile and the deployment work existed only as drafts, and the published validator
could not read the encoding the drafts used. People had nothing consistent to use and try out.

The chair asked for the baseline to be made as good as it can be now, with every pending choice
instantiated and recorded, and reviewed later against a consistent set. CycloneDX 2.0 had
already been set as the carrier target for the PKIC CBOM work.

The choices below were worked out on one concrete subject, Keycloak 26.7.3, written as a product
record, a configured deployment record and an observed deployment record. Each choice exists
because the example could not be written honestly without it.

## Decision

Each choice is provisional. Each can be reopened on its own, and the test suite shows what a
reversal changes.

### Carrier

1. **CycloneDX 2.0 is the target.** It is pinned to `CycloneDX/specification` branch `2.0-dev`,
   commit `76f185c` (23 October 2026), until Ecma ratifies the release. The pinned schema is in
   `tests/schemas/cyclonedx-2.0/`. When 2.0 is released, the schema is replaced and the examples
   are regenerated.
2. **CycloneDX 1.6 and 1.7 are read as legacy.** Today's tools emit 1.x, so refusing it would
   leave no real input. The carrier range in every profile is `min 1.6`, `tested 2.0`. This
   amends decision 0006 in value, not in mechanism.
3. **2.0 constructs used natively.** These are:
   - the subject in `inventories[0].subject`;
   - services as components of type `service`;
   - package URLs as `identifiers` asserted by a party;
   - in-use algorithms in `relatedCryptographicAssets`, with `cipherSuites` meaning supported;
   - module validation and product certification in `certifications`;
   - `ellipticCurve` in place of `curve`.

   `risks` are ignored for conformance and should not appear in a supplier product record
   (decisions 0002 and 0007).
4. **Words.** We write "PKIC CBOM profile" wherever CycloneDX's own `profiles` element could be
   meant. We write "cryptographic interface" where CycloneDX's blueprint `interface` could be
   meant (decision 0021).
5. **SPDX.** The mapping keeps its stated gaps. SPDX 3 is not a target.

### Documents

6. **One stage per document** (baseline P6). The stage is carried in `metadata.lifecycles`.
   A per-interface `lifecycleStage` must agree with it. This resolves the mapping row for I8.
   Mixed stages had let the worked example fill gaps at one stage with invented values from
   another.
7. **The document declares its subject type** (baseline P5). In profiles, `scope.subjectTypes`
   is a set, narrowed by a derived profile. The baseline accepts `product` and `deployment`.
   P3 takes the identifier form from the subject type: a package URL for a product, and a tag URI
   (RFC 4151) for a deployment. This amends decision 0008, which declared a single subject type.
8. **`intended` is not accepted by the disclosure baseline.** The entry profile still accepts it.
   Each kind of intention has another home:
   - a vendor's intention is a capability status (pqc-migration G1);
   - an operator's intention is a requirement, held in policy or a tender;
   - a design document is context (R6).

   This reverses the clause of decision 0008 that kept `intended` in the baseline.
9. **Literal values with a stage restriction.** The literals are `deployment-defined` and
   `peer-defined`. They are accepted for keyExchange, encryption and authentication, and only at
   `implemented`. A truthful build record of Keycloak failed I5 on 7 of 13 interfaces without
   them (decision 0012).
10. **The meaning of a present-state value depends on the stage.** At `implemented` it is the
    product's default as shipped. At `configured` it is the set the deployment permits. At
    `observed` it is the set seen during the observation window.
11. **`defaultState`** (I11, SHOULD, at `implemented`) records whether a product interface is on
    by default.

### Joins

12. **Records are joined, not merged.** This generalises decision 0020.
    - A deployment record cites the documents it builds on by BOM-Link and SHA-256.
    - Each deployment interface names the interface it realises (`correspondsTo`), or states
      `no-product-document`.
    - Only implementation facts follow the join. Present-state facts never do.
    - When the evaluator is given a cited document, it checks the citation's hash. When the
      document is not supplied, the inherited value is reported as unresolved rather than failed.
13. **A deployment-scope profile.** `deployment-disclosure` v0.1 is the first profile of the
    Operation group in draft 0023.
14. **P2 at `observed`.** At this stage P2 is also satisfied in either of two ways:
    - a management interface declared in a cited configured record;
    - the absence reason `not-reached`, accepted only with coverage `partial`.
15. **`unknown` still fails a MUST rule at every stage.** A record with gaps conforms at the entry
    depth instead (decision 0019).

### Context pointers

16. **Reference rules (R).** A profile defines `contextKinds`, and each kind names its CycloneDX
    reference types and its form (document or endpoint). Reference rules require pointers to
    artefacts that the document does not carry. Pointers carry `pkic:profile:context`, and
    endpoints also carry `pkic:profile:accessProtocol`. Conformance checks the pointer and never
    the target. A record points to artefacts that exist when it is written, and to the places
    where later statements will appear. A judgement made afterwards points back to the record by
    digest.
17. **The baseline's reference rules** are:
    - R1, the companion SBOM;
    - R2, where vulnerability statements are published, or a stated absence;
    - R3, advisories, with an access protocol;
    - R4, the security contact;
    - R5, configuration guidance, required wherever a value is `deployment-defined`;
    - R6, design intent.

    The deployment profile adds the configuration source, observation evidence, the data register
    and the issuer policy. pqc-migration adds the support lifecycle. `check_profile.py` gains C18.

### Family

18. **Versions.** The family consists of:
    - enumeration v0.3, the entry profile;
    - the disclosure baseline v0.9;
    - deployment-disclosure v0.1;
    - pqc-migration v0.8;
    - pqc-migration-extended v0.1 (decision 0022);
    - procurement v0.1.

    pqc-migration, its extended depth and procurement are narrowed to products at `implemented`.
    One baseline serves both subject types, and the core-plus-siblings structure is deferred.
    Its revival trigger is a third subject type that needs subject-specific rules.
19. **Perspectives.** Each profile publishes a CycloneDX 2.0 perspective generated from its rules.
    The perspective is informative, and the rules file stays normative.

### Policies, examples and tools

20. **Policies are concrete artefacts.**
    - The policy format, the result format and their schemas.
    - The evaluator, `evaluate_policy.py`.
    - Two example policies: the readiness gap, and an algorithm transition based on the NIST IR
      8547 initial public draft.

    A result names the policy version, the evaluation date and every CBOM it read, by digest.
21. **Keycloak replaces every earlier worked example.** The examples are generated by one script,
    so citations and hashes stay consistent. One product record is also kept in CycloneDX 1.7.
22. **One validator.** `validate_cbom.py` now reads:
    - CycloneDX 2.0 and 1.x;
    - the K7–K9 encoding;
    - literals with a stage restriction;
    - reference rules;
    - joins across documents.

    The demonstration renders reports generated by the validator rather than evaluating them
    itself. This changes how decision 0018 is met, not what it requires.

## Rationale

A consistent set that people can use and challenge is worth more now than a set of choices
that are each argued well and contradict each other. Each choice was tested on a real product,
and none was adopted for symmetry alone.

## Consequences

- **Published artefacts.**
  - Six profiles, four schemas, sixteen example CBOMs, two policies, three policy results, six
    perspectives and five tools.
  - The pinned CycloneDX 2.0 schema and a test suite that checks every example's verdicts and
    schema validity.
  - Site pages rewritten to match, and a new page, Context Pointers.
- **Removed.**
  - The nginx and gateway examples.
  - The promoted drafts of the PQC migration depths and the procurement profile. Their working
    notes stay in `drafts/`.
- **Records affected.**
  - 0006: new values.
  - 0008: single subject type, and `intended` in the baseline.
  - 0018: mechanism.
  - 0020: generalised.
  - 0022: published, then narrowed.
- **Open questions touched.**
  - Q36, Q37 and Q45 now have a home for the operator's data facts: the data register pointer.
  - Q67 and Q68 are partly answered by the deployment profile.
  - Q57 is unchanged: the baseline keeps I9 withholdable, and pqc-migration and procurement
    tighten it.
- **Not in scope.** The IoT, substation and OT drafts, the 0023 change core, and the EU report.
- **Review.** Any choice above can be reopened on its own. The examples and the test suite show
  what a reversal changes before anyone decides it.
