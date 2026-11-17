"""Ask the questions through the real /ask/ page in Chrome and compare what it shows with tools/ask_answers.py.

    python tools/check_ask_page.py

Serves the repo root on a local port, opens /ask/ at 1280 and 390 pixels wide in both themes, and asks the
same sample as tools/check_ask.py through the page (the shareable #q= link). For every answer it reads the
sentences, the numbers, the table behind the chart, the links, the caveat and the note as rendered, and
fails on any difference from the Python answer. It also checks: a typed question that matches nothing gets no
answer; typed questions are matched to the right chip and wait to be confirmed; the Ask button works from
the keyboard; Reset clears the thread and the link; new answers reach the live region; nothing scrolls
sideways; text in the answers meets WCAG AA contrast in both themes; no console errors.
Needs Playwright and Chrome (CHROME may point at the browser binary).
"""
import http.server, json, os, socketserver, sys, threading
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
import ask_answers as AA
import check_ask as CA

ROOT = Path(__file__).resolve().parent.parent
FAIL, OK = [], [0]


def check(name, cond, detail=""):
    if cond:
        OK[0] += 1
    else:
        FAIL.append(name + (f": {detail}" if detail else ""))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


READ = """() => {
  const a = [...document.querySelectorAll('.ask-a[data-n]')].pop();
  if (!a) return null;
  const t = e => e ? e.textContent : null;
  const tb = a.querySelector('table.data');
  return {
    n: +a.getAttribute('data-n'),
    title: t(a.previousElementSibling.querySelector('.ask-qt')),
    say: [...a.querySelectorAll(':scope > .ask-say')].map(t),
    nums: [...a.querySelectorAll('.ask-nums > div')].map(d => [d.getAttribute('data-k'), t(d.querySelector('dt')), t(d.querySelector('dd'))]),
    table: tb ? {head: [...tb.querySelectorAll('thead th')].map(t), rows: [...tb.querySelectorAll('tbody tr')].map(r => [...r.children].map(t))} : null,
    points: [...a.querySelectorAll('.ask-points li')].map(t),
    src: t(a.querySelector('.ask-src')), cav: t(a.querySelector('.ask-cav')), note: t(a.querySelector('.ask-note')),
    link: [...a.querySelectorAll('.ask-links a')].map(x => [x.getAttribute('href'), t(x)]),
    chart: !!a.querySelector('figure.vz'), live: t(document.getElementById('ask-status')), hash: location.hash
  };
}"""

CONTRAST = """() => {
  const P = s => { const m = s.match(/[\\d.]+/g); if (!m) return null; let [r, g, b, a] = m.map(Number);
    if (s.startsWith('color(')) { r *= 255; g *= 255; b *= 255; }   // color-mix() comes back as color(srgb 0 to 1 ...)
    return [r, g, b, a === undefined ? 1 : a]; };
  const lin = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; };
  const L = c => .2126 * lin(c[0]) + .7152 * lin(c[1]) + .0722 * lin(c[2]);
  const over = (f, b) => [0, 1, 2].map(i => f[i] * f[3] + b[i] * (1 - f[3])).concat([1]);
  const bgOf = el => { const st = []; for (let e = el; e; e = e.parentElement) { const c = P(getComputedStyle(e).backgroundColor); if (c && c[3] > 0) { st.push(c); if (c[3] >= 1) break; } }
    let base = P(getComputedStyle(document.body).backgroundColor); for (let i = st.length - 1; i >= 0; i--) base = over(st[i], base); return base; };
  const bad = [];
  for (const el of document.querySelectorAll('.ask-layout *, .ask-head *')) {
    if (el.closest('.vz-plot, .bars, .vz-dots, .vz-split, details:not([open]), [hidden], noscript, option')) continue;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.visibility === 'hidden' || cs.display === 'none' || !r.width) continue;
    const bg = bgOf(el), fg = over(P(cs.color), bg), a = L(fg), b = L(bg), cr = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    const px = parseFloat(cs.fontSize), need = px >= 24 || (+cs.fontWeight >= 700 && px >= 18.66) ? 3 : 4.5;
    if (cr < need) bad.push(el.className + ' "' + el.textContent.trim().slice(0, 40) + '" ' + cr.toFixed(2));
  }
  return bad;
}"""


def expected(D, B, q, s):
    o = AA.answer(D, B, q, s)
    pts = []
    for quotes, href, label, _ in (o["points"] or []):
        pts.append((f"{quotes[0]}: {' '.join(quotes[1:])}" if len(quotes) > 1 else quotes[0]) + " " + label)
    return dict(title=o["title"], say=o["say"], nums=o["nums"], table=o["table"], points=pts, src=("Source " + o["src"]) if o["src"] else None,
                cav=B["caveat"] if o["cav"] else None, note=o["note"] or None, link=o["link"], chart=bool(o["chart"]),
                hash="#q=" + q + "".join(f"&{k}={v}" for k, v in o["slots"].items()))


def main():
    D, B = CA.load()
    C = CA.sample(D, B)
    srv = socketserver.TCPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}/ask/"
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ["CHROME"]) if os.environ.get("CHROME") else p.chromium.launch(channel="chrome")
        for width, theme, every in [(1280, "dark", True), (390, "light", True), (1280, "light", False), (390, "dark", False)]:
            ctx = b.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
            ctx.add_init_script(f"try{{localStorage.setItem('mp-theme','{theme}')}}catch(e){{}}")
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(base, wait_until="networkidle")
            pg.wait_for_selector("html[data-ask=ready]")
            tag = f"{width} {theme}"
            check(f"{tag}: every question has a chip", pg.locator("#ask-bank [data-q]").count() == len(B["questions"]))
            cases = C if every else C[::9]
            for label, q, s in cases:
                before = pg.evaluate(READ)
                n0 = before["n"] if before else 0
                pg.evaluate("h => { location.hash = h; }", "#q=" + q + "".join(f"&{k}={v}" for k, v in s.items()))
                pg.wait_for_function(f"() => {{ const a = [...document.querySelectorAll('.ask-a[data-n]')].pop(); return a && +a.getAttribute('data-n') > {n0}; }}")
                got, want = pg.evaluate(READ), expected(D, B, q, s)
                diff = [k for k in want if got.get(k) != want[k]]
                check(f"{tag}: page shows the Python answer for {q} {s} ({label})", not diff,
                      "; ".join(f"{k}: page {got.get(k)!r} / python {want[k]!r}" for k in diff)[:700])
                check(f"{tag}: answer reaches the live region ({q})", got["live"] == " ".join(want["say"]))
            sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
            check(f"{tag}: nothing scrolls sideways with answers on the page", sw <= width, f"{sw}px")
            pg.evaluate("document.querySelectorAll('details.vz-tab').forEach(d => d.open = true)")
            bad = pg.evaluate(CONTRAST)
            check(f"{tag}: text in the answers meets WCAG AA contrast", not bad, bad[:6])

            # typed questions
            pg.fill("#ask-text", "zzzz qqqq")
            pg.press("#ask-text", "Enter")
            last = pg.locator(".ask-a").last
            check(f"{tag}: typed text that matches nothing gets no answer", "None of the questions here matches that" in last.text_content()
                  and last.locator(".ask-nums").count() == 0)
            for text, q, want in [("How did CIC do on medical in 2024?", "ins-class-year", dict(ins="cic_general", cls="medical", yr="2024")),
                                  ("motor loss ratio each year", "motor-lr", {}),
                                  ("Which insurers grew fastest in 2023", "growth", dict(yr="2023")),
                                  ("has she worked with M-Pesa", "about-mpesa", {}),
                                  ("mpesa experience", "about-mpesa", {}),
                                  ("can she extract data from messy PDFs", "about-pdfs", {}),
                                  ("IBNR experience", "about-done", dict(topic="ibnr")),
                                  ("has she done IFRS 17 work", "about-done", dict(topic="ifrs17"))]:
                pg.fill("#ask-text", text)
                pg.press("#ask-text", "Enter")
                dym = pg.locator(".ask-dym").last
                chip = dym.locator("[data-q]").first
                slots = {e.get_attribute("data-slot"): e.input_value() for e in chip.locator("select").all()}
                check(f"{tag}: '{text}' is matched to {q} {want}", chip.get_attribute("data-q") == q and slots == want, f"{chip.get_attribute('data-q')} {slots}")
                check(f"{tag}: '{text}' waits to be confirmed", dym.locator(".ask-nums").count() == 0)
            n0 = pg.evaluate(READ)["n"]
            dym.locator("button").first.click()
            got = pg.evaluate(READ)
            check(f"{tag}: confirming a matched question answers it", got["n"] == n0 + 1 and got["say"] == expected(D, B, "about-done", dict(topic="ifrs17"))["say"])

            # topics: tabs by click and by arrow key
            pg.locator("#ask-bank .ask-tab").nth(1).click()
            check(f"{tag}: a topic tab shows its questions", pg.locator("#ask-panel-insurer").is_visible() and not pg.locator("#ask-panel-market").is_visible())
            pg.keyboard.press("ArrowRight")
            check(f"{tag}: arrow keys move between topics", pg.locator("#ask-panel-reinsurer").is_visible()
                  and pg.evaluate("document.activeElement.id") == "ask-tab-reinsurer")

            # the keyboard: a question pill asked with Enter
            n0 = pg.evaluate(READ)["n"]
            pg.locator("#ask-panel-reinsurer .ask-pill").first.focus()
            pg.keyboard.press("Enter")
            pg.wait_for_function(f"() => +[...document.querySelectorAll('.ask-a[data-n]')].pop().getAttribute('data-n') > {n0}")
            check(f"{tag}: a question pill works from the keyboard", pg.evaluate(READ)["title"] == AA.title(D, B, "scorecard", AA.defaults(D, B, "scorecard")))

            # change the question, then a follow-up
            last = pg.locator(".ask-a[data-n]").last
            yrs = [o.get_attribute("value") for o in last.locator(".ask-change select[data-slot=yr] option").all()]
            last.locator(".ask-change select[data-slot=yr]").select_option(yrs[0])
            n0 = pg.evaluate(READ)["n"]
            last.locator(".ask-change .ask-go").click()
            pg.wait_for_function(f"() => +[...document.querySelectorAll('.ask-a[data-n]')].pop().getAttribute('data-n') > {n0}")
            s = dict(AA.defaults(D, B, "scorecard"), yr=yrs[0])
            check(f"{tag}: changing the year asks it again", pg.evaluate(READ)["say"] == AA.answer(D, B, "scorecard", s)["say"])
            fp = pg.locator(".ask-a[data-n]").last.locator(".ask-follow").first
            fq, fs = fp.get_attribute("data-q"), json.loads(fp.get_attribute("data-s"))
            n0 = pg.evaluate(READ)["n"]
            fp.click()
            pg.wait_for_function(f"() => +[...document.querySelectorAll('.ask-a[data-n]')].pop().getAttribute('data-n') > {n0}")
            check(f"{tag}: an Ask next pill asks its question", pg.evaluate(READ)["say"] == AA.answer(D, B, fq, fs)["say"], f"{fq} {fs}")

            pg.locator("#ask-reset").click()
            check(f"{tag}: Clear empties the thread and the link", pg.locator("#ask-thread .ask-msg").count() == 0 and pg.evaluate("location.hash") == ""
                  and pg.locator("#ask-welcome").is_visible())
            check(f"{tag}: no console errors", not errs, errs[:3])
            ctx.close()
        b.close()
    srv.shutdown()
    print(f"{OK[0]} checks passed.")
    if FAIL:
        print(f"{len(FAIL)} failed:")
        for f in FAIL[:60]:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
