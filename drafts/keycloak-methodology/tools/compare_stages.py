#!/usr/bin/env python3
"""Show the readiness gap one interface at a time, by following correspondsTo.

Joins a product record (implemented), a deployment record (configured) and an
observation (observed), and prints one row per logical interface with the value
each stage reports. Nothing is merged: each value is read from its own document.

Usage: python3 compare_stages.py <product> <configured> <observed>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluate_draft as E  # noqa: E402

ATTRS = ("keyExchange", "encryption", "authentication")


def fmt(v):
    if v is None:
        return "-"
    return ", ".join(v) if isinstance(v, list) else str(v)


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    reg = E.Registry()
    docs = [reg.add(p) for p in argv[1:]]
    stages = [E.extract(d, reg)[1] for d in docs]
    prod, conf, obs = ({i["interfaceId"]: i for i in s} for s in stages)

    def target(i):
        _doc, ref = E.split_bomlink(i.get("correspondsTo"))
        return ref

    conf_by_prod = {target(i): i for i in conf.values() if target(i)}
    obs_by_conf = {target(i): i for i in obs.values() if target(i)}
    rows = []
    for pid, p in prod.items():
        c = conf_by_prod.get(pid)
        o = obs_by_conf.get(c["interfaceId"]) if c else None
        rows.append((pid, p, c, o))
    for cid, c in conf.items():
        if c.get("correspondsTo") == "no-product-document":
            rows.append(("none:" + cid.split(":")[-1], None, c, obs_by_conf.get(cid)))
    for attr in ATTRS:
        print("\n### %s\n" % attr)
        print("| Product interface | implemented | configured | observed |")
        print("|---|---|---|---|")
        for pid, p, c, o in rows:
            print("| `%s` | %s | %s | %s |" % (
                ("(no product) " + pid[5:]) if pid.startswith("none:") else pid.split(":")[-1], fmt(p.get(attr)) if p else "no product record",
                fmt(c.get(attr)) if c else "not configured",
                fmt(o.get(attr)) if o else ("not observed" if c else "-")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
