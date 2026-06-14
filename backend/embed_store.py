import logging
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "specter_legal_kb"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

_client = None
_collection = None
_model = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def add_chunks_to_db(chunks: List[str], source: str = "legal_kb", namespace: str = "global") -> int:
    if not chunks:
        return 0

    collection = _get_collection()
    model = _get_model()
    embeddings = model.encode(chunks, show_progress_bar=False).tolist()

    existing_ids = set(collection.get(where={"$and": [{"namespace": namespace}, {"source": source}]})['ids'])
    ids = []
    valid_chunks = []
    valid_embeddings = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{namespace}::{source}::{i}"
        if chunk_id not in existing_ids:
            ids.append(chunk_id)
            valid_chunks.append(chunk)
            valid_embeddings.append(emb)

    if not ids:
        logger.info(f"All chunks for {source} already exist in collection.")
        return 0

    collection.add(
        ids=ids,
        embeddings=valid_embeddings,
        documents=valid_chunks,
        metadatas=[{"source": source, "namespace": namespace, "chunk_index": i} for i in range(len(ids))]
    )
    logger.info(f"Added {len(ids)} chunks from '{source}' to ChromaDB.")
    return len(ids)


def search_chunks(query: str, top_k: int = 5, namespace: str = "global") -> List[Dict]:
    collection = _get_collection()
    model = _get_model()

    query_embedding = model.encode(query).tolist()

    where_filter = {"namespace": namespace} if namespace else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        score = 1.0 - dist
        output.append({
            "text": doc,
            "source": meta.get("source", "Unknown"),
            "score": round(score, 4),
            "chunk_index": meta.get("chunk_index", 0)
        })

    return output


def delete_namespace(namespace: str):
    collection = _get_collection()
    results = collection.get(where={"namespace": namespace})
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks from namespace '{namespace}'.")
