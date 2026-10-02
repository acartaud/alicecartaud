# Mise à jour automatique des publications

Ce dépôt contient le site web personnel d'Alice Cartaud, hébergé sur GitHub Pages.
La section **Articles** de `publi.html` se met à jour automatiquement chaque mois
à partir des données bibliographiques d'[OpenAlex](https://openalex.org).

## Comment ça marche

Un workflow GitHub Actions (`.github/workflows/update-publi.yml`) s'exécute le 3 de chaque mois à 7h (UTC) :

1. `scripts/update_publi.py` interroge l'API OpenAlex pour récupérer les **articles de revue** (uniquement) publiés par Alice Cartaud ;
2. les prépublications, communications de conférence, thèses et jeux de données sont **exclus** (champ `type` d'OpenAlex) ;
3. chaque article absent de `publi.html` est mis au format **APA** (auteurs complets dans l'ordre, nom *Cartaud* en gras, revue en italique, volume/pages, DOI cliquable) et **inséré en tête de la section Articles** ;
4. le fichier modifié est **commité et poussé** sur `main` → GitHub Pages redéploie le site ;
5. un **mail de confirmation** est envoyé avec la liste des articles ajoutés.

## Mails

- Nouveaux articles détectés → `[site web] Nouveaux articles publiés`
- Échec du workflow (par ex. API indisponible) → `[site web] ERREUR mise à jour des publications`

## Secrets requis (Settings → Secrets and variables → Actions)

| Secret | Valeur |
|---|---|
| `SMTP_SERVER` | serveur SMTP (ex. `smtp.univ-lille.fr`) |
| `SMTP_PORT` | port (ex. `587`) |
| `EMAIL_FROM` | adresse d'envoi |
| `EMAIL_TO` | adresse de réception |
| `EMAIL_PASSWORD` | mot de passe SMTP |

## Déclencher une mise à jour manuelle

Onglet **Actions** → « Mise à jour automatique des publications » → **Run workflow**.

## Pourquoi OpenAlex et pas Google Scholar ?

Google Scholar n'a pas d'API officielle et bloque les requêtes provenant des IP de GitHub Actions (erreur 403 systématique). OpenAlex est une base bibliographique académique **officielle, gratuite et sans blocage**, avec un typage propre des œuvres (article / preprint / conference-paper / dissertation / dataset) qui garantit que seuls les articles de revue sont ajoutés.

## Structure des fichiers concernés

    publi.html                          page Publications du site
    scripts/update_publi.py             script de mise à jour
    .github/workflows/update-publi.yml  workflow mensuel
