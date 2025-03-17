#!/bin/bash
# Script pour exécuter les tests en mode CI, en simulant l'environnement CI/CD

set -e

# S'assurer qu'on est dans le bon répertoire
if [ ! -d "backend" ] && [ ! -d "../backend" ]; then
    echo "Erreur: Le script doit être exécuté depuis le répertoire racine ou backend du project"
    exit 1
fi

# Aller au répertoire backend si on est dans la racine
if [ -d "backend" ]; then
    cd backend
fi

# Installer pytest-asyncio s'il n'est pas déjà installé
python -m pip install pytest-asyncio httpx python-dotenv pytest-cov

# Exécuter les tests avec les paramètres appropriés
echo "===== Exécution des tests en mode CI ====="
echo "Note: Ceci simule l'environnement CI/CD pour les tests"

# Exécuter pytest avec le mode verbeux et génération des rapports de couverture
pytest -v --cov=app --cov-report=term --cov-report=xml --cov-report=html --junitxml=test-report.xml

# Information sur l'emplacement des rapports
echo "\nRapports générés:"
echo " - Rapport XML de couverture: $(pwd)/coverage.xml (pour SonarCloud)"
echo " - Rapport HTML de couverture: $(pwd)/htmlcov/index.html"
echo " - Rapport JUnit de tests: $(pwd)/test-report.xml"
