# Site web d'Alice Cartaud

Source du site personnel d'Alice Cartaud, docteure en psychologie, post-doctorante à l'ISIR (Institut des Systèmes Intelligents et de Robotique, Sorbonne Université / CNRS / INSERM).

**URL : https://acartaud.github.io/alicecartaud/**

Le site présente :

- **Home** — parcours et thématiques de recherche : décision sociale, interactions humain-agent, traits individuels, anxiété sociale, confiance, attitude face au risque, perception de l'espace et de la menace, expressions faciales émotionnelles, réponses physiologiques
- **Publications** — articles, prépublications, thèse (`publi.html`)
- **Communications** — conférences et congrès (`comm.html`)
- **Teaching** — enseignements (`educ.html`)
- **Skills** — compétences (`skills.html`)
- **Media** — médiatisation des recherches (`media.html`)

## Mise à jour automatique des publications

La section **Articles** de `publi.html` se met à jour automatiquement chaque mois à partir des données bibliographiques d'[OpenAlex](https://openalex.org).

### Fonctionnement

Le workflow `.github/workflows/update-publi.yml` s'exécute le 3 de chaque mois à 7h (UTC) :

1. `scripts/update_publi.py` interroge l'API OpenAlex et récupère les **articles de revue** d'Alice Cartaud (prépublications, communications, thèses et jeux de données exclus via le champ `type`) ;
2. chaque article absent de `publi.html` est mis au format **APA** : auteurs complets dans l'ordre de publication, nom *Cartaud* en gras, revue en italique, volume/pages, DOI cliquable ;
3. le script cherche un éventuel **supplementary material** (matériel supplémentaire) sur **OSF** (projets d'Alice Cartaud) et sur **Zenodo** (recherche par titre) — le lien `materials:` est ajouté dans ce cas ;
4. l'entrée est insérée en tête de la section Articles, commitée et poussée sur `main` → GitHub Pages redéploie le site ;
5. un **mail de confirmation** liste les articles ajoutés ; en cas d'échec du workflow, un mail d'alerte est envoyé.

### Mails

- nouveaux articles → `[site web] Nouveaux articles publiés`
- échec → `[site web] ERREUR mise à jour des publications`

### Secrets requis (Settings → Secrets and variables → Actions)

| Secret | Valeur |
|---|---|
| `SMTP_SERVER` | serveur SMTP (ex. `smtp.univ-lille.fr`) |
| `SMTP_PORT` | port (ex. `587`) |
| `EMAIL_FROM` | adresse d'envoi |
| `EMAIL_TO` | adresse de réception |
| `EMAIL_PASSWORD` | mot de passe SMTP |

### Mise à jour manuelle

Onglet **Actions** → « Mise à jour automatique des publications » → **Run workflow**.

### Pourquoi OpenAlex et pas Google Scholar ?

Google Scholar n'a pas d'API officielle et bloque les requêtes provenant des IP de GitHub Actions (erreur 403 systématique). OpenAlex est une base bibliographique académique officielle, gratuite et sans blocage, avec un typage propre des œuvres (article / preprint / conference-paper / dissertation / dataset).

## Structure du dépôt

    index.html                           page d'accueil
    publi.html                           publications
    comm.html                            communications
    educ.html                            enseignements
    skills.html                          compétences
    media.html                           médias
    style/                               feuilles de style
    files/                               images et documents
    scripts/update_publi.py              script de mise à jour automatique
    .github/workflows/update-publi.yml   workflow mensuel
