"""Build maidenpeter.github.io.

    python tools/build.py                      # write the site into the repo root
    python tools/build.py --repo-index DIR     # also write the index page of each Kenya repo into DIR/<repo>/index.html

Shared parts (head, header, footer, tokens in assets/site.css) are written once here.
Every number comes from tools/figures.py, which tools/check_figures.py checks against its source.
"""
import argparse, html, json, os, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from figures import (KENYA as K, CLASS_RESULTS, BACKTEST, DEALER as D, IFRS17 as I, IFRS17_LINES,
                     BACKTEST_AE, CREDIBILITY, AUCTIONS as A, AUCTION_DECILES, APPS as AP, IPL_URL, HACKATHONS)

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://maidenpeter.github.io"   # change to https://marionpeter.nuruops.com once the custom domain is live
GH = "https://github.com/maidenpeter"
SITE_REPO = f"{GH}/maidenpeter.github.io"
EMAIL = "marionpeter@nuruops.com"
ROLE = "Actuarial Engineer"
LINKEDIN = "https://www.linkedin.com/in/marion-peter"
FONTS = ("https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400"
         "&family=IBM+Plex+Sans+Condensed:wght@400;500;600"
         "&family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC&family=Pinyon+Script"
         "&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap")

# Live pages in the analysis repos. Linked, never copied.
PAGE = dict(
    lossmap=f"{BASE}/ira-kenya-insurance/page/kenya-insurance-loss-map.html",
    structure=f"{BASE}/ira-kenya-insurance/page/kenya-insurance-market-structure.html",
    scorecard=f"{BASE}/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html",
    explorer=f"{BASE}/ira-kenya-data/explorer/kenya-insurer-explorer.html",
)
CODE = dict(data=f"{GH}/ira-kenya-data", insurance=f"{GH}/ira-kenya-insurance", reinsurance=f"{GH}/ira-kenya-reinsurance")


def esc(s):
    return html.escape(s, quote=True)


def d1(v, sign=True):
    """One decimal, half up, ASCII minus."""
    q = Decimal(str(abs(v))).quantize(Decimal("0.1"), ROUND_HALF_UP)
    if not sign:
        return ("-" if v < 0 else "") + str(q)
    return ("-" if v < 0 else "+") + str(q)


def n(v):
    return f"{v:,}"


WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve"}


def w(v, cap=False):
    """Small counts as words, so a count never runs into a year ("In 2020, two insurers")."""
    t = WORDS.get(v, str(v))
    return t[0].upper() + t[1:] if cap else t


def ksh(v):
    return f"KSh {d1(v, sign=False)}bn"


# ----------------------------------------------------------------- layout
# (href, label, short label for the rail and phone bar, icon, section the link belongs to,
#  home page sections that light it up while scrolling)
NAV = [("/", "Home", "Home", "home", "home", ""),
       ("/kenya-insurance/", "Kenya series", "Kenya", "chart", "kenya", "work signals"),
       ("/#cases", "Case studies", "Cases", "doc", "work", "cases"),
       ("/#apps", "Apps", "Apps", "grid", None, "apps products"),
       ("/about/", "About", "About", "person", "about", ""),
       ("/#contact", "Contact", "Contact", "mail", None, "contact")]

# Line icons on a 24px grid, drawn in the text colour so they follow both themes.
ICONS = {
    "home": "M3.5 10.5 12 3.5l8.5 7M6 9v11.5h4.5V15h3v5.5H18V9",
    "chart": "M3.5 20.5h17M7 17v-5M12 17V6.5M17 17V9.5",
    "doc": "M6 3.5h8l4 4v13H6zM14 3.5v4h4M9 12h6M9 15.5h6",
    "grid": "M4 4h6.5v6.5H4zM13.5 4H20v6.5h-6.5zM4 13.5h6.5V20H4zM13.5 13.5H20V20h-6.5z",
    "person": "M12 11.5a3.75 3.75 0 1 0 0-7.5 3.75 3.75 0 0 0 0 7.5zM4.5 20.5c.6-3.9 3.6-6 7.5-6s6.9 2.1 7.5 6",
    "mail": "M3.5 5.5h17v13h-17zM3.5 6.5l8.5 6.5 8.5-6.5",
    "code": "M8.5 7 3.5 12l5 5M15.5 7l5 5-5 5M13.5 4.5l-3 15",
    "theme": "M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z",
}


def icon(name):
    fill = '<path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor" stroke="none"/>' if name == "theme" else ""
    return (f'<svg class="ic" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" '
            f'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{ICONS[name]}"/>{fill}</svg>')


THEME_HEAD = ("<script>try{var t=localStorage.getItem('mp-theme');"
              "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>")
# On the home page, mark the nav item for the section being read. Home keeps its mark only
# while no other item has it (the hero and the strip of figures above the first section).
NAV_JS = """<script>(function(){var d=document.documentElement,nav=document.querySelector('nav.main');if(!nav)return;
var home=location.pathname==='/'||location.pathname==='/index.html',
secs=home?[].slice.call(document.querySelectorAll('main section[id]')):[],
links=[].slice.call(nav.querySelectorAll('a[data-spy]'));if(!secs.length)return;
function spy(){var y=window.innerHeight*0.3,cur='',any=false;
for(var i=0;i<secs.length;i++)if(secs[i].getBoundingClientRect().top<=y)cur=secs[i].id;
if(window.innerHeight+window.scrollY>=d.scrollHeight-2)cur=secs[secs.length-1].id;
links.forEach(function(a){var on=!!cur&&a.getAttribute('data-spy').split(' ').indexOf(cur)>-1;a.classList.toggle('here',on);if(on)any=true});
nav.classList.toggle('spying',any)}
var q=0;window.addEventListener('scroll',function(){if(!q)q=requestAnimationFrame(function(){q=0;spy()})},{passive:true});
window.addEventListener('resize',spy);spy()})();</script>"""
THEME_JS = """<script>(function(){var b=document.querySelector('.theme');if(!b)return;var d=document.documentElement,l=b.querySelector('.l');
function cur(){return d.getAttribute('data-theme')||'dark'}
function lab(){var c=cur();l.textContent=c==='dark'?'Paper theme':'Ink theme';b.setAttribute('aria-label','Switch to '+(c==='dark'?'light':'dark')+' theme')}
b.hidden=false;b.addEventListener('click',function(){var x=cur()==='dark'?'light':'dark';d.setAttribute('data-theme',x);try{localStorage.setItem('mp-theme',x)}catch(e){}lab()});lab()})();</script>"""


CUR = ' aria-current="page"'


def layout(path, title, desc, body, section=None, og_title=None):
    url = BASE + path
    def cur(h, s):
        if h == path:
            return CUR
        return ' aria-current="true"' if s and s == section else ""
    nav = "".join(f'<a href="{h}"{cur(h, s)} data-spy="{spy}">{icon(ic)}<span class="l">{t}</span><span class="s">{st}</span></a>'
                  for h, t, st, ic, s, spy in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="author" content="Marion Peter">
<meta name="theme-color" content="#0f1b2d">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Marion Peter">
<meta property="og:title" content="{esc(og_title or title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Kenya general insurance underwriting result by class, 2018 to 2025: motor KSh -52.6bn, every other class together KSh +19.6bn.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{THEME_HEAD}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
<a class="brand" href="/"><i class="mono" aria-hidden="true">MP</i><b class="nm">Marion Peter</b><span>{ROLE}</span></a>
<nav class="main" aria-label="Main">{nav}</nav>
<div class="side-foot"><button class="theme" type="button" hidden>{icon("theme")}<span class="l">Paper theme</span></button><a class="gh" href="{GH}">{icon("code")}<span class="l">GitHub</span></a></div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<p>Marion Peter, {ROLE}. Everything on this site uses public data or anonymised work; no employer data is used. Kenya figures come from the Insurance Regulatory Authority's quarterly returns, which are unaudited.</p>
<p><a href="{SITE_REPO}">Source for this site</a> &nbsp; <a href="{GH}">GitHub</a> &nbsp; <a href="mailto:{EMAIL}">Email</a></p>
</div></footer>
{THEME_JS}
{NAV_JS}
</body>
</html>
"""


# ------------------------------------------------------------- components
def bars(items, label, unit="", em=lambda name, v: False, inside=0.3):
    """Diverging bars from real text. items: (name, value). Bars longer than `inside` of the track carry their value inside."""
    lo = min(0, min(v for _, v in items))
    hi = max(0, max(v for _, v in items))
    span = hi - lo
    zero = -lo / span * 100
    out = []
    for name, v in items:
        w = max(abs(v) / span * 100, 0.5)
        side = "neg" if v < 0 else "pos"
        inn = " in" if v < 0 and w / 100 > inside else ""
        out.append(f'<span class="lab{" em" if em(name, v) else ""}">{esc(name)}</span>'
                   f'<span class="track" style="--zero:{zero:.2f}%;--w:{w:.2f}%">'
                   f'<span class="bar {side}"></span><span class="val {side}{inn}">{d1(v)}{unit}</span></span>')
    return f'<div class="bars" role="img" aria-label="{esc(label)}">{"".join(out)}</div>'


def class_chart():
    return bars(CLASS_RESULTS,
                f"Underwriting result by class, 2018 to 2025, KSh billions. Motor private {d1(K['uw_motor_private'])}, "
                f"motor commercial {d1(K['uw_motor_commercial'])}, workmen's compensation {d1(K['uw_wc'])}, market total {d1(K['uw_market'])}.",
                em=lambda name, v: name.startswith("Motor"))


def chart_panel(link=True):
    foot = (f'<div class="foot"><span class="small">Source: IRA quarterly returns, full years. Net of reinsurance. Motor commercial includes PSV.</span>'
            f'<a class="more" href="{PAGE["lossmap"]}">Open the Loss Map</a></div>') if link else ""
    return f"""<figure class="panel" style="margin:0">
<h3>Underwriting result by class, 2018 to 2025</h3>
<p class="small">KSh billions, every general insurer in Kenya. Market total {ksh(K['uw_market'])}. Motor lost money in all {K['motor_loss_years']} years.</p>
{class_chart()}
{foot}
</figure>"""


def proof_strip():
    cells = [
        (str(K["quarters"]), "quarters of returns, Q4 2016 to Q1 2026"),
        (str(K["companies"]), "insurers and reinsurers, every one, on stable ids"),
        (n(K["checks"]), "consistency checks, none unexplained"),
        (f'{K["pdf_match"]} of {K["pdf_total"]}', "figures match IRA's own PDF releases"),
        ("3 repos", "public code, tests run on every push"),
    ]
    return '<section class="proof" aria-label="The data in numbers">' + "".join(
        f"<div><b>{b}</b><span>{s}</span></div>" for b, s in cells) + "</section>"


def work_card(tag, title, finding, data, method, page, code, code_label):
    return f"""<article class="card">
<span class="tag">{tag}</span>
<h3>{title}</h3>
<p class="find">{finding}</p>
<dl class="meta"><dt>Data</dt><dd>{data}</dd><dt>Method</dt><dd>{method}</dd></dl>
<div class="links"><a href="{page}">Open the page</a><a href="{code}">Code: {code_label}</a></div>
</article>"""


def kenya_cards():
    return "".join([
        work_card("Profitability", "Kenya Insurance Loss Map",
                  f"Motor lost <b>{ksh(-K['uw_motor'])}</b> on underwriting from 2018 to 2025, in every one of the eight years. "
                  f"On 2023 to 2025 experience, motor commercial premiums would need to rise <b>{d1(K['rate_mc'], False)}%</b> to break even.",
                  "IRA quarterly returns, full years 2018 to 2025, 14 classes, every general insurer.",
                  "Class results by year; break-even rate change by the loss ratio method; Fisher's exact test on motor books that look too good.",
                  PAGE["lossmap"], CODE["insurance"], "ira-kenya-insurance"),
        work_card("Reinsurance", "Kenya Cedant Scorecard",
                  f"Every insurer graded A to E each year the way a reinsurer screens a cedant. <b>{K['bt_bottom']} of the {K['bt_total']}</b> insurers placed under "
                  "statutory management or liquidation since 2022 were in the bottom fifth a year before the regulator acted.",
                  "IRA balance sheets, revenue accounts and return-quality flags, 2016 to 2025.",
                  "Peer percentiles on four pillars (balance sheet, operations, business profile, return quality), a capital cap, a back-test and weight sensitivity.",
                  PAGE["scorecard"], CODE["reinsurance"], "ira-kenya-reinsurance"),
        work_card("Market structure", "Kenya Insurance Market Structure",
                  f"In 2020, {w(K['over10_2020'])} insurers wrote over KSh 10bn a year and held {K['share10_2020']}% of the market. By 2025, <b>{w(K['over10_2025'])}</b> did, "
                  f"holding {K['share10_2025']}%. The {w(K['losing_n'])} insurers losing share ran a median combined ratio of <b>{d1(K['median_cr_losing'], False)}%</b>.",
                  "Written premium and results for every general insurer, 2016 to 2025, pro forma for mergers.",
                  "Herfindahl-Hirschman index, share shifts, growth against combined ratio, and expense rates measured class for class against the five largest insurers.",
                  PAGE["structure"], CODE["insurance"], "ira-kenya-insurance"),
        work_card("Data", "Kenya Insurer Explorer",
                  f"Any insurer, any year: premium, ratios, single quarters, class mix, balance sheet and every return-quality flag, "
                  f"including the <b>{K['error_returns']} returns</b> that add up on their own but cannot be right.",
                  f"{n(K['revenue_rows'])} revenue-account rows and {n(K['class_rows'])} class rows from {K['files']} IRA files catalogued back to {K['first_year']}.",
                  f"Extraction from shifting workbook layouts, a name crosswalk across renames and mergers, single quarters from year-to-date figures, {n(K['checks'])} checks.",
                  PAGE["explorer"], CODE["data"], "ira-kenya-data"),
    ])


def backtest_strip():
    dots = []
    for year, rank, total, bottom in BACKTEST:
        pos = (rank - 0.5) / total * 100
        dots.append(f'<span class="dot{"" if bottom else " out"}" style="left:{pos:.1f}%" title="Rank {rank} of {total}, regulator acted {year}"></span>')
    return f"""<div class="rank" role="img" aria-label="Last scorecard rank before the regulator acted, for five insurers: {', '.join(f'{r} of {t}' for _, r, t, _ in BACKTEST)}. Three in the bottom fifth.">
<span class="zl">Bottom fifth</span><span class="line"></span><span class="zone"></span>{''.join(dots)}
<span class="end" style="left:0">Top of the table</span><span class="end" style="right:0">Bottom</span></div>"""


def share_bars(items, unit=""):
    out = "".join(f'<span class="l">{lab}</span><span class="t"><i class="{c}" style="width:{v:.0f}%"></i></span><span>{v:.0f}%</span>'
                  for lab, v, c in items)
    return f'<div class="share" aria-hidden="true">{out}</div>'


def signals(num=None):
    k = K
    lr_low = k["low_lr_trouble"] / k["low_lr_insurers"] * 100
    lr_oth = k["other_trouble"] / k["other_insurers"] * 100
    return f"""<section id="signals" aria-labelledby="h-signals">
<div class="sechead">{eb(num, "What a reinsurer would act on") if num else '<span class="eyebrow">What a reinsurer would act on</span>'}
<h2 id="h-signals">The warnings were in the public returns</h2>
<p>Three results from the series that change a decision. Insurer names stay inside the analysis pages, next to the method and caveats.</p></div>
<div class="signals">
<div class="panel">
<span class="tag">Cedant Scorecard back-test</span>
<p class="big">{k['bt_bottom']} <small>of {k['bt_total']}</small></p>
<p>insurers the regulator stepped into since 2022 sat in the bottom fifth of the table a year before it acted.</p>
{backtest_strip()}
<div class="legend"><span><i></i>bottom fifth</span><span><i class="out"></i>mid-table, but had stopped filing complete returns</span></div>
<p class="small">Five cases is a small sample, and the test cannot show how many low-graded insurers carried on without trouble.</p>
</div>
<div class="panel">
<span class="tag">Motor books that look too good</span>
<p class="big">{k['low_lr_trouble']} <small>of {k['low_lr_insurers']}</small></p>
<p>insurers that booked a motor loss ratio under 40% in some year had negative equity, a capital shortfall or regulator action at some point since 2018, against {k['other_trouble']} of the other {k['other_insurers']} motor insurers.</p>
{share_bars([("Booked a motor loss ratio under 40%", lr_low, ""), ("Every other motor insurer", lr_oth, "g")])}
<p class="small">Fisher's exact test, p = {k['fisher_p']}. A low loss ratio is often a reserving question, not a pricing success.</p>
</div>
<div class="panel">
<span class="tag">Underwriting profit is getting rarer</span>
<p class="big">{k['profit_2025']} <small>of {k['active_2025']}</small></p>
<p>insurers made an underwriting profit in 2025, down from {k['profit_2016']} of {k['active_2016']} in 2016.</p>
{share_bars([("2016", k['profit_2016'] / k['active_2016'] * 100, "b"), ("2025", k['profit_2025'] / k['active_2025'] * 100, "b")], "of insurers in profit")}
<p class="small">In 2025 the market's {ksh(-k['uw_2025'])} underwriting loss was covered by {ksh(k['inv_2025'])} of investment income.</p>
</div>
</div>
</section>"""


def contact_block(heading="Get in touch", hid="h-contact", num=None):
    return f"""<section id="contact" class="contact" aria-labelledby="{hid}">
<div class="sechead">{eb(num, "Contact") if num else '<span class="eyebrow">Contact</span>'}<h2 id="{hid}">{heading}</h2>
<p>If you are hiring for an actuarial, pricing, reserving or data role at an insurer or reinsurer, write to me.</p></div>
<ul>
<li><a href="mailto:{EMAIL}"><span>Email</span><b>{EMAIL}</b></a></li>
<li><a href="{LINKEDIN}"><span>LinkedIn</span><b>in/marion-peter</b></a></li>
<li><a href="{GH}"><span>GitHub</span><b>github.com/maidenpeter</b></a></li>
</ul>
</section>"""



# ------------------------------------------------------------- run-off triangle
def load_triangles():
    return json.load(open(ROOT / "tools" / "cas_triangles.json", encoding="utf-8"))


def chain_ladder(t):
    """Volume-weighted chain ladder. Returns factors, the completed square and reserve (same units as t)."""
    n = len(t)
    f = []
    for j in range(n - 1):
        r = [i for i in range(n) if t[i][j + 1] is not None]
        f.append(sum(t[i][j + 1] for i in r) / sum(t[i][j] for i in r))
    sq, reserve, paid = [], 0.0, 0.0
    for i in range(n):
        row = list(t[i])
        last = max(j for j in range(n) if row[j] is not None)
        for j in range(last + 1, n):
            row[j] = row[j - 1] * f[j - 1]
        sq.append(row)
        reserve += row[-1] - t[i][last]
        paid += t[i][last]
    return f, sq, reserve, paid


def usm(v):
    """US$ thousands to a US$m label, one decimal."""
    return f"US${d1(v / 1000, sign=False)}m".replace(".0m", ".0m")


def money_m(v):
    q = Decimal(str(v / 1000)).quantize(Decimal("0.1"), ROUND_HALF_UP)
    return f"{q:,}"


TRI_JS = r"""<script>(function(){
var el=document.getElementById('tri');if(!el)return;
var D=JSON.parse(document.getElementById('tri-data').textContent),body=el.querySelector('tbody');
var outU=document.getElementById('tri-ult'),outP=document.getElementById('tri-paid'),outR=document.getElementById('tri-res'),cap=document.getElementById('tri-cap');
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,timer=null;
function fmt(v){return (Math.round(v/100)/10).toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1})}
function cl(t){var n=t.length,f=[],j,i;for(j=0;j<n-1;j++){var a=0,b=0;for(i=0;i<n;i++){if(t[i][j+1]!=null){a+=t[i][j+1];b+=t[i][j]}}f.push(a/b)}
var sq=[],res=0,paid=0,last=[];for(i=0;i<n;i++){var r=t[i].slice(),l=0;for(j=0;j<n;j++)if(r[j]!=null)l=j;for(j=l+1;j<n;j++)r[j]=r[j-1]*f[j-1];sq.push(r);last.push(l);res+=r[n-1]-t[i][l];paid+=t[i][l]}
return{sq:sq,res:res,paid:paid,last:last}}
function draw(k){var L=D.lines[k],t=L.paid,n=t.length,c=cl(t),h='',i,j;
for(i=0;i<n;i++){h+='<tr><th scope="row">'+(D.ay0+i)+'</th>';var u=c.sq[i][n-1];
for(j=0;j<n;j++){var v=c.sq[i][j],a=(0.10+0.72*v/u).toFixed(3),p=j>c.last[i];
h+='<td class="'+(p?'p':'')+'" style="--a:'+a+'" data-d="'+(i+j)+'" title="'+(D.ay0+i)+', year '+(j+1)+(p?' projected':' paid')+': US$'+fmt(v)+'m"></td>'}h+='</tr>'}
body.innerHTML=h;cap.textContent=L.name;outU.textContent=fmt(c.paid+c.res);outP.textContent=fmt(c.paid);
var cells=body.querySelectorAll('td.p');if(timer)clearInterval(timer);
if(still){cells.forEach(function(x){x.classList.add('on')});outR.textContent=fmt(c.res);return}
var d=n,shown=0;outR.textContent='0.0';
timer=setInterval(function(){var add=0;cells.forEach(function(x){if(+x.dataset.d===d)x.classList.add('on')});
for(var ii=0;ii<n;ii++){for(var jj=c.last[ii]+1;jj<n;jj++){if(ii+jj===d)add+=c.sq[ii][jj]-c.sq[ii][jj-1]}}
shown+=add;d++;outR.textContent=fmt(d>2*n-2?c.res:shown);if(d>2*n-2){clearInterval(timer);outR.textContent=fmt(c.res)}},170)}
var btns=document.querySelectorAll('.tri-tabs button');btns.forEach(function(b){b.addEventListener('click',function(){btns.forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');draw(+b.dataset.k)})});
draw(0)})();</script>"""


def triangle_panel():
    """Hero: a chain ladder on real paid triangles, computed in the page. The static table is the same
    calculation done here, so the page reads correctly without JavaScript."""
    d = load_triangles()
    lines = d["lines"]
    total = sum(chain_ladder(L["paid"])[2] for L in lines)
    L0 = lines[0]
    f, sq, res, paid = chain_ladder(L0["paid"])
    n = len(sq)
    rows = []
    for i in range(n):
        last = max(j for j in range(n) if L0["paid"][i][j] is not None)
        u = sq[i][-1]
        cells = "".join(
            f'<td class="{"p on" if j > last else ""}" style="--a:{0.10 + 0.72 * sq[i][j] / u:.3f}"></td>' for j in range(n))
        rows.append(f'<tr><th scope="row">{1988 + i}</th>{cells}</tr>')
    head = "".join(f'<th scope="col">{j + 1}</th>' for j in range(n))
    tabs = "".join(f'<button type="button" data-k="{k}" aria-pressed="{"true" if k == 0 else "false"}">{esc(L["name"])}</button>'
                   for k, L in enumerate(lines))
    data = json.dumps({"ay0": 1988, "lines": [{"name": L["name"], "paid": L["paid"]} for L in lines]}, separators=(",", ":"))
    return f"""<figure class="tri-panel" aria-labelledby="tri-h">
<span class="eyebrow">Calculated on this page</span>
<h2 id="tri-h">A claims reserve, worked out in front of you</h2>
<p class="small">Ten years of US industry paid claims for one line. The page fits a chain ladder on the known cells and fills the empty corner one calendar year at a time.</p>
<div class="tri-tabs" role="group" aria-label="Line of business">{tabs}</div>
<table class="tri" id="tri" aria-describedby="tri-sum">
<caption class="sr-only" id="tri-cap">{esc(L0['name'])}</caption>
<thead><tr><th scope="col"><span class="sr-only">Accident year</span></th>{head}</tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<ul class="tri-key"><li><i style="background:rgba(var(--cell),.6)"></i>Paid to date</li><li><i style="background:var(--mark)"></i>Projected</li><li>Rows: accident year. Columns: development year.</li></ul>
<div class="tri-read" aria-live="polite"><div><span>Paid, US$m</span><b id="tri-paid">{money_m(paid)}</b></div><div><span>Ultimate, US$m</span><b id="tri-ult">{money_m(paid + res)}</b></div><div><span>Reserve, US$m</span><b id="tri-res">{money_m(res)}</b></div></div>
<p class="small" id="tri-sum">NAIC Schedule P, all US insurers, accident years 1988 to 1997. The six lines need US${d1(total / 1e6, sign=False)}bn, the reserve the <a href="/work/ifrs17-measurement/">IFRS 17 case study</a> starts from.</p>
<script type="application/json" id="tri-data">{data}</script>
</figure>"""


def contents(items):
    return '<nav aria-label="Contents"><ol class="contents">' + "".join(
        f'<li><a href="#{a}"><i>{i:02d}</i>{t}</a></li>' for i, (a, t) in enumerate(items, 1)) + "</ol></nav>"


def eb(num, text):
    return f'<span class="eyebrow"><i>{num:02d}</i>{text}</span>'


def apps_section(num):
    a = AP
    hil = f"""<article class="card">
<span class="badge">Live link to follow</span>
<span class="tag">Health reserving, R and Shiny</span>
<h3>Health IBNR Lab</h3>
<p class="find">A synthetic medical book of {n(a['hil_claims'])} claims. Best estimate outstanding KES {n(a['hil_be_kes'])}, Mack CV {d1(a['hil_cv'], False)}%. Then the test that matters: <b>a {a['hil_backlog_months']}-month, {a['hil_backlog_pct']}% payment slowdown makes chain ladder under-reserve by {d1(a['hil_backlog_err_pct'], False)}%</b>.</p>
<dl class="meta"><dt>Method</dt><dd>Paid and received triangles, chain ladder, Mack, Bornhuetter-Ferguson, an ODP bootstrap and an IFRS 17 liability for incurred claims view.</dd><dt>Data</dt><dd>Seeded synthetic portfolio. Illustrative only.</dd></dl>
</article>"""
    ipl = f"""<article class="card">
<span class="badge live">Live</span>
<span class="tag">Health product design, SQL, Python and R</span>
<h3>Instalment Persistency Lab</h3>
<p class="find">Pay-as-you-go health cover on a synthetic book of {n(a['ipl_policies'])} policies. {d1(a['ipl_inforce_10'], False)}% are still in force after the 10th instalment, and members who lapse are paid <b>KES {a['ipl_lapsed_ratio']:.2f} in claims for every KES 1</b> they paid in, against KES {a['ipl_stayed_ratio']:.2f} for members who stay.</p>
<dl class="meta"><dt>Method</dt><dd>Decrement tables in SQL (DuckDB), survival checks in R, an early warning model and a product levers simulator.</dd><dt>Data</dt><dd>Seeded synthetic portfolio. Illustrative only.</dd></dl>
<div class="links"><a href="{IPL_URL}">Open the app</a><a href="{GH}/instalment-persistency-lab">Code: instalment-persistency-lab</a></div>
</article>"""
    return f"""<section id="apps" aria-labelledby="h-apps">
<div class="sechead">{eb(num, "Apps")}
<h2 id="h-apps">Reserving and product questions, as tools you can use</h2>
<p>Built on synthetic books so every number can be published, with the assumptions on the page and tests behind them.</p></div>
<div class="apps">{hil}{ipl}</div>
</section>"""


# ------------------------------------------------------------------ pages
CASES = [
    dict(slug="dealer-revenue", tag="Kenyan motor dealer group, anonymised",
         title=f"Revenue was being reported {D['overstated_pct']}% higher than it was earned",
         data=f"Three system extracts: {n(D['rows'])} rows of parts invoices, service jobs and workshop consumption, January 2022 to August 2026.",
         method=f"Joins tested before any total, every unmatched invoice accounted for, bad rows flagged rather than deleted, every figure built in pandas and in Excel and reconciled cell by cell ({n(D['cells_match'])} of {n(D['cells'])}).",
         desc="A dealer group's revenue counted the same money twice. Finding it before answering the brief on growth and margin."),
    dict(slug="ifrs17-measurement", tag="US industry reserves, IFRS 17",
         title="Discounting makes a reserve smaller. On one line, IFRS 17 makes it bigger",
         data="CAS Loss Reserving Database: NAIC Schedule P paid triangles for six US lines, accident years 1988 to 1997.",
         method=f"Chain ladder to the payment pattern, discounting, and a risk adjustment from {n(I['sims'])} over-dispersed Poisson bootstrap simulations, checked against the point estimate first.",
         desc="US$25.16bn of claims reserves remeasured under IFRS 17: discounting, a bootstrapped risk adjustment, and the one line the standard makes larger."),
    dict(slug="valuation-adequacy", tag="US vehicle auctions, valuation adequacy",
         title="An estimate that is unbiased in total and biased in every condition band",
         data=f"{n(A['rows'])} US wholesale auctions with the market's pre-sale estimate and the price paid, 2014 to 2015 (Kaggle).",
         method="Run as a reserve adequacy test: profile every field, check the aggregate, then segment by condition and try to break the result with value, mileage and seller checks.",
         desc="A reserve adequacy test on 476,882 car auctions: clean in aggregate, biased in every condition band, with 78% of the error cancelling in the total."),
]


def case_rows():
    out = []
    for c in CASES:
        out.append(f"""<article class="case">
<div class="left"><span class="tag">{c['tag']}</span><h3><a href="/work/{c['slug']}/">{c['title']}</a></h3>
<a class="more" href="/work/{c['slug']}/">Read the case study</a></div>
<dl class="meta"><dt>Data</dt><dd>{c['data']}</dd><dt>Method</dt><dd>{c['method']}</dd></dl>
</article>""")
    return '<div class="cases">' + "".join(out) + "</div>"


def load_products():
    p = ROOT / "tools" / "products.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else []


def products_section(num=None):
    items = load_products()
    if not items:
        return ""
    figs = []
    for it in items:
        link = f' <a href="{it["repo"]}">Code</a>' if it.get("repo") else ""
        figs.append(f"""<figure class="shot">
<div class="frame"><img src="/assets/products/{it['image']}" alt="{esc(it['alt'])}" width="1280" height="800" loading="lazy" decoding="async"></div>
<figcaption><b>{esc(it['name'])}</b><span>{esc(it['line'])}{link}</span></figcaption>
</figure>""")
    return f"""<section id="products" aria-labelledby="h-products">
<div class="sechead">{eb(num, "Products") if num else '<span class="eyebrow">Products</span>'}<h2 id="h-products">Things I have built</h2>
<p>Products built outside the day job, where pricing and risk meet a real user. Screenshots from each product's own repository; the analysis above is where the checked numbers are.</p></div>
<div class="shots">{''.join(figs)}</div>
</section>"""


PRINCIPLES = [
    ("Rebuild before analysing", "A regulator's table is a secondary source. Every IRA table was rebuilt from its parts and matched to the printed total before any finding was drawn from it."),
    ("Read across quarters as well as down the page", f"A return can add up and still be wrong. {w(K['error_returns'], True)} IRA returns pass every identity but fail when read against the same insurer's other quarters, so they are flagged and kept out of quarterly totals."),
    ("Flag, never delete", "Excluded rows stay in the data with a flag, so any exclusion can be reversed and audited by someone else."),
    ("Say what it cannot tell you", "Each page names its data and method before its first finding and ends with its limits. Grades and rankings are screening measures, not credit ratings."),
    ("Make it rerun", "One command rebuilds each repository from the raw files, and GitHub Actions runs the tests on every push."),
    ("Show my own errors", "When a check catches a mistake of mine, the fix and what it changed are written up, not quietly patched."),
]


def home():
    principles = "".join(f"<li><b>{t}</b><span>{d}</span></li>" for t, d in PRINCIPLES)
    plac = "".join(f"<span><b>{t.split(',')[0]}</b>, {t.split(', ', 1)[1]} {y}</span>" for y, t, _ in HACKATHONS)
    toc = contents([("work", "Kenya insurance series"), ("signals", "What a reinsurer would act on"), ("apps", "Apps"),
                    ("cases", "Case studies"), ("products", "Products"), ("method", "How I work"), ("contact", "Contact")])
    body = f"""<section class="hero" aria-labelledby="h1">
<div class="hero-text">
<span class="eyebrow">Insurance and reinsurance analysis</span>
<h1 id="h1">I take messy regulatory data, check it properly and turn it into decisions</h1>
<p class="lede">From 2022 to 2025 I worked in data, actuarial and reserving roles at an insurance group in Kenya and Mauritius. The work below rebuilds Kenya's general insurance market from the regulator's own returns, checks it {n(K['checks'])} times, and answers the questions an insurer's board or a reinsurer would ask of it.</p>
<div class="cta"><a class="btn primary" href="#work">See the Kenya series</a><a class="btn quiet" href="{GH}">Code on GitHub</a></div>
<p class="placings">{plac}</p>
</div>
{triangle_panel()}
</section>

{proof_strip()}

{toc}

<section id="work" aria-labelledby="h-work">
<div class="kenya-head">
<div class="sechead">{eb(1, "Featured work")}
<h2 id="h-work">Kenya insurance series</h2>
<p>Every general insurer and reinsurer in Kenya, every quarter from Q4 2016 to Q1 2026, extracted from the Insurance Regulatory Authority's statistics and checked against itself. Four pages, one validated dataset, three public repositories.</p>
<p>Motor lost money in every one of the eight years from 2018 to 2025. Every other class together made {ksh(K['uw_other'])}.</p>
<a class="more" href="/kenya-insurance/">How the series is built</a></div>
{chart_panel()}
</div>
<div class="grid2">{kenya_cards()}</div>
</section>

{signals(2)}

{apps_section(3)}

<section id="cases" aria-labelledby="h-cases">
<div class="sechead">{eb(4, "Case studies")}
<h2 id="h-cases">The same standard on other data</h2>
<p>The first is Kenyan client work, published without client identifiers. The other two use public US data sets with the long claims and price histories the methods need.</p></div>
{case_rows()}
</section>

{products_section(5)}

<section id="method" aria-labelledby="h-method">
<div class="sechead">{eb(6, "How I work")}
<h2 id="h-method">A total that balances is the first thing I check</h2>
<p>The habit from actuarial training that stuck: distrust a clean number until it survives being split apart.</p></div>
<ul class="principles">{principles}</ul>
<div class="next"><span class="tag">Next</span><p>A reserving tool in Streamlit: chain ladder and Bornhuetter-Ferguson on the claims development tables Kenyan insurers publish under IFRS 17, with the reserve each method implies set against what was booked. It will be linked here when it is live.</p></div>
</section>

{contact_block(num=7)}
{TRI_JS}"""
    return layout("/", f"Marion Peter | {ROLE}",
                  "Kenya's general insurance market rebuilt from the regulator's returns and checked 42,246 times: where insurers lose money, what premiums would need to do, and which cedants a reinsurer should worry about.",
                  body, "home", og_title=f"Marion Peter, {ROLE}")


def kenya_series():
    steps = [
        ("Collect", f"{K['files']} files", f"Every IRA statistical publication online from {K['first_year']}, catalogued with source links and SHA-256 hashes."),
        ("Extract", f"{n(K['revenue_rows'] + K['class_rows'])} rows", "Revenue accounts and class tables from workbooks whose layouts and company names shift from year to year."),
        ("Validate", f"{n(K['checks'])} checks", "Accounting identities, class totals, IRA's printed totals and a cross-check against the PDF releases."),
        ("Flag", f"{K['error_returns']} returns", "Returns that add up but cannot be right, such as year-to-date premium that falls, kept out of quarterly totals."),
        ("Analyse", "4 pages", "Profitability, market structure, a reinsurer's scorecard and an explorer, each rebuilt by one command."),
    ]
    pipe = "".join(f'<div class="step"><b>{a}</b><span class="n">{b}</span><p>{c}</p></div>' for a, b, c in steps)
    repos = "".join(f"""<article class="card"><span class="tag">{t}</span><h3><a href="{u}">{r}</a></h3><p>{d}</p></article>""" for t, r, u, d in [
        ("Data layer", "ira-kenya-data", CODE["data"], "Extraction, the company crosswalk, single-quarter panels, quality flags and validation. Tests on the processed tables run on every push."),
        ("Insurer's view", "ira-kenya-insurance", CODE["insurance"], "Class profitability, rate adequacy, the low loss ratio test and market structure. Tests tie class totals to IRA's PDF releases."),
        ("Reinsurer's view", "ira-kenya-reinsurance", CODE["reinsurance"], "The cedant scorecard on four pillars, with its back-test and weight sensitivity. Tests pin down the scoring rules."),
    ])
    body = f"""<section class="hero" aria-labelledby="h1">
<div class="hero-text">
<span class="eyebrow">Kenya's insurance market, rebuilt from the regulator's own returns</span>
<h1 id="h1">Where Kenyan insurers make money, and where they lose it</h1>
<p class="lede">Every general insurer and reinsurer, every quarter from Q4 2016 to Q1 2026, extracted from the Insurance Regulatory Authority's statistics, checked against itself and turned into analysis an insurer's board or a reinsurer could use.</p>
<p class="big loss num">{ksh(K['uw_motor'])}</p><p class="small" style="margin-top:-10px">motor underwriting result, 2018 to 2025</p>
<p class="big gain num">KSh +{d1(K['uw_other'], False)}bn</p><p class="small" style="margin-top:-10px">every other class together, {ksh(K['uw_wc'])} of it from workmen's compensation</p>
</div>
{chart_panel()}
</section>

{proof_strip()}

<section aria-labelledby="h-pages">
<div class="sechead"><span class="eyebrow">The pages</span><h2 id="h-pages">Four ways into the same data</h2>
<p>Each page is a single file built from the validated tables, with the method and caveats on the page.</p></div>
<div class="grid2">{kenya_cards()}</div>
</section>

<section aria-labelledby="h-method">
<div class="sechead"><span class="eyebrow">Method</span><h2 id="h-method">From the regulator's files to a finding</h2>
<p>A return can add up on its own and still be wrong, so every company is also read across its quarters. Errors in the official tables are documented, not hidden: every one of the {K['failed_checks']} failed checks traces to a known IRA publishing error.</p></div>
<div class="pipe">{pipe}</div>
</section>

<section aria-labelledby="h-code">
<div class="sechead"><span class="eyebrow">Code</span><h2 id="h-code">Three repositories, one pipeline</h2>
<p>Python and pandas. Every published number is rebuilt from the raw files, and the raw files are listed with their IRA source links and hashes.</p></div>
<div class="grid3">{repos}</div>
</section>

<section aria-labelledby="h-next">
<div class="sechead"><span class="eyebrow">Coming next</span><h2 id="h-next">What the series adds next</h2></div>
<div class="grid2">
<div class="next"><span class="tag">Reserving</span><p>Chain ladder and Bornhuetter-Ferguson on the claims development tables insurers publish under IFRS 17, with the implied reserve set against what was booked. A Streamlit tool, linked here when live.</p></div>
<div class="next"><span class="tag">IFRS 17 and reinsurance flows</span><p>What the 2024 switch to IFRS 17 changed in reported results, and how much risk Kenyan insurers cede, by class and company.</p></div>
</div>
</section>

<section class="small" aria-label="Source">
<p>Source: Insurance Regulatory Authority, Kenya, quarterly industry statistics (unaudited returns), <a href="https://www.ira.go.ke">ira.go.ke</a>. Everything here is public data; nothing comes from inside any insurer. Grades and rankings are relative screening measures, not credit ratings.</p>
</section>"""
    return layout("/kenya-insurance/", "Kenya Insurance, Rebuilt | Marion Peter",
                  "Kenya's general insurers and reinsurers, every quarter from Q4 2016 to Q1 2026, rebuilt from IRA's returns: profitability, market structure, a reinsurer's scorecard and a data explorer.",
                  body, "kenya", og_title="Kenya Insurance, Rebuilt")


def facts(items):
    return '<div class="facts">' + "".join(f"<div><span>{a}</span><b>{b}</b></div>" for a, b in items) + "</div>"


def checks_list(items):
    return '<ul class="checks">' + "".join(
        f'<li><span class="mk {"ok" if ok else "warn"}" aria-label="{"Passed" if ok else "Caveat"}">{"&#10003;" if ok else "!"}</span><p><b>{t}</b> {d}</p></li>'
        for ok, t, d in items) + "</ul>"


def limits(items):
    return '<ul class="limits">' + "".join(f"<li><b>{t}</b> {d}</li>" for t, d in items) + "</ul>"


def pager(c):
    """Previous and next case study, wrapping round, so a reader can move through them without going home."""
    i = next(k for k, x in enumerate(CASES) if x["slug"] == c["slug"])
    prev, nxt = CASES[i - 1], CASES[(i + 1) % len(CASES)]
    return f"""<nav class="pager" aria-label="More case studies">
<a href="/work/{prev['slug']}/" rel="prev"><span>Previous case study</span><b>{prev['title']}</b></a>
<a class="nx" href="/work/{nxt['slug']}/" rel="next"><span>Next case study</span><b>{nxt['title']}</b></a>
</nav>"""


def case_page(c, eyebrow, lede, fact_items, data, method, sections, lim, code_note):
    body = f"""<section aria-labelledby="h1">
<a class="more" href="/#cases">All case studies</a>
<span class="eyebrow">{eyebrow}</span>
<h1 id="h1" style="font-size:clamp(34px,5vw,54px);max-width:22ch">{c['title']}</h1>
<p class="lede">{lede}</p>
{facts(fact_items)}
<div class="dm"><div><span class="tag">Data</span><p>{data}</p></div><div><span class="tag">Method</span><p>{method}</p></div></div>
</section>
{sections}
<section aria-labelledby="h-limits">
<div class="sechead"><span class="eyebrow">Limits</span><h2 id="h-limits">What this analysis cannot tell you</h2></div>
{limits(lim)}
<p class="note">{code_note}</p>
</section>
{pager(c)}"""
    return layout(f"/work/{c['slug']}/", f"{c['title']} | Marion Peter", c["desc"], body, "work",
                  og_title=c["title"])


def colbars(items, unit, top):
    bars = "".join(f'<div><b>{lab}</b><i style="height:calc((200px - 34px) * {max(v / top, 0.01):.3f});background:var({col})"></i></div>' for v, lab, col, _ in items)
    labels = "".join(f"<span>{t}</span>" for _, _, _, t in items)
    return f'<div role="img" aria-label="{esc(unit)}"><div class="colbars">{bars}</div><div class="collabels">{labels}</div></div>'


def dealer_page():
    c = CASES[0]
    s1 = f"""<section aria-labelledby="h-s1">
<div class="sechead"><span class="eyebrow">Step one</span><h2 id="h-s1">Test the joins before adding the ledgers</h2></div>
<div class="pair">
<div class="prose">
<p>The brief assumed three independent sources: a parts invoice ledger ({n(D['parts_rows'])} lines), a service job ledger ({n(D['job_rows'])} rows) and a workshop consumption log ({n(D['consumption_rows'])} rows). Adding the two ledgers gave the revenue figure in use.</p>
<p>Before adding anything I matched invoice numbers across them. {n(D['overlap'])} of {n(D['jobs'])} job invoices, <b>{d1(D['overlap_pct'], False)}%</b>, also appear as workshop sales on the parts ledger: the same parts, reaching the books by two routes. Each ledger is right on its own. Treating them as additive counted <b>KSh {D['double_bn']}bn</b> twice.</p>
<p>Revenue was KSh {D['actual_bn']}bn, not KSh {D['reported_bn']}bn. Growth rates, branch shares and margin had all been measured against a base that did not exist.</p>
</div>
<figure class="panel" style="margin:0"><h3>Revenue, KSh billions</h3>
{colbars([(D['reported_bn'], str(D['reported_bn']), '--loss', 'As reported'), (D['actual_bn'], str(D['actual_bn']), '--gain', 'After removing the double count')], f"Revenue as reported KSh {D['reported_bn']}bn against KSh {D['actual_bn']}bn after removing the double count", D['reported_bn'])}
<p class="small">January 2022 to August 2026.</p></figure>
</div>
{checks_list([
    (True, f"The {n(D['labour_only'])} unmatched job invoices are labour only.", "None of them carries parts, so removing the overlap drops nothing."),
    (True, f"The KSh {D['residual_m']}m residual between the ledgers is a price basis, not missing money.", f"KSh {D['residual_2022_m']}m of it is 2022, when the job ledger carried parts at {D['ratio_2022']} times the parts ledger price; from 2023 the two agree to within rounding."),
])}
</section>"""
    s2 = f"""<section aria-labelledby="h-s2">
<div class="sechead"><span class="eyebrow">Step two</span><h2 id="h-s2">A few hundred bad rows decided the margin story</h2></div>
<div class="pair">
<div class="prose">
<p>Margin is measured only on lines with a valid cost, from 2024 onward. The 2022 and 2023 lines are left unmeasured rather than estimated.</p>
<p>The later data had its own trap. <b>{D['bad_cost_rows']} credit-sale lines</b> in 2026 carried costs far above the normal level for the same items, about KSh {D['bad_cost_excess_m']}m of excess cost. Left in, they put 2026 gross margin at {d1(D['gm_2026_reported'], False)}% and the story becomes a collapse in profitability. Flagged and excluded, 2026 margin is <b>{d1(D['gm_2026_valid'], False)}%</b>, in line with the {d1(D['gm_group'], False)}% across all lines with valid cost.</p>
<p>A meeting held on the first number would have been about a crisis that was not happening.</p>
</div>
<figure class="panel" style="margin:0"><h3>2026 gross margin</h3>
{colbars([(D['gm_2026_reported'], d1(D['gm_2026_reported'], False) + '%', '--loss', 'With the bad lines'), (D['gm_2026_valid'], d1(D['gm_2026_valid'], False) + '%', '--gain', 'Bad lines flagged')], f"2026 gross margin {d1(D['gm_2026_reported'], False)}% with the bad lines and {d1(D['gm_2026_valid'], False)}% with them flagged", 26)}
<p class="small">January to August 2026.</p></figure>
</div>
</section>"""
    s3 = f"""<section aria-labelledby="h-s3">
<div class="sechead"><span class="eyebrow">Step three</span><h2 id="h-s3">Then answer the brief, on the corrected base</h2></div>
<div class="grid3">
<div class="panel"><p class="big">{D['cagr']}%</p><p>a year compound revenue growth, 2022 to 2025.</p></div>
<div class="panel"><p class="big">{D['accident_value']}%</p><p>of job value came from accident repair, which was {D['accident_jobs']}% of jobs: a commercial opportunity and a capacity risk in one number.</p></div>
<div class="panel"><p class="big">{D['insurer_share']}%</p><p>of revenue came from {D['insurer_customers']} insurers as customers. Growth that leans on so few counterparties is growth with more concentration risk.</p></div>
</div>
</section>
<section aria-labelledby="h-s4">
<div class="sechead"><span class="eyebrow">How it was checked</span><h2 id="h-s4">Every figure built twice</h2></div>
{checks_list([
    (True, f"{n(D['cells_match'])} of {n(D['cells'])} headline cells match.", "Each figure was produced once in pandas and once as live Excel formulas, then compared cell by cell, so the client could open the workbook, change an assumption and watch the number move."),
    (True, "Flags, never deletions.", "Every excluded row stays in the data with a flag column, so any exclusion can be reversed."),
    (True, "Assumptions first.", "Every judgement call is one editable cell, stated before any result that depends on it."),
])}
</section>"""
    lim = [
        ("Margin before 2024 is not reported.", "An estimate was possible, but not one that could be checked."),
        (f"The {D['bad_cost_rows']} bad cost lines were flagged, not repaired.", "Their true cost is unknown, and imputing it would invent margin."),
        (f"The {D['ratio_2022']} price ratio in 2022 is inferred from the data,", "not from documentation. It is consistent across the year and explains the gap, but the pricing policy behind it was not seen."),
        ("This is one dealer group in one market.", "The double-count pattern is common where a parts ledger and a job ledger sit side by side, but nothing here shows how common."),
    ]
    return case_page(c, c["tag"],
                     f"Three system extracts from a Kenyan vehicle dealer group, {n(D['rows'])} rows from January 2022 to August 2026. The brief was growth and margin. The first finding was that the revenue figure everyone was using counted the same money twice.",
                     [("Rows", n(D['rows'])), ("Period", "Jan 2022 to Aug 2026"), ("Sources", "3 system extracts"), ("Tools", "Python, pandas, Excel")],
                     "Parts invoice lines, service job invoices and workshop consumption rows exported from the dealer's systems. The dealer, its branches, brand and counterparties are not named, and none of its data is published.",
                     "Invoice-level matching across ledgers before any total; every unmatched invoice and the residual gap accounted for; bad rows flagged, not deleted; every figure produced in pandas and in Excel formulas and reconciled cell by cell.",
                     s1 + s2 + s3, lim,
                     "Client work. The data and the code stay with the client; this page shows only counts, percentages and the method.")


def ifrs17_page():
    c = CASES[1]
    s = f"""<section aria-labelledby="h-s1">
<div class="sechead"><span class="eyebrow">Why it matters</span><h2 id="h-s1">A claims reserve used to be one number</h2></div>
<div class="prose">
<p>Under the old basis an insurer carried outstanding claims at what it expected to pay, undiscounted, with any prudence inside the estimate. IFRS 17 splits that into the present value of future cash flows plus a risk adjustment for non-financial risk. Two of those pieces are choices as much as calculations: the discount rate, and what uncertainty is worth. So the useful output is not one number but how far the number moves across defensible choices, and on which line.</p>
</div>
</section>
<section aria-labelledby="h-s2">
<div class="sechead"><span class="eyebrow">Step one</span><h2 id="h-s2">Discounting is a question of the payment pattern</h2></div>
<div class="prose">
<p>At a flat {I['rate']}% with a mid-year convention, the six lines fall from US${I['undisc_bn']}bn to US${I['undisc_bn'] + I['disc_effect_bn']:.2f}bn: <b>US${-I['disc_effect_bn']}bn</b> comes off before any judgement is applied. The mean time to payment runs from {I['dur_low']} years for private motor to {I['dur_high']} years for medical malpractice, and that alone sets the order in which discounting shrinks the lines.</p>
</div>
</section>
<section aria-labelledby="h-s3">
<div class="sechead"><span class="eyebrow">Step two</span><h2 id="h-s3">The same three words are worth US${I['ra75_m']}m or US${I['ra95_bn']}bn</h2></div>
<div class="prose">
<p>IFRS 17 does not prescribe the risk adjustment; it requires the confidence level to be disclosed. Here the uncertainty comes from bootstrapping the same triangles: {n(I['sims'])} resampled refits with process variance. At the 75th percentile the six lines need <b>US${I['ra75_m']}m</b>; at the 95th, <b>US${I['ra95_bn']}bn</b>. Both are defensible, so the confidence level is the number, not a footnote.</p>
<p>The spread differs by line. Private motor's simulated reserve has a coefficient of variation of {I['cv_pm']}%; product liability's is {I['cv_pl']}%, with a long right tail.</p>
<p>Adding the six risk adjustments assumes every line goes wrong at once. Treating them as independent gives US${I['indep75_m']}m instead of US${I['ra75_m']}m at the 75th percentile. That one assumption is worth US${I['diversification_m']}m, {I['div_pct']}% of the risk adjustment, and belongs in the disclosure.</p>
</div>
</section>
<section aria-labelledby="h-s4">
<div class="sechead"><span class="eyebrow">Step three</span><h2 id="h-s4">Five lines fall. One rises</h2></div>
<div class="pair">
<figure class="panel" style="margin:0"><h3>IFRS 17 liability against the undiscounted reserve</h3>
<p class="small">Percent change. Discounted at {I['rate']}%, 75th percentile risk adjustment.</p>
{bars(IFRS17_LINES, "Change by line: " + ", ".join(f"{nm} {d1(v)}%" for nm, v in IFRS17_LINES), "%", em=lambda nm, v: v > 0, inside=2)}</figure>
<div class="prose"><p>Product liability is the exception: its risk adjustment is {d1(I['prodliab_ra'], False)}% of the reserve while discounting saves only {d1(-I['prodliab_disc'], False)}%. Every other line's uncertainty is cheaper than its waiting time.</p>
<p>The book as a whole comes down {d1(-I['book_change'], False)}%. Reported alone, that says IFRS 17 releases reserves. On one line it does the opposite, and it is the line where the estimate is least reliable.</p></div>
</div>
{checks_list([
    (True, "The bootstrap reproduces the reserve it measures.", f"The mean of the simulations is within {I['cl_within']}% of the chain ladder reserve on {I['cl_lines_within']} of the {I['lines']} lines. If it were not, the spread would describe the simulation rather than the risk."),
    (False, f"Product liability is {I['cl_pl']}% high, and that is reported rather than smoothed.", "Its triangle has negative incremental payments from recoveries, and its simulated distribution is strongly skewed. The line is flagged as the least reliable of the six."),
    (True, "Residuals are scaled and centred, with over-dispersion fitted per line.", "A single shared parameter would have made motor look riskier and product liability safer than either is."),
])}
</section>"""
    lim = [
        ("No tail beyond development year 10.", "Durations, reserves and the discount effect are all understated, most of all for the liability lines."),
        ("A flat discount rate, not a yield curve.", "IFRS 17 asks for rates consistent with the cash flows; the flat rate is a stated simplification."),
        ("One risk adjustment technique.", "A bootstrap percentile is common, not required. Cost of capital or a stress approach would give other answers from the same data."),
        ("Paid data only.", "No case estimates, claims handling costs, reinsurance or expenses in the fulfilment cash flows."),
        ("US industry data from 1997.", "The point is the measurement mechanics on real claims development, not a statement about any insurer."),
    ]
    return case_page(c, c["tag"],
                     f"US${I['undisc_bn']}bn of US industry claims reserves remeasured the way IFRS 17 requires: discounted for the time until payment, then loaded with an explicit risk adjustment. Five of six lines fall. Product liability rises {d1(I['prodliab_change'], False)}%, because its uncertainty costs more than its waiting time saves.",
                     [("Reserve", f"US${I['undisc_bn']}bn"), ("Lines", str(I['lines'])), ("Valued at", "31 December 1997"), ("Tools", "Python, numpy")],
                     "CAS Loss Reserving Database, the triangles bundled with the chainladder Python package: NAIC Schedule P cumulative paid losses for all reporting US insurers, summed by line, accident years 1988 to 1997.",
                     f"Volume-weighted chain ladder to ultimate and the future payment pattern; present value at a flat rate, mid-year; risk adjustment from an over-dispersed Poisson bootstrap of the same triangle ({n(I['sims'])} simulations with process variance), taken as a percentile less the mean and discounted on the same pattern.",
                     s, lim,
                     "The code is not on GitHub yet. The same triangles feed the reserve back-test listed on the About page.")


def auctions_page():
    c = CASES[2]
    s = f"""<section aria-labelledby="h-s1">
<div class="sechead"><span class="eyebrow">Step one</span><h2 id="h-s1">Profile before you trust: one column, two scales</h2></div>
<div class="prose">
<p>Condition is the variable that matters most here, and it holds two grading scales stacked in one column with nothing to mark which is which: {n(A['short_scale'])} rows graded 1 to 5 and {n(A['long_scale'])} graded on a scale that runs to 49. A grade 5 car sells for a median $22,100, a grade 49 for $20,600 and a grade 17 for $2,600. Treated as one variable, the best cars in the file sort below the worst.</p>
<p>There is no defensible mapping between the scales, so the short-scale rows are excluded and the exclusion is stated. Inventing a conversion would put an unverifiable assumption under every number that follows.</p>
</div>
</section>
<section aria-labelledby="h-s2">
<div class="sechead"><span class="eyebrow">Step two</span><h2 id="h-s2">In aggregate the estimate looks excellent</h2></div>
<div class="grid3">
<div class="panel"><p class="big">${A['median_gap']}</p><p>median gap between price and estimate.</p></div>
<div class="panel"><p class="big">{d1(A['below'], False)}%</p><p>of cars sold below their estimate: a coin flip.</p></div>
<div class="panel"><p class="big">{A['net_pct']}%</p><p>net across the book, US${A['net_m']}m against US${A['appraised_bn']}bn appraised.</p></div>
</div>
<p class="prose">A reviewer would sign this off. The figure that should stop them is the mean absolute error: ${n(A['mae'])} per car, {A['mae_pct']}% of the estimate. Errors that large that average to nothing are going somewhere in an organised way.</p>
</section>
<section aria-labelledby="h-s3">
<div class="sechead"><span class="eyebrow">Step three</span><h2 id="h-s3">Segmented, it overvalues poor cars and undervalues good ones</h2></div>
<div class="pair">
<figure class="panel" style="margin:0"><h3>Average gap between price and estimate, by condition decile</h3>
<p class="small">Percent of the estimate. Negative means the car sold for less, so the estimate was too high.</p>
{bars([(f"Decile {i + 1}", v) for i, v in enumerate(AUCTION_DECILES)], f"Gap by condition decile, poorest to best, from {d1(AUCTION_DECILES[0])}% to {d1(AUCTION_DECILES[-1])}%", "%")}</figure>
<div class="prose"><p>The poorest tenth sells {d1(-A['decile_low'], False)}% below its estimate; the best sells {d1(A['decile_high'], False)}% above. Above the middle the curve flattens near +3%, so the bias sits mostly in the bottom third of the scale.</p>
<p>By condition band, the estimate is {d1(-A['worst_band_pct'], False)}% too high on the poorest cars and {d1(A['best_band_pct'], False)}% too low on the best. Those errors run in opposite directions on comparable sums of money, which is why the total looked clean: <b>US${A['gross_m']}m</b> of gross misvaluation nets to US${A['net_m']}m, and <b>{A['cancel']}%</b> of it cancels.</p></div>
</div>
</section>
<section aria-labelledby="h-s4">
<div class="sechead"><span class="eyebrow">Step four</span><h2 id="h-s4">Trying to break it</h2></div>
{checks_list([
    (True, "Is condition standing in for price?", "Holding appraised value constant, the gradient runs the same way in every value band."),
    (True, "Is it mileage?", "It holds inside each odometer band too."),
    (True, "Is it a few outliers?", "Medians and 1 to 99 percentile trimmed means show the same ordering as the means."),
    (False, "Is it a handful of large sellers?", f"Without the 20 largest sellers ({n(A['excl_rows'])} rows) the poorest band still sells {d1(-A['excl_low'], False)}% below its estimate and the best {d1(A['excl_high'], False)}% above, but the middle bands reorder slightly, so the gradient is not strictly monotonic there."),
    (False, "Are the deciles monotonic?", "Not quite: two of the upper deciles dip by less than 0.1 points. The finding is the gap between the bottom and the rest, not a smooth line."),
])}
</section>
<section aria-labelledby="h-s5">
<div class="sechead"><span class="eyebrow">So what</span><h2 id="h-s5">Who pays for an error that nets to zero</h2></div>
<div class="prose">
<p>An estimate that is unbiased in total but biased by segment costs nothing until the segments are treated differently, and they always are. Settle total-loss claims at this estimate and you overpay on the worst cars and underpay owners of the best, the customers least likely to accept it. Lend against it and advance rates on poor-condition stock rest on a number that is too high on exactly the collateral most likely to default.</p>
<p>The fix is not a new model. It is to stop testing this one only in aggregate: one adequacy test by condition band, run monthly, would have shown this.</p>
</div>
</section>"""
    lim = [
        ("The data is public and it is not Kenyan.", "US wholesale auctions sold between January 2014 and July 2015, most of them from December 2014 to June 2015. The method transfers; the numbers do not."),
        (f"{n(A['short_scale'])} short-scale rows were excluded.", "They may behave differently, and checking that would need the mapping this analysis declined to invent."),
        ("Grades are assigned by inspectors.", "Some of what reads as valuation bias could be grading bias; the data has no inspector or site field to separate them."),
        ("Association, not causation.", "The estimate is biased with respect to condition. This does not show why."),
    ]
    return case_page(c, c["tag"],
                     f"{n(A['rows'])} US wholesale car auctions, each with the market's pre-sale estimate (the Manheim Market Report value) and the price paid. Across the book the estimate is off by {-A['net_pct']}%. Split by condition it is {d1(-A['worst_band_pct'], False)}% too high on the poorest cars and {d1(A['best_band_pct'], False)}% too low on the best, and {A['cancel']}% of the gross error cancels before it reaches the total.",
                     [("Rows analysed", n(A['rows'])), ("Period", "Jan 2014 to Jul 2015"), ("Appraised", f"US${A['appraised_bn']}bn"), ("Tools", "Python, pandas")],
                     f"Kaggle Vehicle Sales Data: {n(A['rows_total'])} US wholesale auction records with make, model, year, odometer, seller, a condition grade, the pre-sale estimate and the selling price. {n(A['rows'])} rows analysed after excluding the incompatible grading scale and incomplete records.",
                     "The estimate treated as a reserve and the selling price as the settled amount. Every field profiled first, then aggregate bias, error by condition, condition within value and mileage bands, and gross overvaluation set against gross undervaluation.",
                     s, lim,
                     "The code and its six tests are ready to publish but are not on GitHub yet. The data is Kaggle's and is not redistributed.")


def about():
    roles = [
        ("2024 to 2025", "Reserving Analyst", "MUA Mauritius and East Africa", "Local and regional market",
         ["Group-level IBNR reserve calculations across multiple entities", "Reserve adequacy testing on the reserving methodology itself", "IFRS 17 reporting support"],
         f"Worked example on public data: a chain ladder fitted on what was known at the end of 1994 and held against the next three years of payments. {w(BACKTEST_AE['over_reserved'], True)} of {w(BACKTEST_AE['lines'])} US industry lines were over-reserved by {BACKTEST_AE['low']} to {BACKTEST_AE['high']}%; private motor came in at {BACKTEST_AE['private_motor']} of expected. See also the <a href=\"/work/ifrs17-measurement/\">IFRS 17 measurement</a> case study."),
        ("2023 to 2024", "Actuarial Analyst", "MUA Insurance (Kenya) Limited", "Local market",
         ["Product and claims analysis to support pricing decisions", "Capital modelling, stress testing and scenario analysis", "Portfolio, intermediary, and risk and profitability analysis"],
         f"Worked example on public data: Buhlmann-Straub credibility across {CREDIBILITY['insurers']} US private motor insurers. An insurer needs about US${CREDIBILITY['k_m']}m of five-year premium before its own experience earns half credibility; for the smaller half of insurers the blend predicted the next loss ratios {d1(CREDIBILITY['small_gain'], False)}% more accurately than their own experience. See also the <a href=\"{PAGE['lossmap']}\">Kenya Loss Map</a> rate gap."),
        ("June 2022 to February 2023", "Data Analyst", "MUA Insurance (Kenya) Limited", "Local market",
         ["Power BI and Excel dashboards tracking KPIs and operational metrics", "Automated claims and performance reporting", "Data cleaning, validation and quality assurance"],
         f"Worked example on public data: the <a href=\"{PAGE['explorer']}\">Kenya Insurer Explorer</a>, every insurer's returns validated with {n(K['checks'])} checks."),
        ("February to May 2021", "Research and Data Analyst", "Utawala Africa", "Where it started",
         ["Data collection and analysis, questionnaire design, prioritisation and team leadership on research projects"], None),
    ]
    cv = "".join(f"""<div class="role"><div class="when">{w}<br>{loc}</div><div class="what"><h3>{t}, {org}</h3>
<ul>{''.join(f'<li>{b}</li>' for b in bl)}</ul>{f'<p class="ex">{ex}</p>' if ex else ''}</div></div>""" for w, t, org, loc, bl, ex in roles)
    edu = [
        ("In progress", "MSc Data Science and Analytics", "Strathmore University, Business Analytics specialisation"),
        ("2025", "Software Engineering Certificate", "Moringa School"),
        ("2023", "BSc Actuarial Science", "Strathmore University"),
    ]
    rec = HACKATHONS
    rows = lambda items: "".join(f'<div class="role"><div class="when">{w}</div><div class="what"><h3>{t}</h3><p class="small" style="font-size:15px">{d}</p></div></div>' for w, t, d in items)
    prods = load_products()
    built = ""
    if prods:
        built = '<section aria-labelledby="h-built"><div class="sechead"><span class="eyebrow">Built outside the day job</span><h2 id="h-built">Products</h2><p>Screenshots are on the <a href="/#products">home page</a>.</p></div><div class="cv">' + "".join(
            f'<div class="role"><div class="when">{esc(p["name"])}</div><div class="what"><p>{esc(p["line"])}</p></div></div>' for p in prods) + "</div></section>"
    body = f"""<section aria-labelledby="h1">
<span class="eyebrow">About</span>
<h1 id="h1">Marion Peter</h1>
<p class="lede">{ROLE}. I studied actuarial science at Strathmore, worked in data, pricing and reserving roles in Kenya and Mauritius, and am now completing an MSc in data science. The work I like best starts by checking whether the data can be trusted.</p>
</section>
<section aria-labelledby="h-exp">
<div class="sechead"><span class="eyebrow">Experience</span><h2 id="h-exp">Roles</h2>
<p>Employer data stays with the employer. Each worked example below runs the role's core skill on public data instead.</p></div>
<div class="cv">{cv}</div>
</section>
<section aria-labelledby="h-edu">
<div class="sechead"><span class="eyebrow">Education</span><h2 id="h-edu">Training</h2></div>
<div class="cv">{rows(edu)}</div>
</section>
<section aria-labelledby="h-rec">
<div class="sechead"><span class="eyebrow">Recognition</span><h2 id="h-rec">Placings</h2></div>
<div class="cv">{rows(rec)}</div>
</section>
{built}
<section aria-labelledby="h-tools">
<div class="sechead"><span class="eyebrow">Tools</span><h2 id="h-tools">What the work is built with</h2>
<p>Python (pandas, numpy, chainladder, pytest), Excel, Power BI, pdftotext for regulator PDFs, Git and GitHub Actions.</p></div>
</section>
{contact_block()}"""
    return layout("/about/", "About | Marion Peter",
                  f"Marion Peter, {ROLE}: reserving, pricing and data roles in Kenya and Mauritius, BSc Actuarial Science, MSc Data Science and Analytics in progress.",
                  body, "about", og_title=f"Marion Peter, {ROLE}")


def not_found():
    body = f"""<section aria-labelledby="h1" style="min-height:40vh;justify-content:center">
<span class="eyebrow">404</span>
<h1 id="h1">That page is not here</h1>
<p class="lede">It may have moved. The Kenya insurance series now lives at <a href="/kenya-insurance/">/kenya-insurance/</a>.</p>
<div class="cta"><a class="btn primary" href="/">Go to the home page</a><a class="btn quiet" href="/kenya-insurance/">Kenya insurance series</a></div>
</section>"""
    return layout("/404.html", "Page not found | Marion Peter", "This page could not be found.", body).replace(
        f'<link rel="canonical" href="{BASE}/404.html">\n', '<meta name="robots" content="noindex">\n')


def repo_index(repo, title, lede, links):
    """Index page for one Kenya repo's GitHub Pages site, in the same style. Links back to the series."""
    items = "".join(f'<article class="card"><span class="tag">{t}</span><h3>{h}</h3><p class="find">{d}</p><div class="links"><a href="{u}">Open the page</a></div></article>' for t, h, d, u in links)
    body = f"""<section aria-labelledby="h1"><span class="eyebrow">{repo}</span><h1 id="h1" style="font-size:clamp(32px,4.6vw,50px)">{title}</h1><p class="lede">{lede}</p>
<div class="cta"><a class="btn quiet" href="{GH}/{repo}">Code and method on GitHub</a><a class="btn quiet" href="/kenya-insurance/">The whole series</a></div></section>
<section class="grid2">{items}</section>
<section class="small"><p>Source: Insurance Regulatory Authority, Kenya, quarterly industry statistics. Public data only.</p></section>"""
    return layout(f"/{repo}/", f"{title} | Marion Peter", lede, body, "kenya")


REPO_INDEX = {
    "ira-kenya-data": ("Kenya Insurer Data", f"The data layer behind the series: every general insurer and reinsurer, every quarter from Q4 2016 to Q1 2026, validated with {n(K['checks'])} checks.",
                       [("Data", "Kenya Insurer Explorer", "Any insurer, any year: premium, ratios, single quarters, class mix, balance sheet and return-quality flags.", "explorer/kenya-insurer-explorer.html")]),
    "ira-kenya-insurance": ("Kenya Insurance Analysis", "Kenya's general insurance market from the insurer's side: where the money is lost, what premiums would have to do, and who holds the market.",
                            [("Profitability", "Kenya Insurance Loss Map", "Class by class results 2018 to 2025, the rate change each class needs, and motor results that look too good.", "page/kenya-insurance-loss-map.html"),
                             ("Market structure", "Kenya Insurance Market Structure", "Concentration, share shifts, growth against results and what fragmentation costs.", "page/kenya-insurance-market-structure.html")]),
    "ira-kenya-reinsurance": ("Kenya Cedant Scorecard", "Every Kenyan general insurer graded each year the way a reinsurer screens a cedant, back-tested against the insurers the regulator stepped into.",
                              [("Reinsurance", "Kenya Cedant Scorecard", "Grades A to E on balance sheet, operating performance, business profile and return quality, 2016 to 2025.", "page/kenya-cedant-scorecard.html")]),
}


def sitemap(paths):
    urls = "".join(f"<url><loc>{BASE}{p}</loc></url>\n" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"{rel:44s} {len(text):>7,} bytes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-index", help="also write each Kenya repo's index.html under this folder")
    a = ap.parse_args()
    pages = {
        "index.html": home(),
        "kenya-insurance/index.html": kenya_series(),
        "about/index.html": about(),
        "work/dealer-revenue/index.html": dealer_page(),
        "work/ifrs17-measurement/index.html": ifrs17_page(),
        "work/valuation-adequacy/index.html": auctions_page(),
        "404.html": not_found(),
    }
    for rel, text in pages.items():
        write(rel, text)
    paths = ["/" + r.replace("index.html", "") for r in pages if r != "404.html"]
    write("sitemap.xml", sitemap(paths))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    if a.repo_index:
        out = Path(a.repo_index)
        for repo, (title, lede, links) in REPO_INDEX.items():
            p = out / repo / "index.html"
            p.parent.mkdir(parents=True, exist_ok=True)
            text = repo_index(repo, title, lede, links)
            # repo pages are served from /<repo>/, so the shared stylesheet and icons come from the site root
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"{p} {len(text):,} bytes")


if __name__ == "__main__":
    main()
