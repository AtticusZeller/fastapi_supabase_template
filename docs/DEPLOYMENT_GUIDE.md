# Guide de configuration des déploiements automatiques

Ce document explique comment configurer et utiliser le système de déploiement automatique mis en place dans notre pipeline CI/CD. Le système utilise une approche basée sur la promotion d'images Docker pour garantir que le même artefact qui a été testé est déployé en production.

## Vue d'ensemble du processus

Notre processus de déploiement suit ces étapes :

1. **Build et Test** : Une image Docker est construite à partir de chaque commit sur les branches `develop` et `main`, ainsi que pour chaque tag de version.
2. **Promotion d'environnement** : Au lieu de reconstruire l'image pour chaque environnement, la même image est promue d'un environnement à l'autre.
3. **Déploiement automatique** : Une fois les tests réussis, le déploiement se fait automatiquement vers les environnements appropriés.

## Règles de déploiement

- **Environnement de développement** : Tous les commits sur la branche `develop` construisent une image Docker avec le tag `latest`.
- **Environnement de staging** : Tous les commits sur la branche `main` construisent une image Docker avec le tag `staging` et la déploient automatiquement vers l'environnement de staging.
- **Environnement de production** : Toute création de tag (version sémantique comme `v1.2.3`) utilise ce tag comme identifiant d'image et la déploie automatiquement vers l'environnement de production.

## Configuration requise

### Secrets GitHub

Les secrets suivants doivent être configurés dans les paramètres de votre repository GitHub :

#### Secrets globaux

```
GITHUB_TOKEN  # Généralement configuré automatiquement
SLACK_WEBHOOK_URL  # Pour les notifications de déploiement (optionnel)
```

#### Secrets pour l'environnement de Staging

Créez un environnement nommé `staging` dans les paramètres GitHub et ajoutez ces secrets :

```
STAGING_HOST  # Adresse IP ou nom d'hôte du serveur de staging
STAGING_USERNAME  # Nom d'utilisateur SSH pour le serveur
STAGING_SSH_KEY  # Clé SSH privée pour l'authentification
STAGING_SSH_PORT  # Port SSH (optionnel, par défaut 22)
STAGING_APP_PATH  # Chemin vers le répertoire de l'application sur le serveur
```

#### Secrets pour l'environnement de Production

Créez un environnement nommé `production` dans les paramètres GitHub et ajoutez ces secrets :

```
PRODUCTION_HOST  # Adresse IP ou nom d'hôte du serveur de production
PRODUCTION_USERNAME  # Nom d'utilisateur SSH pour le serveur
PRODUCTION_SSH_KEY  # Clé SSH privée pour l'authentification
PRODUCTION_SSH_PORT  # Port SSH (optionnel, par défaut 22)
PRODUCTION_APP_PATH  # Chemin vers le répertoire de l'application sur le serveur
```

### Configuration des serveurs

Sur vos serveurs de staging et de production, vous devez :

1. Installer Docker et docker-compose
2. Créer un répertoire pour l'application (correspondant à `STAGING_APP_PATH` ou `PRODUCTION_APP_PATH`)
3. Placer un fichier docker-compose.yml dans ce répertoire avec la configuration suivante :

```yaml
version: '3.8'

services:
  api:
    image: ${REGISTRY:-ghcr.io}/${REPOSITORY_OWNER:-acout}/${IMAGE_NAME:-fastapi-supabase-template}:${IMAGE_TAG:-latest}
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=${ENV:-production}
      # Ajoutez ici les autres variables d'environnement nécessaires
    volumes:
      - ./data:/app/data
```

## Déploiement manuel

Bien que le déploiement soit automatisé, vous pouvez toujours déclencher un déploiement manuellement :

1. Pour un déploiement en staging : Fusionnez vos modifications dans la branche `main`
2. Pour un déploiement en production : Créez un tag de version (par exemple `v1.2.3`)

```bash
# Création d'un tag pour déploiement en production
git tag -a v1.2.3 -m "Version 1.2.3"
git push origin v1.2.3
```

## Vérification de sécurité

En plus du déploiement automatique, notre pipeline CI/CD effectue désormais plusieurs vérifications de sécurité :

1. **Bandit** : Un scanner de sécurité pour Python qui recherche des problèmes de sécurité courants.
2. **Safety** : Vérifie les dépendances Python pour les vulnérabilités connues.
3. **Gitleaks** : Détecte les secrets, les clés privées et les identifiants qui pourraient être exposés accidentellement dans le code.

Les résultats de ces analyses sont disponibles dans les artefacts de chaque exécution du workflow.

## Résolution des problèmes

En cas d'échec de déploiement, vérifiez les points suivants :

1. **Problèmes d'accès SSH** :
   - Assurez-vous que les clés SSH sont correctement configurées dans les secrets GitHub
   - Vérifiez que l'utilisateur a les permissions nécessaires sur le serveur
   - Testez manuellement la connexion SSH pour vérifier l'accès

2. **Erreurs Docker** :
   - Vérifiez que Docker et docker-compose sont installés sur le serveur
   - Assurez-vous que l'utilisateur SSH a les droits d'exécuter des commandes Docker
   - Vérifiez l'espace disque disponible pour les images Docker

3. **Problèmes d'authentification au registre Docker** :
   - Assurez-vous que le token GitHub a les permissions nécessaires pour accéder au registre
   - Vérifiez que le serveur peut communiquer avec le registre Docker (problèmes de réseau/proxy)

4. **Erreurs de l'application** :
   - Consultez les logs du conteneur Docker : `docker logs <container_id>`
   - Vérifiez que toutes les variables d'environnement nécessaires sont définies

## Approche de promotion d'image vs. rebuild

Notre approche utilise la **promotion d'image** plutôt que la reconstruction d'images pour chaque environnement, ce qui présente plusieurs avantages :

1. **Fiabilité** : Vous déployez exactement ce que vous avez testé, éliminant les différences potentielles entre environnements.
2. **Rapidité** : Pas besoin de reconstruire l'image pour chaque environnement, accélérant le processus de déploiement.
3. **Traçabilité** : Une seule image est utilisée à travers tous les environnements, simplifiant le suivi des versions.
4. **Réduction des risques** : Moins d'opportunités pour des problèmes liés à la construction de l'image en production.

## Bonnes pratiques

1. **Ne jamais bypasser le processus** : Résistez à la tentation de déployer directement en production sans passer par le staging.

2. **Conventions de versionnement sémantique** : Utilisez un versionnement sémantique clair (MAJOR.MINOR.PATCH) pour les tags:
   - MAJOR : Changements incompatibles avec les versions précédentes
   - MINOR : Ajouts de fonctionnalités rétrocompatibles
   - PATCH : Corrections de bugs rétrocompatibles

3. **Rollback planifié** : Prévoyez toujours comment revenir en arrière en cas de problème. La commande suivante peut être utilisée :
   ```bash
   # Sur le serveur de production
   docker-compose stop
   echo "IMAGE_TAG=v1.2.2" > .env  # Tag de la version précédente stable
   docker-compose pull
   docker-compose up -d
   ```

4. **Surveillance post-déploiement** : Après un déploiement, surveillez activement les métriques de l'application pour détecter rapidement les problèmes.

5. **Tests de smoke** : Le workflow exécute automatiquement un test de santé basique (curl vers /health), mais envisagez d'ajouter des tests de smoke plus complets.

## Prochaines améliorations

Pour améliorer encore notre pipeline de déploiement, nous prévoyons :

1. **Déploiement bleu-vert** : Implémenter un système de déploiement bleu-vert pour des mises à jour sans interruption de service.

2. **Tests de charge automatiques** : Intégrer des tests de charge automatiques après le déploiement en staging.

3. **Approbation manuelle pour la production** : Ajouter une étape d'approbation manuelle avant le déploiement en production pour les versions critiques.

4. **Canary releases** : Implémenter des déploiements canary pour tester les nouvelles versions sur un sous-ensemble d'utilisateurs avant un déploiement complet.