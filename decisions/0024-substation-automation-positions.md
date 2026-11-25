# 0024. The substation automation use case: two documents, a separate key plane, and a system subject

- **Status:** Proposed
- **Date:** 2026-11-16
- **Aspect:** 3.9 — Building one profile on another (with consequences for 3.1 and 3.3)
- **Topic / issue:** the OT use case draft (`docs/use-cases/substation.html`); Q67, Q68
- **Deciders:** chair's call, for review by the working group
- **Decision rule applied:** owner call, provisional

## Context

The OT use case drafted six positions (O1 to O6) on 4 October 2026, and record 0023 reserved this
number for them. Two design questions were left open, and the draft also asked for a whole system
to be accepted as the subject of a CBOM, which sits against Q67. The use case is being brought to
the same state as the Keycloak example for Release 1: positions closed, a component profile
published and checked, and a worked record evaluated by the reference validator.

## Options considered

For the system subject:

- **Option A — no system subject.** The integrator's facts go into an operator deployment record.
  (Trade-off: a system design is reused across many substations, so it is not one deployment, and
  the integrator is not the operator.)
- **Option B — a `system` subject type, accepted only by the system overlay.** One design, not a
  site. (Trade-off: a third subject type, kept narrow.)
- **Option C — an estate subject.** (Trade-off: Q67 already decided that an estate is an
  aggregation outside profiles.)

## Decision

**Positions O1 to O6 are adopted.**

- **O1.** The OT use case is the substation automation system, named by its decision.
- **O2.** Two profiles: a component profile extending the change core, and a system overlay.
- **O3.** The data plane and the key plane are separate interfaces, linked by `keyStoreRef`. The
  component profile requires `keyStoreRef` on every service interface.
- **O4.** Real-time limits are integration constraints, not a new attribute.
- **O5.** A conduit is an interface of the device that implements it. Connections are joined
  through deployment records; there is no edge object (decision 0026).
- **O6.** Values are illustrative until a supplier volunteers a product.

**The two design questions are closed.**

- `certificationImpact` is a component fact. The supplier states what enabling an interface's
  capability would trigger for its product: `none`, `retest`, `recertification`, or
  `not-applicable` where no capability is planned, with the scheme named in
  `certificationScheme`. The operator's own type approval stays in the operator's register.
- `usage` stays in the system overlay. Whether it becomes a general facility for derived CBOMs is
  carried past Release 1.

**The system subject is Option B.** A `system` subject type names one system design, such as one
substation automation design reused across sites. Only the system overlay accepts it. An estate of
sites stays outside profiles, as Q67 decided.

**What is published.** The component profile `pqc-migration-ot` v0.1 extends the change core v0.1
and adds four rules: `certificationImpact` (I1), `certificationScheme` (I2), `keyStoreRef` on
service interfaces (I3) and `verifierReplaceable` (I4). The update-path rule the draft numbered
P-OT1 is the change core's P2, and the real-time rule it numbered I-OT5 is the change core's I9, so
neither is restated. A worked record of one illustrative protection IED conforms to it, and two
variants each fail one rule.

**What is not published yet.** The `sas-system` overlay is described in the use case and has no
rules file. It needs the `system` subject type in the validator, and reporting of cited verdicts
beside the overlay's own (Q68). Both are tooling carried past Release 1.

## Rationale

Every position follows from rules the methodology already has: monotonic extension, the black-box
boundary, judgements kept in policy, and connections as joins. The component side can be built and
tested now with the existing tools, so it is. The overlay cannot, and publishing a rules file the
validator cannot evaluate would claim more than the methodology delivers.

## Consequences

- `profile-change-core.rules.json` and `profile-pqc-migration-ot.rules.json` are published, with
  `examples/cbom-ot-protection-ied-product.cdx.json` and two failing variants, built by
  `tools/build_ot_examples.py`.
- The Terms section defines `updateMechanism`, `keyReplaceable`, `verifierReplaceable`,
  `certificationImpact`, `certificationScheme`, `usage` and `conduitRef`, and adds the OT protocol
  names to the list.
- The substation page records these positions as decided, and marks the overlay as carried past
  Release 1.
- Standards facts the findings depend on were checked on 16 November 2026: IEC 62351-9:2023 provides
  no post-quantum measures; G-IKEv2 is RFC 9838 (November 2025), which obsoletes RFC 6407; ML-KEM
  for IKEv2 was approved by the IESG and is in the RFC Editor queue, not yet an RFC. No public
  source was found for post-quantum work on IEC 62351-3 in TC 57 WG 15.

## Links

- Record 0023 (the change core), 0026 (connections as joins).
- Q67 (an estate is an aggregation), Q68 (overlay verdicts).
