# CBOM Profile — Interface Disclosure Baseline (Example v0.5)

> **Status:** Illustrative early-concept artifact for the PKIC CBOM Profiles Working Group.
> Not a normative deliverable. CycloneDX crypto field names are aligned to v1.7 / ECMA-424
> (2nd Edition) and should be validated against the current schema before operational use.
> The treatment of CBOMs authored to older carrier versions is described in
> `versioning-and-legacy-cboms.md`.

## 1. Revision rationale

An earlier draft of this example bound a rule to a specific product and interface
(`interfaceId MUST equal "nginx-https"`). That form is inappropriate for a profile. A profile
must be **product-independent and instance-independent**: it states *structural* and
*attribute* requirements that any conforming product satisfies, without reference to a
particular product or interface.

The same early draft carried a `pqcPosture` attribute. That is a judgement rather than a fact:
the criteria behind it change while the product does not, so the same disclosed values would
yield a different answer next year. It was removed before v0.1 and the profile records the
algorithms the judgement is derived from instead, leaving the judgement to external versioned
policy. Recorded as decision 0002 and developed in the Policy Evaluation section. Neither
correction appears in the changelog in §7, because no document was ever authored against that
draft and a changelog records changes between published versions.

Accordingly, this profile does not state that an interface named `nginx-https` must exist. It
states that:

- a product MUST declare its cryptographic interfaces;
- among them there MUST be a management or configuration interface; and
- every declared interface MUST disclose a defined set of attributes.

nginx is used only as an example subject. The same profile applies without modification to any
product that terminates TLS, SSH, or IPsec.

## 2. Vocabulary

- **Cryptographic relationship / interface (edge)** — a location at which cryptography is
  applied between parties (a TLS session, an SSH session, an IPsec tunnel). Product-independent.
- **Endpoint (node)** — a party to an interface (`client`/`server`, `initiator`/`responder`).
- **`interfaceType`** — the role of an interface, drawn from a controlled vocabulary, and not
  an instance name. This profile uses:
  `management` · `service` · `interconnect` · `peer` · `storage`.
  The value relevant to this profile is `management`: the interface through which the product
  is configured or administered.

The profile is protocol-neutral. It uses the terms `encryption`, `keyExchange`, and
`authentication` rather than the TLS-specific term "cipher suite," so that the same rules apply
to a TLS service interface and to an SSH management interface.

### 2.1 Taxonomy of cryptographic relationships

A relationship is more general than a network connection, and the profile has to state which
kinds it covers. Relationships vary along four dimensions: the number of parties, whether those
parties exist at the same time, what passes between them, and how far the protection extends.
The table places the worked examples from the relationship model against those dimensions. Each
is described with a diagram in [model.html](model.html).

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

**Scope for this version.** The profile applies to pairwise relationships. Group relationships,
in the last row, are out of scope for v1 and are recorded as a known limitation rather than
approximated, because decomposing a group into pairwise relationships loses the shared key and
the membership over which it applies. A future revision should address them together with the
first-class attributed-edge model.

The dimensions also indicate where a profile written for one sector may need different rules.
A profile concerned with data at rest will care about retention period, which does not arise for
a session; a profile concerned with signing will care about the verifier population, which has no
counterpart in a transport profile.

## 3. Two directions of use

| Direction | Party | Question |
|---|---|---|
| **Specification** | The party that generates the CBOM | Which interfaces and attributes must be declared? |
| **Conformance checklist** | The consumer or CI gate | Did the product declare its interfaces, including a management interface, each fully described? |

## 4. Rules

Requirement keywords follow BCP 14 (MUST / SHOULD / MAY). This profile uses two of the three kinds of rule the methodology defines: product-level rules constraining the set of interfaces, and per-interface rules applied to each. It uses no group rule, because it reports present state and present state has one answer per attribute. The migration profile derived from it does use one, for capability per cryptographic purpose.

### 4.1 Product-level rules (cardinality; product-independent)

| # | Requirement | Level | Constraint |
|---|---|---|---|
| P1 | The product MUST declare at least one cryptographic interface | **MUST** | `minInterfaces: 1` |
| P2 | The product MUST declare at least one interface of type `management` | **MUST** | `minInterfacesOfType: {management, 1}` |

P2 corrects the requirement the earlier draft stated incorrectly: rather than naming a specific
configuration interface, the profile requires that a configuration or management interface
exist, irrespective of its name.

### 4.2 Per-interface rules (applied to every declared interface)

Attribute names follow the methodology's naming conventions: a bare name denotes present state,
and a `Supported` suffix denotes declared capability. This profile records present state only, so
no attribute here carries the suffix. A profile requiring capability, such as the PQC migration
profile, reuses these names unchanged and adds the suffixed forms alongside them.

| # | Attribute | Level | Allowed values / notes |
|---|---|---|---|
| I1 | `protocol` | **MUST** | present (for example `TLS`, `SSH`, `IPsec`) |
| I2 | `protocolVersion` | **MUST** | present |
| I3 | `keyExchange` | **MUST** | present (registry algorithm identifier) |
| I4 | `encryption` | **MUST** | present (bulk or AEAD algorithm identifier) |
| I5 | `authentication` | **MUST** | present (server or host signature algorithm: certificate signature or host key) |
| I6 | `endpointRoles` | **MUST** | at least two endpoints declared |
| I7 | `interfaceType` | **MUST** | from the vocabulary in §2 |
| I8 | `lifecycleStage` | **MUST** | one of `intended` \| `implemented` \| `configured` \| `observed` |
| I9 | `implementationPurl` | **MUST** | `pkg:` Package URL of the implementing library. Withholdable (see §4.3): a `withheld` marker satisfies this rule, silent omission does not. |

A CBOM conforms if and only if every product-level MUST rule holds and every declared interface
satisfies every per-interface MUST rule. `interfaceId` is an instance label chosen by the
producer; the profile does not constrain its value.

Derived evaluations such as post-quantum posture are deliberately not profile attributes. They
are computed by an external policy from the disclosed facts, because the criteria on which they
depend change over time. See the discussion of policy evaluation in the accompanying documentation.

### 4.3 Disclosure states

An attribute that carries no value may do so for different reasons, and a consumer needs to tell
them apart. Following the 2026 SBOM minimum elements, a producer states whether missing
information is unknown to it or is being withheld. This profile recognises four outcomes per
attribute:

| Outcome | Meaning | Effect on a MUST rule | Effect on a SHOULD rule |
|---|---|---|---|
| value | A value was supplied and is checked against the constraint | passes if valid | passes if valid |
| withheld | The producer holds the information and declines to publish it | passes only if the rule is marked `withholdable` | passes only if the rule is marked `withholdable` |
| unknown | The producer does not have the information | fails, reported as unknown rather than absent | reported, does not fail conformance |
| undeclared | Neither a value nor a marker was supplied | fails | reported, does not fail conformance |

`unknown` never satisfies a MUST rule, because the profile's requirement has not been met. It is
nevertheless reported separately from `undeclared`, since the two carry different information: the
first records a limit of the producing process, the second records that the question was not
addressed at all.

In this profile only I9 (`implementationPurl`) is withholdable, on the basis that a producer may
reasonably decline to publish the version of an implementing library while still meeting the
disclosure objective. Other profiles will make different choices, and a procurement profile may
permit no withholding at all.

The combination of level and withholdability determines whether the disclosure model
affects a verdict. Withholding can only change an outcome on a MUST rule, because a SHOULD rule
does not decide conformance in the first place. Until v0.3 this profile held I9 at SHOULD while
marking it withholdable, so the flag was inert and the model was visible only in the report. I9
is now a withholdable MUST, which is the combination the model exists for: the producer is
obliged to address the attribute and may answer either with a value or with a declared refusal,
and a consumer can tell those apart from a document that never addressed it.

Markers are carried in the CBOM as properties under `pkic:profile:disclosure:`, because neither
CycloneDX nor SPDX provides a native field for them. The mapping records the convention.

### 4.4 Scope

The profile declares a `scope` object stating what it describes and what it will accept. The
four members are one boundary and are decided together, which is why they are carried together
rather than as separate fields.

| Member | This profile | Why |
|---|---|---|
| `orientation` | `inventory` | This profile reports what interfaces do, not what they could do. Under C12 that forbids it from requiring any forward-looking attribute, which is what keeps a present-state name and a capability name from being read as interchangeable across profiles that share a vocabulary. |
| `subjectType` | `product` | The subject is a shipped product held by a consumer who did not build it and cannot inspect it. A profile for a service the consumer operates could ask for more. |
| `relationshipTypes` | `interface` | Every rule here constrains a communication interface. The declaration is checked against the rules rather than trusted, because a scope statement maintained by hand drifts from what the rules actually say. |
| `lifecycleStages` | all four | An acceptance constraint, in the same sense as `appliesTo` for carrier versions: an interface reporting a stage outside the set fails I8. |

The lifecycle-stage member is the one that changes verdicts, and this profile deliberately does not use it
to change any. A disclosure baseline should record whatever a producer is able to report,
including cryptography it has only `intended`, because an intention disclosed is more useful to
an inventory than an intention withheld. What the field buys the baseline is not a restriction
but the ability of a derived profile to impose one: the PQC migration profile accepts only
`implemented`, `configured` and `observed`, on the grounds that a migration plan built on
intentions is a plan built on an intention. A derived profile may narrow the set and may not
widen it, for the same reason it may not relax a rule.

## 5. Expected declaration

A conforming nginx deployment declares at least two interfaces:

```
interface #1  interfaceType = service      protocol = TLS  1.3   (browser <-> nginx, via OpenSSL)
interface #2  interfaceType = management   protocol = SSH  2.0   (admin  <-> host,  via OpenSSH)
```

Each carries protocol, version, keyExchange, encryption, authentication, two endpoint roles,
interfaceType, and lifecycleStage. Interface #2 is the interface that satisfies P2;
without it, the product would provide cryptography for its own configuration that is not
disclosed.

## 6. The two example CBOMs

- `cbom-pass.cyclonedx.json` — declares both interfaces, each fully described. Conforms.
- `cbom-fail.cyclonedx.json` — declares only the `service` (HTTPS) interface, fully described,
  but omits the `management` interface. Product rule P2 fails, because no management interface
  is declared. The CBOM does not conform, even though every attribute of the interface it does
  declare is present. This is a missing mandatory element at the product level, rather than a
  missing attribute.

To evaluate: `python validate_cbom.py <cbom> profile-interface-disclosure.rules.json`, or open
`demo.html`.

## 7. Changelog

The Versioning section asks profile authors to publish a changelog and to say which changes
oblige a producer to do further work. This section is that record for the example, and is
written to the form the methodology proposes.

A change is **tightening** if a document that conformed to the previous version may no longer
conform, **relaxing** if the reverse, and **editorial** if conformance is unaffected. Version
numbers are the profile's own and are independent of the carrier version.

### v0.2 — 2026-08-07

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added the disclosure state model of §4.3, with the `pkic:profile:disclosure:` marker prefix and a `withholdable` flag on every rule | tightening | A document that omitted an attribute silently now fails as `undeclared`; supplying a marker restores conformance |
| Added rule I9 `implementationPurl` at SHOULD, withholdable | none | SHOULD rules are reported, not enforced |
| Recorded `appliesTo` as CycloneDX `min: 1.6`, `tested: 1.7` | editorial | Documents at 1.6 are evaluated and flagged legacy rather than refused |

### v0.3 — 2026-08-09

| Change | Kind | Effect on an existing document |
|---|---|---|
| Raised I9 `implementationPurl` from SHOULD to MUST, keeping it withholdable | tightening | A document omitting the attribute in silence no longer conforms. Adding either a value or a `withheld` marker restores conformance |
| Stated `withholdable` explicitly on every rule | editorial | None. An absent flag was already treated as false; the value is now readable from the profile rather than inferred from a validator's default |

The first change exists because of what the comparison in §4.3 describes: no rule in either
example profile combined MUST with withholdability, and that is the only combination in which
withholding alters a verdict. The disclosure model was therefore stated in the profile without
being applied by any rule.

The derived PQC migration profile pins v0.5 and tightens I9 by removing its withholdability, the
level being already MUST. Under decision 0004 that tightening is permitted; a subsequent baseline
revision that relaxed I9 would place the derived profile in conflict, which is why the base is
pinned by version.

### v0.4 — 2026-08-21

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added the `scope` object of §4.4: `subjectType`, `relationshipTypes`, and the accepted `lifecycleStages` | editorial | None. This profile accepts all four stages, so no document that conformed to v0.3 stops conforming. The field's effect is on profiles derived from this one, which may now narrow the set |
| Added `objective.decisionOptions`, listing the three actions the consumer chooses between | editorial | None. The decision text is unchanged; stating the options is what makes the action-choice test in Method step 1 checkable rather than a matter of review |

Both changes are editorial here and neither is elsewhere: the migration profile's v0.2 narrows
the accepted stages and that is a tightening. The pattern is worth noting when reading a
changelog, because a field can be introduced without effect in one profile and immediately
change verdicts in another that derives from it. Recorded as decision 0008.

### v0.5 — 2026-08-21

| Change | Kind | Effect on an existing document |
|---|---|---|
| Added `scope.orientation`, declared here as `inventory` | editorial | None. The constraint falls on the profile, not the document: an inventory profile may not require forward-looking attributes, checked as C12 |

The value of the field is again in what it permits elsewhere. The migration profile declares
`both`, and C12 then obliges it to require the present-state attribute behind every capability
attribute it asks for. It already did, by inheriting I2, I3 and I5 from this profile — but
nothing had required it to, and a migration profile written standalone could have reported
capability alone. Recorded as decision 0009, which reverses the clause in 0008 that rejected
orientation.

### v0.1 — initial draft

Product-level rules P1 and P2 and per-interface rules I1 to I8. An earlier working draft bound a
rule to a named interface (`interfaceId MUST equal "nginx-https"`); the correction to
product-independent form is described in §1 and recorded as decision 0001. That draft was not
published and no document was authored against it.

### Not yet decided

Whether a tightening obliges a grace window before a consumer may reject documents produced
against the previous version, and whether that window belongs to the profile or to the agreement
between the parties. The Versioning section describes dated grace windows; the example does not
yet exercise one.
