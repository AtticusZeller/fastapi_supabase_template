# Configuration Pre-Commit

Ce document décrit les hooks pre-commit utilisés dans ce project et explique comment les configurer correctement.

## Installation de pre-commit

```bash
pip install pre-commit
pre-commit install
```

## Hooks activés

### Hooks de base

- **check-toml/yaml/json** - Vérifie la syntax des fichiers de configuration
- **pretty-format-json** - Format automatiquement les fichiers JSON
- **check-added-large-files** - Évite l'ajout de fichiers volumineux (>50MB)
- **end-of-file-fixer** - S'assure que les fichiers se terminent par une ligne vide
- **trailing-whitespace** - Supprime les escapes en fin de ligne
- **detect-private-key** - Évite la fuite de clés privées

### Checks de qualité de code

- **codespell** - Vérifie l'orthographe dans le code et les commentaires
  - Utilise `.github/codespell-ignore.txt` pour les mots légitimes
- **ruff** - Linting Python avancé (combination de flake8, isort, etc.)
  - Certaines règles sont désactivées temporairement pour faciliter le workflow
- **ruff-format** - Formattage du code Python (similaire à black)
- **mypy** - Vérification de types statiques

### Infrastructure & Sécurité

- **hadolint-docker** - Vérifie les bonnes pratiques des Dockerfiles
- **uv-lock** - Maintient le fichier de verrouillage des dépendances à jour
- **detect-secrets** - Détecte les secrets et mots de passe dans le code
  - Utilise `.secrets.baseline` pour éviter les faux positifs
- **swagger-validation** - Vérifie la validité des fichiers OpenAPI

## Désactiver temporairement un hook

Ajouter `SKIP=hook-id` avant la commande git :

```bash
SKIP=codespell git commit -m "commit message"
```

Pour ignorer tous les hooks :

```bash
SKIP=codespell,detect-secrets,hadolint-docker git commit -m "commit message"
# OU
git commit -m "commit message" --no-verify
```

## Création ou mise à jour du fichier baseline de detect-secrets

```bash
detect-secrets scan > .secrets.baseline
```

Ensuite, vérifiez manuellement les secrets détectés et ajoutez-les à la liste d'exclusion si nécessaire.

## Intégration CI/CD

Les hooks pre-commit sont également exécutés dans le pipeline CI/CD, avec correction automatique des problèmes de formatage pour les PRs.
