# CBOM Profile — Interface Disclosure Baseline (Example v0.9)

> **Status:** Illustrative early-concept artifact for the PKIC CBOM Profiles Working Group.
> Not a normative deliverable. The machine-readable rules are in
> `profile-interface-disclosure.rules.json`, and that file is normative for the example. The
> CycloneDX 2.0 perspective in `perspectives/perspective-interface-disclosure.cdx.json` is
> generated from the rules and is informative only.
>
> **Carrier.** The target is CycloneDX 2.0. Until Ecma ratifies the release (expected December
> 2026), the target is pinned to the CycloneDX/specification branch `2.0-dev` at commit `76f185c`
> (23 October 2026). The pinned schema is in `tests/schemas/cyclonedx-2.0/`. The validator reads
> CycloneDX 1.6 and 1.7 documents as legacy and flags them, because the tools that produce CBOMs
> today emit 1.x. It refuses anything below 1.6. `cdx17_to_20.py` converts a 1.6 or 1.7 CBOM to
> 2.0. `versioning-and-legacy-cboms.md` describes the treatment of older carrier versions.
>
> **Words.** CycloneDX 2.0 has its own `profiles` element and its own blueprint "interface". Neither
> is the concept the PKIC work uses. Where confusion is possible, the methodology says **PKIC CBOM
> profile** and **cryptographic interface**.
>
> The choices made in v0.9 are recorded in decision 0025
> (`https://github.com/pkic/cbom/blob/main/decisions/0025-baseline-consolidation.md`). Each is provisional and can be reopened on
> its own.

## 1. Revision rationale

An earlier draft of this example bound a rule to a specific product and interface
(`interfaceId MUST equal "nginx-https"`). That form is wrong for a profile. A profile must be
**product-independent and instance-independent**. It states *structural* and *attribute*
requirements that any conforming subject satisfies, and it names no particular product or
interface.

The same early draft carried a `pqcPosture` attribute. That attribute is a judgement, not a fact.
The criteria behind it change while the product does not, so the same disclosed values would
yield a different answer next year. The working group removed it before v0.1. The profile records
the algorithms that the judgement is derived from, and leaves the judgement to external versioned
policy. Decision 0002 records the choice, and the Policy Evaluation section develops it. Neither
correction appears in the changelog in §8. No one authored a document against that draft, and a
changelog records changes between published versions.

The profile therefore does not require an interface with a particular name. It states that:

- a document MUST declare its cryptographic interfaces;
- among them there MUST be a management or configuration interface, or a stated reason why there
  is none;
- every declared interface MUST disclose a defined set of attributes; and
- a document MUST point to the context it does not carry, such as its companion SBOM.

The worked example is **Keycloak 26.7.3**, an open-source identity and access management server.
Keycloak is only the example subject. The same profile applies without change to any product or
deployment that applies cryptography at its boundary, whether over TLS, SSH, IPsec or at the
application layer.

## 2. Vocabulary

- **Cryptographic interface (edge)** — a logical boundary at which cryptography is applied between
  parties, such as a TLS session, an SSH session, an IPsec tunnel, or a signed token. An interface
  is not a port (§2.2). The term is product-independent.
- **Endpoint (node)** — a party to an interface (`client`/`server`, `initiator`/`responder`,
  `issuer`/`relying-party`).
- **`interfaceType`** — the role of an interface, drawn from a controlled vocabulary. It is not an
  instance name. The vocabulary is
  `management` · `service` · `interconnect` · `peer` · `storage`.
  The value that matters most to the baseline is `management`: the interface through which an
  administrator configures or operates the subject.
- **Subject type** — what one document describes: a `product` as built, or a `deployment` of it
  (§4).
- **Lifecycle stage** — where the facts in a document come from: `implemented` (the product as
  built), `configured` (what a deployment permits) or `observed` (what a deployment was seen to
  do). One document has one stage.

The profile is protocol-neutral. It uses the terms `encryption`, `keyExchange` and
`authentication` rather than the TLS-specific term "cipher suite". The same rules then apply to a
TLS service interface, to an SSH management interface and to a token interface.

### 2.1 Taxonomy of cryptographic relationships

A relationship is more general than a network connection, and the profile has to state which
kinds it covers. Relationships vary along four dimensions: the number of parties, whether those
parties exist at the same time, what passes between them, and how far the protection extends.
The table places the worked examples from the relationship model against those dimensions. The
model page ([model.html](model.html)) describes each one with a diagram.

| Relationship | Parties | Simultaneous | What passes | Span | Property it exercises |
|---|---|---|---|---|---|
| TLS session to a service | 2 | yes | data in transit | single hop | the base case |
| Termination at a proxy or CDN | 2 per leg | yes | data in transit | chained, multi-hop | one apparent connection is several relationships |
| Encrypted backup or archive | 2 | no | data at rest | single | parties separated in time; lifetime is the retention period |
| Code or firmware signing | 2 | no | nothing directly; a signed artifact is carried | single | parties never interact; the verifier sets the ceiling |
| Message-level security inside transport | 2 per layer | yes | data in transit | layered, overlapping | relationships overlap rather than partition the path |
| IPsec mesh or operator interconnect | 2 per tunnel, many tunnels | yes | data in transit | single hop, repeated | one asset supports many relationships with differing posture |
| Negotiated fallback between capable peers | 2 | yes | data in transit | single hop | capability is not the negotiated outcome |
| Modern gateway to legacy controller | 2 | yes | data in transit | single hop | the less capable party fixes the posture |
| Application to HSM or TEE | 2 | yes | operation requests; key material is confined | local, crosses a hardware boundary | a relationship that transfers no protected data |
| Broadcast, multicast, or group messaging | n | yes | data in transit | one to many | not represented in v1; see below |
| Signed message verified by a closed membership | n | no | a signed message is carried | one to many | not represented in v1; the upper limit belongs to the membership rather than to either party. Recorded as Q46 |

The Keycloak example exercises several rows. The operator's ingress terminates TLS and forwards
plain HTTP to Keycloak, which is the proxy row. Signed OIDC tokens ride inside TLS, which is the
message-level row. The ingress permits a hybrid key exchange while 29% of sessions still negotiate
a classical one, which is the negotiated-fallback row.

**Scope for this version.** The profile applies to pairwise relationships. Group relationships,
in the broadcast row, are out of scope for v1. The working group records them as a known limitation
and does not approximate them. Decomposing a group into pairwise relationships loses the shared
key and the membership over which it applies. A future revision should address them together with
the first-class attributed-edge model.

The dimensions also show where a profile written for one sector may need different rules. A
profile concerned with data at rest will care about the retention period, which does not arise
for a session. A profile concerned with signing will care about the verifier population, which has
no counterpart in a transport profile.

### 2.2 An interface is a logical boundary, not a port

Two layers of cryptography can protect traffic on one port. Each layer is then its own interface,
and the producer describes each in its own terms. The usual case is application-layer signing or
encryption carried over TLS, such as signed OIDC tokens or SAML assertions on an HTTPS listener:

- The TLS layer is one interface, with protocol `TLS`.
- The token layer is another interface, with protocol `OIDC` or `SAML`. Its `authentication` names
  the token signature algorithm, and its `keyExchange` names how a token encryption key reaches the
  recipient.

The two layers migrate on different timetables and depend on different standards. For Keycloak,
the TLS layer waits on the Java runtime, and the token layer waits on a JOSE standard. One entry
could not state both. Decision 0022 (K2) records this reading.

An application-layer interface counts as an interface in two cases: when it applies cryptography
of its own, or when anyone can reach it without transport protection. One that only rides a
declared transport and applies nothing of its own belongs to that transport's interface, and the
producer does not count it separately. Without this rule, interface counts and the coverage
statement would vary with how many services a producer chose to list (decision 0022, K7).
Keycloak's health and metrics endpoints are an example: they apply no cryptography of their own,
so the management TLS listener carries them.

In CycloneDX 2.0, an application-layer interface is a component of `type: "service"`. CycloneDX's
protocol types cover security protocols only, such as TLS, SSH and IPsec, so OIDC, SAML, an
administrative API and plain HTTP are services. The mapping (`mapping-cyclonedx-spdx.md`) records
how the two layers and the carrying relation are represented.

## 3. Two directions of use

| Direction | Party | Question |
|---|---|---|
| **Specification** | The party that writes the CBOM | Which interfaces, attributes and pointers must the document declare? |
| **Conformance checklist** | The consumer or CI gate | Did the document declare its interfaces, including a management interface, each fully described, and does it point to its context? |

## 4. Subjects and stages

### 4.1 Two subject types

The baseline serves two subject types. Its rules describe an interface the same way whether a
vendor reports what a product does as built or an operator reports what a deployment does.

| Subject type | Who writes it | Stages | Subject identifier (P3) |
|---|---|---|---|
| `product` | The vendor writes the **product record** | `implemented` | A Package URL, for example `pkg:oci/keycloak?repository_url=quay.io/keycloak/keycloak&tag=26.7.3` |
| `deployment` | The operator writes **deployment records** | `configured`, `observed` | A tag URI (RFC 4151), for example `tag:example.org,2026:deployment/sso-prod` |

A deployment has no Package URL. Anyone who controls a domain name can mint a tag URI without
registering anything, which suits an operator naming its own deployments. A URN would need a
registered namespace. Two records of the same deployment must use the same identifier.

The document declares its subject type (P5) with the property `pkic:profile:subjectType`. A
consumer cannot tell from the content alone whether a record describes a product or a deployment,
and the two answer different questions.

### 4.2 One stage per document

A document has one lifecycle stage (P6). The document carries it natively in
`metadata.lifecycles`:

| CycloneDX lifecycle phase | Stage | Accepted by the baseline |
|---|---|---|
| `build` | `implemented` | yes |
| `operations` | `configured` | yes |
| `discovery` | `observed` | yes |
| `design` | `intended` | no |

An interface may also carry its own `lifecycleStage`. Where it does, the value must agree with the
document's stage. A vendor's build record and an operator's scan come from different parties at
different times, and each answers a different question. Mixing stages in one document would make
an interface count meaningless, because one boundary would appear twice. It would also let a
producer fill a gap at one stage with a value from another.

The meaning of a present-state value depends on the stage:

| Stage | A present-state value such as `keyExchange` means |
|---|---|
| `implemented` | the product's default as shipped |
| `configured` | the set the deployment permits |
| `observed` | the set seen during the observation window |

### 4.3 Why `intended` is not accepted

The baseline does not accept `intended`. A design intention answers nothing about deployed
interfaces, and deployed interfaces are the baseline's decision. Each kind of intention has
another home:

- A vendor's intention is a capability status under the PQC migration profile (`pqc-migration#G1`).
  For example, Keycloak's ML-DSA token signing is `committed`, with roadmap issue #43690.
- An operator's intention is a requirement, held in a policy or a tender.
- A design document is context, and a document points to it under R6.

The entry profile, Interface Enumeration v0.3, still accepts `intended`, because a first
inventory takes whatever the producer can report.

## 5. Rules

Requirement keywords follow BCP 14 (MUST / SHOULD / MAY). The baseline uses three kinds of rule:

- product-level rules (`P`), which constrain the document and its set of interfaces;
- per-interface rules (`I`), which apply to each declared interface; and
- reference rules (`R`), which require a pointer to context the document does not carry.

The baseline uses no group rule, because it reports present state and present state has one
answer per attribute. The migration profile derived from it uses one, for capability per
cryptographic purpose.

Rule identifiers are local to the profile and are cited against its tag: `P1` below is
`interface-disclosure#P1` in a report or a claim. The letter says how often the evaluator applies
the rule: `P` once per document, `I` once per declared interface, and `R` once per document or
once per interface, as the rule's `at` field says. A profile derived from the baseline numbers its
own rules from `P1`, `I1` and `R1` in its own space. See decision 0011.

### 5.1 Product-level rules

| # | Requirement | Level | Constraint |
|---|---|---|---|
| P1 | The document declares at least one cryptographic interface | **MUST** | `minInterfaces: 1` |
| P2 | The document declares at least one interface of type `management`, **or states why it has none** | **MUST** | `minInterfacesOfType: {management, 1}`, `orDeclaredAbsent`, `orCitedDeclares` |
| P3 | The document identifies the subject it describes | **MUST** | `subjectIdentified: {product: pkg:, deployment: tag:}` |
| P4 | The document states how complete its declared interface set is | **MUST** | `productAttribute: coverage` (`all`, `all-external`, `partial`) |
| P5 | The document declares its subject type, from the types the profile accepts | **MUST** | `subjectDeclared` |
| P6 | The document declares one lifecycle stage, and every interface reports that stage | **MUST** | `singleStage` |

P2 exists to catch omission. The administrative interface is the one producers most often leave
out. A producer satisfies P2 by declaring a management interface, or by stating why there is none
(`no-configuration-surface`, `configured-out-of-band` or `not-applicable-to-subject`). Silence
fails.

Two further routes apply only to an `observed` record:

- The observer could not reach the management interface, but the record cites a configured record
  that declares one. P2 is then satisfied. The omission stays visible through the join, as an
  interface with no observed counterpart.
- The observer has no configured record to cite, as with an outside assessor. The observer states
  `not-reached`. The evaluator accepts that reason only with coverage `partial`.

The conformance report says which route the document took.

P3 and P4 make the document usable as a record of one subject, not only as a description. Without
P3, the consumer cannot match the record to a deployment or compare it with last quarter's record.
Without P4, a missing interface cannot be interpreted. The interface might not exist, or the
producer might have chosen not to list it.

### 5.2 Per-interface rules

Attribute names follow the methodology's naming conventions. A bare name denotes present state,
and a `Supported` suffix denotes declared capability. The baseline records present state only, so
no attribute here carries the suffix. A profile requiring capability, such as the PQC migration
profile, reuses these names unchanged and adds the suffixed forms alongside them.

| # | Attribute | Level | Allowed values / notes |
|---|---|---|---|
| I1 | `protocol` | **MUST** | present, for example `TLS`, `SSH`, `IPsec`, `OIDC`, `SAML`. Not required of a storage interface |
| I2 | `protocolVersion` | **MUST** | present. Not required of a storage interface |
| I3 | `keyExchange` | **MUST** | registry algorithm identifier, or a literal (§5.3). Not required of a storage interface |
| I4 | `encryption` | **MUST** | bulk or AEAD algorithm identifier, or a literal (§5.3) |
| I5 | `authentication` | **MUST** | signature algorithm that proves the sender (certificate signature, host key, token signature), or a literal (§5.3). Not required of a storage interface |
| I6 | `endpointRoles` | **MUST** | at least two endpoints declared. Not required of a storage interface |
| I7 | `interfaceType` | **MUST** | from the vocabulary in §2 |
| I8 | `lifecycleStage` | **MUST** | one of `implemented` \| `configured` \| `observed`. The effective value is the interface's own stage or, where it has none, the document's stage |
| I9 | `implementationPurl` | **MUST** | `pkg:` Package URL of the implementing library. Withholdable (§5.4): a `withheld` marker satisfies the rule, silent omission does not |
| I10 | `keyWrapping` | **MUST** on a storage interface | the algorithm that protects the data keys, for example RSA-OAEP over an AES key, or `none` |
| I11 | `defaultState` | SHOULD, at `implemented` | `enabled` or `disabled`: whether the interface is active in the product's default configuration |

A storage interface is data at rest. It has no protocol, peer or handshake, so I1, I2, I3, I5 and
I6 do not apply to it. I10 stands in for I3, because wrapping keys at rest is a different job from
establishing keys between parties. I4 and I9 apply to storage unchanged. A network path to remote
storage, such as a backup over TLS, is a separate service or interconnect interface, and it owes
the channel rules there (decision 0022).

I11 matters because some interfaces exist in a product and are off by default. Keycloak's
plaintext HTTP listener is one. Declared without `defaultState`, it reads as an active plaintext
interface. Left out, it hides the interface that becomes the plaintext hop behind a
TLS-terminating proxy. I11 applies only at `implemented`. In a deployment record, every declared
interface is active, and a product interface with no counterpart is not.

A document conforms if and only if every product-level MUST rule holds, every declared interface
satisfies every per-interface MUST rule, and every applicable reference rule at MUST level holds.
`interfaceId` is an instance label that the producer chooses. The profile does not constrain its
value.

Derived evaluations such as post-quantum posture are deliberately not profile attributes. An
external policy computes them from the disclosed facts, because the criteria they depend on change
over time. See the Policy Evaluation section.

### 5.3 Literal values

I3, I4 and I5 accept three literal values in place of an algorithm. A literal is a value, not a
disclosure marker. It stands alone: a producer does not combine it with an algorithm in one value.

| Literal | Meaning | Accepted at | Keycloak example |
|---|---|---|---|
| `none` | The interface applies no algorithm for this job | any stage | Token encryption is off by default, so the OIDC interface declares `keyExchange` and `encryption` as `none` |
| `deployment-defined` | The product does not fix the value. The operator chooses it | `implemented` only | The server certificate on the HTTPS listener is operator-supplied, so `authentication` is `deployment-defined` |
| `peer-defined` | The other endpoint decides the value, or the product negotiates it with that endpoint | `implemented` only | On the connection Keycloak opens to its database, the database chooses the group and presents the certificate |

`none` is a claim about the product, and a consumer can check it like any other value. It differs
from `unknown`, which reports that the producer does not know, and from `withheld`, which reports
that the producer declines to say.

`deployment-defined` and `peer-defined` are accepted only at `implemented`. At `configured` or
`observed`, the producer holds the answer and must give it. Without the two literals, a truthful
build record of Keycloak failed I5 on 7 of its 13 interfaces. Decision 0012 states the principle:
a rule that no legitimate subject can satisfy honestly is wrong, not strict.

A product that declares `deployment-defined` must also tell the operator where to make the choice.
Reference rule R5 requires that pointer.

### 5.4 Disclosure states

An attribute that carries no value may do so for different reasons, and a consumer needs to tell
them apart. Following the 2026 SBOM minimum elements, a producer states whether missing
information is unknown to it or is being withheld. The profile recognises four outcomes per
attribute:

| Outcome | Meaning | Effect on a MUST rule | Effect on a SHOULD rule |
|---|---|---|---|
| value | The producer supplied a value, and the evaluator checks it against the constraint | passes if valid | passes if valid |
| withheld | The producer holds the information and declines to publish it | passes only if the rule is marked `withholdable` | passes only if the rule is marked `withholdable` |
| unknown | The producer does not have the information | fails, reported as unknown rather than absent | reported, does not fail conformance |
| undeclared | The producer supplied neither a value nor a marker | fails | reported, does not fail conformance |

`unknown` never satisfies a MUST rule, at any stage, because the requirement has not been met. The
evaluator still reports it separately from `undeclared`, since the two carry different
information. The first records a limit of the producing process. The second records that the
producer never addressed the question. A record with gaps conforms one depth down, at the entry
profile, instead (decision 0019).

In the baseline only I9 (`implementationPurl`) is withholdable. A producer may reasonably decline
to publish the implementing library and still meet part of the objective. The objective's own
note says what that costs: a withheld library removes library-level vulnerability matching, which
is the use the baseline is built for. The verdict remains "conforms", and the report shows the
withholding. The PQC migration and procurement profiles make I9 non-withholdable.

The combination of level and withholdability decides whether the disclosure model affects a
verdict. Withholding can only change an outcome on a MUST rule, because a SHOULD rule does not
decide conformance in the first place. Until v0.3 the baseline held I9 at SHOULD while marking it
withholdable, so the flag had no effect and the model was visible only in the report. I9 is now a
withholdable MUST, which is the combination the model exists for. The producer must address the
attribute. It may answer either with a value or with a declared refusal, and a consumer can tell
both apart from a document that never addressed it.

Markers are properties under `pkic:profile:disclosure:`, because neither CycloneDX nor SPDX
provides a native field for them. The mapping records the convention.

### 5.5 Reference rules

A reference rule requires the document to point to an artefact that it does not carry. Decision
0020 established the principle for vulnerability statements: a CBOM and the context around it are
joined, not merged. A CBOM records facts that change when the product or deployment changes.
Context that changes on another trigger, or that another party holds, stays outside.

The profile defines each **context kind** in `contextKinds`. For each kind it names the CycloneDX
`externalReferences` types that can carry it, and its form:

- `document`: a fixed artefact, bound by a hash;
- `endpoint`: a feed or API whose content changes, which names its access protocol; or
- `document-or-endpoint`: either of the two.

| # | Context kind | At | Level | Applies to | Carrier types | Form | Notes |
|---|---|---|---|---|---|---|---|
| R1 | `sbom` | document | **MUST** | product | `bom` | document, hash required | The SBOM of the same subject, as a BOM-Link with a hash. It places a library named under I9 in the dependency tree |
| R2 | `vulnerability-statements` | document | **MUST** | product | `vulnerability-assertion`, `exploitability-statement` | document or endpoint; hash required for a document | Where the producer publishes VEX, CSAF VEX or exploitability statements. A producer that publishes none states `not-published`. Silence fails |
| R3 | `advisories` | document | SHOULD | product | `advisories` | endpoint | Where advisories about the subject and its libraries appear, with access protocol `web-page`, `csaf-provider`, `osv-api` or `ghsa-api` |
| R4 | `security-contact` | document | SHOULD | product | `security-contact`, `rfc-9116` | endpoint | Where to report a weakness or ask for a fuller disclosure |
| R5 | `configuration-guidance` | interface | **MUST** | any interface where I3, I4 or I5 is `deployment-defined` | `documentation`, `configuration` | endpoint | Where the operator makes the choice the product leaves open |
| R6 | `design-intent` | document | MAY | any | `threat-model`, `adversary-model`, `documentation` | document or endpoint | A threat model or design document. Design intention lives here now that `intended` is not an accepted stage |

In CycloneDX, each pointer is an external reference with the property `pkic:profile:context`,
which names the kind. The property is needed because two kinds can share one reference type. An
endpoint also carries `pkic:profile:accessProtocol`. CycloneDX 2.0 allows properties on external
references. A stated absence is a subject property, `pkic:profile:contextAbsent:<kind>`, with a
value from `not-published` or `not-applicable-to-subject`.

Two principles govern every reference rule:

- **Conformance checks the pointer, never the target.** The evaluator checks that the pointer is
  present and well formed. Where the evaluator holds the target, it also checks the hash. It never
  evaluates the target's content.
- **Direction follows time.** A record points to artefacts that exist when the producer writes it:
  its companion SBOM, the configuration it was read from, the evidence it was built on. It also
  points to the places where later statements will appear, such as a VEX feed or an advisory API.
  A judgement made afterwards, such as a conformance claim or a policy result, points to the
  record by digest. A record never points to a judgement about itself.

For Keycloak, the product record points to its SBOM by BOM-Link and hash (R1). It states
`not-published` for vulnerability statements, because upstream Keycloak publishes none (R2). It
names the GitHub advisory page as a `web-page` and the OSV API as an `osv-api` endpoint (R3). It
points to the Keycloak security policy (R4). The HTTPS listener points to the Keycloak guide for setting the
server certificate, and the management listener points to the guide for the management interface (R5).

The vulnerability join then runs end to end. The consumer takes library Package URLs from I9,
queries the advisory endpoint under R3, and reads the vendor's affected and not-affected
statements from the source under R2. The CBOM itself carries no vulnerability data.

### 5.6 Scope

The profile declares a `scope` object that states what it describes and what it accepts. The
members form one boundary, and the author decides them together.

| Member | Baseline value | Why |
|---|---|---|
| `orientation` | `inventory` | The baseline reports what interfaces do, not what they could do. Under C12 it may not require any forward-looking attribute. This keeps a present-state name and a capability name from being read as interchangeable across profiles that share a vocabulary. |
| `subjectTypes` | `product`, `deployment` | A set, which replaced the single `subjectType` in v0.9. A derived profile narrows it to a subset, as it narrows the stages. The PQC migration and procurement profiles accept `product` only. The deployment profile accepts `deployment` only. |
| `relationshipTypes` | `interface` | Every rule constrains a cryptographic interface. The checker compares the declaration with the rules instead of trusting it, because a scope statement maintained by hand drifts from what the rules say. |
| `lifecycleStages` | `implemented`, `configured`, `observed` | An acceptance constraint, in the same sense as `appliesTo` for carrier versions. An interface that reports a stage outside the set fails I8. |

A derived profile may narrow `subjectTypes` and `lifecycleStages`. It may not widen them, for the
same reason it may not relax a rule. The PQC migration profile accepts only `implemented`, because
a supplier's migration record describes what the shipped product can do. The deployment profile
accepts only `configured` and `observed`. A deployment record that repeated a vendor's build facts
would add nothing, so it cites the vendor's record instead.

## 6. Expected declaration

The Keycloak 26.7.3 container image, at its defaults, declares 13 interfaces. The subject is the
image, identified by an OCI Package URL, because the image fixes the cryptographic runtime: OpenJDK
21 from Red Hat UBI 9. Coverage is `all-external`.

| Interface | `interfaceType` | Protocol | Default state | Notes |
|---|---|---|---|---|
| TLS on the main listener (port 8443) | service | TLS 1.3 | enabled | Key exchange from the JDK 21 defaults, X25519 first. `authentication` is `deployment-defined`: the operator supplies the server certificate. Points to configuration guidance (R5) |
| TLS on the management listener (port 9000) | management | TLS 1.3 | disabled | Inherits the main listener's scheme. Health and metrics are off by default. Points to configuration guidance (R5) |
| TLS to the database | interconnect | TLS 1.3 | enabled | `keyExchange`, `encryption` and `authentication` are `peer-defined` |
| TLS to the directory (LDAPS or StartTLS) | interconnect | TLS 1.3 | disabled | `peer-defined` |
| TLS to external identity providers | interconnect | TLS 1.3 | disabled | `peer-defined` |
| TLS to the mail server (StartTLS) | interconnect | TLS 1.3 | disabled | `peer-defined` |
| Mutual TLS between cluster nodes | peer | TLS 1.3 | enabled | A product-generated RSA-2048 key, rotated every 30 days. The operator cannot change the key type |
| OIDC and OAuth 2.0 token issuance (JOSE) | service | OIDC 1.0 | enabled | Realm signing RS256 by default. Token encryption is off by default, so `keyExchange` and `encryption` are `none` |
| SAML 2.0 assertions (XML Signature) | service | SAML 2.0 | enabled | RSA-SHA256 signatures. `keyExchange` and `encryption` are `none` |
| HTTP listener (plaintext) | service | HTTP 1.1 | disabled | `none` for every algorithm. Off by default. It is the normal configuration behind a TLS-terminating proxy |
| Admin REST API and Admin Console (bearer tokens) | management | Admin REST (OAuth 2.0 bearer) | enabled | Carried over the HTTPS listener. Bearer tokens signed by the master realm |
| Brokered token verification (external OIDC and SAML providers) | interconnect | OIDC 1.0 | disabled | `authentication` is `peer-defined`: the external provider chooses the signature algorithm |
| Realm and cluster key persistence (database) | storage | – | enabled | Key material held in the database in plaintext (Keycloak issue #39933): `encryption` is `none` and `keyWrapping` is `none` |

Every interface carries its attributes as §5.2 requires. Two management interfaces satisfy P2. The
OIDC, SAML, Admin API and brokered-token interfaces are CycloneDX components of type `service`
(§2.2). Each applies a signature of its own, so each counts as an interface. A TLS interface
carries each of them.

The facts behind several entries come from Keycloak's own documentation and issue tracker. ML-DSA
token signing is committed upstream (issue #43690). It is blocked because the JOSE `AKP` key type
is still an Internet-Draft. The baseline does not record that fact. It is a capability status, and
the PQC migration profile carries it.

## 7. Example documents

All examples are in `examples/` and use CycloneDX 2.0, except the two under `examples/legacy/`. A
script, `tools/build_keycloak_examples.py`, generates them, so citations and hashes stay
consistent.

| File | What it shows | Verdict against the baseline |
|---|---|---|
| `cbom-keycloak-product.cdx.json` | The vendor's build record of the Keycloak 26.7.3 image, 13 interfaces | Conforms. It also conforms to the entry, PQC migration, extended and procurement profiles |
| `legacy/cbom-keycloak-product-1.7.cdx.json` | The same facts in CycloneDX 1.7 | Conforms, flagged legacy |
| `cbom-keycloak-product-fail-R5.cdx.json` | The HTTPS listener declares `deployment-defined` with no configuration-guidance pointer | Fails R5 only |
| `cbom-keycloak-product-fail-P2.cdx.json` | The management interfaces are left out, with no reason | Fails P2. Conforms to the entry profile |
| `cbom-keycloak-product-disclosure-states.cdx.json` | The four disclosure outcomes | Fails I5 on the cluster interface (`unknown`) and I4 on the SAML interface (undeclared). The withheld library is permitted. Conforms to the entry profile |
| `cbom-keycloak-product-intended.cdx.json` | A design record for Keycloak 27.0 with ML-DSA-65 | Fails I8 on every interface, and fails I3–I5 where it repeats build-time literals. Conforms to the entry profile |
| `legacy/cbom-keycloak-scanner-output.cdx.json` | Untargeted scanner output, CycloneDX 1.7 | Fails P1–P6. It also fails the entry profile |
| `cbom-keycloak-deployment-configured.cdx.json` | The configured record of an illustrative operator, Example Org, at `sso.example.org`. TLS ends at an nginx/OpenSSL 3.5 ingress, and Keycloak runs with `http-enabled` behind it | Conforms. It also conforms to the deployment profile |
| `cbom-keycloak-deployment-configured-fail-literal.cdx.json` | `peer-defined` kept at `configured` | Fails I3, I4 and I5 on the database connection |
| `cbom-keycloak-deployment-observed.cdx.json` | The deployment as observed from 18 to 25 October 2026, with an observation method per interface | Conforms. It also conforms to the deployment profile |
| `cbom-keycloak-deployment-observed-fail-unknown.cdx.json` | The group is `unknown`, because the observer used `pg_stat_ssl` only | Fails I3. Conforms to the entry profile |
| `cbom-keycloak-deployment-observed-outside.cdx.json` | An outside assessor who did not reach the management interface | P2 passes through `not-reached`. Fails I9 on the ingress, because the library is not visible from outside. Conforms to the entry profile |

Four further examples conform to the baseline and fail one rule of a derived profile:

- `cbom-keycloak-product-fail-pqc-I12.cdx.json` fails `pqc-migration#I12`, because the storage
  key-wrapping capability is missing.
- `cbom-keycloak-product-fail-ext-I3.cdx.json` fails `pqc-migration-extended#I3`, because the key
  types the Admin API can generate are missing.
- `cbom-keycloak-product-fail-procurement-P5.cdx.json` fails `procurement#P5`, because the storage
  interface is missing.
- `cbom-keycloak-deployment-observed-fail-P1.cdx.json` fails `deployment-disclosure#P1`, because
  the configured record it cites has changed and the hash no longer matches.

To evaluate a document:

```
python validate_cbom.py examples/cbom-keycloak-product.cdx.json profile-interface-disclosure.rules.json
```

A deployment record cites other records. Supply them with `--with`, so that the evaluator can
check the citations and resolve inherited facts:

```
python validate_cbom.py examples/cbom-keycloak-deployment-observed.cdx.json \
    profile-interface-disclosure.rules.json \
    --with examples/cbom-keycloak-deployment-configured.cdx.json \
    --with examples/cbom-keycloak-product.cdx.json
```

Without `--with`, the evaluator reports an inherited value as unresolved (`OPEN`), not as failed.
`compare_stages.py` lays the product, configured and observed records side by side. The demo page
(`demo.html`) shows reports that the validator generated.

## 8. Changelog

The Versioning section asks profile authors to publish a changelog and to say which changes
oblige a producer to do further work. The changelog is that record for the example, written to
the form the methodology proposes.

A change is **tightening** if a document that conformed to the previous version may no longer
conform, **relaxing** if the reverse, and **editorial** if conformance is unaffected. Version
numbers are the profile's own and are independent of the carrier version.

### v0.2 — 2026-08-07

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added the disclosure state model of §5.4, with the `pkic:profile:disclosure:` marker prefix and a `withholdable` flag on every rule | tightening | A document that omitted an attribute silently now fails as `undeclared`; supplying a marker restores conformance |
| Added rule I9 `implementationPurl` at SHOULD, withholdable | none | SHOULD rules are reported, not enforced |
| Recorded `appliesTo` as CycloneDX `min: 1.6`, `tested: 1.7` | editorial | Documents at 1.6 are evaluated and flagged legacy rather than refused |

### v0.3 — 2026-08-09

| Change | Kind | Effect on an existing document |
|---|---|---|
| Raised I9 `implementationPurl` from SHOULD to MUST, keeping it withholdable | tightening | A document omitting the attribute in silence no longer conforms. Adding either a value or a `withheld` marker restores conformance |
| Stated `withholdable` explicitly on every rule | editorial | None. An absent flag was already treated as false; the value is now readable from the profile rather than inferred from a validator's default |

The first change exists for the reason §5.4 describes. No rule in either example profile combined
MUST with withholdability, and that is the only combination in which withholding alters a verdict.
The profile therefore stated the disclosure model without applying it in any rule.

The derived PQC migration profile, now v0.8, pins baseline v0.9. It tightens
`interface-disclosure#I9` by removing its withholdability, since the level is already MUST. Under
decision 0004 that tightening is permitted. A later baseline revision that relaxed I9 would put
the derived profile in conflict, which is why the derived profile pins its base by version.

### v0.4 — 2026-08-21

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added the `scope` object: `subjectType`, `relationshipTypes`, and the accepted `lifecycleStages` | editorial | None. At the time the baseline accepted all four stages, so no document that conformed to v0.3 stopped conforming. The field's effect was on profiles derived from the baseline, which could now narrow the set |
| Added `objective.decisionOptions`, listing the actions the consumer chooses between | editorial | None. The decision text was unchanged; stating the options is what makes the action-choice test in Method step 1 checkable rather than a matter of review |

Both changes were editorial here and neither was elsewhere: the migration profile's v0.2 narrowed
the accepted stages, and that was a tightening. The pattern is worth noting when reading a
changelog. A field can arrive without effect in one profile and immediately change verdicts in
another that derives from it. Recorded as decision 0008.

### v0.5 — 2026-08-21

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added `scope.orientation`, declared as `inventory` | editorial | None. The constraint falls on the profile, not the document: an inventory profile may not require forward-looking attributes, checked as C12 |

The value of the field is again in what it permits elsewhere. The migration profile declares
`both`, and C12 then obliges it to require the present-state attribute behind every capability
attribute it asks for. It already did, by inheriting I2, I3 and I5 from the baseline, but nothing
had required it to. A migration profile written standalone could have reported capability alone.
Recorded as decision 0009, which reverses the clause in 0008 that rejected orientation.

### v0.6 — 2026-08-21

| Change | Kind | Effect on an existing document |
|---|---|---|
| Rewrote the objective. The previous decision was whether the cryptography was "disclosed in enough detail", which is a decision about the document rather than about the product | editorial | None. No rule changes. The decision is now the consumer's actual job: determining which deployed interfaces a published weakness affects, and what has changed since the last record. Every rule traces to it |
| Added **P3**: the document identifies the subject it describes, in the form the profile names | tightening | A document that did not carry a subject identifier no longer conforms. A name and a version are not sufficient: two documents about the same product have to agree on the identifier for either to be usable as a record |
| Added **P4**: the product states how complete its declared interface set is. Moved down from the migration profile | tightening | A document carrying no completeness statement no longer conforms. Settles Q34 |
| Revised **P2**: satisfied by declaring a management interface **or** by stating why there is none | relaxing, deliberately | A subject with no administrative surface, such as a library, a hardware token or an embedded component, previously failed while hiding nothing. It can now say so. Silence still fails: a stated absence is a fact, and this is the disclosure model applied to structure |
| Declared `identifierSchemes` and referenced them from I1, I3, I4, I5, I9 and P3 | editorial | None yet. The profile previously constrained the form of the least contested identifier, the implementing library, and left the most contested free, so free text satisfied `protocol` and `keyExchange`. Naming the required scheme is what makes correlation across suppliers possible. Whether the algorithm scheme should be the CycloneDX registry is Q20 and is unsettled |

The P2 change was the first relaxing change in the baseline's history, and it is worth being
explicit about why it is not a weakening. The rule exists to catch omission. A document that omits
its management interface still fails. What changed is that a subject which genuinely has none can
now say so, instead of being told it does not conform because of a fact about its own design.
Recorded as decision 0012, alongside 0011 for the rule numbering that the two new product rules
made necessary.

### v0.7 — 2026-08-24

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added `profileTag`, `interface-disclosure` | editorial | None. No rule id changes. A rule id is local to the profile that declares it, so the citable form of a rule is now `interface-disclosure#I9` rather than `I9`. The baseline is the base of its family and already used the kind letters `P` and `I`. What changes is that a profile deriving from it may number its own rules from `P1` and `I1` without colliding, at any depth. Recorded as decision 0011 |

### v0.8 — 2026-09-26

| Change | Kind | Effect on an existing document |
|---|---|---|
| I1, I2, I3, I5 and I6 no longer apply to a storage interface | relaxing | Each rule describes a channel: a protocol, its version, a key exchange, a peer authentication and two endpoint roles. A storage interface has none of these, so a product declaring one could not conform honestly. The defence is the one decision 0012 gave for P2: a rule no legitimate subject can satisfy honestly is wrong, not strict. No verdict on an existing example changed, because none declared a storage interface |
| Added **I10** `keyWrapping`, MUST on a storage interface | tightening | A document that declares a storage interface now states how its data keys are protected. See decision 0022 |
| Stated that an interface is a logical boundary, not a port, so two cryptographic layers on one port are two interfaces (K2). Stated that `none` is an accepted value for an algorithm attribute, distinct from the `unknown` and `withheld` markers (K3) | editorial | None. No rule changes: both statements say how existing rules are read. See decision 0022 |
| Stated when an application-layer interface counts as an interface (K7) | editorial | None. The statement sets how P1 and P4 count, and changes no rule |

### v0.9 — 2026-10-25

| Change | Kind | Effect on an existing document |
|---|---|---|
| Removed `intended` from the accepted lifecycle stages | tightening | A document that reports design intention no longer conforms. Design intention is a capability status (`pqc-migration#G1`), a requirement held in policy, or context referenced under R6 |
| `scope.subjectTypes` replaces `subjectType` and accepts `product` and `deployment`. P3 accepts a tag URI (RFC 4151) for a deployment | relaxing | A deployment-scope profile can now extend the baseline, and an operator's record can conform |
| Added **P5** (the document declares its subject type) and **P6** (one lifecycle stage per document) | tightening | A document that does not declare its subject type, or that mixes stages, no longer conforms |
| I3–I5 accept `deployment-defined` and `peer-defined`, at `implemented` only | relaxing | A truthful build record of a product whose certificate or negotiated outcome is decided elsewhere could not conform before. It can now |
| Added **I11** `defaultState` at SHOULD | editorial | None. SHOULD rules are reported, not enforced |
| Added reference rules **R1–R6**. R1, R2 and R5 are MUST | tightening | A product record must now point to its SBOM and to its vulnerability statements, or state that it publishes none. An interface declared `deployment-defined` must point to configuration guidance |
| P2 can be satisfied at `observed` by a management interface declared in a cited configured record, or by the absence reason `not-reached` with coverage `partial` | relaxing | An observer who could not reach the management interface can now produce a conforming record, and the gap stays visible |
| The carrier target is CycloneDX 2.0, pinned to the `2.0-dev` schema of 23 October 2026. CycloneDX 1.6 and 1.7 are read as legacy | editorial | None. 1.6 and 1.7 documents are still evaluated, and the report flags them legacy |
| The conforming example is the Keycloak 26.7.3 product record, replacing the nginx pair | editorial | None. The old examples are deleted |

Decision 0025 records the reasoning for each v0.9 change. Each change was tested on the Keycloak
example, and each can be reopened on its own.

### v0.1 — initial draft

Product-level rules P1 and P2 and per-interface rules I1 to I8. An earlier working draft bound a
rule to a named interface (`interfaceId MUST equal "nginx-https"`). §1 describes the correction to
product-independent form, and decision 0001 records it. The working group did not publish that
draft, and no one authored a document against it.

### Not yet decided

Whether a tightening obliges a grace window before a consumer may reject documents produced
against the previous version, and whether that window belongs to the profile or to the agreement
between the parties. The Versioning section describes dated grace windows; the example does not
yet exercise one.
