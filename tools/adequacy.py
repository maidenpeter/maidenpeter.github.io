"""Reserve adequacy test on Kenya's general insurers, from IRA's quarterly claims settlement statistics.

    python tools/adequacy.py [--repos ..]

Every quarter IRA prints, for each insurer, the amount of claims outstanding at the start, the claims reported,
paid, declined and closed without payment, and the amount still outstanding at the end (KSh thousands, general
liability and general non-liability business, from Q4 2022). Over a year,

    end = start + reported + revisions - paid - declined - closed

so the revisions, the amount by which the estimates of reported claims were raised after they were first set,
can be read from the balances without relying on IRA's printed revisions column. A case reserve set at the right
amount would see revisions near zero on average. The figures on /work/reserve-adequacy/ come from compute(), and
tools/check_figures.py checks figures.ADEQUACY against it.
"""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

YEARS = ("2023", "2024", "2025")            # complete calendar years with amounts
BUSINESS = ("general_liability", "general_non_liability")
MIN_OPEN = 100_000                          # KSh 100m outstanding at the start of the year (KSh thousands)
CHAIN_TOL = 0.01                            # a quarter starts where the last ended, within 1% (or KSh 1m)
UP = 0.05                                   # "raised" means by more than 5% of the year's opening outstanding
MISPRINT = 10                               # a printed revision more than 10 times the claims in play is a misprint

f = lambda v: float(v) if v not in ("", None) else 0.0


def rows(panel):
    return [r for r in csv.DictReader(open(panel, encoding="utf-8")) if r["unit"] == "amount" and r["business"] in BUSINESS]


def year_of(qs, business=None):
    """One insurer's year, from its four quarters (both businesses unless one is named)."""
    pick = lambda q: [r for r in qs[q] if business is None or r["business"] == business]
    allr = [r for q in "1234" for r in pick(q)]
    s = lambda k: sum(f(r[k]) for r in allr)
    start, end = sum(f(r["opening"]) for r in pick("1")), sum(f(r["closing"]) for r in pick("4"))
    released = s("declined") + s("closed") + s("declined_closed")
    reported = s("intimated") + s("revived")
    printed = sum(f(r["revised"]) for r in allr
                  if abs(f(r["revised"])) <= MISPRINT * max(1.0, f(r["opening"]) + f(r["intimated"])))
    misprints = sum(1 for r in allr if abs(f(r["revised"])) > MISPRINT * max(1.0, f(r["opening"]) + f(r["intimated"])))
    # does each quarter start where the one before ended?
    chained = all(abs(sum(f(r["opening"]) for r in pick(q)) - sum(f(r["closing"]) for r in pick(p)))
                  <= CHAIN_TOL * max(1.0, sum(f(r["closing"]) for r in pick(p))) + 1000
                  for p, q in zip("123", "234"))
    return dict(start=start, end=end, reported=reported, paid=s("paid"), released=released,
                raised=end + s("paid") + released - start - reported, printed=printed, misprints=misprints, chained=chained)


def compute(panel, chained_only=False):
    data = rows(panel)
    by = defaultdict(lambda: defaultdict(list))
    for r in data:
        by[(r["company_id"], r["year"])][r["quarter"]].append(r)
    full = {k: qs for k, qs in by.items() if k[1] in YEARS and all(len(qs.get(q, [])) == 2 for q in "1234")}
    ins = {}
    for k, qs in full.items():
        d = year_of(qs)
        if d["start"] >= MIN_OPEN and (d["chained"] or not chained_only):
            ins[k] = d
    rate = lambda d: d["raised"] / d["start"]
    out = dict(insurers=len({c for c, _ in ins}), insurer_years=len(ins),
               misprints=sum(d["misprints"] for d in ins.values()),
               unchained=sum(1 for d in ins.values() if not d["chained"]), years={})
    for y in YEARS:
        ds = [d for (c, yy), d in ins.items() if yy == y]
        S = sum(d["start"] for d in ds)
        rates = sorted(rate(d) for d in ds)
        by_bus = {}
        for b in BUSINESS:
            bs = [year_of(full[k], b) for k in ins if k[1] == y]
            bs = [x for x in bs if x["start"] > 0]
            by_bus[b] = round(100 * sum(x["raised"] for x in bs) / sum(x["start"] for x in bs), 1)
        out["years"][y] = dict(
            n=len(ds), start_bn=round(S / 1e6, 1),
            raised_pct=round(100 * sum(d["raised"] for d in ds) / S, 1),
            printed_pct=round(100 * sum(d["printed"] for d in ds) / S, 1),
            per_100_reported=round(100 * sum(d["raised"] for d in ds) / sum(d["reported"] for d in ds), 1),
            median_pct=round(100 * (rates[len(rates) // 2] if len(rates) % 2 else (rates[len(rates) // 2 - 1] + rates[len(rates) // 2]) / 2), 1),
            up=sum(1 for v in rates if v > UP), down=sum(1 for v in rates if v < -UP),
            liability_pct=by_bus["general_liability"], non_liability_pct=by_bus["general_non_liability"])
    three = [c for c in {c for c, _ in ins} if all((c, y) in ins for y in YEARS)]
    out["three_years"] = len(three)
    out["up_every_year"] = sum(1 for c in three if all(rate(ins[(c, y)]) > UP for y in YEARS))
    out["down_every_year"] = sum(1 for c in three if all(rate(ins[(c, y)]) < -UP for y in YEARS))
    out["persistence"] = {}
    for a, b in zip(YEARS, YEARS[1:]):
        cs = sorted(c for c in {c for c, _ in ins} if (c, a) in ins and (c, b) in ins)
        out["persistence"][f"{a}-{b}"] = dict(n=len(cs), spearman=round(spearman([rate(ins[(c, a)]) for c in cs], [rate(ins[(c, b)]) for c in cs]), 2))
    # one dot per insurer and year, without names, for the chart: (year, rate %, start KSh bn)
    out["dots"] = sorted([[y, round(100 * rate(d), 1), round(d["start"] / 1e6, 2)] for (c, y), d in ins.items()])
    # each insurer in all three years: its three rates, ordered by the average, without names
    out["insurers3"] = sorted([[round(100 * rate(ins[(c, y)]), 1) for y in YEARS] for c in three], key=lambda v: sum(v))
    return out


def spearman(a, b):
    def rk(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); out = [0.0] * len(v)
        i = 0
        while i < len(order):           # average ranks over ties
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                out[order[k]] = (i + j) / 2
            i = j + 1
        return out
    ra, rb = rk(a), rk(b); n = len(a); ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5


def panel_path(repos):
    return Path(repos) / "ira-kenya-data" / "data" / "processed" / "claims_panel.csv"


def liberty_runoff(repos):
    """Liberty Kenya's gross IFRS 17 claims development table (in kenya-reserve-check): the latest estimates of every
    accident year with two or more, against their estimates at the end of the year, in percent. Its estimates
    include IBNR, which IRA's claims tables do not show."""
    p = Path(repos) / "kenya-reserve-check" / "data" / "extracted" / "liberty" / "triangle.csv"
    est = defaultdict(dict)
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r["basis"] == "gross" and r["measure"] == "estimate":
            est[r["accident_year"]][int(r["dev"])] = float(r["value"])
    rows = [v for v in est.values() if len(v) >= 2]
    first, latest = sum(v[min(v)] for v in rows), sum(v[max(v)] for v in rows)
    return round(100 * (latest - first) / first, 1)


def everything(repos):
    """What the page shows: the main reading, the same on chained quarters only, and Liberty's table for contrast."""
    out = compute(panel_path(repos))
    strict = compute(panel_path(repos), chained_only=True)
    out["chained"] = dict(insurer_years=strict["insurer_years"],
                          raised_pct={y: v["raised_pct"] for y, v in strict["years"].items()})
    out["liberty_runoff_pct"] = liberty_runoff(repos)
    bad = [abs(f(r["revised"])) for r in rows(panel_path(repos)) if r["year"] in YEARS
           and abs(f(r["revised"])) > MISPRINT * max(1.0, f(r["opening"]) + f(r["intimated"]))]
    out["misprint_bn"] = round(max(bad) / 1e6) if bad else 0
    return out


JSON = Path(__file__).with_name("adequacy.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--write", action="store_true", help="write tools/adequacy.json, which the page is built from")
    a = ap.parse_args()
    res = everything(a.repos)
    if a.write:
        JSON.write_text(json.dumps(res, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"wrote {JSON.name}")
    print(json.dumps({k: v for k, v in res.items() if k not in ("dots", "insurers3")}, indent=1))
