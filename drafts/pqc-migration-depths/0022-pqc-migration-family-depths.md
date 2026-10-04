# 0022. The PQC migration family has two depths, and a storage interface is described as data at rest

- **Status:** Proposed (draft; promotes to `decisions/` with the two rules files)
- **Date:** 2026-09-26
- **Aspect:** 3.9 — Building one profile on another (with consequences for 3.3, 3.4 and 3.7)
- **Topic / issue:** #9
- **Deciders:** not yet taken
- **Decision rule applied:** lazy consensus (pending)

## Context

`cprofile.json` is a product description format produced independently of an SBOM. It records
network interfaces with per-platform providers and validation status, key management utilities,
security controls and provenance. Read against the PQC migration profile v0.6, it adds little at
the interface level. The profile already asks more about each interface than `cprofile` carries.

What `cprofile` does carry is the estate around each interface. That estate decides whether the
interface can actually move. A listener that supports ML-DSA is not migratable if the product's
key tool cannot generate an ML-DSA key or a certificate request for one. A capability that exists
only outside the module's validated mode is not usable by a regulated operator. A storage path
whose data keys are wrapped under RSA is exposed to harvest-now-decrypt-later while every network
interface is migrated. None of these is expressible in v0.6.

The question is where these facts go: into the existing profile, into a new branch, or into a
deeper profile of the same family.

Drafting the extended depth exposed a second problem, which is older than this work. The
interface type vocabulary has always offered `storage`, and five of the nine interface rules in
the disclosure baseline describe a channel: `protocol`, `protocolVersion`, `keyExchange`,
`authentication`, and two `endpointRoles`. A backup file has none of them. No product declaring a
storage interface could conform honestly, at any depth. The Data Exposure section lists "whether
storage interfaces need attributes of their own" as open. Requiring storage interfaces to be
declared, as the extended depth does, makes the question unavoidable.

## Options considered

- **Option A — add everything to the existing profile.** One migration profile (trade-off: the
  entry cost for a supplier rises sharply, and the key management and storage rules require
  information many producers cannot yet give).
- **Option B — re-issue the existing profile as the baseline with a small addition, and publish
  the rest as an extended depth that extends it.** (trade-off: one more profile to govern.)
- **Option C — carve a new shallower baseline out of v0.6 and re-parent v0.6 onto it.** This is
  Q64 option C (trade-off: settles Q64 as well, and moves rule ids in a profile already reviewed).
- **Option D — a separate key management profile as a branch.** (trade-off: it answers the same
  decision, so ranking suppliers against it and the migration profile compares answers to one
  question under two names, which decision 0019 rules out.)

## Decision

Proposed: Option B.

**Baseline: `pqc-migration` v0.7.** Unchanged objective, scope and existing rules. Adds:

- `I10 moduleValidationScheme` (MUST) and `I11 moduleValidationRef` (MUST where a scheme is
  declared). The vocabulary lists only schemes that validate the cryptographic implementation.
  `none` is a complete answer.
- `G1.4 validatedModeAvailability` (SHOULD), stated per purpose where the capability is available.

**Extended: `pqc-migration-extended` v0.1**, extending v0.7. Same consumer and decision text,
one added decision option (sequence a dependency first). Takes `key-protection` in depth. Adds:

- `P1` storage interfaces declared, or their absence stated (MUST).
- `P2` product-level certification scheme (SHOULD).
- `I1`–`I7` key attributes on management interfaces, guarded by `keyManagementFunction`.
  The most important of them is `I3 keyTypesSupported`.
- `I8 keyStoreRef` from each non-management interface to its key management surface (SHOULD).
- `I9 externalDependencies` (MUST).
- `I10 enablementSetting` where enablement is by configuration (SHOULD).
- Tightens `pqc-migration#G1.4` to MUST.

**Storage interfaces are data at rest.** The channel rules do not apply to them, and one
attribute stands in for key exchange:

- **Interface Enumeration v0.2.** `I1 protocol` and `I2 protocolVersion` are guarded to skip
  storage interfaces. They stay identical to the same rules in the disclosure baseline.
- **Interface Disclosure Baseline v0.8.** `I1`, `I2`, `I3`, `I5` and `I6` are guarded the same
  way. `I4 encryption` and `I9 implementationPurl` still apply. New `I10 keyWrapping`, MUST on a
  storage interface: the algorithm protecting the data keys, or `none`.
- **pqc-migration v0.7.** Its `I1`–`I3` capability rules take the same guard. New
  `I12 keyWrappingSupported`, MUST on a storage interface.
- **pqc-migration-extended v0.1** keeps only the obligation to declare storage interfaces (`P1`).
  Once a storage interface is declared, every depth describes it.
- A network path to remote storage, such as a backup over TLS, is a separate service or
  interconnect interface. One store can therefore appear twice, each time described in the words
  that fit it.

Five subsidiary calls are part of this decision:

- **F1.** The existing profile is the baseline (Option B above). Q64 stays open. Option C
  remains available later.
- **F2.** Variation between platform builds is carried by one document per build, distinguished by
  Package URL qualifiers under `interface-disclosure#P3`. No platform-keyed group.
- **F3.** Key management surfaces are management interfaces with key attributes, not a new
  relationship type.
- **F4.** Module validation is required at the baseline, not only at the extended depth.
- **F5.** `keyStoreRef` is to be evaluated by a new `refersTo` constraint. Until the evaluator
  implements it, the rule checks presence only and says so.

**Applying the family to a real product (K1–K5).** The Keycloak examples forced five further
calls. Each is either a statement of how existing rules are read or a note on one rule, and none
adds a rule:

- **K1. The subject of a product document is a build with a fixed cryptographic runtime.** Where
  a distribution takes its provider from the operator, as a Java application's ZIP takes the
  operator's JDK, the capability of that provider is a deployment fact. The product document
  describes the build that fixes it. For Keycloak, that build is the container image, identified by
  an OCI Package URL with its digest. This is F2 applied: other builds are other documents.
- **K2. An interface is a logical cryptographic boundary, not a port.** Two layers of cryptography
  on one port are two interfaces. Signed tokens carried over HTTPS are a token interface
  (`OIDC`, `SAML`) beside the TLS interface. The existing attributes keep their sense at both
  layers: `authentication` is the signature that proves the sender, and `keyExchange` is how the
  content key reaches the recipient. Stated in the disclosure baseline as `$commentInterface`.
- **K3. `none` is an accepted value for an algorithm attribute.** It states that no algorithm is
  applied for that job, as with tokens that are signed and not encrypted. It is distinct from the
  `unknown` and `withheld` markers, which report the producer's knowledge or willingness rather than
  the product. Stated in the disclosure baseline alongside its identifier schemes.
- **K4. `keyStoreRef` accepts the literal `out-of-band`.** TLS keys supplied as files have no
  managing surface in the product. A `withheld` marker would claim something is held back when
  nothing is. The future `refersTo` constraint must accept the literal.
- **K6. `keyStoreRef` also accepts `product-managed` and `none`.** Keycloak's cluster transport
  key is generated, stored and rotated by the product with no operator surface, so neither a
  reference nor `out-of-band` is true. `product-managed` is the fact that tells an operator the key
  type cannot be changed by configuration. `none` covers an interface with no keys, following K3.
- **K7. In CycloneDX, an application-layer interface is a service.** CycloneDX's protocol types
  are security protocols only (TLS, SSH, IPsec, IKE, QUIC, DTLS and a few others), so OIDC, SAML,
  an administrative API and plain HTTP were being forced into `other`. They are services. A
  service's `dependencies` entry lists what carries it and the algorithm and key components it
  uses itself, so the layering K2 describes becomes machine-readable. HTTPS is itself a service:
  HTTP over TLS is an HTTP service that depends on a TLS component, and a protocol component
  describes the security protocol only. OIDC therefore depends on HTTPS, and HTTPS on TLS.
  JDBC, LDAP, SMTP and the cluster protocol are services over their TLS components in the same
  way. Plain
  HTTP depends on no protocol component, and the document shows the missing protection
  structurally. A key store the product writes to is a service too. A service counts as an
  interface when it applies cryptography of its own or is reachable without transport
  protection; one that only rides a declared transport does not, which keeps interface counts
  and the coverage statement stable. In the carrier, a service that is an interface carries the
  interface attributes; one declared only for its layering carries none. The counting rule is stated in the disclosure baseline; the
  representation is in the draft mapping. The explicit `none` of K3 stays, because a missing
  dependency cannot distinguish "none" from "not declared".
- **K8. Native CycloneDX fields first.** A `pkic:profile:` property is used only where no
  CycloneDX field records the same fact, at a derivable granularity, with a sufficient value set.
  Under that test the interface's `bom-ref` replaces `interfaceId`; `dependencies[].provides`
  carries the implementing library; `executionEnvironment` carries provider location; for TLS,
  `cipherSuites[].tlsGroups` and `.tlsSignatureSchemes` carry the supported sets, with
  `cryptoRefArray` holding what is in use; key components carry key types, formats and wrapping
  (`securedBy`); and `compositions` carries completeness, except `all-external`. The Keycloak
  example drops from 575 properties to 454. What remains is mostly the capability group, which
  CycloneDX does not model. The review is `mapping-native-fields-review.md`.
- **K9. Implementation facts are stated once, on what provides them.** The Keycloak example
  repeated a value on another interface in 283 of 440 interface properties. Its 13 interfaces
  had 5 distinct capability blocks and 2 distinct TLS configurations, because the facts belong
  to the JDK and to Keycloak's services, not to each listener. Module validation, provider
  location, enablement method, minimum product version, coexistence and capability by purpose
  may be stated on the providing implementation and inherited. An interface states only what
  differs, per attribute and per purpose. The cluster transport inherits the JDK block and
  overrides entity authentication. SAML inherits Keycloak's block and overrides two purposes.
  Boundary attributes are never inherited. Rules are evaluated on effective values, so no rule
  changes, and the evaluator must resolve inheritance. Each distinct TLS configuration becomes
  one shared protocol component without `interfaceType`. Effect on the extended example:
  properties 454 → 297, suite group and scheme entries 414 → 89, file size 98 KB → 61 KB. The
  cost: a reader has to resolve inheritance to see an interface's full answer. Future-state
  statements now also sit on library components, which touches Q26.
- **K10. Link, do not restate.** A comparison with a generator-produced CBOM for a commercial
  identity product (not reproduced here) showed three practices the Keycloak example lacked: a
  hashed reference to the source SBOM, a reference to vulnerability information, and the
  generator and supplier in `metadata`. The examples now carry all three natively: an SBOM
  BOM-Link at document level and on each library, the Keycloak advisories page, and `tools`,
  `supplier`, `manufacturer` and `licenses`. No rule requires them. The draft mapping states
  them as conventions. The comparison also confirmed K7 to K9 from the other side. With one TLS
  component shared across listeners, transport facts drift into free text on services and
  contradict the component. With no `provides`, nothing says which of several libraries
  implements an interface. With no algorithm primitive, key exchange and authentication cannot
  be derived.
- **K5. A management interface that performs no key functions declares
  `keyManagementFunction: none`.** Keycloak's health and metrics port is the example. This needed
  no change: the guard already exists.

**What the Keycloak examples showed.** The four example documents were built from the corrected
cprofile, with application-layer interfaces as services under K7, and validate against the
CycloneDX 1.7 schema. With three evaluator gaps patched outside the repository (see the consequences below),
the two conforming documents conform. Each non-conforming document fails exactly one rule:
`pqc-migration#I12` and `pqc-migration-extended#I3`. The extended document also conforms to
every shallower profile in the family, so monotonicity holds on a real product. Five further
findings:

- A `notEquals` guard holds when the guarded attribute is absent. Omitting
  `moduleValidationScheme` therefore fails `I11` as well as `I10`, which is why the baseline's
  non-conforming example isolates `I12` instead.
- CycloneDX's protocol type has no value for OIDC, SAML or plain HTTP. Those interfaces carry
  `other`, and the name survives only in the component name. This is a mapping gap, not a rule
  gap.
- `externalDependencyVocabulary` has no value for a database. Keycloak's key storage depends on
  one. Candidate addition.
- `keyWrappingSupported` on a storage path that supports no wrapping holds the single value
  `none`. K3 applies to lists as well as to single values.
- Every Keycloak interface has `enablementMethod: not-available`. The per-purpose group is what
  makes the document informative anyway: four different blockers on four different timetables.

## Rationale

**Storage.** Three alternatives were rejected. A "not applicable" disclosure marker would reopen
decision 0003 and weaken every rule, because a validator cannot tell an honest answer from
avoidance. Reusing the channel attributes with storage meanings, such as `keyExchange` for the
wrapping algorithm, gives one word two senses, which decision 0021 forbids. Wrapping keys at rest
is the `key-protection` purpose, not key establishment. Dropping `storage` from the interface
types would lose the stored-ciphertext case the harvest-now-decrypt-later analysis depends on,
and with it the per-purpose capability group, which fits storage well.

The guards relax five rules for storage interfaces. The defence is the one decision 0012 gave for
the management-interface rule: a rule that no legitimate subject can satisfy honestly is wrong,
not strict. The cost is small in practice. None of the published examples declares a storage
interface, and every example's verdict against the draft profiles is unchanged.

`keyWrapping` sits in the disclosure baseline, not in a migration profile, because it answers the
baseline's decision. When RSA weakens, a storage path whose data keys are wrapped under RSA is
one of the affected interfaces.

**The two depths.**

The baseline addition is small because it has to be. Module validation is public, `none` answers
it for unregulated products, and without it the existing `blockedBy: certification` value has
nothing to stand on. Everything else `cprofile` offers asks for information a producer may not
hold today, which is the case decision 0019 makes for a deeper profile rather than a heavier
baseline.

The extended depth serves the same decision, so it is a depth and not a branch. The baseline's
decision already asks "what enabling it requires". The baseline answers it at the interface. The
extended depth answers it for the key management surface, the storage path and the external
services the interface cannot move without.

Two separations follow from not repeating `cprofile`'s conflations. Module validation and product
certification certify different objects, so they are different attributes at different depths.
Validated-mode availability is recorded as a fact per purpose; whether validated mode is required
is operator policy and stays out. The attribute was first drafted as `approvedModeAvailability`
and C6 rejected it: "approved" is a judgement token. The rename is correct, not cosmetic. What the
producer can state is whether the capability works in the validated mode. Whether that mode is
approved for a purpose is not the producer's statement to make.

**K2 and K3** were chosen over two alternatives. One was to record token cryptography as a
property of the TLS interface, which would require a second `authentication` value on one entry
and would lose the difference in timetable. For an identity provider, that difference is the whole
migration: the TLS layer follows the Java runtime, and the token layer waits on the JOSE
standards. The other was to leave application-layer cryptography out as internal. It is not
internal. Every relying party verifies it, so it is the most exposed cryptography the product has.

## Consequences

- Baseline v0.6 → v0.7 is a tightening. The v0.6 examples do not state module validation and must
  be updated before promotion.
- The extended profile is well-formed under C1–C17 except C9 (SHOULD). Its examples are drafted
  once the rules are agreed.
- **Evaluator work, deferred.** (1) `enumRef` on list attributes is evaluated against the whole
  list and so fails every document. `I2`, `I5`, `I6` and `I9` need element-wise evaluation. C17
  does not catch this. (2) `refersTo` for `I8`. (3) `check_scope_narrows` does not read
  `cryptographicPurposes`, so dropping an in-scope purpose goes unnoticed.
- Three published profiles change, not one: Interface Enumeration v0.1 → v0.2 (relaxing),
  Interface Disclosure Baseline v0.7 → v0.8 (relaxing for storage, tightening by `keyWrapping`),
  pqc-migration v0.6 → v0.7. All four drafts are well-formed under C1–C17. The two interface
  profiles keep their existing examples and remain clean. The existing examples give the same
  verdicts against the drafts as against the published versions. The shared rules of the
  enumeration and disclosure profiles remain identical.
- `pqc-migration#I8 negotiationControl` (SHOULD) still applies to storage interfaces, where it
  has no meaning. It is a SHOULD and decides no verdict. It is noted here and not guarded, to keep
  the change minimal.
- **The mapping changes** (K7): `mapping-cyclonedx-spdx.md` is drafted beside the profiles and
  replaces the published one on promotion. Brokered token verification became an interface of
  its own under K7, because Keycloak verifies external providers' signatures itself.
- **Evaluator work added by the examples.** The CycloneDX adapter does not read services, and reads a fixed list of
  attributes, so every attribute added in these drafts is reported absent. It has no way to read
  an explicit `none` for an algorithm attribute. And the guard-on-absence behaviour above needs a
  decision. All three are listed in the extended profile's `$pendingTooling`.
- **Deferred with a revival trigger.** A storage counterpart to `protocol`, meaning the container
  or envelope format (for example LUKS2 or CMS). Trigger: a consumer who has to group storage
  interfaces by format to act on a published weakness.
- **Deferred with revival triggers.** `trafficPlane` (trigger: interfaces of one type that migrate
  on different timetables by plane) and a platform-keyed group (trigger: a producer that cannot
  issue one document per build). Both are recorded as exclusions in the extended profile.
- **Model and Terms sections** need the K2 definition when these drafts are promoted. The
  published site is not edited until then.
- `cprofile.json` has no field for application-layer cryptography. Signed tokens can be recorded
  only in notes, which is why the Keycloak cprofile omits them. This is a request to the cprofile
  maintainers, not a methodology question.
- **Generator feedback grows** with items that apply to any CBOM generator, listed in the plan
  (§2a).
- Q22 and Q26 in the open-questions register carry dated notes pointing here.
- Feedback to the `cprofile` maintainers is in `plan-pqc-migration-depths-2026-09.md` §2.

## Links

- Decisions 0002, 0003, 0004, 0005, 0010, 0011, 0012, 0014, 0019, 0021.
- Q26 (inherited position on future-state content), Q36, Q39, Q64. The Data Exposure section's open point on storage attributes.
- `schemas/cprofile.json`; `plan-pqc-migration-depths-2026-09.md`.
