# Review: the proposed mandatory structured preamble

Working note for the PKIC CBOM Profiles Working Group.
Written 21 August 2026, against `docs/methodology/` and `decisions/` at that date.

## The submission

> I suggest to adopt a mandatory structured preamble. Every profile should begin with
> machine-readable and human-readable fields for `profileId`, `version`, `objective`,
> `intendedConsumers`, `supportedDecision`, `orientation`, `subjectType`, `inScope`,
> `outOfScope`, `lifecycleStages`, and `exclusionsRationale`. The decision should be phrased as
> an action choice, such as whether to upgrade, replace, accept, or investigate a system. The
> boundary should be expressible as a tuple of subject, asset/relationship types, interfaces or
> domains, and lifecycle stage.

## Disposition, field by field

| Proposed | Status | Where it already lives / what to do |
|---|---|---|
| `profileId` | Present | Same name. C2, checked mechanically. |
| `version` | Present | Same name. C2. |
| `objective` | Present | Same name, as `{consumer, decision}`. C1. |
| `intendedConsumers` | Duplicate | `objective.consumer`. See the note on plurality below. |
| `supportedDecision` | Duplicate | `objective.decision`. |
| `outOfScope` | Duplicate | `exclusions[].item`. C8. |
| `exclusionsRationale` | Duplicate | `exclusions[].reason`. C8 already fails an exclusion with no reason. |
| `orientation` | Reject | No consumer acts on it. See below. |
| `subjectType` | **Adopt** | Absent. The vocabulary exists in Method step 2 as prose only. |
| `lifecycleStages` | **Adopt** | Absent at profile level, and its absence affects verdicts. |
| `inScope` | Adopt in a weaker form | As `scope.relationshipTypes`, derived and checked rather than hand-written. |
| Decision as an action choice | **Adopt the enforcement** | The test is already in Method step 1; C1 does not enforce it. |
| Boundary as a tuple | Adopt as the structure | Not four fields — one `scope` object. |

Six of the eleven fields are already in the schema. Renaming them would mean a sweep of both
rules files, `validate_cbom.py`, `check_profile.py`, the nine test fixtures, the Terms section
and the Conformance table, and at the end a profile would express exactly what it expresses now.
That should be said plainly on the issue, or the same suggestion returns in three months.

## The three that are worth taking

**`subjectType`.** Method step 2 tells an author to decide whether the subject is a product, a
deployed service, a component, or a bounded part of an estate. That is an enumerable vocabulary
sitting in prose and missing from the rules file, so a consumer cannot mechanically determine
whether a profile applies to what they are holding. Straightforward oversight; adopt with the
vocabulary already written.

**`lifecycleStages`, which is the substantive one.** `lifecycleStage` exists per interface as
rule I8, constrained to `intended`, `implemented`, `configured` or `observed`, and any of the
four satisfies the rule. A vendor may therefore return a document in which every interface is
declared `intended` — cryptography it plans to implement — and that document conforms to the
Interface Disclosure Baseline. Nothing in the profile can currently object.

This is the case the Conformance section warns about in the abstract ("a verdict of conforms does
not assert that the disclosed values are accurate ... the lifecycle stage records how the data
was obtained") without giving a profile any means to act on it. A profile-level accepted set
gives it one, with the same semantics `appliesTo` already has for carrier versions.

Adopting it costs the baseline nothing: a disclosure baseline would accept all four stages, so no
behaviour changes there. The value is that a procurement profile can then narrow the set, which
is the case that needs it.

**The action-choice test.** Method step 1 already states it precisely — "whether to schedule this
system for upgrade, replacement, or no action" passes, "to understand our cryptographic position"
does not. C1 checks only that a `decision` string is present. Adding `objective.decisionOptions`
with two or more entries makes the test mechanical and fails the second example automatically. A
closed vocabulary of upgrade / replace / accept / investigate would be too narrow across sectors;
a declared set of options the consumer chooses between is not.

## The two judgement calls the group should make explicitly

**Plurality of the consumer.** `intendedConsumers` is plural where `objective.consumer` is
singular, and the singular is deliberate: a named consumer with a named decision is what keeps a
profile from growing until it demands everything. This is a design position, not an oversight,
and it should be taken as one rather than reversed inside a rename. Where a profile genuinely
serves two consumers making the same decision, the existing field accommodates that in prose.

**`orientation`.** It currently exists only as a classification of the thirteen aspects in
`_data/aspects.yml`, not of profiles. The question to put is what a consumer does differently on
reading `orientation: migration` that they would not do on reading the objective. If the answer
is nothing, it is a catalogue field and belongs to a registry of profiles rather than to each
profile.

## On the framing

"Mandatory structured preamble" suggests a new document section. What is actually proposed is an
extension of an existing structured object plus two new mandatory members. Putting it to the
group as a change to C1 and a new C11 lands it where the conformance requirements already live,
and gets it checked by the tool that already checks them. Putting it as a preamble invites a
parallel structure alongside the rules, which is how the scope statement and the rules end up
disagreeing.

Recorded as decision record [0008](decisions/0008-profile-scope-declaration.md), status Proposed.
Note that 0008 differs from 0001 to 0007: those ratify positions already built into the worked
example, whereas 0008 asks for a change that would then have to be built. The cost is in its
Consequences section.

---

## Appendix: comment drafted for issue #4 (aspect 3.1)

> The preamble proposal splits into three things that are missing and six that already exist.
>
> Already in the rules file and checked by `check_profile.py`: `profileId` and `version` (C2),
> `objective.consumer` and `objective.decision` (C1), `exclusions[].item` and
> `exclusions[].reason` (C8). `intendedConsumers`, `supportedDecision`, `outOfScope` and
> `exclusionsRationale` are renames of those. Adopting the renames means touching both rules
> files, the validator, the checker, nine fixtures, Terms and Conformance, and a profile ends up
> expressing what it expresses today.
>
> Genuinely missing, and worth taking:
>
> 1. **`subjectType`.** Step 2 of Method already names the vocabulary — product, service,
>    component, estate-subset — but only in prose. A consumer cannot mechanically tell whether a
>    profile applies to what they hold.
> 2. **`lifecycleStages` as an accepted set.** `lifecycleStage` is per-interface (I8) and any of
>    the four values satisfies the rule, so a document declaring every interface `intended`
>    conforms to the baseline. A procurement consumer would not knowingly accept that and the
>    profile currently cannot say so. Same semantics as `appliesTo` has for carrier versions.
>    Costs the baseline nothing — it would accept all four — and gives a procurement profile the
>    lever.
> 3. **The action-choice test made mechanical.** Step 1 states the test; C1 does not enforce it.
>    `objective.decisionOptions` with two or more entries would.
>
> Suggested shape, as one `scope` object rather than four flat fields, since subject, relationship
> types and lifecycle stage are one boundary:
>
> ```json
> "objective": { "consumer": "...", "decision": "...",
>                "decisionOptions": ["upgrade", "replace", "accept as is", "investigate further"] },
> "scope":     { "subjectType": "product", "relationshipTypes": ["interface"],
>                "lifecycleStages": ["implemented", "configured", "observed"] }
> ```
>
> Two questions for the group rather than for the editor: whether `consumer` stays singular (it is
> singular on purpose — see Method step 1), and whether `orientation` has any consumer that acts
> on it, or whether it is a registry field.
>
> Written up as decision record 0008, status Proposed. Two new MUSTs is a tightening: both example
> profiles, `check_profile.py`, two new fixtures, `validate_cbom.py` for I8, Terms and
> Conformance. Roughly a day, and better before Profile and PQC Migration enter a review batch.

## Appendix: comment drafted for issue #5 (aspect 3.2)

> Cross-referencing from #4, where the structured-preamble proposal is being worked through.
>
> The identity half of that proposal — `profileId`, `version` — needs nothing: both exist and are
> checked under C2, alongside the carrier acceptance range from decision 0006.
>
> What touches this aspect is whether `scope.subjectType` is identity or scope. It is proposed in
> #4 as scope, on the grounds that it says what the profile describes rather than which profile it
> is. If the group later builds a registry of profiles, `subjectType` and the rejected
> `orientation` field are both plausible registry facets, and that is the point at which the
> question is worth reopening.
>
> No action proposed here. Flagging so that 3.2 is not surprised by a `scope` object appearing in
> the schema.
