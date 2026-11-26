#!/usr/bin/env bash
# Builds the Word versions of the publications from the Markdown sources.
# Usage: bash publications/build.sh            (from the repository root)
#        CBOM_TAG=release-1 bash publications/build.sh
set -euo pipefail
cd "$(dirname "$0")/src"
export CBOM_TAG="${CBOM_TAG:-release-1}"
OUT=${OUT:-../../docs/assets/publications}
declare -A NAMES=(
  [publication-1-foundations]=CBOM-Profiles-Publication-1-Foundations
)
for src in "${!NAMES[@]}"; do
  pandoc "$src.md" \
    -f markdown-smart-implicit_figures \
    --reference-doc=../templates/reference.docx \
    --lua-filter=../links.lua \
    --resource-path=. \
    -o "$OUT/${NAMES[$src]}.docx"
  python3 ../postprocess.py "$OUT/${NAMES[$src]}.docx"
  echo "built ${NAMES[$src]}.docx"
done
