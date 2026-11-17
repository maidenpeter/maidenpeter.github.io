"""Card thumbnails: one 16:10 picture for every page, app and case study the site links to.

    python tools/render_shots.py [--repos ..] [--apps "../../Streamlit Projects"] [--only flows,lossmap]

Pages on this site and in the three Kenya repositories are served locally the way GitHub Pages
serves them, opened in Chrome on the ink theme with the side bar hidden, and captured at the
chart that best shows what the page does. The two apps are taken from the screenshots in their
own project folders. Everything is written to assets/shots/<id>.webp at 960 x 600.
Needs Playwright, Chrome and Pillow.
"""
import argparse, http.server, io, os, threading
from pathlib import Path
from urllib.parse import unquote, urlsplit
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "shots"
SIZE = (960, 600)
REPOS = {"ira-kenya-data", "ira-kenya-insurance", "ira-kenya-reinsurance"}

# (id, page on the site, where to frame it: a scroll position in px at 1280 wide, or a CSS selector whose
#  element is placed 90px below the top), or (id, file under --apps, crop box or None)
PAGES = [
    ("lossmap", "/ira-kenya-insurance/page/kenya-insurance-loss-map.html", 740),
    ("structure", "/ira-kenya-insurance/page/kenya-insurance-market-structure.html", 1150),
    ("flows", "/ira-kenya-insurance/page/kenya-insurance-reinsurance-flows.html", "#classes .grid2"),
    ("scorecard", "/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html", 0),
    ("explorer", "/ira-kenya-data/explorer/kenya-insurer-explorer.html", 200),
    ("ifrs17", "/work/ifrs17-measurement/", "figure.panel"),
    ("valuation", "/work/valuation-adequacy/", "section[aria-labelledby=h-s3]"),
    ("dealer", "/work/dealer-revenue/", "figure.panel"),
]
FILES = [
    ("hil", "Health IBNR Lab/assets/readme/hero_backlog.png", (0, 0, 1264, 790)),
    ("ipl", "Instalment Persistency Lab/assets/screenshots/0_home.png", None),
]


def handler(repos):
    class H(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            parts = [p for p in unquote(urlsplit(path).path).split("/") if p and p not in (".", "..")]
            base = ROOT
            if parts and parts[0] in REPOS:
                base, parts = repos / parts[0], parts[1:]
            out = str(base.joinpath(*parts))
            return out + os.sep if path.endswith("/") else out

        def log_message(self, *a):
            pass
    return H


def save(img, name):
    img = img.convert("RGB")
    w, h = img.size
    target = SIZE[0] / SIZE[1]
    if abs(w / h - target) > 0.01:  # crop to 16:10 from the top left, where the story starts
        img = img.crop((0, 0, w, round(w / target))) if w / h < target else img.crop((0, 0, round(h * target), h))
    img = img.resize(SIZE, Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.webp"
    img.save(p, "WEBP", quality=80, method=6)
    print(f"assets/shots/{name}.webp  {p.stat().st_size // 1024} KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=str(ROOT.parent), help="folder holding the ira-kenya-* repositories")
    ap.add_argument("--apps", default=str(ROOT.parent.parent / "Streamlit Projects"), help="folder holding the app projects")
    ap.add_argument("--only", help="comma-separated ids to render, leaving the other shots as they are")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    for name, rel, box in FILES:
        if only and name not in only:
            continue
        src = Path(a.apps) / rel
        if not src.exists():  # the app projects live outside this repo; keep the committed shot
            print(f"skip {name}: {src} not found, keeping assets/shots/{name}.webp")
            continue
        img = Image.open(src)
        save(img.crop(box) if box else img, name)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler(Path(a.repos).resolve()))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome") if not os.environ.get("CHROME") else p.chromium.launch(executable_path=os.environ["CHROME"])
        ctx = b.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_init_script("try{localStorage.setItem('mp-theme','dark')}catch(e){}")
        pg = ctx.new_page()
        for name, path, y in PAGES:
            if only and name not in only:
                continue
            pg.goto(base + path, wait_until="networkidle")
            # the page itself, without the navigation around it
            pg.add_style_tag(content=".mp-top,.mp-side,.mp-sub,.mp-skip,.skip{display:none!important}:root{--mp-top:0px!important;--mp-sub:0px!important}"
                                     "body{padding:0!important}html{scroll-behavior:auto!important}")
            pg.evaluate("document.fonts.ready")
            if isinstance(y, str):  # frame on an element, so the shot follows the page when it changes
                y = pg.eval_on_selector(y, "e => Math.max(0, e.getBoundingClientRect().top + scrollY - 90)")
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(700)
            save(Image.open(io.BytesIO(pg.screenshot())), name)
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
