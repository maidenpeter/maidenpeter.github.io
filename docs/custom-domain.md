# Moving the site to marionpeter.nuruops.com

Not live yet. Do these in order; each step can be checked before the next.

## 1. Verify nuruops.com with GitHub

This stops anyone else pointing a GitHub Pages site at the domain.

1. GitHub, your profile picture, Settings, Pages (under "Code, planning, and automation"), Add a domain.
2. Enter `nuruops.com`. GitHub shows a TXT record: a name like `_github-pages-challenge-maidenpeter.nuruops.com` and a value.
3. Cloudflare, nuruops.com, DNS, Records, Add record: type TXT, name `_github-pages-challenge-maidenpeter`, content the value GitHub gave, TTL Auto.
4. Back in GitHub, Verify. DNS can take a few minutes to an hour.

## 2. Point the subdomain at GitHub Pages

1. Cloudflare, DNS, Add record: type CNAME, name `marionpeter`, target `maidenpeter.github.io`.
2. Set Proxy status to DNS only (grey cloud). GitHub has to see the CNAME directly to issue the HTTPS certificate. You can switch the proxy on later if you set Cloudflare SSL to Full, but there is no need to.
3. Leave the existing MX records (Zoho mail) alone; they are separate.

Check: `nslookup marionpeter.nuruops.com` should answer with GitHub's addresses via `maidenpeter.github.io`.

## 3. Tell the repository

1. GitHub, maidenpeter/maidenpeter.github.io, Settings, Pages, Custom domain: `marionpeter.nuruops.com`, Save.
2. GitHub commits a `CNAME` file to `main` when you save. Run `git pull` before your next push so your local copy has it.
3. Wait for the DNS check to pass, then tick Enforce HTTPS. The certificate can take up to a day.

## 4. Update the site's own address

1. In `tools/build.py`, set `BASE = "https://marionpeter.nuruops.com"`.
2. `python tools/build.py`, then commit and push. This updates canonical links, Open Graph URLs, the share image URL and the sitemap.

## What happens to old links

Once the user site has a custom domain, GitHub serves the project sites under it too: `maidenpeter.github.io/ira-kenya-insurance/...` redirects to `marionpeter.nuruops.com/ira-kenya-insurance/...`. Links already shared on LinkedIn keep working through the redirect.

If you remove the custom domain later, delete the `CNAME` file in the repo and the CNAME record in Cloudflare.
