#!/usr/bin/env python3
"""Check that every fixture pinning an example profile pins its current version.

A fixture that extends a profile names the base by exact version, which is the
behaviour under test: a pin that silently followed the base would defeat the
point of pinning. The cost is that bumping a profile version invalidates every
fixture pinning it, and the resulting failure surfaces somewhere unhelpful —
`load_profile` raises on the version mismatch before it reaches the check the
fixture was written to exercise, so the test that breaks is an unrelated
assertion about some word missing from the output.

Run from the repository root, or with the two directories as arguments:

    python3 tests/check-fixture-pins.py [methodology_dir] [fixtures_dir]

Exit codes: 0 all pins current, 1 one or more stale, 2 a directory was unreadable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METHODOLOGY = ROOT / "docs" / "methodology"
DEFAULT_FIXTURES = ROOT / "tests" / "fixtures"


def versions(directory: Path) -> dict[str, str]:
    out = {}
    for path in sorted(directory.glob("profile-*.rules.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            print(f"could not read {path.name}: {err}", file=sys.stderr)
            continue
        if "profileId" in d and "version" in d:
            out[d["profileId"]] = str(d["version"])
    return out


def main(argv: list[str]) -> int:
    methodology = Path(argv[1]) if len(argv) > 1 else DEFAULT_METHODOLOGY
    fixtures = Path(argv[2]) if len(argv) > 2 else DEFAULT_FIXTURES
    for d in (methodology, fixtures):
        if not d.is_dir():
            print(f"not a directory: {d}", file=sys.stderr)
            return 2

    current = versions(methodology)
    stale = []
    for path in sorted(fixtures.glob("profile-*.rules.json")):
        try:
            ext = (json.loads(path.read_text(encoding="utf-8")).get("extends") or {})
        except (OSError, ValueError):
            continue
        pid, ver = ext.get("profileId"), ext.get("version")
        if pid in current and str(ver) != current[pid]:
            stale.append(f"{path.name} pins {pid} v{ver}, which is now v{current[pid]}")

    for s in stale:
        print(f"     {s}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
