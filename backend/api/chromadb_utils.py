import os

import chromadb

from .llm_client import generate_embedding, get_chroma_collection_name

CHROMA_HOST = os.environ.get("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))


def get_chroma_client():
    """Returns a ChromaDB HTTP client."""
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def get_collection():
    """Gets or creates the main ChromaDB collection, named per the active embedding model."""
    client = get_chroma_client()
    collection_name = get_chroma_collection_name()
    return client.get_or_create_collection(collection_name)


def add_or_update_node(doc_id, content, metadata):
    """Adds a new node or updates an existing one in ChromaDB."""
    try:
        embedding = generate_embedding(content)
    except Exception as e:
        print(f"Error generating embedding for node {doc_id}: {e}")
        return

    if embedding:
        collection = get_collection()
        collection.upsert(ids=[doc_id], embeddings=[embedding], documents=[content], metadatas=[metadata])
        print(f"Successfully upserted node: {doc_id}")


def delete_node(doc_id):
    """Deletes a node from ChromaDB by its ID."""
    collection = get_collection()
    try:
        collection.delete(ids=[doc_id])
        print(f"Successfully deleted node: {doc_id}")
    except Exception as e:
        print(f"Could not delete node {doc_id} (it may not exist): {e}")


def query_nodes(query, n_results=4):
    """Queries the collection for the most relevant nodes."""
    try:
        embedding = generate_embedding(query)
    except Exception as e:
        print(f"Error generating embedding for query: {e}")
        return {"documents": [[""]]}

    if not embedding:
        return {"documents": [[""]]}

    collection = get_collection()
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    return results
