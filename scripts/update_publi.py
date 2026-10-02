# -*- coding: utf-8 -*-
"""
Met a jour la section "Articles" de publi.html depuis OpenAlex
(base bibliographique officielle, gratuite, sans blocage - remplace
 le scraping Google Scholar bloque par GitHub Actions).
Ne garde que les ARTICLES de revue (type="article" avec une revue),
exclut preprints, conferences, these, datasets.
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request

PUBLI_FILE = "publi.html"
MAILTO = "alice.cartaud@univ-lille.fr"
AUTHOR_QUERY = "raw_author_name.search:alice cartaud"

def clean(x):
    return html.unescape(re.sub(r"<[^>]+>", "", x or "")).replace("\xa0", " ").strip()

def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())

def fetch_openalex():
    q = urllib.parse.urlencode({
        "filter": f"{AUTHOR_QUERY},from_publication_date:2015-01-01",
        "per_page": 100, "mailto": MAILTO,
    })
    url = f"https://api.openalex.org/works?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": f"publi-updater ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    works = []
    for w in data.get("results", []):
        if w.get("type") != "article":
            continue
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        if not venue:
            continue
        biblio = w.get("biblio") or {}
        pages = biblio.get("first_page") or ""
        if pages and biblio.get("last_page") and biblio["last_page"] != pages:
            pages += "-" + biblio["last_page"]
        works.append({
            "title": w.get("title") or "",
            "venue": venue,
            "year": w.get("publication_year") or "",
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "authors": [(a.get("author") or {}).get("display_name", "") for a in w.get("authorships", [])],
            "volume": (w.get("biblio") or {}).get("volume") or "",
            "pages": pages,
        })
    print(f"OpenAlex: {len(works)} articles de revue")
    return works

def get_articles_section(html_src):
    m = re.search(r'(<span class="text">Articles</span>\s*</h1>\s*<ul class="listing_details">)(.*?)(</ul>)',
                  html_src, re.S)
    if not m:
        raise RuntimeError("Section 'Articles' introuvable dans publi.html")
    return m

def is_known(entry, known_items):
    t = norm_title(entry["title"])
    for item in known_items:
        if t and t in norm_title(item):
            return True
        # mot-cle canonique de la revue (sans mots vides) + meme annee
        stop = {"in", "of", "the", "de", "la", "l", "pour", "revue", "journal",
                "international", "proceedings", "special", "issue", "society", "press"}
        words = [w.lower() for w in entry["venue"].replace("'", " ").split()
                 if w.isalpha() and w.lower() not in stop]
        year = str(entry["year"])
        if words and year:
            key = words[0]
            if len(key) > 3 and key in item.lower() and re.search(r"\b" + year + r"\b", item):
                return True
    return False

def fmt_openalex_author(name):
    """'Alice Cartaud' -> 'Cartaud, A.'"""
    parts = name.rsplit(" ", 1)
    if len(parts) == 2 and parts[0]:
        fam, giv = parts[1], parts[0]
        ini = "".join(p[0] + "." for p in giv.split() if p)
        return f"{fam}, {ini}"
    return name

def _api_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"publi-updater ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

OSF_USER_ID = "fyue4"  # Alice Cartaud sur OSF

STOP_WORDS = {"the", "a", "an", "of", "in", "on", "and", "with", "to", "for",
              "from", "at", "by", "is", "are", "as", "or", "how", "when", "no"}

def _sig_words(title):
    words = []
    for w in re.findall(r"[a-z]+", title.lower()):
        if w in STOP_WORDS or len(w) <= 2:
            continue
        words.append(w[:-1] if w.endswith("s") and len(w) > 3 else w)  # stemming pluriel
    return words

def _api_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"publi-updater ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def find_materials(title):
    """Cherche un supplementary material pour l'article:
    - Zenodo: recherche par debut de titre (record d'Alice).
    - OSF: projets d'Alice Cartaud dont le titre recoupe l'article.
    Retourne [(label, url), ...] ou vide."""
    results = []
    # --- Zenodo
    try:
        phrase = " ".join(re.findall(r"[A-Za-z]+", title)[:6])
        q = urllib.parse.quote(f'metadata.title:"{phrase}"')
        d = _api_json(f"https://zenodo.org/api/records?q={q}&size=3")
        for h in d.get("hits", {}).get("hits", []):
            t = h.get("metadata", {}).get("title", "") or ""
            if norm_title(title) in norm_title(t):
                results.append(("Zenodo", h.get("links", {}).get("self_html") or f"https://zenodo.org/records/{h['id']}"))
    except Exception as e:
        print(f"WARNING Zenodo: {e}")
    # --- OSF (projets d'Alice Cartaud uniquement)
    try:
        arts = set(_sig_words(title))
        d = _api_json(f"https://api.osf.io/v2/users/{OSF_USER_ID}/nodes/?page[size]=20")
        best, best_n = None, 0
        for n in d.get("data", []):
            t = n.get("attributes", {}).get("title", "") or ""
            overlap = len(arts & set(_sig_words(t)))
            if overlap > best_n:
                best, best_n = (n.get("links", {}).get("html"), t), overlap
        if best and best_n >= 3:
            results.append(("OSF", best[0]))
    except Exception as e:
        print(f"WARNING OSF: {e}")
    seen, out = set(), []
    for label, url in results:
        if url and url not in seen:
            seen.add(url)
            out.append((label, url))
    return out

def apa_entry(e):
    authors = [fmt_openalex_author(a) for a in e["authors"] if a]
    if not authors:
        authors = ["Cartaud, A."]
    formatted = [f"<strong>{a}</strong>" if "cartaud" in a.lower() else a for a in authors]
    out = formatted[0]
    rest = formatted[1:]
    if len(rest) == 1:
        out += f", & {rest[0]}"
    elif rest:
        out += ", " + ", ".join(rest[:-1]) + ", & " + rest[-1]
    tail = ", ".join(s for s in [e["volume"], e["pages"]] if s)
    out += f" ({e['year']}). {e['title']}. <i>{e['venue']}</i>" + (f", {tail}" if tail else "") + "."
    if e["doi"]:
        out += f' doi: <a href="https://doi.org/{e["doi"]}" target="_blank">{e["doi"]}</a>'
    if e.get("materials"):
        links = ", ".join(f'<a href="{u}" target="_blank">{lbl}</a>' for lbl, u in e["materials"])
        out += (f' <span style="font-size: small;"><br>materials: {links}</span>')
    return out

def main():
    works = fetch_openalex()

    with open(PUBLI_FILE, encoding="utf-8", newline="") as f:
        src = f.read()
    m = get_articles_section(src)
    known = [clean(li) for li in re.findall(r"<li>(.*?)</li>", m.group(2), re.S)]

    new = [e for e in works if not is_known(e, known)]
    print(f"Nouveaux articles detectes: {len(new)}")

    if not new:
        open("new_articles.txt", "w").write("")
        return

    block = ""
    for e in new:
        entry = apa_entry(e)
        li = ('                            <li>\r\n'
              '                                <p class="text">\r\n'
              f'                                    {entry}\r\n'
              '                                </p>\r\n'
              '                            </li>\r\n')
        block += li
        mats = find_materials(e["title"])
        if mats:
            e["materials"] = mats
            print(f"   materials: {mats}")
        print(f"+ Ajoute: {e['title'][:70]}... ({e['doi'] or 'sans DOI'})")

    insert_at = m.end(1)
    new_src = src[:insert_at] + "\r\n" + block + src[insert_at:]
    with open(PUBLI_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(new_src)

    with open("new_articles.txt", "w", encoding="utf-8") as f:
        for e in new:
            f.write(f"- {e['title']} ({e['venue']}, {e['year']})\n")
            for lbl, url in e.get("materials", []):
                f.write(f"  materials: {lbl} - {url}\n")
    print("publi.html mis a jour.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        sys.exit(1)
