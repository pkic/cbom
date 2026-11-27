# 0028. Attribute names are made clearer and follow four naming rules

- **Status:** Proposed
- **Date:** 2026-11-27
- **Aspect:** 3.3 — Format-independent attribute model (with consequences for 3.7)
- **Topic / issue:** Attribute naming review, `drafts/attribute-naming-review.md`
- **Deciders:** chair's call, for review by the working group
- **Decision rule applied:** owner call, provisional

## Context

A review of every attribute name in the published and draft profiles found five names that mislead
a careful reader, eleven that say too little, and four naming patterns that the profiles apply
inconsistently. The most serious case was `negotiationControl`. Its glossary definition asked
whether an interface can refuse a classical fallback, while every example record used it to say
where the algorithms are configured. Suppliers reading the name and suppliers reading the
definition would have answered different questions.

No release has been published, so the names can still change without a migration path for
adopters. After Release 1 the publications close the work to date (decision 0027), and a rename
would need a deprecation period.

## Options considered

- **Keep the names and improve the definitions.** This is the cheapest option, but a reader meets
  the name far more often than the definition, and three of the problems are in the names
  themselves: one carries a format, one has a generic word with three other meanings in the
  profiles, and one cannot be told apart from "hybrid".
- **Rename only the five misleading attributes.** This fixes the worst cases, but it leaves every
  new application-domain profile without a pattern to follow, and the drafts already show each
  domain inventing its own.
- **Rename and adopt naming rules.** This costs a one-off migration across the profiles, the
  publications, the examples and the drafts, and gives profile authors rules to follow.

## Decision

The working group renames the attributes listed below and adopts four naming rules for profile
authors.

**The naming rules.**

1. A bare attribute name states what the interface uses. The same name with `Supported` states
   what it can do, and the evaluator treats a `Supported` attribute as the capability partner of
   the bare name. Examples: `keyExchange` and `keyExchangeSupported`; `keyCustody` and
   `keyCustodySupported`.
2. An attribute that points to another interface or component is named as a relation, read from
   the interface that carries it: `correspondsTo`, `terminatedBy`, `keysStoredIn`, `keysProvidedBy`.
3. The suffix `Ref` is kept for references to something outside the record, by URL or by
   identifier: `roadmapRef`, `moduleValidationRef`, `productCertificationRef`.
4. A statement that something is absent is named `absent:<thing>`, with the reason as its value:
   `absent:management-interface`, `absent:storage-interface`, `absent:sbom`.

Vocabulary values are lowercase kebab-case, without spaces or full stops.

**The renames.**

| Previous name | New name | Profiles |
|---|---|---|
| `negotiationControl` | `algorithmSelection` | change-core, pqc-migration |
| `coexistence` (`simultaneous`, `exclusive`) | `transitionMode` (`side-by-side`, `switch-over`) | change-core, pqc-migration |
| `usage` (system) | `designUse` | system-disclosure |
| `providerLocation` | `executionEnvironment` | pqc-migration, iot-device |
| `implementationPurl` | `implementingLibrary` | interface-disclosure |
| `cryptoTerminationPoint` (`device`, `gateway`, `either`) | `terminationOptions` (a set of `device` and `gateway`) | iot-device |
| `externalDependencies` | `trustServiceDependencies` | pqc-migration-extended |
| `minimumProductVersion` | `availableFromVersion` | change-core, pqc-migration |
| `certificationScheme` | `impactedCertification` | change-core, pqc-migration |
| `keyManagementFunction` (`keys-and-certificates`, `none`) | `managesKeys` (`yes`, `no`) | pqc-migration-extended |
| `resourceBound` | `resourceLimits` | iot-device |
| `regenerationTrigger` | `recordRefreshTrigger` | service-disclosure |
| `keyStoreRef` | `keysStoredIn` | pqc-migration-extended, pqc-migration-ot |
| `keyProvider` | `keysProvidedBy` | system-disclosure |
| `peerInterface` | `connectsTo` | deployment-disclosure |
| `managementInterfaceAbsence` | `absent:management-interface` | interface-disclosure |
| `storageInterfaceAbsence` | `absent:storage-interface` | pqc-migration-extended, procurement, service-disclosure |
| `contextAbsent:<kind>` | `absent:<kind>` | interface-disclosure and every profile with reference rules |
| context `design-intent` | context `threat-model` | interface-disclosure |
| context `issuer-policy` | context `certificate-policy` | deployment-disclosure |
| `blockedBy` value `provider` | `crypto-library` | change-core, pqc-migration |
| `verifierReplaceable` values `yes`, `via-bootloader-update`, `no` | `in-field`, `bootloader-update`, `not-replaceable` | pqc-migration-ot |

In the draft profiles: `claimedLevel62443` becomes `claimedSecurityLevel` (values `sl-c-1` to
`sl-c-4`), `conduitRef` becomes `crossesConduit`, `boundary` becomes `operatorBoundary`,
`boundaryProxy` becomes `proxiedBy`, `referenceSpecification` becomes `governingSpecification`,
`externalKeyService` becomes `keysHeldBy`, and `keyBlockFormat` becomes `keyBlockFormats` (value
`x9.143` becomes `x9-143`). The HSM draft's `hsmApproval` is replaced by `productCertificationScheme`,
whose vocabulary in pqc-migration-extended gains `pci-pts-hsm`, and `hsmApprovalRef` becomes
`productCertificationRef`.

`executionEnvironment` and `keyStoreLocation` now draw on one shared location vocabulary.

## Rationale

A name is the first and often the only thing a supplier reads before answering. Names that build
in a carrier format, that reuse a word with other meanings in the same profiles, or that suggest
the wrong question produce inconsistent answers, and inconsistent answers cannot be compared across
suppliers. Written rules keep new application-domain profiles consistent with the generic ones.

`executionEnvironment` also matches the name CycloneDX uses for the same concept, which removes one
translation step for readers who know the format.

## Consequences

- The profiles keep their version numbers, because no release has been published. Each changed
  profile records the renames in its changelog, dated 27 November 2026.
- `tools/migrations/attribute-names-2026-11.py` applied the renames and is kept as a record. A
  branch created before the rename can be brought up to date by running it again.
- Decision records, plans and other historical documents keep the names they were written with.
- Two additions proposed by the review are deferred: `classicalFallback` (whether an interface can
  refuse a classical-only peer) and `encryptionSupported`. Both need facts that the examples do not
  yet record. `productCertificationRef` exists only in the HSM draft for now.
- The review proposed folding `cryptoTerminationPoint` into `terminatedBy`. That was wrong: the
  first states what a device model allows and the second what a deployment does. It is renamed
  `terminationOptions` instead, a set of `device` and `gateway`. It is not named
  `terminationSupported`, because under rule 1 that would make it the capability partner of an
  attribute called `termination`, which does not exist.
- The review proposed renaming `intrinsicData` to `inherentContent`. That was also wrong:
  "intrinsic data" is a methodology concept, defined against "payload" on the data exposure page,
  and the attribute is named after it. The name is kept.

## Links

- `drafts/attribute-naming-review.md`
- Decision 0027, the publications close the work to date
