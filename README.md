# Marion Peter | Data & Actuarial Engineer

**[maidenpeter.github.io](https://maidenpeter.github.io)**

[![checks](https://github.com/maidenpeter/maidenpeter.github.io/actions/workflows/checks.yml/badge.svg)](https://github.com/maidenpeter/maidenpeter.github.io/actions/workflows/checks.yml)

Insurance and reinsurance analysis built from public data. The site leads with Kenya's general insurance market, rebuilt from the Insurance Regulatory Authority's quarterly returns and checked 42,246 times, then sets out reserving, IFRS 17 and pricing work on public US data.

> Every number on the site comes from `tools/figures.py` or the Ask the data figures file, and a script recomputes each one from the file it came from. Nothing is typed into a page by hand.

**Contents:** [Pages](#pages) | [The Kenya series](#the-kenya-insurance-series) | [Ask the data](#ask-the-data) | [How it is built](#how-it-is-built) | [Commands](#commands) | [Checks](#checks) | [Custom domain](#custom-domain)

---

## Pages

| Page | What it is |
|---|---|
| [`/`](https://maidenpeter.github.io/) | A chain ladder worked out in the page, then **Part I, Data analysis** (analysis 1, the Kenya series, and what a reinsurer would act on; analysis 2, claims settlement; Ask the data; the M-Pesa series, starting with the statement reader; the dealer audit, CargoShield and two forecasting products) and **Part II, Actuarial analysis** (the reserving and persistency apps, AgroShield pricing, the IFRS 17 and reserve adequacy case studies) |
| [`/kenya-insurance/`](https://maidenpeter.github.io/kenya-insurance/) | Front page of the Kenya insurance series |
| [`/ask/`](https://maidenpeter.github.io/ask/) | Ask the data: questions about the market, any insurer, the scorecard and reserving, answered in the browser |
| [`/work/dealer-revenue/`](https://maidenpeter.github.io/work/dealer-revenue/) | Case study: a Kenyan dealer group's revenue counted twice (anonymised) |
| [`/work/ifrs17-measurement/`](https://maidenpeter.github.io/work/ifrs17-measurement/) | Case study: IFRS 17 discounting and risk adjustment on US industry triangles |
| [`/work/valuation-adequacy/`](https://maidenpeter.github.io/work/valuation-adequacy/) | Case study: a reserve adequacy test on 476,882 car auctions |
| [`/about/`](https://maidenpeter.github.io/about/) | CV, with a career timeline |
| `404.html`, `sitemap.xml`, `robots.txt` | The usual |

## The Kenya insurance series

The analysis pages live in their own repositories and are linked from here, never copied.

| Repository | What it holds | Pages |
|---|---|---|
| [ira-kenya-data](https://github.com/maidenpeter/ira-kenya-data) | Extraction, the company crosswalk, panels, quality flags and 42,246 validation checks | [Insurer Explorer](https://maidenpeter.github.io/ira-kenya-data/explorer/kenya-insurer-explorer.html) |
| [ira-kenya-insurance](https://github.com/maidenpeter/ira-kenya-insurance) | Class profitability, rate adequacy, market structure and reinsurance flows; claims settlement as analysis 2 | [Loss Map](https://maidenpeter.github.io/ira-kenya-insurance/page/kenya-insurance-loss-map.html), [Market Structure](https://maidenpeter.github.io/ira-kenya-insurance/page/kenya-insurance-market-structure.html), [Reinsurance Flows](https://maidenpeter.github.io/ira-kenya-insurance/page/kenya-insurance-reinsurance-flows.html), [Claims Settlement](https://maidenpeter.github.io/ira-kenya-insurance/page/kenya-claims-settlement.html) |
| [ira-kenya-reinsurance](https://github.com/maidenpeter/ira-kenya-reinsurance) | The Cedant Scorecard, its back-test and its weight sensitivity | [Cedant Scorecard](https://maidenpeter.github.io/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html) |

## Ask the data

[`/ask/`](https://maidenpeter.github.io/ask/) answers questions such as which class lost the most money over a range of years, how an insurer did on a class in a year, where it sits on the Cedant Scorecard, which line needs the largest reserve, and what Marion has done (with a link to the evidence).

It reads as a conversation. A visitor picks a question from the topic tabs, or types one into the box held at the bottom of the window, and the page calculates the answer in the browser. Each answer can be changed (its insurer, class or year) and offers two or three questions that follow from it.

**There is no language model and no server.** Every number is a lookup, sum, rank or ratio of the derived figures in `assets/ask/data.json`.

| Part | What it does |
|---|---|
| `tools/build_ask.py` | Writes `assets/ask/data.json` from the processed tables in `ira-kenya-data`, the scorecard outputs in `ira-kenya-reinsurance` and the merger map in `ira-kenya-insurance`. It holds figures per insurer, per class and per year, the level the Insurer Explorer already publishes, and records the last commit that changed each repo's inputs. The file is committed, so the page works without the data repos. |
| `tools/ask_bank.py` | The questions, written once; `tools/build.py` puts them into the page |
| `assets/ask/ask.js` | Draws the questions, computes the answers and draws the charts with the classes of `assets/viz.css` |
| `tools/ask_answers.py` | The same answers computed in Python, for the checks |
| `docs/ask-plan.md` | The field list, the metric definitions with their sources, and the decisions taken |

Answers that name an insurer say the figures come from unaudited returns and are a screening view, not a credit opinion. Insurer names appear on `/ask/` and the Kenya pages, never on the home page.

## How it is built

Static HTML, no framework. `tools/build.py` writes every page from one layout, so the head, navigation, footer and theme script are written once.

**Look.** `assets/site.css` holds the tokens for two themes, ink (dark, the default) and paper (light), with gold for emphasis, teal for gain and oxblood for loss. A copperplate layer matches the Kenya series plates: a grained, foxed ground, IM Fell English for headings, Old Standard TT for labels, Pinyon Script in the name line, double-ruled frames and hatched bars. Charts are plain HTML and CSS from `tools/viz.py` and `assets/viz.css`, and each has a table of its numbers.

**Readability.** The site is written for readers who may need larger, clearer text. In the paper theme every text colour reaches 7:1 contrast on the page and on panels (the stronger WCAG level). Labels are 13px or more and reading text 15px or more, set in a readability block at the end of `assets/site.css` and `assets/viz.css`.

**Navigation.** Written once in `tools/nav.py` and on screen on every page:

- a top bar with the MP seal, the name and the role in the middle, where the reader is on the left ("I Data analysis / Kenya series / Loss map", following the section being read on the home page), and the theme switch and GitHub on the right;
- a side bar with Back, Home, the two chapters, Ask the data, About and Contact. Data analysis is grouped by industry, and each group folds away: **Insurance**, which holds numbered analyses (**1 Kenya series**, its pages numbered 01 to 06, and **2 Claims settlement**), **Mobile money** (**1 M-Pesa series**, its first analysis the statement reader), **Automotive** (the dealer revenue audit) and **Aviation** (CargoShield);
- on Kenya pages, a labelled series strip held under the top bar (shorter labels where six full names do not fit, scrolling on phones);
- on phones, the same links in a bar along the bottom, with each chapter opening as a sheet.

The build writes the navigation's CSS to `assets/nav.css`. `tools/kenya_nav.py` writes the same navigation, a skip link and (on the Kenya series pages) the series strip into the Kenya analysis pages, inline, between `mp-nav` markers, so it can be run again whenever `nav.py` changes.

**Screenshots and pop-outs.** Every card that links somewhere carries a screenshot from `assets/shots/`, made by `tools/render_shots.py`. Work with no public link yet opens a pop-out (the `popover` attribute, so no script is needed) with a larger screenshot and the explanation.

**The triangle.** The home page runs a volume-weighted chain ladder on the six NAIC Schedule P paid triangles in `tools/cas_triangles.json`, the same data as the IFRS 17 case study. The build computes it in Python, so the page reads correctly without JavaScript, and the page then recomputes it and fills the projected corner one calendar year at a time.

## Commands

Rebuild everything after a change to the data or the navigation:

```
python tools/build_ask.py --repos ..       # the Ask the data figures
python tools/build.py                      # every page on this site
python tools/build.py --repo-index ..      # the index page of each Kenya repo
python tools/kenya_nav.py --repos ..       # the navigation inside the Kenya analysis pages
```

| Command | What it does |
|---|---|
| `python tools/build.py` | Writes the pages into the repo root |
| `python tools/build.py --repo-index OUT` | Also writes the index page of each Kenya repo into `OUT/<repo>/index.html` |
| `python tools/build_ask.py --repos ..` | Rebuilds `assets/ask/data.json`; run `build.py` after it |
| `python tools/kenya_nav.py --repos ..` | Writes the navigation into the Kenya analysis pages and their templates |
| `python tools/render_images.py` | Share image, `favicon.ico`, Apple touch icon (Playwright and Chrome) |
| `python tools/render_shots.py` | Card screenshots of the Kenya pages, case studies and apps (Playwright, Chrome, Pillow) |

## Checks

| Command | What it checks |
|---|---|
| `python tools/check_figures.py --repos ..` | Recomputes every figure on the site from the analysis repos beside this one |
| `python tools/check_ask.py [--repos ..]` | Ask the data: the field list, and a seeded sample of 117 questions answered by the page's engine (in Node) and in Python, word for word. With `--repos`, every figure is also rebuilt from the processed tables |
| `python tools/check_ask_page.py` | The same questions asked through the real page in Chrome, both themes, 1280 and 390 px |
| `python tools/check_text.py` | Plain ASCII only, and no flagged phrases |
| `python tools/check_links.py [--external] [--repos ..]` | Internal links, assets and anchors; optionally every external URL, and the pages of the Kenya repos and the M-Pesa tool |
| `python tools/screenshots.py OUT` | Every page at 1280 and 390 px in both themes; fails on sideways scrolling, failed requests or console errors |

**On every push,** GitHub Actions rebuilds the site and fails if the committed pages differ from the build, then runs the text and link checks and `check_ask.py` on the committed figures.

**Offline or without Chrome,** set `CHROME` to the browser binary and `FONTS_DIR` to a folder of the EB Garamond, IBM Plex Sans Condensed, IM Fell English, IM Fell English SC, Pinyon Script and Old Standard TT `.woff2` files.

**Earlier case studies.** `check_figures.py` also checks them when their output files are listed in `tools/local_paths.json`, which stays out of git because the client work is private.

## Custom domain

The site will move to `marionpeter.nuruops.com`; the steps are in [docs/custom-domain.md](docs/custom-domain.md). Until then it is served from `maidenpeter.github.io`.
