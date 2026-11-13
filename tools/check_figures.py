"""Recompute every figure in tools/figures.py from the files it came from.

Kenya figures are checked against the three analysis repos, cloned side by side:

    python tools/check_figures.py --repos "../Marion Peter"

The earlier case studies are checked too when their output files are listed in
tools/local_paths.json (kept out of git, because client work stays private):

    {"ifrs17": ".../ifrs17_site.json", "reserving": ".../reserving.json",
     "pricing": ".../pricing.json", "auctions": ".../findings.json",
     "dealer": ".../headline_results.json", "dealer_check": ".../python_comparison.csv"}

Exits non-zero if any figure differs from its source at the precision shown.
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import figures as F

FAIL = []
OK = [0]


def check(name, shown, actual, tol):
    if actual is None or abs(shown - actual) > tol:
        FAIL.append(f"{name}: site shows {shown}, source gives {actual}")
    else:
        OK[0] += 1


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def count_rows(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


def kenya(root):
    data, ins, rei = root / "ira-kenya-data", root / "ira-kenya-insurance", root / "ira-kenya-reinsurance"
    K = F.KENYA

    man = rows(data / "data/raw/manifest.csv")
    ok = [r for r in man if r["status"] == "ok"]
    check("files", K["files"], len(ok), 0)
    check("first_year", K["first_year"], min(int(r["year"]) for r in ok), 0)
    check("revenue_rows", K["revenue_rows"], count_rows(data / "data/processed/general_revenue_accounts.csv"), 0)
    check("class_rows", K["class_rows"], count_rows(data / "data/processed/general_by_class.csv"), 0)

    val = rows(data / "validation/validation_report.csv")
    check("checks", K["checks"], len(val), 0)
    unexplained = sum(1 for r in val if r["passed"] != "True" and not r["known_issue"].strip())
    check("unexplained", K["unexplained"], unexplained, 0)
    check("failed_checks", K["failed_checks"], sum(1 for r in val if r["passed"] != "True"), 0)

    pdf = rows(data / "validation/crosscheck_pdf_releases.csv")
    check("pdf_total", K["pdf_total"], len(pdf), 0)
    check("pdf_match", K["pdf_match"], sum(1 for r in pdf if float(r["difference"]) == 0), 0)

    flags = rows(data / "validation/quality_flags.csv")
    sev = "severity" if "severity" in flags[0] else None
    if sev:
        errors = {(r["company_id"], r["year"], r["quarter"]) for r in flags if r[sev] == "error"}
        check("error_returns", K["error_returns"], len(errors), 0)  # company quarters, not flags
    else:
        FAIL.append("error_returns: quality_flags.csv has no severity column")

    panel = rows(data / "data/processed/general_revenue_panel.csv")
    check("companies", K["companies"], len({r["company_id"] for r in panel}), 0)
    check("quarters", K["quarters"], len({(r["year"], r["quarter"]) for r in panel}), 0)
    q4 = [r for r in panel if r["quarter"] == "4" and r["segment"] == "insurer"]
    for y in (2016, 2025):
        uw = [float(r["ytd_ksh_000"] or 0) for r in q4 if r["year"] == str(y) and r["line"] == "underwriting_result"]
        check(f"active_{y}", K[f"active_{y}"], sum(1 for v in uw if v != 0), 0)
        check(f"profit_{y}", K[f"profit_{y}"], sum(1 for v in uw if v > 0), 0)
    uw25 = sum(float(r["ytd_ksh_000"] or 0) for r in q4 if r["year"] == "2025" and r["line"] == "underwriting_result") / 1e6
    inv25 = sum(float(r["ytd_ksh_000"] or 0) for r in q4 if r["year"] == "2025" and r["line"] == "investment_income") / 1e6
    check("uw_2025", K["uw_2025"], uw25, 0.005)
    check("inv_2025", K["inv_2025"], inv25, 0.005)

    cm = [r for r in rows(ins / "output/class_market.csv") if 2018 <= int(r["year"]) <= 2025]
    by = defaultdict(float)
    years_motor = defaultdict(float)
    for r in cm:
        by[r["class"]] += float(r["underwriting_result"]) / 1e6
        if r["class"].startswith("Motor"):
            years_motor[r["year"]] += float(r["underwriting_result"])
    names = {"Motor private": "Motor Private", "Motor commercial": "Motor Commercial", "Personal accident": "Personal Accident",
             "Fire industrial": "Fire Industrial", "Fire domestic": "Fire Domestic",
             "Workmen's compensation": "Workmen's Compensation"}
    for label, v in F.CLASS_RESULTS:
        check(f"class {label}", v, by.get(names.get(label, label)), 0.005)
    motor = by["Motor Private"] + by["Motor Commercial"]
    check("uw_market", K["uw_market"], by["All classes"], 0.005)
    check("uw_motor", K["uw_motor"], motor, 0.005)
    check("uw_motor_private", K["uw_motor_private"], by["Motor Private"], 0.005)
    check("uw_motor_commercial", K["uw_motor_commercial"], by["Motor Commercial"], 0.005)
    check("uw_other", K["uw_other"], by["All classes"] - motor, 0.005)
    check("uw_wc", K["uw_wc"], by["Workmen's Compensation"], 0.005)
    check("motor_loss_years", K["motor_loss_years"], sum(1 for v in years_motor.values() if v < 0), 0)

    rg = {r["class"]: r for r in rows(ins / "output/rate_gap.csv")}
    check("rate_mc", K["rate_mc"], 100 * float(rg["Motor Commercial"]["rate_change_to_break_even"]), 0.05)
    check("rate_mp", K["rate_mp"], 100 * float(rg["Motor Private"]["rate_change_to_break_even"]), 0.05)

    t = {r["threshold"][:4]: r for r in rows(ins / "output/low_motor_loss_ratio_test.csv")}["0.40"]
    check("low_lr_insurers", K["low_lr_insurers"], int(t["low_insurers"]), 0)
    check("low_lr_trouble", K["low_lr_trouble"], int(t["low_with_trouble"]), 0)
    check("other_insurers", K["other_insurers"], int(t["other_insurers"]), 0)
    check("other_trouble", K["other_trouble"], int(t["other_with_trouble"]), 0)
    check("fisher_p", K["fisher_p"], float(t["fisher_p"]), 0.0005)

    sm = {r["year"]: r for r in rows(ins / "output/structure_market.csv")}
    for y in ("2020", "2025"):
        check(f"over10_{y}", K[f"over10_{y}"], int(sm[y]["insurers_over_10bn"]), 0)
        check(f"share10_{y}", K[f"share10_{y}"], 100 * float(sm[y]["share_over_10bn"]), 0.5)
    check("hhi_2025", K["hhi_2025"], float(sm["2025"]["hhi"]), 0.5)

    g = rows(ins / "output/structure_growth_results.csv")
    def median(v):
        v = sorted(v); n = len(v)
        return (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)
    lose = [float(r["combined_ratio"]) for r in g if r["gained_share"] == "False"]
    gain = [float(r["combined_ratio"]) for r in g if r["gained_share"] == "True"]
    check("losing_n", K["losing_n"], len(lose), 0)
    check("gaining_n", K["gaining_n"], len(gain), 0)
    check("median_cr_losing", K["median_cr_losing"], 100 * median(lose), 0.05)
    check("median_cr_gaining", K["median_cr_gaining"], 100 * median(gain), 0.05)

    fr = rows(ins / "output/structure_fragmentation.csv")
    check("frag", K["frag"], sum(float(r["extra_expense"]) for r in fr) / 1e6, 0.05)

    bt = rows(rei / "output/backtest.csv")
    check("bt_total", K["bt_total"], len(bt), 0)
    check("bt_bottom", K["bt_bottom"], sum(1 for r in bt if r["bottom_quintile"] == "True"), 0)
    got = sorted((int(r["event_date"][:4]), int(r["rank"].split(" of ")[0]), int(r["rank"].split(" of ")[1]), r["bottom_quintile"] == "True") for r in bt)
    if got != sorted(F.BACKTEST):
        FAIL.append(f"BACKTEST: site shows {sorted(F.BACKTEST)}, source gives {got}")
    else:
        OK[0] += 1

    sc = [r for r in rows(rei / "output/cedant_scorecard.csv") if r["year"] == "2025"]
    check("scored_2025", K["scored_2025"], len(sc), 0)


def ifrs17(path):
    d = json.load(open(path, encoding="utf-8"))
    I = F.IFRS17
    r = I["rate"] / 100
    conf = d["conf"]
    i75, i95 = conf.index(75), conf.index(95)
    pv = lambda cf: sum(c / (1 + r) ** (t + 0.5) for t, c in enumerate(cf))
    tu = tp = tf = ra75 = ra95 = 0.0
    by = {}
    for k in d["order"]:
        x = d["lines"][k]
        u, p, ra = x["undisc"], pv(x["cf"]), x["ra"][i75]
        ful = p + ra * p / u
        by[x["name"]] = (100 * (ful - u) / u, 100 * ra / u, 100 * (p - u) / u)
        tu += u; tp += p; tf += ful; ra75 += ra; ra95 += x["ra"][i95]
    check("ifrs17 lines", I["lines"], len(d["order"]), 0)
    check("ifrs17 undisc_bn", I["undisc_bn"], tu / 1000, 0.005)
    check("ifrs17 disc_effect_bn", I["disc_effect_bn"], (tp - tu) / 1000, 0.005)
    check("ifrs17 ra75_m", I["ra75_m"], ra75, 0.5)
    check("ifrs17 ra95_bn", I["ra95_bn"], ra95 / 1000, 0.005)
    check("ifrs17 indep75_m", I["indep75_m"], d["indep_ra"][i75], 0.5)
    check("ifrs17 diversification_m", I["diversification_m"], ra75 - d["indep_ra"][i75], 0.5)
    check("ifrs17 book_change", I["book_change"], 100 * (tf - tu) / tu, 0.05)
    names = {"Workers' compensation": "Workers' compensation"}
    for label, v in F.IFRS17_LINES:
        check(f"ifrs17 line {label}", v, by.get(names.get(label, label), (None,))[0], 0.05)
    L = [d["lines"][k] for k in d["order"]]
    check("ifrs17 dur_low", I["dur_low"], min(x["dur"] for x in L), 0.005)
    check("ifrs17 dur_high", I["dur_high"], max(x["dur"] for x in L), 0.005)
    check("ifrs17 cv_pm", I["cv_pm"], d["lines"]["ppauto"]["cv"], 0.05)
    check("ifrs17 cv_pl", I["cv_pl"], d["lines"]["prodliab"]["cv"], 0.05)
    check("ifrs17 cl_lines_within", I["cl_lines_within"], sum(1 for x in L if abs(x["cl_diff"]) <= I["cl_within"]), 0)
    check("ifrs17 cl_pl", I["cl_pl"], d["lines"]["prodliab"]["cl_diff"], 0.05)
    check("ifrs17 div_pct", I["div_pct"], 100 * (ra75 - d["indep_ra"][i75]) / ra75, 0.5)
    pl = by["Product liability"]
    check("ifrs17 prodliab_change", I["prodliab_change"], pl[0], 0.05)
    check("ifrs17 prodliab_ra", I["prodliab_ra"], pl[1], 0.05)
    check("ifrs17 prodliab_disc", I["prodliab_disc"], pl[2], 0.05)


def reserving(path):
    d = json.load(open(path, encoding="utf-8"))
    B = F.BACKTEST_AE
    check("backtest private_motor", B["private_motor"], d["ppauto"]["ave"]["ratio"], 0.0005)
    check("backtest all_lines", B["all_lines"], d["_industry"]["ratio"], 0.0005)
    ratios = [v["ave"]["ratio"] for k, v in d.items() if not k.startswith("_")]
    over = [100 * (1 - x) for x in ratios if x < 1]
    check("backtest lines", B["lines"], len(ratios), 0)
    check("backtest over_reserved", B["over_reserved"], len(over), 0)
    check("backtest low", B["low"], min(over), 0.5)
    check("backtest high", B["high"], max(over), 0.5)


def pricing(path):
    d = json.load(open(path, encoding="utf-8"))
    C = F.CREDIBILITY
    s = d["oos"]["smaller half"]
    check("credibility k_m", C["k_m"], d["k"] / 1000, 0.5)
    check("credibility insurers", C["insurers"], d["companies"], 0)
    check("credibility small_gain", C["small_gain"], 100 * (s["own"] - s["cred"]) / s["own"], 0.05)
    check("credibility small_vs_market", C["small_vs_market"], 100 * (s["market"] - s["cred"]) / s["market"], 0.05)


def auctions(path):
    d = json.load(open(path, encoding="utf-8"))
    A = F.AUCTIONS
    ag, cs, mo = d["aggregate"], d["condition_scales"], d["money"]
    bands = d["by_condition_band"]
    check("auctions rows_total", A["rows_total"], d["rows_total"], 0)
    check("auctions rows", A["rows"], d["rows_analysed"], 0)
    check("auctions short_scale", A["short_scale"], cs["rows_short_scale"], 0)
    check("auctions long_scale", A["long_scale"], cs["rows_long_scale"], 0)
    check("auctions appraised_bn", A["appraised_bn"], ag["total_mmr"] / 1e9, 0.005)
    check("auctions median_gap", A["median_gap"], ag["median_gap"], 0)
    check("auctions below", A["below"], ag["pct_below_estimate"], 0.05)
    check("auctions net_pct", A["net_pct"], ag["net_gap_pct"], 0.005)
    check("auctions net_m", A["net_m"], -ag["net_gap"] / 1e6, 0.05)
    check("auctions gross_m", A["gross_m"], mo["gross_misvaluation"] / 1e6, 0.05)
    check("auctions cancel", A["cancel"], mo["pct_cancelling_out"], 0.5)
    check("auctions mae", A["mae"], ag["mean_absolute_error"], 0.5)
    check("auctions mae_pct", A["mae_pct"], ag["mae_pct_of_mmr"], 0.05)
    check("auctions worst_band_pct", A["worst_band_pct"], 100 * bands[0]["total_gap"] / bands[0]["total_mmr"], 0.05)
    check("auctions best_band_pct", A["best_band_pct"], 100 * bands[-1]["total_gap"] / bands[-1]["total_mmr"], 0.05)
    dec = list(d["robustness"]["deciles"].values())
    for i, (a, b) in enumerate(zip(F.AUCTION_DECILES, dec)):
        check(f"auctions decile {i + 1}", a, b, 0.005)
    check("auctions decile_low", A["decile_low"], dec[0], 0.05)
    check("auctions decile_high", A["decile_high"], dec[-1], 0.05)
    check("auctions excl_rows", A["excl_rows"], d["robustness"]["rows_dropped_with_top_sellers"], 0)
    # excl_low and excl_high (-8.9 and +3.4, the end bands without the 20 largest sellers) are not in
    # findings.json; they were recomputed with valuation_adequacy.prepare() on the full file.


def dealer(path, check_path):
    d = json.load(open(path, encoding="utf-8"))
    D = F.DEALER
    reported = d["parts_revenue"] + d["service_revenue_d2"]
    check("dealer parts_rows", D["parts_rows"], d["d1_rows"], 0)
    check("dealer job_rows", D["job_rows"], d["d2_rows"], 0)
    check("dealer consumption_rows", D["consumption_rows"], d["d3_raw_rows"], 0)
    check("dealer rows", D["rows"], d["d1_rows"] + d["d2_rows"] + d["d3_raw_rows"], 0)
    check("dealer reported_bn", D["reported_bn"], reported / 1e9, 0.005)
    check("dealer actual_bn", D["actual_bn"], d["total_revenue"] / 1e9, 0.005)
    check("dealer double_bn", D["double_bn"], d["spare_revenue_d2"] / 1e9, 0.005)
    check("dealer overstated_pct", D["overstated_pct"], 100 * (reported / d["total_revenue"] - 1), 0.5)
    check("dealer jobs", D["jobs"], d["jobs"], 0)
    check("dealer overlap", D["overlap"], d["inv_overlap"], 0)
    check("dealer overlap_pct", D["overlap_pct"], 100 * d["inv_overlap_share"], 0.05)
    check("dealer labour_only", D["labour_only"], d["d2_invoices_without_parts"], 0)
    check("dealer gm_2026_reported", D["gm_2026_reported"], 100 * d["gm_2026_reported"], 0.05)
    check("dealer gm_2026_valid", D["gm_2026_valid"], 100 * d["gm_2026_valid"], 0.05)
    check("dealer gm_group", D["gm_group"], 100 * d["mv_gm"], 0.05)
    check("dealer bad_cost_rows", D["bad_cost_rows"], d["cost_anomaly_2026_rows"], 0)
    check("dealer bad_cost_excess_m", D["bad_cost_excess_m"], d["cost_anomaly_excess"] / 1e6, 0.5)
    check("dealer cagr", D["cagr"], 100 * d["cagr_2022_2025"], 0.5)
    check("dealer residual_m", D["residual_m"], d["spare_vs_d1_gap"] / 1e6, 0.05)
    check("dealer residual_2022_m", D["residual_2022_m"], d["gap_2022"] / 1e6, 0.05)
    check("dealer ratio_2022", D["ratio_2022"], d["ratio_2022"], 0.005)
    check("dealer accident_value", D["accident_value"], 100 * d["accident_repair_share_value"], 0.5)
    check("dealer accident_jobs", D["accident_jobs"], 100 * d["accident_repair_share_jobs"], 0.5)
    check("dealer insurer_share", D["insurer_share"], 100 * d["insurer_share"], 0.5)
    check("dealer insurer_customers", D["insurer_customers"], d["insurer_customers"], 0)
    c = rows(check_path)
    check("dealer cells", D["cells"], len(c), 0)
    check("dealer cells_match", D["cells_match"], sum(1 for r in c if r["status"] == "MATCH"), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=os.environ.get("IRA_REPOS", "../Marion Peter"),
                    help="folder holding ira-kenya-data, ira-kenya-insurance and ira-kenya-reinsurance")
    a = ap.parse_args()
    root = Path(a.repos)
    if not (root / "ira-kenya-data").exists():
        sys.exit(f"Cannot find the analysis repos under {root.resolve()}. Pass --repos.")
    kenya(root)

    local = Path(__file__).with_name("local_paths.json")
    skipped = []
    if local.exists():
        p = json.load(open(local, encoding="utf-8"))
        for key, fn, args in [("ifrs17", ifrs17, ("ifrs17",)), ("reserving", reserving, ("reserving",)),
                              ("pricing", pricing, ("pricing",)), ("auctions", auctions, ("auctions",)),
                              ("dealer", dealer, ("dealer", "dealer_check"))]:
            if all(k in p and Path(p[k]).exists() for k in args):
                fn(*[p[k] for k in args])
            else:
                skipped.append(key)
    else:
        skipped = ["ifrs17", "reserving", "pricing", "auctions", "dealer"]

    print(f"{OK[0]} figures match their source.")
    if skipped:
        print("Not checked (no local_paths.json entry): " + ", ".join(skipped))
    if FAIL:
        print(f"{len(FAIL)} figures do not match:")
        for f in FAIL:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
