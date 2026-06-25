"""Crawler poli, thématique et concurrent de letudiant.fr (respecte robots.txt)."""
import json
import os
import time
import io
import gzip
import xml.etree.ElementTree as ET
import re
import concurrent.futures
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from . import settings

_FICHE_RE = re.compile(r"/metiers/secteur/[^/]+/[^/]+\.html")


def _robots():
    # On récupère robots.txt via requests (UA accepté par le site)
    rp = RobotFileParser()
    try:
        r = requests.get(
            f"https://{settings.CRAWL_ALLOWED_DOMAIN}/robots.txt",
            headers={"User-Agent": settings.CRAWL_USER_AGENT},
            timeout=10,
        )
        if r.status_code == 200:
            rp.parse(r.text.splitlines())
        else:
            rp.allow_all = True
    except requests.RequestException:
        rp.allow_all = True
    return rp


def _same_site(url):
    return urlparse(url).netloc == settings.CRAWL_ALLOWED_DOMAIN


def _wanted(url):
    path = urlparse(url).path
    if not url.endswith(".html"):
        return False
    if "?page=" in url or "/annuaire-" in url:
        return False
    return any(inc in path for inc in settings.CRAWL_URL_INCLUDE)


def _extract_text(soup):
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg", "button"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    lines = [ln.strip() for ln in main.get_text(separator="\n").splitlines()]
    return "\n".join(ln for ln in lines if len(ln) > 1)


def _load_sitemap_urls(sitemap_url, headers):
    try:
        r = requests.get(sitemap_url, headers=headers, timeout=20)
        if r.status_code == 200:
            with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as f:
                xml_content = f.read()
            root = ET.fromstring(xml_content)
            namespaces = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            locs = root.findall('.//s:loc', namespaces)
            return [l.text for l in locs if l.text]
    except Exception as e:
        print(f"Erreur de chargement/lecture du sitemap {sitemap_url} : {e}")
    return []


def _download_page(url, headers, rp, ua):
    if not rp.can_fetch(ua, url):
        return None
    try:
        # Politesse par thread
        time.sleep(settings.CRAWL_DELAY)
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        text = _extract_text(soup)
        if len(text) >= settings.CRAWL_MIN_TEXT:
            title = soup.title.get_text().strip() if soup.title else url
            return {"url": url, "title": title, "text": text}
    except Exception:
        pass
    return None


def crawl(seeds=None, max_pages=None, max_depth=None, verbose=True):
    """Télécharge les sitemaps et extrait/télécharge les pages d'orientation en parallèle."""
    max_pages = max_pages or settings.CRAWL_MAX_PAGES
    ua = settings.CRAWL_USER_AGENT
    headers = {"User-Agent": ua}
    rp = _robots()

    if verbose:
        print("Chargement des sitemaps XML de l'Etudiant...")
        
    sitemaps = settings.CRAWL_SITEMAPS
    all_urls = set()
    
    # Chargement en parallèle des sitemaps
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sitemaps)) as executor:
        futures = [executor.submit(_load_sitemap_urls, sm_url, headers) for sm_url in sitemaps]
        for f in concurrent.futures.as_completed(futures):
            all_urls.update(f.result())
            
    if verbose:
        print(f"Trouvé {len(all_urls)} URLs au total dans les sitemaps.")

    # Filtrage des URLs voulues
    filtered_urls = {u for u in all_urls if _same_site(u) and _wanted(u)}
    if verbose:
        print(f"Filtré {len(filtered_urls)} URLs correspondant aux thématiques (/metiers, /etudes).")

    # Séparation et ordonnancement : prioriser les fiches métiers
    fiches = []
    others = []
    for u in filtered_urls:
        if _FICHE_RE.search(u):
            fiches.append(u)
        else:
            others.append(u)
            
    # Ordonne : toutes les fiches d'abord, puis le reste
    ordered_urls = fiches + others
    urls_to_crawl = ordered_urls[:max_pages]

    if verbose:
        print(f"Démarrage du téléchargement concurrent de {len(urls_to_crawl)} pages (Fiches prioritaires : {len(fiches)})...")

    pages = []
    
    # Crawl concurrent
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CRAWL_CONCURRENCY) as executor:
        futures = {executor.submit(_download_page, url, headers, rp, ua): url for url in urls_to_crawl}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            if res:
                pages.append(res)
                if verbose and len(pages) % 50 == 0:
                    print(f"  [{len(pages):>4}] {res['url']} | {res['title'][:40]}...")
            
            # Arrêt dès qu'on a atteint la limite
            if len(pages) >= max_pages:
                # Annulation des tâches restantes
                for fut in futures:
                    fut.cancel()
                break

    if verbose:
        print(f"Crawl terminé : {len(pages)} pages valides collectées.")
    return pages


def save_corpus(pages, path=None):
    path = path or settings.CORPUS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    return path
