---
title: The cryptographic relationship model
sideMenu: true
weight: 7
aliases:
- /cbom/methodology/model.html
linkTitle: Model
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

A profile states which facts a CBOM must disclose. Those statements are only as precise as the terms they use. The terms defined here are used throughout the methodology, and they must be settled before a profile can be written.

## Why this section exists

The questions that CBOMs are asked to answer are mostly questions about *use*, not about *inventory*. "Which algorithms does this product implement?" is an inventory question, and it is the easier one. "Which of our connections would still be readable if an adversary recorded them today?" is a question about where cryptography is applied, between whom, and under what negotiated terms. Migration planning, procurement conformance, and incident response all depend more on the second kind of question than on the first.

Current CBOM standards answer the first question well. They provide objects for algorithms, keys, certificates, and protocols, with fields for their parameters. They provide no object for the use of those assets between two parties. As a result, facts that belong to a connection have to be attached to the nearest asset. This works while a product has one obvious connection. It becomes unreliable as soon as a product has more than one.

This has a direct effect on profiles. The example profile requires a product to declare its cryptographic interfaces and to include a management interface among them. That requirement means nothing unless "interface" has an agreed definition, unless it is clear that an interface is not the same thing as an algorithm, and unless a producer and a consumer will count the same set of interfaces when they read the same document. Product rule P2 is a statement about relationships, and it is checkable only because the terms below are fixed.

The terms are fixed in four steps. First, the three terms are defined. Second, the boundary between them is drawn by showing what is *not* a relationship. Third, worked examples test the assumptions that a simple TLS session makes easy to hold. Fourth, one case that the current model does not cover is recorded.

{{< figure src="../assets/figures/methodology-model-1.svg" alt="Two endpoint boxes, a client browser and a server running nginx, joined by an edge labelled cryptographic relationship that branches down to key exchange, encryption and certificate assets" >}}

*The security indicator presented by a browser (for example, TLS 1.3, X25519, AES-256-GCM, RSA) describes the relationship; the browser and nginx are the endpoints; each named algorithm is an asset.*

## The three terms

| Term | Definition | In the example |
| --- | --- | --- |
| **Cryptographic relationship** (edge / interface) | The location at which cryptography is applied between parties. It is not itself a cryptographic asset. | The TLS 1.3 session; the SSH session. |
| **Endpoint** (node) | A party to a relationship. | `client` (browser or admin) and `server` (nginx or host). |
| **Cryptographic asset** | An algorithm, protocol, certificate, or key used by the relationship. | X25519, AES-256-GCM, the RSA certificate, OpenSSL. |

### Why the term is "relationship"

Two other terms were considered and set aside. *Interface* reads naturally for a network connection between two systems. However, it is too narrow. It suggests two parties communicating at the same moment over a link, and several of the cases below do not fit that description. The profile keeps the word in the attribute names `interfaceType` and `interfaceId`. Those attributes apply only to the relationships that are interfaces. The word is not used as the general term. *Cryptographic context* conflicts with established usage, where a context is the runtime state held by a cipher implementation. *Cryptographic relationship* has no prior technical meaning in this field, and it describes what the thing is. For these reasons it is the settled term.

## A fourth thing: what the cryptography is for

A relationship says *where* cryptography is applied and an asset says *what* is applied. Neither says what job the cryptography is doing. The job determines when the cryptography can change. A **cryptographic purpose** is that job: establishing a key, encrypting, proving identity, protecting a message from modification, signing something that must verify years later, protecting keys, deriving keys.

A purpose is not the same as an operation, and the two are easily confused. CycloneDX records operations in `cryptoFunctions`: `sign`, `verify`, `encrypt`, `keyagreement`. A TLS certificate signature and a firmware signature are both `sign` and `verify`. The TLS certificate signature proves identity during a session. It can change when the certificate hierarchy changes. The firmware signature must still verify long after it was written. It can change only when the last verifier in the field has been upgraded. The operation is the same, but the two signatures do different work and may change in different decades. An operation describes what the algorithm does. A purpose describes how the algorithm is used. Only the use determines a migration timetable.

Two consequences follow for anyone writing rules.

**A purpose does not partition assets.** AES-GCM serves encryption and data integrity at the same time, and a certificate signature can serve entity authentication in one deployment and non-repudiation in another. A rule written as "each algorithm has a purpose" is therefore wrong. An asset may serve several purposes. For the same reason, the number of purposes at an interface is not the number of algorithms it uses.

**A purpose belongs to a relationship, not to a product.** A product that terminates TLS and also signs firmware is doing different jobs at different boundaries, on different schedules. A purpose is attached where the cryptography is applied, which is the relationship. The same product may therefore hold one purpose in a settled state at one interface and in an unsettled state at another.

The vocabulary of purposes is listed in [Terms](../terms/). Terms also sets out the four-part test that an entry has to pass before it is added. The [PQC Migration](../../use-cases/pqc-migration/) profile shows why the distinction matters. That profile states capability once for each purpose. It does so because key agreement and identity proof migrate on different timetables. A single answer covering both would have to report the worse of the two.

## What is not a relationship

The distinction is easier to understand by looking at facts that do not belong to a relationship. Each row below pairs a node fact with the matching edge fact. A node fact is a property of a thing, such as a product, a library or a certificate. An edge fact is a property of one use of that thing between parties. The left column is what an asset inventory records. The right column is what a migration decision needs.

| Node fact (a property of a thing) | Edge fact (a property of a use) |
| --- | --- |
| The product supports AES-256-GCM. | This connection negotiated AES-256-GCM. |
| OpenSSL 3.4 is installed on the host. | This interface's key exchange is performed by OpenSSL 3.4. |
| The certificate is signed with ECDSA P-384. | This session authenticates the server using that certificate. |
| The device holds an ML-KEM implementation. | This link to the peer falls back to a classical group. |
| The archive is encrypted with AES-256. | The key protecting the archive is wrapped with RSA-2048 and must survive the retention period. |

The most common modelling error is to record a left-column fact and treat it as though it answered a right-column question. Capability is not the same as use. The fact that a product can perform an operation is not evidence that any particular connection performs it.

## Worked examples

A single TLS session makes the terms easy to state. It also makes them easy to underestimate, because the two parties are obvious and are present at the same moment. Each of the following examples breaks a different assumption that the TLS case makes seem true.

### 1 · One apparent connection is several relationships

A browser connects to a service through a content delivery network or a load balancer. The user sees one padlock. There are at least two relationships, and the cryptography on each is chosen independently. It is common for the public leg to be modern while the leg behind it uses an older protocol version, or none at all, on the reasoning that the network is private.

{{< figure src="../assets/figures/methodology-model-2.svg" alt="Browser, CDN or proxy, and origin server in a row, with the first leg labelled TLS 1.3 and the second leg drawn dashed and labelled TLS 1.0 or none" >}}

*An asset inventory that records "TLS 1.3 in use" is accurate for the public leg. It is also misleading, because the risk is on the second relationship, which the user cannot see.*

### 2 · The parties are separated in time, not space

An encrypted backup or archive has two parties: the process that writes it and whatever reads it later. There is no session, and the second party may not exist yet. The relationship still has all the properties that matter, including a lifetime, which here is the retention period rather than the duration of a connection.

This case determines how urgent the harvest-now-decrypt-later risk is. The bulk encryption algorithm is usually adequate. The exposure is in the key wrapping. Whether that exposure matters depends on how long the data must stay confidential. That period is a property of the relationship, not of any algorithm used in it.

{{< figure src="../assets/figures/methodology-model-3.svg" alt="A time axis with a writer backing up today and a reader restoring years later, joined by a relationship spanning the retention period, labelled AES-256 data encryption and RSA-2048 key wrapping" >}}

*An endpoint is a party to the use of cryptography, not necessarily a running host. Here the two parties never coexist.*

### 3 · The parties never interact

A publisher signs firmware or code. A relying party verifies the signature, possibly years afterwards, with no communication between them in either direction. The relationship is one of trust rather than exchange, and its failure has consequences.

For migration, the constraint in this case is at the verifying end. A publisher can adopt a post-quantum signature algorithm at any time. The publisher gains nothing if the deployed devices cannot verify the new signatures. The verifier therefore sets the upper limit for the relationship, meaning the strongest algorithm the relationship can use. The verifier may be a device with no update path.

{{< figure src="../assets/figures/methodology-model-4.svg" alt="A publisher signing an artifact, the signed artifact carried by any means, and a device verifying it years later with no update path, bracketed as one signer to relying party relationship" >}}

*A relationship with no session and no simultaneity. Migration planning that looks only at the signing end reaches the wrong conclusion.*

### 4 · Relationships overlap on the same wire

Transport security and message-level security protect different spans of the path. For example, a signed token travels inside a TLS session, and the token and the session do not share endpoints. Where a gateway terminates TLS, there are two transport relationships. One runs from client to gateway and the other from gateway to service. The signature relationship runs from the originator to the final recipient. It passes through the gateway untouched.

The overlap matters when a consumer asks what protects a given piece of data end to end. The answer differs for each layer. A model that records one relationship per connection cannot express that answer.

{{< figure src="../assets/figures/methodology-model-5.svg" alt="Originator, gateway and service in a row, with a separate TLS relationship on each hop and a signature relationship bracketing the whole path from originator to service" >}}

*Relationships are not a partition of the network path. They overlap, and each has its own endpoints and its own properties.*

### 5 · One asset, many relationships

A gateway with a single IPsec implementation may hold tunnels to many peers. An operator's interconnect, a service mesh, and a partner VPN estate all have this shape. The implementation is one asset. The relationships are many, and their properties differ because each peer negotiates separately.

Post-quantum readiness is therefore not a property that a product can hold on its own. An organization may deploy a fully capable gateway and still have most of its tunnels running classical key exchange, because readiness on any given tunnel depends on the other side as well.

{{< figure src="../assets/figures/methodology-model-6.svg" alt="One gateway box holding a single IPsec implementation, with lines fanning out to four peers: two using hybrid key exchange and two classical only" >}}

*Reporting readiness for the product reduces the results for many tunnels to a single value. A migration plan needs the result for each tunnel.*

### 6 · Capability is not the negotiated outcome

Two systems both implement a post-quantum key exchange. The session between them uses a classical group, because of a configuration setting, an intermediary that rejects the larger handshake, or a policy on one side. Both node records are accurate. The connection is nevertheless not quantum-safe.

There is no node on which this fact can be stored. It belongs to the relationship, and it cannot be derived from either endpoint's inventory entry. This example gives the clearest reason to treat the relationship (the edge) as an object in its own right, rather than as an annotation on an asset.

{{< figure src="../assets/figures/methodology-model-7.svg" alt="Two endpoint boxes, each listing support for ML-KEM-768 and X25519, joined by a link labelled negotiated X25519 only and marked classical" >}}

*Where capability and outcome diverge, only the relationship holds the answer. Node-level reporting will show this estate as ready.*

### 7 · The weaker party sets the upper limit

A modern gateway communicates with a controller installed twenty years ago. The gateway supports current algorithms. The controller supports what it shipped with and cannot be changed. The cryptography the relationship can use is fixed by the less capable end. No upgrade to the gateway changes it.

Planning that works from a product inventory will schedule an upgrade that cannot deliver the intended result. Planning that works from relationships identifies the controller as the item requiring replacement, which is a different and usually more expensive piece of work.

{{< figure src="../assets/figures/methodology-model-8.svg" alt="A modern gateway supporting ML-KEM and AES-256-GCM linked to a legacy controller with a fixed algorithm set and no firmware path, the link labelled posture set by the weaker end" >}}

*Relationship-level planning identifies the item that actually constrains the estate, which is rarely the item being upgraded.*

### 8 · Relationships that carry no data

An application uses a key held in a hardware security module or a trusted execution environment. The key never leaves the module. What passes between them are requests to use the key and the results of those operations. The relationship is one of custody and control, and it crosses a hardware boundary rather than a network.

This distinction affects migration in practice. If the key material is confined to hardware, adopting a new algorithm may require the module to support it, which can mean replacement rather than reconfiguration.

{{< figure src="../assets/figures/methodology-model-9.svg" alt="An application box linked to an HSM or TEE holding a private key that never leaves it, the two-way link labelled custody relationship carrying sign and unwrap requests" >}}

*Not every relationship transfers protected data between two hosts. Some describe where key material is held and who may ask it to act.*

## A known limitation: one-to-many relationships

Every example above is pairwise. Some cryptography is not. A broadcast or multicast group, a mobile air interface serving many receivers, and a group messaging session all apply cryptography among more than two parties at once, and the natural representation is a relationship with n endpoints rather than two.

{{< figure src="../assets/figures/methodology-model-10.svg" alt="A single transmitter with one arrow into a dashed boundary holding four named receivers and a note that further receivers join and leave over time" >}}

*A group relationship does not decompose into pairwise edges without losing the shared key and the membership over which it applies.*

The v1 model treats every relationship as pairwise. This case is therefore recorded as a known limitation and is not modelled. Representing it as several pairwise relationships loses the property that matters, which is the shared key and the set of parties holding it. Group relationships are a candidate for a later revision, together with the first-class attributed-edge model (an object that represents a relationship and carries its attributes). The limitation should be revisited when a consumer needs to express group membership or the posture of a group. See [Challenges](../challenges/).

One-to-many cryptography covers two different cases. Only the first requires a costly change to the model. The first case is a **shared key** held by n parties at once, as described above. No set of pairwise relationships describes it correctly, so the model has to change to carry it. The second case is a **signature verified by a population**. One party signs and many parties verify, each holding its own keys. Each signer-to-verifier leg can be described as a pairwise relationship without losing anything. What is missing in this case is a way to name the population of verifiers that sets the upper limit. A relationship with n endpoints is not needed. This is a smaller change, and it is recorded separately as Q46. A closely related gap is recorded as Q47. It concerns naming the trust anchor and stating whether membership under it is administered. Financial settlement and payment rails were proposed as an example of the shared-key limitation. They appear instead to be an instance of these two. The reasoning is in the multi-party trust design note.

## Summary: a taxonomy of relationships

Taken together, the examples vary along four dimensions: how many parties there are, whether those parties exist at the same time, what passes between them, and how far the protection extends. Setting the examples out in one table shows that the model is more general than the network connection usually used to explain it. The table also gives a way to test the model against a case from a new sector.

| Relationship | Parties | Simultaneous | What passes | Span | Property it exercises |
| --- | --- | --- | --- | --- | --- |
| TLS session to a service | 2 | yes | data in transit | single hop | the base case |
| Termination at a proxy or CDN | 2 per leg | yes | data in transit | chained, multi-hop | one apparent connection is several relationships |
| Encrypted backup or archive | 2 | no | data at rest | single | parties separated in time; lifetime is the retention period |
| Code or firmware signing | 2 | no | a signed artifact is carried | single | parties never interact; the verifier sets the upper limit |
| Message-level security inside transport | 2 per layer | yes | data in transit | layered, overlapping | relationships overlap rather than partition the path |
| IPsec mesh or operator interconnect | 2 per tunnel, many tunnels | yes | data in transit | single hop, repeated | one asset supports many relationships of differing posture |
| Negotiated fallback between capable peers | 2 | yes | data in transit | single hop | capability is not the negotiated outcome |
| Modern gateway to legacy controller | 2 | yes | data in transit | single hop | the less capable party fixes the posture |
| Application to HSM or TEE | 2 | yes | operation requests; key material confined | crosses a hardware boundary | a relationship that transfers no protected data |
| Broadcast, multicast, or group messaging | n | yes | data in transit | one to many | not represented in v1, as described above |
| Signed message verified by a closed membership | n | no | a signed message is carried | one to many | not represented in v1; the upper limit belongs to the membership rather than to either party. Recorded as Q46 |

The dimensions also indicate where a profile written for one sector will need rules that another does not. A profile concerned with data at rest has to address the retention period, which does not arise for a session. A profile concerned with signing has to address the population of verifiers, which has no counterpart in a transport profile. The same table appears in the profile specification at [profile-interface-disclosure.md](https://github.com/pkic/cbom/blob/main/docs/methodology/profile-interface-disclosure.md), where it defines the scope a profile applies to.

Neither CycloneDX nor SPDX currently provides an object that represents this relationship with its cryptographic meaning attached. The two formats fall short in different ways, and the difference affects how the model maps onto each. CycloneDX has cryptographic assets but no edge between endpoints. SPDX has a first-class `Relationship` element that can be addressed and annotated, but it has no cryptographic model to attach to that element. Both formats approximate the relationship by attaching relationship attributes to a protocol asset. This works for a single pairwise interface. It becomes increasingly awkward for the cases above. Providing such an object is the objective of the working group's first-class attributed-edge model. See [Challenges](../challenges/) and [Formats](../formats/).

[← Lifecycle Data](../lifecycle/) [Next: Objects →](../objects/)
