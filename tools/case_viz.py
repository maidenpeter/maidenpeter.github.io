"""Charts for the three case studies (dealer revenue, IFRS 17 measurement, valuation adequacy).

Each function returns one chart panel; tools/build.py places it in the page. Numbers come from
tools/figures.py (DEALER, IFRS17, IFRS17_VIZ, AUCTIONS), which check_figures.py checks against source.
"""
from figures import DEALER as D, IFRS17 as I, IFRS17_VIZ as IV, AUCTIONS as A
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
        dotrows(rows, 1, 3, [1, 1.5, 2, 2.5, 3], lambda v: f"{v:g}",
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
        dotrows(rows, 0, 30, [0, 10, 20, 30], lambda v: f"{v:g}%",
                "Coefficient of variation of the simulated reserve by line: " + ", ".join(f"{nm} {v}%" for nm, v in IV["cv"]) + "."),
        sub="Coefficient of variation of the bootstrapped reserve: standard deviation over mean.",
        key=key([("neg dot", "The line the risk adjustment pushes up"), ("neu dot", "The other five")]),
        table=table(["Line", "Coefficient of variation"], [[nm, f"{v}%"] for nm, v in IV["cv"]]))


# ------------------------------------------------------------------ valuation adequacy
def auctions_cancel():
    gross, net = A["gross_m"], A["net_m"]
    gone = round(gross - net, 1)
    return figure(
        "Errors that cancel out between condition bands",
        split([("neg", "Net error", net, f"US${net}m"), ("ctx", "Cancels out", gone, f"US${gone}m")],
              f"US${gross}m of gross misvaluation across condition bands: US${net}m left net, US${gone}m cancels out between bands valued too high and too low."),
        sub=f"US$ millions. The misvaluation in each condition band, added up without signs: US${gross}m.",
        key=key([("neg", f"Net error left after offsets: US${net}m"), ("ctx", f"Offsets between bands valued too high and too low: US${gone}m, {A['cancel']}%")]),
        table=table(["Part", "US$m"], [["Gross misvaluation", gross], ["Cancels out", gone], ["Net", net]]),
        note=f"A net error of {A['net_pct']}% looks like accuracy. It is cancellation: the mean absolute error is still US${A['mae']:,} per car, {A['mae_pct']}% of the estimate.")
