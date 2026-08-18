# 0005. Attribute names state what is disclosed, not what it implies

- **Status:** Proposed
- **Date:** 2026-08-07
- **Aspect:** 3.7 — Vocabularies & normalisation
- **Topic / issue:** #3
- **Deciders:** drafted while building the worked example; awaiting working-group ratification
- **Decision rule applied:** lazy consensus (pending)

## Context

Two profiles were drafted with overlapping subject matter. The baseline asks what an interface
uses; the migration profile asks what it can be made to use. Without a convention these produce
name pairs whose relationship a reader has to infer, and nothing prevents a third profile from
choosing a third spelling for the same idea.

## Options considered

- **Option A — name each attribute as its author sees fit.** No overhead (trade-off: the same
  concept acquires several names across profiles, which defeats reuse and complicates mapping).
- **Option B — a stated convention.** Present state takes the bare name, declared capability
  takes a `Supported` suffix, sets take a plural, and no name asserts a conclusion (trade-off:
  a rule for authors to learn, and some existing names must change).

## Decision

Option B. `keyExchange` is what an interface uses now; `keyExchangeSupported` is what it can be
configured to use. Plurals indicate a set of values. Names describe disclosure only, so
`pqcReady` and similar are excluded, consistent with decision 0002. The conventions are stated
in the Method section and the terms deliberately not used are listed in the glossary.

## Rationale

The distinction between present state and declared capability is the one a migration planner
depends on, and a suffix makes it visible in the name rather than in prose the reader may not
have. A convention also gives reviewers something to check a proposed profile against.

## Consequences

`*Current` was rejected as redundant with the bare form. Existing attribute names were reviewed
against the convention when the migration profile was written. Mapping tables become more
predictable, since the convention constrains what a name can mean before the mapping is read.

## Links

- Naming conventions subsection of the Method section.
- Terms section, "Terms deliberately not used".
- Decision 0002 (facts rather than judgements).
