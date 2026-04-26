from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="Syndi AI Embed Service", version="1.0.0")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

class EmbedRequest(BaseModel):
    texts: List[str]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimension: int

_model = None
def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

@app.get("/health")
async def health():
    return {"status": "ok", "model": EMBEDDING_MODEL, "dim": EMBEDDING_DIM}

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    vectors = _get_model().encode(request.texts, convert_to_numpy=True)
    return EmbedResponse(embeddings=[v.tolist() for v in vectors], model=EMBEDDING_MODEL, dimension=EMBEDDING_DIM)
