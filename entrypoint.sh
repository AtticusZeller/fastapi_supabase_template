#!/bin/bash
# entrypoint.sh

set -e

echo "Starting application in $APP_MODE mode"

# Démarrage selon le mode configuré
case "$APP_MODE" in
  "api")
    echo "Starting FastAPI server on port $PORT"
    cd backend
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ;;
    
  "worker")
    # Vérifier si la queue est spécifiée
    if [ -z "$CELERY_QUEUE" ]; then
      CELERY_QUEUE="default"
      echo "CELERY_QUEUE not specified, using 'default'"
    fi
    
    # Configurer la concurrence
    if [ -z "$CELERY_CONCURRENCY" ]; then
      CELERY_CONCURRENCY=$(nproc)
      echo "Auto-detecting concurrency: $CELERY_CONCURRENCY"
    fi
    
    echo "Starting Celery worker for queue: $CELERY_QUEUE with concurrency: $CELERY_CONCURRENCY"
    cd backend
    exec python worker.py --queue=$CELERY_QUEUE --concurrency=$CELERY_CONCURRENCY
    ;;
    
  "flower")
    echo "Starting Flower monitoring on port $PORT"
    cd backend
    exec celery -A app.core.celery flower --port=$PORT
    ;;
    
  *)
    echo "ERROR: Unknown APP_MODE: $APP_MODE"
    echo "Supported modes: api, worker, flower"
    exit 1
    ;;
esac
