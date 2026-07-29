# CBOM Profile — Interface Disclosure Baseline (Example v0.1)

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

## 3. Two directions of use

| Direction | Party | Question |
|---|---|---|
| **Specification** | The party that generates the CBOM | Which interfaces and attributes must be declared? |
| **Conformance checklist** | The consumer or CI gate | Did the product declare its interfaces, including a management interface, each fully described? |

## 4. Rules

Requirement keywords follow BCP 14 (MUST / SHOULD / MAY). There are two rule groups.

### 4.1 Product-level rules (cardinality; product-independent)

| # | Requirement | Level | Constraint |
|---|---|---|---|
| P1 | The product MUST declare at least one cryptographic interface | **MUST** | `minInterfaces: 1` |
| P2 | The product MUST declare at least one interface of type `management` | **MUST** | `minInterfacesOfType: {management, 1}` |

P2 corrects the requirement the earlier draft stated incorrectly: rather than naming a specific
configuration interface, the profile requires that a configuration or management interface
exist, irrespective of its name.

### 4.2 Per-interface rules (applied to every declared interface)

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
| I9 | `implementationPurl` | SHOULD | `pkg:` Package URL of the implementing library |

A CBOM conforms if and only if every product-level MUST rule holds and every declared interface
satisfies every per-interface MUST rule. `interfaceId` is an instance label chosen by the
producer; the profile does not constrain its value.

Derived evaluations such as post-quantum posture are deliberately not profile attributes. They
are computed by an external policy from the disclosed facts, because the criteria on which they
depend change over time. See the discussion of policy evaluation in the accompanying documentation.

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
