# Draft section for review: the hardware module dilemma

**Status:** draft for Mike's review. Not yet merged into `EU Report.md`.

**Proposed placement:** as **§3.7**, at the end of chapter 3, after §3.6. Chapter 3 already carries
the hardware track (LYR-T-02), so the reader arrives with the context. Placing it there needs no
chapter renumbering and breaks no cross-references.

**If it goes in, three passages should shrink so the report does not say this three times:**

1. `§3.3 LYR-T-02`, the sub-heading *The module's own cryptography is a separate question*. Cut it
   to two sentences and point forward to §3.7, which supersedes it.
2. `§10.5 WR4`. Keep the six-row table and the profile requirement. Cut the three explanatory
   paragraphs after the table, which §3.7 now carries.
3. `§1` executive summary. One sentence could be added, since this is the report's sharpest concrete
   example. Suggested wording at the end of this file.


---

## 3.7  The hardware module dilemma

A hardware security module is bought to be the strongest component in a system. It is where keys are
kept when they must not be copied. Certificate authorities keep their signing keys in one. So do
payment networks, government systems, and the roots of national public key infrastructure.

Modules now offer post-quantum algorithms. ML-KEM and ML-DSA are available through the application
interface on most current platforms, usually by firmware update. Two modules have completed
FIPS 140-3 Level 3 validations that cover those algorithms inside the validated boundary, one in
July 2026 and one in August 2026.

The cryptography that protects the module is a separate matter. Firmware is authenticated with a
classical signature. Secure boot chains back to a classical root of trust. Administrative
authentication, key backup and attestation are classical. That is the position on almost every
module in service, and on most modules shipping today.

So two things are true of the same device at once. It offers post-quantum algorithms to the
applications that call it. It is itself protected by classical cryptography. The first is what gets
advertised, certified and bought. The second decides whether the module survives a quantum
adversary.

This is not a defect in any particular product. It is where the industry has got to, and it is the
plainest hardware case of the problem this report describes. The cryptography that decides security
is applied between parties, and a description of one component cannot express it.

### 3.7.1  Why a certificate does not settle the question

A validation certificate is accurate, and it is narrower than most readers take it to be.

FIPS 140-3 and Common Criteria evaluate a defined boundary. For a module offering post-quantum
algorithms, the certificate says those algorithms are correctly implemented inside that boundary,
and that the boundary resists the attacks the scheme tests for. It does not say the cryptography
protecting the boundary is post-quantum. Most of that cryptography sits outside the evaluated
perimeter. Where it sits inside, no scheme currently requires it to be quantum-resistant.

The industry distinguishes external from internal support. External support means post-quantum
algorithms exposed through the module's interface, usually delivered as firmware. Internal support
means the module's own architecture has been migrated: roots of trust, secure boot, internal key
wrapping, and the communication between components inside the device. Almost every vendor now offers
the first. Few have redesigned for the second. Of the two recently validated modules, one is built
with hybrid roots of trust and post-quantum secured boot. The other delivers algorithm support by
firmware on a classical foundation.

None of this is a criticism of the schemes. They evaluate what they say they evaluate. The
difficulty is what a procurement officer, a supervisory authority or a board takes from a
certificate, which is a general assurance it was never written to give.

### 3.7.2  What the module actually depends on

A module is not one thing with one cryptographic posture. It is a set of interfaces. Each has a
different party at the far end, each migrates on its own clock, and each is owned by a different
party.

Six of them matter. The application cryptographic API faces the calling application. Firmware update
authentication faces the vendor's signing infrastructure. Secure boot and the root of trust are
internal. Administrative authentication faces operator cards and quorum tokens. Key backup, wrapping
and cloning face a peer module or offline storage. Attestation faces an external verifier.

On a typical validated module today, one of those six has a post-quantum option. The other five are
classical, and four of them cannot be changed by the buyer at any price. Section 10.5 works the same
module through interface by interface, and Figure 4 draws it.

### 3.7.3  Consequences for security

An adversary attacks the weakest crossing, not the strongest algorithm. Nobody holding a quantum
computer needs to attack ML-KEM. Harvested firmware update traffic, a classical attestation key, or
a classical key backup path each defeat the module on their own, and a post-quantum application
interface does not help.

Harvest now, decrypt later applies to the module's own traffic. The argument is usually made about
application data, but it bites harder here. Key backup and cloning traffic can be captured today and
decrypted later, and what it protects is key material rather than a message. The keys held in a
hardware module have the longest sensitivity lifetime of anything in an estate. A backup path
captured in 2026 yields a key whenever the capability arrives, and that key may still be in use.

Firmware signing is where forgery bites, and it is the hardest thing to fix. Signature forgery runs
on a different clock from confidentiality, because a signature has to be broken before it is relied
on rather than afterwards. But a forged firmware image is complete compromise of the device, and the
verification key is fixed for the module's life. A module sold today with a classical firmware
verification key carries that key until it is decommissioned.

The weakness passes upward into the public key infrastructure. A certificate authority can issue
post-quantum certificates from a module whose own protection is classical. The post-quantum chain
then rests on a classical root of trust and a classical backup path. Migration of the trust
infrastructure cannot get ahead of migration of the hardware it runs on, and today it has.

A classical attestation key means a verifier can be told anything. Attestation is how a relying
party learns what state a module is in. If the key signing that evidence is classical, the evidence
is worth what that key is worth.

### 3.7.4  Consequences for the buyer

Almost none of it is the buyer's to fix. The application interface is a configuration task for the
integrator. Firmware authentication and secure boot are architecture decisions for the vendor, taken
on a multi-year cycle. Administrative authentication and key backup sit with the vendor first and
the operator second. A migration plan that does not separate these gives work to parties who cannot
do it. The buyer's real levers are procurement timing and pressure on a vendor roadmap.

Internal migration usually needs new hardware rather than new firmware. Roots of trust and secure
boot are frequently fixed in silicon. Where they are, migration is a capital replacement on a ten to
twenty year cycle. The decision that locks it in is a procurement decision, taken years before
anyone asks the readiness question. A module bought in 2027 with classical roots of trust is a
problem for the 2040s, and it is being bought now.

A buyer also has to be able to tell "not yet" from "never". Some roots of trust are fixed at
manufacture and cannot be changed at all. One answer means waiting for a firmware release and
planning a configuration change. The other means putting a hardware refresh in the capital plan. A
buyer who cannot tell the two apart cannot budget.

A single readiness flag is accurate and useless. "PQC supported" against a module collapses six
interfaces into one bit. The bit is true. What it leaves out is everything the buyer would need to
plan with, and none of that can be recovered by testing, by scanning, or by reading the
certificate.

### 3.7.5  Consequences for policy

A scheme that recognises post-quantum-ready hardware has to say which reading it means. If a
certification or labelling scheme does not distinguish algorithms offered from module protected, the
market will supply the cheaper reading, and it will do so honestly. In the Union this would be
settled in the European cybersecurity certification scheme for ICT products.

One allow list per product cannot describe a module. Cryptographic requirements are being drafted as
a shared component across the vertical standards, with a list of acceptable mechanisms. A module
needs several lists, for technical reasons rather than arbitrary ones. Firmware authentication
favours stateful hash-based signatures, because their security rests on different assumptions from
lattice schemes and the verification key has to outlast the device. Application signing favours
lattice signatures, for size and speed. A requirement written as one list per product cannot express
a device whose interfaces need different answers for good reasons.

A progress metric that counts modules with post-quantum support will count these as done. This is
the midpoint-victory problem in hardware form, and hardware is where it is least recoverable,
because the correction needs a capital cycle rather than a configuration change. A classical
retirement state recorded per interface is what stops the midpoint of a migration being reported as
its end.

Only the vendor knows, which makes this the clearest case for disclosure in the report. A buyer
cannot find any of this by scanning. No test reveals how a module's firmware is authenticated. The
certificate is silent. The information exists, it is not commercially sensitive, and exactly one
party holds it. That combination is what a disclosure obligation is for.

### 3.7.6  What a profile can do here, and what it cannot

A profile requires the module's protective relationships to be listed alongside the relationships
the module serves: firmware authentication, secure boot, administrative authentication, key backup
and wrapping, and attestation. Each gets its own algorithms, its own lifecycle stage, its own
classical retirement state, and a statement of which party can change it. The profile also requires
"fixed at manufacture" to be distinguishable from "migration pending", because the two lead to
different decisions.

The cost to the vendor is enumeration, not investigation. The vendor already knows every answer.
What is being asked is that the answers be written down in a form somebody else can compare.

What a profile does not do. It does not verify that the vendor's declaration is true. It does not
accelerate a silicon respin or shorten a capital cycle. And it does not solve the modelling problem
underneath. No current file format has a native way to express the cryptography that protects a
module, because the endpoints of that relationship are the module and the vendor's signing
infrastructure, and neither party's inventory holds it. That is the gap this report asks the
Commission to raise rather than to solve.

> **Verify (before merge):** the two FIPS 140-3 Level 3 validations covering post-quantum algorithms,
> with vendor, certificate number and date for each, against the CMVP validated modules list. The
> claim that one of the two has hybrid roots of trust and post-quantum secured boot needs a primary
> vendor source rather than commentary. The IETF work is now `draft-ietf-pquip-pqc-hsm-constrained-06`
> (24 June 2026), a PQUIP working group document submitted to the IESG for publication as
> Informational; it addresses constrained devices generally rather than hardware security modules,
> so cite it for the firmware-update and secure-boot treatment only, and update Annex C, which still
> lists the earlier individual draft. Stateful hash-based signatures are standardised in
> NIST SP 800-208; confirm the reference before citing it by number. Confirm which EU certification
> scheme is the right one to name in §3.7.5.


---

## Suggested executive summary sentence

To be added to chapter 1, after the paragraph on migration as a coordination problem:

> The sharpest example is hardware. A hardware security module can hold a current certification
> covering post-quantum algorithms while the cryptography protecting the module itself stays
> classical: its firmware signing, its boot chain, its key backup. Both facts are true at once. Only
> the first is visible to a buyer, and the second decides whether the module survives (§3.7).
