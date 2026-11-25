#!/usr/bin/env python3
"""The published example claim still describes the published product record.

claim-example.json binds itself to cbom-keycloak-product.cdx.json by SHA-256 digest. Rebuilding
the examples changes that digest, so the claim has to be regenerated with it. This check runs the
reference validator's --verify-claim and fails if the claim no longer matches the document or no
longer reproduces its verdicts.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "docs", "methodology")

proc = subprocess.run(
    [sys.executable, "validate_cbom.py", "examples/cbom-keycloak-product.cdx.json",
     "claim-example.json", "--verify-claim"],
    cwd=M, capture_output=True, text=True)
print("Example claim")
if proc.returncode != 0:
    print(proc.stdout[-1500:])
    print("  FAIL  claim-example.json does not verify against the product record (exit %d)."
          " Regenerate it with validate_cbom.py ... --claim." % proc.returncode)
    sys.exit(1)
print("  ok    claim-example.json verifies against cbom-keycloak-product.cdx.json")
