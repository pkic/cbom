# 0026. A connection is the join of its two ends

- **Status:** Proposed
- **Date:** 2026-11-01
- **Aspect:** 3.3 — Format-independent attribute model, and the relationship model
- **Topic / issue:** the parked first-class attributed edge model; Q40 (topology record)
- **Deciders:** chair's call, for review by the working group
- **Decision rule applied:** owner call, provisional

## Context

The relationship model treats an interface as an edge between two endpoints. Neither CycloneDX
nor SPDX has an object for that edge, so a first-class attributed edge model was parked. Its
revival trigger was a consumer that needs per-connection posture which sits on no single
endpoint.

The Keycloak baseline met that trigger. The readiness-gap result classifies key establishment
at the ingress as `enabled-not-negotiated`, which says the limit is the other endpoint. Nothing in
the records names the other endpoint, so the operator cannot act on the finding. The Inventory
section needs the same thing to compose posture along a path, and Q40 asks whether the methodology
defines a topology record.

## Options considered

- **Option A — an edge object in the CBOM.** A new component kind, or CycloneDX 2.0 blueprint
  flows. (Trade-off: a product record cannot know its peers, because every deployment has
  different ones. Blueprint flows describe a deployed system for threat analysis and carry
  encryption as a boolean. Either route waits on format changes.)
- **Option B — a peer pointer in deployment records, and edge findings computed by an
  evaluation.** (Trade-off: the connection has no record of its own. Relationships that are not
  pairwise stay out of reach.)
- **Option C — leave topology to inventory tooling.** (Trade-off: every organization builds its
  own linkage, and comparison across an estate stays out of reach.)

## Decision

Option B, provisionally, in its narrowest useful form.

1. **The pointer.** Deployment Disclosure v0.2 adds interface rule I4, `peerInterface`, at MAY. Its
   value is a BOM-Link to the interface at the far end of the connection, in a document the record
   cites by hash, or the literal `peer-not-recorded`. It is a list, because a server interface
   usually has several clients. It is withholdable, because it reveals internal topology. Either
   end may state it. Product records never carry it.
2. **The edge.** A connection is identified by its two ends, each a subject identifier and an
   interface id. An evaluation joins the ends. Nothing stores the connection itself.
3. **The findings.** `evaluate_policy.py` gains the method `edge-posture`. For each purpose it says
   whether the connection meets the target and, if not, which end limits it, with the limiting
   end's product capability where its product record states one. The example policy
   `pkic.example.policy.edge-posture` v0.1 reuses the readiness-gap classification and targets,
   so the two results can be read together. Findings are dated judgements and live in the result
   (decision 0002).
4. **The worked example.** The database team's configured record for the PostgreSQL cluster names
   Keycloak's `int-db` interface. Evaluated with the Keycloak records, key establishment is
   `limited-by-end`: the database permits X25519MLKEM768, and Keycloak's end does not, because its
   Java provider is blocked (JEP 527). Entity authentication is `neither-end-permits`.
5. **Out of scope.** Composing posture along a whole path stays with the inventory. Group
   relationships, such as a key shared by a cluster, stay parked. Their revival trigger is a
   consumer that needs posture for a shared key or a membership that pairwise edges cannot express.

## Rationale

The pointer keeps product records independent of any deployment. It reuses what Baseline v1
already validates: BOM-Links, hashes on cited documents, and the `refersToCited` constraint. A
finding about a connection is a judgement, so it belongs in a dated result rather than in either
end's record. This is the smallest change that answers the question the readiness gap raises:
which endpoint is the limit.

## Consequences

- **Artefacts.** `profile-deployment-disclosure.rules.json` v0.2; `validate_cbom.py` resolves a list
  of pointers; `evaluate_policy.py` and `policy.schema.json` gain `edge-posture`;
  `policies/policy-edge-posture.policy.json`; `examples/cbom-postgres-deployment-configured.cdx.json`;
  `examples/results/result-edge-posture-sso-db.json`. The tests check the example's verdicts, that
  the result reproduces, and that it names Keycloak's end as the limit.
- **I4 changes no verdict.** A pointer that does not resolve is reported as a warning. The
  evaluator reports it as `peer-not-found` or `peer-not-supplied`.
- **Pages.** Model, Formats, Inventory, Policy Evaluation, Terms and Files describe the join.
- **Q40** is settled provisionally for pairwise connections.
