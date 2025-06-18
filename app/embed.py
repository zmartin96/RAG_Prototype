import json
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import requests
from pathlib import Path




def load_chunks(json_path="preprocessed_chunks.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def get_embedding(text, model="mxbai-embed-large"):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]

def embed_chunks(chunks, collection_name="work_center_notes"):
    client = chromadb.PersistentClient(path="./vectorstore")

    collection = client.get_or_create_collection(name=collection_name)

    existing = set()
    try:
        existing = set(collection.get(include=["metadatas"], limit=10000)["ids"])
    except:
        pass

    for i, chunk in enumerate(chunks):
        if chunk["id"] in existing:
            print(f"[{i+1}/{len(chunks)}] Skipping {chunk['id'][:8]} (already embedded)")
            continue

        print(f"[{i+1}/{len(chunks)}] Embedding {chunk['id'][:8]}")
        emb = get_embedding(chunk["text"])
        collection.add(
            ids=[chunk["id"]],
            embeddings=[emb],
            documents=[chunk["text"]],
            metadatas=[chunk["metadata"]],
        )

    print(f"Succesfully stored {len(chunks)} chunkss in ChromaDB collection '{collection_name}'")

if __name__ == "__main__":
    chunks = load_chunks()
    embed_chunks(chunks)
