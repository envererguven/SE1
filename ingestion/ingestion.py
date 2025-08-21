from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
import requests
import os

app = FastAPI()
es = Elasticsearch("http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/api/embeddings"
SYSTEM_PROMPT = "You are a semantic embedding generator for music content. Generate embeddings that capture song lyrics, genres, and meanings for accurate similarity search."

class Song(BaseModel):
    singer: str
    song_name: str
    genre: str
    lyrics: str

def get_embedding(text: str):
    body = {
        "model": "llama3.2:1b",
        "prompt": f"{SYSTEM_PROMPT} Embed this: {text}"
    }
    response = requests.post(OLLAMA_URL, json=body)
    if response.status_code != 200:
        raise ValueError("Ollama embedding failed")
    return response.json()["embedding"]

# Alternative: Use sentence-transformers (commented out)
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')
# def get_embedding(text: str):
#     return model.encode(text).tolist()

@app.post("/insert")
def insert_song(song: Song):
    embedding = get_embedding(song.lyrics)
    doc = song.dict()
    doc["lyrics_embedding"] = embedding
    res = es.index(index="music_songs", body=doc)
    return {"id": res["_id"]}

@app.put("/update/{doc_id}")
def update_song(doc_id: str, song: Song):
    embedding = get_embedding(song.lyrics)
    doc = song.dict()
    doc["lyrics_embedding"] = embedding
    res = es.update(index="music_songs", id=doc_id, body={"doc": doc})
    return {"updated": True}

@app.get("/select/{doc_id}")
def get_song(doc_id: str):
    res = es.get(index="music_songs", id=doc_id)
    return res["_source"]

@app.delete("/delete/{doc_id}")
def delete_song(doc_id: str):
    es.delete(index="music_songs", id=doc_id)
    return {"deleted": True"}
