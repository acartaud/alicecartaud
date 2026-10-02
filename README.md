# Personal website

Source of a personal academic website, hosted on GitHub Pages.

**URL: https://acartaud.github.io/alicecartaud**

The website contains:

- **Home** — research interests
- **Publications** — journal articles, preprints, PhD dissertation (`publi.html`)
- **Communications** — conference talks and posters (`comm.html`)
- **Teaching** (`educ.html`)
- **Skills** (`skills.html`)
- **Media** (`media.html`)

## Automatic publication updates

The **Articles** section of `publi.html` is updated automatically every month from bibliographic data provided by [OpenAlex](https://openalex.org).

### How it works

The workflow `.github/workflows/update-publi.yml` runs on the 3rd of each month at 7 AM (UTC):

1. `scripts/update_publi.py` queries the OpenAlex API and retrieves the author's **journal articles** (preprints, conference papers, dissertations and datasets are excluded via the OpenAlex `type` field);
2. each article missing from `publi.html` is formatted in **APA style**: full author list in publication order, author's name in bold, journal in italics, volume/pages, clickable DOI;
3. the script searches for a possible **supplementary material** on **OSF** (author's projects) and on **Zenodo** (title-based search) — a `materials:` link is added when found;
4. the entry is inserted at the top of the Articles section, committed and pushed to `main` → GitHub Pages redeploys the website;
5. a **confirmation email** lists the added articles; if the workflow fails, an alert email is sent.

### Emails

- new articles → `[website] New articles published`
- failure → `[website] ERROR publication update`

### Manual update

**Actions** tab → "Mise à jour automatique des publications" → **Run workflow**.

## Repository structure

    index.html                           home page
    publi.html                          publications
    comm.html                           communications
    educ.html                           teaching
    skills.html                         skills
    media.html                          media
    style/                               stylesheets
    files/                               images and documents
    scripts/update_publi.py             automatic update script
    .github/workflows/update-publi.yml  monthly workflow
