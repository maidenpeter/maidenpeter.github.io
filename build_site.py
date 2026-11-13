"""Build the GitHub Pages hub (maidenpeter.github.io) and the index page for each project repo."""
import os, sys
OUT = sys.argv[1]
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans+Condensed:wght@400;500;600&display=swap">'
CSS = r"""
:root{--ground:#f4f6f3;--surface:#ffffff;--ink:#15202b;--ink-2:#4f5a64;--muted:#6d7780;--rule:#d9dfdb;--rule-soft:#e8ece9;--accent:#184f95;--accent-soft:#e3ecf8;--gain:#2a78d6;--loss:#e0612e;
--serif:"EB Garamond",Garamond,"Adobe Garamond Pro",Georgia,serif;--ui:"IBM Plex Sans Condensed","Arial Narrow","Helvetica Neue",Arial,sans-serif}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--ground:#10161c;--surface:#172029;--ink:#e7ebee;--ink-2:#b4bdc5;--muted:#8f99a3;--rule:#2b3640;--rule-soft:#222c35;--accent:#86b6ef;--accent-soft:#1d2a3a;--gain:#4a97ee;--loss:#ee7a45}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.5}
a{color:var(--accent)}a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1140px;margin:0 auto;padding-inline:22px;padding-block:28px 56px;display:flex;flex-direction:column;gap:56px}
.eyebrow{font-family:var(--ui);font-size:12.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(36px,5.4vw,60px);font-weight:500;line-height:1.03;margin:8px 0 14px;letter-spacing:-.01em;text-wrap:balance}
h2{font-size:clamp(26px,3.2vw,34px);font-weight:500;line-height:1.1;margin:4px 0 0;text-wrap:balance}
h3{font-size:22px;font-weight:500;margin:0;line-height:1.15}
p{margin:0}.lede{font-size:clamp(19px,2vw,22px);color:var(--ink-2);max-width:60ch}
.small{font-family:var(--ui);font-size:13.5px;color:var(--muted)}
nav.top{display:flex;justify-content:space-between;align-items:center;gap:12px;font-family:var(--ui);font-size:14px;border-bottom:1px solid var(--rule);padding-bottom:14px;flex-wrap:wrap}
nav.top .me{font-family:var(--serif);font-size:21px;font-weight:600;color:var(--ink);text-decoration:none}
nav.top .links{display:flex;gap:18px;flex-wrap:wrap}nav.top .links a{color:var(--ink-2);text-decoration:none}nav.top .links a:hover{color:var(--accent)}
.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:36px;align-items:center}
.big{display:flex;flex-direction:column;gap:14px;margin-top:22px}
.big div{display:flex;flex-direction:column}
.big b{font-weight:400;font-size:clamp(42px,5.2vw,58px);line-height:1;font-variant-numeric:tabular-nums lining-nums}
.big span{font-family:var(--ui);font-size:14.5px;color:var(--ink-2);margin-top:3px}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:20px}
.chart svg{display:block;width:100%;height:auto}.chart text{font-family:var(--ui);font-size:13px;fill:var(--ink-2)}.chart .v{fill:var(--ink);font-weight:500}.chart .m{fill:var(--ink);font-weight:600}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden}
.stats div{background:var(--surface);padding:16px 18px;display:flex;flex-direction:column;gap:2px}
.stats b{font-weight:400;font-size:34px;line-height:1.05;font-variant-numeric:tabular-nums lining-nums}
.stats span{font-family:var(--ui);font-size:13.5px;color:var(--ink-2)}
.sechead{display:flex;flex-direction:column;gap:8px;max-width:72ch}.sechead p{color:var(--ink-2)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:22px;display:flex;flex-direction:column;gap:10px;text-decoration:none;color:var(--ink);transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card .tag{font-family:var(--ui);font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.card .find{font-size:19px;line-height:1.35}.card .find b{font-weight:600}
.card .go{font-family:var(--ui);font-size:14px;color:var(--accent);margin-top:auto}
.card.soon{background:transparent;border-style:dashed;cursor:default}.card.soon:hover{transform:none;border-color:var(--rule)}
.pipe{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;align-items:stretch}
.step{position:relative;padding:16px 18px 16px 0;border-top:3px solid var(--accent);display:flex;flex-direction:column;gap:6px}
.step b{font-family:var(--ui);font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.step p{font-family:var(--ui);font-size:14.5px;color:var(--ink-2);line-height:1.4}
.step .n{font-family:var(--serif);font-size:26px;color:var(--ink);line-height:1.1}
.repos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.repo{border-top:1px solid var(--rule);padding-top:12px;display:flex;flex-direction:column;gap:6px}
.repo a{font-family:var(--ui);font-size:15px;font-weight:500}.repo p{font-family:var(--ui);font-size:14px;color:var(--ink-2)}
footer{border-top:1px solid var(--rule);padding-top:16px;display:flex;flex-direction:column;gap:6px;font-family:var(--ui);font-size:13.5px;color:var(--muted)}footer p{max-width:110ch}
@media (max-width:860px){.hero,.cards,.repos{grid-template-columns:minmax(0,1fr)}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.pipe{grid-template-columns:minmax(0,1fr);gap:14px}.step{padding-right:0}}
@media (prefers-reduced-motion:reduce){.card{transition:none}.card:hover{transform:none}}
"""
HUB = "https://maidenpeter.github.io"
GH = "https://github.com/maidenpeter"
P = dict(
  explorer=f"{HUB}/ira-kenya-data/explorer/kenya-insurer-explorer.html",
  lossmap=f"{HUB}/ira-kenya-insurance/page/kenya-insurance-loss-map.html",
  structure=f"{HUB}/ira-kenya-insurance/page/kenya-insurance-market-structure.html",
  scorecard=f"{HUB}/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html")

def page(title, desc, body):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">
{FONTS}<style>{CSS}</style></head><body><div class="wrap">
{body}
</div></body></html>
"""

def nav():
    return f"""<nav class="top"><a class="me" href="{HUB}/">Marion Peter</a><div class="links"><a href="#work">The work</a><a href="#method">Method</a><a href="#code">Code</a><a href="{GH}">GitHub</a></div></nav>"""

ROWS = [("Motor private",-29.25),("Motor commercial",-23.38),("Medical",-2.54),("Engineering",-0.85),("Aviation",-0.68),
        ("Personal accident",0.52),("Liability",0.90),("Fire industrial",0.95),("Fire domestic",0.96),("Miscellaneous",0.98),
        ("Theft",2.72),("Marine",3.54),("Workmen's comp.",13.06)]
def fmt(v):
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(str(abs(v))).quantize(Decimal("0.1"), ROUND_HALF_UP)
    return ("-" if v < 0 else "+") + str(d)
def chart():
    W, L, R, T, rh = 560, 150, 52, 4, 27
    lo, hi = -29.25 * 1.2, 13.06 * 1.35
    x = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)
    H = T + rh * len(ROWS) + 6
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Underwriting result by class, 2018 to 2025, KSh billions">']
    s.append(f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="0" y2="{H}" stroke="var(--muted)" stroke-width="1"/>')
    for i, (n, v) in enumerate(ROWS):
        y = T + i * rh; x0 = x(min(0, v)); w = max(abs(x(v) - x(0)), 1.5)
        cls = "m" if n.startswith("Motor") else ""
        s.append(f'<text x="{L-9}" y="{y+rh/2+4.5}" text-anchor="end" class="{cls}">{n}</text>')
        s.append(f'<rect x="{x0:.1f}" y="{y+5}" width="{w:.1f}" height="{rh-10}" rx="2" fill="var({"--loss" if v<0 else "--gain"})"><title>{n}: KSh {fmt(v)}bn</title></rect>')
        lx = x0 - 5 if v < 0 else x0 + w + 5
        s.append(f'<text x="{lx:.1f}" y="{y+rh/2+4.5}" text-anchor="{"end" if v<0 else "start"}" class="v">{fmt(v)}</text>')
    s.append("</svg>")
    return "".join(s)

hub_body = nav() + f"""
<section class="hero" aria-labelledby="h1">
  <div>
    <div class="eyebrow">Kenya's insurance market, rebuilt from the regulator's own returns</div>
    <h1 id="h1">Where Kenyan insurers make money, and where they lose it</h1>
    <p class="lede">Every general insurer and reinsurer, every quarter from Q4 2016 to Q1 2026, extracted from the Insurance Regulatory Authority's statistics, checked against itself and turned into analysis a reinsurer or an insurer's board could use.</p>
    <div class="big">
      <div><b style="color:var(--loss)">-52.6bn</b><span>KSh lost on motor underwriting, 2018 to 2025</span></div>
      <div><b style="color:var(--gain)">+19.6bn</b><span>earned back by every other class together</span></div>
    </div>
  </div>
  <div class="panel">
    <h3>Underwriting result by class, 2018 to 2025</h3>
    <p class="small" style="margin:3px 0 12px">KSh billions. The market's net result: KSh -33.1bn. Motor commercial includes PSV.</p>
    <div class="chart">{chart()}</div>
  </div>
</section>

<section class="stats" aria-label="The data in numbers">
  <div><b>35</b><span>quarters, Q4 2016 to Q1 2026</span></div>
  <div><b>52</b><span>insurers and reinsurers on stable ids</span></div>
  <div><b>42,246</b><span>consistency checks, none unexplained</span></div>
  <div><b>12 of 12</b><span>figures match IRA's own PDF releases</span></div>
</section>

<section id="work" aria-labelledby="h-work" style="display:flex;flex-direction:column;gap:20px">
  <div class="sechead"><div class="eyebrow">The work</div><h2 id="h-work">Four ways into the same data</h2>
  <p>Each page is a single file built from the validated tables, with the method and caveats on the page.</p></div>
  <div class="cards">
    <a class="card" href="{P['lossmap']}"><span class="tag">Profitability</span><h3>Kenya Insurance Loss Map</h3>
      <p class="find">Motor lost money in every year from 2018 to 2025. On 2023 to 2025 experience, motor commercial premiums would need to rise <b>15.6%</b> just to break even.</p>
      <span class="go">Open the loss map</span></a>
    <a class="card" href="{P['scorecard']}"><span class="tag">Reinsurance</span><h3>Kenya Cedant Scorecard</h3>
      <p class="find">Every insurer graded A to E the way a reinsurer screens a cedant. <b>Three of the five</b> insurers placed under statutory management or liquidation since 2022 sat in the bottom fifth a year before.</p>
      <span class="go">Open the scorecard</span></a>
    <a class="card" href="{P['structure']}"><span class="tag">Market structure</span><h3>Kenya Insurance Market Structure</h3>
      <p class="find">In 2020 two insurers wrote over KSh 10bn and held 16% of the market. By 2025 <b>seven</b> did, holding 53%. Insurers losing share ran a median combined ratio of 112%.</p>
      <span class="go">Open market structure</span></a>
    <a class="card" href="{P['explorer']}"><span class="tag">Data</span><h3>Kenya Insurer Explorer</h3>
      <p class="find">Any insurer, any year: premium, ratios, every quarter on its own, class mix, balance sheet and every return-quality flag, including the returns that add up but cannot be right.</p>
      <span class="go">Open the explorer</span></a>
  </div>
  <div class="cards">
    <div class="card soon"><span class="tag">Coming next</span><h3>Reserving tool</h3><p class="find" style="color:var(--ink-2)">Chain ladder and Bornhuetter-Ferguson on published claims development tables, with IBNR set against the reserves insurers booked.</p></div>
    <div class="card soon"><span class="tag">Coming next</span><h3>IFRS 17 and reinsurance flows</h3><p class="find" style="color:var(--ink-2)">What the 2024 switch to IFRS 17 changed in reported results, and how much risk Kenyan insurers cede, by class and company.</p></div>
  </div>
</section>

<section id="method" aria-labelledby="h-method" style="display:flex;flex-direction:column;gap:20px">
  <div class="sechead"><div class="eyebrow">Method</div><h2 id="h-method">From the regulator's files to a finding</h2>
  <p>A return can add up on its own and still be wrong, so every company is also read across its quarters. Errors in the official tables are documented, not hidden.</p></div>
  <div class="pipe">
    <div class="step"><b>Collect</b><span class="n">165 files</span><p>Every IRA statistical publication online from 2008, catalogued with source links and hashes.</p></div>
    <div class="step"><b>Extract</b><span class="n">233,685 rows</span><p>Revenue accounts and class tables from workbooks whose layouts and company names shift every year.</p></div>
    <div class="step"><b>Validate</b><span class="n">42,246 checks</span><p>Identities, class totals, IRA's printed totals and a cross-check against the PDF releases.</p></div>
    <div class="step"><b>Flag</b><span class="n">12 returns</span><p>Returns that add up but cannot be right, such as year-to-date premium that falls, kept out of quarterly totals.</p></div>
    <div class="step"><b>Analyse</b><span class="n">4 pages</span><p>Profitability, market structure, a reinsurer's scorecard and an explorer, each reproducible with one command.</p></div>
  </div>
</section>

<section id="code" aria-labelledby="h-code" style="display:flex;flex-direction:column;gap:20px">
  <div class="sechead"><div class="eyebrow">Code</div><h2 id="h-code">Three repositories, one pipeline</h2>
  <p>Python and pandas, tests run on every push, and every published number rebuilt from the raw files.</p></div>
  <div class="repos">
    <div class="repo"><a href="{GH}/ira-kenya-data">ira-kenya-data</a><p>The data layer: extraction, company crosswalk, single-quarter panels, quality flags and validation.</p></div>
    <div class="repo"><a href="{GH}/ira-kenya-insurance">ira-kenya-insurance</a><p>The insurer's view: class profitability, rate adequacy, reserving warnings and market structure.</p></div>
    <div class="repo"><a href="{GH}/ira-kenya-reinsurance">ira-kenya-reinsurance</a><p>The reinsurer's view: a cedant scorecard on four pillars, with a back-test and sensitivity tests.</p></div>
  </div>
</section>

<footer>
  <p>Source: Insurance Regulatory Authority, Kenya, quarterly industry statistics (unaudited returns). Everything here is public data; nothing comes from inside any insurer. Grades and rankings are relative screening measures, not credit ratings.</p>
  <p>Marion Peter</p>
</footer>
"""

def repo_index(repo, title, lede, links):
    items = "".join(f'<a class="card" href="{u}"><span class="tag">{t}</span><h3>{h}</h3><p class="find">{d}</p><span class="go">Open</span></a>' for t, h, d, u in links)
    body = f"""<nav class="top"><a class="me" href="{HUB}/">Marion Peter</a><div class="links"><a href="{HUB}/">All work</a><a href="{GH}/{repo}">Code</a></div></nav>
<section class="sechead" style="max-width:none"><div class="eyebrow">{repo}</div><h1 style="font-size:clamp(32px,4.4vw,48px)">{title}</h1><p class="lede">{lede}</p></section>
<section class="cards">{items}</section>
<footer><p>Source: Insurance Regulatory Authority, Kenya, quarterly industry statistics. Public data only.</p><p><a href="{GH}/{repo}">Code and method on GitHub</a></p></footer>"""
    return page(f"{title}", lede, body)

os.makedirs(OUT, exist_ok=True)
files = {
 "maidenpeter.github.io/index.html": page("Kenya Insurance, Rebuilt", "Kenya's general insurers and reinsurers, every quarter from Q4 2016 to Q1 2026, rebuilt from IRA's returns: profitability, market structure, a reinsurer's scorecard and a data explorer.", hub_body),
 "ira-kenya-data/index.html": repo_index("ira-kenya-data", "Kenya Insurer Data", "The data layer behind the series: every general insurer and reinsurer, every quarter from Q4 2016 to Q1 2026, validated with 42,246 checks.",
    [("Data","Kenya Insurer Explorer","Any insurer, any year: premium, ratios, single quarters, class mix, balance sheet and return-quality flags.","explorer/kenya-insurer-explorer.html")]),
 "ira-kenya-insurance/index.html": repo_index("ira-kenya-insurance", "Kenya Insurance Analysis", "Kenya's general insurance market from the insurer's side: where the money is lost, what premiums would have to do, and who holds the market.",
    [("Profitability","Kenya Insurance Loss Map","Class by class results 2018 to 2025, the rate change each class needs, and motor results that look too good.","page/kenya-insurance-loss-map.html"),
     ("Market structure","Kenya Insurance Market Structure","Concentration, share shifts, growth against results and what fragmentation costs.","page/kenya-insurance-market-structure.html")]),
 "ira-kenya-reinsurance/index.html": repo_index("ira-kenya-reinsurance", "Kenya Cedant Scorecard", "Every Kenyan general insurer graded each year the way a reinsurer screens a cedant, back-tested against the insurers the regulator stepped into.",
    [("Reinsurance","Kenya Cedant Scorecard","Grades A to E on balance sheet, operating performance, business profile and return quality, 2016 to 2025.","page/kenya-cedant-scorecard.html")]),
}
for k, v in files.items():
    p = os.path.join(OUT, k); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(v)
    print(k, len(v))
