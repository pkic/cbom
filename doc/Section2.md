# The case for CBOM profiles
## 2.1  The problem a profile solves
A CBOM can, in principle, record every cryptographic asset, parameter, and dependency present in a product. In practice, exhaustive coverage is rarely useful coverage. A complete cryptographic inventory of a large product can run to thousands of entries, most of which are irrelevant to any given decision, and which collectively obscure the few that matter.
At the same time, the parties that consume CBOMs — procurement teams, security operations, regulators, migration planners — each need a different and much smaller subset of that information. Absent an agreed structure, the result is the situation the industry already knows from security questionnaires: every consumer asks for cryptographic information in a slightly different shape, every producer answers in a slightly different form, and no two answers are directly comparable. Producers over-disclose in some areas, raising legitimate intellectual-property concerns, and under-disclose in others, leaving consumers without what they need.
## 2.2  What a CBOM profile is
A CBOM profile is a defined subset of CBOM content — a named set of attributes, with stated obligations and meanings — selected to support a specific objective. It does not introduce a new file format or a new data model. It is a statement of which attributes must be present, which should be present, and which are optional for a particular use, together with the rules for interpreting them.
A well-constructed profile does two things at once. It sets a floor that prevents underreporting of the information the objective requires, and a ceiling that bounds what a producer is expected to disclose. Both matter: the floor protects the consumer’s ability to act on the data; the ceiling protects the producer from open-ended disclosure and scope creep.
## 2.3  Why a methodology rather than a catalogue of profiles
Individual profiles are valuable, but they proliferate. Telecommunications needs a procurement profile, a vulnerability-response profile, and a PQC-migration profile; financial services needs its own; a national regulator needs another. If each is defined from scratch, in its own style and with its own conventions, the industry recreates the very fragmentation that profiles were meant to remove — only one level up.
The Working Group’s distinctive contribution is therefore not any single profile, but the method by which profiles are defined: a consistent way to state a profile’s purpose, choose its attributes, fix their semantics, map them to serialization formats, and govern the profile’s lifecycle. A shared method makes profiles from different authors comparable, composable, and tool-processable. It is the method, not a sector profile, that is intended to become the reference others adopt.
## 2.4  Lessons carried over from SBOM and early CBOM practice
The discipline draws directly on operational experience from SBOM adoption, where three properties separated smooth rollouts from difficult ones. Each applies to profiles:
•	Harmonisation. Converging on common structures and delivery mechanisms so that artifacts from different producers can be reconciled at scale.
•	Profiling. Recognising that a defined, purpose-specific subset is more useful than exhaustive coverage.
•	Normalisation. Ensuring that the same thing is named the same way (syntactic) and means the same thing (semantic) across producers and consumers.
A profile methodology is, in effect, a way in which these three properties are operationalised for cryptographic information.
## 2.5  Two broad orientations: inventory and migration
Profiles tend to serve one of two purposes, and the distinction shapes most later design choices:
•	Inventory-oriented profiles describe the current cryptographic state for governance, compliance, and risk purposes. They answer: what cryptography is present, where, and under what configuration?
•	Migration-oriented profiles support cryptographic transformation — most immediately the transition to post-quantum cryptography. They are concerned not only with current state but with capability, readiness, dependency on hardware refresh, certification timelines, and forward commitments.
The methodology should make orientation an explicit property of a profile, because it determines whether forward-looking and capability information is in scope (Section 3.10) and how conformance is judged.
## 2.6  Design principles
The following principles, consistent with the charter, should constrain every aspect that follows:
•	Format independence. A profile is defined in terms of an abstract attribute model, not in terms of CycloneDX or SPDX fields.
•	Simple mappability. That abstract model must map cleanly onto both CycloneDX and SPDX; complexity that cannot be expressed simply in both should be treated as suspect.
•	Avoidance of heavy ontology. The method favours practitioner-usable definitions over formal ontologies.
•	Vendor neutrality and political independence. The method privileges no vendor, tool, or standards body.
