# Ask the data: plan

The page at `/ask/` answers pre-written questions about Kenya's general insurance market from a compact file of
derived figures, `assets/ask/data.json`. Every answer is computed in the browser by `assets/ask/ask.js` from that
file. There is no language model, no server and no request to anything outside the site.

## Data file

`tools/build_ask.py --repos ..` reads the processed tables and writes `assets/ask/data.json`. Same inputs give
the same bytes. The file records the commit of each source repo, and the page prints them in its Methods note.

| Input | Used for |
|---|---|
| `ira-kenya-data/data/processed/general_revenue_panel.csv` (Q4, segment insurer) | insurer totals per full year |
| `ira-kenya-data/data/processed/general_by_class_panel.csv` (Q4, segment insurer, 2018 to 2025) | insurer figures per class per year |
| `ira-kenya-data/reference/company_crosswalk.csv` | display names and the names IRA printed |
| `ira-kenya-data/validation/quality_flags.csv` (flag not_filed, Q4) | years with no full-year return |
| `ira-kenya-reinsurance/output/cedant_scorecard.csv`, `not_scored.csv`, `backtest.csv` | the scorecard answers |
| `marionpeter-portfolio/tools/cas_triangles.json` | the six chain ladder reserves |

### Fields (the complete list; `tools/check_ask.py` fails on any other key)

Money is KSh thousands, as in the processed tables, rounded to three decimals (the shilling).

- `v`, `sources` (repo name to commit), `unit`
- `years`: full years with insurer totals (2016, 2018 to 2025). `cyears`: full years with class figures (2018 to 2025).
- `classes`: the 13 classes as the Loss Map uses them (Motor Commercial PSV inside Motor Commercial).
- `ins`: one entry per insurer: `id`, `n` (name), `s` (short name, the scorecard's rule), `a` (names IRA printed), `m` (micro insurer).
- `tot[id][year]`: `[written premium, net earned premium, incurred claims, commissions plus management expenses, underwriting result, investment income]`. Present only where the insurer appears in that year's Q4 returns.
- `nf[id]`: years whose Q4 return was not filed.
- `cls[id][year][class index]`: `[gross premium, net earned premium, incurred claims, underwriting result]`. Present only where any of the four is non-zero.
- `sc[id][year]`: `[grade, grade before the cap, rank, peers, score, four pillar scores, watch flags]`. `ns[id][year]`: why it was not scored.
- `bt`: the back-test rows as `backtest.csv` has them (id, event, event date, last scored year, grade, rank, peers, bottom fifth, what happened after the last score, source link).
- `mg`: absorbed company to the company it merged into, read from `MERGERS` in `ira-kenya-insurance/src/structure/build.py`.
- `tri`: per line, `[name, paid to date, ultimate, reserve]` in US$ thousands.
- `i17`: the IFRS 17 case study's undiscounted reserve (US$bn), discounting effect (US$bn), discount rate (%) and 75th percentile risk adjustment (US$m), from `tools/figures.py`, which `check_figures.py` ties to their source.

Size: 163 KB, 69 KB compressed. It is fetched only when `/ask/` opens.

This is the level of detail the Insurer Explorer already publishes: per insurer, per class, per year, and less
than it (no quarters, no balance sheet, no commission and expense split by class). No raw extracted rows, no
table that could be downloaded, no export button.

## Definitions (quoted in the page's Methods note)

| Term | Definition | Source |
|---|---|---|
| Full year | Q4 year to date; 2017 has no Q4 workbook online | `ira-kenya-data/docs/data_dictionary.md` line 9, `README.md` line 25 |
| Market | insurers only, micro insurers included, reinsurers left out | `ira-kenya-insurance/src/profitability/build.py` lines 21 to 23 |
| Written premium | gross direct premium plus inward reinsurance | `ira-kenya-data/README.md` line 25 |
| Net earned premium | net premium written plus reserves brought forward less reserves carried forward | `data_dictionary.md` line 30 |
| Incurred claims | net incurred claims | `data_dictionary.md` line 31 |
| Underwriting result | net earned premium less claims, commissions and expenses | `data_dictionary.md` line 34 |
| Investment income | investment income allocated to general business | `data_dictionary.md` line 35 |
| Loss ratio | incurred claims over net earned premium, where earned premium is positive | `ira-kenya-insurance/src/profitability/build.py` lines 58 to 59 |
| Combined ratio | claims, commissions and management expenses over net earned premium | `ira-kenya-data/explorer/template.html` line 417 |
| Market share | written premium over the total of insurers with positive written premium | `ira-kenya-insurance/src/structure/build.py` lines 49 to 54 |
| Class | Motor Commercial PSV counted in Motor Commercial | `ira-kenya-insurance/src/profitability/build.py` line 53 |
| Grade | score bands A 70 and above, B 55, C 40, D 25, E below; negative equity or capital under the floor caps it at D | `ira-kenya-reinsurance/src/scorecard/score.py` lines 36 to 56 |
| Bottom fifth | rank above 0.8 times the number scored | `ira-kenya-reinsurance/src/scorecard/backtest.py` line 67 |
| Reserve | volume-weighted chain ladder on the paid triangle, ultimate less paid to date | `tools/build.py` `chain_ladder()` |

## Questions shipped (22)

Every question in the brief shipped; none was dropped.

| Group | Question | Slots |
|---|---|---|
| The market | Which class lost the most money from {y1} to {y2}, and which made the most? | 2018 to 2025 |
| | How did the market's underwriting result compare with its investment income in {yr}? | 2016, 2018 to 2025 |
| | How many insurers made an underwriting profit in {yr}? | 2016, 2018 to 2025 |
| | How concentrated was the market in {yr}? | 2016, 2018 to 2025 |
| | What has motor's loss ratio been each year? | |
| Any insurer | How did {ins} do on {cls} in {yr}? | 47 insurers, 13 classes, 2018 to 2025 |
| | What is {ins}'s trend from {y1} to {y2}? | 2016, 2018 to 2025 |
| | Where did {ins} rank by premium in {yr}, and how has its share moved? | 2016, 2018 to 2025 |
| | Which classes did {ins} write the most of in {yr}? | 2018 to 2025 |
| A reinsurer's view | Where did {ins} sit on the Cedant Scorecard in {yr}, and what drives its score? | the years scored |
| | Which insurers grew fastest in {yr}, and at what combined ratio? | 2019 to 2025 |
| | How did the scorecard rank insurers a year before the regulator acted? | |
| Reserving | Which line needs the largest reserve, and why? | |
| | How much of {line}'s ultimate is still unpaid? | six lines |
| | How do the six reserves add up, and how does that tie to the IFRS 17 case study? | |
| About Marion | Has she done {topic}? | IBNR reserving, IFRS 17, pricing, reinsurance analysis, health insurance |
| | Has she worked with mobile money or M-Pesa data? | |
| | Can she get clean data out of messy PDFs? | |
| | Which tools does she use: R, Python, SQL, Excel? | |
| | How does she check her numbers? | |
| | What has she built that I can open now? | |
| | How do I contact her? | |

Decisions made while building, where the brief left room:

- Class questions run 2018 to 2025, as the Loss Map does: IRA's 2016 class tables have no earned premium or expense split.
- "Over KSh 10bn" follows the repo's code (`>=`), so the page says "KSh 10bn or more".
- Rank in a class is by gross premium among insurers that wrote it that year. Rank in the market is by written premium. Equal premiums share a rank and are called joint.
- Growth counts merged companies together in both years, as the Market Structure page does. It counts only insurers that filed their own full-year return in both years and had at least KSh 500m of premium the year before (the scorecard's size floor). Without this, a merger or a missing return reads as growth: MUA in 2021 (Saham merged in) and Sanlam Allianz General in 2025 (no 2024 return).
- Every answer about an insurer carries the names IRA printed for it. An insurer that took another one over carries the same as-filed merger note, whichever insurer it is.
- The default insurer is the largest by written premium in the latest full year (CIC General); the default class is Motor Private; the default year is the latest full year.
- About Marion answers are quotes from pages already on the site, each with a link. `check_ask.py` fails if a quote is not on the page it cites. Links to the two live apps say they may take a few seconds to load.

## The page

A conversation in one centred column. A welcome message holds the questions under five topic tabs (arrow keys move between them); each question is a pill asked in one click with its usual values (the latest full year, Motor Private, the largest insurer), and those values are marked in the text. The visitor's question sits on the right, the answer below it as a plate in the site's double rule: the finding, the numbers, the chart and its table, the source, the caveat when an insurer is named, then "Change the question" (its insurer, class or year as dropdowns) and "Ask next" (two or three related questions carrying the same insurer and year). The box to type in is held at the bottom of the window, above the phone navigation bar, with "All questions" and "Clear answers" under it.

## Charts

The site draws every chart as HTML and CSS from `tools/viz.py` (no SVG, no library). The answers use the same
markup and the classes already in `assets/viz.css`, so they follow both themes and the validated palette. This
is a change from the brief, which asked for inline SVG; matching the house style seemed the better reading of it.

## Checks

The sample is 117 questions, seeded so it is the same every run. It covers:

- every question, every class, and the first and last years
- the six merged or renamed companies and the smallest insurer
- a year before an insurer existed, a year with no Q4 return, and an insurer with no business in a class
- a capped grade, a year not scored, and unknown slot values
- a tie made up for the test, since no real ties exist in the data

- `tools/check_ask.py --repos ..` (802 checks pass):
  - every figure in `data.json` is rebuilt from the processed tables by separate code;
  - the sample is answered from those full-precision tables and must read word for word as from `data.json`;
  - market totals tie to `class_market.csv`, `structure_market.csv` and `structure_shares.csv`;
  - the scorecard ties to `cedant_scorecard.csv`;
  - the answer links resolve.
- `tools/check_ask.py`, run in CI without the data repos (234 checks pass):
  - the field list above;
  - the page's engine, run in Node, against `tools/ask_answers.py` on the committed `data.json`;
  - every chart class `ask.js` writes is styled;
  - every About quote is on its page;
  - every `/ask/#q=` link on the site is valid.
- `tools/check_ask_page.py` (632 checks pass): asks the sample through the real page in Chrome at 1280 and 390 px, in both themes, and compares the rendered sentences, numbers, tables, links and caveats with Python. It also checks:
  - typed text that matches nothing, and typed questions that match;
  - topic tabs, the keyboard, changing a question, the follow-up questions, Clear and the live region;
  - sideways scrolling and WCAG AA contrast;
  - console errors.
- `tools/screenshots.py` includes `/ask/` empty, with an insurer answer and with a market answer.

## Swahili strings

None. The site has no English and Swahili labels, so the page adds none and there is nothing to review.

## For Marion

- Confirm that per insurer, per class, per year figures on `/ask/` are fine to publish, given the Insurer Explorer already shows that level (and more).
- Any recruiter question to add to About Marion. It can only quote what the site already says.
- The site lists R and SQL only on the two app cards; the About page's tools line does not mention them. The tools answer quotes both.
