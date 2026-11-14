"""The Kenya series told as a story, for /kenya-insurance/: five parts and an epilogue, each with its chart.

    from kenya_story import story
    story(links)    # links: dict lossmap, structure, scorecard, explorer -> page URL

Every number comes from tools/figures.py (KENYA and KENYA_STORY); nothing is typed in here. Insurers are
named on this page, beside the caveats; the home page stays free of names.
"""
from figures import KENYA as K, KENYA_STORY as S
from viz import figure, key, table, columns, dotrows, scatter, grades, esc

WORDS = "zero one two three four five six seven eight nine ten".split()


def d1(v, sign=True):
    s = f"{abs(v):,.1f}"
    return (("+" if v > 0 else "-" if v < 0 else "") if sign else ("-" if v < 0 else "")) + s


def bn(v, sign=False):
    return f"KSh {d1(v, sign)}bn"


def word(k, cap=False):
    s = WORDS[k] if 0 <= k < len(WORDS) else str(k)
    return s.capitalize() if cap else s


def ordinal(k):
    return f"{k}{'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')}"


def whole(v):
    return f"{round(v):.0f}"   # values are stored to two decimals, so this rounds once


def grade_in(name, year):
    return next((g, rk, pe) for y, g, rk, pe in S["grades"][name] if y == year)


MONTHS = dict(Jan="January", Feb="February", Mar="March", Apr="April", May="May", Jun="June", Jul="July",
              Aug="August", Sep="September", Oct="October", Nov="November", Dec="December")


def acted(name):
    return next(when for n, _, when, _ in S["failed"] if n == name)


def month_year(when):
    m, y = when.split()
    return f"{MONTHS[m]} {y}"


def section(sid, part, title, intro, body):
    return f"""<section id="{sid}" aria-labelledby="h-{sid}">
<div class="sechead"><span class="eyebrow">{part}</span><h2 id="h-{sid}">{title}</h2>{intro}</div>
{body}
</section>"""


# ------------------------------------------------------------------ part I
def part_record(links):
    q = S["ia_ytd_2024"]
    rq = dict(S["ia_return_quality"])
    g23, g25 = grade_in("Intra-Africa", 2023)[0], grade_in("Intra-Africa", 2025)[0]
    chart = figure(
        "Intra-Africa Assurance: premium written so far in 2024",
        columns(["Q1", "Q2", "Q3", "Q4"], [(["neu", "neu", "neg", "neu"], "Year-to-date written premium", q)],
                f"Intra-Africa's year-to-date written premium in 2024: Q1 KSh {q[0]}bn, Q2 {q[1]}bn, Q3 {q[2]}bn, Q4 {q[3]}bn. "
                "A running total cannot fall, so the Q3 return is wrong.",
                lambda v: f"KSh {v:.2f}bn", tick_fmt=lambda v: f"{v:g}", height=190,
                marks={(0, i): f"{v:.2f}" for i, v in enumerate(q)}),
        sub="KSh billions, year to date, as IRA published it. A running total can only rise.",
        key=key([("neg", "The Q3 return, higher than the full year that followed"), ("neu", "Returns that can be right")]),
        table=table(["Quarter", "Year-to-date premium, KSh bn"], [[f"Q{i + 1}", f"{v:.2f}"] for i, v in enumerate(q)]),
        note="Source: IRA quarterly returns. Flagged as an error and kept out of single-quarter market totals.")
    prose = f"""<div class="prose">
<p>IRA's tables say Intra-Africa Assurance had written KSh {q[2]:.2f}bn of premium by September 2024 and KSh {q[3]:.2f}bn by December. A running total cannot fall. Left in, that one return adds a {bn(S['ia_phantom'])} underwriting profit that never happened to the market's third quarter.</p>
<p>Intra-Africa is no rogue: it is one of {word(S['profit_every_year'])} insurers that made an underwriting profit in every year from 2018 to 2025. Good companies file bad returns too, which is why every company is read across its quarters as well as checked for adding up.</p>
<p>The same checks found IRA's own printed totals wrong in three places, and tied {K['companies']} companies together through every rename and merger: UAP to Old Mutual General, AIG Kenya to NCBA Insurance, Jubilee General to Jubilee Allianz to Sanlam Allianz General.</p>
<p class="caveat">The flag follows the company. On the reinsurer's scorecard, Intra-Africa's return quality score fell from {rq[2023]:.0f} to {rq[2024]:.0f} out of 100 in 2024, and its grade slipped from {g23} to {g25}.</p>
</div>"""
    return section("record", "Part I. The record", "A return can add up on its own and still be wrong",
                   f"<p>Before any finding, the data: {K['checks']:,} checks, none unexplained, and {K['pdf_match']} of {K['pdf_total']} figures matching IRA's own PDF releases exactly.</p>",
                   f'<div class="story">{prose}{chart}</div>')


# ------------------------------------------------------------------ part II
def part_money(links):
    years = [str(y) for y, _, _ in S["uw_inv"]]
    uw = [a for _, a, _ in S["uw_inv"]]
    inv = [b for _, _, b in S["uw_inv"]]
    last = len(years) - 1
    pm = S["profit_makers"]
    assert [y for y, *_ in pm] == [y for y, *_ in S["uw_inv"]]
    c1 = figure(
        "Lost on insurance, made back on investments",
        columns(years, [("neg", "Underwriting result", uw), ("pos", "Investment income", inv)],
                f"Underwriting result and investment income, KSh bn, every full year. Underwriting lost money in every year, from {d1(uw[0])} in {years[0]} to {d1(uw[-1])} in {years[-1]}, "
                f"while investment income rose from {d1(inv[0], False)} to {d1(inv[-1], False)}.",
                lambda v: f"KSh {d1(v)}bn", tick_fmt=lambda v: f"{v:g}", height=230,
                marks={(0, last): d1(uw[-1]), (1, last): d1(inv[-1], False), (0, 0): d1(uw[0]), (1, 0): d1(inv[0], False)}),
        sub="KSh billions, every general insurer in Kenya, full years. IRA has no year-end 2017 workbook online.",
        key=key([("neg", "Underwriting result"), ("pos", "Investment income")]),
        table=table(["Year", "Underwriting result, KSh bn", "Investment income, KSh bn", "Insurers with an underwriting profit"],
                    [[y, d1(a), d1(b, False), f"{p[1]} of {p[2]}"] for (y, a, b), p in zip(S["uw_inv"], pm)]),
        note="Source: IRA quarterly returns, year to date at December.")
    pm = S["profit_makers"]
    mm = S["motor_market"]
    worst = min(range(len(mm)), key=lambda i: mm[i][1])
    c3 = figure(
        "Motor lost more than the whole market, every year",
        columns([str(y) for y, *_ in mm], [("neg", "Motor", [m for _, m, _, _ in mm]), ("ctx", "All classes", [a for _, _, a, _ in mm])],
                f"Underwriting result by year, KSh bn: motor against all classes together. Motor lost more than the whole market in each of the {word(len(mm))} years.",
                lambda v: f"KSh {d1(v)}bn", tick_fmt=lambda v: f"{v:g}", height=200,
                marks={(0, worst): d1(mm[worst][1]), (0, len(mm) - 1): d1(mm[-1][1])}),
        sub="KSh billions. Every other class together made money, so motor's loss is bigger than the market's.",
        key=key([("neg", "Motor, private and commercial"), ("ctx", "All classes")]),
        table=table(["Year", "Motor, KSh bn", "All classes, KSh bn", "Workmen's compensation, KSh bn"], [[y, d1(m), d1(a), d1(w)] for y, m, a, w in mm]),
        note="Source: IRA class tables, net of reinsurance. Motor commercial includes PSV.")
    rg = S["rate_gap"]
    c4 = figure(
        "What premiums would have to do",
        columns([n for n, _ in rg], [(["neg", "neg", "neu", "neu"], "Premium change to break even", [v for _, v in rg])],
                "Premium change each class needs to break even on 2023 to 2025 experience: " + ", ".join(f"{n} {d1(v)}%" for n, v in rg) + ".",
                lambda v: f"{d1(v)}%", tick_fmt=lambda v: f"{v:g}%", ticks=[0, 5, 10, 15, 20], height=170,
                marks={(0, i): f"{d1(v)}%" for i, (_, v) in enumerate(rg)}),
        sub="Increase needed to break even on 2023 to 2025 experience, by the loss ratio method.",
        table=table(["Class", "Premium change to break even"], [[n, f"{d1(v)}%"] for n, v in rg]),
        note="An indication of the size of the gap, not a filed rate: no loss trend or charge for capital, so the true need is higher.")
    wc = mm[-1][3]
    wc_first = all(w > 0 for *_, w in mm[:-1]) and wc < 0
    prose = f"""<div class="prose">
<p>In every full year in the data, Kenya's general insurers lost money on the business they exist to do, and made it back on investments. In {years[-1]} the gap was the widest yet: a {bn(-uw[-1])} underwriting loss covered by {bn(inv[-1])} of investment income.</p>
<p>Motor is where the money goes. From 2018 to 2025 the market lost {bn(-K['uw_market'])} on underwriting; motor alone lost {bn(-K['uw_motor'])}. Every other class together made {bn(K['uw_other'])}, {bn(K['uw_wc'])} of it from workmen's compensation.</p>
""" + (f"<p>In {mm[-1][0]} that cushion slipped too: workmen's compensation made its first underwriting loss of the {word(len(mm))} years, KSh {wc:.2f}bn.</p>\n" if wc_first else "") + """<p>The stakes are live. In September 2024 the Court of Appeal ruled that IRA can regulate premium rates, but struck down its 2009 motor guidelines because IRA had not shown that price setting was the right tool. A second attempt will need evidence of this kind.</p>
</div>"""
    return section("money", "Part II. The money", "Insurers lose money on insurance, and motor is the hole",
                   f'<p>Underwriting profit is getting rarer: {pm[0][1]} of {pm[0][2]} insurers made one in {pm[0][0]}, {pm[-1][1]} of {pm[-1][2]} in {pm[-1][0]}. <a href="{links["lossmap"]}">The Loss Map</a> has every class and insurer.</p>',
                   f'<div class="story">{prose}{c1}</div><div class="story-2">{c3}{c4}</div>')


# ------------------------------------------------------------------ part III
LABELS = {  # where each named insurer's label sits on the scatter; '*' keeps it on phones
    "GA": "l*", "Mayfair": "r*", "Intra-Africa": "tr", "Tausi": "b*", "ICEA Lion General": "br", "Heritage": "t",
    "Pioneer": "l", "Kenya Orient": "r*", "Kenindia": "r", "Directline": "tr", "Occidental": "b", "Cannon General": "r",
    "Britam General": "tl", "NCBA Insurance": "l",
}


def part_market(links):
    g = S["growth"]
    mg = S["market_growth"]
    cr = {n: (x, y) for n, x, y in g}
    pts = []
    for name, gr, c in g:
        tip = f"{name or 'An insurer whose growth came mostly from a merger (not named)'}: premium growth {d1(gr)}% a year, combined ratio {c:.1f}%"
        pts.append((gr, c, "pos" if c < 100 else "neg", tip, esc(name) if name in LABELS else "", LABELS.get(name, "")))
    sc = figure(
        "Growth against results, 2018 to 2025",
        scatter(pts, (-8, 28), (80, 140), [-5, 0, 5, 10, 15, 20, 25], [80, 90, 100, 110, 120, 130, 140],
                lambda v: f"{v:g}%", lambda v: f"{v:g}%", "Premium growth a year, 2018 to 2025", "Combined ratio, 2018 to 2025",
                f"Each dot is an insurer: premium growth a year against combined ratio, 2018 to 2025. GA and Mayfair grew about twice as fast as the market ({mg}% a year) "
                "with combined ratios under 90%. The insurers that shrank mostly ran combined ratios above 110%.",
                xref=(mg, f"Market, {mg}% a year"), yref=(100, "Break even"),
                quads=(("tl", "Shrinking and losing money"), ("br", "Growing and making money"))),
        sub="Each dot is an insurer that wrote business in both 2018 and 2025. Below the gold line is an underwriting profit.",
        key=key([("pos dot", "Underwriting profit over the period"), ("neg dot", "Underwriting loss"), ("line", "Market growth and break even")]),
        table=table(["Insurer", "Growth a year", "Combined ratio"], [[esc(n or "Not named (merger-driven growth)"), f"{d1(x)}%", f"{y:.1f}%"]
                                                                    for n, x, y in sorted(g, key=lambda t: t[2])]),
        note="Source: IRA quarterly returns. Growth is nominal. One insurer whose growth came mostly from absorbing another is shown but not named.")
    sc_ = S["scale"]
    i20 = next(i for i, (y, *_) in enumerate(sc_) if y == 2020)
    c2 = figure(
        "Scale is arriving, slowly",
        columns([str(y) for y, _, _ in sc_], [("neu", "Share held by insurers writing over KSh 10bn", [s for _, _, s in sc_])],
                f"Share of the market held by insurers writing over KSh 10bn a year: {sc_[i20][1]} insurers with {whole(sc_[i20][2])}% in 2020, {sc_[-1][1]} with {whole(sc_[-1][2])}% in {sc_[-1][0]}.",
                lambda v: f"{v:.1f}%", tick_fmt=lambda v: f"{v:g}%", ticks=[0, 20, 40, 60], height=170,
                marks={(0, i): f"{n}" for i, (_, n, _) in enumerate(sc_)}),
        sub="Share of written premium held by insurers writing over KSh 10bn a year. The number on each column is how many there were.",
        table=table(["Year", "Insurers over KSh 10bn", "Their share"], [[y, n, f"{s:.1f}%"] for y, n, s in sc_]),
        note="Premium is nominal: part of the move past KSh 10bn is inflation, but the rising share of the top ten is not.")
    mix = S["mix"]
    c3 = figure(
        "Medical is taking over the book",
        columns([str(y) for y, _, _ in mix], [("neu", "Medical", [m for _, m, _ in mix]), ("neg", "Motor", [o for _, _, o in mix])],
                f"Share of gross premium: medical rose from {whole(mix[0][1])}% in {mix[0][0]} to {whole(mix[-1][1])}% in {mix[-1][0]}, motor fell from {whole(mix[0][2])}% to {whole(mix[-1][2])}%.",
                lambda v: f"{v:.1f}%", tick_fmt=lambda v: f"{v:g}%", ticks=[0, 10, 20, 30, 40, 50], height=170,
                marks={(0, 0): whole(mix[0][1]), (1, 0): whole(mix[0][2]), (0, len(mix) - 1): whole(mix[-1][1]), (1, len(mix) - 1): whole(mix[-1][2])}),
        sub="Share of gross written premium, percent.",
        key=key([("neu", "Medical"), ("neg", "Motor, private and commercial")]),
        table=table(["Year", "Medical", "Motor"], [[y, f"{m:.1f}%", f"{o:.1f}%"] for y, m, o in mix]),
        note=f"Medical is the one large class that is concentrated: three insurers write {S['medical_top3_2025']}% of it.")
    prose = f"""<div class="prose">
<p>Kenya had {K['active_2025']} general insurers in 2025 sharing {bn(S['premium_2025'])} of premium. The Herfindahl-Hirschman index was {K['hhi_2025']}, the same as {S['hhi_equal_2025']} equal-sized insurers, and small insurers pay for it: those writing under KSh 3bn spent a median {S['exp_small_2025']}% of premium on management expenses in 2025, against {S['exp_large_2025']}% for those over KSh 10bn.</p>
<p>The market is sorting itself out, slowly. The {word(K['losing_n'])} insurers that lost share from 2018 to 2025 ran a median combined ratio of {K['median_cr_losing']}%; the {K['gaining_n']} that gained ran {K['median_cr_gaining']}%. Cheap growth is not being rewarded.</p>
<p><b>GA</b> and <b>Mayfair</b> answer the market's usual excuse. Both grew about twice as fast as the market and still made an underwriting profit, at combined ratios of {cr['GA'][1]:.1f}% and {cr['Mayfair'][1]:.1f}%. <b>Tausi</b>, a small insurer, ran {cr['Tausi'][1]:.1f}%.</p>
<p><a href="{links['structure']}">Market Structure</a> has every insurer's share, concentration by class, and every entry and exit since 2016.</p>
</div>"""
    return section("market", "Part III. The market", "A crowded market, sorting itself out slowly",
                   "<p>Who is growing, who is shrinking, and whether the market rewards pricing below cost.</p>",
                   f'<div class="story wide">{prose}{sc}</div><div class="story-2">{c2}{c3}</div>')


# ------------------------------------------------------------------ part IV
CITED = {("Trident", 2021), ("Trident", 2022), ("Invesco", 2023)}


def part_too_good(links):
    band = (min(v for _, v in S["motor_lr"]), max(v for _, v in S["motor_lr"]))
    notes = S["low_notes"]
    lo = {(n, y): v for n, y, v in S["low_lr"]}
    order = list(dict.fromkeys(n for n, _, _ in S["low_lr"]))
    order = [n for n in order if notes[n][1]] + [n for n in order if not notes[n][1]]
    rows = []
    for name in order:
        ds = [(v, "neg" if notes[name][1] else "pos", f"{name}, {y}: motor loss ratio {v:.1f}%", str(y) if (name, y) in CITED else "")
              for n, y, v in S["low_lr"] if n == name]
        rows.append((esc(name), notes[name][0], ds))
    chart = figure(
        "Motor books that look too good",
        dotrows(rows, 0, 100, [0, 20, 40, 60, 80, 100], lambda v: f"{v:g}%",
                f"Every insurer-year with a motor loss ratio under 40%, against a market that ran between {whole(band[0])}% and {whole(band[1])}%. "
                f"{word(K['low_lr_trouble'], True)} of the {word(K['low_lr_insurers'])} insurers had regulator action, negative equity or a capital shortfall at some point since 2018.",
                band=(band[0], band[1], "market"), rule=(40, "40%")),
        sub="Each dot is one year's motor loss ratio for one insurer: claims per shilling of earned premium.",
        key=key([("neg dot", "Regulator action, negative equity or a capital shortfall since 2018"), ("pos dot", "None found"), ("band", f"Market range, {whole(band[0])}% to {whole(band[1])}%, 2018 to 2025")]),
        table=table(["Insurer", "Year", "Motor loss ratio", "Since 2018"], [[esc(n), y, f"{v:.1f}%", notes[n][0]] for n, y, v in S["low_lr"]]),
        note=f"Fisher's exact test: {K['low_lr_trouble']} of {K['low_lr_insurers']} against {K['other_trouble']} of the other {K['other_insurers']} motor insurers, p = {K['fisher_p']}. The gap holds at " + ", ".join(f"{x}%" for x in S["robust_thresholds"][:-1]) + f" and {S['robust_thresholds'][-1]}%.")
    prose = f"""<div class="prose">
<p>The market's motor loss ratio ran between {whole(band[0])}% and {whole(band[1])}%. {word(K['low_lr_insurers'], True)} insurers booked a year under 40%. {word(K['low_lr_trouble'], True)} of those {word(K['low_lr_insurers'])} faced regulator action, negative equity or capital below IRA's floor at some point since 2018, against {K['other_trouble']} of the other {K['other_insurers']} motor insurers.</p>
<p><b>Trident</b> booked {whole(lo[('Trident', 2021)])}% and {whole(lo[('Trident', 2022)])}% in 2021 and 2022, then stopped filing returns. It went into statutory management in {month_year(acted('Trident'))}. <b>Invesco</b> booked {whole(lo[('Invesco', 2023)])}% in 2023, the year it was liquidated.</p>
<p>This is where an insurer's question becomes a reinsurer's. Not "is this good business?" but "can I believe these numbers?"</p>
<p class="caveat">A low loss ratio is a warning, not proof. It can reflect a good book, heavy reinsurance or thin reserves. Tausi booked three low years with no trouble at all, and Definite's 2025 figure is its first year, when claims lag premium.</p>
</div>"""
    return section("too-good", "Part IV. The warning", "A motor book that looks too good is more often a reserving question",
                   f"<p>Only three of the {S['motor_insurers']} insurers that wrote motor made money on it from 2018 to 2025. Two of them grew fast and priced properly. The third is a mirage.</p>",
                   f'<div class="story wide">{prose}{chart}</div>{motor_winners()}')


def motor_winners():
    w = S["motor_winners"]
    lo = {(n, y): v for n, y, v in S["low_lr"]}
    t21, t22 = whole(lo[("Trident", 2021)]), whole(lo[("Trident", 2022)])
    rows = [(esc(n), f"rests on two years at {t21}% and {t22}%" if n == "Trident" else "a profit the rest of the data supports",
             [(v, "neg ring" if n == "Trident" else "pos", f"{n}: motor underwriting result 2018 to 2025, KSh {v:.2f}bn", f"KSh {v:.2f}bn")]) for n, v in w]
    losers = S["motor_losers"]
    return '<div class="story-2">' + figure(
        "The only three insurers that made money on motor",
        dotrows(rows, 0, 1, [0, 0.25, 0.5, 0.75, 1], lambda v: f"{v:g}", "Motor underwriting result 2018 to 2025, KSh bn: "
                + ", ".join(f"{n} {v:.2f}" for n, v in w) + ". Trident's result rests on two implausibly low loss ratio years."),
        sub="Motor underwriting result 2018 to 2025, KSh billions.",
        key=key([("pos dot", "Supported by the rest of the data"), ("neg ring", "Rests on loss ratios too low to trust")]),
        table=table(["Insurer", "Motor result 2018 to 2025, KSh bn"], [[n, f"{v:.2f}"] for n, v in w])) + figure(
        "Who carries the motor loss",
        dotrows([(esc(n), "", [(v, "neg", f"{n}: motor underwriting result 2018 to 2025, KSh {v:.2f}bn", f"{v:.2f}")]) for n, v in losers],
                -7, 0, [-7, -6, -5, -4, -3, -2, -1, 0], lambda v: f"{v:g}",
                "The five largest motor losses 2018 to 2025, KSh bn: " + ", ".join(f"{n} {v:.2f}" for n, v in losers) + "."),
        sub=f"The five largest motor underwriting losses 2018 to 2025, KSh billions. The ten largest carry {S['motor_top10']}% of the market's motor loss.",
        table=table(["Insurer", "Motor result 2018 to 2025, KSh bn"], [[esc(n), f"{v:.2f}"] for n, v in losers]),
        note="Britam General carries the largest share, yet its balance sheet and recent results now put it near the top of the scorecard: see Part V.") + "</div>"


# ------------------------------------------------------------------ part V
COLS = ["2016", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]


def grade_cells(name, extra=None, act=None, last=None):
    cells = {}
    for y, g, rk, pe in S["grades"][name]:
        cells[str(y)] = (f"g-{g}" + (" last" if last == y else ""), g, f"{name}, {y}: grade {g}, {ordinal(rk)} of {pe}")
    for y, why in (extra or {}).items():
        cells[y] = ("nr", "", f"{name}, {y}: {'no full-year return filed' if why == 'no return' else 'premium below KSh 500m, not scored'}")
    if act:
        cells["Regulator"] = ("act", act[1], f"{name}: {act[0].lower()}, {act[1]}")
    return cells


def part_verdict(links):
    rows = [(None, "Placed under statutory management or liquidation since 2022", {})]
    lasts = {}
    for name, what, when, extra in S["failed"]:
        last = max(y for y, *_ in S["grades"][name] if y < int(when[-4:]))
        lasts[name] = grade_in(name, last)
        rows.append((esc(name), f"{what}, {when}", grade_cells(name, extra, None, last)))
    rows.append((None, "Graded A in every year scored", {}))
    for name in ("ICEA Lion General", "GA", "Mayfair"):
        rows.append((esc(name), "", grade_cells(name)))
    rows.append((None, "The comeback", {}))
    rows.append(("Britam General", "largest share of the motor loss", grade_cells("Britam General")))
    chart = figure(
        "The grades a reinsurer would have seen",
        grades(rows, COLS, "Scorecard grade by year for the five insurers the regulator stepped into since 2022, three insurers graded A in every year, and Britam General."),
        sub="Grade A to E each year on four pillars: balance sheet, underwriting, the shape of the book, and whether the returns can be trusted. Hover a grade for its rank.",
        key=key([("g-A", "A"), ("g-B", "B"), ("g-C", "C"), ("g-D", "D"), ("g-E", "E"), ("nr", "no full-year return, or too small to score")]),
        note="A framed grade is the last one before the regulator acted; the date under each name is when it did. Grades are relative to each year's peers; they are screening measures, not credit ratings.")
    b19, b25 = grade_in("Britam General", 2019), grade_in("Britam General", 2025)
    xg, xr, xp = lasts["Xplico"]
    ig, ir, ip = lasts["Invesco"]
    res_all_d = all(g == "D" for _, g, _, _ in S["grades"]["Resolution"])
    prose = f"""<div class="prose">
<p>A reinsurer asks four questions of an insurer before taking its business: does it make money on underwriting, can its balance sheet stand behind the business, what kind of book is it, and can its numbers be trusted. The scorecard answers them for every insurer, every year, from public data alone.</p>
<p>{word(K['bt_total'], True)} insurers have been placed under statutory management or liquidation since 2022. <b>Resolution</b> was graded {'D in every year scored' if res_all_d else 'low'}. <b>Xplico</b> was {ordinal(xr)} of {xp} and <b>Invesco</b> {ordinal(ir)} of {ip}, graded {ig}. {word(K['bt_bottom'], True)} of the {word(K['bt_total'])} sat in the bottom fifth a year before the regulator acted.</p>
<p>The other two, <b>Trident</b> and <b>Corporate</b>, fell out of the table because they stopped filing complete returns. Silence is a signal: a reinsurer should treat a missing return as a warning in its own right.</p>
<p><b>Britam General</b> carried the largest share of the market's motor losses, yet climbed from {ordinal(b19[1])} in 2019 to {ordinal(b25[1])} in 2025 as its results recovered and its equity rose from {bn(S['britam_equity'][0])} to {bn(S['britam_equity'][1])}. The loss map shows its past; the scorecard shows its present.</p>
<p class="caveat">{word(K['bt_total'], True)} cases is a small sample, and the test cannot show how many low-graded insurers carried on without trouble. Change the weights and the ranking barely moves: it correlates at {S['sens'][0]} to {S['sens'][1]} with the base case in every year.</p>
</div>"""
    return section("verdict", "Part V. The verdict", "The warning was in the data a year before the regulator acted",
                   f'<p>Every insurer graded the way a reinsurance underwriter screens a cedant. <a href="{links["scorecard"]}">The Cedant Scorecard</a> has every insurer and year.</p>',
                   f'<div class="story wide">{prose}{chart}</div>')


# ------------------------------------------------------------------ epilogue
def epilogue(links):
    r = S["reinsurers"]
    up = sum(v > 0 for _, v in r)
    worst = min(range(len(r)), key=lambda i: r[i][1])
    chart = figure(
        "Kenya's local reinsurers, underwriting result",
        columns([str(y) for y, _ in r], [("sign", "Underwriting result", [v for _, v in r])],
                f"Local reinsurers' underwriting result, KSh bn, by year: a profit in {word(up)} of {word(len(r))} years and a loss of {d1(r[-1][1])} in {r[-1][0]}.",
                lambda v: f"KSh {d1(v)}bn", tick_fmt=lambda v: f"{v:g}", height=170,
                marks={(0, len(r) - 1): f"{r[-1][1]:.2f}", (0, worst): f"{r[worst][1]:.2f}"}),
        sub="KSh billions, the local reinsurers together, full years.",
        key=key([("pos", "Profit"), ("neg", "Loss")]),
        table=table(["Year", "Underwriting result, KSh bn"], [[y, d1(v)] for y, v in r]),
        note=f"Source: IRA quarterly returns, reinsurer segment. Kenya Reinsurance Corporation, the largest by premium, lost KSh {-S['kenya_re_2025']:.2f}bn in {r[-1][0]} on its own.")
    prose = f"""<div class="prose">
<p>The local reinsurers made an underwriting profit in {word(up)} of the {word(len(r))} years, then lost KSh {-r[-1][1]:.2f}bn in {r[-1][0]}. Kenya Reinsurance Corporation, the largest by premium, lost KSh {-S['kenya_re_2025']:.2f}bn on its own, more than the whole group.</p>
<p>Next, the series moves from what insurers earn to whether they pay. IRA's claims settlement statistics from 2017 to 2025 are already collected. Resolution was placed under statutory management over unsettled claims; that is the human cost of everything above.</p>
</div>"""
    return section("next", "Epilogue", "Who screens the screeners?", "", f'<div class="story">{prose}{chart}</div>')


CAVEAT = ("Insurers are named from IRA's public, unaudited returns, next to the method and caveats. A grade or a low loss ratio is a screening signal, "
          "not a finding of wrongdoing, and an insurer still writing business may have explanations the returns do not show.")


def story(links):
    return "\n\n".join([f'<p class="note">{CAVEAT}</p>', part_record(links), part_money(links), part_market(links),
                        part_too_good(links), part_verdict(links), epilogue(links)])
