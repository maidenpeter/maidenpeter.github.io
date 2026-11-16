"""Write assets/ask/data.json, the derived figures behind /ask/.

    python tools/build_ask.py --repos ..

Reads the processed tables in ira-kenya-data, the scorecard outputs in ira-kenya-reinsurance and the six paid
triangles in tools/cas_triangles.json. Writes only what the answers need, at the level of detail the Insurer
Explorer already publishes (per insurer, per class, per year). The field list is in docs/ask-plan.md, and
tools/check_ask.py fails on anything outside it. Same inputs, same bytes.
"""
import argparse, ast, csv, json, os, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import chain_ladder, load_triangles
from figures import IFRS17

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ask" / "data.json"
YEARS = [2016] + list(range(2018, 2026))     # full years with a Q4 return online (no Q4 2017 workbook)
CYEARS = list(range(2018, 2026))             # class years, as the Loss Map (2016 has no earned premium by class)
CLASS_MAP = {"Motor Commercial PSV": "Motor Commercial"}   # as ira-kenya-insurance/src/profitability/build.py
CLASS_TABLES = ["gross_premium", "net_earned_premium", "claims_incurred", "underwriting_result"]
TOT_LINES = ["gross_direct_premium", "inward_reinsurance", "net_earned_premium", "incurred_claims",
             "net_commissions", "management_expenses", "underwriting_result", "investment_income"]
PILLARS = ["pillar_balance_sheet", "pillar_operating", "pillar_business_profile", "pillar_return_quality"]


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    return float(v) if v not in ("", None) else 0.0


def k3(x):
    """KSh thousands to the shilling: an int when whole, so the file stays short."""
    x = round(x, 3) + 0.0
    return int(x) if x == int(x) else x


def short(name):
    """The scorecard page's short name (ira-kenya-reinsurance/src/scorecard/build_page.py, short())."""
    name = name.split(" (")[0]
    for tail in [" Insurance Company", " Assurance Company", " Insurance Kenya", " Insurance", " Assurance", " Company"]:
        if name.endswith(tail) and len(name) > len(tail) + 3:
            return name[: -len(tail)]
    return name


# The files each repo contributes. A repo's stamp is the last commit that changed one of them, so a commit
# that only touches pages (a navigation change, say) leaves the stamp, and data.json, as they are.
INPUTS = {"ira-kenya-data": ["data/processed", "reference", "validation"],
          "ira-kenya-insurance": ["src/structure/build.py"],
          "ira-kenya-reinsurance": ["output"]}


def commit(repo):
    try:
        return subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h", "--abbrev=12", "--", *INPUTS[repo.name]],
                              capture_output=True, text=True, check=True).stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def mergers(ins_repo):
    """Absorbed company to the company it merged into, as ira-kenya-insurance/src/structure/build.py counts them."""
    src = (ins_repo / "src/structure/build.py").read_text(encoding="utf-8")
    return ast.literal_eval(re.search(r"^MERGERS = (\{.*?\})$", src, re.M).group(1))


def build(root):
    data, rei, insr = root / "ira-kenya-data", root / "ira-kenya-reinsurance", root / "ira-kenya-insurance"

    cw = rows(data / "reference/company_crosswalk.csv")
    name, micro, aliases = {}, {}, defaultdict(set)
    for r in cw:
        if r["segment"] != "insurer":
            continue
        name.setdefault(r["company_id"], r["company_name"])
        micro[r["company_id"]] = int(r["is_micro"] or 0)
        aliases[r["company_id"]].add(r["company_raw"])

    # insurer totals, full years (Q4 year to date)
    lines = defaultdict(lambda: defaultdict(float))
    seen = set()
    for r in rows(data / "data/processed/general_revenue_panel.csv"):
        if r["quarter"] != "4" or r["segment"] != "insurer" or int(r["year"]) not in YEARS:
            continue
        key = (r["company_id"], int(r["year"]))
        seen.add(key)
        if r["line"] in TOT_LINES:
            lines[key][r["line"]] += num(r["ytd_ksh_000"])
    tot = defaultdict(dict)
    for (cid, y) in sorted(seen):
        L = lines[(cid, y)]
        tot[cid][str(y)] = [k3(L["gross_direct_premium"] + L["inward_reinsurance"]), k3(L["net_earned_premium"]),
                            k3(L["incurred_claims"]), k3(L["net_commissions"] + L["management_expenses"]),
                            k3(L["underwriting_result"]), k3(L["investment_income"])]

    # years whose Q4 return was not filed
    nf = defaultdict(set)
    for r in rows(data / "validation/quality_flags.csv"):
        if r["flag"] == "not_filed" and r["quarter"] == "4" and r["segment"] == "insurer" and int(r["year"]) in YEARS:
            nf[r["company_id"]].add(int(r["year"]))

    # insurer figures by class, full years 2018 to 2025
    classes = set()
    cl = defaultdict(lambda: [0.0] * 4)
    for r in rows(data / "data/processed/general_by_class_panel.csv"):
        if (r["quarter"] != "4" or r["segment"] != "insurer" or int(r["year"]) not in CYEARS
                or r["table"] not in CLASS_TABLES or r["class_of_business"] == "Total"):
            continue
        c = CLASS_MAP.get(r["class_of_business"], r["class_of_business"])
        classes.add(c)
        cl[(r["company_id"], int(r["year"]), c)][CLASS_TABLES.index(r["table"])] += num(r["ytd_ksh_000"])
    classes = sorted(classes)
    cls = defaultdict(lambda: defaultdict(dict))
    for (cid, y, c), v in sorted(cl.items()):
        if any(round(x, 3) != 0 for x in v):
            cls[cid][str(y)][str(classes.index(c))] = [k3(x) for x in v]

    # the cedant scorecard
    sc = defaultdict(dict)
    for r in rows(rei / "output/cedant_scorecard.csv"):
        # scores as the CSV holds them: rounding here and again on the page could round twice
        pil = [float(r[p]) if r[p] != "" else None for p in PILLARS]
        sc[r["company_id"]][r["year"]] = [r["grade"], r["grade_uncapped"], int(r["rank"]), int(r["peers"]),
                                          float(r["score"])] + pil + [r["watch_flags"]]
    ns = defaultdict(dict)
    for r in rows(rei / "output/not_scored.csv"):
        ns[r["company_id"]][r["year"]] = r["reason"]
    bt = []
    for r in rows(rei / "output/backtest.csv"):
        rk, peers = (r["rank"].split(" of ") + [""])[:2] if r["rank"] else ("", "")
        bt.append([r["company_id"], r["event"], r["event_date"], int(r["last_scored_year"]), r["grade"],
                   int(rk), int(peers), r["bottom_quintile"] == "True", r["after_last_score"], r["source"]])

    # the six paid triangles behind the home page and the IFRS 17 case study (US$ thousands)
    tri = []
    for L in load_triangles()["lines"]:
        f, sq, res, paid = chain_ladder(L["paid"])
        tri.append([L["name"], k3(paid), k3(paid + res), k3(res)])

    ids = sorted(set(tot) | set(cls) | set(sc) | set(ns) | {b[0] for b in bt})
    missing = [i for i in ids if i not in name]
    if missing:
        sys.exit(f"Not in the crosswalk as insurers: {missing}")
    ins = [dict(id=i, n=name[i], s=short(name[i]), a=sorted(aliases[i]), m=micro[i]) for i in ids]

    return dict(
        v=1,
        sources={"ira-kenya-data": commit(data), "ira-kenya-insurance": commit(insr), "ira-kenya-reinsurance": commit(rei)},
        unit="KSh thousands",
        years=YEARS, cyears=CYEARS, classes=classes, ins=ins,
        tot={i: tot[i] for i in ids if i in tot},
        nf={i: sorted(nf[i]) for i in ids if nf.get(i)},
        cls={i: {y: cls[i][y] for y in sorted(cls[i])} for i in ids if i in cls},
        sc={i: {y: sc[i][y] for y in sorted(sc[i])} for i in ids if i in sc},
        ns={i: {y: ns[i][y] for y in sorted(ns[i])} for i in ids if i in ns},
        bt=bt,
        mg=mergers(insr),
        tri=tri,
        # the IFRS 17 case study's figures (tools/figures.py, checked against its source by check_figures.py):
        # undiscounted reserve US$bn, discounting effect US$bn, discount rate %, 75th percentile risk adjustment US$m
        i17=[IFRS17["undisc_bn"], IFRS17["disc_effect_bn"], IFRS17["rate"], IFRS17["ra75_m"]],
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=os.environ.get("IRA_REPOS", ".."),
                    help="folder holding ira-kenya-data and ira-kenya-reinsurance")
    root = Path(ap.parse_args().repos)
    if not (root / "ira-kenya-data").exists():
        sys.exit(f"Cannot find the analysis repos under {root.resolve()}. Pass --repos.")
    d = build(root)
    text = json.dumps(d, separators=(",", ":"), ensure_ascii=True) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"{OUT.relative_to(ROOT).as_posix()}  {len(text):,} bytes, {len(d['ins'])} insurers, "
          f"{sum(len(c) for y in d['cls'].values() for c in y.values())} insurer-class-years")


if __name__ == "__main__":
    main()
