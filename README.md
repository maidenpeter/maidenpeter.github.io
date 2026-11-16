# maidenpeter.github.io

Marion Peter's portfolio: https://maidenpeter.github.io

The home page leads with the Kenya insurance series, built from the Insurance Regulatory Authority's quarterly returns. The live analysis pages stay in their own repositories and are linked from here, never copied:

- [ira-kenya-data](https://github.com/maidenpeter/ira-kenya-data): extraction, company crosswalk, panels, quality flags, 42,246 validation checks, and the Insurer Explorer
- [ira-kenya-insurance](https://github.com/maidenpeter/ira-kenya-insurance): the Loss Map and Market Structure
- [ira-kenya-reinsurance](https://github.com/maidenpeter/ira-kenya-reinsurance): the Cedant Scorecard, its back-test and sensitivity

## Pages

| Path | What it is |
|---|---|
| `/` | Home: a chain ladder calculated in the page, then Part I Data analysis (the Kenya series, what a reinsurer would act on, the dealer audit and two forecasting products) and Part II Actuarial analysis (the two reserving and persistency apps, AgroShield pricing, the IFRS 17 and reserve adequacy case studies), how I work, contact |
| `/kenya-insurance/` | Front page of the Kenya insurance series (its permanent address) |
| `/ask/` | Ask the data: pre-written questions about the market, any insurer, the scorecard and reserving, answered in the browser from the validated figures |
| `/work/dealer-revenue/` | Case study: a Kenyan dealer group's revenue double count (anonymised) |
| `/work/ifrs17-measurement/` | Case study: IFRS 17 discounting and risk adjustment on US industry triangles |
| `/work/valuation-adequacy/` | Case study: a reserve adequacy test on 476,882 car auctions |
| `/about/` | CV |
| `404.html`, `sitemap.xml`, `robots.txt` | The usual |

## How it is built

Static HTML, no framework. `tools/build.py` writes every page from one layout, so the head, header, footer and theme script are written once; `assets/site.css` holds the tokens for the two themes: ink (dark, the default) and paper (light), with gold for emphasis, teal for gain and oxblood for loss. Its copperplate layer matches the Kenya series plates: a grained, foxed ground, IM Fell English for headings, Old Standard TT for labels, Pinyon Script in the name line, double-ruled frames and hatched bars.

The navigation is written once in `tools/nav.py` and stays on screen on every page: a top bar with the MP seal, the name and the role in the middle, where the reader is on the left ("I Data analysis / Kenya series / Loss map"; on the home page it follows the section being read) and the theme switch and GitHub on the right; a side bar with Back, Home, the two chapters (I Data analysis, II Actuarial analysis) and their pages, Ask the data, About and Contact; and on Kenya pages a labelled series strip held under the top bar. On phones the links sit in a bar along the bottom, each chapter opening as a sheet. The build writes its CSS to `assets/nav.css`; `tools/kenya_nav.py` writes the same navigation, a skip link and the series strip into the four analysis pages in the Kenya repositories, inline, between `mp-nav` markers, so it can be run again whenever `nav.py` changes.

Every card that links somewhere carries a screenshot from `assets/shots/`, made by `tools/render_shots.py`. Work with no public link yet opens a pop-out (the `popover` attribute, so no script is needed) with a larger screenshot and the explanation.

The home page triangle is a volume-weighted chain ladder on the six NAIC Schedule P paid triangles in `tools/cas_triangles.json`, the same data as the IFRS 17 case study. The build computes it in Python so the page reads correctly without JavaScript; the page then recomputes it in the browser and fills the projected corner one calendar year at a time.

```
python tools/build.py                      # write the pages into the repo root
python tools/build.py --repo-index OUT     # also write the index page of each Kenya repo into OUT/<repo>/index.html
python tools/render_images.py              # share image, favicon.ico, Apple touch icon (needs Playwright and Chrome)
python tools/render_shots.py               # card screenshots of the Kenya pages, case studies and apps (Playwright, Chrome, Pillow)
python tools/kenya_nav.py --repos ..       # write the side bar into the Kenya analysis pages and their templates
```

Every number on the site lives in `tools/figures.py`. Nothing is typed into a page by hand.

## Ask the data

`/ask/` answers pre-written questions: which class lost the most money over a range of years, how an insurer did on a class in a year, where it sits on the Cedant Scorecard, which line needs the largest reserve, and what Marion has done, with a link to the evidence. A visitor picks a question, sets its insurer, class or year, and the page calculates the answer in the browser. There is no language model and no server: every number is a lookup, sum, rank or ratio of the derived figures in `assets/ask/data.json`.

- `tools/build_ask.py --repos ..` writes `assets/ask/data.json` from the processed tables in `ira-kenya-data`, the scorecard outputs in `ira-kenya-reinsurance` and the merger map in `ira-kenya-insurance`, and records each repo's commit. It holds per insurer, per class, per year figures at the level the Insurer Explorer already publishes; the field list is in `docs/ask-plan.md`. The file is committed, so the page works on GitHub Pages without the data repos.
- `tools/ask_bank.py` holds the questions, written once; `tools/build.py` writes them into the page. `assets/ask/ask.js` draws the question chips, computes the answers and draws the charts with the classes of `assets/viz.css`. `tools/ask_answers.py` computes the same answers in Python.
- Answers that name an insurer carry the caveat that the figures come from unaudited returns and are a screening view, not a credit opinion. Insurer names appear on `/ask/` and the Kenya pages, never on the home page.

```
python tools/build_ask.py --repos ..       # rebuild assets/ask/data.json, then run tools/build.py
python tools/check_ask.py --repos ..       # every figure rebuilt from the processed tables; a seeded sample of 115 questions
                                           # answered by the page's engine (in Node) and in Python, word for word
python tools/check_ask_page.py             # the same sample asked through the real page in Chrome, both themes, 1280 and 390 px
```

## Checks

```
python tools/check_figures.py --repos ..                  # recompute every figure from the analysis repos beside this one
python tools/check_text.py                                # plain ASCII only, no flagged phrases
python tools/check_links.py [--external]                  # internal links, assets and anchors; optionally every external URL
python tools/screenshots.py OUT                           # 1280 and 390 px, ink and paper; fails on sideways scrolling
python tools/check_ask.py [--repos ..]                    # Ask the data: see above
```

On a machine without Chrome on the default path or without internet access, set `CHROME` to the browser binary and `FONTS_DIR` to a folder of the EB Garamond, IBM Plex Sans Condensed, IM Fell English, IM Fell English SC, Pinyon Script and Old Standard TT `.woff2` files.

`check_figures.py` also checks the earlier case studies when their output files are listed in `tools/local_paths.json`, which stays out of git because the client work is private. GitHub Actions rebuilds the site on every push, fails if the committed pages differ from the build, and runs the text and link checks and `check_ask.py` on the committed figures.

## Custom domain

The site will move to `marionpeter.nuruops.com`. The steps are in [docs/custom-domain.md](docs/custom-domain.md); until then the site is served from `maidenpeter.github.io`.

Marion Peter
