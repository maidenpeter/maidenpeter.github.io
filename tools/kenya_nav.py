"""Put the site navigation (tools/nav.py) into the four Kenya analysis pages and their templates.

    python tools/kenya_nav.py [--repos ..]

The analysis pages live in their own repositories and carry their CSS inline, so each still opens
as a single file. This writes the side bar, Back, and the Kenya series links into each template and
into the page built from it (the page is the template with data filled in, so both get the same
change and the next rebuild keeps it). Run it again whenever tools/nav.py changes: the block sits
between mp-nav markers and is replaced in place. The first run replaces the older top header.
"""
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nav import SITE, KENYA, NAV_CSS, NAV_JS, nav_html, series_html

PAGES = [("lossmap", "Loss map", "ira-kenya-insurance/page/kenya-insurance-loss-map.html", ["ira-kenya-insurance/page/template.html"]),
         ("structure", "Market structure", "ira-kenya-insurance/page/kenya-insurance-market-structure.html", ["ira-kenya-insurance/page/structure_template.html"]),
         ("scorecard", "Cedant scorecard", "ira-kenya-reinsurance/page/kenya-cedant-scorecard.html", ["ira-kenya-reinsurance/page/template.html"]),
         ("explorer", "Insurer explorer", "ira-kenya-data/explorer/kenya-insurer-explorer.html", ["ira-kenya-data/explorer/template.html"])]

# The side bar and series strip come from nav.py; these two only matter on the analysis pages.
SUB_CSS = """
.tip{z-index:40}
@media print{body::before{display:none}body{background-image:none}}
"""
# Each page goes to one column below a viewport width of its own (900px, or 860px for the explorer).
# From 861px the side bar takes 240px, so the same rules must also apply while the space left beside
# the side bar is below that width: up to 900 + 240 = 1140px (1100px for the explorer).
_ONE_COL = ".hero,.grid2,.method{grid-template-columns:minmax(0,1fr)}.stamp{text-align:left}"
SIDE_CSS = {
    "lossmap": f"@media (min-width:861px) and (max-width:1140px){{{_ONE_COL}}}\n",
    "structure": f"@media (min-width:861px) and (max-width:1140px){{{_ONE_COL}}}\n",
    "scorecard": ("@media (min-width:861px) and (max-width:1140px){.split{grid-template-columns:1fr}.detail{position:static}"
                  ".summary{grid-template-columns:repeat(2,minmax(0,1fr))}.summary .kpi:first-child{grid-column:1 / -1}"
                  ".grid2,.method{grid-template-columns:1fr}.stamp{text-align:left}}\n"
                  # its sticky detail panel stays below the top bar and the series strip
                  "@media (min-width:861px){.detail{top:calc(var(--mp-top) + var(--mp-sub) + 12px)}}\n"),
    "explorer": ("@media (min-width:861px) and (max-width:1100px){.grid2{grid-template-columns:1fr}"
                 ".kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.tabs{margin-left:0}.stamp{text-align:left}}\n"),
}
CSS_START, CSS_END = "/* mp-nav start */\n", "/* mp-nav end */\n"
HTML_START, HTML_END = "<!-- mp-nav start -->\n", "<!-- mp-nav end -->\n"
OLD_CSS = re.compile(r"/\* portfolio header \*/\n.*?@media print\{\.mp-head,\.mp-sub\{display:none\}body::before\{display:none\}body\{background-image:none\}\}\n", re.S)
OLD_HTML = re.compile(r'<header class="mp-head">.*?</header>\n<nav class="mp-sub".*?</nav>\n', re.S)
OLD_JS = re.compile(r"<script>\(function\(\)\{var b=document\.querySelector\('\.mp-theme'\).*?</script>\n?", re.S)
NEW_JS = re.compile(r'<script id="mp-nav-js">.*?</script>', re.S)


def block(key):
    path = KENYA[key][0]
    # a skip link first and a target after the navigation, both inside the markers so re-runs stay clean
    return (HTML_START + '<a class="mp-skip" href="#mp-content">Skip to content</a>\n'
            + nav_html(path, "data", base=SITE, up="/kenya-insurance/") + "\n"
            + series_html(key, base=SITE) + '\n<span id="mp-content" tabindex="-1"></span>\n' + HTML_END)


def between(s, a, b, new):
    i, j = s.index(a), s.index(b) + len(b)
    return s[:i] + new + s[j:]


def apply(path, key):
    s = orig = path.read_text(encoding="utf-8")
    css = CSS_START + NAV_CSS + SUB_CSS + SIDE_CSS[key] + CSS_END
    if CSS_START in s:
        s = between(s, CSS_START, CSS_END, css)
    else:
        s, n = OLD_CSS.subn(lambda m: css, s)
        assert n == 1, f"{path}: old header CSS not found"
    if HTML_START in s:
        s = between(s, HTML_START, HTML_END, block(key))
    else:
        s, n = OLD_HTML.subn(lambda m: block(key), s)
        assert n == 1, f"{path}: old header not found"
    if NEW_JS.search(s):
        s = NEW_JS.sub(lambda m: NAV_JS, s)
    else:
        s, n = OLD_JS.subn(lambda m: NAV_JS + "\n", s)
        assert n == 1, f"{path}: old theme script not found"
    s = s.replace(".mp-head,.mp-sub,.wrap{position:relative;z-index:1}", ".mp-sub,.wrap{position:relative;z-index:1}")
    assert "mp-head" not in s, f"{path}: old header left behind"
    bad = sorted({c for c in s if ord(c) > 127} - set(orig))
    assert not bad, f"{path}: new non-ASCII {bad}"
    path.write_text(s, encoding="utf-8", newline="\n")
    print(f"{path}  ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default="..", help="folder holding the three ira-kenya-* repositories")
    root = Path(ap.parse_args().repos)
    for key, _, page, templates in PAGES:
        for rel in templates + [page]:
            apply(root / rel, key)


if __name__ == "__main__":
    main()
