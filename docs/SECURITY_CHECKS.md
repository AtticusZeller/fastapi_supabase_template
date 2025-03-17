# Vérifications de sécurité automatiques

Ce document décrit les vérifications de sécurité automatiques intégrées à notre pipeline CI/CD pour garantir la sécurité du code et des dépendances.

## Outils de sécurité intégrés

### 1. Bandit

Bandit est un outil conçu pour trouver des problèmes de sécurité courants dans le code Python.

**Fonctionnalités :**
- Analyse statique du code
- Détection de vulnérabilités connues (ex: injection SQL, désérialisation non sécurisée)
- Génération de rapports au format JSON

**Implémentation dans le CI :**
```yaml
- name: Run Bandit (Python security linter)
  run: |
    bandit -r backend/ -ll -ii -f json -o bandit-results.json || true
    echo "Results saved to bandit-results.json"
```

### 2. Safety

Safety vérifie les dépendances Python par rapport à une base de données de vulnérabilités connues.

**Fonctionnalités :**
- Vérification des dépendances par rapport à la base de données de vulnérabilités
- Identification des versions vulnérables des packages
- Suggestions de mises à jour

**Implémentation dans le CI :**
```yaml
- name: Check dependencies for vulnerabilities with Safety
  run: |
    cd backend
    safety check --full-report --file=pyproject.toml || true
```

### 3. Gitleaks

Gitleaks est un outil SAST (Static Application Security Testing) conçu pour détecter les secrets, les mots de passe, les clés privées, et les jetons d'API dans le code source.

**Fonctionnalités :**
- Détection de secrets via expressions régulières et entraîtropes
- Analyse historique du dépôt
- Support pour plusieurs formats de fichiers

**Implémentation dans le CI :**
```yaml
- name: Check for secrets in code
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

## Vérification de seuil de couverture des tests

Un seuil de couverture de test minimal de 90% est maintenant appliqué dans le pipeline CI/CD. Si la couverture de code tombe en dessous de ce seuil, le pipeline échoue.

**Implémentation dans le CI :**
```yaml
- name: Check coverage threshold
  run: |
    COVERAGE=$(grep -Po 'line-rate="\K[^"]*' backend/coverage.xml | head -1)
    COVERAGE_PCT=$(echo "$COVERAGE * 100" | bc)
    echo "Total coverage: $COVERAGE_PCT%"
    if (( $(echo "$COVERAGE_PCT < 90" | bc -l) )); then
      echo "Code coverage is below the required 90%"
      exit 1
    fi
```

## Rapports générés

Les résultats des analyses de sécurité sont à la fois :

1. Affichés dans les logs de l'exécution du workflow
2. Enregistrés comme artefacts de build pour un examen ultérieur

```yaml
- name: Upload security scan results
  uses: actions/upload-artifact@v4
  with:
    name: security-scan-results
    path: |
      bandit-results.json
      gitleaks-report.json
    retention-days: 7
```

## Gestion des résultats

### Faux positifs

Les outils de sécurité peuvent parfois signaler des faux positifs. Pour les gérer :

1. **Bandit** : Vous pouvez ajouter des commentaires dans le code pour ignorer des avertissements spécifiques :
   ```python
   # nosec B602 - Justification pour ignorer
   subprocess.call(command_args)
   ```

2. **Safety** : Vous pouvez créer un fichier `.safety-policy.yml` pour ignorer des vulnérabilités spécifiques avec justification.

3. **Gitleaks** : Vous pouvez configurer un fichier `.gitleaksignore` ou ajouter des annotations `gitleaks:allow` dans les commentaires de code.

### Procédure en cas de détection

1. **Évaluer la gravité** : Tous les problèmes de sécurité ne sont pas critiques. Évaluez l'impact potentiel.

2. **Corriger rapidement** : Les vulnérabilités critiques doivent être corrigées immédiatement, en particulier celles qui exposent des données sensibles.

3. **Documenter les décisions** : Si vous décidez d'ignorer certaines alertes, documentez clairement pourquoi dans le code ou dans un document de décisions de sécurité.

## Intégration dans le workflow de développement

Les analyses de sécurité s'exécutent :

1. Sur toutes les Pull Requests vers les branches `main` et `develop`
2. Sur tous les pushes vers ces branches
3. Sur les releases taguées

Cela assure que le code est constamment analysé pour les problèmes de sécurité à chaque étape du processus de développement.

## Configuration locale pour les développeurs

Pour que les développeurs puissent exécuter ces vérifications localement avant de soumettre du code :

```bash
# Installation des outils de sécurité
pip install bandit safety

# Exécution de Bandit
bandit -r backend/

# Exécution de Safety
cd backend
safety check --file=pyproject.toml
```

Envisagez d'ajouter ces vérifications à vos hooks pre-commit pour une détection encore plus précoce.