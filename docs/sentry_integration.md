# Intégration Sentry

## Vue d'ensemble

Sentry est un service de surveillance des erreurs qui aide les développeurs à identifier et corriger les bugs en temps réel. Cette documentation explique comment Sentry a été intégré dans notre pipeline CI/CD et comment l'utiliser efficacement.

## Configuration

### Prérequis

1. Compte Sentry avec un project configuré
2. Organisation Sentry et nom de project définis
3. Token d'authentification Sentry

### Variables d'environnement requises

Dans les paramètres secrets GitHub, ajoutez les variables suivantes :

| Variable | Description |
|----------|-------------|
| `SENTRY_AUTH_TOKEN` | Token d'authentification généré dans Sentry |
| `SENTRY_ORG` | Nom de votre organisation Sentry |
| `SENTRY_PROJECT` | Nom de votre project Sentry |

Dans votre fichier `.env` (et dans l'environnement de déploiement), ajoutez :

```
SENTRY_DSN=https://your-dsn-key@sentry.io/your-project
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
SENTRY_ENABLE_TRACING=False
SENTRY_RELEASE=local-dev
```

## Fonctionnement

Le workflow Sentry est automatiquement déclenché lors des opérations suivantes :

- Push sur les branches `main` et `develop`
- Création de tags (format `v*`)

Le workflow effectue automatiquement :

1. La détermination automatique de la version basée sur le contexte Git
2. La création d'une release Sentry avec le bon environment
3. L'association des commits à la release pour le suivi des problèmes

## Environments

Le système configure automatiquement les environments Sentry en function du contexte :

- Tags (`v*`) → environment **production**
- Branche `main` → environment **staging**
- Branche `develop` → environment **development**

## Dépannage

### Le workflow ne s'exécute pas

Vérifiez les points suivants :

1. Les secrets GitHub sont-ils correctement configurés?
2. Le token d'authentification est-il valid et non expiré?

### Les erreurs n'apparaissent pas dans Sentry

1. Vérifiez que le DSN dans vos variables d'environnement est correct
2. Assurez-vous que l'initialisation de Sentry est effectuée au début de votre application
3. Vérifiez que la variable `SENTRY_RELEASE` correspond à la version déployée

## Resources additionnelles

- [Documentation officielle Sentry pour Python](https://docs.sentry.io/platforms/python/)
- [Documentation FastAPI avec Sentry](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Action GitHub Sentry Release](https://github.com/getsentry/action-release)
