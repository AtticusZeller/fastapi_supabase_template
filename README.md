# FastAPI Supabase Template

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=acout_fastapi_supabase_template&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=acout_fastapi_supabase_template)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=acout_fastapi_supabase_template&metric=coverage)](https://sonarcloud.io/summary/new_code?id=acout_fastapi_supabase_template)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=acout_fastapi_supabase_template&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=acout_fastapi_supabase_template)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=acout_fastapi_supabase_template&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=acout_fastapi_supabase_template)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=acout_fastapi_supabase_template&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=acout_fastapi_supabase_template)
[![Codecov](https://codecov.io/gh/acout/fastapi_supabase_template/branch/main/graph/badge.svg)](https://codecov.io/gh/acout/fastapi_supabase_template)

Un template de projet FastAPI intégrant Supabase pour l'authentification, la base de données et le stockage de fichiers.

## Fonctionnalités

- **Authentification** avec Supabase Auth
- **Base de données** PostgreSQL via SQLModel et Supabase
- **Row Level Security (RLS)** pour la protection des données
- **Stockage de fichiers** avec Supabase Storage et policies RLS
- **Upload de fichiers** avec métadonnées en base de données
- **API RESTful** complète avec FastAPI
- **Documentation automatique** avec Swagger UI
- **Tests unitaires** complets
- **Qualité de code** avec hooks pre-commit, linting et formattage automatique
- **Analyse de code** continue avec SonarCloud
- **Couverture de code** avec Codecov

## Structure du projet

```
├── app                  # Application principale
│   ├── api              # Routes de l'API
│   ├── core             # Configuration et fonctionnalités de base
│   ├── crud             # Opérations CRUD pour la base de données
│   ├── models           # Modèles de données SQLModel
│   ├── schemas          # Schémas Pydantic
│   ├── services         # Services d'application
│   └── utils            # Utilitaires
├── tests                # Tests unitaires et d'intégration
├── alembic              # Migrations de base de données
├── docs                 # Documentation du projet et standards de code
└── supabase             # Configuration Supabase
```

## Environnement de développement

### Prérequis

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) pour la gestion des dépendances
- [pre-commit](https://pre-commit.com/) pour les hooks de pré-commit
- [Supabase CLI](https://supabase.com/docs/guides/cli) pour le développement local

### Installation rapide

Utilisez nos scripts d'installation automatique pour configurer rapidement l'environnement de développement :

**Linux/MacOS** :
```bash
# Cloner le repository
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template

# Exécuter le script d'installation
chmod +x scripts/setup-dev-environment.sh
./scripts/setup-dev-environment.sh
```

**Windows** :
```powershell
# Cloner le repository
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template

# Exécuter le script d'installation (PowerShell)
.\scripts\setup-dev-environment.ps1
```

### Installation manuelle

```bash
# Cloner le repository
git clone https://github.com/acout/fastapi_supabase_template.git
cd fastapi_supabase_template

# Installer pre-commit
pip install pre-commit
pre-commit install

# Installer les dépendances avec uv
cd backend
uv sync --all-groups --dev
```

### Python

> [uv](https://github.com/astral-sh/uv) est un gestionnaire de paquets Python ultra-rapide, écrit en Rust.

```bash
cd backend
uv sync --all-groups --dev
```

### [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

Installation de supabase-cli

```bash
# brew sur Linux https://brew.sh/
brew install supabase/tap/supabase
```

Lancement des conteneurs Docker Supabase

```bash
# à la racine du dépôt
supabase start
```

> [!NOTE]
>```bash
># Mise à jour du fichier `.env`
>bash scripts/update-env.sh
>```
> Modifiez le fichier `.env` à partir de la sortie de `supabase start` ou exécutez `supabase status` manuellement.

## Processus de développement

### Workflow de développement

1. **Créer une branche**: Pour chaque tâche, créez une branche dédiée à partir de `main`.
   ```bash
   git checkout -b feature/description-de-la-fonctionnalite
   ```

2. **Développer et tester**: Implémentez vos modifications avec les tests appropriés.

3. **Valider localement**:
   ```bash
   # Vérifier la qualité du code
   pre-commit run --all-files

   # Exécuter les tests
   cd backend
   pytest

   # Vérifier la couverture de tests sur vos changements
   ../scripts/check_test_coverage.sh
   ```

4. **Soumettre les modifications**:
   ```bash
   git add .
   git commit -m "[TICKET-ID] Description du changement"
   git push origin feature/description-de-la-fonctionnalite
   ```

5. **Créer une Pull Request**: Via GitHub, créez une PR de votre branche vers `main`.

### Standards de codage

Voir [CODING_STANDARDS.md](docs/CODING_STANDARDS.md) pour les standards de codage détaillés.

En résumé:
- Nous utilisons **Ruff** pour le linting et le formatage
- **pre-commit** pour automatiser les vérifications avant chaque commit
- Une couverture de tests minimale de **80%** est requise
- Les docstrings au format Google sont utilisées pour documenter le code

### Outils configurés

- **Ruff**: Linting et formattage
- **mypy**: Vérification de types
- **pytest**: Tests unitaires et d'intégration
- **pre-commit**: Hooks de pré-commit pour automatiser les vérifications
- **GitHub Actions**: CI/CD pour exécuter les tests et vérifier la qualité du code
- **SonarCloud**: Analyse statique du code et détection des problèmes
- **Codecov**: Suivi de la couverture de code

Pour plus de détails sur le processus de contribution, voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Utilisation de l'API de stockage

L'API de stockage permet de gérer des fichiers avec Supabase Storage. Voici les principales fonctionnalités :

### Upload de fichiers

```bash
# Upload d'une image de profil
curl -X POST "http://localhost:8000/api/v1/storage/upload/profile-picture" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "description=Ma photo de profil"

# Upload d'un document lié à un item
curl -X POST "http://localhost:8000/api/v1/storage/upload/document/ITEM_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Documentation importante"
```

### Récupération des métadonnées

```bash
# Liste des fichiers de l'utilisateur
curl -X GET "http://localhost:8000/api/v1/storage/files" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Obtenir les métadonnées d'un fichier spécifique
curl -X GET "http://localhost:8000/api/v1/storage/file/FILE_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Téléchargement de fichiers

```bash
# Obtenir une URL de téléchargement signée
curl -X GET "http://localhost:8000/api/v1/storage/file/FILE_ID/url" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Tests

### Tests avec SQLite (mock)

```bash
cd backend
# Exécuter les tests unitaires avec des mocks
python -m pytest tests/
```

### Tests avec Supabase local

```bash
cd backend
# Lancer Supabase local
supabase start
# Test de connexion à la base de données et migration
scripts/pre-start.sh
# Tests unitaires
scripts/test.sh
```

### Tests avec Supabase Cloud

Pour tester avec votre instance Supabase cloud, assurez-vous d'avoir configuré votre fichier `.env` avec les informations de connexion à votre Supabase cloud, puis exécutez :

```bash
cd backend
# Exécuter les tests avec l'instance Supabase cloud
bash scripts/cloud-test.sh
```

## Lancement de l'application

### Avec Supabase local

```bash
# À la racine du projet
supabase start

# Dans le répertoire backend
cd backend
python -m app.main
```

### Avec Supabase Cloud

```bash
cd backend
python -m app.main
```

L'application est ensuite accessible à l'adresse http://localhost:8000 et la documentation Swagger à http://localhost:8000/docs

## Docker

> [!note]
> `acout/fastapi_supabase_template` est le nom de votre image Docker, remplacez-le par le vôtre

Construction de l'image

```bash
cd backend
docker build -t acout/fastapi_supabase_template .
```

Test de l'image

```bash
bash scripts/update-env.sh
supabase start
cd backend
docker run --network host \
  --env-file ../.env \
  -it acout/fastapi_supabase_template:latest \
  bash -c "sh scripts/pre-start.sh && sh scripts/tests-start.sh"
```
