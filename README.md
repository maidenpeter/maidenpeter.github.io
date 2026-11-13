# maidenpeter.github.io

Marion Peter's portfolio: https://maidenpeter.github.io

The home page leads with the Kenya insurance series, built from the Insurance Regulatory Authority's quarterly returns. The live analysis pages stay in their own repositories and are linked from here, never copied:

- [ira-kenya-data](https://github.com/maidenpeter/ira-kenya-data): extraction, company crosswalk, panels, quality flags, 42,246 validation checks, and the Insurer Explorer
- [ira-kenya-insurance](https://github.com/maidenpeter/ira-kenya-insurance): the Loss Map and Market Structure
- [ira-kenya-reinsurance](https://github.com/maidenpeter/ira-kenya-reinsurance): the Cedant Scorecard, its back-test and sensitivity

## Pages

| Path | What it is |
|---|---|
| `/` | Home: who I am, the Kenya series, three findings, earlier case studies, products, how I work, contact |
| `/kenya-insurance/` | Front page of the Kenya insurance series (its permanent address) |
| `/work/dealer-revenue/` | Case study: a Kenyan dealer group's revenue double count (anonymised) |
| `/work/ifrs17-measurement/` | Case study: IFRS 17 discounting and risk adjustment on US industry triangles |
| `/work/valuation-adequacy/` | Case study: a reserve adequacy test on 476,882 car auctions |
| `/about/` | CV |
| `404.html`, `sitemap.xml`, `robots.txt` | The usual |

## How it is built

Static HTML, no framework. `tools/build.py` writes every page from one layout, so the head, header, footer and theme script are written once; `assets/site.css` holds the tokens for the light and dark themes.

```
python tools/build.py                      # write the pages into the repo root
python tools/build.py --repo-index OUT     # also write the index page of each Kenya repo into OUT/<repo>/index.html
python tools/render_images.py              # share image, favicon.ico, Apple touch icon (needs Playwright and Chrome)
```

Every number on the site lives in `tools/figures.py`. Nothing is typed into a page by hand.

## Checks

```
python tools/check_figures.py --repos "../Marion Peter"   # recompute every figure from the analysis repos
python tools/check_text.py                                # plain ASCII only, no flagged phrases
python tools/check_links.py [--external]                  # internal links, assets and anchors; optionally every external URL
python tools/screenshots.py OUT                           # 1280 and 390 px, light and dark; fails on sideways scrolling
```

`check_figures.py` also checks the earlier case studies when their output files are listed in `tools/local_paths.json`, which stays out of git because the client work is private. GitHub Actions rebuilds the site on every push, fails if the committed pages differ from the build, and runs the text and link checks.

## Custom domain

The site will move to `marionpeter.nuruops.com`. The steps are in [docs/custom-domain.md](docs/custom-domain.md); until then the site is served from `maidenpeter.github.io`.

Marion Peter
