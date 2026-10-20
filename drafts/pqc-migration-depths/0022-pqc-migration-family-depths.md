# 0022. The PQC migration family has two depths, and a storage interface is described as data at rest

- **Status:** Proposed (draft; promotes to `decisions/` with the three rules files)
- **Date:** 2026-09-26 (rewritten to match `docs/use-cases/pqc-migration.html`)
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

Applying the family to Keycloak 26.7.3 then showed that several facts about one interface differ
from one cryptographic purpose to another: the route that enables the capability, the minimum
version, how algorithms are negotiated, what constrains enabling it. Stated once per interface they
are wrong for one purpose or the other. They have to be stated per purpose.

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

Proposed: Option B. The decision is the structure in the first two points. Everything after them
records how that structure was worked out and what it touches.

**1. Two depths of one family.** `pqc-migration` v0.7 is the baseline depth. A new profile
`pqc-migration-extended` v0.1 extends it and asks the second group of questions: the key
management surface, the storage path and the external services around an interface. They serve the
same consumer and the same decision (decision 0019).

**2. A storage interface is data at rest.** The channel rules do not apply to it, and its own
attributes stand in for key exchange and authentication. A network path to remote storage is a
separate service or interconnect interface, so one store can appear twice, each time described in
the words that fit it.

The rest of this section states the rules that follow. The use-case page
`docs/use-cases/pqc-migration.html` is the target model; where this record and the page differ, the
difference is listed under "Differences from the page".

### The three profiles and their versions

The word "baseline" has been used for two profiles. It is avoided below: `interface-disclosure` is
the disclosure profile and `pqc-migration` the migration profile.

| Profile | Version | Change |
|---|---|---|
| `interface-disclosure` | v0.7 → v0.8 | Storage guards on `I1`, `I2`, `I3`, `I5`, `I6`. New `I10`, `I11` (module validation) and `I12` (key wrapping). |
| `pqc-migration` | v0.6 → v0.7 | Five interface rules, the nine-member group `G1`, the purpose `key-wrapping`. |
| `pqc-migration-extended` | new, v0.1 | Storage declared, key management, dependencies, product certification. |
| Interface Enumeration | v0.1 → v0.2 | `I1`, `I2` guarded to skip storage. |

### `interface-disclosure` v0.8: what it adds

- **`I10 moduleValidationScheme`** (MUST) and **`I11 moduleValidationRef`** (MUST where a scheme
  other than `none` is declared). The vocabulary lists only schemes that validate the cryptographic
  implementation. `none` is a complete answer. They state present state, so they belong to an
  inventory profile (F4).
- **`I12 keyWrapping`** (MUST on a storage interface): the algorithm protecting the data keys now,
  or `none`. It stands in for `I3 keyExchange` and `I5 authentication` on storage.
- Guards on `I1`, `I2`, `I3`, `I5`, `I6` so that a storage interface is not asked for a protocol,
  version, key exchange, authentication or endpoint roles. `I4 encryption` and `I9
  implementationPurl` still apply.
- The vocabulary `moduleValidationSchemeVocabulary` moves here with the rules.

### `pqc-migration` v0.7: what it holds

**Five interface rules, numbered without gaps.**

| Id | Attribute | Level | Id in the first v0.7 draft |
|---|---|---|---|
| `I1` | `protocolVersionsSupported` | MUST, not on storage | `I1` |
| `I2` | `keyExchangeSupported` | MUST, not on storage | `I2` |
| `I3` | `authenticationSupported` | MUST, not on storage | `I3` |
| `I4` | `providerLocation` | MUST | `I6` |
| `I5` | `coexistence` | MUST | `I7` |

plus **`I6 keyWrappingSupported`** (MUST on a storage interface), the capability counterpart of
`interface-disclosure#I12`. See "Key wrapping: one attribute or a pair".

**One group, `G1`, one entry per cryptographic purpose, nine members.**

| Id | Attribute | Level | Id in the first v0.7 draft |
|---|---|---|---|
| `G1.1` | `enablementMethod` | MUST | `I4` (interface rule) |
| `G1.2` | `minimumProductVersion` | MUST when `enablementMethod` is `software-update` | `I5` (interface rule) |
| `G1.3` | `negotiationStrategy` | MUST | new |
| `G1.4` | `negotiationControl` | SHOULD | `I8` (interface rule) |
| `G1.5` | `integrationConstraints` | SHOULD | `I9` (interface rule) |
| `G1.6` | `capabilityStatus` | MUST | `G1.1` |
| `G1.7` | `blockedBy` | MUST when `capabilityStatus` is not `available` | `G1.2` |
| `G1.8` | `roadmapRef` | MAY | `G1.3` |
| `G1.9` | `validatedModeAvailability` | SHOULD when `capabilityStatus` is `available` | `G1.4` |

`enablementMethod`, `minimumProductVersion`, `negotiationControl` and `integrationConstraints`
were interface rules (`I4`, `I5`, `I8`, `I9`). They are now members, because their answer differs
by purpose on one interface and stating them in both places would define each twice. `I4`, `I5`,
`I8`, `I9` are removed as interface rules. `negotiationStrategy` is new: how the interface selects
an algorithm (`static`, `exclusive`, `preference-order`, `client-controlled`, `dynamic`), where
`negotiationControl` says whether the operator can change it. `algorithms` is not a member: the
algorithms an interface can negotiate are carried by `I2`, `I3` and `I6`. `keyCoverage` stays
`all-purposes`.

The module validation rules are not rules of `pqc-migration`. They arrive by inheritance from
`interface-disclosure` v0.8. The first v0.7 draft of this file carried them as `I10`, `I11`, `I12`.

**Purpose obligations.** Without these the group is not testable:

- A storage interface owes only the `key-wrapping` entry.
- Any other interface owes `key-establishment` and `entity-authentication` with all nine members.
- For the other four purposes (`encryption`, `data-integrity`, `non-repudiation`, `key-derivation`)
  only `G1.6`, `G1.7` and `G1.9`. `encryption` stays a deferred purpose.

**Extended depth.** `pqc-migration-extended` takes `key-wrapping` in depth, so its entry owes all
nine members. It tightens `pqc-migration#G1.9` to MUST and keeps the guard, so the result is a
conditional MUST: a derived profile may remove a guard but not add or narrow one. Its other rules:

- `P1` storage interfaces declared, or their absence stated (MUST).
- `P2` product-level certification scheme (SHOULD).
- `I1`–`I7` key attributes on management interfaces, guarded by `keyManagementFunction`. The most
  important of them is `I3 keyTypesSupported`.
- `I8 keyStoreRef` from each non-management interface to its key management surface (SHOULD).
- `I9 externalDependencies` (MUST).
- `enablementSetting` where enablement is by configuration (SHOULD). It was `I10`, an interface
  rule guarded on `enablementMethod`. That guard has no single value to test now that
  `enablementMethod` exists per purpose, so the attribute belongs in `G1` as a member. The rules
  format cannot express a member added to an inherited group (format addition 3 below), so the
  rules file records it under `$proposedGroupMember` and does not evaluate it.

### The purpose `key-protection` is renamed `key-wrapping`

The vocabulary in decision 0010 lists `key-protection`. This record renames it `key-wrapping`:
the job is wrapping keys at rest, and "protection" says nothing a reader can act on. It is a
vocabulary change to a published decision. It is recorded here and not by editing 0010, whose
history line stays as history. Link it from 0010 when this record is promoted. The tool accepts
both names.

### Key wrapping: one attribute or a pair

The use-case page lists key wrapping as one attribute, `interface-disclosure#I12
keyWrappingSupported`. This record does not follow it, for a reason found by running the profile
checks: the name ends in `Supported`, which the methodology reads as forward-looking. Check C12
forbids an inventory profile (`interface-disclosure` is one) from requiring a forward-looking
attribute, and requires a profile declared `both` (`pqc-migration`) to require the present-state
counterpart of every capability attribute it requires. A single `keyWrappingSupported` in either
profile fails C12.

The decision is to treat key wrapping as key exchange and authentication are treated: a
present-state attribute in `interface-disclosure` (`I12 keyWrapping`, beside `I3 keyExchange` and
`I5 authentication`) and a capability attribute in `pqc-migration` (`I6 keyWrappingSupported`,
beside `I2` and `I3`). `Supported` is the methodology's suffix for what an interface is able to use
(decision 0005). The user directed this on review.

### Differences from the page

The page has been updated to match this record on the four points below, which were differences
earlier. They are kept so the reasoning is not lost, and so the page can be checked against them:

1. Key wrapping is a pair (`interface-disclosure#I12 keyWrapping`, `pqc-migration#I6
   keyWrappingSupported`), not the single `interface-disclosure#I12 keyWrappingSupported`.
2. The page's baseline interface-rule table lists `pqc-migration#I6`.
3. The page's extended table lists `enablementSetting` as the proposed member
   `pqc-migration-extended#G1.10`, pending format addition 3.
4. The page's extended table says conditional MUST for the `G1.9` override.

### Two further decisions on the structure

- **Storage in the other profiles.** Interface Enumeration v0.2: `I1 protocol` and `I2
  protocolVersion` are guarded to skip storage, identical to the same rules in the disclosure
  profile. `pqc-migration` `I1`–`I3` take the same guard. `pqc-migration-extended` keeps only the
  obligation to declare storage interfaces (`P1`). Once a storage interface is declared, every
  depth describes it.
- **Ids are renumbered.** Nothing counts as released, including the published v0.6 file
  (decision 0011 allows renumbering until a version is released). `G1.1`–`G1.3` therefore mean
  different attributes from the published v0.6 file (`capabilityStatus`, `blockedBy`,
  `roadmapRef`), and `I6`, `I7` become `I4`, `I5`. The history lines in decisions 0010 and 0011
  describe the old meaning and stay as history. Once a version is released, an id retired from it
  is not reused.

### Two additions to the rules format, and one open question

The page states things the validator cannot check today. They are **proposed**; this record
declares them in the rules files and does not change `validate_cbom.py`,
`profile.schema.json` or `check_profile.py`.

1. **Applicability guard per purpose key** (`keyApplicability` on the group). `required_keys`
   returns the whole vocabulary for `all-purposes`, so a storage interface would owe an entry for
   every purpose and a TLS interface would owe `key-wrapping`. A guard on a member cannot help:
   it is evaluated against the entry's own attributes and does not see `interfaceType`. The
   guard has the shape of `requiredWhen`, is evaluated with `condition_holds` against the
   interface, and reports a key that does not apply as `n/a`. `key-wrapping` is required where
   `interfaceType` equals `storage`, every other key where it does not. It needs a schema property,
   `required_keys` and `check_group_rule` changes, a check in `check_profile.py` (C13 and C17), and
   a line in decision 0014 that a derived profile may not narrow the guard.
2. **A flag on in-scope-only members** (`inScopeOnly` on `G1.1`–`G1.5`). The validator drops only
   `MAY` members for a purpose outside the declared scope (`check_group_rule`). The page says a
   deferred purpose owes `G1.6`, `G1.7` and `G1.9` only; without the flag five more members would
   be required for it. The flag extends the existing skip from `MAY` members to flagged members.
   One group and nine members are kept. A hand-written guard on each member was rejected: it would
   restate the scope list in a second place, and C13 could no longer see the two drift apart.
   Splitting the group in two was rejected: every example would carry two group names for one
   concept.
3. **Adding a member to an inherited group** (needed for `enablementSetting`). A derived profile
   can override an inherited member's level and nothing more. An `extends` property on a group in
   a derived profile is one possible form. It is not proposed in detail here; it is listed so the
   working group sees that moving `enablementSetting` into `G1` needs it.

If the working group will not accept a change to the evaluator before ratification, the fallback
for the first item is to drop storage from `G1` and keep `interface-disclosure#I12`. The Keycloak
failing example would then fail `I12`, and the per-purpose result for stored keys ("not-planned,
blocked by product") would be lost.

Until the evaluator reads these, it requires an entry for all seven purposes on every interface
and all nine members in every entry, so no document conforms. This is stated in the rules files
and in the extended profile's `$pendingTooling`. The verdicts in this record were produced with
the gaps patched outside the repository.

### The absent-attribute cascade

A `notEquals` guard holds when the guarded attribute is absent. Three rules are affected:
`interface-disclosure#I11` (guard `moduleValidationScheme` not `none`), `pqc-migration#G1.7`
(guard `capabilityStatus` not `available`), and the storage guards (`interfaceType` not
`storage`). Omitting the guarded attribute fails the guarded rule as well, so one omission produces
two failures: `I10` and `I11`, `G1.6` and `G1.7`, `I7` and the channel rules. A guard of `equals`,
such as the one on `G1.2` (`enablementMethod` equals `software-update`), makes the rule not
applicable when the attribute is absent and does not cascade.

**Open for the working group; this record takes no position.** Either the cascade is accepted and
documented, or a `notEquals` guard is treated as not met when its attribute is absent, which changes
the evaluator and every profile that uses one. The rules files and `$pendingTooling` state the
question and the affected rules.

### Subsidiary calls (F1–F5)

- **F1.** The existing profile is the migration profile (Option B above). Q64 stays open.
  Option C remains available later.
- **F2.** Variation between platform builds is carried by one document per build, distinguished by
  Package URL qualifiers under `interface-disclosure#P3`. No platform-keyed group.
- **F3.** Key management surfaces are management interfaces with key attributes, not a new
  relationship type.
- **F4.** Module validation is required in the disclosure profile (`interface-disclosure` v0.8),
  not only at the extended depth. It is a present-state fact, so it belongs to an inventory
  profile, and C12 does not object because neither attribute is forward-looking.
- **F5.** `keyStoreRef` is to be evaluated by a new `refersTo` constraint. Until the evaluator
  implements it, the rule checks presence only and says so.

### Applying the family to a real product (K1–K10)

The Keycloak examples forced further calls. Each is either a statement of how existing rules are
read or a note on one rule, and none adds a rule:

- **K1. The subject of a product document is a build with a fixed cryptographic runtime.** Where
  a distribution takes its provider from the operator, as a Java application's ZIP takes the
  operator's JDK, the capability of that provider is a deployment fact. The product document
  describes the build that fixes it. For Keycloak, that build is the container image, identified by
  an OCI Package URL with its digest. This is F2 applied: other builds are other documents.
- **K2. An interface is a logical cryptographic boundary, not a port.** Two layers of cryptography
  on one port are two interfaces. Signed tokens carried over HTTPS are a token interface
  (`OIDC`, `SAML`) beside the TLS interface. The existing attributes keep their sense at both
  layers: `authentication` is the signature that proves the sender, and `keyExchange` is how the
  content key reaches the recipient. Stated in the disclosure profile as `$commentInterface`.
- **K3. `none` is an accepted value for an algorithm attribute.** It states that no algorithm is
  applied for that job, as with tokens that are signed and not encrypted. It is distinct from the
  `unknown` and `withheld` markers, which report the producer's knowledge or willingness rather than
  the product. Stated in the disclosure profile alongside its identifier schemes.
- **K4. `keyStoreRef` accepts the literal `out-of-band`.** TLS keys supplied as files have no
  managing surface in the product. A `withheld` marker would claim something is held back when
  nothing is. The future `refersTo` constraint must accept the literal.
- **K5. A management interface that performs no key functions declares
  `keyManagementFunction: none`.** Keycloak's health and metrics port is the example. This needed
  no change: the guard already exists.
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
  way. Plain HTTP depends on no protocol component, and the document shows the missing protection
  structurally. A key store the product writes to is a service too. A service counts as an
  interface when it applies cryptography of its own or is reachable without transport
  protection; one that only rides a declared transport does not, which keeps interface counts
  and the coverage statement stable. In the carrier, a service that is an interface carries the
  interface attributes; one declared only for its layering carries none. The counting rule is
  stated in the disclosure profile; the representation is in the draft mapping. The explicit `none`
  of K3 stays, because a missing dependency cannot distinguish "none" from "not declared".
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
  location, coexistence and capability by purpose may be stated on the providing implementation
  and inherited. The capability entry now carries enablement method, minimum product version,
  negotiation strategy, negotiation control and integration constraints, so those are inherited
  and overridden with it, per purpose and as a whole entry. An interface states only what differs.
  The cluster transport inherits the JDK block and overrides entity authentication. SAML inherits
  Keycloak's block and overrides two purposes. Boundary attributes (`interfaceType`,
  `endpointRoles`, `lifecycleStage`, the algorithm attributes) are never inherited. Rules are
  evaluated on effective values, so no rule changes, and the evaluator must resolve inheritance.
  Each distinct TLS configuration becomes one shared protocol component without `interfaceType`.
  Effect on the extended example: properties 454 → 297, suite group and scheme entries
  414 → 89, file size 98 KB → 61 KB. The cost: a reader has to resolve inheritance to see an
  interface's full answer. Future-state statements now also sit on library components, which
  touches Q26.
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

### What the Keycloak examples show

The four example documents were built from the corrected cprofile, with application-layer
interfaces as services under K7, and validate against the CycloneDX 1.7 schema. The model is
13 interfaces: seven TLS interfaces, four application-layer interfaces implemented by Keycloak, the
cluster transport, and the realm key storage `sto-realm-keys`.

With the evaluator gaps patched outside the repository (see the consequences below), the two
conforming documents conform. **Each non-conforming document fails exactly one rule.** The
migration failing example fails the **group rule `pqc-migration#G1`**: `sto-realm-keys` has no
`key-wrapping` entry. A missing entry is reported against the group and names the purpose; a member
such as `G1.6` fails only inside an entry that exists. The extended failing example fails
`pqc-migration-extended#I3`. The extended document also conforms to every shallower profile in the
family, so monotonicity holds on a real product. Further findings:

- The absent-attribute cascade above. It is why the migration failing example isolates the group
  rule and not a rule guarded by `notEquals`.
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
is the `key-wrapping` purpose, not key establishment. Dropping `storage` from the interface
types would lose the stored-ciphertext case the harvest-now-decrypt-later analysis depends on,
and with it the per-purpose capability group, which fits storage well.

The guards relax five rules for storage interfaces. The defence is the one decision 0012 gave for
the management-interface rule: a rule that no legitimate subject can satisfy honestly is wrong,
not strict. The cost is small in practice. None of the published examples declares a storage
interface, and every example's verdict against the draft profiles is unchanged.

`keyWrapping` sits in the disclosure profile, not in a migration profile, because it answers that
profile's decision. When RSA weakens, a storage path whose data keys are wrapped under RSA is one
of the affected interfaces. Its capability counterpart sits in the migration profile for the
reason C12 gives.

**The two depths.**

The migration profile's addition is small because it has to be. Module validation is public,
`none` answers it for unregulated products, and without it the existing `blockedBy: certification`
value has nothing to stand on. Everything else `cprofile` offers asks for information a producer
may not hold today, which is the case decision 0019 makes for a deeper profile rather than a
heavier baseline.

The extended depth serves the same decision, so it is a depth and not a branch. The decision
already asks "what enabling it requires". The migration profile answers it at the interface. The
extended depth answers it for the key management surface, the storage path and the external
services the interface cannot move without.

**The group.** The nine members are the facts that differ from one purpose to another on the same
interface (route, version, negotiation, constraints) and the status facts that were already
per purpose. An interface-level default for the four moved rules was considered. If the working
group wants one, that is a new rule, not a restored one.

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

- `pqc-migration` v0.6 → v0.7 is a tightening. `interface-disclosure` v0.7 → v0.8 is a relaxation
  for storage and a tightening by `I10`, `I11` and `I12`. A document conforming to the published
  v0.6 does not conform to v0.7 until it states module validation and capability per purpose. The
  v0.6 examples do not state either and must be updated before promotion.
- **Every profile extending `interface-disclosure` inherits two further MUSTs** (`I10`, and `I11`
  where a scheme other than `none` is declared). `drafts/procurement/profile-procurement.rules.json`
  extends v0.8 and says it adds no per-interface attribute; that statement holds, but its example
  must state module validation, and its verdicts are rechecked in the supporting drafts.
- The three rules files are well-formed under C1–C17 with no warnings (`check_profile.py`). The
  extended profile's examples are drafted once the rules are agreed.
- **Evaluator work, deferred.** (1) `enumRef` on list attributes is evaluated against the whole
  list and so fails every document. `I2`, `I5`, `I6` and `I9` of the extended profile need
  element-wise evaluation. C17 does not catch this. (2) `refersTo` for `I8`. (3)
  `check_scope_narrows` does not read `cryptographicPurposes`, so dropping an in-scope purpose goes
  unnoticed. (4) The three rules-format additions above.
- Four published profiles change, not one: Interface Enumeration v0.1 → v0.2 (relaxing),
  `interface-disclosure` v0.7 → v0.8, `pqc-migration` v0.6 → v0.7, and the new
  `pqc-migration-extended`. The two interface profiles keep their existing examples and remain
  clean. The shared rules of the enumeration and disclosure profiles remain identical.
- `pqc-migration#G1.4 negotiationControl` (SHOULD) now sits inside each purpose entry. On a storage
  interface only the `key-wrapping` entry exists, and `G1.4` applies there only when
  `key-wrapping` is in scope. It is a SHOULD and decides no verdict.
- **The mapping changes** (K7): `mapping-cyclonedx-spdx.md` is drafted beside the profiles and
  replaces the published one on promotion. Brokered token verification became an interface of
  its own under K7, because Keycloak verifies external providers' signatures itself.
- **Evaluator work added by the examples.** The CycloneDX adapter does not read services, and reads
  a fixed list of attributes, so every attribute added in these drafts is reported absent. It has
  no way to read an explicit `none` for an algorithm attribute. And the guard-on-absence behaviour
  above needs a decision. All are listed in the extended profile's `$pendingTooling`.
- **Deferred with a revival trigger.** A storage counterpart to `protocol`, meaning the container
  or envelope format (for example LUKS2 or CMS). Trigger: a consumer who has to group storage
  interfaces by format to act on a published weakness.
- **Deferred with revival triggers.** `trafficPlane` (trigger: interfaces of one type that migrate
  on different timetables by plane) and a platform-keyed group (trigger: a producer that cannot
  issue one document per build). Both are recorded as exclusions in the extended profile.
- **Open for the working group.** Whether `enablementMethod` is a single value or a set;
  whether `integrationConstraints` can be structured; whether `negotiationControl` gets a separate
  field for the mechanism.
- **Model and Terms sections** need the K2 definition when these drafts are promoted. The
  published site is not edited until then.
- **Decision 0010** is not edited. This record states the rename of `key-protection` to
  `key-wrapping`; link it from 0010 on promotion.
- `cprofile.json` has no field for application-layer cryptography. Signed tokens can be recorded
  only in notes, which is why the Keycloak cprofile omits them. This is a request to the cprofile
  maintainers, not a methodology question.
- **Generator feedback grows** with items that apply to any CBOM generator, listed in the plan
  (§2a).
- Q22 and Q26 in the open-questions register carry dated notes pointing here.
- Feedback to the `cprofile` maintainers is in `plan-pqc-migration-depths-2026-09.md` §2.

## Links

- Decisions 0002, 0003, 0004, 0005, 0009, 0010, 0011, 0012, 0014, 0019, 0021.
- Q26 (inherited position on future-state content), Q36, Q39, Q64. The Data Exposure section's open point on storage attributes.
- `schemas/cprofile.json`; `plan-pqc-migration-depths-2026-09.md`.
- `docs/use-cases/pqc-migration.html`, the target model; `NOTE-alignment-with-use-case-page.md`.
