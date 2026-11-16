"""Check every link and asset reference in the built site.

    python tools/check_links.py              # internal links, assets and #anchors
    python tools/check_links.py --external   # also request every external URL once
    python tools/check_links.py --repos ..   # also check links into, and inside, the three Kenya repos

Internal links are resolved against the repo root the way GitHub Pages serves it
(/path/ -> path/index.html). Anchors must exist as an id on the target page.
Without --repos, pages served from the analysis repos are treated as external URLs (CI has
only this repo). With --repos, /ira-kenya-*/ paths are resolved in the sibling repositories,
and their index pages and analysis pages are crawled as well.
"""
import argparse, sys, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urldefrag

ROOT = Path(__file__).resolve().parent.parent
BASES = ("https://maidenpeter.github.io", "https://marionpeter.nuruops.com")
# Pages served from the analysis repos, not this one.
OTHER_REPOS = ("/ira-kenya-data/", "/ira-kenya-insurance/", "/ira-kenya-reinsurance/")
REPO_PAGES = ("index.html", "page/*.html", "explorer/*.html")


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


def resolve(url, page, repos):
    """The file a reference points at, or None when it is outside what can be checked here."""
    if url == "":
        return page
    if url.startswith("/"):
        p = None
        for r in OTHER_REPOS:
            if url.startswith(r):
                if not repos:
                    return None
                p = repos / r.strip("/") / url[len(r):]
        if p is None:
            p = ROOT / url.lstrip("/")
    else:
        p = page.parent / url
    if url.endswith("/") or p.is_dir():
        p = p / "index.html"
    return p.resolve()


def show(p):
    for base in (ROOT, ROOT.parent):
        try:
            return p.relative_to(base).as_posix()
        except ValueError:
            pass
    return str(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--repos", help="folder holding the ira-kenya-* repositories")
    a = ap.parse_args()
    repos = Path(a.repos).resolve() if a.repos else None
    pages = [p.resolve() for p in ROOT.rglob("*.html") if ".git" not in p.parts and "tools" not in p.parts]
    if repos:
        for r in OTHER_REPOS:
            for pattern in REPO_PAGES:
                pages += [p.resolve() for p in (repos / r.strip("/")).glob(pattern) if "template" not in p.name]
    parsed = {p: parse(p) for p in pages}
    bad, external = [], set()
    for page, x in parsed.items():
        for ref in x.refs:
            if ref.startswith(("mailto:", "tel:", "data:")):
                continue
            url, frag = urldefrag(ref)
            for b in BASES:
                if url.startswith(b):
                    url = url[len(b):] or "/"
            if url.startswith(("http://", "https://")):
                external.add(url)
                continue
            t = resolve(url, page, repos)
            if t is None:
                external.add(BASES[0] + url)
                continue
            if not t.exists():
                bad.append(f"{show(page)}: {ref} -> missing {show(t)}")
                continue
            # /ask/#q=... is a question for the Ask page's script, not an anchor; check_ask.py checks those
            if frag and t.suffix == ".html" and not (frag.startswith("q=") and t == (ROOT / "ask" / "index.html").resolve()):
                ids = parsed[t].ids if t in parsed else parse(t).ids
                if frag not in ids:
                    bad.append(f"{show(page)}: {ref} -> no id '{frag}'")
    print(f"{len(pages)} pages, {sum(len(x.refs) for x in parsed.values())} references, {len(external)} distinct external URLs.")
    if a.external:
        for u in sorted(external):
            if urlparse(u).netloc in ("fonts.googleapis.com", "fonts.gstatic.com"):
                continue
            code = fetch(u)
            # a sleeping app answers 202 (starting) or a redirect while it wakes; both mean the address is live
            live = isinstance(code, int) and (200 <= code < 400 or code == 999)
            note = "" if live else "  <- check"
            if code == 999:
                note = "  (LinkedIn refuses automated requests; open it by hand)"
            print(f"  {code}  {u}{note}")
            if not live:
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
