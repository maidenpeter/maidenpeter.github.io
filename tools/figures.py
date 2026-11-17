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

# Reinsurance flows, full years 2018 to 2025 (ira-kenya-insurance/output/reinsurance_*.csv)
REINSURANCE_FLOWS = dict(
    ceded_2025=66.6,         # KSh bn of premium Kenyan general insurers ceded in 2025
    cession_2025=29.3,       # percent of their gross premium
    ceded_total=402,         # KSh bn ceded, 2018 to 2025
    motor_2025=3.2,          # percent of motor premium ceded, private and commercial together
    aviation_2025=99.3,      # percent of aviation premium ceded
    local_reinsurers=5,
    local_bound_2025=49,     # percent: the most the local reinsurers could have taken of what was ceded
    comm_2018=23.2,          # local reinsurers' commission over earned premium, percent
    comm_2025=32.0,
    lr_2018=65.1,            # their loss ratio, percent
    lr_2025=58.0,
)

# Analysis 2, claims settlement (ira-kenya-insurance/output/claims_*.csv, ira-kenya-data/validation/claims_checks.csv).
# A payment ratio is claims paid in the quarter over the claims open in the quarter, pooled over 2025's four quarters.
CLAIMS = dict(
    quarters=32,             # quarterly workbooks IRA has published, Q1 2017 to Q1 2026
    checks=12791,
    liab_2025=11.7,          # percent of open liability claims paid in an average quarter of 2025
    liab_2017=8.2,
    life_2025=78.7,          # the same for life claims
    open_2025=125141,        # liability claims outstanding at the end of 2025
    open_ksh_2025=33.4,      # KSh bn, the insurers' own estimates
    clear_2025=7.2,          # quarters of 2025 payments the outstanding claims represent
    reg_total=5,             # insurers the regulator stepped into since 2022, all among those compared
    runs=12, compared=39,    # general insurers with four quarters running under half the median insurer's liability
                             # payment ratio at some point since 2017, of the general insurers compared
    runs_acted=3,            # of the twelve, later under the regulator
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
    # the two grading scales in one condition column, and the median price at three grades (US$)
    short_max=5,
    long_max=49,
    median_g5=22100,
    median_g49=20600,
    median_g17=2600,
    top_sellers=20,          # sellers left out in the robustness check
)
AUCTION_DECILES = [-12.16, -3.22, 0.18, 2.37, 2.88, 2.86, 3.05, 3.14, 3.08, 3.34]

# ------------------------------------------------------------- Hero triangle
# tools/cas_triangles.json holds the six paid triangles the IFRS 17 case study uses.
# The home page runs a volume-weighted chain ladder on them; check_figures.py
# confirms the six reserves add up to IFRS17["undisc_bn"].

# --------------------------------------------------------------------- Apps
# Health IBNR Lab: Streamlit Projects/Health IBNR Lab/data/headline.json (checked).
# Instalment Persistency Lab: the repo README, computed by the app from its
# seeded synthetic book (not recomputed here; it needs the app's DuckDB build).
APPS = dict(
    hil_claims=64646,
    hil_be_kes=138821204,
    hil_cv=12.0,
    hil_backlog_months=3,
    hil_backlog_pct=30,
    hil_backlog_err_kes=93608488,
    hil_backlog_err_pct=50.0,
    ipl_policies=20000,
    ipl_inforce_10=57.3,
    ipl_lapsed_ratio=1.14,
    ipl_stayed_ratio=0.65,
)
IPL_URL = "https://instalment-persistency-lab.streamlit.app/"
HIL_URL = "https://maidenpeter.shinyapps.io/health-ibnr-lab/"  # from the app's rsconnect deployment record
# M-Pesa Statement to Excel: a static page in its own repo, served by GitHub Pages (no figures on its card).
MPESA_URL = "https://maidenpeter.github.io/mpesa-statement-to-excel/"
MPESA_REPO = "https://github.com/maidenpeter/mpesa-statement-to-excel"

# ----------------------------------------------------------------- Placings
# Stated by Marion, 14 November 2026.
HACKATHONS = [
    ("2026", "Third place, Kenya Re 3rd AI4 Hackathon", "Catastrophe modelling. Second runners-up nationally."),
    ("2025", "Fourth place, Kenya Re AI4 Hackathon", "A decision support tool for triaging facultative reinsurance submissions."),
]

# ------------------------------------------------- Kenya series: the story charts
# Every series below is recomputed by tools/check_figures.py from the files named on each line.
# Insurers named here appear on /kenya-insurance/ beside the method and caveats; MUA is not named.
KENYA_STORY = dict(
    # Market underwriting result and investment income, KSh bn, full years, insurers incl. micro (ira-kenya-data general_revenue_panel.csv)
    uw_inv=[(2016, -0.39, 4.58), (2018, -1.65, 5.66), (2019, -2.97, 5.98), (2020, -1.18, 6.78), (2021, -6.34, 7.15), (2022, -3.72, 6.97), (2023, -4.96, 10.02), (2024, -5.24, 18.15), (2025, -7.01, 21.31)],
    # Insurers with an underwriting profit, insurers that filed a full year (same file)
    profit_makers=[(2016, 19, 35), (2018, 15, 37), (2019, 15, 36), (2020, 15, 35), (2021, 13, 35), (2022, 14, 33), (2023, 14, 35), (2024, 12, 34), (2025, 9, 34)],
    # Underwriting result, KSh bn: motor (private plus commercial), all classes, workmen's compensation (ira-kenya-insurance class_market.csv)
    motor_market=[(2018, -3.04, -1.65, 0.84), (2019, -6.86, -2.97, 1.45), (2020, -5.44, -1.18, 1.45), (2021, -9.49, -6.34, 2.79), (2022, -7.59, -3.72, 2.61), (2023, -5.92, -4.96, 2.34), (2024, -6.1, -5.24, 1.81), (2025, -8.19, -7.01, -0.24)],
    # Medical and motor share of gross premium, percent (class_market.csv)
    mix=[(2018, 31.2, 35.9), (2019, 32.4, 34.7), (2020, 34.4, 33.0), (2021, 33.8, 31.0), (2022, 32.5, 31.9), (2023, 34.7, 28.8), (2024, 37.4, 27.4), (2025, 41.1, 27.1)],
    # Premium change to break even on 2023 to 2025 experience, percent (rate_gap.csv, recomputed at full precision)
    rate_gap=[("Motor commercial", 15.6), ("Motor private", 12.3), ("All classes", 4.4), ("Medical", 1.2)],
    # Intra-Africa Assurance, 2024 year-to-date written premium (gross direct plus inward), KSh bn, Q1 to Q4 (general_revenue_panel.csv)
    ia_ytd_2024=[0.92, 1.44, 4.32, 2.75],
    # Insurers writing over KSh 10bn a year and their share of the market, percent (structure_market.csv)
    scale=[(2016, 2, 20.6), (2018, 2, 16.5), (2019, 2, 17.5), (2020, 2, 15.9), (2021, 4, 30.4), (2022, 5, 40.3), (2023, 6, 48.6), (2024, 7, 55.3), (2025, 7, 52.9)],
    # Premium growth a year 2018 to 2025 and combined ratio 2018 to 2025, percent; name None is not named (structure_growth_results.csv)
    growth=[
        ('AAR', 12.5, 102.4),
        ('African Merchant', 8.5, 103.7),
        ('APA', 10.6, 100.6),
        ('Britam General', 9.2, 105.5),
        ('Cannon General', 13.1, 120.4),
        ('CIC General', 10.6, 103.2),
        ('Directline', -1.3, 114.2),
        ('Fidelity Shield', 12.0, 103.8),
        ('First Assurance', 9.7, 110.3),
        ('GA', 16.0, 89.6),
        ('Geminia', 1.5, 105.1),
        ('Heritage', 6.9, 96.6),
        ('ICEA Lion General', 7.1, 93.5),
        ('Intra-Africa', 16.3, 91.8),
        ('Kenindia', -0.9, 121.0),
        ('Kenya Orient', -3.7, 126.3),
        ('Kenyan Alliance', 4.2, 113.8),
        ('Madison', 11.2, 102.4),
        ('Mayfair', 17.0, 88.7),
        (None, 16.3, 136.5),
        ('NCBA Insurance', 0.0, 93.6),
        ('Occidental', -5.6, 112.5),
        ('Old Mutual General', 10.3, 100.1),
        ('Pacis', 15.3, 103.6),
        ('Pioneer', 26.2, 104.4),
        ('Takaful', 0.9, 111.5),
        ('Tausi', 9.3, 85.4),
    ],
    market_growth=8.4,
    # Market motor loss ratio by year, percent; the range is the band on the chart (class_market.csv)
    motor_lr=[(2018, 64.8), (2019, 72.4), (2020, 72.6), (2021, 80.6), (2022, 76.0), (2023, 73.3), (2024, 75.0), (2025, 75.6)],
    # Insurer-years with a motor loss ratio under 40 percent, two decimals so each prints rounded once (low_motor_loss_ratio.csv)
    low_lr=[('Invesco', 2023, 11.31), ('Trident', 2021, 13.05), ('Occidental', 2025, 21.02), ('Trident', 2022, 30.49), ('Kenyan Alliance', 2024, 30.62), ('Kenya Orient', 2025, 32.13), ('NCBA Insurance', 2018, 33.37), ('Xplico', 2022, 33.78), ('Tausi', 2018, 33.83), ('Tausi', 2020, 34.66), ('Takaful', 2019, 35.08), ('Occidental', 2024, 35.1), ('Kenyan Alliance', 2020, 35.25), ('Tausi', 2023, 36.77), ('Definite', 2025, 36.82), ('Trident', 2020, 37.15)],
    # Scorecard grade and rank by year (ira-kenya-reinsurance cedant_scorecard.csv)
    grades={
        'GA': [(2016, 'A', 2, 32), (2018, 'A', 4, 36), (2019, 'A', 2, 36), (2020, 'A', 3, 35), (2021, 'A', 5, 35), (2022, 'A', 5, 33), (2023, 'A', 5, 31), (2024, 'A', 6, 31), (2025, 'A', 6, 33)],
        'Mayfair': [(2016, 'A', 4, 32), (2018, 'A', 3, 36), (2019, 'A', 4, 36), (2020, 'A', 8, 35), (2021, 'A', 6, 35), (2022, 'A', 4, 33), (2023, 'A', 3, 31), (2024, 'A', 1, 31), (2025, 'A', 4, 33)],
        'ICEA Lion General': [(2016, 'A', 6, 32), (2018, 'A', 6, 36), (2019, 'A', 5, 36), (2020, 'A', 4, 35), (2021, 'A', 2, 35), (2022, 'A', 2, 33), (2023, 'A', 2, 31), (2024, 'A', 2, 31), (2025, 'A', 1, 33)],
        'Heritage': [(2016, 'A', 1, 32), (2018, 'A', 1, 36), (2019, 'A', 1, 36), (2020, 'A', 1, 35), (2021, 'A', 3, 35), (2022, 'A', 3, 33), (2023, 'A', 4, 31), (2024, 'A', 3, 31), (2025, 'A', 3, 33)],
        'Tausi': [(2016, 'A', 5, 32), (2018, 'A', 2, 36), (2019, 'A', 3, 36), (2020, 'A', 2, 35), (2021, 'A', 1, 35), (2022, 'A', 1, 33), (2023, 'A', 1, 31), (2024, 'A', 5, 31), (2025, 'A', 5, 33)],
        'Britam General': [(2016, 'A', 7, 32), (2018, 'B', 11, 36), (2019, 'B', 15, 36), (2020, 'B', 12, 35), (2021, 'B', 12, 35), (2022, 'A', 10, 33), (2023, 'A', 7, 31), (2024, 'A', 4, 31), (2025, 'A', 2, 33)],
        'Intra-Africa': [(2016, 'C', 21, 32), (2018, 'C', 20, 36), (2019, 'B', 14, 36), (2020, 'B', 13, 35), (2021, 'B', 14, 35), (2022, 'B', 14, 33), (2023, 'B', 13, 31), (2024, 'B', 18, 31), (2025, 'C', 20, 33)],
        'Madison': [(2016, 'C', 24, 32), (2018, 'C', 32, 36), (2019, 'C', 30, 36), (2020, 'C', 27, 35), (2021, 'C', 21, 35), (2022, 'C', 22, 33), (2023, 'C', 19, 31), (2024, 'D', 19, 31), (2025, 'D', 18, 33)],
        'Resolution': [(2016, 'D', 31, 32), (2018, 'D', 36, 36), (2019, 'D', 35, 36), (2020, 'D', 34, 35), (2021, 'D', 33, 35)],
        'Xplico': [(2018, 'C', 29, 36), (2019, 'C', 31, 36), (2022, 'D', 29, 33)],
        'Invesco': [(2016, 'D', 30, 32), (2018, 'D', 35, 36), (2022, 'E', 33, 33), (2023, 'E', 31, 31)],
        'Trident': [(2016, 'C', 20, 32), (2018, 'C', 27, 36), (2019, 'C', 29, 36), (2020, 'C', 29, 35), (2021, 'C', 22, 35), (2022, 'C', 20, 33)],
        'Corporate': [(2019, 'C', 32, 36), (2020, 'D', 30, 35), (2021, 'C', 28, 35)],
    },
    # Intra-Africa return quality pillar score by year, 0 to 100 (cedant_scorecard.csv)
    ia_return_quality=[(2016, 100.0), (2018, 100.0), (2019, 100.0), (2020, 100.0), (2021, 100.0), (2022, 100.0), (2023, 100.0), (2024, 10.0), (2025, 10.0)],
    # Local reinsurers' underwriting result, KSh bn, and Kenya Re's (general_revenue_panel.csv, reinsurer segment)
    reinsurers=[(2016, 1.16), (2018, -0.4), (2019, -2.15), (2020, 0.35), (2021, 0.75), (2022, 1.38), (2023, 0.59), (2024, 0.35), (2025, -0.94)],
    kenya_re_2025=-1.58,
    # Motor underwriting result 2018 to 2025 for the three insurers that made money on it, KSh bn (loss_concentration.csv)
    motor_winners=[("Trident", 0.57), ("Mayfair", 0.4), ("GA", 0.12)],
    # Five largest shares of the motor loss 2018 to 2025, KSh bn (loss_concentration.csv)
    motor_losers=[('Britam General', -6.07), ('Directline', -3.66), ('Sanlam Allianz General', -3.57), ('CIC General', -3.52), ('Geminia', -3.44)],
    # Single figures the story prose uses
    premium_2025=227.17,     # KSh bn written premium, 2025 (structure_market.csv)
    hhi_equal_2025=19,       # equivalent number of equal-sized insurers, 18.86 rounded (structure_market.csv)
    exp_small_2025=34,       # median management expenses over gross premium, insurers under KSh 3bn, percent (expense_scale.csv, 33.6)
    exp_large_2025=15,       # the same, insurers over KSh 10bn (14.7)
    motor_insurers=40,       # insurers that wrote motor 2018 to 2025 (loss_concentration.csv rows)
    motor_top10=62,          # share of the motor loss carried by the ten largest losers, percent (loss_concentration.csv, 0.6154)
    profit_every_year=5,     # insurers with an underwriting profit in every full year 2018 to 2025 (general_revenue_panel.csv)
    ia_phantom=2.4,          # KSh bn underwriting profit the bad Q3 2024 return would add (ira-kenya-data README, quality_flags.csv)
    britam_equity=(2.54, 8.41),  # Britam General equity, KSh bn, 2019 and 2025 (cedant_scorecard.csv)
    sens=(0.97, 0.99),
    medical_top3_2025=44,    # share of medical premium written by the three largest medical insurers, percent (structure_class_mix.csv)
    robust_thresholds=(35, 45, 50),  # other loss ratio thresholds at which the gap stays significant, p < 0.05 (low_motor_loss_ratio_test.csv)       # range of rank correlations under alternative weights (sensitivity.csv, 0.973 to 0.995)
    # What happened to each insurer with a motor loss ratio under 40 percent, and whether it counts as trouble
    # (low_motor_loss_ratio.csv: regulator_action, negative_equity_years, below_capital_floor_years)
    low_notes={
        "Invesco": ("liquidated, Dec 2023", True), "Trident": ("statutory management, Mar 2026", True),
        "Xplico": ("statutory management, Dec 2023", True), "Kenya Orient": ("negative equity 2024 and 2025", True),
        "Kenyan Alliance": ("negative equity 2023 to 2025", True), "Takaful": ("below the capital floor in 5 years", True),
        "Definite": ("below the capital floor, 2025", True), "Occidental": ("below the capital floor, 2023", True),
        "NCBA Insurance": ("none found", False), "Tausi": ("none found", False),
    },
    # The five insurers the regulator stepped into: action, month, and years after their last score with
    # no full-year return or too little premium to score (regulator_actions.csv, backtest.csv, not_scored.csv)
    failed=[
        ("Resolution", "Statutory management", "Apr 2022", {"2022": "no return"}),
        ("Xplico", "Statutory management", "Dec 2023", {"2016": "no return", "2020": "no return", "2021": "no return", "2023": "no return"}),
        ("Invesco", "Liquidation", "Dec 2023", {"2019": "no return", "2020": "no return", "2021": "no return"}),
        ("Trident", "Statutory management", "Mar 2026", {"2023": "no return", "2024": "no return", "2025": "no return"}),
        ("Corporate", "Statutory management", "Mar 2026", {"2016": "too small", "2018": "too small", "2022": "no return", "2023": "too small", "2024": "too small", "2025": "no return"}),
    ],
)

# IFRS 17 charts (ifrs17_site.json): mean years to payment and coefficient of variation by line, and the
# risk adjustment by confidence level, US$m, six lines added together and treated as independent.
IFRS17_VIZ = dict(
    dur=[('Private motor', 1.47), ('Commercial motor', 1.78), ("Workers' compensation", 2.06), ('General liability', 2.14), ('Medical malpractice', 2.29), ('Product liability', 2.28)],
    cv=[('Private motor', 3.8), ('Commercial motor', 3.7), ("Workers' compensation", 5.6), ('General liability', 6.6), ('Medical malpractice', 8.6), ('Product liability', 24.6)],
    ra_conf=[(60, 288.8, 181.6), (70, 625.8, 374.5), (75, 819.0, 484.7), (80, 1038.3, 603.4), (90, 1599.2, 922.3), (95, 2065.6, 1155.5), (99, 3034.1, 1651.0)],
)
