# YAQAT - Yet Another Question Answering Tool

Simple RAG tool experiment.

## Setup
Use `docker compose up` to start the services, the first time you will also need to run `initial_setup.sh` to download the Ollama model and create the DB schema.

## Usage

No UI at the moment, visit http://localhost:8000/docs to store documents, and http://localhost:8090/docs for the QA component.

## Components (planned)

* Postgres: vanilla Postgres database, used to store the documents for RAG and the task queue
* Qdrant: qdrant server, to perform vector search
* docstore: offers an API to index and retrieve documents, responsible for calculating the embeddings and interfacing with postgres and qdrant
* crawler: ingest documents (sending them to the docstore) from the web or other sources, uses the task queue to handle the volume
* Ollama: vanilla Ollama server, used to form a single textual reply from the retrieved documents. May use llama2 or
* QA: uses the docstore and ollama to retrieve relevant documents and form a single textual answer. Includes a web interface to show the stuff nicely and also the crawler status and the insertion of new documents.

## TODO, ideas

- [ ] Implement Hyde
- [ ] Try full text search or FTS/vector hybrids
- [ ] Improve ways to chunk documents (sentences, paragraphs, etc)
- [ ] Add thresholds on retrieval to not fetch more than needed
- [ ] Use "tools" (JSON calls) to make the process iterative
