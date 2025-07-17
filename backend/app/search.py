from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import numpy as np

from .db import SessionLocal
from .models import Embedding
from .embed import embed_text

router = APIRouter()

class EmbedRequest(BaseModel):
    text: str

async def get_db():
    async with SessionLocal() as session:
        yield session

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

@router.post("/search")
async def search_api(body: EmbedRequest, db: AsyncSession = Depends(get_db)):
    query = select(Embedding)
    results = await db.execute(query)
    records = results.scalars().all()

    input_vector = np.array(embed_text(body.text))
    scored = []

    for record in records:
        db_vector = np.array(record.vector)
        sim = cosine_similarity(input_vector, db_vector)
        scored.append((sim, record))

    top = sorted(scored, key=lambda x: x[0], reverse=True)[:5]

    return [
        {
            "id": str(r.id),
            "text": r.text[:100],
            "similarity": round(score, 4),
            "created_at": r.created_at
        }
        for score, r in top
    ]