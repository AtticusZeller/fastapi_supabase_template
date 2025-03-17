# Standards de codage

Ce document définit les standards de codage pour le project Insperio Labs. Ces standards sont appliqués automatiquement via les outils de linting et de formatage configurés dans le project.

## Table des matières

- [Principes généraux](#principes-généraux)
- [Style de code Python](#style-de-code-python)
- [Documentation](#documentation)
- [Tests](#tests)
- [Sécurité](#sécurité)
- [Outils d'application automatique](#outils-dapplication-automatique)

## Principes généraux

### Lisibilité et maintenabilité

- Préférez la lisibilité à la concision ou la performance, sauf cas justifiés.
- Écrivez du code qui peut être facilement compris par d'autres développeurs.
- Évitez les constructions trop complexes ou obscures.

### Simplicité

- Suivez le principe KISS (Keep It Simple, Stupid).
- Évitez la sur-ingénierie.
- Décomposez les problèmes complexes en composants plus simples.

### Cohérence

- Suivez les conventions existantes du project.
- Soyez cohérent dans le nommage, la structure et le style.

## Style de code Python

### Formatage

- Nous utilisons **Ruff** comme formateur de code, configuré pour suivre un style proche de Black.
- Indentation: 4 escapes (pas de tabulations).
- Longueur maximale de ligne: 88 caractères.
- Utilisez des lignes vides pour séparer les sections logiques du code.

### Conventions de nommage

- **Classes**: `PascalCase` (ex: `UserProfile`, `DatabaseManager`)
- **Functions, méthodes, variables**: `snake_case` (ex: `get_user_data`, `db_connection`)
- **Constantes**: `UPPER_SNAKE_CASE` (ex: `MAX_RETRY_COUNT`, `API_VERSION`)
- **Modules/packages**: `snake_case` (ex: `user_authentication`, `data_models`)
- **Arguments de function et variables locales**: `snake_case`
- **Variables privées et méthodes**: commencent par `_` (ex: `_internal_cache`)

### Imports

- Organisez les imports par groupes:
  1. Bibliothèque standard Python
  2. Bibliothèques tierces
  3. Imports du project
- Dans chaque groupe, les imports doivent être par ordre alphabétique.
- Préférez les imports absolus aux imports relatifs.

Example:

```python
# Bibliothèque standard
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Union

# Bibliothèques tierces
import fastapi
from pydantic import BaseModel, Field
from sqlmodel import select, Session

# Imports du project
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
```

### Typing

- Utilisez des annotations de type pour toutes les functions et méthodes.
- Utilisez `Optional` pour les paramètres qui peuvent être `None`.
- Utilisez des types génériques (List, Dict, etc.) à partir du module `typing`.

Example:

```python
from typing import List, Optional, Dict

def get_user_by_id(user_id: int) -> Optional[User]:
    ...

def create_users(user_data: List[Dict[str, any]]) -> List[User]:
    ...
```

### Design patterns et structure

- Nous suivons l'architecture en couches de FastAPI:
  - **Routes/Endpoints**: Définition des routes API
  - **Services**: Logique métier
  - **CRUD**: Opérations de base de données
  - **Modèles**: Définitions des entités et schémas Pydantic
- Privilégiez la composition à l'héritage quand c'est possible.
- Utilisez des classes pour encapsuler les comportements liés.

## Documentation

### Docstrings

- Utilisez des docstrings pour les modules, classes, méthodes et functions.
- Suivez le format Google pour les docstrings.

Example:

```python
def fetch_user_data(user_id: int, include_profile: bool = True) -> Dict[str, any]:
    """
Récupère les données d'un utilisateur depuis la base de données.

Args:
    user_id: L'identifiant de l'utilisateur.
    include_profile: Si True, inclut les information de profil.

Returns:
    Un dictionnaire contenant les données de l'utilisateur.

Raises:
    NotFoundError: Si l'utilisateur n'existe pas.
    """
```

### Commentaires

- Ajoutez des commentaires pour expliquer le "pourquoi", pas le "comment".
- Le code devrait être auto-explicatif quand c'est possible.
- Commentez les parties complexes ou non intuitives du code.

## Tests

### Standards de tests

- Chaque fonctionnalité doit avoir des tests.
- Nous visons une couverture de code minimale de 80%.
- Les tests doivent être indépendants les uns des autres.

### Structure des tests

- Utilisez pytest comme framework de test.
- Nommez les fichiers de test avec le préfixe `test_`.
- Organisez les tests par module et fonctionnalité.

### Types de tests

- **Tests unitaires**: Testent des functions/classes individuelles.
- **Tests d'intégration**: Testent l'interaction entre différents composants.
- **Tests API**: Testent les endpoints FastAPI avec httpx.

## Sécurité

- Évitez de hardcoder des information sensibles (mots de passe, clés API).
- Utilisez des variables d'environnement pour les configurations sensibles.
- Validez toutes les entrées utilisateur côté client et serveur.
- Utilisez des requêtes paramétrées pour éviter les injections SQL.

## Outils d'application automatique

Notre project utilise plusieurs outils pour aider à appliquer ces standards:

### Ruff

Ruff est un linter et formateur de code Python rapide. Il replace Flake8, Black, isort et d'autres outils. La configuration se trouve dans `pyproject.toml`.

### pre-commit

Pre-commit exécute des hooks avant chaque commit pour vérifier que le code respect les standards. Pour l'installer:

```bash
pre-commit install
```

Pour exécuter manuellement sur tous les fichiers:

```bash
pre-commit run --all-files
```

### CI/CD

Notre workflow GitHub Actions vérifie automatiquement que le code respecte ces standards à chaque PR.

---

Ces standards sont évolutifs et peuvent être modifiés pour mieux répondre aux besoins du project. Les suggestions d'amélioration sont toujours bienvenues.
