# Outstanding decisions

Working list, 4 October 2026. Built from every item in `open-questions.md` (Q01–Q68, N01–N04),
the 21 decision records, the drafts in `drafts/`, the open GitHub issues and their comments, and
the ten GitHub Discussions. Its purpose is to decide what goes to a poll, in what order, and what
does not need one.

## Summary

There are 72 register items, 21 decision records marked Proposed, 3 draft decisions, 2 concrete
member proposals in issue comments, and 10 Discussions. After triage:

| Outcome | Count | What happens |
|---|---|---|
| **Close or merge** | 16 register items | Overtaken by later work, answered by a record, or merged into another item. No poll |
| **Confirm by lazy consensus** | 7 register items | The draft already holds a position nobody has argued with. One notice; no poll |
| **Ratify** | 21 records, plus 8 register items they settle | Three polls of Agree / Disagree / Abstain, batched by aspect |
| **Decide** | 41 register items in 14 clusters, plus the 3 drafts, the tooling question, the procurement question and 2 member proposals | Polls, most preceded by a short discussion or a meeting slot |
| **Meeting, not poll** | Release scope, ownership, and strategy | Chair and meeting agenda |

**Three findings shape the order.**

1. **Nothing has ever been ratified.** All 21 decision records say Proposed, and every aspect issue
   on GitHub still reads `status:deliberating` and `needs:owner`. The cheapest progress available
   is ratification. Most records are implemented and tested.
2. **Four items block work in progress:**
   - draft 0022, the PQC migration depths;
   - draft 0023, the grouping and the change core;
   - the deferred validator adapter, without which no Keycloak example gets a tool verdict;
   - the CycloneDX 2.0 poll, which is prepared but unpublished, and whose dates (1 to 6 October)
     need moving.
3. **The OT case reopens a question that was parked as out of scope.** Substation protection
   messages use a key shared by every member of a multicast group. That is exactly Q08.

## 1. Close or merge

| Item | Why it no longer needs a decision | Action |
|---|---|---|
| Q01 Is the PQC migration profile a specification or an illustration? | Overtaken. The profile now lives in the Use Cases section as a worked example, with `pkic.example` identifiers | Close: illustration |
| Q10 Must suppliers name the implementing library? | Answered in part by baseline v0.3: I9 is a MUST that may be withheld. The remaining choice is Q57 | Merge into Q57 |
| Q19 Does the new reference category stay? | Editorial, about the reference register | Close, maintainers' call |
| Q34 Should the completeness statement move into the baseline? | Done. P4 moved in baseline v0.6. The "where it stands" text is out of date | Close with the 0012 ratification |
| Q23 May a profile build on more than one profile? | 0023 depends on single inheritance and shows how to share facts without multiple bases | Close as A with 0023 |
| Q25 How would a sector profile fit? | 0023 answers it: a sector extends its group's base (the baseline or the change core) and adds vocabulary | Close with 0023 |
| Q26 Should a CBOM say what a product will support later? | Option C in practice, and 0007 fixes the form | Close with the 0007 ratification |
| Q35 May a profile narrow an inherited list of values? | Narrowing is settled and checked by 0013. Only widening remains, which is the sector-vocabulary point left open by 0010 | Close narrowing; carry widening into cluster D |
| Q07 Publish the attribute list as its own document? | A release-format question | Merge into N03 |
| Q18 Who watches the formats? | The CycloneDX 2.0 analysis and the versioning notes now do this in practice. The process half belongs with governance | Merge into cluster K |
| Q40 Should the methodology define a topology record? | The overlay in the substation draft is the concrete form of the same need | Merge into Q68 |
| Q09 A proper object for a cryptographic connection | Parked with a revival trigger. The substation analysis found the trigger not met: every conduit sits on a device | Keep parked |
| Q16 SPDX side untested | Waits on SPDX's cryptography model. 0016 covers what can be said now | Keep deferred, trigger: an SPDX crypto profile is published |
| N04 A second worked example from another sector | Answered: IoT, substation (energy) and procurement are worked | Close |
| Q43, Q44 The PQC Maturity Model | Outreach, not methodology. The charter, not the PQCMM, is the precedent for the profile approach | Move to the chair's outreach list |
| Discussion #16 Inventory versus migration framing | Answered by 0009 (orientation is declared) and by the two groups of 0023 | Close with a summary comment |

## 2. Confirm by lazy consensus

Each has a position in the draft that nobody has argued with. One notice at a meeting and in a
Discussion, with two weeks to object, records them. Any objection moves the item to a poll.

| Item | Position recorded |
|---|---|
| Q05 Can enabling a capability need more than one kind of change? | A: one answer per interface |
| Q06 Should "what might break" be free text? | A: free text, SHOULD. The substation draft's structured timing entry stays inside the text |
| Q11 Should "unknown" be more prominent for advisory rules? | A: the report is enough |
| Q12 Must a supplier say why it withholds? | A: the marker alone |
| Q28 What may a roadmap pointer point at? | A: left open |
| Q32 The product-naming rule cannot be fully checked | A: binding, with the limit stated |
| Q52 Distinguish a deferral from a permanent exclusion? | B: in the reasons, not in the schema |

## 3. Ratify

Batched by aspect, following `decisions/adoption-and-readiness.md`. Each record becomes one
Agree / Disagree / Abstain question with a comment box. A record that fails goes back to its aspect
issue.

The readiness note makes an owner a condition, and all twelve aspects are unowned. Either the
group waives that condition for ratification, or owners are named first. That is a meeting
decision.

| Batch | Records | Register items it settles | Ready? |
|---|---|---|---|
| **R1: stable mechanics** | 0003 disclosure model, 0006 carrier range, 0011 rule ids, 0015 claims, 0016 SPDX-only claims, 0017 schemas, 0018 the demonstration | Q24, Q30, Q33, Q48 | Yes. Few open questions touch these, and all are implemented and tested |
| **R2: profile shape and composition** | 0001 product independence, 0004 monotonic extension, 0008 scope, 0009 orientation, 0012 baseline, 0013 constraint monotonicity, 0014 group tightening, 0019 depths | Q02, Q34, Q38, Q49 | After 0022 and 0023 are decided, because both lean on these |
| **R3: facts and vocabulary** | 0002 facts versus judgements, 0005 naming, 0007 status and blocker, 0010 purposes, 0020 vulnerability join, 0021 one word one meaning | Q26, Q27 | After cluster D (names) and the randomness proposal, since 0010 is accepted in part |

## 4. Decide

Grouped into clusters that can each be one discussion and one poll. Priority 1 blocks work in
progress. Priority 2 blocks a use case. Priority 3 is needed before a release. Priority 4 can wait.

### Priority 1: drafts in flight

| Cluster | Items | The choice |
|---|---|---|
| **A. CycloneDX 2.0** | Prepared poll `cyclonedx-2` (5 questions); Q04; Q17 | Carrier stays 1.7 until Ecma ratifies 2.0; `certifications` for module validation; `risks` out of supplier claims; a perspective per profile; send feedback now. Add Q17 (a withheld marker upstream) to the feedback question, and Q04 (a new profile version per format release) as a sixth question |
| **B. PQC migration depths** | Draft 0022 (K1–K10), Q22 | Accept the two-depth family; an interface is a logical boundary (K2); application protocols as services (K7); inheritance from the providing library (K9); the CBOM-to-SBOM link (K10, which answers Q22) |
| **C. Use-case grouping and change core** | Draft 0023, Q64, Q66, Q50, Q51, Q53, naming | Accept the two groups and the change core as a sibling (answers Q64). Is the core target-neutral (Q66)? Where a family is recorded (Q50), whether siblings are re-parented (Q51, now for the core as well as the baseline), and whether depths are numbered (Q53). Keep "change planning" or rename it "migration planning"? |
| **T. Tooling** | The deferred validator adapter | Lift the deferral for two adapter features only: services as interfaces (K7) and inheritance through `provides` (K9). Without them no worked example in either group gets a tool verdict |
| **P. Member proposals** | Issue #9, issue #10 | Add `random-bit-generator` to the run-time dependency list of `pqc-migration-extended#I9` (#9). Add `randomness` as an eighth cryptographic purpose (#10, the open point of 0010) |

### Priority 2: blocks a use case

| Cluster | Items | Blocks | The choice |
|---|---|---|---|
| **D. Names and identity across tools** | Q20, Q21, Q39, Q35 (widening) | Every comparison between tools; rumende's input on issues #1 and #3 | Whose algorithm names (registry); a protocol name list; how a key is identified across tools; how a sector widens an inherited vocabulary |
| **E. Withholding the library** | Q57 (with Q10) | Vulnerability response | Remove withholdability and accept a restricted audience; allow a coarser identifier publicly; or leave it and let the VEX statement carry it |
| **F. Device models and permanent limits** | Q62, Q63, Q65 | IoT, substation, code signing | Who says whether the subject is a model or a deployed device; whether "permanent" is a capability value; whether a rule may require a fact about a process (who can update) |
| **G. System documents** | Q67, Q68 (with Q40), draft 0024 | Substation, service assurance, PKI estate | Is an estate a subject type; what an overlay's verdict says about the documents it cites; the substation decisions O1–O6 |
| **H. Shared keys and shared trust** | Q08, Q46, Q47 | Substation (GOOSE group keys), shared-trust networks | Bring group keys into the model now, or keep them out of scope; a verifier-population attribute; a trust-domain attribute |
| **I. Procurement** | P5 in the baseline? | Procurement, and every disclosure profile | Is "declare where keys are kept at rest, or why there is none" a baseline rule or a procurement rule? |

### Priority 3: before a release

| Cluster | Items | The choice |
|---|---|---|
| **J. Data and harvest-now-decrypt-later** | Q36, Q37, Q45; discussion #35 | Where vendor-stated data facts end and operator-stated facts begin; the confidentiality-lifetime bands; how the operator's half is linked. Lucy Buecking's point in #35 (context that changes over time in rolling CBOMs) belongs here |
| **K. Profile governance** | Q03, Q15, Q18, Q41, Q42, Q61 | Who may publish under the PKIC name; transition periods when a profile tightens; archiving; ownership after publication; notifying consumers of a tightening |
| **L. Conformance and trust in the result** | Q14, Q29; discussions #18 and #37 | Self-declared or independent conformance; signing profiles or identifying them by fingerprint; how a digest is computed (Anton Sokolov's canonicalisation point, #18); whether to add an informative annex on transparency services (SCITT, #37) |
| **M. Confidentiality** | Q54, Q55, Q56 | Whether a profile declares its audience; a variant statement and a split `partial`; whether a structural rule can be met by a withheld declaration |
| **N. Vulnerability statements** | Q58, Q59, Q60 | What a verdict says about embedded vulnerability assertions; finding identifiers; superseded revisions |
| **O. First release** | N01, N02, N03, Q07, Q13, Q31; discussion #14 | Is the procedure the method or guidance; is the model normative; what is in the first release and when. Tied to the December workshop, so this is first among the priority-3 items in time |

### Priority 4: can wait

Strategy and outreach, kept as Discussions and handled in meetings, not polled: positioning against
sector bodies (#15), adoption drivers (#19), and the PQCMM relationship (Q43, Q44).

## 5. Proposed polls

Each poll stays within five to seven questions, matching the prepared CycloneDX 2.0 poll. Questions
are worded as proposals, with Agree / Disagree / Abstain and a comment box, as `polls.yml`
expects. Where a cluster has real alternatives, the options are the alternatives.

| Poll | When | Questions |
|---|---|---|
| **1. CycloneDX 2.0** (prepared) | New dates, after meeting 13 | The five prepared questions. Q17 is added to the feedback question. Q04: "A new CycloneDX release does not by itself require a new profile version; the carrier range is updated editorially." |
| **2. Drafts in flight** | After meeting 13, when 0022 and 0023 have been presented | 1. Accept the two-depth PQC migration family (0022). 2. Accept the use-case grouping and the change core, published beside pqc-migration as a sibling (0023, answers Q64 and Q25). 3. The change core states capability without naming a target; the target belongs to policy (Q66, option C). 4. Build the two adapter features now (services as interfaces, inheritance through `provides`). 5. Add `random-bit-generator` to the run-time dependencies of I9 (#9). 6. Add `randomness` as an eighth cryptographic purpose (#10). |
| **3. Ratify R1** | Alongside poll 2, or the week after | One question each for 0003, 0006, 0011, 0015, 0016, 0017, 0018 |
| **4. Device models and the library** | After a meeting slot on clusters E and F | Q57: three options. Q62: three options. Q63: three options. Q65: three options. P5 in the baseline (cluster I): Agree / Disagree |
| **5. Ratify R2** | After poll 2 closes | 0001, 0004, 0008, 0009, 0012, 0013, 0014, 0019 (eight; split into two polls if that is too many) |
| **6. First release** | Before the December workshop, after a meeting discussion | N01, N02, N03 (three options each), Q13, Q31 |

Clusters D, G, H, J, K, L, M and N go to polls after a discussion has narrowed each one to stated
options. Several of them (D, G, H) depend on input from members with tool or sector experience who
do not use GitHub. Targeted requests to named people will reach them better than a broadcast.

## 6. Discussions: a new list

The six General discussions opened on 17 June (#14–#19) were framing questions for a group that had
not started. Most are now answered by records or drafts, and none has had a comment since August.
Keeping them open suggests the questions are still live.

**Close, each with a short summary comment pointing to where it was answered:**

| Discussion | Answered by |
|---|---|
| #14 How prescriptive should the methodology be? | Carried into cluster O (N01, N02) |
| #16 Inventory versus migration framing | 0009 and the two groups of 0023 |
| #17 How tooling-centric should the methodology be? | 0017 and 0018; the open part is cluster T |
| #18 Format independence without parity | The mappings and 0016; the digest point moves to cluster L |

**Keep:**

- #15 and #19, strategy for meetings.
- #34, #35 and #36, feedback on the position paper chapters, until those chapters are final.
- #37, which becomes the starting post of cluster L.

**Open, one per cluster that is heading for a poll, so that comments gather before a vote:**

| New discussion | Feeds |
|---|---|
| Ratifying the first decisions (R1) | Poll 3 |
| PQC migration depths, the use-case grouping and the change core | Poll 2 |
| Withholding the implementing library | Poll 4 |
| Device models, permanent limits and who can update | Poll 4 |
| System documents and overlays | Cluster G |
| Shared keys and shared trust | Cluster H |
| Names and identity across tools | Cluster D |
| The first release and the December workshop | Poll 6 |

## 7. Housekeeping

- Update `open-questions.md`: mark the closed items with the reason, mark merged items with their
  target, and refresh the out-of-date "where it stands" text on Q10, Q27 and Q34.
- Update the labels on issues #1–#13. Several aspects now have records, and none is still only
  "deliberating".
- Move the CycloneDX 2.0 poll dates, since 1 to 6 October has passed without the poll being
  published.
