# Gestion des Secrets

Ce document explique comment gérer les secrets dans le project, notamment pour les tests en CI/CD.

## Principes généraux

1. **Ne jamais versionner les secrets** : Les fichiers `.env`, `.env.test`, etc. sont exclus du contrôle de version via `.gitignore`.
2. **Utiliser les secrets GitHub** : Pour le CI/CD, tous les secrets sont stockés dans GitHub Actions.
3. **Nomenclature cohérente** : Les secrets pour les tests CI ont le suffixe `_TEST`.

## Configuration locale

### Fichier `.env.test`

Créez un fichier `.env.test` à la racine du project avec les variables suivantes :

```
SUPABASE_URL=...
SUPABASE_KEY=...
POSTGRES_SERVER=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
FIRST_SUPERUSER=...
FIRST_SUPERUSER_PASSWORD=...
```

## Déploiement des secrets vers GitHub

Plusieurs méthodes sont disponibles pour déployer vos secrets vers GitHub :

### Méthode 1 : Utiliser le script shell (Dans le devcontainer)

Le moyen le plus simple avec le devcontainer :

```bash
make deploy-secrets
```

ou

```bash
./scripts/deploy-secrets.sh
```

Ce script utilise GitHub CLI pour s'authentifier et déployer les secrets.

### Méthode 2 : Utiliser directement le script Python

```bash
# Installation des dépendances
pip install python-dotenv>=1.0.0 PyGithub>=1.58.0

# Exportez votre token GitHub (ou le script vous le demandera)
export GITHUB_TOKEN=votre_token_github

# Exécution du script
python scripts/deploy_env_secrets.py
```

Le script vous demandera un token GitHub avec les permissions `repo` si la variable d'environnement `GITHUB_TOKEN` n'est pas définie.

### Méthode 3 : Manuellement via l'interface GitHub

1. Allez sur GitHub → votre dépôt → Settings → Secrets and variables → Actions
2. Cliquez sur "New repository secret"
3. Ajoutez chaque variable avec le suffixe `_TEST` (ex: `SUPABASE_URL_TEST`)

## Vérification

Après exécution, vérifiez les secrets dans votre dépôt GitHub :

1. Allez sur GitHub → votre dépôt → Settings → Secrets and variables → Actions
2. Vous devriez voir tous vos secrets avec le suffixe `_TEST`

## Utilisation dans le CI

Les secrets sont utilisés dans le workflow CI pour créer un fichier `.env.test` temporaire :

```yaml
- name: Create test environment file
  run: |
    cat > .env.test << EOF
    SUPABASE_URL=${{ secrets.SUPABASE_URL_TEST }}
    SUPABASE_KEY=${{ secrets.SUPABASE_KEY_TEST }}
    # ... autres variables
    EOF
```

## Sécurité

- Les secrets GitHub sont chiffrés et ne sont jamais exposés dans les logs.
- L'option `::add-mask::` est utilisée pour masquer les contenus sensibles.
- Les forked PR n'ont pas accès aux secrets (protection par défaut de GitHub).

## Création d'un environment de test isolé

Pour les tests CI, il est recommandé de créer un environment Supabase et une base de données PostgreSQL isolés pour éviter toute contamination des données de production.

1. Créez un project Supabase dédié aux tests
2. Configurez une base de données PostgreSQL temporaire
3. Utilisez ces identifiants dans vos secrets GitHub avec le suffixe `_TEST`
