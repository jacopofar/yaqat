from os import environ

import psycopg
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_CONNECTION_STRING = environ["QDRANT_CONNECTION_STRING"]
POSTGRES_CONNECTION_STRING = environ["POSTGRES_CONNECTION_STRING"]

client = QdrantClient(url=QDRANT_CONNECTION_STRING)
client.recreate_collection(
    collection_name="all_documents",
    vectors_config=VectorParams(size=512, distance=Distance.COSINE),
)

with psycopg.connect(POSTGRES_CONNECTION_STRING) as conn:
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            body TEXT,
            source TEXT
        );""")
        conn.commit()