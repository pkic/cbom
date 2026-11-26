# Carried past Release 1

Items that are not closed by the Release 1 publications and are carried into the next phase of
work. This file starts the register that replaces `open-questions.md` after the line (record 0027).
`open-questions.md` is kept as history. Every item here was recorded on 16 November 2026, during
the closing pass over Publications 1 to 4.

Each item says where it came from, what is already settled about it, and what is left.

On 18 November 2026 the working group widened Release 1 before issue, and most items were resolved in it. Each item ends with its resolution. R2-07 is partly resolved.

## Methodology

**R2-01 — An attribute for the vendor's intrinsic data.**
From: Data Exposure; Publication 2, 11.6. Settled: the vendor states the data an interface exists to
carry for the product's own operation (credentials, keys, tokens, configuration); the operator states
the conveyed payload in its own register. Left: the attribute itself, for example how long a
credential stays valid, and the profile that requires it.
Resolved in Release 1, 18 November 2026. The baseline v0.10 gains `intrinsicData` (I12) and `credentialLifetime` (I13) at MAY, with `credentialLifetime` asked for when `intrinsicData` is not `none`. Publication 2, C.1 and 11.6.

**R2-02 — Grace periods in the rules-file format and the validator.**
From: Q15. Settled: a tightened rule takes effect after a grace period the profile recommends, and a
contract may set a different one. Left: a field in the rules-file format and support in
`validate_cbom.py`, which today report a tightened rule as a failure at once.
Resolved in Release 1, 18 November 2026. A rule, member or override can carry `graceUntil`. Before that date the validator reports a failure as `grace` and does not count it; `--as-of` sets the date. Publication 2, 9.4 (T10) and 9.5; Publication 3, 15.6.

**R2-03 — The claim format's `assessed` field.**
From: the verb convention (a tool evaluates, a rule checks, a claim is verified). Left: renaming the
field to `evaluated`, which changes the claim format version.
Resolved in Release 1, 18 November 2026. Claim format 0.2 renames `assessed` to `evaluated` and adds the `unresolved` and `grace` lists. Publication 2, 9.5.

## Profiles and tooling

**R2-04 — `verifierPopulation` and `trustDomain` in PQC Migration Extended.**
From: Publication 2, 7.4 (provisionally decided at SHOULD, on the `entity-authentication` and
`non-repudiation` purposes). Left: the validator and `check_profile.py` must let a derived profile
add members to an inherited group before the rules can be written.
Resolved in Release 1, 18 November 2026. An override can add members to a group with `addMembers`, and a member can be limited to some group keys with `forKeys`. PQC Migration Extended v0.3 adds `verifierPopulation` and `trustDomain` to G1 for entity authentication and non-repudiation. Publication 2, 6.4 and 6.8.

**R2-05 — Two checker gaps in PQC Migration Extended.**
From: the profile's pending-tooling notes. Left: a `refersTo` constraint for I8, and reading
`cryptographicPurposes` in the scope-narrowing check.
Resolved in Release 1, 18 November 2026. `refersToLocal` checks that a value names a component of the same record, and the profile checker rejects a derived profile that drops a base purpose. Publication 2, 6.2 and 6.8.

## Use cases

**R2-06 — The substation system overlay.**
From: record 0024. Settled: the overlay's rules (S1 to S5) and a `system` subject type accepted only
by the overlay. Left: the rules file, the subject type in the validator, and reporting of cited
verdicts beside the overlay's own (Q68).
Resolved in Release 1, 18 November 2026. Superseded by the System Disclosure profile v0.1, with subject type `system`, and the validator's `--cited-profile` option. Publication 2, 8.2 and 9.4 (T11).

**R2-07 — The rest of the substation worked example.**
From: record 0024. Left: records for the bay controller, station gateway, station server and WAN
router, and the system document; review by a protection IED supplier and a transmission or
distribution operator.
Partly resolved in Release 1, 18 November 2026. The lib60870 product record and the reference substation's system record are worked examples. Left: values marked to confirm in the lib60870 record, and a real supplier product for the IED.

**R2-08 — `usage` as a general facility.**
From: record 0024. Settled: `usage` stays in the substation overlay. Left: whether other derived
documents need it.
Resolved in Release 1, 18 November 2026. `usage` is defined in System Disclosure, so any system record can state it.

**R2-09 — The IoT device estate profile.**
From: the IoT use case. Settled: the subject is a device model (Q62); a hard limit is recorded in
`resourceBound` (Q63); the profile extends the change core (Q64); who can install firmware is
`updateAuthority` (Q65). Left: the rules file; whether `resourceBound` is MUST, and with it
`integrationConstraints`; `updateSupportStatus`, `keyProvisioning` and `cryptoTerminationPoint`;
values of `providerLocation` that fit devices; whether the physical attack surface is in scope; the
worked interface.
Resolved in Release 1, 18 November 2026. The IoT Device Estate profile v0.1 extends the change core, with two soil sensor records as worked examples. Publication 2, 8.2; Publication 3, Chapter 16.

**R2-10 — A transparency-service annex for shared CBOMs.**
From: the Assurance use case. Settled: a digest is SHA-256 over the published file, byte for byte.
Left: whether an informative annex describes transparency services.
Resolved in Release 1, 18 November 2026. Publication 3, informative Annex E. No profile requires registration.

## Application domains

Items raised by the application domain documents after Release 1: the SaaS and cloud services
domain document (Working Draft 0.1, 16 November 2026), the operational technology domain
document (Working Draft 0.2, 17 November 2026), and the telecom service-assurance overlay draft
(17 November 2026).

**R2-11 — The subject type `service` in the baseline and the change core.** Baseline part applied to Release 1, 17 November 2026.
From: the SaaS and cloud services domain document, 8.1. Settled: `service` is already a value in
`profile.schema.json`. Left: adding it to the accepted subject types of the interface disclosure
baseline, and later of the change core. A derived profile may narrow its base's subject types but
never widen them, so no service profile can extend either until they accept `service`. Adding a
subject type changes no rule for product or deployment records. Tested in `drafts/saas-keycloak/`:
with the change, a service record conforms; without it, it fails P3 and P5 and nothing else.
Applied: the interface disclosure baseline v0.10 accepts `service`, identified by a tag URI, and the
service profiles in `drafts/saas-keycloak/` now extend it. Left: the change core.
Resolved in Release 1, 18 November 2026. The change core v0.2 accepts subject type `service` and the update mechanism `provider-managed`.

**R2-12 — Key custody on storage interfaces.**
From: the SaaS and cloud services domain document, 8.2 and Annex B. Proposed: `keyCustodySupported`
on a service record's storage interfaces, as a set from `provider-managed`, `customer-managed` and
`external`, and `keyCustody`, as one of those values: on the service record the default a new tenant
gets, on a tenant record the tenant's choice. Because `keyCustodySupported` is a capability, a service
profile declares orientation `both` (C12). Tested in `drafts/saas-keycloak/`. Left: the attribute list,
the vocabulary, and the CycloneDX mapping.
Resolved in Release 1, 18 November 2026. Key custody is in the Service Disclosure profile v0.1 and its restricted variant.

**R2-13 — A `change-notice` context kind.**
From: the SaaS and cloud services domain document, chapter 7. Proposed: a context kind that points
to where a provider announces changes, so that a customer's policy can judge whether the record it
holds is current. Left: the context kind in the baseline's `contextKinds`, the CycloneDX reference
types that can carry it, and a check under requirement C18.
Resolved in Release 1, 18 November 2026. The baseline defines the context kind `change-notice`, and Service Disclosure requires it. Publication 2, 12.4.

**R2-14 — The subject type `system` in the baseline.** Resolved, 17 November 2026.
From: the OT domain document, 8.3. Decision: the baseline accepts `system`, identified by a tag URI
(RFC 4151) like a deployment. A system record describes one system design as its integrator
delivers it, at the stage `configured`. Like a deployment record, it lists the interfaces in use,
each joined by `correspondsTo` to the product interface it realises, so it cites the product records
rather than repeating them. It differs from a deployment record only in its subject: one design built
at many sites, not one site. Tested in `drafts/r2-14-system/`: the baseline as v0.10-draft, with
`service` (R2-11) and `system` added and no other change, is well-formed. A system record for the
reference substation conforms to it, and inherits the implementing libraries from the protection IED
record through the join; against v0.9 it fails P3 and P5 and nothing else. Applied to Release 1, together
with R2-11: the interface disclosure baseline v0.10 and the interface enumeration profile v0.4. The
draft overlay `ot-system` in `drafts/ot-system/` extends v0.10.

**R2-15 — A generic home for the overlay rules.** Resolved, 17 November 2026.
From: the OT domain document, 8.3. Decision: the two rules stay in `ot-system` until a second sector
writes an overlay. When the telecom service-assurance overlay is drafted, both rules move to a generic
overlay profile in the Operation group document, with subject type `system`, and `ot-system` and the
telecom overlay extend it. Moving them earlier would create a generic profile with one user and
nothing to test it against.
Applied in drafts, 17 November 2026: the telecom service-assurance overlay is drafted
(`drafts/telecom-service-assurance/`), and the rules moved to the generic overlay `system-disclosure`
(`drafts/system-disclosure/`), which `ot-system` v0.2-draft and the telecom overlay extend. S4, the key
provider, moved as well, because telecom needs it: N32 and SBI certificates come from the operator's
PKI. Left: the working group to confirm the move of S4, and the generic overlay's place in the
Operation group document.
Resolved in Release 1, 18 November 2026. The move of S4 is confirmed. System Disclosure v0.1 is published in Release 1, and the OT and telecom drafts extend it.

**R2-16 — `keyStoreRef` on interfaces that use no key.** Resolved, 17 November 2026. No profile change.
From: the OT domain document, 10.3. The libIEC61850 record failed `pqc-migration-ot#I3` on its MMS,
GOOSE and SV interfaces because it left `keyStoreRef` out. The literal `none` already means "this
interface uses no keys" (PQC Migration Extended I8, decision 0022, K3), and I3 accepts it. With
`keyStoreRef` set to `none` on those interfaces, the record passes I3. Left: an editorial change to
the note of `pqc-migration-ot#I3` in its next version, naming the literals `none`, `out-of-band` and
`product-managed` as PQC Migration Extended I8 does.

**R2-17 — R-GOOSE and R-SV in the list of protocol names.** Resolved, 17 November 2026.
From: the OT domain document, chapters 5 and 10. Decision: add `R-GOOSE`, tied to IEC 61850-8-1
Amendment 1, and `R-SV`, tied to IEC 61850-9-2 Amendment 1. The session protocol that carries both is
not a separate name: an interface names the message type it carries. Applied to the list in
Publication 2, C.2, and on the Terms page after Release 1 is tagged.

**R2-18 — Checking that a system record lists every product interface.**
From: the OT domain document, 8.3 (S2), tested in `drafts/ot-system/`. S2 asks a system record to
state `usage` for every interface of every product it cites, so that an interface left enabled and
unused is visible. The evaluator checks `usage` on each interface the record lists. It cannot check
that none is missing: that needs a constraint that reads each cited document and looks for an
interface no `correspondsTo` points at. Left: whether to add that constraint, as a product rule on
cited documents, and whether a missing interface is a failure or a warning. The same check would
serve deployment and service records.
Resolved in Release 1, 18 November 2026. The product constraint `coversCitedInterfaces` checks that every interface of each cited record is matched. System Disclosure P2 uses it.

**R2-19 — One boundary rule for zones and operator boundaries.**
From: the telecom service-assurance overlay, tested in `drafts/telecom-service-assurance/`. The OT
overlay states a zone for each interface and the conduit a path crosses. The telecom overlay states
whether a connection crosses the operator boundary and the component that terminates it. Both are an
attribute that says a connection crosses a boundary and a pointer to the component that guards it.
They stay separate for now, because IEC 62443 zones and 3GPP security domains are defined differently.
Left: whether a third sector shows the same shape, and if so, whether one generic rule with a
sector vocabulary replaces both.
Resolved in Release 1, 18 November 2026. Zones and operator boundaries stay sector rules. Publication 3, Step 2, gives the pattern as guidance.

**R2-20 — Checking a value against a list the record declares.**
From: both overlays. An interface's `zone` should be one of the system's `zones`, and its
`carriesService` one of the system's `services`. A `conduitRef`, `boundaryProxy` or `keyProvider`
should name a component of the same record. The evaluator checks each value on its own and cannot
compare it with another attribute of the same document. Left: whether to add a constraint that does,
and whether a mismatch is a failure or a warning.
Resolved in Release 1, 18 November 2026. `inSubjectList` checks a value against a list the record declares, and `refersToLocal` checks a pointer to a component. Publication 2, 6.2.

**R2-21 — What terminates an interface's cryptography.** Resolved in Release 1, 19 November 2026.
From: the telecom domain document, 8.4, and the Keycloak records, where the ingress terminates TLS for
Keycloak's HTTP listener. Decision: the baseline v0.10 defines `terminatedBy` (I14) at MAY, checked with
`refersToLocal` and the literals `workload` and `platform`. Deployment Disclosure v0.3 raises it to MUST on
every interface but storage, and Service Disclosure v0.1 to SHOULD. IoT Device Estate's
`cryptoTerminationPoint` stays as the product-level statement of what a device model allows.
Publication 2, C.1 and 8.2.


**R2-22 — Keys held outside the record.**
From: the OT document (10.4) and the SaaS tenant draft (8.4, 8.6). `keyStoreRef` names a component of
the same record. OT writes `out-of-band` where the key plane lives outside the library, and SaaS writes
`external-key-service` where the tenant's own service holds the keys. Publication 2, position 31, stops
a derived profile adding values to a vocabulary that does not key a group. Left: one set of literals for
keys held outside the record, added to PQC Migration Extended, and the drafts checked against it.
Proposed, and applied in the working drafts on 19 November 2026. The literals stay those of PQC Migration Extended I8: `none`, `out-of-band` and `product-managed`. The SaaS key-custody draft uses `out-of-band` for keys held by the tenant's own service and drops `external-key-service`. Where that service has a record, the tenant record names it with `externalKeyService`, as before. The OT document already used the Release 1 literals.

**R2-23 — Certification impact in the change core.**
From: the financial services outline (HSM profile, 8.1), the telecom document (NESAS and SCAS) and the
SaaS document (FedRAMP). `certificationImpact` exists only in the substation component profile.
Publication 3, position 36, keeps module validation out of the change core. Left: whether
`certificationImpact` and `certificationScheme` move into the change core, or the HSM profile is based on
PQC Migration Extended instead.
Proposed, and applied in the working draft on 19 November 2026. The change core and PQC Migration declare `certificationImpact` (I17, SHOULD) and `certificationScheme` (I18, SHOULD) under the same ids, with the vocabulary moved from the substation component profile. That profile raises change-core#I17 to MUST and no longer declares its own I1 and I2. Module validation stays out of the change core, so Publication 3 position 36 stands. An HSM profile extends PQC Migration Extended and gets both. Verdicts are unchanged; the rule ids in substation reports change.

**R2-24 — Which device profile applies where.**
From: the OT, telecom and financial services documents. OT field devices use the substation component
profile, telecom SIMs and eSIMs follow IoT Device Estate, and financial services cards and terminals
extend it. OT does not mention IoT Device Estate, though water telemetry RTUs fit it. Left: a rule for
choosing between the two, written in the Change planning group document.
Proposed. IoT Device Estate is for a device model in a fleet, where the decision is update, replace, shield or accept per model and resource limits decide it. The substation component profile is for a component of an engineered system, where certification impact and real-time limits decide it. A device may be evaluated against both. SIMs and eSIMs, payment cards and terminals, and water telemetry RTUs follow IoT Device Estate; protection IEDs follow the substation profile. The rule is written in the Change planning group document, and the OT document says so in chapter 6.

**R2-25 — Shared names for boundary rules.**
From: the OT document (8.3), the telecom document (8.2) and the financial services outline (4).
Follows R2-19. OT records zones and conduits, telecom a crossing value and `boundaryProxy`, financial
services borrows the telecom shape, and SaaS has none. Left: a shared note in the Change planning group
document so that attribute names and checks (`refersToLocal`, `inSubjectList`) line up across sectors.
Proposed. R2-19 stands: boundaries stay sector rules. Every boundary rule has two parts: a value on each interface, checked against a list the subject declares (`inSubjectList`) or a vocabulary, and a pointer to the component that guards it, checked with `refersToLocal`. A new sector reuses the telecom names `boundary` and `boundaryProxy` unless it has a recognised term of its own, as OT has for IEC 62443 zones and conduits. Financial services takes the telecom names. SaaS needs no boundary rule, because tenancy is a separate record. The note is kept in the Change planning group document.

**R2-26 — Multi-party trust networks.**
From: the financial services outline (4, 8.3) and the telecom document (4). Telecom reads interconnect
from both ends, each operator describing its own end. Financial services has a card scheme cite its
participants' records. Publication 2, position 34, limits version 1 of the model to two-party
relationships. Left: one model for a scheme or network with many participants.
Proposed. The model stays within two-party relationships (Publication 2, position 34). Each participant describes its own end, as telecom interconnect does. The scheme operator writes records only for what it runs, such as the scheme CA, directory servers and key distribution. Whether every participant can move is a policy over the set of participants' records: a new policy for the Operation group, not a new profile.

**R2-27 — Key references across records.**
From: the financial services outline (3, 8.4). The HSM has its own product and deployment records, so a
key hierarchy crosses documents. `keyStoreRef` resolves only within one document. Left: a reference by
BOM-Link and hash to a key store in another record, aligned with R2-22.
Proposed, and applied in the working draft on 19 November 2026. `refersToLocal` gains the option `orCited`: the value may then also be a BOM-Link to an interface in a record the document cites, checked as `refersToCited` checks it. PQC Migration Extended I8 and the SaaS key-custody draft use it. Where no record exists, the value stays `out-of-band` (R2-22). I8 is SHOULD, so no verdict changes. Tested in `tests/check-additions.py`.

**R2-28 — What a sector profile extends.**
From: Publication 3, position 27, and the telecom and SaaS documents (12.1, 8.1). The position says a
sector profile extends the baseline or the change core. The domain drafts extend System Disclosure,
Deployment Disclosure, Procurement and Service Disclosure, Restricted. Left: whether position 27 is read
as "directly or through a Release 1 profile", and the wording changed before ratification.
Proposed. Publication 3, position 27, reads: "A sector profile extends a Release 1 profile, directly or through another. It adds only rules specific to its sector; a rule that serves several sectors moves to Release 1 or a group document." The OT and telecom documents quote the new wording. The position is not yet ratified, so it changes before the ballot.
**R2-29 — A service that has no records to cite.**
From: the financial services worked example (AWS Payment Cryptography, chapter 11). Service Disclosure
P3 requires a service record to cite at least one record it builds on, by BOM-Link and hash, and does
not allow it to be withheld. A provider that runs its own platform on hardware whose vendor publishes no
product records cannot meet P3 honestly. Publication 3 holds that a rule no legitimate subject can satisfy
honestly is wrong, not strict (decision 0012). Left: whether P3 accepts a declared absence.
Proposed. P3 gains `orDeclaredAbsent`, as P2 has, with a vocabulary of reasons: `no-records-published`
(the products exist but their vendors publish no records) and `provider-built` (the provider wrote the
software itself and publishes no product record of it). A record that declares an absence still conforms,
and a policy can treat the absence as a gap. Not yet applied.

**R2-30 — The algorithm that verifies updates.**
From: the regulatory sufficiency register (CNSA 2.0, question CNSA-signing; CRA Annex I, Part II, point (7)),
and the automotive and healthcare outlines. The change core requires how updates reach a product (I13) and
whose updates it accepts (I14). It does not require the signature algorithm that verifies an update.
Whether that algorithm and its trust anchor can be replaced is required only by the substation component
profile (`pqc-migration-ot#I4`, `verifierReplaceable`). The update path is the root of trust: if the
verifier cannot change, nothing else on the device can migrate safely. Left: whether the change core
requires both facts.
Proposed. The change core declares two rules, guarded like I14 (`updateMechanism` not `none`):
`updateVerificationAlgorithm` (I19, MUST, an algorithm name under the inherited naming scheme, or
`none` where updates are not verified) and `verifierReplaceable` (I20, SHOULD, with the vocabulary moved
from the substation component profile: `yes`, `via-bootloader-update`, `no`). The substation component
profile no longer declares its own I4 and raises change-core#I20 to MUST, in the same way as R2-23 moved
`certificationImpact`. IoT Device Estate inherits both. The baseline is unchanged. Not yet applied.
Effect on the register: CNSA-signing moves from partial to deeper-profile, and CRA-I-2c gains the
algorithm in its evidence.

**R2-31 — Integrity protection of what a store holds.**
From: the regulatory sufficiency register (CRA Annex I, Part I, point (2)(f)). The CRA requires stored data,
commands, programs and configuration to be protected against unauthorised modification. On a storage
interface the baseline requires `encryption` (I4) and `keyWrapping` (I10), which show confidentiality.
Where the encryption algorithm is authenticated, such as AES-GCM, it also shows integrity. Where it is
not, or where the store holds configuration that is signed rather than encrypted, the record cannot say
how integrity is protected. Left: whether to add an attribute, and at which level.
Options. (a) Add nothing: a policy infers integrity from an authenticated encryption algorithm, and
reports the rest as unknown. (b) Add `integrityProtection` to storage interfaces in the baseline at MAY,
with an algorithm name, `authenticated-encryption` where I4 already covers it, or `none`. A profile written
for CRA evidence raises it to SHOULD or MUST. (c) Add it at MUST in the baseline.
Proposed: (b). Option (a) leaves signed configuration and non-authenticated encryption unanswerable, and
(c) changes the conformance of every published record for a fact that matters to one regulation. At MAY,
no existing record changes its verdict. Not yet applied. Effect on the register: CRA-I-2f stays partial
for the baseline and becomes deeper-profile once a profile requires the attribute.

**R2-32 — Strength for names that do not carry the key size.**
From: the comparison of the example classification set with crypto-algorithm-kb
(`docs/pkic-classification-comparison.md` in that repository). The KB and the PKIC set agree on quantum
vulnerability for every name both classify, and agree in full for 54 names. For 29 names the KB leaves the
strength unknown, because the name does not bind the parameter it depends on: 23 RSA names such as `RS256`,
`rsa_pss_rsae_sha256` and `RSA-PSS-SHA-256` (no modulus size), and 6 elliptic-curve names such as
`ECDSA-SHA256` and `ECDH-ES` (no curve). The PKIC set gives each of them a strength, which assumes a
2048-bit modulus or a particular curve. Left: whether the set may assume.
Proposed. The classification set gives no strength where the name does not bind the parameter, and says
why in a note. The algorithm-transition method reports such a finding as `indeterminate-strength` rather
than applying a schedule row chosen by an assumed strength. For a quantum-vulnerable algorithm the outcome
after 2030 is the same at every strength, so only the current status of possibly short keys changes. The
CBOM can avoid the question: where an interface states the key size, for example in `keyTypes` or the
certificate algorithm, the policy uses it. Not yet applied, because it changes published results.
