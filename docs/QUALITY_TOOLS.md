# Outils de Qualité de Code

Ce document détaille les outils de qualité de code configurés dans ce projet, comment ils sont intégrés dans notre processus de développement, et comment les utiliser efficacement.

## SonarCloud

SonarCloud est un service d'analyse de code automatique en continu qui détecte les bugs, les vulnérabilités et les "code smells" dans votre code.

### Configuration

Le projet est configuré pour utiliser SonarCloud via le fichier `sonar-project.properties` à la racine du projet et le workflow GitHub Actions `.github/workflows/sonarcloud.yml`.

### Métriques surveillées

- **Qualité de code** : Identification des problèmes de code comme les bugs potentiels, les vulnérabilités et les "code smells"
- **Couverture de tests** : Pourcentage du code couvert par les tests automatiques
- **Duplication de code** : Détection des blocs de code dupliqués
- **Complexité** : Analyse de la complexité cyclomatique et cognitive du code
- **Dette technique** : Estimation du temps nécessaire pour corriger tous les problèmes de code

### Consultation des résultats

Les résultats de l'analyse SonarCloud sont disponibles :

1. Sur le [tableau de bord SonarCloud du projet](https://sonarcloud.io/project/overview?id=acout_fastapi_supabase_template)
2. Directement dans les Pull Requests via les commentaires de SonarCloud
3. Via les badges dans le README du projet

### Configuration locale

Pour configurer SonarCloud pour votre fork du projet :

1. Créez un compte sur [SonarCloud](https://sonarcloud.io/) et liez-le à votre compte GitHub
2. Importez votre dépôt dans SonarCloud
3. Générez un token d'accès dans SonarCloud
4. Ajoutez ce token comme secret GitHub dans votre dépôt avec le nom `SONAR_TOKEN`
5. Adaptez le fichier `sonar-project.properties` pour refléter vos informations d'organisation et de projet

## Codecov

Codecov est un outil qui permet de visualiser et d'analyser la couverture de code de votre projet.

### Configuration

Codecov est intégré dans le workflow GitHub Actions principal `.github/workflows/main.yml`. Les rapports de couverture sont générés lors de l'exécution des tests et envoyés à Codecov.

### Fonctionnalités

- **Visualisation de couverture** : Interface graphique pour explorer la couverture de code
- **Évolution de la couverture** : Suivi de l'évolution de la couverture dans le temps
- **Analyse des Pull Requests** : Vérification automatique des changements de couverture lors des PRs
- **Badges** : Badges de couverture pour votre README

### Configuration locale

Pour configurer Codecov pour votre fork :

1. Créez un compte sur [Codecov](https://codecov.io/) et liez-le à votre compte GitHub
2. Importez votre dépôt dans Codecov
3. Générez un token Codecov si nécessaire
4. Ajoutez ce token comme secret GitHub avec le nom `CODECOV_TOKEN`

## Génération locale des rapports de couverture

Vous pouvez générer des rapports de couverture localement pour vérifier les résultats avant de pousser vos modifications :

```bash
cd backend
# Exécuter les tests avec génération des rapports de couverture
bash scripts/run_ci_tests.sh
```

Cela générera :
- Un rapport de couverture HTML dans `backend/htmlcov/index.html`
- Un rapport XML dans `backend/coverage.xml` pour SonarCloud
- Un rapport JUnit dans `backend/test-report.xml`

## Intégration dans le processus de développement

Les outils de qualité de code sont intégrés dans notre processus de développement de la manière suivante :

1. **Localement** : Hooks pre-commit pour vérifier le style et la qualité avant chaque commit
2. **Pull Requests** : Analyse automatique avec SonarCloud et vérification de la couverture avec Codecov
3. **Intégration continue** : Exécution des tests et analyse du code sur chaque push

## Seuils de qualité

Les seuils suivants sont établis pour maintenir la qualité du code :

- **Couverture de tests** : Minimum 80%
- **Duplication de code** : Maximum 5%
- **Dette technique** : Maximum 5% du temps de développement

Les Pull Requests qui ne respectent pas ces seuils seront signalées comme problématiques, mais la décision finale d'acceptation reste à la discrétion des mainteneurs du projet.

## Résolution des problèmes communs

### SonarCloud ne s'exécute pas

1. Vérifiez que le secret `SONAR_TOKEN` est correctement configuré dans votre dépôt
2. Assurez-vous que le fichier `sonar-project.properties` est correctement configuré
3. Vérifiez les logs du workflow GitHub Actions pour identifier les erreurs

### Faible couverture de code

1. Exécutez les tests localement avec rapport de couverture : `bash scripts/run_ci_tests.sh`
2. Ouvrez le rapport HTML (`backend/htmlcov/index.html`) pour identifier les parties non couvertes
3. Ajoutez des tests pour les parties manquantes

### Problèmes détectés par SonarCloud

1. Consultez le tableau de bord SonarCloud pour voir les détails des problèmes
2. Corrigez les problèmes dans votre code
3. Relancez l'analyse pour vérifier que les problèmes sont résolus

## Ressources utiles

- [Documentation SonarCloud](https://docs.sonarcloud.io/)
- [Documentation Codecov](https://docs.codecov.io/)
- [Documentation Pytest Coverage](https://pytest-cov.readthedocs.io/en/latest/)
- [Guide des bonnes pratiques Python](https://docs.python-guide.org/)
