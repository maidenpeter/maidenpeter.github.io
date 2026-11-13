"""Render the share image, the Apple touch icon and favicon.ico with a headless browser.

    python tools/render_images.py

Needs Python Playwright and a local Chrome (it uses the installed Chrome, not a downloaded one).
The share image uses the same chart component and stylesheet as the home page.
"""
import io, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build
from figures import KENYA as K
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = build.ROOT
CSS = (ROOT / "assets" / "site.css").as_uri()

OG = f"""<!doctype html><html data-theme="light"><head><meta charset="utf-8">
<link rel="stylesheet" href="{build.FONTS}"><link rel="stylesheet" href="{CSS}">
<style>
body{{margin:0;width:1200px;height:630px;overflow:hidden;background:var(--ground)}}
.og{{display:grid;grid-template-columns:470px 1fr;gap:40px;padding:48px 56px;height:100%;align-items:center}}
.og h1{{font-size:50px;line-height:1.04;margin:10px 0 16px}}
.og .lede{{font-size:22px}}
.og .who{{font-family:var(--ui);font-size:18px;color:var(--ink-2);margin-top:22px;border-top:1px solid var(--rule);padding-top:14px}}
.og .bars{{font-size:15px;row-gap:3px}}
.og .bars .track{{height:22px}}
.og .panel{{padding:20px 22px}}
</style></head><body><div class="og">
<div><span class="eyebrow">Kenya general insurance, 2018 to 2025</span>
<h1>Motor lost {build.ksh(-K['uw_motor'])}. Every other class made {build.ksh(K['uw_other'])}.</h1>
<p class="lede">Every insurer, every quarter, rebuilt from the regulator's returns and checked {build.n(K['checks'])} times.</p>
<p class="who">Marion Peter, actuarial analyst, Nairobi</p></div>
<div class="panel"><h3>Underwriting result by class, KSh bn</h3>{build.class_chart()}</div>
</div></body></html>"""

ICON = f"""<!doctype html><html><head><style>html,body{{margin:0;background:transparent}}</style></head>
<body><img src="{(ROOT / 'favicon.svg').as_uri()}" width="SIZE" height="SIZE" style="display:block"></body></html>"""


def main():
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        (tmp / "og.html").write_text(OG, encoding="utf-8")
        pg.goto((tmp / "og.html").as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(ROOT / "assets" / "og.png"))
        icons = {}
        for size in (180, 32, 16):
            pg = b.new_page(viewport={"width": size, "height": size})
            (tmp / f"i{size}.html").write_text(ICON.replace("SIZE", str(size)), encoding="utf-8")
            pg.goto((tmp / f"i{size}.html").as_uri())
            icons[size] = pg.screenshot(omit_background=True)
        b.close()
    (ROOT / "assets" / "apple-touch-icon.png").write_bytes(icons[180])
    im32 = Image.open(io.BytesIO(icons[32])).convert("RGBA")
    im32.save(ROOT / "favicon.ico", sizes=[(32, 32), (16, 16)])
    for f in ("assets/og.png", "assets/apple-touch-icon.png", "favicon.ico"):
        print(f, (ROOT / f).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
