---
title: PQC Migration
sideMenu: true
weight: 5
aliases:
- /cbom/use-cases/pqc-migration.html
linkTitle: PQC Migration
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

This page develops one use case, from the decision a consumer is trying to make through to two profile definitions. It applies both profiles to one real product throughout: Keycloak 26.7.3, an open-source identity provider. It follows the twelve steps set out in [Method](../../methodology/method/). It is the reference example for how the other use cases are worked up.

Illustrative, and in review. The profiles and example documents follow draft decision 0022, which revises the migration profile to v0.7, adds a second, more demanding profile (the extended depth), and states how application-layer interfaces are expressed in CycloneDX. The attribute names are proposals made for this example, not established terms. The Keycloak values are taken from its documentation and issue tracker; the few still to be verified are marked.

## The decision being supported

An operator runs a product it did not build and cannot inspect. It needs to answer three questions about every interface that product exposes, and it needs the answers in a form it can aggregate across hundreds of instances.

-   Can this interface be made quantum-safe at all, and if so with which algorithms?
-   What would it take: a configuration change, a software update, or new hardware?
-   What breaks when we do it, and can we do it while the other end is still classical?

An inventory of algorithms cannot answer any of these questions. Knowing which algorithms an interface uses today leaves all three unanswered. The questions concern what the interface is capable of, how that capability is enabled, and what enabling it costs in interoperability. A migration profile therefore has to require the facts those answers rest on.

For Keycloak the operator is typically an enterprise running it as the single sign-on service for its applications. Every relying party trusts the tokens Keycloak signs. Keycloak's migration therefore sets the timetable for many other systems as well as its own.

## The black-box constraint

The defining constraint is that the consumer cannot see inside the product, and the vendor will not expose its internals. Everything the profile asks for therefore has to be declarable at the boundary: observable at an interface, or stated by the vendor as a property of the product it ships. Anything requiring disclosure of source, design or internal architecture is out of scope, and would not be supplied in any case.

{{< figure src="../assets/figures/use-cases-pqc-migration-1.svg" alt="A dark box labelled Keycloak 26.7.3, container image, internals not disclosed. On its left edge, six inbound interfaces: TLS on the main listener, OIDC token issuance, SAML assertions and plain HTTP, all of type service, and the Admin API and TLS on the management port, of type management. On its right edge, five outbound interconnect interfaces: TLS to the database, the directory, external identity providers and the mail server, and brokered token verification. On its bottom edge, the cluster transport of type peer and the realm key store of type storage." >}}

*The profile asks for information one interface at a time. An operator of Keycloak plans against the thirteen interfaces the product presents, because that is all it can verify and all the supplier will state. Each interface declares what it can negotiate, how that is enabled, and what it costs to change.*

The profile is also built around interfaces rather than around the product as a whole. A single answer at product level, such as "this product supports ML-KEM", does not tell the operator what to do. A product may support a post-quantum key exchange on its service interface and not on its management interface, and the operator has to migrate both. Migration is planned and executed one interface at a time.

## The worked product: Keycloak 26.7.3

Keycloak is a useful subject because its most important cryptography is not TLS. It is the signature on every token it issues, which every relying party verifies. That signature migrates on a different timetable from the TLS underneath it, and depends on a different standard. A migration profile must be able to tell the token signature and the TLS apart. A profile that could not would fail on products like this one.

Three more properties make it instructive. Its TLS key exchange comes from the Java runtime rather than from Keycloak, so what blocks post-quantum key exchange lies with the runtime's cryptographic provider, not with Keycloak. It generates the key for its own cluster transport, so the product, not the operator, fixes that key's type. And it stores its realm keys in its database without wrapping (encrypting) them, so the key storage has to be treated as an interface too.

The subject is the container image, `quay.io/keycloak/keycloak:26.7.3`, at its defaults. The image fixes the Java runtime, and with it the TLS capability. The ZIP distribution runs on whatever runtime the operator installs, so its TLS capability is a fact about a deployment and belongs in a separate document.

{{< figure src="../assets/figures/use-cases-pqc-migration-2.svg" alt="Keycloak interfaces by layer. OIDC token issuance, SAML assertions and the Admin API ride on HTTPS on port 8443, which rides on the TLS interface tls-https. Health and metrics ride on HTTPS on port 9000 over the TLS interface tls-mgmt. Brokered token verification rides on outbound HTTPS over the TLS interface int-broker. Plain HTTP on port 8080 rides on nothing." >}}

*An interface is a logical cryptographic boundary, not a port. Signed tokens and the TLS that carries them are two interfaces, because they migrate on different timetables. A service counts as an interface when it applies cryptography of its own or has no transport protection. A service that only rides on TLS does not count.*

This gives thirteen interfaces. The seven TLS interfaces all use the Java runtime's cryptographic providers. The four application-layer interfaces are implemented by Keycloak itself.

| Interface | Type | Protocol | What it protects |
| --- | --- | --- | --- |
| `tls-https` | service | TLS 1.2, 1.3 | The main listener, carrying OIDC, SAML and the Admin API. Certificate supplied by the operator |
| `svc-oidc` | service | OIDC 1.0 | ID and access tokens, signed RS256 with the realm key. Encryption off by default |
| `svc-saml` | service | SAML 2.0 | Assertions, signed RSA-SHA256 with the realm key |
| `svc-http` | service | HTTP | Nothing. Off by default in production mode. Often used behind a TLS-terminating proxy |
| `mgmt-admin` | management | Admin REST | Administration by bearer token. Also the surface that generates and imports realm keys |
| `tls-mgmt` | management | TLS 1.2, 1.3 | Health and metrics on port 9000. Inherits the main listener's TLS settings by default |
| `int-db`, `int-ldap`, `int-broker`, `int-smtp` | interconnect | TLS 1.2, 1.3 | Outbound connections to the database, the directory, external identity providers and the mail server |
| `svc-broker-tokens` | interconnect | OIDC 1.0 | Verification of tokens issued by external identity providers |
| `int-cache` | peer | TLS 1.3, mutual | Cluster transport. RSA-2048 certificate generated by Keycloak, stored in the database, rotated every 30 days |
| `sto-realm-keys` | storage | — | Realm keys and the cluster key, held in the database without wrapping |

## From questions to attributes

Each planning question implies particular facts. Working from the question to the attribute keeps a profile focused on its purpose. Working from the fields a format happens to offer does not. The third column gives the depth, meaning which of the two profiles asks for the fact: the baseline profile or the more demanding extended profile. It also gives the Keycloak case that shows why the fact matters.

| What the consumer needs to know | Attribute that supplies it | Depth, and the Keycloak case |
| --- | --- | --- |
| Which interface are we talking about, and does it matter? | `interfaceType` | Baseline. The token interface and the TLS interface that carries it are separate entries |
| What protocol, and which versions can it speak? | `protocol`, `protocolVersionsSupported` | Baseline. The cluster transport speaks TLS 1.3 only |
| What is it doing now? | `keyExchange`, `authentication` | Baseline. X25519 on TLS; RS256 on tokens; `none` for token encryption |
| What else could it do without changing the product? | `keyExchangeSupported`, `authenticationSupported` | Baseline. The JDK 21 groups, none of them post-quantum |
| How do we switch it on? | `enablementMethod`, `minimumProductVersion` | Baseline. `not-available` on every Keycloak interface today |
| Is this a software change or a hardware one? | `providerLocation`, `implementationPurl` | Baseline. Software throughout; the JDK or Keycloak itself |
| Can the module we are obliged to use do it? | `moduleValidationScheme`, `moduleValidationRef`, `validatedModeAvailability` | Baseline, new in v0.7. Keycloak's validated mode is an opt-in Bouncy Castle FIPS module |
| Are stored keys exposed as well as traffic? | `keyWrapping`, `keyWrappingSupported` | Baseline, new in v0.7. Realm keys are stored unwrapped |
| Can we migrate while the far end is still classical? | `coexistence`, `negotiationControl` | Baseline. Several realm keys can be active at once |
| What is likely to break? | `integrationConstraints` | Baseline. ML-DSA-signed tokens exceed the 4 KB browser cookie limit |
| If it cannot do this yet, what is stopping it, and who can change that? | `capabilityStatus`, `blockedBy`, `roadmapRef`, per purpose | Baseline. Four different blockers across thirteen interfaces |
| Can the product create and hold the new key? | `keyManagementFunction`, `keyOperations`, `keyTypesSupported`, `keyTypes`, `keyStoreLocation` | Extended. The Admin API cannot generate an ML-DSA key |
| Which surface manages this interface's key? | `keyStoreRef` | Extended. Tokens: the Admin API. TLS: files, out of band. Cluster: the product itself |
| What else has to move first? | `externalDependencies` | Extended. The certificate authority, the directory, external identity providers |
| Where is data stored, and is that declared? | storage interfaces, or a stated absence | Extended. The key store in the database |
| How much should we trust this record? | `lifecycleStage` | Baseline. `implemented` where Keycloak fixes the value, `configured` where it depends on the operator's certificate |

## Two profiles, two depths

Keywords follow BCP 14. Both profiles are product-independent: no rule names a product, a vendor or an interface instance. Attribute names follow the conventions in [Method](../../methodology/method/): `keyExchange` and `authentication` denote what the interface uses now, and the `Supported` suffix denotes what it is able to use.

The questions split into two groups. The first is about the interface: what it does, what it could do, and what stands in the way. The second is about what surrounds the interface and has to move with it or before it: the surface that must create the new key, the store that must hold it, and the services it depends on. A supplier can usually answer the first group today. Many suppliers cannot yet answer the second. Putting both groups in one profile would set the minimum requirement so high that few suppliers could meet it. The use case is therefore served by a family of two profiles, ordered by depth: the extended profile asks for everything the baseline asks for, plus the second group of questions ([decision 0019](https://github.com/pkic/cbom/blob/main/decisions/0019-a-family-ordered-by-depth.md)).

| Profile | Extends | Adds |
| --- | --- | --- |
| **Baseline** `pkic.example.pqc-migration` v0.7 | Interface disclosure baseline v0.8 | Capability, enablement and blockers per interface and per purpose; module validation; key wrapping on storage. Makes one inherited rule stricter. |
| **Extended** `pkic.example.pqc-migration-extended` v0.1 | The baseline above | Key management surfaces, key-store references, external dependencies, the obligation to declare storage, product certification. Tightens validated-mode availability to MUST. |

Both profiles serve the same consumer and the same decision. The extended profile therefore goes deeper into the same use case. It is not a branch serving a different purpose. Extension is monotonic: a CBOM conforming to the extended profile also conforms to the baseline, and to the interface profiles beneath it. Rule ids are local to the profile that declares them and are cited with that profile's tag as a prefix, so `pqc-migration#I1` and `interface-disclosure#I1` are different rules. See [Profile](../../methodology/profile/) for the scheme.

### Baseline: product-level rules

| # | Requirement | Level | Note |
| --- | --- | --- | --- |
| `interface-disclosure#P1` | Declare at least one cryptographic interface | MUST | Inherited. |
| `interface-disclosure#P2` | Declare at least one interface of type `management`, or state why there is none | MUST | Inherited. Keycloak's is the Admin API. |
| `interface-disclosure#P3` | Identify the subject the document describes | MUST | Inherited. For Keycloak, the Package URL of the container image. |
| `interface-disclosure#P4` | State the completeness of the interface set | MUST | Inherited. `all-external`, `all` or `partial`. If a partial list looks complete, the plan built from it has gaps that nobody notices. |
| `pqc-migration#P1` | Identify the cryptographic providers the product uses | SHOULD | Lets a consumer reason about update paths shared across interfaces: the JDK serves all seven of Keycloak's TLS interfaces. |

### Baseline: per-interface rules added here

These rules apply to every declared interface, alongside the inherited `interface-disclosure#I1` to `#I10`. A storage interface describes data at rest, not a communication channel. The channel rules (protocol, version, key exchange, authentication, endpoint roles) therefore do not apply to it, and `keyWrapping` takes the place of key exchange.

| # | Attribute | Level | Values and purpose |
| --- | --- | --- | --- |
| `I1` | `protocolVersionsSupported` | MUST | All versions the interface can negotiate. Post-quantum key exchange is unavailable on older versions of some protocols. Not on storage. |
| `I2` | `keyExchangeSupported` | MUST | The full set the interface can negotiate, including hybrid constructions. Not on storage. |
| `I3` | `authenticationSupported` | MUST | Authentication migrates separately from key exchange and usually later. Not on storage. |
| `I4` | `enablementMethod` | MUST | `already-enabled` · `configuration` · `software-update` · `hardware-change` · `licence` · `not-available`. Separates the cheap changes from the expensive ones. |
| `I5` | `minimumProductVersion` | conditional MUST | Where `enablementMethod` is `software-update`. |
| `I6` | `providerLocation` | MUST | `software` · `hsm` · `tee` · `unspecified`. |
| `I7` | `coexistence` | MUST | `simultaneous` · `exclusive` · `unknown`. An exclusive interface forces a coordinated cutover with every counterparty. |
| `I8` | `negotiationControl` | SHOULD | Whether post-quantum can be required and a classical fallback refused. |
| `I9` | `integrationConstraints` | SHOULD | Known effects of enabling the capability: size limits, intermediaries, performance. |
| `I10` | `moduleValidationScheme` | MUST | `fips-140-2` · `fips-140-3` · `iso-19790` · `national-crypto-approval` · `none`. The validation of the module implementing the interface. This is the fact that a `certification` blocker (`G1.2`) rests on. New in v0.7. |
| `I11` | `moduleValidationRef` | conditional MUST | The certificate reference, where a scheme other than `none` is declared. New in v0.7. |
| `I12` | `keyWrappingSupported` | conditional MUST | On a storage interface: the wrapping algorithms the storage path can use, or `none`. New in v0.7. |
| `G1.1` | `capabilityStatus` | MUST | Per cryptographic purpose. `available` · `committed` · `planned` · `under-evaluation` · `not-planned`. Each value states a level of commitment, not a date. |
| `G1.2` | `blockedBy` | conditional MUST | Where the purpose's status is not `available`. `provider` · `product` · `hardware` · `standard` · `certification`. |
| `G1.3` | `roadmapRef` | MAY | Reference to a roadmap entry carrying the target release. Interfaces sharing a blocker reference the same entry. |
| `G1.4` | `validatedModeAvailability` | SHOULD | Where the purpose's capability is available: `in-validated-mode` · `outside-validated-mode-only` · `no-validated-mode`. In regulated settings, a capability commonly ships before the module implementing it is validated. New in v0.7. |

### Extended: rules added at the second depth

| # | Attribute or rule | Level | Applies to, and purpose |
| --- | --- | --- | --- |
| `P1` | Declare at least one storage interface, or state why there is none | MUST | Stored ciphertext is exposed by a shorter route than captured traffic, and a backup path is the interface most easily left out. |
| `P2` | `productCertificationScheme` | SHOULD | Common Criteria, EUCC or a national scheme. Kept apart from module validation because it certifies a different object: enabling a new algorithm can take a product outside its evaluated configuration. |
| `I1` | `keyManagementFunction` | MUST | Management interfaces: whether they manage keys at all. Keycloak's health port does not. |
| `I2` | `keyOperations` | MUST | Surfaces that manage keys: generate, import, export, request-certificate, rotate and so on. |
| `I3` | `keyTypesSupported` | MUST | The key types the surface can generate or import. This rule catches an interface that can use a new algorithm when the product cannot create the key for it. |
| `I4` | `keyTypes` | MUST | The key types held now: the population the migration has to replace. |
| `I5`, `I6` | `keyStoreFormatsSupported`, `keyStoreFormats` | SHOULD | Container formats, where a format cannot carry a new key type. |
| `I7` | `keyStoreLocation` | MUST | Software, HSM, TEE, TPM, OS keyring or external vault: whether the new key type waits on hardware. |
| `I8` | `keyStoreRef` | SHOULD | Every other interface: the management interface that manages its keys, or `out-of-band`, `product-managed` or `none`. |
| `I9` | `externalDependencies` | MUST | Services the interface's cryptography depends on at run time: certificate authority, revocation responder, directory, identity provider, HSM, key vault, time source, or `none`. These are what the operator must migrate first. |
| `I10` | `enablementSetting` | SHOULD | Where enablement is by configuration: the setting that enables it. |
| `pqc-migration#G1.4` | `validatedModeAvailability` | MUST | Tightened from SHOULD. At the extended depth the consumer is deciding the order of actual changes, so it needs this fact. |

### The one inherited rule the baseline makes stricter

| Inherited rule | Baseline | Here |
| --- | --- | --- |
| I9 `implementationPurl` | MUST, may be withheld | MUST, may not be withheld |

Migration planning depends on knowing which library implements an interface, since that determines whether an update exists and when it arrived. If a vendor withholds it, the consumer cannot plan the order of the work. This is the only inherited rule the baseline profile changes. Raising the level is permitted because it makes the rule stricter.

### Conditional rules

Several rules apply only when another attribute has a particular value. A profile is not limited to a flat list of mandatory fields. A requirement can depend on the value of another attribute. `I5` obliges a producer claiming that a capability needs a software update to say which version provides it. `I11` asks for a certificate reference only where a validation scheme is declared, and `I12` asks for wrapping algorithms only on a storage interface. Inside the capability group, `G1.2` asks for a blocker only where a purpose is not available, and `G1.4` asks about validated mode only where it is. Making these rules unconditional would not help. Requiring a version or a certificate from every interface produces noise. Requiring none leaves the useful case unstated.

### Availability, and why it is not a date on an interface

An earlier draft of this profile put a `plannedAvailability` date on each interface. That is the obvious design, but it does not work, because of how interfaces gain capability.

Interfaces do not gain capability independently. A product with six TLS interfaces built on one cryptographic provider gains post-quantum key exchange on all six at the moment that provider is updated and the product integrates it. A date on each interface duplicates one underlying event six times, and the six copies drift apart as they are maintained. Availability is therefore a property of the change that delivers the capability, such as the provider update. The interfaces inherit it from that change.

What a planner needs first is therefore not the date but the obstacle, because the obstacle determines whether any date is credible and who is able to move it.

| `blockedBy` | What has to happen | Who can move it | Predictability |
| --- | --- | --- | --- |
| `provider` | A dependency is upgraded to a version offering the algorithm. | The vendor, by taking the upgrade. | Reasonable |
| `product` | The product's own code must change to expose or negotiate it. | The vendor, in a named release. | Reasonable |
| `hardware` | A module, firmware or platform must support the algorithm. | The vendor together with the module supplier. | Poor |
| `standard` | No specification yet defines the algorithm for this protocol. | Nobody, until the standards process concludes. | None |
| `certification` | A validated implementation is required, for example under a scheme such as FIPS. | An external laboratory or scheme. | Externally determined |

The most important distinction is the fourth row, `standard`. An interface blocked on a protocol standard cannot be given a credible date by any vendor, and a consumer who understands that stops waiting and considers compensating controls instead. Recording it as "planned, date to follow" alongside a case that really is scheduled for the next release mixes up two situations that call for opposite responses.

Keycloak shows four of the five on one product. TLS key exchange is blocked by the `provider`: hybrid ML-KEM groups ship in JDK 27 and are enabled there by default, with backports to earlier releases announced, so the timing depends on the Java runtime's releases, not Keycloak's. Token signing is blocked by a `standard`: an ML-DSA signature provider is committed upstream, but the JSON Web Key representation it needs is still an Internet-Draft. The cluster transport is blocked by the `product`, because Keycloak generates its RSA-2048 key itself. And whether the capability will be usable in validated mode is a `certification` question for the Bouncy Castle FIPS module.

Where a date or release is offered, the profile keeps it out of the interface and out of the CBOM. Target release and date sit in a roadmap entry that interfaces reference through `roadmapRef`, so that interfaces sharing a blocker point at one entry. There are two reasons. First, a CBOM revision is a fixed record of one point in time. A date that slips either goes stale inside a document that looks authoritative, or forces the CBOM to be republished when nothing about the product has changed. Second, roadmap data has a different owner and changes at a different pace from the rest of the document. This is the same argument that the [Governance](../../methodology/governance/) section makes for keeping artifacts with separate lifecycles apart.

A target release is also preferable to a calendar date. Releases are the vendor's own unit of change, and the statement "this lands in 9.x" survives slippage in a way that a date does not.

Three existing parts of the methodology already support this approach, so nothing new has to be added. Forward-looking capability is carried by `capabilityStatus`, `blockedBy` and `roadmapRef`, not by the lifecycle stage. This profile accepts only `implemented`, `configured` and `observed`, so an interface may not report its present state as `intended`. A migration plan cannot rest on cryptography that a producer has not yet implemented. The lifecycle stage says how the reported present state was obtained; the three attributes above say what is coming. A vendor that shares roadmap detail only under agreement records `roadmapRef` as `withheld`, meaning the information exists but is not disclosed. This is more informative than an empty field. And the freshness policy in [Versioning](../../methodology/versioning/) applies to the roadmap entry, so a consumer can tell a current commitment from one nobody has revisited.

## Keycloak under the baseline

The table compares two interfaces: the TLS listener and the token service it carries. Values marked *configured* depend on the certificate the operator installs. The example assumes RSA-2048.

| Attribute | `tls-https` | `svc-oidc` |
| --- | --- | --- |
| `interfaceType` | `service` | `service` |
| `protocol` / `protocolVersionsSupported` | `TLS` / `1.2`, `1.3` | `OIDC` / `1.0` |
| `keyExchange` | `X25519` | `none` (tokens are signed, not encrypted) |
| `keyExchangeSupported` | `x25519`, `secp256r1`, `secp384r1`, `secp521r1`, `x448`, `ffdhe2048` | `RSA-OAEP`, `RSA-OAEP-256`, `ECDH-ES` |
| `authentication` | `RSA-2048` (configured) | `RS256` |
| `authenticationSupported` | ECDSA, EdDSA and RSA signature schemes | RS, PS and ES families, `EdDSA`, HS |
| `implementationPurl` | the Red Hat build of OpenJDK 21 | `pkg:maven/org.keycloak/keycloak-services@26.7.3` |
| `enablementMethod` | `not-available` | `not-available` |
| `coexistence` | `simultaneous` | `simultaneous`: several realm keys can be active at once |
| `negotiationControl` | named groups set by the JVM property `jdk.tls.namedGroups` | signature algorithm set per realm and per client |
| `integrationConstraints` | certificate and key are operator-supplied files | ML-DSA-65 tokens exceed the 4 KB browser cookie limit; relying parties must accept a new key type |
| `moduleValidationScheme` | `none` in default mode | `none` in default mode |
| `lifecycleStage` | `configured` | `implemented` |

### Capability, per purpose

Capability is stated per cryptographic purpose, because the purposes of one interface migrate on different timetables. Across Keycloak the two purposes that matter most look like this.

| Interfaces | `key-establishment` | `entity-authentication` |
| --- | --- | --- |
| The six JDK TLS interfaces | `planned`, blocked by `provider`, roadmap: JEP 527 | `under-evaluation`, blocked by `standard` |
| `int-cache` | `planned`, blocked by `provider` | `under-evaluation`, blocked by `product`: the key type is fixed |
| `svc-oidc`, `mgmt-admin` | `under-evaluation`, blocked by `standard` | `committed`, blocked by `standard`, roadmap: Keycloak issue 43690 |
| `svc-saml` | `under-evaluation`, blocked by `standard` | `under-evaluation`, blocked by `standard` |
| `svc-http`, `sto-realm-keys` | `not-planned`, blocked by `product` | `not-planned`, blocked by `product` |

The other five purposes carry a status as well. On the TLS interfaces, encryption, data integrity and key derivation are `available`, and each says whether it works in validated mode. Key protection is `not-planned` everywhere. This repeats the storage finding: nothing wraps Keycloak's keys at rest. A deferred purpose owes only a status and, where it is not available, a blocker. That costs a producer almost nothing, and it keeps a shallower depth from becoming a permanent floor.

Most of these values are the same across interfaces because they are properties of the library that implements the interfaces. The document states them once, on that library, and an interface states only what differs. The cluster transport inherits the JDK's entries and overrides entity authentication. SAML inherits the Keycloak library's entries and overrides two purposes. Rules are evaluated on the values that result after inheritance and overrides.

A purpose is different from an operation. The purpose vocabulary is useful because it records that difference. CycloneDX already records operations: a certificate signature carries `cryptoFunctions: ["sign", "verify"]`, and so would a firmware signature on the same product. The certificate signature serves entity authentication and migrates when the PKI does. The firmware signature must still verify years after it was written. The operation is the same, but the migration timescale and the work are different. See [Terms](../../methodology/terms/) for the four-part test an entry has to pass, and [decision 0010](https://github.com/pkic/cbom/blob/main/decisions/0010-cryptographic-purpose-vocabulary.md) for the reasoning.

### What a planner concludes

Without seeing inside the product, an operator reading the baseline document can conclude the following. No Keycloak interface can be made quantum-safe by configuration today. TLS key exchange arrives with the Java runtime, so the action is to track the runtime in the image and to test hybrid groups against the directory, the database and the mail server, which must support them too. Token signing will take the longest. It waits on a standard, so pressing the supplier for a date will achieve little. The time is better spent finding relying parties that reject unknown key types and flows that keep tokens in cookies. The cluster transport depends on a change in the product. Plain HTTP behind a proxy carries tokens in clear on the internal hop and should be closed first, because no post-quantum work protects traffic that is not encrypted at all. An inventory of the algorithms in use today yields none of these conclusions.

## Keycloak under the extended profile

The baseline says what each interface could do. The extended profile asks whether the product around it can support the change. For Keycloak the answer is concentrated in one place: the Admin API, which generates and holds the realm keys every token interface signs with.

| Attribute | Keycloak |
| --- | --- |
| `keyManagementFunction` on `mgmt-admin` | `keys-and-certificates` |
| `keyOperations` | `generate`, `import`, `export` (public keys and certificates only), `rotate`, `delete` |
| `keyTypesSupported` | RSA-2048 and 4096, ECDSA P-256 to P-521, Ed25519, Ed448, HMAC, AES. No ML-DSA. |
| `keyTypes` | RSA-2048, HMAC-SHA512, AES-128: the defaults of a new realm |
| `keyStoreLocation` | `software` |
| `keyManagementFunction` on `tls-mgmt` | `none` |
| `keyStoreRef` | `svc-oidc`, `svc-saml`: the Admin API. `tls-https` and the outbound TLS: `out-of-band`, because the keys arrive as files. `int-cache`: `product-managed`. |
| `externalDependencies` | `tls-https`: `certificate-authority`. `int-ldap`: `directory`. `int-broker` and `svc-broker-tokens`: `identity-provider`. Token services: `none`. |
| Storage | `sto-realm-keys` declared, with `keyWrapping` `none` |
| `productCertificationScheme` | `none` for the upstream project (to be verified) |

The extended document adds three conclusions to the baseline's. When ML-DSA signing lands, the key management surface must be able to generate the key as well, and today it cannot. Every baseline rule passes, and yet the operator could not migrate. `pqc-migration-extended#I3` exists to catch this case. TLS migration cannot start until the operator's certificate authority can issue the new certificates, and the directory and identity providers have to follow. And the realm keys that sign every token sit unwrapped in the database, so a database backup is as sensitive as the signing service itself.

## What the profiles deliberately exclude

The profile deliberately leaves out three kinds of information.

It carries no readiness or posture verdict. Whether a declared algorithm set counts as quantum-safe is a judgement against criteria still under revision, so an external policy computes it from these facts at the time of asking and dates the result. [Policy Evaluation](../../methodology/policy-evaluation/) sets out the reasoning, which is also why `pqcPosture` was dropped from the baseline profile.

Maturity scores are excluded on the same grounds. Collapsing different attributes into one number has a further drawback. It tends to hide whichever attribute is actually blocking the migration.

Internal implementation is out of scope, so no source references, design detail or component structure are requested. This exclusion follows directly from the black-box constraint. It is not a compromise made to accommodate vendors. A vendor asked to expose internals will decline, and a profile nobody satisfies achieves nothing.

The profile also omits an `encryptionSupported` attribute. The `encryption` attribute from the interface disclosure baseline is inherited and still required, so an interface states the bulk algorithm it uses. What this profile does not add is an `encryptionSupported` counterpart. Symmetric encryption at adequate key lengths is not the pressing concern in a post-quantum migration, and the interfaces needing work are identified by their key exchange and authentication. A profile combining migration with a broader agility objective would add it.

The extended profile leaves out four more things. Cipher suite lists repeat what the separate key exchange, authentication and encryption attributes already state, and they cannot carry TLS 1.3 key exchange. Port numbers are deployment facts. Secret hygiene, such as how a database password is supplied, is not a migration fact. And individual keys are not identified, because how a key is identified across tools is still open (Q39): the profile describes the stores and what they can hold.

## Expressing it in a CBOM

The attributes do not depend on any format. The full CycloneDX 1.7 mapping is in [Formats](../../methodology/formats/).

-   **Security protocols are protocol components.** Each TLS interface is a `cryptographic-asset` with `assetType: protocol`. A TLS configuration shared by several interfaces is one further component, referenced from each.
-   **Application protocols are services.** OIDC, SAML, the Admin API and plain HTTP are CycloneDX `services`, and so is HTTPS. The dependency graph records what carries what: OIDC depends on HTTPS, HTTPS on the TLS component, and plain HTTP on nothing. A service is counted as an interface only when it carries `interfaceType`.
-   **Native CycloneDX fields are used first.** The implementing library is linked with `dependencies[].provides`. Supported TLS groups and signature schemes are in `cipherSuites`, which lists what is supported, while `cryptoRefArray` lists what is in use. Keys are `related-crypto-material` components, with `securedBy` stating how they are wrapped. Completeness is a `composition`.
-   **Implementation facts are stated once,** on the library that provides the interfaces, and inherited.
-   **Everything else is a property** under the `pkic:profile:` namespace: interface type, endpoint roles, the capability group and the key-management attributes, none of which CycloneDX models.
-   **Related documents are linked, not copied.** The CBOM references its companion SBOM and the supplier's security advisories.

The token interface, in outline:

```
"services": [{
  "bom-ref": "service:svc-oidc",
  "name": "OIDC and OAuth 2.0 token issuance (JOSE)",
  "endpoints": ["https://{hostname}/realms/{realm}/protocol/openid-connect"],
  "properties": [
    { "name": "pkic:profile:interfaceType", "value": "service" },
    { "name": "pkic:profile:protocol",      "value": "OIDC" },
    { "name": "pkic:profile:keyExchange",   "value": "none" }
  ]
}],
"dependencies": [
  { "ref": "service:svc-oidc",
    "dependsOn": ["service:https-main", "crypto:algo:rs256", "crypto:key:realm-rsa"] },
  { "ref": "service:https-main", "dependsOn": ["crypto:protocol:tls-https"] },
  { "ref": "lib:keycloak-services", "provides": ["service:svc-oidc", "service:svc-saml",
                                                  "service:mgmt-admin", "service:svc-broker-tokens"] }
]
```

Where an attribute is unavailable, the four disclosure outcomes apply. `none` is a value, not a marker: it states that no algorithm is applied for that job, as with Keycloak's unencrypted tokens. A supplier that does not know whether an interface can coexist records `coexistence` as `unknown` instead of guessing, because a wrong answer produces a plan that fails at cutover.

## The example documents

Four CycloneDX documents make the use case testable. Each non-conforming document differs from its conforming partner in one attribute, so it fails exactly one rule.

| Document | Verdict |
| --- | --- |
| `cbom-keycloak-pqc-pass` | Conforms to the baseline, and to the interface profiles beneath it |
| `cbom-keycloak-pqc-fail` | Fails `pqc-migration#I12`: the storage interface omits `keyWrappingSupported` |
| `cbom-keycloak-pqc-extended-pass` | Conforms to the extended profile and every shallower depth |
| `cbom-keycloak-pqc-extended-fail` | Fails `pqc-migration-extended#I3`: the Admin API omits `keyTypesSupported` |

The documents, the rules files and the decision record are in review with draft decision 0022. They are published on [Files](../../methodology/files/) once the reference validator can read services, native fields and inheritance. Until then, the published validator reports every new attribute as absent.

## Recorded decisions

Several choices in these profiles were made against the more obvious alternative. Each is written up as a decision record in the repository, with the options considered, the rationale and what reversing it would involve. The records are authoritative. The summaries below are only for orientation.

| Record | Decision | Aspect |
| --- | --- | --- |
| [0002](https://github.com/pkic/cbom/blob/main/decisions/0002-facts-in-cbom-judgements-in-policy.md) | Capability is stated as facts. The profile requires the algorithm sets an interface supports and does not ask whether they amount to being quantum-safe. That judgement is made by an external policy at the time of asking, for the reasons given in [Policy Evaluation](../../methodology/policy-evaluation/). | 3.3 |
| [0007](https://github.com/pkic/cbom/blob/main/decisions/0007-availability-as-status-and-blocker.md) | Availability is expressed as a status and a blocker. Dates and target releases sit in a referenced roadmap entry, away from the interface. | 3.10 |
| [0010](https://github.com/pkic/cbom/blob/main/decisions/0010-cryptographic-purpose-vocabulary.md) | **Capability is stated per cryptographic purpose.** One status per interface cannot express the ordinary position: key agreement done, identity proof not yet. | 3.7 |
| [0019](https://github.com/pkic/cbom/blob/main/decisions/0019-a-family-ordered-by-depth.md) | **Adoption is staged by a family of profiles ordered by depth.** The baseline and extended profiles are two depths of one family. | 3.9 |
| 0022 (draft) | **The two depths, and how they meet a real product.** Module validation and storage in the baseline; key management and dependencies in the extended profile; an interface is a logical boundary; application protocols are CycloneDX services; native fields first; implementation facts inherited from the providing library. | 3.9 |

The rules above also depend on decisions taken elsewhere in the methodology: [0004](https://github.com/pkic/cbom/blob/main/decisions/0004-monotonic-profile-extension.md) for what this profile is permitted to change in the baseline it extends, and [0005](https://github.com/pkic/cbom/blob/main/decisions/0005-attribute-naming-conventions.md) for the `Supported` suffix. The full index is in [decisions/](https://github.com/pkic/cbom/tree/main/decisions).

## Open questions for the working group

These are also carried in the [open questions register](https://github.com/pkic/cbom/blob/main/open-questions.md), which collects the unresolved items from every section and maps each to the methodology aspect that tracks it.

-   Whether raising `implementationPurl` to a non-withholdable MUST is acceptable to vendors. It is the one place where the baseline makes a rule of the interface profile it extends stricter.
-   Whether `enablementMethod` should be a single value or a set, since some capabilities need both an update and a configuration change.
-   Whether `integrationConstraints` can be structured usefully or should remain prose.
-   Whether an interface should be defined as a logical boundary rather than a port. Keycloak needs it, because its token signatures and its TLS migrate separately, but it means one port can carry several interfaces.
-   Whether implementation facts stated on a library and inherited by interfaces make a document harder to read than they make it shorter. Keycloak's document halves in size, but a reader has to resolve the inheritance to see an interface's full answer.
-   Whether a CBOM should carry forward-looking data at all (Q26). This one is a substantive disagreement, not a detail to be tidied up. A procurement profile has a defensible claim on it. A runtime assurance profile arguably has none. Stating capability on library components as well as interfaces widens where the question applies.
-   How the family relates to a sector baseline. A telecommunications or finance profile would most likely add required interface types and constrain the acceptable algorithm sets, leaving the attribute list intact.

The pattern to take from this section: name the consumer and the decision, derive the questions that decision raises, and turn each question into an attribute that can be declared at the boundary. The list of attributes is the output of that analysis. Beginning instead from the fields a format happens to offer produces a profile with no stated purpose, and no way to argue about whether it asks for the right things.

[← Change Planning](../change-planning/) [Next: IoT Device Estate →](../iot/)
