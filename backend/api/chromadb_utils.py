# backend/api/chromadb_utils.py

import os

import chromadb
from django.conf import settings
from openai import OpenAI

# --- Configuration ---
CHROMA_COLLECTION = "portfolio_knowledge"
# Use the Docker service name for inter-container communication by default,
# but allow overriding via environment variables for CI/CD.
CHROMA_HOST = os.environ.get("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))


def get_chroma_client():
    """Returns a ChromaDB HTTP client."""
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def get_collection():
    """Gets or creates the main ChromaDB collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(CHROMA_COLLECTION)


def embed_text(text):
    """Generates an embedding for the given text using OpenAI."""
    try:
        # Ensure OPENAI_API_KEY is set, especially for CI environments
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            print("Warning: OPENAI_API_KEY is not set. Embedding will fail.")
            return None
        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(input=[text], model="text-embedding-3-small")
        return resp.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def add_or_update_node(doc_id, content, metadata):
    """Adds a new node or updates an existing one in ChromaDB."""
    collection = get_collection()
    embedding = embed_text(content)
    if embedding:
        collection.upsert(ids=[doc_id], embeddings=[embedding], documents=[content], metadatas=[metadata])
        print(f"Successfully upserted node: {doc_id}")


def delete_node(doc_id):
    """Deletes a node from ChromaDB by its ID."""
    collection = get_collection()
    try:
        collection.delete(ids=[doc_id])
        print(f"Successfully deleted node: {doc_id}")
    except Exception as e:
        # ChromaDB can raise an error if the ID doesn't exist, which is fine.
        print(f"Could not delete node {doc_id} (it may not exist): {e}")


def query_nodes(query, n_results=4):
    """Queries the collection for the most relevant nodes."""
    collection = get_collection()
    embedding = embed_text(query)
    if not embedding:
        return {"documents": [[]]}  # Return empty structure on embedding failure
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    return results
