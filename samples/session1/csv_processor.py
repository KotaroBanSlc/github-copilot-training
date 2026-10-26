import csv
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent
IN_FILE = BASE / "data" / "sample.csv"
OUT_FILE = BASE / "data" / "sample_output.csv"


def f(p):
    a = []
    with open(p, "r", encoding="utf-8") as fp:
        r = csv.DictReader(fp)
        for x in r:
            a.append(x)
    return a


def g(a, k1, k2):
    b = {}
    for x in a:
        kk = x[k1]
        if kk not in b:
            b[kk] = 0
        try:
            v = int(x[k2]) * int(x["unit_price"])
        except Exception:
            v = 0
        b[kk] = b[kk] + v
    return b


def h(a):
    tmp = {}
    for x in a:
        rg = x["region"]
        pr = x["product"]
        if rg not in tmp:
            tmp[rg] = {}
        if pr not in tmp[rg]:
            tmp[rg][pr] = 0
        try:
            tmp[rg][pr] += int(x["quantity"])
        except Exception:
            pass
    out = []
    for rg, m in tmp.items():
        for pr, q in m.items():
            out.append({"region": rg, "product": pr, "total_quantity": q})
    return out


def w(rows, p):
    if not rows:
        return
    fn = list(rows[0].keys())
    with open(p, "w", encoding="utf-8", newline="") as fp:
        wr = csv.DictWriter(fp, fieldnames=fn)
        wr.writeheader()
        for r in rows:
            wr.writerow(r)


def do_it():
    if not IN_FILE.exists():
        print("input not found", file=sys.stderr)
        return 1
    a = f(IN_FILE)
    s1 = g(a, "region", "quantity")
    s2 = h(a)
    print("=== sales by region ===")
    for k, v in s1.items():
        print(k, v)
    print("=== quantity by region/product ===")
    for x in s2:
        print(x)
    w(s2, OUT_FILE)
    print("written:", OUT_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(do_it())
