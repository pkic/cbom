A CBOM is not a vulnerability report. That is deliberate.

People often ask the PKI Consortium CBOM Profiles Working Group whether a Cryptographic Bill of Materials (CBOM) tells them if their cryptography is vulnerable. It does not.

A CBOM declares facts: which algorithms and libraries a product uses, and at which interfaces. Whether those are weak is a judgement. A different party makes that judgement, at a different time, against criteria that change.

When you keep the facts and the judgement apart, both become more useful:

• For implementation bugs, the CBOM narrows an advisory down to the interfaces that use the affected library. That includes the management interface, which responders need most and producers most often leave out.
• For weak algorithms, such as SHA-1, 1024-bit RSA or classical key exchange that a quantum computer could break, there is no CVE, no feed and no patch. The CBOM is the only evidence you have, and that makes it central to post-quantum migration.

My new article explains how the CBOM, the advisory and the VEX statement work together: linked, but kept separate.

👉 [link to article]

If you work in vulnerability response, VEX or PSIRT, we would value your input.

#CBOM #PostQuantum #PQC #Cryptography #VEX #SBOM #SupplyChainSecurity #PKIConsortium #CyberSecurity #QuantumSafe
