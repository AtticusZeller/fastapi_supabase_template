# RAG System Guide - Complete Workflow

## System Architecture

The Insperio Engine RAG (Retrieval Augmented Generation) system uses a fully asynchronous architecture enabling scalable document processing across multiple machines. The workflow includes:

1. **REST API Ingestion** - Unified entry point
2. **Asynchronous Processing** - Via Celery and PGMQ
3. **Vector Storage** - With pgvector
4. **Semantic Search** - Vector similarity

## Requirements

- PostgreSQL with pgvector extension enabled
- PGMQ configured as Celery broker
- FastAPI exposing ingestion and search endpoints
- Celery worker (can be deployed on separate machine)

## Ingestion and Processing Workflow

1. **Document Reception**
   - The `/api/v1/rag/ingest` API receives a file with metadata
   - File is saved to Supabase Storage
   - A `Document` record is created with "pending" status
   - A Celery `process_document` task is triggered

2. **Document Processing** (Celery task)
   - Task retrieves document and changes status to "processing"
   - Text is extracted based on format (PDF, DOCX, etc.)
   - Document is hierarchically structured (sections, chunks)
   - Format-specific metadata is extracted
   - Status changes to "indexing"
   - A second `generate_embeddings` task is triggered

3. **Embedding Generation** (Celery task)
   - Each chunk is vectorized via embedding model
   - Vectors are stored in PostgreSQL database (pgvector)
   - Final status changes to "ready"

4. **Monitoring and Reporting**
   - API allows progress tracking via `/api/v1/rag/document/{id}`
   - Processing statistics available through same endpoint
   - Errors are logged in document with "error" status

## Search Workflow

1. **Search Query**
   - The `/api/v1/rag/search` API receives text query and optional filters
   - Query is vectorized using same embedding model
   - Vector similarity search performed via pgvector
   - Results returned sorted by relevance

## Deployment Across Separate Machines

The system is designed for distributed deployment:

1. **API Server**
   - Hosts FastAPI endpoints
   - Connects to PostgreSQL database
   - Sends tasks to PGMQ broker

2. **Processing Workers**
   - Runs Celery with `python worker.py`
   - Can be horizontally scaled
   - Connects to same PGMQ broker
   - Accesses PostgreSQL database for read/write operations

3. **Multi-machine Configuration**
   - Use same environment variables on each machine
   - Ensure all workers and API can access PostgreSQL
   - Verify storage paths are accessible to all workers

## Monitoring and Maintenance

- Regularly check Celery logs for errors
- Use `/api/v1/rag/documents` endpoint to list all documents
- Monitor pgvector indexing and search performance
- Optimize vector indexes if needed
