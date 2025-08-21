from fastapi import FastAPI
from elasticsearch import Elasticsearch
import requests
import os

app = FastAPI()
es = Elasticsearch("http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/api/embeddings"
SYSTEM_PROMPT = "You are a semantic embedding generator for music content. Generate embeddings that capture song lyrics, genres, and meanings for accurate similarity search."

def get_embedding(text: str):
    body = {
        "model": "llama3.2:1b",
        "prompt": f"{SYSTEM_PROMPT} Embed this: {text}"
    }
    response = requests.post(OLLAMA_URL, json=body)
    if response.status_code != 200:
        raise ValueError("Ollama embedding failed")
    return response.json()["embedding"]

# Alternative: sentence-transformers (commented)
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')
# def get_embedding(text: str):
#     return model.encode(text).tolist()

@app.get("/search")
def search(query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    body = {
        "query": {
            "script_score": {
                "query": {"match": {"lyrics": query}},  # Keyword (BM25)
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'lyrics_embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        },
        "size": top_k
    }
    res = es.search(index="music_songs", body=body)
    return [hit["_source"] for hit in res["hits"]["hits"]]
