# maidenpeter.github.io

Marion Peter's portfolio: https://maidenpeter.github.io

The home page leads with the Kenya insurance series, built from the Insurance Regulatory Authority's quarterly returns. The live analysis pages stay in their own repositories and are linked from here, never copied:

- [ira-kenya-data](https://github.com/maidenpeter/ira-kenya-data): extraction, company crosswalk, panels, quality flags, 42,246 validation checks, and the Insurer Explorer
- [ira-kenya-insurance](https://github.com/maidenpeter/ira-kenya-insurance): the Loss Map and Market Structure
- [ira-kenya-reinsurance](https://github.com/maidenpeter/ira-kenya-reinsurance): the Cedant Scorecard, its back-test and sensitivity

## Pages

| Path | What it is |
|---|---|
| `/` | Home: a chain ladder calculated in the page, the Kenya series, three findings, apps, case studies, products, how I work, contact |
| `/kenya-insurance/` | Front page of the Kenya insurance series (its permanent address) |
| `/work/dealer-revenue/` | Case study: a Kenyan dealer group's revenue double count (anonymised) |
| `/work/ifrs17-measurement/` | Case study: IFRS 17 discounting and risk adjustment on US industry triangles |
| `/work/valuation-adequacy/` | Case study: a reserve adequacy test on 476,882 car auctions |
| `/about/` | CV |
| `404.html`, `sitemap.xml`, `robots.txt` | The usual |

## How it is built

Static HTML, no framework. `tools/build.py` writes every page from one layout, so the head, header, footer and theme script are written once; `assets/site.css` holds the tokens for the two themes: ink (dark, the default) and paper (light), with gold for emphasis, teal for gain and oxblood for loss.

The home page triangle is a volume-weighted chain ladder on the six NAIC Schedule P paid triangles in `tools/cas_triangles.json`, the same data as the IFRS 17 case study. The build computes it in Python so the page reads correctly without JavaScript; the page then recomputes it in the browser and fills the projected corner one calendar year at a time.

```
python tools/build.py                      # write the pages into the repo root
python tools/build.py --repo-index OUT     # also write the index page of each Kenya repo into OUT/<repo>/index.html
python tools/render_images.py              # share image, favicon.ico, Apple touch icon (needs Playwright and Chrome)
```

Every number on the site lives in `tools/figures.py`. Nothing is typed into a page by hand.

## Checks

```
python tools/check_figures.py --repos ..                  # recompute every figure from the analysis repos beside this one
python tools/check_text.py                                # plain ASCII only, no flagged phrases
python tools/check_links.py [--external]                  # internal links, assets and anchors; optionally every external URL
python tools/screenshots.py OUT                           # 1280 and 390 px, ink and paper; fails on sideways scrolling
```

On a machine without Chrome on the default path or without internet access, set `CHROME` to the browser binary and `FONTS_DIR` to a folder of the EB Garamond and IBM Plex Sans Condensed `.woff2` files.

`check_figures.py` also checks the earlier case studies when their output files are listed in `tools/local_paths.json`, which stays out of git because the client work is private. GitHub Actions rebuilds the site on every push, fails if the committed pages differ from the build, and runs the text and link checks.

## Custom domain

The site will move to `marionpeter.nuruops.com`. The steps are in [docs/custom-domain.md](docs/custom-domain.md); until then the site is served from `maidenpeter.github.io`.

Marion Peter
