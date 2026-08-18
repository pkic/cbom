# 0001. Profile rules are product- and instance-independent

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.1 — Profile objective & scope
- **Topic / issue:** #4
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

An early draft of the worked example profile required `interfaceId` to equal `"nginx-https"`.
That made the profile applicable to exactly one product, which defeats the purpose of a
methodology intended for any sector to adopt. The question is what a profile is permitted to
constrain.

## Options considered

- **Option A — allow rules to name instances.** Simple to write and to check (trade-off:
  the profile applies to one product only, and every adopter must rewrite it).
- **Option B — constrain kinds and counts only.** Rules describe categories of interface and
  required attributes (trade-off: cannot express a requirement about one named system, which
  must instead be handled by deployment policy).

## Decision

Option B. No rule in a profile may name a product, a vendor, or an interface instance.
Structural rules constrain the set of interfaces by kind and count; per-attribute rules apply
uniformly to every declared interface. `interfaceId` remains a producer-chosen label that the
profile does not constrain.

## Rationale

A profile that names an instance is a configuration, not a specification. The property that
makes the methodology reusable is that the same profile text applies unchanged to any product
in scope, which requires that nothing in it refers to a particular one.

## Consequences

The baseline profile was rewritten to this shape. Product-level rules exist specifically to
catch omission, since per-attribute rules say nothing about an interface that was never
declared. Anyone reviewing a proposed profile should check for instance names as a first pass.

## Links

- Profile section of the methodology documentation.
- Method section, step 7 and the failure-modes table.
