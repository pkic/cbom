# Lifecycle stages and the disclosure baseline: the Keycloak example

Working draft, 25 October 2026. Nothing here is published by the site. The recommendations are
superseded by `drafts/keycloak-methodology/README.md`, which builds and tests them.

Checked against the Interface Disclosure Baseline v0.8 draft
(`drafts/pqc-migration-depths/profile-interface-disclosure.rules.json`). Rules P1–P4 and I1–I9
are the same in the published v0.7, so every finding applies to v0.7 as well. The verdicts come
from reading the rules. The published validator does not yet read the K7–K9 encoding the
Keycloak examples use, so it could not be used to confirm them.

## Summary

The baseline accepts all four stages, but only a document at `configured` is easy to make
conform. A truthful Keycloak document at `implemented` fails I5 on seven of its 13 interfaces.
A truthful document at `observed` fails P3 and I9, and may fail P2. A document at `configured`
conforms. However, it describes one deployment while the baseline treats it as a description
of the product. A document at `intended` conforms on paper, but it gives no answer to the
question the baseline exists to answer.

The worked example already shows the first problem. The seven interfaces whose values Keycloak
does not fix are exactly the seven the example labels `configured`. To fill them, it supplies an
assumed RSA-2048 certificate and the JDK defaults. On four of them it also states the
authentication algorithm of a server that Keycloak only connects to, such as the database.
The example passes because it contains invented deployment facts.

| Stage | P3 subject | I3–I5 algorithms | I9 library | P2 management | Serves the baseline's decision | Result for a truthful Keycloak document |
|---|---|---|---|---|---|---|
| `intended` | Strained: no artefact exists yet | Target values, often conditional | Often unknown, so it fails | Passes | No | Conforms, but serves a different consumer |
| `implemented` | Passes | **Fails** where the operator or a peer decides the value | Passes | Passes | Yes | Fails on 7 of 13 interfaces |
| `configured` | **Wrong kind of subject** | Passes; values are permitted sets | Passes | Passes | Yes, for one deployment | Conforms, but names the product as its subject |
| `observed` | **Fails**: a scan sees endpoints, not packages | Passes per source; some sources leave gaps | **Fails**: invisible on the wire | May fail: depends on the scan's vantage point | Yes, and it is the best evidence | Fails |

## Stage 1: `intended`

**Who produces it, and from what.** There are two possible producers. The Keycloak project can
produce one from its design for 27.0, using epic #43690, which plans ML-DSA token signing. An
operator's architect can produce one from the design of a planned identity service.

**What a reasonable document contains.** The vendor's version looks like the 26.7.3 document
with one change. `svc-oidc` gets `authentication: ML-DSA-65` and `lifecycleStage: intended`.
Every other interface repeats today's values, because nothing else is planned. The architect's
version states target values. For example, it might give hybrid ML-KEM key exchange on the
external TLS interface, ES256 tokens until ML-DSA is available, and `verify-full` TLS to the
database.

**Where it meets the baseline.**

- **P3.** The vendor can write `pkg:oci/keycloak?...&tag=27.0`. The validator accepts it,
  because it starts with `pkg:`, but no such image exists, so the identifier resolves to
  nothing. The architect's subject is a planned deployment, which has no package URL at all.
- **I9.** A design often has not chosen the library yet. For example, ML-DSA could come from a
  JDK 24+ provider or from Bouncy Castle. `unknown` fails a MUST rule. `withheld` would be
  false, because the producer is not holding anything back.
- **I3–I5.** Design values are often conditional ("ML-DSA-65 once the AKP key type is
  standardised, otherwise RS256"). A single present-state value cannot carry a condition.
- **The decision.** The baseline's consumer wants to know which deployed interfaces a published
  weakness affects. An intended value answers nothing about deployed interfaces. The baseline
  also allows one stage per interface. So if an inventory accepts the intended record of
  `svc-oidc`, that record replaces the implemented one, and RS256 disappears from the record
  at exactly the moment a consumer needs to see it.
- **Two homes for one fact.** The migration profile already excludes `intended`. It records the
  vendor's intention as a capability status instead: for `svc-oidc` it records
  `capabilityStatus: committed`, `blockedBy: standard`, milestone 27.0. The family therefore
  records the same Keycloak intention in two different ways.

**How to manage it.** There are two options.

- **Keep `intended` in the baseline.** This is the reasoning in §4.4 and in decision 0008: an
  intention that is disclosed is more useful to an inventory than one that is withheld. Accepting
  a stage costs nothing in itself.
- **Remove `intended` from the disclosure baseline and keep it in the enumeration profile.**
  A vendor's intention already has a home in the capability group G1. An architect's intention
  is a requirement, so it belongs in a profile or a tender, not in a CBOM. The Lifecycle page
  already says this about procurement: at `intended`, a buyer states the requirement and does
  not check it. The enumeration profile's decision is about where to look and whom to ask, and
  an intention helps with that decision.

Recommendation: take the second option. It narrows the accepted stages, which is a tightening,
and it reverses part of decision 0008, so it needs a decision record. No existing example uses
`intended`.

## Stage 2: `implemented`

**Who produces it, and from what.** The Keycloak project or a downstream builder produces it in
the build pipeline. The sources are a source and dependency scan, the image manifest (which
gives the JDK version, K1) and the documented defaults.

**What a reasonable document contains.** It describes the 26.7.3 image at its defaults. The
interfaces split into two groups.

| Interface | Does the product fix the value? | Truthful value for I3 / I4 / I5 |
|---|---|---|
| `svc-oidc`, `svc-saml`, `mgmt-admin` | Yes (realm and client defaults) | `none` / `none` / RS256 or RSA-SHA256 |
| `svc-http` | Yes | `none` / `none` / `none`. The listener is off by default, and nothing in the baseline can say so |
| `int-cache` | Yes, including the key type | x25519 / AES-256-GCM / RSA-2048, generated by the product |
| `sto-realm-keys` | Yes | encryption `none`, keyWrapping `none` (#39933) |
| `tls-https`, `tls-mgmt` | Key exchange and cipher, yes (JDK defaults). Certificate, no | x25519 / AES-256-GCM / **decided by the operator's certificate** |
| `int-db`, `int-ldap`, `int-broker`, `int-smtp` | Keycloak's offer is fixed. The outcome and the server's certificate are not | **Negotiated with the peer** / **negotiated with the peer** / **the peer's certificate** |
| `svc-broker-tokens` | No. The external identity provider chooses the signature | **decided by the peer** |

**Where it meets the baseline.**

- **I3–I5 on seven interfaces.** None of the four disclosure outcomes is true for these values.
  The producer has no value to give. `unknown` would be false, because the producer does know
  the fact: the operator or the peer decides the value. `withheld` would also be false. `none`
  would be wrong. A truthful build document therefore fails the baseline.
- **What "present state" means at this stage.** The baseline says present state has one answer
  per attribute. At build time the product's TLS stack offers a list of groups. The example uses
  the first group in the default order. Nothing in the profile says to do that, so two producers
  can describe the same image differently.
- **Disabled interfaces.** `svc-http` exists in the product and is off by default. If the
  producer declares it, the document reads as if a plaintext interface is active. If the
  producer leaves it out, the document hides the interface that becomes the plaintext hop behind
  a TLS-terminating proxy.

**How to manage it.** The working group has already handled the case of "no truthful value"
three times. Each time it added a literal value that states a fact: `none` (K3), `out-of-band`
(K4) and `product-managed` (K6). The same approach fits here.

1. Accept `deployment-defined` on I3–I5 for values the operator decides, such as the server
   certificate. Accept `peer-defined` for values the counterpart decides, such as an
   interconnect's negotiated group and the server's certificate. Each value tells a consumer who
   has to act. The first means the operator acts. The second means another system has to migrate
   first, which links to `trustServiceDependencies` in the extended depth.
2. Accept these values only at `implemented`. At `configured` or `observed` they would let a
   producer avoid giving an answer it has. This needs a stage-conditional constraint, which the
   evaluator does not support yet.
3. State in the baseline that a present-state value at `implemented` is the product's default
   as shipped.
4. Consider a SHOULD attribute that says whether an interface is enabled by default. Without
   it, `svc-http` stays ambiguous.
5. Correct the Keycloak example. Label the seven interfaces `implemented`, give them the new
   values, and remove the assumed RSA-2048 certificate. Move that illustration to a separate
   `configured` document (stage 3). The pair then shows the split between a product CBOM and a
   service CBOM that the Lifecycle page describes.

The migration profile is not affected. Its capability attributes, such as
`keyExchangeSupported`, are already true facts at `implemented`.

## Stage 3: `configured`

**Who produces it, and from what.** The operator or integrator produces it. The sources are
`keycloak.conf` or the container environment, the realm export, the JVM's `java.security`
(`jdk.tls.namedGroups`), the certificate files, the JDBC URL and the LDAP settings.

**What a reasonable document contains.** The following is an illustrative deployment. It runs on
Kubernetes. TLS is terminated at the ingress, and Keycloak runs with `http-enabled=true` and
`proxy-headers=xforwarded`.

- `tls-https` is not configured. The external TLS interface belongs to the ingress controller,
  which is a different product with its own document.
- `svc-http` is now active: `none` / `none` / `none`, carrying tokens in clear on the hop from
  the ingress.
- `svc-oidc` uses the realm's `defaultSignatureAlgorithm`, which the operator has changed to
  ES256.
- `int-db` has `sslmode=verify-full`. Key exchange is the permitted list from the JVM, and
  authentication is the database server's certificate (for example RSA-2048 from the internal
  CA). The operator knows both.

Two of the product document's interfaces change at this stage: one disappears and one becomes
live. This is the point of keeping the two documents apart.

**Where it meets the baseline.** Every rule can be met. The problem is the subject.

- **P3 and `subjectType: product`.** A deployment has no package URL, so the operator writes the
  image's purl. The document then claims to describe the product, but it describes one
  deployment. Two deployments of the same image produce two different records under the same
  subject identifier. The baseline's decision includes comparing this record with last
  quarter's. That comparison, and correlation across organisations, stop working.
- The Lifecycle page says that a service CBOM, not a product CBOM, covers `configured` and
  `observed`. The baseline is scoped to a product and accepts both stages. The published nginx
  pair shows the same mix: it records HTTPS as `observed` and SSH as `configured`, and §5 of the
  baseline calls its subject "a conforming nginx deployment".
- **I3/I4.** A configured value is a permitted list, while the outcome is negotiated. This is
  acceptable, provided the baseline says so.

**How to manage it.** There are two options.

- **Option A, a conditional product rule.** Add P5 to the baseline: if any interface is
  `configured` or `observed`, the document identifies the deployment and references the product
  document it builds on. This is the smallest change.
- **Option B, the Operation group.** Limit the product baseline to `implemented`, and give
  `configured` and `observed` to a deployment-scope profile. That profile extends the baseline,
  declares `subjectType: deployment`, identifies the deployment and cites the supplier documents
  it builds on as an overlay (DR-12). Draft 0023 already proposes this group, "Operation", where
  the producer is the operator, the stages are mostly `configured` and `observed`, and supplier
  documents are cited, not repeated. `profile.schema.json` already lists `deployment` and
  `system` as subject types.

Recommendation: take Option B, and use Option A only if the Operation group is not accepted.
Under Option B, the nginx pair has to be relabelled or re-scoped. Option B also takes in Q67
(whether an estate is a subject type) and Q68 (what an overlay's verdict says about the
documents it cites).

## Stage 4: `observed`

**Who produces it, and from what.** Operations or monitoring teams produce it. The sources are a
TLS scan of the listeners from inside the cluster, a fetch of the realm's JWKS and SAML
descriptor, `pg_stat_ssl` on the database, flow telemetry for outbound connections and a query
of the key table.

**What a reasonable document contains.**

- The ingress's negotiated group and certificate. These belong to the ingress's document.
- `svc-oidc`: the JWKS shows an active ES256 key, and the default RSA key is still published. A
  client with an RS256 override would still receive RS256 tokens. This is a fact that the
  configured record of the realm default does not show.
- `int-db`: `pg_stat_ssl` shows TLS 1.3 and `TLS_AES_256_GCM_SHA384`. It does not show the
  negotiated group, so `keyExchange` is `unknown` from this source.
- `int-cache`: port 7800 shows TLS 1.3 and the product's RSA-2048 certificate.
- `sto-realm-keys`: the database query shows plaintext private keys.
- `mgmt-health`: present only if the scanner can reach port 9000.

**Where it meets the baseline.**

- **P3.** A scanner sees hosts and ports, not packages. To meet the rule, someone has to join the
  scan to an asset inventory or to the product document.
- **I9.** The implementing library is not visible on the wire. `unknown` fails, and `withheld`
  would be false.
- **P2.** If the scan cannot reach the management port, the producer cannot declare the
  interface. None of the absence values (`no-configuration-surface`, `configured-out-of-band`,
  `not-applicable-to-subject`) is true either.
- **I3–I5.** Each source sees some attributes and not others, as `int-db` shows. A negotiated
  value also depends on what the probing client offered. A probe that supports hybrid groups
  sees a hybrid group, while older relying parties still get x25519. The baseline has no field
  for the observation's vantage point, the probe or the time.

This is the stage that the baseline handles worst, and the Lifecycle page treats it as the
evidence that matters most: "The evidence for progress against harvest-now-decrypt-later is the
handshake, not the version number."

**How to manage it.**

1. Do not relax I9. Instead, let an observed interface inherit I9 from the record of the same
   interface in the product document. This extends K9 inheritance across documents (see the
   cross-cutting issue below).
2. Record the observation context, preferably in native fields: CycloneDX
   `metadata.lifecycles[].phase = discovery`, `metadata.tools` and the timestamp. Add a SHOULD
   attribute for the probe and the vantage point.
3. For P2, accept a stated "not reached" only when coverage is `partial`. Under Option B this
   moves to the Operation profile.
4. Decide whether `unknown` is acceptable at `observed` on internal interconnects, where no
   single source sees every attribute. Keep it failing on external interfaces, because those are
   the ones exposed to harvest-now-decrypt-later.

## Cross-cutting issue: one stage per interface

The readiness gap is the difference between `implemented` and `observed` for the same interface.
The Lifecycle page says that "a CBOM that records both views shows that difference explicitly."
The model does not support this. An interface carries one stage. To show both, a producer would
declare `svc-oidc` twice, and P1, P4 and the objective would then count two interfaces where
there is one.

**How to manage it.** Write one document per stage and join the documents. Do not merge them.
This is the pattern decision 0020 uses for vulnerability statements. It needs one addition: a
reference from an interface to the same logical interface in another document, such as a
`correspondsTo` BOM-Link (`urn:cdx:<serial>/<version>#<bom-ref>`). A plain `bom-ref` is not
enough, because it is local to its document. The same reference allows the I9 inheritance in
stage 4.

This approach has two further effects.

- When every document has a single stage, I8 can map to the native CycloneDX
  `metadata.lifecycles[].phase`: `design`, `build`, `operations` and `discovery`. That resolves
  the row that is still marked unresolved in the mapping.
- The sentence on the Lifecycle page should then say "two CBOMs, joined".

The lifecycle-aware attribute model can stay parked. Keycloak does not need it once the join
exists. A revival case would be a consumer who needs both stages inside one document and cannot
accept two.

## Smaller items

- **The cbomgen input.** The cprofile's `lifecycle_stage` applies to the whole document and uses
  `development`, `build`, `release`, `deployment` and `decommission`. Its `build` and `release`
  values map to `implemented`, and `deployment` maps to `configured`. No value maps to
  `observed`, and `development` is not the same as `intended`. The Keycloak cprofile says
  `release` and contains deployment values (plan §1, item 6). Send this to the cbomgen
  maintainers with the other §1 findings.
- **Decommissioning.** The four stages have nothing for retirement. For Keycloak, realm private
  keys are stored in plaintext in the database (#39933), so database backups keep them after the
  service is retired. CycloneDX has a `decommission` phase. This is outside the current question,
  and it would need a named issue if anyone wants it.

## Order of work

1. Settle the `implemented` values (`deployment-defined`, `peer-defined`) and the definition of a
   default as present state, and correct the Keycloak example. This affects the worked example
   now.
2. Decide between Option A and Option B for `configured` and `observed`. Option B is decided
   together with the Operation group in 0023.
3. Add the cross-document interface reference. Both the observed I9 fix and the join depend on
   it.
4. Write the decision record that removes `intended` from the disclosure baseline.
5. Write evaluator support for stage-conditional constraints. Items 1 and 3 need it.

## Sources

- Keycloak, Configuring the management interface: https://www.keycloak.org/server/management-interface
- Keycloak, Configuring distributed caches: https://www.keycloak.org/server/caching
- Keycloak, Using a reverse proxy: https://www.keycloak.org/server/reverseproxy
- Keycloak issue #39933, encrypt key provider material: https://github.com/keycloak/keycloak/issues/39933
- PostgreSQL, `pg_stat_ssl`: https://www.postgresql.org/docs/current/monitoring-stats.html
- CycloneDX 1.7, `metadata.lifecycles`: https://cyclonedx.org/docs/1.7/json/#metadata_lifecycles
