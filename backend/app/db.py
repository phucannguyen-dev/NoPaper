import os
import uuid
from sqlalchemy import (
    Column, Text, TIMESTAMP, func, Float, text
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Cấu hình cơ sở dữ liệu
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Định nghĩa model
class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    vector = Column(ARRAY(Float), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Hàm khởi tạo bảng và extension
async def init_models():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

# Đã gộp nội dung từ db.py và models.py vào file này.