#!/usr/bin/env python3
"""Check that the demonstration page shows what the reference validator says.

The page renders docs/methodology/demo-reports.json and evaluates nothing
itself. This check regenerates the reports with validate_cbom.py and fails if
the committed file differs, and checks that the page loads that file and holds
no copy of any rules file (decision 0018).

Usage:  python3 tests/check-demo.py
Exit:   0 the page agrees with the tool, 1 otherwise
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "docs", "methodology", "demo.html")


def main():
    failures = 0
    html = open(PAGE, encoding="utf-8").read()
    if 'fetch("demo-reports.json")' in html:
        print("  ok   the page renders the generated reports")
    else:
        failures += 1
        print("  FAIL the page renders the generated reports\n     demo.html does not load demo-reports.json")
    if re.search(r'"(productRules|interfaceRules|groupRules)"', html):
        failures += 1
        print("  FAIL the page holds no copy of the rules\n     a rules section appears in demo.html")
    else:
        print("  ok   the page holds no copy of the rules")
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "tools", "build_demo_reports.py"), "--check"])
    if rc == 0:
        print("  ok   the committed reports are what validate_cbom.py produces today")
    else:
        failures += 1
        print("  FAIL the committed reports are what validate_cbom.py produces today\n"
              "     regenerate with: python3 tools/build_demo_reports.py")
    print("  the demonstration agrees with the reference tool" if not failures else
          "  %d problem(s) with the demonstration" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
