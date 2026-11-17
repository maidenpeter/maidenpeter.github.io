"""Check Ask the data (/ask/): the figures, the answers and the page they come from.

    python tools/check_ask.py              # the committed assets/ask/data.json (run in CI)
    python tools/check_ask.py --repos ..   # also rebuild every figure from the processed tables

Always:
  - data.json holds only the fields listed in docs/ask-plan.md, full years only, no row-level table;
  - a seeded sample of questions (every question, every class, first and last years, merged companies,
    the smallest insurer, missing years, a tie made up for the test) answered by the page's engine
    (assets/ask/ask.js, run in Node) and by tools/ask_answers.py must agree word for word;
  - every chart class ask.js writes exists in assets/viz.css, assets/site.css or assets/ask/ask.css;
  - every quote in the About answers is on the page it cites;
  - every /ask/#q= link on the site names a question and slots that exist.
With --repos:
  - every figure in data.json equals the processed tables, rebuilt here by separate code;
  - the sample answered from those full-precision tables reads exactly as from data.json;
  - market totals tie to ira-kenya-insurance/output (class_market, structure_market, structure_shares) and the
    scorecard to ira-kenya-reinsurance/output, and the links in the answers resolve.
Prints the sample and its answers with -v.
"""
import argparse, csv, html, json, math, os, random, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ask_answers as AA

ROOT = Path(__file__).resolve().parent.parent
FAIL = []
OK = [0]


def check(name, cond, detail=""):
    if cond:
        OK[0] += 1
    else:
        FAIL.append(name + (f": {detail}" if detail else ""))


def load():
    D = json.load(open(ROOT / "assets/ask/data.json", encoding="utf-8"))
    page = (ROOT / "ask/index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="ask-bank-data">(.*?)</script>', page, re.S)
    return D, json.loads(m.group(1).replace("<\\/", "</"))


# ------------------------------------------------------------------ fields
TOP = {"v", "sources", "unit", "years", "cyears", "classes", "ins", "tot", "nf", "cls", "sc", "ns", "bt", "mg", "tri", "i17"}


def fields(D):
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    check("data.json top-level fields", set(D) == TOP, sorted(set(D) ^ TOP))
    full = set(D["years"])
    check("full years only", 2017 not in full and all(2016 <= y <= 2025 for y in full) and set(D["cyears"]) <= full, D["years"])
    check("insurer fields", all(set(x) == {"id", "n", "s", "a", "m"} for x in D["ins"]))
    ids = {x["id"] for x in D["ins"]}
    for key in ("tot", "nf", "cls", "sc", "ns"):
        check(f"{key}: insurers only", set(D[key]) <= ids, sorted(set(D[key]) - ids))
    bad = [(i, y) for i, t in D["tot"].items() for y, e in t.items() if int(y) not in full or len(e) != 6 or not all(num(v) for v in e)]
    check("tot: six figures per insurer and full year", not bad, bad[:5])
    nclass = len(D["classes"])
    bad = [(i, y, c) for i, t in D["cls"].items() for y, cs in t.items() for c, e in cs.items()
           if int(y) not in D["cyears"] or not 0 <= int(c) < nclass or len(e) != 4 or not all(num(v) for v in e)]
    check("cls: four figures per insurer, class and full year", not bad, bad[:5])
    bad = [(i, y) for i, t in D["sc"].items() for y, r in t.items() if len(r) != 10]
    check("sc: ten fields per scored year", not bad, bad[:5])
    check("bt: ten fields per row", all(len(b) == 10 for b in D["bt"]))
    check("mg: insurer ids only", all(a in ids and b in ids for a, b in D["mg"].items()), D["mg"])
    check("tri: four fields per line", len(D["tri"]) == 6 and all(len(t) == 4 for t in D["tri"]))
    check("i17: four figures", len(D["i17"]) == 4 and all(num(v) for v in D["i17"]))
    check("no quarterly figures", '"q1"' not in json.dumps(D).lower() and "quarter" not in json.dumps(D["tot"]).lower())


# ------------------------------------------------------------------ the sample
def sample(D, B):
    rnd = random.Random(20261116)
    ins = [x["id"] for x in D["ins"]]
    cy, ys = [str(y) for y in D["cyears"]], [str(y) for y in D["years"]]
    last = ys[-1]
    wp = {i: D["tot"][i][last][0] for i in ins if i in D["tot"] and last in D["tot"][i] and D["tot"][i][last][0] > 0}
    smallest = min(wp, key=wp.get)
    merged = ["mua", "saham", "sanlam_allianz_general", "sanlam_general", "allianz_kenya", "jubilee_composite"]
    slugs = [AA.slug(c) for c in D["classes"]]
    C = []

    def add(q, label, **s):
        C.append((label, q, {k: str(v) for k, v in s.items()}))

    for y1, y2 in [(cy[0], cy[-1]), (cy[-1], cy[-1]), (cy[0], cy[0]), (cy[-1], cy[0])] + [tuple(sorted(rnd.sample(cy, 2))) for _ in range(2)]:
        add("class-range", "range", y1=y1, y2=y2)
    for y in [ys[0], ys[-1], rnd.choice(ys)]:
        add("uw-inv", "year", yr=y)
        add("profit-count", "year", yr=y)
        add("concentration", "year", yr=y)
    add("motor-lr", "fixed")
    for k, c in enumerate(slugs):   # every class, the first and last years among them
        add("ins-class-year", "every class", ins=rnd.choice(list(wp)), cls=c, yr=cy[0] if k % 3 == 0 else cy[-1] if k % 3 == 1 else rnd.choice(cy))
    for i in merged:
        add("ins-class-year", "merged company", ins=i, cls="motor-private", yr=rnd.choice(cy))
        add("ins-trend", "merged company", ins=i, y1=ys[0], y2=ys[-1])
        add("ins-rank", "merged company", ins=i, yr=rnd.choice(ys))
    add("ins-class-year", "smallest insurer", ins=smallest, cls=rnd.choice(slugs), yr=cy[-1])
    add("ins-trend", "smallest insurer", ins=smallest, y1=ys[0], y2=ys[-1])
    add("ins-rank", "smallest insurer", ins=smallest, yr=ys[-1])
    add("ins-mix", "smallest insurer", ins=smallest, yr=cy[-1])
    # an insurer active that year with no business in one class
    for i in sorted(D["cls"]):
        y = cy[-1]
        if y in D["cls"][i] and len(D["cls"][i][y]) < len(slugs):
            gap = next(c for c in range(len(slugs)) if str(c) not in D["cls"][i][y])
            add("ins-class-year", "no business in the class", ins=i, cls=slugs[gap], yr=y)
            break
    # a year before the insurer existed, and a year with no Q4 return
    late = next(i for i in ins if i in D["tot"] and min(int(y) for y in D["tot"][i]) >= 2025)
    add("ins-class-year", "before it existed", ins=late, cls="medical", yr=cy[0])
    add("ins-trend", "before it existed", ins=late, y1=ys[0], y2=ys[2])
    add("ins-rank", "before it existed", ins=late, yr=ys[0])
    nf = next(((i, str(y)) for i, v in sorted(D["nf"].items()) for y in v if str(y) in cy), None)
    if nf:
        add("ins-class-year", "no Q4 return", ins=nf[0], cls="motor-private", yr=nf[1])
        add("ins-mix", "no Q4 return", ins=nf[0], yr=nf[1])
    for _ in range(6):
        add("ins-trend", "random", ins=rnd.choice(ins), y1=rnd.choice(ys), y2=rnd.choice(ys))
        add("ins-rank", "random", ins=rnd.choice(ins), yr=rnd.choice(ys))
        add("ins-mix", "random", ins=rnd.choice(ins), yr=rnd.choice(cy))
        add("ins-class-year", "random", ins=rnd.choice(ins), cls=rnd.choice(slugs), yr=rnd.choice(cy))
    sy = sorted({y for t in D["sc"].values() for y in t})
    capped = next(((i, y) for i, t in sorted(D["sc"].items()) for y, r in sorted(t.items()) if r[0] != r[1]), None)
    add("scorecard", "grade capped", ins=capped[0], yr=capped[1])
    ns = next((i, y) for i, t in sorted(D["ns"].items()) for y in sorted(t) if y in sy)
    add("scorecard", "not scored", ins=ns[0], yr=ns[1])
    add("scorecard", "not in the scorecard", ins=late, yr=sy[0])
    for _ in range(5):
        i = rnd.choice(sorted(D["sc"]))
        add("scorecard", "random", ins=i, yr=rnd.choice(sorted(D["sc"][i])))
    for y in AA.ctx(D).gyears:
        add("growth", "every year", yr=y)
    add("backtest", "fixed")
    add("tri-largest", "fixed")
    add("tri-sum", "fixed")
    for t in D["tri"]:
        add("tri-unpaid", "every line", line=AA.slug(t[0]))
    for k, *_ in B["topics"]:
        add("about-done", "every topic", topic=k)
    for q in ("about-tools", "about-checks", "about-open", "about-contact"):
        add(q, "fixed")
    add("ins-trend", "unknown slot values fall back", ins="no-such-insurer", y1="1999", y2="abc")
    return C


def strip(o):
    """The parts of an answer both engines produce (the chart's drawing is the page's business)."""
    if o is None:
        return None
    keep = ["title", "slots", "ok", "say", "nums", "table", "points", "src", "link", "cav", "note", "chart"]
    o = {k: o[k] for k in keep}
    o["chart"] = o["chart"] and {"type": o["chart"]["type"], "title": o["chart"]["title"]}
    return json.loads(json.dumps(o))


def node(D, B, cases):
    r = subprocess.run(["node", str(ROOT / "tools/ask_node.js")], input=json.dumps(dict(D=D, B=B, cases=cases)),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit("Node could not run the engine:\n" + r.stderr)
    return json.loads(r.stdout)


def engines(D, B, C, verbose):
    js = node(D, B, [[q, s] for _, q, s in C])
    for (label, q, s), j in zip(C, js):
        p = strip(AA.answer(D, B, q, s))
        diff = [k for k in p if p[k] != j.get(k)]
        check(f"engine and Python agree: {q} {s} ({label})", not diff, "; ".join(f"{k}: JS {j.get(k)!r} / Python {p[k]!r}" for k in diff)[:600])
        if verbose:
            print(f"[{label}] {p['title']}\n    " + " ".join(p["say"]))
    groups = {Q["g"] for Q in B["questions"]}
    check("sample covers every question", {q for _, q, _ in C} == {Q["id"] for Q in B["questions"]})
    check("sample covers every group", groups == {g for g, _ in B["groups"]})
    check("sample covers every class", {s.get("cls") for _, q, s in C if q == "ins-class-year"} >= {AA.slug(c) for c in D["classes"]})
    check("sample has at least 50 questions", len(C) >= 50, len(C))
    return js


def tie(D, B):
    """Two insurers given the same premium in one class: both engines must call it a joint rank."""
    T = json.loads(json.dumps(D))
    y, ci = str(D["cyears"][-1]), str(D["classes"].index("Medical"))
    writers = sorted((T["cls"][i][y][ci][0], i) for i in T["cls"] if y in T["cls"][i] and ci in T["cls"][i][y] and T["cls"][i][y][ci][0] > 0)
    (g1, a), (g2, b) = writers[-3], writers[-2]
    T["cls"][a][y][ci][0] = T["cls"][b][y][ci][0]
    case = [["ins-class-year", dict(ins=a, cls="medical", yr=y)], ["ins-class-year", dict(ins=b, cls="medical", yr=y)]]
    js = node(T, B, case)
    for (q, s), j in zip(case, js):
        p = strip(AA.answer(T, B, q, s))
        check(f"tie: engines agree for {s['ins']}", p == j, f"{p['nums']} / {j['nums']}")
        check(f"tie: called joint for {s['ins']}", "joint 2nd of" in " ".join(p["say"]), p["say"][0])


# ------------------------------------------------------------------ the page
def classes():
    js = (ROOT / "assets/ask/ask.js").read_text(encoding="utf-8")
    css = "".join((ROOT / p).read_text(encoding="utf-8") for p in ("assets/viz.css", "assets/site.css", "assets/ask/ask.css"))
    defined = set(re.findall(r"[.#]([a-zA-Z][\w-]*)", css))
    used = set(re.findall(r"\b((?:vz|ask)-[a-z0-9-]+)\b", js))
    used |= {"panel", "vz", "pos", "neg", "neu", "ctx", "ring", "up", "dn", "bars", "lab", "track", "bar", "val", "in", "data", "tag", "small", "btn", "quiet"}
    ids = {"ask-status", "ask-reset", "ask-form", "ask-text", "ask-loading", "ask-bank-data", "ask-browse", "ask-panel"}
    missing = sorted(c for c in used - ids if c not in defined)
    check("every class ask.js writes is styled", not missing, missing)


def visible(path):
    """A built page's text as a reader sees it: tags become spaces, entities decoded, scripts and styles dropped."""
    s = path.read_text(encoding="utf-8")
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<head>.*?</head>", " ", s, flags=re.S | re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s)


def about_quotes(B):
    pages = {}
    for key, item in B["about"].items():
        items = item.values() if key == "about-done" else [item]
        for it in items:
            for quotes, href, label, page in it["points"]:
                f = ROOT / (page.strip("/") + "/index.html" if page.strip("/") else "index.html")
                text = pages.setdefault(f, visible(f))
                for q in quotes:
                    check(f"About quote on {page}: {q[:60]}", q in text)


def hash_links(D, B):
    for f in ROOT.rglob("*.html"):
        if ".git" in f.parts:
            continue
        for h in re.findall(r'href="/ask/#([^"]+)"', f.read_text(encoding="utf-8")):
            p = dict(kv.split("=", 1) for kv in html.unescape(h).split("&"))
            q = p.pop("q", None)
            ok = AA.question(B, q) is not None and AA.normalize(D, B, q, p) == p
            check(f"/ask/ link in {f.relative_to(ROOT).as_posix()}: {h}", ok)


# ------------------------------------------------------------------ the processed tables (--repos)
def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fnum(v):
    return float(v) if v else 0.0


def from_tables(root, D):
    """data.json rebuilt from the processed tables at full precision, written separately from build_ask.py."""
    data, rei = root / "ira-kenya-data", root / "ira-kenya-reinsurance"
    years = set(D["years"])
    acc = defaultdict(lambda: defaultdict(float))
    present = set()
    for r in rows(data / "data/processed/general_revenue_panel.csv"):
        y = int(r["year"])
        if r["segment"] == "insurer" and r["quarter"] == "4" and y in years:
            present.add((r["company_id"], y))
            acc[(r["company_id"], y)][r["line"]] += fnum(r["ytd_ksh_000"])
    tot = defaultdict(dict)
    for (i, y) in sorted(present):
        a = acc[(i, y)]
        tot[i][str(y)] = [a["gross_direct_premium"] + a["inward_reinsurance"], a["net_earned_premium"], a["incurred_claims"],
                          a["net_commissions"] + a["management_expenses"], a["underwriting_result"], a["investment_income"]]
    pos = {"gross_premium": 0, "net_earned_premium": 1, "claims_incurred": 2, "underwriting_result": 3}
    idx = {c: str(k) for k, c in enumerate(D["classes"])}
    idx["Motor Commercial PSV"] = idx["Motor Commercial"]
    cl = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])))
    for r in rows(data / "data/processed/general_by_class_panel.csv"):
        y = int(r["year"])
        if (r["segment"] == "insurer" and r["quarter"] == "4" and y in D["cyears"] and r["table"] in pos
                and r["class_of_business"] != "Total"):
            cl[r["company_id"]][str(y)][idx[r["class_of_business"]]][pos[r["table"]]] += fnum(r["ytd_ksh_000"])
    cls = {i: {y: {c: v for c, v in sorted(cs.items(), key=lambda kv: int(kv[0])) if any(abs(x) >= 0.0005 for x in v)}
               for y, cs in sorted(t.items())} for i, t in sorted(cl.items())}
    cls = {i: {y: cs for y, cs in t.items() if cs} for i, t in cls.items()}
    cls = {i: t for i, t in cls.items() if t}
    nf = defaultdict(list)
    for r in rows(data / "validation/quality_flags.csv"):
        if r["flag"] == "not_filed" and r["quarter"] == "4" and r["segment"] == "insurer" and int(r["year"]) in years:
            nf[r["company_id"]].append(int(r["year"]))
    sc = defaultdict(dict)
    for r in rows(rei / "output/cedant_scorecard.csv"):
        sc[r["company_id"]][r["year"]] = [r["grade"], r["grade_uncapped"], int(r["rank"]), int(r["peers"]), float(r["score"])] + \
            [float(r[p]) if r[p] else None for p in ("pillar_balance_sheet", "pillar_operating", "pillar_business_profile", "pillar_return_quality")] + [r["watch_flags"]]
    ns = defaultdict(dict)
    for r in rows(rei / "output/not_scored.csv"):
        ns[r["company_id"]][r["year"]] = r["reason"]
    bt = [[r["company_id"], r["event"], r["event_date"], int(r["last_scored_year"]), r["grade"], int(r["rank"].split(" of ")[0]),
           int(r["rank"].split(" of ")[1]), r["bottom_quintile"] == "True", r["after_last_score"], r["source"]] for r in rows(rei / "output/backtest.csv")]
    tri = []
    for line in json.load(open(ROOT / "tools/cas_triangles.json", encoding="utf-8"))["lines"]:
        t = line["paid"]
        n = len(t)
        f = [sum(t[i][j + 1] for i in range(n) if t[i][j + 1] is not None) / sum(t[i][j] for i in range(n) if t[i][j + 1] is not None) for j in range(n - 1)]
        paid = ult = 0.0
        for i in range(n):
            last = max(j for j in range(n) if t[i][j] is not None)
            u = t[i][last]
            for j in range(last, n - 1):
                u *= f[j]
            paid += t[i][last]
            ult += u
        tri.append([line["name"], paid, ult, ult - paid])
    src = (root / "ira-kenya-insurance/src/structure/build.py").read_text(encoding="utf-8")
    line = next(l for l in src.splitlines() if l.startswith("MERGERS = "))
    mg = dict(re.findall(r'"(\w+)": "(\w+)"', line))
    F = dict(D)
    F.update(mg=mg, tot=dict(tot), cls=cls, nf={i: sorted(v) for i, v in nf.items()}, sc=dict(sc), ns=dict(ns), bt=bt, tri=tri)
    return F


def same(a, b, tol=0.0006):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(same(a[k], b[k], tol) for k in a)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= tol
    return a == b


def repos(root, D, B, C):
    F = from_tables(root, D)
    for key in ("tot", "cls", "nf", "sc", "ns", "bt", "mg"):
        check(f"data.json {key} equals the processed tables", same(D[key], F[key]),
              next((f"{i}" for i in sorted(set(D[key]) | set(F[key])) if not same(D[key].get(i), F[key].get(i))), "") if isinstance(D[key], dict) else "")
    check("data.json triangles equal a chain ladder on tools/cas_triangles.json", same(D["tri"], F["tri"], 0.001))
    import build_ask   # the stamp is the last commit that changed the files data.json is built from
    now = {r: build_ask.commit((root / r).resolve()) for r in D["sources"]}
    check("data.json sources are the last commits that changed its inputs", now == D["sources"], f"{D['sources']} / now {now}")
    for label, q, s in C:
        a, b = strip(AA.answer(D, B, q, s)), strip(AA.answer(F, B, q, s))
        diff = [k for k in a if a[k] != b[k]]
        check(f"answer from data.json reads as from the tables: {q} {s}", not diff, "; ".join(f"{k}: {a[k]!r} / {b[k]!r}" for k in diff)[:400])

    ins = root / "ira-kenya-insurance" / "output"
    for r in rows(ins / "class_market.csv"):
        y = r["year"]
        cs = [str(k) for k, c in enumerate(D["classes"]) if r["class"] in (c, "All classes")]
        got = [sum(AA.cls_sum(D, [y], c, f) for c in cs) for f in range(4)]
        want = [float(r[k]) for k in ("gross_premium", "net_earned_premium", "claims_incurred", "underwriting_result")]
        check(f"class_market {y} {r['class']}", all(abs(g - w) < 1.0 for g, w in zip(got, want)), f"{got} / {want}")
    # the structure CSVs print shares and the index to four decimals, so they are compared to that precision
    for r in rows(ins / "structure_market.csv"):
        c = AA.conc(D, r["year"])
        check(f"structure_market {r['year']}", c["n"] == int(r["insurers"]) and abs(c["t"] - float(r["written_premium"])) < 1
              and abs(c["hhi"] - float(r["hhi"])) < 0.0006 and abs(c["top5"] - float(r["top5_share"])) < 0.00006
              and c["nb"] == int(r["insurers_over_10bn"]) and abs(c["bs"] - float(r["share_over_10bn"])) < 0.00006, f"{c} / {dict(r)}")
    for r in rows(ins / "structure_shares.csv"):
        k = AA.rank_in(D, r["year"], r["company_id"])
        check(f"structure_shares {r['year']} {r['company_id']}", k and k[0] == int(float(r["rank"])) and abs(k[3] - float(r["share"])) < 0.00006, f"{k} / {dict(r)}")
    for name, path in AA.LINK.items():
        p = path[0].split("#")[0]
        f = (root / p.strip("/")) if p.startswith("/ira-kenya") else ROOT / (p.strip("/") or "index.html")
        f = f / "index.html" if f.is_dir() else f
        check(f"answer link {name} resolves", f.exists(), str(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", help="folder holding ira-kenya-data, ira-kenya-insurance and ira-kenya-reinsurance")
    ap.add_argument("-v", action="store_true", help="print the sample and its answers")
    a = ap.parse_args()
    D, B = load()
    fields(D)
    C = sample(D, B)
    engines(D, B, C, a.v)
    tie(D, B)
    classes()
    about_quotes(B)
    hash_links(D, B)
    if a.repos:
        root = Path(a.repos)
        if not (root / "ira-kenya-data").exists():
            sys.exit(f"Cannot find the analysis repos under {root.resolve()}.")
        repos(root, D, B, C)
    print(f"{len(C)} sample questions; {OK[0]} checks passed.")
    if FAIL:
        print(f"{len(FAIL)} failed:")
        for f in FAIL:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
