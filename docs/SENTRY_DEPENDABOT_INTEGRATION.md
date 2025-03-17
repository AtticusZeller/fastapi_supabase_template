# Intégration Sentry et Dependabot

Ce document décrit l'intégration de Sentry pour la surveillance des erreurs et de Dependabot pour la gestion automatisée des dépendances dans le project Insperio Labs.

## Sentry

### Aperçu

Sentry a été intégré pour fournir:
- Surveillance des erreurs en temps réel
- Alertes automatisées en cas d'exceptions
- Traçage des performances
- Profilage des opérations
- Association des releases avec les déploiements

### Configuration

#### Variables d'environnement

Les variables suivantes doivent être configurées:

```env
# Sentry
SENTRY_DSN=https://votre-clé@sentry.io/project
SENTRY_ENVIRONMENT=production|staging|development
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

- `SENTRY_DSN`: URL fournie par Sentry pour votre project
- `SENTRY_ENVIRONMENT`: Environment actuel (production, staging, development)
- `SENTRY_TRACES_SAMPLE_RATE`: Taux d'échantillonnage pour le traçage des performances (0.0 à 1.0)
- `SENTRY_PROFILES_SAMPLE_RATE`: Taux d'échantillonnage pour le profilage (0.0 à 1.0)

#### GitHub Actions

Un workflow Sentry a été configuré pour:
1. Créer automatiquement des releases dans Sentry à chaque push sur main/develop ou tag
2. Lier les commits à la release pour le suivi des corrections
3. Définir l'environnement approprié en function de la branche/tag

#### Secrets GitHub requis

Les secrets suivants doivent être configurés dans les paramètres GitHub du dépôt:

- `SENTRY_AUTH_TOKEN`: Token d'authentification pour l'API Sentry
- `SENTRY_ORG`: Nom de l'organisation Sentry
- `SENTRY_PROJECT`: Nom du project Sentry

### Test de l'intégration

Une route de test a été ajoutée pour vérifier que Sentry capture correctement les erreurs:

```
GET /debug-sentry
```

Cette route génère intentionnellement une division par zéro pour tester la capture d'exceptions.

### Bonnes pratiques

1. **Utilisation des contextes**: Ajouter des contextes aux événements Sentry pour faciliter le débogage
   ```python
   sentry_sdk.set_context("user", {"id": user_id, "email": user_email})
   ```

2. **Capture manuelle**: Capturer des exceptions spécifiques quand nécessaire
   ```python
   try:
       # Code qui peut échouer
   except Exception as e:
       sentry_sdk.capture_exception(e)
   ```

3. **Performances**: Utiliser le SDK Sentry pour mesurer les performances des opérations critiques
   ```python
   with sentry_sdk.start_transaction(op="task", name="process_data"):
       # Logique critique
   ```

## Dependabot

### Aperçu

Dependabot a été configuré pour:
- Surveiller automatiquement les dépendances Python et GitHub Actions
- Créer des pull requests pour les mises à jour disponibles
- Approuver et fusionner automatiquement les mises à jour mineures et de correctifs
- Regrouper les mises à jour pour réduire le nombre de PRs

### Configuration

#### Fichier dependabot.yml

Le fichier `.github/dependabot.yml` définit:
- Les écosystèmes surveillés (pip, github-actions, docker)
- La fréquence des vérifications (hebdomadaire)
- Les préfixes de message de commit
- Les labels automatiques pour les PRs
- Les stratégies de regroupement
- Les limites de PRs simultanées

#### Auto-merge

Un workflow GitHub Action `dependabot-auto.yml` a été configuré pour:
1. Détecter automatiquement les PRs de Dependabot
2. Approuver et fusionner automatiquement les mises à jour mineures et de correctifs
3. Demander une révision manuelle pour les mises à jour majeures

### Personnalisation

Pour personnaliser davantage:

1. **Ignorer des dépendances**: Ajouter des règles `ignore` dans `dependabot.yml`
2. **Modifier la fréquence**: Changer `interval` dans `dependabot.yml` (daily/weekly/monthly)
3. **Ajuster l'auto-merge**: Modifier les conditions dans le workflow `dependabot-auto.yml`

## Maintenance

### Sentry

- Vérifier régulièrement le tableau de bord Sentry pour les nouvelles erreurs
- Examiner les métriques de performance pour identifier les goulots d'étranglement
- Maintenir à jour le token d'authentification Sentry

### Dependabot

- Examiner périodiquement les PRs en attente de Dependabot
- Vérifier les notes de mise à jour des dépendances majeures avant de les approuver
- Ajuster les règles d'auto-merge si nécessaire

## Dépannage

### Sentry

- Si les erreurs ne sont pas capturées, vérifier que `SENTRY_DSN` est correctement configuré
- Pour les problèmes de performance, essayer d'augmenter `SENTRY_TRACES_SAMPLE_RATE`
- Si le workflow GitHub Actions échoue, vérifier les secrets et autorisations

### Dependabot

- Si Dependabot crée trop de PRs, ajuster les paramètres de regroupement
- Si l'auto-merge échoue, vérifier les logs du workflow et les autorisations GitHub
