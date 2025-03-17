#!/bin/bash
# Script pour exécuter les tests avec Supabase
# Utilisation: bash scripts/run_tests_with_supabase.sh [options de pytest]

set -e

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "backend" ] && [ -d "../backend" ]; then
    cd ../
fi

if [ ! -d "backend" ]; then
    echo "Erreur: Le script doit être exécuté depuis la racine du project ou le dossier backend"
    exit 1

fi

# Vérifier si le fichier .env.test existe
if [ ! -f ".env.test" ] && [ ! -f "backend/.env.test" ]; then
    echo "Erreur: Le fichier .env.test n'existe pas"
    echo "Créez un fichier .env.test à la racine du project ou dans le dossier backend"
    exit 1
fi

# Vérifier la connection Supabase
echo "Vérification de la connection Supabase..."
python -m pip install -q httpx python-dotenv
python backend/scripts/verify_supabase.py

# Si verify_supabase.py échoue, arrêter le script
if [ $? -ne 0 ]; then
    echo "Erreur: Vérification de Supabase échouée"
    exit 1
fi

# Aller dans le dossier backend
cd backend

# Exécuter pytest avec les arguments supplémentaires
echo "Exécution des tests avec Supabase..."
python -m pytest -v "$@"
