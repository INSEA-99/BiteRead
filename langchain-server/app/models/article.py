from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sentences = relationship("Sentence", back_populates="article", cascade="all, delete-orphan")


class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    article = relationship("Article", back_populates="sentences")
    progress = relationship("UserProgress", back_populates="sentence")
