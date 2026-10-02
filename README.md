# Alice Cartaud's personal website

Source of Alice Cartaud's personal website, hosted on GitHub Pages.

**URL: https://acartaud.github.io/alicecartaud**

The website presents:

- **Home** — research interests: social decision making, human–agent interactions, individual traits, social anxiety, trust, risk attitude, approach/avoidance behavior, emotional facial expressions, threat perception, space perception, physiological response
- **Publications** — articles, preprints, PhD dissertation (`publi.html`)
- **Communications** — conferences (`comm.html`)
- **Teaching** (`educ.html`)
- **Skills** (`skills.html`)
- **Media** (`media.html`)

## Automatic publication updates

The **Articles** section of `publi.html` is updated automatically every month from the [OpenAlex](https://openalex.org) bibliographic database.

### How it works

The workflow `.github/workflows/update-publi.yml` runs on the 3rd of each month at 7 AM (UTC):

1. `scripts/update_publi.py` queries the OpenAlex API and retrieves Alice Cartaud's **journal articles** (preprints, conference papers, dissertations and datasets are excluded via the `type` field);
2. each article missing from `publi.html` is formatted in **APA style**: full author list in publication order, *Cartaud* in bold, journal in italics, volume/pages, clickable DOI;
3. the script searches for an associated **supplementary material** on **OSF** (Alice Cartaud's own projects) and **Zenodo** (title search) — a `materials:` link is added when found;
4. the entry is inserted at the top of the Articles section, committed and pushed to `main` → GitHub Pages redeploys the site;
5. a **confirmation email** lists the added articles; if the workflow fails, an alert email is sent.

### Emails

- new articles → `[site web] Nouveaux articles publiés`
- failure → `[site web] ERREUR mise à jour des publications`

### Required secrets (Settings → Secrets and variables → Actions)

| Secret | Value |
|---|---|
| `SMTP_SERVER` | SMTP server (e.g. `smtp.univ-lille.fr`) |
| `SMTP_PORT` | port (e.g. `587`) |
| `EMAIL_FROM` | sender address |
| `EMAIL_TO` | recipient address |
| `EMAIL_PASSWORD` | SMTP password |

### Manual update

**Actions** tab → "Mise à jour automatique des publications" → **Run workflow**.

### Why OpenAlex instead of Google Scholar?

Google Scholar has no official API and blocks requests from GitHub Actions IPs (systematic 403 error). OpenAlex is an official, free, unrestricted academic bibliographic database with clean work typing (article / preprint / conference-paper / dissertation / dataset).

## Repository structure

    index.html                           home page
    publi.html                           publications
    comm.html                            communications
    educ.html                            teaching
    skills.html                          skills
    media.html                           media
    style/                               stylesheets
    files/                               images and documents
    scripts/update_publi.py              automatic update script
    .github/workflows/update-publi.yml   monthly workflow
