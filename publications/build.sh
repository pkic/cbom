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
  [publication-2-profiles-and-conformance]=CBOM-Profiles-Publication-2-Profiles-and-conformance
  [publication-3-applying-the-methodology]=CBOM-Profiles-Publication-3-Applying-the-methodology
  [domain-operational-technology]=CBOM-Profiles-Application-domain-Operational-technology
  [domain-saas-and-cloud-services]=CBOM-Profiles-Application-domain-SaaS-and-cloud-services
  [domain-telecommunications]=CBOM-Profiles-Application-domain-Telecommunications
  [domain-financial-services]=CBOM-Profiles-Application-domain-Financial-services
  [domain-hsm-and-key-management]=CBOM-Profiles-Application-domain-HSMs-and-key-management
  [domain-healthcare]=CBOM-Profiles-Application-domain-Healthcare
  [domain-automotive]=CBOM-Profiles-Application-domain-Automotive
)
for src in "${!NAMES[@]}"; do
  pandoc "$src.md" \
    -f markdown-smart-implicit_figures \
    --reference-doc=../templates/reference.docx \
    --lua-filter=../links.lua \
    --resource-path=. \
    -o "$OUT/${NAMES[$src]}.docx"
  # The document date is the draft date in the header line ("Working Draft 0.1 · Nov 26, 2026"),
  # so a rebuild gives a byte-identical file until the author changes the source.
  date=$(python3 -c 'import re,sys,datetime
m=re.search(r"^Working Draft [^\n]*?(\w{3} \d{1,2}, \d{4})", open(sys.argv[1]).read(), re.M)
print(datetime.datetime.strptime(m.group(1), "%b %d, %Y").strftime("%Y-%m-%dT00:00:00Z") if m else "2026-01-01T00:00:00Z")' "$src.md")
  TZ=UTC python3 ../postprocess.py "$OUT/${NAMES[$src]}.docx" --date "$date"
  echo "built ${NAMES[$src]}.docx"
done
