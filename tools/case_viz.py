"""Charts for the three case studies (dealer revenue, IFRS 17 measurement, reserve adequacy).

Each function returns one chart panel; tools/build.py places it in the page. Numbers come from
tools/figures.py (DEALER, IFRS17, IFRS17_VIZ, ADEQUACY), which check_figures.py checks against source.
"""
from figures import DEALER as D, IFRS17 as I, IFRS17_VIZ as IV, ADEQUACY as Q
from viz import figure, key, table, columns, dotrows, split


def n(v):
    return f"{v:,}"


# ------------------------------------------------------------------ dealer revenue
def dealer_revenue():
    real, twice = D["actual_bn"], D["double_bn"]
    return figure(
        "What the reported revenue was made of",
        split([("pos", "Revenue", real, f"KSh {real}bn"), ("neg", "Counted twice", twice, f"KSh {twice}bn")],
              f"Reported revenue of KSh {D['reported_bn']}bn: KSh {real}bn of real revenue and KSh {twice}bn counted twice."),
        sub=f"KSh billions, January 2022 to August 2026. The bar is the KSh {D['reported_bn']}bn in use when the brief arrived.",
        key=key([("pos", f"Revenue, KSh {real}bn"), ("neg", f"Counted twice, KSh {twice}bn: the same parts again, through the job ledger")]),
        table=table(["Part", "KSh bn"], [["Revenue", real], ["Counted twice", twice], ["Reported", D["reported_bn"]]]))


def dealer_jobs():
    both, labour = D["overlap"], D["labour_only"]
    return figure(
        "Job invoices that also appear on the parts ledger",
        split([("neg", "In both ledgers", both, n(both)), ("neu", "Labour only", labour, n(labour))],
              f"{n(both)} of {n(D['jobs'])} job invoices, {D['overlap_pct']}%, also appear on the parts ledger; {n(labour)} are labour only."),
        sub=f"{n(D['jobs'])} service job invoices, matched by invoice number.",
        key=key([("neg", f"In both ledgers: {n(both)}, {D['overlap_pct']}%"), ("neu", f"Labour only, no parts: {n(labour)}")]),
        table=table(["Job invoices", "Count"], [["In both ledgers", n(both)], ["Labour only", n(labour)], ["All", n(D["jobs"])]]))


def dealer_mix():
    rows = [("Job value", "accident repair", D["accident_value"]), ("Jobs", "accident repair", D["accident_jobs"]),
            ("Revenue", f"{D['insurer_customers']} insurers as customers", D["insurer_share"])]
    bars = "".join(f'<div class="vz-splitrow"><span class="vz-name">{a}<small>{b}, {v}%</small></span>'
                   + split([("neu", b, v, f"{v}%"), ("ctx", "Everything else", 100 - v, "")], f"{a}: {b} {v}%, everything else {100 - v}%")
                   + "</div>" for a, b, v in rows)
    return figure(
        "Where the corrected revenue comes from",
        f'<div class="vz-splits">{bars}</div>',
        sub="Percent, on the corrected base.",
        key=key([("neu", "The part named on the left"), ("ctx", "Everything else")]),
        table=table(["Measure", "Part", "Share"], [[a, b, f"{v}%"] for a, b, v in rows]),
        note=f"Accident repair is {D['accident_value']}% of job value from {D['accident_jobs']}% of jobs: a commercial opportunity and a capacity risk in one number. "
             f"With {D['insurer_share']}% of revenue from {D['insurer_customers']} insurers, growth carries more concentration risk.")


# ------------------------------------------------------------------ IFRS 17
def ifrs17_duration():
    rows = [(nm, "", [(v, "neu", f"{nm}: mean time to payment {v} years", f"{v} yrs")]) for nm, v in IV["dur"]]
    return figure(
        "How long each line waits to be paid",
        dotrows(rows, 1, 4, [1, 1.5, 2, 2.5, 3, 3.5, 4], lambda v: f"{v:g}",
                "Mean years to payment by line: " + ", ".join(f"{nm} {v}" for nm, v in IV["dur"]) + "."),
        sub="Mean time to payment of the outstanding reserve, years. The longer the wait, the more discounting takes off.",
        table=table(["Line", "Mean years to payment"], [[nm, v] for nm, v in IV["dur"]]),
        note=f"Discounted at a flat {I['rate']}%, mid-year. No tail beyond development year 10, so every duration here is understated.")


def ifrs17_ra():
    ra = IV["ra_conf"]
    i75 = next(i for i, (c, *_) in enumerate(ra) if c == 75)
    i95 = next(i for i, (c, *_) in enumerate(ra) if c == 95)
    return figure(
        "The risk adjustment depends on the confidence level you choose",
        columns([f"{c}th" for c, _, _ in ra], [("neg", "Lines added together", [s for _, s, _ in ra]), ("neu", "Lines independent", [x for _, _, x in ra])],
                f"Risk adjustment, US$m, by confidence level: at the 75th percentile US${ra[i75][1]:,.0f}m added together and US${ra[i75][2]:,.0f}m treating lines as independent; "
                f"at the 95th US${ra[i95][1]:,.0f}m added together.",
                lambda v: f"US${v:,.0f}m", tick_fmt=lambda v: f"{v:,.0f}", height=210,
                marks={(0, i75): f"{ra[i75][1]:,.0f}", (1, i75): f"{ra[i75][2]:,.0f}", (0, i95): f"{ra[i95][1]:,.0f}"}),
        sub="US$ millions, six lines. The percentile of the bootstrapped reserve, less its mean, discounted.",
        key=key([("neg", "Six lines added together: all go wrong at once"), ("neu", "Lines treated as independent")]),
        table=table(["Confidence level", "Added together, US$m", "Independent, US$m"], [[f"{c}th", f"{s:,.0f}", f"{x:,.0f}"] for c, s, x in ra]),
        note=f"{I['sims']:,} bootstrap simulations per line, with process variance.")


def ifrs17_cv():
    rows = [(nm, "", [(v, "neg" if nm == "Product liability" else "neu", f"{nm}: coefficient of variation {v}%", f"{v}%")]) for nm, v in IV["cv"]]
    return figure(
        "How uncertain each line's reserve is",
        dotrows(rows, 0, 50, [0, 10, 20, 30, 40, 50], lambda v: f"{v:g}%",
                "Coefficient of variation of the simulated reserve by line: " + ", ".join(f"{nm} {v}%" for nm, v in IV["cv"]) + "."),
        sub="Coefficient of variation of the bootstrapped reserve: standard deviation over mean.",
        key=key([("neg dot", "The line the risk adjustment pushes up"), ("neu dot", "The other five")]),
        table=table(["Line", "Coefficient of variation"], [[nm, f"{v}%"] for nm, v in IV["cv"]]))


# ------------------------------------------------------------------ reserve adequacy
SOURCE = "Source: IRA quarterly claims settlement statistics, read and checked in ira-kenya-data."


def adequacy_years():
    Y = Q["years"]; ys = list(Y)
    a = [Y[y]["raised_pct"] for y in ys]; b = [Y[y]["printed_pct"] for y in ys]
    return figure(
        "How far the estimates of reported claims were raised",
        columns(ys, [("neg", "Read from the balances", a), ("ctx", "IRA's printed revisions", b)],
                "Raises as a percent of the claims outstanding at the start of the year: "
                + ", ".join(f"{y} {x:.1f}% from the balances and {z:.1f}% in IRA's printed column" for y, x, z in zip(ys, a, b)) + ".",
                lambda v: f"{v:.1f}%", tick_fmt=lambda v: f"{v:g}%", height=210,
                marks={(0, i): f"{v:.0f}%" for i, v in enumerate(a)}),
        sub="Percent of the claims outstanding at the start of each year, general insurers with KSh 100m or more outstanding.",
        key=key([("neg", "Read from the balances"), ("ctx", "IRA's printed revisions column, its one misprinted row left out")]),
        table=table(["Year", "Insurers", "Outstanding at the start", "Raised, from the balances", "Printed revisions", "Per KSh 100 reported"],
                    [[y, Y[y]["n"], f"KSh {Y[y]['start_bn']}bn", f"{Y[y]['raised_pct']}%", f"{Y[y]['printed_pct']}%", f"KSh {Y[y]['per_100_reported']:.0f}"] for y in ys]),
        note=SOURCE)


def adequacy_insurers(lo=-100, hi=250):
    years = list(Q["years"])
    cls = lambda v: "neg" if v > 5 else ("pos" if v < -5 else "ctx")
    rows = []
    for vals in reversed(Q["insurers3"]):        # the highest average at the top
        k = sum(1 for v in vals if v > 5)
        dots = [(min(max(v, lo), hi), cls(v), f"{y}: {v:+.1f}%", f"{v:.0f}%" if v > hi else "") for y, v in zip(years, vals)]
        rows.append((f"{k} of 3", "", dots))
    over = [v for vals in Q["insurers3"] for v in vals if v > hi]
    return figure(
        "Each insurer, three years",
        dotrows(rows, lo, hi, [-100, -50, 0, 50, 100, 150, 200, 250], lambda v: "0" if v == 0 else f"{v:+g}%",
                f"Raises for each of the {Q['three_years']} insurers in all three years: {Q['up_every_year']} raised by more than 5% every year, "
                f"{Q['down_every_year']} lowered by more than 5% every year.", band=(-5, 5, "within 5%")),
        sub="Raises as a percent of each insurer's claims outstanding at the start of the year, one dot for each of 2023, 2024 and 2025. "
            "One row per insurer, unnamed, the highest average at the top. On the left, the years it raised by more than 5%.",
        key=key([("neg dot", "Raised by more than 5%"), ("ctx dot", "Within 5%"), ("pos dot", "Lowered by more than 5%")]),
        table=table(["Insurer", *years], [[str(i), *[f"{v:+.1f}%" for v in vals]] for i, vals in enumerate(reversed(Q["insurers3"]), 1)]),
        note=(f"{len(over)} value above the scale ({', '.join(f'{v:.0f}%' for v in over)}) is drawn at its edge and labelled. " if over else "") + SOURCE)
