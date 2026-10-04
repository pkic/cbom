# Plan: a baseline and an extended PQC migration profile, informed by `cprofile.json`

Working note for the PKIC CBOM Profiles Working Group.
Written 26 September 2026, against `schemas/cprofile.json` and the state of `docs/methodology/`
at that date (interface-enumeration v0.1, interface-disclosure v0.7, pqc-migration v0.6).

**Status, 26 September 2026.** Forks F1 to F5 settled as recommended. Both profiles are drafted in
`drafts/pqc-migration-depths/` with decision record 0022, and both are well-formed under C1–C17
(C9 warns: examples pending). Tooling is deferred. Drafting changed four things against §4 and §5:

- `approvedModeAvailability` failed C6, because "approved" is a judgement token. It is now
  `validatedModeAvailability`, with values `in-validated-mode`, `outside-validated-mode-only`,
  `no-validated-mode`.
- Common Criteria left the baseline's validation vocabulary. It certifies a product, not a module,
  and is now the extended profile's P2, `productCertificationScheme` (SHOULD).
- The extended profile gained a guard, `I1 keyManagementFunction`, so that a management console
  that never touches a key owes no key attributes. It also gained `keyStoreFormats` next to
  `keyStoreFormatsSupported`, which C12 requires. Rules renumbered I1–I12.
- One finding for the tooling step: the evaluator tests `enumRef` against a whole list, so list
  rules with a vocabulary fail every document. It is recorded in decision 0022.

**Update, same day: storage interfaces.** No storage interface could satisfy the baseline's
channel rules at any depth. Settled in decision 0022: the channel rules skip storage interfaces,
and `keyWrapping` stands in for key exchange. That adds two more drafts: Interface Enumeration
v0.2 and Interface Disclosure Baseline v0.8. `keyWrapping` moved into the disclosure baseline,
`keyWrappingSupported` into pqc-migration v0.7 (as I12), and the extended depth keeps only P1.
Its interface rules are now I1–I10. All four drafts are well-formed, and the existing examples
give unchanged verdicts against them.

**Update, 27 September: Keycloak examples.** K1–K5 are settled and recorded in decision 0022.
The plan for the example pairs is in `drafts/pqc-migration-depths/examples-keycloak-plan.md`. Later the same day, the cprofile was corrected, K6 settled, and four Keycloak example documents written. With the evaluator gaps patched outside the repository, the pass documents conform and each fail document isolates one rule. Then K7: application-layer interfaces became CycloneDX services, with a draft mapping beside the profiles. Then K8 to K10: native CycloneDX fields first, implementation facts inherited from the providing library, and document-level references to the SBOM and vulnerability information. Q22 and Q26 carry dated notes. The site pages to change on promotion are listed in the drafts README.
The updated `schemas/cprofile.json` resolves §2 findings 3, 5 and 6. Findings 1, 2, 4 and 7
stand.

## Summary

`cprofile.json` describes a product in five blocks: identity, network interfaces with their
per-platform cryptographic providers, key management utilities, security controls, and
provenance metadata. Set against the existing migration profile, it adds little at the interface
level and a great deal around it. The existing profile already asks more about each interface than
`cprofile` can carry. What `cprofile` shows is the surrounding estate that decides whether an
interface can actually move: the tool that must generate the new key, the store that must hold
it, the validated module that must approve it, the storage path whose data keys are wrapped under
RSA, and the external services that must migrate first.

That splits cleanly into two depths of one family (decision 0019):

- **Baseline.** The existing `pqc-migration` profile, re-issued as v0.7 with three additions
  about module validation and approved-mode availability.
- **Extended.** A new profile, `pqc-migration-extended` v0.1, extending the baseline. It adds key
  management surfaces, storage key wrapping, external dependencies and enablement settings.

Both serve the same consumer and the same decision. The extended profile answers "what enabling
it requires" more completely. It does not answer a different question, so it is a depth and not a
branch.

---

## 1. What `cprofile.json` carries

| Block | Content | Orientation |
|---|---|---|
| `product`, `version`, `sbom_ref` | Subject identity and a link to a companion SBOM | n/a |
| `interfaces[]` | Network role, data classification, application protocols and ports, transport protocol and versions, cipher suites, feature flags, and per platform: OS, security provider, library, FIPS/CC status, algorithm list | Present state, with capability mixed in through `features` |
| `key_management_interfaces[]` | Tool, interaction mode, store type, store formats, key operations, key entry method, FIPS-compliant management, platforms | Present state |
| `security_controls[]` | Control type (16 kinds), governing parameters, external dependencies, per-platform status, transport, role and secret protection, data-at-rest protection | Present state |
| `metadata` | Created, author, `source` (manual, documentation, automated, repository, scanner, vendor), tool version | Provenance |

`cprofile` is an inventory-oriented record. It has no capability status, no blocker, no
enablement method and no statement of coverage. A converter can populate the present-state half
of the baseline from it. It cannot populate the migration half without further supplier input.

## 2. Findings about `cprofile.json` itself

These go back to the `cbomgen` maintainers. None of them blocks the profile work.

1. **Judgements sit beside facts.** `quantum_safe` and `fips_approved` are verdicts. Decision
   0002 keeps them out of a CBOM. `fips_approved` is derivable from the module's validation
   certificate and security policy. `quantum_safe` depends on policy that changes while the
   product does not.
2. **Library capability is recorded where interface use belongs.** `supported_algorithms` sits on
   the platform's library, not on the interface. It says what the library can do. It does not
   say what this interface negotiates or can be configured to negotiate. A library offering
   ML-KEM tells the operator nothing about whether the listener exposes it.
3. **Cipher suites do not carry TLS 1.3 key exchange.** TLS 1.3 suites name only the AEAD and
   hash. The key exchange group (for example `X25519MLKEM768`) and the signature algorithms are
   negotiated separately. `cprofile` has no field for either, and falls back on a feature flag
   (`quantum-safe-ML-KEM`). The flag cannot say which group, or whether it is hybrid.
4. **Supported and enabled are one flag.** `features` is described as "supported by this
   interface". It cannot distinguish a capability shipped but disabled from one on by default.
   The methodology's bare/`*Supported` naming exists for exactly this distinction.
5. **Two certification schemes share one enum.** FIPS 140 validates a cryptographic module.
   Common Criteria evaluates a product against a protection profile. They certify different
   objects, and a single `level` field hides which object was certified.
6. **`data_classification` mixes two axes.** Sensitivity labels (`confidential`, `secret`) and
   traffic planes (`control-plane`, `data-plane`) share one enum, so an interface cannot state
   both.
7. **`source` is not `lifecycleStage`.** `source` records how the profile was produced.
   `lifecycleStage` records what state the fact describes. A scanner result is `observed`; a
   `documentation` result could be `intended` or `implemented`. A converter must not infer one
   from the other.

## 2a. Findings for CBOM generators generally

Added 27 September 2026, from building the Keycloak example and comparing it with a
generator-produced CBOM for a commercial product. These apply to any generator, cbomgen
included.

1. One TLS protocol component per listener or connection. Share a configuration component only
   where the configuration is identical. Keep per-listener facts, such as mutual TLS or FIPS
   mode, on that listener's component.
2. State transport facts in native protocol fields (`version`, `cipherSuites`, `tlsGroups`,
   `tlsSignatureSchemes`), not as free text on services.
3. Give every algorithm component a `primitive` and its parameters. Key agreement is
   `key-agree` or `kem`.
4. Record the certificate or signature algorithm that authenticates each TLS interface.
5. Link each library to the interfaces it implements with `dependencies[].provides`, and emit
   each package once.
6. Record application-layer cryptography, such as token signing and encryption, as algorithm and
   key dependencies of the service.
7. Model key-management tools and security policies as attributes of interfaces, not as
   services.
8. Keep role, interaction mode and store type in separate fields, and use an owned property
   namespace, not a generic `crypto:` prefix.
9. Give the subject a Package URL, state completeness with `compositions`, and link the source
   SBOM with a hash.

## 3. Mapping `cprofile` to the family

"Base" means already required by interface-disclosure v0.7 or pqc-migration v0.6. "B" is new in
the baseline (pqc-migration v0.7). "E" is new in the extended profile. "X" is excluded, with the
reason in §6.

| `cprofile` element | Treatment | Attribute |
|---|---|---|
| `product`, `version` | Base | Subject purl (`interface-disclosure#P3`) |
| `sbom_ref` | Out of profile | Carrier-level link, Q22 |
| `interfaces[].type` | Base | `endpointRoles`, `interfaceType` |
| `application_protocols[].name` | Base | `protocol` |
| `application_protocols[].port` | X | Deployment-configured |
| `transport_security.protocol`, `supported_versions` | Base | `protocol`, `protocolVersion`, `protocolVersionsSupported` |
| `transport_security.cipher_suites` | X | Decomposed into `keyExchange`, `encryption`, `authentication` |
| `features: quantum-safe-*`, `hybrid-classical-pqc` | Base | `keyExchangeSupported`, `authenticationSupported`, G1 status |
| `features` (hardening flags) | X | Configuration hygiene, not migration |
| `platforms[].security_provider`, `cryptographic_library` | Base | `implementationPurl`, `pqc-migration#P1` |
| `platforms[]` as a variant axis | Base, by subject | One CBOM per platform build, distinguished by purl qualifiers (fork F2) |
| `platforms[].fips_compliance` | **B** | `moduleValidationScheme`, `moduleValidationRef` |
| `supported_algorithms[].fips_approved` | **B**, as a fact | G1 member `approvedModeAvailability` |
| `supported_algorithms[].quantum_safe` | X | Judgement, decision 0002 |
| `key_management_interfaces[]` | **E** | Management interfaces with `keyOperations`, `keyTypesSupported`, `keyStoreFormats(Supported)`, `keyStoreLocation` |
| `key_management_ref` | **E** | `keyStoreRef` on service and storage interfaces |
| `key_entry_method` | X | Operational procedure, not a migration fact |
| `security_controls[].external_dependencies` | **E** | `externalDependencies` |
| `governing_parameters` of a `quantum_safe_migration_policy` or `tls_policy` | **E** | `enablementSetting` |
| `data_at_rest_protection` | **E** | Storage interfaces declared or absent; `keyWrapping`, `keyWrappingSupported` |
| `roles[].authentication_algorithm` | Base | `authentication` on the management interface, already required by `interface-disclosure#P2` and `#I5` |
| `revocation_check` | **E**, folded | `externalDependencies: revocation-responder` |
| `secret_protection` | X | Classical secret hygiene |
| Audit, IDS, authorisation, programmatic exit controls | X | Not cryptographic migration facts |
| `data_classification` (sensitivity) | X | Deployment scope, see Data Exposure and Q36 |
| `data_classification` (plane) | Candidate, held back | `trafficPlane`, see §5.4 |
| `metadata.source` | Out of profile | Carrier metadata, not `lifecycleStage` |

## 4. Baseline: pqc-migration v0.7

Everything in v0.6 stays. Three additions, all traceable to `cprofile`, all serving the existing
decision.

| Id | Attribute | Level | Withholdable | Constraint | Why it earns its place |
|---|---|---|---|---|---|
| I10 | `moduleValidationScheme` | MUST | no | enum: `fips-140-2`, `fips-140-3`, `iso-19790`, `common-criteria`, `national-other`, `none` | `blockedBy: certification` is already in the vocabulary. Without the current validation stated, that blocker is unverifiable. `none` makes the rule cheap for unregulated products |
| I11 | `moduleValidationRef` | MUST | no | present, when scheme ≠ `none` | The certificate number lets policy derive approval status. Certificates are public, so withholding protects nothing |
| G1.4 | `approvedModeAvailability` | SHOULD | no | enum: `yes`, `no`, `no-approved-mode`; when `capabilityStatus` = `available` | The common regulated case: ML-KEM ships, but only outside the validated mode. For a regulated operator, that makes "available" false in practice |

Kind of change: tightening (a new MUST). Documents conforming to v0.6 need I10 and I11 to
conform to v0.7.

`approvedModeAvailability` starts at SHOULD so the baseline stays reachable. The extended profile
tightens it to MUST.

## 5. Extended: pqc-migration-extended v0.1

**Objective.** Same consumer and same decision text as the baseline, verbatim. One added
decision option: "sequence a dependency first, where another system must migrate before this
interface can".

**Scope.** Same subject type, orientation `both`, relationship types and lifecycle stages.
Proposed: add `key-protection` to `scope.cryptographicPurposes`. Taking a further purpose in depth
asks for more, so it is a tightening. `check_scope_narrows` does not look at
`cryptographicPurposes` at all today. Adding a purpose passes, and so would dropping one, which
is a relaxation the checker should reject.

### 5.1 Product rules

| Id | Rule | Level | Constraint |
|---|---|---|---|
| P1 | Product declares at least one storage interface, or states why it has none | MUST | `minInterfacesOfType: storage` + `orDeclaredAbsent: storageInterfaceAbsence` |

The same pattern as `interface-disclosure#P2`, with no new mechanism. Stored ciphertext is exposed
to harvest-now-decrypt-later by a shorter route than captured traffic. It is also easier to omit,
because a backup path is not a network listener.

### 5.2 Interface rules

| Id | Attribute | Level | Applies when | Constraint | Source in `cprofile` |
|---|---|---|---|---|---|
| I1 | `keyOperations` | MUST | `interfaceType` = management | list, enumRef (`generate`, `import`, `export`, `wrap`, `unwrap`, `derive`, `request-certificate`, `rotate`, `zeroize`, `none`) | `key_operations` |
| I2 | `keyTypesSupported` | MUST | `interfaceType` = management | list, minCount 1, registry names | none; this is the gap `cprofile` does not cover |
| I3 | `keyTypes` | MUST | `interfaceType` = management | list, minCount 1 | present-state counterpart of I2, required by C12 |
| I4 | `keyStoreFormatsSupported` | SHOULD | `interfaceType` = management | list | `supported_formats` |
| I5 | `keyStoreLocation` | MUST | `interfaceType` = management | enumRef (`software`, `hsm`, `tee`, `tpm`, `os-keyring`, `external-vault`) | `store_type` |
| I6 | `keyStoreRef` | SHOULD | `interfaceType` ∈ service, peer, storage | reference to a declared management interface | `key_management_ref` |
| I7 | `externalDependencies` | MUST | always | list, enumRef (`certificate-authority`, `revocation-responder`, `directory`, `identity-provider`, `hsm`, `key-vault`, `time-source`, `none`) | `external_dependencies`, `revocation_check` |
| I8 | `enablementSetting` | SHOULD | `enablementMethod` = configuration | present | `governing_parameters` |
| I9 | `keyWrapping` | MUST | `interfaceType` = storage | present | `data_at_rest_protection` |
| I10 | `keyWrappingSupported` | MUST | `interfaceType` = storage | list, minCount 1 | none |

I2 is the attribute with the most value in the extended profile. The case it catches is ordinary.
A TLS listener supports ML-DSA certificates, and the product's key tool can neither generate an
ML-DSA key nor produce a CSR for one. Every interface rule in the baseline passes, and the
operator still cannot migrate.

I7 records operator-side sequencing. It is not a supplier blocker. `blockedBy` says what stops the
supplier. `externalDependencies` says what the operator must move first. An interface cannot
present an ML-DSA chain before the CA issues one, and cannot rely on revocation before the
responder signs with an algorithm its clients verify.

I9 and I10 target asymmetric wrapping of data keys, for example RSA-OAEP over an AES key. The
bulk cipher is out of scope for the same reason `encryptionSupported` is excluded in the baseline.

### 5.3 Overrides

| Target | Change |
|---|---|
| `pqc-migration#G1.4` | SHOULD → MUST |

### 5.4 Candidates held back

- **`trafficPlane`** (control, management, data). It comes from `data_classification`. It is
  intrinsic to the product, so it passes the Q36 test for product scope. It has not yet been
  shown to change a planning action beyond what `interfaceType` already gives. Revival trigger:
  a telecom or IoT use case where signalling and user-plane interfaces of the same type migrate
  on different timetables.
- **Per-platform capability within one document.** See fork F2. Revival trigger: a producer
  that cannot issue one document per platform build.

## 6. Exclusions to record

| Item | Reason |
|---|---|
| Cipher suite lists | Redundant with the decomposed attributes, and TLS 1.3 suites do not carry key exchange or signature |
| Port numbers | Deployment-configured; the product's default is documentation, not a migration fact |
| `quantum_safe`, `fips_approved` flags | Judgements or derivations; decision 0002. The facts they derive from are required instead |
| Secret protection (stash files, obfuscation, environment variables) | Classical hygiene with no bearing on migration sequencing. It belongs to a hardening profile |
| Key entry method and key ceremony | Operational procedure, not declarable at an interface |
| Audit, intrusion detection, authorisation filters, programmatic exits | Not cryptographic facts |
| Sensitivity labels and confidentiality lifetime | Deployment scope; Data Exposure and Q36 |
| Individual keys and key identifiers | Q39 is unsettled. The profile describes stores and what they can hold, not keys |

## 7. Forks that need a call

**F1. What the baseline is.**
- A: the existing `pqc-migration`, re-issued as v0.7. *(recommended)*
- B: a new, shallower profile carved out of v0.6, with v0.6 re-parented onto it. This is Q64
  option C.
- A keeps a reviewed profile intact and adds a depth. B would settle Q64 as well, at the cost of
  moving rule ids and revising a reviewed profile. A does not prevent B later.

**F2. Platform variance.**
- A: one document per platform build, distinguished by purl qualifiers. No new mechanism;
  `interface-disclosure#P3` already requires subject identity. *(recommended)*
- B: a platform-keyed group inside each interface.
- The case is real: the same product may reach ML-KEM on one platform's provider a release before
  another. A handles it with nothing new. B is only needed if a producer cannot issue separate
  documents.

**F3. How key management is modelled.**
- A: as management interfaces carrying key attributes. *(recommended)*
- B: a new relationship type, `key-management`, in `scope.relationshipTypes`.
- A fits the existing model and `interface-disclosure#P2`. B is more expressive, and it opens the
  Model section and the parked edge model.

**F4. Where module validation sits.**
- A: baseline MUST. *(recommended)*
- B: extended only.
- A is cheap because `none` is a valid answer, and it gives `blockedBy: certification` something to
  stand on.

**F5. `keyStoreRef` needs a new constraint kind.**
- A: add `refersTo`, which checks that the reference resolves to a declared interface of a named
  type. C17 then requires the evaluator to implement it. *(recommended)*
- B: use `present`, which accepts any string and so catches only omission.

**F6. Future-state content.**
- Nothing new here. The extended profile inherits the baseline's position on Q26.

## 8. Work sequence

| Step | Output | Depends on | Size |
|---|---|---|---|
| 1 | Calls on F1 to F5 | — | Small |
| 2 | Decision record 0022, covering both depths and the `cprofile` mapping; new open questions from Q66 for held-back candidates | 1 | Small |
| 3 | `profile-pqc-migration.rules.json` v0.7: I10, I11, G1.4, changelog entry | 1 | Small |
| 4 | Update `cbom-pqc-pass` and `cbom-pqc-fail` for v0.7 | 3 | Small |
| 5 | `profile-pqc-migration-extended.rules.json` v0.1 | 3 | Medium |
| 6 | Two new example documents. Pass: listener, key tool able to generate ML-DSA, storage interface with ML-KEM wrapping available. Fail: the key tool gap only, so the example isolates I2 | 5 | Medium |
| 7 | Evaluator: `refersTo` (if F5-A), storage absence attribute, a check in `check_scope_narrows` that a derived profile does not drop an in-scope purpose; fixtures for each new rule; `run-profile-tests.sh` and `check-family.py` asserting extended ⊇ baseline | 5 | Medium |
| 8 | `mapping-cyclonedx-spdx.md` rows for the new attributes, CycloneDX first | 5 | Small |
| 9 | Site: PQC Migration and Maturity pages show the family; the use-case page names both depths | 5–7 | Small |
| 10 | Note to `cbomgen` with §2 and a `cprofile` → CycloneDX conversion sketch | 2 | Small |

The worked example should use a neutral product, as the existing examples use nginx. The
`cprofile` descriptions draw on a specific vendor's product (`runmqakm`, `CHLAUTH`, GSKit). The
patterns carry over, but the methodology examples should not name that product.
