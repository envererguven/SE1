import json
import uuid
import requests
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import faiss
import numpy as np

app = Flask(__name__)

# Elasticsearch setup
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])

# Faiss setup: Dimensionality based on LLM embedding size (assume 1024 for LLaMA 3.2:1b; adjust if needed)
embedding_dim = 1024
faiss_index = faiss.IndexFlatL2(embedding_dim)  # L2 distance (can switch to cosine if needed)
song_id_to_metadata = {}  # In-memory map for song details (for simplicity; persist if needed)

# Ollama API endpoint (assume running locally)
OLLAMA_URL = "http://host.docker.internal:11434/api/embeddings"  # Use host.docker.internal to access host's Ollama from Docker

# Elasticsearch index name
INDEX_NAME = "songs"

# Create Elasticsearch index if not exists
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body={
        "mappings": {
            "properties": {
                "singer": {"type": "text"},
                "song_name": {"type": "text"},
                "genre": {"type": "keyword"},
                "lyrics": {"type": "text"}
            }
        }
    })

# Function to get embedding from Ollama
def get_embedding(text):
    body = {
        "model": "llama3.2:1b",
        "prompt": text
    }
    response = requests.post(OLLAMA_URL, json=body)
    if response.status_code == 200:
        return np.array(response.json()["embedding"], dtype=np.float32)
    else:
        raise ValueError("Failed to get embedding from Ollama")

# Load sample data on startup
def load_sample_data():
    with open('sample_data.json', 'r') as f:
        songs = json.load(f)
    for song in songs:
        insert_song(song)

load_sample_data()

# Insert song endpoint
@app.route('/insert', methods=['POST'])
def insert_song():
    data = request.json
    if not all(k in data for k in ['singer', 'song_name', 'genre', 'lyrics']):
        return jsonify({"error": "Missing fields"}), 400
    
    song_id = str(uuid.uuid4())
    
    # Generate embedding (combine lyrics and metadata for semantic richness)
    text_to_embed = f"{data['singer']} - {data['song_name']} ({data['genre']}): {data['lyrics']}"
    embedding = get_embedding(text_to_embed)
    
    # Store in Elasticsearch
    es.index(index=INDEX_NAME, id=song_id, body=data)
    
    # Store in Faiss
    faiss_index.add(np.array([embedding]))
    song_id_to_metadata[song_id] = data  # Map ID to metadata (Faiss IDs are indices)
    
    return jsonify({"message": "Song inserted", "id": song_id}), 201

# Search endpoint
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    search_type = request.args.get('type', 'hybrid')  # hybrid, keyword, semantic
    genre_filter = request.args.get('genre')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    results = []
    
    if search_type in ['keyword', 'hybrid']:
        # Keyword search with Elasticsearch
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["singer", "song_name", "lyrics"]
                }
            }
        }
        if genre_filter:
            es_query["query"] = {
                "bool": {
                    "must": es_query["query"],
                    "filter": {"term": {"genre": genre_filter}}
                }
            }
        es_results = es.search(index=INDEX_NAME, body=es_query)['hits']['hits']
        keyword_results = [(hit['_id'], hit['_score']) for hit in es_results]
        results.extend(keyword_results)
    
    if search_type in ['semantic', 'hybrid']:
        # Semantic search with Faiss
        query_embedding = get_embedding(query)
        distances, indices = faiss_index.search(np.array([query_embedding]), k=10)  # Top 10
        semantic_results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1:  # Valid index
                song_id = list(song_id_to_metadata.keys())[idx]  # Faiss indices map to list order
                semantic_results.append((song_id, 1 / (1 + dist)))  # Convert distance to similarity score
        results.extend(semantic_results)
    
    # Blend if hybrid (simple average score)
    if search_type == 'hybrid':
        # Aggregate scores (assuming equal weight)
        score_dict = {}
        for song_id, score in results:
            if song_id not in score_dict:
                score_dict[song_id] = []
            score_dict[song_id].append(score)
        blended_results = [(sid, np.mean(scores)) for sid, scores in score_dict.items()]
        blended_results.sort(key=lambda x: x[1], reverse=True)
        results = blended_results
    
    # Fetch metadata for top results
    final_results = []
    for song_id, score in results[:10]:  # Top 10
        metadata = song_id_to_metadata.get(song_id, es.get(index=INDEX_NAME, id=song_id)['_source'])
        final_results.append({
            "id": song_id,
            "singer": metadata['singer'],
            "song_name": metadata['song_name'],
            "genre": metadata['genre'],
            "lyrics_snippet": metadata['lyrics'][:100] + '...',
            "score": score
        })
    
    return jsonify({"results": final_results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
