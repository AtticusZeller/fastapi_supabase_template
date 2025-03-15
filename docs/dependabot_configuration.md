# Configuration Dependabot

## Vue d'ensemble

Ce projet utilise Dependabot pour automatiser la gestion des dépendances et maintenir nos packages à jour, tout en privilégiant la sécurité. Cette documentation explique notre configuration et les bonnes pratiques associées.

## Configuration

Notre configuration Dependabot gère trois écosystèmes distincts :

1. **GitHub Actions** - Mises à jour des actions dans nos workflows CI/CD
2. **Python (pip)** - Dépendances Python de notre application
3. **Docker** - Mises à jour des images Docker

### Fréquence et planification

Toutes les mises à jour sont planifiées le **lundi à 9h00 (heure de Paris)** afin de minimiser les perturbations pendant la semaine de travail. Cette planification permet à l'équipe de traiter les PRs de dépendances en début de semaine.

### Regroupement intelligent

Pour réduire le bruit et la charge de travail liée aux revues, nous avons configuré des regroupements :

- **GitHub Actions** : Toutes les mises à jour d'actions sont regroupées
- **Python** : Séparation entre dépendances de production et de développement
  - Regroupement des mises à jour mineures et de patchs
  - Traitement individuel des mises à jour majeures qui peuvent introduire des incompatibilités
- **Docker** : Toutes les mises à jour Docker sont regroupées

### Automatisation des Pull Requests

Nous avons mis en place un workflow d'automatisation pour Dependabot :

- **Approbation automatique** pour les mises à jour mineures et de patchs
- **Merge automatique** pour les mises à jour de GitHub Actions 
- **Revue manuelle requise** pour les mises à jour majeures

## Bonnes pratiques

### Traitement des PRs Dependabot

1. **Mises à jour mineures/patchs** : Généralement sûres, elles sont approuvées et fusionnées automatiquement
2. **Mises à jour majeures** : Examiner attentivement les changements et les notes de version avant de fusionner
3. **Vulnérabilités de sécurité** : Priorité absolue, à traiter dès que possible

### Résolution des conflits

En cas de conflits dans les PRs Dependabot :

1. Vérifier les changements dans chaque fichier concerné
2. Résoudre les conflits manuellement en fonction des besoins du projet
3. Exécuter la suite de tests complète avant d'approuver

### Ignorer certaines dépendances

Dans certains cas, il peut être nécessaire d'ignorer temporairement les mises à jour d'une dépendance spécifique. Pour ce faire :

1. Décommentez la section `ignore` dans `.github/dependabot.yml`
2. Ajoutez le nom de la dépendance à ignorer
3. Ajoutez un commentaire expliquant pourquoi cette dépendance est ignorée et jusqu'à quand

## Dépannage

### PRs Dependabot en échec

Si les tests échouent sur une PR Dependabot :

1. Vérifiez si la mise à jour est compatible avec les autres dépendances
2. Consultez les notes de version pour identifier les changements importants
3. Mettez à jour le code ou les tests si nécessaire pour s'adapter aux nouvelles versions

### Trop de PRs ouvertes

Si le nombre de PRs Dependabot devient difficile à gérer :

1. Ajustez la fréquence des vérifications de `weekly` à `monthly`
2. Réduisez la valeur de `open-pull-requests-limit`
3. Envisagez de regrouper davantage de mises à jour ensemble

## Ressources additionnelles

- [Documentation Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates)
- [Configuration avancée de Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories/about-coordinated-disclosure-of-security-vulnerabilities)
