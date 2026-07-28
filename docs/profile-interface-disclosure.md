# CBOM Profile — Interface Disclosure Baseline (Example v0.1)

> **Status:** Illustrative early-concept artifact for the PKIC CBOM Profiles Working Group.
> Not a normative deliverable. CycloneDX crypto field names are aligned to v1.7 / ECMA-424
> (2nd Edition) but should be schema-checked before real use. For how this profile handles
> CBOMs authored to older carrier versions, see `versioning-and-legacy-cboms.md`.

## 1. What changed and why

An earlier draft of this example bound a rule to a specific product and interface
(`interfaceId MUST equal "nginx-https"`). That is the wrong shape for a profile. A profile
must be **product-independent and instance-independent**: it states *structural* and
*attribute* requirements that any conforming product satisfies, without naming a particular
product or a particular interface.

So this profile does **not** say "there must be an interface called nginx-https." It says:

- a product **MUST declare its cryptographic interfaces**, and
- among them there **MUST be a management/configuration interface**, and
- **every** declared interface **MUST disclose a defined set of attributes**.

nginx is used only as an example subject to make it concrete. The same profile applies
unchanged to any TLS/SSH/IPsec-terminating product.

## 2. Vocabulary

- **Cryptographic relationship / interface (edge)** — a locus where cryptography is applied
  between parties (a TLS session, an SSH session, an IPsec tunnel). Product-independent.
- **Endpoint (node)** — a party to an interface (`client`/`server`, `initiator`/`responder`).
- **`interfaceType`** — the *role* of an interface, drawn from a controlled vocabulary, **not**
  an instance name. This profile uses:
  `management` · `service` · `interconnect` · `peer` · `storage`.
  The value that matters for this profile is `management`: the interface through which the
  product is configured/administered.

The profile is deliberately protocol-neutral: it names `encryption`, `keyExchange`, and
`authentication` rather than TLS-specific "cipher suite," so the same rules judge a TLS
service interface and an SSH management interface identically.

## 3. Dual use

| Direction | Who | Question |
|---|---|---|
| **Production recipe** | Whoever generates the CBOM | "Which interfaces and attributes must I declare?" |
| **Conformance checklist** | The consumer / CI gate | "Did this product declare its interfaces, including a management one, each fully described?" |

## 4. Rules

Keywords follow BCP 14 (MUST / SHOULD / MAY). There are two rule groups.

### 4.1 Product-level rules (cardinality — product-independent)

| # | Requirement | Level | Constraint |
|---|---|---|---|
| P1 | The product MUST declare at least one cryptographic interface | **MUST** | `minInterfaces: 1` |
| P2 | The product MUST declare at least one interface of type `management` | **MUST** | `minInterfacesOfType: {management, 1}` |

P2 is the point the earlier draft got wrong: instead of naming a config interface, the
profile requires that *a* configuration/management interface exists, whatever it is called.

### 4.2 Per-interface rules (applied to EVERY declared interface)

| # | Attribute | Level | Allowed values / notes |
|---|---|---|---|
| I1 | `protocol` | **MUST** | present (e.g. `TLS`, `SSH`, `IPsec`) |
| I2 | `protocolVersion` | **MUST** | present |
| I3 | `keyExchange` | **MUST** | present (registry algorithm id) |
| I4 | `encryption` | **MUST** | present (bulk/AEAD algorithm id) |
| I5 | `authentication` | **MUST** | present (server/host signature algorithm: cert signature *or* host key) |
| I6 | `endpointRoles` | **MUST** | at least two endpoints declared |
| I7 | `interfaceType` | **MUST** | from the vocabulary in §2 |
| I8 | `lifecycleStage` | **MUST** | one of `intended` \| `implemented` \| `configured` \| `observed` |
| I9 | `pqcPosture` | **MUST** | one of `classical` \| `hybrid` \| `pqc` |
| I10 | `implementationPurl` | SHOULD | `pkg:` Package URL of the implementing library |

**A CBOM conforms if and only if** every product-level MUST rule holds **and** every declared
interface satisfies every per-interface MUST rule. `interfaceId` is an instance label the
product chooses freely; the profile never constrains its value.

## 5. Worked expectation

A conforming nginx deployment declares (at least) two interfaces:

```
interface #1  interfaceType = service      protocol = TLS  1.3   (browser <-> nginx, via OpenSSL)
interface #2  interfaceType = management   protocol = SSH  2.0   (admin  <-> host,  via OpenSSH)
```

Each carries protocol, version, keyExchange, encryption, authentication, two endpoint roles,
interfaceType, lifecycleStage, and pqcPosture. Note interface #2 is what satisfies P2 —
without it, the product would be shipping crypto to configure itself that nobody can see.

## 6. What the two example CBOMs show

- `cbom-pass.cyclonedx.json` — declares both interfaces, each fully described. **Conforms.**
- `cbom-fail.cyclonedx.json` — declares only the `service` (HTTPS) interface, fully described,
  but **omits the `management` interface entirely**. Product rule **P2** fails: no management
  interface is declared. **Does not conform** — even though every attribute of the interface it
  *did* declare is present. This is a missing-mandatory-*element* failure at the product level.

Run `python validate_cbom.py <cbom> profile-interface-disclosure.rules.json`, or open
`demo.html`.
