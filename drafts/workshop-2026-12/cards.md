# Cards and wall

Print one set of role cards and one set of inject cards per table. Seal each inject card in an
envelope marked with its time. Print gap cards on A6 or large sticky notes, thirty per table.

## Role cards

Each team has five roles. With six players, two people share the security architect role.

### Migration lead

**Your job:** own the plan sheet and make the call on each action. You report to the board.

**Your worry:** a plan full of "escalate to supplier" will not survive the board. You need dates you
can defend.

**You will be asked:** which system moves first, and why.

### Security architect

**Your job:** read the documents for the cryptographic facts, and say what each interface uses and
could use.

**Your worry:** a document can be complete and still not tell you what you need. Notice where that
happens.

**You will be asked:** what the documents say a product *could* do, as opposed to what it does now.

### Procurement manager

**Your job:** own the supplier relationships. You decide what to ask a supplier for, and what you can
require at the next contract renewal.

**Your worry:** "send us a CBOM" got you three very different documents. Next time you have to ask
for something specific.

**You will be asked:** what you would put in the next tender so that every supplier answers the same
question.

### Protection and control engineer

**Your job:** the substations. You know the outage windows, the certification of each relay, and the
refurbishment plan for 2028 and 2033.

**Your worry:** any change to a relay's firmware means re-testing, and possibly re-certification and
type approval. You cannot afford to do that twice.

**You will be asked:** what can happen at the 2028 refurbishment, and what has to wait for 2033.

### Compliance officer

**Your job:** the regulator and the auditor. You receive two of the inject cards.

**Your worry:** whatever the plan says, you will have to show the evidence it was built on.

**You will be asked:** whether you could hand these documents to an auditor as they are.

## Inject cards

### Inject 1, at 0:30: advisory

> A security advisory is published today against OpenSSL 3.4.x, affecting TLS 1.3 key exchange.
> The national CSIRT asks every essential entity which of its internet-facing systems are affected,
> by close of business.
>
> **Answer in 5 minutes: which of your three systems are affected, and how sure are you?**

### Inject 2, at 0:45: regulator (to the compliance officer)

> The national authority writes: "List the systems that carry data which must remain confidential
> beyond 2035, and state when the key exchange protecting that data becomes quantum-safe."
>
> **Can you answer from the documents? What is missing, and who has it?**

### Inject 3, at 0:55: supplier slip

> The JOSE working group announces that the representation for ML-DSA keys in JSON Web Keys will
> take another eighteen months.
>
> **What in your plan moves? What does not?**

### Inject 4, at 1:05: auditor (to the compliance officer)

> Your auditor asks you to show that the three documents you planned from are the ones your
> suppliers issued, that they have not been altered, and that none has been replaced by a newer
> version since.
>
> **What can you show today?**

## Gap card

Print as below, one per card.

```
GAP                                          Team ____   Document  A  B  C  all
--------------------------------------------------------------------------------
The question we could not answer:



Who could answer it:   supplier   us   a standards body   nobody yet
Does it block a decision?   yes   no
--------------------------------------------------------------------------------
(facilitators)  Group: D  CP  O  A  none     Row: profile  draft  none
```

## Wall layout

| | **Disclosure**: what a product uses | **Change planning**: how it can change | **Operation**: what we run | **Assurance**: proof for an auditor |
|---|---|---|---|---|
| **A profile already requires it** | | | | |
| **A draft profile requires it** | | | | |
| **No profile requires it yet** | | | | |

A fifth area beside the grid: **Not a CBOM question** (for example budget, staffing, contract
price).

## Temperature poll

An open Formbricks link shown as a QR code. Each question: Agree / Disagree / Not sure. The result is
advisory and recorded as such.

1. When we buy a product, we should ask for a CBOM to a named profile, not just "a CBOM".
2. A supplier should not be allowed to withhold the implementing library from a CBOM shared under a
   confidentiality agreement.
3. I would give a supplier's CBOM to my regulator or auditor as evidence, if it came with a
   checkable conformance claim.
