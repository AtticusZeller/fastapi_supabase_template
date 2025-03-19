#!/usr/bin/env python
import argparse

from app.core.celery import celery_app


def main():
    """Point d'entrée pour démarrer un worker Celery"""
    parser = argparse.ArgumentParser(description="Start Celery worker")
    parser.add_argument(
        "--queue", type=str, default="default", help="Queue to listen on"
    )
    parser.add_argument(
        "--concurrency", type=int, default=4, help="Number of worker processes"
    )
    parser.add_argument("--loglevel", type=str, default="INFO", help="Logging level")

    args = parser.parse_args()

    print(f"Starting worker for queue: {args.queue}")
    print(f"Concurrency: {args.concurrency}")

    # Arguments pour Celery
    argv = [
        "worker",
        f"--queues={args.queue}",
        f"--concurrency={args.concurrency}",
        f"--loglevel={args.loglevel}",
        f"--hostname=worker.{args.queue}@%h",
    ]

    # Démarrer le worker
    celery_app.worker_main(argv)


if __name__ == "__main__":
    main()
