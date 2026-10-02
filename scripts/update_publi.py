# -*- coding: utf-8 -*-
"""
Met a jour la section "Articles" de publi.html depuis le profil Google Scholar.
- Exclut conferences/congres/workshops, prepublications, these.
- Detecte les nouveaux articles (non presents dans publi.html).
- Recupere les metadonnees (DOI, auteurs, revue) via Crossref.
- Insere l'entree au format APA existant, en tete de liste.
"""
import html
import json
import re
import sys
import time
import random
import urllib.parse
import urllib.request

SCHOLAR_ID = "mkzYFXoAAAAJ"
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en&pagesize=100"
PUBLI_FILE = "publi.html"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

EXCLUDE_VENUE = [
    "conference", "congress", "meeting", "workshop", "symposium",
    "escop", "icsp", "icps", "suppl", "université", "universite",
    "preprint", "dissertation",
]

def clean(x):
    return html.unescape(re.sub(r"<[^>]+>", "", x or "")).replace("\xa0", " ").strip()

def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", t.lower())

def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa
            last = e
            time.sleep(10 + random.uniform(0, 20))
    raise RuntimeError(f"Echec de la requete vers {url}: {last}")

def parse_scholar(content):
    s = content.decode("utf-8", errors="replace")
    if "gsc_a_tr" not in s:
        raise RuntimeError("Page Google Scholar illisible (blocage anti-robot ?)")
    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', s, re.S)
    entries = []
    for r in rows:
        title = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', r, re.S)
        metas = [clean(m) for m in re.findall(r'<div class="gs_gray">(.*?)</div>', r, re.S)]
        year = re.search(r'gsc_a_h[^>]*>(\d{4})', r)
        venue = metas[1] if len(metas) > 1 else ""
        entries.append({
            "title": clean(title.group(1)) if title else "",
            "venue": venue,
            "year": int(year.group(1)) if year else 0,
        })
    return entries

def is_article(e):
    v = e["venue"].lower()
    if not v:
        return False
    if any(k in v for k in EXCLUDE_VENUE):
        return False
    # abstract de conference publie dans une revue : pages identiques (ex: "58, 224-224")
    if re.search(r"\b(\d+)-\1\b", v):
        return False
    return True

def get_articles_section(html_src):
    m = re.search(r'(<span class="text">Articles</span>\s*</h1>\s*<ul class="listing_details">)(.*?)(</ul>)',
                  html_src, re.S)
    if not m:
        raise RuntimeError("Section 'Articles' introuvable dans publi.html")
    return m

def known_titles_in_section(section_body):
    return [clean(li) for li in re.findall(r"<li>(.*?)</li>", section_body, re.S)]

def is_known(entry, known_items):
    """Connu si le titre apparait dans un <li> existant, OU si un <li>
    mentionne la meme revue ET la meme annee (les titres peuvent differer)."""
    t = norm_title(entry["title"])
    for item in known_items:
        if t and t in norm_title(item):
            return True
        venue_words = " ".join(w for w in entry["venue"].split()[:5] if w.isalpha()).lower()
        year = str(entry["year"])
        if venue_words and len(venue_words) > 6 and year:
            if venue_words in item.lower() and re.search(r"\b" + year + r"\b", item):
                return True
    return False

def crossref_lookup(title):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 3})
    data = json.loads(fetch(f"https://api.crossref.org/works?{q}"))
    norm = norm_title(title)
    for it in data.get("message", {}).get("items", []):
        if norm_title(it.get("title", [""])[0]) == norm:
            return it
    return None

def fmt_author(a):
    fam = a.get("family", "")
    ini = "".join(p[0] + "." for p in a.get("given", "").replace("-", " ").split() if p)
    return f"{fam}, {ini}".strip()

def full_apa(cr, fallback_authors, fallback_year):
    authors = [fmt_author(a) for a in cr.get("author", [])]
    if not authors:
        authors = [fallback_authors]
    year = (cr.get("issued", {}).get("date-parts", [[None]])[0][0]) or fallback_year
    title = cr.get("title", [""])[0]
    venue = cr.get("container-title", [""])[0]
    vol = cr.get("volume", "")
    page = cr.get("page", "")
    doi = cr.get("DOI", "")
    seg = [s for s in [venue, str(vol) if vol else "", str(page) if page else ""] if s]
    out = f"<strong>{authors[0]}</strong>"
    rest = authors[1:]
    if len(rest) == 1:
        out += f", & {rest[0]}"
    elif rest:
        out += ", " + ", ".join(rest[:-1]) + ", & " + rest[-1]
    out += f" ({year}). {title}. <i>{', '.join(seg)}</i>."
    if doi:
        out += f' doi: <a href="https://doi.org/{doi}" target="_blank">{doi}</a>'
    return out

def main():
    content = fetch(SCHOLAR_URL)
    entries = parse_scholar(content)
    print(f"Scholar: {len(entries)} entrees")

    with open(PUBLI_FILE, encoding="utf-8", newline="") as f:
        src = f.read()
    m = get_articles_section(src)
    known = known_titles_in_section(m.group(2))

    articles = [e for e in entries if is_article(e)]
    print(f"Dont {len(articles)} articles (hors conferences/preprints)")

    new = [e for e in articles if not is_known(e, known)]
    print(f"Nouveaux articles detectes: {len(new)}")

    if not new:
        open("new_articles.txt", "w").write("")
        return

    block = ""
    for e in new:
        cr = crossref_lookup(e["title"])
        if cr:
            entry = full_apa(cr, "Cartaud, A.", e["year"])
            doi_info = cr.get("DOI", "pas de DOI trouve")
        else:
            print(f"WARNING Crossref: aucun resultat pour {e['title']} - entree basique")
            entry = f"<strong>Cartaud, A.</strong> et al. ({e['year']}). {e['title']}. <i>{e['venue']}</i>."
            doi_info = "pas de DOI trouve"
        li = ('                            <li>\r\n'
              '                                <p class="text">\r\n'
              f'                                    {entry}\r\n'
              '                                </p>\r\n'
              '                            </li>\r\n')
        block += li
        print(f"+ Ajoute: {e['title'][:70]}... ({doi_info})")

    insert_at = m.end(1)
    new_src = src[:insert_at] + "\r\n" + block + src[insert_at:]
    with open(PUBLI_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(new_src)

    with open("new_articles.txt", "w", encoding="utf-8") as f:
        for e in new:
            f.write(f"- {e['title']} ({e['venue']}, {e['year']})\n")
    print("publi.html mis a jour.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        sys.exit(1)
