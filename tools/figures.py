"""Every number the site prints, in one place.

Pages read their figures from here, and tools/check_figures.py recomputes each
one from the files it came from. Kenya figures come from the published CSVs in
ira-kenya-data, ira-kenya-insurance and ira-kenya-reinsurance. The earlier case
studies come from their own output files, listed in each section.
"""

# ---------------------------------------------------------------- Kenya series
# Sources: ira-kenya-data (data/raw/manifest.csv, data/processed/*.csv,
# validation/*.csv), ira-kenya-insurance/output/*.csv,
# ira-kenya-reinsurance/output/*.csv.
KENYA = dict(
    quarters=35,             # Q4 2016 to Q1 2026
    companies=52,            # after the name crosswalk
    files=165,               # IRA files catalogued, from 2008
    first_year=2008,
    revenue_rows=21900,
    class_rows=211785,
    checks=42246,
    unexplained=0,
    failed_checks=97,        # every one traced to a documented IRA publishing error
    pdf_match=12,
    pdf_total=12,
    error_returns=12,        # returns flagged as errors and kept out of quarterly totals
    # Underwriting result, full years 2018 to 2025, KSh bn
    uw_market=-33.06,
    uw_motor=-52.63,
    uw_motor_private=-29.25,
    uw_motor_commercial=-23.38,
    uw_other=19.57,
    uw_wc=13.06,
    motor_loss_years=8,      # of the 8 years 2018 to 2025
    # Insurers with an underwriting profit (full year, insurers that filed)
    profit_2016=19, active_2016=35,
    profit_2025=9, active_2025=34,
    uw_2025=-7.01,           # KSh bn
    inv_2025=21.31,          # KSh bn
    # Premium change to break even, 2023 to 2025 experience (percent)
    rate_mc=15.6,
    rate_mp=12.3,
    # Motor loss ratios under 40 percent
    low_lr_insurers=10, low_lr_trouble=8,
    other_insurers=28, other_trouble=7,
    fisher_p=0.006,
    # Cedant scorecard back-test
    bt_bottom=3, bt_total=5,
    scored_2025=33,
    # Market structure
    over10_2020=2, share10_2020=16,
    over10_2025=7, share10_2025=53,
    losing_n=10, median_cr_losing=112.0,
    gaining_n=17, median_cr_gaining=103.2,
    frag=23.9,               # KSh bn extra management expense outside the five largest, 2018 to 2025
    hhi_2025=530,
)

# Underwriting result by class, 2018 to 2025, KSh bn (ira-kenya-insurance/output/class_market.csv)
CLASS_RESULTS = [
    ("Motor private", -29.25),
    ("Motor commercial", -23.38),
    ("Medical", -2.54),
    ("Engineering", -0.85),
    ("Aviation", -0.68),
    ("Personal accident", 0.52),
    ("Liability", 0.90),
    ("Fire industrial", 0.95),
    ("Fire domestic", 0.96),
    ("Miscellaneous", 0.98),
    ("Theft", 2.72),
    ("Marine", 3.54),
    ("Workmen's compensation", 13.06),
]

# Last scorecard rank before the regulator acted (ira-kenya-reinsurance/output/backtest.csv).
# Names stay on the scorecard page; the home page shows positions only.
BACKTEST = [
    # (year the regulator acted, rank, insurers scored, in bottom fifth)
    (2022, 33, 35, True),
    (2023, 29, 33, True),
    (2023, 33, 33, True),
    (2026, 20, 33, False),
    (2026, 28, 35, False),
]

# ------------------------------------------------------ Dealer revenue integrity
# Source: the analysis outputs (headline_results.json, python_comparison.csv).
# Client data and code stay private; only counts and percentages are shown.
DEALER = dict(
    rows=347852,
    parts_rows=185699,
    job_rows=30787,
    consumption_rows=131366,
    reported_bn=2.83,        # parts ledger plus job ledger, as summed in the brief
    actual_bn=1.76,
    double_bn=1.07,
    overstated_pct=61,
    jobs=30779,
    overlap=28666,
    overlap_pct=93.1,
    labour_only=2113,
    gm_2026_reported=6.7,
    gm_2026_valid=23.4,
    gm_group=23.9,
    bad_cost_rows=447,
    bad_cost_excess_m=52,
    cells=5189,
    cells_match=5189,
    cagr=27,
    residual_m=27.3,         # job ledger parts value above the parts ledger, all years
    residual_2022_m=26.6,    # of which 2022, where the job ledger carries parts at 1.25 times
    ratio_2022=1.25,
    accident_value=32,       # accident repair, percent of job value
    accident_jobs=3,         # accident repair, percent of jobs
    insurer_share=26,        # insurers as customers, percent of revenue
    insurer_customers=50,
)

# --------------------------------------------------------- IFRS 17 measurement
# Source: ifrs17_site.json (5,000 bootstrap simulations per line).
IFRS17 = dict(
    undisc_bn=25.16,
    disc_effect_bn=-2.14,
    rate=5.7,
    ra75_m=819,
    ra95_bn=2.07,
    indep75_m=485,
    diversification_m=334,
    book_change=-5.5,
    prodliab_change=1.8,
    prodliab_ra=15.0,
    prodliab_disc=-11.5,
    lines=6,
    sims=5000,
    dur_low=1.47,            # mean years to payment, private motor
    dur_high=2.29,           # medical malpractice
    cv_pm=3.8,               # bootstrap coefficient of variation, private motor
    cv_pl=24.6,              # product liability
    cl_within=0.35,          # bootstrap mean within this percent of the chain ladder ...
    cl_lines_within=5,       # ... on this many lines
    cl_pl=2.4,               # product liability bootstrap mean above the chain ladder, percent
    div_pct=41,              # diversification as a share of the 75th percentile risk adjustment
)
# Change from undiscounted reserve to IFRS 17 liability, 5.7% rate, 75th percentile (percent)
IFRS17_LINES = [
    ("Private motor", -5.2),
    ("Commercial motor", -6.9),
    ("Workers' compensation", -7.0),
    ("General liability", -7.0),
    ("Medical malpractice", -6.5),
    ("Product liability", 1.8),
]
# Reserve back-test, actual over expected payments 1994 to 1997 (reserving.json)
BACKTEST_AE = dict(private_motor=0.867, all_lines=0.882, over_reserved=5, lines=6, low=6, high=13)
# Credibility pricing (pricing.json)
CREDIBILITY = dict(k_m=418, insurers=74, small_gain=11.0, small_vs_market=4.6)

# ------------------------------------------------------- Valuation adequacy
# Source: findings.json from analysis-repo/src/valuation_adequacy.py on the full file.
AUCTIONS = dict(
    rows_total=558837,
    rows=476882,
    short_scale=70101,
    long_scale=476916,
    appraised_bn=6.66,
    median_gap=0,
    below=50.0,
    net_pct=-0.59,
    net_m=39.3,
    gross_m=176.5,
    cancel=78,
    mae=1039,
    mae_pct=11.9,
    worst_band_pct=-12.7,
    best_band_pct=2.3,
    decile_low=-12.2,
    decile_high=3.3,
    excl_rows=166636,
    excl_low=-8.9,
    excl_high=3.4,
)
AUCTION_DECILES = [-12.16, -3.22, 0.18, 2.37, 2.88, 2.86, 3.05, 3.14, 3.08, 3.34]
