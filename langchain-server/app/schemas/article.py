from pydantic import BaseModel
from datetime import datetime


class SentenceResponse(BaseModel):
    id: int
    text: str
    order: int

    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    title: str
    content: str


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    sentences: list[SentenceResponse] = []

    class Config:
        from_attributes = True
