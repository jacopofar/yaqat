#!/bin/sh
docker compose exec ollama ollama pull mistral
docker compose exec document_storage python3 /document_storage/initial_setup.py