from os import environ
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from ollama import Client
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting QA service...")

DOCUMENT_STORAGE_URL = environ["DOCUMENT_STORAGE_URL"]
OLLAMA_URL = environ["OLLAMA_URL"]

OLLAMA_CLIENT = Client(host=OLLAMA_URL)

app = FastAPI()

class Query(BaseModel):
    body: str
    with_rag: bool = True

@app.post("/query")
async def query(q: Query):
    question = q.body
    if q.with_rag:
        # retrieve the documents
        response = requests.get(
            f"{DOCUMENT_STORAGE_URL}/similar_to/{requests.utils.quote(question)}"
        )
        matches = response.json()
        logger.info("matches:")
        logger.info(matches)
        prompt = "Based only on the following text, answer the question: " + question + "\n\n"
        for match in matches:
            prompt += match["body"] + "\n\n"
        logger.info(f"Generated prompt: {prompt}")
        response = OLLAMA_CLIENT.generate(model='mistral', prompt=prompt)
        return {
            "response": response,
            "sources": matches,
        }
    else:
        response = OLLAMA_CLIENT.generate(model='mistral', prompt=question)
        return {
            "response": response,
        }
