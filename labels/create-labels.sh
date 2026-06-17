#!/usr/bin/env bash
#
# Create (or update) the Working Group label scheme using the GitHub CLI.
#
# Prerequisites:
#   - gh CLI installed and authenticated:  gh auth login
#   - run from inside a clone of the repo, OR pass the repo explicitly:
#         REPO=owner/name ./labels/create-labels.sh
#
# Idempotent: --force updates a label if it already exists, so this is safe to re-run.

set -euo pipefail

REPO_FLAG=()
if [[ -n "${REPO:-}" ]]; then
  REPO_FLAG=(--repo "$REPO")
fi

mk() {
  # mk <name> <color-hex> <description>
  gh label create "$1" --color "$2" --description "$3" --force "${REPO_FLAG[@]}"
}

# --- Aspect (blue) ---
mk "aspect:objective-scope"        1D76DB "3.1 Profile objective & scope"
mk "aspect:identity-metadata"      1D76DB "3.2 Profile identity & metadata"
mk "aspect:attribute-model"        1D76DB "3.3 Format-independent attribute model"
mk "aspect:obligations"            1D76DB "3.4 Obligation levels & conformance semantics"
mk "aspect:conformance-validation" 1D76DB "3.5 Conformance & validation"
mk "aspect:format-mapping"         1D76DB "3.6 Mapping to CycloneDX & SPDX (cross-cutting)"
mk "aspect:normalisation"          1D76DB "3.7 Vocabularies & normalisation (cross-cutting)"
mk "aspect:layering"               1D76DB "3.8 Relationship to SBOM/HBOM & layering"
mk "aspect:extensibility"          1D76DB "3.9 Extensibility & profile composition"
mk "aspect:roadmap"                1D76DB "3.10 Forward-looking / roadmap information"
mk "aspect:governance"             1D76DB "3.11 Profile governance & lifecycle"
mk "aspect:regulatory"             1D76DB "3.12 Regulatory & policy alignment"
mk "aspect:templates-tooling"      1D76DB "3.13 Templates, worked examples & tooling"

# --- Status (traffic light) ---
mk "status:deliberating" FBCA04 "Open argument — options being explored"
mk "status:converging"   D4C5F9 "Options narrowed; proposed decision posted"
mk "status:decided"      0E8A16 "Decision taken and recorded in /decisions"
mk "status:blocked"      B60205 "Cannot proceed until a dependency is resolved"
mk "status:deferred"     C2E0C6 "Parked deliberately; revisit later"

# --- Orientation (purple) ---
mk "orientation:inventory" 5319E7 "Relevant to inventory-oriented profiles"
mk "orientation:migration" 5319E7 "Relevant to migration-oriented profiles"

# --- Type ---
mk "type:discussion" 006B75 "Open-ended deliberation"
mk "type:decision"   006B75 "A concrete choice to be resolved"
mk "type:editorial"  BFDADC "Spec wording / structure, no policy change"
mk "type:dependency" BFDADC "Cross-cutting item referenced by several aspects"

# --- Workflow helpers ---
mk "needs:owner"       E99695 "No aspect owner assigned yet"
mk "good-first-topic"  7057FF "Self-contained; good entry point for new contributors"

echo "Labels created/updated."
