# Guide de contribution

## Table des matières

- [Introduction](#introduction)
- [Environment de développement](#environnement-de-développement)
- [Workflow de développement](#workflow-de-développement)
- [Standards de codage](#standards-de-codage)
- [Tests](#tests)
- [Revue de code](#revue-de-code)
- [Gestion des branches](#gestion-des-branches)
- [Pull Requests](#pull-requests)

## Introduction

Bienvenue dans le guide de contribution d'Insperio Labs! Ce document a pour but de fournir toutes les directives nécessaires pour contribuer efficacement à ce project.

## Environment de développement

### Prérequis

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) pour la gestion des dépendances
- [pre-commit](https://pre-commit.com/) pour les hooks de pré-commit
- [Supabase CLI](https://supabase.com/docs/guides/cli) pour le développement local

### Installation

1. **Cloner le dépôt**:
   ```bash
   git clone https://github.com/acout/fastapi_supabase_template.git
   cd fastapi_supabase_template
   ```

2. **Configurer l'environnement**:
   ```bash
   # Installer uv si ce n'est pas déjà fait
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Installer les dépendances
   cd backend
   uv sync
   ```

3. **Installer les hooks pre-commit**:
   ```bash
   pre-commit install
   ```

## Workflow de développement

1. **Créer une branche**: Pour chaque tâche, créez une branche dédiée à partir de `main`.
   ```bash
   git checkout -b feature/ticket-description
   ```

2. **Développer et tester**: Implémentez vos modifications avec les tests appropriés.

3. **Valider localement**:
   ```bash
   # Exécuter les tests
   cd backend
   pytest

   # Vérifier la qualité du code
   pre-commit run --all-files
   ```

4. **Soumettre les modifications**:
   ```bash
   git add .
   git commit -m "[TICKET-ID] Description du changement"
   git push origin feature/ticket-description
   ```

5. **Créer une Pull Request**: Via GitHub, créez une PR de votre branche vers `main`.

## Standards de codage

Nous suivons les standards PEP 8 avec quelques modifications, appliqués automatiquement avec Ruff:

### Principes généraux

- **Lisibilité**: Le code doit être facile à lire et à comprendre
- **Simplicité**: Préférez le code simple et direct aux solutions complexes
- **Commentaires**: Commentez le code lorsque nécessaire, mais privilégiez du code auto-explicatif
- **Docstrings**: Utilisez des docstrings pour les modules, classes, et functions publiques

### Style de code

- **Indentation**: 4 escapes
- **Longueur de ligne**: Limitée à 88 caractères (standard Black)
- **Nommage**:
  - Modules: `snake_case`
  - Classes: `PascalCase`
  - Functions/méthodes: `snake_case`
  - Variables: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`
- **Type hints**: Utilisez des annotations de type pour toutes les functions et méthodes

### Structure des imports

Les imports doivent être groupés dans l'ordre suivant, avec une ligne vide entre chaque groupe:
1. Imports de la bibliothèque standard
2. Imports de bibliothèques tierces
3. Imports depuis d'autres modules du project

## Tests

Chaque fonctionnalité doit être accompagnée de tests:

- **Tests unitaires**: Pour tester des functions/classes individuelles
- **Tests d'intégration**: Pour tester l'interaction entre différents composants
- **Tests API**: Pour tester les endpoints FastAPI

### Exécution des tests:

```bash
# Tous les tests
cd backend
pytest

# Tests spécifiques
pytest tests/path/to/test_file.py

# Avec couverture de code
pytest --cov=app
```

## Revue de code

Lors de la revue de code, nous nous concentrons sur:

1. **Fonctionnalité**: Le code fait-il ce qu'il est censé faire?
2. **Qualité**: Le code est-il bien structuré, lisible et maintenable?
3. **Tests**: Les tests sont-ils suffisants et pertinents?
4. **Documentation**: La documentation est-elle claire et complète?

## Gestion des branches

- **main**: Branche principale, toujours déployable
- **feature/xxx**: Pour les nouvelles fonctionnalités
- **fix/xxx**: Pour les corrections de bugs
- **refactor/xxx**: Pour les refactorisations
- **docs/xxx**: Pour les mises à jour de documentation

## Pull Requests

Une bonne PR doit:

1. **Avoir un titre clair**: Commençant par le numéro du ticket (ex: `[ENG-123] Ajouter l'authentification par OAuth`)
2. **Contenir une description**: Expliquant le changement et comment le tester
3. **Être de taille raisonnable**: Idéalement moins de 500 lignes de code modifiées
4. **Passer tous les tests**: Locaux et CI
5. **Respecter les standards de code**: Validés par les hooks pre-commit
