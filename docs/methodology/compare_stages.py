#!/usr/bin/env python3
"""Show what each lifecycle stage reports for each interface, by following correspondsTo.

Joins a product record (implemented), a deployment record (configured) and an
observation (observed), and prints one row per logical interface with the value
each record states. Nothing is merged: each value is read from its own record.
The readiness-gap policy (evaluate_policy.py) makes the judgement; this tool
only lays the facts side by side.

Usage: python3 compare_stages.py <product> <configured> <observed>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_cbom as V  # noqa: E402

ATTRS = ("keyExchange", "encryption", "authentication")


def fmt(v):
    if v is None:
        return "-"
    return ", ".join(v) if isinstance(v, list) else str(v)


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    reg = V.Registry()
    docs = [reg.add(p) for p in argv[1:]]
    prod, conf, obs = ({i["interfaceId"]: i for i in V.extract_interfaces(d, reg)} for d in docs)

    def target(i):
        return V.split_bomlink(i.get("correspondsTo"))[1]

    conf_by_prod = {target(i): i for i in conf.values() if target(i)}
    obs_by_conf = {target(i): i for i in obs.values() if target(i)}
    rows = [(pid.split(":")[-1], p, conf_by_prod.get(pid)) for pid, p in prod.items()]
    rows += [("(no product record) " + cid.split(":")[-1], None, c) for cid, c in conf.items()
             if c.get("correspondsTo") == "no-product-document"]
    for attr in ATTRS:
        print("\n### %s\n" % attr)
        print("| Interface | implemented | configured | observed |")
        print("|---|---|---|---|")
        for name, p, c in rows:
            o = obs_by_conf.get(c["interfaceId"]) if c else None
            print("| `%s` | %s | %s | %s |" % (
                name, fmt(p.get(attr)) if p else "-",
                fmt(c.get(attr)) if c else "not configured",
                fmt(o.get(attr)) if o else ("not observed" if c else "-")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
