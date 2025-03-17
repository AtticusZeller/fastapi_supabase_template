#!/bin/bash
set -e

# Ce script lance les tests en utilisant l'instance Supabase cloud

# Chemin du fichier .env.test (à la racine du project)
ENV_TEST_FILE="../.env.test"

# Vérifier si le fichier .env.test existe
if [ ! -f "$ENV_TEST_FILE" ]; then
    echo "Erreur: Le fichier .env.test n'existe pas à la racine du project."
    echo "Veuillez créer ce fichier avec les variables nécessaires pour les tests."
    exit 1
fi

# Vérifier que le fichier .env.test contient les variables nécessaires
if ! grep -q "SUPABASE_SERVICE_KEY" "$ENV_TEST_FILE"; then
    echo "Attention: La variable SUPABASE_SERVICE_KEY n'est pas définie dans votre fichier .env.test"
    echo "Cette variable est requise pour les tests. Assurez-vous qu'elle est définie."
    exit 1
fi

echo "Utilisation du fichier .env.test existent pour les tests."

# Exécuter les tests
echo "Exécution des tests avec vos paramètres..."
python -m pytest tests/ -v

echo "Tests terminés."
