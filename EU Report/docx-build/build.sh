#!/usr/bin/env bash
# Build the Word version from the published markdown.
# Run from this directory, with Cryptographic-Transparency-in-the-Supply-Chain.md
# and figures/ in the parent directory.
set -e
cd "$(dirname "$0")"
cp ../Cryptographic-Transparency-in-the-Supply-Chain.md report.md
ln -sfn ../figures figures 2>/dev/null || cp -r ../figures .
python3 mkpandoc.py
pandoc report.pandoc.md -f markdown-implicit_figures+pipe_tables \
  --reference-doc=reference.docx --resource-path=.:figures -o report.docx
rm -rf work && mkdir work && (cd work && unzip -qo ../report.docx)
(cd work && python3 ../fixtables.py && python3 ../fixtoc.py)
rm -f ../Cryptographic-Transparency-in-the-Supply-Chain.docx
(cd work && zip -qXr ../../Cryptographic-Transparency-in-the-Supply-Chain.docx .)
echo "wrote ../Cryptographic-Transparency-in-the-Supply-Chain.docx"
