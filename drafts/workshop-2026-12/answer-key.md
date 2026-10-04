# Answer key (facilitators only)

Do not hand this out. Floaters use it to keep teams moving. The lead uses it to walk the wall.

**Where things are defined:**

- **Published profiles:** the interface disclosure baseline v0.7 and PQC migration v0.6.
- **Draft profiles, from decision 0022:** baseline v0.8, PQC migration v0.7 and its extended depth.
- **Other drafts:** the procurement profile, the IoT and substation use cases, and the Operation
  and Assurance groups.
- **Open questions** use their register numbers (Q36 and so on).

## What a reasonable plan looks like

There is no single right plan. A team has done well if it separates the systems it can plan from
those it cannot, and can say why.

**Identity, document A.** This system can be planned even though nothing is quantum-safe today.

| Interfaces | Action | Why |
|---|---|---|
| TLS (seven interfaces) | **Software update** | Arrives with the Java runtime in the supplier's image, so the date is the runtime's. The team must check that the database, directory, mail server and external identity providers support the hybrid groups as well |
| Token signing (`svc-oidc`, `svc-saml`, `mgmt-admin`) | **Accept and revisit**, with **escalate** for a dated commitment | Waits on a standard, so pressing the supplier achieves little. Better use of the time: find relying parties that reject unknown key types, and flows that keep tokens in cookies (4 KB limit) |
| Cluster transport (`int-cache`) | **Escalate** | The product fixes the key type |
| Realm keys at rest (`sto-realm-keys`) | **Escalate**, possibly **shield** | Database-level encryption is the operator's own measure |
| Plain HTTP (`svc-http`) | **Enable now**: close it | No post-quantum work protects traffic that is not encrypted at all. Teams that spot this have read the document well |

**Customer portal edge, document B.** It cannot be planned from the document. The document says what
is used and nothing about what could be used, so the honest action is **escalate**: ask for a CBOM
to the PQC migration profile.

A team that knows OpenSSL 3.5 added ML-KEM may plan a software update. Point out that the knowledge
came from outside the document. That is exactly what `keyExchangeSupported`, `enablementMethod` and
`minimumProductVersion` would have carried.

**Substations, document C.** It cannot be planned. No algorithms, partial coverage, nothing about
updates. Realistic actions:

- **Shield** the WAN link from the substation, at the conduit.
- **Escalate** for a baseline-depth CBOM at least.
- **Replace** at the 2033 refurbishment as the default, unless the supplier states an update path.

A team that knows IEC 62351-6 may say GOOSE is protected with a symmetric MAC, and that the exposure
sits in group key distribution and firmware verification. Again, that is knowledge the document
should have carried.

**Priorities.** Most teams put identity first, because it is plannable and every application
depends on it. Then the portal edge, because it is internet-facing. Then substations, because of the
long lead time. Teams that say "substations first, because the lead time is longest" have a good
argument too.

## Inject answers

**Inject 1: advisory.**

| System | Affected? | How sure |
|---|---|---|
| nginx `svc-https` | **Likely yes** | OpenSSL 3.4.0 is named |
| nginx `mgmt-ssh` | **Cannot tell** | The library is withheld |
| Keycloak | **No** | The TLS is the Java runtime's, not OpenSSL. The team can say so because the library is named |
| PR-500 | **Cannot tell** | The entry depth does not ask for the library |

*Lands on:* Disclosure, with `implementationPurl` (I9) already required. Withholding it is allowed
by the baseline; whether a vulnerability-response profile should forbid that is Q57, and the drafted
procurement profile already does.

**Inject 2: regulator.** No document says what data an interface carries or how long it must stay
confidential, and no supplier can, because it depends on what Nordhaven sends through the product.
Document A gives part of the answer: realm keys are stored unwrapped, and the administrative surface
carries credentials. That is data the supplier does know (Q36).

*Lands on:* Operation, in the "no profile yet" row (Q36, Q37, Q45).

**Inject 3: supplier slip.** Teams that recorded a blocker per purpose see that only token signing
moves. The TLS plan is untouched, because it is blocked by the provider, not by the standard. A
supplier date would have hidden this.

*Lands on:* Change planning, already required (capability and blocker per purpose; decisions 0007
and 0010).

**Inject 4: auditor.** A conformance claim bound to the document by digest exists in the methodology
(decision 0015), but none of the three documents came with one. Nothing says whether profiles or
documents are signed (Q29), or what happens when a document is superseded (Q60).

*Lands on:* Assurance. Partly already provided (claims, 0015), partly no profile yet (Q29, Q60,
Discussion #37).

## Expected gaps and where they land

| Gap (as teams tend to phrase it) | Doc | Group | Row | Covered by |
|---|---|---|---|---|
| "What could it support that it doesn't use today?" | B, C | Change planning | Profile already | `keyExchangeSupported`, `authenticationSupported` (PQC migration) |
| "Is it a config change, an update or new hardware?" | B, C | Change planning | Profile already | `enablementMethod`, `providerLocation`, `minimumProductVersion` |
| "When will it be quantum-safe, and what is stopping it?" | B, C | Change planning | Profile already | `capabilityStatus`, `blockedBy`, `roadmapRef` per purpose |
| "Can we migrate while the far end is still classical?" | B, C | Change planning | Profile already | `coexistence`, `negotiationControl` |
| "What breaks when we switch?" | B, C | Change planning | Profile already | `integrationConstraints` (the 4 KB cookie limit in A) |
| "Which algorithms does the relay use at all?" | C | Disclosure | Profile already | Baseline I3 to I5. The entry depth does not ask |
| "Is this the whole list?" | C | Disclosure | Profile already | Coverage (P4). C says partial, which is honest |
| "Which library does SSH use?" | B | Disclosure | Profile already | I9, but withholdable. Q57; the procurement draft forbids withholding |
| "Is SSH traffic encrypted?" | B | Disclosure | Profile already | I4. The supplier said unknown, which the disclosure model allows |
| "Where are keys kept, and are they protected?" | B, C | Disclosure | Draft | `keyWrapping` (baseline v0.8 draft); a storage interface or stated absence (procurement draft P5) |
| "Can the product create and hold the new key type?" | A, B | Change planning | Draft | `keyTypesSupported`, `keyStoreRef` (extended draft) |
| "Will it work in FIPS mode?" | A | Change planning | Draft | `validatedModeAvailability`, module validation (PQC migration v0.7 draft) |
| "Does changing the relay's crypto mean re-certification?" | C | Change planning | Draft | `certificationImpact` (substation draft) |
| "Can the relay's firmware verification ever change?" | C | Change planning | Draft | `verifierReplaceable` (substation draft), `keyReplaceable` (IoT draft) |
| "Who can install new firmware, and how?" | C | Change planning | Draft | `updateAuthority`, `updateMechanism` (IoT draft; change core) |
| "Does it fit the protection timing budget?" | C | Change planning | Draft | `integrationConstraints` with a timing entry (substation draft) |
| "Where do GOOSE keys come from?" | C | Change planning | Draft | `keyStoreRef` mandatory for group-keyed interfaces (substation draft); shared keys are Q08 |
| "Can our forty applications accept ML-DSA tokens?" | A | Operation | None yet | The operator's estate, not the supplier's product (PKI estate placeholder) |
| "How many relays, and which firmware where?" | C | Operation | None yet | Instance data the operator holds (Q67) |
| "Which data must stay confidential beyond 2035?" | all | Operation | None yet | Q36, Q37, Q45 |
| "What did the database and directory actually negotiate?" | A | Operation | None yet | Lifecycle stage `observed` in an operator document |
| "Is this the document the supplier issued, and still current?" | all | Assurance | Partly | Claims bound by digest (0015); signing (Q29) and supersession (Q60) not yet |
| "Could I give this to my regulator as evidence?" | all | Assurance | None yet | The Assurance group's open question |
| "How much will it cost?" | all | — | Not a CBOM question | — |

## Three points for the walk

1. **The top row of Change planning is the reason profiles exist.** Every one of those gaps was
   answered in document A and missing from B and C. All three documents are honest; only one was
   written for a plan.
2. **Operation and Assurance are mostly in the bottom row.** That is where the working group needs
   people from this room.
3. **Document C conforms to something.** An entry-depth CBOM is a real start. The question for the
   procurement manager is what to ask for next time, and the answer is a named profile.
