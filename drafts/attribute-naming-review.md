# Attribute naming review

Status: draft for discussion, 27 November 2026. The cost of each change is deliberately left out of the assessment.

Scope: every attribute in the published example profiles under `docs/methodology/`, every attribute in the draft profiles under `drafts/`, and the reference contexts. The definitions are taken from `terms.html`. The usage is taken from the example records.

## How the names were judged

Each name was tested against five questions.

1. **Does the name say what is described?** A reader who sees the name alone should be able to guess what kind of answer it expects.
2. **Does the name match the definition and the usage?** Where the glossary and the example records disagree, the name has failed.
3. **Is the name free of a carrier or a standard?** The methodology is format-independent, so a name should not build in a format such as purl, or one standard's numbering.
4. **Does the name follow the same pattern as its neighbours?** Pairs, pointers and absence statements should be built the same way everywhere.
5. **Can the name be confused with another term in the field?** "Hybrid", "provider" and "service" already carry meanings that readers bring with them.

Most names pass. The ones that fail fall into three groups. Some say something different from what the attribute means. Some say too little. Some break a pattern that the rest of the set follows.

## Summary

| Priority | Attribute | Recommended name | Main reason |
|---|---|---|---|
| 1 | `negotiationControl` | `algorithmSelection`, plus a new `classicalFallback` | The definition and every example answer different questions |
| 1 | `coexistence` | `transitionMode` | Does not say what coexists; confused with hybrid |
| 1 | `providerLocation` | `executionEnvironment` | "Provider" has three other meanings in the profiles; CycloneDX already uses `executionEnvironment` |
| 1 | `implementationPurl` | `implementingLibrary` | Names a carrier format in a format-independent methodology |
| 1 | `cryptoTerminationPoint` (IoT) | fold into `terminatedBy` | Two names for one concept |
| 2 | `externalDependencies` | `trustServiceDependencies` | Reads as software dependencies |
| 2 | `minimumProductVersion` | `availableFromVersion` | Reads as a requirement on the deployment |
| 2 | `certificationScheme` | `impactedCertification` | Reads as the product's certification |
| 2 | `intrinsicData` | `inherentContent` | The word "intrinsic" does not tell a reader what to answer |
| 2 | `usage` (system) | `designUse` | Too generic to search for or recognise |
| 2 | `keyManagementFunction` | `managesKeys` | A yes/no question dressed as a vocabulary |
| 2 | `resourceBound` (IoT) | `resourceLimits` | Plainer English |
| 2 | `claimedLevel62443` (OT draft) | `claimedSecurityLevel` | Builds one standard's number into the name |
| 2 | `regenerationTrigger` | `recordRefreshTrigger` | Does not say that the record is what is regenerated |
| 2 | `referenceSpecification` (telecom draft) | `governingSpecification` | "Reference" collides with "reference point" |
| 2 | `boundary` (telecom draft) | `operatorBoundary` | Too generic |
| 3 | Pointer attributes | one pattern (see below) | Four different patterns for the same kind of value |
| 3 | `...Ref` suffix | one meaning (see below) | Used for local pointers, URLs and certificate numbers |
| 3 | Absence statements | one pattern (see below) | `...Absence` and `contextAbsent:` side by side |
| 3 | `keyBlockFormat` / `keyBlockFormats` (HSM drafts) | `keyBlockFormats` | Singular in one draft, plural in the other |
| 3 | `encryption` | add `encryptionSupported` | The only one of the three core attributes without a "supported" partner |
| 3 | Context `design-intent` | `threat-model` | Says what the document actually is |
| 3 | Context `issuer-policy` | `certificate-policy` | The established term |

Priority 1 means the name misleads a careful reader today, so different suppliers will answer differently. Priority 2 means the name is weaker than it could be, but a reader who checks the definition will answer correctly. Priority 3 means the names are individually acceptable but inconsistent as a set.

## Priority 1: names that mislead

### `negotiationControl`

The glossary says: "Whether the interface can be configured to require post-quantum key exchange and refuse a classical fallback." That is a capability question with a yes or no answer.

Every example record answers a different question: where the algorithms are set. Keycloak's records say "JVM named groups". OpenSSH's record says "KexAlgorithms, Ciphers, MACs and HostKeyAlgorithms in sshd_config". ExampleGate's record says "IKE proposals in the gateway configuration". Those answers are useful, but none of them says whether a classical fallback can be refused.

Both questions are worth asking, so the attribute should become two:

- **`algorithmSelection`** (free text): where and how an operator chooses the algorithms the interface offers. This is what the examples already record.
- **`classicalFallback`** (vocabulary: `can-refuse`, `cannot-refuse`, `unknown`): whether the interface can be set to refuse a peer that offers only classical algorithms. This is what the glossary describes, and it is the fact that matters for harvest-now-decrypt-later exposure. An interface that cannot refuse a classical fallback leaves every connection open to a downgrade.

The word "negotiation" also fits only protocols that negotiate. A firmware verification interface or a key store has no negotiation, which is why so many example interfaces answer "Not applicable".

### `coexistence`

The attribute asks whether switching an interface to post-quantum cryptography forces every counterpart to switch at the same moment. The name does not say what coexists. A supplier can read it as "does the product contain both kinds of algorithm?", and almost every product does. The name also invites confusion with hybrid key exchange, which is often described as classical and post-quantum cryptography "coexisting" in one handshake. The value `exclusive` contradicts the attribute name it answers.

Recommended: **`transitionMode`**, with the values `side-by-side`, `switch-over` and `unknown`. The definition should say explicitly that an interface that offers only a hybrid algorithm, with no classical fallback, is `switch-over`. The name also works for storage interfaces, where the question is whether a key store can hold classical and post-quantum keys at the same time.

The second choice is `cutover`, with the values `gradual`, `coordinated` and `unknown`.

### `providerLocation`

The attribute records where key operations run: in software, in an HSM, in a TEE, in a secure element. The word "provider" already appears in three other places in the profiles, each with a different meaning:

- `blockedBy: provider`, meaning the cryptographic library;
- `keyCustody: provider-managed`, meaning the cloud service operator;
- `keyProvider` in the system profile, meaning any system component that supplies keys.

A reader who meets `providerLocation` cannot tell which of these it refers to.

Recommended: **`executionEnvironment`**. CycloneDX already uses this name for the same concept in its algorithm properties, and the validator already reads that field as a source for this attribute. The two vocabularies differ, so the mapping in `mapping-cyclonedx-spdx.md` still has to translate values. The shared name removes a translation step for every reader who knows CycloneDX.

The vocabulary should also be reconciled with `keyStoreLocation`. The two lists overlap (`software`, `hsm`, `tee`), but each has values the other lacks (`secure-element`, `mcu-internal` and `otp-fuses` in one; `tpm`, `os-keyring` and `external-vault` in the other). A TPM can run key operations, and a secure element can store keys, so both attributes should draw on one vocabulary.

### `implementationPurl`

The attribute identifies the library that implements the interface's cryptography. The name builds in one identifier format, the Package URL. The baseline profile already separates concept from encoding: its `identifierSchemes` block states that a library is identified by purl. The attribute name repeats that decision and would be wrong for any carrier or community that identifies libraries another way, for example by CPE or by an SWID tag.

Recommended: **`implementingLibrary`**. The scheme stays in `identifierSchemes`, where it already is.

### `cryptoTerminationPoint` (IoT device profile)

This attribute asks whether a device's cryptography ends at the device or at a gateway. The baseline's `terminatedBy` asks the same question for every interface: what terminates the cryptography, the workload or the platform. Having two names for one concept means a consumer joining an IoT record with a deployment record cannot match them.

Recommended: **remove `cryptoTerminationPoint` and extend `terminatedBy`**. The IoT profile would add `device` and `gateway` to the literals that `terminatedBy` accepts. "Either" becomes a list with both values.

## Priority 2: names that say too little

| Attribute | Recommended | Reasoning |
|---|---|---|
| `externalDependencies` | `trustServiceDependencies` | The vocabulary lists certificate authorities, revocation responders, directories, identity providers, HSMs, key vaults, time sources and random bit generators. Those are services the interface relies on for keys, trust and time. "External dependencies" is what an SBOM lists, so readers will expect software. A random bit generator is not strictly a trust service; `cryptographicDependencies` is the alternative if that matters more than plainness. |
| `minimumProductVersion` | `availableFromVersion` | It records the first release in which a capability is available. "Minimum" reads as a requirement the deployment must meet, which reverses the direction of the fact. |
| `certificationScheme` | `impactedCertification` | It names the certification that a change would affect (`certificationImpact`). On its own it reads as the product's certification, which is `productCertificationScheme`. The pair `certificationImpact` and `impactedCertification` makes the link explicit. |
| `intrinsicData` | `inherentContent` | It records what an interface carries by its nature, whatever the deployment: credentials, keys, tokens or configuration. "Intrinsic data" is accurate but does not prompt the right answer. `inherentContent` is still not ideal; a clear definition matters more here than the name. |
| `usage` (system profile) | `designUse` | It says whether a system design uses, disables or leaves unconnected a component's interface. "Usage" is generic, collides with ordinary prose ("the usage of TLS"), and is hard to search for. |
| `keyManagementFunction` | `managesKeys` | The vocabulary has two values, `keys-and-certificates` and `none`, so the question is yes or no. The name and the first value suggest a richer classification that does not exist. If more functions are planned, the current name is right and the vocabulary should grow. |
| `resourceBound` (IoT) | `resourceLimits` | Plainer, and it matches the definition's own wording ("the hard limits"). |
| `claimedLevel62443` (OT draft) | `claimedSecurityLevel` | The scheme belongs in the value or in a companion attribute, not in the name. A record for a device certified under a different scheme should not need a new attribute. |
| `regenerationTrigger` | `recordRefreshTrigger` | It says what causes the service provider to issue a new record. The current name does not say what is regenerated. |
| `referenceSpecification` (telecom draft) | `governingSpecification` | It names the 3GPP or O-RAN specification that defines a reference point. "Reference specification" sits next to `referencePoint` and reads as a specification of the reference point itself, which it is, but "governing" says why the specification matters. This one is close; keep the current name if the telecom group prefers its own terminology. |
| `boundary` (telecom draft) | `operatorBoundary` | The values are `intra-operator` and `inter-operator`. The name should say which boundary. |

## Priority 3: patterns across the set

### Capability and present state

The profiles mostly follow one pattern, and it is a good one. The bare name states what the interface uses (`keyExchange`, `keyTypes`, `keyCustody`). The same name with `Supported` states what the interface can do (`keyExchangeSupported`, `keyTypesSupported`, `keyCustodySupported`). The pattern should be written down as a naming rule, so that new profiles follow it. The current exceptions are:

- `encryption` has no `encryptionSupported` partner, while `keyExchange` and `authentication` do. A migration consumer cannot see which ciphers a product could switch to. This is a gap in the attribute set, not only a naming issue.
- `protocolVersion` (singular) pairs with `protocolVersionsSupported` (plural). This is acceptable because an interface uses one version at a time, but the rule should say so.
- The HSM drafts use `keyBlockFormat` in one profile and `keyBlockFormats` in the other. Use `keyBlockFormats` in both, to match `keyStoreFormats`.

### Pointers

An attribute that points to another interface or component is named in four different ways today:

| Pattern | Examples |
|---|---|
| Relation, ending in "By" | `terminatedBy`, `protectedBy` |
| Relation, as a verb phrase | `correspondsTo` |
| Noun | `peerInterface`, `keyProvider`, `boundaryProxy`, `externalKeyService` |
| Noun with `Ref` | `keyStoreRef`, `conduitRef` |

The relation pattern reads best, because it states the direction of the link: "this interface is terminated by that one". Recommended pattern: **a pointer is named as a relation from the interface that carries it**.

| Current | Recommended |
|---|---|
| `keyStoreRef` | `keysStoredIn` |
| `keyProvider` | `keysProvidedBy` |
| `conduitRef` | `crossesConduit` |
| `peerInterface` | `connectsTo` |
| `boundaryProxy` | `proxiedBy` |
| `externalKeyService` | `keysHeldBy` |
| `correspondsTo`, `terminatedBy`, `protectedBy` | unchanged |

`peerInterface` is the weakest candidate for change, because "peer interface" is a clear noun. It is included for consistency only.

### The `Ref` suffix

`Ref` currently means three different things:

- a pointer to a component in the same record (`keyStoreRef`, `conduitRef`);
- a URL to an external document (`roadmapRef`);
- an identifier such as a certificate number (`moduleValidationRef`, `hsmApprovalRef`).

If pointers follow the relation pattern above, `Ref` is left for external references only. Recommended: keep `Ref` for "a reference to something outside the record, by URL or identifier", and write that down. `roadmapRef`, `moduleValidationRef` and `hsmApprovalRef` then fit. `productCertificationScheme` has no `Ref` partner for the certificate itself, unlike `moduleValidationScheme` and `hsmApproval`; adding `productCertificationRef` would complete the pattern.

### Absence statements

Two patterns exist side by side:

- `managementInterfaceAbsence` and `storageInterfaceAbsence`, on the subject;
- `contextAbsent:<kind>`, also on the subject.

Recommended: one pattern, **`absent:<thing>`**, with the reason as the value: `absent:management-interface`, `absent:storage-interface`, `absent:sbom`, `absent:roadmap`. A consumer can then find every absence statement with one prefix, and a new profile that adds a new kind of absence needs no new attribute name.

### Certification and approval

Three attributes describe a formal assessment of the product or a part of it:

- `moduleValidationScheme` and `moduleValidationRef`, for the cryptographic module;
- `productCertificationScheme`, for the whole product;
- `hsmApproval` and `hsmApprovalRef`, in the HSM draft, for PCI PTS HSM.

PCI PTS HSM approval is a product-level assessment, so it belongs in `productCertificationScheme` with `pci-pts-hsm` added to the vocabulary by the HSM profile. A separate `hsmApproval` attribute repeats the concept under a domain name.

### Vocabulary values

The values follow lowercase kebab-case almost everywhere. The exceptions are `SL-C 1` to `SL-C 4` in the OT draft (capitals and a space) and `x9.143` in the HSM drafts (a full stop). Values with spaces are hard to match in queries. Recommended: `sl-c-1` to `sl-c-4`, and `x9-143`.

`blockedBy: provider` should become `blockedBy: crypto-library`, for the reason given under `providerLocation`.

### Reference contexts

Most context names are clear. Two are not:

- `design-intent` covers threat models and adversary models. **`threat-model`** says what the document is. If design documents other than threat models are meant to count, the definition should say so, and the current name can stay.
- `issuer-policy` points to the policy of the CA that issues the deployment's certificates. **`certificate-policy`** is the established term (RFC 3647) and covers both the policy and the practice statement.

## Names that work well

The review found most names sound. These are worth keeping, and they are good models for new profiles:

- `keyExchange`, `encryption` and `authentication`. These are the three jobs every secure channel does, in the words practitioners already use.
- `capabilityByPurpose`, `capabilityStatus`, `blockedBy` and `roadmapRef`. Each one says exactly what it holds.
- `enablementMethod` and `enablementSetting`.
- `correspondsTo`, `terminatedBy` and `protectedBy`. These are relations that read as sentences.
- `defaultState`, `lifecycleStage`, `interfaceType` and `coverage`.
- `observationMethod` and `observedAt`.
- `keyCustody`, `keyCustodySupported` and `replicaProtection`.
- `keyReplaceable` and `verifierReplaceable`. These are a good pair, but their values should be aligned: one uses `in-field`, `software-update` and `not-replaceable`, the other uses `yes`, `via-bootloader-update` and `no`.
- `verifierPopulation` and `trustDomain`.
- `zone`, `zonePath`, `referencePoint` and `carriesService` in the drafts.

## Open questions for the working group

1. Should the naming rules above (capability pairs, pointers as relations, `Ref` for external references, `absent:` for absence) be written into the methodology as normative guidance for profile authors? Without them, every new application-domain profile will invent its own patterns.
2. Should `negotiationControl` become two attributes, or should the working group choose one of the two questions it currently mixes?
3. Should `executionEnvironment` adopt the CycloneDX vocabulary as well as the CycloneDX name, or keep its own vocabulary with a mapping?
