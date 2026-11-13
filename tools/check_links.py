"""Check every link and asset reference in the built site.

    python tools/check_links.py              # internal links, assets and #anchors
    python tools/check_links.py --external   # also request every external URL once

Internal links are resolved against the repo root the way GitHub Pages serves it
(/path/ -> path/index.html). Anchors must exist as an id on the target page.
"""
import argparse, sys, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urldefrag

ROOT = Path(__file__).resolve().parent.parent
BASES = ("https://maidenpeter.github.io", "https://marionpeter.nuruops.com")
# Pages served from the analysis repos, not this one: checked as external URLs.
OTHER_REPOS = ("/ira-kenya-data/", "/ira-kenya-insurance/", "/ira-kenya-reinsurance/")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k) and not (tag == "link" and a.get("rel") in ("preconnect",)):
                self.refs.append(a[k])
        if tag == "meta" and a.get("property") in ("og:image", "og:url"):
            self.refs.append(a["content"])


def parse(p):
    x = Links()
    x.feed(p.read_text(encoding="utf-8"))
    return x


def target(path):
    p = ROOT / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--external", action="store_true")
    a = ap.parse_args()
    pages = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "tools" not in p.parts]
    parsed = {p: parse(p) for p in pages}
    bad, external = [], set()
    for page, x in parsed.items():
        rel = page.relative_to(ROOT).as_posix()
        for ref in x.refs:
            if ref.startswith(("mailto:", "tel:", "data:")):
                continue
            url, frag = urldefrag(ref)
            for b in BASES:
                if url.startswith(b):
                    url = url[len(b):] or "/"
            if url.startswith(("http://", "https://")) or url.startswith(OTHER_REPOS):
                external.add(url if url.startswith("http") else BASES[0] + url)
                continue
            if url == "":
                t = page
            elif url.startswith("/"):
                t = target(url)
            else:
                t = target((page.parent / url).relative_to(ROOT).as_posix() + ("/" if url.endswith("/") else ""))
            if not t.exists():
                bad.append(f"{rel}: {ref} -> missing {t.relative_to(ROOT).as_posix()}")
                continue
            if frag and t.suffix == ".html" and frag not in parsed.get(t, parse(t)).ids:
                bad.append(f"{rel}: {ref} -> no id '{frag}'")
    print(f"{len(pages)} pages, {sum(len(x.refs) for x in parsed.values())} references, {len(external)} distinct external URLs.")
    if a.external:
        for u in sorted(external):
            if urlparse(u).netloc in ("fonts.googleapis.com", "fonts.gstatic.com"):
                continue
            code = fetch(u)
            note = "" if code in (200, 999) else "  <- check"
            if code == 999:
                note = "  (LinkedIn refuses automated requests; open it by hand)"
            print(f"  {code}  {u}{note}")
            if code not in (200, 999):
                bad.append(f"external {u} returned {code}")
    if bad:
        print(f"{len(bad)} broken:")
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print("No broken internal links, assets or anchors." + (" External links answered." if a.external else ""))


def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (link check)"})
    for method in ("HEAD", "GET"):
        req.method = method
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405):
                return e.code
        except Exception as e:
            return f"error {type(e).__name__}"
    return None


if __name__ == "__main__":
    main()
