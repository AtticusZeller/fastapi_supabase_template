#!/bin/bash

# Script pour activer l'extension pgvector dans Supabase
# À exécuter après avoir démarré Supabase local

set -e

# Récupérer les informations de connexion à la base de données
DB_URL=${SUPABASE_DB_URL:-"postgresql://postgres:postgres@localhost:54322/postgres"}

echo "Activation de l'extension pgvector dans la base de données..."

# Exécuter la commande SQL pour activer l'extension pgvector
psql "${DB_URL}" -c 'CREATE EXTENSION IF NOT EXISTS vector;'

echo "Extension pgvector activée avec succès!"
