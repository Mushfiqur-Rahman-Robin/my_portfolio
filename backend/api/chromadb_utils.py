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


def add_or_update_node(doc_id, content, metadata, job_name=None):
    """Adds a new node or updates an existing one in ChromaDB."""
    try:
        embedding = generate_embedding(content, job_name=job_name)
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


def query_nodes(query, n_results=4, session=None):
    """Queries the collection for the most relevant nodes.

    Automatically caps n_results to the number of documents in the collection
    to avoid ChromaDB warnings when the collection is smaller than n_results.
    """
    try:
        embedding = generate_embedding(query, session=session)
    except Exception as e:
        print(f"Error generating embedding for query: {e}")
        return {"documents": [[""]]}

    if not embedding:
        return {"documents": [[""]]}

    collection = get_collection()

    # Cap n_results to avoid querying more than what exists in the collection.
    # ChromaDB emits a WARNING (and silently adjusts anyway) when n_results
    # exceeds the document count; we handle it explicitly here.
    actual_count = collection.count()
    if actual_count == 0:
        return {"documents": [[""]]}
    n_results = min(n_results, actual_count)

    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    return results
