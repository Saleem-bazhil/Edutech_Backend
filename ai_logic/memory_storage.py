import chromadb
from chromadb.config import Settings
from core.config import settings

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.Client(Settings(persist_directory=settings.CHROMA_DIR))
    if _collection is None:
        _collection = _client.get_or_create_collection("memory")
    return _collection

def add_memory(texts, metadatas=None, ids=None):
    col = get_collection()
    # Generate IDs if not provided
    if ids is None:
        ids = [str(i) for i in range(col.count() or 0, (col.count() or 0) + len(texts))]
    col.add(documents=texts, metadatas=metadatas or [{}]*len(texts), ids=ids)

def query_memory(query_text, n_results=4):
    col = get_collection()
    res = col.query(query_texts=[query_text], n_results=n_results)
    docs = res.get("documents", [[]])[0]
    return docs
