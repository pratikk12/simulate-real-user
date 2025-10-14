# parse_sitemap.py
"""
Parse HTML or XML sitemaps (recursive) and produce a deduplicated file all_urls.txt

Outputs:
    all_urls.txt  -- one URL per line (absolute URLs only)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

MAX_RETRIES = 2
TIMEOUT = 15

def fetch_text(url):
    tries = 0
    while tries <= MAX_RETRIES:
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
            r.raise_for_status()
            return r.text
        except Exception:
            tries += 1
            time.sleep(1)
    return None

def extract_links_from_html(text, base_domain):
    soup = BeautifulSoup(text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a['href'].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        links.add(href)
    abs_links = [l for l in links if l.startswith("http")]
    if base_domain:
        abs_links = [l for l in abs_links if urlparse(l).netloc.endswith(base_domain)]
    return abs_links

def extract_links_from_xml(text, base_domain):
    soup = BeautifulSoup(text, "xml")
    locs = soup.find_all("loc")
    links = []
    for l in locs:
        if l.string:
            links.append(l.string.strip())
    if base_domain:
        links = [l for l in links if urlparse(l).netloc.endswith(base_domain)]
    return links

def collect_recursive(seed_url, base_domain=None, visited_sitemaps=None):
    if visited_sitemaps is None:
        visited_sitemaps = set()

    to_visit = [seed_url]
    collected_urls = []
    while to_visit:
        s = to_visit.pop(0)
        if s in visited_sitemaps:
            continue
        visited_sitemaps.add(s)
        print(f"Fetching sitemap: {s}")
        text = fetch_text(s)
        if not text:
            print(f"  -> failed to fetch {s}")
            continue

        # detect XML vs HTML
        if text.lstrip().startswith("<?xml") or "<urlset" in text or "<sitemapindex" in text:
            sub_urls = extract_links_from_xml(text, base_domain)
            print(f"  -> XML sitemap: found {len(sub_urls)} urls/locs")
            soup = BeautifulSoup(text, "xml")
            sitemap_tags = soup.find_all("sitemap")
            for sm in sitemap_tags:
                loc = sm.find("loc")
                if loc and loc.string:
                    sub = loc.string.strip()
                    if sub not in visited_sitemaps:
                        to_visit.append(sub)
            for u in sub_urls:
                if u not in collected_urls:
                    collected_urls.append(u)
        else:
            html_links = extract_links_from_html(text, base_domain)
            print(f"  -> HTML sitemap: found {len(html_links)} absolute links")
            for link in html_links:
                if 'sitemap' in link and link not in visited_sitemaps and link not in to_visit:
                    to_visit.append(link)
                else:
                    if link not in collected_urls:
                        collected_urls.append(link)

    return collected_urls

# -------------------------
# Hardcoded run (no CLI args needed)
# -------------------------
if __name__ == "__main__":
    seed = "https://entechonline.com/sitemap.html"   # hardcoded default
    base_domain = "entechonline.com"

    urls = collect_recursive(seed, base_domain=base_domain)

    print(f"\nCollected {len(urls)} unique URLs. Writing to all_urls.txt")
    with open("all_urls.txt", "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u.strip() + "\n")

    print("Done. all_urls.txt created.")
