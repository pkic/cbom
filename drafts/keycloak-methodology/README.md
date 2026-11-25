# Keycloak across the lifecycle: refinements to the methodology

Working draft, 25 October 2026. Nothing here is published by the site. Supersedes the
recommendations in `drafts/lifecycle-stages-keycloak/README.md`, which remains as the first
analysis.

## Files

| File | What it is |
|---|---|
| `profiles/profile-interface-disclosure-0.9.rules.json` | Disclosure baseline v0.9 draft, built from the v0.8 draft in `drafts/pqc-migration-depths` |
| `profiles/profile-deployment-disclosure-0.1.rules.json` | Deployment-scope profile v0.1 draft, extending the baseline. A first profile for the Operation group in draft 0023 |
| `examples/kc-product-implemented.cdx.json` | Keycloak 26.7.3 image, build record. Conforms to the baseline |
| `examples/kc-deployment-configured.cdx.json` | Example Org's deployment, read from its configuration. Conforms to the deployment profile |
| `examples/kc-deployment-observed.cdx.json` | The same deployment, observed over one week. Conforms to the deployment profile |
| `examples/*-fail-*.cdx.json` | Five non-conforming variants, each isolating one rule (see the table under "Checking") |
| `tools/build_examples.py` | Writes every example. The product record is derived from the pqc-migration worked example, so it keeps all migration attributes |
| `tools/evaluate_draft.py` | Evaluator for the drafts. Reuses `validate_cbom.py` and adds the K7–K9 encoding, stage-restricted literals, reference rules and joins across documents |
| `tools/check_examples.py` | Runs every example against its expected verdict and failed rules |
| `tools/compare_stages.py` | Joins the three records along `correspondsTo` and prints the value each stage reports |

The deployment, its operator, hostnames and configuration values are invented. Keycloak facts
come from the sources in `drafts/pqc-migration-depths/examples-keycloak-plan.md`.

## What the example changed

The baseline was written as if one document could carry any lifecycle stage. Building one record
per stage for a real product shows that it cannot. A vendor and an operator report the same
interface with different facts, at different times, for different reasons. The methodology
works once three things are true:

1. **A document has one stage and one subject.** The vendor writes a product record at
   `implemented`. The operator writes deployment records at `configured` and `observed`.
2. **Documents are joined, not merged.** A deployment record cites the product record by
   BOM-Link and hash. Each of its interfaces names the product interface it realises. The
   readiness gap is computed from the join.
3. **Context is pointed to, not carried.** Each profile defines which artefacts a document
   must reference: the SBOM, where vulnerability statements are published, where the operator
   sets a value the vendor leaves open, the configuration a record was read from, the evidence
   behind an observation. The profile also says how each reference is formed. Conformance
   checks the pointer and never the target.

Every proposal below was built into the draft profiles and checked against the examples with
`tools/check_examples.py`. All eight examples validate against the CycloneDX 1.7 schema.

## Proposals

Each proposal says what changes, what in the Keycloak example forced it, and how the examples
test it.

### M1. One lifecycle stage per document (baseline P6)

**Change.** A document declares its stage once, in `metadata.lifecycles`. Every interface
reports that stage. A per-interface `lifecycleStage` stays legal, but it must agree with the
document's stage.

**Why.** The pqc-migration worked example mixes `implemented` and `configured` in one product
record. The seven interfaces labelled `configured` are exactly those whose values Keycloak does
not fix. The example fills them with an assumed RSA-2048 certificate and the JDK defaults, and on
four of them it states the certificate algorithm of a server that Keycloak only connects to.
Mixed stages let a producer fill a gap at one stage with an invented value from another.

**Effect.** Rule I8 maps onto the native CycloneDX field: `build` gives `implemented`,
`operations` gives `configured` and `discovery` gives `observed`. The mapping row that is still
marked "unresolved" is resolved. A producer that follows the 2026 SBOM minimum elements already
records this field.

**Tested by.** The existing worked example fails P6 under v0.9. All three new records pass.

### M2. The document declares its subject type (P5), and the baseline serves two subject types

**Change.**

- A document states whether it describes a `product` or a `deployment`.
- The profile's `scope.subjectType` becomes `scope.subjectTypes`, which is a set. A derived
  profile narrows it to a subset, in the same way it narrows `lifecycleStages`.
- P3 takes its identifier form from the subject type. A product uses a package URL. A
  deployment uses a tag URI (RFC 4151), for example `tag:example.org,2026:deployment/sso-prod`.

**Why.**

- An operator's record of Keycloak names the image's package URL as its subject today. Two
  deployments of the same image then produce conflicting records under one identifier.
- The published nginx pair has the same problem. Its subject is "a conforming nginx deployment",
  but it is evaluated against a profile scoped to a product.
- A deployment profile cannot extend the baseline today. `check_scope_narrows` rejects a derived
  profile with a different `subjectType` as an independent profile. The rules are the same for
  both subjects, so they would have to be copied.
- A tag URI suits an operator's identifier because anyone who controls a domain can mint one.
  A URN would need a registered namespace.

**Tested by.** P3 and P5 pass on all three records. The deployment profile composes from the
baseline. `profile.schema.json` already lists `deployment` as a subject type.

### M3. Remove `intended` from the disclosure baseline

**Change.** The baseline accepts `implemented`, `configured` and `observed`. The enumeration
profile keeps `intended`.

**Why.** A design record answers nothing about deployed interfaces, and the baseline's decision
is about deployed interfaces. Under M1, a design record would also replace the build record
rather than sit beside it. The intention already has three better homes:

- A vendor's intention is a capability status (pqc-migration G1). Keycloak's ML-DSA token signing
  is recorded as `committed`, with the epic as its roadmap reference.
- An operator's intention is a requirement. It belongs in policy or in a tender, which is where
  the Lifecycle page already puts procurement at this stage.
- A design document is context. Rule R6 lets any record point to it.

**Effect.** This reverses part of decision 0008 and needs its own record. It is a tightening, and
no existing example uses `intended`.

**Tested by.** `kc-product-intended-fail-I8` describes Keycloak 27.0 with ML-DSA-65 token
signing. It fails I8 on every interface.

### M4. Two literal values, accepted only at `implemented` (I3–I5)

**Change.**

- `deployment-defined` states that the product does not fix the value and the operator chooses
  it, as with the server certificate.
- `peer-defined` states that the other endpoint decides the outcome, or that it is negotiated
  with that endpoint, as with the group, the cipher and the server certificate on a connection
  Keycloak opens to a database.
- Both are values, alongside `none`. They are not disclosure markers.
- The profile gives each literal the set of stages at which it is accepted. A literal also has
  to stand alone and cannot appear in a list of values.

**Why.** A truthful build record of Keycloak fails I5 on 7 of its 13 interfaces. None of the
four disclosure outcomes is true for these values. The producer knows the fact: someone else
decides the value. Decision 0012 settles it: a rule that no legitimate subject can satisfy
honestly is wrong, not strict. The two values also tell a consumer who has to act. With
`deployment-defined`, the operator acts. With `peer-defined`, another system has to migrate
first.

**Effect.** The general construct is a literal with a stage restriction. It can absorb
`out-of-band` and `product-managed` from K4 and K6.

**A definition the baseline needs.** What a present-state value means differs by stage:

| Stage | Meaning of the value |
|---|---|
| `implemented` | The product's default as shipped |
| `configured` | The set the deployment permits |
| `observed` | The set seen during the observation window |

**Tested by.** `kc-deployment-configured-fail-literal` keeps `peer-defined` on the database
connection at `configured`. It fails I3, I4 and I5 on that interface only.

### M5. Whether an interface is on by default (I11, SHOULD, at `implemented`)

**Why.** Keycloak's plaintext listener exists in the product and is off by default. If it is
declared without this attribute, it reads as an active plaintext interface. If it is left out,
the record hides the interface that becomes the plaintext hop behind a TLS-terminating proxy. In
the example deployment, that is exactly what happened.

In a deployment record the attribute is not needed. A declared interface is active, and a product
interface with no counterpart in the deployment is not.

### M6. A deployment-scope profile that joins documents

**Change.** `deployment-disclosure` v0.1 extends the baseline. It narrows the scope to
`deployment` and to `configured` and `observed`, and adds four rules:

| Rule | Requirement |
|---|---|
| P1 | The record cites the documents it builds on, each by BOM-Link and SHA-256. If the evaluator is given the cited document, it checks the serial number, the version and the hash |
| I1 | Each interface names the interface it realises in a cited document (`correspondsTo`), or states `no-product-document` |
| I2 | At `observed`, each interface names the methods its values came from |
| I3 | At `observed`, each interface gives the time or interval of the observation |

**Inheritance across documents.** Implementation facts follow the join, and present-state facts
never do. In the observed record, `implementationPurl` for the database connection is
inherited through two hops: observed, then configured, then product. Algorithms are never
inherited, because each stage reports its own.

**Why I2 matters.** A single source rarely sees every attribute:

- A passive sensor sees the group in a TLS 1.3 ServerHello but not the server certificate,
  which TLS 1.3 encrypts.
- An active probe sees the certificate.
- `pg_stat_ssl` reports the version and the cipher, but not the group.
- A JWKS shows which signing keys are published.

Naming the methods tells a consumer what the record could and could not have seen.

**What the join shows.** `tools/compare_stages.py` prints the following from the three records.
Each row is one logical interface.

| Interface | implemented | configured | observed |
|---|---|---|---|
| `tls-https` | X25519, cert `deployment-defined` | not configured (TLS ends at the ingress) | — |
| ingress TLS | no product record | X25519MLKEM768, X25519 | X25519MLKEM768 and X25519 (29% of sessions still classical only) |
| `svc-http` | none, off by default | active, plaintext | plaintext on the internal hop |
| `svc-oidc` | RS256 | ES256 | ES256 and RS256 (one client overrides) |
| `int-db` | `peer-defined` | JDK default groups, RSA-2048 server certificate | X25519, RSA-2048 |
| `int-smtp` | `peer-defined` | not configured | — |

No single record contains any of these findings. Each row depends on the join. The Lifecycle
page's sentence "a CBOM that records both views" should read "two CBOMs, joined".

**Tested by.** `kc-deployment-observed-fail-unknown` observes the database connection through
`pg_stat_ssl` only. It declares the group `unknown` and fails I3. `kc-deployment-observed-fail-P1`
cites a revision of the configured record that has since changed. The hash does not match, so it
fails P1.

### M7. Reference rules: context the CBOM points to and does not carry

This is the main addition. Decision 0020 joined vulnerability statements to the CBOM instead of
merging them. The Keycloak records needed the same treatment for about a dozen other artefacts,
so the pattern needs its own kind of rule.

**The construct.** A profile gains a `referenceRules` section with rule letter R. For each kind
of context, the profile defines:

| Field | Meaning |
|---|---|
| `context` | A named kind from the profile's `contextKinds`. A derived profile may add kinds and may not redefine an inherited one |
| `at` | Where the pointer sits: on the document, on an interface, or on a library |
| `carrier` | Which CycloneDX `externalReferences` types can express it |
| `form` | `document`, which is a fixed artefact, or `endpoint`, which is a feed or an API whose content changes. An endpoint names its access protocol, such as `osv-api` or `csaf-provider` |
| `hashRequired` | Whether the pointer binds a revision. Fixed documents usually need a hash. Endpoints cannot have one |
| `orDeclaredAbsent` | Whether the producer may state that no such artefact exists, for example `not-published` |
| `withholdable` | As for attributes |
| `requiredWhen` | A condition on subject type, document stage, or an interface value |

In CycloneDX, every pointer is an `externalReferences` entry. It carries a
`pkic:profile:context` property, because carrier types are shared between kinds:
`documentation` serves several. Endpoints add `pkic:profile:accessProtocol`. CycloneDX 1.7 allows
properties on an external reference.

**Two principles.**

1. **Conformance checks the pointer, never the target.** A verdict says that the pointer exists,
   is well formed, and matches its hash where the evaluator holds the target. It says nothing
   about what the target contains.
2. **Direction follows time.** A record points to artefacts that exist when it is written: its
   SBOM, its configuration revision, its evidence. It also points to the places where later
   statements will appear, such as a VEX feed or an advisory API. A judgement made about the
   record afterwards points to the record by digest. Conformance claims, policy evaluations,
   posture scores and risk ratings all work this way. A record never points to them.

**Three kinds of reference, which the methodology currently mixes.**

| Kind | Target | Form | Example |
|---|---|---|---|
| Internal | An element in the same document | `bom-ref` | `keyStoreRef` |
| Cross-document | Another CBOM or SBOM | BOM-Link and hash | `correspondsTo`, cited documents, companion SBOM |
| Context | Any other artefact | URL, with a hash for documents and an access protocol for endpoints | VEX, advisories, guides, evidence |

`roadmapRef` (pqc-migration G1) and `moduleValidationRef` (pqc-migration I11) are context
references that are modelled as attributes today. They should move under reference rules, so
that one construct governs every pointer.

**Catalogue.** Rows marked "drafted" are in the two draft profiles and are tested.

| Context kind | Points to | Published by | Where it applies | Level | Form, hash | Keycloak example | Status |
|---|---|---|---|---|---|---|---|
| `sbom` | The companion SBOM | Vendor | Product | MUST | Document, hash | BOM-Link (illustrative) | Drafted, baseline R1 |
| `vulnerability-statements` | A VEX or CSAF VEX document, or a feed of them | Vendor | Product | MUST, or stated absent | Either. A document needs a hash | `not-published`: upstream publishes none (to verify) | Drafted, R2 |
| `advisories` | An advisory source, queryable by the package URLs in the record | Vendor or third party | Product | SHOULD | Endpoint, with `web-page`, `csaf-provider`, `osv-api` or `ghsa-api` | GitHub advisories page, and the OSV API | Drafted, R3 |
| `security-contact` | `security.txt` (RFC 9116) or a policy page | Vendor | Product | SHOULD | Endpoint | Keycloak security policy | Drafted, R4 |
| `configuration-guidance` | Where the operator sets a `deployment-defined` value | Vendor | Product, per interface | MUST when a value is `deployment-defined` | Endpoint | TLS guide, management-interface guide | Drafted, R5 |
| `design-intent` | A threat model or design | Vendor or architect | Any | MAY | Either | — | Drafted, R6 |
| `cited-document` | The product record and the configured record | Vendor or operator | Deployment | MUST | Document, hash checked | Product and configured records | Drafted, deployment P1 |
| `configuration-source` | The configuration revision the record was read from | Operator | `configured` | MUST | Immutable revision | Configuration repository commit | Drafted, deployment R1 |
| `observation-evidence` | A scan report, sensor extract or query result | Operator | `observed`, per interface | SHOULD, withholdable | Document, hash | Zeek summary, JWKS, `pg_stat_ssl` result | Drafted, deployment R2 |
| `data-register` | Data classification and confidentiality lifetime per interface | Operator | Deployment | SHOULD, withholdable (MUST in a harvest-now-decrypt-later profile) | Either | Operator's register | Drafted, deployment R3 |
| `issuer-policy` | The issuing CA's CP or CPS | CA | Deployment | MAY | Endpoint | Internal CPS | Drafted, deployment R4 |
| `roadmap` | A vendor roadmap item | Vendor | Product, per purpose | As G1 | Endpoint | Epic #43690, JEP 527 | Exists as `roadmapRef`; move it |
| `module-validation` | A CMVP certificate and security policy | Lab or vendor | Library | As pqc-migration I11 | Document, hash recommended | None in default mode | Exists as `moduleValidationRef`; move it |
| `support-lifecycle` | End of support for the version | Vendor | Product | SHOULD in pqc-migration | Endpoint | Community releases have no long-term support line | Proposed |
| `code-analysis` | Static analysis findings (failure mode 6, integration) | Vendor or assessor | Product | Assurance profiles | Document, hash | — | Proposed |
| `protocol-testing` | Fallback and downgrade testing of the running service (failure mode 10) | Operator or assessor | `observed` | Assurance profiles | Document, hash | — | Proposed |
| `build-provenance` | A provenance attestation (SLSA, Sigstore) | Vendor | Product | Assurance profiles | Document, hash | — | Proposed |
| `platform-assessment` | An entropy and platform assessment (failure mode 9) | Operator or assessor | Deployment | Assurance profiles | Document | — | Proposed |

Three things are deliberately not on this list:

- **Key material.** It is never pointed to.
- **Conformance claims and policy results.** These point to the record, not the other way
  round, under principle 2.
- **Distribution limits.** These are native in CycloneDX 1.7 as
  `metadata.distributionConstraints` (TLP), which is a property of the record and not a
  pointer.

**How the vulnerability join now works end to end.**

1. A consumer takes the library package URLs from I9.
2. The consumer queries the advisory endpoint named under R3. For Keycloak this is the OSV API.
3. The consumer reads whether the vendor considers the product affected, from the VEX source
   under R2. For upstream Keycloak, R2 says none is published, so the consumer knows the answer
   has to come from elsewhere.

The CBOM carries no vulnerability data at any step.

**Tested by.** `kc-product-implemented-fail-R5` drops the guide pointer from the HTTPS listener
while still saying the certificate is `deployment-defined`. It fails R5 on that interface only.

### M8. Smaller corrections found along the way

- **Every published example is invalid against the CycloneDX 1.7 schema.** The top-level
  `$comment` breaks the schema's `additionalProperties: false`. All seven
  `docs/methodology/*.cyclonedx.json` files are affected, and so are the pqc-migration drafts.
  The new examples carry the note in `metadata.properties` (`pkic:example:comment`) instead.
- **`check_profile.py` C3 rejects a guard on `lifecycleStage`.** For example, it rejects
  "required when observed", because the stage vocabulary is defined by the methodology, not by
  the profile. C3 should accept methodology-level vocabularies.
- **pqc-migration should narrow to `product` and `implemented`.** Its subject is the product.
  Operator migration tracking belongs in the Operation group. This is a tightening.
- **The nginx pair needs relabelling or re-scoping.** It mixes `observed` and `configured`
  under a product subject.
- **The cbomgen cprofile's stage vocabulary** (`development`, `build`, `release`, `deployment`,
  `decommission`) applies to the whole document and has no observed value. Send this to the
  maintainers with the earlier findings.

## Checking

Run `python3 tools/check_examples.py`.

| Example | Profile | Expected verdict |
|---|---|---|
| `kc-product-implemented` | baseline v0.9 | Conforms |
| `kc-product-implemented-fail-R5` | baseline v0.9 | Fails R5 on `tls-https` |
| `kc-product-intended-fail-I8` | baseline v0.9 | Fails I8 everywhere, and I3–I5 wherever it repeats a literal |
| `kc-deployment-configured` | deployment v0.1 | Conforms (product record supplied for the join) |
| `kc-deployment-configured-fail-literal` | deployment v0.1 | Fails I3, I4 and I5 on `int-db` |
| `kc-deployment-observed` | deployment v0.1 | Conforms (both cited records supplied) |
| `kc-deployment-observed-fail-unknown` | deployment v0.1 | Fails I3 on `int-db` |
| `kc-deployment-observed-fail-P1` | deployment v0.1 | Fails deployment P1 (hash mismatch) |
| `cbom-keycloak-pqc-pass` (existing) | baseline v0.9 | Fails P3, P5 and P6, as M1 and M2 intend |

To evaluate one document, run
`python3 tools/evaluate_draft.py <cbom> <profile> --with <cited document> ...`.

## What the example does not settle

- **P2 at `observed`.** A scan that cannot reach the management port can neither declare the
  interface nor truthfully state that it is absent. The example avoids the problem by scanning
  from inside the cluster. One option is an absence value `not-observed`, accepted only when
  coverage is `partial`.
- **`unknown` at `observed` on internal interfaces.** The draft keeps `unknown` failing, which
  pushes the operator to combine sources. That may be too strict for estates with no passive
  sensor inside the cluster.
- **One baseline for two subjects, or two siblings sharing a core.** The draft uses one baseline
  with rules keyed by subject type (P3, R1–R4). Draft 0023 takes the sibling-core route for
  change planning. Both work. One baseline keeps the family's single inheritance intact.
- **Whether evidence hashes are practical.** An operator may regenerate evidence. R2 is SHOULD
  and withholdable for that reason.
- **Freshness of endpoints.** A record vouches for the location of a feed, not for its
  content. A consumer reading the feed later sees the current state. That is the intent, but the
  conformance section should say so.
- **The companion SBOM is a placeholder.** Its hash is illustrative, so R1 is checked for form
  only.

## Tooling consequences

The draft evaluator shows that each change can be evaluated. To promote any of them, the
following tools need these changes:

- **`validate_cbom.py`** needs:
  - the K7–K9 adapter (services as interfaces, algorithms from the dependency graph, library
    from `provides`);
  - the document stage from `metadata.lifecycles`;
  - literal constraints with stage restrictions;
  - `subjectTypes` as a set;
  - a `referenceRules` section;
  - BOM-Link resolution with hash checks;
  - inheritance along `correspondsTo`.
- **`check_profile.py`** needs:
  - C11 to accept `subjectTypes`;
  - C3 to accept methodology-level vocabularies;
  - C17 to accept the new constraint keys;
  - a check that every reference rule names a defined context kind.
- **`profile.schema.json`** needs `subjectTypes`, `referenceRules` and `contextKinds`.

## Decision records to write

1. One stage per document, and the native stage field (M1). This amends decision 0008.
2. The subject declared by the document, subject types as a set, and tag URIs for deployments
   (M2).
3. Removing `intended` from the baseline (M3). This reverses part of decision 0008.
4. Literal values with stage restrictions, and the meaning of present state per stage (M4).
5. Joins across documents: citation, correspondence and inheritance (M6). This builds on
   decision 0020 and on Q68.
6. Reference rules and the direction principle (M7). This generalises decision 0020 and moves
   `roadmapRef` and `moduleValidationRef` under the new construct.

## Sources

- Keycloak, Configuring the management interface: https://www.keycloak.org/server/management-interface
- Keycloak, Configuring TLS: https://www.keycloak.org/server/enabletls
- Keycloak, Using a reverse proxy: https://www.keycloak.org/server/reverseproxy
- Keycloak, Configuring distributed caches: https://www.keycloak.org/server/caching
- Keycloak security policy: https://github.com/keycloak/keycloak/security/policy
- OSV API: https://google.github.io/osv.dev/api/
- RFC 4151, The 'tag' URI Scheme: https://www.rfc-editor.org/rfc/rfc4151
- RFC 9116, security.txt: https://www.rfc-editor.org/rfc/rfc9116
- PostgreSQL, `pg_stat_ssl`: https://www.postgresql.org/docs/current/monitoring-stats.html
- CycloneDX 1.7 JSON schema (`metadata.lifecycles`, `externalReferences`): https://cyclonedx.org/docs/1.7/json/
