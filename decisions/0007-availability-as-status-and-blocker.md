# 0007. Forward-looking capability is stated as a status and a blocker, not a date

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.10 — Forward-looking / roadmap information
- **Topic / issue:** #10
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

A consumer planning a migration needs to know when an interface that is not yet quantum-safe
will become so. The first draft answered this with a `plannedAvailability` date on each
interface. Reviewing it against how products are actually released showed the shape was wrong:
interfaces do not gain capability independently of one another, and a date offered for an
interface whose blocker is an unfinished standard is not a date the vendor can keep.

## Options considered

- **Option A — a date per interface.** Directly answers the planner's question (trade-off:
  implies per-interface release independence that does not exist, and produces dates whose
  reliability varies by an order of magnitude with no way to tell which is which).
- **Option B — status, blocker and roadmap reference.** `capabilityStatus` says where the
  capability stands, `blockedBy` says what is preventing it, `roadmapRef` points at whatever
  commitment the vendor is willing to make (trade-off: the consumer does not get a date directly
  and must follow the reference or ask).

## Decision

Option B. `plannedAvailability` was removed. The migration profile carries `capabilityStatus`,
`blockedBy` — required whenever the status is anything other than available — and `roadmapRef`.
A date, where a vendor offers one, belongs to the release commitment the reference points at,
not to the interface record.

## Rationale

The blocker is the more useful field. `standard` tells a planner that no date is credible until
the specification settles, `dependency` points at a third party whose schedule the vendor does
not control, and `implementation` indicates work the vendor does control. A planner responds to
each of these differently, whereas a date on its own supports no such response. Availability is
also a property of a change event, so recording it against an interface places it on the wrong
object.

## Consequences

`blockedBy` is conditionally required, which exercised the `requiredWhen` construct and is
covered by the tests. Whether `capabilityStatus` is the right granularity — per interface, or
per algorithm role within an interface — remains open and is recorded in the open questions
register.

## Links

- PQC Migration section of the methodology documentation, rules M10 to M12.
- Open questions register, aspect 3.10.
