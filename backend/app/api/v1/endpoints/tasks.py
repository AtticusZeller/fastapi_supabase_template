# backend/app/api/v1/endpoints/tasks.py
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.core.celery import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task_status(
    task_id: str, user: CurrentUser = Depends()
) -> dict[str, Any]:
    """
    Récupère le statut d'une tâche Celery.

    Cette fonction permet de suivre l'état d'avancement de n'importe quelle tâche asynchrone
    dans le système, qu'elle soit liée au RAG, au traitement d'image, etc.
    """
    # Récupérer le résultat de la tâche Celery
    task_result: AsyncResult[Any] = AsyncResult(task_id, app=celery_app)

    # Préparer la réponse
    result = {"task_id": task_id, "status": task_result.status}

    # Ajouter des informations supplémentaires selon l'état
    if task_result.successful():
        result["result"] = task_result.get()
    elif task_result.failed():
        # Gérer les exceptions en ne renvoyant que le message, pas la trace
        if isinstance(task_result.result, Exception):
            result["error"] = str(task_result.result)
        else:
            result["error"] = "Unknown error"
    elif task_result.status == "PROGRESS":
        # Pour les tâches qui rapportent leur progression
        if isinstance(task_result.info, dict):
            result["progress"] = task_result.info.get("progress", 0)
            result["current"] = task_result.info.get("current", 0)
            result["total"] = task_result.info.get("total", 100)

    return result


@router.get("/")
async def get_active_tasks(user: CurrentUser = Depends()) -> dict[str, Any]:
    """
    Récupère la liste des tâches actives dans le système.

    Renvoie les tâches en cours d'exécution ou en attente dans la file.
    Utile pour monitorer l'activité globale du système.
    """
    # Cette implémentation est simplifiée et démontre le concept.
    # Dans une implémentation complète, vous utiliseriez l'inspection Celery.

    # Pour une implémentation réelle, utiliser:
    # from celery.task.control import inspect
    # inspector = inspect()
    # active_tasks = inspector.active()
    # reserved_tasks = inspector.reserved()

    # Simuler le résultat pour la démonstration
    return {
        "active": [
            {
                "id": "simulated-task-1",
                "name": "process_document",
                "started": "2023-05-19T10:23:54.000Z",
            },
            {
                "id": "simulated-task-2",
                "name": "generate_embeddings",
                "started": "2023-05-19T10:24:12.000Z",
            },
        ],
        "queued": [
            {
                "id": "simulated-task-3",
                "name": "process_document",
                "queued": "2023-05-19T10:25:00.000Z",
            }
        ],
        "note": "Cette liste est simulée. Dans une implémentation réelle, elle serait dynamique.",
    }
