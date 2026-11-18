# A CBOM is not a vulnerability report. That is what makes it useful.

When people first see a Cryptographic Bill of Materials (CBOM), they often ask the same question: "Does it tell me whether my cryptography is vulnerable?"

In the PKI Consortium CBOM methodology, the answer is no, and that is deliberate.

A CBOM declares which cryptography a product uses. That is a fact about the product. Whether that cryptography is weak is a judgement. A different party makes that judgement, at a different time, against criteria that change. If a producer puts the judgement inside the CBOM, the document goes out of date without anyone noticing.

## Three documents, three authors

Vulnerability response uses three different documents:

- **The CBOM.** The product's producer writes it. It declares which algorithms and libraries the product uses, and at which interfaces.
- **The advisory.** A third party writes it: a library maintainer, a body that issues CVE identifiers, or a research team. It states that a component, in certain versions, has a weakness.
- **The VEX statement** (Vulnerability Exploitability eXchange). The producer writes it. It states whether this product is affected by a given advisory, and why.

The producer writes both the CBOM and the VEX statement, so it is tempting to merge them into one document. Don't. The two change at different times:

- A CBOM changes when the product changes.
- A VEX statement changes when an advisory changes.

If you merge them, you are left with two bad options. You either republish the whole CBOM every time an advisory changes, or you leave an outdated document in circulation that still looks authoritative.

The working group therefore links the documents but keeps them separate. We call this "joined, not merged". A CBOM profile requires the producer to declare the facts that let someone evaluate whether the product is affected. A profile never requires the producer to state that verdict, and it does not allow the verdict as an attribute in the CBOM.

## Two kinds of cryptographic weakness

Cryptography fails in two very different ways, and the CBOM plays a different role in each.

The first kind is an **implementation defect**: a bug in the code that performs cryptography. Examples are a buffer overrun in a TLS parser, a timing side channel, or a padding oracle. Defects like these follow a well-known path:

- The defect receives a CVE identifier for a range of versions.
- An advisory is published, and producers issue VEX statements.
- You fix the defect by updating the component.

The tooling for this path already exists. The CBOM makes it more precise, because it shows which interfaces use the affected library.

The second kind is an **algorithm or parameter weakness**: a weak choice, not a bug. Examples are SHA-1 signatures, 1024-bit RSA keys, static Diffie-Hellman groups, and classical key exchange that a future quantum computer could break. These weaknesses follow no such path:

- Correct code that uses a deprecated algorithm never receives a CVE.
- No feed sends an alert, and no patch arrives.
- The fix may be a configuration change on one interface and a hardware replacement on another.

For this second kind, the CBOM is the only evidence you have. That is why the CBOM is central to post-quantum migration.

## What a CBOM tells you that an SBOM does not

A software bill of materials (SBOM) tells you that a library is present. The methodology's entry-level profile is called the interface disclosure baseline. A CBOM that meets it also tells you, for each interface:

- which library implements the interface
- what kind of interface it is
- who is at each end, and whether the product starts the connection or accepts it
- which protocol and protocol version it uses

Consider an OpenSSL advisory and an nginx deployment. The SBOM confirms that OpenSSL is present. The CBOM shows that three interfaces use it:

- the public HTTPS interface
- an outgoing TLS connection to an upstream server
- the management interface

Suppose a malicious server is needed to trigger the defect. Then the upstream connection is the real exposure, because that is where nginx acts as the client. A responder can see this immediately, instead of working it out from the product's configuration.

Pay particular attention to the management interface. Responders need information about it most, and producers most often leave it out. The baseline therefore requires the producer to declare the management interface, or to state explicitly that the product has none.

## What lets you link the documents

You can match a CBOM to advisories and VEX statements when the CBOM declares three things:

1. **A shared identifier for each library.** The methodology uses the Package URL (purl), a standard identifier format, so that documents about the same library match. Product names and marketing versions do not match reliably.
2. **A lifecycle stage for each fact.** The stage records how the producer obtained the fact: intended (from the design), implemented (from the build), configured (from the deployment) or observed (from the running system). Incident response needs configured or observed facts, not design intent.
3. **A digest of the document.** A digest is a hash that identifies one exact revision of the CBOM. A VEX statement can record the digest of the revision its analysis used. You can then still check the analysis after the product has been patched.

## What a conforming CBOM does not tell you

When a CBOM passes validation against a profile, the result means only one thing: the producer declared the required facts in the required form. It does not mean that the cryptography is safe, up to date, unaffected by any advisory, or adequate for your purpose. A profile sets a minimum for disclosure. It is not a security rating.

Because the CBOM holds facts and not judgements, one CBOM can serve procurement, incident response, compliance and PQC migration. Each of these uses applies its own policy to the same facts and reaches its own conclusion.

You can read the full methodology page here: https://pkic.github.io/cbom/methodology/vulnerabilities.html

If you work on vulnerability response, VEX or PSIRT processes, please contribute to the PKI Consortium CBOM Profiles Working Group.

#CBOM #PostQuantum #PQC #Cryptography #VEX #SBOM #SupplyChainSecurity #PKIConsortium
