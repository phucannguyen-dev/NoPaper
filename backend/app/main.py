import os
import json
from uuid import UUID
from typing import List

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionLocal, init_models
from .embed import embed_text
from .models import Embedding
from .ocr import run_ocr
from .search import router as search_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    await init_models()

@app.get("/")
def root():
    return {"status": "Backend running on port 8001"}

class EmbedRequest(BaseModel):
    text: str

@app.post("/ocr")
async def ocr_api(file: UploadFile = File(...)):
    content = await file.read()
    text = run_ocr(content)
    return {"text": text}

@app.post("/embed")
async def embed_api(body: EmbedRequest, db: AsyncSession = Depends(get_db)):
    vector = embed_text(body.text)
    record = Embedding(text=body.text, vector=vector)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"id": str(record.id), "embedding": vector}

app.include_router(search_router)

@app.get("/list")
async def list_embeddings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Embedding))
    records = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "text": r.text[:100],
            "created_at": r.created_at
        }
        for r in records
    ]

@app.delete("/delete/{id}")
async def delete_embedding(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Embedding).where(Embedding.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    await db.delete(record)
    await db.commit()
    return {"message": f"Deleted record {id}"}

@app.get("/detail/{id}")
async def get_embedding_detail(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Embedding).where(Embedding.id == id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": str(record.id),
        "text": record.text,
        "embedding": record.vector,
        "created_at": record.created_at
    }

@app.delete("/clear")
async def clear_all_embeddings(db: AsyncSession = Depends(get_db)):
    if os.getenv("APP_ENV") != "development":
        raise HTTPException(status_code=403, detail="Operation not allowed in this environment")
    await db.execute(delete(Embedding))
    await db.commit()
    return {"message": "All embeddings deleted"}
class DeleteBatchRequest(BaseModel):
    ids: List[UUID]

@app.delete("/delete-batch")
async def delete_batch(request: DeleteBatchRequest, db: AsyncSession = Depends(get_db)):
    if not request.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    stmt = delete(Embedding).where(Embedding.id.in_(request.ids))
    result = await db.execute(stmt)
    await db.commit()

    return {"message": f"Deleted {result.rowcount} records"}

@app.get("/count")
async def count_embeddings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count()).select_from(Embedding))
    count = result.scalar_one()
    return {"count": count}