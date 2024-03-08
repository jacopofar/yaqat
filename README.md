# YAQAT - yet Anothr Question Answering Tool

Simple RAG

## Components (planned)

* Postgres: vanilla Postgres database, used to store the documents for RAG and the task queue
* Qdrant: qdrant server, to perform vector search
* docstore: offers an API to index and retrieve documents, responsible for calculating the embeddings and interfacing with postgres and qdrant
* crawler: ingest documents (sending them to the docstore) from the web or other sources, uses the task queue to handle the volume
* Ollama: vanilla Ollama server, used to form a single textual reply from the retrieved documents. May use llama2 or
* QA: uses the docstore and ollama to retrieve relevant documents and form a single textual answer. Includes a web interface to show the stuff nicely and also the crawler status and the insertion of new documents.