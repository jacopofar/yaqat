from os import environ
import logging

from fastapi import FastAPI
from pydantic import BaseModel
import psycopg
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from sonic import IngestClient, SearchClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting document storage service...")

POSTGRES_CONNECTION_STRING = environ["POSTGRES_CONNECTION_STRING"]

INDEX_MODE = environ["INDEX_MODE"]

if INDEX_MODE == "SONIC":
    SONIC_HOST = environ["SONIC_HOST"]
    SONIC_PORT = int(environ["SONIC_PORT"])
    SONIC_PASSWORD = environ["SONIC_PASSWORD"]
elif INDEX_MODE == "QDRANT":
    # NOTE that the SENTENCE_TRANSFORMERS_HOME will specify where to store it
    # using Docker, this should be some mounted volume
    MODEL = SentenceTransformer("distiluse-base-multilingual-cased-v1")
    QDRANT_CONNECTION_STRING = environ["QDRANT_CONNECTION_STRING"]
    QDRANT_CLIENT = QdrantClient(url=QDRANT_CONNECTION_STRING)
else:
    raise ValueError(f"Unknown INDEX_MODE: {INDEX_MODE}")


app = FastAPI()

class Document(BaseModel):
    body: str
    source: str

@app.post("/add_document")
async def add_document(doc: Document):
    with psycopg.connect(POSTGRES_CONNECTION_STRING) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO documents (body, source)
                VALUES (%(body)s, %(source)s)
                RETURNING id;
                """,
                {"body": doc.body, "source": doc.source},
            )
            doc_id = cur.fetchone()[0]
            conn.commit()
    if INDEX_MODE == "SONIC":
        with IngestClient(SONIC_HOST, SONIC_PORT, SONIC_PASSWORD) as ingestcl:
            ingestcl.push("all_documents", "paragraph", f"{doc_id}", doc.body)
    elif INDEX_MODE == "QDRANT":
        QDRANT_CLIENT.upsert(
            collection_name="all_documents",
            points=[
                PointStruct(
                    id=doc_id,
                    vector=MODEL.encode(doc.body).tolist(),
                    payload={"id": doc_id}
                )
            ],
        )
    return {"id": doc_id}

@app.post("/add_documents")
async def add_documents(docs: list[Document]):
    with psycopg.connect(POSTGRES_CONNECTION_STRING) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO documents (body, source)
                VALUES (%(body)s, %(source)s)
                RETURNING id;
                """,
                [dict(body=d.body, source=d.source) for d in docs],
                returning=True,
            )
            doc_ids = []
            # executemany requires this unusual way of fetching
            # see https://www.psycopg.org/psycopg3/docs/api/cursors.html#psycopg.Cursor.executemany
            while True:
                doc_ids.append(cur.fetchone()[0])
                if not cur.nextset():
                    break
            conn.commit()
    if INDEX_MODE == "SONIC":
        with IngestClient(SONIC_HOST, SONIC_PORT, SONIC_PASSWORD) as ingestcl:
            for doc_id, doc in zip(doc_ids, docs):
                ingestcl.push("all_documents", "paragraph", f"{doc_id}", doc.body)
    elif INDEX_MODE == "QDRANT":
        QDRANT_CLIENT.upsert(
            collection_name="all_documents",
            points=[
                PointStruct(
                    id=doc_id,
                    vector=MODEL.encode(doc.body).tolist(),
                    payload={"id": doc_id}
                )
                for doc_id, doc in zip(doc_ids, docs)
            ],
        )
    return {"ids": doc_ids}

@app.get("/similar_to/{body}")
async def similar_to(body: str):
    if INDEX_MODE == "SONIC":
        with SearchClient(SONIC_HOST, SONIC_PORT, SONIC_PASSWORD) as querycl:
            hits = querycl.query("all_documents", "paragraph", body)
    elif INDEX_MODE == "QDRANT":
        vector = MODEL.encode(body).tolist()
        hits = QDRANT_CLIENT.search(
            collection_name="all_documents",
            query_vector=vector,
            limit=10,
        )
    logger.debug(hits)
    result = []
    with psycopg.connect(POSTGRES_CONNECTION_STRING) as conn:
        for hit in hits:
            doc_id = hit.id
            score = hit.score
            # NOTE: we could fetch them together in a single query
            # but for 5 documents is still fast enough to not bother
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT body, source FROM documents
                    WHERE id = %(id)s;
                    """,
                    {"id": doc_id},
                )
                body, source = cur.fetchone()
                result.append({
                    "body": body,
                    "source": source,
                    "score": score,
                    "id": doc_id
                })
    return result