"""Screenshot every page at 1280 and 390 pixels wide, in light and dark, and flag sideways scrolling.

    python tools/screenshots.py OUTPUT_DIR

Serves the repo root on a local port the way GitHub Pages does, opens each page in the
installed Chrome, and reports any page wider than its viewport, any failed request to this
site and any console error. Screenshots go to OUTPUT_DIR, outside the repo.
"""
import http.server, os, socketserver, sys, threading
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["/", "/kenya-insurance/", "/about/", "/work/dealer-revenue/", "/work/ifrs17-measurement/",
         "/work/valuation-adequacy/", "/no-such-page/"]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_error(self, code, message=None, explain=None):
        if code == 404:  # serve 404.html the way GitHub Pages does
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)


def local_fonts(ctx, folder):
    """Offline machines: serve the two typefaces from local woff2 files (for example the
    @fontsource npm packages) instead of Google Fonts. FONTS_DIR holds the .woff2 files."""
    faces = [("EB Garamond", "eb-garamond", w, st) for w in (400, 500, 600) for st in ("normal", "italic")]
    faces += [("IBM Plex Sans Condensed", "ibm-plex-sans-condensed", w, "normal") for w in (400, 500, 600)]
    css = "".join(f"@font-face{{font-family:'{f}';font-style:{st};font-weight:{w};font-display:swap;"
                  f"src:url(https://fonts.gstatic.com/local/{slug}-latin-{w}-{st}.woff2) format('woff2')}}"
                  for f, slug, w, st in faces)
    ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=css))
    ctx.route("https://fonts.gstatic.com/local/**", lambda r: r.fulfill(
        status=200, content_type="font/woff2", body=(folder / r.request.url.rsplit("/", 1)[1]).read_bytes()))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("screenshots")
    out.mkdir(parents=True, exist_ok=True)
    srv = socketserver.TCPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    problems = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome") if not os.environ.get("CHROME") else p.chromium.launch(executable_path=os.environ["CHROME"])
        for width in (1280, 390):
            for scheme in ("light", "dark"):
                ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme,
                                    device_scale_factor=1)
                # the site defaults to the ink (dark) theme; "light" means the paper theme
                ctx.add_init_script(f"try{{localStorage.setItem('mp-theme','{scheme}')}}catch(e){{}}")
                if os.environ.get("FONTS_DIR"):
                    local_fonts(ctx, Path(os.environ["FONTS_DIR"]))
                for path in PAGES:
                    pg = ctx.new_page()
                    errs = []
                    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                    pg.on("requestfailed", lambda r: errs.append("failed " + r.url))
                    pg.on("response", lambda r: errs.append(f"{r.status} {r.url}")
                          if r.status >= 400 and "127.0.0.1" in r.url and "no-such-page" not in r.url else None)
                    pg.goto(f"http://127.0.0.1:{port}{path}", wait_until="networkidle")
                    pg.evaluate("document.fonts.ready")
                    # scroll through so lazy images load, then return to the top
                    pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) {
                        window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); }""")
                    pg.wait_for_load_state("networkidle")
                    pg.wait_for_timeout(2200)  # let the triangle finish filling in
                    sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                    name = (path.strip("/").replace("/", "_") or "home") + f"_{width}_{scheme}.png"
                    pg.screenshot(path=str(out / name), full_page=True)
                    if sw > width:
                        problems.append(f"{path} at {width}px {scheme}: page is {sw}px wide")
                    for e in errs:
                        if path == "/no-such-page/" and "404" in e:
                            continue  # the 404 test page reports its own status, as intended
                        problems.append(f"{path} at {width}px {scheme}: {e}")
                    pg.close()
                ctx.close()
        b.close()
    srv.shutdown()
    print(f"{len(PAGES) * 4} screenshots in {out}")
    if problems:
        print(f"{len(problems)} problems:")
        for x in sorted(set(problems)):
            print("  " + x)
        sys.exit(1)
    print("No sideways scrolling, failed requests or console errors.")


if __name__ == "__main__":
    main()
