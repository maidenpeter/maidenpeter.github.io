"""The site navigation, written once for every page on maidenpeter.github.io.

Used by tools/build.py for the portfolio pages (which load the CSS from assets/nav.css) and by
tools/kenya_nav.py for the four Kenya analysis pages (which carry it inline, so each still opens
as a single file). Class names all start with mp- so they never meet the analysis pages' own CSS.

Three parts, always on screen, on every page and at every width:
- The top bar, fixed: the seal, the name and the role in the middle; on the left, where the reader
  is ("I Data analysis / Kenya series / Loss map"; on the home page it follows the section being
  read); on the right, the theme switch and GitHub. On phones the "where" line sits under the name.
- The side bar, from 861px: Back, Home, chapter I Data analysis and chapter II Actuarial analysis
  with their pages, About and Contact. On phones the same links sit in a bar along the bottom, and a
  chapter opens as a sheet listing its pages (the popover attribute, with a fallback without it).
- On Kenya pages, a second, labelled strip held under the top bar: "I Kenya series", its five pages
  numbered, the current one filled.
Back returns to the previous page when that page was on this site, and otherwise goes up a level.
"""

import html
import json

SITE = "https://maidenpeter.github.io"
GH = "https://github.com/maidenpeter"
ROLE = "Data & Actuarial Engineer"

KENYA = {  # the Kenya series pages, in reading order: (path, label in the side bar, label in the strip)
    "overview": ("/kenya-insurance/", "Kenya series", "Overview"),
    "lossmap": ("/ira-kenya-insurance/page/kenya-insurance-loss-map.html", "Loss map", "Loss map"),
    "structure": ("/ira-kenya-insurance/page/kenya-insurance-market-structure.html", "Market structure", "Market structure"),
    "scorecard": ("/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html", "Cedant scorecard", "Cedant scorecard"),
    "explorer": ("/ira-kenya-data/explorer/kenya-insurer-explorer.html", "Insurer explorer", "Insurer explorer"),
}

# (key, numeral, title, short title for the phone bar, icon, home page anchor, one line of story,
#  home page sections that mark it while scrolling, [(href, label)])
CHAPTERS = [
    ("data", "I", "Data analysis", "Data", "chart", "/#data", "Kenya's insurers, rebuilt from the regulator's returns",
     "data work signals ask data-more",
     [(h, t) for h, t, _ in KENYA.values()] + [("/work/dealer-revenue/", "Dealer revenue audit")]),
    ("actuarial", "II", "Actuarial analysis", "Actuarial", "tri", "/#actuarial", "Reserving, IFRS 17 and pricing",
     "actuarial apps actuarial-cases",
     [("/#hil", "Health IBNR Lab"), ("/#ipl", "Persistency Lab"), ("/work/ifrs17-measurement/", "IFRS 17 measurement"),
      ("/work/valuation-adequacy/", "Reserve adequacy test"), ("/#agroshield", "AgroShield pricing")]),
]
# (href, label, short label, icon, section, home page sections that mark it)
HOME = ("/", "Home", "Home", "home", "home", "")
ASK = ("/ask/", "Ask the data", "Ask", "ask", "ask", "")
END = [("/about/", "About", "About", "person", "about", "method"),
       ("/#contact", "Contact", "Contact", "mail", None, "contact")]

# Where the reader is, on the home page, for each section the scroll reaches. A crumb is either
# (numeral, chapter, href) or (label, href); the last one is where the reader is.
_I, _II = ("I", "Data analysis", "/#data"), ("II", "Actuarial analysis", "/#actuarial")
HOME_WHERE = {
    "": [("Home", None)],
    "data": [_I], "work": [_I, ("Kenya series", "/#work")], "signals": [_I, ("Reinsurer signals", "/#signals")],
    "ask": [_I, ("Ask the data", "/#ask")], "data-more": [_I, ("Audit and models", "/#data-more")],
    "actuarial": [_II], "apps": [_II, ("Apps and pricing", "/#apps")], "actuarial-cases": [_II, ("Case studies", "/#actuarial-cases")],
    "method": [("How I work", "/#method")], "contact": [("Contact", "/#contact")],
}

# Line icons on a 24px grid, drawn in the text colour so they follow both themes.
ICONS = {
    "back": "M19.5 12h-15M10.5 6l-6 6 6 6",
    "home": "M3.5 10.5 12 3.5l8.5 7M6 9v11.5h4.5V15h3v5.5H18V9",
    "chart": "M3.5 20.5h17M7 17v-5M12 17V6.5M17 17V9.5",
    "tri": "M4 4h4.5v4.5H4zM9.75 4h4.5v4.5h-4.5zM15.5 4H20v4.5h-4.5zM4 9.75h4.5v4.5H4zM9.75 9.75h4.5v4.5h-4.5zM4 15.5h4.5V20H4z",
    "person": "M12 11.5a3.75 3.75 0 1 0 0-7.5 3.75 3.75 0 0 0 0 7.5zM4.5 20.5c.6-3.9 3.6-6 7.5-6s6.9 2.1 7.5 6",
    "mail": "M3.5 5.5h17v13h-17zM3.5 6.5l8.5 6.5 8.5-6.5",
    "ask": "M3.5 4.5h17v11.5h-9l-5 4v-4h-3zM9.6 8.4a2.4 2.4 0 1 1 3.4 2.2c-.6.3-1 .8-1 1.5M12 14v.1",
    "code": "M8.5 7 3.5 12l5 5M15.5 7l5 5-5 5M13.5 4.5l-3 15",
    "theme": "M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z",
}


def icon(name, cls="mp-ic"):
    fill = '<path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor" stroke="none"/>' if name == "theme" else ""
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="none" '
            f'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{ICONS[name]}"/>{fill}</svg>')


# The seal: an engraved monogram, double ruled, with a beaded ring and a hatched ground.
# The beaded ring turns a little when the pointer is over the name.
SEAL = """<svg class="mp-seal" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
<defs><pattern id="mp-hatch" width="2.6" height="2.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0v2.6" stroke="currentColor" stroke-width=".55"/></pattern></defs>
<circle cx="32" cy="32" r="30.6" fill="none" stroke="currentColor" stroke-width="1.5"/>
<circle cx="32" cy="32" r="28.3" fill="none" stroke="currentColor" stroke-width=".5"/>
<circle class="mp-beads" cx="32" cy="32" r="25.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="0 3.377"/>
<circle cx="32" cy="32" r="23.2" fill="url(#mp-hatch)" fill-opacity=".22" stroke="currentColor" stroke-width=".8"/>
<circle cx="32" cy="32" r="21.6" fill="none" stroke="currentColor" stroke-width=".35"/>
<path d="M32 13.4l1.7 1.7-1.7 1.7-1.7-1.7z" fill="currentColor"/>
<text x="32" y="40.6" text-anchor="middle"><tspan>M</tspan><tspan dx="-2.4">P</tspan></text>
<path d="M21.5 46.6h8M34.5 46.6h8" stroke="currentColor" stroke-width=".7" stroke-linecap="round"/>
<path d="M32 44.5l2.1 2.1-2.1 2.1-2.1-2.1z" fill="currentColor"/>
</svg>"""


def where_html(crumbs, base=""):
    """The "where you are" line: earlier crumbs are links, the last one is plain text."""
    out = []
    for i, c in enumerate(crumbs):
        num, label, href = c if len(c) == 3 else (None, c[0], c[1])
        inner = (f'<b class="mp-wn">{num}</b>' if num else "") + html.escape(label)
        if i == len(crumbs) - 1 or not href:
            out.append(f'<span class="mp-wc" aria-current="location">{inner}</span>')
        else:
            out.append(f'<a class="mp-wc" href="{base}{href}">{inner}</a>')
    return '<span class="mp-ws" aria-hidden="true">/</span>'.join(out)


def crumbs_for(path, section, extra=None):
    """Where a page sits: its chapter, then the Kenya series for the analysis pages, then the page."""
    if path == "/":
        return HOME_WHERE[""]
    if section == "about":
        return [("About", None)]
    ch = next((c for c in CHAPTERS if c[0] == section), None)
    out = [(ch[1], ch[2], ch[5])] if ch else []
    if extra is not None:
        return out + extra
    if ch:
        kenya = [v[0] for v in KENYA.values()]
        if path in kenya and path != KENYA["overview"][0]:
            out.append(("Kenya series", KENYA["overview"][0]))
        out += [(t, None) for h, t in ch[8] if h == path]
    return out


def nav_html(path, section=None, base="", up="/", where=None):
    """The top bar and side bar for one page. path: this page's address on the site; section: the
    chapter key ("data", "actuarial"), "home" or "about"; base: "" for root-relative links, or SITE for
    pages that may be opened as a file; up: where Back goes when the visitor did not arrive from this
    site; where: crumbs to show after the chapter, when the page is not in the chapter's list."""
    def cur(h, s):
        if h == path:
            return ' aria-current="page"'
        return ' aria-current="true"' if s and s == section else ""

    def top(h, t, st, ic, s, spy):
        return f'<a href="{base}{h}"{cur(h, s)} data-spy="{spy}">{icon(ic)}<span class="mp-l">{t}</span><span class="mp-s">{st}</span></a>'

    q = chr(34)
    chapters = []
    for key, num, title, short, ic, anchor, line, spy, items in CHAPTERS:
        on = section == key
        rows = "".join(f'<a class="mp-it" href="{base}{h}"{" aria-current=" + q + "page" + q if h == path else ""}>{t}</a>' for h, t in items)
        chapters.append(
            f'<div class="mp-ch">'
            f'<button class="mp-ch-btn{" mp-cur" if on else ""}"{" aria-current=" + q + "true" + q if on else ""} type="button" popovertarget="mp-ch-{key}" data-spy="{spy}">{icon(ic)}<span class="mp-s">{short}</span></button>'
            f'<div class="mp-items" id="mp-ch-{key}" popover aria-label="{title}">'
            f'<a class="mp-ch-link" href="{base}{anchor}"{" aria-current=" + q + "true" + q if on else ""} data-spy="{spy}">'
            f'<span class="mp-num">{num}</span><span class="mp-ch-t">{title}</span><span class="mp-ch-line">{line}</span></a>'
            f'{rows}</div></div>')
    # On the home page there is no level above, so Back shows only once there is somewhere to go back to.
    back = (f'<a class="mp-back" href="{base}{up}"{" hidden data-home" if path == "/" else ""}>'
            f'{icon("back")}<span class="mp-l">Back</span><span class="mp-s">Back</span></a>')
    links = top(*HOME) + "".join(chapters) + top(*ASK) + "".join(top(*e) for e in END)
    crumbs = crumbs_for(path, section, where)
    live = ""
    if path == "/":  # the home page follows the reader through its sections
        live = ' data-where="' + html.escape(json.dumps(HOME_WHERE, separators=(",", ":")), quote=True) + '"'
    return f"""<header class="mp-top">
<nav class="mp-where" aria-label="You are here"{live}>{where_html(crumbs, base)}</nav>
<a class="mp-brand" href="{base}/">{SEAL}<span class="mp-who"><b class="mp-nm">Marion Peter</b><span class="mp-role">{html.escape(ROLE)}</span></span></a>
<div class="mp-tools"><button class="mp-theme" type="button" hidden>{icon("theme")}<span class="mp-l">Paper theme</span></button><a class="mp-gh" href="{GH}" aria-label="GitHub" title="GitHub">{icon("code")}<span class="mp-l">GitHub</span></a></div>
</header>
<div class="mp-side"><nav class="mp-nav" aria-label="Main">{back}{links}</nav></div>"""


def series_html(current, base=""):
    """The Kenya series strip under the top bar on every Kenya page; current is a KENYA key or None."""
    q = chr(34)
    links = "".join(f'<li><a href="{base}{h}"{" aria-current=" + q + "page" + q if k == current else ""}><span class="mp-sub-n">{i:02d}</span>{t}</a></li>'
                    for i, (k, (h, _, t)) in enumerate(KENYA.items(), 1))
    return (f'<nav class="mp-sub" aria-label="Kenya series pages"><div class="mp-in">'
            f'<span class="mp-sub-tag"><b>I</b>Kenya series<small>{len(KENYA)} pages</small></span>'
            f'<ol class="mp-sub-list">{links}</ol></div></nav>')


# Theme switch, Back, the sheets and pop-outs, and on the home page the "where" line and the mark on
# the chapter for the section being read. Home keeps its mark only while no other link has it.
NAV_JS = """<script id="mp-nav-js">(function(){var d=document.documentElement,side=document.querySelector('.mp-side');if(!side)return;
var each=function(sel,f){[].forEach.call(document.querySelectorAll(sel),f)},hide=function(p){try{p.hidePopover()}catch(x){}};
var b=document.querySelector('.mp-theme');if(b){var l=b.querySelector('.mp-l');
var cur=function(){return d.getAttribute('data-theme')||'dark'};
var lab=function(){var c=cur();l.textContent=c==='dark'?'Paper theme':'Ink theme';b.setAttribute('aria-label','Switch to '+(c==='dark'?'paper':'ink')+' theme')};
b.hidden=false;b.addEventListener('click',function(){var x=cur()==='dark'?'light':'dark';d.setAttribute('data-theme',x);try{localStorage.setItem('mp-theme',x)}catch(e){}lab()});lab()}
var touched=false;['wheel','touchstart','keydown','mousedown'].forEach(function(t){addEventListener(t,function(){touched=true},{once:true,passive:true})});
var ready=function(){var h=location.hash,t=null;try{t=h&&document.getElementById(decodeURIComponent(h.slice(1)))}catch(e){}if(t&&!touched)t.scrollIntoView();d.classList.add('mp-ready')};
if(document.readyState==='complete')d.classList.add('mp-ready');else addEventListener('load',ready);
var bk=side.querySelector('.mp-back');if(bk){var same=false;try{same=new URL(document.referrer).origin===location.origin}catch(e){}
var st=function(){var s=history.state;return s&&typeof s==='object'?s:null},put=function(n){var s=st()||{};s.mpd=n;try{history.replaceState(s,'')}catch(e){}};
var s0=st(),depth=s0&&typeof s0.mpd==='number'?s0.mpd:(same?1:0);put(depth);
var show=function(){if(bk.hasAttribute('data-home'))bk.hidden=depth<1},sync=function(){var s=st();if(s&&typeof s.mpd==='number')depth=s.mpd;show()};
bk.addEventListener('click',function(e){if(depth>0&&history.length>1){e.preventDefault();history.back()}});
addEventListener('popstate',sync);addEventListener('pageshow',sync);
addEventListener('hashchange',function(){var s=st();if(s&&typeof s.mpd==='number')depth=s.mpd;else{depth+=1;put(depth)}show()});show()}
var guard=false;
document.addEventListener('pointerdown',function(e){var o=document.querySelector('[popover]:popover-open');guard=!!o&&!o.contains(e.target)&&!(e.target.closest&&e.target.closest('[popovertarget]'))},true);
document.addEventListener('pointercancel',function(){guard=false},true);
document.addEventListener('click',function(e){if(guard&&e.detail){guard=false;e.preventDefault();e.stopPropagation();return}guard=false;
var a=e.target.closest&&e.target.closest('[popover] a[href]'),p=a&&a.closest('[popover]');if(p&&p.matches(':popover-open'))hide(p)},true);
each('.pop',function(p){p.addEventListener('focusout',function(e){if(e.relatedTarget&&!p.contains(e.relatedTarget)&&p.matches(':popover-open'))hide(p)})});
var mq=matchMedia('(min-width:861px)'),shut=function(){if(mq.matches)each('.mp-items',function(p){if(p.matches(':popover-open'))hide(p)})};
if(mq.addEventListener)mq.addEventListener('change',shut);else if(mq.addListener)mq.addListener(shut);
if(!HTMLElement.prototype.hasOwnProperty('popover')){each('.mp-ch-btn',function(x){x.addEventListener('click',function(){var a=x.nextElementSibling&&x.nextElementSibling.querySelector('.mp-ch-link');if(a)location.href=a.href})});
each('button[popovertarget]:not(.mp-ch-btn)',function(x){x.addEventListener('click',function(){var t=document.getElementById(x.getAttribute('popovertarget'));if(t)t.toggleAttribute('data-open')})})}
var nav=side.querySelector('.mp-nav'),home=location.pathname==='/'||location.pathname==='/index.html',
secs=home?[].slice.call(document.querySelectorAll('main section[id]')):[],
links=[].slice.call(nav.querySelectorAll('[data-spy]'));if(!secs.length)return;
var wh=document.querySelector('.mp-where[data-where]'),wmap={},shown=null;try{wmap=JSON.parse(wh.getAttribute('data-where'))}catch(e){}
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
var draw=function(key){var cr=wmap.hasOwnProperty(key)?wmap[key]:wmap[''];if(!wh||!cr||shown===key)return;shown=key;
wh.innerHTML=cr.map(function(c,i){var t=c.length===3?c:[null,c[0],c[1]],inner=(t[0]?'<b class="mp-wn">'+t[0]+'</b>':'')+esc(t[1]);
return(i===cr.length-1||!t[2])?'<span class="mp-wc" aria-current="location">'+inner+'</span>':'<a class="mp-wc" href="'+esc(t[2])+'">'+inner+'</a>'}).join('<span class="mp-ws" aria-hidden="true">/</span>')};
function spy(){var y=window.innerHeight*0.3,c='',any=false;
for(var i=0;i<secs.length;i++)if(secs[i].getBoundingClientRect().top<=y)c=secs[i].id;
if(window.innerHeight+window.scrollY>=d.scrollHeight-2)c=secs[secs.length-1].id;
links.forEach(function(a){var on=!!c&&a.getAttribute('data-spy').split(' ').indexOf(c)>-1;a.classList.toggle('mp-here',on);if(on)any=true});
nav.classList.toggle('mp-spying',any);draw(c)}
var q=0;window.addEventListener('scroll',function(){if(!q)q=requestAnimationFrame(function(){q=0;spy()})},{passive:true});
window.addEventListener('resize',spy);spy()})();</script>"""

THEME_HEAD = ("<script>try{var t=localStorage.getItem('mp-theme');"
              "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>")

_SR = "position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap"

NAV_CSS = """/* Site navigation. Written by tools/nav.py; edit it there, not here.
   Needs the site tokens: --ground --surface --grain --ink --ink-2 --muted --rule --rule-soft --rule-strong --accent
   --accent-soft --on-accent and the fonts --ui --serif --display --display-sc --script --label. */
:root{--mp-side:0px;--mp-top:68px;--mp-sub:0px}
:root:has(.mp-sub){--mp-sub:52px}
html{scroll-padding-top:calc(var(--mp-top) + var(--mp-sub) + 20px)}
@media (prefers-reduced-motion:no-preference){html.mp-ready{scroll-behavior:smooth}}
body{padding-top:var(--mp-top)}
.mp-top,.mp-side{box-sizing:border-box;font-family:var(--ui)}
.mp-top *,.mp-side *{box-sizing:border-box}
.mp-ic{flex:none;display:block;width:22px;height:22px}

/* the top bar: where the reader is, the seal, name and role in the middle, then the switches */
.mp-top{position:fixed;top:0;left:0;right:0;z-index:35;height:var(--mp-top);display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);grid-template-areas:"where brand tools";align-items:center;column-gap:18px;padding:0 22px;background-color:var(--ground);background-image:var(--grain,none);border-bottom:3px double var(--rule-strong);box-shadow:0 10px 24px -18px rgba(0,0,0,.6)}
.mp-where{grid-area:where;min-width:0;display:flex;align-items:center;gap:9px;white-space:nowrap;overflow:hidden;font-family:var(--label);font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.mp-wc{display:inline-flex;align-items:baseline;min-width:0;overflow:hidden;text-overflow:ellipsis;color:var(--ink-2);text-decoration:none}
a.mp-wc:hover{color:var(--accent)}
span.mp-wc{color:var(--ink)}
.mp-wn{flex:none;margin-right:8px;font-family:var(--display);font-weight:400;font-size:18px;line-height:1;letter-spacing:0;text-transform:none;color:var(--accent)}
.mp-ws{flex:none;color:var(--rule-strong);font-family:var(--serif);font-size:16px;letter-spacing:0}
.mp-brand{grid-area:brand;display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink)}
.mp-who{display:flex;flex-direction:column;gap:1px;min-width:0}
.mp-nm{font-family:var(--display-sc);font-weight:400;font-size:23px;line-height:1.05;letter-spacing:.02em;white-space:nowrap;color:var(--ink);transition:color .2s}
.mp-role{font-family:var(--script);font-size:19px;line-height:1.1;white-space:nowrap;color:var(--accent)}
.mp-seal{flex:none;display:block;width:48px;height:48px;color:var(--accent);overflow:visible}
.mp-seal text{font-family:var(--display-sc);font-size:21px;fill:var(--ink);letter-spacing:0}
.mp-beads{transform-origin:32px 32px;transition:transform 1.4s cubic-bezier(.2,.7,.2,1)}
.mp-brand:hover .mp-beads{transform:rotate(42deg)}
.mp-brand:hover .mp-nm{color:var(--accent)}
.mp-tools{grid-area:tools;justify-self:end;display:flex;align-items:center;gap:8px}
.mp-theme,.mp-gh{display:inline-flex;align-items:center;justify-content:center;gap:9px;font-family:var(--ui);font-size:14px;line-height:1.2;white-space:nowrap;color:var(--ink-2);text-decoration:none;background:transparent;border:1px solid var(--rule);border-radius:2px;padding:6px 12px;min-height:38px;cursor:pointer}
.mp-gh{width:40px;padding:0}
.mp-gh .mp-l{@SR}
.mp-theme:hover,.mp-gh:hover{border-color:var(--accent);color:var(--ink)}
.mp-theme[hidden]{display:none}
.mp-top a:focus-visible,.mp-top button:focus-visible,.mp-side a:focus-visible,.mp-side button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* the side bar */
.mp-nav{display:flex;margin:0;padding:0}
.mp-nav a,.mp-nav .mp-ch-btn{position:relative;display:flex;align-items:center;color:var(--ink-2);text-decoration:none;font-family:var(--ui);font-size:16px;font-weight:400;line-height:1.3;border-radius:2px;transition:color .15s,background-color .15s}
.mp-nav .mp-ch-btn{background:transparent;border:0;margin:0;cursor:pointer;-webkit-appearance:none;appearance:none}
.mp-nav a:hover,.mp-nav .mp-ch-btn:hover{color:var(--accent)}
.mp-nav > a[aria-current],.mp-nav > a.mp-here,.mp-nav .mp-ch-btn.mp-cur,.mp-nav .mp-ch-btn.mp-here{color:var(--ink);background:var(--accent-soft)}
.mp-nav > a[aria-current] .mp-ic,.mp-nav > a.mp-here .mp-ic,.mp-ch-btn.mp-cur .mp-ic,.mp-ch-btn.mp-here .mp-ic{color:var(--accent)}
.mp-nav > a[aria-current]::before,.mp-nav > a.mp-here::before,.mp-ch-btn.mp-cur::before,.mp-ch-btn.mp-here::before,.mp-nav .mp-ch-link[aria-current]::before,.mp-nav .mp-ch-link.mp-here::before{content:"";position:absolute;background:var(--accent)}
.mp-nav.mp-spying > a[aria-current="page"]:not(.mp-here){color:var(--ink-2);background:transparent}
.mp-nav.mp-spying > a[aria-current="page"]:not(.mp-here) .mp-ic{color:inherit}
.mp-nav.mp-spying > a[aria-current="page"]:not(.mp-here)::before{display:none}
.mp-nav .mp-back{color:var(--ink)}
.mp-nav .mp-back[hidden]{display:none}
.mp-s{display:none}
/* chapters: a numeral, a title in engraved capitals, one line of story, then its pages */
.mp-nav .mp-ch-link{display:grid;grid-template-columns:26px minmax(0,1fr);column-gap:8px;align-items:baseline;padding:8px 10px 7px}
.mp-num{grid-row:span 2;font-family:var(--display);font-size:21px;line-height:1;color:var(--accent);text-align:center}
.mp-ch-t{font-family:var(--label);font-size:12.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink)}
.mp-ch-line{grid-column:2;font-family:var(--serif);font-style:italic;font-size:13.5px;line-height:1.3;color:var(--muted);margin-top:2px}
.mp-nav .mp-ch-link:hover .mp-ch-t,.mp-nav .mp-ch-link[aria-current] .mp-ch-t,.mp-nav .mp-ch-link.mp-here .mp-ch-t{color:var(--accent)}
.mp-nav .mp-it{margin-left:22px;padding:5px 10px 5px 14px;font-size:14.5px;line-height:1.3;border-left:1px solid var(--rule);border-radius:0}
.mp-nav .mp-it:hover{border-left-color:var(--accent)}
.mp-nav .mp-it[aria-current]{color:var(--ink);border-left:2px solid var(--accent);padding-left:13px;background:var(--accent-soft)}
.mp-skip{position:absolute;left:-9999px;top:8px;z-index:40;padding:8px 14px;background:var(--accent);color:var(--on-accent,var(--ground));font-family:var(--ui);font-size:15px;text-decoration:none}
.mp-skip:focus{left:12px}
#mp-content:focus{outline:none}
@supports not selector(:popover-open){@media (max-width:860px){.mp-items{display:none}}}

/* the Kenya series strip: a second, labelled bar held under the top bar, the series' own contents */
.mp-sub{position:sticky;top:var(--mp-top);z-index:25;min-height:var(--mp-sub);display:flex;align-items:center;background-color:var(--ground);background-image:linear-gradient(var(--accent-soft),var(--accent-soft)),var(--grain,none);border-bottom:1px solid var(--rule-strong);box-shadow:0 8px 18px -16px rgba(0,0,0,.6)}
.mp-sub .mp-in{width:100%;max-width:1180px;margin:0 auto;padding:7px 20px;display:flex;align-items:center;gap:8px 18px;font-family:var(--ui)}
.mp-sub-tag{flex:none;display:inline-flex;align-items:baseline;gap:8px;padding:5px 12px 4px;border:1px solid var(--accent);outline:1px solid var(--rule);outline-offset:2px;font-family:var(--label);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink)}
.mp-sub-tag b{font-family:var(--display);font-weight:400;font-size:17px;letter-spacing:0;color:var(--accent)}
.mp-sub-tag small{font-size:11px;letter-spacing:.06em;text-transform:none;color:var(--muted)}
.mp-sub-list{list-style:none;margin:0;padding:2px;display:flex;flex-wrap:nowrap;gap:4px 6px;min-width:0;overflow-x:auto;scrollbar-width:none}
.mp-sub-list::-webkit-scrollbar{display:none}
.mp-sub-list a{display:inline-flex;align-items:baseline;gap:7px;padding:5px 10px;border:1px solid transparent;color:var(--ink-2);text-decoration:none;font-size:14px;white-space:nowrap}
.mp-sub-list a:hover{border-color:var(--rule-strong);color:var(--ink)}
.mp-sub-n{font-family:var(--label);font-size:11px;letter-spacing:.06em;color:var(--muted)}
.mp-sub-list a[aria-current]{background:var(--accent);border-color:var(--accent);color:var(--on-accent,var(--ground))}
.mp-sub-list a[aria-current] .mp-sub-n{color:inherit;opacity:.8}
.mp-sub a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* side bar from 861px, under the top bar */
@media (min-width:861px){
  :root{--mp-side:240px}
  body{padding-left:var(--mp-side)}
  .mp-side{position:fixed;top:var(--mp-top);left:0;bottom:0;z-index:30;width:var(--mp-side);padding:18px;overflow-y:auto;scrollbar-width:thin;background-color:var(--ground);background-image:var(--grain,none);border-right:3px double var(--rule-strong)}
  .mp-nav{flex-direction:column;gap:2px}
  .mp-nav > a{gap:13px;padding:8px 10px}
  .mp-nav > a[aria-current]::before,.mp-nav > a.mp-here::before,.mp-nav .mp-ch-link[aria-current]::before,.mp-nav .mp-ch-link.mp-here::before{left:-18px;top:6px;bottom:6px;width:3px}
  .mp-nav .mp-back{margin-bottom:6px;border:1px solid var(--rule)}
  .mp-ch{display:flex;flex-direction:column;margin:8px 0 4px}
  .mp-ch-btn{display:none!important}
  .mp-items{display:flex;flex-direction:column;position:static;inset:auto;margin:0;padding:0;border:0;background:none;color:inherit;width:auto;height:auto;overflow:visible}
}
@media (min-width:1200px){
  :root{--mp-side:264px;--mp-top:72px}
  .mp-side{padding:22px}
  .mp-seal{width:52px;height:52px}
  .mp-nm{font-size:25px}
  .mp-role{font-size:20px}
  .mp-nav > a[aria-current]::before,.mp-nav > a.mp-here::before,.mp-nav .mp-ch-link[aria-current]::before,.mp-nav .mp-ch-link.mp-here::before{left:-22px}
}
/* shorter windows: the side bar tightens step by step so every link stays on screen */
@media (min-width:861px) and (max-height:900px){.mp-ch-line{display:none}.mp-nav .mp-ch-link{padding-block:6px 5px}.mp-ch{margin:4px 0 2px}}
@media (min-width:861px) and (max-height:720px){.mp-side{padding-block:12px}.mp-nav > a{padding-block:6px}.mp-nav .mp-back{margin-bottom:2px}.mp-nav .mp-it{padding-block:3px}}
@media (min-width:861px) and (max-height:620px){:root{--mp-top:58px}.mp-seal{width:40px;height:40px}.mp-nm{font-size:21px}.mp-role{font-size:17px}.mp-nav > a{padding-block:4px;font-size:15px}.mp-nav .mp-it{padding-block:1px;font-size:13.5px}.mp-nav .mp-ch-link{padding-block:4px 3px}}
@media (min-width:861px) and (max-height:540px){.mp-side{padding-block:8px}.mp-nav > a{padding-block:2px}.mp-nav .mp-it{padding-block:0;font-size:13px}}
@media (min-width:861px) and (max-width:1060px){.mp-theme .mp-l{@SR}.mp-theme{width:40px;padding:0}}

/* phones: the name in the middle of the top bar with the switches either side and the "where" line
   under it; Back, Home, the chapters, About and Contact along the bottom */
@media (max-width:860px){
  :root{--mp-top:88px}
  :root:has(.mp-sub){--mp-sub:48px}
  .mp-top{grid-template-columns:40px minmax(0,1fr) 40px;grid-template-rows:56px minmax(0,1fr);grid-template-areas:"theme brand gh" "where where where";column-gap:10px;padding:0 12px}
  .mp-tools{display:contents}
  .mp-theme{grid-area:theme;width:40px;padding:0}
  .mp-gh{grid-area:gh}
  .mp-theme .mp-l{@SR}
  .mp-brand{justify-self:center;min-width:0;gap:10px}
  .mp-seal{width:42px;height:42px}
  .mp-nm{font-size:20px}
  .mp-role{font-size:16px}
  .mp-where{justify-content:center;align-self:stretch;font-size:11px;letter-spacing:.1em;border-top:1px solid var(--rule-soft)}
  .mp-wn{font-size:15px;margin-right:6px}
  .mp-sub .mp-in{padding:6px 12px;gap:10px}
  .mp-sub-tag{padding:4px 9px 3px;font-size:11px;letter-spacing:.1em}
  .mp-sub-tag small{display:none}
  .mp-sub-list a{padding:4px 8px;font-size:13.5px}
  .mp-nav{position:fixed;left:0;right:0;bottom:0;z-index:30;gap:2px;padding:5px 6px calc(5px + env(safe-area-inset-bottom));background-color:var(--ground);background-image:var(--grain,none);border-top:3px double var(--rule-strong);box-shadow:0 -10px 24px -16px rgba(0,0,0,.6)}
  .mp-ch{display:contents}
  .mp-nav > a,.mp-nav .mp-ch-btn{flex:1 1 0;min-width:0;flex-direction:column;justify-content:center;gap:3px;padding:6px 0 5px;min-height:52px}
  .mp-nav .mp-l{display:none}
  .mp-s{display:block;font-size:11.5px;line-height:1.1;white-space:nowrap}
  .mp-nav > a[aria-current]::before,.mp-nav > a.mp-here::before,.mp-ch-btn.mp-cur::before,.mp-ch-btn.mp-here::before{top:-5px;left:22%;right:22%;height:2px}
  .mp-items:popover-open{position:fixed;inset:auto 8px calc(74px + env(safe-area-inset-bottom)) 8px;margin:0;width:auto;max-height:70vh;overflow:auto;display:flex;flex-direction:column;gap:2px;padding:12px 12px 14px;background-color:var(--surface);background-image:var(--grain,none);color:var(--ink);border:3px double var(--rule-strong);box-shadow:0 -12px 40px -10px rgba(0,0,0,.6)}
  .mp-items::backdrop{background:rgba(5,10,18,.45)}
  .mp-items .mp-ch-link{margin-bottom:6px;border-bottom:1px solid var(--rule);padding-bottom:10px}
  .mp-nav .mp-it{padding-block:10px;font-size:16px}
  body{padding-bottom:calc(64px + env(safe-area-inset-bottom))}
}
/* landscape phones: one slim top bar, as on a desktop, and the series strip scrolls with the page */
@media (max-width:860px) and (max-height:480px){
  :root{--mp-top:50px}
  :root:has(.mp-sub){--mp-sub:0px}
  .mp-sub{position:relative;top:auto}
  .mp-top{grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);grid-template-rows:1fr;grid-template-areas:"where brand tools"}
  .mp-tools{display:flex;justify-self:end;gap:6px}
  .mp-where{justify-content:flex-start;border-top:0}
  .mp-seal{width:32px;height:32px}
  .mp-who{flex-direction:row;align-items:baseline;gap:10px}
  .mp-nm{font-size:18px}
  .mp-role{font-size:15px}
  .mp-theme,.mp-gh{width:34px;min-height:34px}
  .mp-nav > a,.mp-nav .mp-ch-btn{min-height:40px;flex-direction:row;gap:6px;padding-block:4px}
  .mp-items:popover-open{max-height:calc(100dvh - 64px);bottom:calc(52px + env(safe-area-inset-bottom))}
  body{padding-bottom:calc(52px + env(safe-area-inset-bottom))}
}
@media (max-width:380px){.mp-top{padding:0 8px;column-gap:6px}.mp-seal{width:36px;height:36px}.mp-brand{gap:8px}.mp-nm{font-size:18px}.mp-role{font-size:14.5px}.mp-where{font-size:10px;letter-spacing:.06em}}
@media (max-width:360px){.mp-nav{padding-inline:2px;gap:0}.mp-s{font-size:10.5px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.mp-nav a,.mp-beads,.mp-nm{transition:none}}
@media print{.mp-top,.mp-side,.mp-sub{display:none}body{padding:0!important}}
""".replace("@SR", _SR)
