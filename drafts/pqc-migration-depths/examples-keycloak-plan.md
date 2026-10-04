# Plan: Keycloak as the worked example for the two migration depths

Source: `cprofile/Linux_Keycloak_26.7.3_cprofile.json` (generated 27 September 2026 by an
automated parser from documentation). Checked against Keycloak's own documentation, the Keycloak
GitHub PQC discussion, and the OpenJDK record on 27 September 2026.

**Status, 27 September 2026, final.** The examples now use native fields (K8), inherit implementation facts from the providing library (K9) and carry document-level references to the companion SBOM and the Keycloak advisories (K10).

**Status, 27 September 2026, late.** Every application protocol is now a service, HTTPS included, and every protocol component is a TLS instance. The TLS interfaces are renamed `tls-https` and `tls-mgmt` (formerly `svc-https` and `mgmt-health`); the ids in the sections below predate the change.

**Status, 27 September 2026, evening.** OIDC, SAML, the Admin API, plain HTTP, brokered token verification and the key store are now CycloneDX services (K7). The examples have 13 interfaces and validate against the CycloneDX 1.7 schema.

**Status, 27 September 2026, afternoon.** The cprofile has been corrected to product defaults for the container image (previous version kept in `_to_delete/`). K6 is settled. The four example documents are in `examples/`. Earlier status notes follow.

**Status, 27 September 2026, updated after the cprofile revision of 09:11.** §1 is replaced by a review of the revised file, and K6 is proposed in §2.

**Status, 27 September 2026.** K1–K5 are settled as recommended and recorded in decision 0022.
The disclosure baseline v0.8 draft now defines an interface as a logical boundary (K2) and accepts
`none` for algorithm attributes (K3). Extended I8 accepts `out-of-band` (K4). The cprofile schema
has been updated (see §1). The Keycloak cprofile validates against it, and its content errors are
unchanged, because they were in the data and not in the schema.

## Recommendation

Use Keycloak for both examples. Author the examples by hand from primary sources, and record the
source of each value. Use the cprofile as a checklist of what to look up, not as the source of
the values.

Keycloak suits the migration family better than the gateway example does. Its critical
cryptography is not TLS. It is the token signatures that every relying party verifies. That
signing capability is committed upstream but blocked by an unfinished standard, which the
per-purpose capability group (G1) exists to express. Its TLS key exchange is supplied by the Java
runtime, so it shows `blockedBy: provider` and the platform-build question (F2). And the realm key
management it exposes lets the extended depth demonstrate its main rule on a real product.

## 1. Review of the cprofile (revision of 27 September, 09:11)

The revised file validates against the updated schema and fixes most of the first review. The
plaintext listener, the management port and the admin API are now placed correctly. The default
JDK provider is separated from the opt-in BC-FIPS provider, and the invented certificate number is
gone. The outbound database, LDAP, brokering and cluster interfaces are declared. Token signing is
recorded as a `payload_protection` control. Data at rest is stated as not performed by Keycloak.

What remains, in order of consequence for the examples:

| # | Item in the cprofile | What is actually the case | Source |
|---|---|---|---|
| 1 | Token signing control: realm private keys "encrypted-at-rest", parameter `REALM_PRIVATE_KEYS_STORED_IN_KEYCLOAK_DB_WITH_ENC_KEY` | Key provider material is stored in the database **in plaintext**. The request to encrypt it (#39933) is open with no milestone. This is the `keyWrapping: none` fact for `sto-realm-keys`, and the cprofile states the opposite | keycloak/keycloak #39933 |
| 2 | Management interface (9000): `transport_security.protocol: none` | `http-management-scheme` defaults to `inherited`. When TLS is set for the main server, the management interface uses HTTPS with the same certificate | Keycloak, *Configuring the management interface* |
| 3 | Cluster transport (7800): TLS 1.2 and 1.3, no key facts | TLS 1.3 only. mTLS on by default (`cache-embedded-mtls-enabled`). Keycloak generates a self-signed **RSA-2048** certificate, stores key and certificate **in the database**, and rotates it every 30 days. No key management surface is involved, and the key type is fixed by the product | Keycloak, *Configuring distributed caches* |
| 4 | BC-FIPS "2.1.0", "FIPS-140-2", modes `strict` or `permissive` | Keycloak names `bc-fips` 2.1.2, `bctls-fips` 2.1.22, `bcpkix-fips` 2.1.10, `bcutil-fips` 2.1.5. The modes are `strict` and `non-strict`. `fips-provider=bc-fips-2.1` is not a Keycloak option. Which FIPS 140 version validates the BC-FIPS 2.x module must be read from its CMVP entry, not from Keycloak's page title | Keycloak, *FIPS 140-2 support*; CMVP |
| 5 | JDK "21.0.4" | A July 2024 update. The JDK in the 26.7.3 image must be read from the image. Under K1 it decides the TLS key-establishment capability | Image manifest |
| 6 | Deployment values: `db-url=jdbc:postgresql://db.internal…`, `sslmode=verify-full`, `revokeRefreshToken=true`, `bruteForceProtected=true`, `failureFactor=10`, `eventsEnabled=true` | These are one operator's configuration, not the product's defaults (`revokeRefreshToken`, `bruteForceProtected` and `eventsEnabled` default to false). `metadata.lifecycle_stage: deployment` agrees, and `information_source: documentation` contradicts it. The file mixes a product description and a deployment | Keycloak admin guide |
| 7 | Upper-case "hardening parameters" such as `REQUIRE_HTTPS_FOR_TOKEN_ENDPOINT`, `REQUIRE_JDBC_TLS_VERIFY_FULL`, `KC_DB_PASSWORD_FROM_SECRETS_MANAGER` | Not Keycloak options. They are descriptive labels written as if they were identifiers. The realm option that governs HTTPS is `sslRequired` | — |
| 8 | Key management: `kcadm.sh` and the Admin Console listed as two surfaces, with different `fips_compliant_management` and `key_entry_method` values | One surface, the Admin REST API; `kcadm.sh` and the console are its clients. `sign` and `verify` are not key-management operations. `export` covers public keys and certificates only | Keycloak admin CLI and REST API |
| 9 | `supportedAlgorithms=RS256,ES256,PS256,HS256`; note says RSA and ECDSA key generation | Incomplete. The realm key providers also generate EdDSA, HMAC and AES keys, and the signature list includes the 384 and 512 variants. Verify against 26.7 | Keycloak realm keys |
| 10 | `features: mutual-auth` on the main listener and LDAP | Client-certificate authentication is off by default on the listener (`https-client-auth=none`). Interface `features` still cannot say supported rather than enabled (plan §2, finding 4) | Keycloak TLS guide |
| 11 | Missing | Outbound SMTP (StartTLS). Outbound fetches of client JWKS for signed client authentication. Both are interconnects | Keycloak documentation |
| 12 | `sbom_ref: urn:uuid:keycloak-26.7.3-quarkus-linux-x86_64`; `cbomgen_version` with `generation_method: manual` | Not a UUID. A tool version on a manual profile | — |

Items 1 and 3 matter most. Both are facts the extended example depends on, and item 1 in the
cprofile is the reverse of the truth.

Token signing now appears in the cprofile only as a control, because the schema has no
application-layer interface. The conversion takes that control as the source for the `svc-oidc`
and `svc-saml` interfaces (K2).

## 2. Modelling decisions the examples force

**K1. Subject: the container image, not the ZIP distribution.** The ZIP distribution runs on
whatever JDK the operator installs. Its TLS key exchange capability is then a deployment fact.
The container image fixes the JDK, so the product document can state it. The subject should be
the image, `pkg:oci/keycloak@<digest>?repository_url=quay.io/keycloak/keycloak&tag=26.7.3`, with
the ZIP distribution noted as a separate subject. This is fork F2 applied: one document per build.

**K2. Token issuance is its own interface, layered on the HTTPS port.** It gets protocol `OIDC`
(and a sibling for `SAML`), `authentication` set to the token signature algorithm, and
`keyExchange` set to the token encryption key management algorithm. This reuses the channel
attributes in their own sense: protected content between two parties. That differs from the
storage case, where there was no second party. It needs one statement in the Model section: an
interface is a logical boundary, not a port, and two cryptographic layers on one port are two
interfaces. **Candidate open question.**

**K3. Token encryption is off by default.** `keyExchange` on the token interface then has no
present-state value. Options: state `none`, or make the rule conditional. `none` is honest and
consistent with `keyWrapping: none`. The examples should use it, and the decision record should
say that `none` is an accepted value for algorithm attributes.

**K4. TLS keys provisioned out of band.** `pqc-migration-extended#I8 keyStoreRef` has no truthful
value for the HTTPS interface. A `withheld` marker would be false, because nothing is being
withheld. Allow the literal `out-of-band` alongside a reference, and record that in the rule's
note now so the future `refersTo` constraint accepts it.

**K6. Keys the product generates and rotates by itself.** The cluster transport's mTLS key has
no management surface and is not provisioned out of band: Keycloak creates it, stores it in the
database and rotates it. Neither a reference nor `out-of-band` is true. Proposed: `keyStoreRef`
also accepts `product-managed`. It is a fact, and it is the one that tells the operator the key
type cannot be changed by configuration. RSA-2048 on the cluster transport then reads as
`blockedBy: product` under G1.

**K5. The management port is a management interface without key functions.** Port 9000 is the
test case for the `keyManagementFunction: none` guard. The Admin REST API, on the main port, is
the key management surface.

## 3. Interface set

| Interface | Type | Protocol | Present state | Source |
|---|---|---|---|---|
| `svc-https` | service | TLS 1.2, 1.3 | keyExchange x25519; encryption AES-256-GCM; authentication per deployed certificate (example: ECDSA P-256) | cprofile, checked against JDK defaults |
| `svc-oidc` | service | OIDC / JOSE | authentication RS256; keyExchange `none` | Keycloak realm key defaults |
| `svc-saml` | service | SAML 2.0 | authentication RSA-SHA256; keyExchange `none` | Keycloak defaults |
| `mgmt-admin` | management | TLS + Admin REST | as `svc-https`; administrators authenticate with realm tokens | Keycloak documentation |
| `mgmt-health` | management | TLS (inherited from the main listener by default) | as `svc-https`; health and metrics only | *Configuring the management interface* |
| `int-db` | interconnect | TLS (JDBC) | per driver configuration | Keycloak database guide |
| `int-ldap` | interconnect | LDAPS / StartTLS | per directory | Keycloak user federation |
| `int-broker` | interconnect | HTTPS + OIDC/SAML | verifies external providers' signatures | Keycloak identity brokering |
| `int-cache` | peer | TLS 1.3, mutual | keyExchange per JDK default; authentication RSA-2048, product-generated, rotated every 30 days | *Configuring distributed caches* |
| `int-smtp` | interconnect | SMTP StartTLS | per mail server | Keycloak email settings |
| `sto-realm-keys` | storage | — | realm key material and cluster mTLS keys held in the database in plaintext: encryption and keyWrapping `none` | #39933; *Configuring distributed caches* |

Plaintext HTTP on 8080 is declared, not left out: `protocol: HTTP`, and `none` for every algorithm (K3). It is off unless `http-enabled` is set, and it is the normal configuration behind a TLS-terminating proxy, where it carries tokens in clear on the internal hop. That is a fact an operator assessing harvest-now-decrypt-later exposure needs. Coverage `all-external`.

## 4. Baseline example (pqc-migration v0.7)

Capability by purpose, for the interfaces where the answer teaches something:

| Interface | Purpose | Status | Blocked by | Enablement | Evidence |
|---|---|---|---|---|---|
| `svc-https` | key-establishment | depends on the JDK in the image | provider | software-update | Hybrid ML-KEM groups ship in JDK 27, enabled by default. Oracle's JDK 25 update (October 2026) and announced JDK 21 backports follow. The image's JDK decides the value |
| `svc-https` | entity-authentication | under-evaluation | standard, provider | not-available | No ML-DSA certificates in JDK TLS |
| `svc-oidc` | entity-authentication, data-integrity | committed | standard | software-update | Keycloak epic #43690, milestone 27.0. The JWK representation (the JOSE `AKP` key type) is still an Internet-Draft. Maintainers name the JWK gap and signature size as the challenges |
| `svc-oidc` | key-establishment | not-planned | standard | not-available | No PQC JWE key management is standardised |
| `sto-realm-keys` | key-protection | not-planned | product | not-available | Keys are not wrapped |

Module validation: in default mode, `moduleValidationScheme: none` on every interface.
Two options follow:

- **(a)** Keep the example in default mode. G1.4 then only applies where a purpose is `available`,
  which, depending on the image's JDK, may be nowhere. That is accurate, and it leaves G1.4 unshown.
- **(b)** Add a second, FIPS-mode subject document, with `moduleValidationScheme: fips-140-3` and
  the reference taken from the CMVP entry for the BC-FIPS 2.1 module. It would show
  `validatedModeAvailability` on the TLS key-establishment purpose.

Recommend (a) for the example pair. Hold (b) for the maturity or demo page, because every value in
it needs to be checked against the security policy of the validated module.

**Non-conforming baseline example:** identical except `svc-oidc` omits `moduleValidationScheme`.
It isolates `pqc-migration#I10`, the rule new in v0.7.

## 5. Extended example (pqc-migration-extended v0.1)

Adds to the baseline document:

- **P1:** `sto-realm-keys` declared.
- **P2:** `productCertificationScheme: none` for upstream Keycloak, verified.
- **`mgmt-admin`:**
  - `keyManagementFunction: keys-and-certificates`
  - `keyOperations`: generate, import, rotate, delete
  - `keyTypesSupported`: the realm key providers, which are RSA, EC P-256/P-384/P-521, Ed25519,
    Ed448, HMAC and AES (to verify against 26.7), with no ML-DSA
  - `keyTypes`: the default realm set
  - `keyStoreFormatsSupported`: pkcs12, jks (the java-keystore provider) and pem (imported keys)
  - `keyStoreLocation`: software
- **`mgmt-health`:** `keyManagementFunction: none`.
- **`keyStoreRef`:** `svc-oidc` and `svc-saml` point to `mgmt-admin`; `svc-https` takes
  `out-of-band` (K4); `int-cache` takes `product-managed` (K6, proposed).
- **`externalDependencies`:**
  - `svc-https`: certificate-authority
  - `int-broker`: identity-provider
  - `int-ldap`: directory
  - `svc-oidc`: none
  - where the X.509 client authenticator checks revocation: revocation-responder
- **`enablementSetting`:** for TLS on a capable JDK, the JVM's named-groups property. For
  tokens, the realm's default signature algorithm, once an ML-DSA provider exists.

The example makes the extended depth's central point without contrivance. The token interface's
signing capability is `committed`, and the key management surface cannot yet generate an ML-DSA
key. The operator learns both from one document.

**Non-conforming extended example:** identical except `mgmt-admin` omits `keyTypesSupported`.
It isolates `pqc-migration-extended#I3`.

## 6. Order of work

1. Settle K1–K5. K2 and K3 change the Model section and decision 0022. K4 changes I8's note.
2. Verify the values marked "to verify" in §3–§5 against the Keycloak 26.7 source and
   documentation. List each source in the example's `$comment`.
3. Author the baseline pair. It can be checked with the existing `validate_cbom.py` now.
4. Author the extended pair. It cannot be checked correctly until the evaluator evaluates
   `enumRef` element by element on list rules (`$pendingTooling`). Until then it fails on I2, I5,
   I6 and I9 for a reason that is the tool's, not the document's.
5. Send the §1 findings to the cbomgen maintainers, with the schema version mismatch first.

## Sources

- Keycloak, Configuring the management interface: https://www.keycloak.org/server/management-interface
- Keycloak, FIPS 140-2 support: https://www.keycloak.org/server/fips
- Keycloak discussion #40496, post-quantum keys: https://github.com/keycloak/keycloak/discussions/40496
- Secondary, not a primary source: https://skycloak.io/blog/post-quantum-oidc-ml-dsa-cookie-limits-keycloak/
  (JDK 24+ for ML-DSA key loading, FAPI policy executor rejecting ML-DSA)
- JEP 527: https://openjdk.org/jeps/527
- JDK 27 security enhancements: https://seanjmullan.org/blog/2026/09/15/jdk27
- Keycloak issue #39933, encrypt key provider material: https://github.com/keycloak/keycloak/issues/39933
- Keycloak, Configuring distributed caches: https://www.keycloak.org/server/caching
